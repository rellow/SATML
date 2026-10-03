---
ID: R1-029
validation_status: statically confirmed
severity: high
disclosure_status: internal research
attack_chains:
  []
related_ai_sessions:
  - CC-R1-001
  - CC-R1-002
---

# R1-029 OTA TAR Path Traversal

## 1. Summary

OTA TAR Path Traversal. The code path and root cause are confirmed, but an unambiguous physical-device closed loop has not yet been completed.

## 2. Affected Products and Versions

Unitree R1; primary research baseline: firmware 1.4.2.

## 3. Validation Status

`statically confirmed`.Migration decision: TAR and UPK packages are not committed.

## 4. Attack Preconditions

The attacker must be able to reach the network, protocol, or service entry point described in the report; practical reachability is bounded by the validation status for this model.

## 5. Root Cause

Filenames, paths, or target directories are not adequately canonicalized or allowlisted, allowing attacker-controlled input to reach privileged file operations.

## 6. Attack Procedure

1. Reach the entry point described by the report and satisfy the stated preconditions.
2. Use the minimal probe from the sanitized reproduction manifest to exercise the target code path.
3. Collect only non-destructive evidence such as status codes, process restarts, a minimal file marker, or `id`.
4. Immediately perform cleanup and verify that services and configuration have been restored.

For `refuted` items, the attack procedure describes validation of the original hypothesis only; it does not imply that an exploitable path exists.

## 7. Impact

May compromise the confidentiality, integrity, or availability of robot services and may serve as one stage of a composite attack chain.

## 8. Reproduction

The `复现/材料清单.md` file records screened scripts or their external storage locations. All parameters must use placeholders or experiment environment variables; real serial numbers, passwords, tokens, cookies, private keys, and cloud credentials are prohibited. For dynamically validated findings, prefer the smallest non-destructive command and clean up immediately afterward.

## 9. Supporting Evidence

See `证据/材料清单.md` for the evidence index. Source material: `AUD-ota-tar-traversal`.Large or sensitive evidence that is not committed is recorded centrally in `材料清单/未提交材料.csv` at the repository root.

## 10. Recommendations

- Enforce strong authentication, fine-grained authorization, message-integrity validation, and replay protection at the entry point.
- Apply allowlists and strict validation to lengths, indices, paths, state transitions, and target resources.
- Drop privileges for high-risk services and establish process, filesystem, and network boundaries.
- Remove hard-coded or shared credentials, rotate exposed material, and add security-audit logging.
- Add automated regression tests and negative test cases for this vulnerability.

## 11. Related AI Sessions

- [CC-R1-001](../../../../AI轨迹/会话索引.md#cc-r1-001)
- [CC-R1-002](../../../../AI轨迹/会话索引.md#cc-r1-002)


## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review the evidence, reproducibility, and vendor-coordination status according to `SECURITY.md`.
