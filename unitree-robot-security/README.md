# 宇树机器人安全研究

本仓库用于 SIG-Void 内部整理宇树 GO2、R1 及其他机器人平台的授权安全研究、漏洞验证、攻击链、AI 执行轨迹与论文材料。仓库不是固件镜像，不包含完整原厂固件、未脱敏凭据或用户 Claude 配置。

## 研究概览

- GO2：28 个稳定漏洞，入口见 [GO2 研究索引](研究成果/GO2/README.md)。
- R1：43 个稳定漏洞，入口见 [R1 研究索引](研究成果/R1/README.md)。
- 跨型号：2 个同源漏洞，入口见 [跨型号研究索引](研究成果/跨型号/README.md)。
- 其他机器人：伽利略、优必选人型、优必选 AI 悟空 EDU，入口见 [其他机器人研究索引](研究成果/其他机器人/README.md)。
- 跨机器人：不同机器人之间的共性问题，入口见 [跨机器人研究索引](研究成果/跨机器人/README.md)。

## 重要确认漏洞

| 编号 | 名称 | 型号 | 验证状态 |
|---|---|---|---|
| [G2-001](研究成果/GO2/漏洞/G2-001-零凭证未授权控制/README.md) | 零凭证未授权控制 | GO2 | 动态确认 |
| [G2-002](研究成果/GO2/漏洞/G2-002-编程执行器到-root-RCE/README.md) | 编程执行器到 root RCE | GO2 | 动态确认 |
| [G2-004](研究成果/GO2/漏洞/G2-004-OTA-固件远程获取链/README.md) | OTA 固件远程获取链 | GO2 | 动态确认 |
| [G2-013](研究成果/GO2/漏洞/G2-013-UDP-伪发现以-SN-为唯一凭据/README.md) | UDP 伪发现以 SN 为唯一凭据 | GO2 | 动态确认 |
| [G2-015](研究成果/GO2/漏洞/G2-015-BLE-握手零熵与授权态残留/README.md) | BLE 握手零熵与授权态残留 | GO2 | 动态确认 |
| [R1-001](研究成果/R1/漏洞/R1-001-audio_detect-socket-to-shell/README.md) | audio_detect socket-to-shell | R1 | 动态确认 |
| [R1-002](研究成果/R1/漏洞/R1-002-App-WebView-桥劫持/README.md) | App WebView 桥劫持 | R1 | 动态确认 |
| [R1-003](研究成果/R1/漏洞/R1-003-arm_service-无鉴权-RPC/README.md) | arm_service 无鉴权 RPC | R1 | 动态确认 |
| [R1-004](研究成果/R1/漏洞/R1-004-arm_service-任意文件投放/README.md) | arm_service 任意文件投放 | R1 | 动态确认 |
| [R1-005](研究成果/R1/漏洞/R1-005-arm_service-rename-路径穿越/README.md) | arm_service rename 路径穿越 | R1 | 动态确认 |
| [R1-006](研究成果/R1/漏洞/R1-006-chat_go-知识库路径穿越写入/README.md) | chat_go 知识库路径穿越写入 | R1 | 动态确认 |
| [R1-007](研究成果/R1/漏洞/R1-007-OTA-固件远程获取/README.md) | OTA 固件远程获取 | R1 | 动态确认 |
| [R1-008](研究成果/R1/漏洞/R1-008-TURN-中继滥用/README.md) | TURN 中继滥用 | R1 | 动态确认 |
| [R1-009](研究成果/R1/漏洞/R1-009-固件硬编码云凭据泄露/README.md) | 固件硬编码云凭据泄露 | R1 | 动态确认 |
| [R1-010](研究成果/R1/漏洞/R1-010-gpt-proxy-以-SN-认证/README.md) | gpt-proxy 以 SN 认证 | R1 | 动态确认 |
| [R1-011](研究成果/R1/漏洞/R1-011-云端知识库未授权写入/README.md) | 云端知识库未授权写入 | R1 | 动态确认 |
| [R1-012](研究成果/R1/漏洞/R1-012-共享-aes_key-体系失效/README.md) | 共享 aes_key 体系失效 | R1 | 动态确认 |
| [UT-001](研究成果/跨型号/漏洞/UT-001-btgatt-server-分片重组溢出到-root-RCE/README.md) | btgatt-server 分片重组溢出到 root RCE | 跨型号 | 动态确认 |
| [UT-002](研究成果/跨型号/漏洞/UT-002-AES-GCM-解密先写后验栈溢出/README.md) | AES-GCM 解密先写后验栈溢出 | 跨型号 | 动态确认 |

## 攻击链

| 编号 | 名称 | 状态 |
|---|---|---|
| [GO2-CHAIN-001](研究成果/GO2/攻击链/GO2-CHAIN-001-零凭证接入到-root-RCE/README.md) | 零凭证接入到 root RCE | 已动态闭环 |
| [GO2-CHAIN-002](研究成果/GO2/攻击链/GO2-CHAIN-002-BLE-配网到网络劫持/README.md) | BLE 配网到网络劫持 | 待动态闭环 |
| [R1-CHAIN-001](研究成果/R1/攻击链/R1-CHAIN-001-arm_service-文件投放与-rename-到-root/README.md) | arm_service 文件投放与 rename 到 root | 已动态闭环 |
| [R1-CHAIN-002](研究成果/R1/攻击链/R1-CHAIN-002-chat_go-写入到-bashrunner-root/README.md) | chat_go 写入到 bashrunner root | 已动态闭环 |
| [UT-CHAIN-001](研究成果/跨型号/攻击链/UT-CHAIN-001-BLE-分片重组到-root-命令执行/README.md) | BLE 分片重组到 root 命令执行 | 已动态闭环（双型号） |

## 阅读路径

1. 从 [研究成果](研究成果/README.md) 选择型号；
2. 打开唯一权威漏洞 README；
3. 跟随其中的复现、证据和 [AI 会话索引](AI轨迹/会话索引.md)；
4. 论文引用关系见 [论文结论—证据对应表](论文/数据表/论文结论-证据对应表.md)。

## 保密与披露

仓库必须保持 Private。任何外发、公开披露或向厂商提交前，请先阅读 [SECURITY.md](SECURITY.md)，并重新执行凭据扫描与材料审查。
