# -*- coding: utf-8 -*-
# scan_online_sample.py — 小范围 SN 在线状态抽样（只读，不交互）
# 边界：仅 im/isOnline 状态查询；不发消息、不取凭据、不拉机主信息。
import hashlib, time, urllib3, requests, json, os, sys
urllib3.disable_warnings()

CENTER = 10000227          # 自有 SN 数字段
SPAN = 50                  # 前后各 50 → 共 101 个候选
PREFIX = '<其他机器人设备_01>'
BATCH = 20

def im_sig(t):
    return hashlib.md5(('IM$SeCrET' + t).encode()).hexdigest()

def query(accs):
    t = str(int(time.time() * 1000))
    r = requests.get('https://apis.ubtrobot.com/im/isOnline',
                     params={'signature': im_sig(t), 'time': t,
                             'userId': 'sigvoid_probe_nonexist_9x7z',
                             'accounts': ','.join(accs), 'channel': 'MINIEDUCN'},
                     timeout=20, verify=False)
    return r.json()

candidates = [f'{PREFIX}{CENTER + d}' for d in range(-SPAN, SPAN + 1)]
hits, errors = [], []
print(f'[*] 抽样范围 {candidates[0]} .. {candidates[-1]}  共 {len(candidates)} 个 SN（{BATCH}/批）')
for i in range(0, len(candidates), BATCH):
    batch = candidates[i:i + BATCH]
    j = query(batch)
    if j.get('returnCode') != '0':
        errors.append((i, j.get('returnMsg')))
        continue
    for sn, st in j['returnMap'].items():
        if st:
            hits.append((sn, st))
    time.sleep(0.4)   # 限速，礼貌探测

print(f'[*] 探测完成：{len(candidates)} 个候选中发现 {len(hits)} 台真实设备：')
for sn, st in hits:
    tag = ' (本团队自有)' if sn.endswith(str(CENTER)) else ''
    print(f'    {sn}  ->  {st}{tag}')
if errors:
    print('[i] 批次错误:', errors)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   f'online_sample_scan_{time.strftime("%Y%m%d_%H%M%S")}.log')
with open(out, 'w', encoding='utf-8') as f:
    f.write(f'小范围 SN 在线状态抽样（只读）· {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
    f.write(f'范围 {candidates[0]}..{candidates[-1]} 共{len(candidates)}个\n\n')
    for sn, st in hits:
        tag = ' (本团队自有)' if sn.endswith(str(CENTER)) else ''
        f.write(f'{sn}  {st}{tag}\n')
print('[+]', out)
