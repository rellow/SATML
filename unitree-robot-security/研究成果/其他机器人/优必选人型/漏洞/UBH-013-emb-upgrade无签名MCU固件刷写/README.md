---
ID: UBH-013
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: emb-upgrade无签名MCU固件刷写
---
# UBH-013 V2 · Unsigned MCU Firmware Flashing via `/emb/upgrade`

## 1. Summary

- Impact: **Critical in the source report** — the update interface accepts MCU firmware without a cryptographic signature, creating a firmware-persistence risk.
- The service and request schema were confirmed; destructive MCU flashing was intentionally not performed.

## 2. Affected Products and Versions

- Component: vision-board `/emb/upgrade` bridge plus downstream MCU update path over SocketCAN or the internal UDP transport.
- The request exposes `board + ota_path` and contains no signature field.

## 3. Validation Status

`statically confirmed` with live service/schema evidence. Firmware flashing itself was not executed.

## 4. Attack Preconditions

The attacker must reach the internal upgrade service and provide an accessible firmware path. Verification must use researcher-owned hardware and should not flash production motor-control MCUs without a repair/recovery setup.

## 5. Root Cause

The MCU update protocol accepts raw firmware images without cryptographic signature verification, encryption, or rollback protection.

## 6. Attack Procedure

The retained probe confirms the service, request fields, and transport path, and can construct an update request without transmitting it.

## 7. Impact

If an unauthorized firmware image is accepted, malicious behavior can persist below the Linux host layer across reboot or host-system reinstallation. Depending on the MCU's role, this can affect motor control, sensor reporting, or power management.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The retained test does not flash an MCU.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Require cryptographic firmware signatures anchored in a device/vendor trust root.
- Enforce anti-rollback/version policy.
- Authenticate and authorize callers of the MCU update service.
- Separate update transport from normal application access.
- Add negative tests for unsigned, modified, and downgraded firmware.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review firmware evidence and vendor-coordination status.

## 13. Sanitized Original Research Body

# V2 · Unsigned MCU Firmware Flashing via `/emb/upgrade`

| Item | Value |
|---|---|
| Component | Vision-board `/emb/upgrade` bridge plus MCU update path over SocketCAN / internal UDP |
| Impact | **Critical in the source report** — an unsigned firmware image can be supplied to the MCU flashing path |
| Source | `report_vision_core(1).md` (V2) |
| Re-verification | 🟢 `/emb/upgrade` is present; the `Upgrade.srv` request has no signature field |

## Vulnerability Mechanism

`/emb/upgrade` accepts `board + ota_path` and transfers the referenced firmware image to an MCU using the platform's CAN/UDP update path.

The source analysis found:

- no cryptographic firmware-signature verification;
- no transport-level firmware confidentiality requirement;
- no rollback/version protection;
- the uploaded object is the raw MCU image.

A compromised update path could therefore place persistent code in an MCU. Because that code runs below the Linux host, reinstalling the host operating system would not necessarily remove it.

## Reproduction Script

`scripts/exploit_mcu_upgrade.py`

Safe default behavior:

1. Confirm the `/emb/upgrade` service exists.
2. Display the `Upgrade.srv` fields (`board` and `ota_path`) and absence of a signature field.
3. Confirm the documented CAN/UDP update transport evidence.

The danger mode only constructs an update request and does not send it.

## Evidence Output

- `Upgrade.srv` schema.
- Update transport and destination evidence.
- Example benign firmware-layout information.
- Supporting material retained under `evidence/`.

## Safety Boundary

⚠️ MCU flashing can permanently damage a controller or render a joint unusable. The retained verification does not transmit a firmware update.

A full authorized reproduction requires repair-grade hardware, a known-good image, and a reliable recovery procedure.
