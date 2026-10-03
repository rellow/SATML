---
ID: UBW-002
validation_status: dynamically confirmed
severity: critical
disclosure_status: internal research
source_platform: UBTECH AI Wukong EDU
source_candidate_directory: 云端任意机器人未授权控制
---
# UBW-002 UBTECH Wukong (Alpha Mini) Cloud IM Chain: Unauthorized Remote Control — Complete Analysis and Reproduction Guide

## 1. Summary

- # UBTECH Wukong (Alpha Mini) Cloud IM Chain: Unauthorized Remote Control — Complete Analysis and Reproduction Guide
- ## 1. Executive Summary
- **A robot serial number (SN) is sufficient to reach the tested cloud-control path: no user account and no shared local network with the target are required. On the researcher-owned device, the chain was dynamically closed end to end rather than inferred only from static analysis.**
- Severity: **Critical** in the source report because the path is unauthenticated, WAN-reachable, potentially scalable, and affects both privacy and physical safety for a child-oriented product.
- ## 2. Impact Overview

## 2. Affected Products and Versions

- > Version: 2026-07-31 · Environment: SRC-authorized test environment · Validated device: researcher-owned Wukong Education Edition (SN=<其他机器人设备_01>, firmware v1.6.3.919)
- Firmware for **five product lines** was publicly retrievable through the same signing system; three included complete system OTA packages.
- The source report identifies high-impact OTA handlers (cmd 313/314) that can instruct the robot to download and install upgrade packages. It further reports that the tested device trusted an **AOSP public test key** for OTA verification, creating a serious persistence risk if maliciously signed firmware could be accepted.
- `im/getInfo` is the UBTECH cloud endpoint that issues Tencent IM login credentials (`userSig`) to Apps/robots. The source report found that its protection depended on a static client-side secret recoverable from public App/firmware code, while the server did not enforce the expected time window, account existence, or meaningful rate limits.
- Three IM tenants (1400032988 / 1400059787 / 1400031700) were tested successfully with forged login credentials.
- **Wukong 2:** forged IM-tenant login was directly validated; because the firmware uses the same `persist.mini.sid` identity structure, application of the complete chain is treated as a strong inference rather than separately closed.
- **AlphaMini standard edition (X100):** likely falls under the default tenant based on the tested login behavior; the 1.26 GB system firmware had been acquired for follow-up validation.

## 3. Validation Status

`dynamically confirmed`. This status reflects the validation boundary of the source report; the migration process does not infer dynamic confirmation from directory names.

## 4. Attack Preconditions

Attack preconditions are defined by the sanitized research body below. Reproduction must use researcher-owned devices, isolated networks, and authorized environments and must not perform write, control, or destructive operations against third-party devices.

## 5. Root Cause

- ## 3. Vulnerability Root Cause: Six-Link Mechanism
- The source report found that the server did not enforce the expected signature time window, so otherwise valid signed requests could remain replayable.
- The core failure is an authentication and authorization chain in which client-distributed secrets can mint IM credentials, the IM tenant accepts those credentials, the robot does not validate the sender against its binding relationship, and a large handler surface is exposed behind that identity.
- Defense-in-depth recommendations in the source report include sender-binding checks before IM dispatch, secondary authentication plus anti-replay for high-risk commands, and replacement of the public OTA test trust root.

## 6. Attack Procedure

The source report's entry points, protocols, and sequencing are preserved in the sanitized research body in Section 13. This directory retains only minimal reproduction material and does not duplicate large raw evidence.

## 7. Impact

- # UBTECH Wukong (Alpha Mini) Cloud IM Chain: Unauthorized Remote Control — Complete Analysis and Reproduction Guide
- Severity: **Critical** in the source report because the path is unauthenticated, WAN-reachable, potentially scalable, and affects child privacy and physical safety.
- ## 2. Impact Overview
- ### 2.2 Persistent Control: From One Message to Long-Lived Compromise
- The handler table includes code-execution, OTA, debugging, reset, and real-time audio/video functionality; the source report differentiates dynamically validated behavior from code-only evidence.
- ### 2.4 Social-Engineering Channel Against Children
- Because the product is designed for children, unauthorized contact-list modification and text-to-speech behavior can create a distinctive social-engineering risk beyond ordinary IoT compromise.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Imported scripts were text-sanitized; original scripts, logs, packet captures, and binaries not imported are recorded in the repository-level material manifest.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13. Source files are represented only by hashes and local storage paths; raw sensitive material is not copied into Git.

## 10. Recommendations

