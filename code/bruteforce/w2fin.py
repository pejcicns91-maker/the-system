# W2 streaming finalize — exact binomial p + exact BH q=.10/family over 428M cells on a 4GB box.
# Stages in fin_state.json: A (per-file p + histograms) -> B (exact t* per family) -> C (outputs).
# Exactness: p per cell = same minlike two-sided binomial; BH threshold t* found exactly via
# histogram bracket + sliver enumeration (boundary never splits a tie group, proven earlier).
import numpy as np, pandas as pd, glob, os, json, time, hashlib, sys
from scipy.stats import binom
SEED=20260723
ST="fin_state.json"; PD="w2_p"; os.makedirs(PD,exist_ok=True)
st=json.load(open(ST)) if os.path.exists(ST) else {"stage":"A","cursor":0}
FAMS=["bounce","through","b50","fastres"]
KC={"bounce":"kb","through":"kt","b50":"k5","fastres":"kf"}
def bases():
    if os.path.exists("fin_bases.json"): return json.load(open("fin_bases.json"))
    Vw=pd.read_parquet("bf_vantage_ALL_wide.parquet",columns=['fwd_favU','fwd_advU'])
    V2=pd.read_parquet("bf_w2cols.parquet",columns=['b50','fastres'])
    b={"bounce":float(((Vw.fwd_favU>=0.25)&(Vw.fwd_advU<0.25)).mean()),
       "through":float((Vw.fwd_advU>=0.6).mean()),
       "b50":float(V2.b50.mean()),"fastres":float(V2.fastres.mean())}
    json.dump(b,open("fin_bases.json","w")); return b
B=bases()
EDGES=np.linspace(-350,0,70001)   # log10 p bins
cnt=sorted(glob.glob("w2_counts/cnt_*.parquet"))

_CACHE={}; _CB=[0]
def tables(nv,f):
    key=(nv,f)
    if key in _CACHE: return _CACHE[key]
    ar=np.arange(nv+1); pmf=binom.pmf(ar,nv,B[f]); cdf=np.cumsum(pmf)
    tup=(pmf,cdf,int(np.argmax(pmf)))
    if _CB[0]>350_000_000: _CACHE.clear(); _CB[0]=0
    _CACHE[key]=tup; _CB[0]+=pmf.nbytes*2
    return tup
def minlike(k,nv,f):
    pmf,cdf,mode=tables(nv,f)
    d=pmf[k]*(1+1e-7); out=np.empty(len(k))
    left=k<mode; right=k>mode; mid=~left&~right
    out[mid]=1.0
    if left.any():
        kl=k[left]
        tail=pmf[mode:]                       # decreasing
        j=mode+np.searchsorted(-tail,-d[left],side='left')
        lo=cdf[kl]
        hi=np.where(j>=1,1.0-cdf[np.minimum(j-1,nv)],1.0)
        hi=np.where(j>nv,0.0,hi)
        out[left]=lo+hi
    if right.any():
        kr=k[right]
        head=pmf[:mode+1]                     # increasing
        j=np.searchsorted(head,d[right],side='right')-1
        lo=np.where(j>=0,cdf[np.maximum(j,0)],0.0)
        hi=1.0-cdf[kr-1]
        out[right]=lo+hi
    return np.minimum(out,1.0)
def pfile(path):
    D=pd.read_parquet(path,columns=['depth','kb','kt','k5','kf','n'])
    n=D.n.to_numpy(np.int64)
    o=np.argsort(n,kind='stable'); ns=n[o]
    uq,a=np.unique(ns,return_index=True); b2=np.append(a[1:],len(ns))
    out={f:np.empty(len(n)) for f in FAMS}
    ks={f:D[KC[f]].to_numpy(np.int64)[o] for f in FAMS}
    for nv,i0,i1 in zip(uq,a,b2):
        for f in FAMS:
            out[f][o[i0:i1]]=minlike(ks[f][i0:i1],int(nv),f)
    R=pd.DataFrame({("p_"+f):out[f] for f in FAMS})
    R["n"]=D.n.astype(np.int32); R["depth"]=D.depth.astype(np.int8)
    return R

if st["stage"]=="A":
    todo=[p for p in cnt if not os.path.exists(os.path.join(PD,os.path.basename(p)))]
    t0=time.time(); done=len(cnt)-len(todo)
    for pth in todo:
        R=pfile(pth); R.to_parquet(os.path.join(PD,os.path.basename(pth)),index=False)
        done+=1
        if done%100==0: print(f"A {done}/{len(cnt)} {time.time()-t0:.0f}s",flush=True)
        if time.time()-t0>235: break
    if len(glob.glob(f"{PD}/cnt_*.parquet"))>=len(cnt):
        H={f:np.zeros(70000,np.int64) for f in FAMS}
        for pth in glob.glob(f"{PD}/cnt_*.parquet"):
            P=pd.read_parquet(pth,columns=[("p_"+f) for f in FAMS])
            for f in FAMS:
                H[f]+=np.histogram(np.log10(np.maximum(P["p_"+f].to_numpy(),1e-320)),bins=EDGES)[0]
        np.savez("fin_hist.npz",H=H)
        st["stage"]="B"; st["cursor"]=0
    json.dump(st,open(ST,"w"))
    print("stage A:",len(glob.glob(f"{PD}/cnt_*.parquet")),"/",len(cnt),flush=True)

