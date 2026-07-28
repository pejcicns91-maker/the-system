#!/usr/bin/env python3
"""b1_daychar.py — LAYER B, first query set: DAY-CHARACTER CAMPAIGN (day grain).
Counting only, no models: every rate carries its n; frequency is an output, sorted desc.
Reads results/record/. Writes results/daychar/:
  labels_dist.parquet      — every candidate label at every swept parameter, per coin, class counts
  forecast_counts.parquet  — P(label_today | ONE prior-day conditioner) for every conditioner ALONE
  markdays_{COIN}.parquet  — RAW mark-day interaction facts (kept per rule 3; aggregates ride beside)
  sweep_rates.parquet      — P(sweep-and-reverse at a mark | day label) under swept p,r in U and ATR rulers
  pullback_rates.parquet   — P(continuation after pullback >= q | day label), structural + ATR rulers
  REPORT.md                — shapes, top-n lines, named gaps. Verdicts belong to Svet, not this file.
Bar-grain Layer B (components x offsets x 100-bar windows) is the NEXT job — not folded in here."""
import pandas as pd, numpy as np, json, os, sys, time, argparse
ap=argparse.ArgumentParser(); ap.add_argument('--budget-min',type=float,default=230)
A,_=ap.parse_known_args(); T0=time.time()
COINS=['BTC','ETH','SOL','XRP']; REC='results/record'; OUT='results/daychar'
os.makedirs(OUT,exist_ok=True); os.makedirs('results/state',exist_ok=True)
SF='results/state/b1_daychar_v2.json'; st=json.load(open(SF)) if os.path.exists(SF) else {'done':[]}
DTEST=int(os.environ.get('TEST_DAYS','0'))

E_GRID=[0.4,0.5,0.6]; G_GRID=[0.8,1.0,1.3]; C_GRID=[4,6,8]; L_GRID=[4,6,8]
P_GRID=[0.1,0.25,0.5]; R_GRID=[0.1,0.25,0.5]; Q_GRID=[0.25,0.382,0.5]; K_GRID=[0.5,1.0,1.5]

def labels_for(D):
    out={}
    for e in E_GRID: out[f'd1_eff@{e}']=np.select([D.d1_eff>=e],[np.where(D.c>=D.o,'TREND_UP','TREND_DN')],default='RANGE')
    for g in G_GRID:
        out[f'd2_u@{g}']=np.where(D.d2_rng_u>=g,'BIG','SMALL')
        out[f'd2_atr@{g}']=np.where(D.d2_rng_atr>=g,'BIG','SMALL')
    for c in C_GRID: out[f'd3_cross@{c}']=np.where(D.d3_opencross>=c,'RANGE','TREND')
    for L in L_GRID: out[f'd4_ladder@{L}']=np.where(D.d4_ladder>=L,'TREND','RANGE')
    out['d5_dtype']=D.d5_dtype.fillna('na'); out['d6_ob55']=D.d6_ob55_fired.fillna('na').astype(str)
    out['d7_arch']=D.d7_yd_arch_today
    return pd.DataFrame(out,index=D.index)

def markday_facts(f5,D,MP):
    rows=[]
    mp=MP[MP.conv=='ET']
    g5=dict(list(f5.groupby('wdate')))
    marks_by_day=dict(list(mp.groupby('wdate')))
    for _,d in D.iterrows():
        w=str(d.wdate); g=g5.get(d.wdate); mk=marks_by_day.get(w)
        if g is None or mk is None: continue
        h=g.h.to_numpy(); l=g.l.to_numpy(); o=float(d.o); c=float(d.c)
        for _,m in mk.iterrows():
            mpx=float(m.price)
            if not np.isfinite(mpx): continue
            if o>=mpx:
                pen=max(0.0,mpx-l.min())
                if pen>0:
                    i=int(l.argmin()); rev=float(h[i:].max()-mpx)
                else: rev=np.nan
                side='above'
            else:
                pen=max(0.0,h.max()-mpx)
                if pen>0:
                    i=int(h.argmax()); rev=float(mpx-l[i:].min())
                else: rev=np.nan
                side='below'
            rows.append((w,m.name if isinstance(m.name,str) else m['name'],mpx,side,pen,rev,
                         'open_side' if (np.sign(c-mpx)==np.sign(o-mpx) and o!=mpx) else 'crossed'))
    return pd.DataFrame(rows,columns=['wdate','mark','price','open_side','pen','rev_after','close_side'])

