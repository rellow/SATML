---
编号: UBH-011
验证状态: 静态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选人型
源候选目录: cc_api-jsonrpc零认证远程控制
---
# UBH-011 V5 · cc_api tbox JSON-RPC 零认证远程控制

## 1. 一句话结论

- \| 危害 \| **高** — `motion.cmd_vel` / `network.wifi.ap.set` / `settings.iot.mqtt.set` / `skill.*` / `work.*` 全部无认证 \|
- 帧格式逆向由子代理完成，结论见 `_worknotes/cc_api_protocol.md`（生成中）。
- - RE 帧格式结论（若就绪）

## 2. 影响产品与版本

- \| 组件 \| vision 板 `cc_api_client_tbox_main_demo`（容器 walker-system.cc_api_client-1） \|
- \| 端口 \| `0.0.0.0:40000`（TCP，tbox JSON-RPC 二进制帧） \|
- \| 复验 \| 🟢 40000 端口存活，TCP 连入回 3 字节应答 `ff fe 01`；本会话已提取 12.7MB 二进制 \|
- 服务注册），暴露数百个 `method`，**均无身份认证 / 无令牌**：

## 3. 验证状态

`静态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- \| 危害 \| **高** — `motion.cmd_vel` / `network.wifi.ap.set` / `settings.iot.mqtt.set` / `skill.*` / `work.*` 全部无认证 \|
- 只读方法（`cc.api.fault.*`）可作无认证调用的最小证明。
- 40000 → 返回机器人故障列表（未登录/无认证）即证明方法调用面完全暴露。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # V5 · cc_api tbox JSON-RPC 零认证远程控制
- \| 危害 \| **高** — `motion.cmd_vel` / `network.wifi.ap.set` / `settings.iot.mqtt.set` / `skill.*` / `work.*` 全部无认证 \|
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

# V5 · cc_api tbox JSON-RPC 零认证远程控制

| 项 | 值 |
|---|---|
| 组件 | vision 板 `cc_api_client_tbox_main_demo`（容器 walker-system.cc_api_client-1） |
| 端口 | `0.0.0.0:40000`（TCP，tbox JSON-RPC 二进制帧） |
| 危害 | **高** — `motion.cmd_vel` / `network.wifi.ap.set` / `settings.iot.mqtt.set` / `skill.*` / `work.*` 全部无认证 |
| 来源 | report_vision_core(1).md (V5) |
| 复验 | 🟢 40000 端口存活，TCP 连入回 3 字节应答 `ff fe 01`；本会话已提取 12.7MB 二进制 |

## 漏洞原理
cc_api 实现 tbox JSON-RPC 框架（C++ nlohmann::json，`ubt::walker::cc::api::TcpClient`
服务注册），暴露数百个 `method`，**均无身份认证 / 无令牌**：
- `motion.cmd_vel` — 直接发运动速度指令
- `network.wifi.ap.set` — 改网络配置（可致失联）
- `settings.iot.mqtt.set` — 改云端连接
- `skill.*` / `work.*` — 技能/任务下发

本会话实测：裸发 JSON 行回 `ff fe 01`（非裸 JSON，走二进制帧协议）。
帧格式逆向由子代理完成，结论见 `_worknotes/cc_api_protocol.md`（生成中）。

## 利用脚本
`scripts/exploit_cc_api.py`

- 默认（安全）：
  1. 读取 RE 逆向笔记（若已生成）
  2. 静态提取方法表（运行二进制 grep + 本地 `_analysis/cc_api/cc_api.bin` 离线提取）
  3. `--probe`：TCP 连 40000 指纹只读探测
- `--method`：指定只读方法名（默认 `cc.api.fault.current.get` 故障查询）。

## 用法
```
python exploit_cc_api.py                    # 指纹 + 方法表
python exploit_cc_api.py --probe            # 额外做 40000 只读探测
```

## 证据输出
- 方法表（几十到上百个 method 名）
- 40000 指纹应答
- RE 帧格式结论（若就绪）
- `evidence/` 目录留存

## 红线 / 风险
⚠️ `motion.cmd_vel` / `network.*` / `skill.*` 均有物理/网络副作用，**不调用**。
只读方法（`cc.api.fault.*`）可作无认证调用的最小证明。

## 复现要点（只读）
按 `_worknotes/cc_api_protocol.md` 帧格式，构造 `cc.api.fault.current.get` 请求发往
40000 → 返回机器人故障列表（未登录/无认证）即证明方法调用面完全暴露。
