#!/usr/bin/env python3
"""e1_episodes.py — EPISODES: the outcome layer at full sequence (Svet's go in chat, 2026-07-28).
One row = one level-touch episode extending the Layer-B anchors 1:1, keyed identically
(coin, wdate, mark, price, t0). Story on 5m bars, raw dollars + UTC timestamps, no
thresholds stored. Ships -> results/episodes/: episodes_{COIN}.parquet (wide, 37 cols) ·
episode_path_{COIN}.parquet (grid ruler) · episode_exc_{COIN}.parquet (the joint-4
alternating-excursion ladder: every strict extension of running fav/adv excursion per
entry basis — stop x target ORDER questions answer from this table; same-bar ambiguity
counted, never guessed) · REPORT.md when all coins done.
Also (Svet's order): commits docs/newproject/{PHASE_CONTRACT_v1.md(v1.1), RECORD_SPEC_v0.md,
EPISODE_SPEC_v0.md} — runner only; never overwrites: existing+different = DRIFT, exit 1.
GATES (full population, any FAIL = exit 1): A anchors reproduced per the b2 algorithm ·
B episode<->anchor reconcile, gap-through exceptions counted+LISTED · C closeback from 1D ·
D internal (ladder endpoints == MAE/MFE; keys 1:1; windows). Deterministic, no RNG.
Counts only; verdicts are Svet's."""
import pandas as pd, numpy as np, json, os, sys, time, argparse, hashlib, subprocess

ap = argparse.ArgumentParser()
ap.add_argument('--budget-min', type=float, default=230)
ap.add_argument('--coins', type=str, default='BTC,ETH,SOL,XRP')
A_, _ = ap.parse_known_args(); T0 = time.time()
COINS = [c for c in A_.coins.split(',') if c]
REC, OUT = 'results/record', 'results/episodes'
os.makedirs(OUT, exist_ok=True); os.makedirs('results/state', exist_ok=True)
SF = 'results/state/e1.json'
st = json.load(open(SF)) if os.path.exists(SF) else {'done': [], 'stats': {}}
NS5 = np.int64(300_000_000_000)  # 5 minutes in ns

