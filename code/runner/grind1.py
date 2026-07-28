# W1 GRIND — d5 over FE25 + t2-quartile extension. Chunked, budget-boxed, cursor-resumable.
# Modes: grind (default) processes combos until --budget-min; finalize computes p+BH+register
# over the completed set. Phase B4 (t2 d4, ~475k combos, artifact-scale) requires --b4 1.
# Seed 20260723. Laws: n>=40 floor, extinction logged, BH q=.10/family over the finalized set.
import numpy as np, pandas as pd, json, os, sys, time, glob, hashlib, argparse
from itertools import combinations
np.random.seed(20260723)
ap = argparse.ArgumentParser()
ap.add_argument("--budget-min", type=float, default=230)
ap.add_argument("--b4", type=int, default=0)
ap.add_argument("--finalize", type=int, default=0)
A = ap.parse_args()
OUT = "out_counts"; os.makedirs(OUT, exist_ok=True)
SF = "gha_state.json"

V = pd.read_parquet("bf_vantage_ALL_wide.parquet")
V['bounce'] = (V.fwd_favU >= 0.25) & (V.fwd_advU < 0.25)
V['through'] = V.fwd_advU >= 0.6
for col, q in [('dq','distU'),('sq','speedUh'),('vq','relvol'),('wq','widthU'),
               ('rq','rng_used'),('kq','wk_used'),('uq','u_trend')]:
    try: V[col] = pd.qcut(pd.to_numeric(V[q], errors='coerce'), 4, duplicates='drop')
    except Exception: V[col] = np.nan
V['cb'] = pd.cut(V.contact, [-1,30,49.5,101], labels=['c<30','c30-49','c>=50'])
V['tn'] = pd.cut(pd.to_numeric(V.test_no, errors='coerce'), [0,1,2,99], labels=['t1','t2','t3+'])
FE25 = ['coin','etype','zone','virgin','cb','wq','session','wknd','hayden','hayden_btc','btc_pi',
        'origin','tn','dq','sq','vq','rq','kq','uq','yd_arch','ob55','dtype','lean','scen_state','scen_failed']
T2 = [f"{b}_{f}" for b in ['net100','net20','rng100','pos100','volr','zt100','zlast']
      for f in ['5m','15m','1h','4h','1d']]                  # 35 cols; lnb/fnb are coverage flags, excluded
for c in T2:
    try: V['q_'+c] = pd.qcut(pd.to_numeric(V[c], errors='coerce'), 4, duplicates='drop')
    except Exception: V['q_'+c] = np.nan
FE = FE25 + ['q_'+c for c in T2]                              # 60 columns
codes = {}; labels = {}
for f in ['station'] + FE:
    s = V[f]
    if isinstance(s.dtype, pd.CategoricalDtype):
        codes[f] = s.cat.codes.to_numpy(np.int32); labels[f] = [str(x) for x in s.cat.categories]
    else:
        c, u = pd.factorize(s, use_na_sentinel=True)
        codes[f] = c.astype(np.int32); labels[f] = [str(x) for x in u]
card = {f: len(labels[f]) for f in codes}
b_arr = V.bounce.to_numpy(bool); t_arr = V.through.to_numpy(bool)

NEWT = set(range(25, 60))
combos = [(5, c) for c in combinations(range(25), 5)]                      # phase A: 53,130
for k in range(1, 4):                                                      # phase B d1-d3 t2-involving
    combos += [(k, c) for c in combinations(range(60), k) if set(c) & NEWT]
if A.b4:
    combos += [(4, c) for c in combinations(range(60), 4) if set(c) & NEWT]
print("total combos this configuration:", len(combos), flush=True)

def process(depth, combo):
    cols = ['station'] + [FE[i] for i in combo]
    cm = np.stack([codes[c] for c in cols]); mask = (cm >= 0).all(axis=0)
    dims = [card[c] for c in cols]
    idx = np.ravel_multi_index(tuple(cm[:, mask]), dims)
    n_ = np.bincount(idx, minlength=int(np.prod(dims)))
    sel = np.nonzero(n_ >= 40)[0]
    er = (depth, '|'.join(cols[1:]), len(sel))
    if not len(sel): return [], er
    kb = np.bincount(idx[b_arr[mask]], minlength=len(n_))[sel]
    kt = np.bincount(idx[t_arr[mask]], minlength=len(n_))[sel]
    uidx = np.unravel_index(sel, dims)
    lab = [np.array(labels[c], dtype=object)[uidx[d]] for d, c in enumerate(cols)]
    head = ['|'.join(x) for x in zip(*[lab[d] for d in range(len(cols)-1)])]
    f1 = '|'.join(cols[:-1]); f2 = cols[-1]
    return [(depth, f1, head[r], f2, lab[-1][r], int(kb[r]), int(kt[r]), int(n_[sel][r]))
            for r in range(len(sel))], er

if not A.finalize:
    st = json.load(open(SF)) if os.path.exists(SF) else {"cursor": 0, "b4": A.b4}
    cur = st["cursor"]; BLOCK = 200; t0 = time.time()
    while cur < len(combos) and (time.time() - t0) / 60 < A.budget_min:
        rows, ext = [], []
        for depth, combo in combos[cur:cur+BLOCK]:
            rr, er = process(depth, combo); rows += rr; ext.append(er)
        tag = f"{cur:07d}"
        pd.DataFrame(rows, columns=['depth','f1','v1','f2','v2','kb','kt','n']) \
          .to_parquet(f"{OUT}/cnt_{tag}.parquet", index=False, compression='zstd')
        pd.DataFrame(ext, columns=['depth','combo','cells']).to_parquet(f"{OUT}/ext_{tag}.parquet", index=False)
        cur += min(BLOCK, len(combos) - cur)
        json.dump({"cursor": cur, "b4": A.b4}, open(SF, 'w'))
        print(f"cursor {cur}/{len(combos)}  {(time.time()-t0)/60:.1f}min", flush=True)
    print("chunk done; complete" if cur >= len(combos) else "chunk done; resume next run", flush=True)
