---
编号: R1-014
验证状态: 候选
严重程度: 高
披露状态: 内部研究
所属攻击链:
  []
关联AI会话:
  - CC-R1-001
  - CC-R1-002
---

# R1-014 aisport 配置污染组合链

## 1. 一句话结论

aisport 配置污染组合链.当前仅有候选线索或关键运行时条件尚未确认.

## 2. 影响产品与版本

Unitree R1; primary research baseline: firmware 1.4.2.

## 3. 验证状态

`候选`.迁移裁决：标明写入内容受限.

## 4. 攻击前提

The attacker must be able to reach the network, protocol, or service entry point described in the report; practical reachability is bounded by the validation status for this model.

## 5. 根本原因

源材料确认的核心安全缺陷为“aisport 配置污染组合链”；根因位于输入信任边界、权限分离或安全状态校验不足.

## 6. 攻击过程

1. 到达报告所述入口并满足本节前提；
2. Use the minimal probe from the sanitized reproduction manifest to exercise the target code path.
3. 只采集状态码、进程重启、最小文件标记或 `id` 等无害证据；
4. 立即执行清理步骤，并核验服务与配置已恢复.

`已证伪`项目的“攻击过程”仅指原假设的验证过程，不表示存在可利用攻击路径.

## 7. 实际影响

May compromise the confidentiality, integrity, or availability of robot services and may serve as one stage of a composite attack chain.

## 8. 复现方法

本目录的 `复现/材料清单.md` 记录筛选后的脚本或外部保管位置.所有参数必须使用占位符或实验环境变量；禁止填入真实 SN、密码、Token、Cookie、私钥或云凭据.动态项目优先使用最小无害命令并在完成后清理.

## 9. 支撑证据

See `证据/材料清单.md` for the evidence index. 源材料：`AUD-r3-aisport-config-poison-composition`.Large or sensitive evidence that is not committed is recorded centrally in `材料清单/未提交材料.csv` at the repository root.

## 10. 修复建议

- 在入口处实施强身份认证、细粒度授权、消息完整性校验和重放防护；
- 对长度、索引、路径、状态转换和目标资源使用允许列表；
- Drop privileges for high-risk services and establish process, filesystem, and network boundaries.
- 删除硬编码或共享凭据，轮换已暴露材料，并增加安全审计日志；
- 为本漏洞加入自动化回归测试和负向用例.

## 11. 相关 AI 会话

- [CC-R1-001](../../../../AI轨迹/会话索引.md#cc-r1-001)
- [CC-R1-002](../../../../AI轨迹/会话索引.md#cc-r1-002)


## 12. 披露记录

- 当前披露状态：内部研究.
- 对外披露前必须按 `SECURITY.md` 重新审查证据、复现能力和厂商协调状态.
