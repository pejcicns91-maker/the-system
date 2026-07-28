#!/usr/bin/env python3
"""b2_offsets.py — LAYER B bar grain: EVERY COMPONENT ALONE x EVERY OFFSET (0..99) x EVERY TF.
Anchors: first 5m bar whose range contains each ET period mark, per coin-day ((b)-line).
Offset 0 = last COMPLETED bar strictly before the touch bar ((b)-line: no within-bar peek).
Outcomes per anchor (raw $ kept per rule 3; rulers re-derivable): pen, rev_after, close_side
 + profiled flags: closeback (ruler-free) and play_atr (pen<=0.25*ATR1d & rev>=0.25*ATR1d).
Outputs -> results/layerb/: anchors_{COIN}.parquet (RAW) · profile_offsets.parquet ·
profile_day.parquet · profile_shape.parquet · REPORT.md. Cursor-resumable per coin."""
import pandas as pd, numpy as np, json, os, sys, time, argparse
ap=argparse.ArgumentParser(); ap.add_argument('--budget-min',type=float,default=230)
A,_=ap.parse_known_args(); T0=time.time()
COINS=['BTC','ETH','SOL','XRP']; REC='results/record'; OUT='results/layerb'
os.makedirs(OUT,exist_ok=True); os.makedirs('results/state',exist_ok=True)
SF='results/state/b2_offsets.json'; st=json.load(open(SF)) if os.path.exists(SF) else {'done':[]}
DTEST=int(os.environ.get('TEST_DAYS','0')); K=100
BINS={'rsi':[0,30,40,50,60,70,101],'rng_x':[0,0.7,1.0,1.5,1e9],'close_pos':[-0.01,0.33,0.66,1.01],
'body_frac':[-0.01,0.33,0.66,1.01],'volr':[0,0.8,1.2,1e9],'relvol':[0,0.7,1.5,3,1e9]}
def binify(name,v):
    if name in BINS:
        e=BINS[name]; b=np.digitize(v,e)-1
        lab=np.array([f"{e[i]}-{e[i+1]}" for i in range(len(e)-1)]+['na'])
        b=np.where(np.isfinite(v),np.clip(b,0,len(e)-2),len(e)-1); return lab[b]
    return v.astype(str)
def outcomes(f5,D,MP):
    rows=[]; g5=dict(list(f5.groupby('wdate'))); mp=MP[MP.conv=='ET']
    mbd=dict(list(mp.groupby('wdate')))
    for _,d in D.iterrows():
        g=g5.get(d.wdate); mk=mbd.get(str(d.wdate))
        if g is None or mk is None: continue
        h=g.h.to_numpy(); l=g.l.to_numpy(); dts=g.dt.to_numpy(); o=float(d.o); c=float(d.c)
        for _,m in mk.iterrows():
            mpx=float(m['price'])
            if not np.isfinite(mpx): continue
            hit=np.nonzero((h>=mpx)&(l<=mpx))[0]
            if len(hit)==0: continue
            i0=int(hit[0])
            if o>=mpx:
                pen=max(0.0,mpx-l.min()); j=int(l.argmin()); rev=float(h[j:].max()-mpx) if pen>0 else np.nan; side=1
            else:
                pen=max(0.0,h.max()-mpx); j=int(h.argmax()); rev=float(mpx-l[j:].min()) if pen>0 else np.nan; side=-1
            cb=int(np.sign(c-mpx)==np.sign(o-mpx) and o!=mpx)
            rows.append((str(d.wdate),m['name'],mpx,dts[i0],side,pen,rev,cb,float(d.atr14_1d) if pd.notna(d.atr14_1d) else np.nan,float(d.uabs) if pd.notna(d.uabs) else np.nan))
    return pd.DataFrame(rows,columns=['wdate','mark','price','t0','open_side','pen','rev_after','closeback','atr1d','uabs'])
