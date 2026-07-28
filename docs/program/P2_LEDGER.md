# MAP V3 — P2 LEDGER (2026-07-23)
**Artifact:** p2_events_ALL.csv — 185,452 events · sha `fcf1262aff20e062…` · per-coin: BTC 50,004 (`5be9f922…`) · ETH 50,256 (`f058fa80…`) · SOL 35,206 (`7d6ef50e…`) · XRP 49,986 (`b6c93728…`) · rerun: `python3 p2.py {SYM} {NM}` (BTC first — it writes btc_ctx.csv), seed 20260723.

**EXAMINED (this step):** all 4 coins, full listing history, weekends in — 3,229/3,229/2,139/2,969 days. Event taxonomy incl. the new **EXIT** type (day-opens-inside → closes out through an edge): 12,681 EXITs, 22,302 BREAKs, 4,379 TRAVs, 17,571 TOUCHes, 9,215 PENs, 23,852 STALLs, 95,452 RETESTs. Groups A/B/D/E full. Group C: hayden (own) 100%, hayden_btc 100%, btc_pi 97% (na = pre-2018-07, 350-day MA warmup) — **pi formula validated against the engine's live state (down=down) before adoption.**

**The graze answer (Svet's buffer request, measured not assumed):** TOUCH+PEN depth quantiles = 0.021 / 0.058 / 0.141 / 0.283 U at 25/50/75/90%. A quarter of all touches penetrate ≤0.02U — today's 12:20 tag (0.007U) sits in that graze mass. P3 will carve the graze subclass from this distribution.

**REMAINING (from design):** daytype, yd_arch, lean columns — still 'na': their exact engine definitions aren't reconstructable without inventing them (contract §2 forbids); options are a validated engine-port later or forward-filling from daily briefs. Inside-edge taps. T1 marginals / T2 certified pairs / T3 triples. Transition matrix. Forecast layer + Brier scoring. Synthesis (MAP_V3.md).

**DROPPED/DEFERRED:** nothing dropped. Deferred with reason: the three 'na' columns above.

**Deviations this step:** two performance rewrites (precomputed day-ranges & week-to-date ranges — no semantic change); EXIT convention set to one-per-edge-per-day (mirrors the one-trade-per-wall convention); pi-cycle formula (111d MA vs 2×350d MA on day closes) adopted only after validation.

**Assumption-for-measurement flags:** none new — proximity/cool-off constants unchanged from P1 disclosure.
