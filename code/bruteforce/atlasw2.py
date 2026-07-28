# ATLAS-W2 extraction — per-station certified top-K from the w2 register, exact t* applied.
# Stages (aw2_state.json): R (32 ranges, candidate shards) -> F (station fill via
# descending-lift string fetch) -> done. Curation per W2_SPEC: top-12 per station x family
# x source w2, certified n>=100; unfilled buckets reported with their lift-coverage floor.
import numpy as np, pandas as pd, glob, os, json, time
from scipy.stats import binom
SEED=20260723; np.random.seed(SEED)
ST="aw2_state.json"
st=json.load(open(ST)) if os.path.exists(ST) else {"stage":"R","cursor":0}
def sv(): json.dump(st,open(ST,"w"))
FAMS=["bounce","through","b50","fastres"]; KC={"bounce":"kb","through":"kt","b50":"k5","fastres":"kf"}
B=json.load(open("fin_bases.json")); TS=json.load(open("fin_tstar2.json"))["tstar"]
cnt=sorted(glob.glob("w2_counts/cnt_*.parquet"))
NB=32
def ranges():
    cuts=json.load(open("fin2_cuts.json"))
    edges=[0]+[cuts[j] for j in range(1,63,2)]+[10**9]
    return list(zip(edges[:-1],edges[1:]))
def load_ranges(rspecs):
    acc=[dict(Ns=[],Ks={f:[] for f in FAMS},Fid=[],Row=[],Dep=[]) for _ in rspecs]
    cols=["n","kb","kt","k5","kf","depth"]
    for fi,pth in enumerate(cnt):
        D=pd.read_parquet(pth,columns=cols)
        n=D.n.to_numpy(np.int32)
        kv={f:D[KC[f]].to_numpy(np.int32) for f in FAMS}
        dep=D.depth.to_numpy(np.int8)
        for a,(rlo,rhi) in zip(acc,rspecs):
            m=(n>=rlo)&(n<rhi)
            if not m.any(): continue
            a["Ns"].append(n[m])
            for f in FAMS: a["Ks"][f].append(kv[f][m])
            a["Fid"].append(np.full(int(m.sum()),fi,np.int16))
            a["Row"].append(np.nonzero(m)[0].astype(np.int32))
            a["Dep"].append(dep[m])
    out=[]
    for a in acc:
        if not a["Ns"]: out.append(None); continue
        out.append((np.concatenate(a["Ns"]),{f:np.concatenate(a["Ks"][f]) for f in FAMS},
                    np.concatenate(a["Fid"]),np.concatenate(a["Row"]),np.concatenate(a["Dep"])))
    return out

