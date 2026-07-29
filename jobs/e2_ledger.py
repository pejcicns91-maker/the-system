#!/usr/bin/env python3
"""e3_bc.py — B/C MACHINERY vs EPISODE OUTCOMES, UNADJUSTED (Svet's signed design; his explicit
word runs the PRE-RULING vectors: ATRp-denominated trade outcomes O6-O8 as originally pitched.
Ruling 1 — primaries structural/pips/percent, ATR-family+U as additional measures only — remains
binding law for future tables and is not repealed by this run; it is simply not applied here.)

PART 1 — anchor_outcomes_{COIN}.parquet: one row per anchor (keyed identically), TEN weight
vectors, NaN = out of universe (the third outcome and 'neither' never become coin flips):
 o1_closed_beyond (all) · o2_traded_beyond (all) · o3_bounce_corridor: bounce_ext reached the
 bounce-side corridor mark before any close-beyond; 0 when no pre-break bounce window existed;
 na when that corridor side is missing · o4_retest_given_break (universe: o1==1) ·
 o5_held_given_retest (universe: retested; 1 = no reclaim close by window end) ·
 o6_fade_atrp_100_025, o7_fade_atrp_100_050, o8_rt_atrp_100_050, o9_rt_struct_100_050:
 ledger-grain trade wins (win=1 loss=0; ambiguous/neither/entry-bar = NaN; ATRp = PRIOR-day
 ATR14; STRUCT = corridor gaps) · o10_closeback (legacy vector riding beside).
PART 2 — B singles x10: the b2_offsets loops mirrored EXACTLY (same anchors, same pos =
 last completed bar before touch, same bins, same comps, same shape trio, same daily join),
 scored per outcome -> bprof_offsets / bprof_day / bprof_shape (long: outcome in the key;
 n = finite count in cell, s = sum).
PART 3 — C1 x10: the shipped per-anchor dial matrices (results/layerc/dials_{COIN}) re-used
 after an alignment gate (dials.cb must equal anchors.closeback row-wise), pairs + triples,
 floor n>=50 per outcome row (floor declared, matrices raw so nothing is lost).
GATES (any FAIL = exit 1): vector universes reconcile (o1 n == anchors; o4 universe == broke;
 o5 universe == retested; o10 mean == anchors closeback); if results/ledger/ledger_cells.parquet
 is present, o6-o9 decided n and win sums must MATCH the shipped ledger cells exactly
 (family ALL, both sides summed) — absent ledger = named skip, not silence.
Ships -> results/bcep/. Deterministic, no RNG. Counts only; verdicts are Svet's."""
import pandas as pd, numpy as np, json, os, sys, time, argparse
from itertools import combinations

ap = argparse.ArgumentParser(); ap.add_argument('--budget-min', type=float, default=230)
A_, _ = ap.parse_known_args(); T0 = time.time()
COINS = ['BTC','ETH','SOL','XRP']
REC, EPD, LB, LC, OUT = 'results/record','results/episodes','results/layerb','results/layerc','results/bcep'
os.makedirs(OUT, exist_ok=True); os.makedirs('results/state', exist_ok=True)
SF = 'results/state/e3.json'
st = json.load(open(SF)) if os.path.exists(SF) else {'done': [], 'c1done': [], 'uni': {}}
K = 100; INF = np.int64(2**62)
OCOLS = ['o1_closed_beyond','o2_traded_beyond','o3_bounce_corridor','o4_retest_given_break',
         'o5_held_given_retest','o6_fade_atrp_100_025','o7_fade_atrp_100_050',
         'o8_rt_atrp_100_050','o9_rt_struct_100_050','o10_closeback']
BINS = {'rsi':[0,30,40,50,60,70,101],'rng_x':[0,0.7,1.0,1.5,1e9],'close_pos':[-0.01,0.33,0.66,1.01],
        'body_frac':[-0.01,0.33,0.66,1.01],'volr':[0,0.8,1.2,1e9],'relvol':[0,0.7,1.5,3,1e9]}
