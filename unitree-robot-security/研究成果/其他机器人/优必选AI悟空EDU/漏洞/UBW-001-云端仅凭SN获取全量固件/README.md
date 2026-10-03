---
ID: UBW-001
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH AI Wukong EDU
source_candidate_directory: 云端仅凭SN获取全量固件
---
# UBW-001 UBTECH Wukong 2 (AlphaMini2): Full Firmware Retrieval from the Cloud Using Only an SN — Analysis and Reproduction Guide

## 1. Summary

- ## 1. Executive Summary
- **An attacker does not need an account, device ownership, or network proximity to the device. Using only a publicly extractable appId/appKey pair from firmware/App code and an arbitrary SN string (even a nonexistent SN), the attacker can enumerate and download all released firmware for Wukong 2 from the UBTECH cloud**—including the 1.18 GB full Android OTA image (eight partitions including boot/system/vendor), the chest-controller MCU firmware, and firmware for six servos.
- Severity: **High**. Firmware acts as an attack-surface map: anyone can analyze current firmware offline, identify N-days, extract embedded keys (OTA/IM/MQTT credentials are all exposed in firmware), and study MCU/servo update chains. When combined with the report on unauthorized control of arbitrary robots through the cloud, this creates the full prerequisite sequence “obtain firmware → find vulnerabilities → attack online devices at scale.”
- ## 2. Impact Overview
- Headers: X-UBT-AppId / X-UBT-DeviceId(arbitrary SN) / X-UBT-Sign / X-UBT-Timestamp / X-UBT-Nonce

## 2. Affected Products and Versions

- # UBTECH Wukong 2 (AlphaMini2): Full Firmware Retrieval from the Cloud Using Only an SN — Analysis and Reproduction Guide
- > Version: 2026-07-29 · Environment: SRC-authorized test environment · Validated device: researcher-owned Wukong (SN=<其他机器人设备_01>)
- **An attacker does not need an account, device ownership, or network proximity to the device. Using only a publicly extractable appId/appKey pair from firmware/App code and an arbitrary SN string (even a nonexistent SN), the attacker can enumerate and download all released firmware for Wukong 2 from the UBTECH cloud**—including the 1.18 GB full Android OTA image (eight partitions including boot/system/vendor), the chest-controller MCU firmware, and firmware for six servos.
- **One public credential set** is sufficient: appId `980020069` (embedded in firmware OtaService). The server checks only whether the deviceId is self-consistent with the signature and **does not verify that the SN actually exists or belongs to the caller**. A nonexistent SN `<其他机器人设备_01>` produced exactly the same response as a real SN during testing.
- **Eight firmware modules** were downloadable at the time of testing: Android full image v1.6.0.3 (released 2026-08-24), MCU app v1.1.2.9, and six 2 kg servo firmware images v2.25.09.09.
- Severity: **High**. Firmware acts as an attack-surface map: anyone can analyze current firmware offline, identify N-days, extract embedded keys (OTA/IM/MQTT credentials are all exposed in firmware), and study MCU/servo update chains. When combined with the report on unauthorized control of arbitrary robots through the cloud, this creates the full prerequisite sequence “obtain firmware → find vulnerabilities → attack online devices at scale.”

## 3. Validation Status

`dynamically confirmed`. This status reflects the validation boundary of the source report; the migration process does not treat a directory name as evidence of dynamic confirmation.

## 4. Attack Preconditions

Attack preconditions are defined by the sanitized research body below. Reproduction must use researcher-owned devices, isolated networks, and authorized environments, and must not perform writes, control actions, or destructive operations against third-party devices.

## 5. Root Cause

- ## 3. Vulnerability Root Cause
- | `mcu-app` | v1.1.2.9 | 90,832 B | 2026-08 | Chest-controller MCU firmware (unsigned; MD5 only) |
- | Symptom | Cause and Handling |

## 6. Attack Procedure

The entry point, protocol, and sequence described by the source report appear in the sanitized research body in Section 13. This directory retains only minimal reproduction material and does not duplicate large raw evidence.

## 7. Impact

- > No write or control operation was performed against any third-party device. This guide is for defensive research and responsible disclosure only.
- Severity: **High**. Firmware acts as an attack-surface map: anyone can analyze current firmware offline, identify N-days, extract embedded keys (OTA/IM/MQTT credentials are all exposed in firmware), and study MCU/servo update chains. When combined with the report on unauthorized control of arbitrary robots through the cloud, this creates the full prerequisite sequence “obtain firmware → find vulnerabilities → attack online devices at scale.”
- ## 2. Impact Overview
- **Obtaining firmware using only an SN is therefore not merely an information leak; it defeats every protection that depends on a “client-side secret.”**
- See `脱壳分析/OTA/` for related downstream-impact analysis.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Imported scripts were text-sanitized; original scripts, logs, packet captures, and binaries that were not imported are recorded in the repository-level material manifest.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13 below. Source files are represented only by hashes and local storage paths; raw sensitive material is not copied into Git.

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

# UBTECH Wukong 2 (AlphaMini2): Full Firmware Retrieval from the Cloud Using Only an SN — Analysis and Reproduction Guide