if st["stage"]=="R":
    t0=time.time(); j=st["cursor"]; RG=ranges()
    w=2 if j<30 else 1
    rc=f"aw2_rc{j}.npz"
    if w==1 and os.path.exists(rc):
        Z=np.load(rc)
        loaded=[(Z["n"],{f:Z[KC[f]] for f in FAMS},Z["fid"],Z["row"],Z["dep"])]
        print(f"  cache hit {len(Z['n']):,}",flush=True)
    else:
        loaded=load_ranges(RG[j:j+w])
    for tup in loaded:
        if tup is None: j+=1; continue
        n,ks,fid,row,dep=tup
        o=np.argsort(n,kind="stable")
        n=n[o]; fid=fid[o]; row=row[o]; dep=dep[o]
        for f in FAMS: ks[f]=ks[f][o]
        if w==1 and not os.path.exists(rc):
            np.savez(rc,n=n,fid=fid,row=row,dep=dep,**{KC[f]:ks[f] for f in FAMS})
        uq,a=np.unique(n,return_index=True); b2=np.append(a[1:],len(n))
        sub0=st.get("sub",0) if w==1 else 0
        TOP={f:[] for f in FAMS}
        def prune(force=False):
            for f in FAMS:
                if TOP[f] and (force or sum(len(x[0]) for x in TOP[f])>200_000):
                    fi_=np.concatenate([x[0] for x in TOP[f]]); rw=np.concatenate([x[1] for x in TOP[f]])
                    dp=np.concatenate([x[2] for x in TOP[f]]); rt=np.concatenate([x[3] for x in TOP[f]])
                    nn_=np.concatenate([x[4] for x in TOP[f]]); lf=np.concatenate([x[5] for x in TOP[f]])
                    if len(lf)>3000:
                        ix=np.argpartition(lf,-3000)[-3000:]
                        fi_,rw,dp,rt,nn_,lf=fi_[ix],rw[ix],dp[ix],rt[ix],nn_[ix],lf[ix]
                    TOP[f]=[(fi_,rw,dp,rt,nn_,lf)]
        def dump(tag):
            prune(True)
            fr=[]
            for f in FAMS:
                if not TOP[f]: continue
                fi_,rw,dp,rt,nn_,lf=TOP[f][0]
                fr.append(pd.DataFrame({"fid":fi_,"row":rw,"depth":dp,"family":f,"rate":rt,"n":nn_,"lift":lf}))
            if fr: pd.concat(fr,ignore_index=True).to_parquet(f"aw2_cand_{j}_{tag}.parquet",index=False)
        for gi,(nv,i0_,i1_) in enumerate(zip(uq,a,b2)):
            if gi<sub0: continue
            nv=int(nv); ar=np.arange(nv+1)
            for f in FAMS:
                pmf=binom.pmf(ar,nv,B[f]); d=pmf[ks[f][i0_:i1_]]*(1+1e-7)
                sp=np.sort(pmf); cs=np.cumsum(sp); pos=np.searchsorted(sp,d,side="right")
                pv=np.minimum(np.where(pos>0,cs[np.maximum(pos-1,0)],0.0),1.0)
                seg_n=n[i0_:i1_]
                cert=(pv<=TS[f])&(seg_n>=100)
                if cert.any():
                    kk=ks[f][i0_:i1_][cert].astype(float); nn=seg_n[cert].astype(float)
                    rt=np.round(kk/nn,3)
                    TOP[f].append((fid[i0_:i1_][cert],row[i0_:i1_][cert],dep[i0_:i1_][cert],
                                   rt,seg_n[cert],np.abs(rt-round(B[f],3))))
            if gi%40==0: prune()
            if w==1 and time.time()-t0>210 and gi+1<len(uq):
                dump(str(sub0))
                st["sub"]=gi+1; sv()
                print(f"R range {j+1}/{NB} PARTIAL sub={gi+1}/{len(uq)}",flush=True)
                import sys; sys.exit(0)
        dump("t" if sub0 else "full")
        st.pop("sub",None)
        j+=1
        print(f"R range {j}/{NB} {time.time()-t0:.0f}s",flush=True)
    st["cursor"]=j
    if j>=NB: st["stage"]="F"
    sv(); print("R cursor",j,flush=True)

elif st["stage"]=="F":
    C=pd.read_parquet("aw2_C.parquet") if os.path.exists("aw2_C.parquet") else None
    if C is None:
        C=pd.concat([pd.read_parquet(p) for p in sorted(glob.glob("aw2_cand_*.parquet"))],ignore_index=True)
        C=C.sort_values(["fid","row"]).reset_index(drop=True)
        C.to_parquet("aw2_C.parquet",index=False)
    fids=np.sort(C.fid.unique())
    i=st.get("fcur",0); t0=time.time(); out=[]
    while i<len(fids) and time.time()-t0<200:
        fid=int(fids[i]); g=C[C.fid==fid]
        src=pd.read_parquet(cnt[fid],columns=["f1","v1","f2","v2"])
        for r in g.itertuples():
            rw=int(r.row); v1=str(src.v1.iloc[rw])
            out.append(dict(fid=fid,row=rw,depth=int(r.depth),family=r.family,
                rate=float(r.rate),n=int(r.n),lift=float(r.lift),
                station=v1.split("|")[0],
                stack=" · ".join(f"{a}={b}" for a,b in list(zip(str(src.f1.iloc[rw]).split("|")[1:],v1.split("|")[1:]))+[(str(src.f2.iloc[rw]),str(src.v2.iloc[rw]))])))
        del src; i+=1
    if out: pd.DataFrame(out).to_parquet(f"aw2_res_{st.get('fcur',0):05d}.parquet",index=False)
    st["fcur"]=i; sv()
    print(f"F {i}/{len(fids)} fids resolved",flush=True)
    if i>=len(fids):
        R=pd.concat([pd.read_parquet(p) for p in sorted(glob.glob("aw2_res_*.parquet"))],ignore_index=True)
        stations=sorted(pd.read_csv("atlas_cells.csv").station.unique())
        W=pd.concat([R[(R.station==s_)&(R.family==f)].nlargest(12,"lift")
                     for s_ in stations for f in FAMS],ignore_index=True)
        W["source"]="w2"; W["base"]=W.family.map(lambda f: round(B[f],3))
        W.to_csv("aw2_rows.csv",index=False)
        fillc={(s_,f):int(((W.station==s_)&(W.family==f)).sum()) for s_ in stations for f in FAMS}
        unf={k:v for k,v in fillc.items() if v<12}
        print("w2 rows:",len(W),"| unfilled buckets:",len(unf),
              "| candidate lift floor:",round(float(C.lift.min()),3),flush=True)
        st["stage"]="done"; sv()
else:
    print("done")
