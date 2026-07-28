#!/usr/bin/env python3
"""d55_grain.py — Option B DON-55 at FULL GRAIN (contract item 1). Verbatim b0a_ob55 mechanics
on the record's 4h bars: sig = close > prior-55-bar high-max; risk=2*ATR14(4h); half at +1R then
stop->breakeven; 48-bar time stop; re-entry at exit bar. Daily sample at 08:00 ET.
Columns per coin-day: ob55_open, ob55_fired, bars_in_trade, dist_entry, dist_stop, half_off,
unrealized_R, skip_state (pi down & daily Hayden anchor not Bull), warmup flag.
GATE (contract): open/fired must equal the sealed b0 table exactly on 2022-01-01..2026-07-23,
or nothing ships (exit 1). Output -> results/record/d55_daily_{COIN}.parquet (new table; record append-only)."""
import pandas as pd, numpy as np, json, os, sys, time, argparse
from zoneinfo import ZoneInfo
ap=argparse.ArgumentParser(); ap.add_argument('--budget-min',type=float,default=60)
A,_=ap.parse_known_args(); ET=ZoneInfo("America/New_York")
COINS=['BTC','ETH','SOL','XRP']; REC='results/record'
B0=pd.read_parquet('data/state/b0_ob55_state.parquet')
fails=0
for coin in COINS:
    fr=pd.read_parquet(f'{REC}/bars_{coin}_4h.parquet')[['dt','o','h','l','c']].copy()
    fr['dt']=pd.to_datetime(fr.dt,utc=True); fr=fr.sort_values('dt').reset_index(drop=True)
    o,h,l,c=fr.o.values,fr.h.values,fr.l.values,fr.c.values
    pc=fr.c.shift(); tr=np.maximum(fr.h-fr.l,np.maximum((fr.h-pc).abs(),(fr.l-pc).abs()))
    atr=tr.rolling(14).mean().values; hh=fr.h.shift(1).rolling(55).max().values
    sig=(c>hh)&np.isfinite(hh)&np.isfinite(atr)
    n=len(fr); trades=[]; i=60
    while i<n-1:
        if sig[i]:
            entry=c[i]; risk=2*atr[i]; stop=entry-risk; tgt=entry+risk
            halved=False; hj=None; closed=False; ex=n-1
            for j in range(i+1,n):
                if o[j]<=stop: ex=j; closed=True; break
                if not halved and o[j]>=tgt:
                    halved=True; hj=j; stop=entry
                    if l[j]<=stop: ex=j; closed=True; break
                elif l[j]<=stop: ex=j; closed=True; break
                elif not halved and h[j]>=tgt: halved=True; hj=j; stop=entry
                if j-i==48: ex=j; closed=True; break
            trades.append(dict(i=i,ex=ex,entry=entry,risk=risk,hj=hj,open=not closed))
            i=ex
            if sig[i] and i<n-1: continue
        i+=1
    D=pd.read_parquet(f'{REC}/bars_{coin}_1D.parquet')[['wdate','pi_state','hayden_daily_anchor']]
    close_t=(fr.dt+pd.Timedelta(hours=4)).values.astype('datetime64[ns]').astype('int64')
    sig_close=close_t[sig]
    ent=np.array([close_t[t['i']] for t in trades]); exi=np.array([close_t[t['ex']] for t in trades])
    rows=[]
    for _,d in D.iterrows():
        dd=pd.Timestamp(str(d.wdate))
        w0=pd.Timestamp(dd.year,dd.month,dd.day,8,tzinfo=ET).tz_convert('UTC').value
        w1=w0-86_400_000_000_000
        act=np.nonzero((ent<=w0)&(w0<exi))[0]
        fired=bool(((sig_close>w1)&(sig_close<=w0)).any())
        asof=int(np.searchsorted(close_t,w0,'right'))-1
        r=dict(coin=coin,date=str(d.wdate),warmup=str(d.wdate)<'2022-01-01',ob55_fired=fired,
               ob55_open=False,bars_in_trade=np.nan,dist_entry=np.nan,dist_stop=np.nan,
               half_off=np.nan,unrealized_R=np.nan,
               skip_state=bool((d.pi_state=='down') and (d.hayden_daily_anchor!='Bull')))
        if len(act) and asof>=0:
            t=trades[act[0]]
            hb=(t['hj'] is not None) and (t['hj']<=asof)
            stop_now=t['entry'] if hb else t['entry']-t['risk']
            r.update(ob55_open=True,bars_in_trade=int(asof-t['i']),
                     dist_entry=float(c[asof]-t['entry']),dist_stop=float(c[asof]-stop_now),
                     half_off=bool(hb),unrealized_R=float((c[asof]-t['entry'])/t['risk']))
        rows.append(r)
    S=pd.DataFrame(rows)
    ref=B0[(B0.coin==coin)].copy(); ref['date']=ref.date.astype(str)
    m=S.merge(ref[['date','ob55_open','ob55_fired']],on='date',suffixes=('','_ref'))
    m=m[(m.date>='2022-01-01')&(m.date<='2026-07-23')]
    bad=int((m.ob55_open!=m.ob55_open_ref).sum()+(m.ob55_fired!=m.ob55_fired_ref).sum())
    print(f"{coin}: {len(trades)} trades | gate window {len(m)} days | mismatches {bad} "+("PASS" if bad==0 else "FAIL"))
    if bad>0:
        print(m[(m.ob55_open!=m.ob55_open_ref)|(m.ob55_fired!=m.ob55_fired_ref)].head(5).to_string()); fails+=1; continue
    S.to_parquet(f'{REC}/d55_daily_{coin}.parquet',compression='zstd',index=False)
print("D55 GRAIN","ALL GATES PASS — SHIPPED" if fails==0 else f"{fails} coin(s) FAILED — those not shipped; report in chat")
sys.exit(1 if fails else 0)
