#!/usr/bin/env python3
"""e4c_commit.py — RECOVERY SHIP v2 (in-job pushes: each coin commits and pushes its own index from inside the job under GH_TOKEN, the e2 pattern, so an eviction can cost at most one coin) for e4 (Svet's chat order, 2026-07-30). The e4 compute succeeded
and its cell ledgers live as release 'c2x10' assets, but runner evictions skipped the commit step,
so the in-tree artifacts (index_{COIN}, DECODE, REPORT, state) never landed. This job does not
recompute pairs: it fetches the released cells, GATES them, rebuilds the index tables from them
with e4's exact sep formula, and ships in-tree. GATES (any FAIL = exit 1):
B1 parts readable, total cell rows counted · B2 per-pair kept-cell counts == pair_index.cells,
exact, every pair · B3 streamed (n, s_o10) == c2 'ledgers' release (n, n_cb), exact, every row
(fetch failure = named SKIP, never silence) · B4 dials_dict pair space == pair_index rows.
n_total is sourced from pair_index — chain: runner G4 PASS at full grid (run 1 log) + v2 kernel
frame-equal regression + local cut G4 PASS; named here, not silent. sep_oV = per-pair
n_v-weighted mean |rate - base_v|, bases from results/state/e3.json, identical to e4's formula.
Deterministic, no RNG. Counts only; verdicts are Svet's."""
import pandas as pd, numpy as np, json, os, sys, time, zipfile, urllib.request, subprocess
import pyarrow.parquet as pq
T0=time.time(); COINS=['BTC','ETH','SOL','XRP']
C2='results/layerc2'; OUT='results/c2ep'; os.makedirs(OUT,exist_ok=True); os.makedirs('results/state',exist_ok=True)
VEC=['o1_closed_beyond','o2_traded_beyond','o3_bounce_corridor','o4_retest_given_break',
'o5_held_given_retest','o6_fade_atrp_100_025','o7_fade_atrp_100_050','o8_rt_atrp_100_050',
'o9_rt_struct_100_050','o10_closeback']
PARTIAL=[2,3,4,5,6,7,8]
UNI=json.load(open('results/state/e3.json'))['uni']
R10='https://github.com/pejcicns91-maker/the-system/releases/download/c2x10'
RCB='https://github.com/pejcicns91-maker/the-system/releases/download/ledgers'
any_fail=False; rep=[f"# E4B RECOVERY SHIP — {pd.Timestamp.now('UTC')}"]
def gate(tag,ok,detail):
    global any_fail; s='PASS' if ok else 'FAIL'
    if not ok: any_fail=True
    print(f'{tag}: {s} — {detail}',flush=True); rep.append(f'{tag}: {s} — {detail}')
