---
ID: G2-012
validation_status: statically confirmed
severity: medium
disclosure_status: internal research
attack_chains:
  []
related_ai_sessions:
  - CC-GO2-001
---

# G2-012 Credentials Written to Disk in Cleartext Logs

## 1. Summary

Credentials Written to Disk in Cleartext Logs. The code path and root cause are confirmed, but an unambiguous physical-device closed loop has not yet been completed.

## 2. Affected Products and Versions

Unitree GO2 Air; primary research baseline: stock firmware 1.1.15.

## 3. Validation Status

`statically confirmed`.Migration decision: retain only fully sanitized field-level evidence.

## 4. Attack Preconditions

The attacker must be able to reach the network, protocol, or service entry point described in the report; practical reachability is bounded by the validation status for this model.

## 5. Root Cause

Long-lived credentials are hard-coded, shared, recorded in cleartext, or incorrectly bound to device identity, causing the secret boundary to fail.

## 6. Attack Procedure

1. Reach the entry point described by the report and satisfy the stated preconditions.
2. Use the minimal probe from the sanitized reproduction manifest to exercise the target code path.
3. Collect only non-destructive evidence such as status codes, process restarts, a minimal file marker, or `id`.
4. Immediately perform cleanup and verify that services and configuration have been restored.

For `refuted` items, the attack procedure describes validation of the original hypothesis only; it does not imply that an exploitable path exists.

## 7. Impact

May enable impersonation, cloud-resource abuse, or provide authentication material for later attack chains.

## 8. Reproduction

The `复现/材料清单.md` file records screened scripts or their external storage locations. All parameters must use placeholders or experiment environment variables; real serial numbers, passwords, tokens, cookies, private keys, and cloud credentials are prohibited. For dynamically validated findings, prefer the smallest non-destructive command and clean up immediately afterward.

## 9. Supporting Evidence

See `证据/材料清单.md` for the evidence index. Source material: 未动态闭环 09.Large or sensitive evidence that is not committed is recorded centrally in `材料清单/未提交材料.csv` at the repository root.

## 10. Recommendations

- Enforce strong authentication, fine-grained authorization, message-integrity validation, and replay protection at the entry point.
- Apply allowlists and strict validation to lengths, indices, paths, state transitions, and target resources.
- Drop privileges for high-risk services and establish process, filesystem, and network boundaries.
- Remove hard-coded or shared credentials, rotate exposed material, and add security-audit logging.
- Add automated regression tests and negative test cases for this vulnerability.

## 11. Related AI Sessions

- [CC-GO2-001](../../../../AI轨迹/会话索引.md#cc-go2-001)


## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review the evidence, reproducibility, and vendor-coordination status according to `SECURITY.md`.
