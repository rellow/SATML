---
name: unitree-r1-firmware-rce-research
description: "宇树 R1 v1.4.2 固件 RCE 挖掘项目 — 已完成 11 路静态分析,报告与工具位置、核心结论、待验证项"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7f5a177d-113c-411e-8f34-60d759ff6604
  modified: 2026-09-01T00:37:14.252Z
---

宇树 R1 机器人固件(v1.4.2, aarch64 rootfs,位于 `C:\zyh\work\宇树固件\real_unitree_r1_1.4.2`)授权安全审计,2026-07-31 完成 11 路静态分析(5 路初始 + 6 路闭环)。

**核心产物**:完整报告 `RCE_挖掘报告.md`(固件根目录);自研工具 `tools/`(strings.py、disasm.py capstone 反汇编、fmx_decrypt.py FMX 加解密器)。

**确认级发现**:RCE-1 vui_service audio_detect.py TCP 8888 硬编码 unitree123(官方工厂诊断,2.2.0.19 后引入);RCE-4 BLE 未配对 + 固件共享 AES 密钥(etc/key/aes_key.bin)→ 配网劫持 → 8888 = 零秘密近场 root;OTA-1 MQTT 消息验签是死代码 + ExecuteOTACmd system() 注入;RCE-2/RCE-3 WebRTC/DDS → bashrunner 白名单脚本(物理破坏级,注入不可升级为任意命令)。

**关键架构事实**:FMX=File MiXer(Blowfish,种子内嵌,可任意伪造);DDS 仅绑 eth0、仅 Authentication、私钥 etc/ds/ 随机群分发;ota-update/deb-update/chrony-update 无条件执行 /unitree/var/data/ 下脚本;DDS→master_service Save 链不存在(MSClient 只转发 Start/Stop);ServiceSwitch force:true 可绕过 ProtectedService(DoS);config key 有白名单不能穿越。

**用户背景**:有 WebRTC/xfkTon 方向研究积累(知道信令层有共享 GCM key),指出过固件来源可能是"后门状态"(已考证 audio_detect.py 高概率官方)。

**2026-08-03 动态验证补充**:RTSP 8551 实测在线零认证(OPTIONS 200,DESCRIBE 503 因 eth0 组播流源离线);9991 信令在线;8888 不常驻。用户持有 SSH root(端口 2234,密码 sigvoid —— 与固件内实验室 WiFi 密码 sigvoid1234 同源,密码复用),但当前机器人 wlan0(192.168.8.117)未开放 2234。WebView DevTools 可调(webview_devtools_remote),借 App 数据通道成功发送 rt/api/voice api 1001 TTS(未经 LLM 直发文本)。知识库机制终审:R1 上进云端存储但不注入 prompt(模型自证+事实召回失败),G1 机型本地 prompt 原文拼接路径存在(知识投毒对 G1 直接成立);云端四层防护(输入/输出过滤+指令层级+知识不注入)合格。已记录但暂停:SSH 打补丁让 R1 本地加载知识库的 PoC。

**2026-08-03 SSH 持久化部署完成**:sysmond(改名 sshd 躲 pkill)监听 22022,root/sigvoid1234,登录已验证(paramiko uid=0);配置 /unitree/etc/sysmond/sshd_config(含 SFTP 子系统);master_service 服务定义已建;**FMX init 启动列表已写入 sysmond**(MD5 校验一致,原件备份 init.bak)→ 开机自启。工具:tools/fmx_encrypt.py(加密器,roundtrip 验证)、tools/deploy_ssh.py、bd_exec.py。net-init 会 pkill sshd(此前 2234 后门死因),sysmond 改名规避。8888 已关闭,22022 保留为维护通道。注意:重启后需验证 master_service 是否按 init 拉起 sysmond。

**2026-08-03 audio_detect 二次验证**:手柄 L1+L2+Start 触发后 8888 复现(root id 回读),已按用户要求 pkill 关闭并确认端口 CLOSED。后门"失效"根因=一次性触发(FSM 写回 0x0b),进程死即消失需重新触发。无实体手柄远程触发路径排除(rt/wirelesscontroller 仅 eth0,WebRTC 白名单不转发)。复现文档: C:\zyh\work\漏洞整理\unitree_R1\R1_audio_detect网络rce\。用户持有该漏洞的完整利用脚本(r1_audio_detect_exploit.py)。