POf=[];PDy=[];PSh=[]
for coin in COINS:
    if coin in st['done']: print(coin,'done'); continue
    if (time.time()-T0)/60>A.budget_min-8: print('budget; resume'); break
    D=pd.read_parquet(f'{REC}/bars_{coin}_1D.parquet')
    if DTEST: D=D.tail(DTEST).reset_index(drop=True)
    MP=pd.read_parquet(f'{REC}/marks_periods_{coin}.parquet')
    f5=pd.read_parquet(f'{REC}/bars_{coin}_5m.parquet')
    f5=f5[f5.wdate.isin(set(D.wdate))]
    AN=outcomes(f5[['dt','h','l','wdate']].assign(dt=pd.to_datetime(f5.dt,utc=True)),D,MP)
    AN['t0']=pd.to_datetime(AN.t0,utc=True)
    AN['play_atr']=((AN.pen>0)&(AN.pen<=0.25*AN.atr1d)&(AN.rev_after>=0.25*AN.atr1d)).astype(int)
    AN.to_parquet(f'{OUT}/anchors_{coin}.parquet',compression='zstd',index=False)
    t0=AN.t0.to_numpy(); ncb=AN.closeback.to_numpy(); npl=AN.play_atr.to_numpy()
    frames={'5m':f5,'15m':pd.read_parquet(f'{REC}/bars_{coin}_15m.parquet'),'1h':pd.read_parquet(f'{REC}/bars_{coin}_1h.parquet'),'4h':pd.read_parquet(f'{REC}/bars_{coin}_4h.parquet')}
    for tfk,fr in frames.items():
        fr=fr.copy(); fr['dt']=pd.to_datetime(fr.dt,utc=True); dta=fr.dt.to_numpy()
        pos=np.searchsorted(dta,t0,'right')-2  # last completed bar before touch bar
        comps=[c for c in ['hy_state','rsi','rng_x','close_pos','body_frac','hl_tok','volr','relvol','div_bull','div_bear','session'] if c in fr.columns]
        if tfk=='4h' and 'btc_state' in fr.columns: comps.append('btc_state')
        offs=np.arange(K); IDX=pos[:,None]-offs[None,:]
        valid=IDX>=0; IDXc=np.clip(IDX,0,len(fr)-1)
        for cname in comps:
            V=fr[cname].to_numpy()[IDXc]
            if V.dtype!=object and V.dtype!=bool: Vb=binify(cname,V.astype(float))
            else: Vb=V.astype(str)
            Vb=np.where(valid,Vb,'na')
            df=pd.DataFrame({'offset':np.broadcast_to(offs,IDX.shape).ravel(),'bin':Vb.ravel(),
                'cb':np.repeat(ncb,K),'pl':np.repeat(npl,K)})
            g=df[df['bin']!='na'].groupby(['offset','bin']).agg(n=('cb','size'),n_cb=('cb','sum'),n_pl=('pl','sum')).reset_index()
            g['coin']=coin; g['tf']=tfk; g['component']=cname; POf.append(g)
        # shape trio at anchor (offset0): bars_in_state native col; flips/div/slope-run over trailing 100
        if 'hy_state' in fr.columns:
            stt=fr['hy_state'].to_numpy(); flips=(stt[1:]!=stt[:-1]).astype(int); flips=np.concatenate([[0],flips])
            cf=np.cumsum(flips); cb_=np.cumsum(fr['div_bull'].to_numpy().astype(int)); cs_=np.cumsum(fr['div_bear'].to_numpy().astype(int))
            sl=np.sign(np.nan_to_num(fr['hy_rsi_slope'].to_numpy())) if 'hy_rsi_slope' in fr.columns else np.zeros(len(fr))
            run=np.zeros(len(fr),int)
            for i in range(1,len(fr)): run[i]=run[i-1]+1 if sl[i]==sl[i-1] and sl[i]!=0 else (1 if sl[i]!=0 else 0)
            p0=np.clip(pos,0,len(fr)-1); pK=np.clip(pos-K,0,len(fr)-1)
            sh=pd.DataFrame({'flips100':cf[p0]-cf[pK],'divb100':cb_[p0]-cb_[pK],'divs100':cs_[p0]-cs_[pK],
                'bars_in':fr['hy_bars_in'].to_numpy()[p0],'slope_run':run[p0],'cb':ncb,'pl':npl})
            for cname,edges in [('flips100',[0,3,6,10,1e9]),('divb100',[0,2,5,1e9]),('divs100',[0,2,5,1e9]),('bars_in',[0,6,20,50,1e9]),('slope_run',[0,3,6,1e9])]:
                b=np.digitize(sh[cname],edges)-1; lab=[f"{edges[i]}-{edges[i+1]}" for i in range(len(edges)-1)]
                sh['bin']=np.array(lab)[np.clip(b,0,len(lab)-1)]
                g=sh.groupby('bin').agg(n=('cb','size'),n_cb=('cb','sum'),n_pl=('pl','sum')).reset_index()
                g['coin']=coin; g['tf']=tfk; g['component']=cname; PSh.append(g)
    Dk=D.assign(w=D.wdate.astype(str)).set_index('w')
    j=AN.join(Dk[['pi_state','hayden_daily_anchor','d5_dtype','lean_dir','yd_arch','ob55_open','d6_ob55_fired']],on='wdate')
    for cname in ['pi_state','hayden_daily_anchor','d5_dtype','lean_dir','yd_arch','ob55_open','d6_ob55_fired']:
        g=j.assign(bin=j[cname].astype(str)).groupby('bin').agg(n=('closeback','size'),n_cb=('closeback','sum'),n_pl=('play_atr','sum')).reset_index()
        g['coin']=coin; g['component']=cname; PDy.append(g)
    st['done'].append(coin); json.dump(st,open(SF,'w')); print('DONE',coin,len(AN),'anchors',flush=True)
