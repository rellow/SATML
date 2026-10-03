# Externally Stored Material Manifest

This directory records metadata for raw materials that cannot be committed to Git. It does not copy the material itself.

- [未提交材料.csv](未提交材料.csv): GO2/R1 research artifacts and historical firmware items excluded because they exceed 50 MiB or are firmware packages, archives, models, shared libraries, packet captures, or source-result artifacts such as `.pyc`/`.docx`; records size, SHA-256, local storage path, and exclusion reason.
- [已导入材料.csv](已导入材料.csv): sources and hashes for 17 small text scripts that were screened, sanitized, and imported under `工具/`.
- [其他机器人-未提交材料.csv](其他机器人-未提交材料.csv): large, sensitive, cached, dependency, and raw-evidence material for Galileo, UBTECH humanoid, and UBTECH AI Wukong EDU; records size, SHA-256, local storage path, and exclusion reason.
- [其他机器人-已导入材料.csv](其他机器人-已导入材料.csv): sources and hashes for 83 sanitized text scripts imported under `工具/复现工具/其他机器人/` during the other-robot migration.

The historical firmware trees contain 81 broken symbolic links or unreadable paths for which file hashes could not be computed. They are not committed to Git and are not counted as real material. Complete firmware trees, vendor binaries, keys, packet captures, and unsanitized logs remain only at their original local storage locations.
