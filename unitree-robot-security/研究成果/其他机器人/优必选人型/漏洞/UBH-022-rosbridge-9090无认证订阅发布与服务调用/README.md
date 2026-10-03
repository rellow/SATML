---
ID: UBH-022
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: rosbridge-9090无认证订阅发布与服务调用-1
---
# UBH-022 Unauthenticated rosbridge :9090 Subscription, Publication, and Service Calls

## 1. Summary

The vision board exposes ROS 2 rosbridge over WebSocket port 9090 without an authentication layer. Read-only validation confirmed anonymous subscription and service enumeration/calls, while the source report identified motion, firmware-update, network, voice, and camera interfaces reachable through the same bridge. No motion-control topic was published during validation.

## 2. Affected Products and Versions

- Component: ROS 2 rosbridge_suite on vision-board port 9090.
- Live evidence includes anonymous subscription to `/emb/battery_state` and read-only service calls returning board/version data.
- High-impact interfaces such as `/emb/upgrade` were enumerated but not called.

## 3. Validation Status

`statically confirmed` for the broader high-impact control surface, with live read-only confirmation of unauthenticated rosbridge access.

## 4. Attack Preconditions

The attacker must reach the WebSocket service. Verification should remain limited to read-only subscription/enumeration unless physical safety controls are in place.

## 5. Root Cause

rosbridge exposes the robot's ROS graph to network clients without an integrated authentication and authorization layer, and high-impact topics/services do not have a separate per-caller security boundary at the bridge.

## 6. Attack Procedure

The retained validation subscribes to benign state topics and invokes read-only version/identity services. It does not publish motion messages or invoke firmware/network-changing services.

## 7. Impact

Unauthenticated access can expose sensor/state information and, if publication/service-call operations are used, potentially project a network caller into internal motion, network, firmware-update, voice, and camera interfaces.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Use read-only subscription and enumeration for routine validation.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Place rosbridge behind an authenticated gateway.
- Apply topic/service-level ACLs, especially for motion, firmware, network, and camera interfaces.
- Restrict port 9090 to a dedicated management network.
- Add separate authentication/signature checks to high-impact services such as firmware update.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Unauthenticated rosbridge :9090 Subscription, Publication, and Service Calls

> Version: 2026-08-29 · Method: report evidence plus read-only live confirmation.
> **Boundary statement:** validation was limited to subscription, enumeration, and benign read-only service calls. No motion-control publication or firmware update was performed.

## 1. Executive Summary

The vision board runs ROS 2 rosbridge_suite on port 9090 with no observed authentication layer. The research confirmed that an anonymous client could:

- subscribe to `/emb/battery_state`;
- advertise a topic without an authentication challenge;
- call read-only services such as `/emb/getVer`, `/sys/sn/read`, and `/emb/bat_info_get`.

The exposed graph also includes higher-impact interfaces associated with EtherCAT/servo control, navigation, Wi-Fi configuration, speech, camera data, and `/emb/upgrade`. Those interfaces were not exercised during safety-bounded validation.

Severity in the source report: **Critical**, because a network bridge reaches the internal robot control plane.

## 2. Root Cause

The ROS 2 rosbridge deployment does not provide an authentication/authorization mechanism equivalent to a caller identity plus per-topic/service ACLs. As a result, the network-exposed bridge inherits the authority of the internal ROS graph.

## 3. Attack Surface

| Category | Example | Risk |
|---|---|---|
| Subscription | `/emb/battery_state` | passive state/sensor disclosure |
| Publication | arbitrary advertised topics | false-state/control injection if accepted downstream |
| Read-only services | `/emb/getVer`, `/sys/sn/read`, `/emb/bat_info_get` | board/version/identifier disclosure |
| Firmware update | `/emb/upgrade` | potential update abuse; not invoked |
| High-impact interfaces | EtherCAT servo, navigation, Wi-Fi, speech, camera topics/services | physical/network/privacy impact |

## 4. Affected Scope

- Component: rosbridge_suite (ROS 2).
- Entry point: WebSocket port 9090.
- A second WebSocket service on 9099 is tracked separately in the broader research notes.

## 5. Reproduction

The source report's safe validation consisted of anonymous WebSocket connection, read-only topic subscription, service enumeration, and benign service calls. The retained artifact does not publish motion messages or invoke update operations.

## 6. Recommendations

1. Add an authenticated gateway in front of rosbridge.
2. Enforce fine-grained topic/service ACLs.
3. Restrict network reachability to a management plane.
4. Independently authenticate high-impact services such as firmware update.

## 7. Evidence

The source `WALKER_S2_PWN.md` records anonymous subscription results, the enumerated service set, and the exposed high-impact interfaces.
