---
ID: GAL-005
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: TCP8888网络手柄协议未授权接入与配置泄露-1
---
# GAL-005 Galileo TCP 8888 Virtual-Gamepad Service Unauthenticated Access and Configuration Disclosure

## 1. Summary

The robot's virtual-gamepad TCP service listens on `0.0.0.0:8888` without authentication or pairing. A three-byte synchronization request triggers disclosure of the complete virtual-joystick YAML configuration. Arbitrary clients can also read/write 14 virtual bit slots and receive periodic state updates. Earlier claims that this directly controlled motion were downgraded after independent review showed the callback/control chain is not connected in the tested firmware.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: `libgamepad_sdk.so` / `GamepadReceiver`, loaded by the virtual-joystick app.
- Listener: TCP 8888 on all interfaces.

## 3. Validation Status

`statically confirmed` through protocol reverse engineering and cross-review. The unauthenticated/configuration-disclosure behavior is retained; direct motion-control impact is explicitly **not** claimed for the tested version.

## 4. Attack Preconditions

The attacker needs network reachability to TCP 8888.

## 5. Root Cause

The service accepts connections without authentication, source restriction, or pairing and includes an unauthenticated configuration-file response path.

## 6. Attack Procedure

The retained proof can request the configuration file, receive state updates, or write virtual bit slots. The report treats bit-slot manipulation as state interference/log impact rather than motion control because the downstream callback is unconnected.

## 7. Impact

- Disclosure of joystick configuration, mapping, and internal-network information.
- Unauthorized receipt of status updates.
- Interference with shared virtual bit state.
- Exposure of an unauthenticated network service.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The configuration request is read-only.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Authenticate the connection and restrict source networks.
- Disable configuration-file download for unauthenticated clients.
- Bind the service only to an intended management interface.
- If the bit-to-control callback is re-enabled in future firmware, require authorization before accepting control input.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo TCP 8888 Virtual-Gamepad Service Unauthenticated Access and Configuration Disclosure

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | `libgamepad_sdk.so` GamepadReceiver |
| Type | Unauthenticated network access + configuration disclosure |
| Listener | TCP 8888, `0.0.0.0` |
| Validation | Reverse engineering + external-audit cross-check |

## Vulnerability Overview

`GamepadReceiver` accepts TCP connections with no authentication/pairing/source restriction.

Protocol summary:

- state frame: fixed header, 14 bytes of virtual bit data, fixed trailer;
- a short synchronization request causes the server to stream the virtual-joystick YAML configuration;
- the service periodically sends state packets to the connected client;
- writes update shared virtual bit slots with last-writer-wins semantics.

## Important Impact Downgrade

The research originally treated the bit-writing path as unauthorized motion control. Independent review corrected that conclusion:

1. `GamepadReceiver::setCallback` has no effective caller in the tested build.
2. The only consumer of the active bits logs their state and does not import/publish through DataCenter/LCM/SHM control APIs.
3. Several configured switch bits are structurally outside the available 14-byte data region.

Therefore, **the unauthenticated listener and configuration disclosure are real, but the tested bit data does not directly drive motion control**.

## Protocol Evidence

- listener: bind `INADDR_ANY`, listen backlog 1;
- receive thread: accept/recv → parser;
- short sync frame → `sendConfigFile`;
- normal frame → update virtual bit slots;
- send thread → periodic state packets.

## Safe Reproduction

The retained tool supports:

- configuration retrieval;
- receiving periodic state;
- writing bit slots for non-physical state-interference validation.

## Evidence

- `evidence/parsePacket_disassembly.txt`
- `evidence/virtual_joystick_app_config.yaml`
- independent dynsym/import review
- external audit `AUD-udp-gamepad-tcp8888-unauth.md`
