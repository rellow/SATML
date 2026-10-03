---
ID: GAL-017
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: vis模型WebSocket13140未授权关节控制-1
---
# GAL-017 Galileo Visualization WebSocket 13140 Unauthenticated Joint/Motor Control

## 1. Summary

The `robot_urdf_web` visualization backend exposes an unauthenticated WebSocket service on port 13140. Static analysis and downstream-consumer validation show that specific `robot.joint` commands publish real HAL-consumed motor-enable and joint-zero messages. The same interface also permits lidar runtime-configuration changes. A separate velocity-command path was initially suspected to control locomotion but was later **refuted for the tested firmware** because its shared-memory topic has no consumer.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: `galileo-robot-vis/bin/robot_urdf_web`, websocketpp server on port 13140.
- Frontend connects directly to `ws://<host>:13140`.

## 3. Validation Status

`statically confirmed` for the joint/motor and lidar control paths. Live high-impact motor-disable/joint-zero commands were not executed during routine validation.

## 4. Attack Preconditions

The attacker must reach TCP 13140. Any live joint/motor test requires a safely restrained robot and immediate recovery capability.

## 5. Root Cause

The WebSocket command channel has no authentication, origin/source validation, or rate limiting before dispatching high-impact joint-control and configuration messages into internal shared-memory topics.

## 6. Attack Procedure

An unauthenticated client sends a JSON command frame selecting the joint-control domain. The dispatcher translates commands such as motor enable/disable or joint-zero into HAL-consumed shared-memory messages.

## 7. Impact

- Unauthorized disabling of all joint motors, creating a fall/loss-of-control risk if the robot is active.
- Unauthorized joint-zero operations that can disrupt calibration.
- Lidar runtime-configuration tampering that can affect navigation/avoidance.
- **Not claimed:** direct locomotion-speed control through the analyzed `hw_user_command` path, because no consumer was found in the tested image.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Routine verification should stop at connection/schema inspection; do not issue motor-disable or joint-zero actions without physical safety controls.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Authenticate WebSocket clients and enforce origin/source policy.
- Bind the service to localhost or a dedicated management interface where possible.
- Require explicit authorization and safety-state checks for motor/joint commands.
- Remove dead/unconsumed control paths from production builds.
- Rate-limit and audit high-impact commands.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo Visualization WebSocket 13140 Unauthenticated Joint/Motor Control

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | `robot_urdf_web` |
| Interface | WebSocket TCP 13140 |
| Type | Unauthenticated command channel |
| Confirmed Control | Motor enable/disable, joint zeroing, lidar configuration |
| Refuted Control | Direct locomotion speed through `hw_user_command` on the tested firmware |

## Vulnerability Mechanism

The visualization backend accepts JSON command frames with fields such as protocol version, domain, function code, frame ID, timestamp, response type, and payload.

For the `robot.joint` command family, analysis identified operations that publish:

- motor-enable state to `hw_robot_joint_enable_ctrl`;
- joint-zero commands to `hw_joint_zeropos_set`.

The HAL configuration subscribes to both topics, establishing a real consumer path.

The interface also accepts lidar runtime configuration through a sensor-domain command.

## Important Corrected Boundary

A `robot.motion` path writes `UserCommandData` to `hw_user_command`, but independent review found no consumer of that shared-memory topic in the tested firmware. Therefore the earlier claim that WebSocket 13140 directly controls base velocity is not supported and is excluded.

## Security Chain

```
unauthenticated WebSocket client
        ↓
robot.joint command
        ↓
internal motor-enable / joint-zero SHM topic
        ↓
HAL consumer
        ↓
physical joint-state effect
```

## Evidence

- reverse-engineered `robot_urdf_web` command/router functions;
- frontend WebSocket URL logic;
- HAL `shm_channel.yaml` subscriptions;
- external audit `AUD-vislcm-ws-motion-control.md`.

## Safety Boundary

Do not invoke motor-disable/joint-zero while the robot is bearing weight. A live test requires suspension/restraint and an operator at the emergency stop.
