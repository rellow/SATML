---
ID: GAL-008
validation_status: dynamically confirmed
severity: medium
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: UDP10086空指针单包DoS
---
# GAL-008 Galileo UDP 10086 Single-Packet NULL-Dereference DoS

## 1. Summary

Two unauthenticated UDP 10086 command handlers invoke the UDP response routine with a null data pointer while selecting a response-encoding path that immediately dereferences that pointer. A header-only packet can therefore crash the monitor/control process. The same command family also exposes a read-only status response containing real-time telemetry, including world-position fields.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: `galileo-robot-monitor/lib/libNetworkSdk.so`.
- Attack surface: UDP 10086 bound to all interfaces.
- Trigger size: a header-only packet; no application payload is required.

## 3. Validation Status

`dynamically confirmed`, with supporting independent instruction-level analysis of the null-dereference path.

## 4. Attack Preconditions

The attacker requires only network reachability to UDP 10086. Live testing must use a safely stopped researcher-owned robot because the crash removes multiple monitor/control interfaces.

## 5. Root Cause

The affected handlers call the UDP send routine with `data = NULL`, `len = 0`, and an encoding mode whose implementation loads through the supplied data pointer without checking it for null.

## 6. Attack Procedure

A header-only request selecting one of the affected command IDs reaches the handler, which passes a null pointer into the response encoder. The encoder dereferences address zero and terminates the monitor process.

## 7. Impact

- Deterministic unauthenticated remote crash/DoS of the monitor manager.
- Loss of multiple services hosted by the process, including UDP 10086, ZMQ 5555, TCP 8888, LCM-related functions, system status, and voice/control surfaces.
- A separate status command returns approximately 169 bytes of telemetry including world-coordinate fields, creating an unauthenticated location/state-disclosure side effect.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Use before/after process and port checks and allow the device to recover before repeating the test.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Null-check response data before dereference.
- Fix the affected handlers to provide a valid response buffer or return an explicit error.
- Authenticate/source-restrict UDP 10086.
- Add regression tests for zero-length/header-only requests to every registered command.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo UDP 10086 Single-Packet NULL-Dereference DoS

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | `libNetworkSdk.so` loaded by monitor_manager |
| Type | NULL-pointer dereference → unauthenticated remote DoS |
| Attack Surface | UDP 10086 |
| Packet Requirement | Header only; no payload |
| Validation | Dynamic confirmation + instruction-level review |

## Vulnerability Overview

The command registry includes small command IDs corresponding to status, laser-point-cloud, and version operations. The laser-point-cloud and version handlers call the UDP response path with a null data pointer.

The response encoder's type-0 path then loads the supplied data pointer and dereferences it without a null check, resulting in a SIGSEGV.

The monitor manager hosts multiple network/control functions, so the crash removes several services at once.

## Instruction-Level Evidence

The research independently confirmed:

1. registration of the affected command IDs;
2. the handlers setting `data = NULL`;
3. transfer into the response encoder;
4. an unconditional load through the null data pointer in the selected encoding branch.

## Telemetry Side Channel

A neighboring status command returns a fixed-size status structure that includes world-position data. This creates an unauthenticated state/location-disclosure surface distinct from the crash.

## Security Consequences

```
unauthenticated UDP request
        ↓
affected handler supplies NULL response data
        ↓
response encoder dereferences NULL
        ↓
monitor_manager terminates
        ↓
multiple network/control interfaces disappear
```

## Safe Reproduction

The retained workflow supports:

- checking current process/port state without sending a packet;
- one bounded crash request on the owned device;
- a read-only status query;
- post-test process/port comparison.

## Evidence

- `evidence/指令级验证_20260829.md`
- external audit `AUD-w2sdk-udp10086-nullderef-dos.md`
- associated monitor/service-state logs