> Version: 2026-07-29 · Environment: SRC-authorized test environment · Validated device: researcher-owned Wukong (SN=<其他机器人设备_01>)
> **Boundary statement:** all queries requested only upgrade metadata and HTTP HEAD probes; full-package downloads were limited to the product line corresponding to researcher-owned devices.
> No write or control operation was performed against any third-party device. This guide is for defensive research and responsible disclosure only.

---

## 1. Executive Summary

**An attacker does not need an account, device ownership, or network proximity to the device. Using only a publicly extractable appId/appKey pair from firmware/App code and an arbitrary SN string (even a nonexistent SN), the attacker can enumerate and download all released firmware for Wukong 2 from the UBTECH cloud**—including the 1.18 GB full Android OTA image (eight partitions including boot/system/vendor), the chest-controller MCU firmware, and firmware for six servos.

Key figures:

- **One public credential set** is sufficient: appId `980020069` (embedded in firmware OtaService). The server checks only whether the deviceId is self-consistent with the signature and **does not verify that the SN actually exists or belongs to the caller**. A nonexistent SN `<其他机器人设备_01>` produced exactly the same response as a real SN during testing.
- **Eight firmware modules** were downloadable at the time of testing: Android full image v1.6.0.3 (released 2026-08-24), MCU app v1.1.2.9, and six 2 kg servo firmware images v2.25.09.09.
- **All download URLs were publicly accessible without authentication:** all eight CDN URLs at assets-new.ubtrobot.com returned HTTP 200 to HEAD requests and could be fetched directly by a browser.
- **The signing algorithm was fully recoverable:** `X-UBT-Sign = MD5(second-level ts + appKey + nonce8 + deviceId) + " ts nonce v2"`; the timestamp is provided by a public cloud endpoint.

Severity: **High**. Firmware acts as an attack-surface map: anyone can analyze current firmware offline, identify N-days, extract embedded keys (OTA/IM/MQTT credentials are all exposed in firmware), and study MCU/servo update chains. When combined with the report on unauthorized control of arbitrary robots through the cloud, this creates the full prerequisite sequence “obtain firmware → find vulnerabilities → attack online devices at scale.”

---

## 2. Impact Overview

### 2.1 Firmware as an Attack-Surface Map and Key Store

The downloaded Android package can reconstruct the complete system image; the eight partition SHA-256 values were verified against the manifest. In cleartext it contains:

- OTA query credentials (appId `980020069` plus appKey in `com.ubtrobot.mini.ota.BuildConfig`);
- Tencent Cloud IM/MQTT-related appKeys in the 980020055 / 980020054 families, embedded in MainApp/SpeechService;
- complete code for system applications including MainApp, Master, OtaService, and SpeechService. Analysis in this workspace used that code to identify issues such as unauthenticated master-bus access, silent installation without signature verification, MD5-only MCU firmware flashing, and Zip Slip; see the reports under `脱壳分析/OTA/32-36`.

**Obtaining firmware using only an SN is therefore not merely an information leak; it defeats every protection that depends on a “client-side secret.”** Any interface whose authentication relies on keys embedded in firmware—such as OTA, robot-login, and im/getInfo—must be treated as exposed to an attacker who can obtain the firmware.

### 2.2 MCU / Servo Firmware Attack Surface

- `app-wk2_mcu_v1.1.2.9_signed.bin` (90 KB, Cortex-M) was found to contain **no cryptographic-signature space**; only a 64-byte ASCII version trailer was present. Flashing validation is MD5-only, so the firmware format can be analyzed without relying on a signing trust anchor.
- Six 2 kg servo firmware images (12 KB each) were publicly downloadable, allowing the servo-bus protocol and IAP flow to be studied offline.

### 2.3 Scale and Product-Line Reach

- SN values use a sequential-looking range (`<其他机器人设备_01>` plus eight digits), but **this vulnerability does not require a real SN at all**; deviceId is free-form text.
- The same signing system spans multiple product lines; reports in the same directory confirmed downloadable firmware for five product lines. AlphaMini2 queries also showed that productName is not isolated by credential domain: robot-firmware credentials can query mobile-App channels and vice versa.

---

## 3. Vulnerability Root Cause

```
Public App / firmware
 ① Extract appId 980020069 + appKey (cleartext constants in OtaService BuildConfig)
 ② Recover signing algorithm: MD5(ts+appKey+nonce+deviceId)
    (second-level ts is returned by /v1/client-auth-service/api/timestamp)
 ③ GET /v1/upgrade-rest/version/upgradable?productName=AlphaMini2&moduleNames=...&versionNames=...
    Headers: X-UBT-AppId / X-UBT-DeviceId(arbitrary SN) / X-UBT-Sign / X-UBT-Timestamp / X-UBT-Nonce
 ④ Server checks only that signature and appId/deviceId are self-consistent
    → returns package name / URL / MD5 / size / publication time
 ⑤ packageUrl points to a public CDN → direct unauthenticated download
```

Three design defects are involved:

