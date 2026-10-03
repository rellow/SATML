# R1-CHAIN-001 arm_service File Placement and Rename to Root

- Status: dynamically closed-loop
- Attack preconditions: authorized devices and isolated networks only; stage-specific preconditions are defined in each vulnerability README.
- Final impact: completing the chain reaches the impact stated in the title.

## Stages

1. [R1-003](../../漏洞/R1-003-arm_service-无鉴权-RPC/README.md)
2. [R1-004](../../漏洞/R1-004-arm_service-任意文件投放/README.md)
3. [R1-005](../../漏洞/R1-005-arm_service-rename-路径穿越/README.md)

## Cleanup

After dynamic reproduction, remove temporary files, restore configuration, stop test listeners, and verify again that the relevant services are in their expected state.

This directory only links vulnerabilities into a chain; it does not duplicate vulnerability reports, PoCs, or evidence.
