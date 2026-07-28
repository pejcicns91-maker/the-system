# B3: ladder depth 3-4 over vantage rows (5m frame). Extends b2_ladder.py per RUN_STATE resume order 1.
# Full grid, no seeding. n>=40 floor. BH q=.10 within family over the d3-4 tested set (per-run).
# Exact two-sided binomial p (central/minlike, rerr 1+1e-7) computed vectorized; validated vs scipy on seeded sample.
import numpy as np, pandas as pd, hashlib, json, os, sys, time
from itertools import combinations
from scipy import stats
from scipy.stats import binom

SEED = 20260723
np.random.seed(SEED)
CKPT = "ckpt_d34"; os.makedirs(CKPT, exist_ok=True)
BLOCK = 250

# ---------- preprocessing: identical to b2_ladder.py ----------
V = pd.read_parquet("bf_vantage_ALL_5m.parquet")
V['bounce'] = (V.fwd_favU >= 0.25) & (V.fwd_advU < 0.25)
V['through'] = V.fwd_advU >= 0.6
for col, q in [('dq','distU'),('sq','speedUh'),('vq','relvol'),('wq','widthU'),
               ('rq','rng_used'),('kq','wk_used'),('uq','u_trend')]:
    try: V[col] = pd.qcut(pd.to_numeric(V[q], errors='coerce'), 4, duplicates='drop')
    except Exception: V[col] = np.nan
V['cb'] = pd.cut(V.contact, [-1,30,49.5,101], labels=['c<30','c30-49','c>=50'])
V['tn'] = pd.cut(pd.to_numeric(V.test_no, errors='coerce'), [0,1,2,99], labels=['t1','t2','t3+'])
FE = ['coin','etype','zone','virgin','cb','wq','session','wknd','hayden','hayden_btc',
      'btc_pi','origin','tn','dq','sq','vq','rq','kq','uq']
base_b = V.bounce.mean(); base_t = V.through.mean()

# ---------- integer codes (-1 = NaN, excluded like pandas groupby dropna) ----------
codes = {}; labels = {}
for f in ['station'] + FE:
    s = V[f]
    if isinstance(s.dtype, pd.CategoricalDtype):
        codes[f] = s.cat.codes.to_numpy(np.int32)
        labels[f] = [str(x) for x in s.cat.categories]
    else:
        c, u = pd.factorize(s, use_na_sentinel=True)
        codes[f] = c.astype(np.int32)
        labels[f] = [str(x) for x in u]
card = {f: len(labels[f]) for f in codes}
b_arr = V.bounce.to_numpy(bool); t_arr = V.through.to_numpy(bool)

combos = [(3, c) for c in combinations(range(len(FE)), 3)] + \
         [(4, c) for c in combinations(range(len(FE)), 4)]
assert len(combos) == 969 + 3876
blocks = [combos[i:i+BLOCK] for i in range(0, len(combos), BLOCK)]
state_f = f"{CKPT}/state.json"
done = json.load(open(state_f))['done'] if os.path.exists(state_f) else 0

# ---------- counting pass (checkpointed per block) ----------
t0 = time.time()
for bi in range(done, len(blocks)):
    rows = []; ext = []
    for depth, combo in blocks[bi]:
        cols = ['station'] + [FE[i] for i in combo]
        cm = np.stack([codes[c] for c in cols])
        mask = (cm >= 0).all(axis=0)
        dims = [card[c] for c in cols]
        idx = np.ravel_multi_index(tuple(cm[:, mask]), dims)
        M = int(np.prod(dims))
        n_ = np.bincount(idx, minlength=M)
        sel = np.nonzero(n_ >= 40)[0]
        ext.append((depth, '|'.join(cols[1:]), len(sel)))
        if len(sel) == 0: continue
        kb = np.bincount(idx[b_arr[mask]], minlength=M)[sel]
        kt = np.bincount(idx[t_arr[mask]], minlength=M)[sel]
        nn = n_[sel]
        uidx = np.unravel_index(sel, dims)
        labcols = [np.array(labels[c], dtype=object)[uidx[d]] for d, c in enumerate(cols)]
        head = ['|'.join(x) for x in zip(*[labcols[d] for d in range(len(cols)-1)])]
        f1 = '|'.join(cols[:-1]); f2 = cols[-1]
        for r in range(len(sel)):
            rows.append((depth, f1, head[r], f2, labcols[-1][r], int(kb[r]), int(kt[r]), int(nn[r])))
    pd.DataFrame(rows, columns=['depth','f1','v1','f2','v2','kb','kt','n']) \
      .to_parquet(f"{CKPT}/blk_{bi:03d}.parquet", index=False)
    pd.DataFrame(ext, columns=['depth','combo','cells']).to_parquet(f"{CKPT}/ext_{bi:03d}.parquet", index=False)
    json.dump({'done': bi+1}, open(state_f,'w'))
    print(f"block {bi+1}/{len(blocks)}  {time.time()-t0:.0f}s", flush=True)

print("counting complete; run b3_assemble.py")
