# HANDOFF — state of the work as of 2026-11-13

Written so a fresh Claude on a new machine can pick up. `CLAUDE.md` has the short version; this is the full record.
Repo: `sidharthjeyaballnt/hmi_address_mapping`, branch `main`. Paths below assume the repo is at `~/copilot/HMI` (adjust if different).

## 1. What the project is
- A Pro-face HMI touchscreen is the operator panel for a wall-painting robot.
- The HMI exposes its **internal word memory (0-9999)** to a PC over Ethernet using Pro-face's **Memory Link** protocol (not Modbus). The ROS 2 node `memlink_bridge_node` polls button bits from that memory and publishes robot commands; it writes robot status back for the HMI to display.
- The robot software is a ROS 2 Humble workspace in `painting_seq_sid/` (FSM, wall following, painting, sim in Gazebo Classic).

## 2. Layout
| Path | What |
|---|---|
| `memlink_read.py` | Core Memory Link client (read), polling/CSV options |
| `memlink_write.py` | Write whole word, or single bit via read-modify-write |
| `address_mapper.py` | Snapshot-diff tool to discover which address a button/control uses |
| `button_monitor.py` | Classifies presses from touch X coordinate (addr 9235/9236/9237) |
| `read_hmi_bits.py` | Separate Modbus TCP (port 502) coil reader |
| `memory_map_hmi.ods` | The HMI address map (see section 4) |
| `painting_seq_sid/src/painting_robot_hmi/` | `memlink_bridge_node.py`, `memlink_protocol.py` (copy of the client so colcon can build), joystick/keyboard teleop |
| `painting_seq_sid/src/painting_robot_mcu/` | `portenta_bridge_node.py` (real hardware inputs), `safety_monitor_node.py`, `pmc_io_map.py` |
| `painting_seq_sid/src/painting_robot_bringup/` | launch files (`corner_bringup.launch.py` = the sim used here) and `config/pmc_io_map.yaml` |
| `painting_seq_sid/src/painting_robot_painting/` | `actuator_bridge_node.py` (sim + real backends), paint planner/executor |

Not in git (copy by hand): `dig_mtm.pdf` / `dig_mtm.txt` (Pro-face Memory Link manual, gitignored), `token.txt` (gitignored), `build/ install/ log/` (rebuild with colcon).

## 3. Memory Link protocol (verified against the real HMI on 2026-11-05)
- TCP to `192.168.1.100:1024`. Frame = marker (`B` host->HMI, `b` HMI->host) + 3 control bytes + 4-byte big-endian length + payload.
- Read: `ESC 'R'` + addr(2B BE) + count(2B BE) -> `ESC 'A'` + words. Write: `ESC 'W'` + addr + count + words -> `ACK (0x06)` or `NAK`+code.
- The HMI sends **"Demand Polling"** keepalives; the host must answer "Polling Command" (handled transparently in the client).
- Limits (manual): address 0-9999; **1-512 words per read/write** over Ethernet (256 applies to older serial modes); each word is 16-bit, 0-65535. Values above 65535 are silently wrapped by `v & 0xFFFF`. Negative = two's complement. 32-bit values need two words.
- GP-Pro EX 6-digit addresses decode as `word = first 4 digits, bit = last 2` (e.g. `500003` = word 5000 bit 3).
- Free-running noise addresses to ignore when diffing: 8, 2035, 2036, 2038, 2052, 2053. Touch event: 9235 (pulse), 9236 X, 9237 Y; 9945/9946 look like resolution (800/480).
- Unverified: whether the HMI accepts more than one simultaneous TCP client. Avoid running two clients while the bridge is connected.

## 4. HMI address map (from `memory_map_hmi.ods`)
Outputs from HMI (bridge polls word 5000 and 5102): word 5000 bit 1/2 Sprayhead Up/Down; 3 Right; 4 Back; 5 Left; 6/7 Gantry Up/Down; 8 Front; word 5102 bit 0 E-stop.
Inputs to HMI (bridge writes): 3000.0 boot-up OK; 4001 software check; 4002 battery check; 4003 sensors check; 4004 camera check; 5100 paint level (x100); 5101 battery level; 5103 system status (FSM state as int 1-10).
Not bridged / purpose NA: 400000, 6000, 700001, 800001, one blank row.

