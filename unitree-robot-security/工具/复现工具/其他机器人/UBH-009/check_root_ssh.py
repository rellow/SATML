#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看宿主 /root/.ssh 现状（只读）。"""
import sys
import paramiko

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("192.168.11.3", username="walker", password="<密码_01>", timeout=15)
for cmd in [
    "sudo ls -la /root/.ssh/",
    "sudo stat -c '%A %U:%G %n' /root/.ssh",
    "sudo wc -c /root/.ssh/authorized_keys 2>/dev/null || echo 'no authorized_keys'",
    "sudo head -c 200 /root/.ssh/authorized_keys 2>/dev/null",
]:
    _, o, e = c.exec_command(cmd, timeout=20)
    print(f"$ {cmd}\n{o.read().decode(errors='replace').strip()}\n")
c.close()