def binify(name, v):
    if name in BINS:
        e = BINS[name]; b = np.digitize(v, e) - 1
        lab = np.array([f"{e[i]}-{e[i+1]}" for i in range(len(e)-1)] + ['na'])
        b = np.where(np.isfinite(v), np.clip(b, 0, len(e)-2), len(e)-1); return lab[b]
    return v.astype(str)

# ---------------------------------------------------------------- PART 1: vectors
def build_vectors(coin):
    E = pd.read_parquet(f'{EPD}/episodes_{coin}.parquet', columns=['wdate','mark','price','t0',
        'corridor_up_price','corridor_dn_price','first_trade_beyond_at','first_close_beyond_at',
        'bounce_ext_price','retest_touch_at','reclaim_close_at'])
    A = pd.read_parquet(f'{LB}/anchors_{coin}.parquet',
        columns=['wdate','mark','price','t0','open_side','closeback'])
    D = pd.read_parquet(f'{REC}/bars_{coin}_1D.parquet', columns=['wdate','atr14_1d'])
    D['wdate'] = D.wdate.astype(str); D = D.sort_values('wdate'); D['atrp'] = D.atr14_1d.shift(1)
    M = E.merge(A, on=['wdate','mark','price','t0'], validate='1:1').merge(
        D[['wdate','atrp']], on='wdate', how='left')
    M['o1_closed_beyond'] = M.first_close_beyond_at.notna().astype(float)
    M['o2_traded_beyond'] = M.first_trade_beyond_at.notna().astype(float)
    ahead = np.where(M.open_side == 1, M.corridor_up_price, M.corridor_dn_price)
    reach = np.where(M.open_side == 1, M.bounce_ext_price >= ahead, M.bounce_ext_price <= ahead)
    M['o3_bounce_corridor'] = np.where(np.isfinite(ahead),
        np.where(M.bounce_ext_price.notna(), reach.astype(float), 0.0), np.nan)
    M['o4_retest_given_break'] = np.where(M.o1_closed_beyond == 1,
        M.retest_touch_at.notna().astype(float), np.nan)
    M['o5_held_given_retest'] = np.where(M.retest_touch_at.notna(),
        M.reclaim_close_at.isna().astype(float), np.nan)
    M['o10_closeback'] = M.closeback.astype(float)
    for c in ['o6_fade_atrp_100_025','o7_fade_atrp_100_050','o8_rt_atrp_100_050','o9_rt_struct_100_050']:
        M[c] = np.nan
    X = pd.read_parquet(f'{EPD}/episode_exc_{coin}.parquet').sort_values(
        ['wdate','mark','t0','basis','side','seq'])
    meta = M.set_index(['wdate','mark','t0'])
    o6 = {}; o7 = {}; o8 = {}; o9 = {}
    for (wd, mk, t0v, basis), g in X.groupby(['wdate','mark','t0','basis'], sort=False):
        r = meta.loc[(wd, mk, t0v)]
        m = float(r.price); osd = int(r.open_side); d = osd if basis == 'fade' else -osd
        fv = g[g.side == 'fav']; av = g[g.side == 'adv']
        fex = d*(fv.px.to_numpy() - m); fat = fv['at'].values.astype('datetime64[ns]').astype(np.int64)
        aex = -d*(av.px.to_numpy() - m); aat = av['at'].values.astype('datetime64[ns]').astype(np.int64)
        e0 = fat[0]
        def res(s_thr, t_thr):
            i = int(np.searchsorted(aex, s_thr)); j = int(np.searchsorted(fex, t_thr))
            ts = aat[i] if i < len(aat) else INF; tt = fat[j] if j < len(fat) else INF
            first = min(ts, tt)
            if first == INF or first == e0 or ts == tt: return np.nan
            return 1.0 if tt < ts else 0.0
        atr = float(r.atrp) if pd.notna(r.atrp) else np.nan
        if basis == 'fade':
            if np.isfinite(atr):
                o6[(wd, mk, t0v)] = res(1.00*atr, 0.25*atr)
                o7[(wd, mk, t0v)] = res(1.00*atr, 0.50*atr)
        else:
            if np.isfinite(atr):
                o8[(wd, mk, t0v)] = res(1.00*atr, 0.50*atr)
            cu, cd = r.corridor_up_price, r.corridor_dn_price
            ah = (cu - m) if d == 1 else (m - cd); bh = (m - cd) if d == 1 else (cu - m)
            if pd.notna(ah) and pd.notna(bh):
                o9[(wd, mk, t0v)] = res(1.00*float(bh), 0.50*float(ah))
    keys = list(zip(M.wdate, M['mark'], M.t0))
    M['o6_fade_atrp_100_025'] = [o6.get(k, np.nan) for k in keys]
    M['o7_fade_atrp_100_050'] = [o7.get(k, np.nan) for k in keys]
    M['o8_rt_atrp_100_050']   = [o8.get(k, np.nan) for k in keys]
    M['o9_rt_struct_100_050'] = [o9.get(k, np.nan) for k in keys]
    V = M[['wdate','mark','price','t0'] + OCOLS].copy(); V.insert(0, 'coin', coin)
    V.to_parquet(f'{OUT}/anchor_outcomes_{coin}.parquet', compression='zstd', index=False)
    ok = (len(V) == len(A)
          and int(V.o4_retest_given_break.notna().sum()) == int(V.o1_closed_beyond.sum())
          and int(V.o5_held_given_retest.notna().sum()) == int(np.nansum(V.o4_retest_given_break))
          and abs(float(V.o10_closeback.mean()) - float(A.closeback.mean())) < 1e-12)
    led = 'results/ledger/ledger_cells.parquet'
    gl = 'ledger gate: SKIPPED (results/ledger absent — named, not silent)'
    if os.path.exists(led):
        L = pd.read_parquet(led)
        def cell(basis, ruler, sk, tk):
            c = L[(L.coin == coin) & (L.family == 'ALL') & (L.basis == basis) &
                  (L.ruler == ruler) & (L.stop_k == sk) & (L.tgt_k == tk)]
            return int(c.n_dec.sum()), int(c.n_win.sum())
        chk = [('o6_fade_atrp_100_025', cell('fade','ATRp',1.00,0.25)),
               ('o7_fade_atrp_100_050', cell('fade','ATRp',1.00,0.50)),
               ('o8_rt_atrp_100_050',   cell('rt','ATRp',1.00,0.50)),
               ('o9_rt_struct_100_050', cell('rt','STRUCT',1.00,0.50))]
        bad = [(c, int(V[c].notna().sum()), int(np.nansum(V[c])), nd, nw)
               for c, (nd, nw) in chk
               if int(V[c].notna().sum()) != nd or int(np.nansum(V[c])) != nw]
        gl = 'ledger gate: PASS (o6-o9 decided n and wins match shipped ledger exactly)' if not bad \
             else f'ledger gate: FAIL {bad}'
        ok = ok and not bad
    uni = {c: [int(V[c].notna().sum()), float(np.nanmean(V[c]))] for c in OCOLS}
    print(f'{coin} vectors: {len(V):,} rows · ' + gl)
    return V, uni, ok

