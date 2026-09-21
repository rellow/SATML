#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ws_cmd.py — 8801 端口 WebSocket PyPi 通道客户端（U-02/U-17，零第三方依赖）。
协议（来自官方 SDK mini/pkg_tool.py）：
  WS 文本帧 = base64(Message) + "&"；Message{header{id=1,target=2,command=3}, bodyData=2}
  命令：1=装包 8=上传脚本 10=运行脚本 11=停脚本 12=列脚本
用法：
  python ws_cmd.py list
  python ws_cmd.py upload <本地文件> <远端文件名>
  python ws_cmd.py run <远端文件名>
  python ws_cmd.py stop <远端文件名>
"""
import argparse
import base64
import os
import socket
import struct
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "lib"))
from lan_channel_client import _varint, _tag, pb_str, pb_bytes, pb_i32, pb_decode, _s, _n

ROBOT = "192.168.8.200"
WPORT = 8801


# ---------------------------------------------------------------- 最小 WS 客户端
def ws_connect(host, port, timeout=10):
    s = socket.create_connection((host, port), timeout=timeout)
    key = base64.b64encode(os.urandom(16)).decode()
    req = (f"GET / HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\n"
           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
    s.sendall(req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        c = s.recv(4096)
        if not c:
            raise RuntimeError("WS 握手失败：连接被关闭")
        resp += c
    line = resp.split(b"\r\n", 1)[0].decode("utf-8", "replace")
    if "101" not in line:
        raise RuntimeError(f"WS 握手失败：{line}")
    print(f"[+] WS 升级成功（{line.strip()}）")
    return s


def ws_send_text(s, data: bytes):
    mask = os.urandom(4)
    n = len(data)
    hdr = b"\x81"
    if n < 126:
        hdr += bytes([0x80 | n])
    elif n < 65536:
        hdr += bytes([0x80 | 126]) + struct.pack(">H", n)
    else:
        hdr += bytes([0x80 | 127]) + struct.pack(">Q", n)
    s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


def _recvn(s, n):
    b = b""
    while len(b) < n:
        c = s.recv(n - len(b))
        if not c:
            raise ConnectionError("WS 对端关闭")
        b += c
    return b


def ws_recv(s):
    """返回 (opcode, payload)；自动回 pong。"""
    while True:
        h = _recvn(s, 2)
        op = h[0] & 0x0F
        ln = h[1] & 0x7F
        if ln == 126:
            ln = struct.unpack(">H", _recvn(s, 2))[0]
        elif ln == 127:
            ln = struct.unpack(">Q", _recvn(s, 8))[0]
        payload = _recvn(s, ln) if ln else b""
        if op == 0x9:                # ping → pong
            ws_send_frame(s, 0xA, payload)
            continue
        return op, payload


def ws_send_frame(s, op, payload):
    mask = os.urandom(4)
    n = len(payload)
    hdr = bytes([0x80 | op])
    if n < 126:
        hdr += bytes([0x80 | n])
    elif n < 65536:
        hdr += bytes([0x80 | 126]) + struct.pack(">H", n)
    else:
        hdr += bytes([0x80 | 127]) + struct.pack(">Q", n)
    s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))


# ---------------------------------------------------------------- 消息层
def build_msg(cmd, body: bytes, mid="0"):
    header = pb_str(1, mid) + pb_i32(3, cmd)
    return pb_bytes(1, header) + pb_bytes(2, body)


def transact(s, cmd, body, wait=15):
    payload = base64.b64encode(build_msg(cmd, body)) + b"&"
    ws_send_text(s, payload)
    end = time.time() + wait
    while time.time() < end:
        s.settimeout(max(0.5, end - time.time()))
        try:
            op, data = ws_recv(s)
        except socket.timeout:
            continue
        if op == 0x8:
            print("[-] WS 收到关闭帧")
            return None
        if op != 0x1:
            continue
        raw = base64.b64decode(data.rstrip(b"&"))
        m = pb_decode(raw)
        hdr = pb_decode(m[1][0]) if 1 in m else {}
        return {"command": _n(hdr, 3), "id": _s(hdr, 1), "body": m[2][0] if 2 in m else b""}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["list", "upload", "run", "stop"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--robot", default=ROBOT)
    a = ap.parse_args()

    s = ws_connect(a.robot, WPORT)
    try:
        if a.action == "list":
            r = transact(s, 12, b"")
            if r:
                d = pb_decode(r["body"])
                print(f"[+] cmd={r['command']} fields={d}")
                for f, vals in d.items():
                    for v in vals:
                        print(f"    f{f}: {v if not isinstance(v, bytes) else v.decode('utf-8','replace')}")
            else:
                print("[-] 无响应")
        elif a.action == "upload":
            local, remote = a.args[0], a.args[1]
            content = open(local, "rb").read()
            body = pb_str(1, remote) + pb_bytes(2, content)
            r = transact(s, 8, body, wait=30)
            if r:
                d = pb_decode(r["body"])
                print(f"[+] upload resultCode={_n(d,1)} message={_s(d,2)!r}")
            else:
                print("[-] 无响应")
        elif a.action in ("run", "stop"):
            body = pb_str(1, a.args[0])
            r = transact(s, 10 if a.action == "run" else 11, body, wait=30)
            if r:
                d = pb_decode(r["body"])
                print(f"[+] {a.action} resultCode={_n(d,1)} message={_s(d,2)!r}")
            else:
                print("[-] 无响应")
    finally:
        try:
            ws_send_frame(s, 0x8, b"")
            s.close()
        except OSError:
            pass


if __name__ == "__main__":
    main()
