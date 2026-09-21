---
编号: GAL-002
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: Flask管理后台未授权RCE-1
---
# GAL-002 伽利略（Galileo）机器人 Flask 管理后台未授权 RCE 漏洞复现报告

## 1. 一句话结论

- # 伽利略（Galileo）机器人 Flask 管理后台未授权 RCE 漏洞复现报告
- \| 漏洞类型 \| 未授权访问 + 任意命令执行（RCE） \|
- ## 1. 漏洞概述
- 的 tar 包实现**任意命令执行（RCE）**。
- **影响**：同一 WiFi/LAN 内任意设备可零交互地：

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）四足机器人（SSID `C1W-1.0-007`） \|
- \| 漏洞组件 \| Flask Web 管理后台（`/home/galileo/galileo-web-manger`，5000 端口，Werkzeug/3.1.4） \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- 机器人 5000 端口运行一个 **Flask Web 管理后台**（页面标题 "galileo robot 管理工具"），
- "集成包"，服务端解压后**自动查找并执行包内的 `install.sh` 脚本**（实测返回
- ⑤ 完全控制机器人（读固件、改配置、植入持久化后门）

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- **完全无认证**：直接 `GET /` 即返回完整管理页面。后台提供 `/upload` 接口接收 `.tar.gz`
- ### 3.2 高危 API 端点（均无认证）
- f = request.files['file']           # 无认证、无文件类型校验
- tar.extractall(tempdir)              # 解压（未做路径穿越防护）
- curl http://192.168.2.1:5000/          # 直接返回管理页面，无认证
- 2. `/upload` 做文件类型/大小/路径穿越校验，且**不自动执行**包内脚本；

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- \| 权限 \| galileo（uid=1000）；配合 sudo 免密可提权 root \|
- \| 测试机 \| 与机器人同 WiFi 的 root 手机（经 adb 中转） \|
- **影响**：同一 WiFi/LAN 内任意设备可零交互地：
- - 配合 sudo 免密（见同目录提权漏洞）一步提权到 root，完全接管机器人。
- │     若命令以 sudo 开头 → 直接 root(uid=0)（见 sudo 提权漏洞）
- ⑤ 完全控制机器人（读固件、改配置、植入持久化后门）

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

# 伽利略（Galileo）机器人 Flask 管理后台未授权 RCE 漏洞复现报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）四足机器人（SSID `C1W-1.0-007`） |
| 系统 | Ubuntu 22.04（OpenSSH 8.9p1，Python 3.10.12） |
| 主控 | Quectel WiFi 模组（BC:2A:33），AP `192.168.2.1` |
| 漏洞组件 | Flask Web 管理后台（`/home/galileo/galileo-web-manger`，5000 端口，Werkzeug/3.1.4） |
| 漏洞类型 | 未授权访问 + 任意命令执行（RCE） |
| 权限 | galileo（uid=1000）；配合 sudo 免密可提权 root |
| 测试机 | 与机器人同 WiFi 的 root 手机（经 adb 中转） |
| 复现日期 | 2026-08-29 |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

机器人 5000 端口运行一个 **Flask Web 管理后台**（页面标题 "galileo robot 管理工具"），
**完全无认证**：直接 `GET /` 即返回完整管理页面。后台提供 `/upload` 接口接收 `.tar.gz`
"集成包"，服务端解压后**自动查找并执行包内的 `install.sh` 脚本**（实测返回
"File uploaded and installed successfully"），且执行用户为 galileo（uid=1000）。
因此任何与机器人同网络的攻击者，无需任何凭据，即可通过上传一个含恶意 `install.sh`
的 tar 包实现**任意命令执行（RCE）**。

**影响**：同一 WiFi/LAN 内任意设备可零交互地：
- 执行任意命令（galileo 身份）；
- 读写 `/home/galileo` 下 galileo 属主的数据；
- 配合 sudo 免密（见同目录提权漏洞）一步提权到 root，完全接管机器人。

## 2. 攻击链

