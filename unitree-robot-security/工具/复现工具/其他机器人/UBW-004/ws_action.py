#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ws_action.py — 8800 端口零鉴权动作执行（U-02 武器化）。
协议与官方 alphamini SDK（mini/apis/api_action.py）一致：
  WS 文本帧 = base64(Message) + "&"；MessageHeader{id=1,target=2,command=3}
  命令号（_PCProgramCmdId）：1=播放动作 2=移动 3=停止全部动作 33=取动作列表

⚠ 实机怪癖（v1.6.3.919）：响应恒为 isSuccess=False / resultCode=-92，
  但动作实际会正常执行（实机已验证：下蹲/点头/举双手/打招呼/弯腰）。
  因此本脚本以"发送成功"为准，结果码仅供参考。

用法：
  python ws_action.py list [inner|custom]        # 列动作（默认内置）
  python ws_action.py play "动作名或ID"           # 播放动作（如 011、standbysquat_001）
  python ws_action.py move forward 3             # 前进 3 步（forward/backward/leftward/rightward）
  python ws_action.py stop                       # 停止全部动作
仅用于自有设备。
"""
import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "lib"))
import ws_cmd
from lan_channel_client import pb_str, pb_i32, pb_decode, _s, _n

ROBOT = "192.168.8.200"
WPORT = 8800

CMD_PLAY = 1
CMD_MOVE = 2
CMD_STOP = 3
CMD_LIST = 33

DIRECTIONS = {"leftward": 1, "rightward": 2, "forward": 3, "backward": 4,
              "左": 1, "右": 2, "前": 3, "后": 4}


def decode_action_list(body):
    d = pb_decode(body)
    out = []
    for raw in d.get(1, []):
        a = pb_decode(raw)
        out.append({"id": _s(a, 1), "cnName": _s(a, 2), "enName": _s(a, 3), "type": _n(a, 4)})
    return out, bool(_n(d, 2)), _n(d, 3)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["list", "play", "move", "stop"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--robot", default=ROBOT)
    a = ap.parse_args()

    s = ws_cmd.ws_connect(a.robot, WPORT)
    try:
        if a.action == "list":
            atype = 1 if (a.args and a.args[0].lower() == "custom") else 0
            r = ws_cmd.transact(s, CMD_LIST, pb_i32(2, atype), wait=20)
            if not r:
                print("[-] 无响应")
                return 1
            items, ok, rc = decode_action_list(r["body"])
            print(f"[+] isSuccess={ok} resultCode={rc}，共 {len(items)} 个动作：")
            for it in items:
                print(f"    {it['cnName'] or it['enName'] or it['id']}"
                      f"{'  (' + it['enName'] + ')' if it['cnName'] and it['enName'] else ''}")
        elif a.action == "play":
            if not a.args:
                ap.error("play 需要动作名")
            name = " ".join(a.args)
            print(f"[*] 播放动作 {name!r}（动作执行期间机器人会动，请注意周围安全）")
            r = ws_cmd.transact(s, CMD_PLAY, pb_str(1, name), wait=60)
            if not r:
                print("[-] 无响应")
                return 1
            d = pb_decode(r["body"])
            print(f"[+] isSuccess={bool(_n(d, 1))} resultCode={_n(d, 2)}")
        elif a.action == "move":
            if not a.args or a.args[0].lower() not in DIRECTIONS:
                ap.error(f"move 需要方向：{'/'.join(DIRECTIONS)}")
            steps = int(a.args[1]) if len(a.args) > 1 else 1
            dval = DIRECTIONS[a.args[0].lower()]
            print(f"[*] 移动 direction={dval} step={steps}")
            r = ws_cmd.transact(s, CMD_MOVE, pb_i32(1, dval) + pb_i32(2, steps), wait=30)
            if not r:
                print("[-] 无响应")
                return 1
            d = pb_decode(r["body"])
            print(f"[+] isSuccess={bool(_n(d, 1))} code={_n(d, 2)}")
        elif a.action == "stop":
            r = ws_cmd.transact(s, CMD_STOP, b"", wait=15)
            if not r:
                print("[-] 无响应")
                return 1
            d = pb_decode(r["body"])
            print(f"[+] isSuccess={bool(_n(d, 1))} resultCode={_n(d, 2)}")
        return 0
    finally:
        try:
            ws_cmd.ws_send_frame(s, 0x8, b"")
            s.close()
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
