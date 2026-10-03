---
ID: UBH-021
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: mqtt-云端fileDownloadLink命令执行
---
# UBH-021 V4 · MQTT Cloud `fileDownloadLink` Reaches a Shell-Based Download/Extraction Path

## 1. Summary

- Impact: **Critical in the source report** — an MQTT message containing `fileDownloadLink` reaches a shell-based download path and automatic extraction.
- The report statically confirms the processing chain and treats live external-broker interaction as out of bounds for routine verification.

## 2. Affected Products and Versions

- Component: built-in MQTT client on the vision board, connected to a vendor cloud broker.
- The path can direct the robot to retrieve attacker-selected URLs if an unauthorized party gains message-publishing authority to the subscribed topic.

## 3. Validation Status

`statically confirmed`. The source report did not publish a message to the external production broker.

## 4. Attack Preconditions

An attacker would need authority to publish to the relevant MQTT topic, for example through broker compromise, credential exposure, or an improperly authorized integration. Verification must remain inside an authorized test environment.

## 5. Root Cause

Cloud-originated message fields are passed into a shell-based download command and subsequent archive-processing logic without a sufficiently strong authentication boundary or safe argument construction.

## 6. Attack Procedure

The retained probe extracts local broker/configuration evidence, confirms the binary strings associated with the download path, and constructs a representative message without transmitting it to the external broker.

## 7. Impact

If an unauthorized sender can publish to the subscribed topic, the robot can be directed to retrieve arbitrary URLs, including internal resources, and to process downloaded archives. The source report treats this as a potential code-execution path depending on the downloaded content and extraction behavior.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). The retained test does not connect to the external broker.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Require per-device or per-principal MQTT authentication and narrowly scoped topic ACLs.
- Remove hard-coded broker credentials and rotate exposed values.
- Do not construct shell commands from message-supplied URLs; use a library API with explicit arguments.
- Verify TLS certificates and restrict redirects/allowed download origins.
- Treat downloaded archives as untrusted input and validate paths and signatures before extraction.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.
- Before external disclosure, re-review broker identifiers, credentials, evidence, and vendor-coordination status.

## 13. Sanitized Original Research Body

# V4 · MQTT Cloud `fileDownloadLink` Reaches a Shell-Based Download/Extraction Path

| Item | Value |
|---|---|
| Component | Built-in MQTT client on the vision board |
| Cloud Broker | `upilotdev.uqirobot.com:21883`; credential values are sanitized in the public artifact |
| Impact | **Critical in the source report** — a message containing `fileDownloadLink` triggers the shell-based download path followed by automatic extraction |
| Source | `report_vision_core(1).md` (V4) |
| Re-verification | 🔒 Static confirmation only; external broker interaction remained read-only/out of scope |

## Vulnerability Mechanism

The robot's MQTT client subscribes to a cloud topic. When a message contains `fileDownloadLink`, the analyzed implementation invokes a shell-based `curl` path with redirect following and disabled TLS certificate verification, then automatically processes the downloaded archive.

The source report identifies two security consequences if an unauthorized sender can publish to the topic:

1. The robot can be instructed to fetch an arbitrary URL, including potentially internal network resources.
2. Downloaded archive content is automatically processed, increasing the impact of an untrusted download.

The broker credentials are stored locally in device configuration and can be extracted from firmware/device material. Their actual values remain sanitized in the repository.

## Reproduction Script

`scripts/exploit_mqtt.py`

Safe default behavior:

1. Read the local `mqtt_client.json` configuration.
2. Confirm `fileDownloadLink`, download-command, and topic-related evidence in the local binary.
3. Construct and display a representative MQTT message without publishing it.

The optional danger mode only explains the external publishing path; it does not connect to the production broker.

## Evidence Output

- Sanitized broker/configuration provenance.
- Binary-level download-handler evidence.
- Representative message structure.
- Supporting material retained under `evidence/`.

## Safety Boundary

⚠️ Connecting to and publishing on the external broker could cause a real robot to download/process remote content. The retained verification therefore does not perform that action.

A fully authorized controlled-broker test would publish a benign message pointing to a harmless test artifact and observe whether the robot reaches the expected download path; that external action was not part of the retained evidence.
