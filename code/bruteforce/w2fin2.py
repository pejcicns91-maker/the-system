# W2 finalize v2 — global-by-n bucket architecture, exact, storage-free, 4GB-safe.
# Stages (fin2_state.json): H (n histogram) -> K (bucket build) -> P1 (p pass -> log-histograms)
# -> B (exact t*) -> P2 (cert counters + digest candidates) -> OUT.
import numpy as np, pandas as pd, glob, os, json, time, hashlib
from scipy.stats import binom
SEED=20260723; np.random.seed(SEED)
ST="fin2_state.json"; BK="fin2_bk"; os.makedirs(BK,exist_ok=True)
st=json.load(open(ST)) if os.path.exists(ST) else {"stage":"H","cursor":0}
def sv(): json.dump(st,open(ST,"w"))
FAMS=["bounce","through","b50","fastres"]; KC={"bounce":"kb","through":"kt","b50":"k5","fastres":"kf"}
B=json.load(open("fin_bases.json"))
cnt=sorted(glob.glob("w2_counts/cnt_*.parquet"))
REC=np.dtype([("n",np.int32),("kb",np.int32),("kt",np.int32),("k5",np.int32),("kf",np.int32),
              ("fid",np.int16),("row",np.int32),("dep",np.int8)])
NB=32; EDGES=np.linspace(-350,0,70001)

def load_ranges(rspecs,need_meta):
    acc=[dict(Ns=[],Ks={f:[] for f in FAMS},Fid=[],Row=[],Dep=[]) for _ in rspecs]
    cols=["n","kb","kt","k5","kf"]+(["depth"] if need_meta else [])
    for fi,pth in enumerate(cnt):
        if fi%1000==0: print(f"  scan {fi}/{len(cnt)}",flush=True)
        D=pd.read_parquet(pth,columns=cols)
        n=D.n.to_numpy(np.int32)
        kv={f:D[KC[f]].to_numpy(np.int32) for f in FAMS}
        dep=D.depth.to_numpy(np.int8) if need_meta else None
        for a,(rlo,rhi) in zip(acc,rspecs):
            m=(n>=rlo)&(n<rhi)
            if not m.any(): continue
            a["Ns"].append(n[m])
            for f in FAMS: a["Ks"][f].append(kv[f][m])
            if need_meta:
                a["Fid"].append(np.full(int(m.sum()),fi,np.int16))
                a["Row"].append(np.nonzero(m)[0].astype(np.int32))
                a["Dep"].append(dep[m])
    out=[]
    for a in acc:
        n=np.concatenate(a["Ns"]) if a["Ns"] else np.empty(0,np.int32)
        ks={f:(np.concatenate(a["Ks"][f]) if a["Ks"][f] else np.empty(0,np.int32)) for f in FAMS}
        meta=(np.concatenate(a["Fid"]),np.concatenate(a["Row"]),np.concatenate(a["Dep"])) if (need_meta and a["Fid"]) else None
        out.append((n,ks,meta))
    return out

def ranges():
    cuts=json.load(open("fin2_cuts.json"))
    edges=[0]+[cuts[j] for j in range(1,63,2)]+[10**9]
    return list(zip(edges[:-1],edges[1:]))


if st["stage"]=="H":
    h=np.zeros(600001,np.int64); t0=time.time(); i=st["cursor"]
    while i<len(cnt) and time.time()-t0<230:
        n=pd.read_parquet(cnt[i],columns=["n"]).n.to_numpy(np.int64)
        h+=np.bincount(np.minimum(n,600000),minlength=600001); i+=1
    if os.path.exists("fin2_nh.npy"): h+=np.load("fin2_nh.npy")
    np.save("fin2_nh.npy",h); st["cursor"]=i
    if i>=len(cnt):
        cum=np.cumsum(h); tot=cum[-1]
        cuts=[int(np.searchsorted(cum,tot*(j+1)/NB)) for j in range(NB-1)]
        json.dump(cuts,open("fin2_cuts.json","w"))
        st["stage"]="P1"; st["cursor"]=0
    sv(); print("H",i,"/",len(cnt),flush=True)