# ---------------------------------------------------------------- PART 2: B mirror x10
def profile_cells(off_flat, lab_codes, labels, valid_ok, OMAT_rep, coin, tf, comp):
    rows = []
    nl = len(labels); gid = off_flat*nl + lab_codes
    for oi, oc in enumerate(OCOLS):
        ov = OMAT_rep[:, oi]
        msk = valid_ok & np.isfinite(ov)
        if not msk.any(): continue
        cnt = np.bincount(gid[msk], minlength=K*nl)
        s = np.bincount(gid[msk], weights=ov[msk], minlength=K*nl)
        nz = np.flatnonzero(cnt)
        for z in nz:
            off, li = divmod(int(z), nl)
            if labels[li] == 'na': continue
            rows.append((coin, tf, comp, off, labels[li], oc, int(cnt[z]), float(s[z])))
    return rows

def build_b(coin, V):
    AN = pd.read_parquet(f'{LB}/anchors_{coin}.parquet')
    OMAT = AN.merge(V, on=['wdate','mark','price','t0'], validate='1:1')[OCOLS].to_numpy(float)
    assert OMAT.shape[0] == len(AN)
    t0 = pd.to_datetime(AN.t0, utc=True).to_numpy()
    N = len(AN); offs = np.arange(K)
    OMAT_rep = np.repeat(OMAT, K, axis=0)
    off_flat = np.broadcast_to(offs, (N, K)).ravel()
    POf, PSh, PDy = [], [], []
    frames = {'5m': pd.read_parquet(f'{REC}/bars_{coin}_5m.parquet'),
              '15m': pd.read_parquet(f'{REC}/bars_{coin}_15m.parquet'),
              '1h': pd.read_parquet(f'{REC}/bars_{coin}_1h.parquet'),
              '4h': pd.read_parquet(f'{REC}/bars_{coin}_4h.parquet')}
    for tfk, fr in frames.items():
        fr = fr.copy(); fr['dt'] = pd.to_datetime(fr.dt, utc=True); dta = fr.dt.to_numpy()
        pos = np.searchsorted(dta, t0, 'right') - 2
        comps = [c for c in ['hy_state','rsi','rng_x','close_pos','body_frac','hl_tok','volr',
                             'relvol','div_bull','div_bear','session'] if c in fr.columns]
        if tfk == '4h' and 'btc_state' in fr.columns: comps.append('btc_state')
        IDX = pos[:, None] - offs[None, :]
        valid = (IDX >= 0).ravel(); IDXc = np.clip(IDX, 0, len(fr)-1)
        for cname in comps:
            Vv = fr[cname].to_numpy()[IDXc]
            if Vv.dtype != object and Vv.dtype != bool: Vb = binify(cname, Vv.astype(float))
            else: Vb = Vv.astype(str)
            flat = Vb.ravel()
            codes, labels = pd.factorize(flat)
            ok = valid & (flat != 'na')
            POf += profile_cells(off_flat, codes, list(labels), ok, OMAT_rep, coin, tfk, cname)
        if 'hy_state' in fr.columns:
            stt = fr['hy_state'].to_numpy(); flips = np.concatenate([[0], (stt[1:] != stt[:-1]).astype(int)])
            cf = np.cumsum(flips)
            cb_ = np.cumsum(fr['div_bull'].to_numpy().astype(int)) if 'div_bull' in fr.columns else np.zeros(len(fr), int)
            cs_ = np.cumsum(fr['div_bear'].to_numpy().astype(int)) if 'div_bear' in fr.columns else np.zeros(len(fr), int)
            sl = np.sign(np.nan_to_num(fr['hy_rsi_slope'].to_numpy())) if 'hy_rsi_slope' in fr.columns else np.zeros(len(fr))
            run = np.zeros(len(fr), int)
            for i in range(1, len(fr)):
                run[i] = run[i-1] + 1 if (sl[i] == sl[i-1] and sl[i] != 0) else (1 if sl[i] != 0 else 0)
            p0 = np.clip(pos, 0, len(fr)-1); pK = np.clip(pos-K, 0, len(fr)-1)
            sh = pd.DataFrame({'flips100': cf[p0]-cf[pK], 'divb100': cb_[p0]-cb_[pK],
                               'divs100': cs_[p0]-cs_[pK], 'bars_in': fr['hy_bars_in'].to_numpy()[p0],
                               'slope_run': run[p0]})
            for cname, edges in [('flips100',[0,3,6,10,1e9]),('divb100',[0,2,5,1e9]),
                                 ('divs100',[0,2,5,1e9]),('bars_in',[0,6,20,50,1e9]),('slope_run',[0,3,6,1e9])]:
                b = np.digitize(sh[cname], edges) - 1
                lab = [f"{edges[i]}-{edges[i+1]}" for i in range(len(edges)-1)]
                sb = np.array(lab)[np.clip(b, 0, len(lab)-1)]
                df = pd.DataFrame(OMAT, columns=OCOLS).assign(bin=sb)
                g = df.groupby('bin').agg(['count','sum'])
                for oc in OCOLS:
                    for binv, row in g[oc].iterrows():
                        if row['count'] > 0:
                            PSh.append((coin, tfk, cname, binv, oc, int(row['count']), float(row['sum'])))
    D = pd.read_parquet(f'{REC}/bars_{coin}_1D.parquet')
    Dk = D.assign(w=D.wdate.astype(str)).set_index('w')
    j = AN.join(Dk[['pi_state','hayden_daily_anchor','d5_dtype','lean_dir','yd_arch','ob55_open','d6_ob55_fired']], on='wdate')
    for cname in ['pi_state','hayden_daily_anchor','d5_dtype','lean_dir','yd_arch','ob55_open','d6_ob55_fired']:
        df = pd.DataFrame(OMAT, columns=OCOLS).assign(bin=j[cname].astype(str).to_numpy())
        g = df.groupby('bin').agg(['count','sum'])
        for oc in OCOLS:
            for binv, row in g[oc].iterrows():
                if row['count'] > 0:
                    PDy.append((coin, cname, binv, oc, int(row['count']), float(row['sum'])))
    return POf, PSh, PDy