```
攻击者（同 WiFi，拿到 192.168.2.x）
   │  ① 连入机器人 AP（C1W-1.0-007 / 88888888，公开弱口令）
   ▼
② 直接 GET http://192.168.2.1:5000/   → 返回管理页面，无任何登录/认证
   ▼
③ POST /upload，multipart 上传恶意 evil.tar.gz（内含 install.sh，内容为任意命令）
   │     后端 tar 解压 → 发现 install.sh → subprocess 执行
   ▼
④ install.sh 以 galileo(uid=1000) 执行任意命令 → RCE
   │     若命令以 sudo 开头 → 直接 root(uid=0)（见 sudo 提权漏洞）
   ▼
⑤ 完全控制机器人（读固件、改配置、植入持久化后门）
```

## 3. 协议与漏洞细节

### 3.1 未授权访问

- `GET /` 直接返回管理页面（Content-Type: text/html，lang="zh-CN"），无 302 跳登录、无 cookie 校验。
- 页面标题：`<title>galileo robot 管理工具</title>`。
- 功能区块：集成包文件上传、日志下载、WiFi 管理、robot.env 配置、脚本功能、操作日志。

### 3.2 高危 API 端点（均无认证）

| 端点 | 方法 | 功能 | 危害 |
|---|---|---|---|
| `/upload` | POST | 上传并解压 .tar.gz 集成包 | **自动执行 install.sh → RCE** |
| `/run_script` | POST | 执行脚本（`{script, args}`） | 执行任意已存在脚本 + 任意文件读取 |
| `/change_port` | POST | 修改端口 | 配置篡改 |
| `/network/connect_wifi` | POST | 连接 WiFi | 网络劫持 |
| `/network/interface/toggle` | POST | 切换网络接口 | DoS/网络接管 |

### 3.3 /upload 自动执行 install.sh（核心漏洞）

实测行为：
- 上传不含 install.sh 的 tar 包 → 返回 `"File uploaded successfully (no install script found)"`；
- 上传含 install.sh 的 tar 包 → 返回 `"File uploaded and installed successfully"`，且
  install.sh 内的 `touch /tmp/pwned_galileo` 确实执行（后续经 `/run_script` 验证文件存在）。

后端逻辑（推断自行为）：
```python
# 伪代码
@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']           # 无认证、无文件类型校验
    save(f)                              # 保存到临时目录
    tar.extractall(tempdir)              # 解压（未做路径穿越防护）
    install = tempdir / 'install.sh'     # 查找 install.sh
    if install.exists():
        subprocess.run(['sh', str(install)])   # ← 直接执行，shell 语义
        return 'File uploaded and installed successfully'
    return 'File uploaded successfully (no install script found)'
```

### 3.4 执行权限

- install.sh 以 **galileo（uid=1000）** 身份执行（实测 `id` → `uid=1000(galileo)`）。
- Flask 服务本身可能以 root 或 galileo 运行，但 install.sh 落到的执行身份是 galileo。

## 4. 复现步骤

```bash
# 前置：连入机器人 AP C1W-1.0-007（密码 88888888）

# 1. 验证未授权
curl http://192.168.2.1:5000/          # 直接返回管理页面，无认证

# 2. 一键 RCE（见 exploit.py）
python3 exploit.py 192.168.2.1 "id"
# 期望：响应 "File uploaded and installed successfully"

# 3. 验证命令执行（写文件后经任意文件读取回读）
python3 exploit.py 192.168.2.1 "id > /tmp/pwned_result.txt"

# 4. 直接提权到 root（配合 sudo 免密）
python3 exploit.py 192.168.2.1 "sudo id > /tmp/root_result.txt"
```

## 5. 影响范围

- 任意命令执行（galileo 身份），可读 `/home/galileo` 下用户数据；
- 配合 sudo 免密提权到 root，完全接管机器人（读全盘、改固件、植入后门）；
- 可进一步用于横向移动（机器人所在 WiFi/以太网内的其他设备）。

## 6. 修复建议

1. Flask 后台增加认证（登录 + 会话/token）；
2. `/upload` 做文件类型/大小/路径穿越校验，且**不自动执行**包内脚本；
3. `/run_script` 白名单限制脚本路径，禁止任意路径/参数；
4. 收敛 galileo 用户的 sudo 权限（见 sudo 提权漏洞）；
5. 修改 AP 默认弱口令 `88888888`。

## 7. 证据

- `evidence/explore.txt`：文件系统结构探测结果（含 /home/galileo 目录、执行用户）
- `evidence/` 其余文件：漏洞验证过程中的原始响应
