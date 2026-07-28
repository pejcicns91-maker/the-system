#!/usr/bin/env python3
"""
DAILY BRIEF ENGINE v4 — "Daily Pack" (2026-07)
================================================
v3 + Option B integration + portable state. Designed to run inside a Claude chat
(code-execution sandbox), on a PC, or in any Python 3.9+ with pandas/numpy/requests
(+yfinance for the non-crypto & NDX legs; --ndx manual fallback exists).

STATE ROUND-TRIP (the Daily Pack mechanic):
  - If ./brief_state.zip is present (uploaded to the chat), it is unpacked automatically.
  - The engine fetches ONLY the missing bars since the last run (seconds, not minutes).
  - At the end it re-zips everything to ./brief_state.zip -> download it, upload tomorrow.
  - No zip present -> full bootstrap build (~3-6 min). `--rebuild` forces it.

WHAT IT PRINTS PER ASSET: range forecast + day-type + levels + direction lean
(validated cells only) + OPTION B block (sleeves fired at prior close, open positions,
overlap warnings when a down-lean opposes an open long) + one C-bridge payload line.

DIRECTION INVENTORY (earned; nothing else ships):
  A6b fade prior-day NDX: SOL .558/.581  XRP .553/.579  ETH .545/.564  BTC .540/.552
  E6c + I-1 (SOL only) | A8c DXY note (SOL/BTC/XRP, PROV) | F4-X FOMC overlay (SOL/BTC/ETH)
  ETH open-DON55 -> lean UP .577/.560 (R4 VALIDATED; supersedes A6b, forward-monitored)
  JPY don20-top -> slight_lean UP .581 (R4 PROV; provisional tier caps at slight_lean)
  R5-a FADE-open cells: PROV-NULL -> display-only, no lean.
All leans: no_bracket_vehicle. Wording ladder on 2024+ estimate; PROV caps at slight_lean.

USAGE: python3 brief_engine_v4.py [--date YYYY-MM-DD] [--at0900] [--ndx -0.0123]
       [--assets SOL,BTC] [--rebuild] [--eq 100000] [--dd -1.2]

v4.4 (2026-07-03) — six additions, display/infrastructure only, no rule changes:
  1. WEEKLY U line (crypto only) — HORIZON-validated pooled-KNN weekly range forecast
     (K=40, frozen features, walk-forward; Spearman .527, cov70/85 .753/.870). Frozen at
     the week's first brief in state/wk_forecasts.csv; "used" gauge + median-formed map.
  2. PW/PM levels for ALL assets (prior ISO-week & prior calendar-month H/L/C) — Layer-1
     map, ships on correctness. Payload gains PWH..PMC (+WU/WP70/WP85/WUSED/WDAY crypto).
     Existing CB2 Pine ignores unknown keys (key-scan parser) — payload is append-safe.
     MONTH forecast does NOT ship (registered exclusion; provisional only).
  3. REGIME light — BTC pi-state + per-asset Hayden-4H label + v1.2 gate status.
  4. DRIFT-GUARD (S1 doctrine) — cache is append-only; overlap tail re-fetched and
     compared each run. Genuine vendor revisions -> WARN, cached values kept ("detect,
     never absorb"). Exception: the cache's final bar, if it was an in-progress snapshot
     (same open, fresh H>=old H, fresh L<=old L), is silently REPAIRED — that is an
     engine artifact, not vendor history. This also fixes a v4.3 defect: incremental
     fetch started at last_ts+1ms, so the last cached 1d/4h bar (fetched mid-bar at
     08:00 ET) was never completed — stale partial bars slowly corrupted PDH/PDL/PDC,
     ATR and DON-55 state detection. v4.4 re-fetches the boundary bar every run.
  5. LOT-SIZE lines — per fired Option B signal: lots for 2*ATR stop at the v1.2-locked
     sizing (0.375% uniform, ladder 0.375/0.25/0.125 at -3/-6; config.yaml base_risk_pct
     values are pre-lock history). --eq equity (default 100000), --dd current drawdown %
     (default 0 -> step 1). JPY-quote via USDJPY, EUR-quote via EURUSD; min-lot rounding
     0.01 printed (indices may be 0.1 on account — verify).
  6. GER40 briefed (kind=y, ^GDAXI cash 1h since 2023-08; S1 unblocked). Cash-hours
     caveat: the 08:00-14:00 ET window truncates at Xetra close (~11:30 ET) and the
     overnight window is thin (5-6 bars) — printed as [cash-hours] on the asset line.
"""
import os, sys, csv, time, json, zipfile, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, requests
from datetime import datetime, timezone, date, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
HERE = os.path.dirname(os.path.abspath(__file__))
ST = os.path.join(HERE, "state"); LOG = os.path.join(ST, "direction_log_v4.csv")
ZIPF = os.path.join(HERE, "brief_state.zip")
HEAD = {"User-Agent": "Mozilla/5.0"}
API = "https://data-api.binance.vision/api/v3/klines"
K, WARMUP = 75, 300

ASSETS = {
 "SOL": dict(kind="b", sym="SOLUSDT", tier="FULL", a6b=(.558,.581), e6c=True,  a8c=True,  f4x=True),
 "BTC": dict(kind="b", sym="BTCUSDT", tier="FULL", a6b=(.540,.552), e6c=False, a8c=True,  f4x=True),
 "ETH": dict(kind="b", sym="ETHUSDT", tier="FULL", a6b=(.545,.564), e6c=False, a8c=False, f4x=True, ob_up=True),
 "XRP": dict(kind="b", sym="XRPUSDT", tier="FULL", a6b=(.553,.579), e6c=False, a8c=True,  f4x=False),
 "JPY": dict(kind="y", sym="JPY=X",   tier="PROV", a6b=None, jtop=True),
 "US30": dict(kind="y", sym="YM=F",   tier="PROV", a6b=None),
 "US500": dict(kind="y", sym="ES=F",  tier="PROV", a6b=None),
 "US100": dict(kind="y", sym="NQ=F",  tier="PROV", a6b=None),
 "GER40": dict(kind="y", sym="^GDAXI", tier="PROV", a6b=None, cash=True),
}
PENDING = {"XAU":"band recalibration pending","XAG":"band recalibration pending"}
# Option B universe on ITS OWN feeds (matches bt.py / the validated books exactly)
OB_FEED = {"XAUUSD":"GC=F","XAGUSD":"SI=F","USDJPY":"JPY=X","US30":"^DJI","GER40":"^GDAXI","US500":"^GSPC","US100":"^NDX"}
SLEEVES = {"FADE": dict(instr=["XAUUSD","USDJPY","US30","GER40","US500","US100"], tf="d", texit=10, kind="fade"),
           "DON20": dict(instr=["XAUUSD","XAGUSD","US500","US100"], tf="d", texit=40, kind="don", lb=20),
           "DON55": dict(instr=["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT"], tf="4h", texit=48, kind="don", lb=55)}
BRIEF2OB = {"SOL":"SOLUSDT","BTC":"BTCUSDT","ETH":"ETHUSDT","XRP":"XRPUSDT","JPY":"USDJPY","US30":"US30","US500":"US500","US100":"US100","GER40":"GER40"}
BRIEF2OB_R = {"SOLUSDT":"SOL","BTCUSDT":"BTC","ETHUSDT":"ETH","XRPUSDT":"XRP"}
FOMC = {"2026-01-28","2026-03-18","2026-04-29","2026-06-17","2026-07-29","2026-09-16","2026-10-28","2026-12-09",
        "2025-01-29","2025-03-19","2025-05-07","2025-06-18","2025-07-30","2025-09-17","2025-10-29","2025-12-10"}

