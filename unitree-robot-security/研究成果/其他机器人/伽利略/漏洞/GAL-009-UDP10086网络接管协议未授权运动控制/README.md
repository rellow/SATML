---
ID: GAL-009
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: UDP10086网络接管协议未授权运动控制-1
---
# GAL-009 Galileo UDP 10086 Unauthenticated Network-Control Takeover

## 1. Summary

The monitor manager exposes a proprietary remote-control protocol on UDP `0.0.0.0:10086`. The only packet gate is a fixed four-byte magic value embedded in firmware; there is no credential, source authorization, challenge, signature, or replay protection. Dynamic evidence confirms that an unauthenticated packet can change the robot's control mode. Reverse engineering of the same dispatch table shows commands for gait, body posture, translational/yaw velocity, and soft-stop state. Full walking/velocity execution was not exercised during the retained safety-bounded validation.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: `galileo-robot-monitor/lib/libNetworkSdk.so`, loaded by `orrt_monitor_manager_main`.
- Listener: UDP 10086 on all interfaces.
- The path is direct unicast and does not depend on multicast/LCM routing.

## 3. Validation Status

`dynamically confirmed` for unauthenticated control-mode takeover. The broader gait/velocity command surface is supported by high-confidence reverse engineering of the same dispatcher but was not physically driven during routine verification.

## 4. Attack Preconditions

The attacker must be able to send UDP traffic to port 10086. Any live motion test requires a restrained/suspended robot, an operator at the emergency stop, and an isolated network.

## 5. Root Cause

A safety-critical motion-control protocol treats a public constant packet magic as its only acceptance check and lacks authentication, source binding, freshness/replay protection, and operation-specific authorization.

## 6. Attack Procedure

The retained analysis reconstructs the packet framing and command registry. Dynamic testing was limited to a control-mode transition that produced a corresponding robot log entry. The English report intentionally does not duplicate a ready-to-run motion-driving command sequence.

## 7. Impact

- Unauthenticated takeover of the control mode.
- Potential gait/posture and three-axis velocity control through the same command table.
- Soft-stop enable/disable abuse.
- Interference with legitimate joystick/SLAM control.
- Physical-safety impact if motion commands are exercised.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Routine validation should stop after confirming control-mode transition; do not command locomotion unless the physical safety setup is appropriate.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Add cryptographic authentication and integrity protection to every command.
- Use per-session/per-device keys and monotonic sequence numbers to prevent replay.
- Require stronger confirmation for takeover and soft-stop state changes.
- Bind the listener only to the intended control interface and apply source/rate restrictions.
- Enforce independent velocity, acceleration, and state safety limits below the network protocol.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo UDP 10086 Unauthenticated Network-Control Takeover

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | `libNetworkSdk.so` / monitor manager |
| Type | Unauthenticated physical-control protocol |
| Attack Surface | UDP 10086, `0.0.0.0` |
| Dynamic Evidence | Control-mode takeover observed in robot logs |
| Safety Boundary | Full gait/velocity driving not performed during retained validation |

## Vulnerability Overview

The monitor manager implements a phone/app remote-control protocol over UDP. Its acceptance gate is a fixed magic constant available in the firmware. The analysis found no authentication token, signature, challenge-response, serial-number binding, or replay defense.

The packet format contains:

- a fixed magic field;
- command ID;
- either an inline parameter or payload length;
- a type selector;
- optional body data.

The dispatcher registers commands covering:

- stand/lie/walk/balance transitions;
- body-height and attitude adjustment;
- forward, lateral, and yaw velocity;
- normal/stair/creeping/running gait changes;
- policy/control-mode selection;
- soft-stop enable/disable.

Configuration maps control modes including joystick, SLAM, and network-app control.

## Dynamic Evidence

A prior authorized test sent the control-mode command to the owned robot. The monitor log immediately recorded a control-mode transition, confirming that an unauthenticated network-protocol request reached the real control state.

The remaining command table shares the same parser/dispatcher and is strongly supported by reverse engineering, but full locomotion was deliberately left for a physically safe suspended test.

## Security Consequences

```
network host reaches UDP 10086
        ↓
fixed magic passes packet gate
        ↓
unauthenticated control-mode command
        ↓
robot changes active control authority
        ↓
same dispatcher exposes gait/velocity/soft-stop commands
```

Unlike the multicast control paths studied elsewhere, this listener is bound to all interfaces and is directly reachable by unicast from the relevant network.

## Safe Reproduction

For routine verification:

1. confirm the listener;
2. send only a benign/control-mode test on the owned device;
3. correlate with the monitor log;
4. stop before gait/velocity commands unless the robot is safely restrained.

## Evidence

- `evidence/processdata_dis.txt`
- `evidence/init_dis.txt`
- `evidence/cmd_scan.txt`
- monitor log showing the authorized control-mode transition
