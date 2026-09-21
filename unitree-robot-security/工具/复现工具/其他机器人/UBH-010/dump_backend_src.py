#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dump t800-web-backend 容器全部 .py 源码 → evidence/backend_source_dump.txt
经 vision 板 <密码_01> 进容器 docker exec（只读，不修改设备）。
用法: python dump_backend_src.py
"""
import os
import sys

import paramiko

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VISION = "192.168.11.3"
CONTAINER = "walker-web.web-backend-1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence", "backend_source_dump.txt")


def main():
    print(f"[*] ssh {VISION} (<密码_01>) → docker exec {CONTAINER} dump /app *.py")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(VISION, username="walker", password="<密码_01>", timeout=15)
    cmd = (
        f"docker exec {CONTAINER} sh -c "
        "'cd /app && for f in $(find . -name \"*.py\" | sort); do "
        "echo \"===== $f =====\"; cat \"$f\"; done'"
    )
    _, o, e = c.exec_command(cmd, timeout=120)
    out = o.read().decode(errors="replace")
    err = e.read().decode(errors="replace")
    c.close()

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"[+] 已保存 {os.path.abspath(OUT)}  ({len(out)} 字节)")
    if err.strip():
        print(f"[!] stderr: {err[:300]}")

    # 打印文件清单
    print("\n--- /app 文件清单 ---")
    import re
    for m in re.finditer(r"===== (\S+) =====", out):
        print("  " + m.group(1))


if __name__ == "__main__":
    main()