**2026-08-06 TURN 中继滥用确认(中危)**:turn.unitree.com:5349(Coturn 4.5.1.1)对凭据持有者放行任意 UDP 目标中继,无白名单。凭据 webrtc/account 领取(账号 token+SN,sk=RSA(SN)可算),机器人 webrtc_bridge.LOG 明文记录。影响:带宽盗用/DDoS 反射/攻击源伪装。漏洞包: C:\zyh\work\漏洞整理\unitree_R1\TURN中继滥用\。另:用户账号(uid 143838)下 R1+Go2 的 webrtc/connect 恒 500、online/status 恒 false —— 云端直连通道账号级损坏(wechat/account 中继通道正常),需宇树后台重置;设备 id 65272 重绑不重建。App 显示"不在线"根因 = 云端状态判定,非网络。热点/AP 模式因硬编码 192.168.12.1 绕过云端状态故能连。

**2026-08-05 云端复现轮**:①AWS IAM **root** 密钥有效(账户 380729983040,arn:...:root,固件 chat_go/tests/polly_tts.py)Critical;②DashScope sk-947ec... 有效(200);③博查 sk-347d... 有效;④gpt-proxy 同 SN 并行会话不互踢(无会话抢占 DoS,反利攻击者隐蔽);⑤KMS 10.0.9.205 外网不可达;⑥App robot-api 流量绕过系统代理(疑 NO_PROXY 客户端),Burp 无法被动拦截;RDelivery 组件证书校验正常(SSLHandshake 拒绝 Burp CA),hostnameVerifier恒真仅 RetrofitFactory 单点,真实利用需网络层 MitM。跨产品固件:公开源(Bin4ry README)已下 Go2/G1 包验证,OSS bucket 同样无鉴权;REST 归属校验挡住跨账号 SN(无权限),bind 需 BLE 证明。

**2026-08-05 OTA 固件获取链闭环(Critical)**:MQTT 令牌可离线伪造(token="<访问令牌_01>"+md5("unitree-"+SN+"-"+nonce)+"|"+nonce,client_id 必须=SN,生产 rc=0;ACL: subscribe cmd 允许/msg 0x80 拒/publish msg 接受);伪报 reportVersion(msg/<SN>,schema 从 ota_report_utils.LOG 提取: cmd/modules[]/msgId/package{version}/sn)实测把云端版本记录 1.4.2 改写为 1.0.0;curl_cffi(chrome) 绕 WAF → v1/firmware/package/upgrade/list?sn= 返回 firmwareId 9212 + md5 + CDN 路径;firmware-cdn 无签名直下 870MB 包(MD5 一致);UniTEABag 可解。已恢复版本记录。漏洞包+完整复现文档: C:\zyh\work\漏洞整理\unitree_R1\OTA固件远程获取链\(含 870MB 实下载包)。tools/ 已清理归档(核心工具+README 索引,_archive/ 存一次性脚本)。注意: broker 发布 ACL 挡住 cmd/<SN> 方向(远程 OTA-RCE 推包被断,厂商加分项)。SSH sysmond 自启失败原因=/run/sshd 属主(已修 deb_update.sh);mscli 不加载自定义服务定义。

**2026-08-04 云端探测收官**:gpt-proxy 命令面仅 6 cmd(40+ 候选枚举全 KeyError);伪造 SN 可连接(计费门拦截)→ 真实 SN 余额盗刷 IDOR;伪造 SN 可写知识库;traceback 泄露。REST 面合格(token+归属校验,第三方 SN 返回"无权限"),仅 SN 预言机(设备不存在 vs 无权限)。567=行为封禁,换出口 IP(手机 curl)可绕。unistore internal/ 端点公网可达(500)。SN 结构 E39N{子型号}Q{7位base36} 不可遍历;泄露面=组播/BLE/标签/固件日志(含 3 台测试机 SN)。WSS 漏洞包已归档: C:\zyh\work\漏洞整理\unitree_R1\云端WSS_gpt-proxy_SN即凭证\。