# ---------------------------------------------------------------- PART 3: C1 mirror x10
def build_c1(coin, V):
    AN = pd.read_parquet(f'{LB}/anchors_{coin}.parquet')
    X = pd.read_parquet(f'{LC}/dials_{coin}.parquet')
    assert len(X) == len(AN) and (X.cb.to_numpy() == AN.closeback.to_numpy()).all(), \
        'dials alignment gate FAIL'
    OM = AN.merge(V, on=['wdate','mark','price','t0'], validate='1:1')[OCOLS]
    assert len(OM) == len(AN)
    W = pd.concat([X.reset_index(drop=True), OM.reset_index(drop=True)], axis=1)
    dials = [c for c in X.columns if c not in ('cb','pl','mark')]
    PP, TT = [], []
    for k, sink in [(2, PP), (3, TT)]:
        for combo in combinations(dials, k):
            g = W.groupby(list(combo), observed=True)[OCOLS].agg(['count','sum']).reset_index()
            binstr = g[list(combo)].astype(str).agg(' | '.join, axis=1)
            for oc in OCOLS:
                n = g[(oc,'count')]; s = g[(oc,'sum')]
                m = n >= 50
                if not m.any(): continue
                sink.append(pd.DataFrame({'coin': coin, 'combo': ' + '.join(combo),
                    'bins': binstr[m].to_numpy(), 'outcome': oc,
                    'n': n[m].to_numpy(int), 's': s[m].to_numpy(float)}))
    return PP, TT

