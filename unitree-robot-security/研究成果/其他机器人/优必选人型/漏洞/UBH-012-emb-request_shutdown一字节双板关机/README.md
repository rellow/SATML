---
ID: UBH-012
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: emb-request_shutdown一字节双板关机
---
# UBH-012 S4 · One-Byte Dual-Board Shutdown via `/emb/request_shutdown`

## 1. Summary

- Impact: **Critical in the source report** — a one-byte request can cause both the vision and motion boards to shut down.
- The service/topic was observed live, but the destructive shutdown action was deliberately not triggered.

## 2. Affected Products and Versions

- Component: vision-board `/emb/*` service bridge.
- The shutdown path uses privileged internal SSH from the vision board to the motion board.
- Recovery after a full shutdown requires manual power-on.

## 3. Validation Status

`statically confirmed` with live presence/reachability evidence. The destructive effect was not dynamically executed.

## 4. Attack Preconditions

The attacker must be able to reach the relevant internal service interface. Reproduction must use researcher-owned devices and an authorized environment; destructive shutdown should not be triggered during ordinary verification.

## 5. Root Cause

A high-impact shutdown action is exposed through an unauthenticated service request and is executed using privileged internal credentials held by the service.

## 6. Attack Procedure

The source report records the one-byte trigger structure and downstream shutdown sequence. The retained safe probe verifies service presence and payload structure without sending the destructive request.

## 7. Impact

A successful trigger would shut down both vision and motion boards, causing whole-robot unavailability until manual power restoration. In combination with a persistence mechanism, repeated triggering could create sustained physical denial of service.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The retained probe is intentionally non-destructive.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Require authentication and operation-specific authorization for shutdown services.
- Restrict shutdown interfaces to a dedicated trusted maintenance domain.
- Remove passwordless cross-board root SSH where possible.
- Add rate limiting, audit logging, and negative regression tests for shutdown control paths.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review evidence and vendor-coordination status.

## 13. Sanitized Original Research Body

# S4 · One-Byte Dual-Board Shutdown via `/emb/request_shutdown`

| Item | Value |
|---|---|
| Component | Vision-board `/emb/*` service (JS bridge) |
| Interface | `/emb/request_shutdown`, `value = 0xAA` |
| Impact | **Critical in the source report** — one byte can request shutdown of both the vision and motion boards |
| Source | `report_system(1).md` (S4) |
| Re-verification | 🟢 Service/topic remained present under read-only probing; actual shutdown was not triggered |

## Vulnerability Mechanism

When `/emb/request_shutdown` receives `0xAA`, the implementation invokes privileged shutdown operations for both boards through internal SSH.

- No caller authentication is enforced at the exposed service boundary.
- The service itself holds privileged internal SSH capability.
- A successful trigger would shut down the robot and require manual power restoration.
- If combined with a persistent foothold, repeated triggering could create sustained physical unavailability.

## Reproduction Script

`scripts/exploit_shutdown.py`

- Default safe mode: confirms the topic/service exists and displays the `data=[0xAA]` payload without transmitting it.
- `--danger`: displays the triggering code path, but the script intentionally refuses to send the destructive request.

## Evidence Output

- Topic/service presence.
- One-byte trigger structure.
- Downstream dual-board shutdown sequence.
- Evidence retained under `evidence/`.

## Safety Boundary

⚠️ **Do not trigger the actual shutdown during normal verification.** A successful trigger disconnects the robot and requires physical power restoration.

The source report states that sending `{"value": 0xAA}` to `/emb/request_shutdown` would cause both boards to execute their shutdown paths within seconds; this destructive step was intentionally not executed during the retained validation.
