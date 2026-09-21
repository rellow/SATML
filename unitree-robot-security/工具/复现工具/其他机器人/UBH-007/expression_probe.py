#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walker S2 · /api/expression/* 表情管理面探测（只读，不实际上传/删除）

用法:
    python expression_probe.py
    可选: --key hacker_by_Polaris  查看单个表情
"""
import argparse
import json
import sys

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    ap = argparse.ArgumentParser(description="expression 表情管理面探测")
    ap.add_argument("--host", default="192.168.11.3")
    ap.add_argument("--key", default=None, help="查看单个表情 /api/expression/{key}")
    args = ap.parse_args()
    base = f"http://{args.host}:5000"

    print("=" * 66)
    print("[*] 发现   : openapi 暴露 expression 管理系列（报告未列）")
    print(f"[*] 目标   : {base}/api/expression/*")
    print("=" * 66)

    # 1. 表情列表
    r = requests.get(f"{base}/api/expressions", timeout=10)
    print(f"\n[1] GET /api/expressions  →  HTTP {r.status_code}")
    try:
        exprs = r.json().get("data", {}).get("expressions", [])
        print(f"    共 {len(exprs)} 个表情:")
        for e in exprs:
            print(f"      key={e.get('key')}  name={e.get('name_cn')}  type={e.get('type')}  "
                  f"time={e.get('update_time')}  default={e.get('is_default')}")
    except Exception:
        print("    " + r.text[:300])

    # 2. 上传接口方法限制（不实际上传）
    for meth in ("OPTIONS", "GET", "POST"):
        try:
            rr = requests.request(meth, f"{base}/api/expression/upload", timeout=8)
            allow = rr.headers.get("allow", "")
            print(f"\n[2] {meth} /api/expression/upload  →  HTTP {rr.status_code}"
                  + (f"  Allow: {allow}" if allow else ""))
            if rr.status_code != 405 and rr.status_code != 404 and rr.text:
                print("    响应: " + rr.text[:200])
        except Exception as e:
            print(f"[2] {meth} 失败: {e}")

    # 3. 单个表情（--key 指定或取列表第一个）
    if args.key is None and exprs:
        args.key = exprs[0].get("key")
    if args.key:
        r = requests.get(f"{base}/api/expression/{args.key}", timeout=10)
        print(f"\n[3] GET /api/expression/{args.key}  →  HTTP {r.status_code}")
        ct = r.headers.get("content-type", "")
        print(f"    content-type: {ct}  size={len(r.content)}B")
        if r.status_code == 200 and "json" in ct:
            print("    " + r.text[:300])
        elif r.status_code == 200:
            print(f"    文件头: {r.content[:16]!r}  (可能是视频/表情文件)")

    print("\n[*] 结论方向:")
    print("    - /api/expressions 未认证可读 → 表情目录枚举")
    print("    - 若 upload 无需认证 → 可上传/覆盖/删除机器人显示表情（存储型内容注入）")
    print("    - 需进一步确认 upload 参数是否含路径字段（若可写任意路径则升级为文件写）")


if __name__ == "__main__":
    main()
