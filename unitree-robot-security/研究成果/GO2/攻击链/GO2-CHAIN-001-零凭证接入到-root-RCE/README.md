# GO2-CHAIN-001 Zero-Credential Access to Root RCE

- Status: dynamically closed-loop
- Attack preconditions: authorized devices and isolated networks only; stage-specific preconditions are defined in each vulnerability README.
- Final impact: completing the chain reaches the impact stated in the title.

## Stages

1. [G2-001](../../漏洞/G2-001-零凭证未授权控制/README.md)
2. [G2-002](../../漏洞/G2-002-编程执行器到-root-RCE/README.md)

## Cleanup

After dynamic reproduction, remove temporary files, restore configuration, stop test listeners, and verify again that the relevant services are in their expected state.

This directory only links vulnerabilities into a chain; it does not duplicate vulnerability reports, PoCs, or evidence.
