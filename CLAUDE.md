# Project: Pro-face HMI + painting robot (ROS 2 Humble)

This repo has two parts. Full history and open items are in `HANDOFF.md` — read it first when resuming.

1. **Memory Link tools** (repo root, plain Python, no pip deps): read/write the Pro-face HMI's internal word memory (addresses 0-9999) over Ethernet.
   `memlink_read.py`, `memlink_write.py`, `address_mapper.py`, `button_monitor.py`, `read_hmi_bits.py` (Modbus TCP coils).
2. **`painting_seq_sid/`** — ROS 2 Humble colcon workspace for the wall-painting robot. `src/painting_robot_hmi/.../memlink_bridge_node.py` bridges the physical HMI touchscreen to the robot topics.

## Setup facts
- HMI: `192.168.1.100:1024` (Memory Link). PC wired NIC `enp44s0` = `192.168.1.50/24`.
- The Gazebo sim runs on **`ROS_DOMAIN_ID=77` + `ROS_LOCALHOST_ONLY=1`**. Every other terminal (bridge, echo, debugging) must export the same, or topics appear to work but the sim never sees them.
- `install/` is NOT symlinked: after editing a package run `colcon build --packages-select <pkg>` and re-source.

## Run the sim + HMI
Terminal 1 (sim) and Terminal 2 (bridge), both after `export ROS_DOMAIN_ID=77 ROS_LOCALHOST_ONLY=1` and sourcing `/opt/ros/humble/setup.bash` + `painting_seq_sid/install/setup.bash`:
```
ros2 launch painting_robot_bringup corner_bringup.launch.py
ros2 run painting_robot_hmi memlink_bridge_node --ros-args -p hmi_host:=192.168.1.100 -p hmi_port:=1024
```

## Working rules (from the user)
- Explain things in first-principles-teacher style (simple language, step by step, one worked example) — see `~/.claude/CLAUDE.md`.
- Never commit `token.txt` or any credential; both `token.txt` files are gitignored. Never print tokens in output.
- Don't push, delete, or kill the user's running processes without being asked. Prefer reversible steps (move aside instead of delete).
- When testing a sim yourself while the user's may run, use an isolated `ROS_DOMAIN_ID=88` and `GAZEBO_MASTER_URI=http://localhost:11999`, and stop only your own processes.
