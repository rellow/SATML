# Unitree Robot Security Research

This repository is used within SIG-Void to organize authorized security research, vulnerability validation, attack chains, AI execution traces, and paper materials for Unitree GO2, R1, and other robot platforms. This repository is not a firmware mirror and does not contain complete vendor firmware, unsanitized credentials, or users' Claude configuration.

## Research Overview

- GO2: 28 stable findings. Start with the [GO2 research index](研究成果/GO2/README.md).
- R1: 43 stable findings. Start with the [R1 research index](研究成果/R1/README.md).
- Cross-model: 2 same-origin findings. Start with the [cross-model research index](研究成果/跨型号/README.md).
- Other robots: Galileo, UBTECH humanoid, and UBTECH AI Wukong EDU. Start with the [other-robot research index](研究成果/其他机器人/README.md).
- Cross-robot: issues shared across different robot platforms. Start with the [cross-robot research index](研究成果/跨机器人/README.md).

## Important Confirmed Vulnerabilities

| ID | Name | Model | Validation Status |
|---|---|---|---|
| [G2-001](研究成果/GO2/漏洞/G2-001-零凭证未授权控制/README.md) | Zero-credential unauthorized control | GO2 | Dynamically confirmed |
| [G2-002](研究成果/GO2/漏洞/G2-002-编程执行器到-root-RCE/README.md) | Programmable actuator to root RCE | GO2 | Dynamically confirmed |
| [G2-004](研究成果/GO2/漏洞/G2-004-OTA-固件远程获取链/README.md) | Remote OTA firmware acquisition chain | GO2 | Dynamically confirmed |
| [G2-013](研究成果/GO2/漏洞/G2-013-UDP-伪发现以-SN-为唯一凭据/README.md) | Spoofed UDP discovery using SN as the sole credential | GO2 | Dynamically confirmed |
| [G2-015](研究成果/GO2/漏洞/G2-015-BLE-握手零熵与授权态残留/README.md) | BLE handshake zero entropy and residual authorization state | GO2 | Dynamically confirmed |
| [R1-001](研究成果/R1/漏洞/R1-001-audio_detect-socket-to-shell/README.md) | audio_detect socket-to-shell | R1 | Dynamically confirmed |
| [R1-002](研究成果/R1/漏洞/R1-002-App-WebView-桥劫持/README.md) | App WebView bridge hijacking | R1 | Dynamically confirmed |
| [R1-003](研究成果/R1/漏洞/R1-003-arm_service-无鉴权-RPC/README.md) | Unauthenticated arm_service RPC | R1 | Dynamically confirmed |
| [R1-004](研究成果/R1/漏洞/R1-004-arm_service-任意文件投放/README.md) | arm_service arbitrary file placement | R1 | Dynamically confirmed |
| [R1-005](研究成果/R1/漏洞/R1-005-arm_service-rename-路径穿越/README.md) | arm_service rename path traversal | R1 | Dynamically confirmed |
| [R1-006](研究成果/R1/漏洞/R1-006-chat_go-知识库路径穿越写入/README.md) | chat_go knowledge-base path-traversal write | R1 | Dynamically confirmed |
| [R1-007](研究成果/R1/漏洞/R1-007-OTA-固件远程获取/README.md) | Remote OTA firmware acquisition | R1 | Dynamically confirmed |
| [R1-008](研究成果/R1/漏洞/R1-008-TURN-中继滥用/README.md) | TURN relay abuse | R1 | Dynamically confirmed |
| [R1-009](研究成果/R1/漏洞/R1-009-固件硬编码云凭据泄露/README.md) | Hard-coded cloud credential exposure in firmware | R1 | Dynamically confirmed |
| [R1-010](研究成果/R1/漏洞/R1-010-gpt-proxy-以-SN-认证/README.md) | gpt-proxy authentication by SN | R1 | Dynamically confirmed |
| [R1-011](研究成果/R1/漏洞/R1-011-云端知识库未授权写入/README.md) | Unauthorized cloud knowledge-base write | R1 | Dynamically confirmed |
| [R1-012](研究成果/R1/漏洞/R1-012-共享-aes_key-体系失效/README.md) | Shared aes_key scheme failure | R1 | Dynamically confirmed |
| [UT-001](研究成果/跨型号/漏洞/UT-001-btgatt-server-分片重组溢出到-root-RCE/README.md) | btgatt-server fragment-reassembly overflow to root RCE | Cross-model | Dynamically confirmed |
| [UT-002](研究成果/跨型号/漏洞/UT-002-AES-GCM-解密先写后验栈溢出/README.md) | AES-GCM write-before-verify stack overflow | Cross-model | Dynamically confirmed |

## Attack Chains

| ID | Name | Status |
|---|---|---|
| [GO2-CHAIN-001](研究成果/GO2/攻击链/GO2-CHAIN-001-零凭证接入到-root-RCE/README.md) | Zero-credential access to root RCE | Dynamically closed-loop |
| [GO2-CHAIN-002](研究成果/GO2/攻击链/GO2-CHAIN-002-BLE-配网到网络劫持/README.md) | BLE provisioning to network hijacking | Pending dynamic closure |
| [R1-CHAIN-001](研究成果/R1/攻击链/R1-CHAIN-001-arm_service-文件投放与-rename-到-root/README.md) | arm_service file placement + rename to root | Dynamically closed-loop |
| [R1-CHAIN-002](研究成果/R1/攻击链/R1-CHAIN-002-chat_go-写入到-bashrunner-root/README.md) | chat_go write to bashrunner root | Dynamically closed-loop |
| [UT-CHAIN-001](研究成果/跨型号/攻击链/UT-CHAIN-001-BLE-分片重组到-root-命令执行/README.md) | BLE fragment reassembly to root command execution | Dynamically closed-loop on both models |

## How to Read the Repository

1. Start in [Research Results](研究成果/README.md) and choose a model.
2. Open the canonical vulnerability README for the finding.
3. Follow its reproduction materials, evidence, and [AI session index](AI轨迹/会话索引.md).
4. For paper-to-evidence traceability, see the [paper claim–evidence mapping](论文/数据表/论文结论-证据对应表.md).

## Confidentiality and Disclosure

This repository must remain private. Before any external sharing, public disclosure, or vendor submission, read [SECURITY.md](SECURITY.md) and rerun the credential scan and material review.

> **Translation note:** Human-facing documentation is being translated to English on this branch. Raw AI-session transcripts and captured tool outputs are retained in their original language because they are provenance artifacts and should not be rewritten.
