# GO2-CHAIN-002 BLE Provisioning to Network Hijacking

- Status: pending dynamic closure
- Attack preconditions: authorized devices and isolated networks only; stage-specific preconditions are defined in each vulnerability README.
- Final impact: completing the chain reaches the impact stated in the title.

## Stages

1. [G2-003](../../漏洞/G2-003-BLE-配网注入与网络劫持/README.md)
2. [G2-011](../../漏洞/G2-011-BLE-F2-密钥投递/README.md)
3. [G2-015](../../漏洞/G2-015-BLE-握手零熵与授权态残留/README.md)

## Cleanup

After dynamic reproduction, remove temporary files, restore configuration, stop test listeners, and verify again that the relevant services are in their expected state.

This directory only links vulnerabilities into a chain; it does not duplicate vulnerability reports, PoCs, or evidence.
