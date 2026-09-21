#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bashrunner 白名单碰壁实录(GO2)— 博客图5用
对 bashrunner 连发三类注入 + 一个白名单对照,终端原样打印,供截图。
GO2 参数(2026-09-04 实测可用):
  SN=<GO2设备_01>  IP=192.168.8.154(D1-LAB,STA)  key=d47e8a9a...(Go2 机群共享)
"""
import asyncio, json, logging
logging.basicConfig(level=logging.WARNING)
from aiortc import RTCPeerConnection
RTCPeerConnection.addTransceiver = lambda *a, **k: None   # GO2/R1 桥只完成 datachannel ICE
from unitree_webrtc_connect.webrtc_driver import UnitreeWebRTCConnection, WebRTCConnectionMethod

SN = '<GO2设备_01>'
IP = '192.168.8.154'
KEY = 'd47e8a9a4b19478b6e5991c3d937a0b1'

async def main():
    conn = UnitreeWebRTCConnection(WebRTCConnectionMethod.LocalSTA,
        serialNumber=SN, ip=IP, aes_128_key=KEY, device_type='Go2', region='cn')
    await asyncio.wait_for(conn.connect(), timeout=45)
    print(f'[+] WebRTC 已连接 {IP} (SN={SN}, 免配对)\n')
    pub = conn.datachannel.pub_sub

    async def fire(name, tag):
        try:
            r = await asyncio.wait_for(pub.publish_request_new('rt/api/bashrunner/request',
                {"api_id": 1001, "parameter": json.dumps({"script": name})}), timeout=10)
            d = r['data']; code = d['header']['status']['code']
            info = d.get('data', '')
            print(f'{tag} script={name!r}')
            print(f'      → code={code}  info={str(info)[:100]}\n')
        except asyncio.TimeoutError:
            print(f'{tag} script={name!r}')
            print(f'      → (静默丢弃,无响应)\n')

    await fire('evil.sh; id',    '[注入① 命令拼接]')
    await fire('../../tmp/x.sh', '[注入② 路径穿越]')
    await fire('$(id).sh',       '[注入③ 元字符]')
    await fire('get_sn.sh',      '[对照·白名单内]')
    await conn.pc.close()

asyncio.run(main())