VERSION = "4.4"
# --- v4.4 constants -----------------------------------------------------------
# HORIZON Layer-2 pooled median cum-range fraction by elapsed day (horizon_results.json,
# seed 20260711, descriptive map — embedded, refresh at a future rev if desired)
WEEK_MED  = {1:.42, 2:.60, 3:.76, 4:.89, 5:1.00, 6:1.00, 7:1.00}
MONTH_MED = {1:.17,2:.24,3:.29,4:.33,5:.38,6:.42,7:.47,8:.50,9:.56,10:.60,11:.63,12:.66}
# HORIZON Layer-3 WEEK model (VALIDATED): pooled KNN over 4 cryptos, frozen features
WK_K, WK_MIN_TRAIN = 40, 100
# FTMO 2-Step Swing contracts (verified ftmo.com symbols API 2026-06-12; confirm on account)
CONTRACTS = {"XAUUSD":(100,"USD"),"XAGUSD":(5000,"USD"),"USDJPY":(100000,"JPY"),
             "US30":(1,"USD"),"GER40":(1,"EUR"),"US500":(1,"USD"),"US100":(1,"USD"),
             "BTCUSDT":(1,"USD"),"ETHUSDT":(10,"USD"),"SOLUSDT":(100,"USD"),"XRPUSDT":(10000,"USD")}
CRYPTO_LEV = 1  # swing crypto 1:1 -> margin = notional
def ladder_step(dd_pct):
    """v1.2-locked sizing: 0.375% uniform base; steps at -3%/-6% (OPTION_B_v1_2.md)."""
    base = 0.375
    return base if dd_pct > -3 else (base*2/3 if dd_pct > -6 else base/3)

def et_utc(d, hh, mm=0): return pd.Timestamp(datetime(d.year,d.month,d.day,hh,mm,tzinfo=ET)).tz_convert("UTC")
def fp(x): return f"{x:.0f}" if x>=5000 else f"{x:.2f}" if x>=10 else f"{x:.4f}"

# ---------------- data layer (incremental) ----------------
DRIFT = []   # v4.4: (source, symbol, n_rows, max_rel_diff) — printed in the brief header

def _merge_guard(old, new, src, key):
    """v4.4 append-only merge with drift-guard.
    old/new indexed identically (dt or date). Rules:
      - rows only in `new` -> appended
      - overlap rows equal (rtol 2e-6) -> nothing
      - FINAL old row(s) that are an in-progress snapshot of the fresh bar
        (same open, new H >= old H, new L <= old L) -> REPAIRED silently (engine
        artifact, not vendor history; fixes the v4.3 stale-boundary-bar defect)
      - any other overlap difference -> DRIFT warning, CACHED VALUES KEPT (S1: detect,
        never absorb)."""
    if old is None or not len(old): return new, 0
    ov = new.index.intersection(old.index)
    add = new.loc[new.index.difference(old.index)]
    rep = 0
    if len(ov):
        o_, n_ = old.loc[ov, ["o","h","l","c"]].astype(float), new.loc[ov, ["o","h","l","c"]].astype(float)
        bad = ~np.isclose(o_.values, n_.values, rtol=2e-6, atol=1e-12).all(axis=1)
        if bad.any():
            last_old = old.index[-1]
            keep_bad = []
            for ix in ov[bad]:
                same_open = np.isclose(float(o_.loc[ix,"o"]), float(n_.loc[ix,"o"]), rtol=2e-6)
                envelope  = (float(n_.loc[ix,"h"]) >= float(o_.loc[ix,"h"]) - 1e-12 and
                             float(n_.loc[ix,"l"]) <= float(o_.loc[ix,"l"]) + 1e-12)
                if ix == last_old and same_open and envelope:
                    old.loc[ix, ["o","h","l","c"]] = n_.loc[ix].values; rep += 1
                else:
                    keep_bad.append(ix)
            if keep_bad:
                mx = float(np.max(np.abs(n_.loc[keep_bad,"c"].values/o_.loc[keep_bad,"c"].values - 1)))
                DRIFT.append((src, key, len(keep_bad), mx))
    out = pd.concat([old, add]).sort_index()
    return out, rep

def binance(sym, iv, start_dt=None):
    fpth = f"{ST}/{sym}_{iv}.pkl"
    old = pd.read_pickle(fpth) if os.path.exists(fpth) else None
    if old is not None:
        # v4.4: re-fetch from OVERLAP bars back (drift-guard + completes the boundary bar)
        tail = old["dt"].iloc[-min(len(old), 10)]
        start = int(tail.timestamp()*1000)
    else:
        start = int((start_dt or datetime(2020,8,1,tzinfo=timezone.utc)).timestamp()*1000)
    end = int(datetime.now(timezone.utc).timestamp()*1000)
    out, cur = [], start
    while cur < end:
        for _ in range(3):
            try:
                r = requests.get(API, params=dict(symbol=sym, interval=iv, startTime=cur, endTime=end, limit=1000),
                                 headers=HEAD, timeout=30)
                if r.status_code == 200: break
            except Exception: pass
            time.sleep(1)
        d = r.json()
        if not d: break
        out += d
        if len(d) < 1000: break
        cur = d[-1][0]+1; time.sleep(0.04)
    if out:
        new = pd.DataFrame(out, columns=["t","o","h","l","c","v","ct","qv","n","tb","tq","ig"])
        for k_ in ["o","h","l","c"]: new[k_] = new[k_].astype(float)
        new["dt"] = pd.to_datetime(new["t"].astype(np.int64), unit="ms", utc=True)
        new = new[["dt","o","h","l","c"]].set_index("dt")
        oldx = old.set_index("dt") if old is not None else None
        merged, _ = _merge_guard(oldx, new, "binance", f"{sym}_{iv}")
        old = merged.reset_index(); old.to_pickle(fpth)
    return old

def binance_1h_since(sym, since_dt):
    """fresh (not stored) 1h from `since_dt` for session updates + today's overnight"""
    s = int(pd.Timestamp(since_dt).tz_localize("UTC").timestamp()*1000) if pd.Timestamp(since_dt).tzinfo is None \
        else int(pd.Timestamp(since_dt).timestamp()*1000)
    out, cur, end = [], s, int(datetime.now(timezone.utc).timestamp()*1000)
    while cur < end:
        r = requests.get(API, params=dict(symbol=sym, interval="1h", startTime=cur, endTime=end, limit=1000),
                         headers=HEAD, timeout=30); d = r.json()
        if not d: break
        out += d
        if len(d) < 1000: break
        cur = d[-1][0]+1; time.sleep(0.04)
    df = pd.DataFrame(out, columns=["t","o","h","l","c","v","ct","qv","n","tb","tq","ig"])
    for k_ in ["o","h","l","c"]: df[k_] = df[k_].astype(float)
    df["dt"] = pd.to_datetime(df["t"].astype(np.int64), unit="ms", utc=True)
    return df[["dt","o","h","l","c"]].set_index("dt").sort_index()

