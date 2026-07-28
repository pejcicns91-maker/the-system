# B0-A: DON55 port. Exact bt.py conventions (loop from bar 60, re-entry at exit bar,
# base costs rt=0.0011 + financing 0.00007/4h-bar, t-window filter AFTER generation).
# Frames: state-zip 4h pkls. Gate: exact match vs ob_trades_S1.csv DON55 rows.
import numpy as np, pandas as pd, hashlib
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York")
def et_utc(d,hh): return pd.Timestamp(datetime(d.year,d.month,d.day,hh,tzinfo=ET)).tz_convert("UTC")
SYMS=["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT"]; RT={"base":0.0011,"stress":0.0017}; FIN=0.00007
def run_trade(df,i,cost):
    o,h,l,c=df.o.values,df.h.values,df.l.values,df.c.values
    entry,atr=c[i],df.atr.values[i]; risk=2*atr; stop,tgt=entry-risk,entry+risk
    riskfrac=risk/entry; legs=[]; halved=False; closed=False; n=len(df)
    for j in range(i+1,n):
        if o[j]<=stop: legs.append((0.5 if halved else 1.0,o[j],j)); closed=True; break
        if not halved and o[j]>=tgt:
            legs.append((0.5,o[j],j)); halved=True; stop=entry
            if l[j]<=stop: legs.append((0.5,stop,j)); closed=True; break
        elif l[j]<=stop: legs.append((0.5 if halved else 1.0,stop,j)); closed=True; break
        elif not halved and h[j]>=tgt: legs.append((0.5,tgt,j)); halved=True; stop=entry
        if j-i==48: legs.append((0.5 if halved else 1.0,c[j],j)); closed=True; break
    if not closed: legs.append((0.5 if halved else 1.0,c[n-1],n-1))
    gross=sum(w*(px-entry)/risk for w,px,_ in legs)
    cst=sum(w*(RT[cost]+FIN*(j-i)*1)/riskfrac for w,px,j in legs)
    return dict(entry_bar=i,entry=entry,stop0=entry-risk,tgt=tgt,atr=atr,t=df.dt.values[i],
                exit_bar=max(j for *_,j in legs),open=not closed,halved=halved,R=gross-cst,riskfrac=riskfrac)
all_tr=[]
for sym in SYMS:
    df=pd.read_pickle(f"/home/claude/bstate/state/{sym}_4h.pkl").reset_index(drop=True)
    pc=df.c.shift(); tr=np.maximum(df.h-df.l,np.maximum((df.h-pc).abs(),(df.l-pc).abs()))
    df["atr"]=tr.rolling(14).mean(); df["hh55"]=df.h.shift(1).rolling(55).max()
    sig=((df.c>df.hh55)&df.hh55.notna()&df.atr.notna()).values
    i,n=60,len(df)
    while i<n-1:
        if sig[i]:
            t=run_trade(df,i,"base"); t2=run_trade(df,i,"stress")
            t.update(sym=sym,R_stress=t2["R"]); all_tr.append(t)
            i=t["exit_bar"]
            if sig[i] and i<n-1: continue
        i+=1
T=pd.DataFrame(all_tr); T["t"]=pd.to_datetime(T.t,utc=True)
W=(T.t>=pd.Timestamp("2020-09-01",tz="UTC"))&(T.t<=pd.Timestamp("2026-05-31",tz="UTC")+pd.Timedelta(days=1))
G=T[W].sort_values(["t","sym"]).reset_index(drop=True)
R55=pd.read_csv("/mnt/project/ob_trades_S1.csv"); R55=R55[R55.sleeve=="DON55"].copy()
R55["t"]=pd.to_datetime(R55.t,utc=True); R55=R55.sort_values(["t","sym"]).reset_index(drop=True)
print("ref:",len(R55),"replay(window):",len(G))
if len(R55)==len(G):
    key_ok=bool((R55.sym.values==G.sym.values).all() and (R55.t.values==G.t.values).all())
    print("identity (sym,t) aligned:",key_ok)
    for c in ["entry_bar","entry","stop0","tgt","atr","exit_bar","R","riskfrac"]:
        d=np.abs(R55[c].values-G[c].values).max(); print(f"  {c}: max|diff| {d:.3e}")
    dA=np.abs(R55.R_A.values-G.R_stress.values).max(); print(f"  R_A vs stress-R: max|diff| {dA:.3e}")
    ho=int((R55.halved.values!=G.halved.values).sum())+int((R55.open.values!=G.open.values).sum())
    print("  halved/open flag mismatches:",ho)
    gate=key_ok and ho==0 and all(np.abs(R55[c].values-G[c].values).max()<1e-8 for c in ["entry","stop0","tgt","atr","R"]) and (R55.entry_bar.values==G.entry_bar.values).all() and (R55.exit_bar.values==G.exit_bar.values).all()
    print("GATE:","MATCH — ADOPT" if gate else "NO MATCH — DO NOT ADOPT")
else:
    print("GATE: count mismatch — DO NOT ADOPT")
# daily state series from FULL (unfiltered) trade set, ob_state semantics at 08:00 ET
rows=[]
for sym in SYMS:
    df=pd.read_pickle(f"/home/claude/bstate/state/{sym}_4h.pkl").reset_index(drop=True)
    pc=df.c.shift(); trr=np.maximum(df.h-df.l,np.maximum((df.h-pc).abs(),(df.l-pc).abs()))
    atr=trr.rolling(14).mean(); hh=df.h.shift(1).rolling(55).max()
    sig=((df.c>hh)&hh.notna()&atr.notna()).values
    sig_close=(df.dt[sig]+pd.Timedelta(hours=4)).to_numpy(dtype="datetime64[ns]").astype("int64")
    tt=T[T.sym==sym]
    iv=np.stack([(tt.t+pd.Timedelta(hours=4)).to_numpy(dtype="datetime64[ns]").astype("int64"),
        (pd.to_datetime(df.dt.iloc[tt.exit_bar].values,utc=True)+pd.Timedelta(hours=4)).to_numpy(dtype="datetime64[ns]").astype("int64")],axis=1)
    d,d1=df.dt.iloc[0].date()+timedelta(days=61),date(2026,7,23)
    while d<=d1:
        w0=et_utc(d,8).value; w1=(et_utc(d,8)-pd.Timedelta(days=1)).value
        rows.append(dict(coin=sym[:3],date=str(d),
            ob55_open=bool(((iv[:,0]<=w0)&(w0<iv[:,1])).any()),
            ob55_fired=bool(((sig_close>w1)&(sig_close<=w0)).any())))
        d+=timedelta(days=1)
S=pd.DataFrame(rows); S.to_csv("b0_ob55_state.csv",index=False)
print("state rows:",len(S),"| open-day frac:",round(S.ob55_open.mean(),3),"| fired-day frac:",round(S.ob55_fired.mean(),3))
print("sha",hashlib.sha256(open("b0_ob55_state.csv","rb").read()).hexdigest()[:12])
