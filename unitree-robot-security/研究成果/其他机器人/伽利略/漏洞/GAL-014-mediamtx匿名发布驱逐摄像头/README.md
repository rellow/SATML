---
ID: GAL-014
validation_status: dynamically confirmed
severity: medium
disclosure_status: internal research
source_platform: Galileo
source_candidate_directory: mediamtx匿名发布驱逐摄像头-1
---
# GAL-014 Galileo MediaMTX Anonymous Read/Publish and Publisher Override

## 1. Summary

The robot's MediaMTX configuration grants anonymous users both read and publish permission on arbitrary paths and enables `overridePublisher: yes`. This permits unauthenticated viewing of camera streams and allows another publisher to replace the legitimate camera publisher for a path. The configuration and live media service exposure were confirmed; video-injection testing must remain bounded to an owned device.

## 2. Affected Products and Versions

- Target: Galileo research robot.
- Component: MediaMTX streaming service.
- Interfaces include RTSP 8554, RTMP 1935, WebRTC-related ports, and other MediaMTX listeners.
- Camera pipeline publishes locally into MediaMTX.

## 3. Validation Status

`dynamically confirmed` according to the source report, with configuration and service evidence supporting anonymous read/publish behavior.

## 4. Attack Preconditions

The attacker must reach the media-service ports. Publisher-override testing can disrupt the legitimate camera feed and should be performed only on researcher-owned devices.

## 5. Root Cause

The default MediaMTX authorization configuration permits `user: any` to read and publish to unrestricted paths and permits later publishers to override existing publishers.

## 6. Attack Procedure

An unauthenticated client can read a known stream path. A second publisher can attempt to publish to the same path; with publisher override enabled, the legitimate source can be displaced.

## 7. Impact

- Camera privacy exposure through anonymous viewing.
- Camera-feed denial of service by displacing the legitimate publisher.
- Video-content injection toward operators or downstream vision consumers.
- Potential composition with visual-following/detection logic, although physical effects require a separate confirmed consumer chain.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Use a benign test stream and an owned robot if publisher override is tested.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Remove anonymous publish permission.
- Restrict camera publishing to localhost or authenticated principals.
- Set `overridePublisher: no` unless explicitly required.
- Require authentication for stream readers where camera privacy matters.
- Monitor unexpected publisher changes.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# Galileo MediaMTX Anonymous Read/Publish and Publisher Override

| Item | Value |
|---|---|
| Target | Galileo research robot |
| Component | MediaMTX |
| Type | Anonymous publish/read + publisher override |
| Configuration | Firmware `galileo-rtsp/opt/bin/mediamtx.yml` |

## Vulnerability Mechanism

The deployed configuration contains an internal authentication block that effectively grants anonymous users unrestricted publish and read permissions and enables publisher replacement.

Representative structure:

```yaml
authMethod: internal
authInternalUsers:
  - user: any
    ips: []
    permissions:
      - action: publish
      - action: read
      - action: playback
overridePublisher: yes
```

The robot's normal camera pipeline publishes a local camera feed into an RTSP path. Because anonymous clients can publish to that same path and publisher override is enabled, a competing publisher can become the active source.

## Consequences

1. Anonymous clients can view camera streams.
2. An anonymous publisher can displace the legitimate camera source.
3. Consumers of the path can receive attacker-selected imagery until the legitimate publisher recovers.
4. If a downstream physical behavior relies on that imagery, the media defect can become one stage in a larger control chain; that composition requires separate evidence.

## Evidence

- `evidence/mediamtx.yml`
- camera-pipeline configuration/script evidence
- listener inventory for MediaMTX services

## Safe Reproduction

Use read-only stream access for routine validation. Publisher-override testing should use a harmless local test source on a researcher-owned robot and should restore the camera publisher immediately.
