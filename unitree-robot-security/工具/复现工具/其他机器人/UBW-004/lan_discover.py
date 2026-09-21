#!/usr/bin/env python3
"""LAN 通道发现：原始 mDNS 查询，自动拿到机器人 IP + SRV 端口（+ 序列号/电量）。

为什么要它：LAN 通道端口是 `Random.nextInt(2000)+50000`，**每次通道重启都换**（docs/09 §3、
docs/12 §1），硬编码必错 —— 必须每次以 SRV 记录为准。本机 `avahi-daemon` 未运行、无 `zeroconf`
模块（docs/12 §2），故这里自写零依赖的原始 mDNS 客户端：向 `224.0.0.251:5353` 发 PTR 查询、
解析 PTR/SRV/TXT/A，聚合出 {序列号, ip, port, txt}。

两种用法：
  1) 独立跑（只发现，不连接）：
       python3 firmware_research/tools/lan_discover.py --src <板卡在目标网段的IP>
     加 --emit 直接吐出可粘贴的 `--robot <ip> --port <port>` 片段。
  2) 被 lan_pull.py / lan_shell.py 复用：不传 --robot/--port 时自动调用本模块解析
     （`resolve_target()`），--src 默认取 --lhost（板卡 IP）。

注意：QU（单播响应）位已置位 ⇒ 机器人多半直接单播回你的临时端口；同时也 join 组播 224.0.0.251
兜底。若同网段有多台机器人，用 --serial 指定（模糊匹配实例名/序列号）。
"""
import argparse
import socket
import struct
import sys
import time

try:
    import fcntl  # Linux SIOCGIFADDR，用于 --iface 自动取板卡 IPv4
    _HAS_FCNTL = True
except ImportError:
    _HAS_FCNTL = False


def iface_ipv4(name: str) -> str:
    """取网卡 name 的 IPv4（Linux）。板卡网卡如 wlp0s20f0u3u1。取不到抛异常。"""
    if not _HAS_FCNTL:
        raise RuntimeError("本平台不支持 --iface 自动取 IP，请显式 --lhost")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        packed = struct.pack("256s", name[:15].encode())
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, packed)[20:24])  # SIOCGIFADDR
    finally:
        s.close()

MDNS_GROUP = "224.0.0.251"
MDNS_PORT = 5353
DEFAULT_SERVICE = "_Dedu_mini_channel_server._tcp.local"  # 国内教育版 DEDU；海外/标准版可换
_TYPE_A, _TYPE_PTR, _TYPE_TXT, _TYPE_SRV = 1, 12, 16, 33


# ----------------------------------------------------------------------------- DNS 报文
def _build_query(qname: str, qtype: int = _TYPE_PTR) -> bytes:
    hdr = struct.pack(">HHHHHH", 0, 0, 1, 0, 0, 0)  # id=0, qd=1（mDNS 忽略 id）
    body = b""
    for label in qname.split("."):
        if label:
            body += bytes([len(label)]) + label.encode()
    body += b"\x00"
    body += struct.pack(">HH", qtype, 0x8001)  # QU 位(0x8000) + class IN(1)
    return hdr + body


def _read_name(buf: bytes, off: int):
    """解析 DNS 名（含 0xC0 压缩指针）。返回 (name, next_off)。"""
    labels, jumped, nxt = [], False, off
    guard = 0
    while True:
        guard += 1
        if guard > 128 or off >= len(buf):
            break
        ln = buf[off]
        if ln == 0:
            off += 1
            break
        if ln & 0xC0 == 0xC0:
            ptr = ((ln & 0x3F) << 8) | buf[off + 1]
            if not jumped:
                nxt = off + 2
            off, jumped = ptr, True
            continue
        off += 1
        labels.append(buf[off:off + ln].decode("utf-8", "replace"))
        off += ln
    return ".".join(labels), (nxt if jumped else off)


def _parse(buf: bytes):
    """返回记录列表 [{name,type,...}]。只解析我们关心的 PTR/SRV/TXT/A。"""
    if len(buf) < 12:
        return []
    _id, _flags, qd, an, ns, ar = struct.unpack(">HHHHHH", buf[:12])
    off = 12
    for _ in range(qd):
        _, off = _read_name(buf, off)
        off += 4
    recs = []
    for _ in range(an + ns + ar):
        if off + 10 > len(buf):
            break
        name, off = _read_name(buf, off)
        rtype, _rclass, _ttl, rdlen = struct.unpack(">HHIH", buf[off:off + 10])
        off += 10
        rd = buf[off:off + rdlen]
        rec = {"name": name, "type": rtype}
        if rtype == _TYPE_PTR:
            rec["ptr"], _ = _read_name(buf, off)
        elif rtype == _TYPE_SRV and rdlen >= 6:
            _pri, _wt, port = struct.unpack(">HHH", rd[:6])
            tgt, _ = _read_name(buf, off + 6)
            rec["port"], rec["target"] = port, tgt
        elif rtype == _TYPE_TXT:
            txts, i = [], 0
            while i < len(rd):
                ln = rd[i]
                i += 1
                if ln:
                    txts.append(rd[i:i + ln].decode("utf-8", "replace"))
                i += ln
            rec["txt"] = txts
        elif rtype == _TYPE_A and rdlen >= 4:
            rec["a"] = ".".join(str(b) for b in rd[:4])
        off += rdlen
        recs.append(rec)
    return recs


