#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""robot_ssh.py — 通过 SSH 在自有 Alpha Mini 上执行命令（root）。
用法: python robot_ssh.py "命令" ["命令2" ...]
      python robot_ssh.py --file cmds.txt
      python robot_ssh.py --get /remote/path local_dir   # 拉文件
"""
import sys
import paramiko

HOST = "192.168.8.200"
PORT = 22022
USER = "root"
PASS = "sigvoid1234"


def connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=PORT, username=USER, password=<密码_01>, timeout=15,
              allow_agent=False, look_for_keys=False)
    return c


def run(c, cmd, timeout=60):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    return out, err


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    c = connect()
    if args[0] == "--get":
        sftp = c.open_sftp()
        import os
        remote, local = args[1], args[2]
        os.makedirs(local, exist_ok=True)
        name = os.path.basename(remote.rstrip("/"))
        sftp.get(remote, os.path.join(local, name))
        print(f"[+] {remote} -> {os.path.join(local, name)}")
        return 0
    cmds = []
    if args[0] == "--file":
        cmds = [l.strip() for l in open(args[1], encoding="utf-8") if l.strip() and not l.startswith("#")]
    else:
        cmds = args
    for cmd in cmds:
        out, err = run(c, cmd)
        print(f"$ {cmd}\n{out}{('STDERR: ' + err) if err.strip() else ''}")
    c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
