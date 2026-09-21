# 优必选人型 研究索引

候选主题经重复合并后形成 26 份权威报告。

| 编号 | 报告 | 验证状态 |
|---|---|---|
| [UBH-001](漏洞/UBH-001-EtherCAT-FoE无签名固件刷写/README.md) | EtherCAT-FoE无签名固件刷写 | 静态确认 |
| [UBH-002](漏洞/UBH-002-EtherCAT-任意SDO读写-无认证/README.md) | EtherCAT-任意SDO读写-无认证 | 静态确认 |
| [UBH-003](漏洞/UBH-003-EtherCAT-原始关节指令无钳位/README.md) | EtherCAT-原始关节指令无钳位 | 静态确认 |
| [UBH-004](漏洞/UBH-004-FastAPI-5000无认证信息泄露与docs暴露/README.md) | FastAPI-5000无认证信息泄露与docs暴露 | 动态确认 |
| [UBH-005](漏洞/UBH-005-agora-遥操作AppID硬编码云端注入/README.md) | agora-遥操作AppID硬编码云端注入 | 静态确认 |
| [UBH-006](漏洞/UBH-006-api-export路径穿越任意文件读到双板root/README.md) | api-export路径穿越任意文件读到双板root | 动态确认 |
| [UBH-007](漏洞/UBH-007-api-expression管理-无认证上传篡改-lead/README.md) | api-expression管理-无认证上传篡改-lead | 候选 |
| [UBH-008](漏洞/UBH-008-api-rename-folder任意目录移动/README.md) | api-rename-folder任意目录移动 | 静态确认 |
| [UBH-009](漏洞/UBH-009-api-sysupload任意路径写-宿主root-RCE/README.md) | api-sysupload任意路径写-宿主root-RCE | 动态确认 |
| [UBH-010](漏洞/UBH-010-api-sysupload任意路径写跨板SFTP-RCE/README.md) | api-sysupload任意路径写跨板SFTP-RCE | 动态确认 |
| [UBH-011](漏洞/UBH-011-cc_api-jsonrpc零认证远程控制/README.md) | cc_api-jsonrpc零认证远程控制 | 静态确认 |
| [UBH-012](漏洞/UBH-012-emb-request_shutdown一字节双板关机/README.md) | emb-request_shutdown一字节双板关机 | 静态确认 |
| [UBH-013](漏洞/UBH-013-emb-upgrade无签名MCU固件刷写/README.md) | emb-upgrade无签名MCU固件刷写 | 静态确认 |
| [UBH-014](漏洞/UBH-014-executecmd-蓝牙技能system执行/README.md) | executecmd-蓝牙技能system执行 | 候选 |
| [UBH-015](漏洞/UBH-015-jetson-启动链测试签名固件可重签/README.md) | jetson-启动链测试签名固件可重签 | 静态确认 |
| [UBH-016](漏洞/UBH-016-jetson-调试UART无认证root-shell/README.md) | jetson-调试UART无认证root-shell | 动态确认 |
| [UBH-017](漏洞/UBH-017-list-files任意递归列目录全盘文件泄露-1到ssh/README.md) | list-files任意递归列目录全盘文件泄露-1到ssh | 动态确认 |
| [UBH-018](漏洞/UBH-018-lora-ecc_control零认证RF命令帧/README.md) | lora-ecc_control零认证RF命令帧 | 静态确认 |
| [UBH-019](漏洞/UBH-019-map_http_node-Zip-Slip任意文件写/README.md) | map_http_node-Zip-Slip任意文件写 | 静态确认 |
| [UBH-020](漏洞/UBH-020-motion-运动控制服务无认证与重放检查关闭/README.md) | motion-运动控制服务无认证与重放检查关闭 | 静态确认 |
| [UBH-021](漏洞/UBH-021-mqtt-云端fileDownloadLink命令执行/README.md) | mqtt-云端fileDownloadLink命令执行 | 静态确认 |
| [UBH-022](漏洞/UBH-022-rosbridge-9090无认证订阅发布与服务调用/README.md) | rosbridge-9090无认证订阅发布与服务调用 | 静态确认 |
| [UBH-023](漏洞/UBH-023-udoke未授权WS终端容器Root-RCE/README.md) | udoke未授权WS终端容器Root-RCE | 动态确认 |
| [UBH-024](漏洞/UBH-024-voice-无认证语音服务与ASR堆越界读/README.md) | voice-无认证语音服务与ASR堆越界读 | 静态确认 |
| [UBH-025](漏洞/UBH-025-wifi-set_ap命令注入到root/README.md) | wifi-set_ap命令注入到root | 静态确认 |
| [UBH-026](漏洞/UBH-026-硬编码凭证全线泄露/README.md) | 硬编码凭证全线泄露 | 静态确认 |

攻击链仅在完成多漏洞关系复核后建立；当前报告正文和材料清单以各漏洞目录为准。

## 攻击链

- [UBH-CHAIN-001 sysupload 到跨板 root](攻击链/UBH-CHAIN-001-sysupload到跨板root/README.md)
- [UBH-CHAIN-002 任意读取到跨板 root](攻击链/UBH-CHAIN-002-任意读取到跨板root/README.md)
