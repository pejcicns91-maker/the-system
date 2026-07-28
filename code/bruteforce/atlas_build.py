# B6 — give-reaction atlas builder. Mode: synthesis of certified reading-layer registers.
# Data: bf_ladder_d012.csv, bf_ladder_d34.parquet, bf_ladder_b0x.parquet (streamed),
# w1_digest.csv (as-committed runner curation), extinction maps, b5_scores.csv.
# Selection (stated): spine = all d0 rows; singles = all certified d1 (n>=40);
# stacks = per station x family, top 12 by |rate-base| among certified n>=100 from each
# source, then parsimony dedup (drop deeper cell if a kept shallower cell's feature:value
# set is a subset and |d_rate|<=.010), final cap 24 per station x family.
# Reading layer only: rates with n; no verdict words anywhere in output.
import numpy as np, pandas as pd, pyarrow.parquet as pq, json, hashlib
KEEP_PER_SRC, FINAL_CAP, NMIN = 12, 24, 100

def parse(f1, v1, f2, v2):
    fs = f1.split('|'); vs = str(v1).split('|')
    st = vs[0]
    feats = list(zip(fs[1:], vs[1:])) + [(f2, str(v2))]
    return st, feats

def pool_top(df, src):
    rows = []
    for r in df.itertuples():
        st, feats = parse(r.f1, r.v1, r.f2, r.v2)
        rows.append(dict(source=src, depth=int(r.depth), station=st, family=r.family,
                         feats=feats, rate=float(r.rate), base=float(r.base), n=int(r.n)))
    P = pd.DataFrame(rows)
    if not len(P): return P
    P['lift'] = (P.rate - P.base).abs()
    return P.sort_values('lift', ascending=False).groupby(['station','family'], group_keys=False).head(KEEP_PER_SRC)

pools = []
# d012: spine + singles + d2 stacks
L0 = pd.read_csv('bf_ladder_d012.csv', low_memory=False)
L0['certified'] = L0.certified.astype(str) == 'True'
spine = L0[L0.depth == 0].copy()
singles = [L0[(L0.depth == 1) & L0.certified & (L0.n >= 40)].assign(src='d012')]
pools.append(pool_top(L0[(L0.depth == 2) & L0.certified & (L0.n >= NMIN)], 'd012'))

# big parquets: streamed top-K
for path, src in [('bf_ladder_d34.parquet', 'd34'), ('bf_ladder_b0x.parquet', 'b0x')]:
    pf = pq.ParquetFile(path)
    acc = []
    for batch in pf.iter_batches(batch_size=500_000,
            columns=['family','depth','f1','v1','f2','v2','rate','base','n','certified']):
        B = batch.to_pandas()
        B = B[B.certified & (B.n >= NMIN)]
        if not len(B): continue
        if src == 'b0x' and (B.depth == 1).any():
            singles.append(B[B.depth == 1].assign(src='b0x'))
        B['station'] = B.v1.astype(str).str.split('|').str[0]
        B['lift'] = (B.rate - B.base).abs()
        acc.append(B)
        if len(acc) >= 6:
            acc = [pd.concat(acc, ignore_index=True).sort_values('lift', ascending=False)
                     .groupby(['station','family'], group_keys=False).head(KEEP_PER_SRC)]
    P = pool_top(pd.concat(acc, ignore_index=True).sort_values('lift', ascending=False)
                   .groupby(['station','family'], group_keys=False).head(KEEP_PER_SRC), src) if acc else pd.DataFrame()
    pools.append(P)
    print(src, 'pooled', len(P), flush=True)

# w1 digest (runner-committed curation; registers live in repo counts)
W = pd.read_csv('w1_digest.csv')
pools.append(pool_top(W[W.n >= NMIN], 'w1'))

# singles layer (kept whole, no top-K)
S1 = pd.concat(singles, ignore_index=True)
s_rows = []
for r in S1.itertuples():
    st, feats = parse(r.f1, r.v1, r.f2, r.v2)
    s_rows.append(dict(source=getattr(r, 'src', 'd012'), depth=1, station=st, family=r.family,
                       feats=feats, rate=float(r.rate), base=float(r.base), n=int(r.n)))
SING = pd.DataFrame(s_rows); SING['lift'] = (SING.rate - SING.base).abs()

# stacks: merge pools, parsimony dedup, cap
ALL = pd.concat([p for p in pools if len(p)], ignore_index=True)
kept = []
for (st, fam), g in ALL.sort_values(['depth', 'lift'], ascending=[True, False]).groupby(['station','family']):
    chosen = []
    for r in g.itertuples():
        fset = set(f"{a}={b}" for a, b in r.feats)
        dup = any(set(f"{a}={b}" for a, b in c.feats) <= fset and abs(c.rate - r.rate) <= 0.010
                  for c in chosen)
        if not dup:
            chosen.append(r)
        if len(chosen) >= FINAL_CAP: break
    kept += chosen
K = pd.DataFrame([dict(source=r.source, depth=r.depth, station=r.station, family=r.family,
                       stack=' · '.join(f"{a}={b}" for a, b in r.feats),
                       rate=r.rate, base=r.base, n=r.n, lift=round(r.lift, 3)) for r in kept])
K = K.sort_values(['station','family','lift'], ascending=[True, True, False]).reset_index(drop=True)

SINGC = SING.assign(stack=SING.feats.map(lambda fs: ' · '.join(f"{a}={b}" for a, b in fs))) \
            [['source','depth','station','family','stack','rate','base','n','lift']]
OUT = pd.concat([K, SINGC], ignore_index=True)
OUT.to_csv('atlas_cells.csv', index=False)

# b5 strip + frontier facts + spine
B5 = pd.read_csv('b5_scores.csv')
b5s = B5.groupby(['frame','family']).agg(med=('skill','median'), pos=('skill', lambda s: (s > 0).mean())) \
        .round(3).reset_index().to_dict('records')
spine_rows = [dict(station=r.v1, family=r.family, rate=float(r.rate), n=int(r.n))
              for r in spine.itertuples()]
data = dict(
    built='2026-07-24', bases=dict(bounce=0.302, through=0.299),
    frontier="extinction 0 combos through depth 5 (min d5 combo: 204 cells); certified fraction thins with depth: bounce 86.6/70.1/51.0/29.0%, through 92.1/83.5/71.0/50.9% at d1/d2/d3/d5",
    b5=b5s, spine=spine_rows,
    cells=OUT.to_dict('records'))
json.dump(data, open('atlas_data.json','w'))
print("atlas: stacks", len(K), "| singles", len(SINGC), "| total rows", len(OUT))
print("stations", OUT.station.nunique(), "| sources:", OUT.source.value_counts().to_dict())
print("sha atlas_cells", hashlib.sha256(open('atlas_cells.csv','rb').read()).hexdigest()[:12])
