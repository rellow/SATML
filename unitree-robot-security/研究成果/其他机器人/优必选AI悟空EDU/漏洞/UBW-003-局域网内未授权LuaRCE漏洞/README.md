---
ID: UBW-003
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH AI Wukong EDU
source_candidate_directory: 局域网内未授权LuaRCE漏洞
---
# UBW-003 UBTECH Alpha Mini (Wukong Education Edition) Unauthenticated LAN RCE to Root Privilege Escalation — Reproduction Report

## 1. Summary

- # UBTECH Alpha Mini (Wukong Education Edition) Unauthenticated LAN RCE to Root Privilege Escalation — Reproduction Report
- | Related Findings | **U-03** (unauthenticated LAN channel), **U-30** (cmd 365 Lua injection → system-level RCE), **U-20** (CVE-2020-0069 mtk-su → root) |
- ## 1. Vulnerability Overview
- Any host on the same network can connect and invoke all 93 handlers.
- `DemoRunLuaScriptHandler` (cmd 365) passes attacker-supplied Lua to the LuaJava engine embedded in SpeechActor (`/system/priv-app/`, running as **system uid**).

## 2. Affected Products and Versions

- | Target | UBTECH Alpha Mini Wukong domestic Education Edition (instance `Dedu_<其他机器人设备_01>`) |
- | Firmware | `v1.6.3.919` (2023-12; latest first-generation release and now end-of-life) |
- The Alpha Mini LAN command channel uses Netty plus cleartext protobuf and advertises a random port through mDNS; **the handshake contains no credential**.
- The discovery path exposes the robot IP, random port (50000–51999), serial number, and battery level.
- cmd 1000 returns `isSuccess=True` and exposes firmware version v1.6.3.919 without authentication.
- mDNS service type: `_Dedu_mini_channel_server._tcp.local`; instance name: `Dedu_<serial number>`.

## 3. Validation Status

`dynamically confirmed`. This status reflects the validation boundary of the source report; the migration process does not infer dynamic confirmation from directory names.

## 4. Attack Preconditions

Attack preconditions are defined by the sanitized research body below. Reproduction must use researcher-owned devices, isolated networks, and authorized environments and must not perform write, control, or destructive operations against third-party devices.

## 5. Root Cause

- One contributing root cause is that the first-generation product line is no longer maintained; the source report recommends a final security update or an explicit end-of-service notice.

## 6. Attack Procedure

The source report's entry point, protocol, and sequence are preserved in the sanitized research body in Section 13. This directory retains only minimal reproduction material and does not duplicate large raw evidence.

## 7. Impact

- # UBTECH Alpha Mini (Wukong Education Edition) Unauthenticated LAN RCE to Root Privilege Escalation — Reproduction Report
- | Related Findings | **U-03** (unauthenticated LAN channel), **U-30** (cmd 365 Lua injection → system-level RCE), **U-20** (CVE-2020-0069 mtk-su → root) |
- **CVE-2020-0069 (mtk-su) is unpatched**, enabling escalation from the system account to **root (uid=0)**.
- **Impact:** any device on the same LAN (for example, a classroom, office, or shared Wi-Fi network) can reach the robot without user interaction.
- With system privileges, an attacker can access application data and camera/microphone/face-database functionality; root then extends access to the device filesystem, including system partitions.

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

# UBTECH Alpha Mini (Wukong Education Edition) Unauthenticated LAN RCE to Root Privilege Escalation — Reproduction Report

| Item | Value |
|---|---|
| Target | UBTECH Alpha Mini Wukong domestic Education Edition (instance `Dedu_<其他机器人设备_01>`) |
| Firmware | `v1.6.3.919` (2023-12; latest first-generation release and now end-of-life) |
| System | Android 7.0 / NRD90M, MediaTek MT6755, kernel 3.18.35, security patch level 2018-05-05 |
| Test Host | Ordinary PC on the same subnet as the robot; no credential, pairing, or physical contact required |
| Reproduction Date | 2026-07-29 |
| Related Findings | **U-03** (unauthenticated LAN channel), **U-30** (cmd 365 Lua injection → system-level RCE), **U-20** (CVE-2020-0069 mtk-su → root) |
| Authorization Boundary | Researcher-owned device only, tested on an isolated LAN |

---

## 1. Vulnerability Overview

The Alpha Mini LAN command channel uses Netty with cleartext protobuf and announces a random port over mDNS. **The handshake contains no credential**, so any host on the same subnet can connect and invoke all 93 handlers.

`DemoRunLuaScriptHandler` (cmd 365) passes arbitrary Lua to the LuaJava engine embedded in SpeechActor (`/system/priv-app/`, running with the **system uid**). After `openLibs()`, the engine does **not remove dangerous libraries or impose a sandbox**. The source report confirms that Java reflection through LuaJava can reach process-execution functionality and produce command execution as the **system** account.

The device runs kernel 3.18.35 with a 2018-05-05 patch level. **CVE-2020-0069 (mtk-su) remains unpatched**, enabling escalation from the system account to **root (uid=0)**.

> Additional dynamic observation: an earlier report described SELinux as enforcing, but the physical device returned **Permissive** from `getenforce`, and `/sys/fs/selinux/enforce` contained `0`. Thus no mandatory-access-control enforcement blocked the tested escalation path.

**Impact:** any device on the same LAN can reach the command channel without user interaction. With system privileges, an attacker can access application data and camera/microphone/face-database functionality; root extends access across the device filesystem, including system partitions.

## 2. Attack Chain