## 5. memlink_bridge_node behaviour
- Socket thread polls at `poll_rate_hz` (10 requested, ~6 Hz in practice: 2 reads + 4 writes per cycle) with auto-reconnect; on any connection error it publishes a safe stop (zero Twist, Z_STOP).
- Base jog -> `/paint_bot/cmd_vel` (0.20 m/s, 0.40 rad/s), level-triggered, **suppressed in auto FSM states** (SYSTEM_CHECK, WALL_ALIGN, WALL_FOLLOW, STEP_REALIGN, CORNER_LOGIC, CORNER_APPROACH, PAINT_EXECUTE). Z jog -> `/z_axis_cmd` (Z_VEL +/-400 rpm), only in IDLE/SYSTEM_CHECK. Wrist jog -> `/wrist_cmd` (5 deg/s increments seeded from last actual angle). E-stop rising edge -> `/start_cmd` "ESTOP".
- **Local edit made this session (revert for real hardware):** status words 4001-4004 (software, battery, sensors, camera) are hardcoded to **2** because the user has no battery/sensor hardware. Originals were `battery_ok = 1 if bms_valid else 0`, `sensors_ok = 1 if scan_fresh else 0`, software/camera `1`. The user asked for `2` as the default; what each value means on the HMI screen was not verified here.

## 6. Real hardware inputs (e-stop, auto/manual selector, paint level switch)
Handled by `portenta_bridge_node` (package `painting_robot_mcu`), NOT by the HMI bridge. It talks raw TCP packets to a Portenta MCU, decodes the digital-input byte with `config/pmc_io_map.yaml`, and publishes `/di_status_ros` (`DiStatus`: `estop` (active-low, DI3), `auto_manual` (DI1, True=auto), `paint_level_ok` (DI7), plus pause_resume, on_off, limits), `/mcu_status_ros` (`McuStatus`) and `/mcu_bridge_ok`. Paint level here is a digital OK/low flag, not analog.
Known defects, **not fixed**:
- `PORTENTA_IP = '192.168.1.100'` (port 5000) is hardcoded and is the **same IP as the HMI**; one must move. It should become a ROS parameter.
- `_handle_ultrasonic_status` publishes on `self._ultrasonic_pub`, which is never created -> `AttributeError` on the first ultrasonic packet.

## 7. The sim debugging story (all root causes found)
1. **HMI jog showed in `ros2 topic echo /paint_bot/cmd_vel` but sim robot didn't move -> ROS domain mismatch.** The sim ran on `ROS_DOMAIN_ID=77`/`ROS_LOCALHOST_ONLY=1`, the bridge on domain 0. Fixed by exporting the same vars in the bridge terminal. (Direct publish to `/paint_bot/cmd_vel` moved the sim fine, proving the controller path was OK.)
2. **Gantry/spray head didn't move -> the corner launch hardcoded `attach_gantry:=false`** so `zAxis_joint`/`wrist_joint` did not exist and `paint_axis_controller` failed to activate ("Not existing: zAxis_joint/position").
3. **Z jog then blocked by the homing gate** (`jog blocked — press LB to arm homing first`): homing is armed by the joystick LB button and the HMI bridge has no homing path. The HMI map has no teach-homing buttons.
4. **Pre-homed sim then auto-stopped at once** because `_loop` stops at `pos <= z_soft_lower_mm` and the sim starts at exactly 0 mm.
5. **Sim `set_wrist` only logged**; the sim `wrist_joint` is a 0-1.4 m *prismatic* slide, and Z trajectories forced the wrist to 0.

