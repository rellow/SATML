---
ID: UBH-006
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: api-export路径穿越任意文件读到双板root-1
---
# UBH-006 t800-web-backend `/api/export` Path Traversal Arbitrary File Read to Dual-Board Root Access

## 1. Summary

The unauthenticated `POST /api/export` endpoint concatenates caller-controlled `map_names` beneath the map directory without canonicalizing and enforcing the final path. On the researcher-owned device, path traversal was dynamically validated with a harmless read of `/etc/hostname`. The source report further documents that reading host SSH material through the same primitive enabled root access to both vision and motion boards.

## 2. Affected Products and Versions

- Evidence date: 2026-08-29.
- Component: `t800-web-backend` v0.2.9, FastAPI on port 5000.
- The container runs as root and exposes host filesystem material through bind mounts.

## 3. Validation Status

`dynamically confirmed`. The migration-period re-check used `/etc/hostname` as a minimum-impact proof rather than rereading sensitive private-key material.

## 4. Attack Preconditions

The attacker must reach the unauthenticated export endpoint. Verification must use researcher-owned systems and should read only harmless files.

## 5. Root Cause

`map_names` values are passed through `os.path.join(MAP_ROOT, name)` without rejecting traversal components or checking that the canonicalized path remains beneath `MAP_ROOT`.

## 6. Attack Procedure

A traversal path supplied as a map name causes the export function to package a file outside the intended map directory. The retained live proof reads only a benign host file.

## 7. Impact

The primitive can expose files reachable through the container's host bind mounts. In the source report, access to SSH private-key material was sufficient to obtain privileged access to both boards. This makes the arbitrary-read primitive a full-compromise enabler rather than a standalone information leak.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Use only benign targets such as `/etc/hostname` for live validation.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Authenticate and authorize `/api/export`.
- Canonicalize every requested path and require the final path to remain beneath `MAP_ROOT`.
- Remove sensitive host bind mounts from the web-backend container.
- Run the container as a non-root user.
- Clean up generated export archives immediately.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# t800-web-backend `/api/export` Path Traversal Arbitrary File Read to Dual-Board Root Access

> Version: 2026-08-29 · Method: live validation on researcher-owned hardware + source audit.
> **Boundary statement:** the re-check read only `/etc/hostname` as a minimum-impact proof. Sensitive private-key material was not reread during repository migration.

## 1. Executive Summary

`POST /api/export` builds export paths by joining the map root with caller-controlled `map_names`. Traversal components are not rejected and the resulting path is not canonicalized and checked against the intended root.

On the current v0.2.9 layout, the map root is `/etc/walker/map/`, so the number of parent-directory components required depends on that base path. A traversal reaching `/etc/hostname` was dynamically confirmed on the owned device.

The original source report documents a higher-impact chain in which the same primitive exposed host SSH private-key material. That material enabled authenticated access to both robot boards and, because the corresponding account had passwordless sudo/docker authority, led to root.

Severity in the source report: **Critical**.

## 2. Root Cause

Reconstructed logic from `t800-web-backend/controller/upload.py`:

```python
@app.post("/api/export")
def export(map_names: list[str]):
    for name in map_names:
        src = os.path.join(MAP_ROOT, name)
        # no canonical realpath + allowed-prefix check
        ...
```

The live error behavior also exposed the unnormalized joined path, corroborating the source-level analysis.

## 3. Security Chain

```
Unauthenticated POST /api/export
        ↓
caller-controlled map_names with traversal
        ↓
read file outside MAP_ROOT through container-visible filesystem
        ↓
sensitive host material may become accessible
        ↓
compose with ordinary service credentials/privileges
```

The exact sensitive-key values are not included in the translated artifact.

## 4. Affected Scope

- `t800-web-backend` v0.2.9.
- Entry: unauthenticated `POST /api/export`.
- Container-visible host bind mounts expand the effective read scope beyond ordinary application data.

## 5. Live Reproduction (2026-08-29)

The retained proof requested a traversal targeting `/etc/hostname`. The response was a gzip/tar archive containing the expected benign hostname file, confirming the arbitrary-read primitive on the owned device.

The source report also notes that each successful export leaves a temporary archive under `/tmp/exports/`, which is tracked separately as a storage-exhaustion issue.

## 6. Recommendations

1. Canonicalize every requested path and verify it remains under `MAP_ROOT`.
2. Require authentication/authorization for the export API.
3. Remove host SSH/configuration bind mounts from the web container.
4. Delete temporary export artifacts or stream responses.

## 7. Evidence

- `evidence/export_hostname_proof.md`: minimum-impact live proof.
- Original `WALKER_S2_PWN.md`: source-level evidence and the previously validated privilege chain.
