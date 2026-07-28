#!/usr/bin/env python3
"""c2_seqpairs.py — CONTRACT ITEM 2: SEQUENTIAL PAIRS. Every (component x offset 0..99) dial
crossed with every other, trimmed roster, all coins, DON-55 grain + day dials included.
NOTHING dropped: full per-cell ledger -> zip -> release asset 'ledgers' (Option A, signed).
Repo carries per-coin pair INDEX (pair_id, n, cells>=floor, separation) + dial dictionary + DECODE.
Floor n>=50 declared (cells below floor exist in counts but are not written; pair index counts them).
TEST_PAIR_STRIDE env = local pipeline test only; runner default = FULL grid."""
import pandas as pd, numpy as np, json, os, sys, time, argparse, subprocess, zipfile
ap=argparse.ArgumentParser(); ap.add_argument('--budget-min',type=float,default=230)
A,_=ap.parse_known_args(); T0=time.time()
COINS=['BTC','ETH','SOL','XRP']; REC='results/record'; LB='results/layerb'; OUT='results/layerc2'
os.makedirs(OUT,exist_ok=True); os.makedirs('results/state',exist_ok=True)
SF='results/state/c2.json'; st=json.load(open(SF)) if os.path.exists(SF) else {'done':[]}
STRIDE=int(os.environ.get('TEST_PAIR_STRIDE','1')); FLOOR=50
BINS={'rng_x':[0,0.7,1.0,1.5,1e9],'body_frac':[-.01,.33,.66,1.01],'uw_frac':[-.01,.2,.5,1.01],
'lw_frac':[-.01,.2,.5,1.01],'close_pos':[-.01,.33,.66,1.01],'volr':[0,.8,1.2,1e9],
'relvol':[0,.7,1.5,3,1e9],'bars_in_trade':[0,5,12,24,1e9],'unrealized_R':[-1e9,-0.5,0,0.5,1,1e9]}
CATS={'hy_state':['Chop','Bull','Bear'],'btc_state':['Chop','Bull','Bear'],
'hl_tok':['up','down','outside','inside'],'session':['asia','eu','us_open','lunch','us_close','evening'],
'pi_state':['up','down'],'hayden_daily_anchor':['Chop','Bull','Bear'],'yd_arch':['UP','DN','CHOP'],
'ob55_open':['False','True'],'wknd':['False','True'],'half_off':['False','True'],'skip_state':['False','True']}
def enc(name,vals):
    if name in BINS:
        e=BINS[name]; v=vals.astype(float); b=np.digitize(v,e)-1
        b=np.where(np.isfinite(v),np.clip(b,0,len(e)-2),len(e)-1); return b.astype(np.int8),len(e)-1
    cats=CATS[name]; mp={c:i for i,c in enumerate(cats)}
    b=np.array([mp.get(str(x),len(cats)) for x in vals],dtype=np.int8); return b,len(cats)
