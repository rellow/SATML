---
ID: GAL-001
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: Flask上传文件名路径穿越任意文件写-1
---
# GAL-001 Galileo /upload Filename Path Traversal to Arbitrary *.tar.gz File Write

## 1. Summary

The unauthenticated Flask `POST /upload` handler preserves the multipart filename and joins it directly beneath the upload directory without sanitizing absolute paths or traversal. Because the extension check is a substring match for `tar.gz`, an attacker can write arbitrary content to any writable path whose name contains that substring. The file is saved before archive extraction, so the write succeeds even if tar extraction later fails.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: Flask management backend `POST /upload`.
- Validation: dynamically reproduced in an authorized isolated environment.

## 3. Validation Status

`dynamically confirmed`.

## 4. Attack Preconditions

The attacker must reach the unauthenticated Flask management service. Reproduction must use researcher-owned devices and harmless destination files.

## 5. Root Cause

Two path-validation defects compose:

1. `allowed_file()` checks whether the string `tar.gz` occurs anywhere in the filename instead of enforcing a safe suffix.
2. `os.path.join` is used with the unsanitized filename, so absolute paths or traversal can escape the upload directory.

The implementation writes the file before invoking tar, so archive validity does not prevent the file-write primitive.

## 6. Attack Procedure

A multipart upload supplies a filename containing `tar.gz` plus an absolute or traversed destination. The retained proof uses harmless content and authorized paths.

## 7. Impact

The primitive can overwrite or create attacker-controlled `*.tar.gz`-named files in writable locations, including firmware/distribution packages, or consume disk space. The filename constraint prevents direct writes to arbitrary names such as `authorized_keys`, so the source report rates the practical impact **High**, not automatically Critical.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Use only harmless target paths.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Sanitize filenames with a strict basename operation.
- Reject absolute paths and traversal components.
- Replace substring matching with exact `.tar.gz` suffix validation.
- Validate archive type before saving/processing it.
- Require authentication on the management interface.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo /upload Filename Path Traversal to Arbitrary *.tar.gz File Write

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | Flask management backend `POST /upload` → `upload_and_extract_file` |
| Type | Path traversal → arbitrary constrained file write |
| Privilege | Unauthenticated caller writes with service-user permissions |
| Severity | High |
| Validation Date | 2026-08-29 |

## Vulnerability Mechanism

Reconstructed source logic:

```python
if not allowed_file(file.filename):
    return error
file_path = os.path.join(upload_folder, file.filename)
file.save(file_path)
subprocess.run(["tar", "-xzf", file_path, "-C", upload_folder], check=True)
```

The source report identifies two issues:

- `allowed_file()` performs substring matching against `tar.gz`.
- The unsanitized filename can be absolute or traversed, allowing the final save path to escape the upload directory.

Because `file.save()` happens before tar extraction, malformed archives still produce the file write.

## Difference from the install.sh RCE

| | install.sh RCE | This Finding |
|---|---|---|
| Requirement | Valid archive containing `install.sh` | Filename contains `tar.gz` and arbitrary content |
| Effect | Execute uploaded install script | Write constrained arbitrary file |
| If extraction fails | No script execution | File has already been written |

## Security Consequences

- Replace firmware/distribution tar packages.
- Place attacker-controlled tar artifacts in writable directories.
- Fill disk space with large files.
- Compose with a consumer that later processes a writable tar artifact.

## Constraint

The destination name must contain `tar.gz`, so the primitive cannot directly overwrite arbitrary filenames that lack that substring. This is why the report keeps the finding at High absent an additional privileged consumer.

## Recommendations

1. Sanitize and basename filenames.
2. Enforce exact extension matching.
3. Reject absolute/traversed paths.
4. Verify archive format before committing it to disk.

## Evidence

- `evidence/AUD-web-upload-filename-path-traversal.md`
- `analysis/webmgr_extract/custom_dis.txt`
