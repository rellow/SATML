# -*- coding: utf-8 -*-
# ota_url_probe.py — HEAD 探测 OTA 命中的固件 URL 是否公网直读
import json, glob, os, urllib3, requests
urllib3.disable_warnings()

base = os.path.dirname(os.path.abspath(__file__))
jf = sorted(glob.glob(os.path.join(base, 'ota_enum_*.json')))[-1]
j = json.load(open(jf, encoding='utf-8'))
print('[*] 数据源:', jf)
urls = []
for h in j['hits']:
    try:
        mods = json.loads(h['body'])
        if isinstance(mods, dict):
            mods = mods.get('data', mods.get('result', [mods]))
        for m in (mods if isinstance(mods, list) else [mods]):
            if isinstance(m, dict) and m.get('packageUrl'):
                urls.append((h['product'], m.get('moduleName'), m.get('versionName'),
                             m['packageUrl'], m.get('packageSize'), m.get('packageMd5')))
    except Exception as e:
        print('parse err', h['product'], e)

results = []
for p, mod, ver, u, size, md5 in urls:
    try:
        r = requests.head(u, timeout=15, verify=False, allow_redirects=True)
        cl = r.headers.get('Content-Length', '?')
        line = f'{p:16} {mod:10} {ver:10} HTTP {r.status_code} CDN-Length={cl}'
        print(line)
        results.append({'product': p, 'module': mod, 'version': ver, 'url': u,
                        'size': size, 'md5': md5, 'http': r.status_code, 'cdn_length': cl})
    except Exception as e:
        print(f'{p:16} {mod:10} ERR {e}')
        results.append({'product': p, 'module': mod, 'version': ver, 'url': u, 'error': str(e)})

out = os.path.join(base, 'ota_firmware_urls_verified.json')
json.dump(results, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('[+]', out)
