# MAPMONEY-1 — Wall touch-fade money test (pre-registration, 2026-07-23)
**Untested-list item 1. This file precedes all measurement. Contract CONTRACT_AUDIT.md applies.**

## Mode
MONEY TEST → sealed split required (rule 4). Discovery = first 70% of each coin's history by date; SEALED = last 30%, opened once, after the discovery read is written. Production numbers refit on full history only if the gate passes. A regime-flip FAIL routes to the map (rule 3), not the graveyard.

## What data it sees
Binance spot 5m klines, FULL listing history per coin (BTCUSDT, ETHUSDT from 2017-08; XRPUSDT 2018-05; SOLUSDT 2020-08) → 2026-07-23, fetched fresh, sha256 hash-logged per the vendor-revision law. First 35 days per coin excluded (warmup for PW/PM windows and the 14-day U median). Weekends included.

## Wall reconstruction (faithful port of m9b_daily.py, deterministic)
Per coin per day D (day boundary = 08:00 ET, m9b's `wd` convention), using ONLY data before D's boundary: levels = {PD,ON,PS,PW,PM} × {H,L,C,POC} (POC = m9b's 100-bin volume-mid method); uAbs = median of the last 14 daily ranges; walls = levels clustered at gap > 0.25·uAbs; contact% = m9b's banked gravity interp on yesterday's gap; virgin flag = 20-day straddle count 0. Hayden-4H state per day from m9b's gated port.
**Port-validation gate (binding):** the port's 2026-07-23 wall sets must reproduce today's live m9b lines on all 4 coins (edges within print rounding). Fail → STOP, report, no backtest.

## Trade specification (locked)
- Event: FIRST entry of price into a wall zone from outside during day D (5m bar crossing the proximal edge). One trade per wall per day; one open position per coin (first-come); re-entry into the same wall that day: none.
- Entry: limit at the proximal edge, filled on the crossing bar at the edge price (gap-aware: fill at open if it gaps through).
- Direction: fade — away from the wall (approach from below → short; from above → long).
- Stop: 0.6·uAbs beyond the proximal edge in the adverse direction (the banked 79%-continues line). R := 0.6·uAbs.
- Target: proximal edge of the NEXT wall in the profit direction from that day's wall set. No such wall → no trade (count reported).
- Same-bar stop+target touch → stop first (conservative). Unresolved by the next 08:00 ET boundary → exit at that bar's close (mark-to-market R).
- Costs, dual rows: P0 frictionless; FTMO = 0.135% round-trip of entry notional (in R via R-distance) + 0.082% per crossed 00:00 UTC.

## Endpoints & gate
Primary: mean R per trade and R/month at FTMO costs. Gate to "alive": discovery FTMO mean R > 0 AND sealed FTMO mean R ≥ 0 with sealed n ≥ 40, AND sealed placebo p ≤ BH-q=.10 within the family {4 coins × 2 sides}. UNDERPOWERED (n<40) is re-queued, never killed.

## Null
100 placebo sims per coin×side: matched trade count, uniform random entry bars, same 0.6U stop, TP distance resampled from that coin×side's realized TP-distance distribution, same queue and time-exit. Empirical two-sided p on netR. Seed 20260723.

## Regime columns emitted (rules 1–3)
Full-history headline beside: per-year · per-Hayden-4H · weekday/weekend (ET) · per-asset · per-side · wall-strength bucket (contact <30 / 30–49 / ≥50) · virgin flag. Instability across splits = regime marker, promoted as conditional, never averaged away.

## Deviations
Any deviation from this file is reported in the results under DEVIATIONS, never promoted. DROPPED section mandatory.
