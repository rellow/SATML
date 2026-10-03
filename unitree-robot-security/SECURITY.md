# Security and Confidentiality Rules

## Authorization Boundary

This repository is only for authorized Unitree GO2/R1 security research. Reproduction tools must not be used against unauthorized devices, accounts, cloud resources, or networks.

## Do Not Commit

- Complete firmware images, UPK/ZIP/TAR archives, complete extracted filesystem trees, APKs, models, or large binaries;
- Valid passwords, tokens, cookies, Authorization headers, private keys, signing keys, cloud credentials, full device serial numbers, or account identifiers;
- Unsanitized logs, packet captures, personal information, Claude configuration, environment snapshots, caches, or login state;
- Unnecessary large excerpts of third-party proprietary source code.

## Commit Workflow

All raw materials must first be sanitized outside the repository. They may be copied into the repository only after a second credential scan passes. If an unsanitized value ever enters Git history, treat it as a release-gate failure: stop pushing and rebuild a clean history.

## Vulnerability Disclosure

The default disclosure state is **internal research**. Before any external disclosure, confirm affected versions, validation evidence, cleanup results, the vendor-coordination plan, and a minimized proof of concept.
