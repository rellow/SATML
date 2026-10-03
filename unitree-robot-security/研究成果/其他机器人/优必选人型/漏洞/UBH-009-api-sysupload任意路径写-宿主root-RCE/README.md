---
ID: UBH-009
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: api-sysupload任意路径写-宿主root-RCE
---
# UBH-009 t800-web-backend Arbitrary Path Write to Host-Root RCE

## 1. Summary

The unauthenticated `/api/sysupload` endpoint permits an arbitrary local destination path. Because the web-backend container runs as root and bind-mounts sensitive host paths read/write, the container write can directly modify the host filesystem. The source report dynamically closed the chain on the researcher-owned vision board and restored the modified file afterward.

## 2. Affected Products and Versions

- Evidence date: 2026-08-29.
- Component: `walker-web.web-backend-1`, t800-web-backend v0.2.9.
- The container runs as root and has read/write bind mounts including host SSH/configuration locations.

## 3. Validation Status

`dynamically confirmed`. The source report records a complete backup → benign authorized modification → privileged login validation → restoration cycle on the owned device.

## 4. Attack Preconditions

The attacker must reach the unauthenticated web backend. Reproduction must be limited to researcher-owned hardware, with backups and automatic cleanup/restoration.

## 5. Root Cause

Three properties compose:

1. `/api/sysupload` accepts caller-controlled destination paths without a safe-root allowlist.
2. The container runs as root.
3. Sensitive host directories are mounted read/write into the container.

This makes an arbitrary container-path write equivalent to an arbitrary host-path write for mounted locations.

## 6. Attack Procedure

The retained artifact documents the chain and includes a harmless probe mode. Sensitive credential values and reusable private material are not reproduced in the English report.

## 7. Impact

An unauthenticated network caller can cross the container boundary and obtain host-root authority on the vision board. The source report rates this **Critical** because it is a zero-credential arbitrary-write-to-root chain.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Prefer the safe probe mode; any full chain must back up and restore the affected authorization file on the owned device.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Authenticate and authorize `/api/sysupload`.
- Restrict destination paths to a narrow upload directory after canonicalization.
- Run the web container as a non-root user.
- Remove read/write bind mounts of host-sensitive directories.
- Add regression tests for arbitrary absolute/traversal paths and host-mount escapes.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# t800-web-backend Arbitrary Path Write to Host-Root RCE

> Version: 2026-08-29 · **Live validation on the researcher-owned device**: unauthenticated web write → host authorization-file modification → privileged host login → restoration.
> This finding shares the `/api/sysupload` root cause with the cross-board write finding but has a shorter and higher-impact local host path.

## 1. Executive Summary

The `walker-web.web-backend-1` container runs as root and exposes host files through read/write bind mounts. The source report confirmed mounts corresponding to:

| Host Source | Container Destination | Mode |
|---|---|---|
| `/root/.ssh` | `/root/.ssh` | rw |
| `/etc/walker` | `/etc/walker` | rw |
| `/tmp` | `/tmp` | rw |
| `/home/walker/.ssh` | `/home/ubt/.ssh` | rw |

Because `board_name=vision` writes the caller-selected `path/filename` locally, a request through `/api/sysupload` can write into those host-mounted paths.

The source report dynamically validated a root-access chain on the owned vision board, then restored the original authorization file and permissions.

## 2. Root Cause

- The container is not privilege-dropped.
- Sensitive host directories are bind-mounted read/write.
- The upload endpoint accepts unrestricted path/filename combinations.

A previous interpretation that one host SSH mount was read-only was corrected by live `docker inspect` evidence; the earlier HTTP error was caused by an accidental directory/file collision rather than a read-only mount.

## 3. Validated Chain

```
Unauthenticated /api/sysupload
        ↓
write controlled content into a host-mounted authorization path
        ↓
authenticate to the owned vision board using the added test credential
        ↓
host uid=0 confirmed
        ↓
restore the original file and permissions
```

Reusable key material is not included in this translation.

## 4. Live Validation Workflow

The retained `vision_host_root_rce.py` separates a harmless `--probe` mode from the full authorized validation mode.

The source run performed:

1. benign temporary write/readback;
2. backup of the original authorization file;
3. controlled addition of a temporary research key;
4. root-login verification;
5. restoration and byte-count verification.

Evidence is retained in `evidence/host_root_rce_2026-08-29.txt`.

## 5. Relationship to the Cross-Board Finding

- UBH-010 uses the same endpoint to write through an internal SFTP path to the motion board.
- UBH-009 is shorter: the vision-side container write directly reaches the host through bind mounts.

## 6. Recommendations

1. Run the web backend as non-root.
2. Remove read/write host mounts for SSH/configuration directories.
3. Add authentication and a canonicalized destination allowlist to `/api/sysupload`.