def flush(lst,name,keys):
    if not lst: return None
    df=pd.concat(lst,ignore_index=True); old=f'{OUT}/{name}.parquet'
    if os.path.exists(old): df=pd.concat([pd.read_parquet(old),df]).drop_duplicates(subset=keys,keep='last')
    df.to_parquet(old,compression='zstd',index=False); return df
Po=flush(POf,'profile_offsets',['coin','tf','component','offset','bin'])
Pd=flush(PDy,'profile_day',['coin','component','bin']); Ps=flush(PSh,'profile_shape',['coin','tf','component','bin'])
if Po is not None:
    base=Po.groupby(['coin','tf'])[['n','n_cb']].sum(); base['b']=base.n_cb/base.n
    Po2=Po.merge(base['b'],on=['coin','tf']); Po2['rate']=Po2.n_cb/Po2.n; Po2['lift']=(Po2.rate-Po2.b).abs()
    top=Po2[Po2.n>=2000].sort_values('lift',ascending=False).drop_duplicates(['coin','tf','component']).head(12)
    lines=[f"# LAYERB OFFSETS REPORT — {pd.Timestamp.now(tz='UTC')}",
    f"profile_offsets {len(Po):,} cells · profile_day {0 if Pd is None else len(Pd):,} · profile_shape {0 if Ps is None else len(Ps):,}",
    "top closeback lifts by |rate-base| (cells n>=2000):"]+[f"  {r.coin} {r.tf} {r.component} off{r.offset} bin {r.bin}: {r.rate:.3f} vs {r.b:.3f} (n={r.n})" for r in top.itertuples()]+[
    "(b)-LINES: anchor=first 5m bar containing the mark; offset0=last completed bar before touch; fixed bins as coded; outcomes raw in anchors_ files — any ruler re-derivable. Counts only; verdicts are Svet's."]
    open(f'{OUT}/REPORT.md','w').write('\n'.join(lines))
print('B2',' COMPLETE' if len(st['done'])==4 else f' partial {st["done"]} — run again')
