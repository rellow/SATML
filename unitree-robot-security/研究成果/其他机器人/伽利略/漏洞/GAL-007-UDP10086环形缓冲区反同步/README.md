---
ID: GAL-007
validation_status: statically confirmed
severity: medium
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: UDP10086环形缓冲区反同步
---
# GAL-007 Galileo UDP 10086 Ring-Buffer Desynchronization, Heap Out-of-Bounds Read, and Crash

## 1. Summary

The UDP 10086 packet parser handles an invalid attacker-controlled length by passing `length + 16` to the ring-buffer release routine without clamping it to buffered data. This can underflow the internal used-byte counter, move the read offset beyond the ring's actual capacity, and cause subsequent parsing to read outside the heap buffer. A separate integer-wrap variant can desynchronize parser accounting. The current evidence supports an unauthenticated single-packet remote crash, parser desynchronization, and an out-of-bounds-read primitive; it does **not** establish RCE.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: `libNetworkSdk.so`, specifically `ProcessData` and `HRingBuf::free`.
- Attack surface: any host able to reach UDP 10086.

## 3. Validation Status

`statically confirmed` through instruction-level independent review and external-audit cross-validation.

## 4. Attack Preconditions

The attacker requires only network reachability to UDP 10086. Live crash testing must be limited to a safely stopped, recoverable researcher-owned robot.

## 5. Root Cause

The invalid-length path trusts the unvalidated packet length during ring-buffer bookkeeping. `HRingBuf::free` subtracts the supplied amount from the used-byte count without bounding it and can assign an attacker-derived value to the read offset without constraining it to ring capacity.

## 6. Attack Procedure

A malformed header declares a length outside the valid packet range. Instead of discarding only the header, the parser advances/frees the ring using the attacker-controlled declared length. Later parser iterations operate on corrupted ring state and may read outside the allocated buffer.

## 7. Impact

- Unauthenticated single-packet crash of the monitor/control process.
- Repeatable denial of service.
- Heap out-of-bounds data may enter later command-processing logic, creating information-disclosure potential dependent on heap layout.
- Integer-wrap variants can desynchronize parser state and cause subsequent packets to be misinterpreted.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The retained workflow compares service state before and after a bounded malformed-packet test and includes cleanup/recovery guidance.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Reject invalid lengths before any ring-buffer bookkeeping.
- On malformed packets, consume only bytes that are known to be present.
- Clamp release amounts to the actual used-byte count.
- Keep read offsets modulo/bounded by ring capacity.
- Add parser fuzzing around large, wrapped, and truncated length fields.
- Authenticate or source-restrict UDP 10086.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo UDP 10086 Ring-Buffer Desynchronization, Heap Out-of-Bounds Read, and Crash

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | `libNetworkSdk.so`: `ProcessData` invalid-length path → `HRingBuf::free` |
| Type | Unchecked length corrupts ring-buffer accounting and read offset |
| Attack Surface | UDP 10086, unauthenticated |
| Validation | Independent instruction-level review + external audit |

## Vulnerability Overview

For type-1 packets, `ProcessData` accepts normal lengths only within a bounded range. When the length is invalid, the implementation logs the error but still passes the attacker-derived `length + 16` value to the ring-buffer release routine.

The analyzed `HRingBuf::free` implementation:

- subtracts the amount from the internal `used` counter without a lower bound;
- may set `read_off` directly from the supplied amount;
- does not force the offset back within the approximately `0x2800`-byte ring capacity.

A large declared length can therefore make `used` underflow to a very large unsigned value and place `read_off` far outside the ring. Later checks relying on `used` can then pass incorrectly, and later reads may dereference heap memory outside the ring.

A second variant uses values near the 32-bit wrap boundary so that `length + 16` wraps to a small number, causing the parser's accounting to diverge from the actual bytes consumed.

## Independent Instruction-Level Review

The research independently confirmed:

- a comparison against `0x400` in `ProcessData`;
- the invalid-length path reaching `HRingBuf::free`;
- an unchecked subtraction from `used`;
- attacker-influenced assignment of the read offset.

These observations match the external audit's ring-desynchronization finding.

## Security Consequences

```
malformed UDP header
        ↓
invalid declared length reaches ring-buffer release logic
        ↓
used counter underflow / read offset leaves ring bounds
        ↓
later parser iteration reads outside allocated ring
        ↓
process crash, parser desynchronization, possible heap-data exposure
```

The report intentionally does not promote this to RCE. Exploitability beyond crash/OOB-read depends on additional memory-layout and mitigation conditions.

## Safe Reproduction

The retained tool supports:

- a large-length desynchronization case;
- an integer-wrap case;
- before/after service-status verification.

Testing should be performed only on a stationary, recoverable device.

## Evidence

- `evidence/processdata_dis.txt`
- external audit `AUD-udp-ringbuf-desync.md`
- independent instruction-level validation notes