- Enforce authentication, fine-grained authorization, message-integrity validation, and replay protection at the entry point.
- Apply allowlists to paths, lengths, protocol fields, file types, and state transitions.
- Remove hard-coded credentials and rotate exposed material.
- Drop privileges for high-risk services and add audit logging and negative regression tests.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report. If such a record is added later, it will be registered in the [AI session index](../../../../../AI轨迹/会话索引.md).

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review credentials, device identifiers, evidence, and vendor-coordination status.

## 13. Sanitized Original Research Body

# UBTECH Wukong (Alpha Mini) Cloud IM Chain: Unauthorized Remote Control — Complete Analysis and Reproduction Guide

> Version: 2026-07-31 · Environment: SRC-authorized test environment · Validated device: researcher-owned Wukong Education Edition (SN=<其他机器人设备_01>, firmware v1.6.3.919)
> **Boundary statement:** all command execution was limited to the research team's own robot. For third-party devices, testing was limited to read-only online-status queries; no messages were delivered, no credentials were forged for those devices, and no data was read from them. This guide is for defensive research and responsible disclosure only.

---

## 1. Executive Summary

**A robot serial number (SN) is sufficient to reach the tested cloud-control path: no user account and no shared local network with the target are required. On the researcher-owned device, the chain was dynamically closed end to end rather than inferred only from static analysis.**

Key figures reported by the source study:

- A **six-link attack chain**, dynamically validated on the owned device.
- Roughly **110 remote command handlers** reachable behind the same unauthenticated dispatch path, including reset, Lua execution, OTA, and real-time video functionality.
- **Three Tencent IM tenants** accepted credentials derived from the same hard-coded static secret family, covering the first-generation Wukong Education Edition, Wukong 2, and a default product line.
- In a bounded sample around a known serial-number range, **50 of 101 candidates** corresponded to real devices according to the cloud online-status endpoint. This sampling result is not presented as a global population estimate.
- Firmware for **five product lines** was retrievable through the same signing system, including full-system OTA packages for three lines.

Severity: **Critical** in the source report because the path is unauthenticated, WAN-reachable, potentially scalable, and affects both privacy and physical safety for a child-oriented product.

---

## 2. Impact Overview

### 2.1 Potential for Scaled Device Disruption

The source report found that each prerequisite can be mechanically checked. Serial numbers follow a structured format, and `im/isOnline` accepts batched account queries and returns distinguishable online/offline/nonexistent states. In a bounded ±50 sample around one known device, 50 of 101 candidates mapped to real devices.

The command registry includes reset/clear-data functionality. Those destructive commands were **not executed against third-party devices**; their reachability is based on the same handler-dispatch mechanism that was dynamically validated with non-destructive commands.

### 2.2 Persistent Control and High-Privilege Paths

- **cmd 365 (DemoRunLuaScript):** the same handler was dynamically validated over the LAN path to reach system-context execution on the researcher-owned robot. The cloud IM path reaches that same handler according to the analyzed dispatch table.
- **cmd 313/314 (OTA download and upgrade):** the source report found that the tested device used an **AOSP public test key** as an OTA trust root, materially weakening firmware authenticity.
- **cmd 316 (ADB control):** the handler table includes a remote debugging-interface control operation.

The report separates these code-supported capabilities from the non-destructive commands that were actually executed through the cloud path.

### 2.3 Cameras, Microphones, and Remote Physical Behavior

- **cmd 704–709 (RTAV):** the analyzed command family can establish real-time audio/video behavior and includes a motion-control operation.
- **cmd 109:** the report dynamically validated reachability of the handler that returns video-room credentials when such a room exists; the research device had no active third-party session to access.
- **SetCameraPrivacyHandler:** analysis identified a remotely reachable camera-privacy control.

These findings make the cloud identity failure relevant to both privacy and physical-safety analysis.

### 2.4 Child-Focused Social-Engineering Risk

Wukong is a child-oriented educational robot. The source report dynamically validated two primitives that create a distinct social-engineering surface:

1. **cmd 120 (contact import):** test data could be inserted into the researcher-owned robot's address book. A maliciously labeled contact could misrepresent whom a child is calling.
2. **cmd 91 (TTS):** the message path could cause the owned robot to speak supplied content.

The report treats these as security consequences of unauthorized command authority, not as claims about actual attacks on children.

### 2.5 Sensitive Data Exposure Without Normal Account Credentials

