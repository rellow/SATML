// im_send_test.js — 陌生账号 → 机器人 C2C 投递测试（验证腾讯 IM 关系链校验是否开启）
// 用法: node im_send_test.js <fromUserId> <toUserId> [文本]
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

(async () => {
  const [fromId, toId] = [process.argv[2], process.argv[3]];
  const text = process.argv[4] || 'sigvoid_probe_ping';
  if (!fromId || !toId) { console.error('usage: node im_send_test.js <from> <to> [text]'); process.exit(1); }

  const tim = TIM.create({ SDKAppID: SDKAPPID });
  tim.setLogLevel(0);
  let readyResolve;
  const ready = new Promise(r => readyResolve = r);
  tim.on(TIM.EVENT.SDK_READY, () => readyResolve());
  tim.on(TIM.EVENT.KICKED_OUT, e => console.log('[!] KICKED_OUT:', JSON.stringify(e.data)));

  const userSig = await mintUserSig(fromId);
  await tim.login({ userID: <账户_01>, userSig });
  console.log('[+] 已登录为', fromId);
  await Promise.race([ready, sleep(10000)]);

  const msg = tim.createTextMessage({ to: toId, conversationType: TIM.TYPES.CONV_C2C, payload: { text } });
  try {
    const r = await tim.sendMessage(msg);
    console.log('[+] 发送成功! Tencent 已接受并投递 C2C:', JSON.stringify({
      to: r.data.message.to, ID: r.data.message.ID, status: r.data.message.status,
    }));
    console.log('[!] 结论: 该 SDKAppID 未开启关系链校验，任意账号可 C2C 投递到机器人');
  } catch (e) {
    console.log('[-] 发送被拒绝:', e.code, e.message);
    console.log('[i] 结论: 可能存在关系链校验（需绑定关系才能投递）');
  }
  await sleep(2000);
  try { await tim.logout(); } catch (e) {}
  process.exit(0);
})().catch(e => { console.error('[-] 失败:', e.code || '', e.message); process.exit(2); });
