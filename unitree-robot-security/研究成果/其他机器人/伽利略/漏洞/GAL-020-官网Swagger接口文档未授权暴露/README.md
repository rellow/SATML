---
编号: GAL-020
验证状态: 动态确认
严重程度: 高
披露状态: 内部研究
源平台: 伽利略
源候选目录: 官网Swagger接口文档未授权暴露-1
---
# GAL-020 伽利略官网 Swagger UI / OpenAPI 接口文档未授权暴露 漏洞报告

## 1. 一句话结论

- # 伽利略官网 Swagger UI / OpenAPI 接口文档未授权暴露 漏洞报告
- \| 权限 \| 无需任何凭据，公网任意可达 \|
- ## 1. 漏洞概述
- - `GET /api/swagger-resources` → 200 `[{"name":"default","url":"/v3/api-docs","swaggerVersion":"3.0.3"}]`
- ## 2. 危害

## 2. 影响产品与版本

- \| 漏洞组件 \| 官网后台若依 RuoYi v3.9.1（路径 `/api`，Spring Boot + SpringDoc） \|
- \| 漏洞类型 \| 敏感信息泄露——Swagger UI 与全量 OpenAPI 接口文档无认证公开 + 开发环境配置泄漏 \|
- 2. **开发环境配置泄漏**：所有路径带 `/dev-api/` 前缀 = **开发 profile 的 swagger 配置原样进了生产**；
- 1. 生产环境关闭 SpringDoc/Swagger（`springdoc.api-docs.enabled=false`）或加 Spring Security 鉴权；

## 3. 验证状态

`动态确认`。该状态来自源报告的验证边界；迁移过程不把目录名称自动视为动态确认。

## 4. 攻击前提

攻击前提以脱敏研究正文为准；复现必须使用自有设备、隔离网络和授权环境，不得对第三方设备执行写入、控制或破坏性操作。

## 5. 根本原因

- \| 漏洞类型 \| 敏感信息泄露——Swagger UI 与全量 OpenAPI 接口文档无认证公开 + 开发环境配置泄漏 \|

## 6. 攻击过程

源报告描述的入口、协议和利用顺序见第 13 节脱敏正文；本目录只保留最小复现材料，不复制原始大型证据。

## 7. 实际影响

- \| 漏洞类型 \| 敏感信息泄露——Swagger UI 与全量 OpenAPI 接口文档无认证公开 + 开发环境配置泄漏 \|
- \| 严重度 \| 🟠 Medium（接口面全量泄露，为后续越权/注入测试提供完整地图） \|
- 其 **Swagger UI 与 OpenAPI 文档端点未做任何访问控制**，公网可直接读取：
- 泄露内容包括：
- ## 2. 危害

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

# 伽利略官网 Swagger UI / OpenAPI 接口文档未授权暴露 漏洞报告

| 项 | 值 |
|---|---|
| 目标 | 伽利略（天津）技术有限公司官网 `https://www.galileotime.com`（厂商云端资产） |
| 漏洞组件 | 官网后台若依 RuoYi v3.9.1（路径 `/api`，Spring Boot + SpringDoc） |
| 漏洞类型 | 敏感信息泄露——Swagger UI 与全量 OpenAPI 接口文档无认证公开 + 开发环境配置泄漏 |
| 严重度 | 🟠 Medium（接口面全量泄露，为后续越权/注入测试提供完整地图） |
| 权限 | 无需任何凭据，公网任意可达 |
| 复现日期 | 2026-08-29 |
| 授权边界 | 授权比赛范围内厂商云端资产，只读取证 |

---

## 1. 漏洞概述

官网 `www.galileotime.com` 的后端是**若依 RuoYi v3.9.1 管理框架**（挂在前端 SPA 的 `/api` 前缀下）。
其 **Swagger UI 与 OpenAPI 文档端点未做任何访问控制**，公网可直接读取：

