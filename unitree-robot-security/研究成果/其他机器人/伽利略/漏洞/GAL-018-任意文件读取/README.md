---
ID: GAL-018
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: 任意文件读取-1
---
# GAL-018 Galileo Flask /run_script Arbitrary Readable-File Disclosure

## 1. Summary

The unauthenticated Flask `/run_script` endpoint accepts an arbitrary filesystem path as the script to execute. If the target is an ordinary text file rather than a shell script, the backend invokes `sh <file>`; shell parse failures echo the original line content into stderr, which is returned to the caller. This allows disclosure of files readable by the `galileo` service account. The source report dynamically validated the primitive using `/etc/passwd`.

## 2. Affected Products and Versions

- Target: Galileo research robot running Ubuntu 22.04.
- Component: Flask management backend `/run_script`.
- Read boundary: files readable by the `galileo` account unless combined with a separate privilege-escalation primitive.

## 3. Validation Status

`dynamically confirmed`.

## 4. Attack Preconditions

The attacker must reach the unauthenticated web manager. Verification should use non-sensitive files such as `/etc/hostname` or a disposable text file.

## 5. Root Cause

The endpoint allows arbitrary path selection and executes the selected file through the shell. Shell errors containing source-line text are returned to the unauthenticated caller.

## 6. Attack Procedure

A caller selects a readable non-script text file. The backend invokes it through `sh`; each line that is not a valid shell command produces an error containing that line, allowing reconstruction of the file contents.

## 7. Impact

- Unauthenticated disclosure of service-readable account/configuration/log/source files.
- Environment and deployment-layout disclosure useful for subsequent attacks.
- Composition with the separate sudo/root path can expand access to otherwise privileged files.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Use only harmless readable files during validation.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Authenticate the endpoint.
- Restrict executable scripts to an explicit canonical allowlist.
- Do not execute arbitrary filesystem paths through `sh`.
- Avoid returning raw shell stderr to unauthenticated clients.
- Separate script execution into fixed operations with validated parameters.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo Flask /run_script Arbitrary Readable-File Disclosure

| Item | Value |
|---|---|
| Target | Galileo research robot |
| Component | Flask `/run_script` |
| Type | File-content disclosure through shell error output |
| Read Privilege | Files readable by `galileo` |
| Validation | Dynamic |

## Vulnerability Mechanism

The endpoint receives a `script` path and optional arguments. If the path exists, the backend invokes it through the shell.

When an ordinary text file is supplied, the shell attempts to parse each line as a command. Failed lines are printed to stderr, often including the original line text. Because stderr is returned in the API response, the caller can reconstruct the input file.

The source report dynamically validated this behavior against `/etc/passwd`, observing account lines reflected in the response.

## Security Chain

```
unauthenticated POST /run_script
        ↓
caller selects readable text file
        ↓
backend invokes sh <file>
        ↓
shell errors echo line contents
        ↓
API returns stderr
        ↓
file content disclosed
```

## Permission Boundary

This primitive alone operates with the service user's filesystem permissions. Root-only files require a separate authority increase; the report does not attribute those reads to this primitive alone.

## Safe Reproduction

Use a benign file such as `/etc/hostname` or a test file created for the experiment.

## Evidence

The associated `evidence/` directory contains the original response captures from the owned device.
