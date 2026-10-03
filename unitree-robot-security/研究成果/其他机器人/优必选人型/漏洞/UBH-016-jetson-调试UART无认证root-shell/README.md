---
ID: UBH-016
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: jetson-调试UART无认证root-shell
---
# UBH-016 VB1 · Unauthenticated Root Shell over Jetson Debug UART

## 1. Summary

- Impact: **Critical in the source report** — physical access to the debug UART (115200 baud) yields an automatically logged-in `walker` shell, followed by passwordless sudo to root.
- The source report dynamically confirmed the live mechanism.

## 2. Affected Products and Versions

- Component: vision-board Jetson T234 debug serial port `ttyTCU0`.

## 3. Validation Status

`dynamically confirmed`. This status reflects the validation boundary of the source report; the migration process does not infer dynamic confirmation from directory names.

## 4. Attack Preconditions

The attacker requires physical access to the debug UART. Reproduction must use researcher-owned devices and an authorized laboratory environment.

## 5. Root Cause

The debug console is configured for systemd autologin as the `walker` user, and that account has passwordless sudo. Physical access to the exposed UART therefore crosses directly from console access to root authority.

## 6. Attack Procedure

The sanitized research body in Section 13 records the observed console configuration and live process evidence. This repository retains only non-destructive verification material.

## 7. Impact

Physical access to the debug UART yields an unauthenticated `walker` shell. Because `walker` has passwordless sudo, the user can obtain root privileges on the vision board.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Imported scripts were text-sanitized; original logs and larger evidence remain referenced through the repository-level material manifest.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13 below. Source files are represented by hashes and local storage paths rather than copied wholesale into Git.

## 10. Recommendations

- Disable autologin on production debug consoles.
- Require authenticated maintenance access for UART consoles.
- Remove passwordless sudo from ordinary service accounts.
- Disable or physically protect production debug headers where feasible.
- Add regression checks for boot-console and getty configuration.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report. If one is added later, it will be registered in the [AI session index](../../../../../AI轨迹/会话索引.md).

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review device identifiers, evidence, and vendor-coordination status.

## 13. Sanitized Original Research Body

# VB1 · Unauthenticated Root Shell over Jetson Debug UART

| Item | Value |
|---|---|
| Component | Vision-board Jetson T234 debug UART `ttyTCU0` |
| Mechanism | **systemd autologin**: `<个人邮箱_01>.d/autologin.conf` configures `agetty --autologin walker` |
| Impact | **Critical in the source report** — physical connection to the 115200-baud debug UART drops directly into a walker shell; passwordless sudo reaches root |
| Source | `report_voice_boot(1).md` (VB1), with live re-verification in the research session |
| Re-verification | 🟢 **Confirmed**: autologin configuration, live `/bin/login -f`, and an active `-bash` session were all observed on `ttyTCU0` |

## Live Re-Verification Evidence (2026-08-29)

```
/etc/systemd/system/<个人邮箱_01>.d/autologin.conf:
    ExecStart=-/sbin/agetty --autologin walker --keep-baud 115200 %I $TERM

ps aux | grep ttyTCU0:
    root   1906  /bin/login -f
    walker 2609  -bash
```

- `console=ttyTCU0,115200` was confirmed in both the payload command line and DTB `/chosen/bootargs`.
- Equivalent autologin configuration also covers `ttyAMA0`, `ttyAMA6`, `ttyS0`, and `tty1`.
- The `walker` account has passwordless sudo and can enter a root shell.
- **Difference from the earlier report:** the string “Press [ENTER] to start bash” described in the initrd was not found in `kernel_only_payload` or `/boot/initrd`. The actual mechanism is systemd autologin, which produces the same security outcome.

## Conclusion

Physical access to the debug port leads to an unauthenticated shell through automatic login and then to root through passwordless sudo. Although the earlier report's proposed initrd mechanism was not found, **the vulnerability itself was confirmed on the live system**.

See `evidence/uart_shell_evidence.txt`, currently retained in the shared evidence directory `漏洞整理/evidence/`.
