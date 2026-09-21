---
编号: GAL-017
验证状态: 静态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: vis模型WebSocket13140未授权关节控制-1
---
# GAL-017 伽利略（Galileo）机器人 vis 模型 WebSocket 13140 未授权关节控制 漏洞报告

## 1. 一句话结论

- # 伽利略（Galileo）机器人 vis 模型 WebSocket 13140 未授权关节控制 漏洞报告
- \| 漏洞类型 \| 未授权 WebSocket 命令通道 → 关节电机使能/禁用 + 关节回零（+ lidar 配置篡改） \|
- \| 权限 \| 任意可达 TCP 13140 的主机（同 WiFi/LAN） \|
- ## 1. 漏洞概述
- \| `robot.sensor.lidar` / 2002 \| 任意 JSON \| 覆盖 lidar 运行时配置 \|

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| `galileo-robot-vis/bin/robot_urdf_web`（C++ websocketpp），端口 13140，绑定通配（AF_INET6 any 双栈） \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- URDF 可视化后端 `robot_urdf_web` 在 **13140 端口**起一个 WebSocket 服务（绑定全接口，
- 1. WebSocket 服务加认证（token/origin 白名单）并默认只绑 127.0.0.1；
- 3. 移除生产环境无消费者的 `hw_user_command` 速度写路径（或补上消费者前先禁用）。

## 3. 验证状态

`静态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- **全链路无认证、无 origin/来源检查、无速率限制**。可触发：

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # 伽利略（Galileo）机器人 vis 模型 WebSocket 13140 未授权关节控制 漏洞报告
- - 前端 JS `webroot/assets/index-DA85TxWu.js`：`getWebSocketURL()` → `ws://...:13140`
- python exploit.py killmotors       # 全关节电机禁用（危害最大）
- ## 5. 影响范围
- - 未授权远程**电机禁用**：运行中触发 = 物理坠机/失控（高危安全）；
- - lidar 配置篡改：影响导航/避障；

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

# 伽利略（Galileo）机器人 vis 模型 WebSocket 13140 未授权关节控制 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） |
| 漏洞组件 | `galileo-robot-vis/bin/robot_urdf_web`（C++ websocketpp），端口 13140，绑定通配（AF_INET6 any 双栈） |
| 漏洞类型 | 未授权 WebSocket 命令通道 → 关节电机使能/禁用 + 关节回零（+ lidar 配置篡改） |
| 权限 | 任意可达 TCP 13140 的主机（同 WiFi/LAN） |
| 复现日期 | 2026-08-29（来源：外部审计 `AUD-vislcm-ws-motion-control`，含其复审修正） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

URDF 可视化后端 `robot_urdf_web` 在 **13140 端口**起一个 WebSocket 服务（绑定全接口，
双栈），其前端页面经 `ws://<host>:13140` 直连。消息为 JSON 命令帧：

```json
{"ver":"1.0","type":"command","domain":"robot.joint","func_code":4001,
 "frame_id":N,"ts":M,"resp_type":1,"payload":{...}}
```

**全链路无认证、无 origin/来源检查、无速率限制**。可触发：

| domain/func_code | 命令 | 效果 |
|---|---|---|
| `robot.joint` / 4001 | `{"type":"motor_enable","enabled":false}` | 发布 `Robot_Joint_Enable_Ctrl`（哈希 0x218B67A0E56B6BDD）→ **全部关节电机禁用** |
| `robot.joint` / 4001 | `{"type":"joint_zero","scope":"all"}` | 发布关节回零命令 |
| `robot.joint` / 4001 | `{"type":"joint_zero_each","joints":["fl_hip",...]}` | 逐关节回零 |
| `robot.sensor.lidar` / 2002 | 任意 JSON | 覆盖 lidar 运行时配置 |

关键证据：`DrainJointGenericCommand@0x6EF80` 把 motor_enable/joint_zero 发布到
`hw_robot_joint_enable_ctrl` / `hw_joint_zeropos_set` 共享内存话题，**HAL 的
shm_channel.yaml 消费这些话题**（外部复审实测确认：HAL 侧订阅，二者真实生效）。

**诚实边界（外部复审修正，我方认同）**：同一 WebSocket 的
`robot.motion/1001` 速度命令把 `UserCommandData` 写入 `hw_user_command` SHM 话题，
但该话题 **dump 内无任何消费者**（仅 robot_urdf_web 自身含此字符串；mc/hal 都不订阅），
故"经 WS 遥控底盘速度"**不成立**——**成立的是电机禁用 + 关节回零 + lidar 配置**。
此外 mc 侧 LcmUserCommandSubscriber 有 ~1 秒死区（无新命令即回零），但 motor_enable/
joint_zero 为一次性命令、无死区。

## 2. 证据（外部审计反汇编 + 我方方向复核）

- `robot_urdf_web` 符号完好（未 strip）：
  `WebSocketServer::Run(ushort)@0x8F460`（wildcard AF_INET6 + listen + message handler）
  → `HandleInbound@0x670A0` → `RobotCommandIntentRouter::HandleCommand@0x48540`
  → `RobotCommandExecutor::RunLoop@0x6FCB0`（发布 `UserCommandData`/`Robot_Joint_Enable_Ctrl`）
  → `DrainJointGenericCommand@0x6EF80`（motor_enable/joint_zero/joint_zero_each 分发）
- 前端 JS `webroot/assets/index-DA85TxWu.js`：`getWebSocketURL()` → `ws://...:13140`
- 消费链：`galileo-robot-hal/.../shm_channel.yaml` 订阅 `hw_robot_joint_enable_ctrl`/
  `hw_joint_zeropos_set`（见 HAL 配置）
- 启动：`robot_urdf_web.sh` 开机启动 `robot_urdf_web <robot_name>`（WS 13140）+ `_http`（13141）

## 3. 攻击链

```
攻击者（同 WiFi）
   │ ws://<robot>:13140（无握手凭据）
   ▼
发送 robot.joint/4001 motor_enable=false
   ▼
HAL 消费 → 全关节电机断电（运行中的机器人直接摔落/失控停车）
   （+ joint_zero 破坏标定 / lidar 配置篡改）
```

## 4. 复现（adb 桥接版见 exploit.py）

```bash
python exploit.py killmotors       # 全关节电机禁用（危害最大）
python exploit.py zero --scope all # 全关节回零
python exploit.py zero --joints fl_hip,fr_hip
```

## 5. 影响范围

- 未授权远程**电机禁用**：运行中触发 = 物理坠机/失控（高危安全）；
- 未授权关节回零：破坏标定、可能导致运动异常；
- lidar 配置篡改：影响导航/避障；
- 与 LCM/UDP10086/ZMQ5555 并列的**第 5 条未授权控制面**（本条目成立的是关节/电机，非速度）。

## 6. 修复建议

1. WebSocket 服务加认证（token/origin 白名单）并默认只绑 127.0.0.1；
2. motor_enable/joint_zero 等高权限命令要求会话授权 + 二次确认；
3. 移除生产环境无消费者的 `hw_user_command` 速度写路径（或补上消费者前先禁用）。

## 7. 证据

- `evidence/`：外部审计反汇编要点摘录（或指向其原始报告）
- 外部审计原文：`AUD-vislcm-ws-motion-control.md`
- 待动态确认：13140 端口实际绑定、生产 yaml 是否启用 vis 模块