for coin in COINS:
    zp=f'/tmp/cells10_{coin}.zip'
    if not os.path.exists(zp): urllib.request.urlretrieve(f'{R10}/cells10_{coin}.zip',zp)
    PX=pd.read_parquet(f'{C2}/pair_index_{coin}.parquet'); NP=len(PX)
    dd=pd.read_parquet(f'{C2}/dials_dict_{coin}.parquet'); Dn=len(dd)
    gate(f'{coin} B4 pair space',Dn*(Dn-1)//2==NP,f'dials {Dn} -> {Dn*(Dn-1)//2:,} vs index {NP:,}')
    bases=np.array([UNI[coin][o][1] for o in VEC])
    cc=np.zeros(NP,np.int64); tot=0
    num=np.zeros((10,NP),np.float64); den=np.zeros((10,NP),np.float64)
    zf=zipfile.ZipFile(zp); names=sorted(zf.namelist())
    # c2 reference stream for B3
    ref_ok=True; rlen=0
    try:
        zc=f'/tmp/c2cells_{coin}.zip'
        if not os.path.exists(zc): urllib.request.urlretrieve(f'{RCB}/cells_{coin}.zip',zc)
        with zipfile.ZipFile(zc) as z: z.extract(f'cells_{coin}.parquet','/tmp/c2ref')
        rpf=pq.ParquetFile(f'/tmp/c2ref/cells_{coin}.parquet'); rlen=rpf.metadata.num_rows
        rit=rpf.iter_batches(batch_size=2_000_000,columns=['pair_id','cell','n','n_cb'])
        rbuf={k:np.array([],dtype=np.int64) for k in ['pair_id','cell','n','n_cb']}
        def pull(L):
            global rbuf
            while len(rbuf['pair_id'])<L:
                b=next(rit).to_pydict()
                for k in rbuf: rbuf[k]=np.concatenate([rbuf[k],np.asarray(b[k],dtype=np.int64)])
            out={k:rbuf[k][:L] for k in rbuf}; rbuf={k:rbuf[k][L:] for k in rbuf}; return out
    except Exception as e:
        ref_ok=None; print(f'{coin} B3: SKIP — reference fetch failed ({type(e).__name__})',flush=True)
        rep.append(f'{coin} B3: SKIP — {type(e).__name__}')
    for nm in names:
        P=pd.read_parquet(zf.open(nm)); L=len(P); tot+=L
        pid=P.pair_id.to_numpy(); cc+=np.bincount(pid,minlength=NP)
        nn=P.n.to_numpy().astype(np.float64)
        if ref_ok:
            try:
                q=pull(L)
                ref_ok=bool(np.array_equal(q['pair_id'],pid.astype(np.int64)))and bool(np.array_equal(q['cell'],P.cell.to_numpy().astype(np.int64)))\
                    and bool(np.array_equal(q['n'],P.n.to_numpy().astype(np.int64)))and bool(np.array_equal(q['n_cb'],P.s_o10_closeback.to_numpy().astype(np.int64)))
            except Exception: ref_ok=False
        for vi,o in enumerate(VEC):
            nv=P[f'n_{o}'].to_numpy().astype(np.float64) if vi in PARTIAL else nn
            sv=P[f's_{o}'].to_numpy().astype(np.float64)
            with np.errstate(invalid='ignore',divide='ignore'):
                d=np.where(nv>0,np.abs(sv/np.maximum(nv,1)-bases[vi]),0.0)
            num[vi]+=np.bincount(pid,weights=nv*d,minlength=NP); den[vi]+=np.bincount(pid,weights=nv,minlength=NP)
        del P
    gate(f'{coin} B1 parts',tot>0,f'{len(names)} parts · {tot:,} cell rows')
    gate(f'{coin} B2 cells==pair_index',bool(np.array_equal(cc.astype(PX.cells.dtype),PX.cells.to_numpy())),'per-pair exact')
    if ref_ok is not None:
        gate(f'{coin} B3 vs c2 release',bool(ref_ok) and tot==rlen,f'{tot:,} rows vs {rlen:,}, n and closeback channels exact')
    IX=pd.DataFrame({'pair_id':np.arange(NP,dtype=np.int32),'cells':cc.astype(np.int16),'n_total':PX.n_total.to_numpy()})
    with np.errstate(invalid='ignore',divide='ignore'):
        sep=np.where(den>0,num/np.maximum(den,1e-12),0.0).astype(np.float32)
    for vi,o in enumerate(VEC): IX[f'sep_{o}']=sep[vi]
    IX.to_parquet(f'{OUT}/index_{coin}.parquet',compression='zstd',index=False)
    rep.append(f'{coin}: {tot:,} cell rows in {len(names)} parts · index {NP:,} pairs rebuilt')
    if os.environ.get('GITHUB_ACTIONS'):
        subprocess.run(['git','config','user.name','job-bot']); subprocess.run(['git','config','user.email','bot@none'])
        subprocess.run(['git','add',f'{OUT}/index_{coin}.parquet'])
        subprocess.run(['git','commit','-m',f'e4c: index_{coin} [skip ci]'],capture_output=True)
        subprocess.run(['git','pull','--rebase'],capture_output=True); r=subprocess.run(['git','push'],capture_output=True,text=True)
        print(f'{coin} in-job push:','OK' if r.returncode==0 else 'FAILED '+r.stderr[-120:],flush=True)
    print('DONE',coin,'|',tot,'cell rows |',round((time.time()-T0)/60,2),'min',flush=True)
open(f'{OUT}/DECODE.md','w').write("cells10_{COIN}_partNNN.parquet (release 'c2x10', concatenate parts in NNN order): cell = codeA*(nbB+1)+codeB; dial ids/bins in results/layerc2/dials_dict (identical grid, G2-gated on the compute run). Columns: n = anchors in cell; s_oV = win sum (NaN=0); n_oV for o3..o9 = finite count (o1/o2/o10 full universe: n_oV == n). rate = s/n_v. Floor n>=50 on total n (cell set identical to c2). index_{COIN}: per-pair cells, n_total (from pair_index; see REPORT provenance), sep_oV = n_v-weighted mean |rate - base_v|, bases sealed in results/state/e3.json.\n")
json.dump({'done':COINS},open('results/state/e4.json','w'))
rep.append(f'total {round((time.time()-T0)/60,2)} min · deterministic, no RNG')
open(f'{OUT}/REPORT.md','w').write('\n'.join(rep)+'\n')
if os.environ.get('GITHUB_ACTIONS'):
    subprocess.run(['git','add','-A','results']); subprocess.run(['git','commit','-m','e4c: docs+state [skip ci]'],capture_output=True)
    subprocess.run(['git','pull','--rebase'],capture_output=True); subprocess.run(['git','push'],capture_output=True)
print(f'total {round((time.time()-T0)/60,2)} min · deterministic, no RNG',flush=True)
print('E4B COMPLETE' if not any_fail else 'E4B FAILED')
sys.exit(1 if any_fail else 0)