- `GET /api/swagger-ui/index.html` → 200 Swagger UI 页面
- `GET /api/swagger-resources` → 200 `[{"name":"default","url":"/v3/api-docs","swaggerVersion":"3.0.3"}]`
- `GET /api/v3/api-docs` → 200 **47KB 完整 OpenAPI 3.0.3 JSON**

泄露内容包括：

1. **35 个后端接口全量清单**（官网 CMS：文章/栏目/素材/产品/招聘/客户信息/简历上传、
   测试模块 `test/user` 全套 CRUD、`/dev-api/cms/...`）——含每个接口的参数结构、
   实体 schema（`CustomerInfo`/`Resume`/`UserEntity`/文章/栏目/素材实体）；
2. **开发环境配置泄漏**：所有路径带 `/dev-api/` 前缀 = **开发 profile 的 swagger 配置原样进了生产**；
3. `servers` 字段暴露推断源 `http://www.galileotime.com:80`；
4. 后端框架指纹（若依管理系统 v3.9.1）——历史漏洞库直接可查。

对比：管理类接口（`/api/system/user/list`、`/api/getInfo`、`/api/test/user/list`）均有
Spring Security 鉴权（401），**唯独接口文档端点裸奔**。

## 2. 危害

- 攻击者零凭据获得**完整后端攻击面地图**（正常应藏在内网）；
- `dev-api` 前缀表明 CI/CD 配置管理混乱，提示可能存在其他 dev 残留；
- 简历上传（`/website/posts/uploadResume`）、客户信息收集（`commitCustomerInfo`）等
  写接口的参数结构直接可得，便于构造恶意上传/注入测试；
- 若依 v3.9.1 指纹 + 接口清单 = 可直接套用若依已知漏洞（SQLi 模式、默认口令等）做定向验证。

## 3. 复现步骤

任意公网主机（浏览器或 curl）：

```bash
# ① Swagger UI 页面（无需任何认证）
curl -k 'https://www.galileotime.com/api/swagger-ui/index.html'

# ② swagger-resources
curl -k 'https://www.galileotime.com/api/swagger-resources'

# ③ 完整 OpenAPI 文档（47KB，核心证据）
curl -k 'https://www.galileotime.com/api/v3/api-docs' -o api-docs.json
python -c "import json;d=json.load(open('api-docs.json'));print(d['info']['title'],len(d['paths']))"
```

浏览器直接打开 `https://www.galileotime.com/api/swagger-ui/index.html` 同样可见
可交互调试界面。

⚠️ 注意：目标站点前置腾讯 EdgeOne WAF。python-requests 默认指纹/代理出口可能被
567 拦截页命中；**直连（不走代理）+ 浏览器 UA** 即正常返回（exp 已内置该处理）。

## 4. exp 使用

```bash
python exploit.py                    # 取证: 拉取三件套 + 枚举全部接口 + 存 evidence/
python exploit.py --open             # 顺手用系统浏览器打开 Swagger UI
```

判定：`/api/v3/api-docs` 返回 200 且 JSON 含 `"openapi":"3.0.3"` 与 paths 列表 = 复现成功。

## 5. 修复建议

1. 生产环境关闭 SpringDoc/Swagger（`springdoc.api-docs.enabled=false`）或加 Spring Security 鉴权；
2. 清理 `dev-api` 开发前缀等 dev 配置残留，按 profile 隔离；
3. WAF 规则拦截 `/swagger*`、`/v3/api-docs`、`/actuator` 等管理路径的外网访问。

## 6. 证据

- `evidence/v3_api-docs_20260829.json`：47KB OpenAPI 文档原样存档（本次取证拉取）
- `evidence/swagger-ui_index.html`：Swagger UI 页面存档
- `evidence/endpoint_list_20260829.txt`：35 接口清单（exp 自动生成）
- 发现过程记录：`C:\zyh\work\机器人\伽利略\analysis\security-record.md` 云端第二轮章节
