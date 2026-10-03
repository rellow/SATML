---
ID: R1-038
validation_status: statically confirmed
severity: high
disclosure_status: internal research
attack_chains:
  []
related_ai_sessions:
  - CC-R1-001
  - CC-R1-002
---

# R1-038 demarcate Emergency-Stop Rebinding

## 1. Summary

demarcate Emergency-Stop Rebinding. The code path and root cause are confirmed, but an unambiguous physical-device closed loop has not yet been completed.

## 2. Affected Products and Versions

Unitree R1; primary research baseline: firmware 1.4.2.

## 3. Validation Status

`statically confirmed`.Migration decision: explicitly state the internal-network/bridge-allowlist precondition.

## 4. Attack Preconditions

The attacker must have reached the robot's local system, internal eth0 bus, or an equivalent post-compromise position.

## 5. Root Cause

The source material identifies the core security issue as demarcate Emergency-Stop Rebinding; the root cause lies in inadequate input trust-boundary enforcement, privilege separation, or security-state validation.

## 6. Attack Procedure

1. Reach the entry point described by the report and satisfy the stated preconditions.
2. Use the minimal probe from the sanitized reproduction manifest to exercise the target code path.
3. Collect only non-destructive evidence such as status codes, process restarts, a minimal file marker, or `id`.
4. Immediately perform cleanup and verify that services and configuration have been restored.

`refuted`项目的“攻击过程”仅指原假设的验证过程，不表示存在可利用攻击路径.

## 7. Impact

May alter robot motion or safety state, creating physical-safety risk, denial of service, or loss of control.

## 8. Reproduction

The `复现/材料清单.md` file records screened scripts or their external storage locations. All parameters must use placeholders or experiment environment variables; real serial numbers, passwords, tokens, cookies, private keys, and cloud credentials are prohibited. For dynamically validated findings, prefer the smallest non-destructive command and clean up immediately afterward.

## 9. Supporting Evidence

See `证据/材料清单.md` for the evidence index. Source material: `AUD-demarcate-estop-rebind`.Large or sensitive evidence that is not committed is recorded centrally in `材料清单/未提交材料.csv` at the repository root.

## 10. Recommendations

- Enforce strong authentication, fine-grained authorization, message-integrity validation, and replay protection at the entry point.
- Apply allowlists and strict validation to lengths, indices, paths, state transitions, and target resources.
- 将high风险服务降权并建立进程、文件系统和网络边界；
- Remove hard-coded or shared credentials, rotate exposed material, and add security-audit logging.
- Add automated regression tests and negative test cases for this vulnerability.

## 11. Related AI Sessions

- [CC-R1-001](../../../../AI轨迹/会话索引.md#cc-r1-001)
- [CC-R1-002](../../../../AI轨迹/会话索引.md#cc-r1-002)


## 12. Disclosure Record

- 当前披露状态：internal research.
- Before external disclosure, re-review the evidence, reproducibility, and vendor-coordination status according to `SECURITY.md`.
