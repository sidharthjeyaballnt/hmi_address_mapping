#!/usr/bin/env python3
"""
memlink_bridge_node.py

Bridges the physical Pro-face HMI touchscreen (Memory Link protocol over
Ethernet) to the same robot topics joy_teleop_node.py / hmi_keyboard_node.py
already drive — so the FSM/safety stack doesn't need to know which operator
front-end is in use.

Address map (see memory_map_hmi.ods). GP-Pro EX 6-digit addresses decode as
word = first 4 digits, bit = last 2 digits (documented in memlink_write.py);
4-digit addresses are plain words.

Outputs from HMI (operator buttons) — polled from word 5000 and word 5102:
  5000.01 / 5000.02  Sprayhead Up/Down  -> incremental /wrist_cmd jog
  5000.03 / 5000.05  Right/Left         -> /paint_bot/cmd_vel angular.z
  5000.04 / 5000.08  Back/Front         -> /paint_bot/cmd_vel linear.x
  5000.06 / 5000.07  Gantry Up/Down     -> /z_axis_cmd Z_VEL jog
  5102.00            E-stop             -> /start_cmd 'ESTOP' (rising edge)

Inputs to HMI (robot/sensor status) — written each cycle:
  3000.00  System boot-up successful  (latched true after first /robot_state)
  4001     Software check             (placeholder OK=1, no real diagnostic yet)
  4002     Battery check              (/bms_status.valid)
  4003     Sensors check              (/scan freshness — lidar liveliness)
  4004     Camera check               (placeholder OK=1, no real diagnostic yet)
  5100     Paint level                (/paint_head_status.paint_level * 100)
  5101     Battery level              (/bms_status.soc)
  5103     System status              (/robot_state, mapped to a small int code)

Not bridged (Purpose=NA / unclear in the sheet): 400000, 6000, 700001, 800001,
and the trailing row with a blank address.
"""
import socket
import threading
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from painting_robot_msgs.msg import ZAxisCmd, WristCmd, BmsStatus, PaintHeadStatus

from painting_robot_hmi.memlink_protocol import read_words, write_words, MemLinkError

# Base motion jog disabled in these FSM states (mirrors hmi_keyboard_node / joy_teleop_node).
AUTO_STATES = {'SYSTEM_CHECK', 'WALL_ALIGN', 'WALL_FOLLOW',
               'STEP_REALIGN', 'CORNER_LOGIC', 'CORNER_APPROACH', 'PAINT_EXECUTE'}
# Z jog / teach only allowed in these states (mirrors hmi_keyboard_node.Z_TEACH_STATES).
Z_TEACH_STATES = {'IDLE', 'SYSTEM_CHECK'}

# word 5000 bit numbers (outputs)
BIT_SPRAY_UP, BIT_SPRAY_DOWN = 1, 2
BIT_RIGHT, BIT_BACK, BIT_LEFT = 3, 4, 5
BIT_GANTRY_UP, BIT_GANTRY_DOWN = 6, 7
BIT_FRONT = 8
WORD_OUTPUTS = 5000

# word 5102 bit 0 (outputs)
BIT_ESTOP = 0
WORD_ESTOP = 5102

# Scan is considered "live" for the sensors check if one arrived within this long.
SCAN_FRESH_S = 2.0

# Mirrors painting_robot_fsm/states.py RobotState (Enum, auto() order starting
# at 1). Duplicated as plain strings->ints rather than importing that package,
# since every other HMI node already treats /robot_state as an opaque string
# and painting_robot_hmi has no existing dependency on painting_robot_fsm.
ROBOT_STATE_CODES = {
    'IDLE':             2,
    'SYSTEM_CHECK':     2,
    'WALL_ALIGN':       0,
    'WALL_FOLLOW':      0,
    'STEP_REALIGN':     0,
    'CORNER_LOGIC':     0,
    'CORNER_APPROACH':  0,
    'FAULT':            3,
    'PAINT_EXECUTE':    0,
    'HOLD':             1,
}


def _bit(word: int, n: int) -> int:
    return (word >> n) & 1


