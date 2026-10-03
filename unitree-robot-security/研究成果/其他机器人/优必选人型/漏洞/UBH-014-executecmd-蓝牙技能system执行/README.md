---
ID: UBH-014
validation_status: candidate
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: executecmd-蓝牙技能system执行
---
# UBH-014 V3 · ExecuteCmd Bluetooth Skill to `system()` — Candidate

## 1. Summary

An earlier static report described a Bluetooth skill mechanism in which a writable skill file could feed a command to `system()`. Live re-verification on the current `walker-s2/system:ws2_vision-v0.40.1` image did **not** find the expected `/etc/walker/skills` directory or the `ExecuteCmd` implementation string. The finding is therefore retained only as a **candidate/version-dependent lead**, not a confirmed vulnerability on the tested image.

## 2. Affected Products and Versions

- Component originally attributed to the vision-board Bluetooth-control container `walker-system.ae_bt_master`.
- Current live image: `walker-s2/system:ws2_vision-v0.40.1`.
- On that image, neither the host nor relevant containers contained the expected skill directory or `ExecuteCmd` string.

## 3. Validation Status

`candidate`. Live re-verification failed to reproduce the earlier static mechanism.

## 4. Attack Preconditions

Any follow-up must first establish that the relevant firmware version actually contains the skill-execution code path and that the Bluetooth control surface can reach it.

## 5. Root Cause

The original hypothesis was that a Bluetooth-controlled skill mechanism read commands from a host-writable skill directory and passed them to `system()`. That mechanism was not found on the current tested firmware.

## 6. Attack Procedure

No live exploit procedure is claimed for the current image. The retained script performs search and evidence collection only.

## 7. Impact

If the older/version-specific mechanism exists as originally reported, combining a writable skill definition with remote skill triggering could lead to command execution. This remains unverified on the current firmware.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Do not create or trigger skill payloads unless the code path is first confirmed in an authorized firmware version.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13, including the negative live evidence.

## 10. Recommendations

- Continue treating skill execution as a privileged operation.
- Require authenticated, authorized skill installation and invocation.
- Avoid shell execution of skill-defined content.
- Preserve the negative/version-specific evidence so the finding is not overstated.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.
- This item remains a lead pending confirmation on another firmware/code path.

## 13. Sanitized Original Research Body

# V3 · ExecuteCmd Bluetooth Skill to `system()` — Candidate

| Item | Value |
|---|---|
| Component | Originally attributed to vision-board Bluetooth control (`walker-system.ae_bt_master`) |
| Hypothesized Capability | `ExecuteCmd` reads a skill command and passes it to `system()` |
| Original Impact | Writable skill directory could make skill creation equivalent to privileged command execution |
| Source | `report_vision_core(1).md` (V3) |
| Re-verification | ⚠️ **Not reproduced** on `walker-s2/system:ws2_vision-v0.40.1` |

## Re-Verification Result

A full live search across the host and relevant containers did not find:

- `/etc/walker/skills`;
- an `ExecuteCmd` string;
- the reported skill-file execution path.

The running `ae_bt_master` instead appeared to use the tbox JSON-RPC framework, similar to the cc_api interface. If equivalent skill functionality still exists, it may be exposed through a different method family rather than the originally reported filesystem path.

## Original Hypothesis

The earlier static report proposed:

1. a Bluetooth-accessible skill mechanism;
2. a host-writable skill directory;
3. skill files containing commands;
4. direct execution through `system()`.

If all four properties existed together, a malicious skill could become a command-execution primitive. Because the live image did not contain the expected mechanism, the repository does **not** claim that chain for the current firmware.

## Reproduction Script

`scripts/exploit_executecmd.py`

Safe behavior:

1. Confirm the `ae_bt_master` container is running.
2. Check whether `/etc/walker/skills` exists and inspect permissions.
3. Search the container for `ExecuteCmd`, `system(`, and skill-related strings.

The optional danger mode only displays the hypothetical skill structure and does not write or trigger anything.

## Conclusion

This item is retained to document a previously reported/version-dependent code path and the negative live re-verification. Further work should first identify a firmware image containing the original mechanism.
