# Graph Report - src  (2026-11-04)

## Corpus Check
- 148 files · ~126,890 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 650 file(s) not represented in the graph (top: .npy 534, .msg 26, .STL 20)

## Summary
- 2175 nodes · 3656 edges · 166 communities (81 shown, 85 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 205 edges (avg confidence: 0.84)
- Token cost: 761,345 input · 0 output

## Community Hubs (Navigation)
- HMI Logging Node
- Bringup Bug Fixes & Launch
- SUCKIN Fault Diagnosis
- Corner Detection Pipeline
- Navigation Arc Turn Utils
- FSM State Handlers
- Env Monitoring V2
- Paint Bot Controller Config
- Ultrasonic Sensor Node
- Corner Event Test Suite
- FSM Safety & Collision
- HMI Node Callbacks
- FSM Motion Queue
- MCU Safety Policy Gate
- Robot Workflow Diagram
- Navigation Geometry Utils
- Actuator Bridge Config
- Navigation RANSAC/PCA Fit
- Paint Executor: Stroke Lifecycle
- Paint Executor: Homing & Wrist
- Paint Executor: FSM Sync
- Rotation Calibration Test
- State Machine & Safety Monitor
- Battery Management (BMS) Node
- HMI Keyboard & Joystick Teleop
- Wrist Motor Test
- Wall Motion Params Config
- Perception Geometry Utils
- Bumpout & Corner Detection
- Painted Area Report Test
- EKF Localization Config
- Gantry Limit Teach-Homing
- Wrist Driver Commands
- Safety Logic Test Harness
- Sim Actuator Backend
- Joystick Teleop Handlers
- Env Monitoring Config
- Leadshine Motor Driver
- Leadshine Driver Test
- Actuator Bridge Node
- Segment Corner Classification
- Portenta Bridge Node
- ROS Graph: Control Nodes
- ROS Node/Topic Graph
- Joystick Quick Reference
- Scan Capture & Arc Test
- ROS2 Controllers Config
- Base Drive Kinematics
- Leadshine Driver (standalone)
- Base Drive Test
- Paint Demo Node
- Maneuver Planner Geometry
- Stanley Sim (Uniform)
- Base Drive Test (2)
- Wall Pose Pipeline Diagram
- PMC IO Map
- MCU Heartbeat & IO Commands
- Portenta TCP Client
- Corner Spray Analysis
- Flake8 Lint Test
- Stanley Sim (Base)
- PEP257 Lint Test
- Cliff Detection Node
- Actuator Backend Interface
- Paint Planner Node
- Arc 90° Test
- Bump Depth Limit Diagram
- Suck-in vs Two Corners Diagram
- Leadshine Standalone Script
- Yaw Monitor Test
- Leadshine RPi Driver
- Copyright Lint Test
- Bump Room 10x8 Layout
- Execution Flow State Diagram
- PMC IO Map Config
- Wall Detection Config
- Arc Test Node
- Single Scan Capture
- 1m Bump Sequence Diagram
- Bump Room Strokes+Pose Plot
- PCA Line Fitting Example
- Internal Defer Guard Diagram
- Lidar Scan Capture Node
- Distance Check Skip Diagram
- Telemetry Logging Node
- Paint Level Sensor Config
- PCA Direction Angle Utils
- Z-Limit Switch Test
- LiDAR Robot Frame Diagram
- LiDAR Arc Zones Diagram
- Stanley Sim Output Plot
- Cliff Scan Capture Test
- Bump Room Strokes Plot
- External Turn Geometry Diagram
- Sketch Layout Dimensions
- FSM Corner Logic Handler
- Send IO Packet Script
- Z-Axis Motor Test
- Bump Depth Circles Diagram
- Paint Quality Spray Angle Plot
- Stroke Redundancy Gate Fix
- Combined Arc RANSAC Fit
- Just-Bump-Out Dimensions Diagram
- Copyright Lint Test (dup A)
- Copyright Lint Test (dup B)
- Copyright Lint Test (dup C)
- Copyright Lint Test (dup D)
- Run-With-Log Script
- Sim Time Config
- Gazebo Params Config
- IO Map: Buzzer Config
- IO Map: Ceiling Detect Config
- IO Map: E-Stop Limits Config
- IO Map: E-Stop Config
- IO Map: Lower Limit Config
- IO Map: On/Off Config
- IO Map: Pause/Resume Config
- IO Map: Relay Status Config
- IO Map: Upper Limit Config
- IO Map: Safety Relay Config
- IO Map: Tower Amber Config
- IO Map: Tower Green Config
- HMI PEP257 Lint
- MCU PEP257 Lint
- Navigation Flake8 Lint
- Painting Flake8 Lint
- Perception Flake8 Lint
- Perception PEP257 Lint
- Corner Recovery Hysteresis Fix
- Systemd Autostart Setup
- Wheel Diameter Calibration
- Track Width Calibration
- SBC-PMC Network Setup
- Stroke Gate Reset on Hold
- Paint Stroke Start Tracking
- Project README
- LiDAR Pipeline Mermaid Diagram
- Actuator Bridge Edit Note
- Sam Robot Description Build

## God Nodes (most connected - your core abstractions)
1. `StateMachineNode` - 47 edges
2. `EnvMonitoringV2` - 33 edges
3. `WallMotionNode` - 32 edges
4. `PortentaBridgeNode` - 29 edges
5. `ros__parameters` - 28 edges
6. `SafetyMonitorNode` - 28 edges
7. `HMINode` - 27 edges
8. `ros__parameters` - 24 edges
9. `MotionQueue` - 23 edges
10. `LoggingNode` - 23 edges

## Surprising Connections (you probably didn't know these)
- `EnvStatus.msg` --semantically_similar_to--> `EnvStatus.msg (crawl_backup field)`  [INFERRED] [semantically similar]
  painting_robot_msgs/CMakeLists.txt → docs/SESSION_HANDOFF.md
- `painting_robot_fsm/src/state_machine_node.cpp (C++ port)` --semantically_similar_to--> `state_machine_node.py (fsm_context latched_corner_type)`  [INFERRED] [semantically similar]
  docs/SESSION_HANDOFF_2026-10-30.md → docs/SESSION_HANDOFF.md
- `StateMachineNode` --uses--> `MotionQueue`  [INFERRED]
  painting_robot_fsm/painting_robot_fsm/state_machine_node.py → painting_robot_fsm/painting_robot_fsm/motion_queue.py
- `StateMachineNode` --uses--> `CornerApproachHandler`  [INFERRED]
  painting_robot_fsm/painting_robot_fsm/state_machine_node.py → painting_robot_fsm/painting_robot_fsm/states.py
- `StateMachineNode` --uses--> `CornerLogicHandler`  [INFERRED]
  painting_robot_fsm/painting_robot_fsm/state_machine_node.py → painting_robot_fsm/painting_robot_fsm/states.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **WALL_DIST / obstacle_persist fault chain across sessions (same failure mode, iteratively fixed)** — docs_session_handoff_internal_corner_reverse_crawl, docs_session_handoff_mid_recipe_wall_dist_skip, docs_handoff1027_post_corner_recovery, docs_handoff1030_1567819_recovery_hysteresis, docs_bump_room_fault_report_suckin_issue [INFERRED 0.85]
- **Redundant-stroke gate feature evolution across sessions** — docs_session_handoff_redundant_stroke_gate, docs_handoff1027_stroke_gate_mode, docs_handoff1030_c8471ff_corner_stroke_gate, docs_handoff1030_abf0f80_stroke_suppression [INFERRED 0.85]
- **painting_robot_msgs interface package: all generated ROS message types** — painting_robot_msgs_envstatus_msg, painting_robot_msgs_wallpose_msg, painting_robot_msgs_wallstatus_msg, painting_robot_msgs_paintheadstatus_msg, painting_robot_msgs_zaxiscmd_msg, painting_robot_msgs_wristcmd_msg, painting_robot_msgs_spraycmd_msg [EXTRACTED 1.00]

## Communities (166 total, 85 thin omitted)

### Community 0 - "HMI Logging Node"
Cohesion: 0.07
Nodes (19): atomic_write(), LoggingNode, OnlineStat, analyze(), base_to_world(), body_corners(), chassis_outline(), clr_entry() (+11 more)

### Community 1 - "Bringup Bug Fixes & Launch"
Cohesion: 0.07
Nodes (18): bugs_n_fixes_Gaja.txt (display/env fixes, sim launch & lidar/wrist tty setup), joy_teleop_node (Direct Z_HOME sent), depth_fixture_detection_node (painting_robot_perception), hmi_keyboard_node (painting_robot_hmi), arctest_real_bot.launch.py, receive_io.py (raw socket receiver utility), painting_robot_ws_Nyx.txt (command notes: kills, bench/arctest launch, ssh hosts, serial device ids), paint_bot_description.launch.py (URDF) (+10 more)

### Community 2 - "SUCKIN Fault Diagnosis"
Cohesion: 0.04
Nodes (34): docs/bump_room_fault_report.md, bump_defer_internal guard (confirmed correct in this run), bump_room_10x8 first run — fault report, env_monitoring_v2 (no SUCKIN handler), maneuver_planner.py (SUCKIN_CUTOFF, suckin_radii), bump_box_1p2.world, bump_room_10x8.world, _do_internal_corner() (wall_motion_node.py) (+26 more)

### Community 3 - "Corner Detection Pipeline"
Cohesion: 0.10
Nodes (27): _detect_corner_event(), _detect_corner_event(), abs_line_angle_diff_deg(), classify_segment_pair(), clean_endpoint_from_fit(), debug_segment_geometry(), detect_best_corner(), detect_terminal_edges_from_fits() (+19 more)

### Community 5 - "FSM State Handlers"
Cohesion: 0.07
Nodes (11): CornerApproachHandler, FaultHandler, HoldHandler, IdleHandler, PaintExecuteHandler, RobotState, StateHandler, StepRealignHandler (+3 more)

### Community 7 - "Paint Bot Controller Config"
Cohesion: 0.05
Nodes (44): controller_manager, ros__parameters, joint_state_broadcaster, ros__parameters, type, paint_axis_controller, ros__parameters, type (+36 more)

### Community 8 - "Ultrasonic Sensor Node"
Cohesion: 0.08
Nodes (24): main(), UltrasoundNode, alarm_clear(), alarm_read(), calc(), crc16(), crc_check(), current_read() (+16 more)

### Community 9 - "Corner Event Test Suite"
Cohesion: 0.11
Nodes (19): _detect_corner_event(), classify_segment_pair(), clean_endpoint_from_fit(), detect_best_corner(), detect_terminal_edges_from_fits(), extract_combined_arc(), find_orientation_change(), fit_segment() (+11 more)

### Community 11 - "HMI Node Callbacks"
Cohesion: 0.09
Nodes (3): HMINode, main(), run_ui()

### Community 14 - "Robot Workflow Diagram"
Cohesion: 0.10
Nodes (31): After the maneuver (Re-align to wall; close distance error; skip paint if far out), After the maneuver (Re-align to wall; close distance error in bounded window; skip paint while too far out of position), Bump-out (Approach -> outward arc -> return arc -> align; depth bounded), Corner / shape detected (Latch geometry + choose recipe), Corner / shape detected (Latch geometry + choose recipe), External corner (Approach -> arc around vertex -> align with new wall), FAULT / ESTOP (Stop and flush queue), FAULT / ESTOP (Stop and flush queue; after reset, return to IDLE; start job again) (+23 more)

### Community 15 - "Navigation Geometry Utils"
Cohesion: 0.08
Nodes (11): angle_diff(), arc_slice(), main(), pca_fit(), range_check(), ransac_line(), theta_check(), WallDetectionNode (+3 more)

### Community 16 - "Actuator Bridge Config"
Cohesion: 0.07
Nodes (29): actuator_bridge_node, ros__parameters, base_accel_ms, base_counts_per_rev, base_decel_ms, base_frame_id, base_gear_ratio, base_left_id (+21 more)

### Community 17 - "Navigation RANSAC/PCA Fit"
Cohesion: 0.09
Nodes (7): angle_diff(), main(), pca_fit(), range_check(), ransac_line(), theta_check(), WallDetectionNode

### Community 21 - "Rotation Calibration Test"
Cohesion: 0.13
Nodes (6): main(), RotationTest, Unwrapper, yaw_of(), main(), StraightDrive

### Community 22 - "State Machine & Safety Monitor"
Cohesion: 0.11
Nodes (10): main(), main(), main(), main(), main(), main(), main(), CollisionWarnNode (+2 more)

### Community 23 - "Battery Management (BMS) Node"
Cohesion: 0.12
Nodes (5): BmsNode, main(), KvmsBms, r(), temp()

### Community 24 - "HMI Keyboard & Joystick Teleop"
Cohesion: 0.15
Nodes (3): main(), arc_slice(), main()

### Community 26 - "Wall Motion Params Config"
Cohesion: 0.08
Nodes (23): angle_kp, corner_fault_timeout_s, corner_swatch_pause_s, corner_turn_kp, corner_turn_segments, corner_turn_speed, corner_turn_tolerance, crawl_speed (+15 more)

### Community 27 - "Perception Geometry Utils"
Cohesion: 0.11
Nodes (13): clean_endpoint_from_fit(), find_orientation_change(), fit_plane_from_points(), fit_segment(), in_wrapped_arc(), mad_filter(), merge_collinear(), pca_fit() (+5 more)

### Community 28 - "Bumpout & Corner Detection"
Cohesion: 0.13
Nodes (14): _beam_continuity(), detect_bumpout(), detect_corners(), detect_external_corner(), detect_gapped_internal_from_fits(), _ends(), _line(), detect_motion_events() (+6 more)

### Community 30 - "EKF Localization Config"
Cohesion: 0.10
Nodes (20): ekf_filter_node, ros__parameters, base_link_frame, frequency, imu0, imu0_config, imu0_differential, imu0_relative (+12 more)

### Community 33 - "Safety Logic Test Harness"
Cohesion: 0.32
Nodes (10): check(), s_cliff_latch(), s_estop_no_autoresume(), s_fault_then_estop(), s_obstacle_autoresume(), s_obstacle_escalate(), s_operator_pause(), s_priority() (+2 more)

### Community 36 - "Env Monitoring Config"
Cohesion: 0.10
Nodes (19): env_monitoring_v2, ros__parameters, enable_wall_lost_ext_search, ext_trigger_turnaxis, external_latch_max, fake_stroke_ticks, front_cone_half_deg, internal_approach_dist (+11 more)

### Community 40 - "Segment Corner Classification"
Cohesion: 0.15
Nodes (11): abs_line_angle_diff_deg(), classify_segment_pair(), debug_segment_geometry(), detect_best_corner(), line_intersection(), _orient_toward_origin(), oriented_wall_dir(), pca_direction_angle() (+3 more)

### Community 42 - "ROS Graph: Control Nodes"
Cohesion: 0.24
Nodes (18): /controller_manager, /diff_cont, /diff_cont/odom (topic), /ekf_filter_node, /gazebo, /gazebo_ros2_control, paintbott_P1.png (ROS2 Node Graph), /imu/out (topic) (+10 more)

### Community 43 - "ROS Node/Topic Graph"
Cohesion: 0.14
Nodes (18): rosgraph.svg (rqt_graph ROS2 node/topic graph), /controller_manager, /diff_cont, /diff_cont/odom, /ekf_filter_node, /gazebo, /gazebo_ros2_control, /imu/out (+10 more)

### Community 44 - "Joystick Quick Reference"
Cohesion: 0.17
Nodes (17): /paint_bot/cmd_vel Topic, Emergency Stop (X Button / ESTOP), Painting Robot Finite State Machine (FSM), /gantry_limit_cmd Topic (Teach Upper/Lower Z Limits), Painting Robot Operator Joystick Quick Reference (Image), Joystick Quick Reference Guide, Lidar Scan Recording Toggle (B Button, /scan data), Logitech Gamepad (F310-style controller) (+9 more)

### Community 45 - "Scan Capture & Arc Test"
Cohesion: 0.20
Nodes (6): scan_cb(), main(), main(), Odom90Test, wrap_angle(), yaw_from_quat()

### Community 46 - "ROS2 Controllers Config"
Cohesion: 0.12
Nodes (16): controller_manager, ros__parameters, diff_cont, ros__parameters, type, type, base_frame_id, diff_cont (+8 more)

### Community 50 - "Paint Demo Node"
Cohesion: 0.17
Nodes (3): main(), PaintDemoNode, main()

### Community 51 - "Maneuver Planner Geometry"
Cohesion: 0.20
Nodes (8): bumpout_geometry(), _clamp(), external_radius(), _fmt(), Plan, plan_maneuver(), Step, suckin_radii()

### Community 52 - "Stanley Sim (Uniform)"
Cohesion: 0.19
Nodes (8): closed_loop_step(), compute_dist_error(), drift_increment(), lidar_geometry(), run(), run_sim(), select_gains(), stanley_correction()

### Community 54 - "Wall Pose Pipeline Diagram"
Cohesion: 0.14
Nodes (15): Arc Segmentation, EMA Filter (Front branch), EMA Filter (Right branch), Front Arc 0 degrees +/-30 degrees, Front Wall Pose, LiDAR Scan, PCA Fit (Front branch), PCA Fit (Right branch) (+7 more)

### Community 59 - "Corner Spray Analysis"
Cohesion: 0.27
Nodes (12): analyze(), base_to_world(), body_corners(), build(), chassis_outline(), clr_front(), clr_min_signed(), clr_right() (+4 more)

### Community 61 - "Flake8 Lint Test"
Cohesion: 0.16
Nodes (3): test_flake8(), test_flake8(), test_flake8()

### Community 62 - "Stanley Sim (Base)"
Cohesion: 0.23
Nodes (6): dist_error_corrected(), lidar_reading(), run(), stanley_omega(), step_realign(), wall_follow()

### Community 63 - "PEP257 Lint Test"
Cohesion: 0.15
Nodes (3): test_pep257(), test_pep257(), test_pep257()

### Community 64 - "Cliff Detection Node"
Cohesion: 0.21
Nodes (3): arc_mask(), CliffDetectionNode, main()

### Community 67 - "Arc 90° Test"
Cohesion: 0.23
Nodes (4): Arc90Test, main(), wrap_angle(), yaw_from_quat()

### Community 68 - "Bump Depth Limit Diagram"
Cohesion: 0.26
Nodes (11): Box Obstacle Depth d (protrusion from wall), Bump-Out Maneuver (Two-Arc Path), Case d=0.70m: R1=0.65 R2=0.30 phi=74.7deg OK, Case d=0.80m: R1=0.60 R2=0.30 phi=83.6deg OK, Case d=0.90m: R1=0.60 R2=0.30 phi=90.0deg LIMIT, Case d=1.00m: R1=0.60 R2=0.30 phi=96.4deg FAILS, Depth Limit d=0.90m (phi=90 degrees LIMIT case), R1 = 1 - 0.5d, clamped 0.60-0.85 (+3 more)

### Community 69 - "Suck-in vs Two Corners Diagram"
Cohesion: 0.24
Nodes (12): Bump-out Geometry (rear face depth), Corner Recipes (turn right, drive along rear face, turn left back onto wall), External Corner (Corner 1, end of face), Suck-in vs Two Corners Comparison Diagram, Internal Corner (Corner 2, meets wall), 1.2m Bump Rear Face -> Two Corners Worked Scenario, Robot Path Offset (0.77m from bump face), 0.5m Bump Rear Face -> SUCKIN Fault Scenario (+4 more)

### Community 71 - "Yaw Monitor Test"
Cohesion: 0.27
Nodes (3): deg(), yaw_from_quat(), YawMonitor

### Community 74 - "Bump Room 10x8 Layout"
Cohesion: 0.31
Nodes (11): bump_room_10x8.world (Gazebo World File), E Bump Obstacle (depth=0.5, dark gray wall bump-out), bump_room_10x8_layout.png (Room Layout Diagram), N Bump Obstacle (depth=1.0, dark gray wall bump-out), N Pillar (gap 0.24, orange obstacle near north wall), Robot Path (counter-clockwise, wall on right, green dashed), Room Boundary Walls (10m x 8m, light gray thick border), S Bump Obstacle (depth=0.8, dark gray wall bump-out) (+3 more)

### Community 75 - "Execution Flow State Diagram"
Cohesion: 0.27
Nodes (11): Wall Painting Execution Flow Diagram, CORNER_APPROACH, CORNER_LOGIC, FAULT, IDLE, Initial State (start marker), PAINT_EXECUTE, STEP_REALIGN (+3 more)

### Community 76 - "PMC IO Map Config"
Cohesion: 0.18
Nodes (10): solenoid, tower_red, pmc_io, digital_outputs, bit, enabled, type, bit (+2 more)

### Community 77 - "Wall Detection Config"
Cohesion: 0.18
Nodes (10): max_range, min_points, min_range, publish_rate, ray_window, right_center_deg, right_max_fit_dist, right_spread_deg (+2 more)

### Community 80 - "1m Bump Sequence Diagram"
Cohesion: 0.31
Nodes (9): Step 1: ARC1 - Spin In Place Left ~96 degrees, Step 2: ARC2 - Wide Arc Right 96 degrees, radius 0.90m, Box / Bump-out (1.0 m deep wall recess), Closest Robot-to-Box Gap on Path: 37 cm, 1.0m Box Robot Sequence Diagram, Lateral Shift ~1.0 m (sideways move achieved by ARC2), Robot Centre Path (green arc, ARC2), Robot Footprint (0.85 x 0.60 m) (+1 more)

### Community 81 - "Bump Room Strokes+Pose Plot"
Cohesion: 0.38
Nodes (10): Bump-out Painting Sequence Planner, Door/Window Zone (orange rectangles), Bump Room Strokes Pose Plot, Obstacle / Furniture Blocks (gray rectangles), Overlap Pair Count (8 overlap pairs), Overlapping Stroke, Robot Path (Odometry Trace), Room Perimeter Walls (+2 more)

### Community 82 - "PCA Line Fitting Example"
Cohesion: 0.24
Nodes (8): Covariance Ellipse (2-sigma), Fitted Wall (PCA) Line, Minor Axis - Wall Normal, PCA Line Fitting Intuition Figure, Principal Axis - Fitted Wall Length, plot_events(), plot_events(), plot_events()

### Community 83 - "Internal Defer Guard Diagram"
Cohesion: 0.29
Nodes (10): BUMPOUT Detector (range window 0.5-1.5 m), BUMPOUT latches -> normal two-arc maneuver, GUARD (new): remembers 'bump seen here', Internal Defer Guard Diagram, INTERNAL corner latch (front wall at 1.2 m, in window), Pillar seen but too far (1.6 m > 1.5 m window) - ignored, Two-arc maneuver (bumpout navigation), wall_lost -> FAULT state (+2 more)

### Community 85 - "Distance Check Skip Diagram"
Cohesion: 0.53
Nodes (9): Bump Obstacle (d = 1.2), Bumpout Painting Sequence, Distance Check Skip Position Diagram, Position A: Follow Wall (check ON), Position B: Beside Bump Face (check ON), Position C: After External Turn, Heading to Wall (CHECK SKIPPED), Position D: Internal Approach (check ON again), Position E: After Internal Turn, Back on Wall (check ON) (+1 more)

### Community 86 - "Telemetry Logging Node"
Cohesion: 0.22
Nodes (3): main(), main(), yaw_of()

### Community 87 - "Paint Level Sensor Config"
Cohesion: 0.22
Nodes (9): active_low, bit, enabled, auto_manual, paint_level_ok, active_low, bit, enabled (+1 more)

### Community 88 - "PCA Direction Angle Utils"
Cohesion: 0.22
Nodes (5): abs_line_angle_diff_deg(), debug_segment_geometry(), pca_direction_angle(), point_line_distance(), split_one_segment_by_line_deviation()

### Community 90 - "LiDAR Robot Frame Diagram"
Cohesion: 0.43
Nodes (8): Four-Wheeled Differential/Skid-Steer Robot Base, Front Arc: 0 deg +/- 30 deg (Total 60 deg), LiDAR 360 Degree Scan Boundary, LiDAR Robot Frame Top-View Diagram, Right Arc: 270 deg +/- 45 deg (Total 90 deg), Robot Frame Angle Convention (0 deg = +X forward, CCW positive), X Axis (Forward), Y Axis (Left)

### Community 91 - "LiDAR Arc Zones Diagram"
Cohesion: 0.57
Nodes (8): Angle Convention (counter-clockwise increasing), Front Arc Detection Zone (0 deg +/- 30 deg, 60 deg total), LiDAR Scan Range (360 degree dotted circle), Right Arc Detection Zone (270 deg +/- 45 deg, 90 deg total), Robot Chassis (wheeled base, top view), Robot Top-View Coordinate & LiDAR Arc Diagram, X Axis (Front, 0 degrees), Y Axis (Left, 90 degrees)

### Community 92 - "Stanley Sim Output Plot"
Cohesion: 0.39
Nodes (8): FOLLOW Mode, Angle Error per Cycle (heading tracking), Simulation Parameters (kd=2.5, kt=1.0, lidar_offset=195mm, drift=+8.0mm/step), Stanley Path-Tracking Controller, Stanley STEP_REALIGN Simulation Plot, STEP_REALIGN Mode, Distance Error per Cycle (wall offset tracking), Wall-Following Navigation (painting_robot_navigation)

### Community 94 - "Bump Room Strokes Plot"
Cohesion: 0.48
Nodes (7): Bump-Out Painting Sequence (overall algorithm/process), Bump Room Strokes Plot (126 strokes, 19 skipped, 8 overlap pairs), Overlapping Stroke Points, Robot Path (Odometry Trace), Room Obstacles / Furniture (dark gray and orange blocks), Skipped Strokes (19 total), Stroke (Spray Head) Points

### Community 95 - "External Turn Geometry Diagram"
Cohesion: 0.71
Nodes (7): External Turn Diagram, 0.10m Offset Margin from Vertex, Turn Radius R=0.80m Path, Turn Radius R=0.90m Path, Robot Body (at Turn Axis), Turn Axis (Start Point), Wall Vertex (0,0)

### Community 96 - "Sketch Layout Dimensions"
Cohesion: 0.48
Nodes (7): Bump-out Wall Geometry (0.9m / 4.0m / 0.7m segments, 0.15m thick, 3.0m tall), Sketch Layout Dimensions (sketch_layout.world top view), Origin Reference Point (0,0) with 0.575m offset, Overall Layout Dimensions (5.6m width x 10.0m length, wall centrelines), Pillar Obstacle (0.46m wide, 0.165m gap from wall, unattached), Robot Spawn Point (4.618, -8.0), yaw 90 degrees (north), sketch_layout.world (Gazebo world file)

### Community 99 - "Send IO Packet Script"
Cohesion: 0.48
Nodes (4): build_io_packet(), crc16_modbus(), describe(), main()

### Community 101 - "Bump Depth Circles Diagram"
Cohesion: 0.80
Nodes (6): 1.00m Box, Same Small Circles (R1=0.60, R2=0.30, phi=96deg) - Robot Points Backward Failure, 1.00m Box, Bigger 2nd Circle (R1=0.60, R2=0.55, phi=83deg) - Fix, Bump Depth Circles Diagram, Sideways Shift Formula: (R1+R2)*(1-cos(phi)), 0.70m Box, Small Circles (R1=0.65, R2=0.30, phi=75deg), Turn Radius Parameters R1/R2 for Bump-Out Path Planning

### Community 102 - "Paint Quality Spray Angle Plot"
Cohesion: 0.53
Nodes (5): Incidence Angle Classification (good/ok/bad/none), Painting Robot Spray Trajectory (perimeter path), Room Floor Plan with Bump-outs and Obstacles, Spray Angle on Wall Plot (per stroke), Stroke Count Summary (good 90, ok 0, bad 30, none 6)

### Community 103 - "Stroke Redundancy Gate Fix"
Cohesion: 0.33
Nodes (4): _stroke_redundant_pose(), painting_robot_hmi/.../logging_node.py (user's own edit), stroke_is_redundant(), WallAlignHandler ITEM_COMPLETE stroke-skip logic

### Community 104 - "Combined Arc RANSAC Fit"
Cohesion: 0.33
Nodes (4): extract_combined_arc(), _pipeline_fits(), segment_points(), split_segments_by_line_deviation()

### Community 105 - "Just-Bump-Out Dimensions Diagram"
Cohesion: 0.70
Nodes (5): just_bump_out_dimensions.png (Bump-Out Dimensions Diagram), just_bump_out.world (Gazebo World File), Pillar Obstacle (center 5.055, -5.575; size 0.46 x 0.9; gap 0.24m to wall), Robot Spawn Point (4.618, -8.0, yaw 90 deg north), Bump-Out Wall (thickness 0.15m, height 3.0m, centreline length 10.0m)

### Community 110 - "Run-With-Log Script"
Cohesion: 0.50
Nodes (3): PYTHONUNBUFFERED, RCUTILS_CONSOLE_OUTPUT_FORMAT, run_with_log.sh script

### Community 111 - "Sim Time Config"
Cohesion: 0.50
Nodes (3): controller_manager, ros__parameters, use_sim_time

### Community 112 - "Gazebo Params Config"
Cohesion: 0.50
Nodes (3): gazebo, ros__parameters, publish_rate

### Community 113 - "IO Map: Buzzer Config"
Cohesion: 0.50
Nodes (4): bit, enabled, type, buzzer

### Community 114 - "IO Map: Ceiling Detect Config"
Cohesion: 0.50
Nodes (4): active_low, bit, enabled, ceiling_detect

### Community 115 - "IO Map: E-Stop Limits Config"
Cohesion: 0.50
Nodes (4): emg_limits, active_low, bit, enabled

### Community 116 - "IO Map: E-Stop Config"
Cohesion: 0.50
Nodes (4): estop, active_low, bit, enabled

### Community 117 - "IO Map: Lower Limit Config"
Cohesion: 0.50
Nodes (4): lower_limit, active_low, bit, enabled

### Community 118 - "IO Map: On/Off Config"
Cohesion: 0.50
Nodes (4): on_off, active_low, bit, enabled

### Community 119 - "IO Map: Pause/Resume Config"
Cohesion: 0.50
Nodes (4): pause_resume, active_low, bit, enabled

### Community 120 - "IO Map: Relay Status Config"
Cohesion: 0.50
Nodes (4): relay_status, active_low, bit, enabled

### Community 121 - "IO Map: Upper Limit Config"
Cohesion: 0.50
Nodes (4): upper_limit, active_low, bit, enabled

### Community 122 - "IO Map: Safety Relay Config"
Cohesion: 0.50
Nodes (4): safety_relay, bit, enabled, type

### Community 123 - "IO Map: Tower Amber Config"
Cohesion: 0.50
Nodes (4): tower_amber, bit, enabled, type

### Community 124 - "IO Map: Tower Green Config"
Cohesion: 0.50
Nodes (4): tower_green, bit, enabled, type

## Ambiguous Edges - Review These
- `Door/Window Zone (orange rectangles)` → `Bump-out Painting Sequence Planner`  [AMBIGUOUS]
  docs/bump_room_strokes_pose.png · relation: conceptually_related_to
- `/state_machine_node` → `/wall_detection_node`  [AMBIGUOUS]
  docs/diagrams/paintbott_P1.png · relation: conceptually_related_to
- `/state_machine_node` → `/wall_detection_node`  [AMBIGUOUS]
  docs/diagrams/rosgraph.svg · relation: conceptually_related_to
- `Recoverable HOLD (Stop and preserve queue; RESUME retries item)` → `FAULT / ESTOP (Stop and flush queue)`  [AMBIGUOUS]
  docs/robot_workflow.svg · relation: conceptually_related_to
- `wall_dist FAULT` → `Corner Recipes (turn right, drive along rear face, turn left back onto wall)`  [AMBIGUOUS]
  docs/suckin_vs_two_corners.png · relation: conceptually_related_to

## Knowledge Gaps
- **60 isolated node(s):** `RCUTILS_CONSOLE_OUTPUT_FORMAT`, `PYTHONUNBUFFERED`, `Painting Robot (README)`, `docs/robot_workflow.png (workflow diagram)`, `sketch_layout.world` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 880 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **85 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LeadshineMotor` connect `Leadshine Motor Driver` to `Leadshine Standalone Script`, `Leadshine TODO: Clear Alarm`, `Leadshine TODO: Disable`, `Leadshine TODO: Enable`, `Base Drive Kinematics`, `Leadshine TODO: Read Alarm`, `Leadshine TODO: Read Velocity`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `StateMachineNode` (e.g. with `MotionQueue` and `CornerApproachHandler`) actually correct?**
  _`StateMachineNode` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `RCUTILS_CONSOLE_OUTPUT_FORMAT`, `PYTHONUNBUFFERED`, `Painting Robot (README)` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `HMI Logging Node` be split into smaller, more focused modules?**
  _Cohesion score 0.0746606334841629 - nodes in this community are weakly interconnected._
- **Why does `StateMachineNode` connect `FSM Safety & Collision` to `FSM Corner Logic Handler`, `FSM State Handlers`, `FSM Motion Queue`, `State Machine & Safety Monitor`, `FSM Motion Queue Display`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Door/Window Zone (orange rectangles)` and `Bump-out Painting Sequence Planner`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `/state_machine_node` and `/wall_detection_node`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._