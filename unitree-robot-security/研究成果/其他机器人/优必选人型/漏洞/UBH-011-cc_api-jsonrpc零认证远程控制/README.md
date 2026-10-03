---
ID: UBH-011
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: cc_api-jsonrpc零认证远程控制
---
# UBH-011 V5 · Unauthenticated cc_api tbox JSON-RPC Control Surface

## 1. Summary

The `cc_api_client_tbox_main_demo` service exposes a large JSON-RPC-style method surface over TCP port 40000. Static analysis found motion, network, MQTT, skill, and work-control methods without a visible authentication/token layer. The live service responded to a connection fingerprint, while high-impact methods were not invoked.

## 2. Affected Products and Versions

- Component: vision-board `cc_api_client_tbox_main_demo` in container `walker-system.cc_api_client-1`.
- Port: `0.0.0.0:40000`, using a binary-framed tbox JSON-RPC protocol.
- Port 40000 was live and returned the expected short fingerprint response.

## 3. Validation Status

`statically confirmed` with live port/service evidence. No motion or network-changing RPC was executed.

## 4. Attack Preconditions

The attacker must reach TCP port 40000 and speak the proprietary binary framing protocol. Verification should use read-only methods only.

## 5. Root Cause

A broad privileged method registry is exposed without a caller-authentication or per-method authorization mechanism visible in the analyzed implementation.

## 6. Attack Procedure

The retained script extracts method names, fingerprints the service, and uses protocol notes to support a read-only RPC proof. High-impact methods are explicitly excluded from testing.

## 7. Impact

The exposed method set includes motion velocity, Wi-Fi/AP configuration, MQTT settings, and skill/work operations. If arbitrary callers can invoke those methods, the interface can cross network, cloud, and physical-control boundaries.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Use only read-only methods for live verification.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Add mutually authenticated transport and principal identity at the RPC layer.
- Apply per-method authorization rather than exposing one flat method namespace.
- Bind motion/network/cloud-changing methods to privileged local principals only.
- Add rate limits and audit logs for control-plane RPC calls.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# V5 · Unauthenticated cc_api tbox JSON-RPC Control Surface

| Item | Value |
|---|---|
| Component | Vision-board `cc_api_client_tbox_main_demo` (container `walker-system.cc_api_client-1`) |
| Port | `0.0.0.0:40000` (TCP, binary-framed tbox JSON-RPC) |
| Impact | **High** — method registry includes `motion.cmd_vel`, `network.wifi.ap.set`, `settings.iot.mqtt.set`, `skill.*`, and `work.*` |
| Source | `report_vision_core(1).md` (V5) |
| Re-verification | 🟢 Port 40000 live; a TCP connection returned a three-byte fingerprint response; the 12.7 MB runtime binary was extracted for analysis |

## Vulnerability Mechanism

The cc_api service implements a tbox JSON-RPC framework using C++/nlohmann::json and registers a large number of named methods. Static analysis did not identify a caller-authentication or token gate around the method registry.

Representative methods include:

- `motion.cmd_vel` — motion velocity;
- `network.wifi.ap.set` — network configuration;
- `settings.iot.mqtt.set` — cloud/MQTT configuration;
- `skill.*` and `work.*` — skill/task operations.

A raw JSON line did not work because the service uses a proprietary binary framing layer. Reverse-engineering notes for that framing are retained under `_worknotes/cc_api_protocol.md`.

## Reproduction Script

`scripts/exploit_cc_api.py`

Safe behavior:

1. Read the reverse-engineering notes when available.
2. Extract method names from the runtime/offline binary.
3. Optionally perform a read-only TCP fingerprint probe.

The intended minimal proof uses a read-only method such as `cc.api.fault.current.get`; motion, network, and skill methods are not invoked.

## Evidence Output

- Extracted method table.
- TCP fingerprint response.
- Binary framing notes.
- Supporting logs under `evidence/`.

## Safety Boundary

⚠️ Motion, network, and skill-control methods can have physical or connectivity effects and are not called by the retained verification.
