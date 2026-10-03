---
ID: GAL-012
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: ZMQ5555未授权RPC运动控制
---
# GAL-012 Galileo ZMQ 5555 Unauthenticated RPC Motion-Control Surface

## 1. Summary

The Galileo middleware exposes a ZeroMQ RPC backend on `tcp://*:5555` using the default NULL security mechanism and a broad service/method registration policy. Reverse engineering recovered the wire format and 19 method names, including control-mode, policy, stand/down/passive, real-time motion, battery, and GPS methods. An unauthenticated ZMTP/NULL connection was accepted during testing; high-impact motion calls were not exercised in routine validation.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: hermesmm RPC backend in `libhermesmmSdk.so`, loaded by monitor_manager.
- Listener: `tcp://*:5555`.

## 3. Validation Status

`statically confirmed` for the command/control impact, with live confirmation that the unauthenticated ZMTP/NULL connection is accepted and instruction-level recovery of the RPC framing.

## 4. Attack Preconditions

The attacker needs TCP reachability to port 5555. Motion-changing calls must be tested only on a safely restrained robot.

## 5. Root Cause

The RPC server binds to all interfaces without transport authentication and broadly exposes registered service methods. Safety-critical methods rely on internal control-mode state rather than an authenticated caller identity; the control-mode setter itself is exposed through the same unauthenticated RPC surface.

## 6. Attack Procedure

The retained implementation performs the ZMTP NULL handshake and can use read-only RPC methods. The source analysis also reconstructs control methods, but the English report does not duplicate ready-to-run motion/soft-stop invocation strings.

## 7. Impact

- Unauthenticated access to robot RPC methods.
- Potential control-mode takeover and policy/task switching.
- Potential stand/down/passive and real-time motion commands.
- Read-only battery/GPS disclosure.
- An independent motion-control entry point from UDP 10086 and multicast LCM.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Routine validation should use read-only methods only.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Enable authenticated ZeroMQ security such as CURVE with server/client key allowlists.
- Bind RPC only to an intended management interface if remote access is unnecessary.
- Register a narrow allowlist of methods rather than wildcard service names.
- Require authenticated, signed requests for high-impact motion/state changes.
- Add rate limiting and audit logs.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo ZMQ 5555 Unauthenticated RPC Motion-Control Surface

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | hermesmm RPC backend / `libhermesmmSdk.so` |
| Listener | `tcp://*:5555` |
| Security Mechanism | ZMTP NULL; no application authentication identified |
| Validation | Framing/method recovery + live unauthenticated handshake; motion calls not exercised |

## Vulnerability Overview

The hermesmm middleware exposes a ZeroMQ request/response service. Configuration binds it to all interfaces and originally allowed wildcard service-function registration. The analysis found no CURVE/PLAIN or application-level authentication mechanism.

The recovered text request format is:

```
<sequence>:<method-name>:<payload>
```

The method table includes:

- set/get robot control mode;
- set/get policy state;
- stand up/down and passive;
- real-time motion control;
- motion status;
- battery/charge status;
- GPS altitude/latitude/longitude/satellite/speed/validity.

The motion-control consumers forward accepted requests into internal data/LCM control channels.

## Important Control-Gate Observation

Some control operations require the current control mode to equal `GalileoClientSdkControl`. The source analysis found that `SetRobotControlMode` is itself available through the same RPC surface, so this is a state gate rather than caller authentication.

## Live/Static Evidence

- ZMTP greeting and NULL security handshake were accepted by the real service.
- Instruction-level analysis recovered colon-delimited parsing.
- Nineteen method strings were independently confirmed.
- No authentication string/path was identified in the relevant library.

## Safe Reproduction

Use a read-only method such as querying current control mode or battery status. Do not invoke passive, policy, or real-time motion methods unless physical safety controls are in place.

## Evidence

- `evidence/wire格式还原与验证_20260829.md`
- `evidence/hermesmm.yaml`
- `evidence/strings_symbols.txt`
- cross-static-validation notes
