---
编号: GAL-005
验证状态: 静态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: TCP8888网络手柄协议未授权接入与配置泄露-1
---
# GAL-005 伽利略（Galileo）机器人 TCP 8888 网络手柄服务未授权接入与配置泄露 漏洞报告

## 1. 一句话结论

- # 伽利略（Galileo）机器人 TCP 8888 网络手柄服务未授权接入与配置泄露 漏洞报告
- \| 漏洞类型 \| 未授权网络接入 + 配置信息泄露（`AA BB 55` 触发服务端回传整份 YAML 配置） \|
- \| 权限 \| 任意可达该端口的主机 \|
- ## 1. 漏洞概述
- 2. **状态位共享 + 未授权接入**：连接即可读/写 14 个虚拟手柄位槽（last-writer-wins，

## 2. 影响产品与版本

- # 伽利略（Galileo）机器人 TCP 8888 网络手柄服务未授权接入与配置泄露 漏洞报告
- \| 目标设备 \| 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| `galileo-robot-monitor/lib/libgamepad_sdk.so`（GamepadReceiver，TCP 服务端），由 monitor_manager 的 `galileo_sdk_virtual_joystick_app` 节点加载（release/develop 任务表均启用，开机自启） \|
- \| 漏洞类型 \| 未授权网络接入 + 配置信息泄露（`AA BB 55` 触发服务端回传整份 YAML 配置） \|
- \| 权限 \| 任意可达该端口的主机 \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|

## 3. 验证状态