def flush(rows_or_dfs, name, keys, cols=None):
    if not rows_or_dfs: return None
    df = pd.concat(rows_or_dfs, ignore_index=True) if isinstance(rows_or_dfs[0], pd.DataFrame) \
         else pd.DataFrame(rows_or_dfs, columns=cols)
    p = f'{OUT}/{name}.parquet'
    if os.path.exists(p):
        df = pd.concat([pd.read_parquet(p), df]).drop_duplicates(subset=keys, keep='last')
    df.to_parquet(p, compression='zstd', index=False); return df

# ---------------------------------------------------------------- main
any_fail = False
for coin in COINS:
    if coin in st['done']: print(coin, 'done'); continue
    if (time.time()-T0)/60 > A_.budget_min - 12: print('budget; resume'); break
    t_c = time.time()
    V, uni, ok = build_vectors(coin)
    if not ok:
        print(f'VECTOR GATE FAIL on {coin} — STOP.'); any_fail = True; break
    POf, PSh, PDy = build_b(coin, V)
    flush(POf, 'bprof_offsets', ['coin','tf','component','offset','bin','outcome'],
          ['coin','tf','component','offset','bin','outcome','n','s'])
    flush(PSh, 'bprof_shape', ['coin','tf','component','bin','outcome'],
          ['coin','tf','component','bin','outcome','n','s'])
    flush(PDy, 'bprof_day', ['coin','component','bin','outcome'],
          ['coin','component','bin','outcome','n','s'])
    st['uni'][coin] = uni; st['done'].append(coin)
    json.dump(st, open(SF, 'w')); print(f'{coin} B done {round((time.time()-t_c)/60,2)}min', flush=True)
