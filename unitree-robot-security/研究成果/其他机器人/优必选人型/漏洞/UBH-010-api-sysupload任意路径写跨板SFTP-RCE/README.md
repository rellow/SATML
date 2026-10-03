---
ID: UBH-010
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: api-sysupload任意路径写跨板SFTP-RCE-1
---
# UBH-010 t800-web-backend `/api/sysupload` Arbitrary Path Write via Cross-Board SFTP to RCE

## 1. Summary

The unauthenticated multipart endpoint `/api/sysupload` accepts caller-controlled file, path, and board-name parameters. For `board_name=motion`, the backend uses embedded internal SFTP credentials to copy the uploaded object to the motion board at the caller-selected path. The source report dynamically validated the resulting arbitrary-write-to-root chain on researcher-owned hardware and restored the modified file.

## 2. Affected Products and Versions

- Evidence date: 2026-08-29.
- Component: `t800-web-backend` v0.2.9 on port 5000.
- Internal target: motion board reached through the backend's SFTP helper.

## 3. Validation Status

`dynamically confirmed`. The source report records a complete probe, backup, controlled authorization-file modification, privileged login, and restoration cycle.

## 4. Attack Preconditions

The attacker must reach the unauthenticated web backend. No preexisting internal SSH credential is required from the caller because the backend itself holds the cross-board credential. Reproduction must remain on researcher-owned devices.

## 5. Root Cause

The endpoint combines three trust failures:

1. caller-controlled remote destination path and filename;
2. no authentication at the web API;
3. a backend-held cross-board SFTP credential that is automatically used to write to the motion board.

## 6. Attack Procedure

The English report preserves the chain and safety boundaries without reproducing reusable credential values. The retained script contains a harmless probe and an authorized full validation mode with restoration.

## 7. Impact

An unauthenticated web caller can turn the vision-board service into a privileged file-transfer deputy and place attacker-controlled content on the motion board. The source report dynamically closed this to root authority on the owned motion board.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Prefer harmless temporary-file probes; full validation requires backup/restoration.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Authenticate and authorize `/api/sysupload`.
- Canonicalize and allowlist destination paths and filenames.
- Remove embedded cross-board passwords and replace generic SFTP with a narrow authenticated service.
- Scope cross-board credentials to the minimum writable directory and operation.
- Add audit logs and regression tests for cross-board writes.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# t800-web-backend `/api/sysupload` Arbitrary Path Write via Cross-Board SFTP to RCE

> Version: 2026-08-29 · **Full chain dynamically validated on owned hardware**: unauthenticated HTTP → arbitrary write → backend SFTP transfer → motion-board privileged login → restoration.

## 1. Executive Summary

`POST /api/sysupload` accepts multipart `file`, `path`, and `board_name` parameters without authentication.

For a non-vision target such as the motion board, the backend:

1. writes the upload locally;
2. looks up the board's internal IP;
3. opens SFTP using an embedded backend credential;
4. writes the file to `path/filename` on the target board.

Because both path and filename are caller controlled, the endpoint becomes a cross-board arbitrary file-write primitive. The source report dynamically validated a chain in which a temporary test authorization key was placed on the owned motion board, root authority was confirmed through the board's configured privilege path, and the original file was restored.

Severity in the source report: **Critical**.

## 2. Root Cause

Source review of `/app/controller/upload.py` showed:

- an embedded internal SSH/SFTP credential;
- caller-controlled `path` and `filename`;
- automatic selection of the motion board's internal address;
- no destination allowlist or canonical containment check.

Credential values are deliberately sanitized in the repository.

## 3. Validated Chain

```
Unauthenticated POST /api/sysupload
        ↓
board_name selects motion board
        ↓
backend uses its own embedded SFTP authority
        ↓
caller-controlled remote path receives uploaded content
        ↓
controlled authorization-file modification on owned board
        ↓
privileged access confirmed
        ↓
original content restored
```

## 4. Affected Scope

- `t800-web-backend` v0.2.9.
- Entry: unauthenticated `POST /api/sysupload`.
- Cross-board reach: vision service to motion board via internal SFTP.

## 5. Live Validation

The retained `sysupload_rce.py` separates non-destructive probing from the full authorized chain.

The recorded run:

1. proved arbitrary write using a temporary marker;
2. backed up the target authorization file;
3. removed a prior local directory/file collision when necessary;
4. performed a controlled test modification;
5. confirmed the expected privileged shell path;
6. restored the original file and verified cleanup.

Evidence is retained in `evidence/rce_motion_shell_2026-08-29.txt`. Reusable credential and key material are not reproduced here.

## 6. Recommendations

1. Require authentication and authorization.
2. Restrict `path` to an explicit canonical upload root and sanitize filenames.
3. Remove generic embedded SFTP credentials and replace them with a narrowly scoped internal update service.
4. Treat vision-to-motion file transfer as a privilege boundary with explicit authorization.