## 8. Changes made this session (committed, pushed: `bea39d7`, `b125101`)
- `corner_bringup.launch.py`: new launch arg `attach_gantry` (default `true`) used in the xacro command; actuator bridge gets `sim_pre_homed: True` and `z_soft_lower_mm: -5.0`.
- `actuator_bridge_node.py` (`SimBackend`): param `sim_pre_homed` (skip LB homing, sim only); params `wrist_sim_center_m` (0.15) and `wrist_sim_m_per_deg` (0.15/45). Wrist degrees map to the slide: +45 deg -> 0.30 m, 0 -> 0.15 m, -45 -> 0. **Positive degrees = up** (matches the HMI "Sprayhead UP" button). The paint executor's own convention is the opposite (its +45 is a "down" flick), so in the sim an executor down-flick looks like the head going up. A negative `wrist_sim_m_per_deg` flips it. `set_wrist` now publishes a trajectory; Z trajectories include the current wrist target instead of 0.
- `.gitignore`: `painting_seq_sid/build|install|log`.
- Verified in an isolated headless sim (domain 88): gantry up to 1.2 m / down to 0; wrist 20 deg -> 0.217 m, -45 -> 0.0, +45 -> 0.30, 0 -> 0.15; a Z jog leaves the wrist unchanged. **Not** verified with the physical HMI buttons or in the Gazebo GUI.

## 9. Open items / ideas (none started)
- **Bridge publishes zero Twists continuously** (~6 Hz) when no base button is held. This fights any other publisher on `/paint_bot/cmd_vel` (measured: travel 0.55 m instead of ~0.8 m in 4 s with a second publisher). Proposed fix: publish only while a button is held plus one zero on release; the diff-drive `cmd_vel_timeout` is 0.5 s.
- `stub_bringup.launch.py` and `paintbot_sim_bringup.launch.py` still hardcode `attach_gantry:=false`.
- Decide whether the HMI needs buttons to arm/teach homing for the real machine (real SBC backend still requires teach-homing; the `sim_pre_homed` shortcut is sim only).
- Revert the hardcoded "2" status words when real battery/sensors exist.
- Fix the Portenta IP conflict and the ultrasonic publisher (section 6).
- `rplidar_ros` did not show up in the pushed file list (probably ignored by `painting_seq_sid/src/.gitignore` or empty) — clone the driver separately on a new machine if the real lidar is needed.

## 10. History and housekeeping
- `painting_seq_sid/src` used to be its own git repo (`sidharthjeyaballnt/sid_painting_robot`, last commit `ee46e56`, 2026-11-04). On 2026-11-13 its `.git` was **moved** (not deleted) to `~/copilot/sid_painting_robot_dotgit_backup` on the old machine, and the files were absorbed into this repo. That GitHub repo still exists with its history.
- **Security:** the `origin` remote URL of this repo contained a GitHub personal access token in plain text, and it was printed in a chat transcript. Revoke it at github.com/settings/tokens and set a clean URL: `git remote set-url origin https://github.com/sidharthjeyaballnt/hmi_address_mapping.git`. Check this has been done before assuming pushes work.
- Test technique: run your own isolated sim with `ROS_DOMAIN_ID=88 ROS_LOCALHOST_ONLY=1 GAZEBO_MASTER_URI=http://localhost:11999 ros2 launch painting_robot_bringup corner_bringup.launch.py headless:=true`; when piping `ros2 topic echo` use `timeout -s INT` (SIGTERM loses buffered output); if `ros2 topic echo` fails with `!rclpy.ok()`, run `ros2 daemon stop && ros2 daemon start`.

## 11. Things that do not travel via git
- `~/.claude/CLAUDE.md` (the user's global rules, incl. first-principles-teacher explanation style) and `~/.claude/skills/first-principles-teacher/` (and `graphify/`) — copy to the new machine.
- Auto-memory: `~/.claude/projects/-home-ira-linux-copilot-HMI/memory/` (one note: sim runs on domain 77). Same content is in `CLAUDE.md`, so copying is optional.
- `token.txt` files (gitignored) — copy or regenerate; the Pro-face manual `dig_mtm.pdf`.
- Optional: this session's transcript `~/.claude/projects/-home-ira-linux-copilot-HMI/2d733ba1-53a0-48ff-bdb5-32b4572d6b5d.jsonl` (~3 MB). Copy it to the same path with the repo at the same location and `claude --resume` can reopen it. The two markdown files are the reliable route.

To resume: clone the repo, open Claude Code in the folder, and say "Read HANDOFF.md and tell me where we are."
