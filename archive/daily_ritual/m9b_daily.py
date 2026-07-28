#!/usr/bin/env python3
"""m9b_daily.py — SELF-FETCHING CB11 payload builder (M9b-lite, 2026-07-15).
No stored data needed: fetches ~40 days of Binance 5m klines per coin (public API),
builds today's 8am-ET board (PD/ON/PS/PW/PM x H/L/C/POC), merges walls (r=0.25U),
attaches contact odds (banked C1 gravity lookup), tags (* stepping-POC, V virgin),
Hayden 4H regime (the gated port), cascade scenario states, and emits one CB11
line per coin. Optional: --dtype BTC:normal,ETH:EXPANSION,... (copy from the brief).
v1 honesty: yd (yesterday archetype) = 'na' unless --yd given; uAbs = trailing-14
median window range (engine-U equivalent to ~1%). Hash-log per vendor law: prints
sha256 of each fetched kline set."""
import sys, json, time, hashlib, datetime, urllib.request
import numpy as np, pandas as pd

CRY={"BTC":"BTCUSDT","ETH":"ETHUSDT","SOL":"SOLUSDT","XRP":"XRPUSDT"}
LV=['PDH','PDL','PDC','PDPOC','ONH','ONL','ONC','ONPOC','PSH','PSL','PSC','PSPOC',
    'PWH','PWL','PWC','PWPOC','PMH','PML','PMC','PMPOC']
GRAV=[(0.0,56.4),(0.03,42.8),(0.26,32.2),(0.46,22.2),(1.1,9.8),(3.0,0.5)]
def grav(g): return float(np.interp(min(max(g,0),3.0),[x for x,_ in GRAV],[y for _,y in GRAV]))

