---
ID: UBH-024
validation_status: statically confirmed
severity: medium
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: voice-无认证语音服务与ASR堆越界读-1
---
# UBH-024 VB3 · Unauthenticated Voice Services and ASR Heap Out-of-Bounds Read

## 1. Summary

The vision-board voice stack exposes ASR, TTS, voiceprint, and extension services on all interfaces without an authentication layer. Static analysis additionally identified an ASR WAV parsing path that validates the 44-byte header but does not adequately ensure the declared data length matches the available buffer, creating an out-of-bounds-read/crash risk.

## 2. Affected Products and Versions

- Ports: 2022 (ASR), 2024 (TTS WebSocket), 2025 (voiceprint `/sv`), and 2026 (extension service).
- All four ports were live during re-verification.
- A benign TTS request to port 2024 returned a successful response without authentication.

## 3. Validation Status

`statically confirmed` for the ASR memory-safety issue, with live reachability evidence for the unauthenticated voice-service surface. The malformed-ASR crash probe was not sent.

## 4. Attack Preconditions

The attacker must be able to reach the voice-service ports on the network. Dynamic malformed-input testing should be confined to researcher-owned devices because it may crash the ASR process.

## 5. Root Cause

The service family lacks caller authentication, and the ASR parser trusts WAV length metadata without verifying that the corresponding payload bytes are actually present.

## 6. Attack Procedure

The retained probe fingerprints the four ports, sends a benign TTS request, checks voiceprint connectivity, and constructs a malformed WAV header offline without delivering it to ASR.

## 7. Impact

- Unauthenticated access to voice-related service functionality.
- Potential ASR process crash or unintended memory disclosure from an out-of-bounds read.
- Unauthenticated voiceprint registration/verification functionality is also part of the exposed surface.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The malformed ASR input is not transmitted by default.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Authenticate all voice-service connections.
- Validate all WAV chunk lengths against the actual received buffer before reading.
- Apply input-size limits and fail closed on malformed audio.
- Restrict voiceprint enrollment/verification to authenticated principals.
- Add fuzzing and regression tests for malformed audio headers.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# VB3 · Unauthenticated Voice Services and ASR Heap Out-of-Bounds Read

| Item | Value |
|---|---|
| Component | Vision-board voice stack (TTS / ASR / voiceprint / extension services) |
| Ports | `2022` ASR · `2024` TTS WebSocket · `2025` voiceprint `/sv` · `2026` extension; all bound to `0.0.0.0` |
| Impact | **Medium–High in the source report** — unauthenticated voice access plus an ASR heap out-of-bounds-read/crash condition |
| Source | `report_voice_boot(1).md` (VB3, VB5) |
| Re-verification | 🟢 All four ports live; a benign TTS request returned a success response |

## Vulnerability Mechanism

- **Unauthenticated service family:** ASR, TTS, and voiceprint services are reachable from the LAN without a token or message signature.
- **ASR out-of-bounds read:** the WAV parser checks the fixed-size header but does not adequately validate that the declared audio-data length is backed by actual received bytes. A mismatch can make the parser read beyond the available input.
- **Voiceprint endpoint:** the `/sv` service exposes enrollment/verification functionality without an observed authentication gate.

## Reproduction Script

`scripts/exploit_voice.py`

Safe default behavior:

1. Fingerprint the four ports.
2. Send a benign TTS text request and parse the response.
3. Probe the voiceprint WebSocket connection.
4. Construct a minimal WAV header locally to illustrate the length-validation issue.

The danger mode only describes the malformed-ASR delivery path; it does not send the payload.

## Evidence Output

- Four-port reachability.
- TTS request/response evidence.
- Constructed WAV header bytes.
- Supporting logs under `evidence/`.

## Safety Boundary

⚠️ Delivering the malformed ASR input may consume resources or crash the ASR service. The retained workflow does not send it.
