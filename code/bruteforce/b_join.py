# FE JOIN: fold B0 A-E categoricals into the wide vantage table under the stated no-lookahead rules.
import numpy as np, pandas as pd, hashlib
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
ET=ZoneInfo("America/New_York")
M=pd.read_parquet("bf_vantage_ALL_mf.parquet")
ts=pd.to_datetime(M.t_station,unit="ms",utc=True)
et=ts.dt.tz_convert(ET)
M["utc_date"]=ts.dt.date.astype(str)
etd=et.dt.date; eth=et.dt.hour
# ob55 snapshot day: ET date if time>=08:00 else previous ET date
ob_day=np.where(eth>=8, etd.astype(str), (etd-timedelta(days=1)).astype(str))
# brief-day assignment: valid only 09:00<=ET<24:00 -> that ET date, else None
brief_day=np.where(eth>=9, etd.astype(str), "none")
Y=pd.read_csv("b0_ydarch.csv"); ymap={(r.coin,r.date):r.yd_arch for r in Y.itertuples()}
OB=pd.read_csv("b0_ob55_state.csv")
obmap={(r.coin,r.date):("open_fired" if (r.ob55_open and r.ob55_fired) else "open" if r.ob55_open else "fired" if r.ob55_fired else "flat") for r in OB.itertuples()}
DTt=pd.read_csv("b0_dtype.csv"); dmap={(r.coin,r.date):r.dtype for r in DTt.itertuples()}
L=pd.read_csv("b0_lean.csv"); lmap={(r.coin,r.date):r.lean_dir for r in L.itertuples()}
DF=pd.read_csv("b0_scen_defs.csv"); EV=pd.read_csv("b0_scen_events.csv")
SC={}
for (c,d),g in EV.merge(DF[["coin","date","sc","kind"]],on=["coin","date","sc"]).groupby(["coin","date"]):
    SC[(c,d)]=g[["sc","kind","armed_t","failed_t","hit_t"]].to_dict("records")
def scen_at(coin,bday,tns,ethour):
    if bday=="none": return "na","na"
    recs=SC.get((coin,bday))
    if recs is None: return "na","na"
    if ethour>=14: 
        failed_any=any(r["failed_t"]==r["failed_t"] and r["failed_t"] is not None and not pd.isna(r["failed_t"]) for r in recs)
        return "dead",("T" if failed_any else "F")
    st="pre"; failed=False; armed_kind=None; armed_first=None
    for r in recs:
        a=r["armed_t"]; f=r["failed_t"]; h=r["hit_t"]
        a=None if pd.isna(a) else a; f=None if pd.isna(f) else f; h=None if pd.isna(h) else h
        if f is not None and f<=tns: failed=True; continue
        if h is not None and h<=tns: st="hit" if st=="pre" else st; continue
        if a is not None and a<=tns and (armed_first is None or a<armed_first):
            armed_first=a; armed_kind=r["kind"]
    if armed_kind: st={"LONG":"armedL","SHORT":"armedS","FADE":"armedF"}[armed_kind]
    return st,("T" if failed else "F")
coinv=M.coin.values; tns=ts.to_numpy(dtype="datetime64[ns]").astype("int64")
M["yd_arch"]=[ymap.get((c,u),"na") for c,u in zip(coinv,M.utc_date.values)]
M["ob55"]=[obmap.get((c,o),"na") for c,o in zip(coinv,ob_day)]
M["dtype"]=[dmap.get((c,b),"na") if b!="none" else "na" for c,b in zip(coinv,brief_day)]
M["lean"]=[lmap.get((c,b),"na") if b!="none" else "na" for c,b in zip(coinv,brief_day)]
ss,sf=[],[]
ethv=eth.values
for c,b,t,hh in zip(coinv,brief_day,tns,ethv):
    a,bfl=scen_at(c,b,t,hh); ss.append(a); sf.append(bfl)
M["scen_state"]=ss; M["scen_failed"]=sf
for c in ["dtype","lean"]: M[c]=M[c].replace({np.nan:"na"})
M["scen_state"]=np.where((M.dtype=="na")&(pd.Series(ss)=="dead"),"na",M.scen_state)  # dead only on covered days
M.to_parquet("bf_vantage_ALL_wide.parquet",index=False)
print("rows",len(M))
for c in ["yd_arch","ob55","dtype","lean","scen_state","scen_failed"]:
    print(c,M[c].value_counts(normalize=True).round(3).to_dict())
print("sha",hashlib.sha256(open("bf_vantage_ALL_wide.parquet","rb").read()).hexdigest()[:12])
