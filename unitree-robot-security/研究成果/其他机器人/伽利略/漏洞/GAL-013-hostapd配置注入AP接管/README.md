---
编号: GAL-013
验证状态: 动态确认
严重程度: 中
披露状态: 内部研究
源平台: 伽利略
源候选目录: hostapd配置注入AP接管-2
---
# GAL-013 伽利略（Galileo）机器人 /api/ssid hostapd.conf 配置注入 → AP 接管/断网 漏洞报告

## 1. 一句话结论

- \| 权限 \| 未授权 → 机器人 AP 凭据篡改（接管热点）或 AP 永久瘫痪（DoS） \|
- ## 1. 漏洞概述
- 未授权接口 `POST /api/ssid` 允许设置机器人 AP 的 SSID。后端 `set_ssid` 仅校验
- 携带 `\n` 的 SSID 即可向 hostapd.conf **注入任意配置指令**（32 字节预算内）：
- - `wpa=0` / `auth_algs=0` → 关闭加密（开放网络，任意接入）;

## 2. 影响产品与版本

- \| 目标设备 \| 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） \|
- \| 漏洞组件 \| Flask 管理后台 `routes/init_status.py::api_ssid` → `modules/init_status.py::set_ssid` \|
- \| 授权边界 \| 仅对自有设备、隔离环境进行 \|
- - 固件路径：`galileo-web-manger`（PyInstaller → modules/init_status.pyc）

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- 详见下方脱敏研究正文和材料清单。

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- ; 替换与写回（无换行/控制字符过滤）
- ## 5. 影响范围
- - 与漏洞 4 的"切 WiFi 断 AP"互为补充：本条影响的是**重启后仍然生效**的持久断网。

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

# 伽利略（Galileo）机器人 /api/ssid hostapd.conf 配置注入 → AP 接管/断网 漏洞报告

| 项 | 值 |
|---|---|
| 目标设备 | 伽利略（Galileo）GRQ05W（固件 galileo-inter 1.0.44） |
| 漏洞组件 | Flask 管理后台 `routes/init_status.py::api_ssid` → `modules/init_status.py::set_ssid` |
| 漏洞类型 | 配置注入（换行未过滤写入 /etc/hostapd/hostapd.conf 并重启 hostapd） |
| 权限 | 未授权 → 机器人 AP 凭据篡改（接管热点）或 AP 永久瘫痪（DoS） |
| 复现日期 | 2026-08-29（字节码级证据完整；实际接管效果依赖设备 hostapd.conf 布局，待实机确认） |
| 授权边界 | 仅对自有设备、隔离环境进行 |

---

## 1. 漏洞概述

未授权接口 `POST /api/ssid` 允许设置机器人 AP 的 SSID。后端 `set_ssid` 仅校验
**非空**与 **≤32 字节（UTF-8）**，**不过滤换行符**，随后用正则把 `hostapd.conf` 中
`ssid=` 一行整体替换为 `ssid=<用户输入>` 再写回、并**重启 hostapd**：

```python
new_content = re.sub(r'^ssid\s*=.*$', f'ssid={new_ssid}', content, flags=re.MULTILINE)
open(conf_file, 'w').write(new_content)
restart_hostapd()   # systemctl restart hostapd / service hostapd restart
```

携带 `\n` 的 SSID 即可向 hostapd.conf **注入任意配置指令**（32 字节预算内）：

- `wpa_passphrase=新密码` → **重置 AP 密码**（配合 ssid 改名 = 热点接管，原用户被踢）；
- `wpa=0` / `auth_algs=0` → 关闭加密（开放网络，任意接入）;
- `channel=999` 等非法值 → hostapd 启动失败 → **AP 永久下线**（未授权远程断网 DoS，
  且重启机器人前无法自愈——注意该接口经 WiFi 即达，"断 AP"即断自己的管理通道）。

## 2. 证据（PyInstaller 解包 modules/init_status.pyc 反汇编）

```
; 长度校验（唯一的输入校验）
265  len(new_ssid.encode('utf-8')) > 32 → 拒绝
258  new_ssid.strip() 非空
; 替换与写回（无换行/控制字符过滤）
281  re.sub('^ssid\\s*=.*$', 'ssid=' + new_ssid, content, flags=MULTILINE)
289  open(conf_file,'w').write(new_content)
295  restart_hostapd()
```

- 路由：`@init_status_bp.route('/api/ssid', methods=['GET','POST'])`，JSON 键 `ssid`
- 配置文件路径来自 `web_config.json` → `HOSTAPD_CONF=/etc/hostapd/hostapd.conf`
- 接口无任何认证（同后台全部接口）

## 3. 攻击链

```
攻击者（同 WiFi）
   │ POST /api/ssid  {"ssid": "C1W\nwpa_passphrase=pwned123"}
   ▼
set_ssid 换行注入写 hostapd.conf → restart hostapd
   ▼
┌─ 密码/加密被改 → 原用户失联，攻击者以新凭据独占 AP（AP 接管）
└─ 配置非法 → hostapd 启动失败 → AP 永久瘫痪（未授权 DoS）
```

## 4. 复现

```bash
# AP 密码重置（注入 wpa_passphrase；注意 hostapd 后出现的同名键优先生效，若原文件
# 在 ssid 行之后已有 wpa_passphrase，需选择不被覆盖的键或制造 DoS）
python exploit.py 192.168.2.1 --inject "wpa_passphrase=pwned123"
# 纯断网 DoS（非法信道号使 hostapd 起不来）
python exploit.py 192.168.2.1 --inject "channel=999"
# 恢复：需物理接触或经 Web 管理器（若 AP 已断则需有线/重启）
```

## 5. 影响范围

- 未授权篡改机器人 AP 凭据/加密 → 热点接管（后续所有"同网段"漏洞的准入门槛被重置为攻击者掌握）；
- 未授权使 AP 永久瘫痪（机器人遥控/管理通道全断，远程无法恢复）；
- 与漏洞 4 的"切 WiFi 断 AP"互为补充：本条影响的是**重启后仍然生效**的持久断网。

## 6. 修复建议

1. `set_ssid` 拒绝含 `\r\n\0` 及不可打印字符的 SSID（或白名单 `[ -~]`）；
2. `re.sub` 的**替换串**改用 `lambda m: 'ssid=' + safe_ssid` 避免替换串转义歧义；
3. 写配置前备份、失败自动回滚（hostapd 重启失败时恢复原文件）。

## 7. 证据

- `evidence/set_ssid_disassembly.txt`：set_ssid 反汇编关键段（校验/替换/写回/重启）
- 固件路径：`galileo-web-manger`（PyInstaller → modules/init_status.pyc）
- 待实机确认项：设备 /etc/hostapd/hostapd.conf 的键顺序（决定注入键是否被后位同名键覆盖）