for coin in COINS:
    if coin in st['done']: print(coin,'done'); continue
    if (time.time()-T0)/60>A.budget_min-15: print('budget; resume'); break
    AN=pd.read_parquet(f'{LB}/anchors_{coin}.parquet'); t0=pd.to_datetime(AN.t0,utc=True).to_numpy()
    wcb=AN.closeback.to_numpy().astype(np.int32); wpl=AN.play_atr.to_numpy().astype(np.int32); NA=len(AN)
    codes=[]; nbs=[]; names=[]
    for tfk,comps in [('5m',['rng_x','body_frac','uw_frac','lw_frac','close_pos','hl_tok','volr','relvol','session']),
                      ('15m',['hy_state','rng_x','body_frac','uw_frac','lw_frac','close_pos','hl_tok','volr']),
                      ('1h',['hy_state','rng_x','body_frac','uw_frac','lw_frac','close_pos','hl_tok','volr']),
                      ('4h',['hy_state','rng_x','body_frac','uw_frac','lw_frac','close_pos','hl_tok','volr','btc_state'])]:
        fr=pd.read_parquet(f'{REC}/bars_{coin}_{tfk}.parquet')
        fr['dt']=pd.to_datetime(fr.dt,utc=True); dta=fr.dt.to_numpy()
        pos=np.searchsorted(dta,t0,'right')-2
        for cname in comps:
            if cname not in fr.columns: continue
            col=fr[cname].to_numpy()
            for k in range(0,100,STRIDE):
                idx=pos-k; ok=idx>=0; v=col[np.clip(idx,0,len(fr)-1)]
                b,nb=enc(cname,v); b=np.where(ok,b,nb).astype(np.int8)
                codes.append(b); nbs.append(nb); names.append(f'{tfk}.{cname}@{k}')
    D=pd.read_parquet(f'{REC}/bars_{coin}_1D.parquet').assign(w=lambda d:d.wdate.astype(str)).set_index('w')
    d5=pd.read_parquet(f'{REC}/d55_daily_{coin}.parquet').set_index('date')
    j=AN.wdate.astype(str)
    for cname,src in [('pi_state',D),('hayden_daily_anchor',D),('yd_arch',D),('wknd',None),
                      ('ob55_open',d5),('half_off',d5),('skip_state',d5),('bars_in_trade',d5),('unrealized_R',d5)]:
        if cname=='wknd': v=(pd.to_datetime(AN.wdate).dt.dayofweek>=5).astype(str).to_numpy()
        else: v=src[cname].reindex(j).astype(str if cname in CATS else float).to_numpy()
        b,nb=enc(cname,v); codes.append(b.astype(np.int8)); nbs.append(nb); names.append(f'day.{cname}@0')
    M=np.stack(codes,axis=1); nbs=np.array(nbs); Dn=M.shape[1]
    print(coin,'anchors',NA,'dials',Dn,'pairs',Dn*(Dn-1)//2,flush=True)
    base=wcb.mean()
    ip=[]; ic=[]; isep=[]; itot=[]
    ch_p=[];ch_c=[];ch_n=[];ch_b=[];ch_l=[]
    pid=0; t_last=time.time()
    for a in range(Dn-1):
        Ma=M[:,a].astype(np.int16); nba=nbs[a]
        for b_ in range(a+1,Dn):
            nbb=nbs[b_]; code=Ma*(nbb+1)+M[:,b_]
            K=(nba+1)*(nbb+1)
            n=np.bincount(code,minlength=K); ncb=np.bincount(code,weights=wcb,minlength=K)
            valid=np.zeros(K,bool); valid.reshape(nba+1,nbb+1)[:nba,:nbb]=True
            keep=(n>=FLOOR)&valid
            tot=int(n[valid].sum())
            if keep.any():
                r=ncb[keep]/n[keep]; sep=float((n[keep]*np.abs(r-base)).sum()/n[keep].sum())
                npl=np.bincount(code,weights=wpl,minlength=K)
                kk=np.nonzero(keep)[0]
                ch_p.append(np.full(len(kk),pid,np.int32)); ch_c.append(kk.astype(np.int16))
                ch_n.append(n[kk].astype(np.int32)); ch_b.append(ncb[kk].astype(np.int32)); ch_l.append(npl[kk].astype(np.int32))
            else: sep=0.0
            ip.append(pid); ic.append(int(keep.sum())); isep.append(sep); itot.append(tot); pid+=1
        if time.time()-t_last>120: print(f'  ..dial {a}/{Dn}',flush=True); t_last=time.time()
    IX=pd.DataFrame({'pair_id':np.array(ip,np.int32),'cells':np.array(ic,np.int16),
        'sep':np.array(isep,np.float32),'n_total':np.array(itot,np.int32)})
    IX.to_parquet(f'{OUT}/pair_index_{coin}.parquet',compression='zstd',index=False)
    pd.DataFrame({'dial_id':np.arange(Dn),'name':names,'nbins':nbs}).to_parquet(f'{OUT}/dials_dict_{coin}.parquet',index=False)
    CL=pd.DataFrame({'pair_id':np.concatenate(ch_p),'cell':np.concatenate(ch_c),
        'n':np.concatenate(ch_n),'n_cb':np.concatenate(ch_b),'n_pl':np.concatenate(ch_l)})
    cpath=f'/tmp/cells_{coin}.parquet'; CL.to_parquet(cpath,compression='zstd',index=False)
    zp=f'/tmp/cells_{coin}.zip'
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_STORED) as z: z.write(cpath,f'cells_{coin}.parquet')
    if os.environ.get('GITHUB_ACTIONS'):
        subprocess.run(['gh','release','create','ledgers','-t','Cell ledgers','-n','full per-cell pair ledgers'],capture_output=True)
        r=subprocess.run(['gh','release','upload','ledgers',zp,'--clobber'],capture_output=True,text=True)
        print('release upload:','OK' if r.returncode==0 else 'FAILED '+r.stderr[:200])
    else: print('local test: release upload skipped;',zp,os.path.getsize(zp),'bytes; cells rows',len(CL))
    st['done'].append(coin); json.dump(st,open(SF,'w')); print('DONE',coin,'| pairs',pid,'| cell rows',len(CL),flush=True)
open(f'{OUT}/DECODE.md','w').write("cells_{COIN}.parquet (release 'ledgers'): cell = codeA*(nbB+1)+codeB; bins per dial in dials_dict; last bin index = na (excluded). rate=n_cb/n; play=n_pl/n. Floor n>=50; below-floor cells counted in pair_index.n_total, not written.\n")
print('C2',' COMPLETE' if len(st['done'])==4 else f' partial {st["done"]} — run again')