def pullback_facts(f5,D):
    rows=[]; g5=dict(list(f5.groupby('wdate')))
    for _,d in D.iterrows():
        g=g5.get(d.wdate)
        if g is None or len(g)<50: continue
        h=g.h.to_numpy(); l=g.l.to_numpy(); o=float(d.o)
        up= d.c>=d.o
        if up:
            rh=np.maximum.accumulate(h); leg=rh-o; fin=rh[-1]-o
            valid=(leg>=0.25*fin)&(fin>0)
            pb=(rh-l); frac=np.where(valid,pb/np.where(leg>0,leg,np.nan),np.nan)
            ok=np.isfinite(frac).any()
            j=int(np.nanargmax(frac)) if ok else 0
            cont=int(h.argmax())>j; fmax=float(np.nanmax(frac)) if ok else np.nan
            pmax=float(np.nanmax(np.where(valid,pb,np.nan))) if valid.any() else np.nan
        else:
            rl=np.minimum.accumulate(l); leg=o-rl; fin=o-rl[-1]
            valid=(leg>=0.25*fin)&(fin>0)
            pb=(h-rl); frac=np.where(valid,pb/np.where(leg>0,leg,np.nan),np.nan)
            ok=np.isfinite(frac).any()
            j=int(np.nanargmax(frac)) if ok else 0
            cont=int(l.argmin())>j; fmax=float(np.nanmax(frac)) if ok else np.nan
            pmax=float(np.nanmax(np.where(valid,pb,np.nan))) if valid.any() else np.nan
        rows.append((str(d.wdate),'up' if up else 'dn',fmax,pmax,cont,float(d.atr14_1d) if pd.notna(d.atr14_1d) else np.nan))
    return pd.DataFrame(rows,columns=['wdate','dir','pb_frac_max','pb_abs_max','continued','atr1d'])

allL=[]; allF=[]; allS=[]; allP=[]
for coin in COINS:
    if coin in st['done']: print(coin,'done; skip'); continue
    if (time.time()-T0)/60>A.budget_min-6: print('budget; resume'); break
    D=pd.read_parquet(f'{REC}/bars_{coin}_1D.parquet')
    if DTEST: D=D.tail(DTEST).reset_index(drop=True)
    f5=pd.read_parquet(f'{REC}/bars_{coin}_5m.parquet',columns=['dt','o','h','l','c','wdate'])
    f5=f5[f5.wdate.isin(set(D.wdate))]
    MP=pd.read_parquet(f'{REC}/marks_periods_{coin}.parquet')
    LB=labels_for(D)
    # label distributions
    for col in LB.columns:
        vc=LB[col].value_counts()
        for v,n in vc.items(): allL.append((coin,col,str(v),int(n)))
    # forecast by counting: conditioners known BEFORE the day, each ALONE
    conds={'yd_label:'+c: LB[c].shift(1) for c in LB.columns}
    conds.update({'yd_arch':D.yd_arch,'d5_call':D.d5_dtype,'pi':D.pi_state,'hayden_anchor':D.hayden_daily_anchor,
                  'weekday':pd.to_datetime(D.wdate.astype(str)).dt.dayofweek.astype(str),
                  'ob55_open':D.ob55_open.astype(str),'lean':D.lean_dir})
    for lcol in LB.columns:
        y=LB[lcol]
        for cn,cv in conds.items():
            t=pd.crosstab(cv.fillna('na'),y)
            for u in t.index:
                tot=int(t.loc[u].sum())
                for v in t.columns:
                    allF.append((coin,lcol,cn,str(u),str(v),int(t.loc[u,v]),tot))
    MD=markday_facts(f5,D,MP); MD.to_parquet(f'{OUT}/markdays_{coin}.parquet',compression='zstd',index=False)
    Dk=D.assign(wdate=D.wdate.astype(str)).set_index('wdate')
    MD2=MD.join(Dk[['uabs','atr14_1d','rng']],on='wdate')
    for lcol in LB.columns:
        lab=pd.Series(LB[lcol].values,index=D.wdate.astype(str))
        MD2['lab']=MD2.wdate.map(lab)
        for ruler,den in [('U',MD2.uabs),('ATR1d',MD2.atr14_1d),('DAYRNG',MD2.rng)]:
            penx=MD2.pen/den; revx=MD2.rev_after/den
            for p in P_GRID:
                for r in R_GRID:
                    sw=(MD2.pen>0)&(penx<=p)
                    ok=sw&(revx>=r)
                    grp=MD2[sw].groupby(['lab','mark']).size()
                    okg=MD2[ok].groupby(['lab','mark']).size()
                    for key,n in grp.items():
                        k=int(okg.get(key,0))
                        allS.append((coin,lcol,str(key[0]),key[1],ruler,p,r,k,int(n)))
    PB=pullback_facts(f5,D)
    for lcol in LB.columns:
        lab=pd.Series(LB[lcol].values,index=D.wdate.astype(str))
        PB['lab']=PB.wdate.map(lab)
        for q in Q_GRID:
            m=PB.pb_frac_max>=q
            g=PB[m].groupby('lab'); 
            for lv,gg in g: allP.append((coin,lcol,str(lv),'frac',q,int(gg.continued.sum()),len(gg)))
        for k in K_GRID:
            m=PB.pb_abs_max>=k*PB.atr1d
            g=PB[m].groupby('lab')
            for lv,gg in g: allP.append((coin,lcol,str(lv),'ATR1d',k,int(gg.continued.sum()),len(gg)))
    st['done'].append(coin); json.dump(st,open(SF,'w')); print('DONE',coin,flush=True)

