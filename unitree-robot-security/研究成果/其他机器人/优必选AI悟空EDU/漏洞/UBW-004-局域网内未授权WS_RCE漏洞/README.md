---
ID: UBW-004
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH AI Wukong EDU
source_candidate_directory: 局域网内未授权WS_RCE漏洞
---
# UBW-004 UBTECH Alpha Mini (Wukong Education Edition) Unauthenticated WebSocket RCE on Port 8801 to Root Privilege Escalation — Reproduction Report

## 1. Summary

- # UBTECH Alpha Mini (Wukong Education Edition) Unauthenticated WebSocket RCE on Port 8801 to Root Privilege Escalation — Reproduction Report
- | Related Findings | **U-02** (unauthenticated 8800/8801 WebSocket channel → upload and execute arbitrary Python; dynamically upgraded to complete RCE), **U-20** (CVE-2020-0069 mtk-su → root) |
- ## 1. Vulnerability Overview
- `cmd 8 (PYPI_UPLOAD_SCRIPT_REQUEST)` permits uploading a Python script to the robot.
- A host on the same subnet can therefore reach an unauthenticated execution path, with the uploaded code running as `u0_a29` (platform_app).

## 2. Affected Products and Versions

- | Target | UBTECH Alpha Mini Wukong domestic Education Edition (`Dedu_<其他机器人设备_01>`) |
- | Firmware | `v1.6.3.919` (2023-12; latest first-generation release and now end-of-life) |
- Ports 8800 and 8801 expose TooTallNate Java-WebSocket services used by the official Python SDK.
- This path is independent from U-30 (the LAN random-port cmd 365 Lua path): U-30 reaches SpeechActor/LuaJava, while this finding reaches the fixed 8801 WebSocket package-management path.
- Reproduction environment: Python 3.8+ on the same subnet as the researcher-owned robot.

## 3. Validation Status

`dynamically confirmed`. This status reflects the validation boundary of the source report; the migration process does not infer dynamic confirmation from directory names.

## 4. Attack Preconditions

Attack preconditions are defined by the sanitized research body below. Reproduction must use researcher-owned devices, isolated networks, and authorized environments and must not perform write, control, or destructive operations against third-party devices.

## 5. Root Cause

- See the sanitized research body and material manifests below. The root cause is an unauthenticated WebSocket application channel that exposes script upload and execution operations.

## 6. Attack Procedure

The source report's entry point, protocol, and sequence are preserved in the sanitized research body in Section 13. This directory retains only minimal reproduction material and does not duplicate large raw evidence.

## 7. Impact

- # UBTECH Alpha Mini (Wukong Education Edition) Unauthenticated WebSocket RCE on Port 8801 to Root Privilege Escalation — Reproduction Report
- | Related Findings | **U-02** (unauthenticated 8800/8801 WebSocket channel → arbitrary Python execution), **U-20** (CVE-2020-0069 → root) |
- Combined with the unpatched local kernel vulnerability, the dynamically validated path reaches **root (uid=0)** on the researcher-owned device.
- The source report records this as an independent RCE path from the Lua-based U-30 chain.

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

# UBTECH Alpha Mini (Wukong Education Edition) Unauthenticated WebSocket RCE on Port 8801 to Root Privilege Escalation — Reproduction Report

| Item | Value |
|---|---|
| Target | UBTECH Alpha Mini Wukong domestic Education Edition (`Dedu_<其他机器人设备_01>`) |
| Firmware | `v1.6.3.919` (2023-12; latest first-generation release and now end-of-life) |
| System | Android 7.0 / NRD90M, MediaTek MT6755, kernel 3.18.35, security patch level 2018-05-05 |
| Test Host | Ordinary PC on the same subnet as the robot; no credentials or pairing required |
| Reproduction Date | 2026-07-29 |
| Related Findings | **U-02** (unauthenticated 8800/8801 WebSocket channel → upload and execute arbitrary Python), **U-20** (CVE-2020-0069 mtk-su → root) |
| Authorization Boundary | Researcher-owned device only, tested on an isolated LAN |

---

## 1. Vulnerability Overview

Ports 8800 and 8801 expose TooTallNate Java-WebSocket services used by the official Python SDK. **The WebSocket upgrade succeeds without credentials, and the application messages above the WebSocket layer also lack authentication.**