def yahoo_daily(sym, tag):
    import yfinance as yf
    fpth = f"{ST}/{tag}_1d.pkl"
    old = pd.read_pickle(fpth) if os.path.exists(fpth) else None
    per = "max" if old is None else "3mo"
    h = yf.download(sym, period=per, interval="1d", progress=False, auto_adjust=True)
    if isinstance(h.columns, pd.MultiIndex): h.columns = h.columns.get_level_values(0)
    h = h.rename(columns={"Open":"o","High":"h","Low":"l","Close":"c"})[["o","h","l","c"]].dropna()
    if old is not None:
        # v4.4: S1 append-only — cached history is never overwritten by a vendor re-print;
        # differences beyond tolerance raise a DRIFT warning; only the boundary bar
        # (in-progress snapshot) is repaired.
        h, _ = _merge_guard(old, h, "yahoo", tag)
    h.to_pickle(fpth); return h

def yahoo_1h(sym, days):
    import yfinance as yf
    h = yf.download(sym, period=f"{min(max(days,8),720)}d", interval="1h", progress=False, auto_adjust=True)
    if isinstance(h.columns, pd.MultiIndex): h.columns = h.columns.get_level_values(0)
    h = h.rename(columns={"Open":"o","High":"h","Low":"l","Close":"c"})[["o","h","l","c"]].dropna()
    h.index = h.index.tz_convert("UTC") if h.index.tz is not None else h.index.tz_localize("UTC")
    return h

# ---------------- session history maintenance ----------------
def to_daily_frame(obj):
    if isinstance(obj, pd.DataFrame) and "dt" in obj.columns:
        return pd.DataFrame(dict(d=[x.date() for x in obj["dt"]], o=obj["o"].values,h=obj["h"].values,
                                 l=obj["l"].values,c=obj["c"].values))
    return pd.DataFrame(dict(d=[x.date() for x in obj.index], o=obj["o"].values,h=obj["h"].values,
                             l=obj["l"].values,c=obj["c"].values))

def update_sessions(nm, cfg, D, today):
    fpth = f"{ST}/{nm}_sess.csv"
    S = pd.read_csv(fpth) if os.path.exists(fpth) else pd.DataFrame(columns=["date","pc","wr","on_move","on_rng"])
    last = pd.Timestamp(S["date"].iloc[-1]).date() if len(S) else date(2020,8,10)
    if last >= today - timedelta(days=1): return S
    if cfg["kind"] == "b":
        H = binance_1h_since(cfg["sym"], pd.Timestamp(last) - pd.Timedelta(days=1))
    else:
        H = yahoo_1h(cfg["sym"], (today - last).days + 6)
    Hi = H.index; dmap = {r.d:i for i,r in enumerate(D.itertuples())}
    rows, d = [], last + timedelta(days=1)
    while d < today:
        if pd.Timestamp(d).weekday() < 5 and dmap.get(d) not in (None, 0):
            di = dmap[d]; pcv = float(D["c"].iloc[di-1])
            w0, wE = et_utc(d,8), et_utc(d,14)
            win = H.loc[(Hi>=w0)&(Hi<wE)]; on = H.loc[(Hi>=w0-pd.Timedelta(hours=14))&(Hi<w0)]
            if len(win) >= 3 and win.index[0] == w0 and len(on) >= 5:
                rows.append(dict(date=str(d), pc=pcv,
                    wr=(float(win["h"].max())-float(win["l"].min()))/pcv,
                    on_move=abs(float(win["c"].iloc[0])-float(on["c"].iloc[-1]))/pcv,
                    on_rng=(float(on["h"].max())-float(on["l"].min()))/pcv))
        d += timedelta(days=1)
    if rows: S = pd.concat([S, pd.DataFrame(rows)], ignore_index=True)
    S.to_csv(fpth, index=False); return S

# ---------------- frozen forecast core ----------------
def daily_feats(D):
    pc = D["c"].shift(); h,l,c = D["h"],D["l"],D["c"]
    ret = c.pct_change(); tr = np.maximum(h-l, np.maximum((h-pc).abs(),(l-pc).abs()))
    atr14 = tr.ewm(alpha=1/14, adjust=False).mean(); ma50 = c.rolling(50).mean()
    hi20, lo20 = h.rolling(20).max(), l.rolling(20).min()
    rv14, rv90 = ret.rolling(14).std(), ret.rolling(90).std()
    return pd.DataFrame({"atrpct":(atr14/c).shift(1),"donch_pos":(((c-lo20)/(hi20-lo20)).clip(0,1)).shift(1),
        "dist_ma50_atr":((c-ma50)/atr14).shift(1),"vol_z":((rv14-rv90)/rv90).shift(1),
        "daily_rng14":((h-l)/pc).rolling(14).mean().shift(1)}, index=range(len(D)))

def forecast(nm, cfg, D, S, d, at0900):
    F = daily_feats(D); dmap = {r.d:i for i,r in enumerate(D.itertuples())}
    S = S.copy(); S["di"] = [dmap.get(pd.Timestamp(x).date()) for x in S["date"]]
    S = S[S["di"].notna()]; hist = S["wr"].shift(1)
    S["wrng_prev"], S["wrng5"], S["wrng14"] = hist, hist.rolling(5).mean(), hist.rolling(14).mean()
    for col in F.columns: S[col] = [F[col].iloc[int(di)] for di in S["di"]]
    feats = ["atrpct","wrng_prev","wrng5","wrng14","donch_pos","dist_ma50_atr","vol_z","daily_rng14","on_move","on_rng"]
    ok = S[feats+["wr"]].notna().all(axis=1)
    Xp, yp = S.loc[ok,feats].values.astype(float), S.loc[ok,"wr"].values.astype(float)
    if len(yp) < WARMUP+10: raise RuntimeError(f"{nm}: history too short ({len(yp)})")
    if cfg["kind"] == "b": H = binance_1h_since(cfg["sym"], pd.Timestamp(d)-pd.Timedelta(days=2))
    else: H = yahoo_1h(cfg["sym"], 6)
    Hi = H.index; w0 = et_utc(d,8)
    on = H.loc[(Hi>=w0-pd.Timedelta(hours=14))&(Hi<w0)]
    if len(on) < 5: raise RuntimeError(f"{nm}: no overnight for {d}")
    onH,onL,onc = float(on["h"].max()), float(on["l"].min()), float(on["c"].iloc[-1])
    if at0900:
        wb = H.loc[(Hi>=w0)&(Hi<w0+pd.Timedelta(hours=1))]
        px8 = float(wb["c"].iloc[-1]) if len(wb) else onc
    else: px8 = onc
    di_prev = (dmap.get(d) or len(D)) - 1
    pcv = float(D["c"].iloc[di_prev])
    fi = dmap.get(d, len(D)-1)
    fr = {c_: (float(F[c_].iloc[fi]) if F[c_].iloc[fi]==F[c_].iloc[fi] else float(F[c_].iloc[-1])) for c_ in F.columns}
    lw = S.loc[ok,"wr"]
    xq = np.array([fr["atrpct"], lw.iloc[-1], lw.iloc[-5:].mean(), lw.iloc[-14:].mean(),
                   fr["donch_pos"], fr["dist_ma50_atr"], fr["vol_z"], fr["daily_rng14"],
                   abs(px8-onc)/pcv, (onH-onL)/pcv], dtype=float)
    mu, sd = Xp.mean(0), Xp.std(0)+1e-9
    dist = np.sqrt((((Xp-mu)/sd - (xq-mu)/sd)**2).sum(1))
    nn = np.argpartition(dist, K)[:K]; rr = yp[nn]; trail = yp[-90:]
    med = float(np.median(rr))
    return dict(U=med, p70=float(np.percentile(rr,70)), p85=float(np.percentile(rr,85)),
        dtype="EXPANSION" if med>np.percentile(trail,80) else ("QUIET" if med<np.percentile(trail,20) else "normal"),
        pc=pcv, spot=onc, onH=onH, onL=onL,
        on_pos=(onc-onL)/(onH-onL) if onH>onL else np.nan,
        PDH=float(D["h"].iloc[di_prev]), PDL=float(D["l"].iloc[di_prev]), PDC=pcv,
        don20=fr["donch_pos"])