for coin in COINS:
    if any_fail or coin in st['c1done'] or coin not in st['done']: continue
    if (time.time()-T0)/60 > A_.budget_min - 8: print('budget; resume'); break
    V = pd.read_parquet(f'{OUT}/anchor_outcomes_{coin}.parquet')
    PP, TT = build_c1(coin, V)
    flush(PP, 'c1ep_pairs', ['coin','combo','bins','outcome'])
    flush(TT, 'c1ep_triples', ['coin','combo','bins','outcome'])
    st['c1done'].append(coin); json.dump(st, open(SF, 'w')); print(f'{coin} C1 done', flush=True)

if not any_fail and all(c in st['c1done'] for c in COINS):
    Po = pd.read_parquet(f'{OUT}/bprof_offsets.parquet')
    lines = [f'# B/C vs EPISODE OUTCOMES (UNADJUSTED) — {pd.Timestamp.now(tz="UTC")}',
             f'bprof_offsets {len(Po):,} cells · bprof_day {len(pd.read_parquet(f"{OUT}/bprof_day.parquet")):,} · '
             f'bprof_shape {len(pd.read_parquet(f"{OUT}/bprof_shape.parquet")):,} · '
             f'c1ep_pairs {len(pd.read_parquet(f"{OUT}/c1ep_pairs.parquet")):,} · '
             f'c1ep_triples {len(pd.read_parquet(f"{OUT}/c1ep_triples.parquet")):,}',
             'vector universes per coin (n, base rate):']
    for coin in COINS:
        for oc, (n, b) in st['uni'][coin].items():
            lines.append(f'  {coin} {oc}: n={n:,} base={b:.4f}')
    Po['rate'] = Po.s / Po.n
    base = Po.groupby(['coin','tf','outcome']).apply(
        lambda g: g.s.sum()/g.n.sum(), include_groups=False).rename('b').reset_index()
    P2 = Po.merge(base, on=['coin','tf','outcome']); P2['lift'] = (P2.rate - P2.b).abs()
    lines.append('top lifts per outcome (offsets cells, n>=2000):')
    for oc in OCOLS:
        t = P2[(P2.outcome == oc) & (P2.n >= 2000)].sort_values('lift', ascending=False).head(3)
        for r in t.itertuples():
            lines.append(f'  {oc}: {r.coin} {r.tf} {r.component} off{r.offset} bin {r.bin}: '
                         f'{r.rate:.3f} vs {r.b:.3f} (n={r.n:,})')
    lines.append('(b)-LINES: everything mirrored from b2/c1 — anchor = first 5m bar containing the '
                 'ET mark; offset 0 = last completed bar before the touch bar; fixed bins as coded; '
                 'dial matrices re-used after the cb alignment gate; floor n>=50 on combo cells only. '
                 'Vectors: NaN = out of universe, counted; trade vectors carry the entry-bar and '
                 'same-bar third-outcome rules; ATRp = prior-day ATR14; STRUCT = corridor. '
                 'UNADJUSTED BY SVET\'S WORD: pre-ruling ATRp denominators run as signed; ruling 1 '
                 'governs future tables. Counts only; verdicts are Svet\'s.')
    open(f'{OUT}/REPORT.md', 'w').write('\n'.join(lines) + '\n')
    print('REPORT written')
print(f'total {round((time.time()-T0)/60,2)} min · deterministic, no RNG')
sys.exit(1 if any_fail else 0)