# ---------------------------------------------------------------- docs (Svet's order)
DOCS = {}  # {relpath: (sha256hex, text)}  -- injected by builder
DOCS['docs/newproject/PHASE_CONTRACT_v1.md'] = ('2bd4318705e72bdade59377a95f5de183a1bfc18c695f3a3d00a5ca26b97ba54', """# PHASE CONTRACT v1 — The System, post-trim plan (2026-07-28)
Chat supersedes this file; rules 1–10 govern it. Purpose: the fixed text Svet checks Claude against.
Any deviation below without Svet's explicit word in chat = breach, to be named by whoever spots it first.

## SCOPE LAWS (this phase)
S1. CRYPTO-ONLY. No non-crypto data enters The System — no feeds, no tickers, no joins.
    Revisit trigger: only after sequential-C is read, only by Svet's word.
S2. RECORD IMMUTABLE. Every cut below is a ROSTER cut (what gets tested), never a record cut.
    All columns stay stored. Any cut reverses with one word, zero rebuild.
S3. Standing record laws carry: native units · no thresholds stored · rulers ride beside ·
    the 100-bar window law · counts reconcile · gaps named, never silent.

## ROSTER — TESTED
Per-TF (15m/1h/4h unless noted): Hayden machine (state, its internal RSI, bars-in-state, slope;
BTC 4h state on alts) · candle range vs own last-20 · body fraction · wick fractions ·
close position · HH/LL token · volume ratio 20/100 · same-hour relvol (5m) ·
session/weekend/clock (5m) · ATR14 (ruler).
Daily: pi · Hayden daily anchor · yd_arch · day-type call (na beyond 2026-07-24, printed) ·
lean chain OUTPUT ONLY (dir+strength; same na window) · U as ruler only ·
the seven day-label candidates.
Option B: DON-55 at FULL GRAIN — bars_in_trade, dist_entry, dist_stop, half_off,
unrealized_R, skip_state — computed from sealed crypto data via the gated port.
GATE: its open/fired series must reproduce the b0 table (495/495-gated lineage) exactly
where covered, or the columns don't ship.
Path shape: time-in-state + RSI-slope run length, on 15m/1h/4h only.

## ROSTER — CUT (named, reversible by one word)
Standalone RSI dial (all TFs) · divergence flags and window-counts · path-shape flip-count ·
path-shape on 5m · DON-20 sleeve (gold, silver, US500, US100) · FADE-K5 sleeve (six instruments) ·
lean-chain raw inputs (NDX/DXY/JPY/overnight — deferred with S1) · all non-crypto anything.

## BENCH (defined, not computed; each enters only by Svet's word, as add-a-column)
Vote / thrust / drive24 / wear family · cascade states · armed-scenario per-15m states ·
W2 encodings · TradingView suite (Pine unread — read before use) · level-map-era uhist-U.

## SEQUENCE (checkable, in order)
1. DON-55 full-grain columns job (paste+run; ships with its gate result printed).
2. Sequential-C pairs job: every (component × offset) crossed with every other —
   ~1.6M pairs, all four coins, NO pruning, n on every cell, floor declared.
3. Triples: NOT auto-run, NOT auto-pruned. Svet designs the narrowing off the pair
   ledger, or declines. Any triple run without his signed design = breach.
4. Reads happen in chat over the shipped tables; verdicts are Svet's.

## BREACH LIST (what Svet checks for)
B1 any roster change not in this file and not ordered in chat ·
B2 any summary replacing raw anywhere ·
B3 any threshold born un-swept or under one ruler ·
B4 any narrowing beyond signed scope announced-and-run instead of pitched-and-signed ·
B5 "done" claimed without checking against Svet's original words ·
B6 non-crypto data entering under any pretext ·
B7 findings shipped without n, or pruned below the last page.

## STANDING FACTS (context for future checks)
Base closeback at a mark ≈ 0.44–0.46 · singles are whispers (±1–3pp; clock ≈ ±7pp) ·
the record: ~2.97M bar-rows, 4 coins, 5 TFs, repo-resident, probe-sealed.

## v1.1 — STANDING RULE (confirmed by Svet in chat, 2026-07-28)
No strategy-language numbers — no win rates, no R, no expectancy — anywhere in shipped
output until computed from EPISODE grain, where entry, stop, target and their ORDER are
measured. Until then, situation-language only: hold rates, penetration depths, separations.
""")
DOCS['docs/newproject/RECORD_SPEC_v0.md'] = ('fba57a479a253e08e6630bb90011906fb2618efb9ed1016367d1f664fd8a5bec', """# RECORD SPEC v0 — Layer A of The System (DRAFT for Svet's markup; nothing runs until signed)

## 1. WHAT ONE ROW IS
One row = one bar of one timeframe of one coin. Key: (coin, tf, bar_open_utc).
Every bar of history — not only bars near zones. Weekends in. Five TFs: 5m, 15m, 1h, 4h, 1D (day = 08:00→08:00 ET).
The record is TF-native: a 4h row carries 4h readings; higher-TF context on a 5m bar is an as-of JOIN at query time, never a copied column.

## 1b. THE WINDOW LAW — where the 100 lives
The commissioned view is the current bar plus the 100 bars behind it, per TF, per component — 100×5m, 100×15m, 100×1h, 100×4h, 100×1D — read bar by bar, never summarized. The record stores EVERY bar precisely so that this window exists at EVERY possible anchor: a 100-bar lookback is 100 rows of this table per TF, cut at query time, for any zone interaction in history and for "right now" in the analyst's morning run — the same operation. Writing 100 into the storage would turn the record back into event-anchored extraction (edges, gaps, a frozen constant inside the record — the rule-10 disease). So 100 is the working window of every Layer-B and Layer-C question and of the analyst's live read: it holds as commissioned, and because the record is complete it can also be varied later without any re-extraction. The only short windows in existence are the first 100 bars of each TF's history — named and counted, never silently padded.

## 2. ROW COUNT, MULTIPLIED OUT
Per coin on the frozen vintage (2021-09 → 2026-07-06): 5m 509,720 · 15m ≈169,907 · 1h ≈42,477 · 4h ≈10,619 · 1D ≈1,770 → ≈734,500/coin.
× 4 coins ≈ **2,938,000 bar-rows**, plus the verified append to present (append-only, drift law).
Law: actual row count must equal the fetch counts summed; every gap named (rule 5).

## 3. THE TWO TABLES
**BARS** (wide, fixed schema) — one row per bar per TF per coin.
**MARKS** (long, extensible) — one row per marked price per day: coin · date · generator · tf · anchor period · price · born_at · died_at.
Generators in the census (all candidates, none privileged): the 20 period levels (PD/ON/PS/PW/PM × H/L/C/POC) · pivots per TF (pivot strength SWEPT, not fixed) · weekly + monthly VAH/VAL · scenario trigger/target/invalidation prices (the system's own declared levels).
Distance from any bar to any mark = close − mark.price, **derived by join, never stored** — so adding a generator later is adding rows, zero schema change, and no radius/threshold ever enters the record.

## 4. BARS COLUMN CENSUS (definitions per COMPONENTS.md; ~40 component series across the 8 groups — ALL ride)
A. **Native price**: o, h, l, c, v (absolute), bar_open_utc. The chart redraws from this alone — reconstruction passes by construction (rule 3).
B. **Group 1 regime**: hayden own (state, rsi, bars_in_state, rsi_slope) on 4h/1D + fast variants 15m/1h · hayden BTC · pi (state, ma_gap) on 1D.
C. **Group 2 day-character inputs**: day-type KNN call + range forecast · weekly budget/forecast · yd_arch · range-used — daily cadence, live on 1D rows.
D. **Group 3 tape dials, per TF, ruler-free**: candle range vs own last-20 median · body/range · upper/lower wick fractions · close position in bar · this push vs prior push · pullback depth as fraction of its leg · HH/HL/LH/LL token · gap flag. All ratios of the chart to itself.
E. **Group 4 level context**: derived by MARKS join (freshness, wear, tests-today, virgin, confluence count are query-time labels — parameters attached, re-runnable).
F. **Group 5 volume**: relvol vs 20-day same-hour median · volr 20/100, per TF.
G. **Group 6 momentum relations**: RSI per TF · divergence events (bull/bear, bars-since, count-in-window) · per-component confirm/diverge vs price.
H. **Group 7 clock**: session block · hours since 08:00 · weekday/weekend · FOMC.
I. **Group 8 book/system, full grain**: DON-55 per coin (fired, open, bars_in_trade, dist_entry, dist_stop, half_off, unrealized_R, skip_state) · DON-20 states ×4 instruments · FADE-K5 states ×6 · book aggregate (open count, direction load, overlap flag) · lean chain output AND its raw inputs (prior-day NDX, DXY, JPY state) · scenario card states per 15m bar · cascade states. Excluded by signed default only: Track B log, ladder/equity tier.
J. **Rulers (derived, beside — rule 10)**: U-levelmap and U-bruteforce (labeled, never mixed) · ATR14 of the row's own TF · percent-of-price. Plus the structural-relational language of group D. Five representations total; cross-ruler comparison is a standing output.

## 5. DAY-LABEL CANDIDATES — trend vs range, IN THE MIX (derived per coin-day; ALL computed, NONE chosen; which one means "trend day" is an empirical output)
d1 efficiency |close−open| / (high−low) of the 8–8 day
d2 day range vs trailing — computed under each ruler separately
d3 open-cross count (times price crossed the day open)
d4 structural ladder: longest consecutive HH/HL (or LL/LH) leg run on 15m within the day
d5 legacy day-type call (EXPANSION/QUIET/normal) — one candidate, no seniority
d6 DON-55 fired/open that day — one candidate, no spotlight
d7 yd_arch formula applied to today
Each is a column; each gets its per-coin distribution; forecastability of each is a Layer-B question; your two conditionals (sweep-and-reverse | range-day, pullback-continuation | trend-day) run against every candidate label, per coin, n on everything.

## 6. WHAT IS THROWN AWAY
From the inputs: **nothing.** Deliberately NOT stored (derived at query time, by design): distances (join), cross-TF copies (as-of join), any thresholded label (event, touch, break, graze — query-time with parameters attached), any U-denominated value (derived column only). No minimums exist anywhere in the record.

## 7. STORAGE
Parquet zstd, partitioned coin/tf; MARKS separate; append-only; vendor drift detected never absorbed; every build ships expected-vs-actual counts. Estimated full size: a few hundred MB — travels in the pack, read by code only.

## 8. ACCEPTANCE — before anything scales
a) counts reconcile to fetch sums, gaps named;
b) chart + every component reading redraw from the tables alone;
c) **your eyes**: one named day + coin rendered from the record vs TradingView, plus the bar-by-bar narration through all components;
d) the same day's labels computed under two rulers, side by side, so ruler-dependence is visible from day one.

## 9. SEQUENCE
Spec markup (you) → one-day proof (under the cost gate, runs on your word) → full-build pitch (three lines, you say go) → Layer B: every component alone, complete → Layer C: combinations → day-character campaign = the first query set on the finished record. Full statistical tables ship as files, sorted by n descending — the frequent and identifiable on page one, the rare still on the last page.""")
DOCS['docs/newproject/EPISODE_SPEC_v0.md'] = ('016b0c90af158d8e94d8bde41e69bce0844b5ca417d9d6c648529dee941a74b6', """# EPISODE SPEC v0 — the outcome layer at full sequence (SIGNED: Svet's go in chat, 2026-07-28)
Governed by rules 1–10, PHASE_CONTRACT v1.1, RECORD_SPEC v0. Joints 1/2/3/5 approved as designed; joint 4 amended by Svet's word: the alternating-excursion ladder ships as a third table in v0 — stop×target ORDER questions must be answerable from shipped tables, same-bar ambiguity counted, never guessed. Built by jobs/e1_episodes.py; situation-language only — this layer is what makes trade language legal later.

## 1. WHAT ONE ROW IS
One row of EPISODES = one level-touch episode: the ordered story of one ET period mark's first touch of the day, from the touch bar to the end of its 08:00→08:00 ET window, told on 5m bars in raw dollars and UTC timestamps.
Key: (coin, wdate, mark, price, t0) — IDENTICAL to the Layer-B anchors (b2_offsets (b)-line: anchor = first 5m bar whose range contains the ET mark, per coin-day). Episodes EXTEND the anchors; the anchors file is untouched and joins 1:1 by key. Nothing about the touch definition is new.

## 2. ROW COUNTS, MULTIPLIED OUT
EPISODES = the anchor population exactly: BTC 16,657 · ETH 16,507 · SOL 16,242 · XRP 16,237 = **65,643 rows**, one per anchor, zero added, zero dropped. 37 columns ≈ 2.4M cells.
EPISODE_PATH (long) = one row per (episode × other same-day ET mark first-tagged in the window). Ceiling 19/episode; actual count is a ship-time output, reconciled and printed.
EPISODE_EXC (long, the joint-4 ladder) = one row per new running-extreme event per entry basis: every time the running favorable or running adverse excursion strictly extends, one row (side, raw extreme price, bar timestamp). Two bases: fade-at-touch (always) and enter-at-retest (iff a retest exists). This event sequence is threshold-free and COMPLETE for order questions: for any stop distance s and target distance t, first-hit times are read off the staircases; equal timestamps = the same 5m bar = AMBIGUOUS, a counted third outcome, never a coin flip. Actual row count is a ship-time output, reconciled per episode.
Named sub-populations (facts, not filters — all rows ship): never-traded-beyond 154 (0.2%) · touch-on-day-open ~28%/coin (same-day approach fields null) · no-retest · held-to-close · final-partial-day truncations · gap-through exceptions (listed one by one) · same-bar both-sides event pairs (entry-bar structural pairs counted separately from interior pairs).

## 3. THE THREE TABLES
**EPISODES** (wide, fixed schema) — one row per anchor.
**EPISODE_PATH** (long) — the level grid as its own ruler: key · seq · path_mark · path_price · first_tag_at, time order.
**EPISODE_EXC** (long) — the excursion ladder: key · basis (fade|rt) · seq · side (fav|adv) · px · at.
Adding a story fact later = adding a column (S2); adding a grid or a basis = adding rows.

## 4. EPISODES COLUMN CENSUS (raw dollars + UTC timestamps; no thresholds stored; distances and labels by subtraction or join, never duplicated)
KEY (5): coin · wdate · mark · price · t0. Everything the anchor stores (open_side, pen, rev_after, closeback, atr1d, uabs, play_atr) stays in anchors_ and arrives by the 1:1 join — never copied.
SETUP (9): approach_local_close (last 5m close before t0; null = opened into it) · prior_mark_name / prior_mark_price / prior_mark_at (most recent pre-t0 bar tagging a different-PRICE same-day ET mark; on a multi-mark bar the mark nearest in price to this episode's mark, names at that price joined by '+'; null = none) · tie_count (marks at EXACTLY this price — parameter-free; radius-confluence stays a query-time label with parameters) · corridor_up_name / corridor_up_price · corridor_dn_name / corridor_dn_price (nearest same-day ET marks strictly above/below; names at the corridor price joined by '+'; gap widths = subtraction, not columns).
ORDERED STORY (12): first_trade_beyond_at · first_close_beyond_at · bounce_ext_price / bounce_ext_at (bounce-side extreme BEFORE first_close_beyond; whole window if never closed beyond) · max_cont_price / max_cont_at (extreme beyond, from first_trade_beyond to window end) · retest_touch_at (first tag of the mark after first_close_beyond) · retest_ext_price / retest_ext_at (extreme against the break, retest touch → reclaim close inclusive, or window end) · reclaim_close_at (first close back on the original side after retest touch; null = held to window end) · travel_after_price / travel_after_at (continuation-side extreme from retest touch to window end).
ENTRY BASES (8): fade_mae_price/at · fade_mfe_price/at · rt_mae_price/at · rt_mfe_price/at — the ladder's endpoints, kept for join-free reads; each MUST equal its basis's terminal staircase value (internal gate).
CLOSE/FRAME (3): day_close_price · day_end_at · bars_in_window.

## 5. CONVENTIONS (named, not parameters)
Tag = bar h ≥ price ≥ l. Beyond = STRICTLY past the mark on the far side of open_side (inherited). Close-beyond / reclaim = close STRICTLY past. Story grain = 5m, the record's finest. Excursion event = the running extreme strictly extends; the entry bar seeds one fav and one adv event by construction (structural pair, counted separately). SAME-BAR LAW: facts on one 5m bar carry equal timestamps; seq breaks equal-at ties by a stated fixed order (adv before fav; path by name) that carries NO within-bar meaning; every order-question resolving inside one bar is AMBIGUOUS and counted. NULL LAW: null = the stage never happened, populations named, never padded. GRID LAW: corridor and PATH use the same-day ET period marks — the anchors' own grid; pivots/VA/scenario marks join at query time. Retest is defined off first CLOSE beyond; the trade-beyond variant is a re-query of BARS, which remain complete. Window end = last 5m bar of the wdate + 5min; the final partial day truncates there, counted.

## 6. WHAT IS THROWN AWAY
Nothing. Anchors, BARS, MARKS untouched; every label (broke, held, failed, deep, fast) derivable at query time with its parameters attached; anchor outcomes (pen, rev_after, closeback) must be REPRODUCED by this build, not replaced; longer horizons = query-time join to the following days' bars — the window is inherited from the anchor's day frame, not a new constant.

## 7. ACCEPTANCE (full population; any FAIL stops the ship)
a) EPISODES rows == anchors rows per coin; key join 1:1, zero orphans either side;
b) Gate A — anchors reproduced: pen, rev_after, closeback, open_side, t0 recomputed per the b2 algorithm from the record match the stored anchors for every row (≤1e-9);
c) Gate B — episode↔anchor reconcile: |price − max_cont_price| == pen and post-extreme reversal == rev_after for every row; the only licensed exceptions are gap-through days (a pre-t0 bar sits entirely beyond the mark — price crossed with no containing bar), each counted and LISTED with its gap bar, never absorbed;
d) Gate C — sign(day_close_price − price) vs sign(day open − price) reproduces closeback for every row;
e) Gate D — internal: MAE/MFE columns == EXC terminal extremes per basis; every timestamp inside [t0, day_end_at]; rt basis exists iff retest_touch_at exists; per-episode event counts sum to EXC table length;
f) Svet's eyes: the worked example (BTC · 2024-08-05 · PDC 51340.00) printed in the REPORT, narrated from the shipped row;
g) storage: results/episodes/ · parquet zstd per coin · append-only · REPORT.md with expected-vs-actual and every named population counted. Counts only; verdicts are Svet's.

## 8. SEQUENCE AFTER GATE
Re-run the B/C machinery against episode outcomes (outcome-agnostic — swap the weight vectors). Only after that may stop×target×situation cells speak trade language (v1.1) — and order questions answer from EPISODE_EXC, ambiguity counted. Triples stay locked behind Svet's signed design (contract item 3).
""")

