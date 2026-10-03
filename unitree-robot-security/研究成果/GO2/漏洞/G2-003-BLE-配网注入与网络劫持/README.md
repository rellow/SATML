---
ID: G2-003
validation_status: candidate
severity: high
disclosure_status: internal research
attack_chains:
  - GO2-CHAIN-002
related_ai_sessions:
  - CC-GO2-001
---

# G2-003 BLE provisioning injection and network hijacking

## 1. Summary

BLE provisioning injection and network hijacking。当前仅有candidate线索或关键运行时条件尚未确认。

## 2. Affected Products and Versions

Unitree GO2 Air; primary research baseline: stock firmware 1.1.15.

## 3. Validation Status

`candidate`。Migration decision: 保留待真机闭环限制。

## 4. Attack Preconditions

攻击者需要处于 BLE 近场范围；需要会话材料的步骤已在复现说明medium单独标注。

## 5. Root Cause

The source material identifies the core security issue as“BLE provisioning injection and network hijacking”; the root cause lies in inadequate input trust-boundary enforcement, privilege separation, or security-state validation.

## 6. Attack Procedure

1. Reach the entry point described by the report and satisfy the stated preconditions;
2. 使用脱敏复现清单medium的最小探针触发目标代码路径；
3. Collect only non-destructive evidence such as status codes, process restarts, a minimal file marker, or `id`;
4. Immediately perform cleanup and verify that services and configuration have been restored.

For `refuted` items, the “attack procedure” describes validation of the original hypothesis only; it does not imply that an exploitable path exists.

## 7. Impact

May alter robot motion or safety state, creating physical-safety risk, denial of service, or loss of control.

## 8. Reproduction

The `复现/材料清单.md` file in this directory records the screened scripts or their external storage locations. All parameters must use placeholders or experiment environment variables; real serial numbers, passwords, tokens, cookies, private keys, and cloud credentials are prohibited. For dynamically validated findings, prefer the smallest non-destructive command and clean up immediately afterward.

## 9. Supporting Evidence

See `证据/材料清单.md` for the evidence index. 源材料：`Go2_BLE配网注入劫持网络`。Large or sensitive evidence that is not committed is recorded centrally in `材料清单/未提交材料.csv` at the repository root.

## 10. Recommendations

- Enforce strong authentication, fine-grained authorization, message-integrity validation, and replay protection at the entry point;
- Apply allowlists and strict validation to lengths, indices, paths, state transitions, and target resources;
- 将high风险服务降权并建立进程、文件系统和网络边界；
- Remove hard-coded or shared credentials, rotate exposed material, and add security-audit logging;
- Add automated regression tests and negative test cases for this vulnerability.

## 11. Related AI Sessions

- [CC-GO2-001](../../../../AI轨迹/会话索引.md#cc-go2-001)


## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review the evidence, reproducibility, and vendor-coordination status according to `SECURITY.md`.
