---
ID: UBH-003
validation_status: statically confirmed
severity: medium
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: EtherCAT-原始关节指令无钳位
---
# UBH-003 E2 · Raw EtherCAT Joint Commands Without Safety Clamping

## 1. Summary

- Impact: **Critical in the source report** — the raw servo-command topic carries CSP/CSV/CST control modes and target position/velocity/torque values for 50 joints without an independent server-side safety clamp.
- The topic and live RL-controller traffic were observed; unsafe command publication was intentionally not performed.

## 2. Affected Products and Versions

- Component: motion-board EtherCAT master node `ubt_ethercat_master`.
- ROS 2 topic: `/ecat/servo/cmd` using `ecat_task_msgs/msg/ServoCmdArray`.
- The topic appears in the runtime ROS graph when the motion stack is active.

## 3. Validation Status

`statically confirmed` with live read-only topic evidence. No malicious joint command was published.

## 4. Attack Preconditions

An attacker must obtain publish access to the robot's ROS/DDS control graph, for example through another exposed bridge or an existing foothold. Verification should remain read-only unless the robot is safely suspended and emergency-stop controls are in place.

## 5. Root Cause

The low-level servo command interface accepts raw position, velocity, torque, and operating-mode values without enforcing independent bounds at the EtherCAT command boundary.

## 6. Attack Procedure

The retained probe subscribes to the topic and records real controller traffic to establish message structure and reachability. The danger mode constructs an out-of-range example but does not publish it.

## 7. Impact

A publisher with access to this topic could interfere with the normal controller by supplying extreme torque or position values, potentially causing joint overtravel, loss of balance, or other unsafe motion.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The committed probe only subscribes to `/ecat/servo/cmd`.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Enforce hard position, velocity, torque, acceleration, and mode limits below the ROS publisher boundary.
- Authenticate/authorize publishers to safety-critical DDS topics.
- Add watchdogs and arbitration between high-level controllers and raw servo commands.
- Add regression tests for out-of-range and conflicting commands.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review safety evidence and vendor-coordination status.

## 13. Sanitized Original Research Body

# E2 · Raw EtherCAT Joint Commands Without Safety Clamping

| Item | Value |
|---|---|
| Component | Motion-board EtherCAT master node `ubt_ethercat_master` |
| Topic | `/ecat/servo/cmd` (`ecat_task_msgs/msg/ServoCmdArray`) |
| Impact | **Critical in the source report** — raw CSP/CSV/CST commands plus target position/velocity/torque for 50 joints are accepted without an independent clamp |
| Source | `report_motion.md` (E2) |
| Re-verification | 🟢 Topic/service present in the runtime graph; robot was in STANDBY during the retained review |

## Vulnerability Mechanism

`/ecat/servo/cmd` carries a raw control-word array for 50 joints, including CSP/CSV/CST operating modes and target position, velocity, torque, acceleration, and deceleration fields.

The source analysis found no independent bound enforcement at this service boundary. The normal RL gait controller itself publishes to the same interface. If an attacker obtains publish authority through an exposed DDS/bridge path or prior compromise, conflicting or extreme values could reach the servo layer.

Potential outcomes include:

- excessive torque requests;
- positions outside mechanical operating limits;
- interference with the normal RL control stream, causing instability or falls.

## Reproduction Script

`scripts/exploit_servo_cmd.py`

- Default safe mode subscribes to `/ecat/servo/cmd` and records authentic RL-controller traffic.
- `--danger` only constructs and prints an extreme 50-joint test message; it does not publish it.
- `--n` limits the number of observed messages.

## Evidence Output

- Real command-array examples with operating mode and target fields.
- Topic type and array structure.
- Session logs under `evidence/`.

## Safety Boundary

⚠️ The retained script never publishes to the topic. Any active test would require a safely suspended robot, emergency-stop readiness, and explicit human approval.