def docs_step():
    changed = []
    for rel, (sha, text) in DOCS.items():
        b = text.encode('utf-8')
        assert hashlib.sha256(b).hexdigest() == sha, f'embedded doc corrupt: {rel}'
        if os.path.exists(rel):
            cur = open(rel, 'rb').read()
            if cur == b:
                print(f'DOC OK already present: {rel}'); continue
            print(f'DOC DRIFT: {rel} exists with different bytes ({len(cur)} vs {len(b)}) — never overwritten. STOP.')
            sys.exit(1)
        os.makedirs(os.path.dirname(rel), exist_ok=True)
        open(rel, 'wb').write(b)
        assert hashlib.sha256(open(rel,'rb').read()).hexdigest() == sha
        print(f'DOC WRITTEN: {rel} ({len(b)} bytes, sha {sha[:12]})'); changed.append(rel)
    if not changed:
        return
    if os.environ.get('GITHUB_ACTIONS'):
        try:
            subprocess.run(['git','config','user.name','job-bot'], check=True)
            subprocess.run(['git','config','user.email','bot@none'], check=True)
            subprocess.run(['git','add'] + changed, check=True)
            subprocess.run(['git','commit','-m','docs: PHASE_CONTRACT v1.1 + RECORD_SPEC v0 + EPISODE_SPEC v0 (Svet\'s word in chat 2026-07-28) [skip ci]'], check=True)
            subprocess.run(['git','push'], check=True)
            print('DOCS COMMITTED AND PUSHED:', ', '.join(changed))
        except subprocess.CalledProcessError as e:
            print(f'DOCS COMMIT FAILED ({e}) — named, not silent; build continues, docs sit in the working tree.')
    else:
        print('local run: docs written, commit skipped (not on runner).')

