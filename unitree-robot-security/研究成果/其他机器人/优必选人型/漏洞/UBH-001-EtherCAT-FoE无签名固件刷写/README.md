---
ID: UBH-001
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: EtherCAT-FoE无签名固件刷写
---
# UBH-001 E3 · Unsigned Firmware Flashing over EtherCAT FoE

## 1. Summary

- Impact: **Critical in the source report** — the EtherCAT File-over-EtherCAT update service can transfer raw firmware images to servo slaves without a cryptographic signature check.
- The service and firmware artifacts were confirmed; destructive flashing was intentionally not performed.

## 2. Affected Products and Versions

- Component: motion-board EtherCAT master plus servo devices through the Ecat2Can bridge.
- Service: ROS 2 `/ecat/slave/download_file`.
- The running service was visible in the robot's ROS graph while the robot was in STANDBY.

## 3. Validation Status

`statically confirmed` with live service-presence evidence. No servo firmware was flashed during verification.

## 4. Attack Preconditions

The attacker must reach the motion-board ROS/EtherCAT service boundary. Verification must use researcher-owned hardware and should not flash servo firmware without a repair and recovery environment.

## 5. Root Cause

The FoE update path accepts raw firmware images without a cryptographic signature, and the source analysis identified weak/fixed password behavior rather than a strong per-device authorization mechanism.

## 6. Attack Procedure

The retained probe confirms the service registration, locates a factory firmware image for format evidence, and records the password candidates. It can construct a request but does not transmit it.

## 7. Impact

A malicious firmware image accepted by a servo would persist in device flash and execute below the host operating system. This creates a lower-level persistence and physical-safety risk, including potential joint-controller failure.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). No firmware flashing is performed by the committed safe probe.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Require cryptographic signatures on all servo firmware images.
- Use per-device or securely provisioned update authorization rather than fixed/weak passwords.
- Enforce anti-rollback.
- Restrict update services to authenticated maintenance contexts.
- Add recovery-safe negative tests for modified/unsigned firmware.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review firmware material, evidence, and vendor-coordination status.

## 13. Sanitized Original Research Body

# E3 · Unsigned Firmware Flashing over EtherCAT FoE

| Item | Value |
|---|---|
| Component | Motion-board EtherCAT master + servo devices (Ecat2Can bridge) |
| Service | ROS 2 `/ecat/slave/download_file` (FoE = File over EtherCAT) |
| Impact | **Critical in the source report** — raw firmware can be delivered to servo flash without a cryptographic signature |
| Source | `report_motion.md` (E3) |
| Re-verification | 🟢 Service present in the runtime graph; robot was in STANDBY |

## Vulnerability Mechanism

The FoE `download_file` service transfers a firmware image to a selected EtherCAT slave.

The source report found:

- no digital-signature verification on the raw image;
- password candidates consisting of an empty value or a fixed bridge-layer value;
- a servo slave address identified in the analyzed configuration.

If an unauthorized image is accepted, malicious code can persist in servo flash and run on power-up. This is lower in the stack than host RCE and can create repair-level joint-controller damage.

## Reproduction Script

`scripts/exploit_foe_flash.py`

Safe default behavior:

1. Locate a factory `app.bin` firmware image in the local container for format evidence.
2. Confirm that `/ecat/slave/download_file` is registered.
3. Display the FoE password evidence.

The danger mode only constructs a request and does not send it.

## Evidence Output

- Factory firmware hash and MCU header evidence.
- Service-registration result.
- Password-candidate provenance.
- Supporting material under `evidence/`.

## Safety Boundary

⚠️ Servo firmware flashing is potentially irreversible and can damage joint control. The retained test never sends the update request.

A full authorized validation requires a powered-down/repair-capable environment, a known-good recovery image, and a safe method to restore the servo controller.
