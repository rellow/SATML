---
ID: GAL-011
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: WiFi连接接口命令注入与网络劫持-1
---
# GAL-011 Galileo Wi-Fi Connection API Command Injection and Unauthorized Network Hijacking

## 1. Summary

The unauthenticated Flask endpoint `/network/connect_wifi` inserts caller-supplied SSID/password values into a shell command and executes the resulting Wi-Fi-selection script through sudo. This creates two independent risks: command injection into a privileged shell path, and unauthenticated network reconfiguration. Historical device logs contain direct evidence of a successful injected command and its marker file; a later bounded test also confirmed that an ordinary unauthenticated request can switch the robot away from its own AP and disconnect clients.

## 2. Affected Products and Versions

- Target: Galileo robot, tested on the GRQ05W research unit.
- Component: Flask web manager on port 5000, endpoint `/network/connect_wifi`.
- System: Ubuntu 22.04 in the analyzed image.

## 3. Validation Status

`dynamically confirmed`. The source evidence includes both historical command-injection artifacts and a live network-switch side effect on the owned device.

## 4. Attack Preconditions

The attacker must reach the unauthenticated web manager. Dynamic testing can interrupt network connectivity, so a recovery plan and physical access are required.

## 5. Root Cause

Caller-controlled SSID/password data is interpolated into a shell command rather than passed as data through a non-shell API. The endpoint also lacks authentication, and the resulting script is invoked through a privileged sudo path.

## 6. Attack Procedure

An unauthenticated request supplies crafted network fields. Shell metacharacters can escape the intended data context; even benign values invoke the real network-switching script. The English report intentionally omits ready-to-run shell payloads.

## 7. Impact

- Privileged command execution through command injection.
- Unauthenticated Wi-Fi reconfiguration.
- Remote denial of service when the robot leaves its AP.
- Potential redirection onto an attacker-controlled network, creating a man-in-the-middle position.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Prefer static/log validation; any live request may disconnect the device.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Authenticate the endpoint.
- Never build shell command strings from SSID/password fields.
- Pass network parameters through a safe API or parameterized script interface.
- Restrict sudo to narrowly scoped fixed commands.
- Validate/limit network transitions and require explicit authorized confirmation.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo Wi-Fi Connection API Command Injection and Unauthorized Network Hijacking

| Item | Value |
|---|---|
| Target | Galileo research robot |
| Component | Flask `/network/connect_wifi` on port 5000 |
| Type | OS command injection + unauthenticated network reconfiguration |
| Privilege | Command path executes through sudo |
| Validation | Historical log/file evidence + live network-switch observation |

## Vulnerability Mechanism

Reverse engineering of the packaged network-management module shows that the handler constructs a command equivalent to:

```python
script_path = "/home/galileo/galileo-web-manger/opt/bin/channel_choose.sh"
command = f'printf "{ssid}\n{password}\n" | sudo bash {script_path}'
run_command(command)
```

The SSID and password originate in the request and are not safely escaped or passed as separate arguments. Shell syntax in those fields can therefore alter command structure.

Independently, a normal unauthenticated request causes the robot to execute the actual Wi-Fi switch script. During testing, this caused the robot AP to disappear as the device attempted to join the supplied SSID.

## Historical Dynamic Evidence

The packaged `operation.log` preserves a prior authorized test in which a crafted SSID caused creation of a benign marker file. That marker also exists in the extracted filesystem with a matching timestamp, creating a static-after-the-fact evidence chain for successful command injection.

## Security Consequences

```
unauthenticated web request
        ↓
caller data interpolated into shell command
        ↓
sudo-executed network script / injected command
        ↓
privileged command execution

parallel path:
unauthenticated ordinary SSID request
        ↓
real network reconfiguration
        ↓
robot leaves its AP / joins supplied network
```

## Safety Boundary

Live testing can make the robot unreachable over Wi-Fi. Retained reproduction material therefore emphasizes evidence collection and safe recovery rather than interactive shell payloads.

## Evidence

- packaged `operation.log`
- matching historical benign marker artifact
- reverse-engineered `modules_network.pyc`
- bounded live network-switch observation