# ---------------- Option B module (frozen bt.py conventions) ----------------
def prep_ob(df):
    pc = df["c"].shift(); tr = np.maximum(df.h-df.l, np.maximum((df.h-pc).abs(),(df.l-pc).abs()))
    df = df.copy(); df["atr"] = tr.rolling(14).mean()
    df["hh20"] = df.h.shift(1).rolling(20).max(); df["hh55"] = df.h.shift(1).rolling(55).max()
    df["ret5"] = df.c/df.c.shift(5)-1
    return df

def sigmask(df, cfg):
    if cfg["kind"]=="fade": return ((df.ret5 < -1.0*(df.atr/df.c)*np.sqrt(5)) & df.atr.notna()).values
    hh = df[f"hh{cfg['lb']}"]; return ((df.c > hh) & hh.notna() & df.atr.notna()).values

def exit_bar(df, i, texit):
    o,h,l,c = df.o.values, df.h.values, df.l.values, df.c.values
    entry, atr = c[i], df.atr.values[i]; stop, tgt = entry-2*atr, entry+2*atr; halved=False
    for j in range(i+1, len(df)):
        if o[j] <= stop: return j
        if not halved and o[j] >= tgt:
            halved=True; stop=entry
            if l[j] <= stop: return j
        elif l[j] <= stop: return j
        elif not halved and h[j] >= tgt: halved=True; stop=entry
        if j-i == texit: return j
    return len(df)-1

def ob_state(sleeve, sym, df, d):
    """returns (fired_recently, open_now, entry_info) at 08:00 ET of date d"""
    cfg = SLEEVES[sleeve]; df = prep_ob(df); sig = sigmask(df, cfg)
    w0 = et_utc(d,8)
    if cfg["tf"] == "4h":
        tclose = df["dt"] + pd.Timedelta(hours=4)
        idx_before = np.where((tclose <= w0).values & sig)[0]
        fired = bool(len(np.where(((tclose > w0-pd.Timedelta(days=1)) & (tclose <= w0)).values & sig)[0]))
    else:
        dts = [x.date() if hasattr(x,"date") else x for x in (df["dt"].dt.date if "dt" in df else df["d"])]
        df = df.reset_index(drop=True)
        idx_before = np.array([i for i in np.where(sig)[0] if dts[i] < d])
        fired = bool(len(idx_before)) and dts[idx_before[-1]] >= d - timedelta(days=4) and \
                dts[idx_before[-1]] == max(x for x in dts if x < d)
    open_now, info = False, None
    i, n = 60, len(df)
    last_exit = -1
    while i < n:
        if sig[i] and i > last_exit:
            e = exit_bar(df, i, cfg["texit"])
            if cfg["tf"]=="4h":
                t_in, t_out = df["dt"].iloc[i]+pd.Timedelta(hours=4), df["dt"].iloc[e]+pd.Timedelta(hours=4)
                if t_in <= w0 < t_out: open_now, info = True, dict(entry=float(df.c.iloc[i]), since=str(t_in.date()))
            else:
                d_in, d_out = dts[i], dts[e]
                if d_in < d <= d_out: open_now, info = True, dict(entry=float(df.c.iloc[i]), since=str(d_in))
            last_exit = e; i = e
            if not (i < n and sig[i]): i += 1
        else: i += 1
    return fired, open_now, info

# ---------------- shared conditioners ----------------
def get_ndx(manual, d):
    if manual is not None: return manual, "manual"
    try:
        import yfinance as yf
        h = yf.download("^NDX", period="30d", interval="1d", progress=False, auto_adjust=True)
        if isinstance(h.columns, pd.MultiIndex): h.columns = h.columns.get_level_values(0)
        h = h[[x.date() < d for x in h.index]]; r = h["Close"].pct_change().dropna()
        return float(r.iloc[-1]), f"^NDX {h.index[-1].date()}"
    except Exception as e: return None, f"unavailable ({type(e).__name__})"

def get_dxy(d):
    try:
        h = yahoo_1h("DX-Y.NYB", 5); idx = h.index; p8 = et_utc(d,8)
        a = h["o"][idx<=p8]; b = h["o"][idx<=p8-pd.Timedelta(hours=13)]
        if len(a) and len(b): return float(a.iloc[-1]/b.iloc[-1]-1)
    except Exception: pass
    return None

def round_step(p):
    for s in [0.0001,0.001,0.01,0.1,0.5,1,2,5,10,25,50,100,250,500,1000,2500]:
        if 0.004*p <= s <= 0.02*p: return s
    return 10**int(np.floor(np.log10(p)))/10

# ---------------- v4.4: WEEKLY module (HORIZON Layer-3 WEEK, VALIDATED) ----------------
def _isoweek(dd): i = pd.Timestamp(dd).isocalendar(); return f"{i.year}-W{i.week:02d}"

def _weekly_rows(cd1):
    """Pooled (asset, week_start, y, features) rows — exact horizon_bootstrap.run_l3('W')
    feature recipe: [prev wk rng, mean4, mean8, mean13, rv14/rv90, ATR14%/c, donch20 pos,
    21d rng/c] all as-of the day BEFORE the week's first day. Pooled across 4 cryptos,
    sorted by week-start date (cross-asset neighbors, as validated)."""
    rows = []
    for nm, df in cd1.items():
        df = df.copy(); df["d"] = [x.date() for x in df["dt"]]
        df["W"] = [_isoweek(x) for x in df["d"]]
        g = df.groupby("W", sort=True)
        P = pd.DataFrame(dict(H=g["h"].max(), L=g["l"].min(), C=g["c"].last(),
                              first=g["d"].first())).reset_index()
        P["PC"] = P["C"].shift(1); P["rng"] = (P["H"]-P["L"])/P["PC"]
        c = df.set_index("d")["c"]
        rv14 = c.pct_change().rolling(14).std(); rv90 = c.pct_change().rolling(90).std()
        atrp = ((df["h"]-df["l"]).rolling(14).mean()/df["c"]).values
        hi20 = df["h"].rolling(20).max(); lo20 = df["l"].rolling(20).min()
        dpos = ((df["c"]-lo20)/(hi20-lo20)).values
        aux  = (df["h"].rolling(21).max()-df["l"].rolling(21).min())/df["c"]
        dmap = {dd_: i for i, dd_ in enumerate(df["d"])}
        r = P["rng"].values
        for idx in range(14, len(P)):
            d0 = P["first"].iloc[idx]; di = dmap.get(d0)
            if di is None or di < 95: continue
            fs = [r[idx-1], np.nanmean(r[idx-4:idx]), np.nanmean(r[idx-8:idx]), np.nanmean(r[idx-13:idx]),
                  float(rv14.iloc[di-1]/rv90.iloc[di-1]) if rv90.iloc[di-1] > 0 else np.nan,
                  float(atrp[di-1]), float(dpos[di-1]), float(aux.iloc[di-1])]
            y = float(P["rng"].iloc[idx])
            if all(x == x for x in fs):
                rows.append(dict(asset=nm, wk=P["W"].iloc[idx], d0=str(d0),
                                 y=y if y == y else np.nan, f=fs))
    rows.sort(key=lambda r_: r_["d0"])
    return rows