1. **A client-distributed key is used as a server-side authentication secret.** The appKey ships with every device firmware image and App package and therefore cannot be treated as secret.
2. **No object-level authorization.** deviceId (SN) is not checked for existence or ownership; it is only another field in the signed string.
3. **No CDN access control or short-lived signing.** packageUrl values remain directly accessible; HEAD requests returned 200 without Cookie or Referer requirements.

Key evidence anchors:

| Stage | Evidence |
|---|---|
| Embedded credentials | `com/ubtrobot/mini/ota/BuildConfig.java:24-25` in firmware (cleartext appId/appKey) |
| Signing algorithm | `HttpSignInterceptor.java:64` (v2 signing construction) |
| deviceId source | `OtaService.java:261-263` (`SysApi.readRobotSid()`; no corresponding server-side ownership check) |
| Identical responses | `evidence/ota_full_enum_20260729.json`: own_sn and fake_sn results are byte-for-byte identical |
| Public CDN | Same file, `url_head_check`: 8/8 URLs returned HTTP 200 to HEAD |

---

## 4. Currently Downloadable Inventory

Measured 2026-07-29 with productName=AlphaMini2.

| Module | Version | Size | Publication Time | Description |
|---|---|---|---|---|
| `android` | v1.6.0.3 | 1,181,357,667 B (1.1 GB) | 2026-08-24 | Full system OTA (eight A/B payload partitions) |
| `mcu-app` | v1.1.2.9 | 90,832 B | 2026-08 | Chest-controller MCU firmware (unsigned; MD5 only) |
| `1g/2g/3g/4g/11g/12g` | v2.25.09.09 | 12,072 B ×6 | 2025-09 | 2 kg servo firmware |
| `mcu-boot / firmware / uboot / dtbo / boot / main-service / 5a-10a,13a,14a / 5g-10g,13g,14g` | — | — | — | Not published by the cloud endpoint (empty result) |

Note: in 2026-06, the previous Android v1.4.0.5 package (MD5 `a421645b87613d6d2a21d9fbea4b4e97`) was downloaded and fully analyzed. The later query showed that the cloud had advanced to v1.6.0.3 and the MCU image had advanced from v1.1.2.6 to v1.1.2.9, demonstrating that the endpoint can expose current firmware over time.

---

## 5. Reproduction Environment

- Internet-connected computer with Python 3; the script uses only the standard library.
- No robot, account, or shared network with a device is required for the metadata-query portion described by the source report.

## 6. Reproduction Steps

### 6.1 Automated Enumeration

```bash
python evidence/ota_firmware_query.py
```

Expected output is recorded in `evidence/ota_full_enum_20260729.json`. Using the nonexistent SN `<其他机器人设备_01>` still returned metadata for the Android v1.6.0.3 package, MCU app v1.1.2.9, and the other published modules.

### 6.2 Manual curl Verification

The source report also records a manual verification sequence that reconstructs the same signed request using the recovered client-side signing format. The exact command is retained in the authorized research artifact.

### 6.3 Public-Download Verification Without Downloading the Full Package

The source report used an HTTP HEAD request against the returned package URL and observed HTTP 200 with the expected Content-Length and no additional authentication requirement.

### Troubleshooting

| Symptom | Cause and Handling |
|---|---|
| 403 `非法客户端` ("illegal client") | The source report attributes this to using local time rather than the server-provided timestamp, or to constructing the signed field order incorrectly |
| Returned `[]` | Incorrect productName or an unpublished module; see the inventory above |
| nonce is not 8 characters | The nonce in the signed string must match the X-UBT-Nonce field and the format expected by the service |

---

## 7. Evidence and File Index

```
云端仅凭SN获取全量固件/
├── README.md
└── evidence/
    ├── ota_firmware_query.py
    └── ota_full_enum_20260729.json
```

The original report describes `ota_firmware_query.py` as the reproducible metadata-enumeration script and `ota_full_enum_20260729.json` as the raw enumeration plus eight HEAD checks; equality between own_sn and fake_sn is the core object-authorization evidence.

Related downstream analysis is under `脱壳分析/OTA/`: `33_channel_check.md`, `37_mqtt_idor_remote_rce.md`, and `38_final_report.md`.

## 8. Recommendations

1. **Stop using embedded client credentials as API authentication.** Rotate the appKey and retire old values. OTA/upgrade services should use device-specific, short-lived credentials such as a manufacturing-provisioned challenge-response key or mTLS device certificate.
2. **Enforce object-level authorization.** `version/upgradable` should verify that deviceId exists and is bound to the caller's credential; credentials should also be scoped to productName.
3. **Protect CDN downloads.** Return short-lived signed package URLs rather than permanently public URLs.
4. **Minimize secrets in firmware.** Assume firmware will be reverse engineered; it should not contain long-lived values that directly confer authorization.
5. **Monitor enumeration behavior.** Alert on high-rate or wide-range SN queries associated with the same appId.

---

*All conclusions in this guide were reproduced within the authorized research environment. Before external submission, re-check the evidence directory for any sensitive information associated with researcher-owned devices.*
