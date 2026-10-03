---
ID: UBH-017
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: list-files任意递归列目录全盘文件泄露-1到ssh
---
# UBH-017 t800-web-backend `/list-files` Arbitrary Recursive Directory Listing

## 1. Summary

The unauthenticated `GET /list-files` endpoint accepts a caller-controlled directory parameter and recursively enumerates that directory tree. The original report captured a roughly 60,040-entry root-level listing, making the endpoint useful for locating sensitive configuration, keys, scripts, and other files before combining it with separate read/write primitives.

## 2. Affected Products and Versions

- Component: `t800-web-backend` v0.2.9 on port 5000.
- Evidence combines source review, report-level evidence, and a 2026-08-29 live re-check.
- The live re-check showed an unexpected Windows-style path mapping, which is preserved as an environment ambiguity.

## 3. Validation Status

`dynamically confirmed` for unauthenticated endpoint behavior; the exact runtime filesystem mapping observed in the later re-check requires clarification.

## 4. Attack Preconditions

The attacker must reach port 5000. Directory listing is read-only, but any follow-on file access should remain within authorized data.

## 5. Root Cause

The `map_dir` parameter is accepted without an allowed-root constraint or effective canonicalized-path check before recursive traversal.

## 6. Attack Procedure

A caller supplies a target directory and receives recursive file-tree metadata. The retained validation uses benign directories and does not access file contents.

## 7. Impact

Directory enumeration can expose the names and locations of keys, configuration files, service scripts, SSH material, and other sensitive targets. Combined with separate arbitrary-read/write endpoints, this significantly lowers the cost of exploitation.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Keep tests read-only.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Require authentication.
- Canonicalize `map_dir` and restrict it to explicit allowed roots.
- Limit recursion depth and maximum result count.
- Avoid returning sensitive filesystem topology to untrusted callers.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# t800-web-backend `/list-files` Arbitrary Recursive Directory Listing

> Version: 2026-08-29 · Method: source audit + report evidence + live re-check

## 1. Executive Summary

`GET /list-files` accepts caller-controlled `map_dir` and `is_map_folder` parameters and recursively enumerates the selected path without authentication. The original report recorded a roughly **60,040-entry** file tree when using the root filesystem.

The source report rates this directory-enumeration issue **Medium**, while noting that it composes strongly with the separate export/read and sysupload/write findings.

## 2. Root Cause

Reconstructed logic:

```python
@app.get("/list-files")
def list_files(map_dir: str = "", is_map_folder: bool = False):
    # caller-controlled map_dir
    # recursive traversal and return of the complete tree
```

No allowed-root constraint was identified for `map_dir`.

## 3. Security Path

```
Unauthenticated GET /list-files?map_dir=<target>
        ↓
recursive filesystem tree
        ↓
locate SSH material, configuration, scripts, keys, or other targets
        ↓
combine with separate file-read/write primitives if available
```

## 4. Affected Scope

- Component: `t800-web-backend` v0.2.9.
- Entry point: unauthenticated `GET /list-files`.

## 5. Live Re-Check (2026-08-29)

A benign request using `map_dir=/tmp` returned an error containing a Windows-style temporary path rather than the expected Linux container path. That suggests the specific target reached by the later probe may have been a Windows-mapped reproduction environment rather than the physical robot service.

This discrepancy is retained explicitly. It does not change the source-level path-validation issue, but the exact live deployment environment should be clarified before making additional device-specific claims.

## 6. Recommendations

1. Require authentication.
2. Canonicalize `map_dir` and constrain it to approved roots.
3. Bound traversal depth and response size.

## 7. Evidence

- Original `WALKER_S2_PWN.md` report with the large recursive listing.
- `evidence/listfiles_live.txt` with the 2026-08-29 path-mapping anomaly.
