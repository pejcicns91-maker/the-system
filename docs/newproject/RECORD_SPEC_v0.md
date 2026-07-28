# RECORD SPEC v0 — Layer A of The System (DRAFT for Svet's markup; nothing runs until signed)

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
Spec markup (you) → one-day proof (under the cost gate, runs on your word) → full-build pitch (three lines, you say go) → Layer B: every component alone, complete → Layer C: combinations → day-character campaign = the first query set on the finished record. Full statistical tables ship as files, sorted by n descending — the frequent and identifiable on page one, the rare still on the last page.