elif st["stage"]=="K_disabled":
    cuts=np.array(json.load(open("fin2_cuts.json")))
    t0=time.time(); i=st["cursor"]
    fh=[open(f"{BK}/b{j:02d}.bin","ab") for j in range(NB)]
    while i<len(cnt) and time.time()-t0<225:
        D=pd.read_parquet(cnt[i],columns=["n","kb","kt","k5","kf","depth"])
        r=np.empty(len(D),REC)
        r["n"]=D.n; r["kb"]=D.kb; r["kt"]=D.kt; r["k5"]=D.k5; r["kf"]=D.kf
        r["fid"]=i; r["row"]=np.arange(len(D)); r["dep"]=D.depth
        bid=np.searchsorted(cuts,r["n"],side="left")
        for j in np.unique(bid): fh[j].write(r[bid==j].tobytes())
        i+=1
        if i%200==0: print(f"K {i}/{len(cnt)} {time.time()-t0:.0f}s",flush=True)
    for f in fh: f.close()
    st["cursor"]=i
    if i>=len(cnt): st["stage"]="P1"; st["cursor"]=0
    sv(); print("K",i,"/",len(cnt),flush=True)

elif st["stage"] in ("P1","S","P2"):
    if st["stage"]=="P2":
        ts=json.load(open("fin_tstar2.json"))["tstar"]
        ck="fin2_c.npz"
        if os.path.exists(ck):
            Z=np.load(ck,allow_pickle=True); summ=Z["summ"].item(); digj=Z["dig"].item(); val=Z["val"].item()
        else:
            summ={}; digj={f:[] for f in FAMS}; val={"maxdiff":0.0,"nv":0}
    elif st["stage"]=="P1":
        H=np.load("fin2_H.npz",allow_pickle=True)["H"].item() if os.path.exists("fin2_H.npz") else {f:np.zeros(70000,np.int64) for f in FAMS}
    else:
        BR=json.load(open("fin2_bracket.json"))
        CAND=None  # shard files fin2_sh_*.npz; merged at B
    t0=time.time(); j=st["cursor"]; RG=ranges()
    w=2 if j<30 else 1
    pair=RG[j:j+w]
    nm=st["stage"]=="P2"
    rc=f"fin2_rc{j}_{int(nm)}.npz"
    if w==1 and os.path.exists(rc):
        Z=np.load(rc)
        n=Z["n"]; ks={f:Z[KC[f]] for f in FAMS}
        meta=(Z["fid"],Z["row"],Z["dep"]) if nm else None
        loaded=[("CACHED",None,None)]
        print(f"  range cache hit: {len(n):,} cells",flush=True)
    else:
        loaded=load_ranges(pair,nm) if j<NB else []
    for tup in loaded:
        if not (isinstance(tup[0],str) and tup[0]=="CACHED"):
            n,ks,meta=tup
            print(f"  range compute: {len(n):,} cells",flush=True)
            o=np.argsort(n,kind="stable"); n=n[o]
            for f in FAMS: ks[f]=ks[f][o]
            if meta: meta=(meta[0][o],meta[1][o],meta[2][o])
            if w==1:
                sv_={"n":n,**{KC[f]:ks[f] for f in FAMS}}
                if meta: sv_.update(fid=meta[0],row=meta[1],dep=meta[2])
                np.savez(rc,**sv_)
        uq,a=np.unique(n,return_index=True); b2=np.append(a[1:],len(n))
        sub0=st.get("sub",0) if w==1 else 0
        print(f"  unique n: {len(uq):,} range [{uq.min() if len(uq) else 0},{uq.max() if len(uq) else 0}] sub0={sub0}",flush=True)
        pj={f:np.empty(len(n)) for f in FAMS}
        partial=False
        for gi,(nv,i0_,i1_) in enumerate(zip(uq,a,b2)):
            if gi<sub0: continue
            nv=int(nv); ar=np.arange(nv+1)
            for f in FAMS:
                pmf=binom.pmf(ar,nv,B[f]); d=pmf[ks[f][i0_:i1_]]*(1+1e-7)
                sp=np.sort(pmf); cs=np.cumsum(sp); pos=np.searchsorted(sp,d,side="right")
                pj[f][i0_:i1_]=np.minimum(np.where(pos>0,cs[np.maximum(pos-1,0)],0.0),1.0)
            if w==1 and time.time()-t0>215 and gi+1<len(uq):
                st["sub"]=gi+1; partial=True
                lo,hi=a[sub0],b2[gi]
                if st["stage"]=="P1":
                    for f in FAMS:
                        H[f]+=np.histogram(np.log10(np.maximum(pj[f][lo:hi],1e-320)),bins=EDGES)[0]
                    np.savez("fin2_H.npz",H=H)
                elif st["stage"]=="S":
                    sh={}
                    for f in FAMS:
                        b=BR[f]; seg=pj[f][lo:hi]
                        sh[f]=seg[(seg>b["e_lo"])&(seg<=b["e_hi"])]
                    np.savez(f"fin2_sh_{j}_{sub0}.npz",**sh)
                else:
                    fid,row,dep=meta
                    for f in FAMS:
                        seg=pj[f][lo:hi]; cert=seg<=ts[f]
                        segdep=dep[lo:hi]; segn=n[lo:hi]; segk=ks[f][lo:hi]
                        for d_ in np.unique(segdep):
                            m_=segdep==d_; key=(f,int(d_)); c0,c1=summ.get(key,(0,0))
                            summ[key]=(c0+int(m_.sum()),c1+int((cert&m_).sum()))
                        m2=cert&(segn>=100)
                        if m2.any():
                            kk=segk[m2].astype(float); nn=segn[m2].astype(float)
                            lift=np.abs(np.round(kk/nn,3)-round(B[f],3))
                            top=np.argsort(lift)[::-1][:400]
                            digj[f].append(pd.DataFrame({"fid":fid[lo:hi][m2][top],"row":row[lo:hi][m2][top],
                                "depth":segdep[m2][top],"rate":np.round(kk/nn,3)[top],"n":segn[m2][top],
                                "lift":lift[top],"family":f}))
                    np.savez("fin2_c.npz",summ=summ,dig={f:[pd.concat(digj[f],ignore_index=True).nlargest(4000,"lift")] if digj[f] else [] for f in FAMS},val=val)
                sv(); print(f"{st['stage']} range {j+1}/{NB} PARTIAL sub={gi+1}/{len(uq)}",flush=True)
                import sys; sys.exit(0)
        if w==1 and sub0>0:
            lo=a[sub0]
            if st["stage"]=="P1":
                for f in FAMS:
                    H[f]+=np.histogram(np.log10(np.maximum(pj[f][lo:],1e-320)),bins=EDGES)[0]
            elif st["stage"]=="S":
                sh={}
                for f in FAMS:
                    b=BR[f]; seg=pj[f][lo:]
                    sh[f]=seg[(seg>b["e_lo"])&(seg<=b["e_hi"])]
                np.savez(f"fin2_sh_{j}_t{sub0}.npz",**sh)
            else:
                fid,row,dep=meta
                for f in FAMS:
                    seg=pj[f][lo:]; cert=seg<=ts[f]
                    segdep=dep[lo:]; segn=n[lo:]; segk=ks[f][lo:]
                    for d_ in np.unique(segdep):
                        m_=segdep==d_; key=(f,int(d_)); c0,c1=summ.get(key,(0,0))
                        summ[key]=(c0+int(m_.sum()),c1+int((cert&m_).sum()))
                    m2=cert&(segn>=100)
                    if m2.any():
                        kk=segk[m2].astype(float); nn=segn[m2].astype(float)
                        lift=np.abs(np.round(kk/nn,3)-round(B[f],3))
                        top=np.argsort(lift)[::-1][:400]
                        digj[f].append(pd.DataFrame({"fid":fid[lo:][m2][top],"row":row[lo:][m2][top],
                            "depth":segdep[m2][top],"rate":np.round(kk/nn,3)[top],"n":segn[m2][top],
                            "lift":lift[top],"family":f}))
            st.pop("sub",None)
            skip_std=True
        else:
            skip_std=False
        if skip_std:
            pass
        elif st["stage"]=="P1":
            for f in FAMS:
                H[f]+=np.histogram(np.log10(np.maximum(pj[f],1e-320)),bins=EDGES)[0]
        elif st["stage"]=="S":
            sh={}
            for f in FAMS:
                b=BR[f]
                sel=(pj[f]>b["e_lo"])&(pj[f]<=b["e_hi"])
                sh[f]=pj[f][sel]
            np.savez(f"fin2_sh_{j}_full.npz",**sh)
        else:
            fid,row,dep=meta
            for f in FAMS:
                cert=pj[f]<=ts[f]
                for d_ in np.unique(dep):
                    m_=dep==d_; key=(f,int(d_)); c0,c1=summ.get(key,(0,0))
                    summ[key]=(c0+int(m_.sum()),c1+int((cert&m_).sum()))
                m2=cert&(n>=100)
                if m2.any():
                    kk=ks[f][m2].astype(float); nn=n[m2].astype(float)
                    lift=np.abs(np.round(kk/nn,3)-round(B[f],3))
                    top=np.argsort(lift)[::-1][:400]
                    digj[f].append(pd.DataFrame({"fid":fid[m2][top],"row":row[m2][top],
                        "depth":dep[m2][top],"rate":np.round(kk/nn,3)[top],"n":n[m2][top],
                        "lift":lift[top],"family":f}))
            if val["nv"]<200 and len(n):
                from scipy import stats
                ii=np.random.randint(len(n)); f=FAMS[np.random.randint(4)]
                pv=stats.binomtest(int(ks[f][ii]),int(n[ii]),B[f]).pvalue
                val["maxdiff"]=max(val["maxdiff"],abs(pv-pj[f][ii])); val["nv"]+=1
        j+=1
        print(f"{st['stage']} range {j}/{NB} {time.time()-t0:.0f}s",flush=True)
    st["cursor"]=j
    if st["stage"]=="P1":
        np.savez("fin2_H.npz",H=H)
        if j>=NB:
            H=np.load("fin2_H.npz",allow_pickle=True)["H"].item()
            q=0.10; m=int(H["bounce"].sum()); BR={}
            for f in FAMS:
                cum=np.cumsum(H[f]); eU=10.0**EDGES[1:]; eL=10.0**EDGES[:-1]
                nec=eL<q*cum/m
                U=int(np.nonzero(nec)[0].max())
                pred=eU<=q*cum/m
                L=int(np.nonzero(pred)[0].max()) if pred.any() else 0
                BR[f]=dict(e_lo=float(10.0**EDGES[max(L-1,0)]) if pred.any() else 0.0,
                           e_hi=float(10.0**EDGES[min(U+1,70000)]),
                           Glo=int(cum[max(L-2,0)]) if pred.any() and L>=2 else 0, m=m)
                print(f"bracket {f}: ({BR[f]['e_lo']:.3g}, {BR[f]['e_hi']:.3g}] Glo={BR[f]['Glo']:,}",flush=True)
            json.dump(BR,open("fin2_bracket.json","w"))
            st["stage"]="S"; st["cursor"]=0
    elif st["stage"]=="S":
        if j>=NB: st["stage"]="B"; st["cursor"]=0
    else:
        np.savez("fin2_c.npz",summ=summ,dig={f:[pd.concat(digj[f],ignore_index=True).nlargest(4000,"lift")] if digj[f] else [] for f in FAMS},val=val)
        if j>=NB: st["stage"]="OUT"; st["cursor"]=0
    sv(); print(st["stage"],"cursor",st["cursor"],flush=True)