else:
    st = json.load(open(SF))
    assert st["cursor"] >= len(combos), f"grind incomplete: {st['cursor']}/{len(combos)} — finalize refused"
    from scipy import stats
    from scipy.stats import binom
    base_b = float(V.bounce.mean()); base_t = float(V.through.mean())
    parts = sorted(glob.glob(f"{OUT}/cnt_*.parquet"))
    N = pd.concat([pd.read_parquet(p, columns=['depth','kb','kt','n']) for p in parts], ignore_index=True)
    kb = N.kb.to_numpy(np.int64); kt = N.kt.to_numpy(np.int64)
    n_ = N.n.to_numpy(np.int64); dep = N.depth.to_numpy(np.int8); del N
    def pvec(k, n, p0):
        out = np.empty(len(k)); o = np.argsort(n, kind='stable'); ns, ks = n[o], k[o]
        uq, a = np.unique(ns, return_index=True); b = np.append(a[1:], len(ns))
        for nv, i0, i1 in zip(uq, a, b):
            pmf = binom.pmf(np.arange(nv+1), nv, p0); d = pmf[ks[i0:i1]] * (1+1e-7)
            sp = np.sort(pmf); cs = np.cumsum(sp); pos = np.searchsorted(sp, d, side='right')
            out[o[i0:i1]] = np.minimum(np.where(pos > 0, cs[np.maximum(pos-1, 0)], 0.0), 1.0)
        return out
    p_b = pvec(kb, n_, base_b); p_t = pvec(kt, n_, base_t)
    def bh(ps, q=0.10):
        m = len(ps); o = np.argsort(ps, kind='stable'); sp = ps[o]
        sat = np.nonzero(sp <= q*np.arange(1, m+1)/m)[0]
        kmax = int(sat[-1]+1) if len(sat) else 0
        ok = np.zeros(m, bool); ok[o[:kmax]] = True; return ok
    cb_, ct_ = bh(p_b), bh(p_t)
    rng = np.random.default_rng(20260723); ix = rng.choice(len(n_), 200, replace=False)
    md = max(max(abs(stats.binomtest(int(kb[i]), int(n_[i]), base_b).pvalue - p_b[i]) for i in ix),
             max(abs(stats.binomtest(int(kt[i]), int(n_[i]), base_t).pvalue - p_t[i]) for i in ix))
    import pyarrow as pa, pyarrow.parquet as pq
    schema = pa.schema([('family',pa.string()),('depth',pa.int8()),('f1',pa.string()),('v1',pa.string()),
                        ('f2',pa.string()),('v2',pa.string()),('rate',pa.float64()),('base',pa.float64()),
                        ('n',pa.int64()),('p',pa.float64()),('certified',pa.bool_())])
    os.makedirs("out_register", exist_ok=True); digest = []; part_i = 0
    w = pq.ParquetWriter(f"out_register/reg_{part_i:03d}.parquet", schema, compression='zstd')
    for fam, pp, cc, bb, kv0 in [('bounce', p_b, cb_, base_b, 'kb'), ('through', p_t, ct_, base_t, 'kt')]:
        off = 0
        for p in parts:
            B = pd.read_parquet(p); s = slice(off, off+len(B)); off += len(B)
            kv = B[kv0].to_numpy(np.int64)
            D = pd.DataFrame({'family':fam,'depth':B.depth.astype(np.int8),'f1':B.f1,'v1':B.v1,'f2':B.f2,'v2':B.v2,
                              'rate':np.round(kv/n_[s],3),'base':round(bb,3),'n':n_[s],'p':pp[s],'certified':cc[s]})
            w.write_table(pa.Table.from_pandas(D, schema=schema, preserve_index=False))
            if os.path.getsize(f"out_register/reg_{part_i:03d}.parquet") > 80_000_000:
                w.close(); part_i += 1
                w = pq.ParquetWriter(f"out_register/reg_{part_i:03d}.parquet", schema, compression='zstd')
            dd = D[(D.certified) & (D.n >= 100)].assign(lift=lambda x: (x.rate-x.base).abs())
            if len(dd): digest.append(dd.nlargest(min(800, len(dd)), 'lift'))
            del B, D, dd
    w.close()
    DG = pd.concat(digest, ignore_index=True)
    DG = pd.concat([DG[(DG.family==f)&(DG.depth==d)].nlargest(200,'lift')
                    for f in ['bounce','through'] for d in sorted(set(dep))], ignore_index=True)
    DG.drop(columns=['lift']).to_csv("w1_digest.csv", index=False)
    E = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(f"{OUT}/ext_*.parquet"))], ignore_index=True)
    E['extinct'] = E.cells == 0; E.to_csv("w1_extinction.csv", index=False)
    print(f"FINALIZED | cells/fam {len(n_):,} | cert b {int(cb_.sum()):,} t {int(ct_.sum()):,} | "
          f"extinct {int(E.extinct.sum())}/{len(E)} | pval-check {md:.2e}")
    for f in ["w1_digest.csv","w1_extinction.csv"]:
        print(f, "sha", hashlib.sha256(open(f,'rb').read()).hexdigest()[:12])