**漏洞包**:App FHTTP 端口抢占→JSBridge 全接管已整理成证据包 `C:\zyh\work\宇树固件\vuln_reports\unitree_app_fhttp_hijack\`(报告+PoC+日志+代码证据);已动态实证页面接管/26桥可用/Token附带机制,最后一帧真实 token 抓取未做(需 App 连机器人触发 RTC_Start)。测试后已恢复手机状态(adb reverse 移除,App 重启)。

**2026-08-03 agent RCE 终审**:机器人侧 chat_go 无任何 RCE 路径(所有 sink fail-closed/固定路径/钉死 host);唯一候选 ZMQ 板载 LLM 通道明文无认证(行为劫持级)。App JSBridge:Critical 确认 = FHTTP 17979 端口抢占→恶意 App 全桥接管+token/key 白送;Critical 候选 = webSendHttpRequest 任意 @Url + contains 子串匹配 Token 外带;High = webSendNavFile 路径遍历、全局 WebView 无 URL 过滤;Medium = FHTTP 绑 0.0.0.0 无鉴权(LAN 可读 3D 地图)。

**2026-08-21 CHAIN-D(chat_go)确认 CRITICAL**:`rt/api/gpt/request` api 1006(上传知识库)uid 零校验 → `save_knowledge` 字符串拼接 `{knowledge_dir}/{uid}.md`(knowledge_dir=/unitree/robot/config/chat_go/knowledge,4 跳 `../` 穿越)→ 任意内容写任意 *.md 路径 as root(无内容解析门,比 CHAIN-E 的 YAML polyglot 更简单,纯 shell 直写);api 1008 = 任意 *.md 删除。链:uid=`../../../../module/bashrunner/command_execution/pwn` → 重启 bashrunner(listdir 无扩展名过滤)→ `sh pwn.md` root RCE。远程可达:webrtc_bridge.LOG.1:731/760 注册该 topic 读写。verbatim 函数离线四步实跑全过。报告:`AUD-chatgo-knowledge-write-traversal.md`(固件根目录,与三份 AUD-arm 同级)。副作用:WSS 重连把穿越 uid 条目上传云端知识库(robot.py:515-521)。chat_go 其余 sink 排除:my_eval=float 转换、shell_manger 只拼 int、dual_ssl 证书路径不可控。待办:真机实弹 CHAIN-D/CHAIN-E(工具 tools/r1_webrtc.py chain、chain_e.py 已备,payload poly_b64.txt)。

**2026-08-21 漏洞包已归档**:CHAIN-D → `C:\zyh\work\漏洞整理\unitree_R1\chat_go知识库任意文件写RCE\`,CHAIN-E → `arm服务rename穿越RCE链\`(各含 README/漏洞报告.md/poc 直连 WebRTC 全链 PoC(默认无害 payload、--clean 清理)/evidence 离线+真机日志/docs 英文 AUD 审查)。PoC 密钥=共享 AES 85b3f0b12c51dfb5815df26000107d6a。

**2026-09-01 云端全绿复测+OTA一键链**:五包当日全过——AWS(root)/DashScope博查(200)/WSS+知识库写入(差异证明)/TURN(重领凭据 wyXccZS0...,Allocate ✓)/OTA。**OTA 一键脚本**:`OTA固件远程获取链/poc/ota_one_click.py`(复用原 PoC 函数;自动记录原版本→MQTT伪报→查清单→CDN首1MB Range验证→**自动恢复+复核**;--full 全量870MB;token 自动读 b2dog_tokens.txt 最新)。实测:云端当前记录=1.0.0(8/5恢复值,机器人长期离线未上报),伪报1.0.0→清单9212/1.4.2/md5+CDN 206 ✓;--fake-version 0.9.9 演示记录改写但清单空(版本不匹配升级活动)。**下午"MQTT不可达"虚惊=我测试漏 tls_set()**(固件 mqtts://),教训:临时验证脚本先对照当年闭环 PoC 的连接参数。近场四包昨检:默认IP全12.1/audio_detect 补8.118→12.1/八脚本语法过/零时效凭据。

**2026-08-30 云端知识库未授权写包已归档**:`漏洞整理\unitree_R1\云端知识库未授权写入\`(High)。核心证据=**差异证明**:set_user_knowledge 静默接受 vs 未知 cmd 立即 KeyError traceback(agent.py:922 callbacks 分发表)→handler 存在且执行无错;持久化实证=testsec01(7/31 写)留存至今+delete 500 无法删(api.py:848 traceback)。消费面:R1 被 prompt 防护挡(数据污染),**G1 g1_pub_prompt.py:58 原文拼 prompt=直接投毒(代码级,无设备)**。用户已理清三曾混淆:写入层(通)/R1 生效(从未通,7/31 testsec01 是误判)/本地生效(是我们 8/3 自装的 robot.py 补丁,8/29 已拆)。

**2026-08-30 TURN 复测闭环(免机器人)**:webrtc/account 云端取凭据全流程打通——①system/pubKey GET 在 PC 直连可用(无鉴权不拦)②webrtc/account POST 被 WAF 567 须走手机热点出口③**body 是 form 编码非 JSON**(库 requests data=dict 行为)④返回 AES-ECB 加密,解出 {user:unix时间戳:SN, passwd, realm}。凭据数小时时效可无限重领;手机在机器人 AP 内无公网上行,须先切回公网 WiFi。证据 evidence/turn_abuse_run_2026-08-30.log,漏洞报告已补免机器人路径。坑:Windows 写 sh 必须 LF。

**2026-08-30 共享密钥体系包已归档(根因级)**:`漏洞整理\unitree_R1\共享密钥体系失效_aes_key\`(Critical 9.1)。核心:etc/key/aes_key.bin 一钥三用(BLE 配网 GCM/WebRTC 数据通道/云端 dev.key)三方互证(bindlist 补齐),全机群共享无法吊销;同体系并列实例=FMX Blowfish 内嵌种子(独立失效,非此 key——已纠正早前材料文档笔误)+App 信令 GCM key e85682bd+DDS 私钥。凭证类四包齐:AWS root(Crit)/DashScope博查(High)/共享密钥(Crit)/硬编码凭证全线泄露(旧总包)。

**2026-08-30 DashScope/博查包已归档+复测有效**:`漏洞整理\unitree_R1\云端API凭证泄露_DashScope博查\`。qwen_tts.py:100 DashScope(sk-947ec...)+ function_prompt.py:10 博查(sk-347dbb...),2026-08-30 复测双 HTTP 200(最小计费纪律:每 key 1 次最小调用即止)。同源根因=生产固件携带云端凭证(AWS root 包同批)。用户已明确边界:AWS 账户内不执行命令(只读 GetCallerIdentity 即止),理由=凭证有效≠使用授权+负责任披露立场。

**2026-08-30 AWS root 包已归档+复测有效**:`漏洞整理\unitree_R1\AWS_root凭证泄露\`(README/漏洞报告/poc verify_aws_key.py 只读 GetCallerIdentity/evidence 复测日志)。凭证在 `module/chat_go/tests/polly_tts.py:6-7`(完整对;生产版 polly_tts.py:10 只有 AKIA,secret 走运行时下发=另有云端下发面)。**arn:aws:iam::380729983040:root,2026-08-05 首证→08-30 复测仍有效 ≥25 天未轮换**。测试纪律:只读验证即止(不列举资源/不创建对象/不产生费用)。

**2026-08-30 R1 复现材料已备齐(App 提取)**:归档 `漏洞整理\unitree_R1\R1复现材料_20260830.md`(+b2dog_tokens.txt/r1_bindlist.json)。要点:①SN E39N1000Q72DJE8G 四方一致;②**云端 dev.key=固件 aes_key=85b3f0b1...(三方互证,共享 key 实锤)**;③uid143838 新 access_token 有效至 09-29;④r1_cloud.py 签名配方仍有效但**必须经手机出口**(PC 直连 567);⑤提取通道:Pixel(9B141FFBA0037Z)**adb root**(userdebug)直拉 MMKV(Git Bash 双斜杠路径坑);WebView DevTools 找当前 pid socket,B2App@17979(doggo2 进程承载 R1 页);android.webSendHttpRequest({requestId,url,method,data,timeout})回包走 appSendHttpResponse=**裸透传无鉴权**(13004);⑥App 切后台=freezer 冻结,DevTools 全挂需 monkey 拉前台;⑦doggo2 里另有账号 156274(空设备,Go2 归别人管)。开工还差:R1 上电+同网段+**关本机 TUN 代理**(198.18.0.1 假打通所有端口)。

**2026-08-28 可达性复核与降噪(未闭环二轮)**:核心结构事实——**R1 远程 DDS 攻击面=桥 writer 白名单 22 条 topic**(从 webrtc_bridge.LOG 分方向提取;rt/api/{15 服务}/request+arm_service_inbound+log_system_inbound+videohub/inner+rtc/state+rtc_status+servicestateactivate+wirelesscontroller);**rt/lf/* 全家(bmsstate/lowstate/sportmodestate 等)subscriber-only 不可注入**(桥二进制 write_* 函数族无 lf/bms 写函数,soc 仅在 subscriber/lf_bmsstate.h;write_wireless_controller 存在且 cjson 解析 keys 键)。**降噪裁决**:🔻batguard BMS 瘫倒 WiFi 远程不可达(内部网限定);🔻mqtt answer 注入当前不可达(ACL);🔻motionsw form RCE 写入面封闭降 HIGH(触发可达);🔻aisport log_path 内容=日志文本,"复合 bashrunner"降级(路径任意/内容受限);⚠espeak 运行时引擎待证(lic_active=1 走在线?);⚠msvc .md 加载跳保持弱跳(falsifier size:28);⚠kvsmem PoC 勘误:9991 是 con_notify(公钥交换→AES)非裸 JSON。✅确认可达:audiodetect-02/03(keys 映射实证)、basicsvc(basic_demarcate/request 在白名单)、config-kv、aisport damping(.yaml 匹配)、audiohub/llmapi/robottype/vui-1003、kvsmem(信令层)、btgatt。**已闭环包勘误**:AUD-arm-unauth-rpc 的"四门可 spoof"加注"仅 eth0-DDS 场景"(主结论不受影响,CHAIN-E 不依赖 spoof)。文档:未闭环/可达性复核与降噪.md。

**2026-08-28 未闭环包已归档**:`漏洞整理\unitree_R1\未闭环\`(10 包/29 份 AUD 文档/15 个 PoC,全部语法校验过;只收"我们未发现+复核成立"的;msvc-fmx 因重叠已剔除)。总索引 未闭环/README.md 含包索引(含 PoC 清单)+与已闭环包对照表+推翻清单。每包 README+漏洞报告.md(中文摘要+裁决)+docs/(原始 AUD)+poc/。PoC 设计原则:崩溃/DoS 级优先(不武器化控制流)、危险物理面默认只读模式(batguard --fire 才注入)、msvc 只装弹不开火;高危真机验证优先级=msvc 加载(size:28 falsifier)→audiodetect-02 任意读(8888 武装+读 /etc/shadow)→basicsvc PARTIAL 一发定生死。

**2026-08-28 外部情报包交叉验证完成**(`r1-待验证(1).zip`,46 份 AUD 报告,固件根目录已解压至 C:\tmp\r1_intel):6 路指令级复核 → 42 成立/1 部分/3 推翻。**净增量**:①kvsmem 内存破坏 ×6(DCEP label 堆溢出、SDP 属性名**预认证**堆溢出、offer 栈溢出、offertoken/reqid 堆溢出、NACK/TWCC OOB 读可报 AWS KVS 上游)——同入口更多弹药;②audio_detect-02 **任意文件读**(audio_detect.py:60-75 path 直取,8888 后门内,我们此前漏掉)+ 03 keys=38 经 rt/wirelesscontroller **远程武装** 8888;③msvc-unauth-rpc-socket + service-cmd-file-rce=**第二 root 终端**(明文 service JSON 覆写→开机 root 开火);④corr-.md-persistence(CHAIN-D 落 service/ 目录持久化);⑤motionsw form-cmd=**第三 root 终端**;⑥ai_sport log_path=**无后缀任意路径 root 写**(打破"写必带后缀"旧约束)+ damping 堆溢出 + FMX 失败明文直通;⑦chatgo-llmapi-redirect(1010 持久劫持 LLM 端点);⑧P1 物理 4 链成立(瘫倒闩锁/校准销毁/e-stop 重绑/autotest 武装)。**推翻**:logsys-crash、motionsw-rpc-crash(Thread::Wrap 自带两层 catch 的系统性误读,凡"未捕获异常→terminate"机制都需重审);basicsvc-crash PARTIAL 待真机。**我方更正**:OTA .upk 整块跳过 RSA 验签+空 sign 单独短路(OTA-4/5 原结论失效);OTA tar 解包无 .. 过滤;ResetPassword 不可注入(插值为 crypt 串)。**我们更准**:bashrunner=白名单非任意命令;ssid-bss 溢出与我们的分片重组是同一 bug,decrypt 栈溢出才是第二个独立 bug。

**2026-08-24 日志清理 + 终审**:全日志区漏洞痕迹清除(webrtc_bridge 369 条/bt 103/robot_state 197/chat_go 235 等,复扫零命中);终轮自抹除技巧=截断 payload 的执行抹掉其自身 1006 记录,残留仅 1 条知识删除+4 次服务开关(运维形态)。终审全维度排查通过:服务定义 27 项与固件全同、cron/rc/进程/var.data 自启区干净、监听仅 8551/9991(+systemd-resolved 本地 53)。**遗留观察项(用户选择保留)**:`/root/.ssh/authorized_keys` 有陌生个人 key `<个人邮箱_01>`(ssh-ed25519 …Jf+n),sshd_config PermitRootLogin yes 但 sshd 未运行(22 未监听)=休眠 root 通道,疑前手/来源方,用户已知悉并选择暂保留。注意:本机固件镜像只含 /unitree,rootfs 层(/root,/etc/ssh)无本地基线可比对。

**2026-08-24 机器人全量恢复出厂干净态**:①测试残留全清(知识库 poc1/诊断脚本/marker,bashrunner 15 个 .sh md5 与固件全同,chat_go 配置 md5 全同);②**sysmond SSH 后门已应用户要求拆除**(22022 已关,文件/init/deb_update.sh 均恢复固件 md5——注意:SSH 维护通道不复存在,后续真机操作只能走 WebRTC);③robot.py KNOWLEDGE-PATCH 已用 .bak 恢复(md5=固件),chat_go 重启生效;④运行时正常差异无需处理(ds 证书每机随机/vui 设置/RemoteConnectionEnabled=OFF/led/logconf/wifi)。审计方法:find -newermt 测试窗口 + 固件 md5 比对,63 个变动文件全部定性。**遗留(云端,本地管不到)**:云端知识库副本 poc1+testsec01 需 App/厂商清理。教训:bashrunner bashtext 拼行无换行,解析 md5sum 输出要按 "hash␣␣" 切分。

**2026-08-24 BLE 包定稿**:用户明确——**保留"网络+BLE"组合的一键脚本(one_click_rce.py,已实测 PASS),不要"纯网络"脚本**;纯 BLE 盲打(rce_shell_blind)同时保留为零辅助通道模式。包内:one_click_rce/rce_shell_blind/ble_l_hijack/ble_leak_probe + 复现指南三路线。**实战要点**:btgatt SIGABRT 后高负载窗口内 bashrunner 触发持续丢响应(疑 Deadline QoS 1ms 丢样本),重连 WebRTC+重种重启即恢复(one_click 内置"重试→重连→重种"三级恢复);gpt 1008 删除在高负载窗口也会丢,清理必须带验证循环。注入本身 5/5 全部命中,base byte3 实测 7b/7d/67/90/57/76/80 均∈[0x40,0xa0],盲打区间假设充分互证。

**2026-08-24 R1 BLE 溢出真机闭环(uid=0)**:BLE 扫描得 `R1_05439`(14:0A:02:F0:B1:75)→ 0x0B/0x0C 会话(固件 key)→ 42 片 Write Command(plen=58)零丢片 → dispatcher → system() uid=0(root) marker 读回验证,已清理复原(leakbase.md/marker 删除,白名单刷新验证,btgatt 由 master_service 自动恢复)。base=0x557b040000(经 CHAIN-D 读 maps 脚手架;byte3=0x7b ∈ 盲打区间互证)。证据 evidence/live_run_2026-08-24.log,报告状态已改"已真机闭环"。**实战要点**:白名单内脚本可用 gpt 1006 覆写内容免重启(名字已在 listdir 快照,内容执行时才读)——CHAIN-D 二次利用免重启。至此 R1 三条 RCE 链(CHAIN-D/CHAIN-E/BLE)全部真机闭环。

**2026-08-24 R1 btgatt-server BLE 溢出包已归档**:`漏洞整理\unitree_R1\R1蓝牙btgatt-server分片重组溢出到RCE\`(**R1 独立成篇**:不提 GO2、无 SSH 辅助——应用户要求重写;纯 BLE 盲打为主路径)。核心事实:R1 与 GO2 的 btgatt-server 全 section MD5 逐字节相同(同一构建)→ 全部偏移(wf_setting 1008B/L+0x830/dispatcher 0x6c68/system@plt 0x3580/free@plt 0x38d0)原样成立,且已在 R1 本机二进制逐项核验(DWARF 标识符+dispatcher 反汇编+重定位表,证据 evidence/r1_binary_verification_2026-08-24.log);R1 二进制含完整 DWARF。差异仅:BLE key=85b3f0b1...(=WebRTC/FMX 同一把)、广播名前缀 R1_。脚本:ble_l_hijack.py(pc/sys/rce 三模式,纯 BLE 无回填)、rce_shell_blind.py(--lhost 必填,~24K 枚举)、ble_leak_probe.py,语法过,**R1 端到端待打**。文件读助盲打结论:root 读 /proc/pid/maps 可坍缩 24K 盲打,但 R1 网络侧文件读⇒已有 CHAIN-D root,纯 BLE 盲打下界 16bit 不变。

**2026-08-24 任意文件读排查收官**(Python 服务面):无纯血任意读;任意读=写链副产品(bashrunner 回传 stdout,已实证)。新发现:①log_system 日志下载服务无鉴权且桥已注册(rt/log_system_inbound/outbound),配置内含 webrtc_bridge.LOG(TURN 凭据明文)/sta.log(WiFi 凭据)等高价值文件,协议=req_id 触发+分片 ack,**探针已备好待机器人开机实测**;②audio_hub api 1004 __delete_audio_file 零校验(不查 sqlite,对比 1002 播放有校验)→ 任意 *.wav 删除。排除:arm upload 卡死单目录、bashrunner 采集脚本无 $1、audio 上传 UUID 重命名、7108 读执行不回传。log_system 二进制:rt/log_system/MsgBody,CollectAndPack(无参,打全量),请求键仅 name/code/data/type,paths 来自配置不可控。

**2026-08-21 双链真机打穿(均 uid=0(root) 回显,已清理复原)**:R1 v1.4.2 @ 192.168.8.117,直连 WebRTC 数据通道(无 App)。CHAIN-D 四跳全 code:0;CHAIN-E 六跳全 code:0(filedrop 1002/1003 outbound 回包确认→rename 7109→重启→触发)。清理:1008/7112 删除投放文件+重启 bashrunner,复触发无响应验证白名单已恢复。**两个实战要点**(PoC 已内置):①R1 桥 r1_kvsrtc 只完成 datachannel 组件 ICE,必须屏蔽 addTransceiver 发 datachannel-only offer,否则 PC 永远 connecting;②String_ 型 topic(rt/arm_service_inbound)须发 type=msg、data 直接是业务 JSON,req 型包装桥不投递(报错 7403=动作未注册即此症状);filedrop 回包在 rt/arm_service_outbound 需订阅。

**待办**(旧):真机验证(rt/api/sport 7101 两跳全集切换、7105 duration 上限、basic_demarcate powerswitch api_id 枚举);ota_boxed MQTT set_verify 确认决定 OTA-1 能否被 MitM 引爆。

**2026-07-31 语音/动作面增补**:语音面 RCE 完整排除(唯一原语知识库 uid 穿越写钉死 .md 后缀无消费者);任意动作控制确认成立 —— rt/api/sport 7101 SetFsmId 两跳(Stance 枢纽)全集切换 + 7105 SetVelocity API 层零钳制;r1_arm file_sync 上传 yaml(q 无校验)→ 7108 播放 = 自定义双臂轨迹;basic_demarcate 远程 powerswitch + 关节/IMU 零偏写。App 侧提取信令共享 GCM key e85682bd16549b008e04a6682bb3ebe3(BLE v3 + :9991 + xfkTon 三处同一把)。App DB 交叉确认 BLE AES key 全机群共享。8888 后门已动态验证(用户确认)。语音链路:手机讯飞 ASR → DataChannel rt/api/gpt api1001 → chat_go 零过滤。

**2026-07-31 云端实测**(tools/cloud_llm_probe.py):gpt-proxy 认证仅 SN;question 有中英文关键词过滤+人格护栏;**set_user_knowledge 不过滤且按 SN 服务端持久化 → 跨设备投毒链(组播白嫖 SN→云端注入→动作块下发)**;event/delete 类 cmd 使服务端崩溃(api.py:845,traceback 回传);每条消息顶层须带 "api":"r1_pub"。测试残留:SN E39N1000Q72DJE8G 的云端知识库有 testsec01 条目("开始测试"触发无害开场动作),delete 无效,待 App 或厂商清理。