if allL:
    L=pd.DataFrame(allL,columns=['coin','label','value','n']); 
    F=pd.DataFrame(allF,columns=['coin','label','conditioner','cond_value','label_value','n','n_cond'])
    S=pd.DataFrame(allS,columns=['coin','label','label_value','mark','ruler','p_max','r_min','n_ok','n'])
    P=pd.DataFrame(allP,columns=['coin','label','label_value','ruler','q','n_cont','n'])
    for nm,df in [('labels_dist',L),('forecast_counts',F),('sweep_rates',S),('pullback_rates',P)]:
        old=f'{OUT}/{nm}.parquet'
        if os.path.exists(old):
            df=pd.concat([pd.read_parquet(old),df]).drop_duplicates()
        df.to_parquet(old,compression='zstd',index=False)
    F['rate']=F.n/F.n_cond; S['rate']=S.n_ok/S.n; P['rate']=P.n_cont/P.n
    top=S[S.n>=200].sort_values('n',ascending=False).head(12)
    lines=[f"# DAYCHAR REPORT — {pd.Timestamp.now(tz='UTC')}",
    f"tables: labels_dist {len(L):,} · forecast_counts {len(F):,} · sweep_rates {len(S):,} · pullback_rates {len(P):,} · markdays per coin (raw) shipped",
    "top sweep cells by n (n>=200):"]+[f"  {r.coin} {r.label}={r.label_value} {r.mark} {r.ruler} p<={r.p_max} r>={r.r_min}: {r.rate:.3f} (n={r.n})" for r in top.itertuples()]+[
    "NAMED: labels carry their parameters in the column name — every claim re-runnable at other values; three rulers on sweep (U, ATR1d, DAYRNG = the day's own range — the structural one); structural + ATR1d on pullback; d5/d6 na beyond b0 window (n printed); pullback (b)-lines = retrace vs running leg, legs guarded to >=25% of the day final leg (structural) + ATR1d ruler; PDC==ONC by construction (both segments end at the same pre-08:00 bar) so their cells duplicate; verdicts are Svet's, files only report counts."]
    open(f'{OUT}/REPORT.md','w').write('\n'.join(lines))
print('B1 DAYCHAR',' COMPLETE' if len(st['done'])==4 else f' partial {st["done"]} — run again')
