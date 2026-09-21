# -*- coding: utf-8 -*-
# ota_enum_products.py — OTA 升级 API 产品线枚举（只读元数据，限速）
# 命中即拿到该产品线固件下载信息（packageUrl/md5/size/versionName）。
import hashlib, time, uuid, json, os, sys, urllib3, requests
urllib3.disable_warnings()

APP_ID = '100020114'
APP_KEY = 'b4e01f307c614ded9f7ac59cf9960874'
DEVICE_ID = 'sigvoidprobe0001'
URL = 'https://upgrade.ubtrobot.com/v1/upgrade-rest/version/upgradable'

CANDIDATES = [
    "AlphaMini", "AlphaMini2", "AlphaMiniInEdu",
    "AlphaMiniBE", "AlphaMiniCE", "AlphaMiniDE", "AlphaMiniEDU", "AlphaMiniKor",
    "AlphaMiniPro", "AlphaMini2Edu", "AlphaMini2InEdu", "AlphaMini3",
    "MiniEdu", "Dedu", "Mini", "WK2", "X100",
    "Yanshee", "YanShee", "YansheePro", "YansheeEdu", "Yanshee2", "Yan",
    "Alpha1", "Alpha1S", "Alpha1P", "Alpha1E", "Alpha1X", "Alpha1Pro",
    "Alpha2", "Alpha2Pro", "AlphaEbot", "AlphaEbot2", "Ebot",
    "Jimu", "JimuRobot", "Jimu2", "Meebot", "UKit", "UKit2",
    "Cruzr", "CruzrK", "CruzrMini", "Aimbot", "AimbotADT", "Atris", "ATRIS",
    "Panda", "Youyou", "Lynx",
    "Walker", "WalkerX", "WalkerS", "WalkerS1", "WalkerS2",
    "ZZZNotARealProduct", "",
]
MODULES = 'android,firmware,mcu-app,mcu-boot,AndroidApp'
VERSIONS = ','.join(['0.0.0'] * len(MODULES.split(',')))


def headers():
    ts = str(int(time.time()))
    nonce = uuid.uuid4().hex[:8]
    s = hashlib.md5((ts + APP_KEY + nonce + DEVICE_ID).encode()).hexdigest()
    return {'X-UBT-AppId': APP_ID, 'X-UBT-DeviceId': DEVICE_ID,
            'X-UBT-Sign': f'{s} {ts} {nonce} v2'}


def main():
    hits, empty, errors = [], [], []
    print(f'[*] 共 {len(CANDIDATES)} 个候选 productName，modules={MODULES}')
    for p in CANDIDATES:
        try:
            r = requests.get(URL, headers=headers(),
                             params={'productName': p, 'moduleNames': MODULES, 'versionNames': VERSIONS},
                             timeout=15, verify=False)
            body = r.text
            has_pkg = 'packageUrl' in body and '"packageUrl":""' not in body and '"packageUrl":null' not in body
            if r.status_code == 200 and has_pkg:
                hits.append((p, body))
                print(f'  [HIT] {p!r} -> 有固件!')
            elif r.status_code == 200:
                empty.append(p)
            else:
                errors.append((p, r.status_code, body[:80]))
                print(f'  [?] {p!r} -> HTTP {r.status_code} {body[:80]}')
        except Exception as e:
            errors.append((p, 'EXC', str(e)[:80]))
            print(f'  [ERR] {p!r} {e}')
        time.sleep(0.3)

    print(f'\n[*] 命中 {len(hits)} / 空 {len(empty)} / 异常 {len(errors)}')
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       f'ota_enum_{time.strftime("%Y%m%d_%H%M%S")}.json')
    json.dump({'hits': [{'product': p, 'body': b} for p, b in hits],
               'empty': empty, 'errors': errors},
              open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('[+]', out)
    for p, b in hits:
        try:
            mods = json.loads(b)
            if isinstance(mods, dict):
                mods = mods.get('data', mods.get('result', [mods]))
            for m in (mods if isinstance(mods, list) else [mods]):
                if isinstance(m, dict):
                    print(f'    {p}: module={m.get("moduleName")} ver={m.get("versionName")} '
                          f'url={str(m.get("packageUrl"))[:90]}')
        except Exception:
            print(f'    {p}: {b[:200]}')


if __name__ == '__main__':
    main()
