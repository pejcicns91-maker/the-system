#!/usr/bin/env python3
"""c1_combos.py — LAYER C v1: dial COMBINATIONS (pairs + triples) at the anchor.
Reading (stated): combines each component's offset-0 reading (last completed bar before touch)
plus day-cadence dials; deeper-offset combos are a later expansion, named not folded.
Outputs -> results/layerc/: dials_{COIN}.parquet (RAW per-anchor dial matrix — rule 3;
makes any future k-way combo a one-line groupby) · combo_pairs.parquet · combo_triples.parquet
(cells with n>=50; floor declared) · REPORT.md. Cursor-resumable per coin."""
import pandas as pd, numpy as np, json, os, time, argparse
from itertools import combinations
ap=argparse.ArgumentParser(); ap.add_argument('--budget-min',type=float,default=230)
A,_=ap.parse_known_args(); T0=time.time()
COINS=['BTC','ETH','SOL','XRP']; REC='results/record'; LB='results/layerb'; OUT='results/layerc'
os.makedirs(OUT,exist_ok=True); os.makedirs('results/state',exist_ok=True)
SF='results/state/c1_combos.json'; st=json.load(open(SF)) if os.path.exists(SF) else {'done':[]}
FLOOR=50
BINS={'rsi':[0,30,40,50,60,70,101],'rng_x':[0,0.7,1.0,1.5,1e9],'close_pos':[-0.01,0.33,0.66,1.01],
'relvol':[0,0.7,1.5,3,1e9],'bars_in':[0,6,20,50,1e9],'flips100':[0,3,6,10,1e9]}
def bn(name,v):
    e=BINS[name]; b=np.digitize(v,e)-1
    lab=np.array([f"{e[i]}-{e[i+1]}" for i in range(len(e)-1)]+['na'])
    return lab[np.where(np.isfinite(v),np.clip(b,0,len(e)-2),len(e)-1)]
def at0(fr,t0,col):
    dta=pd.to_datetime(fr.dt,utc=True).to_numpy()
    pos=np.searchsorted(dta,t0,'right')-2; ok=pos>=0
    v=fr[col].to_numpy()[np.clip(pos,0,len(fr)-1)]
    return v,ok
PP=[];TT=[]
for coin in COINS:
    if coin in st['done']: print(coin,'done'); continue
    if (time.time()-T0)/60>A.budget_min-8: print('budget; resume'); break
    AN=pd.read_parquet(f'{LB}/anchors_{coin}.parquet'); t0=pd.to_datetime(AN.t0,utc=True).to_numpy()
    F={k:pd.read_parquet(f'{REC}/bars_{coin}_{k}.parquet') for k in ['5m','15m','1h','4h']}
    D=pd.read_parquet(f'{REC}/bars_{coin}_1D.parquet').assign(w=lambda d:d.wdate.astype(str)).set_index('w')
    X=pd.DataFrame({'cb':AN.closeback.to_numpy(),'pl':AN.play_atr.to_numpy(),'mark':AN['mark'].to_numpy()})
    def add(nm,fr,col,binname=None):
        v,ok=at0(fr,t0,col)
        if binname: s=bn(binname,v.astype(float))
        else: s=v.astype(str)
        X[nm]=np.where(ok,s,'na')
    add('h4_state',F['4h'],'hy_state'); add('h4_rsi',F['4h'],'hy_rsi','rsi'); add('h4_barsin',F['4h'],'hy_bars_in','bars_in')
    if 'btc_state' in F['4h'].columns: add('btc4',F['4h'],'btc_state')
    add('h1_state',F['1h'],'hy_state'); add('h1_rsi',F['1h'],'hy_rsi','rsi')
    add('m15_state',F['15m'],'hy_state'); add('m15_rsi',F['15m'],'rsi','rsi'); add('m15_rngx',F['15m'],'rng_x','rng_x')
    add('m5_rsi',F['5m'],'rsi','rsi'); add('m5_rngx',F['5m'],'rng_x','rng_x'); add('m5_relvol',F['5m'],'relvol','relvol')
    add('m5_cpos',F['5m'],'close_pos','close_pos'); add('sess',F['5m'],'session')
    j=D.reindex(AN.wdate.astype(str))
    for nm,col in [('pi','pi_state'),('hy_day','hayden_daily_anchor'),('yd','yd_arch'),('ob55','ob55_open')]:
        X[nm]=j[col].astype(str).to_numpy()
    X['wknd']=(pd.to_datetime(AN.wdate).dt.dayofweek>=5).astype(str)
    X.to_parquet(f'{OUT}/dials_{coin}.parquet',compression='zstd',index=False)
    dials=[c for c in X.columns if c not in ('cb','pl','mark')]
    for k,sink in [(2,PP),(3,TT)]:
        for combo in combinations(dials,k):
            g=X.groupby(list(combo),observed=True).agg(n=('cb','size'),n_cb=('cb','sum'),n_pl=('pl','sum')).reset_index()
            g=g[g.n>=FLOOR]
            if len(g)==0: continue
            g['combo']=' + '.join(combo)
            g['bins']=g[list(combo)].astype(str).agg(' | '.join,axis=1)
            sink.append(g[['combo','bins','n','n_cb','n_pl']].assign(coin=coin))
    st['done'].append(coin); json.dump(st,open(SF,'w')); print('DONE',coin,len(AN),flush=True)
def flush(lst,name):
    if not lst: return None
    df=pd.concat(lst,ignore_index=True); old=f'{OUT}/{name}.parquet'
    if os.path.exists(old): df=pd.concat([pd.read_parquet(old),df]).drop_duplicates(subset=['coin','combo','bins'],keep='last')
    df.to_parquet(old,compression='zstd',index=False); return df
P2=flush(PP,'combo_pairs'); P3=flush(TT,'combo_triples')
if P2 is not None:
    base=P2.groupby('coin').apply(lambda g:g.n_cb.sum()/g.n.sum(),include_groups=False).rename('b').reset_index()
    for df,nm in [(P2,'pairs'),(P3,'triples')]:
        if df is None: continue
        d=df.merge(base,on='coin'); d['r']=d.n_cb/d.n; d['lift']=(d.r-d.b)
        top=d[d.n>=300].assign(al=lambda x:x.lift.abs()).sort_values('al',ascending=False).head(8)
        lines=[f"top {nm} by |lift| (n>=300):"]+[f"  {r.coin} [{r.combo}] {r.bins}: {r.r:.3f} vs {r.b:.3f} (n={r.n})" for r in top.itertuples()]
        open(f'{OUT}/REPORT.md','a').write('\n'.join([f"# LAYERC — {pd.Timestamp.now(tz='UTC')}"]+lines+["floor n>=50; offset-0 reading declared; raw dial matrices shipped per coin.\n"]))
print('C1',' COMPLETE' if len(st['done'])==4 else f' partial {st["done"]} — run again')
