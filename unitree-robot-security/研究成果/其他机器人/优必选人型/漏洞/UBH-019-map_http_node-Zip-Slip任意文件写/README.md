---
ID: UBH-019
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: map_http_node-Zip-Slip任意文件写
---
# UBH-019 S3 · Zip Slip in map_http_node Map Upload Enables Arbitrary Host File Write

## 1. Summary

- Impact: **Critical in the source report** — archive entries containing absolute paths or `../` traversal can escape the intended extraction directory and write files on the host filesystem.
- The service is a host process rather than a containerized component.

## 2. Affected Products and Versions

- Component: vision-board host process `map_http_node`, listening on `0.0.0.0:30023`.
- Live route probing confirmed the service and upload surface.

## 3. Validation Status

`statically confirmed` with live service reachability evidence and a safe proof mode limited to a temporary marker file.

## 4. Attack Preconditions

The attacker must be able to reach the map-upload interface. Reproduction must use a researcher-owned system and should constrain proof writes to a temporary directory.

## 5. Root Cause

`ArchiveUtility::Decompress` does not sufficiently canonicalize or constrain archive member paths before extraction, so path-traversal or absolute-path entries can escape the intended destination.

## 6. Attack Procedure

The safe reproduction path fingerprints the service, constructs a traversal archive, and optionally proves the primitive by writing a harmless marker under `/tmp` and deleting it afterward.

## 7. Impact

Because `map_http_node` runs directly on the host, a successful traversal write affects the host filesystem rather than a container overlay. Depending on process privileges and writable targets, this can become a persistence or privilege-escalation primitive.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The `--prove` mode is restricted to a temporary marker file and cleans it up after validation.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Canonicalize every archive entry and reject absolute paths, traversal, symlinks, and paths escaping the extraction root.
- Extract into a dedicated low-privilege directory.
- Authenticate the upload endpoint and restrict accepted archive formats.
- Add regression tests for Zip Slip variants and nested path tricks.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review evidence and vendor-coordination status.

## 13. Sanitized Original Research Body

# S3 · Zip Slip in map_http_node Map Upload Enables Arbitrary Host File Write

| Item | Value |
|---|---|
| Component | Vision-board **host process** `map_http_node` (not containerized), listening on `0.0.0.0:30023` |
| Function | `ArchiveUtility::Decompress` @ 0x5f310 |
| Impact | **Critical in the source report** — archive members with absolute paths or `../` entries can write outside the extraction directory |
| Source | `report_system(1).md` (S3) |
| Re-verification | 🟢 `/health`, `/version`, and `/map/list` responded; OPTIONS on `/map/upload` returned 204 |

## Vulnerability Mechanism

After a map archive is uploaded, `map_http_node` passes it to `ArchiveUtility::Decompress`. The source analysis found that member paths are not normalized and constrained to the intended extraction root before files are created.

- The process runs on the host, so escaped writes reach the host filesystem.
- Depending on privileges, a generic arbitrary-write primitive can become a persistence or code-execution building block.
- Live service probing confirmed the map API surface.

## Reproduction Script

`scripts/exploit_zip_slip.py`

- Default safe mode:
  1. Fingerprint the service through benign routes.
  2. Construct a traversal archive locally without uploading it.
- `--prove`: upload an archive whose escaped path is limited to a harmless marker under `/tmp`; verify the marker, then delete it.

## Evidence Output

- Service fingerprints.
- Constructed archive size and member path.
- In prove mode, upload response and host-side readback of the temporary marker.
- Supporting material retained under `evidence/`.

## Safety Boundary

⚠️ The prove mode writes only a temporary marker under `/tmp` and cleans it up. The retained script does not automatically target persistent or security-sensitive locations.

The source report describes the primitive as sufficient for arbitrary host-path writes, but the committed proof intentionally demonstrates only the harmless temporary-file case.