# ---------------------------------------------------------------- helpers
def first_true(b):
    return int(np.argmax(b)) if b.size and b.any() else None

def ts(ns):
    return pd.Timestamp(int(ns), unit='ns', tz='UTC') if ns is not None else pd.NaT

def px(v):
    return float(v) if v is not None else np.nan

def exc_events(vals_fav, vals_adv, dts, fav_up):
    """Running-extreme staircases. fav_up: favorable = rising highs (else falling lows).
    Returns list of (at_ns, side, price) — one event per STRICT extension; bar 0 seeds both."""
    ev = []
    if fav_up:
        rf = np.maximum.accumulate(vals_fav)   # highs
        ra = np.minimum.accumulate(vals_adv)   # lows
        fi = np.concatenate(([0], np.flatnonzero(np.diff(rf) > 0) + 1))
        ai = np.concatenate(([0], np.flatnonzero(np.diff(ra) < 0) + 1))
    else:
        rf = np.minimum.accumulate(vals_fav)   # lows
        ra = np.maximum.accumulate(vals_adv)   # highs
        fi = np.concatenate(([0], np.flatnonzero(np.diff(rf) < 0) + 1))
        ai = np.concatenate(([0], np.flatnonzero(np.diff(ra) > 0) + 1))
    for i in fi: ev.append((int(dts[i]), 'fav', float(rf[i])))
    for i in ai: ev.append((int(dts[i]), 'adv', float(ra[i])))
    ev.sort(key=lambda r: (r[0], r[1]))  # equal-at tiebreak adv<fav: fixed, meaningless within-bar
    return ev

