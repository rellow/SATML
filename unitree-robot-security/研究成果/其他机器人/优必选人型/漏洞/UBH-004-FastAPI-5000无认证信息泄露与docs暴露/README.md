---
编号: UBH-004
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 优必选人型
源候选目录: FastAPI-5000无认证信息泄露与docs暴露-1
---
# UBH-004 t800-web-backend FastAPI :5000 无认证信息泄露 + Swagger 暴露 + 磁盘填满 DoS

## 1. 一句话结论

- ## 1. 执行摘要
- 未认证可反复调用耗尽磁盘（DoS）。该服务同时承载 export/sysupload/rename-folder 等读写原语，
- \| `GET /api/sn` \| `{"code":200,...,"sn":"<其他机器人设备_01>"}`（未认证泄露 SN） \|
- \| `POST /api/export` \| 路径穿越任意文件读（见 export 目录） \|
- - 未认证反复调用 → 磁盘耗尽 → 服务/系统不可用；

## 2. 影响产品与版本

- > 版本：2026-08-29 · 方法：实机验证（当日）+ 源码审计
- 未认证可反复调用耗尽磁盘（DoS）。该服务同时承载 export/sysupload/rename-folder 等读写原语，
- - 未认证反复调用 → 磁盘耗尽 → 服务/系统不可用；
- - 组件：`t800-web-backend` v0.2.9（:5000 FastAPI，Alpine 容器 root）

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- # t800-web-backend FastAPI :5000 无认证信息泄露 + Swagger 暴露 + 磁盘填满 DoS
- **FastAPI :5000 整个 API 面无认证，暴露 `/docs`（Swagger UI）、`/openapi.json`（完整路由）与
- 未认证可反复调用耗尽磁盘（DoS）。该服务同时承载 export/sysupload/rename-folder 等读写原语，
- \| `GET /api/sn` \| `{"code":200,...,"sn":"<其他机器人设备_01>"}`（未认证泄露 SN） \|
- \| `POST /api/export` \| 路径穿越任意文件读（见 export 目录） \|
- - 未认证反复调用 → 磁盘耗尽 → 服务/系统不可用；

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- # t800-web-backend FastAPI :5000 无认证信息泄露 + Swagger 暴露 + 磁盘填满 DoS
- 多个信息泄露端点（`/api/sn` 等）。此外 `/api/export` 每次成功导出在 `/tmp/exports/` 永久留档，
- 严重度定级：**中危（Medium）**——信息泄露 + 磁盘 DoS；其承载的读写原语已单独定级 Critical。
- \| `GET /api/sn` \| `{"code":200,...,"sn":"<其他机器人设备_01>"}`（未认证泄露 SN） \|
- ## 4. 受影响范围
- - 组件：`t800-web-backend` v0.2.9（:5000 FastAPI，Alpine 容器 root）

## 8. 复现方法

复现材料见 [复现材料清单](复现/材料清单.md)。导入脚本已做文本脱敏；未导入的原始脚本、日志、抓包和二进制见根目录材料清单。

## 9. 支撑证据

见 [证据材料清单](证据/材料清单.md) 和本页第 13 节。来源文件只登记哈希和本地保管路径，不把原始敏感材料带入 Git。

## 10. 修复建议

- 对入口实施身份认证、细粒度授权、消息完整性校验和重放防护；
- 对路径、长度、协议字段、文件类型和状态转换使用允许列表；
- 删除硬编码凭据并轮换已暴露材料；
- 对高风险服务降权，增加审计日志和负向回归测试。

## 11. 相关 AI 会话

当前未发现与该报告一一对应的完整 Claude Code 会话记录；如后续补齐，将在 [AI 会话索引](../../../../../AI轨迹/会话索引.md) 中登记。

## 12. 披露记录

- 当前披露状态：内部研究。
- 对外披露前必须重新审查凭据、设备标识、证据和厂商协调状态。

## 13. 脱敏后的原始研究正文

# t800-web-backend FastAPI :5000 无认证信息泄露 + Swagger 暴露 + 磁盘填满 DoS

> 版本：2026-08-29 · 方法：实机验证（当日）+ 源码审计

---

## 1. 执行摘要

**FastAPI :5000 整个 API 面无认证，暴露 `/docs`（Swagger UI）、`/openapi.json`（完整路由）与
多个信息泄露端点（`/api/sn` 等）。此外 `/api/export` 每次成功导出在 `/tmp/exports/` 永久留档，
未认证可反复调用耗尽磁盘（DoS）。该服务同时承载 export/sysupload/rename-folder 等读写原语，
是本设备攻击面的中枢。**

严重度定级：**中危（Medium）**——信息泄露 + 磁盘 DoS；其承载的读写原语已单独定级 Critical。

---

## 2. 实机验证（2026-08-29）

| 端点 | 结果 |
|---|---|
| `GET /api/sn` | `{"code":200,...,"sn":"<其他机器人设备_01>"}`（未认证泄露 SN） |
| `GET /docs` | HTTP 200（Swagger UI 暴露） |
| `GET /openapi.json` | 15 条路由（见下） |
| `POST /api/export` | 路径穿越任意文件读（见 export 目录） |

**openapi.json 实际路由（15 条，含报告未列的 expression 系列）**：
`/api/sysupload`、`/api/export`、`/list-files`、`/api/ping`、`/api/sn`、`/static/{filename}`、
`/api/rename-folder`、`/api/faultconfig/update`、`/api/expressions`、`/api/expression/upload`、
`/api/expression/delete`、`/api/expression/update`、`/api/expression/check/{key}`、`/api/expression/{key}`

> 报告此前记录 12 条路由；实机为 15 条（新增 expression 系列），详见源码审计 lead。

## 3. 磁盘填满 DoS

- `/api/export` 每次成功导出在 `/tmp/exports/tmp*/` 生成 `exported_maps.tar.gz`，**不清理**；
- 未认证反复调用 → 磁盘耗尽 → 服务/系统不可用；
- 研究过程已清理一次（`find /tmp/exports -name exported_maps.tar.gz -delete`）。

## 4. 受影响范围

- 组件：`t800-web-backend` v0.2.9（:5000 FastAPI，Alpine 容器 root）
- 入口：任意 `:5000` 路由，无认证

## 5. 修复建议

1. 全局增加认证/鉴权中间件（修复 auth 缺失根因）；
2. 生产关闭 `/docs`、`/openapi.json`；
3. `/api/export` 完成后清理留档，或流式返回不落盘。

## 6. 证据文件

| 文件 | 内容 |
|---|---|
| `evidence/fastapi_live.txt` | /api/sn、/docs、/openapi 路由、SRS banner 实机响应 |
