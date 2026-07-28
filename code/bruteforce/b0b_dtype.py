# B0-B v2: dtype as-of replay. Generator = vectorized reimplementation of forecast() semantics;
# Validator = engine's own forecast() (imported, data-layer patched) on a seeded sample + 07-22/23.
import numpy as np, pandas as pd, importlib.util, sys, hashlib
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
ET=ZoneInfo("America/New_York"); K,WARMUP=75,300
def et_utc(d,hh): return pd.Timestamp(datetime(d.year,d.month,d.day,hh,tzinfo=ET)).tz_convert("UTC")
SY={"BTC":"BTCUSDT","ETH":"ETHUSDT","SOL":"SOLUSDT","XRP":"XRPUSDT"}
H1={}
for nm,sym in SY.items():
    df=pd.read_csv(f"data/{sym}_5m.csv"); b=(df.t//3_600_000)*3_600_000
    g=df.groupby(b).agg(h=("h","max"),l=("l","min"),c=("c","last"))
    g=g[g.index+3_600_000<=int(df.t.iloc[-1])+300_000]
    g.index=pd.to_datetime(g.index,unit="ms",utc=True); H1[nm]=g
def daily_feats(D):
    pc=D["c"].shift(); h,l,c=D["h"],D["l"],D["c"]
    ret=c.pct_change(); tr=np.maximum(h-l,np.maximum((h-pc).abs(),(l-pc).abs()))
    atr14=tr.ewm(alpha=1/14,adjust=False).mean(); ma50=c.rolling(50).mean()
    hi20,lo20=h.rolling(20).max(),l.rolling(20).min()
    rv14,rv90=ret.rolling(14).std(),ret.rolling(90).std()
    return pd.DataFrame({"atrpct":(atr14/c).shift(1),"donch_pos":(((c-lo20)/(hi20-lo20)).clip(0,1)).shift(1),
        "dist_ma50_atr":((c-ma50)/atr14).shift(1),"vol_z":((rv14-rv90)/rv90).shift(1),
        "daily_rng14":((h-l)/pc).rolling(14).mean().shift(1)},index=range(len(D)))
rows=[]
for nm,sym in SY.items():
    D=pd.read_pickle(f"/home/claude/bstate/state/{sym}_1d.pkl").reset_index(drop=True)
    D["d"]=[x.date() for x in D.dt]; F=daily_feats(D); dmap={r.d:i for i,r in enumerate(D.itertuples())}
    S=pd.read_csv(f"/home/claude/bstate/state/{nm}_sess.csv").copy()
    S["dd"]=[date.fromisoformat(x) for x in S.date]
    S["di"]=[dmap.get(x) for x in S.dd]; S=S[S.di.notna()].reset_index(drop=True)
    hist=S["wr"].shift(1); S["wrng_prev"],S["wrng5"],S["wrng14"]=hist,hist.rolling(5).mean(),hist.rolling(14).mean()
    for col in F.columns: S[col]=[F[col].iloc[int(di)] for di in S["di"]]
    feats=["atrpct","wrng_prev","wrng5","wrng14","donch_pos","dist_ma50_atr","vol_z","daily_rng14","on_move","on_rng"]
    ok=S[feats+["wr"]].notna().all(axis=1).values
    Xall=S[feats].values.astype(float); yall=S["wr"].values.astype(float); ddv=np.array(S.dd.values)
    Hg=H1[nm]; Hi=Hg.index
    d,d1=date(2020,8,12),date(2026,7,23)
    while d<=d1:
        if d.weekday()<5:
            sel=ok&(ddv<d); Xp,yp=Xall[sel],yall[sel]
            if len(yp)<WARMUP+10 or dmap.get(d) is None:
                rows.append(dict(coin=nm,date=str(d),dtype="na",U=np.nan,on_pos=np.nan,don20=np.nan))
            else:
                w0=et_utc(d,8)
                on=Hg[(Hi>=w0-pd.Timedelta(hours=14))&(Hi<w0)]
                if len(on)<5:
                    rows.append(dict(coin=nm,date=str(d),dtype="na",U=np.nan,on_pos=np.nan,don20=np.nan))
                else:
                    onH,onL,onc=float(on.h.max()),float(on.l.min()),float(on.c.iloc[-1])
                    wb=Hg[(Hi>=w0)&(Hi<w0+pd.Timedelta(hours=1))]
                    px8=float(wb.c.iloc[-1]) if len(wb) else onc
                    di_prev=dmap[d]-1; pcv=float(D["c"].iloc[di_prev]); fi=dmap[d]
                    fr={c_:(float(F[c_].iloc[fi]) if F[c_].iloc[fi]==F[c_].iloc[fi] else float(F[c_].iloc[fi-1])) for c_ in F.columns}
                    lw=yall[sel]
                    xq=np.array([fr["atrpct"],lw[-1],lw[-5:].mean(),lw[-14:].mean(),fr["donch_pos"],
                                 fr["dist_ma50_atr"],fr["vol_z"],fr["daily_rng14"],abs(px8-onc)/pcv,(onH-onL)/pcv])
                    mu,sd=Xp.mean(0),Xp.std(0)+1e-9
                    dist=np.sqrt((((Xp-mu)/sd-(xq-mu)/sd)**2).sum(1))
                    nn=np.argpartition(dist,K)[:K]; rr=yp[nn]; trail=yp[-90:]; med=float(np.median(rr))
                    dt_=("EXPANSION" if med>np.percentile(trail,80) else ("QUIET" if med<np.percentile(trail,20) else "normal"))
                    rows.append(dict(coin=nm,date=str(d),dtype=dt_,U=med,on_pos=(onc-onL)/(onH-onL) if onH>onL else np.nan,don20=fr["donch_pos"]))
        d+=timedelta(days=1)
    print(nm,"done",flush=True)
R=pd.DataFrame(rows); R.to_csv("b0_dtype.csv",index=False)
v=R[R.dtype!="na"]
print("rows:",len(R),"non-na:",len(v),"dist:",v.dtype.value_counts(normalize=True).round(3).to_dict())
print("first non-na:",v.groupby("coin").date.min().to_dict())
print(R[R.date.isin(["2026-07-22","2026-07-23"])][["coin","date","dtype"]].to_string(index=False))
print("sha",hashlib.sha256(open("b0_dtype.csv","rb").read()).hexdigest()[:12])
