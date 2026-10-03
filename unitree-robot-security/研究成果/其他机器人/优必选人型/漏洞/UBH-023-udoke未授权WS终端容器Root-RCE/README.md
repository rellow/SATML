---
ID: UBH-023
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: udoke未授权WS终端容器Root-RCE-1
---
# UBH-023 Unauthenticated UDoke WebSocket Terminal to Container Root and Host Root

## 1. Summary

The vision board's UDoke container-management service exposes a WebSocket terminal endpoint on port 9001 without authentication. On the researcher-owned device, the source report dynamically confirmed root command execution inside arbitrary containers. Because containers bind-mount the host user's SSH directory read/write, the chain was also validated to host-root authority and then restored.

## 2. Affected Products and Versions

- Device: UBTECH Walker S2 research unit.
- Component: `udoke`, a Rust/actix-web container-management service using the Docker API.
- Service: vision-board port 9001.

## 3. Validation Status

`dynamically confirmed`. The source report records live container-root execution, host SSH-material access, a controlled authorization-file modification, host privilege validation, and restoration.

## 4. Attack Preconditions

The attacker needs network reachability to the UDoke WebSocket service. Full host validation must remain on researcher-owned devices and include backup/restoration of any modified authorization file.

## 5. Root Cause

Two authority failures compose:

1. the terminal WebSocket endpoint performs Docker exec without authenticating the network caller;
2. containers have read/write bind mounts of host SSH material.

Container-root authority therefore becomes a host-identity modification primitive.

## 6. Attack Procedure

The retained script validates the unauthenticated terminal with benign identity commands. The source report documents the full authorized host transition without exposing reusable keys in the English text.

## 7. Impact

An unauthenticated network caller can obtain root command execution inside vision-board containers and, through host bind mounts, escalate to the host user's SSH identity and ultimately host root via configured privilege delegation.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Default verification should run only harmless commands inside a disposable container context.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Require authenticated sessions and explicit authorization for terminal endpoints.
- Restrict UDoke management ports to a dedicated administrative network.
- Do not bind-mount host SSH directories read/write into application containers.
- Limit Docker exec users/capabilities and log every terminal session.
- Remove unnecessary passwordless privilege paths on the host.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Unauthenticated UDoke WebSocket Terminal to Container Root and Host Root

## Target and Scope

- Device: researcher-owned UBTECH Walker S2.
- Component: `udoke`, an internal container-management service built with Rust/actix-web and the Docker API.
- Host: vision board.
- Service: port 9001.
- Validation date: 2026-08-29.

## Vulnerability Overview

The UDoke slave exposes a WebSocket terminal endpoint of the form:

```
/ws/slave/terminal/{container}
```

The source report found no authentication gate before the service opens a Docker exec session. A network client could therefore select a container and establish a root-context shell inside it.

Live validation on the owned robot confirmed:

- successful unauthenticated connection;
- `uid=0(root)` inside the selected container;
- host SSH material visible through a container bind mount;
- a controlled temporary authorization-key modification;
- host login as the expected user followed by configured sudo to root;
- restoration of the original authorization file.

## Authority Chain

```
Unauthenticated WebSocket terminal
        ↓
Docker exec as container root
        ↓
container has rw bind mount of host user's .ssh directory
        ↓
controlled host authorization-file modification
        ↓
host user authentication
        ↓
configured sudo path to host root
```

Reusable private-key material is intentionally omitted from this translation.

## Key Evidence

The retained evidence shows:

1. root identity inside a selected container;
2. identical host/container SSH-directory content through the bind mount;
3. successful controlled modification and cross-container readback;
4. host user membership in privileged groups and configured sudo authority;
5. restoration confirmation.

Complete output is stored in `evidence/verify_terminal_rce3.txt`.

## Reproduction Script

`scripts/udoke_ws_terminal.py`

The safe validation connects to the terminal endpoint and runs benign identity/hostname/kernel queries. The original research package contains the authorized host-chain verification and cleanup workflow.

## Relationship to Other RCE Paths

| Finding | Entry | Primitive | Target |
|---|---|---|---|
| UBH-010 | sysupload HTTP | backend-mediated cross-board file write | motion |
| UBH-009 | sysupload HTTP | local host bind-mount file write | vision |
| UBH-023 | UDoke WebSocket | unauthenticated Docker exec → host bind mount | vision |

The UDoke route is an independent entry point from the sysupload findings.

## Safety Boundary

Validation used only researcher-owned equipment. Motion-control interfaces were not touched, and temporary authorization changes were backed up and restored.
