#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""信令预检 — 跑 one_click 前先跑这个,逐层定位问题(不改动 one_click 主体)
检查项:
  ① 本机 WiFi SSID(防止"以为连着机器人,实际 Windows 漫游切走"——真实踩过)
  ② 系统代理残留(HTTP_PROXY/TUN 常见坑)
  ③ ping 机器人
  ④ TCP 9991 握手
  ⑤ 完整 POST /con_notify(15s 超时,打印原始应答)
根据结果给出诊断与建议。
用法: python signaling_check.py [--ip 192.168.12.1]
"""
import argparse, os, socket, subprocess, sys, urllib.request

def wifi_ssid():
    try:
        raw = subprocess.run(['netsh','wlan','show','interfaces'], capture_output=True,
                             timeout=10).stdout
        # 先严格 UTF-8(本机实测),失败则 GBK —— 严格解码保证不会"合法地解出乱码"
        try:
            out = raw.decode('utf-8')
        except UnicodeDecodeError:
            out = raw.decode('gbk', errors='replace')
        for ln in out.splitlines():
            if 'SSID' in ln and 'BSSID' not in ln:
                return ln.split(':',1)[1].strip()
    except Exception:
        pass
    return '?'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ip', default='192.168.12.1')
    a = ap.parse_args()

    print(f'[①] 本机 WiFi: {wifi_ssid()!r}')
    prox = {k: v for k, v in os.environ.items() if 'proxy' in k.lower()}
    print(f'[②] 代理环境变量: {prox if prox else "无"}')
    if prox: print('     ⚠ 有代理变量,建议清除后重试')

    # ping
    r = subprocess.run(['ping','-n','2','-w','1500',a.ip], capture_output=True)
    ok = b'TTL=' in r.stdout
    print(f'[③] ping {a.ip}: {"通" if ok else "不通(不一定是问题,机器人可能禁 ICMP)"}')

    # TCP
    s = socket.socket(); s.settimeout(4)
    try:
        s.connect((a.ip, 9991)); print(f'[④] TCP 9991: 握手成功')
        tcp_ok = True
    except OSError as e:
        print(f'[④] TCP 9991: 失败({type(e).__name__})→ 网络层不通,检查 WiFi/网段'); return
    finally:
        s.close()

    # HTTP con_notify(禁代理,15s)
    req = urllib.request.Request(f'http://{a.ip}:9991/con_notify', method='POST')
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        body = resp.read(200)
        print(f'[⑤] POST /con_notify: HTTP {resp.status}, 应答 {len(body)}B')
        print(f'    应答开头: {body[:80]!r}')
        if resp.status == 200 and len(body) > 50:
            print('\n[✓] 信令正常 → 直接跑 one_click_rce.py --ip ' + a.ip)
        else:
            print('\n[!] 有应答但异常,把上面输出发给分析')
    except urllib.error.HTTPError as e:
        print(f'[⑤] POST /con_notify: HTTP {e.code} {e.reason}')
        print('    服务活着但拒绝了——把此输出发给分析')
    except Exception as e:
        print(f'[⑤] POST /con_notify: {type(e).__name__}({e})')
        print('''
[✗] TCP 通但信令不应答 —— 即 8-30 卡住的症状。按序排查:
    1. 其他设备全部断开机器人 WiFi(手机杀掉宇树 App + 忘记网络)→ 只留本机 → 重跑本脚本
       (信令疑似单会话:App/其他客户端占用时,后来的 con_notify 全部挂起)
    2. 仍不通 → 重启机器人,开机后单设备连接再试(清僵尸会话)
    3. 仍不通 → 切 STA 模式(App 配网连路由器,保底路径,8-21/8-24 双实证)''')

if __name__ == '__main__':
    main()