def weekly_forecast(nm, d, cd1):
    """Forecast the CURRENT ISO week's range for asset nm, frozen at first computation
    (state/wk_forecasts.csv). Training = all pooled COMPLETED prior weeks (d0 < this
    week's start AND week != any current week), K=min(40, t-1), median/p70/p85 of
    neighbor realized ranges. Returns dict or None (guards: pooled train >= 100)."""
    fpth = f"{ST}/wk_forecasts.csv"
    wk = _isoweek(d)
    Fz = pd.read_csv(fpth) if os.path.exists(fpth) else pd.DataFrame(
        columns=["asset","week","d0","U","p70","p85","ntrain"])
    hit = Fz[(Fz["asset"] == nm) & (Fz["week"] == wk)]
    if len(hit):
        h0 = hit.iloc[0]
        return dict(U=float(h0["U"]), p70=float(h0["p70"]), p85=float(h0["p85"]),
                    week=wk, frozen=True)
    rows = _weekly_rows(cd1)
    cur = [r_ for r_ in rows if r_["asset"] == nm and r_["wk"] == wk]
    if not cur: return None
    q = cur[0]
    train = [r_ for r_ in rows if r_["d0"] < q["d0"] and r_["wk"] != wk and r_["y"] == r_["y"]]
    if len(train) < WK_MIN_TRAIN: return None
    X = np.array([r_["f"] for r_ in train]); Y = np.array([r_["y"] for r_ in train])
    mu, sd = X.mean(0), X.std(0)+1e-9
    dd_ = np.sqrt((((X-mu)/sd - (np.array(q["f"])-mu)/sd)**2).sum(1))
    k = min(WK_K, len(train)-1)
    nb = np.argpartition(dd_, k)[:k]
    U, p70, p85 = float(np.median(Y[nb])), float(np.percentile(Y[nb],70)), float(np.percentile(Y[nb],85))
    Fz = pd.concat([Fz, pd.DataFrame([dict(asset=nm, week=wk, d0=q["d0"], U=round(U,5),
                    p70=round(p70,5), p85=round(p85,5), ntrain=len(train))])], ignore_index=True)
    Fz.to_csv(fpth, index=False)
    return dict(U=U, p70=p70, p85=p85, week=wk, frozen=False)

def week_month_ctx(D, d):
    """Layer-1 map for ANY asset: prior completed ISO-week and prior calendar-month
    H/L/C, plus current week/month to-date extremes, elapsed-day counts and PC bases.
    Pure arithmetic on the asset's own daily frame (includes today's partial bar)."""
    dd = D.copy(); dd = dd[[x is not None for x in dd["d"]]]
    dd = dd[dd["d"] <= d]
    wkkey = [_isoweek(x) for x in dd["d"]]; mokey = [f"{x.year}-{x.month:02d}" for x in dd["d"]]
    dd = dd.assign(W=wkkey, M=mokey)
    cw, cm = _isoweek(d), f"{d.year}-{d.month:02d}"
    out = {}
    for tag, key, curk in [("PW","W",cw), ("PM","M",cm)]:
        g = dd.groupby(key, sort=True)
        P = pd.DataFrame(dict(H=g["h"].max(), L=g["l"].min(), C=g["c"].last()))
        prior = P[P.index < curk]
        if len(prior):
            pr = prior.iloc[-1]
            out[tag] = dict(H=float(pr["H"]), L=float(pr["L"]), C=float(pr["C"]))
        curg = dd[dd[key] == curk]
        if len(curg):
            out[tag+"td"] = dict(H=float(curg["h"].max()), L=float(curg["l"].min()),
                                 day=len(curg))
    return out

# ---------------- v4.4: lot sizing (display arithmetic; rulebook executes) ----------------
def q2usd(quote, usdjpy_c, eurusd_c):
    if quote == "USD": return 1.0
    if quote == "JPY": return (1.0/usdjpy_c) if usdjpy_c else None
    if quote == "EUR": return eurusd_c
    return None

def lot_line(sym, px, atr, eq, step_pct, usdjpy_c, eurusd_c):
    if sym not in CONTRACTS or not (atr == atr) or atr <= 0: return None
    csize, quote = CONTRACTS[sym]
    fx = q2usd(quote, usdjpy_c, eurusd_c)
    if fx is None: return f"    SIZE {sym}: {quote}-quote rate unavailable -- size manually"
    risk = eq*step_pct/100.0; stop = 2.0*atr
    lots = risk/(stop*csize*fx)
    lots_r = np.floor(lots*100)/100
    ntl = lots_r*csize*px*fx
    note = " [min-lot may be 0.1 on indices -- verify]" if sym in ("US30","GER40","US500","US100") else ""
    marg = f" | 1:1 margin ${ntl:,.0f}" if sym.endswith("USDT") else ""
    return (f"    SIZE {sym}: stop 2*ATR={fp(stop)} -> {lots:.3f} lots (round {lots_r:.2f})"
            f" @ ${risk:,.0f} risk | ntl ${ntl:,.0f}{marg}{note}")

def fired_size_info(sleeve, sym, df):
    """(close, ATR14) at the most recent signal bar for a fired sleeve (bt.py conventions)."""
    cfg = SLEEVES[sleeve]; df = prep_ob(df); sig = sigmask(df, cfg)
    ix = np.where(sig)[0]
    if not len(ix): return None
    i = int(ix[-1])
    return float(df["c"].iloc[i]), float(df["atr"].iloc[i])

