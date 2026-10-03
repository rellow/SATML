---
ID: UBH-005
validation_status: statically confirmed
severity: medium
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: agora-遥操作AppID硬编码云端注入
---
# UBH-005 E6 · Hard-Coded Agora RTM AppID Enables Cloud-Side Teleoperation Injection

## 1. Summary

- Impact: **High in the source report** — a party able to join the relevant Agora RTM channel could inject teleoperation data into robot motion topics.
- The hard-coded identifiers were confirmed in the running binary; no live connection to the external Agora cloud was made.

## 2. Affected Products and Versions

- Component: motion-board `rtm_receiver`, which receives cloud teleoperation data through Agora RTM.
- This creates a cloud-facing attack surface outside the local network if the channel can be joined without an independent secret.

## 3. Validation Status

`statically confirmed` with binary-level evidence. No live external-cloud injection was performed.

## 4. Attack Preconditions

The source report assumes the attacker can obtain the hard-coded Agora identifiers from firmware and that the project/channel does not require an additional effective token. External-cloud interaction was intentionally excluded from routine verification.

## 5. Root Cause

The teleoperation receiver embeds cloud connection identifiers in firmware and the inbound dispatch path does not apply an independent MAC/signature check before translating received data into motion-related topics.

## 6. Attack Procedure

The retained safe script extracts and confirms the embedded identifiers locally. It does not connect to Agora or transmit motion data.

## 7. Impact

If the channel is joinable under the recovered identifiers without an additional effective credential, injected teleoperation messages could reach motion-control topics from outside the local network.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The retained probe is local and non-invasive.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Remove product-wide hard-coded cloud identifiers from firmware where they confer access.
- Require per-session or per-device authenticated tokens for teleoperation channels.
- Authenticate and integrity-protect teleoperation payloads independently of transport membership.
- Add allowlists and safety checks before cloud-originated data reaches motion topics.
- Audit and rotate any exposed Agora project credentials.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review cloud identifiers, evidence, and vendor-coordination status.

## 13. Sanitized Original Research Body

# E6 · Hard-Coded Agora RTM AppID Enables Cloud-Side Teleoperation Injection

| Item | Value |
|---|---|
| Component | Motion-board `rtm_receiver` (Agora RTM cloud teleoperation receiver) |
| Hard-Coded Material | AppID `<云凭据_01>`, channel `walker28`, userid `654321` |
| Impact | **High in the source report** — a client able to join the channel could inject teleoperation data toward `/quest_vr/*`, `/pico_vr/*`, `/mc/wbc/motion_d`, and glove-related topics |
| Source | `report_motion.md` (E6) |
| Re-verification | 🟢 All three strings were confirmed in the runtime binary; no token string was found |

## Vulnerability Mechanism

The robot uses Agora RTM to receive teleoperation data for controller, Quest VR, and Pico VR workflows. The AppID, channel name, and receiver userid are embedded in `rtm_receiver`.

- No token string was found in the binary, suggesting the project may rely on AppID-only access.
- The inbound `MessageDispatcher::dispatch` path deserializes received messages and publishes them toward motion-related topics.
- The source report found no independent MAC or signature validation in that inbound payload path.

This creates a potential cloud-side motion-control surface outside the LAN if an unauthorized client can join the channel with the embedded identifiers.

## Reproduction Script

`scripts/exploit_agora.py`

- Default safe mode extracts and confirms the three embedded identifiers from the local `rtm_receiver` binary.
- `--danger` only displays a code skeleton for the potential channel-join/injection flow; it does **not** connect to Agora.

## Evidence Output

- Local confirmation of AppID, channel, and userid strings.
- Documentation of the inbound dispatch path.
- Evidence retained under `evidence/`.

## Safety Boundary

⚠️ Joining the production Agora channel would involve external cloud interaction and could drive physical motion. The retained verification therefore stops at local credential/path confirmation.

The source report describes a full authorized test as joining the configured channel with the vendor SDK and observing whether a test payload reaches the relevant motion topics on a safely suspended robot; that external action was not performed in the retained validation.
