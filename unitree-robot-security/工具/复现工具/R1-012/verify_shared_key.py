#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""共享密钥三方互证 PoC(离线比对,零网络动作)
① 固件 etc/key/aes_key.bin 读取
② 与已知三方值比对(BLE/WebRTC PoC 参数、云端 bindlist 返回)
用法: python verify_shared_key.py [固件根目录]
"""
import sys, hashlib

FW = sys.argv[1] if len(sys.argv) > 1 else r'C:\zyh\work\宇树固件\real_unitree_r1_1.4.2'
KEY_PATH = FW + r'\etc\key\aes_key.bin'

# 三方已知值(证据来源见 evidence/three-way-verification.md)
WEBRTC_POC_KEY = '85b3f0b12c51dfb5815df26000107d6a'   # CHAIN-D/E PoC aes_128_key
CLOUD_DEV_KEY  = '85b3f0b12c51dfb5815df26000107d6a'   # 2026-08-30 bindlist 返回
BLE_SESSION_KEY = '85b3f0b12c51dfb5815df26000107d6a'  # BLE RCE 包 GCM key

data = open(KEY_PATH, 'rb').read()
firmware_hex = data.hex()
print(f'固件 aes_key.bin : {firmware_hex}  ({len(data)} 字节, md5={hashlib.md5(data).hexdigest()})')
for name, val in [('WebRTC 数据通道 PoC', WEBRTC_POC_KEY),
                  ('云端 bindlist dev.key', CLOUD_DEV_KEY),
                  ('BLE 会话 GCM key', BLE_SESSION_KEY)]:
    same = '一致 ✓' if val == firmware_hex else '不一致 ✗'
    print(f'{name:22}: {val}  → {same}')
print()
print('三方一致 = 一把公开常量承担近场/远程/云端三层信任(详见漏洞报告)。')