# ---------------- direction (locked rules) ----------------
def direction(nm, cfg, core, ndx, dxy, is_fomc, ob_open55):
    notes, basis = [], []; out = dict(dir="none", strength="none")
    if cfg.get("a6b") and ndx is not None and ndx != 0:
        hist, y24 = cfg["a6b"]; strength = "lean" if y24 >= .58 else "slight_lean"
        if ndx > 0: out = dict(dir="down", strength=strength, hist=hist, y24=y24); basis=["A6b"]
        else:
            out = dict(dir="up", strength="slight_lean", hist=hist, y24=y24); basis=["A6b"]
            if nm == "SOL": out.update(hist=.525, y24=.525)
    if cfg.get("e6c") and core["on_pos"]==core["on_pos"] and core["on_pos"]>=0.75:
        if ndx is None:
            out = dict(dir="down", strength="lean", hist=.583, y24=.563); basis=["E6c"]; notes.append("E6c alone (NDX missing); decay caveat")
        elif ndx > 0:
            basis.append("E6c"); notes.append("I-1 AGREE-DOWN (fwd gate 30 firings; capped at lean)")
        else:
            out = dict(dir="none", strength="none"); basis=["I-1 CONFLICT"]; notes.append("E6c vs NDX-down -> no lean")
    if cfg.get("ob_up") and ob_open55:
        out = dict(dir="up", strength="slight_lean", hist=.577, y24=.560); basis=["OB-state(open-DON55)"]
        notes.append("R4-validated; supersedes A6b on open days (forward-monitored precedence)")
    if cfg.get("jtop") and core.get("don20",np.nan) >= 2/3:
        out = dict(dir="up", strength="slight_lean", hist=.581, y24=.581); basis=["JPY don20-top [PROV]"]
    if cfg.get("a8c") and dxy is not None and out["dir"]=="down":
        notes.append(("+DXY agrees" if dxy>0 else "DXY disagrees")+" (A8c PROV, note-only)")
    if cfg.get("f4x") and is_fomc:
        notes.append("FOMC 14:00 ET: F4-X pre-decision drift UP (validated-mechanism; 2024+ ~57%)")
    out.update(basis="+".join(basis) if basis else "none", notes=notes, no_bracket_vehicle=True)
    return out

# ---------------- forward log ----------------
def log_and_grade(d, todays, graders):
    fields = ["date","asset","dir","strength","basis","ovl","outcome"]
    rows = list(csv.DictReader(open(LOG))) if os.path.exists(LOG) else []
    for r in rows:
        if not r["outcome"] and r["asset"] in graders:
            H = graders[r["asset"]]; Hi = H.index; dd = pd.Timestamp(r["date"]).date()
            a = H.loc[Hi==et_utc(dd,8)]; b = H.loc[Hi==et_utc(dd,13)]
            if len(a) and len(b): r["outcome"] = "up" if float(b["c"].iloc[0])>float(a["o"].iloc[0]) else "down"
    have = {(r["date"],r["asset"]) for r in rows}
    for nm,(dr,ovl) in todays.items():
        if (str(d),nm) not in have:
            rows.append(dict(date=str(d),asset=nm,dir=dr["dir"],strength=dr["strength"],basis=dr["basis"],ovl=int(ovl),outcome=""))
    w = csv.DictWriter(open(LOG,"w",newline=""), fieldnames=fields); w.writeheader()
    for r in rows: w.writerow({k:r.get(k,"") for k in fields})
    g=[r for r in rows if r["outcome"] and r["dir"] in ("up","down")]
    return len(g), sum(1 for r in g if r["dir"]==r["outcome"]), \
           sum(1 for r in rows if r["asset"]=="SOL" and "E6c" in str(r["basis"]) and "A6b" in str(r["basis"]) and r["outcome"])

# ---------------- main ----------------
def scenarios(core, dr, spot, rnd, open55, has_long):
    """2-3 honest trade scenarios from validated pieces: range budget + level map + leans + OB state.
    Returns (human_lines, payload_frag). Direction is never invented: lean tags only where a
    validated cell applies; everything else is explicitly [context]."""
    U, PDC = core["U"], core["PDC"]
    buf = 0.15*U*PDC; cap = 0.70*U*PDC
    levs = [("PDH",core["PDH"]),("PDL",core["PDL"]),("PDC",PDC),("ONH",core["onH"]),("ONL",core["onL"]),("RND",rnd)]
    levs = [(n,v) for n,v in levs if v==v and v>0]
    ups = sorted([lv for lv in levs if lv[1]>spot], key=lambda x:x[1])
    dns = sorted([lv for lv in levs if lv[1]<spot], key=lambda x:x[1], reverse=True)
    def mk(kind, trig, tgt, inv, tag):
        return dict(kind=kind, trig=trig, tgt=tgt, inv=inv, tag=tag)
    out=[]
    lean = dr["dir"] if dr["dir"] in ("up","down") else None
    lt = f"lean {dr.get('hist','')}" if lean else "context"
    # break-up
    if ups:
        t = ups[0]; tgt = ups[1][1] if len(ups)>1 and ups[1][1]<=spot+cap else spot+cap
        out.append(mk("LONG", (t[0],t[1]), tgt, t[1]-buf, lt if lean=="up" else "context"))
    # break-down
    if dns:
        t = dns[0]; tgt = dns[1][1] if len(dns)>1 and dns[1][1]>=spot-cap else spot-cap
        out.append(mk("SHORT", (t[0],t[1]), tgt, t[1]+buf, lt if lean=="down" else "context"))
    # range-fade (QUIET days, or no lean on a normal day)
    if core["dtype"]=="QUIET" or (lean is None and core["dtype"]!="EXPANSION"):
        if ups:
            f_ = ups[-1] if ups[-1][1]<=spot+cap else ups[0]
            ftgt = max([v for v in (PDC, core["onL"]) if v==v and v < f_[1]] or [spot-cap])
            ftgt = max(ftgt, spot-cap)
            out.append(mk("FADE", (f_[0],f_[1]), ftgt, f_[1]+buf,
                          "QUIET-day context" if core["dtype"]=="QUIET" else "context"))
    # v4.4 guard: a scenario whose target is not beyond its trigger is geometrically
    # dead (tiny-U days made spot+cap fall inside the trigger) — suppress, don't print.
    out = [s_ for s_ in out if (s_["kind"]=="LONG" and s_["tgt"]>s_["trig"][1]) or
                               (s_["kind"] in ("SHORT","FADE") and s_["tgt"]<s_["trig"][1])]
    # order: lean-aligned first
    if lean: out.sort(key=lambda x_: 0 if ((x_["kind"]=="LONG")==(lean=="up") and x_["kind"]!="FADE") else 1)
    out = out[:3]
    lines=[]; frags=[]
    for i,sc in enumerate(out,1):
        warn = ""
        if sc["kind"]=="SHORT" and has_long: warn = " !!opposes-open-OB-long"
        if sc["kind"]=="LONG" and open55: warn = " (OB already long: duplicates exposure)"
        verb = "hold>" if sc["kind"]=="LONG" else "hold<" if sc["kind"]=="SHORT" else "probe "
        arrow = "-> tgt" if sc["kind"]!="FADE" else "-> back to"
        lines.append(f"       S{i} {sc['kind']:5s} {verb}{fp(sc['trig'][1])}({sc['trig'][0]}) {arrow} {fp(sc['tgt'])} | inval {'<' if sc['kind']=='LONG' else '>'}{fp(sc['inv'])} | [{sc['tag']}]{warn}")
        k = {"LONG":"L","SHORT":"S","FADE":"F"}[sc["kind"]]
        frags.append(f"SC{i}:{k},{fp(sc['trig'][1])},{fp(sc['tgt'])},{fp(sc['inv'])},{'lean' if 'lean' in sc['tag'] else 'ctx'}")
    return lines, "|".join(frags)

