import requests, io, zipfile, csv, hashlib, sys, time, datetime
from concurrent.futures import ThreadPoolExecutor
sym=sys.argv[1]; y0,m0=int(sys.argv[2]),int(sys.argv[3])
months=[]
y,m=y0,m0
while (y,m)<=(2026,6):
    months.append(f"{y}-{m:02d}")
    m+=1
    if m>12: y+=1; m=1
def get(mon):
    url=f"https://data.binance.vision/data/spot/monthly/klines/{sym}/5m/{sym}-5m-{mon}.zip"
    for _ in range(3):
        try:
            r=requests.get(url,timeout=60)
            if r.status_code==200:
                z=zipfile.ZipFile(io.BytesIO(r.content))
                rows=[]
                with z.open(z.namelist()[0]) as f:
                    for ln in io.TextIOWrapper(f):
                        p=ln.strip().split(",")
                        if p[0]=="open_time": continue
                        t=int(p[0]); t = t//1000 if t>10**14 else t
                        rows.append([t,p[1],p[2],p[3],p[4],p[5]])
                return rows
            if r.status_code==404: return []
        except Exception: time.sleep(1)
    return []
allrows=[]
with ThreadPoolExecutor(8) as ex:
    for rr in ex.map(get,months): allrows+=rr
# tail: current month via API
BASES=["https://data-api.binance.vision","https://api.binance.com"]
start=int(datetime.datetime(2026,7,1,tzinfo=datetime.timezone.utc).timestamp()*1000)
while True:
    d=None
    for b in BASES:
        try:
            r=requests.get(b+"/api/v3/klines",params={"symbol":sym,"interval":"5m","limit":1000,"startTime":start},timeout=20)
            if r.status_code==200: d=r.json(); break
        except Exception: pass
    if not d: break
    allrows+=[[k[0],k[1],k[2],k[3],k[4],k[5]] for k in d]
    if len(d)<1000: break
    start=d[-1][0]+1
seen=set(); out=[]
for r in sorted(allrows,key=lambda x:x[0]):
    if r[0] not in seen: seen.add(r[0]); out.append(r)
with open(f"data/{sym}_5m.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["t","o","h","l","c","v"]); w.writerows(out)
h=hashlib.sha256(open(f"data/{sym}_5m.csv","rb").read()).hexdigest()
print(sym,len(out),"sha256",h[:16],flush=True)
