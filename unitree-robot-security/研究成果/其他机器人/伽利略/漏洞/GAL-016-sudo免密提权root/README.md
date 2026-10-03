---
ID: GAL-016
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: sudo免密提权root-1
---
# GAL-016 Galileo Passwordless sudo Privilege Escalation to Root

## 1. Summary

The ordinary `galileo` account is configured for non-interactive passwordless sudo. Once another vulnerability provides command execution as `galileo`, an attacker can immediately execute commands as root. The source report dynamically confirmed `sudo -n id` returning uid 0 on the researcher-owned robot.

## 2. Affected Products and Versions

- Target: Galileo research robot running Ubuntu 22.04.
- Component: sudoers configuration for the `galileo` user.
- Typical prerequisite: user-level command execution, such as the separately documented Flask management-backend RCE.

## 3. Validation Status

`dynamically confirmed`.

## 4. Attack Preconditions

The attacker must first obtain command execution as `galileo` or another account covered by the same sudo rule. Verification must use benign root commands on owned hardware.

## 5. Root Cause

The `galileo` user is granted broad NOPASSWD sudo authority instead of narrowly scoped, operation-specific privilege.

## 6. Attack Procedure

After gaining a `galileo` shell, a non-interactive sudo command succeeds without a password and runs as uid 0.

## 7. Impact

- Immediate local privilege escalation from `galileo` to root.
- Full filesystem and service authority.
- Ability to modify firmware/configuration or create persistence.
- Amplifies every user-level RCE affecting the `galileo` account.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). A safe proof is `sudo -n id`; avoid persistent modifications.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Remove broad NOPASSWD sudo.
- If sudo is required, allow only narrowly specified commands with constrained arguments.
- Separate the web/service account from interactive administrative accounts.
- Audit sudoers and privileged group membership as part of release testing.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo Passwordless sudo Privilege Escalation to Root

| Item | Value |
|---|---|
| Target | Galileo research robot |
| System | Ubuntu 22.04 |
| Component | sudoers configuration |
| Type | Local privilege escalation |
| Prerequisite | Command execution as `galileo` |
| Validation | Dynamic |

## Vulnerability Overview

The `galileo` user (uid 1000) can invoke sudo non-interactively without supplying a password. On the owned robot, a benign identity query through sudo returned:

```
uid=0(root) gid=0(root)
```

This turns any command-execution primitive in the `galileo` account into a root-compromise chain with no additional credential requirement.

## Composition with Web RCE

```
unauthenticated Flask command execution
        ↓
galileo user context
        ↓
passwordless sudo
        ↓
root
```

The source package used this transition to validate the privilege boundary; the English translation does not reproduce persistence or sensitive-file modification commands.

## Impact

Root authority includes access to system configuration, firmware/application content, privileged services, and persistence mechanisms.

## Safe Reproduction

Use only a non-destructive identity check such as `sudo -n id`.

## Evidence

The associated `evidence/` directory records the privilege-validation response from the owned device.
