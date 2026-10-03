---
ID: GAL-010
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: Werkzeug调试台PIN泄露RCE-2
---
# GAL-010 Galileo Werkzeug Debugger PIN Disclosure to Unauthenticated RCE

## 1. Summary

The Galileo web manager runs the Flask development server with `debug=True` on `0.0.0.0:5000`, exposing the Werkzeug interactive debugger. The debugger PIN is written in cleartext to startup logs, and the same web manager provides an unauthenticated log/file-read path capable of retrieving the current boot's log. This composes into disclosure of the current debugger PIN and access to the interactive Python console. The source record confirms the PIN-disclosure chain; interactive command execution was prepared for authorized testing and is treated within the source validation boundary.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: `galileo_web_manger`, Flask/Werkzeug 3.1.4 on port 5000.
- Service runs as the `galileo` user; the separate passwordless-sudo finding can further elevate this context.

## 3. Validation Status

`dynamically confirmed` according to the source report's validation status. The retained evidence directly establishes debug exposure and current-PIN disclosure.

## 4. Attack Preconditions

The attacker must reach the web manager on the same reachable network. Testing must be limited to researcher-owned devices and harmless console actions.

## 5. Root Cause

Production firmware exposes the Werkzeug debugger, logs its authentication PIN in cleartext, and independently exposes those current logs through an unauthenticated read path.

## 6. Attack Procedure

The chain is: enumerate the current web-manager log, read it through the unauthenticated log-download path, extract the current debugger PIN, authenticate to the debugger console, and use the console under the web-service account. The English report does not duplicate shell or reverse-shell payloads.

## 7. Impact

- Unauthenticated interactive Python code execution in the web-service account context.
- Additional source, stack, and environment disclosure through debug functionality.
- Composition with broad passwordless sudo can raise the impact to root.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Use a benign expression such as an identity/query operation only.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Disable Flask/Werkzeug debug mode in production and use a production WSGI server.
- Never write debugger PINs or equivalent secrets to remotely readable logs.
- Fix the log/file-read traversal independently.
- Require authentication for management interfaces.
- Remove broad passwordless sudo from the service user.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo Werkzeug Debugger PIN Disclosure to Unauthenticated RCE

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | `galileo_web_manger` with Flask/Werkzeug debug server |
| Type | Debugger exposure + cleartext PIN logging + unauthenticated file read |
| Network | `0.0.0.0:5000` |
| Privilege | Web-service user; separate sudo finding may elevate further |

## Vulnerability Mechanism

The packaged web manager starts Flask in debug mode on all interfaces. Werkzeug's debugger therefore exposes `/console` with PIN protection.

Startup logs contain lines of the form:

```
* Debugger PIN: xxx-xxx-xxx
```

The PIN changes with boot-derived material, so an attacker needs the current value. The separate unauthenticated log-download path provides exactly that: callers can enumerate the current startup log and retrieve it without credentials.

The combined authority flow is:

```
unauthenticated web access
        ↓
enumerate current startup log
        ↓
read current Werkzeug PIN
        ↓
authenticate to exposed debugger
        ↓
interactive Python in web-service context
```

## Evidence

- PyInstaller/PYC analysis confirming `debug=True`, `host='0.0.0.0'`, and port 5000.
- Startup logs containing current/previous debugger PIN values.
- Log enumeration/download behavior from the related arbitrary-file-read finding.

## Safe Reproduction

The retained workflow automates current-log discovery and PIN extraction and can confirm debugger authentication with a non-destructive operation. It does not need to create files or alter robot state.

## Recommendations

1. Disable debug mode in production.
2. Replace the development server with a production server.
3. Prevent debugger credentials from entering logs.
4. Canonicalize and authorize log-download paths.
