# B1 tranche 2 — multi-frame features on the frozen 585,176-row vantage basis. Seed 20260723.
# Forward (15m/1h/4h/1D): fav/adv/end from station px over next <=100 completed F-bars starting at
#   the bar AFTER the one containing t_station (mirror of tranche-1's hit+1 exclusion); fnb_F = window
#   length; <5 bars -> NaN block. Orientation identical to tranche-1 (frm_below).
# Lookback (5m/15m/1h/4h/1D): prior w=min(100, available) completed F-bars ending at the last bar
#   fully closed before t_station; w<20 -> NaN block. net100/net20/rng100/pos100 in U, volr (20/100
#   mean volume), zt100 (bars overlapping event zone), zlast (bars since last overlap, 100 = none),
#   lnb_F = w.
# fwd5m_trunc: rows whose tranche-1 5m forward window was cut by the original raw end (from trunc_rows.json).
import numpy as np, pandas as pd, json, hashlib, os, time
np.random.seed(20260723)
SYMS = {'BTC':'BTCUSDT','ETH':'ETHUSDT','SOL':'SOLUSDT','XRP':'XRPUSDT'}
FRAMES = [('15m','15min'), ('1h','1h'), ('4h','4h'), ('1d','1D')]
V = pd.read_parquet('bf_vantage_ALL_5m.parquet')
trunc = {(c, int(e), s) for c, lst in json.load(open('trunc_rows.json')).items() for e, s in lst}
V['fwd5m_trunc'] = [ (c, int(e), s) in trunc for c, e, s in zip(V.coin, V.event_id, V.station) ]
parts = []
for NM, SYM in SYMS.items():
    ck = f'mfpart_{NM}.parquet'
    if os.path.exists(ck):
        parts.append(pd.read_parquet(ck)); print(NM, 'checkpoint reused', flush=True); continue
    t0 = time.time()
    A = V[V.coin == NM].copy()
    ev = pd.read_csv(f'p2_events_{NM}.csv')
    keep = ['id','side','z_lo','z_hi'] + (['exit_dir'] if 'exit_dir' in ev.columns else [])
    ev = ev[keep].drop_duplicates('id')
    A = A.merge(ev.rename(columns={'id':'event_id'}), on='event_id', how='left')
    fb = (A.side.astype(str) == 'below')
    if 'exit_dir' in A.columns: fb |= (A.exit_dir.astype(str) == 'up')
    A['frm_below'] = fb.values
    df = pd.read_csv(f'data/{SYM}_5m.csv')
    df['dt'] = pd.to_datetime(df.t, unit='ms', utc=True)
    last_close_ms = int(df.t.iloc[-1]) + 300_000
    ts = A.t_station.to_numpy(np.int64)
    px = A.st_px.to_numpy(float); Uu = A.U.to_numpy(float)
    zlo = A.z_lo.to_numpy(float); zhi = A.z_hi.to_numpy(float)
    fbv = A.frm_below.to_numpy(bool)
    frames_5m = [('5m', df[['t','h','l','c','v']].rename(columns={'t':'To','h':'H','l':'L','c':'C','v':'Vv'}))]
    for tag, rule in FRAMES:
        g = df.set_index('dt').resample(rule, label='left', closed='left').agg(
            H=('h','max'), L=('l','min'), C=('c','last'), Vv=('v','sum')).dropna(subset=['H'])
        g['To'] = ((g.index - pd.Timestamp(0, tz='UTC')) // pd.Timedelta('1ms')).astype('int64')
        dur = int(pd.Timedelta(rule).total_seconds()*1000)
        g = g[g.To + dur <= last_close_ms]                      # completed frame bars only
        frames_5m.append((tag, g.reset_index(drop=True)))
    for tag, g in frames_5m:
        To = g.To.to_numpy(np.int64); H = g.H.to_numpy(float); L = g.L.to_numpy(float)
        C = g.C.to_numpy(float); Vo = g.Vv.to_numpy(float); n = len(g)
        idx = np.searchsorted(To, ts, side='right') - 1         # containing bar
        # ---- lookback (all frames incl 5m) ----
        a = idx - 1                                             # last completed bar
        w = np.minimum(a + 1, 100); ok = w >= 20
        rmxH = pd.Series(H).rolling(100, min_periods=20).max().to_numpy()
        rmnL = pd.Series(L).rolling(100, min_periods=20).min().to_numpy()
        vm20 = pd.Series(Vo).rolling(20, min_periods=20).mean().to_numpy()
        vm100 = pd.Series(Vo).rolling(100, min_periods=20).mean().to_numpy()
        ac = np.clip(a, 0, n-1); i0 = np.maximum(0, a - w + 1); i20 = np.maximum(0, a - 19)
        C0 = C[ac]
        net100 = np.where(ok, (C0 - C[np.clip(i0,0,n-1)]) / Uu, np.nan)
        net20  = np.where(ok, (C0 - C[np.clip(i20,0,n-1)]) / Uu, np.nan)
        rr = rmxH[ac] - rmnL[ac]
        rng100 = np.where(ok, rr / Uu, np.nan)
        pos100 = np.where(ok & (rr > 0), (C0 - rmnL[ac]) / np.where(rr>0, rr, np.nan), np.nan)
        volr = np.where(ok & (vm100[ac] > 0), vm20[ac] / np.where(vm100[ac]>0, vm100[ac], np.nan), np.nan)
        zt = np.full(len(A), np.nan); zl = np.full(len(A), np.nan)
        for r in np.nonzero(ok & (a >= 0))[0]:
            s0 = i0[r]; aa = a[r]
            ov = (L[s0:aa+1] <= zhi[r]) & (H[s0:aa+1] >= zlo[r])
            zt[r] = ov.sum()
            nz = np.nonzero(ov)[0]
            zl[r] = (aa - (s0 + nz[-1])) if len(nz) else 100
        A[f'net100_{tag}'] = np.round(net100,3); A[f'net20_{tag}'] = np.round(net20,3)
        A[f'rng100_{tag}'] = np.round(rng100,3); A[f'pos100_{tag}'] = np.round(pos100,3)
        A[f'volr_{tag}'] = np.round(volr,3); A[f'zt100_{tag}'] = zt; A[f'zlast_{tag}'] = zl
        A[f'lnb_{tag}'] = np.where(a >= 0, w, 0).astype(np.int16)
        # ---- forward (higher frames only; 5m fwd exists in tranche-1) ----
        if tag == '5m': continue
        fmax = pd.Series(H[::-1]).rolling(100, min_periods=1).max().to_numpy()[::-1]
        fmin = pd.Series(L[::-1]).rolling(100, min_periods=1).min().to_numpy()[::-1]
        s = idx + 1
        fnb = np.clip(n - s, 0, 100)
        okf = fnb >= 5
        sc = np.clip(s, 0, n-1); ec = np.clip(s + fnb - 1, 0, n-1)
        mx = fmax[sc]; mn = fmin[sc]; Ce = C[ec]
        fav = np.where(fbv, (mx - px), (px - mn)) / Uu
        adv = np.where(fbv, (px - mn), (mx - px)) / Uu
        end = (Ce - px) / Uu * np.where(fbv, 1.0, -1.0)
        A[f'fav_{tag}'] = np.round(np.where(okf, fav, np.nan),3)
        A[f'adv_{tag}'] = np.round(np.where(okf, adv, np.nan),3)
        A[f'end_{tag}'] = np.round(np.where(okf, end, np.nan),3)
        A[f'fnb_{tag}'] = fnb.astype(np.int16)
    A = A.drop(columns=[c for c in ['side','exit_dir','z_lo','z_hi','frm_below'] if c in A.columns])
    A.to_parquet(ck, index=False)
    parts.append(A)
    print(NM, f'done {time.time()-t0:.0f}s rows {len(A)}', flush=True)
M = pd.concat(parts, ignore_index=True)
M.to_parquet('bf_vantage_ALL_mf.parquet', index=False)
new_cols = [c for c in M.columns if c not in V.columns or c == 'fwd5m_trunc']
print('rows', len(M), '| new cols', len([c for c in M.columns if c not in pd.read_parquet("bf_vantage_ALL_5m.parquet").columns]))
print('fwd5m_trunc rows:', int(M.fwd5m_trunc.sum()))
print('sha', hashlib.sha256(open('bf_vantage_ALL_mf.parquet','rb').read()).hexdigest()[:12],
      '| size MB', round(os.path.getsize('bf_vantage_ALL_mf.parquet')/1e6,1))