```
Attacker PC (same subnet)
   │ ① Query mDNS service _Dedu_mini_channel_server._tcp.local
   │   → robot IP + random port (50000–51999) + serial number + battery level
   ▼
② Connect over TCP and send commandId=0 handshake
   │   uuid is client-supplied; no token/signature/pairing code is required
   │   ← cmd 1000 isSuccess=True; firmware v1.6.3.919 is disclosed
   ▼
③ Send cmd 365 with RunLuaScriptRequest{ script }
   │   SpeechActor LuaJava executes the script as the system account
   ▼
④ Obtain an interactive system-context shell
   ▼
⑤ Exercise the documented local privilege-escalation path on the owned device
   ← uid=0(root)
```

## 3. Protocol and Vulnerability Details

### 3.1 Discovery and Frame Format

- mDNS service type: `_Dedu_mini_channel_server._tcp.local`; instance name `Dedu_<serial number>`.
- The TXT record broadcasts the battery level in cleartext.
- The channel chooses a new random port after restart with `Random.nextInt(2000)+50000`.
- Frame format: `FB BF | ver(1) | length(2,big-endian) | payload(protobuf) | 01 | ED`; the transport is cleartext and does not use TLS.

### 3.2 Credential-Free Handshake (U-03)

- The LAN handshake condition is only `header.commandId == 0`.
- `BluetoothHandShakeRequest.uuid` and `sessionId` are supplied by the client and are not validated server-side.
- cmd 1000 `BluetoothShakeResponse` includes `robotSoftVersionName`.
- `Policy.KickOff` allows a later unauthenticated client to disconnect the existing legitimate client and take over the session.

### 3.3 cmd 365 Lua Injection (U-30)

- `DemoRunLuaScriptHandler` applies no meaningful authorization filter beyond checks for low battery (999) and a high-risk action state (998).
- The handler wraps the submitted script as `ret = 0;<script>; _processor:finished();`, so the input must be statement-oriented rather than ending with `return`.
- After LuaJava `openLibs()`, reflection and object construction remain available.
- Execution identity equals the SpeechActor process identity: **system (uid 1000)**, not root and not the Android shell account.
- The long-lived channel requires periodic heartbeats. The first Master IPC call after a cold start can take substantially longer than subsequent calls.

### 3.4 Local Privilege Escalation (U-20, CVE-2020-0069)

- Kernel 3.18.35 and security patch level 2018-05-05 leave the MediaTek CVE-2020-0069 path unpatched on the tested device.
- The source report dynamically confirmed escalation to uid 0 on the researcher-owned robot.
- SELinux was observed in Permissive mode, so it did not add an enforcing MAC barrier in the tested configuration.

## 4. Reproduction Method

Environment: Python 3.8+ on a host in the same subnet as the researcher-owned robot.

The source package contains an automated reproduction script that performs discovery, the credential-free handshake, the Lua execution check, and local privilege-escalation validation. To avoid duplicating operational detail in this English translation, use the sanitized reproduction material already retained in the repository and the evidence manifest associated with this finding.

The complete test-session output is stored in `evidence/exploit_run.log`.

> Note: the source report observes that Lua execution can be refused when the robot battery is too low (`errCode=999 "low power."`).

Package layout:

```
LuaRCE复现包/
├── exploit.py
├── lib/
│   ├── lan_channel_client.py
│   └── lan_discover.py
├── tools/mtk-su
├── evidence/
└── 漏洞复现报告.md
```

## 5. Reproduction Evidence

The original evidence is under `evidence/`:

- `exploit_run.log` — complete automated-session log from discovery through privilege-escalation validation
- `2026-07-29_提权root证据.log` — session showing `uid=0(root)`
- `2026-07-29_首次复现证据.log` — first physical-device reproduction record
- `01_发现与握手.png` — mDNS discovery and successful credential-free handshake
- `02_system身份shell.png` — cmd 365 execution with `whoami = system`
- `03_提权root.png` — root-privilege validation

The source report notes that the SpeechActor Lua executor is serial and somewhat fragile under repeated high-frequency calls; sustained timeouts may require waiting or restarting the robot.

Key evidence excerpts:

```
[+] handshake response cmd=1000 isSuccess=True
    robotSoftVersionName = v1.6.3.919

$ whoami
system

$ id
uid=1000(system) gid=1000(system) groups=... context=u:r:system_app:s0

$ uname -a
Linux localhost 3.18.35 #1 SMP PREEMPT Tue Nov 21 20:35:33 HKT 2023 aarch64

$ ... -c id
uid=0(root) gid=0(root) groups=0(root)
```

## 6. Recommendations

1. **Authenticate LAN-channel access.** Add a device-bound credential to the handshake, for example a challenge-response mechanism derived from a provisioning secret. Do not expose business handlers until authentication succeeds, and remove unauthenticated session takeover through `Policy.KickOff`.
2. **Sandbox or remove remote Lua execution.** Remove dangerous LuaJava/OS/IO capabilities from the remotely reachable interpreter, or retire cmd 365. At minimum, require signed scripts.
3. **Encrypt transport.** Use TLS with certificate validation to prevent cleartext observation and modification.
4. **Patch the kernel.** Apply the CVE-2020-0069 fix, return SELinux to enforcing, and reduce the privileges of the system application domain.
5. Because the first-generation product line is no longer maintained, provide a final security update or an explicit end-of-service notice.

## 7. Timeline

- 2026-07-28: protocol reverse engineering and static analysis completed.
- 2026-07-29: U-03 → U-30 → U-20 chain reproduced on the physical device; SELinux confirmed to be Permissive.
