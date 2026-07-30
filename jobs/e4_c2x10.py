#!/usr/bin/env python3
"""e4_c2x10.py — C2 x 10: SEQUENTIAL PAIRS vs EPISODE OUTCOMES (Svet's go in chat, 2026-07-29;
runs the PRE-RULING vector set by the same explicit order as e3 — ruling 1 not repealed, not applied).
(b)-LINES — everything mirrored from c2_seqpairs.py EXACTLY: same dial roster (tf x component x
offset 0..99 + day dials at @0), same pos = last completed bar before the touch bar, same bin
edges and category maps, same na coding (last index), same pair order (pair_id identical), same
valid mask, same FLOOR n>=50 on cell total-n (cell set identical to c2's), same n_total = n over
valid cells. THE ONE SWAP: the score. Ten weight vectors from the shipped, sealed
results/bcep/anchor_outcomes_{COIN}.parquet (the canonical vector source; nothing recomputed from
raw bars), key-aligned to anchors by (wdate, mark, price, t0). Per kept cell: n (all anchors),
s_o1..s_o10 (win sums, NaN contributes 0), n_o3..n_o9 (finite counts; o1/o2/o10 have full
universes so n_ov == n). Per pair: sep_ov = n-weighted mean |rate - base_v| over kept cells,
base_v = the per-coin universe mean sealed in results/state/e3.json.
GATES (any FAIL = exit 1): G1 vectors align 1:1 zero orphans and o10 reproduces anchors.closeback
row-wise · G2 dial dictionary reproduces dials_dict_{COIN} exactly · G3 pair count == pair_index
rows · G4 per-pair n_total and kept-cell counts == pair_index columns exactly · G5 my (n, s_o10)
per cell reproduces c2's released cells (n, n_cb) exactly, full table (release fetch fails =
named SKIP, never silence) · G6 per-vector finite totals == e3.json sealed universes.
G2-G4 require the full grid; under TEST_PAIR_STRIDE they print named SKIPs.
Ships -> results/c2ep/: index_{COIN}.parquet in-tree; full per-cell ledger -> zip -> release
asset 'c2x10' (Option A pattern). Deterministic, no RNG. Counts only; verdicts are Svet's."""
import pandas as pd, numpy as np, json, os, sys, time, argparse, subprocess, zipfile, urllib.request
ap=argparse.ArgumentParser(); ap.add_argument('--budget-min',type=float,default=230)
A,_=ap.parse_known_args(); T0=time.time()
COINS=['BTC','ETH','SOL','XRP']; REC='results/record'; LB='results/layerb'
BC='results/bcep'; C2='results/layerc2'; OUT='results/c2ep'
os.makedirs(OUT,exist_ok=True); os.makedirs('results/state',exist_ok=True)
SF='results/state/e4.json'; st=json.load(open(SF)) if os.path.exists(SF) else {'done':[]}
STRIDE=int(os.environ.get('TEST_PAIR_STRIDE','1')); FLOOR=50
VEC=['o1_closed_beyond','o2_traded_beyond','o3_bounce_corridor','o4_retest_given_break',
'o5_held_given_retest','o6_fade_atrp_100_025','o7_fade_atrp_100_050','o8_rt_atrp_100_050',
'o9_rt_struct_100_050','o10_closeback']
PARTIAL=[2,3,4,5,6,7,8]  # 0-based vector indices with partial universes (o3..o9)
UNI=json.load(open('results/state/e3.json'))['uni']
REL='https://github.com/pejcicns91-maker/the-system/releases/download/ledgers'
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
any_fail=False; rep=[f"# C2 x 10 — SEQUENTIAL PAIRS vs EPISODE OUTCOMES — {pd.Timestamp.now('UTC')}"]
def gate(tag,ok,detail):
    global any_fail; s='PASS' if ok else 'FAIL'
    if not ok: any_fail=True
    print(f'{tag}: {s} — {detail}',flush=True); rep.append(f'{tag}: {s} — {detail}')
