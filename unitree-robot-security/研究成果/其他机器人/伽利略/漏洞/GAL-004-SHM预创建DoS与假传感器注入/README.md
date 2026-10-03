---
ID: GAL-004
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: SHM预创建DoS与假传感器注入
---
# GAL-004 Galileo Shared-Memory Pre-Creation DoS and Fake-Sensor Injection

## 1. Summary

The motion-control stack exchanges sensor/command data through predictable POSIX shared-memory objects. The common initialization routine accepts pre-existing objects without authenticating their creator and can adopt attacker-controlled object sizes. An attacker with local filesystem access to `/dev/shm` can therefore squat the names before startup to break initialization or pre-create sensor segments and influence data consumed by control logic.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Components: motion-control shared-memory IMU, joint-state, odometry subscribers and joint-command publisher.
- Attack surface: any local UID able to create the relevant `/dev/shm` objects; remote compromise can compose into the same local primitive.

## 3. Validation Status

`statically confirmed` from configuration plus independently reviewed code/disassembly evidence. Destructive live sensor injection was not performed.

## 4. Attack Preconditions

The attacker requires local file/shared-memory creation authority on the robot, directly or through another RCE. Physical-effects testing requires safety restraints and cleanup.

## 5. Root Cause

Shared-memory names are predictable and the initializer uses an open-then-create pattern without validating the owner/creator, expected fixed size, origin, or message authenticity.

## 6. Attack Procedure

The safe workflow inspects configured SHM names and existing objects. A controlled squat test can create deliberately wrong-sized temporary objects before restarting the corresponding service, followed by cleanup.

## 7. Impact

- Persistent service-startup failure/DoS while the squatted object remains.
- Potential injection of false IMU, joint-state, or odometry data into motion-control observations.
- Potential direct command-segment tampering by a user/group with write permission.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Restore/remove all test SHM objects after validation.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Create SHM objects with exclusive ownership and restricted permissions.
- Validate object owner, fixed expected size, and creation provenance on attach.
- Add sequence numbers, integrity checks, and heartbeats to shared-memory messages.
- Isolate safety-critical SHM objects in a protected namespace/directory.
- Fail safely if sensor provenance is invalid.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo Shared-Memory Pre-Creation DoS and Fake-Sensor Injection

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Components | SHM IMU/joint-state/odometry subscribers and joint-command publisher |
| Type | Insecure IPC: predictable, unauthenticated POSIX shared memory |
| Attack Surface | Local `/dev/shm`; remotely composable after another RCE |
| Validation | Configuration-level confirmation + independently reviewed disassembly |

## Vulnerability Mechanism

Motion control and HAL components exchange data through objects named from predictable prefixes such as:

- `shm_hw_imu`
- `shm_hw_joint_state`
- `shm_hw_joint_command`
- `shm_hw_odometry`

The analyzed `SharedMemoryData::Init` behavior is an open-then-create pattern:

- open an existing object if present;
- create it only if absent;
- on attach, accept the existing object's size;
- for create-mode callers, throw if an existing object's size differs;
- map the object read/write without authenticating its creator.

Because POSIX shared-memory objects are represented under `/dev/shm`, a local attacker can squat a predictable name even without using the SHM API.

## Attack A: Pre-Creation Squat / DoS

Before a service starts, create the command-segment name with the wrong size. The legitimate publisher later sees a size mismatch and fails initialization. Keeping the object present can make the failure persist across service restarts.

## Attack B: Fake Sensor Injection

Pre-create sensor-side SHM objects with attacker-controlled content. Consumers attach to the existing object and parse bytes as IMU/joint/odometry structures. False gravity/joint-state/odometry data can therefore influence control observations or localization.

The source report notes the physical risk of a controller reacting to falsified balance inputs.

## Safe Reproduction

The retained script supports:

- `check`: inspect SHM objects and motion processes.
- `squat`: controlled wrong-size pre-creation for a test segment plus service-start observation.
- `clean`: remove test segments and confirm recovery.

Sensor-falsification and live joint-command tampering are not part of routine validation.

## Evidence

- `evidence/shm_channel.yaml` / `evidence/shm_channel_yaml.txt`
- cross-static-validation notes
- external audit `AUD-w2mc-shm-precreate-dos.md`