| Data | Channel | Evidence Level |
|---|---|---|
| Owner-account PII (userId/user name/nickname/avatar/binding time) | cloud `relation/getBindUsers?robotUserId=<SN>`, without the normal user token | dynamically validated on authorized data |
| Address-book phone numbers / call history | cmd 121 / 125 | dynamically validated using test data on the owned device |
| Registered face data | cmd 116 | handler execution validated; no face data existed on the test unit |
| Photo list / photos | cmd 112 / 111 / 53 | code-supported path |
| Emergency contact number | cmd 324 | code-supported path |
| Tencent DingDang TVS product credential | cmd 108 response | dynamically validated |
| Current network/IP information | cmd 311 | code-supported path |
| Device registration and online state | `equipment/listBySerialNum` / `im/isOnline` | dynamically validated |

The Education Edition did not expose a real-name identity system in the analyzed source tree; the report explicitly excludes national-ID numbers from the claimed attack surface.

### 2.6 Systemic IM Credential Failure

`im/getInfo` issues Tencent IM login credentials (`userSig`) for Apps and robots. The source report found that the endpoint depended on a static client-side secret recoverable from public App/firmware code and did not enforce the expected signature time window, account existence, or meaningful rate limits. Three IM tenants (1400032988 / 1400059787 / 1400031700) accepted forged credentials during authorized testing.

The report therefore characterizes the weakness as a product-line identity-system failure rather than a single isolated endpoint bug.

### 2.7 Product-Line Reach

- **Wukong 2:** forged login to its IM tenant was directly validated; applicability of the full chain is a strong inference based on shared firmware identity structure.
- **AlphaMini standard edition (X100):** likely associated with the tested default tenant; system firmware was acquired for follow-up validation.
- **Firmware supply-chain surface:** upgrade packages for five product lines (AlphaMini, AlphaMini2, AlphaMiniInEdu, and two Yanshee variants) were reachable through the same static signing system.

---

## 3. Vulnerability Root Cause: Six-Link Mechanism

```
SN (mDNS/BLE broadcast or cloud range enumeration)
 ① im/getInfo issues a forged userSig from a client-distributed static-secret scheme
 ② Tencent IM accepts the resulting credential for the tenant
 ③ C2C message delivery accepts the sender in the tested tenant configuration
 ④ Robot-side dispatcher does not compare the sender against the robot's binding relationship
 ⑤ ~110 registered handlers become reachable
 ⑥ Responses are returned over IM and correlated with the request
```

Key evidence anchors:

| Stage | Evidence |
|---|---|
| Static secret | App `com/common/channel/security/Auth.java`; robot `TencentIMManager.java:226` |
| Robot IM id = SN | `Robot2PhoneMsgMgr.java:22` → `persist.mini.sid`, also checked on the physical device |
| Missing sender validation | `RobotPhoneCommuniteProxy`: peer is used as the reply destination without binding/allowlist comparison |
| Command registry | `ImProtoLiteMsgRelation.java` (~110 handlers) and `IMCmdId.java` |

---

## 4. Affected Scope

| Product Line | Identifier | Status |
|---|---|---|
| Wukong Education Edition (AlphaMiniInEdu) | SDKAppID 1400032988 | **complete chain dynamically validated** |
| Wukong 2 (AlphaMini2/WK2) | SDKAppID 1400059787 | forged login validated; full-chain applicability is a strong inference based on shared firmware structure |
| Default product line (likely including AlphaMini X100) | SDKAppID 1400031700 | forged login validated |
| OTA / firmware surface | upgrade.ubtrobot.com | firmware for five product lines publicly reachable; X100/WK2/InEdu include full system OTA packages |
| Jimu / Cruzr / Walker / Yanshee system families | — | no evidence in this report that they share this IM/OTA system |

---

## 5. Reproduction Environment

- Internet-connected Windows/Linux/macOS computer.
- Node.js 18+ and Python 3 with `requests`.
- A **researcher-owned** Wukong robot connected to the Internet; it does not need to share the attacker's LAN for the cloud-path validation.
- Burp Suite may be used for HTTP inspection; the repository contains corresponding sanitized scripts and request-generation helpers.

## 6. Reproduction Procedure

The source package separates reproduction into four stages:

### Stage A: Cloud-API Validation

Authorized tests exercised the cloud credential-issuance, online-status, owner-binding, and device-registration endpoints using researcher-controlled identifiers and sanitized placeholders. The source scripts generate the signed requests and retain the exact request format in the authorized artifact.

The evidence establishes:

- `im/getInfo` returned a Tencent IM credential for a test identity that did not correspond to a normally registered user.
- `im/isOnline` distinguished real/online, real/offline, and nonexistent serial-number values in the bounded sample.
- `relation/getBindUsers` returned owner-binding information for the researcher-owned robot.
- `equipment/listBySerialNum` returned device-registration information under the same client-side signing system.

### Stage B: IM Chain Closure on the Owned Robot

The repository's `run_full_chain.js` automates credential acquisition, Tencent IM login, online-state validation, a non-destructive control query, and response correlation on the researcher-owned robot.

The retained log shows the sequence:

```
[step 1] im/getInfo ... returnCode=0
[step 2] Tencent IM login: actionStatus=OK
[step 3] im/isOnline: target -> Online
[step 4] C2C delivery of a non-destructive query: status=success
[robot response] battery and firmware information returned
[conclusion] cloud credential path → IM → robot dispatcher → correlated response
```

### Stage C: Specialized Test Scripts

The source package contains dedicated scripts for identity-login behavior, message delivery, non-destructive control queries, test-contact data, TTS, RTAV credential handling, and multi-tenant login. Their exact invocation syntax remains in the sanitized reproduction artifacts rather than being duplicated here.

### Stage D: Robot-Side Verification

The source report used local inspection on the researcher-owned robot to verify effects such as configuration changes and the mapping between `persist.mini.sid` and the IM identity.

### Troubleshooting

| Symptom | Source-Report Interpretation |
|---|---|
| `im/getInfo` returns nonzero status | Signature construction or timestamp formatting mismatch |
| Node login fails | Node dependencies not installed or network path to Tencent IM unavailable |
| command values >127 fail in the Web SDK | Known transport limitation of the test tooling; the report treats this as a tooling issue, not an authorization control |
| Robot does not respond | Robot offline or handler intentionally does not return a response |
| prodapi returns 400 | Strict Content-Length/body mismatch at the front-end load balancer |

---

## 7. Capability Matrix

The table below preserves the source report's distinction between dynamic evidence, handler-level evidence, and inference.

| Command / Function | Effect | Evidence Level |
|---|---|---|
| cmd 68 | Battery and firmware query | **dynamically validated** |
| cmd 108 | Returns TVS product credential | **dynamically validated** |
| cmd 99 | Writes owner nickname configuration | **dynamically validated** on the owned robot |
| cmd 120/121/125 | Test contact insertion / contact readback / call-history behavior | **dynamically validated with synthetic data** |
| cmd 116/112/111 | Face/photo data handlers | handler execution or code path validated; test unit had no corresponding private data |
| cmd 109 | Video-room credential handler | handler execution validated; no active third-party room was accessed |
| cmd 91 | TTS speech | delivery validated; handler is designed without a response |
| cmd 365 | Lua execution | code path supported; same handler dynamically validated over the LAN path |
| cmd 370/371 | Factory reset / clear data | code-supported only; destructive action not executed |
| cmd 312–315 | OTA update functions | code-supported |
| cmd 704–709 | RTAV / remote-motion family | code-supported |
| cmd 316 | ADB control | code-supported |
| NetConnectOneWifi | Network-reconfiguration primitive | code-supported |

## 8. Evidence and File Index

```
cloud_im_rce_package/
├── README.md
├── BURP_GUIDE.md
├── evidence/
│   ├── evidence_im_chain_20260731.log
│   ├── full_chain_run_20260731_124027.log
│   ├── relation_getBindUsers_redacted.json
│   ├── online_sample_scan_20260731_125356.log
│   ├── ota_enum_20260731_134711.json
│   ├── ota_firmware_urls_verified.json
│   ├── firmware/
│   └── *.py
├── screenshots/
└── scripts/
```

The repository manifest records which large firmware packages and sensitive raw artifacts remain outside Git. Any screenshot containing real third-party PII must remain redacted before external disclosure.

## 9. Recommendations

1. **UBTECH cloud:** add caller authentication and userId ownership checks to `im/getInfo`; enforce object-level authorization across business APIs; retire the static IM secret and rotate affected credentials; use per-device or per-principal credentials instead of product-wide shared values; isolate OTA credentials by productName.
2. **Tencent IM configuration:** enable relationship/allowlist validation for affected tenants and protect administrative REST credentials.
3. **Robot firmware:** validate the IM sender against the robot's bound principals before dispatch; require secondary authorization and anti-replay for high-impact commands; replace the public OTA test trust root.

---

*All conclusions in this guide were reproduced within the authorized research environment. When citing the results, preserve the evidence level: dynamically validated, code-supported, or strong inference.*
