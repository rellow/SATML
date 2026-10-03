---
ID: UBH-025
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: wifi-set_ap命令注入到root
---
# UBH-025 V1 · Command Injection in `/sys/wifi/set_ap` Reaches Root Context

## 1. Summary

- Impact: **Critical in the source report** — SSID/password fields are incorporated into a shell command executed in a root context.
- Live triggering was intentionally avoided because changing Wi-Fi configuration could disconnect the research robot.

## 2. Affected Products and Versions

- Component: vision-board `ae_sys` service exposing the `/sys/*` API family.
- A full dynamic test requires a controlled environment in which network loss and recovery are acceptable.

## 3. Validation Status

`statically confirmed`. The unsafe string construction and gate identifier were confirmed; the command-injection path was not triggered on the live network interface.

## 4. Attack Preconditions

The attacker must reach the relevant service/API boundary and satisfy any interface-level gate. Verification should remain on researcher-owned hardware in an environment where network reconfiguration can be safely recovered.

## 5. Root Cause

The `/sys/wifi/set_ap` handler builds a shell command by interpolating attacker-controlled SSID/password strings without robust argument separation or escaping, then executes that command in a root context. The interface gate identifier is also embedded in the binary rather than providing a strong authenticated authorization boundary.

## 6. Attack Procedure

The retained script extracts the gate identifier, reconstructs the vulnerable command locally, and checks interface reachability. It does not submit a live network-changing request.

## 7. Impact

If the vulnerable handler is invoked with crafted input, the resulting shell command can execute unintended operations with the privileges of the service. Because the service runs as root, the impact extends to complete host compromise.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The retained test is intentionally non-invasive and does not alter Wi-Fi settings.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Replace shell-string construction with direct library/API calls or argv-style process execution.
- Strictly validate SSID/password data as data, not shell syntax.
- Replace static gate identifiers with authenticated and authorized callers.
- Drop service privileges and isolate network-management operations.
- Add regression tests for shell metacharacters and encoding edge cases.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review embedded identifiers, evidence, and vendor-coordination status.

## 13. Sanitized Original Research Body

# V1 · Command Injection in `/sys/wifi/set_ap` Reaches Root Context

| Item | Value |
|---|---|
| Component | Vision-board `ae_sys` service (`/sys/*` API) |
| Interface | `/sys/wifi/set_ap` (JSON-RPC) → `system()` |
| Impact | **Critical in the source report** — SSID/password fields are concatenated into a shell command executed as root |
| Source | `report_vision_core(1).md` (V1) |
| Re-verification | 🔒 Static confirmation only; live `/sys/wifi/*` calls were avoided because they can break network connectivity |

## Vulnerability Mechanism

The `ae_sys` handler for `/sys/wifi/set_ap` incorporates SSID and password strings directly into a shell command. The source report confirmed that the resulting command is executed by a root-context service.

A crafted value containing shell syntax could therefore alter the intended command structure. The gate UUID `51b00e11-112d-cbec-1828-17c0734624df` is present in cleartext in the binary and is not, by itself, a cryptographic authorization mechanism.

## Reproduction Script

`scripts/exploit_wifi_setap.py`

Safe default behavior:

1. Extract the API key/gate UUID evidence.
2. Construct and display a representative injected command locally without invoking it.
3. Probe whether the surrounding RPC bridge is online.

The optional danger mode only displays the service-call structure; it does not send the network-changing request.

## Evidence Output

- Embedded UUID/API-key material.
- Locally reconstructed vulnerable command string.
- Supporting material retained under `evidence/`.

## Safety Boundary

🚫 The retained test does **not** invoke `/sys/wifi/*`, because changing the robot's network configuration could disconnect the test system. A fully authorized dynamic proof should use a disposable network setup and a harmless marker operation, followed by restoration of the original configuration.