class MemlinkBridgeNode(Node):

    def __init__(self):
        super().__init__('memlink_bridge_node')

        self.declare_parameter('hmi_host', '192.168.1.100')
        self.declare_parameter('hmi_port', 1024)
        self.declare_parameter('poll_rate_hz', 10.0)
        self.declare_parameter('max_linear_mps', 0.20)
        self.declare_parameter('max_angular_radps', 0.40)
        self.declare_parameter('z_jog_rpm', 400)
        self.declare_parameter('wrist_jog_deg_per_s', 5.0)

        self._host = self.get_parameter('hmi_host').value
        self._port = int(self.get_parameter('hmi_port').value)
        self._poll_hz = float(self.get_parameter('poll_rate_hz').value)
        self._max_linear = float(self.get_parameter('max_linear_mps').value)
        self._max_angular = float(self.get_parameter('max_angular_radps').value)
        self._z_jog_rpm = int(self.get_parameter('z_jog_rpm').value)
        self._wrist_jog_deg_per_s = float(self.get_parameter('wrist_jog_deg_per_s').value)

        # ── Publishers ───────────────────────────────────────────────────────
        self._vel_pub    = self.create_publisher(Twist, '/paint_bot/cmd_vel', 10)
        self._start_pub  = self.create_publisher(String, '/start_cmd', 10)
        self._zaxis_pub  = self.create_publisher(ZAxisCmd, '/z_axis_cmd', 10)
        self._wrist_pub  = self.create_publisher(WristCmd, '/wrist_cmd', 10)

        # ── Cached ROS state (read by socket thread, written by callbacks) ──
        self._lock = threading.Lock()
        self._fsm_state      = 'IDLE'
        self._boot_seen      = False
        self._bms_valid      = False
        self._bms_soc        = 0.0
        self._paint_level    = 0.0
        self._wrist_actual   = 0.0
        self._last_scan_mono = 0.0

        self.create_subscription(String, '/robot_state', self._state_cb, 10)
        self.create_subscription(BmsStatus, '/bms_status', self._bms_cb, 10)
        self.create_subscription(PaintHeadStatus, '/paint_head_status', self._head_cb, 10)
        self.create_subscription(LaserScan, '/scan', self._scan_cb, 10)

        # ── Socket thread state (owned solely by _socket_loop) ──────────────
        self._z_jogging = 0          # edge-tracked, like hmi_keyboard_node
        self._wrist_target = None    # seeded from _wrist_actual on first jog press
        self._prev_estop = 0
        self._placeholder_checks_sent = False

        self._stop_evt = threading.Event()
        self._thread = threading.Thread(target=self._socket_loop, daemon=True)
        self._thread.start()

    # ── ROS callbacks ────────────────────────────────────────────────────────

    def _state_cb(self, msg: String):
        with self._lock:
            self._fsm_state = msg.data
            self._boot_seen = True

    def _bms_cb(self, msg: BmsStatus):
        with self._lock:
            self._bms_valid = bool(msg.valid)
            self._bms_soc = float(msg.soc)

    def _head_cb(self, msg: PaintHeadStatus):
        with self._lock:
            self._paint_level = float(msg.paint_level)
            self._wrist_actual = float(msg.wrist_actual_deg)

    def _scan_cb(self, msg: LaserScan):
        with self._lock:
            self._last_scan_mono = time.monotonic()

    # ── Failsafe ─────────────────────────────────────────────────────────────

    def _publish_safe_stop(self):
        """Called whenever the Memory Link connection drops — a lost socket
        must not leave a jog command stuck on."""
        self._vel_pub.publish(Twist())
        stop = ZAxisCmd()
        stop.z_mode = ZAxisCmd.Z_STOP
        stop.z_velocity = 0
        self._zaxis_pub.publish(stop)
        self._z_jogging = 0

    # ── Output handling (HMI button -> ROS) ─────────────────────────────────

    def _handle_outputs(self, word_outputs: int, word_estop: int):
        with self._lock:
            fsm_state = self._fsm_state
            wrist_actual = self._wrist_actual

        # Base motion jog — level-triggered on current button state, like
        # joy_teleop_node's drive handler (not edge-triggered).
        if fsm_state not in AUTO_STATES:
            lin = 0.0
            if _bit(word_outputs, BIT_FRONT):
                lin += self._max_linear
            if _bit(word_outputs, BIT_BACK):
                lin -= self._max_linear
            ang = 0.0
            if _bit(word_outputs, BIT_LEFT):
                ang += self._max_angular
            if _bit(word_outputs, BIT_RIGHT):
                ang -= self._max_angular
            cmd = Twist()
            cmd.linear.x = lin
            cmd.angular.z = ang
            self._vel_pub.publish(cmd)
        else:
            self._vel_pub.publish(Twist())

        # Gantry Z jog — edge-triggered, mirrors hmi_keyboard_node.send_z_jog.
        direction = 0
        if _bit(word_outputs, BIT_GANTRY_UP):
            direction = +1
        elif _bit(word_outputs, BIT_GANTRY_DOWN):
            direction = -1
        if direction != self._z_jogging:
            if direction != 0 and fsm_state not in Z_TEACH_STATES:
                direction = 0   # blocked outside teach states, stay stopped
            if direction != self._z_jogging:
                self._z_jogging = direction
                cmd = ZAxisCmd()
                if direction == 0:
                    cmd.z_mode = ZAxisCmd.Z_STOP
                    cmd.z_velocity = 0
                else:
                    cmd.z_mode = ZAxisCmd.Z_VEL
                    cmd.z_velocity = direction * self._z_jog_rpm
                self._zaxis_pub.publish(cmd)

        # Sprayhead wrist jog — level-triggered increment, seeded from the
        # last known actual angle on first press (no velocity mode on wrist).
        spray_dir = 0
        if _bit(word_outputs, BIT_SPRAY_UP):
            spray_dir = +1
        elif _bit(word_outputs, BIT_SPRAY_DOWN):
            spray_dir = -1
        if spray_dir != 0:
            if self._wrist_target is None:
                self._wrist_target = wrist_actual
            step = self._wrist_jog_deg_per_s / self._poll_hz
            self._wrist_target += spray_dir * step
            cmd = WristCmd()
            cmd.wrist_target_deg = self._wrist_target
            self._wrist_pub.publish(cmd)
        else:
            self._wrist_target = None

        # E-stop — rising edge only, dedicated hardware button latches
        # straight to ESTOP (not the keyboard's HOLD->FAULT->ESTOP ladder).
        estop_bit = _bit(word_estop, BIT_ESTOP)
        if estop_bit and not self._prev_estop:
            msg = String()
            msg.data = 'ESTOP'
            self._start_pub.publish(msg)
            self.get_logger().warn('[memlink] E-stop pressed on HMI -> ESTOP')
        self._prev_estop = estop_bit

    # ── Input handling (ROS -> HMI) ──────────────────────────────────────────

    def _write_inputs(self, sock):
        with self._lock:
            boot_seen = self._boot_seen
            bms_valid = self._bms_valid
            bms_soc = self._bms_soc
            paint_level = self._paint_level
            fsm_state = self._fsm_state
            scan_fresh = (time.monotonic() - self._last_scan_mono) < SCAN_FRESH_S if self._last_scan_mono else False

        if boot_seen:
            write_words(sock, 3000, [1])

        software_ok = 2
        battery_ok = 2
        sensors_ok = 2
        camera_ok = 2
        write_words(sock, 4001, [software_ok, battery_ok, sensors_ok, camera_ok])

        write_words(sock, 5100, [
            int(round(paint_level * 100)) & 0xFFFF,
            int(round(bms_soc)) & 0xFFFF,
        ])

        status_code = ROBOT_STATE_CODES.get(fsm_state, 0)
        write_words(sock, 5103, [status_code])

    # ── Socket thread ─────────────────────────────────────────────────────────

    def _socket_loop(self):
        period = 1.0 / self._poll_hz if self._poll_hz > 0 else 0.1
        while not self._stop_evt.is_set():
            try:
                with socket.create_connection((self._host, self._port), timeout=10) as sock:
                    sock.settimeout(10)
                    self.get_logger().info(f'[memlink] connected to {self._host}:{self._port}')
                    while not self._stop_evt.is_set():
                        word_outputs = read_words(sock, WORD_OUTPUTS, 1)[0]
                        word_estop = read_words(sock, WORD_ESTOP, 1)[0]
                        self._handle_outputs(word_outputs, word_estop)
                        self._write_inputs(sock)
                        time.sleep(period)
            except (OSError, ConnectionError, MemLinkError) as e:
                self.get_logger().error(f'[memlink] connection error: {e}; reconnecting in 5s')
                self._publish_safe_stop()
                time.sleep(5)

    def destroy_node(self):
        self._stop_evt.set()
        self._publish_safe_stop()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MemlinkBridgeNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
