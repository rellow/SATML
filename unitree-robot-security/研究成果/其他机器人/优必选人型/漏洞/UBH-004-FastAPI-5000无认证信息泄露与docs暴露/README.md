---
ID: UBH-004
validation_status: dynamically confirmed
severity: high
disclosure_status: internal research
source_platform: UBTECH Humanoid
source_candidate_directory: FastAPI-5000无认证信息泄露与docs暴露-1
---
# UBH-004 t800-web-backend FastAPI :5000 Unauthenticated Information Exposure, Swagger Exposure, and Disk-Exhaustion DoS

## 1. Summary

The FastAPI service on port 5000 exposes its API surface without authentication, including Swagger/OpenAPI documentation and information endpoints such as `/api/sn`. The export endpoint also leaves generated archives behind, allowing repeated unauthenticated requests to consume disk space. Higher-impact read/write primitives hosted by the same service are tracked separately.

## 2. Affected Products and Versions

- Evidence date: 2026-08-29.
- Method: live validation plus source review.
- Component: `t800-web-backend` v0.2.9, FastAPI on port 5000.

## 3. Validation Status

`dynamically confirmed`. The documentation and information endpoints were observed live; destructive disk exhaustion was not driven to failure.

## 4. Attack Preconditions

The attacker must be able to reach port 5000. Verification should avoid repeated export calls that could materially consume storage.

## 5. Root Cause

The service lacks a global authentication/authorization layer and exposes administrative/debug documentation plus data-bearing endpoints directly to unauthenticated network callers. Exported archive files are not automatically cleaned up.

## 6. Attack Procedure

The retained evidence uses read-only GET requests and bounded export behavior to confirm exposure. It does not intentionally fill the disk.

## 7. Impact

- Serial-number and route metadata disclosure.
- Complete Swagger/OpenAPI enumeration of the attack surface.
- Potential storage exhaustion through repeated archive creation.
- The same service also hosts separate arbitrary-read/write primitives documented in their own reports.

## 8. Reproduction

See [Reproduction Material Manifest](复现/材料清单.md). Keep export testing bounded and clean up any temporary archives.

## 9. Supporting Evidence

See [Evidence Material Manifest](证据/材料清单.md) and Section 13.

## 10. Recommendations

- Add global authentication and authorization middleware.
- Disable `/docs` and `/openapi.json` in production or restrict them to administrators.
- Clean up export artifacts immediately or stream them without persistent temporary files.
- Add rate limits and storage quotas.
- Audit all routes exposed by the service.

## 11. Related AI Sessions

No complete Claude Code session record has currently been identified that maps one-to-one to this report.

## 12. Disclosure Record

- Current disclosure status: internal research.

## 13. Sanitized Original Research Body

# t800-web-backend FastAPI :5000 Unauthenticated Information Exposure, Swagger Exposure, and Disk-Exhaustion DoS

> Version: 2026-08-29 · Method: live validation + source audit

## 1. Executive Summary

The FastAPI service on port 5000 exposes its entire API surface without authentication. Live testing confirmed:

- `GET /api/sn` returned the robot serial number.
- `GET /docs` returned the Swagger UI.
- `GET /openapi.json` exposed the complete route schema.
- `POST /api/export` reaches the separately documented file-export primitive.

The export endpoint stores generated `exported_maps.tar.gz` files under `/tmp/exports/tmp*/` and does not remove them automatically. Repeated unauthenticated export calls can therefore consume disk space.

The source report rates this specific information-exposure/DoS issue **Medium**, while separate read/write primitives hosted by the same service are individually rated higher.

## 2. Live Validation (2026-08-29)

| Endpoint | Result |
|---|---|
| `GET /api/sn` | HTTP success and robot SN returned |
| `GET /docs` | HTTP 200, Swagger UI exposed |
| `GET /openapi.json` | Fifteen routes exposed |
| `POST /api/export` | Separate path-traversal read primitive documented elsewhere |

The live OpenAPI schema included `/api/sysupload`, `/api/export`, `/list-files`, `/api/ping`, `/api/sn`, `/static/{filename}`, `/api/rename-folder`, `/api/faultconfig/update`, and the expression-management route family.

## 3. Disk-Exhaustion Behavior

Every successful export creates a persistent temporary archive under `/tmp/exports/`. Because the endpoint is unauthenticated and the archives are not cleaned up, repeated requests can consume available storage.

The research process performed cleanup after bounded validation rather than attempting to exhaust the disk.

## 4. Affected Scope

- Component: `t800-web-backend` v0.2.9.
- Entry point: port 5000.
- Authentication: none observed at the service level.

## 5. Recommendations

1. Add global authentication/authorization.
2. Disable or restrict Swagger/OpenAPI in production.
3. Stream export results or delete temporary files immediately after transfer.
4. Add quotas/rate limiting and monitoring for abnormal export volume.

## 6. Evidence

`evidence/fastapi_live.txt` records live responses for `/api/sn`, `/docs`, and `/openapi.json`.
