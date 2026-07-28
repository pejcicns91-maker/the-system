import numpy as np, pandas as pd, glob
from scipy import stats
from scipy.stats import binom
SEED=20260723
V=pd.read_parquet("bf_vantage_ALL_wide.parquet",columns=['fwd_favU','fwd_advU'])
base_b=float(((V.fwd_favU>=0.25)&(V.fwd_advU<0.25)).mean()); base_t=float((V.fwd_advU>=0.6).mean()); del V
NB=len(glob.glob("ckpt_b0x/blk_*.parquet"))
N=pd.concat([pd.read_parquet(f"ckpt_b0x/blk_{i:03d}.parquet",columns=['depth','kb','kt','n']) for i in range(NB)],ignore_index=True)
kb=N.kb.to_numpy(np.int64); kt=N.kt.to_numpy(np.int64); n_=N.n.to_numpy(np.int64); dep=N.depth.to_numpy(np.int8); del N
def pvec(k,n,p0):
    out=np.empty(len(k)); order=np.argsort(n,kind='stable')
    ns=n[order]; ks=k[order]
    uq,starts=np.unique(ns,return_index=True); ends=np.append(starts[1:],len(ns))
    for nv,a,b in zip(uq,starts,ends):
        pmf=binom.pmf(np.arange(nv+1),nv,p0); d=pmf[ks[a:b]]*(1+1e-7)
        sp=np.sort(pmf); cs=np.cumsum(sp); pos=np.searchsorted(sp,d,side='right')
        out[order[a:b]]=np.minimum(np.where(pos>0,cs[np.maximum(pos-1,0)],0.0),1.0)
    return out
p_b=pvec(kb,n_,base_b); print("p_b done",flush=True)
p_t=pvec(kt,n_,base_t); print("p_t done",flush=True)
def bh(ps,q=0.10):
    m=len(ps); order=np.argsort(ps,kind='stable'); sp=ps[order]
    thr=q*np.arange(1,m+1)/m; sat=np.nonzero(sp<=thr)[0]
    kmax=int(sat[-1]+1) if len(sat) else 0
    ok=np.zeros(m,bool); ok[order[:kmax]]=True; return ok
cb=bh(p_b); ct=bh(p_t)
rng=np.random.default_rng(SEED); ix=rng.choice(len(n_),200,replace=False)
d1=max(abs(stats.binomtest(int(kb[i]),int(n_[i]),base_b).pvalue-p_b[i]) for i in ix)
d2=max(abs(stats.binomtest(int(kt[i]),int(n_[i]),base_t).pvalue-p_t[i]) for i in ix)
np.savez("b0x_num.npz",p_b=p_b,p_t=p_t,cb=cb,ct=ct,base_b=base_b,base_t=base_t,maxdiff=max(d1,d2),dep=dep,n_=n_)
print("numeric cached | cells",len(n_),"| val maxdiff %.2e"%max(d1,d2),flush=True)
