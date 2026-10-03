---
ID: GAL-003
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: ONNX策略未签名供应链植入
---
# GAL-003 Galileo Unsigned ONNX Motion-Policy Supply-Chain Implant

## 1. Summary

Galileo motion policies are stored as writable ONNX models and YAML configuration in the `galileo` user's tree and are loaded by the motion-control process without a vendor signature or pinned hash. Policy transitions rebuild the ONNX runtime session from disk. A prior web-RCE/file-write primitive can therefore become a persistent physical-control implant by replacing a policy artifact, and a remotely reachable policy-switch mechanism can later activate it.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Components: ONNX policy inference/recovery libraries and `share/policy/<name>/policy.onnx`.
- Seven policy directories and their configuration files were independently confirmed.

## 3. Validation Status

`statically confirmed`. File-level integrity properties and loader behavior are supported by source/binary evidence; a malicious policy was not deployed on the robot.

## 4. Attack Preconditions

The attacker first needs write authority to the policy tree, such as through a separate web/file-write finding or local access. Activation then requires a policy transition through a reachable control path.

## 5. Root Cause

Motion-control artifacts have no cryptographic signature/hash binding, reside in a writable tree, and are reloaded from disk during policy transitions.

## 6. Attack Procedure

The retained safe workflow hashes policy files, inspects configuration, and can substitute a benign structurally compatible model in a controlled test with automatic backup/restore. It does not install a malicious motion policy.

## 7. Impact

- Persistent modification of robot motion behavior across restart.
- Tampering with policy safety limits and gains stored in YAML.
- Motion-control denial of service by corrupting/removing a model.
- A remote file-write vulnerability can therefore become a long-lived physical backdoor without a persistent shell.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Keep any substitution benign and restore the original immediately.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Sign policy ONNX/YAML artifacts with a vendor key or place them on an immutable verified partition.
- Verify signatures/hashes before every policy load or transition.
- Move hard safety limits out of the writable policy tree.
- Restrict policy-transition APIs to authenticated callers.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo Unsigned ONNX Motion-Policy Supply-Chain Implant

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Components | ONNX policy inference and recovery libraries |
| Type | Missing integrity protection for safety-critical model artifacts (CWE-494) |
| Attack Surface | Writable `galileo` policy tree; can compose with remote file-write/RCE findings |
| Validation | File-level confirmation + loader-path analysis |

## Vulnerability Overview

Each locomotion behavior is represented by an ONNX network loaded by the motion-control process. Policy output maps directly to joint targets. The policy tree contains several model directories and writable YAML files describing gains, limits, scaling, default joint positions, and fall-detection thresholds.

The source report identified three key properties:

1. **No cryptographic integrity check.** The loader relies on ONNX parsing rather than a vendor signature or pinned digest.
2. **Runtime reload.** A policy transition rebuilds the ONNX runtime session from the model on disk.
3. **Writable safety configuration.** Related YAML files containing safety/limit parameters live in the same writable tree.

A separate network file-write or web-RCE primitive can therefore replace a policy without maintaining a resident process. A later policy transition activates the changed artifact.

## Confirmed File-Level Evidence

The research confirmed seven policy directories, including locomotion, slope/stair, quadruped, release, and recovery variants, with corresponding ONNX/YAML files.

Representative configuration fields included:

- action position/velocity scaling;
- `clip_actions`;
- joint-name and default-position arrays;
- joint torque/velocity limits;
- fall-detection thresholds.

## Security Chain

```
remote/local file-write authority
        ↓
replace policy.onnx or related safety YAML
        ↓
policy transition reloads artifact from disk
        ↓
unverified model/config drives joint targets
        ↓
persistent altered motion behavior or DoS
```

## Safe Reproduction

The retained test records hashes/configuration and can use a benign compatible policy substitution with backup/restore to demonstrate the absence of an integrity gate. No malicious motion model is deployed.

## Recommendations

1. Vendor-sign policy and configuration artifacts.
2. Verify on every load/transition.
3. Keep hard safety limits in a separately protected layer.
4. Authenticate policy-transition control paths.

## Evidence

- `evidence/policy目录清单.txt`
- cross-validation report under the external audit archive
- original round-2 analysis `AUD-w2mc-onnx-unsigned-policy-supply-chain.md`
