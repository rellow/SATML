---
编号: GAL-003
验证状态: 静态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: ONNX策略未签名供应链植入
---
# GAL-003 伽利略（Galileo）ONNX 策略未签名供应链植入 漏洞报告

## 1. 一句话结论

- \| 权限 \| galileo（= web RCE 落地用户） \|
- ## 1. 漏洞概述
- 在策略切换时从盘重建 onnxruntime 会话；切换可被未授权 **ZMQ 5555**（#25，
- - 文件在 web 可写 home 树内 → 任一 wave-1 web RCE 即成**持久化物理后门**
- 攻击者（web RCE → galileo，或本地）

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W 轮足机器人（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| `galileo-robot-mc/lib/liborrt_motion_control_wheel_onnx_policy_inference.so`、`..._rl_control_recovery.so`（onnxruntime 加载器） \|
- \| 漏洞类型 \| 供应链完整性缺失（CWE-494）：控制面工件无签名/哈希/版本固定 \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- - 恶意模型输出 clip 饱和关节目标 → 持续剧烈关节运动（貌似固件 bug）；

## 3. 验证状态

`静态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- \| 漏洞类型 \| 供应链完整性缺失（CWE-494）：控制面工件无签名/哈希/版本固定 \|
- 1. **零完整性校验**：加载路径无签名/哈希/固定（库内无 openssl/crc/摘要字符串），

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- \| 漏洞类型 \| 供应链完整性缺失（CWE-494）：控制面工件无签名/哈希/版本固定 \|
- 在运动控制进程内按策略频率执行，输出直接映射关节目标
- ### 影响
- - 抹掉/损坏文件 → `PolicyTransition/Inference` 抛异常 → 运动控制不可用（DoS）；
- 恶意模型以策略频率输出关节目标 —— 持久物理控制（重启存活，无进程常驻）
- ## 4. 复现（root 通道 adb 桥接版 exploit.py，无破坏演示）

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

# 伽利略（Galileo）ONNX 策略未签名供应链植入 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W 轮足机器人（固件 galileo-inter 1.0.44） |
| 漏洞组件 | `galileo-robot-mc/lib/liborrt_motion_control_wheel_onnx_policy_inference.so`、`..._rl_control_recovery.so`（onnxruntime 加载器） |
| 漏洞类型 | 供应链完整性缺失（CWE-494）：控制面工件无签名/哈希/版本固定 |
| 攻击面 | 本地文件写（galileo 树）；经 #1/#4/#19 任一远程写原语即远程链式 |
| 权限 | galileo（= web RCE 落地用户） |
| 发现来源 | 外部 round-2 `AUD-w2mc-onnx-unsigned-policy-supply-chain`；我方文件级独立复核 |
| 复现日期 | 2026-08-29（文件级确证；加载路径零校验字符串采信 round-2） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

每个运动行为（站立/行走/下楼梯/左坡/quadruped/恢复）是一个 ONNX 网络，
在运动控制进程内按策略频率执行，输出直接映射关节目标
（`policy.yaml`: `action_pos_scale: 0.25`，`clip_actions: 100.0` —— 我方固证原文）。

加载路径 `share/policy/<name>/policy.onnx`（我方固证 7 个目录，777KB–1MB，
galileo 属主）存在三重缺陷：

1. **零完整性校验**：加载路径无签名/哈希/固定（库内无 openssl/crc/摘要字符串），
   唯一"验证"是 onnxruntime 自身模型解析；
2. **热重载 + 远程触发**：`CheckPolicyTransition@0x25ba0 → PolicyTransition@0x24d70`
   在策略切换时从盘重建 onnxruntime 会话；切换可被未授权 **ZMQ 5555**（#25，
   `SetRobotPolicy`/`StandUp`/`RealtimeMotionControl`，TCP 实测可达）触发，
   LCM 路径（mc_policy_desired）已随 #6/#20 删除条目定性为不可达 —— **植入后一条
   ZMQ RPC 调用即激活**；
3. **安全限幅同树明文**：`policy.yaml`（joint_kp/max_velocity/clip_actions）、
   `wheel_onnx_policy_inference.yaml`（joint_tor_limit: 60, wheel_joint_vel_limit: 33）、
   `joint_default_wheel.yaml`（joint_kp: 200, projected_gravity_threshold: 0.1 跌倒检测阈值）
   全部可改。

### 影响
- 恶意模型输出 clip 饱和关节目标 → 持续剧烈关节运动（貌似固件 bug）；
- 抹掉/损坏文件 → `PolicyTransition/Inference` 抛异常 → 运动控制不可用（DoS）；
- 文件在 web 可写 home 树内 → 任一 wave-1 web RCE 即成**持久化物理后门**
  （无需常驻 shell，重启存活）。

## 2. 我方固证（文件级）

```
share/policy/{locomotion_blind, locomotion_blind-down-stair,
              locomotion_blind-left-slope, locomotion_blind-right-flat,
              quadruped, release, rl_control_recovery}/policy.onnx
  尺寸 777,009–1,001,491 B，各配 policy.yaml

locomotion_blind/policy.yaml（我方读取原文节选）：
  action_pos_scale: 0.25
  action_vel_scale: 2.0
  clip_actions: 100.0
  joint_names: [16 关节]
  default_joint_pos: [...]
  input_obs_scales_map: {projected_gravity: 1.0, joint_vel: 0.05, ...}
```

## 3. 攻击链

```
攻击者（web RCE → galileo，或本地）
   │ cp evil.onnx share/policy/rl_control_recovery/policy.onnx
   ▼
（任意延迟后）未授权 ZMQ 5555 `SetRobotPolicy`/`RealtimeMotionControl`（#25）← "rl_control_recovery"
   ▼
CheckPolicyTransition 命中 policy_list → PolicyTransition 从盘重建会话（无校验）
   ▼
恶意模型以策略频率输出关节目标 —— 持久物理控制（重启存活，无进程常驻）
```

## 4. 复现（root 通道 adb 桥接版 exploit.py，无破坏演示）

```bash
python exploit.py check     # 7 目录 + sha256 基线 + 明文限幅清单
python exploit.py plant     # ★ 同构策略覆盖 rl_control_recovery（自动备份）→ 前后 sha256
python exploit.py restore   # 恢复
```

关键证据：植入后 sha256 变为源策略哈希、加载路径无任何拦截 —— 同构模型互换
被 loader 接受即为"无完整性校验"的实证（真实攻击换任意恶意同构模型）。

## 5. 影响范围

- 持久化物理控制植入（配合 web RCE 免常驻）；
- 安全限幅（tor_limit/kp/跌倒阈值）篡改；
- 运动控制可用性破坏。

## 6. 修复建议

1. policy.onnx/策略 yaml 签名（厂商私钥）或固化只读分区 + 启动时哈希校验；
2. PolicyTransition 拒绝运行时非签名来源的重载；
3. 安全限幅移出可写树（root 属主只读）。

## 7. 证据

- `evidence/policy目录清单.txt`：7 目录/尺寸/yaml 关键参数（固证）
- `C:\zyh\work\机器人\伽利略\ext_audit\round2\round2-交叉静态验证_20260829.md` §二.6
- 外部 round-2 原文：`AUD-w2mc-onnx-unsigned-policy-supply-chain.md`
