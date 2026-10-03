# Other-Robot Research Results

This directory organizes non-Unitree research by robot or product line. Each subdirectory retains only the canonical vulnerability reports, minimal reproduction material, and evidence indexes for that robot or platform.

## Robots / Platforms

| Robot / Platform | Entry Point | Current Status |
|---|---|---|
| Galileo | [Research index](伽利略/README.md) | Migrated; pending further manual review |
| UBTECH humanoid | [Research index](优必选人型/README.md) | Migrated; pending further manual review |
| UBTECH AI Wukong EDU | [Research index](优必选AI悟空EDU/README.md) | Migrated; pending further manual review |

## ID Conventions

- Galileo: `GAL-001`, `GAL-CHAIN-001`
- UBTECH humanoid: `UBH-001`, `UBH-CHAIN-001`
- UBTECH AI Wukong EDU: `UBW-001`, `UBW-CHAIN-001`

IDs were assigned after duplicate reports were merged, validation status was initially adjudicated, and sanitization was reviewed. Later review must not reuse or reorder existing IDs. See the [other-robot migration manifest](../其他机器人迁移清单.md) for the complete migration record. Materials that are not committed are registered under the repository-root `材料清单/` directory.

## Scope Boundary

The existing [GO2](../GO2/README.md), [R1](../R1/README.md), and [cross-model](../跨型号/README.md) directories remain separate. Issues shared across different robot families are tracked under [cross-robot](../跨机器人/README.md).