# ---------------------------------------------------------------- per-coin build
def build_coin(coin):
    t_c = time.time()
    AN = pd.read_parquet(f'results/layerb/anchors_{coin}.parquet')
    F  = pd.read_parquet(f'{REC}/bars_{coin}_5m.parquet', columns=['dt','h','l','c','wdate'])
    D  = pd.read_parquet(f'{REC}/bars_{coin}_1D.parquet',
                         columns=['wdate','o','c','atr14_1d','uabs']).set_index('wdate')
    MK = pd.read_parquet(f'{REC}/marks_periods_{coin}.parquet')
    MK = MK[MK.conv == 'ET']
    F['dt'] = pd.to_datetime(F.dt, utc=True)
    F['wdate'] = F.wdate.astype(str)
    D.index = D.index.astype(str)
    AN['t0'] = pd.to_datetime(AN.t0, utc=True)
    days = {}
    for wd, g in F.groupby('wdate', sort=True):
        g = g.sort_values('dt')
        days[wd] = (g.dt.values.astype('datetime64[ns]').astype(np.int64),
                    g.h.to_numpy(float), g.l.to_numpy(float), g.c.to_numpy(float))
    mks = {wd: (g.name.to_numpy(), g.price.to_numpy(float)) for wd, g in MK.groupby('wdate')}

    ep_rows, path_rows, exc_rows = [], [], []
    gA = {'n':0,'mism':0,'max_pen':0.0,'max_rev':0.0,'bad':[]}
    gB_exc = []          # gap-through exceptions: (wdate, mark, gap_bar_iso)
    gB_fail = []
    gD_fail = []
    pop = {'never_beyond':0,'touch_on_open':0,'no_close_beyond':0,'no_retest':0,
           'held_to_close':0,'final_day':0,'tie_rows':0,
           'sb_entry_pairs':0,'sb_interior_fade':0,'sb_interior_rt':0,
           'exc_fade_events':0,'exc_rt_events':0,'d_nan_rows':0}
    last_wd = max(days.keys())

    AN = AN.sort_values(['wdate','t0','mark']).reset_index(drop=True)
    cur_wd, T = None, None
    for a in AN.itertuples(index=False):
        wd, mkname, m, t0 = a.wdate, a.mark, float(a.price), a.t0
        dts, H, L, C = days[wd]
        names, prices = mks[wd]
        if wd != cur_wd:
            T = (H[:, None] >= prices[None, :]) & (L[:, None] <= prices[None, :])
            cur_wd = wd
        drow = D.loc[wd]; do, dc = float(drow.o), float(drow.c)
        t0ns = np.int64(t0.value)
        i0 = int(np.searchsorted(dts, t0ns))
        if not (i0 < len(dts) and dts[i0] == t0ns):
            print(f'FATAL: t0 not found in day bars: {coin} {wd} {mkname} {t0}'); sys.exit(1)
        side = int(a.open_side)
        Wh, Wl, Wc, Wd = H[i0:], L[i0:], C[i0:], dts[i0:]
        nW = len(Wd); day_end = int(dts[-1] + NS5)

        # ---- Gate A: reproduce the anchor per b2's exact algorithm (whole day)
        if do >= m:
            rpen = max(0.0, m - L.min()); j = int(L.argmin())
            rrev = float(H[j:].max() - m) if rpen > 0 else np.nan; rside = 1
        else:
            rpen = max(0.0, H.max() - m); j = int(H.argmax())
            rrev = float(m - L[j:].min()) if rpen > 0 else np.nan; rside = -1
        rcb = int(np.sign(dc - m) == np.sign(do - m) and do != m)
        ra1, ru = float(drow.atr14_1d) if pd.notna(drow.atr14_1d) else np.nan, \
                  float(drow.uabs) if pd.notna(drow.uabs) else np.nan
        rplay = int((rpen > 0) and (rpen <= 0.25*ra1) and (rrev >= 0.25*ra1)) if np.isfinite(ra1) else 0
        gA['n'] += 1
        okA = (abs(rpen - a.pen) <= 1e-9 and rside == side and rcb == int(a.closeback)
               and ((np.isnan(rrev) and np.isnan(a.rev_after)) or abs(rrev - a.rev_after) <= 1e-9)
               and ((np.isnan(ra1) and np.isnan(a.atr1d)) or abs(ra1 - a.atr1d) <= 1e-9)
               and ((np.isnan(ru) and np.isnan(a.uabs)) or abs(ru - a.uabs) <= 1e-9)
               and rplay == int(a.play_atr))
        if not okA:
            gA['mism'] += 1
            if len(gA['bad']) < 20: gA['bad'].append((wd, mkname))
        gA['max_pen'] = max(gA['max_pen'], abs(rpen - a.pen))
        if not (np.isnan(rrev) or np.isnan(a.rev_after)):
            gA['max_rev'] = max(gA['max_rev'], abs(rrev - a.rev_after))

        # ---- setup
        alc = float(C[i0-1]) if i0 > 0 else np.nan
        if i0 == 0: pop['touch_on_open'] += 1
        diffp = prices != m
        pmn = pmp = None; pma = None
        if i0 > 0 and diffp.any():
            anyrow = T[:i0, diffp].any(axis=1)
            if anyrow.any():
                r = int(np.flatnonzero(anyrow)[-1])
                hit = np.flatnonzero(T[r] & diffp)
                k = hit[int(np.argmin(np.abs(prices[hit] - m)))]
                pmp = float(prices[k]); pma = int(dts[r])
                pmn = '+'.join(sorted(names[(prices == pmp)]))
        tie = int(((prices == m) & (names != mkname)).sum())
        if tie: pop['tie_rows'] += 1
        up = prices[prices > m]; dn = prices[prices < m]
        cupn = cupp = cdnn = cdnp = None
        if up.size:
            cupp = float(up.min()); cupn = '+'.join(sorted(names[prices == cupp]))
        if dn.size:
            cdnp = float(dn.max()); cdnn = '+'.join(sorted(names[prices == cdnp]))

        # ---- ordered story (side-mirrored; strict beyond)
        if side == 1:
            beyond, cbey = Wl < m, Wc < m
        else:
            beyond, cbey = Wh > m, Wc > m
        i_tr, i_cl = first_true(beyond), first_true(cbey)
        if i_tr is None: pop['never_beyond'] += 1
        if i_cl is None: pop['no_close_beyond'] += 1
        hb = i_cl if i_cl is not None else nW
        b_px = b_at = None
        if hb > 0:
            seg = Wh[:hb] if side == 1 else Wl[:hb]
            jb = int(np.argmax(seg)) if side == 1 else int(np.argmin(seg))
            b_px, b_at = float(seg[jb]), int(Wd[jb])
        mc_px = mc_at = None
        if i_tr is not None:
            seg = Wl[i_tr:] if side == 1 else Wh[i_tr:]
            jm = int(np.argmin(seg)) if side == 1 else int(np.argmax(seg))
            mc_px, mc_at = float(seg[jm]), int(Wd[i_tr + jm])
        rt_at = rr_at = rte_px = rte_at = ta_px = ta_at = None
        i_rt = None
        if i_cl is not None and i_cl + 1 < nW:
            q0 = i_cl + 1
            back = (Wh[q0:] >= m) if side == 1 else (Wl[q0:] <= m)
            rel = first_true(back)
            if rel is not None:
                i_rt = q0 + rel; rt_at = int(Wd[i_rt])
                rec = (Wc[i_rt:] > m) if side == 1 else (Wc[i_rt:] < m)
                rel2 = first_true(rec)
                i_rr = (i_rt + rel2) if rel2 is not None else None
                rr_at = int(Wd[i_rr]) if i_rr is not None else None
                hi = (i_rr + 1) if i_rr is not None else nW
                seg = Wh[i_rt:hi] if side == 1 else Wl[i_rt:hi]
                jr = int(np.argmax(seg)) if side == 1 else int(np.argmin(seg))
                rte_px, rte_at = float(seg[jr]), int(Wd[i_rt + jr])
                seg2 = Wl[i_rt:] if side == 1 else Wh[i_rt:]
                jt = int(np.argmin(seg2)) if side == 1 else int(np.argmax(seg2))
                ta_px, ta_at = float(seg2[jt]), int(Wd[i_rt + jt])
                if rr_at is None: pop['held_to_close'] += 1
        if i_cl is not None and i_rt is None: pop['no_retest'] += 1
        if wd == last_wd: pop['final_day'] += 1

        # ---- entry bases: MAE/MFE endpoints + excursion ladder
        if side == 1:   # fade = long the mark: fav up
            jf, ja = int(np.argmax(Wh)), int(np.argmin(Wl))
            f_mfe, f_mfe_at, f_mae, f_mae_at = float(Wh[jf]), int(Wd[jf]), float(Wl[ja]), int(Wd[ja])
            ev_f = exc_events(Wh, Wl, Wd, fav_up=True)
        else:           # fade = short the mark: fav down
            jf, ja = int(np.argmin(Wl)), int(np.argmax(Wh))
            f_mfe, f_mfe_at, f_mae, f_mae_at = float(Wl[jf]), int(Wd[jf]), float(Wh[ja]), int(Wd[ja])
            ev_f = exc_events(Wl, Wh, Wd, fav_up=False)
        r_mfe = r_mfe_at = r_mae = r_mae_at = None; ev_r = []
        if i_rt is not None:
            Qh, Ql, Qd = Wh[i_rt:], Wl[i_rt:], Wd[i_rt:]
            if side == 1:   # retest-entry = continuation short: fav down
                jf2, ja2 = int(np.argmin(Ql)), int(np.argmax(Qh))
                r_mfe, r_mfe_at, r_mae, r_mae_at = float(Ql[jf2]), int(Qd[jf2]), float(Qh[ja2]), int(Qd[ja2])
                ev_r = exc_events(Ql, Qh, Qd, fav_up=False)
            else:
                jf2, ja2 = int(np.argmax(Qh)), int(np.argmin(Ql))
                r_mfe, r_mfe_at, r_mae, r_mae_at = float(Qh[jf2]), int(Qd[jf2]), float(Ql[ja2]), int(Qd[ja2])
                ev_r = exc_events(Qh, Ql, Qd, fav_up=True)

        key = (coin, wd, mkname, m, t0)
        for basis, ev in (('fade', ev_f), ('rt', ev_r)):
            if not ev: continue
            bysb = {}
            for at_, sd_, _ in ev: bysb.setdefault(at_, set()).add(sd_)
            pairs = sum(1 for v in bysb.values() if len(v) == 2)
            ent = 1 if len(bysb.get(ev[0][0], ())) == 2 else 0
            pop['sb_entry_pairs'] += ent
            pop['sb_interior_fade' if basis == 'fade' else 'sb_interior_rt'] += (pairs - ent)
            pop['exc_fade_events' if basis == 'fade' else 'exc_rt_events'] += len(ev)
            for s_i, (at_, sd_, p_) in enumerate(ev, 1):
                exc_rows.append(key + (basis, s_i, sd_, p_, at_))

        # ---- Gate D endpoint check (ladder terminal == MAE/MFE)
        tf = {}; 
        for at_, sd_, p_ in ev_f: tf[sd_] = p_
        okD = abs(tf.get('fav', np.nan) - f_mfe) <= 0 and abs(tf.get('adv', np.nan) - f_mae) <= 0
        if ev_r:
            tr = {}
            for at_, sd_, p_ in ev_r: tr[sd_] = p_
            okD = okD and abs(tr.get('fav', np.nan) - r_mfe) <= 0 and abs(tr.get('adv', np.nan) - r_mae) <= 0
        if not okD and len(gD_fail) < 20: gD_fail.append((wd, mkname))

        # ---- Gate B: episode<->anchor reconcile with gap-through licensing
        if side == 1:
            gaprows = np.flatnonzero(H[:i0] < m) if i0 > 0 else np.array([], int)
        else:
            gaprows = np.flatnonzero(L[:i0] > m) if i0 > 0 else np.array([], int)
        has_gap = gaprows.size > 0
        ep_pen = abs(m - mc_px) if mc_px is not None else 0.0
        ep_rev = np.nan
        if mc_px is not None:
            k_ = i_tr + (int(np.argmin(Wl[i_tr:])) if side == 1 else int(np.argmax(Wh[i_tr:])))
            ep_rev = float(Wh[k_:].max() - m) if side == 1 else float(m - Wl[k_:].min())
        pen_ok = abs(ep_pen - a.pen) <= 1e-9
        rev_ok = (np.isnan(ep_rev) and np.isnan(a.rev_after)) or \
                 (np.isfinite(ep_rev) and np.isfinite(a.rev_after) and abs(ep_rev - a.rev_after) <= 1e-9)
        if not (pen_ok and rev_ok):
            if has_gap:
                gB_exc.append((wd, mkname, str(ts(int(dts[gaprows[0]])))))
            else:
                gB_fail.append((wd, mkname, ep_pen, a.pen, ep_rev, a.rev_after))
        if not np.isfinite(do) or not np.isfinite(dc): pop['d_nan_rows'] += 1

        # ---- PATH: every other-NAME mark, first tag in window
        othr = names != mkname
        for k2 in np.flatnonzero(othr):
            col = T[i0:, k2]
            ftg = first_true(col)
            if ftg is not None:
                path_rows.append(key + (names[k2], float(prices[k2]), int(Wd[ftg])))

        ep_rows.append(key + (alc, pmn, pmp, pma, tie, cupn, cupp, cdnn, cdnp,
                              int(Wd[i_tr]) if i_tr is not None else None,
                              int(Wd[i_cl]) if i_cl is not None else None,
                              b_px, b_at, mc_px, mc_at, rt_at, rte_px, rte_at, rr_at,
                              ta_px, ta_at, f_mae, f_mae_at, f_mfe, f_mfe_at,
                              r_mae, r_mae_at, r_mfe, r_mfe_at, dc, day_end, nW))

    epcols = ['coin','wdate','mark','price','t0','approach_local_close','prior_mark_name',
              'prior_mark_price','prior_mark_at','tie_count','corridor_up_name','corridor_up_price',
              'corridor_dn_name','corridor_dn_price','first_trade_beyond_at','first_close_beyond_at',
              'bounce_ext_price','bounce_ext_at','max_cont_price','max_cont_at','retest_touch_at',
              'retest_ext_price','retest_ext_at','reclaim_close_at','travel_after_price',
              'travel_after_at','fade_mae_price','fade_mae_at','fade_mfe_price','fade_mfe_at',
              'rt_mae_price','rt_mae_at','rt_mfe_price','rt_mfe_at','day_close_price','day_end_at',
              'bars_in_window']
    EP = pd.DataFrame(ep_rows, columns=epcols)
    for col in ['prior_mark_price','corridor_up_price','corridor_dn_price','bounce_ext_price',
                'max_cont_price','retest_ext_price','travel_after_price','rt_mae_price','rt_mfe_price']:
        EP[col] = pd.to_numeric(EP[col])
    for col in [c for c in epcols if c.endswith('_at')]:
        EP[col] = pd.to_datetime(EP[col], unit='ns', utc=True)
    PA = pd.DataFrame(path_rows, columns=['coin','wdate','mark','price','t0','path_mark','path_price','first_tag_at'])
    PA['first_tag_at'] = pd.to_datetime(PA.first_tag_at, unit='ns', utc=True)
    PA = PA.sort_values(['wdate','t0','mark','first_tag_at','path_mark']).reset_index(drop=True)
    PA['seq'] = PA.groupby(['wdate','mark','t0']).cumcount() + 1
    PA = PA[['coin','wdate','mark','price','t0','seq','path_mark','path_price','first_tag_at']]
    EX = pd.DataFrame(exc_rows, columns=['coin','wdate','mark','price','t0','basis','seq','side','px','at'])
    EX['at'] = pd.to_datetime(EX['at'], unit='ns', utc=True)

    # ---- Gate D keys 1:1
    kA = AN[['wdate','mark','price','t0']].sort_values(['wdate','mark']).reset_index(drop=True)
    kE = EP[['wdate','mark','price','t0']].sort_values(['wdate','mark']).reset_index(drop=True)
    keys_ok = len(kA) == len(kE) and kA.equals(kE)

    EP.to_parquet(f'{OUT}/episodes_{coin}.parquet', compression='zstd', index=False)
    PA.to_parquet(f'{OUT}/episode_path_{coin}.parquet', compression='zstd', index=False)
    EX.to_parquet(f'{OUT}/episode_exc_{coin}.parquet', compression='zstd', index=False)

    stats = {'anchors': int(len(AN)), 'episodes': int(len(EP)), 'path': int(len(PA)),
             'exc': int(len(EX)), 'keys_1to1': bool(keys_ok),
             'gateA_n': gA['n'], 'gateA_mism': gA['mism'],
             'gateA_maxdiff_pen': gA['max_pen'], 'gateA_maxdiff_rev': gA['max_rev'],
             'gateA_bad': gA['bad'],
             'gateB_exceptions': gB_exc, 'gateB_fail': gB_fail, 'gateD_fail': gD_fail,
             'pop': pop, 'minutes': round((time.time()-t_c)/60, 2)}
    print(f'{coin}: episodes {len(EP):,} (anchors {len(AN):,}) · path {len(PA):,} · exc {len(EX):,} '
          f'· gateA mism {gA["mism"]} · gateB exceptions {len(gB_exc)} fails {len(gB_fail)} '
          f'· keys1to1 {keys_ok} · {stats["minutes"]}min')
    hard_fail = (gA['mism'] > 0) or (len(gB_fail) > 0) or (len(gD_fail) > 0) or (not keys_ok) \
                or (len(EP) != len(AN))
    return stats, hard_fail

