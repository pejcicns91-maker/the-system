# B0-E: armed-scenario replay. Scenario CONSTRUCTION = engine scenarios() (imported) with a
# verbatim-copied struct builder self-gated per day by payload-frag string equality.
# ARMING PROTOCOL-BY-DECISION (logged, pending ratification): window = 15m closes in
# (09:00 ET, 14:00 ET]; LONG arms on close>trig, SHORT close<trig, FADE close>=trig;
# armed->failed on close beyond inv (L:<inv, S/F:>inv); armed->hit on close beyond tgt
# (L:>tgt, S/F:<tgt); no pre-arm death; no re-arm after fail; all die 14:00 ET.
import numpy as np, pandas as pd, importlib.util, sys, hashlib
from datetime import date, datetime
from zoneinfo import ZoneInfo
ET=ZoneInfo("America/New_York")
def et_utc(d,hh): return pd.Timestamp(datetime(d.year,d.month,d.day,hh,tzinfo=ET)).tz_convert("UTC")
spec=importlib.util.spec_from_file_location("bev4","/mnt/project/brief_engine_v4.py")
E=importlib.util.module_from_spec(spec); sys.modules["bev4"]=E; spec.loader.exec_module(E)
SY={"BTC":"BTCUSDT","ETH":"ETHUSDT","SOL":"SOLUSDT","XRP":"XRPUSDT"}
H1={};Q15={}
for nm,sym in SY.items():
    df=pd.read_csv(f"data/{sym}_5m.csv")
    for tag,dur,store in [("1h",3_600_000,H1),("15m",900_000,Q15)]:
        b=(df.t//dur)*dur
        g=df.groupby(b).agg(h=("h","max"),l=("l","min"),c=("c","last"))
        g=g[g.index+dur<=int(df.t.iloc[-1])+300_000]
        g["close_t"]=g.index+dur
        store[nm]=g
def build_out(core,dr,spot,rnd):   # verbatim copy of scenarios() construction (self-gated by frag)
    U,PDC=core["U"],core["PDC"]; buf=0.15*U*PDC; cap=0.70*U*PDC
    levs=[("PDH",core["PDH"]),("PDL",core["PDL"]),("PDC",PDC),("ONH",core["onH"]),("ONL",core["onL"]),("RND",rnd)]
    levs=[(n,v) for n,v in levs if v==v and v>0]
    ups=sorted([lv for lv in levs if lv[1]>spot],key=lambda x:x[1])
    dns=sorted([lv for lv in levs if lv[1]<spot],key=lambda x:x[1],reverse=True)
    out=[]; lean=dr["dir"] if dr["dir"] in ("up","down") else None
    lt=f"lean {dr.get('hist','')}" if lean else "context"
    if ups:
        t=ups[0]; tgt=ups[1][1] if len(ups)>1 and ups[1][1]<=spot+cap else spot+cap
        out.append(dict(kind="LONG",trig=t,tgt=tgt,inv=t[1]-buf,tag=lt if lean=="up" else "context"))
    if dns:
        t=dns[0]; tgt=dns[1][1] if len(dns)>1 and dns[1][1]>=spot-cap else spot-cap
        out.append(dict(kind="SHORT",trig=t,tgt=tgt,inv=t[1]+buf,tag=lt if lean=="down" else "context"))
    if core["dtype"]=="QUIET" or (lean is None and core["dtype"]!="EXPANSION"):
        if ups:
            f_=ups[-1] if ups[-1][1]<=spot+cap else ups[0]
            ftgt=max([v for v in (PDC,core["onL"]) if v==v and v<f_[1]] or [spot-cap]); ftgt=max(ftgt,spot-cap)
            out.append(dict(kind="FADE",trig=f_,tgt=ftgt,inv=f_[1]+buf,
                            tag="QUIET-day context" if core["dtype"]=="QUIET" else "context"))
    out=[s for s in out if (s["kind"]=="LONG" and s["tgt"]>s["trig"][1]) or (s["kind"] in ("SHORT","FADE") and s["tgt"]<s["trig"][1])]
    if lean: out.sort(key=lambda x: 0 if ((x["kind"]=="LONG")==(lean=="up") and x["kind"]!="FADE") else 1)
    out=out[:3]
    frags=[f"SC{i}:{ {'LONG':'L','SHORT':'S','FADE':'F'}[s['kind']] },{E.fp(s['trig'][1])},{E.fp(s['tgt'])},{E.fp(s['inv'])},{'lean' if 'lean' in s['tag'] else 'ctx'}" for i,s in enumerate(out,1)]
    return out,"|".join(frags)
DT=pd.read_csv("b0_dtype.csv"); L=pd.read_csv("b0_lean.csv"); OB=pd.read_csv("b0_ob55_state.csv")
lean_m={(r.coin,r.date):(r.lean_dir,r.lean_strength) for r in L.itertuples()}
ob_m={(r.coin,r.date):bool(r.ob55_open) for r in OB.itertuples()}
Dc={nm:pd.read_pickle(f"/home/claude/bstate/state/{sym}_1d.pkl").reset_index(drop=True) for nm,sym in SY.items()}
for nm in Dc: Dc[nm]["dd"]=[x.date() for x in Dc[nm].dt]
dmaps={nm:{r.dd:i for i,r in enumerate(Dc[nm].itertuples())} for nm in Dc}
defs,evs=[],[]; frag_bad=0
for r in DT[DT.dtype!="na"].itertuples():
    nm=r.coin; d=date.fromisoformat(r.date)
    di=dmaps[nm].get(d)
    if di is None or di==0: continue
    D=Dc[nm]; w0=et_utc(d,8)
    Hg=H1[nm]; Hi=pd.to_datetime(Hg.index,unit="ms",utc=True)
    on=Hg[(Hi>=w0-pd.Timedelta(hours=14))&(Hi<w0)]
    if len(on)<5: continue
    onH,onL,onc=float(on.h.max()),float(on.l.min()),float(on.c.iloc[-1])
    core=dict(U=r.U,PDC=float(D.c.iloc[di-1]),PDH=float(D.h.iloc[di-1]),PDL=float(D.l.iloc[di-1]),
              onH=onH,onL=onL,dtype=r.dtype)
    spot=onc; rs=E.round_step(spot); rnd=round(spot/rs)*rs
    ld,_=lean_m.get((nm,r.date),("na","na")); dr={"dir":ld if ld in ("up","down") else "none","hist":""}
    o55=ob_m.get((nm,r.date),False)
    out,myfrag=build_out(core,dr,spot,rnd)
    _,efrag=E.scenarios(core,dr,spot,rnd,o55,o55)
    if myfrag!=efrag: frag_bad+=1; continue
    t9,t14=et_utc(d,9).value,et_utc(d,14).value
    Q=Q15[nm]; ct=(Q.close_t.values.astype("int64"))*1_000_000
    m=(ct>t9)&(ct<=t14); cc=Q.c.values[m]; tt=ct[m]
    for i,s in enumerate(out,1):
        trig=s["trig"][1]; armed_t=failed_t=hit_t=None; st="pending"
        for j in range(len(cc)):
            c=cc[j]
            if st=="pending":
                if (s["kind"]=="LONG" and c>trig) or (s["kind"]=="SHORT" and c<trig) or (s["kind"]=="FADE" and c>=trig):
                    st="armed"; armed_t=tt[j]
            elif st=="armed":
                if (s["kind"]=="LONG" and c<s["inv"]) or (s["kind"] in ("SHORT","FADE") and c>s["inv"]):
                    st="failed"; failed_t=tt[j]; break
                if (s["kind"]=="LONG" and c>s["tgt"]) or (s["kind"] in ("SHORT","FADE") and c<s["tgt"]):
                    st="hit"; hit_t=tt[j]; break
        defs.append(dict(coin=nm,date=r.date,sc=i,kind=s["kind"],trig_name=s["trig"][0],
                         trig=round(trig,6),tgt=round(s["tgt"],6),inv=round(s["inv"],6),
                         tag="lean" if "lean" in s["tag"] else "ctx"))
        evs.append(dict(coin=nm,date=r.date,sc=i,state_final=st,
                        armed_t=armed_t,failed_t=failed_t,hit_t=hit_t))
DF=pd.DataFrame(defs); EV=pd.DataFrame(evs)
DF.to_csv("b0_scen_defs.csv",index=False); EV.to_csv("b0_scen_events.csv",index=False)
print("scenario rows:",len(DF),"days:",DF.groupby(['coin']).date.nunique().to_dict(),"| frag self-gate fails:",frag_bad)
print("final states:",EV.state_final.value_counts(normalize=True).round(3).to_dict())
g=DF[(DF.coin=="SOL")&(DF.date.isin(["2026-07-22","2026-07-23"]))&(DF.sc==1)]
print("GATE vs trackB:"); print(g.to_string(index=False))
for f in ["b0_scen_defs.csv","b0_scen_events.csv"]:
    print(f,"sha",hashlib.sha256(open(f,'rb').read()).hexdigest()[:12])