# ----------------------------------------------------------------------------- 发现
def discover(src: str = "", service: str = DEFAULT_SERVICE, secs: float = 4.0):
    """发多播 PTR 查询、收 secs 秒、聚合。返回 [{instance,fqdn,ip,port,txt}]。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except (AttributeError, OSError):
        pass
    bound_5353 = True
    try:
        s.bind((src or "", MDNS_PORT))            # 绑 5353 收组播；被占用则退临时端口靠 QU 单播
    except OSError:
        bound_5353 = False
        s.bind((src or "", 0))
    if src:
        try:
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(src))
        except OSError:
            pass
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
    if bound_5353:
        mreq = socket.inet_aton(MDNS_GROUP) + socket.inet_aton(src or "0.0.0.0")
        try:
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except OSError:
            pass

    for q in (service, "_services._dns-sd._udp.local"):
        try:
            s.sendto(_build_query(q), (MDNS_GROUP, MDNS_PORT))
        except OSError:
            pass

    recs = []
    deadline = time.time() + secs
    while time.time() < deadline:
        s.settimeout(max(0.05, deadline - time.time()))
        try:
            data, _ = s.recvfrom(9000)
        except socket.timeout:
            break
        except OSError:
            break
        try:
            recs += _parse(data)
        except Exception:
            pass
    s.close()

    # 聚合：A 记录建 host→ip 映射，SRV/TXT/PTR 建 instance→info，再把 SRV.target 解析成 ip
    hosts, insts = {}, {}
    for r in recs:
        t = r["type"]
        if t == _TYPE_A:
            hosts[r["name"]] = r["a"]
        elif t == _TYPE_PTR and r["name"] == service:
            insts.setdefault(r["ptr"], {})
        elif t == _TYPE_SRV and r["name"].endswith(service):
            insts.setdefault(r["name"], {}).update(port=r["port"], target=r["target"])
        elif t == _TYPE_TXT and r["name"].endswith(service):
            insts.setdefault(r["name"], {})["txt"] = r["txt"]

    out = []
    for fqdn, info in insts.items():
        if "port" not in info:
            continue
        out.append({
            "instance": fqdn.split(".")[0],          # 序列号，如 Dedu_<其他机器人设备_01>
            "fqdn": fqdn,
            "ip": hosts.get(info.get("target", "")),
            "port": info["port"],
            "txt": info.get("txt", []),
        })
    out.sort(key=lambda x: x["instance"])
    return out


def resolve_target(robot, port, src, serial=None, service=DEFAULT_SERVICE, secs=4.0):
    """给 lan_pull / lan_shell 用：robot+port 都给了就直接返回；否则 mDNS 补齐缺的那个。
    返回 (ip, port)；无法确定时 SystemExit 并给出可读提示。"""
    if robot and port:
        return robot, int(port)
    found = discover(src=src, service=service, secs=secs)
    if serial:
        found = [f for f in found if serial in f["instance"] or serial in f["fqdn"]]
    if not found:
        raise SystemExit("[-] mDNS 未发现机器人。检查：--src 是否为板卡在目标网段的 IP、"
                         "板卡是否已 wifi_link 上目标 AP；或直接手动给 --robot/--port。")
    if len(found) > 1 and not serial:
        lines = "\n".join(f"    {f['instance']}  {f['ip']}:{f['port']}  {f['txt']}" for f in found)
        raise SystemExit(f"[-] 发现多台，用 --serial 指定其一：\n{lines}")
    f = found[0]
    ip = robot or f["ip"]
    pt = int(port) if port else f["port"]
    if not ip:
        raise SystemExit(f"[-] 解析到端口 {f['port']} 但无 A 记录 IP（target={f['fqdn']}）；手动加 --robot。")
    print(f"[+] mDNS: {f['instance']} → {ip}:{pt}  txt={f['txt']}", file=sys.stderr)
    return ip, pt


# ----------------------------------------------------------------------------- CLI
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default="", help="发查询用的本机 IP（板卡在目标网段的 IP，强烈建议指定）")
    ap.add_argument("--service", default=DEFAULT_SERVICE, help=f"mDNS 服务类型（默认 {DEFAULT_SERVICE}）")
    ap.add_argument("--secs", type=float, default=4.0, help="收集秒数（默认 4）")
    ap.add_argument("--serial", help="只显示实例名/序列号含此子串的那台")
    ap.add_argument("--emit", action="store_true", help="额外输出可粘贴的 `--robot <ip> --port <port>` 片段")
    a = ap.parse_args()

    found = discover(src=a.src, service=a.service, secs=a.secs)
    if a.serial:
        found = [f for f in found if a.serial in f["instance"] or a.serial in f["fqdn"]]
    if not found:
        print("[-] 未发现。检查 --src 与板卡是否在目标网段。", file=sys.stderr)
        return 1
    print(f"[+] 发现 {len(found)} 台：", file=sys.stderr)
    for f in found:
        print(f"  {f['instance']:28s} {str(f['ip']):15s}:{f['port']}  {f['txt']}")
    if a.emit and len(found) == 1 and found[0]["ip"]:
        print(f"--robot {found[0]['ip']} --port {found[0]['port']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
