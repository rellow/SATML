// im_speak_test.js — 陌生账号 WAN 远控实证：cmd 91 让机器人开口说话（TTS）
// 用法: node im_speak_test.js <fromUserId> <robotSN> [英文文本]
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

// 手工组 protobuf（所有字节 <0x80，过 web SDK 的 UTF-8 不损坏）：
// AlphaMessage{ header{cmd=91 ver=1 serial=77} body=CmSpeechEntityRequest{content, language="en"} }
function buildSpeakMsg(text) {
  const enc = [];
  const pushFieldBytes = (field, bytes) => { enc.push((field << 3) | 2, bytes.length, ...bytes); };
  const ascii = s => [...s].map(c => c.charCodeAt(0) & 0x7f);
  const header = [0x08, 91, 0x10, 1, 0x18, 77];           // cmd=91, ver=1, sendSerial=77
  const body = [];
  pushFieldBytes.call(null, 0, []);                        // noop 占位避免误用
  body.length = 0;
  // field1 content, field3 language
  body.push(0x0a, text.length, ...ascii(text));
  body.push(0x1a, 2, 0x65, 0x6e);                          // "en"
  const msg = [0x0a, header.length, ...header, 0x12, body.length, ...body];
  if (msg.some(b => b > 0x7f)) throw new Error('non-ASCII byte in payload');
  return String.fromCharCode(...msg);
}

(async () => {
  const [fromId, robotId] = [process.argv[2], process.argv[3]];
  const text = (process.argv[4] || 'Hello. This message comes from the wide area network.').replace(/[^\x20-\x7e]/g, '');
  if (!fromId || !robotId) { console.error('usage: node im_speak_test.js <from> <robotSN> [text]'); process.exit(1); }

  const tim = TIM.create({ SDKAppID: SDKAPPID });
  tim.setLogLevel(0);
  let readyResolve;
  const ready = new Promise(r => readyResolve = r);
  tim.on(TIM.EVENT.SDK_READY, () => readyResolve());
  tim.on(TIM.EVENT.KICKED_OUT, e => console.log('[!] KICKED_OUT:', JSON.stringify(e.data)));
  let gotReply = false;
  tim.on(TIM.EVENT.MESSAGE_RECEIVED, e => {
    e.data.forEach(m => {
      gotReply = true;
      let p = '';
      try { p = JSON.stringify(m.payload).slice(0, 300); } catch (_) {}
      console.log('[!!!] 机器人回包 from=', m.from, 'type=', m.type, 'payload=', p);
    });
  });

  const userSig = await mintUserSig(fromId);
  await tim.login({ userID: <账户_01>, userSig });
  console.log('[+] 已登录为', fromId);
  await Promise.race([ready, sleep(10000)]);

  const msg = tim.createCustomMessage({
    to: robotId, conversationType: TIM.TYPES.CONV_C2C,
    payload: { data: buildSpeakMsg(text), description: '', extension: '' },
  });
  try {
    const r = await tim.sendMessage(msg);
    console.log('[+] cmd 91(TTS 说话) 已投递, status=', r.data.message.status, ' 文本=', JSON.stringify(text));
  } catch (e) { console.log('[-] 发送失败:', e.code, e.message); process.exit(2); }

  console.log('[*] 等待 25s（机器人应开口说话 + 回包）...');
  await sleep(25000);
  console.log(gotReply ? '[+] WAN 远控实证闭环' : '[i] 未收到回包');
  try { await tim.logout(); } catch (e) {}
  process.exit(0);
})().catch(e => { console.error('[-] 失败:', e.code || '', e.message); process.exit(2); });
