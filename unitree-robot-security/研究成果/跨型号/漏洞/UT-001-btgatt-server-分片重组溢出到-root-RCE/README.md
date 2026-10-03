---
ID: UT-001
validation_status: dynamically confirmed
severity: critical
disclosure_status: internal research
attack_chains:
  - UT-CHAIN-001
related_ai_sessions:
  - CC-GO2-002
  - CC-R1-002
---

# UT-001 btgatt-server Fragment-Reassembly Overflow to Root RCE

## 1. Summary

A fragment-reassembly overflow in btgatt-server reaches root RCE. The conclusion is supported by closed-loop evidence from physical devices or live services.

## 2. Affected Products and Versions

Unitree GO2 Air stock firmware 1.1.15 and R1 firmware 1.4.2; conclusions are recorded separately for each model.

## 3. Validation Status

`dynamically confirmed`. Migration decision: the two source reports were merged; GO2 and R1 reproduction/evidence material remains separated by model, and the original `aes_key.bin` is not committed.

## 4. Attack Preconditions

The attacker must be within BLE radio range. Steps that require session material are identified separately in the reproduction documentation.

## 5. Root Cause

Attacker-controlled lengths or indices are not validated against the destination-buffer boundary before a read or write.

## 6. Attack Procedure

1. Reach the entry point described by the report and satisfy the stated preconditions.
2. Use the minimal probe from the sanitized reproduction manifest to exercise the target code path.
3. Collect only non-destructive evidence such as status codes, process restarts, a minimal file marker, or `id`.
4. Immediately perform cleanup and verify that services and configuration have been restored.

For `refuted` items, the attack procedure describes validation of the original hypothesis only; it does not imply that an exploitable path exists.

## 7. Impact

Successful exploitation can execute commands in a high-privilege robot service context and may result in complete device compromise.

## 8. Reproduction

The `复现/材料清单.md` file records screened scripts or their external storage locations. All parameters must use placeholders or experiment environment variables; real serial numbers, passwords, tokens, cookies, private keys, and cloud credentials are prohibited. For dynamically validated findings, prefer the smallest non-destructive command and clean up immediately afterward.

## 9. Supporting Evidence

See `证据/材料清单.md` for the evidence index. Source material consists of the same-origin GO2 and R1 evidence sets. Large or sensitive evidence that is not committed is recorded centrally in `材料清单/未提交材料.csv` at the repository root.

## 10. Recommendations

- Enforce strong authentication, fine-grained authorization, message-integrity validation, and replay protection at the entry point.
- Apply strict length and index validation against the actual destination buffer.
- Drop privileges for high-risk services and establish process, filesystem, and network boundaries.
- Remove hard-coded or shared credentials, rotate exposed material, and add security-audit logging.
- Add automated regression tests and negative test cases for this vulnerability, including fragmented BLE inputs.

## 11. Related AI Sessions

- [CC-GO2-002](../../../../AI轨迹/会话索引.md#cc-go2-002)
- [CC-R1-002](../../../../AI轨迹/会话索引.md#cc-r1-002)

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review the evidence, reproducibility, and vendor-coordination status according to `SECURITY.md`.
