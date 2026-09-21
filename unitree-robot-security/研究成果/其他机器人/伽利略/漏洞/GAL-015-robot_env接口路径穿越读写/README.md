---
编号: GAL-015
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: robot_env接口路径穿越读写
---
# GAL-015 伽利略（Galileo）机器人 /get_robot_env 与 /change_port 路径穿越读写 漏洞报告

## 1. 一句话结论

- \| 漏洞类型 \| 路径穿越 → 任意文件读 + 任意文件截断/改写 \|
- \| 权限 \| 未授权（同后台全部接口） \|
- ## 1. 漏洞概述
- - `GET /get_robot_env?dir=<..>` → 打开该路径 `'r'` → 逐行以 JSON 返回（**任意文件读**）；
- `LCM_PORT=<数字>` 一行 + 其余行原样），即**任意文件截断/改写**（限定目标文件名含 robot.env）。

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| Flask 管理后台 `routes/robot.py` → `modules/robot_env.py`（`get_robot_env`/`change_port`） \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- - 未授权任意 `robot.env` 截断改写（可破坏 LCM 端口/网络配置 → 后续功能异常，或篡改
- 环境使运动控制/监控模块加载失败）。

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- # 伽利略（Galileo）机器人 /get_robot_env 与 /change_port 路径穿越读写 漏洞报告
- \| 漏洞类型 \| 路径穿越 → 任意文件读 + 任意文件截断/改写 \|
- \| 复现日期 \| 2026-08-29（来源：外部审计 `AUD-web-robot-env-path-traversal`，我方已有 `/change_port` 部分观测，此处补全读侧与越界写侧） \|

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- 两个接口都用 `os.path.join(config.ENV_ROOT, selected_dir, 'robot.env')` 构造目标路径，
- 绝对路径 `dir` 会重置 `os.path.join` 前缀，`..` 段可逃出 `ENV_ROOT`。
- `target_env = os.path.join(ENV_ROOT, dir, 'robot.env')` → `open(target_env, 'r'/'w')`
- 任意文件内容以 JSON 逐行泄露（配置/源码/凭据）
- ## 5. 影响范围
- 环境使运动控制/监控模块加载失败）。

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

# 伽利略（Galileo）机器人 /get_robot_env 与 /change_port 路径穿越读写 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） |
| 漏洞组件 | Flask 管理后台 `routes/robot.py` → `modules/robot_env.py`（`get_robot_env`/`change_port`） |
| 漏洞类型 | 路径穿越 → 任意文件读 + 任意文件截断/改写 |
| 权限 | 未授权（同后台全部接口） |
| 复现日期 | 2026-08-29（来源：外部审计 `AUD-web-robot-env-path-traversal`，我方已有 `/change_port` 部分观测，此处补全读侧与越界写侧） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

两个接口都用 `os.path.join(config.ENV_ROOT, selected_dir, 'robot.env')` 构造目标路径，
`selected_dir` 为原始客户端输入，**无 basename/realpath/白名单校验**：

- `GET /get_robot_env?dir=<..>` → 打开该路径 `'r'` → 逐行以 JSON 返回（**任意文件读**）；
- `POST /change_port`（form: `port`+`dir`）→ 打开该路径 `'w'` → 全文改写（仅
  `LCM_PORT=<数字>` 一行 + 其余行原样），即**任意文件截断/改写**（限定目标文件名含 robot.env）。

绝对路径 `dir` 会重置 `os.path.join` 前缀，`..` 段可逃出 `ENV_ROOT`。

## 2. 我方已有部分观测

- 本团队之前已记录 `change_port` 的 `dir` 穿越（原 F 类，MEDIUM-LOW），
  定性为"任意 robot.env 有限改写"；
- 外部审计补全了**读侧**（`get_robot_env` 任意文件读，此前漏报）并强化了
  `change_port` 的**截断/改写**语义（open 'w' 非追加）。

## 3. 证据

- `routes/robot.pyc`：`get_robot_env`/`change_port` 直接透传 `request.args/forms` 的
  `dir`/`port`；`port` 有 `isdigit` 校验，`dir` 无任何校验。
- `modules/robot_env.pyc!RobotEnvManager.get_robot_env`/`change_port`：
  `target_env = os.path.join(ENV_ROOT, dir, 'robot.env')` → `open(target_env, 'r'/'w')`
- `list_env_dirs` 可用于先枚举候选目录。

## 4. 攻击链

```
攻击者（同 WiFi）
   │ GET /get_robot_env?dir=../../../etc   → 读 /etc/<...>/robot.env（或借绝对路径读任意）
   ▼
任意文件内容以 JSON 逐行泄露（配置/源码/凭据）
   └ POST /change_port -d port=31337 -d dir=/path → 截断+改写目标 robot.env（配置篡改/破坏）
```

## 5. 影响范围

- 未授权任意文件读（与 /download_log、/run_script 并列的第三条读原语）；
- 未授权任意 `robot.env` 截断改写（可破坏 LCM 端口/网络配置 → 后续功能异常，或篡改
  环境使运动控制/监控模块加载失败）。

## 6. 修复建议

1. `selected_dir` 做 `realpath` 后校验在 `ENV_ROOT` 内 + 白名单目录枚举；
2. `get_robot_env` 拒绝绝对路径与 `..` 段；`change_port` 用原子写+备份。

## 7. 证据

- 外部审计原文：`AUD-web-robot-env-path-traversal.md`
- 我方反汇编：`analysis/webmgr_extract/custom_dis.txt`（robot_env.py 段）