def fetch_5m(sym, days=70):  # FIX 2026-07-23: 40d truncated prev-month levels (PML bug); 70d covers full prev calendar month
    end=int(time.time()*1000); start=end-days*86400*1000; rows=[]
    HOSTS=["https://data-api.binance.vision","https://api.binance.com","https://api1.binance.com","https://api-gcp.binance.com"]
    while start<end:
        d=None
        for hb in HOSTS:
            try:
                url=f"{hb}/api/v3/klines?symbol={sym}&interval=5m&startTime={start}&limit=1000"
                with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as r:
                    d=json.loads(r.read()); break
            except Exception: continue
        if d is None: raise RuntimeError("all Binance endpoints failed")
        if not d: break
        rows+=d; start=d[-1][0]+1
        if len(d)<1000: break
    df=pd.DataFrame(rows,columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','ig'])
    for c_ in 'ohlcv': df[c_]=df[c_].astype(float)
    df['dt']=pd.to_datetime(df.t,unit='ms',utc=True)
    print(f"  [{sym}] {len(df)} bars sha256={hashlib.sha256(df[['t','o','h','l','c','v']].to_csv(index=False).encode()).hexdigest()[:16]}",file=sys.stderr)
    return df

def poc(g):
    if not len(g): return np.nan
    lo,hi=g.l.min(),g.h.max()
    if hi<=lo: return float(g.c.iloc[-1])
    bins=np.linspace(lo,hi,101); mid=(g.h+g.l)/2
    ix=np.clip(np.digitize(mid,bins)-1,0,99)
    vv=np.zeros(100)
    for i,v in zip(ix,g.v.values): vv[i]+=v
    return float((bins[vv.argmax()]+bins[vv.argmax()+1])/2)

def wilder_rsi(x,n=14):
    dd=np.diff(x,prepend=x[0]); up=np.where(dd>0,dd,0.); dn=np.where(dd<0,-dd,0.)
    r=np.full(len(x),np.nan)
    if len(x)<n+2: return r
    au,ad=up[1:n+1].mean(),dn[1:n+1].mean(); r[n]=100-100/(1+au/max(ad,1e-12))
    for i in range(n+1,len(x)):
        au=(au*(n-1)+up[i])/n; ad=(ad*(n-1)+dn[i])/n; r[i]=100-100/(1+au/max(ad,1e-12))
    return r

def hayden(df):  # gated port: OHLC4, 4H UTC, 67/33->61/39
    h4=df.set_index('dt').resample('4h').agg({'o':'first','h':'max','l':'min','c':'last'}).dropna()
    x=((h4.o+h4.h+h4.l+h4.c)/4).values; r=wilder_rsi(x); cur=0
    for i in range(1,len(r)):
        r0,r1=r[i-1],r[i]
        if np.isnan(r1): continue
        if r1>67 and (np.isnan(r0) or r0<=67): cur=1
        elif r1<33 and (np.isnan(r0) or r0>=33): cur=2
        elif cur==1 and r1<39 and r0>=39: cur=3
        elif cur==2 and r1>61 and r0<=61: cur=3
    return {1:'Bull',2:'Bear',0:'Chop',3:'Chop'}[cur]

def build(nm,sym,dtype='na',yd='na'):
    df=fetch_5m(sym)
    et=df.dt.dt.tz_convert('America/New_York')
    df['wd']=(et-pd.Timedelta(hours=8)).dt.date
    df['hr']=et.dt.hour
    days=sorted(df.wd.unique())
    today=days[-1]; prev=days[-2]
    # windows
    W={d_:df[df.wd==d_] for d_ in days}
    def hlc(g,pre):
        return {pre+'H':g.h.max(),pre+'L':g.l.min(),pre+'C':g.c.iloc[-1],pre+'POC':poc(g)}
    pd_=hlc(W[prev],'PD')
    on=W[prev][(W[prev].hr>=17)|(W[prev].hr<8)]  # FIX 2026-07-23: completed overnight = prev-wd evening + this morning 00-08 (old fallback dropped the 00-08 leg)
    if not len(on): on=W[prev][W[prev].hr>=17]
    on_=hlc(on,'ON') if len(on) else {k:np.nan for k in ('ONH','ONL','ONC','ONPOC')}
    ps=W[prev][(W[prev].hr>=8)&(W[prev].hr<17)]
    ps_=hlc(ps,'PS') if len(ps) else {k:np.nan for k in ('PSH','PSL','PSC','PSPOC')}
    iso=pd.Timestamp(today).isocalendar()
    wk_days=[d_ for d_ in days if pd.Timestamp(d_).isocalendar()[:2]<(iso[0],iso[1])]
    lw=pd.Timestamp(wk_days[-1]).isocalendar()[:2] if wk_days else None
    pw=df[[pd.Timestamp(x).isocalendar()[:2]==lw for x in df.wd]] if lw else df.iloc[:0]
    pw_=hlc(pw,'PW') if len(pw) else {k:np.nan for k in ('PWH','PWL','PWC','PWPOC')}
    m0=pd.Timestamp(today).replace(day=1)
    pmm=df[(pd.to_datetime(df.wd.astype(str))<m0)&(pd.to_datetime(df.wd.astype(str))>=m0-pd.DateOffset(months=1))]
    pm_=hlc(pmm,'PM') if len(pmm) else {k:np.nan for k in ('PMH','PML','PMC','PMPOC')}
    V={**pd_,**on_,**ps_,**pw_,**pm_}
    open8=W[today].o.iloc[0] if len(W[today]) else W[prev].c.iloc[-1]
    rngs=[(W[d_].h.max()-W[d_].l.min()) for d_ in days[-15:-1] if len(W[d_])]
    uAbs=float(np.median(rngs)) if rngs else np.nan
    # gaps yesterday per level (min distance of yesterday's range to level, in U)
    yh,yl=W[prev].h.max(),W[prev].l.min()
    def gapU(v):
        if not np.isfinite(v) or not np.isfinite(uAbs): return 9.9
        if yl<=v<=yh: return 0.0
        return float(min(abs(v-yh),abs(v-yl))/uAbs)
    # virgin: 20-window straddle count
    def am20(v):
        c=0
        for d_ in days[-21:-1]:
            g=W[d_]
            if len(g) and g.l.min()<=v<=g.h.max(): c+=1
        return c
    # stepping POC runs (PD/ON/PS POCs across last 4 windows)
    runs=set()
    for pre,win in (('PD',lambda d_: W[d_]),('PS',lambda d_: W[d_][(W[d_].hr>=8)&(W[d_].hr<17)])):
        vals=[poc(win(d_)) for d_ in days[-5:-1]]
        vals=[v for v in vals if np.isfinite(v)]
        if len(vals)>=4 and (all(np.diff(vals)>0) or all(np.diff(vals)<0)): runs.add(pre+'POC')
    # cascade states from 5 window closes vs PSPOC/PML/PWC
    closes=[W[d_].c.iloc[-1] for d_ in days[-6:-1] if len(W[d_])]
    scn=[]
    def state(v):
        if not np.isfinite(v) or len(closes)<5: return None
        ab=[c_>v for c_ in closes]
        side='ab' if ab[-1] else 'bl'; cross='no' if all(x==ab[-1] for x in ab) else ('xup' if ab[-1] else 'xdn')
        return side+'|'+cross
    if state(V['PSPOC'])=='bl|xdn': scn.append('POC-CASC-DN')
    if state(V['PSPOC'])=='ab|xup': scn.append('POC-CASC-UP')
    if state(V['PML'])=='bl|xdn': scn.append('ML-CASC')
    if state(V['PWC'])=='ab|no': scn.append('WC-SUPP')
    reg=hayden(df[df.dt>=df.dt.max()-pd.Timedelta(days=40)])  # FIX 2026-07-23: keep Hayden on its specified 40d window despite 70d fetch
    wkc='wkend' if pd.Timestamp(today).weekday()>4 else 'wkday'
    # walls r=0.25U
    vals=np.array([V.get(l,np.nan) for l in LV]); okm=np.isfinite(vals)
    order=np.argsort(vals[okm]); names=np.array(LV)[okm][order]; sv=vals[okm][order]
    wid=np.zeros(len(sv),int); w=0
    for j in range(1,len(sv)):
        if sv[j]-sv[j-1]>0.25*uAbs: w+=1
        wid[j]=w
    parts=[f'CB12|{nm}|{today}',f'U:{uAbs/open8*100:.2f}',f'UA:{uAbs:.6g}',
           f'CTX:{reg},{yd},{wkc},{dtype}','SCN:'+('/'.join(scn) if scn else 'none')]
    for wl in range(w+1):
        m=wid==wl; mem=names[m]; lo,hi=sv[m].min(),sv[m].max()
        wm='WM' if any(x[:2] in ('PW','PM') for x in mem) else 'D'
        c=grav(min(gapU(V[x]) for x in mem))
        tags=''
        if any(x in runs for x in mem): tags+='★'
        if all(am20(V[x])==0 for x in mem): tags+='V'
        parts.append(f'W{wl+1}:{lo:.6g},{hi:.6g},{wm},{c:.0f},{tags or "-"}')
    return '|'.join(parts)

if __name__=='__main__':
    dt={}; yd={}
    for a in sys.argv[1:]:
        if a.startswith('--dtype'): dt=dict(x.split(':') for x in sys.argv[sys.argv.index(a)+1].split(','))
        if a.startswith('--yd'): yd=dict(x.split(':') for x in sys.argv[sys.argv.index(a)+1].split(','))
    for nm,sym in CRY.items():
        try: print(build(nm,sym,dt.get(nm,'na'),yd.get(nm,'na')))
        except Exception as e: print(f'CB9|{nm}|ERROR|{e}',file=sys.stderr)
