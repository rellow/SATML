import base64, json, sys
b = sys.argv[1]
# kD: urlsafe decode
s = b.replace("-","+").replace("_","/")
s += "="*(-len(s)%4)
inner = base64.b64decode(s).decode()
print("=== notify JSON ===")
print(inner[:200])
try:
    obj = json.loads(inner)
    print("\nkeys:", list(obj.keys()))
    print("data2 =", obj.get("data2"))
    d1 = obj["data1"]
    print("data1 len =", len(d1))
    print("data1[:40] =", d1[:40])
    print("data1[-40:] =", d1[-40:])
    # structure: drop first 10, split last 10
    m = d1[10:]
    E = m[-10:]; pub = m[:-10]
    print("\n--> 前缀10:", repr(d1[:10]))
    print("--> 后缀E(10):", repr(E), "  ML(E)映射=", ''.join(str(ord(c)-65) for i,c in enumerate(E) if (i+1)%2==0))
    print("--> pub部分(len=%d):" % len(pub), pub[:60], "...")
except Exception as e:
    print("parse err", e)
