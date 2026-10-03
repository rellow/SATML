# Cross-Model Research Index

| ID | Vulnerability | Validation Status | Impact | Attack Chain | Reproduction | AI Trace |
|---|---|---|---|---|---|---|
| [UT-001](漏洞/UT-001-btgatt-server-分片重组溢出到-root-RCE/README.md) | btgatt-server fragment-reassembly overflow to root RCE | Dynamically confirmed | Successful exploitation can execute commands in a high-privilege robot service context | UT-CHAIN-001 | [Manifest](漏洞/UT-001-btgatt-server-分片重组溢出到-root-RCE/复现/材料清单.md) | [CC-GO2-002, CC-R1-002](../../AI轨迹/会话索引.md) |
| [UT-002](漏洞/UT-002-AES-GCM-解密先写后验栈溢出/README.md) | AES-GCM write-before-verify stack overflow | Dynamically confirmed | Can crash a high-privilege service; under suitable memory-layout conditions it may further enable control-flow hijacking | — | [Manifest](漏洞/UT-002-AES-GCM-解密先写后验栈溢出/复现/材料清单.md) | [CC-GO2-001, CC-R1-002](../../AI轨迹/会话索引.md) |
