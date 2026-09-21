import socket, struct, json, time, sys
DOG="192.168.8.154"; ME="192.168.8.186"; SN="<GO2设备_01>"
SEND_PORT=10131; RECV_PORT=10134
groups=["231.1.1.1","231.1.1.2","239.255.1.1","239.255.1.2"]
payload=json.dumps({"sn":SN,"key":ME,"name":"unitree_dapengche"}).encode()
# receiver
recv=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
recv.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
try:
    recv.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
except: pass
recv.bind(("0.0.0.0",RECV_PORT))
recv.settimeout(4.0)
# sender
snd=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
snd.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,struct.pack("b",4))
# send to dog unicast + multicast groups
for t in range(3):
    snd.sendto(payload,(DOG,SEND_PORT))
    for g in groups:
        try: snd.sendto(payload,(g,SEND_PORT))
        except Exception as e: print("mcast send err",g,e)
    time.sleep(0.3)
print(f"[+] sent discovery for {SN}, listening :{RECV_PORT} ...")
deadline=time.time()+5
while time.time()<deadline:
    try:
        data,addr=recv.recvfrom(2048)
        print(f"[<<<] from {addr[0]}:{addr[1]} len={len(data)} :: {data[:300]!r}")
    except socket.timeout:
        break
print("[*] done")
