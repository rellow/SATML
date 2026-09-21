---
编号: GAL-007
验证状态: 静态确认
严重程度: 中
披露状态: 内部研究
源平台: 伽利略
源候选目录: UDP10086环形缓冲区反同步
---
# GAL-007 伽利略（Galileo）机器人 UDP 10086 环形缓冲区反同步（堆越界读+崩溃）漏洞报告

## 1. 一句话结论

- \| 权限 \| 任意可达 UDP 10086 的主机（未授权，单个 UDP 包） \|
- ## 1. 漏洞概述
- u32 0x55AA55AA \| u32 任意已注册 cmd \| u32 length=0x00100000 \| u32 type=1   （仅16字节头）
- - 未授权单包远程崩溃监控主进程（与栈溢出漏洞互补的第二条崩溃路径）；

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| `libNetworkSdk.so`：`ProcessData@0x6A39C`（非法长度分支）→ `HRingBuf::free@0x6DAC8` \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- exploit.py 已重写为"攻击前/后服务状态对比"版（同 #21/#14 模板）：

## 3. 验证状态

`静态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- # 伽利略（Galileo）机器人 UDP 10086 环形缓冲区反同步（堆越界读+崩溃）漏洞报告
- \| 漏洞类型 \| 未校验长度直传环形缓冲区释放 → 读偏移/已用量被攻击者改写 → 堆越界读进入命令处理 + 可靠远程崩溃 \|
- 2. **read_off 越界**（如 length=0x00100000 → read_off=0x100010，环形缓冲实际只有
- `HBuf` 并交给命令处理函数 → **堆越界读** + 大概率段错误崩溃。
- - 堆越界读内容进入命令处理链（信息泄露潜力，取决于堆布局）；

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- ## 5. 影响范围
- - 堆越界读内容进入命令处理链（信息泄露潜力，取决于堆布局）；

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

# 伽利略（Galileo）机器人 UDP 10086 环形缓冲区反同步（堆越界读+崩溃）漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） |
| 漏洞组件 | `libNetworkSdk.so`：`ProcessData@0x6A39C`（非法长度分支）→ `HRingBuf::free@0x6DAC8` |
| 漏洞类型 | 未校验长度直传环形缓冲区释放 → 读偏移/已用量被攻击者改写 → 堆越界读进入命令处理 + 可靠远程崩溃 |
| 权限 | 任意可达 UDP 10086 的主机（未授权，单个 UDP 包） |
| 复现日期 | 2026-08-29（来源：外部审计 `AUD-udp-ringbuf-desync`，我方对其反汇编逻辑独立复核认同） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

`ProcessData` 对 `type==1` 的包**先信任、后校验** length：当 length 超出 `1..0x400`
时走"Invalid packet size"分支，但仍把 **未校验的 `length+16`** 交给 `HRingBuf::free`：

```c
if (len <= 0x400 && len) { ...正常路径... }
else {
  printf("Invalid packet size: %u, skipping header\n", len);
  HRingBuf::free(rb, len + 16);        // ← 攻击者 u32 + 16，无钳制
}
```

`HRingBuf::free` 不做任何钳制：

```c
this->used -= a2;                      // used 下溢成巨大 u64 → 后续所有 size() 守卫恒真
if (a2 > capacity - read_off) this->read_off = a2;   // read_off = 攻击者值（远超 0x2800 容量）
else this->read_off += a2;
```

后果（一个 16 字节 UDP 包触发）：
1. **used 下溢** → `HRingBuf::size()` 返回巨大值 → 后续所有 `size() >= length+16`
   守卫无条件通过；
2. **read_off 越界**（如 length=0x00100000 → read_off=0x100010，环形缓冲实际只有
   0x2800 字节）→ 下一轮循环从野指针读 magic、`memcpy` 最多 1024 字节堆外数据进
   `HBuf` 并交给命令处理函数 → **堆越界读** + 大概率段错误崩溃。

另有整数回绕变体：`length ≥ 0xFFFFFFF1` 时 `(u32)length+16` 回绕成 `1..15`，
使缓冲区记账与内容错位（后续包的 payload 字节被当作包头消费）。

## 2. 证据链（外部审计反汇编 + 我方复核）

- `ProcessData@0x6A39C` 无效长度分支（我方 processdata_dis.txt 中
  `0x6a578` 日志路径与 `0x6a5f8` free 调用对应）；
- `HRingBuf::free@0x6DAC8`：无钳制赋值（外部审计给出反汇编，逻辑与 hv 库
  环形缓冲实现一致）；
- 环形缓冲容量 0x2800（`NetworkAppImplInit` 中 `HBuf::resize(this+272, 0x2800)`）。

## 3. PoC 包格式

```
u32 0x55AA55AA | u32 任意已注册 cmd | u32 length=0x00100000 | u32 type=1   （仅16字节头）
变体: length=0xFFFFFFF1..0xFFFFFFFF → free(1..15) 记账错位
观察: monitor 日志 "Invalid packet size" 后进程崩溃/后续包解析错乱
```

## 4. 复现（adb 桥接版见 exploit.py）

```bash
python exploit.py desync                 # read_off 野指针 → 崩溃
python exploit.py wrap                   # 整数回绕变体
```

## 5. 影响范围

- 未授权单包远程崩溃监控主进程（与栈溢出漏洞互补的第二条崩溃路径）；
- 堆越界读内容进入命令处理链（信息泄露潜力，取决于堆布局）；
- 记账错位变体可造成协议状态混乱（后续合法/攻击包被错误解析）。

## 6. 修复建议

1. 无效长度分支只 `free(rb, 16)`（消费包头本身），绝不信任 length；
2. `HRingBuf::free` 对 a2 做 `min(a2, used)` 钳制，read_off 永远模容量；
3. length 上限校验提前到任何缓冲区操作之前。

## 7. 证据

- `evidence/processdata_dis.txt`（我方反汇编全文）
- 外部审计原文：`AUD-udp-ringbuf-desync.md`

---

## 8. 我方指令级独立复核（2026-08-29 晚，补强原 §2"采信外部审计"）

`libNetworkSdk.so` 手工反汇编（非采信 round-2）：

```
ProcessData@0x6A560: 7110001f = CMP W0,#0x400; B.hi 0x6a578（无效长度分支）
                     → 0x6a5f8 调 free（旧 dis 固证）

HRingBuf::free@0x6DAC8:
  0x6dad8  LDR  X1,[X0,#0x30]   ; used
  0x6dadc  LDR  X0,[SP,#0]      ; a2 = 攻击者 len+16
  0x6dae0  SUBS X1,X1,X0        ; ★ used -= a2 —— 无钳制（下溢成巨大 u64）
  0x6dae8  STR  X1,[X0,#0x30]   ; 写回 used（size() 守卫此后恒真）
  0x6daf0  LDR  X1,[X0,#0x10]   ; capacity
  0x6daf8  LDR  X0,[X0,#0x20]   ; read_off
  0x6dafc  SUBS X0,X1,X0        ; capacity - read_off
  0x6db04  CMP  a2, ...; B.cond 0x6db48
  0x6db48  LDR  X0,[SP,#8]; LDR X1,[SP,#0]
  0x6db50  STR  X1,[X0,#0x20]   ; ★ read_off = 攻击者值（容量仅 0x2800）
```

exploit.py 已重写为"攻击前/后服务状态对比"版（同 #21/#14 模板）：
`smash`（len=0x00100000，自动补发常规包驱动 read_off 消费）/ `smash --len 0xFFFFFFF1`
（回绕变体）/ `verify`。