`静态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- `0.0.0.0:8888`，无认证、无配对、无来源限制：任何能连上的主机即可接入。
- 结论：**监听/无认证/配置回传真实存在；但位数据不驱动运动控制**。
- - 暴露 `0.0.0.0:8888` 攻击面（无认证接入点）。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # 伽利略（Galileo）机器人 TCP 8888 网络手柄服务未授权接入与配置泄露 漏洞报告
- \| 漏洞类型 \| 未授权网络接入 + 配置信息泄露（`AA BB 55` 触发服务端回传整份 YAML 配置） \|
- 两条实际影响：
- 1. **配置回传泄露**：3 字节 `AA BB 55` 同步帧触发 `sendConfigFile@0x113F4`，服务端
- **此前的"未授权运动控制"定性过高，已降级为 MEDIUM**，依据如下（我方用自有工具复核通过）：
- 结论：**监听/无认证/配置回传真实存在；但位数据不驱动运动控制**。

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

# 伽利略（Galileo）机器人 TCP 8888 网络手柄服务未授权接入与配置泄露 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） |
| 漏洞组件 | `galileo-robot-monitor/lib/libgamepad_sdk.so`（GamepadReceiver，TCP 服务端），由 monitor_manager 的 `galileo_sdk_virtual_joystick_app` 节点加载（release/develop 任务表均启用，开机自启） |
| 漏洞类型 | 未授权网络接入 + 配置信息泄露（`AA BB 55` 触发服务端回传整份 YAML 配置） |
| 监听 | TCP 8888，绑定 `0.0.0.0`（INADDR_ANY） |
| 权限 | 任意可达该端口的主机 |
| 复现日期 | 2026-08-29（协议自 .so 逆向还原 + 外部审计包交叉复核） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

机器人运行网络虚拟手柄 TCP 服务（`GamepadReceiver`），`listen(fd,1)` 绑定
`0.0.0.0:8888`，无认证、无配对、无来源限制：任何能连上的主机即可接入。

协议帧：`AA <14 字节数据> 55`（长度严格 `data_bytes+2`=16），头/尾字节为配置中
公布的固定常量，**不构成秘密**。parser `parsePacket@0xEF40` 长度安全（固定 16 字节、
循环上界 `data_bytes`）。

两条实际影响：
1. **配置回传泄露**：3 字节 `AA BB 55` 同步帧触发 `sendConfigFile@0x113F4`，服务端
   把整份 `virtual_joystick_app_config.yaml` 流式回传客户端（含通道/动作映射、
   内网目标 IP `192.168.50.86` 等）。
2. **状态位共享 + 未授权接入**：连接即可读/写 14 个虚拟手柄位槽（last-writer-wins，
   可干扰合法手柄操作），服务端还会周期性（200ms）向已连客户端推送状态包。

## 2. 关键降级修正（外部审计复审 + 我方独立复核确认）

**此前的"未授权运动控制"定性过高，已降级为 MEDIUM**，依据如下（我方用自有工具复核通过）：

1. **回调链断裂**：`GamepadReceiver::setCallback@0x10BE0` 虽导出，但**全库无调用者**；
   唯一链接 `libgamepad_sdk.so` 的 `liborrt_..._virtual_joystick_app.so` 的
   `DT_NEEDED`/dynsym 中**不导入 setCallback**（我方实测：其 undefined import 只有
   `start/stop/loadConfig/getAllActiveBits/getConfig/Ctor/Dtor`）。因此 parsePacket
   在 `0xf368` 处调用的回调是空 `std::function` —— 那段是死代码。
2. **消费端只打日志**：`GalileoSdkVirtualJoystickApp::Execute()@0x9E70` 唯一消费
   `getAllActiveBits()`，但其非 std 导入只有 `mem*`/`pthread_rwlock_*`/`sched_yield`
   等——**无 DataCenter/LCM/SHM/发布 API**（我方实测 dynsym 无任何 Publish/Lcm/Topic
   类符号）。位数据只用于输出 `"[Virtual Joystick] Bit {} is active"` 日志。
3. **配置位不可达**：配置里 switch 位 38/39/60-65/70/71 均 > `data_bytes=14`，
   结构性不可达。

结论：**监听/无认证/配置回传真实存在；但位数据不驱动运动控制**。

## 3. 协议还原（我方独立逆向，协议正确性不受降级影响）

- `start@0xE34C`：socket(AF_INET,SOCK_STREAM) → setsockopt(REUSEADDR) → htons(port)
  → bind(INADDR_ANY) → listen(1)
- `receiveThread@0xEAD4`：accept/recv → parsePacket
- `parsePacket@0xEF40`：len==3 且 AA BB 55 → 回传配置；len==16 且头 0xAA 尾 0x55 →
  逐字节 setBit(i, data[i+1]) → （空）回调
- `sendThread@0x10F8C`：200ms 周期向客户端推送状态

## 4. 复现（adb 桥接版见 exploit.py）

```bash
python exploit.py --getconfig    # AA BB 55 → 整份 yaml 回传（配置泄露证据）
python exploit.py --status       # 连接并接收状态推送
python exploit.py --bits 0,3,7   # 写位槽（仅影响日志/干扰合法手柄，不驱动运动）
```

## 5. 影响范围

- 未授权配置信息泄露（通道/动作映射、内网 IP 等）；
- 未授权状态信息泄露（机器人状态推送可被任意连接者接收）；
- 位洪泛可干扰/抢占正常手柄的位状态（last-writer-wins）；
- 暴露 `0.0.0.0:8888` 攻击面（无认证接入点）。

## 6. 修复建议

1. 该通道加认证（连接首包握手 token）+ 来源白名单；
2. `sendConfigFile` 回传默认关闭或仅限本地；
3. 端口只绑管理网段；补齐/移除失效的位→控制映射（当前 setCallback 未接线属配置缺陷，
   若未来接上回调即为真正的控制面，应同步加鉴权）。

## 7. 证据

- `evidence/parsePacket_disassembly.txt`：parsePacket 全量反汇编（帧头尾校验/状态写入/回调）
- `evidence/virtual_joystick_app_config.yaml`：tcp_config 端口与帧格式
- 我方复核：virtual_joystick_app 的 undefined dynsym 导入（无 setCallback / 无控制面 API）
- 外部审计：`AUD-udp-gamepad-tcp8888-unauth.md`（其复审结论与此一致）
- 旁证：前任测试者 `.bash_history` 第 193/210 行 `ss -ulpn | grep -E "...|8888"`
