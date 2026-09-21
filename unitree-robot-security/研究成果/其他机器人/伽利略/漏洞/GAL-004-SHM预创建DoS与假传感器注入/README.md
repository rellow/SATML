---
编号: GAL-004
验证状态: 静态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: SHM预创建DoS与假传感器注入
---
# GAL-004 伽利略（Galileo）SHM 预创建 DoS 与假传感器注入 漏洞报告

## 1. 一句话结论

- \| 攻击面 \| 本地任意 UID（/dev/shm）；经任一远程 RCE（#1/#4）即可远程链式 \|
- \| 权限 \| galileo（或经 web RCE 的任意远程攻击者） \|
- ## 1. 漏洞概述
- fd = shm_open(name, O_RDWR, 0);              // 附加已有对象——任意创建者
- - 本地/链式远程（经 #1/#4 任一 RCE）：机器人控制面拒绝服务（可持续、跨重启）；

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W 轮足机器人（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| `galileo-robot-mc/lib/liborrt_motion_control_shm_{imu,joint_state,odometry}_subscriber.so`、`..._shm_joint_command_publisher.so`（共享 `ocm::SharedMemoryData<unsigned char>::Init@0xe710`） \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- 服务启动前（开机 / kill_motion_control 后）以错误 size 预建 create 型段
- - 站立中注入假重力向量 → 平衡策略**主动驱倒机器人**（物理拒绝服务）；
- - 本地/链式远程（经 #1/#4 任一 RCE）：机器人控制面拒绝服务（可持续、跨重启）；

## 3. 验证状态

`静态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- 详见下方脱敏研究正文和材料清单。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- 运动控制进程与 HAL 经 POSIX 共享内存交换传感器/命令，对象名
- `"Existing shared memory ... size mismatch"` → 节点初始化失败 → **机器人无法被控制**。
- 攻击者保持对象 pinned 即跨重启持续生效——难诊断的"开机进不了控制"状态。
- ## 3. 复现（root 通道 adb 桥接版 exploit.py）
- ## 4. 影响范围
- - 本地/链式远程（经 #1/#4 任一 RCE）：机器人控制面拒绝服务（可持续、跨重启）；

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

# 伽利略（Galileo）SHM 预创建 DoS 与假传感器注入 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W 轮足机器人（固件 galileo-inter 1.0.44） |
| 漏洞组件 | `galileo-robot-mc/lib/liborrt_motion_control_shm_{imu,joint_state,odometry}_subscriber.so`、`..._shm_joint_command_publisher.so`（共享 `ocm::SharedMemoryData<unsigned char>::Init@0xe710`） |
| 漏洞类型 | 不安全 IPC（CWE-918/476 类）：未验证 shm 身份/尺寸/权限 + 世界可创建 POSIX shm 对象 |
| 攻击面 | 本地任意 UID（/dev/shm）；经任一远程 RCE（#1/#4）即可远程链式 |
| 权限 | galileo（或经 web RCE 的任意远程攻击者） |
| 发现来源 | 外部 round-2 `AUD-w2mc-shm-precreate-dos`；我方配置级独立复核 |
| 复现日期 | 2026-08-29（配置确证；代码模式采信 round-2 反汇编） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

运动控制进程与 HAL 经 POSIX 共享内存交换传感器/命令，对象名
`openrobot_ocm_ + {shm_hw_imu, shm_hw_joint_state, shm_hw_joint_command, shm_hw_odometry}`
（我方固证 `shm_channel.yaml` 原文）。`SharedMemoryData::Init` 为经典
open-then-create 模式，无属主/创建者校验、无握手/序列号/校验和：

```c
fd = shm_open(name, O_RDWR, 0);              // 附加已有对象——任意创建者
if (fd == -1 && errno == ENOENT)
    fd = shm_open(name, O_CREAT|O_RDWR, 0664);  // 创建；attach 时采纳已有 size
else { fstat(fd,&st); if(!create_flag) size = st.st_size;   // ★ 采纳攻击者的 size
       else if (size != st.st_size) throw "size mismatch";  // create 遇 squat 即抛
       mmap(RW|SHARED); }
```

（`shm_open(name)` ≡ `open("/dev/shm/"+name)`——**dd 建文件即完成 squat**，
无需任何 shm API。）

### 攻击 A：预创建 squat（可用性）
服务启动前（开机 / kill_motion_control 后）以错误 size 预建 create 型段
（如 `shm_hw_joint_command`）→ `ShmJointCommandPublisher::Init` 抛
`"Existing shared memory ... size mismatch"` → 节点初始化失败 → **机器人无法被控制**。
攻击者保持对象 pinned 即跨重启持续生效——难诊断的"开机进不了控制"状态。

### 攻击 B：假传感器注入（完整性）
预建 subscriber 段（`shm_hw_imu/joint_state/odometry`，0666）。订阅者以 attach
路径打开（无 create 标志 → **size 采纳已有对象**）并把字节解析为
`lcm_types::ImuData/JointStateData`（joint_state 订阅者甚至直接跑
`_decodeNoHash`）。RL 观测（projected_gravity/joint_pos/joint_vel）完全来自攻击者内存：
- 站立中注入假重力向量 → 平衡策略**主动驱倒机器人**（物理拒绝服务）；
- 伪造里程计 → SLAM 定位漂移。

命令段（0664 组可写）同组账号可直接覆写 HAL 消费的关节命令结构，
绕过全部 LCM 侧死区/规则检查。

## 2. 证据

- `evidence/shm_channel.yaml`：四段名（我方固证原文）
- `ocm::SharedMemoryData::Init@0xe710` 反编译（round-2；open-then-create/0664/采纳 size）
- 通道消费关系：HAL shm_channel.yaml 订阅 joint_enable_ctrl 等（与 #16 关节命令链同构）

## 3. 复现（root 通道 adb 桥接版 exploit.py）

```bash
python exploit.py check    # 查看当前段 + motion 进程（无副作用）
python exploit.py squat    # ★ dd 预建4段(16B) → 杀motion → 拉起前后对比 + 日志 size mismatch
python exploit.py clean    # 清除 → 重建恢复
```

关键证据输出：squat 前 motion 在线 → 拉起后 motion 缺席 + 日志出现
`Existing shared memory ... size mismatch`。

## 4. 影响范围

- 本地/链式远程（经 #1/#4 任一 RCE）：机器人控制面拒绝服务（可持续、跨重启）；
- 假传感器注入 → 平衡策略驱倒机器人（物理危害）、定位破坏；
- 命令段覆写 → 绕过死区/规则的直接关节命令。

## 5. 修复建议

1. shm 段以独占属主创建（O_EXCL + 受限目录/权限），attach 校验创建者与尺寸常量；
2. 段内加序号/校验和/心跳，消费端校验；
3. 敏感段（命令/IMU）挂 /dev/shm 受保护子目录（root 属主，服务专用组）。

## 6. 证据

- `evidence/shm_channel_yaml.txt`：四段名配置原文
- `C:\zyh\work\机器人\伽利略\ext_audit\round2\round2-交叉静态验证_20260829.md` §二.5
- 外部 round-2 原文：`AUD-w2mc-shm-precreate-dos.md`