Port 8801 is used by the SDK package-management channel (`mini/pkg_tool.py`) and exposes operations corresponding to:

- `cmd 8 (PYPI_UPLOAD_SCRIPT_REQUEST)`: upload a Python script to
  `/storage/emulated/0/Android/data/com.ubt.pccodemao/files/pyscripts/`
- `cmd 10 (PYPI_RUN_UPLOAD_SCRIPT_REQUEST)`: execute the uploaded script using Termux Python 3.8

On the tested device, the resulting Python code ran as `u0_a29` (platform_app), with access to groups associated with audio, camera, media, storage, and networking. The unpatched CVE-2020-0069 path was then dynamically validated to reach **root (uid=0)** on the researcher-owned robot.

This path is independent from U-30, the random-port LAN Lua path:

| | U-30 | This Finding (U-02 Extended) |
|---|---|---|
| Entry | Random LAN port, cmd 365 | Fixed port 8801, WebSocket cmd 8/10 |
| Execution Runtime | SpeechActor LuaJava | CodeMao / Termux Python |
| Initial Identity | system (uid 1000) | u0_a29 |
| Observed Stability | Serial executor; can stall | Source report observed reliable, second-scale execution |

## 2. Attack Chain

```
Attacker PC (same subnet)
   │ ① TCP 8801 → WebSocket 101 upgrade without credentials
   ▼
② Use the exposed upload operation to place a test Python runner
   ▼
③ Use the exposed run operation
   │   → code executes as uid=10029(u0_a29)
   ▼
④ Validate the documented local privilege-escalation path on the owned device
   ▼
⑤ uid=0(root)
```

## 3. Protocol Details

- WebSocket text-frame format: `base64(Message.SerializeToString()) + "&"`, structurally similar to the 8800 SDK channel.
- Envelope: `Message{ header{ id=1(string), target=2, command=3 }, bodyData=2 }`.
- Upload request: `UploadScript{ fileName=1, content=2 }`; response: `UploadScriptResponse{ resultCode=1, message=2 }`.
- The source report maps commands 8 and 10 to upload and execute, along with adjacent package-management and ADB-control operations.
- The uploaded runner is attacker-controlled Python; the report used it only on the researcher-owned robot to validate the security boundary.

## 4. Reproduction Method

Environment: Python 3.8+ on a host in the same subnet as the researcher-owned robot.

The source package contains a one-command reproduction script that exercises the 8801 channel, validates Python execution, and confirms the local privilege-escalation result. To avoid duplicating operational exploit instructions in this English translation, use the sanitized scripts already retained in the repository and their associated evidence manifest.

The source report states that the complete chain takes roughly 30 seconds under the tested configuration and records output in `evidence/exploit_ws_run.log`.

Package layout:

```
WS_RCE复现包/
├── exploit_ws.py
├── root_shell.py
├── sig_runner.py
├── sig_rootsh.py
├── ws_action.py
├── ws_cmd.py
├── lib/
├── tools/mtk-su
├── evidence/
└── 漏洞复现报告.md
```

## 5. Reproduction Evidence

Key output from `evidence/exploit_ws_run.log`:

```
[+] WebSocket 101 upgrade succeeded; no application-layer authentication observed

$ id
uid=10029(u0_a29) gid=10029(u0_a29) groups=...,1005(audio),1006(camera),...

$ ... -c id
uid=0(root) gid=0(root) groups=0(root)

[+] privilege escalation confirmed: uid=0(root)
```

## 6. Recommendations

1. **Authenticate both 8800 and 8801 WebSocket channels.** Require device-bound credentials during the upgrade and for business messages; disable script upload/execution and ADB-control operations until authentication succeeds.
2. **Constrain script execution.** Require signed scripts or retire the remotely reachable upload/execute feature. Avoid shell-style command construction for package-management operations.
3. **Patch the kernel.** Apply the CVE-2020-0069 fix, return SELinux to enforcing, and reduce the platform_app domain's privileges.
4. Use TLS with certificate validation to prevent cleartext observation and modification.

## 7. Timeline

- 2026-07-28: U-02 initially recorded as “WebSocket 101 upgrade succeeded; application-layer authentication not yet verified.”
- 2026-07-29: physical-device testing confirmed no application-layer authentication and demonstrated the upload/run path to `u0_a29`, followed by root privilege validation.