def main():
    a = sys.argv[1:]
    d = pd.Timestamp(a[a.index("--date")+1]).date() if "--date" in a else datetime.now(ET).date()
    at0900 = "--at0900" in a; manual = float(a[a.index("--ndx")+1]) if "--ndx" in a else None
    names = a[a.index("--assets")+1].split(",") if "--assets" in a else list(ASSETS)
    if "--rebuild" in a and os.path.isdir(ST):
        import shutil; shutil.rmtree(ST)
    if not os.path.isdir(ST):
        os.makedirs(ST, exist_ok=True)
        if os.path.exists(ZIPF):
            with zipfile.ZipFile(ZIPF) as z: z.extractall(HERE)
            print("state restored from brief_state.zip")
    eq = float(a[a.index("--eq")+1]) if "--eq" in a else 100000.0
    dd_in = float(a[a.index("--dd")+1]) if "--dd" in a else 0.0
    step_pct = ladder_step(dd_in)
    ndx, ndx_src = get_ndx(manual, d); dxy = get_dxy(d); is_fomc = str(d) in FOMC
    def hayden_state(df4):
        """v4.4: returns the state CODE (0 none / 1 Bull / 2 Bear / 3 Chop-exit).
        The v1.2 skip logic consumes (code == 1) — byte-identical to the old boolean."""
        x = (df4["o"]+df4["h"]+df4["l"]+df4["c"]).values/4.0
        n_=14
        dd = np.diff(x, prepend=x[0]); up=np.where(dd>0,dd,0.); dn=np.where(dd<0,-dd,0.)
        if len(x) <= n_+2: return None
        au,ad = up[1:n_+1].mean(), dn[1:n_+1].mean()
        r = np.full(len(x), np.nan); r[n_] = 100-100/(1+au/max(ad,1e-12))
        for i in range(n_+1, len(x)):
            au=(au*(n_-1)+up[i])/n_; ad=(ad*(n_-1)+dn[i])/n_
            r[i]=100-100/(1+au/max(ad,1e-12))
        cur=0
        for i in range(1, len(r)):
            r0,r1=r[i-1],r[i]
            if np.isnan(r1): continue
            if r1>67 and (np.isnan(r0) or r0<=67): cur=1
            elif r1<33 and (np.isnan(r0) or r0>=33): cur=2
            elif cur==1 and r1<39 and r0>=39: cur=3
            elif cur==2 and r1>61 and r0<=61: cur=3
        return cur
    # ---- Option B module across its whole universe ----
    ob_open, ob_fired = {}, {}
    d55_frames = {}
    for sym in SLEEVES["DON55"]["instr"]:
        d55_frames[sym] = binance(sym, "4h")
    cd1 = {}   # v4.4: crypto daily frames, fetched once (weekly module + per-asset loop)
    for sym in SLEEVES["DON55"]["instr"]:
        cd1[BRIEF2OB_R[sym]] = binance(sym, "1d")
    for sym in SLEEVES["DON55"]["instr"]:
        f, o, info = ob_state("DON55", sym, d55_frames[sym], d)
        if f: ob_fired[f"DON55:{sym}"] = True
        if o: ob_open[f"DON55:{sym}"] = info
    hb = {}
    _cut = pd.Timestamp(str(d)+" 08:00", tz="America/New_York").tz_convert("UTC")
    try:
        _b1d = binance("BTCUSDT", "1d")
        _b1d = _b1d[_b1d["dt"] + pd.Timedelta(days=1) <= _cut]
        _pi_up = bool((_b1d["c"].rolling(111).mean().iloc[-1] / _b1d["c"].rolling(350).mean().iloc[-1]) > 1)
    except Exception:
        _pi_up = None
    for sym in SLEEVES["DON55"]["instr"]:
        try:
            sub = d55_frames[sym][d55_frames[sym]["dt"]+pd.Timedelta(hours=4) <= _cut]
            hb[sym] = hayden_state(sub)
        except Exception:
            hb[sym] = None
    def _htag(k):
        if not k.startswith("DON55:"): return k
        code = hb.get(k.split(":")[1])
        if code is None: return k
        st = (code == 1)
        if (_pi_up is False) and (not st):
            return k + "[SKIP v1.2: pi-down & H:not-Bull]"
        return k + ("[H:Bull+]" if st else "[H:not-]")
    def _is_skip(k):
        if not k.startswith("DON55:"): return False
        code = hb.get(k.split(":")[1])
        return (code is not None) and (_pi_up is False) and (code != 1)
    ob_daily = {}
    for obsym, ysym in OB_FEED.items():
        try: ob_daily[obsym] = to_daily_frame(yahoo_daily(ysym, f"OB{obsym}")).assign(dt=lambda x: pd.to_datetime(x["d"]))
        except Exception as e: print(f" [OB {obsym}] data fail: {e}")
    for sl in ["FADE","DON20"]:
        for obsym in SLEEVES[sl]["instr"]:
            if obsym not in ob_daily: continue
            f, o, info = ob_state(sl, obsym, ob_daily[obsym], d)
            if f: ob_fired[f"{sl}:{obsym}"] = True
            if o: ob_open[f"{sl}:{obsym}"] = info
    print(f"\n{'='*66}\n DAILY BRIEF v{VERSION} -- {d} (08:00-14:00 ET)")
    print(f" NDX_prev={None if ndx is None else round(ndx,5)} [{ndx_src}] | DXY_on={None if dxy is None else round(dxy,5)} | FOMC={'YES' if is_fomc else 'no'}")
    # v4.4 REGIME light (inputs of the live v1.2 rule; display only)
    _pis = "UP" if _pi_up else ("DOWN" if _pi_up is False else "?")
    _hlab = {None:"?",0:"-",1:"Bull",2:"Bear",3:"Chop"}
    _hstr = " ".join(f"{BRIEF2OB_R[s]}:{_hlab[hb.get(s)]}" for s in SLEEVES["DON55"]["instr"])
    if _pi_up is False:
        _armed = [BRIEF2OB_R[s] for s in SLEEVES["DON55"]["instr"] if hb.get(s) is not None and hb.get(s) != 1]
        _gate = "ARMED for " + ",".join(_armed) if _armed else "pi-down, all Bull -> inactive"
    else:
        _gate = "inactive (pi-up)" if _pi_up else "inputs unavailable"
    print(f" REGIME: BTC-pi {_pis} | H4 {_hstr} | v1.2 DON55 gate: {_gate}")
    if DRIFT:
        for src, key_, n_, mx_ in DRIFT:
            print(f" !! DRIFT [{src}:{key_}] {n_} settled bar(s) differ from vendor re-print, max |dC| {mx_*100:.3f}% -- CACHED S1 VALUES KEPT (detect, never absorb)")
    print(f" OPTION B fired at prior close: {[_htag(k) for k in sorted(ob_fired)] or '-'}")
    print(f" OPTION B open at 08:00: " + (", ".join(f"{_htag(k)}(since {v['since']})" for k,v in sorted(ob_open.items())) or "-"))
    if any(k.startswith("DON55:") for k in list(ob_fired)+list(ob_open)):
        print("   OPTION B v1.2 RULE: DON-55 signals skipped when BTC pi-downtrend AND own Hayden-4H != Bull (validated; poison subset -0.42R, 4/4 assets). Other tags informational.")
    # v4.4 SIZE lines (display arithmetic at v1.2-locked sizing; the rulebook executes)
    usdjpy_c = float(ob_daily["USDJPY"]["c"].iloc[-1]) if "USDJPY" in ob_daily and len(ob_daily["USDJPY"]) else None
    try:
        eurusd_c = float(yahoo_daily("EURUSD=X", "FXEUR")["c"].iloc[-1])
    except Exception:
        eurusd_c = None
    if ob_fired:
        print(f" SIZING: eq ${eq:,.0f} | DD {dd_in:+.1f}% -> step {step_pct:.3f}%/trade (v1.2 ladder 0.375/0.25/0.125 at -3/-6)")
        for k in sorted(ob_fired):
            sl, sym = k.split(":")
            if _is_skip(k):
                print(f"    SIZE {sym}: -- v1.2 SKIP, no size"); continue
            fr = d55_frames[sym] if sl == "DON55" else ob_daily.get(sym)
            si = fired_size_info(sl, sym, fr) if fr is not None else None
            if si:
                ln = lot_line(sym, si[0], si[1], eq, step_pct, usdjpy_c, eurusd_c)
                if ln: print(ln)
    print("="*66)
    payloads, todays, graders = [], {}, {}
    for nm in names:
        cfg = ASSETS[nm]
        try:
            if cfg["kind"]=="b":
                D = to_daily_frame(cd1[nm] if nm in cd1 else binance(cfg["sym"], "1d"))
            else:
                D = to_daily_frame(yahoo_daily(cfg["sym"], nm))
            S = update_sessions(nm, cfg, D, d)
            core = forecast(nm, cfg, D, S, d, at0900)
            open55 = f"DON55:{BRIEF2OB[nm]}" in ob_open
            dr = direction(nm, cfg, core, ndx, dxy, is_fomc, open55)
            has_long = any(k.endswith(":"+BRIEF2OB[nm]) for k in ob_open)
            ovl = dr["dir"]=="down" and has_long
            todays[nm] = (dr, ovl)
            if cfg["kind"]=="b": graders[nm] = binance_1h_since(cfg["sym"], pd.Timestamp(d)-pd.Timedelta(days=6))
            spot = core["spot"]; rs = round_step(spot); rnd = round(spot/rs)*rs
            cash = " [cash-hours]" if cfg.get("cash") else ""
            print(f" [{nm}] {cfg['tier']}{cash}  spot {fp(spot)} | range ~{core['U']*100:.1f}% (p85 {core['p85']*100:.1f}%) | {core['dtype']}")
            # ---- v4.4: weekly U (crypto, HORIZON-validated) + PW/PM map (all assets) ----
            ctx = week_month_ctx(D, d)
            wkf = None
            if cfg["kind"] == "b":
                try: wkf = weekly_forecast(nm, d, cd1)
                except Exception as e_: print(f"     WEEK: unavailable ({type(e_).__name__})")
            wfrag = ""
            if wkf and "PW" in ctx:
                pcw = ctx["PW"]["C"]; wtd = ctx.get("PWtd")
                used = ((wtd["H"]-wtd["L"])/pcw) if (wtd and pcw) else np.nan
                kday = wtd["day"] if wtd else 0
                med = WEEK_MED.get(min(kday,7), 1.0)
                pct_of_U = f"{used/wkf['U']*100:.0f}% of U" if used == used and wkf["U"] > 0 else "-"
                print(f"     WEEK: U {wkf['U']*100:.1f}% (p70 {wkf['p70']*100:.1f} / p85 {wkf['p85']*100:.1f})"
                      f" | used {used*100:.1f}% ({pct_of_U}) | day {kday}/7 (median week {med*100:.0f}% formed)")
                wfrag = (f"|WU:{wkf['U']*100:.2f}|WP70:{wkf['p70']*100:.2f}|WP85:{wkf['p85']*100:.2f}"
                         f"|WUSED:{used*100:.2f}|WDAY:{kday}")
            pmfrag = ""
            if "PW" in ctx or "PM" in ctx:
                seg = []
                if "PW" in ctx:
                    w_ = ctx["PW"]; seg.append(f"PW {fp(w_['H'])}/{fp(w_['L'])}/{fp(w_['C'])}")
                    pmfrag += f"|PWH:{fp(w_['H'])}|PWL:{fp(w_['L'])}|PWC:{fp(w_['C'])}"
                if "PM" in ctx:
                    m_ = ctx["PM"]; seg.append(f"PM {fp(m_['H'])}/{fp(m_['L'])}/{fp(m_['C'])}")
                    pmfrag += f"|PMH:{fp(m_['H'])}|PML:{fp(m_['L'])}|PMC:{fp(m_['C'])}"
                mtd = ctx.get("PMtd")
                if mtd: seg.append(f"mo d{mtd['day']} (med {MONTH_MED.get(min(mtd['day'],12),.66)*100:.0f}% formed)")
                print(f"     MAP:  " + " | ".join(seg))
            if dr["dir"]!="none":
                print(f"     DIR: {dr['dir'].upper()} ({dr['strength']}) [{dr['basis']}] hist {dr.get('hist','-')} / 2024+ {dr.get('y24','-')}")
            else:
                print(f"     DIR: none" + (f" [{dr['basis']}]" if dr['basis']!='none' else ""))
            for n_ in dr["notes"]: print(f"       - {n_}")
            if ovl: print(f"     !! OVERLAP: down-lean vs open Option B long ({BRIEF2OB[nm]}) -- policy: don't day-trade against your own swing, or hedge knowingly")
            print(f"     LVLS: PDH {fp(core['PDH'])} PDC {fp(core['PDC'])} PDL {fp(core['PDL'])} | ONH {fp(core['onH'])} ONL {fp(core['onL'])} | RND {fp(rnd)}")
            sc_lines, sc_frag = scenarios(core, dr, spot, rnd, open55, has_long)
            if sc_lines:
                print("     SCENARIOS:")
                for l_ in sc_lines: print(l_)
            obcode = "o55" if open55 else ("long" if has_long else "none")
            payloads.append(f"CB2|{nm}|{d}|U:{core['U']*100:.2f}|p70:{core['p70']*100:.2f}|p85:{core['p85']*100:.2f}"
                f"|type:{core['dtype']}|dir:{dr['dir']}|str:{dr['strength']}|basis:{dr['basis']}"
                f"|PDH:{fp(core['PDH'])}|PDL:{fp(core['PDL'])}|PDC:{fp(core['PDC'])}|ONH:{fp(core['onH'])}|ONL:{fp(core['onL'])}"
                f"|RND:{fp(rnd)}|S08:{fp(spot)}|fomc:{int(is_fomc)}|ob:{obcode}|ovl:{int(ovl)}|tier:{cfg['tier']}"
                + pmfrag + wfrag
                + (f"|{sc_frag}" if sc_frag else ""))
        except Exception as e:
            print(f" [{nm}] SKIPPED: {e}")
    for nm, why in PENDING.items(): print(f" [{nm}] not briefed -- {why}")
    n, hit, agree = log_and_grade(d, todays, graders)
    print(f"\n LOG: {n} graded, {hit} hits | SOL I-1 agree-fires graded: {agree}/30")
    print("\n C-BRIDGE PAYLOADS:")
    for p in payloads: print(" "+p)
    with zipfile.ZipFile(ZIPF, "w", zipfile.ZIP_DEFLATED) as z:
        for f_ in os.listdir(ST): z.write(os.path.join(ST,f_), arcname=f"state/{f_}")
    print(f"\n STATE SAVED -> brief_state.zip ({os.path.getsize(ZIPF)//1024} KB). Download it; upload it tomorrow.")

if __name__ == "__main__":
    main()
