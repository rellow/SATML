---
编号: UBH-014
验证状态: 候选
严重程度: 高
披露状态: 内部研究
源平台: 优必选人型
源候选目录: executecmd-蓝牙技能system执行
---
# UBH-014 V3 · ExecuteCmd 蓝牙(BT)节点 → `system()` 命令执行

## 1. 一句话结论

- \| 危害 \| **严重** — 技能目录 `/etc/walker/skills/` 宿主可写 → 写技能 = root 命令执行 \|
- - 组合：攻击者（含局域网已有 RCE 者）写一个技能文件 → 触发 ExecuteCmd → root 执行任意命令
- - 即使无 RCE 前置，BLE 广播/配网攻击也可能直达该接口

## 2. 影响产品与版本

- \| 组件 \| vision 板蓝牙控制节点（容器 `walker-system.ae_bt_master`） \|
- \| 复验 \| ⚠️ **现场未复现**：当前镜像 `walker-s2/system:ws2_vision-v0.40.1` 上，宿主与 ae_bt_master 容器内**均无 `/etc/walker/skills` 目录、无 `ExecuteCmd` 字符串**。子代理报告基于静态分析，可能对应其他固件版本 → **降级为待验证** \|
- > 该发现**未能现场确认**，按反误报纪律标记为"静态报告、待新固件/其他代码路径验证"。
- > `ae_bt_master` 实际运行的是 tbox JSON-RPC 服务 `ae_master`（与 cc_api 同框架），
- ## 复现要点（实验环境）

## 3. 验证状态

`候选`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- # V3 · ExecuteCmd 蓝牙(BT)节点 → `system()` 命令执行
- \| 能力 \| `ExecuteCmd` — 对技能文件中的命令直接 `system()` 执行 \|
- 蓝牙控制节点提供 `ExecuteCmd`：读取技能文件并把其中命令交给 `system()`。
- - 蓝牙控制面（手机 APP / BLE 连接）**无认证触发**

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- \| 组件 \| vision 板蓝牙控制节点（容器 `walker-system.ae_bt_master`） \|
- \| 危害 \| **严重** — 技能目录 `/etc/walker/skills/` 宿主可写 → 写技能 = root 命令执行 \|
- 蓝牙控制节点提供 `ExecuteCmd`：读取技能文件并把其中命令交给 `system()`。
- - 蓝牙控制面（手机 APP / BLE 连接）**无认证触发**
- - 组合：攻击者（含局域网已有 RCE 者）写一个技能文件 → 触发 ExecuteCmd → root 执行任意命令
- ## 红线 / 风险

## 8. 复现方法

复现材料见 [复现材料清单](复现/材料清单.md)。导入脚本已做文本脱敏；未导入的原始脚本、日志、抓包和二进制见根目录材料清单。

## 9. 支撑证据

见 [证据材料清单](证据/材料清单.md) 和本页第 13 节。来源文件只登记哈希和本地保管路径，不把原始敏感材料带入 Git。

## 10. 修复建议

- 对入口实施身份认证、细粒度授权、消息完整性校验和重放防护；
- 对路径、长度、协议字段、文件类型和状态转换使用允许列表；
- 删除硬编码凭据并轮换已暴露材料；
- 对高风险服务降权，增加审计日志和负向回归测试。

## 11. 相关 AI 会话

当前未发现与该报告一一对应的完整 Claude Code 会话记录；如后续补齐，将在 [AI 会话索引](../../../../../AI轨迹/会话索引.md) 中登记。

## 12. 披露记录

- 当前披露状态：内部研究。
- 对外披露前必须重新审查凭据、设备标识、证据和厂商协调状态。

## 13. 脱敏后的原始研究正文

# V3 · ExecuteCmd 蓝牙(BT)节点 → `system()` 命令执行

| 项 | 值 |
|---|---|
| 组件 | vision 板蓝牙控制节点（容器 `walker-system.ae_bt_master`） |
| 能力 | `ExecuteCmd` — 对技能文件中的命令直接 `system()` 执行 |
| 危害 | **严重** — 技能目录 `/etc/walker/skills/` 宿主可写 → 写技能 = root 命令执行 |
| 来源 | report_vision_core(1).md (V3) |
| 复验 | ⚠️ **现场未复现**：当前镜像 `walker-s2/system:ws2_vision-v0.40.1` 上，宿主与 ae_bt_master 容器内**均无 `/etc/walker/skills` 目录、无 `ExecuteCmd` 字符串**。子代理报告基于静态分析，可能对应其他固件版本 → **降级为待验证** |

> ⚠️ **重要**：本会话在活体系统上全盘检索（宿主 /opt /etc /usr/local + ae_bt_master /
> task_manager / control_center 容器）均未找到 `skills` 目录或 `ExecuteCmd` 字符串。
> 该发现**未能现场确认**，按反误报纪律标记为"静态报告、待新固件/其他代码路径验证"。
> `ae_bt_master` 实际运行的是 tbox JSON-RPC 服务 `ae_master`（与 cc_api 同框架），
> 技能执行能力若存在，更可能经 tbox method（如 skill.*）暴露，而非此前的 `/etc/walker/skills/` 路径。

## 漏洞原理
蓝牙控制节点提供 `ExecuteCmd`：读取技能文件并把其中命令交给 `system()`。
- 技能目录 `/etc/walker/skills/` 为**宿主可写**（bind-mount 进容器）
- 蓝牙控制面（手机 APP / BLE 连接）**无认证触发**
- 组合：攻击者（含局域网已有 RCE 者）写一个技能文件 → 触发 ExecuteCmd → root 执行任意命令
- 即使无 RCE 前置，BLE 广播/配网攻击也可能直达该接口

## 利用脚本
`scripts/exploit_executecmd.py`

- 默认（安全）：
  1. 确认 `ae_bt_master` 容器运行态
  2. 检查 `/etc/walker/skills` 权限（宿主可写?）
  3. grep 容器内 `ExecuteCmd` / `system(` / 技能关键字证据
- `--danger`：展示恶意技能 JSON（`{"name":"poc","cmd":"id > /tmp/bt_pwned ..."}`），**不写入/不触发**。

## 用法
```
python exploit_executecmd.py            # 运行态 + 权限 + 静态证据
python exploit_executecmd.py --danger   # 查看恶意技能载荷（不触发）
```

## 证据输出
- 容器运行状态
- 技能目录权限（`stat -c '%A %U:%G'`）
- `ExecuteCmd` 静态证据
- `evidence/` 目录留存

## 红线 / 风险
⚠️ 触发 ExecuteCmd 会真实执行命令且影响蓝牙链路，默认不写技能/不触发。

## 复现要点（实验环境）
```
echo '{"name":"poc","cmd":"id > /tmp/bt_pwned"}' > /etc/walker/skills/poc.json
# 经 BLE/手机 APP 触发该技能 → cat /tmp/bt_pwned 验证 root
```
