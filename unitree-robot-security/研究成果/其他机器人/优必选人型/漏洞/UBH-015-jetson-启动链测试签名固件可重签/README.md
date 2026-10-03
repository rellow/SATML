---
ID: UBH-015
validation_status: statically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: jetson-启动链测试签名固件可重签
---
# UBH-015 VB2 · Jetson Boot Chain Uses Test-Signed Firmware Without a Fused Production Root

## 1. Summary

The analyzed Jetson T234 boot-chain artifacts use an EDK II test certificate chain, while the inspected boot configuration did not show a fused production PKC/SBK root constraining the accepted signer. The report therefore identifies a persistent boot-chain integrity risk if an attacker first obtains the authority needed to replace boot firmware.

## 2. Affected Products and Versions

- Component: vision-board Jetson T234 boot chain (TegraBoot capsule plus BCT).
- Firmware copies were inspected under `/opt/ota_package/t23x/`.
- No device flashing or capsule replacement was performed.

## 3. Validation Status

`statically confirmed`. This finding concerns the observed trust configuration; boot acceptance of an attacker-repacked image was not dynamically tested.

## 4. Attack Preconditions

An attacker must already have sufficient local write/update authority to replace boot-chain artifacts. Offline verification should use copies only; live reflashing is outside routine testing.

## 5. Root Cause

Production boot integrity appears to rely on an expired/public test-signing chain without an independently fused production root that binds the accepted signer.

## 6. Attack Procedure

The retained script extracts the capsule's PKCS#7 material, inspects the certificate chain with OpenSSL, and checks BCT PKC/SBK configuration. It does not re-sign or flash firmware.

## 7. Impact

If the platform accepts replacement boot firmware signed under a non-production trust configuration, an attacker with prior write authority could establish persistence below the Linux OS, surviving ordinary software reinstallation.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Verification is read-only/offline.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Fuse a production PKC/SBK root unique to the intended trust domain.
- Remove public/test signing chains from production boot acceptance.
- Require authenticated update authorization before boot artifacts can be replaced.
- Add secure-boot regression checks and key-rotation/revocation procedures.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# VB2 · Jetson Boot Chain Uses Test-Signed Firmware Without a Fused Production Root

| Item | Value |
|---|---|
| Component | Vision-board Jetson T234 boot chain (TegraBoot capsule + BCT) |
| Signature | EDK II **test** PKI: TestCert / TestSub / TestRoot, validity 2017-04-10 to 2018-04-10 |
| BCT | No populated production PKC/SBK root observed in the analyzed copy |
| Impact | **Critical in the source report** — weak boot-root binding could allow persistent replacement of boot firmware after a prior compromise |
| Source | `report_voice_boot(1).md` (VB2) |
| Re-verification | 🔒 Static analysis of firmware copies stored under `/opt/ota_package/t23x/` |

## Vulnerability Mechanism

The analyzed TegraBoot capsule is signed with an EDK II test certificate chain. The report found that:

- the certificate chain is an expired test chain rather than a production device/vendor chain;
- the test-signing material is not intended to function as a production secret;
- the inspected BCT did not show a production PKC hash/SBK binding that would independently restrict the accepted signer.

This creates a potential persistence risk if another vulnerability first grants authority to replace boot firmware. Such persistence would execute before Linux and could survive ordinary OS reflashing.

## Reproduction Script

`scripts/exploit_boot_sig.py`

Safe default behavior:

1. Locate a `TEGRA_BL*.Cap` copy.
2. Extract the embedded PKCS#7 signature material.
3. Use local OpenSSL inspection to display the TestCert/TestSub/TestRoot chain and its expired validity period.
4. Inspect BCT PKC/SBK fields.

The script does not modify, re-sign, or flash anything.

## Evidence Output

- Capsule location and signature block metadata.
- Extracted `evidence/tegrabl_pkcs7.der`.
- Certificate-chain and validity information.
- BCT root-key configuration evidence.
- Supporting logs under `evidence/`.

## Safety Boundary

⚠️ The retained workflow is read-only. Any signer-replacement experiment should be performed only on an offline laboratory image or dedicated recoverable hardware, not on the research robot.
