# BRUTE-FORCE B1 — vantage-row extraction (checkpointed, resumable). Seed 20260723.
# Tranche 1: 5m frame. Stations crossed during each event episode; 100-bar forward profile per station.
import numpy as np, pandas as pd, sys, hashlib
SYM,NM=sys.argv[1],sys.argv[2]
EV=pd.read_csv(f"/home/claude/mm1/p2_events_{NM}.csv")
EV=EV[EV.etype!='RETEST'].reset_index(drop=True)
df=pd.read_csv(f"/home/claude/mm1/data/{SYM}_5m.csv")
for c in "ohlcv": df[c]=df[c].astype(float)
df['dt']=pd.to_datetime(df.t,unit='ms',utc=True)
t2i={t:i for i,t in enumerate(df.t.values)}
H,L,C,Tm=df.h.values,df.l.values,df.c.values,df.t.values
STATIONS=[('out_1.0',-1.0),('out_0.5',-0.5),('out_0.25',-0.25),('edge',0.0),
          ('in_25',0.25),('mid',0.5),('in_75',0.75),('faredge',1.0),
          ('beyond_0.25',1.25),('beyond_0.5',1.5),('beyond_1.0',2.0)]
rows=[]
for _,e in EV.iterrows():
    if e.t_event not in t2i: continue
    i0=t2i[e.t_event]; U=e.U
    lo,hi=e.z_lo,e.z_hi; w=max(hi-lo,1e-9)
    frm_below = (e.side=='below') or (e.get('exit_dir')=='up')
    nearE,farE=(lo,hi) if frm_below else (hi,lo); sgn=1 if frm_below else -1
    for name,q in STATIONS:
        if q<=0: px=nearE+sgn*q*U
        elif q<1.0: px=lo+q*w if frm_below else hi-q*w
        elif q==1.0: px=farE
        else: px=farE+sgn*(q-1.0)*U
        hit=None
        for i in range(i0,min(i0+289,len(C))):
            if L[i]<=px<=H[i]: hit=i; break
        if hit is None: continue
        f=slice(hit+1,min(hit+101,len(C)))
        if f.stop-f.start<5: continue
        fav=((H[f].max()-px) if frm_below else (px-L[f].min()))/U
        adv=((px-L[f].min()) if frm_below else (H[f].max()-px))/U
        end=(C[f.stop-1]-px)/U*(1 if frm_below else -1)
        rows.append(dict(event_id=int(e.id),coin=NM,station=name,st_px=round(px,6),
            t_station=int(Tm[hit]),bars_after_event=hit-i0,
            fwd_favU=round(fav,3),fwd_advU=round(adv,3),fwd_endU=round(end,3),
            etype=e.etype,zone=int(e.zone),contact=e.contact,virgin=e.virgin,widthU=e.widthU,
            hayden=e.hayden,hayden_btc=e.hayden_btc,btc_pi=e.btc_pi,session=e.session,
            wknd=e.wknd,origin=e.origin,distU=e.distU,speedUh=e.speedUh,relvol=e.relvol,
            test_no=e.test_no,rng_used=e.rng_used,wk_used=e.wk_used,u_trend=e.u_trend,U=U))
V=pd.DataFrame(rows)
V.to_parquet(f"bf_vantage_{NM}_5m.parquet",index=False)
print(NM,"events",len(EV),"vantage rows",len(V),"sha",
      hashlib.sha256(open(f"bf_vantage_{NM}_5m.parquet",'rb').read()).hexdigest()[:12],flush=True)
