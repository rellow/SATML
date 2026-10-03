# UT-CHAIN-001 BLE Fragment Reassembly to Root Command Execution

- Status: dynamically closed-loop on both models
- Attack preconditions: authorized devices and isolated networks only; stage-specific preconditions are defined in each vulnerability README.
- Final impact: completing the chain reaches the impact stated in the title.

## Stages

1. [UT-001](../../漏洞/UT-001-btgatt-server-分片重组溢出到-root-RCE/README.md)

## Cleanup

After dynamic reproduction, remove temporary files, restore configuration, stop test listeners, and verify again that the relevant services are in their expected state.

This directory only links vulnerabilities into a chain; it does not duplicate vulnerability reports, PoCs, or evidence.