for coin in COINS:
    if coin in st['done']: print(coin,'done'); continue
    if (time.time()-T0)/60>A.budget_min-25: print('budget; resume'); break
    AN=pd.read_parquet(f'{LB}/anchors_{coin}.parquet'); t0=pd.to_datetime(AN.t0,utc=True).to_numpy(); NA=len(AN)
    AO=pd.read_parquet(f'{BC}/anchor_outcomes_{coin}.parquet')
    m=AN.merge(AO,on=['wdate','mark','price','t0'],how='left',indicator=True)
    g1=(len(m)==NA)and int((m._merge!='both').sum())==0 and bool((m.o10_closeback==m.closeback).all())
    gate(f'{coin} G1 align',g1,f'{NA} rows, orphans {(m._merge!="both").sum()}, o10==closeback {bool((m.o10_closeback==m.closeback).all())}')
    if not g1: st['done'].append(coin); continue
    W=m[VEC].to_numpy(dtype=np.float64)
    for vi,o in enumerate(VEC):
        gate(f'{coin} G6 uni {o}',int(np.isfinite(W[:,vi]).sum())==UNI[coin][o][0],
             f'finite {int(np.isfinite(W[:,vi]).sum()):,} == sealed {UNI[coin][o][0]:,}')
    FIN=[np.flatnonzero(np.isfinite(W[:,vi])).astype(np.int32) for vi in range(10)]
    WIN=[np.flatnonzero(W[:,vi]==1.0).astype(np.int32) for vi in range(10)]
    MISS=[np.flatnonzero(W[:,vi]==0.0).astype(np.int32) for vi in range(10)]
    USEMISS=[len(MISS[vi])<len(WIN[vi]) for vi in range(10)]
    NVSRC={3:0,4:3}  # sealed universe identities: o4 finite == o1 wins; o5 finite == o4 wins (G6-chained)
    HISTV=[vi for vi in PARTIAL if vi not in NVSRC]  # partial-universe vectors needing a finite histogram
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
    if STRIDE==1:
        dd=pd.read_parquet(f'{C2}/dials_dict_{coin}.parquet')
        gate(f'{coin} G2 dials',list(dd.name)==names and list(dd.nbins)==list(nbs),f'{Dn} dials vs dict {len(dd)}')
    else: print(f'{coin} G2 dials: SKIP (TEST_PAIR_STRIDE={STRIDE})',flush=True)
    bases=np.array([UNI[coin][o][1] for o in VEC])
    NP=Dn*(Dn-1)//2
    ic=np.zeros(NP,np.int16); itot=np.zeros(NP,np.int64); iseps=np.zeros((10,NP),np.float32)
    ch_p=[];ch_c=[];ch_rows=[]; ch_n=0; parts=[]
    PART_ROWS=int(os.environ.get('PART_ROWS','6000000'))
    pdir=f'/tmp/parts_{coin}'; os.makedirs(pdir,exist_ok=True)
    for f_ in os.listdir(pdir): os.remove(f'{pdir}/{f_}')
    def flush():
        global ch_p,ch_c,ch_rows,ch_n
        if ch_n==0: return
        R=np.concatenate(ch_rows,axis=1)
        P=pd.DataFrame({'pair_id':np.concatenate(ch_p),'cell':np.concatenate(ch_c),'n':R[0]})
        for vi,o in enumerate(VEC): P[f's_{o}']=R[1+vi]
        for pi_,vi in enumerate(PARTIAL): P[f'n_{VEC[vi]}']=R[11+pi_]
        fp=f'{pdir}/cells10_{coin}_part{len(parts):03d}.parquet'
        P.to_parquet(fp,compression='zstd',index=False); parts.append((fp,len(P)))
        ch_p=[];ch_c=[];ch_rows=[]; ch_n=0
    pid=0; t_last=time.time()
    for a in range(Dn-1):
        Ma=M[:,a].astype(np.int32); nba=nbs[a]
        for b_ in range(a+1,Dn):
            nbb=nbs[b_]; code=Ma*(nbb+1)+M[:,b_].astype(np.int32)
            K=(nba+1)*(nbb+1)
            n=np.bincount(code,minlength=K)
            valid=np.zeros(K,bool); valid.reshape(nba+1,nbb+1)[:nba,:nbb]=True
            keep=(n>=FLOOR)&valid
            tot=int(n[valid].sum())
            if keep.any():
                kk=np.nonzero(keep)[0]; nk=n[kk].astype(np.float64)
                S=np.empty((10,len(kk))); NV=np.empty((10,len(kk)))
                hist=lambda idx: np.bincount(code[idx],minlength=K)[kk].astype(np.float64)
                for vi in range(10):
                    NV[vi]=nk if vi not in PARTIAL else (S[NVSRC[vi]] if vi in NVSRC else hist(FIN[vi]))
                    S[vi]=(NV[vi]-hist(MISS[vi])) if USEMISS[vi] else hist(WIN[vi])
                with np.errstate(invalid='ignore',divide='ignore'):
                    rate=np.where(NV>0,S/np.maximum(NV,1),np.nan)
                for vi in range(10):
                    wv=NV[vi]; sw=wv.sum()
                    term=np.where(wv>0,wv*np.abs(rate[vi]-bases[vi]),0.0)
                    iseps[vi,pid]=term.sum()/sw if sw>0 else 0.0
                ch_p.append(np.full(len(kk),pid,np.int32)); ch_c.append(kk.astype(np.int16))
                ch_rows.append(np.rint(np.vstack([nk,S,NV[PARTIAL]])).astype(np.int32))
                ch_n+=len(kk)
                if ch_n>=PART_ROWS: flush()
            ic[pid]=keep.sum(); itot[pid]=tot; pid+=1
        if time.time()-t_last>120: print(f'  ..dial {a}/{Dn} {round((time.time()-T0)/60,1)}min',flush=True); t_last=time.time()
    IX=pd.DataFrame({'pair_id':np.arange(NP,dtype=np.int32),'cells':ic,'n_total':itot})
    for vi,o in enumerate(VEC): IX[f'sep_{o}']=iseps[vi]
    if STRIDE==1:
        PX=pd.read_parquet(f'{C2}/pair_index_{coin}.parquet')
        gate(f'{coin} G3 pairs',pid==len(PX),f'{pid:,} vs index {len(PX):,}')
        gate(f'{coin} G4 n_total+cells',bool(np.array_equal(IX.n_total.to_numpy(),PX.n_total.to_numpy()))
             and bool(np.array_equal(IX.cells.to_numpy(),PX.cells.to_numpy())),'per-pair exact')
    else: print(f'{coin} G3/G4: SKIP (TEST_PAIR_STRIDE={STRIDE})',flush=True)
    flush()
    ncells=sum(l for _,l in parts)
    if STRIDE==1:
        try:
            zp0=f'/tmp/c2cells_{coin}.zip'
            if not os.path.exists(zp0): urllib.request.urlretrieve(f'{REL}/cells_{coin}.zip',zp0)
            with zipfile.ZipFile(zp0) as z: z.extract(f'cells_{coin}.parquet','/tmp/c2ref')
            RF=pd.read_parquet(f'/tmp/c2ref/cells_{coin}.parquet'); lenRF=len(RF)
            ok=('n_cb' in RF) and lenRF==ncells; cur=0
            for fp,L in parts:
                if not ok: break
                P=pd.read_parquet(fp); Q=RF.iloc[cur:cur+L]; cur+=L
                ok=bool(np.array_equal(Q.pair_id.to_numpy(),P.pair_id.to_numpy())) \
                   and bool(np.array_equal(Q.cell.to_numpy(),P.cell.to_numpy())) \
                   and bool(np.array_equal(Q.n.to_numpy(),P.n.to_numpy().astype(RF.n.dtype))) \
                   and bool(np.array_equal(Q.n_cb.to_numpy(),P.s_o10_closeback.to_numpy().astype(RF.n_cb.dtype)))
            del RF
            gate(f'{coin} G5 c2 cells',ok,f'{ncells:,} cell rows vs released {lenRF:,} (streamed over {len(parts)} parts)')
        except Exception as e:
            print(f'{coin} G5 c2 cells: SKIP — release fetch/read failed ({type(e).__name__}: {str(e)[:120]})',flush=True)
            rep.append(f'{coin} G5: SKIP — {type(e).__name__}')
    else: print(f'{coin} G5: SKIP (TEST_PAIR_STRIDE={STRIDE})',flush=True)
    IX.to_parquet(f'{OUT}/index_{coin}.parquet',compression='zstd',index=False)
    zp=f'/tmp/cells10_{coin}.zip'
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_STORED) as z:
        for fp,_ in parts: z.write(fp,os.path.basename(fp))
    if os.environ.get('GITHUB_ACTIONS'):
        subprocess.run(['gh','release','create','c2x10','-t','C2 x 10 cell ledgers','-n','sequential pairs vs the ten episode outcome vectors'],capture_output=True)
        r=subprocess.run(['gh','release','upload','c2x10',zp,'--clobber'],capture_output=True,text=True)
        print('release upload:','OK' if r.returncode==0 else 'FAILED '+r.stderr[:200],flush=True)
    else: print('local: release upload skipped;',zp,os.path.getsize(zp),'bytes; cell rows',ncells,'in',len(parts),'parts',flush=True)
    rep.append(f'{coin}: pairs {pid:,} · kept-cell rows {ncells:,} in {len(parts)} parts · dials {Dn} · anchors {NA:,}')
    st['done'].append(coin); json.dump(st,open(SF,'w')); print('DONE',coin,'| pairs',pid,'| cell rows',ncells,flush=True)
open(f'{OUT}/DECODE.md','w').write("cells10_{COIN}_partNNN.parquet (release 'c2x10', concatenate parts in NNN order): cell = codeA*(nbB+1)+codeB; dial ids/bins in results/layerc2/dials_dict (identical grid, G2-gated). Columns: n = anchors in cell; s_oV = win sum (NaN=0); n_oV for o3..o9 = finite count (o1/o2/o10 full universe: n_oV == n). rate = s/n_v. Floor n>=50 on total n (cell set identical to c2). index_{COIN}: per-pair cells, n_total (valid cells incl. below-floor), sep_oV = n_v-weighted mean |rate - base_v|, bases sealed in results/state/e3.json.\n")
rep.append(f'total {round((time.time()-T0)/60,2)} min · deterministic, no RNG')
open(f'{OUT}/REPORT.md','w').write('\n'.join(rep)+'\n')
print(f'total {round((time.time()-T0)/60,2)} min · deterministic, no RNG',flush=True)
print('E4',' COMPLETE' if len(st['done'])==4 else f' partial {st["done"]} — run again')
sys.exit(1 if any_fail else 0)
