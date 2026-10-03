---
ID: UBH-026
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: 硬编码凭证全线泄露
---
# UBH-026 System-Wide Hard-Coded Credential Exposure

## 1. Summary

The Walker S2 software stack contains reusable credentials across frontend code, board-to-board logic, firmware configuration, container management, SSH, and cloud/registry access. The source report treats this as a systemic credential-management failure that amplifies otherwise separate vulnerabilities. Full private keys and complete access tokens are intentionally excluded from the repository.

## 2. Affected Products and Versions

- Evidence date: 2026-08-29.
- Sources: frontend JavaScript, firmware configuration, local service configuration, and report-level live validation.
- Credential classes include console credentials, OTA/client tokens, Wi-Fi API keys, internal SSH credentials, registry access tokens, SSH private keys, and UDoke secrets/JWTs.

## 3. Validation Status

`statically confirmed` with report-level validation of several credential classes and their downstream authority.

## 4. Attack Preconditions

The attacker must obtain firmware, frontend assets, local configuration, or another read primitive exposing the embedded material. External/cloud reuse must be evaluated only in authorized environments.

## 5. Root Cause

Long-lived reusable secrets are distributed in client-side code, firmware, local configuration, or containers rather than being provisioned per device/principal and scoped to the minimum authority.

## 6. Attack Procedure

This report is an inventory/impact analysis rather than a single exploit chain. The public translation retains only credential types, fingerprints, and provenance—not full reusable values.

## 7. Impact

A single firmware or filesystem disclosure can yield credentials for multiple trust domains, including device administration, board-to-board transfer, container management, image registries, and cloud APIs. This substantially increases the blast radius of arbitrary-read vulnerabilities.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Do not publish or reuse live credential values.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Remove long-lived secrets from frontend/firmware images.
- Provision unique per-device/per-principal credentials.
- Rotate all exposed credentials and revoke shared legacy values.
- Move secrets to a managed vault/HSM or equivalent protected service.
- Scope registry/cloud tokens to least privilege and short lifetimes.
- Stop sharing SSH private keys across boards or mounting them broadly into containers.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.
- External material must contain only redacted identifiers/fingerprints, never full private keys or PATs.

## 13. Sanitized Original Research Body

# System-Wide Hard-Coded Credential Exposure

> Version: 2026-08-29 · Method: frontend JavaScript audit + firmware/configuration extraction + report-level live validation.
> **Sensitivity note:** this repository retains credential categories, shortened fingerprints, and source locations only. Full private keys and complete personal-access tokens remain in private research storage.

## 1. Executive Summary

The Walker S2 stack contains reusable credentials across multiple layers:

- management-console credentials;
- OTA/client tokens;
- Wi-Fi API keys;
- an internal board-to-board SSH credential;
- registry access tokens on both boards;
- a shared SSH private key used across boards and mounted into containers;
- UDoke slave secrets and long-lived JWT material;
- production/research cloud and registry endpoints.

The source report rates the issue **High** because these credentials magnify the impact of arbitrary-read and firmware-disclosure primitives.

## 2. Credential Inventory (Sanitized)

| Category | Material Type | Source | Potential Authority |
|---|---|---|---|
| Management console | username/password values | frontend SPA JavaScript | administrative UI |
| OTA | client token | frontend JavaScript | update API |
| Wi-Fi | API keys | frontend JavaScript | network configuration |
| Board-to-board SSH | embedded user/password | sysupload backend | cross-board SFTP |
| Root SSH | shared RSA private key fingerprint | host SSH material | board login / privileged path |
| Registry | shortened GitLab PAT fingerprints | board Docker configs | image-registry access |
| UDoke | slave secret, long-lived JWT/hash material | local UDoke database | container-management plane |
| Cloud/research infrastructure | endpoint and client configuration | firmware configs | cloud/API/registry reachability |

## 3. Impact Analysis

- A shared SSH key across boards turns one key disclosure into a multi-board identity failure.
- Registry access tokens can expose historical firmware versions and therefore enable version-diff analysis.
- Container-mounted SSH material increases the number of processes capable of leaking host credentials.
- Long-lived container-management tokens/secrets can turn local configuration disclosure into persistent management authority.

## 4. Recommendations

1. Remove plaintext credentials/tokens from frontend assets.
2. Replace shared secrets with per-device/per-principal material managed by a central secret service.
3. Stop sharing root/administrative SSH keys between boards and containers.
4. Use short-lived, least-privilege registry/cloud tokens.
5. Rotate/revoke all values exposed in shipped images.

## 5. Evidence and Redaction

The full source evidence remains in the private research archive. Public/submission material should expose only fingerprints, credential categories, and provenance locations, never complete private keys or live access tokens.
