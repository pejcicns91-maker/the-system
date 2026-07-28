# Widened ladder: all d1-d4 stacks involving >=1 of the 6 new B0 columns. FE 19->25.
# 6+129+1331+8774 = 10,240 combos x station x 2 families. Checkpointed. Seed 20260723.
import numpy as np, pandas as pd, json, os, time
from itertools import combinations
np.random.seed(20260723)
CK="ckpt_b0x"; os.makedirs(CK,exist_ok=True); BLOCK=250
V=pd.read_parquet("bf_vantage_ALL_wide.parquet")
V['bounce']=(V.fwd_favU>=0.25)&(V.fwd_advU<0.25); V['through']=V.fwd_advU>=0.6
for col,q in [('dq','distU'),('sq','speedUh'),('vq','relvol'),('wq','widthU'),('rq','rng_used'),('kq','wk_used'),('uq','u_trend')]:
    try: V[col]=pd.qcut(pd.to_numeric(V[q],errors='coerce'),4,duplicates='drop')
    except Exception: V[col]=np.nan
V['cb']=pd.cut(V.contact,[-1,30,49.5,101],labels=['c<30','c30-49','c>=50'])
V['tn']=pd.cut(pd.to_numeric(V.test_no,errors='coerce'),[0,1,2,99],labels=['t1','t2','t3+'])
FE=['coin','etype','zone','virgin','cb','wq','session','wknd','hayden','hayden_btc','btc_pi','origin','tn','dq','sq','vq','rq','kq','uq',
    'yd_arch','ob55','dtype','lean','scen_state','scen_failed']
codes={};labels={}
for f in ['station']+FE:
    s=V[f]
    if isinstance(s.dtype,pd.CategoricalDtype):
        codes[f]=s.cat.codes.to_numpy(np.int32); labels[f]=[str(x) for x in s.cat.categories]
    else:
        c,u=pd.factorize(s,use_na_sentinel=True); codes[f]=c.astype(np.int32); labels[f]=[str(x) for x in u]
card={f:len(labels[f]) for f in codes}
b_arr=V.bounce.to_numpy(bool); t_arr=V.through.to_numpy(bool)
NEW=set(range(19,25))
combos=[]
for k in range(1,5):
    for c in combinations(range(25),k):
        if set(c)&NEW: combos.append((k,c))
assert len(combos)==10240, len(combos)
blocks=[combos[i:i+BLOCK] for i in range(0,len(combos),BLOCK)]
sf=f"{CK}/state.json"; done=json.load(open(sf))['done'] if os.path.exists(sf) else 0
t0=time.time()
for bi in range(done,len(blocks)):
    rows=[];ext=[]
    for depth,combo in blocks[bi]:
        cols=['station']+[FE[i] for i in combo]
        cm=np.stack([codes[c] for c in cols]); mask=(cm>=0).all(axis=0)
        dims=[card[c] for c in cols]; idx=np.ravel_multi_index(tuple(cm[:,mask]),dims); Mn=int(np.prod(dims))
        n_=np.bincount(idx,minlength=Mn); sel=np.nonzero(n_>=40)[0]
        ext.append((depth,'|'.join(cols[1:]),len(sel)))
        if not len(sel): continue
        kb=np.bincount(idx[b_arr[mask]],minlength=Mn)[sel]; kt=np.bincount(idx[t_arr[mask]],minlength=Mn)[sel]
        uidx=np.unravel_index(sel,dims)
        lab=[np.array(labels[c],dtype=object)[uidx[d]] for d,c in enumerate(cols)]
        head=['|'.join(x) for x in zip(*[lab[d] for d in range(len(cols)-1)])]
        f1='|'.join(cols[:-1]); f2=cols[-1]
        for r in range(len(sel)):
            rows.append((depth,f1,head[r],f2,lab[-1][r],int(kb[r]),int(kt[r]),int(n_[sel][r])))
    pd.DataFrame(rows,columns=['depth','f1','v1','f2','v2','kb','kt','n']).to_parquet(f"{CK}/blk_{bi:03d}.parquet",index=False)
    pd.DataFrame(ext,columns=['depth','combo','cells']).to_parquet(f"{CK}/ext_{bi:03d}.parquet",index=False)
    json.dump({'done':bi+1},open(sf,'w'))
    print(f"block {bi+1}/{len(blocks)} {time.time()-t0:.0f}s",flush=True)
print("counting complete" if done<len(blocks) or True else "")
