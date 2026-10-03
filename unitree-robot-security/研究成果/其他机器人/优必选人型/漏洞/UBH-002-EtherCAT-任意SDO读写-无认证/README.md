---
ID: UBH-002
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: EtherCAT-任意SDO读写-无认证
---
# UBH-002 E1 · Unauthenticated Arbitrary EtherCAT SDO Read/Write

## 1. Summary

The ROS 2 service `/ecat/servo/access_sdo_16` accepts caller-supplied EtherCAT object-dictionary indices for SDO access without an allowlist at the service boundary. This exposes a lower-level servo configuration surface beneath ordinary motion-control APIs.

## 2. Affected Products and Versions

- Component: motion-board EtherCAT master node `ubt_ethercat_master`.
- Service: `/ecat/servo/access_sdo_16`.
- Service presence depends on the motion stack being active; the retained test distinguishes STANDBY from active runtime.

## 3. Validation Status

`statically confirmed` with service-presence/read-only validation where available. Dangerous SDO writes were not performed.

## 4. Attack Preconditions

The attacker must already have access to the robot's ROS/DDS graph through an exposed bridge, unauthenticated DDS domain, or prior foothold.

## 5. Root Cause

The SDO service accepts arbitrary object-dictionary indices and read/write mode without a server-side allowlist or operation-specific authorization.

## 6. Attack Procedure

The retained probe performs only safe reads of benign object-dictionary entries when the service is active. A danger mode displays representative write requests but does not send them.

## 7. Impact

An attacker with service access could bypass higher-level motion APIs and modify low-level servo configuration, potentially changing torque/position limits, state, or vendor-specific parameters.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Default behavior is read-only.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Restrict SDO indices to a narrow allowlist and separate read from write permissions.
- Authenticate and authorize callers at the DDS/service layer.
- Disable arbitrary write access outside maintenance mode.
- Add safety-state checks and audit logging for all servo-parameter writes.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# E1 · Unauthenticated Arbitrary EtherCAT SDO Read/Write

| Item | Value |
|---|---|
| Component | Motion-board EtherCAT master node `ubt_ethercat_master` |
| Service | ROS 2 `/ecat/servo/access_sdo_16` |
| Impact | **Critical in the source report** — arbitrary object-dictionary entries can be read or written without an index allowlist |
| Source | `report_motion.md` (E1) |
| Re-verification | 🟢 Service is part of the runtime graph when the motion stack is enabled |

## Vulnerability Mechanism

`access_sdo_16` accepts a slave address, object-dictionary index/sub-index, data value, and access direction. The analyzed implementation does not restrict the caller to a safe subset of indices.

The source report identifies representative safety-sensitive or low-level entries including position/torque/state values and vendor-specific SDOs. Access to this service therefore bypasses higher-level motion-control mediation and reaches the servo configuration layer directly.

## Reproduction Script

`scripts/exploit_sdo_readwrite.py`

- Default safe mode reads benign entries such as device type/status when the service is active.
- The script explicitly reports when the motion master is not running rather than treating absence as a failure.
- `--danger` only prints representative write messages; it does not send them.

## Evidence Output

- Successful read response when the service is active.
- Clear STANDBY indication when the motion master is not running.
- Session logs under `evidence/`.

## Safety Boundary

⚠️ The retained script does not write any SDO. Actual writes can alter joint parameters and require a safely suspended robot, emergency-stop readiness, and explicit human authorization.
