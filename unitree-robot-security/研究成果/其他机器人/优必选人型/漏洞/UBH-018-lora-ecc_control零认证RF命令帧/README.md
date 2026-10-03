---
ID: UBH-018
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: lora-ecc_control零认证RF命令帧
---
# UBH-018 S1 · Unauthenticated LoRa RF Command Frames in `ecc_control`

## 1. Summary

The motion-board `ecc_control` process receives LoRa command frames and translates them into robot control actions without an authenticated pairing or cryptographic message-authentication layer visible in the analyzed protocol. The process/device and frame checksum algorithm were confirmed; live RF motion commands were not transmitted.

## 2. Affected Products and Versions

- Component: root-privileged motion-board `ecc_control` LoRa bridge using `/dev/ttyLORA`.
- RF range may substantially exceed ordinary Wi-Fi/LAN proximity.
- Safe validation requires an RF-isolated environment and physical robot safety controls.

## 3. Validation Status

`statically confirmed` with live process/device evidence and offline frame/CRC validation. No physical motion command was sent.

## 4. Attack Preconditions

An attacker would need RF reachability to the LoRa interface and knowledge of the command-frame format. Any live test must ensure no unrelated robot can receive the transmission.

## 5. Root Cause

The RF command protocol relies on a checksum for integrity/error detection but does not provide authenticated origin, pairing, encryption, or replay-resistant message authentication.

## 6. Attack Procedure

The retained script confirms the process/device, validates the CRC algorithm against known frames, and can generate frame bytes offline. It does not write to the LoRa device by default.

## 7. Impact

If unauthorized RF frames are accepted, commands such as stop/start can directly affect physical robot behavior from a potentially long-distance radio position.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Do not transmit RF control frames outside a shielded/authorized setup.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Add cryptographic message authentication and replay protection to every RF command.
- Provision per-device keys and authenticated pairing.
- Bind dangerous commands to local safety state and explicit authorization.
- Rate-limit and log rejected/accepted RF control commands.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# S1 · Unauthenticated LoRa RF Command Frames in `ecc_control`

| Item | Value |
|---|---|
| Component | Root-privileged motion-board `ecc_control` LoRa bridge (`/dev/ttyLORA`) |
| Impact | **Critical in the source report** — unauthenticated RF command frames can encode robot STOP/START actions |
| Source | `report_system(1).md` (S1) |
| Re-verification | 🟢 `ecc_control` was live as root and the LoRa device was present |

## Vulnerability Mechanism

The source report reverse engineered a compact frame structure containing a magic byte, length, CRC-8 checksum, command type, label, delay, command value, and address list. The CRC was reproduced offline against known frames.

The important security distinction is that a CRC provides accidental-corruption detection, not sender authentication. The analyzed protocol contains no cryptographic pairing, encryption, or MAC layer, so an attacker who can reproduce the frame format may be able to impersonate an RF controller.

## Reproduction Script

`scripts/exploit_lora_rf.py`

Safe default behavior:

1. Confirm the `ecc_control` process and LoRa device.
2. Recompute CRC-8 for known recorded frames to validate the frame parser.
3. Generate representative RemoteCmd frames offline.

Transmission options are intentionally gated and are not used during routine verification.

## Evidence Output

- Process, privilege, and device evidence.
- Byte-for-byte CRC validation for known frames.
- Generated frame encoding for offline audit.
- Supporting logs under `evidence/`.

## Safety Boundary

⚠️ RF commands directly affect robot movement. The retained workflow does not write frames to `/dev/ttyLORA`. A live demonstration requires an RF-isolated environment, a safely restrained robot, emergency-stop readiness, and explicit authorization.
