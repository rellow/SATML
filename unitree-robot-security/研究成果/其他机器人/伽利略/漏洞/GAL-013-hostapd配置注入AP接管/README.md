---
ID: GAL-013
validation_status: dynamically confirmed
severity: medium
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: hostapd配置注入AP接管-2
---
# GAL-013 Galileo /api/ssid hostapd.conf Configuration Injection for AP Takeover or Persistent DoS

## 1. Summary

The unauthenticated `POST /api/ssid` endpoint writes a caller-supplied SSID into `hostapd.conf`. Input is checked only for non-emptiness and a 32-byte UTF-8 limit; newline/control characters are not rejected. A newline in the SSID can therefore inject additional hostapd directives before the service is restarted. Depending on the injected directive and configuration ordering, this can alter AP credentials/encryption or make hostapd fail to start.

## 2. Affected Products and Versions

- Target: Galileo GRQ05W, firmware `galileo-inter 1.0.44`.
- Component: Flask management backend `/api/ssid` → `set_ssid`.
- Configuration target: `/etc/hostapd/hostapd.conf`.

## 3. Validation Status

`dynamically confirmed` according to the source report's status. The configuration-injection mechanism is supported by bytecode-level evidence; exact takeover behavior can depend on hostapd key ordering.

## 4. Attack Preconditions

The attacker must reach the unauthenticated web manager. Live testing can disrupt the robot's AP and should be done only with a physical recovery path.

## 5. Root Cause

The endpoint places untrusted SSID text directly into a line-oriented configuration file without rejecting embedded newlines or control characters, then restarts the affected network service.

## 6. Attack Procedure

A crafted SSID contains a newline followed by an additional hostapd directive. The backend rewrites the `ssid=` line with the multi-line value and restarts hostapd.

## 7. Impact

- Unauthorized AP credential or encryption changes.
- Potential takeover of the robot's management hotspot.
- Persistent AP failure/DoS if an invalid directive prevents hostapd from starting.
- The persistent configuration effect complements the separate one-shot Wi-Fi switching issue.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Avoid live disruptive directives unless an out-of-band recovery path is available.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Reject CR/LF/NUL and other control characters in SSIDs.
- Parse and update hostapd configuration structurally instead of interpolating raw text.
- Back up configuration and automatically roll back if hostapd fails.
- Authenticate the endpoint.
- Add regression tests for multiline/config-injection input.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo /api/ssid hostapd.conf Configuration Injection

| Item | Value |
|---|---|
| Target | Galileo GRQ05W (`galileo-inter 1.0.44`) |
| Component | Flask `/api/ssid` → `modules/init_status.py::set_ssid` |
| Type | Newline-based configuration injection |
| Privilege | Unauthenticated |
| Target File | `/etc/hostapd/hostapd.conf` |

## Vulnerability Mechanism

The handler validates only that the new SSID is non-empty and no longer than 32 UTF-8 bytes. It then performs a multiline regular-expression replacement equivalent to:

```python
new_content = re.sub(
    r"^ssid\s*=.*$",
    "ssid=" + new_ssid,
    content,
    flags=re.MULTILINE,
)
write(conf_file, new_content)
restart_hostapd()
```

Because newlines are accepted, the replacement text can add another hostapd directive. Short directives can alter WPA behavior, passphrase-related state, or channel configuration.

The precise result of duplicate keys depends on the existing configuration order, so the report preserves that dependency rather than claiming every injection produces an identical takeover.

## Security Consequences

```
unauthenticated POST /api/ssid
        ↓
SSID contains embedded newline/directive
        ↓
hostapd.conf receives attacker-controlled extra line
        ↓
hostapd restart
        ↓
AP security/configuration changes or AP fails
```

## Evidence

- `evidence/set_ssid_disassembly.txt`
- PyInstaller/PYC analysis of `modules/init_status.pyc`
- live/source configuration evidence

## Safe Reproduction

Routine verification should confirm multiline acceptance and resulting test configuration only in a recoverable environment. A deliberately invalid channel or credential change can sever the tester's own management connection.