elif st["stage"]=="B":
    H=np.load("fin_hist.npz",allow_pickle=True)["H"].item()
    q=0.10; m=int(H["bounce"].sum()); ts={}
    for f in FAMS:
        cum=np.cumsum(H[f])                      # G at upper edges
        e=EDGES[1:]                               # log10 upper edges
        pred=(10.0**e)<=q*cum/m
        hi_i=int(np.nonzero(pred)[0].max())       # last bin whose upper edge satisfies
        lo=10.0**EDGES[max(hi_i-1,0)]; hi=10.0**EDGES[min(hi_i+2,70000)]
        Glo=int(cum[max(hi_i-2,0)])               # exact count <= edge below bracket
        cand=[]
        for pth in sorted(glob.glob(f"{PD}/cnt_*.parquet")):
            v=pd.read_parquet(pth,columns=["p_"+f])["p_"+f].to_numpy()
            cand.append(v[(v>10.0**EDGES[max(hi_i-2,0)])&(v<=hi)])
        cv=np.sort(np.concatenate(cand))
        best=0.0
        for j,t in enumerate(cv):
            G=Glo+np.searchsorted(cv,t,side='right')
            if t<=q*G/m: best=t
        ts[f]=float(best)
        print(f"t* {f}: {best:.6g} (bracket size {len(cv):,})",flush=True)
    json.dump({"m":m,"tstar":ts},open("fin_tstar.json","w"))
    st["stage"]="C"; st["cursor"]=0; json.dump(st,open(ST,"w"))

elif st["stage"]=="C":
    TS=json.load(open("fin_tstar.json")); ts=TS["tstar"]
    ck="fin_c.npz"
    if os.path.exists(ck):
        Z=np.load(ck,allow_pickle=True); dig=Z["dig"].item(); summ=Z["summ"].item(); val=Z["val"].item()
    else:
        dig={f:[] for f in FAMS}; summ={}; val={"maxdiff":0.0,"n":0}
    rng=np.random.default_rng(SEED)
    t0=time.time(); i=st["cursor"]
    while i<len(cnt) and time.time()-t0<200:
        pth=cnt[i]; D=pd.read_parquet(pth); P=pd.read_parquet(os.path.join(PD,os.path.basename(pth)))
        for f in FAMS:
            pv=P["p_"+f].to_numpy(); cert=pv<=ts[f]
            for d in np.unique(D.depth):
                m2=(D.depth.values==d)
                key=(f,int(d)); c0,c1=summ.get(key,(0,0))
                summ[key]=(c0+int(m2.sum()), c1+int((cert&m2).sum()))
            m3=cert&(D.n.values>=100)
            if m3.any():
                dd=D[m3].copy(); dd["rate"]=np.round(dd[KC[f]]/dd.n,3); dd["base"]=round(B[f],3)
                dd["family"]=f; dd["lift"]=(dd.rate-dd.base).abs()
                dig[f].append(dd.nlargest(min(400,len(dd)),"lift")[["family","depth","f1","v1","f2","v2","rate","base","n","lift"]])
        if val["n"]<200 and len(D):
            from scipy import stats
            j=int(rng.integers(len(D))); f=FAMS[int(rng.integers(4))]
            pd_=stats.binomtest(int(D[KC[f]].iloc[j]),int(D.n.iloc[j]),B[f]).pvalue
            val["maxdiff"]=max(val["maxdiff"],abs(pd_-float(P["p_"+f].iloc[j]))); val["n"]+=1
        i+=1
        if i%150==0:
            for f in FAMS:
                if len(dig[f])>40: dig[f]=[pd.concat(dig[f],ignore_index=True).nlargest(4000,"lift")]
            print(f"C {i}/{len(cnt)} {time.time()-t0:.0f}s",flush=True)
    np.savez(ck,dig={f:[pd.concat(dig[f],ignore_index=True)] if dig[f] else [] for f in FAMS},summ=summ,val=val)
    st["cursor"]=i
    if i>=len(cnt):
        DG=pd.concat([pd.concat(dig[f],ignore_index=True) for f in FAMS if dig[f]],ignore_index=True)
        deps=sorted(set(int(k[1]) for k in summ))
        DG=pd.concat([DG[(DG.family==f)&(DG.depth==d)].nlargest(200,"lift") for f in FAMS for d in deps],ignore_index=True)
        DG.drop(columns=["lift"]).to_csv("w2_digest.csv",index=False)
        E=pd.concat([pd.read_parquet(p) for p in sorted(glob.glob("w2_counts/ext_*.parquet"))],ignore_index=True)
        E["extinct"]=E.cells==0; E.to_csv("w2_extinction.csv",index=False)
        S=pd.DataFrame([dict(family=f,depth=d,cells=summ[(f,d)][0],cert=summ[(f,d)][1]) for (f,d) in sorted(summ)])
        S.to_csv("w2_summary.csv",index=False)
        print("FINALIZED | m",f"{TS['m']:,}","| t*",{k:round(v,6) for k,v in ts.items()},"| scipy check",f"{val['maxdiff']:.2e} over {val['n']}")
        for fn in ["w2_digest.csv","w2_extinction.csv","w2_summary.csv"]:
            print(fn,"sha",hashlib.sha256(open(fn,'rb').read()).hexdigest()[:12])
        st["stage"]="done"
    json.dump(st,open(ST,"w"))
    print("stage C:",i,"/",len(cnt),flush=True)
else:
    print("done")
