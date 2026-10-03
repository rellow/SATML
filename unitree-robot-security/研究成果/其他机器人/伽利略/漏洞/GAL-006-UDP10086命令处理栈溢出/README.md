---
ID: GAL-006
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: UDP10086命令处理栈溢出-1
---
# GAL-006 Galileo UDP 10086 Command-Handler Stack Overflow

## 1. Summary

Several unauthenticated UDP 10086 command handlers pass an attacker-controlled payload length, allowed up to 0x400 bytes, directly to `memcpy` into 4-byte or 16-byte stack locals. The source and independent disassembly confirm stack corruption. In the current evidence, the practical result is an unauthenticated remote crash of the monitor/control process because stack-canary checks fire before a useful return-address overwrite can be exploited. RCE would require an additional information-leak/bypass primitive.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: `libNetworkSdk.so`, loaded by the persistent monitor manager.
- Attack surface: any host able to send UDP packets to port 10086.

## 3. Validation Status

`statically confirmed` through independent disassembly and external-audit cross-validation. The report does not claim a demonstrated RCE.

## 4. Attack Preconditions

The attacker only requires network reachability to UDP 10086. Live crash testing should be done only on a safely stopped/recoverable research robot.

## 5. Root Cause

The dispatcher validates only a generic maximum payload length and forwards that length unchanged to handlers whose local destination buffers are much smaller. Those handlers then use `memcpy(dst, payload, len)`.

## 6. Attack Procedure

A packet selecting one of the affected commands and a payload longer than the handler's local variable corrupts the stack. The retained proof is bounded to crash-level validation and does not attempt control-flow hijacking.

## 7. Impact

- Remote unauthenticated crash/restart of the robot monitor/control process.
- Repeatable denial of service.
- Memory-corruption primitive that may become more severe if combined with an independent disclosure or mitigation bypass.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Keep live tests to the minimum required to demonstrate process failure and recovery.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Enforce per-command exact payload lengths before dispatch.
- Replace attacker-sized copies with fixed-size/checked copies.
- Authenticate/source-restrict the control protocol.
- Preserve stack canaries/PIE and add fuzzing for all command handlers.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo UDP 10086 Command-Handler Stack Overflow

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | `libNetworkSdk.so` |
| Type | Remote stack-buffer overflow |
| Current Demonstrated Impact | Unauthenticated remote crash of `orrt_monitor_manager_main` |
| Attack Surface | UDP 10086 |
| Validation | Independent disassembly + external-audit cross-check |

## Vulnerability Overview

The top-level `ProcessData` logic accepts payload lengths up to `0x400` and passes the original length to command handlers. Several handlers use that value as the size for a stack `memcpy` even though their destinations are only 4 or 16 bytes.

Representative layouts from the analysis:

- translation/turn handlers: 4-byte destination immediately adjacent to the stack canary;
- control/policy mode handlers: 16-byte destination with a larger but still bounded gap to the canary.

A packet containing a sufficiently long payload therefore overwrites the canary and triggers `__stack_chk_fail`, terminating the monitor/control process.

## Honest Exploitability Boundary

The report explicitly limits the current claim to crash-level memory corruption:

- the handler's own canary check runs before a useful overwritten return address can be used;
- saved return state is not directly overwritten in the simplest affected layouts;
- the caller also uses stack-protection;
- the same socket does not provide a known stack-memory disclosure.

Thus **RCE is not demonstrated** and would require an additional primitive.

## Evidence

Independent disassembly confirms:

- generic `0x400` maximum in the dispatcher;
- forwarding of `payload,length` to the selected handler;
- destination addresses/sizes and `memcpy` call sites.

## Safe Reproduction

The retained script can construct affected command frames with a minimally oversized or maximum-sized payload and observe process termination/restart on an owned, stationary device.

## Recommendations

1. Validate exact expected length per command.
2. Use fixed-size copies or safe structured decoding.
3. Authenticate the UDP control protocol.
4. Fuzz all command handlers and retain compiler hardening.

## Evidence Files

- `evidence/processdata_dis.txt`
- `evidence/handler_disassembly.txt`
- external audit `AUD-udp-cmdhandler-stack-smash.md`
