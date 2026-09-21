---
编号: GAL-001
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: Flask上传文件名路径穿越任意文件写-1
---
# GAL-001 伽利略（Galileo）机器人 /upload 文件名路径穿越 —— 任意 *.tar.gz 文件写 漏洞报告

## 1. 一句话结论

- # 伽利略（Galileo）机器人 /upload 文件名路径穿越 —— 任意 *.tar.gz 文件写 漏洞报告
- \| 漏洞类型 \| 路径穿越 → 任意文件写（独立于 install.sh 执行链的写原语） \|
- \| 权限 \| 未授权 → 以服务用户写**任意含 `tar.gz` 的路径** \|
- ## 1. 漏洞概述
- ## 2. 与 install.sh RCE（#1）的区别

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| Flask 管理后台 `POST /upload`（`routes/upload.py` → `utils/file_utils.py!upload_and_extract_file`） \|
- \| 权限 \| 未授权 → 以服务用户写**任意含 `tar.gz` 的路径** \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- 2. **`os.path.join` 遇绝对路径组件重置前缀**：`join('/tmp/uploads','/etc/x.tar.gz')`==`/etc/x.tar.gz`。
- ┌─ 覆盖 /home/galileo/123.tar.gz（230MB 固件升级包）→ 供应链/升级注入

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- # 伽利略（Galileo）机器人 /upload 文件名路径穿越 —— 任意 *.tar.gz 文件写 漏洞报告
- \| 漏洞类型 \| 路径穿越 → 任意文件写（独立于 install.sh 执行链的写原语） \|

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- \| 严重度 \| 🟠 High（外部审计标 Critical；详见 §6 约束说明） \|
- ## 5. 影响范围
- （若能找到某个含 tar.gz 且被 root/sudo 消费的路径，则可升级回 Critical。）

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

# 伽利略（Galileo）机器人 /upload 文件名路径穿越 —— 任意 *.tar.gz 文件写 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） |
| 漏洞组件 | Flask 管理后台 `POST /upload`（`routes/upload.py` → `utils/file_utils.py!upload_and_extract_file`） |
| 漏洞类型 | 路径穿越 → 任意文件写（独立于 install.sh 执行链的写原语） |
| 权限 | 未授权 → 以服务用户写**任意含 `tar.gz` 的路径** |
| 严重度 | 🟠 High（外部审计标 Critical；详见 §6 约束说明） |
| 复现日期 | 2026-08-29（外部审计本地验证 PASSED） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

`/upload` 把 multipart `Content-Disposition: filename=` **原样**取为文件名，直接
`os.path.join(UPLOAD_FOLDER, file.filename)` 后 `file.save()`，全程**未调 `secure_filename`**：

```python
# utils/file_utils.py!upload_and_extract_file（还原自 pyc）
if not allowed_file(file.filename): return {'status':'error',...}
file_path = os.path.join(upload_folder, file.filename)   # ← filename 原样拼接
file.save(file_path)                                     # ← 写盘，先于 tar
subprocess.run(['tar','-xzf', file_path, '-C', upload_folder], check=True)  # 之后失败也无所谓
```

两个缺陷：
1. **`allowed_file()` 是子串匹配**：`any(ext in filename for ext in ALLOWED_EXTENSIONS)`
   （`['tar.gz']`）—— 不是后缀校验，`/etc/…/pwn.tar.gz`、`../../…/x.tar.gz` 均满足。
2. **`os.path.join` 遇绝对路径组件重置前缀**：`join('/tmp/uploads','/etc/x.tar.gz')`==`/etc/x.tar.gz`。

且 `file.save()` 在 `tar -xzf` **之前**执行——即使上传的不是合法 gzip、tar 报错，**文件早已落盘**。

## 2. 与 install.sh RCE（#1）的区别

| | install.sh RCE（#1） | 本漏洞 |
|---|---|---|
| 触发条件 | tar 是合法 gzip 且含 install.sh | 文件名含 tar.gz 子串 + 任意内容 |
| 效果 | 执行 /tmp/uploads/install.sh | 写任意「含 tar.gz」路径 |
| tar 失败时 | 无执行 | 文件仍已写盘 |

## 3. 攻击链（受 tar.gz 约束的写原语）

```
攻击者（同 WiFi）
   │ POST /upload，filename=<含 tar.gz 的绝对/穿越路径>
   ▼
file.save() → 写任意「含 tar.gz」路径（galileo 权限）
   ▼
┌─ 覆盖 /home/galileo/123.tar.gz（230MB 固件升级包）→ 供应链/升级注入
├─ 覆盖 /home/galileo/galileo-robot-hal.tar.gz 等已分发 tar 包
├─ 写任意目录下的 *.tar.gz（含 /tmp/uploads/，配合 #1 若内容合法 gzip 则触发 install.sh）
└─ 批量写大文件 → 磁盘耗尽 DoS
```

## 4. PoC（adb 桥接版见 exploit.py）

```bash
python exploit.py --target /home/galileo/123.tar.gz --content "PWNED"        # 覆盖固件包
python exploit.py --target ../../../../tmp/pwn.tar.gz --content "PWNED"      # 穿越写法
# 验证：GET /download_log 或 /list_logs_in_dir 回读，或 /get_robot_env 穿越读确认内容
```

## 5. 影响范围

- 未授权写任意「含 tar.gz」路径（独立写原语，不依赖 tar 解压成功）；
- 覆盖固件/分发 tar 包 → 供应链注入；
- 磁盘填充 DoS。

## 6. 约束与定级说明（重要）

外部审计标 **Critical**，理由是"任意文件写原语"。但 `allowed_file()` 的**子串匹配同时构成约束**：
目标路径**必须含 `tar.gz` 子串**，因此**不能直接写** `~/.ssh/authorized_keys`、
`service_launcher.sh`、`check_and_fix_multicast.sh`、`*.so` 等不含 tar.gz 的提权目标——
这些直接提权链不成立。可写目标被限制在「*.tar.gz 命名的路径」内，故实际定级为 **High**。
（若能找到某个含 tar.gz 且被 root/sudo 消费的路径，则可升级回 Critical。）

## 7. 修复建议

1. `secure_filename()` + 丢弃绝对路径与 `..` 段；
2. `allowed_file` 改后缀精确匹配 `endswith('.tar.gz')`；
3. `save` 与 `tar` 之间校验文件确为合法 gzip。

## 8. 证据

- `evidence/AUD-web-upload-filename-path-traversal.md`：外部审计原文（本地验证 PASSED）
- 我方反汇编：`analysis/webmgr_extract/custom_dis.txt` file_utils 段