elif st["stage"]=="B":
    BR=json.load(open("fin2_bracket.json"))
    CAND={f:[np.load("fin2_cand.npz")[f]] if os.path.exists("fin2_cand.npz") else [] for f in FAMS}
    for shp in sorted(glob.glob("fin2_sh_*.npz")):
        Z=np.load(shp)
        for f in FAMS: CAND[f].append(Z[f])
    CAND={f:(np.concatenate(CAND[f]) if CAND[f] else np.empty(0)) for f in FAMS}
    q=0.10; ts={}; m=BR["bounce"]["m"]
    for f in FAMS:
        cv=CAND[f]; b=BR[f]
        if len(cv)==0: ts[f]=0.0; print(f"t* {f}: 0 (empty sliver)"); continue
        uq2,uc=np.unique(cv,return_counts=True)
        G=b["Glo"]+np.cumsum(uc)
        ok=uq2<=q*G/m
        ts[f]=float(uq2[ok].max()) if ok.any() else 0.0
        print(f"t* {f}: {ts[f]:.6g} (sliver {len(cv):,}, unique {len(uq2):,})",flush=True)
    json.dump({"m":int(m),"tstar":ts},open("fin_tstar2.json","w"))
    st["stage"]="P2"; st["cursor"]=0; sv()

elif st["stage"]=="OUT":
    Z=np.load("fin2_c.npz",allow_pickle=True); summ=Z["summ"].item(); dig=Z["dig"].item(); val=Z["val"].item()
    TS=json.load(open("fin_tstar2.json"))
    frames=[]
    for f in FAMS:
        if not dig[f]: continue
        DD=pd.concat(dig[f],ignore_index=True)
        for fid,g in DD.groupby("fid"):
            src=pd.read_parquet(cnt[int(fid)],columns=["f1","v1","f2","v2"])
            gg=g.copy()
            gg["f1"]=src.f1.values[g.row.values]; gg["v1"]=src.v1.values[g.row.values]
            gg["f2"]=src.f2.values[g.row.values]; gg["v2"]=src.v2.values[g.row.values]
            gg["base"]=round(B[f],3); frames.append(gg)
    DG=pd.concat(frames,ignore_index=True)
    deps=sorted(set(int(k[1]) for k in summ))
    DG=pd.concat([DG[(DG.family==f)&(DG.depth==d)].nlargest(200,"lift") for f in FAMS for d in deps],ignore_index=True)
    DG[["family","depth","f1","v1","f2","v2","rate","base","n"]].to_csv("w2_digest.csv",index=False)
    E=pd.concat([pd.read_parquet(p) for p in sorted(glob.glob("w2_counts/ext_*.parquet"))],ignore_index=True)
    E["extinct"]=E.cells==0; E.to_csv("w2_extinction.csv",index=False)
    S=pd.DataFrame([dict(family=f,depth=d,cells=summ[(f,d)][0],cert=summ[(f,d)][1]) for (f,d) in sorted(summ)])
    S.to_csv("w2_summary.csv",index=False)
    print("W2 FINALIZED | m",f"{TS['m']:,}","| t*",{k:round(v,8) for k,v in TS["tstar"].items()},
          "| scipy check",f"{val['maxdiff']:.2e}/{val['nv']}")
    for fn in ["w2_digest.csv","w2_extinction.csv","w2_summary.csv"]:
        print(fn,"sha",hashlib.sha256(open(fn,'rb').read()).hexdigest()[:12])
    st["stage"]="done"; sv()
else: print("done")
