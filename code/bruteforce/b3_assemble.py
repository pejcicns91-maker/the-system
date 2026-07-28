# B3 assembly: p-values (exact two-sided binom, vectorized) + BH q=.10 per family over d3-4 set,
# streaming register write (parquet), certified digest, extinction map. Seed 20260723.
import numpy as np, pandas as pd, hashlib, json, os, glob
import pyarrow as pa, pyarrow.parquet as pq
from scipy import stats
from scipy.stats import binom

SEED = 20260723
NB = len(glob.glob("ckpt_d34/blk_*.parquet"))

# bases identical to b2 preprocessing
V = pd.read_parquet("bf_vantage_ALL_5m.parquet", columns=['fwd_favU','fwd_advU'])
base_b = float(((V.fwd_favU>=0.25)&(V.fwd_advU<0.25)).mean())
base_t = float((V.fwd_advU>=0.6).mean()); del V

# numeric pass
parts = [pd.read_parquet(f"ckpt_d34/blk_{i:03d}.parquet", columns=['depth','kb','kt','n']) for i in range(NB)]
sizes = [len(x) for x in parts]
N = pd.concat(parts, ignore_index=True); del parts
kb = N.kb.to_numpy(np.int64); kt = N.kt.to_numpy(np.int64)
n_ = N.n.to_numpy(np.int64); dep = N.depth.to_numpy(np.int8); del N

def pvec(k, n, p0):
    out = np.empty(len(k))
    for nv in np.unique(n):
        m = np.nonzero(n == nv)[0]
        pmf = binom.pmf(np.arange(nv+1), nv, p0)
        d = pmf[k[m]] * (1 + 1e-7)
        sp = np.sort(pmf); cs = np.cumsum(sp)
        pos = np.searchsorted(sp, d, side='right')
        out[m] = np.minimum(np.where(pos > 0, cs[np.maximum(pos-1,0)], 0.0), 1.0)
    return out

p_b = pvec(kb, n_, base_b); p_t = pvec(kt, n_, base_t)

def bh(ps, q=0.10):
    m = len(ps); order = np.argsort(ps, kind='stable')
    sp = ps[order]; thr = q * np.arange(1, m+1) / m
    sat = np.nonzero(sp <= thr)[0]
    kmax = int(sat[-1] + 1) if len(sat) else 0
    ok = np.zeros(m, bool); ok[order[:kmax]] = True
    return ok, kmax

cert_b, _ = bh(p_b); cert_t, _ = bh(p_t)

# scipy validation, seeded
rng = np.random.default_rng(SEED)
ix = rng.choice(len(n_), 250, replace=False)
d1 = max(abs(stats.binomtest(int(kb[i]), int(n_[i]), base_b).pvalue - p_b[i]) for i in ix)
d2 = max(abs(stats.binomtest(int(kt[i]), int(n_[i]), base_t).pvalue - p_t[i]) for i in ix)
maxdiff = max(d1, d2)

# streaming register: parquet, family-major then block order
schema = pa.schema([('family',pa.string()),('depth',pa.int8()),('f1',pa.string()),('v1',pa.string()),
                    ('f2',pa.string()),('v2',pa.string()),('rate',pa.float64()),('base',pa.float64()),
                    ('n',pa.int64()),('p',pa.float64()),('certified',pa.bool_())])
w = pq.ParquetWriter("bf_ladder_d34.parquet", schema, compression='zstd')
digest = []
for fam, kk, pp, cc, bb in [('bounce',kb,p_b,cert_b,base_b), ('through',kt,p_t,cert_t,base_t)]:
    off = 0
    for i in range(NB):
        B = pd.read_parquet(f"ckpt_d34/blk_{i:03d}.parquet")
        s = slice(off, off+len(B)); off += len(B)
        D = pd.DataFrame({'family':fam,'depth':B.depth.astype(np.int8),'f1':B.f1,'v1':B.v1,'f2':B.f2,'v2':B.v2,
                          'rate':np.round(kk[s]/n_[s],3),'base':round(bb,3),'n':n_[s],'p':pp[s],'certified':cc[s]})
        w.write_table(pa.Table.from_pandas(D, schema=schema, preserve_index=False))
        dd = D[(D.certified) & (D.n>=100)].assign(lift=lambda x:(x.rate-x.base).abs())
        if len(dd): digest.append(dd.nlargest(min(400,len(dd)),'lift'))
        del B, D, dd
w.close()

DG = pd.concat(digest, ignore_index=True)
DG = pd.concat([DG[(DG.family==f)&(DG.depth==d)].nlargest(200,'lift')
                for f in ['bounce','through'] for d in [3,4]], ignore_index=True)
DG.drop(columns=['lift']).to_csv("bf_ladder_d34_digest.csv", index=False)

E = pd.concat([pd.read_parquet(f"ckpt_d34/ext_{i:03d}.parquet") for i in range(NB)], ignore_index=True)
E['extinct'] = E.cells == 0
E.to_csv("bf_extinction_d34.csv", index=False)

tot = len(n_)
print("=== B3 d3-4 assembly complete ===")
print(f"bases: bounce {base_b:.3f} through {base_t:.3f}")
print(f"cells (per family): {tot:,} | register rows: {2*tot:,}")
for d in [3,4]:
    m = dep==d
    print(f"depth {d}: cells {int(m.sum()):,} | certified bounce {int(cert_b[m].sum()):,} through {int(cert_t[m].sum()):,}")
print(f"certified total: bounce {int(cert_b.sum()):,} ({cert_b.mean():.1%}) through {int(cert_t.sum()):,} ({cert_t.mean():.1%})")
print(f"combos: d3 {int((E.depth==3).sum())} d4 {int((E.depth==4).sum())} | extinct d3 {int(E[E.depth==3].extinct.sum())} d4 {int(E[E.depth==4].extinct.sum())}")
print(f"cells/combo median: d3 {E[E.depth==3].cells.median():.0f} d4 {E[E.depth==4].cells.median():.0f}")
print(f"p-validation max|diff| vs scipy (500 seeded): {maxdiff:.2e}")
for f in ["bf_ladder_d34.parquet","bf_ladder_d34_digest.csv","bf_extinction_d34.csv"]:
    sz = os.path.getsize(f)/1e6
    print(f, f"{sz:.1f}MB", "sha", hashlib.sha256(open(f,'rb').read()).hexdigest()[:12])
