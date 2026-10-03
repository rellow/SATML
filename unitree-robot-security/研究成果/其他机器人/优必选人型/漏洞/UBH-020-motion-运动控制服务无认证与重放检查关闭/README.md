---
ID: UBH-020
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: motion-运动控制服务无认证与重放检查关闭
---
# UBH-020 E4/E5 · Unauthenticated Motion-Control Services and Disableable Replay Checks

## 1. Summary

The motion stack exposes lifecycle/control services without a caller-authentication boundary, and a separate service can disable command-timestamp validation. Together, these properties weaken both authorization and replay protection on safety-relevant motion control.

## 2. Affected Products and Versions

- Component: motion-board control stack such as `rosa_control_node`.
- Representative services include `/mc/sdk/start_ecat`, `/mc/sdk/start_mc`, `/mc/sdk/robot_command`, and `/mc/sdk/disable_check_command_stamp`.
- The retained verification enumerates the services without changing robot state.

## 3. Validation Status

`statically confirmed` with live service enumeration. State-changing calls were intentionally not performed.

## 4. Attack Preconditions

The attacker must have access to the ROS/DDS service graph or an exposed bridge. Dynamic testing requires a suspended robot or other physical safety controls.

## 5. Root Cause

Motion lifecycle and command operations are reachable without per-caller authorization, and the command-age/replay safeguard itself can be disabled through a service call.

## 6. Attack Procedure

The safe probe enumerates the `/mc/sdk/*` interface surface and associated topics. It can display the replay-check-disable request but does not send it.

## 7. Impact

A caller with ROS/DDS access could potentially start or interfere with the motion stack and weaken freshness checks, making stale or replayed commands more likely to be accepted.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The committed probe is enumeration-only.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Authenticate and authorize all motion lifecycle/control services.
- Make replay/freshness validation mandatory rather than remotely disableable in normal operation.
- Separate maintenance-only controls from runtime interfaces.
- Add command sequencing, freshness, and rate-limit checks below bridge layers.
- Audit all changes to safety-control settings.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# E4/E5 · Unauthenticated Motion-Control Services and Disableable Timestamp Replay Checks

| Item | Value |
|---|---|
| Component | Motion-board control stack (`rosa_control_node`, etc.) |
| Services | `/mc/sdk/start_ecat`, `/mc/sdk/start_mc`, `/mc/sdk/robot_command`, `/mc/sdk/disable_check_command_stamp`, and related interfaces |
| Impact | **High** — control services lack caller authentication, and command timestamp checking can be disabled |
| Source | `report_motion.md` (E4, E5) |

## Vulnerability Mechanism

- **E4:** motion lifecycle and command services do not visibly authenticate the caller at the service boundary.
- **E5:** `/mc/sdk/disable_check_command_stamp` can disable timestamp validation that normally rejects stale/replayed commands.

Once that check is disabled, old commands are no longer constrained by the same freshness window, increasing the risk that stale input can interfere with current control state.

The source report notes that an exposed ROS/DDS bridge can therefore compose with these interfaces to create unauthorized motion-control authority.

## Reproduction Script

`scripts/exploit_motion_svc.py`

- Default safe mode enumerates `/mc/sdk/*` services and relevant control topics.
- The danger mode only displays the request that would disable timestamp checking; it does not transmit it.

## Evidence Output

- Registered `/mc/sdk/*` service set.
- Topic and message-type information.
- Call timing/response metadata for safe enumeration.
- Supporting logs under `evidence/`.

## Safety Boundary

⚠️ `start_ecat`, `start_mc`, `robot_command`, and replay-check configuration can alter robot motion state. The retained validation does not call them. Any dynamic test requires physical safety controls.