# ---------------------------------------------------------------- report
def narrate_example():
    try:
        EP = pd.read_parquet(f'{OUT}/episodes_BTC.parquet')
        r = EP[(EP.wdate == '2024-08-05') & (EP.mark == 'PDC')].iloc[0]
        AN = pd.read_parquet('results/layerb/anchors_BTC.parquet')
        ar = AN[(AN.wdate == '2024-08-05') & (AN.mark == 'PDC')].iloc[0]
        f = lambda t: str(t)[:16] if pd.notna(t) else 'null'
        g = lambda v: f'{v:.2f}' if pd.notna(v) else 'null'
        pen_ep = abs(r.price - r.max_cont_price)
        return (f"WORKED EXAMPLE (from the shipped row) — BTC · 2024-08-05 · PDC @ {r.price:.2f} · "
                f"t0 {f(r.t0)} · tie_count {int(r.tie_count)} · corridor {r.corridor_up_name} {g(r.corridor_up_price)} / "
                f"{r.corridor_dn_name} {g(r.corridor_dn_price)} · prior mark {r.prior_mark_name if isinstance(r.prior_mark_name,str) else 'null'} · "
                f"trade-beyond {f(r.first_trade_beyond_at)} · close-beyond {f(r.first_close_beyond_at)} · "
                f"bounce {g(r.bounce_ext_price)} @ {f(r.bounce_ext_at)} · max-cont {g(r.max_cont_price)} @ {f(r.max_cont_at)} · "
                f"retest {f(r.retest_touch_at)} · retest-ext {g(r.retest_ext_price)} @ {f(r.retest_ext_at)} · "
                f"reclaim {f(r.reclaim_close_at)} · travel-after {g(r.travel_after_price)} @ {f(r.travel_after_at)} · "
                f"fade MAE {g(r.fade_mae_price)}@{f(r.fade_mae_at)} MFE {g(r.fade_mfe_price)}@{f(r.fade_mfe_at)} · "
                f"rt MFE {g(r.rt_mfe_price)}@{f(r.rt_mfe_at)} MAE {g(r.rt_mae_price)}@{f(r.rt_mae_at)} · "
                f"day close {g(r.day_close_price)} · bars {int(r.bars_in_window)} · "
                f"GATE pen {pen_ep:.5f} == anchor {ar.pen:.5f} {'PASS' if abs(pen_ep-ar.pen)<=1e-9 else 'FAIL'}")
    except Exception as e:
        return f'example narration unavailable: {e}'

