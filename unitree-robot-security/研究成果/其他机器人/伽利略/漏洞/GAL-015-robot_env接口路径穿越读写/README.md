---
ID: GAL-015
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: robot_env接口路径穿越读写
---
# GAL-015 Galileo /get_robot_env and /change_port Path-Traversal Read/Write

## 1. Summary

The unauthenticated `/get_robot_env` and `/change_port` endpoints build a target path by joining a configured environment root with a caller-controlled directory and the filename `robot.env`. The directory is not canonicalized or constrained to the intended root. This enables traversal/absolute-path reads of matching targets and permits truncation/rewrite of an escaped `robot.env` file through the port-changing endpoint.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: Flask `routes/robot.py` → `modules/robot_env.py`.
- Both interfaces are part of the unauthenticated management backend.

## 3. Validation Status

`dynamically confirmed` according to the source report, with prior observations of `/change_port` behavior and supplementary source/static validation of the read side and path escape.

## 4. Attack Preconditions

The attacker must reach the management backend. Write testing should use only a disposable test `robot.env` with backup and restoration.

## 5. Root Cause

Caller-controlled directory input is passed to `os.path.join(ENV_ROOT, selected_dir, "robot.env")` without rejecting absolute paths, traversal components, or a canonical path outside `ENV_ROOT`.

## 6. Attack Procedure

The read endpoint opens the resulting path and returns lines as JSON. The write endpoint opens the resulting path in write mode, updates the LCM port line, and writes the rest back, allowing corruption/truncation of an escaped target whose final name is `robot.env`.

## 7. Impact

- Unauthenticated disclosure of matching configuration/source/credential files.
- Unauthorized truncation or modification of escaped `robot.env` files.
- Potential disruption or manipulation of LCM/network configuration and dependent motion/monitor services.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Read-only validation is preferred; write tests must use a disposable target.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Canonicalize the selected directory and require it to remain beneath `ENV_ROOT`.
- Reject absolute paths, traversal components, and symlink escapes.
- Use an explicit directory allowlist.
- Make configuration updates atomic and backed up.
- Authenticate both endpoints.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo /get_robot_env and /change_port Path-Traversal Read/Write

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | Flask robot routes and `modules/robot_env.py` |
| Type | Path traversal → read + constrained truncate/rewrite |
| Privilege | Unauthenticated |

## Vulnerability Mechanism

Both endpoints derive a target using logic equivalent to:

```python
target_env = os.path.join(ENV_ROOT, selected_dir, "robot.env")
```

The caller supplies `selected_dir`, but there is no basename, realpath, or allowed-root validation.

- `GET /get_robot_env` opens the result for reading and returns its lines.
- `POST /change_port` opens the result for writing and rewrites the `LCM_PORT` line while preserving other parsed lines.

Absolute paths can reset the join prefix and traversal segments can escape `ENV_ROOT`.

## Security Consequences

```
unauthenticated selected_dir
        ↓
unconstrained joined path
        ├─ get_robot_env → read target robot.env
        └─ change_port → truncate/rewrite target robot.env
```

The write primitive is constrained by the final `robot.env` filename and the endpoint's update semantics, so the report does not describe it as an unconstrained arbitrary-file write.

## Evidence

- external audit `AUD-web-robot-env-path-traversal.md`
- `routes/robot.pyc`
- `modules/robot_env.pyc`
- `analysis/webmgr_extract/custom_dis.txt`

## Safe Reproduction

Use read-only traversal against a harmless test configuration. If validating the write path, create a disposable `robot.env`, back it up, perform the update, and remove/restore it immediately.
