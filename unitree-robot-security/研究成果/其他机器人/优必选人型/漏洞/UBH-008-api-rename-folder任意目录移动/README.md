---
ID: UBH-008
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: api-rename-folder任意目录移动
---
# UBH-008 t800-web-backend `/api/rename-folder` Arbitrary Directory Move

## 1. Summary

The unauthenticated FastAPI endpoint `/api/rename-folder` accepts fully caller-controlled source, destination, and target-directory parameters. Source review shows no canonicalization or containment check, so the primitive can move directories outside the intended application root.

## 2. Affected Products and Versions

- Component: `t800-web-backend` v0.2.9 on port 5000.
- Evidence date: 2026-08-29.
- The destructive move operation was not repeated on the live robot because the risk outweighed the value of re-validation.

## 3. Validation Status

`statically confirmed` from source-level evidence. No destructive live move was performed.

## 4. Attack Preconditions

The attacker must be able to reach the unauthenticated backend endpoint. Any dynamic proof should be limited to a disposable temporary directory and restore the moved object afterward.

## 5. Root Cause

All three path-related parameters are user controlled, including `target_dir`, and the implementation calls `shutil.move` without resolving and constraining the source/destination to an allowed root.

## 6. Attack Procedure

The source report demonstrates the vulnerable path composition. The migration does not add a destructive live proof.

## 7. Impact

An unauthenticated caller can potentially move application or bind-mounted host directories, causing configuration loss, denial of service, or moving writable content into a security-sensitive load path.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). A safe proof should use only a temporary test directory.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Require authentication and authorization for the endpoint.
- Resolve `src`, `dst`, and `target_dir` with realpath/canonicalization and require all final paths to remain beneath approved roots.
- Reject absolute paths, traversal components, and symlink escapes.
- Add regression tests for path traversal and cross-mount moves.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# t800-web-backend `/api/rename-folder` Arbitrary Directory Move

> Version: 2026-08-29 · Method: source audit (report-level evidence); destructive movement was not repeated on the live robot.

## 1. Executive Summary

The FastAPI endpoint `/api/rename-folder` accepts three caller-controlled path parameters. In particular, `target_dir` may be an arbitrary or traversed path. The implementation performs an unauthenticated directory move without a containment check.

Potential consequences include configuration loss, service disruption, and moving attacker-writable content into a sensitive load/execution location.

Severity in the source report: **High**.

## 2. Root Cause

Source: `t800-web-backend/controller/upload.py`.

```python
# reconstructed pseudocode
@app.post("/api/rename-folder")
def rename_folder(src: str, dst: str, target_dir: str):
    # no realpath/prefix containment check
    shutil.move(join(MAP_ROOT, src), join(target_dir, dst))
```

- `target_dir` can select an arbitrary destination.
- `src` and `dst` are concatenated without a final-path containment check.

## 3. Security Path

```
Unauthenticated POST /api/rename-folder
        ↓
caller-controlled source and destination
        ↓
directory moved outside expected application root
        ↓
configuration loss / service failure / sensitive-load-path placement
```

## 4. Affected Scope

- Component: `t800-web-backend` v0.2.9 (FastAPI :5000).
- Entry point: unauthenticated `POST /api/rename-folder`.
- Container bind mounts may expose host paths such as `/etc/walker`.

## 5. Reproduction

The report confirms the three caller-controlled parameters from source. A minimal live test should move only a disposable directory under `/tmp/<random>` and restore it immediately. That destructive operation was not executed during repository migration.

## 6. Recommendations

1. Add authentication.
2. Canonicalize all paths and constrain them to explicit allowed roots.
3. Reject absolute paths and `..` traversal.

## 7. Evidence

The source report `WALKER_S2_PWN.md` contains the path-control analysis and remediation notes.
