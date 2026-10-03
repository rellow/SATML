---
ID: GAL-002
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: Flask管理后台未授权RCE-1
---
# GAL-002 Galileo Flask Management Backend Unauthenticated RCE

## 1. Summary

The robot exposes a Flask management backend on port 5000 without authentication. Its `/upload` endpoint accepts a `.tar.gz` integration package, extracts it, and automatically executes an included `install.sh`. On the researcher-owned device, a benign proof confirmed arbitrary command execution as the `galileo` user. The separately documented passwordless-sudo configuration can then elevate that user to root.

## 2. Affected Products and Versions

- Target: Galileo quadruped robot, tested on the device AP environment.
- System: Ubuntu 22.04 / Python 3.10 / Werkzeug 3.1.4.
- Component: `/home/galileo/galileo-web-manger`, port 5000.

## 3. Validation Status

`dynamically confirmed`.

## 4. Attack Preconditions

The attacker must reach the robot's management web service, for example from the same LAN/AP. Testing must remain on owned hardware and use harmless commands.

## 5. Root Cause

The management backend lacks authentication and automatically executes an uploaded package's `install.sh` without establishing a trusted publisher or signature boundary.

## 6. Attack Procedure

The retained validation uses a harmless integration archive whose install script writes benign evidence. The report preserves the chain but does not add additional weaponized payloads.

## 7. Impact

An unauthenticated LAN caller can execute commands as the `galileo` user. Because that account has a separate passwordless-sudo path, the chain can lead to full device root compromise.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Use non-destructive commands only.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Add authentication and authorization to the management backend.
- Require signed integration packages from a trusted key.
- Never auto-execute package-provided shell scripts.
- Validate archive paths/types/sizes.
- Remove passwordless broad sudo from the service user.
- Change default network credentials.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo Flask Management Backend Unauthenticated RCE

| Item | Value |
|---|---|
| Target | Galileo quadruped robot |
| System | Ubuntu 22.04, OpenSSH 8.9p1, Python 3.10.12 |
| Component | Flask management backend on port 5000 |
| Type | Unauthenticated access + arbitrary command execution |
| Execution Identity | `galileo` (uid 1000); separate sudo issue can reach root |
| Validation Date | 2026-08-29 |

## Vulnerability Overview

A direct `GET /` returns the management UI without login or session validation. The `/upload` endpoint accepts an integration `.tar.gz`, extracts it, searches for `install.sh`, and executes that script.

Live testing distinguished two cases:

- archive without `install.sh` → upload succeeds without execution;
- archive with `install.sh` → backend reports successful installation and the benign test action is observed.

This confirms command execution as the service user.

## Attack Surface

Representative unauthenticated endpoints include:

| Endpoint | Function | Risk |
|---|---|---|
| `/upload` | upload/extract integration package | automatic `install.sh` execution |
| `/run_script` | execute existing script | command/file-access surface |
| `/change_port` | alter network/service port | configuration tampering |
| `/network/connect_wifi` | connect to Wi-Fi | network reconfiguration |
| `/network/interface/toggle` | switch interface | DoS/network takeover |

## Execution Identity

The source report confirms `install.sh` executes as `galileo` (uid 1000). The separate GAL-016 finding documents passwordless sudo, which composes this user-level RCE into root.

## Reproduction

The retained proof uses an archive containing a benign install script and verifies a harmless marker/identity output. Full command examples remain in the private authorized research artifact.

## Recommendations

1. Authenticate all management routes.
2. Require signed packages and remove automatic script execution.
3. Apply strict archive validation and extraction containment.
4. Restrict `/run_script` to approved operations.
5. Remove broad passwordless sudo.
6. Replace default AP credentials.

## Evidence

`evidence/explore.txt` and the associated response captures record the service behavior and execution identity.