def write_report():
    S = st['stats']; L = []
    L.append(f'# EPISODES REPORT — {pd.Timestamp.now(tz='UTC')}')
    L.append('tables: episodes (wide, 37 cols) · episode_path (grid ruler) · episode_exc (joint-4 excursion ladder)')
    te = sum(S[c]['episodes'] for c in S); ta = sum(S[c]['anchors'] for c in S)
    tp = sum(S[c]['path'] for c in S); tx = sum(S[c]['exc'] for c in S)
    L.append(f'expected vs actual: episodes {te:,} vs anchors {ta:,} '
             f'({"MATCH" if te==ta else "MISMATCH"}) · path {tp:,} · exc {tx:,} (ship-time outputs, reconciled per episode)')
    for c in S:
        s = S[c]; p = s['pop']
        L.append(f"{c}: episodes {s['episodes']:,}/{s['anchors']:,} · path {s['path']:,} · exc {s['exc']:,} "
                 f"(fade ev {p['exc_fade_events']:,} · rt ev {p['exc_rt_events']:,}) · keys1:1 {s['keys_1to1']} · "
                 f"gateA {s['gateA_n']:,} rows, mism {s['gateA_mism']}, maxdiff pen {s['gateA_maxdiff_pen']:.2e} rev {s['gateA_maxdiff_rev']:.2e} · "
                 f"gateB exceptions {len(s['gateB_exceptions'])} (gap-through, listed) fails {len(s['gateB_fail'])} · "
                 f"gateD fails {len(s['gateD_fail'])}")
        L.append(f"  populations: never-beyond {p['never_beyond']} · touch-on-open {p['touch_on_open']:,} · "
                 f"no-close-beyond {p['no_close_beyond']:,} · no-retest {p['no_retest']:,} · held-to-close {p['held_to_close']:,} · "
                 f"final-partial-day {p['final_day']} · exact-tie rows {p['tie_rows']:,} · 1D-nan rows {p['d_nan_rows']}")
        L.append(f"  same-bar both-sides pairs: entry-bar (structural) {p['sb_entry_pairs']:,} · "
                 f"interior fade {p['sb_interior_fade']:,} · interior rt {p['sb_interior_rt']:,} — ambiguity is COUNTED; "
                 f"order questions resolving inside one 5m bar are a third outcome, never guessed")
        for e in s['gateB_exceptions']:
            L.append(f'  gap-through exception: {c} {e[0]} {e[1]} — first fully-beyond pre-t0 bar {e[2]}')
    L.append(narrate_example())
    L.append('(b)-LINES: tag = h>=price>=l · beyond/close-beyond/reclaim strict · side inherited from anchor open_side · '
             'retest defined off first CLOSE beyond · story grain 5m (record finest) · corridor+path grid = same-day ET period marks · '
             'prior mark = last pre-t0 different-price tag, nearest price on multi-mark bars, names "+"-joined · '
             'exc event = strict extension of running excursion; entry bar seeds both sides (structural pair) · '
             'seq ties at equal timestamps break by fixed side/name order and carry NO within-bar meaning · '
             'window end = last 5m bar of the wdate + 5min; final partial day truncates there. '
             'Raw dollars + UTC timestamps only; no thresholds stored; labels are query-time with parameters attached. '
             'Counts only; verdicts are Svet\'s.')
    open(f'{OUT}/REPORT.md','w').write('\n'.join(L) + '\n')
    print(f'REPORT written -> {OUT}/REPORT.md')

# ---------------------------------------------------------------- main
docs_step()
any_fail = False
for coin in COINS:
    if coin in st['done']:
        print(coin, 'done'); continue
    if (time.time()-T0)/60 > A_.budget_min - 8:
        print('budget; resume'); break
    stats, hard_fail = build_coin(coin)
    st['stats'][coin] = stats
    if hard_fail:
        json.dump(st, open(SF,'w'), default=str)
        print(f'GATE FAIL on {coin} — STOP (drift law); coin NOT marked done.'); any_fail = True; break
    st['done'].append(coin)
    json.dump(st, open(SF,'w'), default=str)
if not any_fail and all(c in st['done'] for c in ['BTC','ETH','SOL','XRP']):
    write_report()
print(f'total {round((time.time()-T0)/60,2)} min · deterministic, no RNG')
sys.exit(1 if any_fail else 0)
