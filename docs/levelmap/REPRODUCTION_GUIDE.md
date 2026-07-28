# REPRODUCTION GUIDE — rebuild the Level Map from raw data (2026-07-09)
*This pack contains the RAW SOURCE (5m pickles) + all definitions + derived layers for cross-checking + verify_results.py (runnable assertions). A competent quant or AI following this file must land on the same numbers; verify_results.py is the pass/fail.*

## 0. SOURCE DATA (in /data of this pack)
`{SYM}USDT_5mv.pkl` ×4 (BTC/ETH/SOL/XRP): pandas DataFrame, columns dt (UTC tz or naive-UTC), o,h,l,c(,v). Binance spot 5m, 2021-09→2026-07-06. `se_ref_uhist.csv`: per (asset,d) the U unit — each coin's day-move unit in % (if median<0.5 it's stored as fraction: ×100). `v6_witness_days.csv`: per (a,d) daily Hayden label `hy` (Bull/Bear/Chop) — reference artifact for the indicator parity gate.

## 1. CORE DEFINITIONS (everything downstream uses these verbatim)
- **Day window**: 08:00 ET → next 08:00 ET (America/New_York, DST-aware). wdate = (timestamp − 8h).date(). 288 bars nominal; DST days 276/300.
- **U (absolute)**: uU = U% /100 × first bar's open of the window. All distances in "U" divide by this.
- **The 20 board levels** per day: PD/ON/PS/PW/PM × {H,L,C,POC}. PD = prior 8am-window; ON = overnight session (17:00→08:00 ET); PS = prior RTH-ish session (08:00→17:00 ET of prior day); PW = prior ISO week; PM = prior calendar month. POC = volume point of control of that period at 5m grain (max-volume price bin; bin = period's range/100). Levels roll: PD/ON/PS daily, PW Mondays, PM on the 1st. **Weekends are first-class**: Sat's PD = Fri's window, Sun's PD = Sat's (own rolled boards).
- **Zone**: level ± band. Band = 0.04·uU half-width for price-anchored (C, POC) and extreme levels alike (recorder spec constant).
- **Touch**: bar range overlaps zone (l≤zone_hi ∧ h≥zone_lo). **Event** = FIRST touch per (a,day,level): reach_bar, side = prior close vs zone (from_below/from_above/open_inside), **pen_U** = max penetration beyond the FAR edge in U over the rest of the day, exit_side at day end.
- **Outcomes**: brk = pen_U > 0.60 (the discovered boundary) · cont = exit_side continues past (above if from_below, below if from_above) · sided only (open_inside excluded from direction stats, ~4%).
- **Episodes** (multi-touch): contiguous touch runs; consolidation ruler k = bars clear required to end one (findings ruler-invariant k=1..24; k=6 canonical).

## 2. THE DIAL DEFINITIONS + BAKED CUTS
- **thr30**: signed 30-min displacement toward the level at touch, in U: s·(close[reach]−close[reach−6])/uU. Terciles (all-sided frame): ≤0.0999 rev / ≤0.2303 slow / else fast. (Contest-frame variant used by the calibrated table: 0.109/0.251.)
- **drive24**: signed displacement over 273 5m-bars (~22.75h) toward the level / uU. Terciles: ≤−0.0268 calm / ≤0.4959 mid / else driven. (Requires ≥288 bars history; n=45,481 sided events qualify.)
- **am20**: count of last 20 window-days whose daily range straddled the level value. Bins: 0–2 few / 3–7 mid / 8+ many.
- **days_since_touch**: calendar days since the level's PRICE REGION last touched (per levels_daily); virgin = >20.
- **CONTEST band**: cumulative pen ∈ (0.30, 0.60] with close still outside → the certified table's frame.
- **Hayden 4H (gated port)**: 4H bars = UTC-anchored resample of 5m; source = OHLC4; RSI-14 = SMA-seeded Wilder; state machine: cross>67→Bull(1), cross<33→Bear(2), from Bull cross<39→Chop(3), from Bear cross>61→Chop. Daily label anchor = state TWO completed 4H closes before 08:00 ET (parity 99.07% vs witness; residual = vendor vintage at marginal crossings).
- **Constellation state (M2 grammar)** per level A per day: side (yesterday close vs A) × 5-day cross (no/xup/xdn from last 5 closes vs A's TODAY value) × freshness (dst≤1 f1 / else f2) → 12 states.
- **Walls (M8.5)**: sort the 20 values; merge adjacent gaps ≤ r·uU; r ∈ {0.15,0.25,0.35}, canonical 0.25.
- **Vote (M7)**: dials {thr,drv,am,yday-type,weekday,4H-regime,flip,RSI-side,density}; each value votes +1/−1/0 by the sign of its full-history brk deviation at ±1pp floor. Baked sign map: fast+1 rev−1 slow−1 · calm+1 mid−1 driven 0 · few+1 many−1 · trend+1 lean−1 · wkday+1 wkend−1 · dens alone/1-2 +1.
- **Day archetypes**: k-means k=10 on the 288-bar close paths, frame FA = (c−open)/uU (daypaths.npz holds the paths; daypath_meta.csv the labels). yday-type map: clusters {0:lean,1:churn,2:churn,3:trend,4:parked} (FA_U_k10).

## 3. THE PIPELINE STAGES (rebuild order)
S1 levels+zones per day (from pickles) → S2 events/episodes/day-summaries → S3 M1 join (all conditioning columns; this pack ships M1_state.parquet to diff against) → S4 studies: gravity/hover (C1–C2), knocks (C3, ruler sweep), legs (C4), day-types (C5), wear (C6), lattice (D), gates (E), battery (F: 5 trigger classes per F_BATTERY_SHEET.md in the docs), archetypes, M2 constellation grid (380 pairs, shuffle census), M7 vote (TRIANGLE: fit H1≤2023-08-31→judge H2, the mirror, full-on-full, robust placebo), M8 registry, M8.5 walls.
**The Triangle Protocol** (binding on every gated claim): T1 H1→H2 · T2 H2→H1 · T3 full→full · T4 comparison; era-proof iff all agree; asymmetry → regime marker.

## 4. VERIFICATION TARGETS — run `python3 verify_results.py` (asserts all of these from the shipped layers)
Coverage 135,360 level-days · sided events 45,481 with 24h history · all-sided brk base 42.4% · CONTEST cont base ~37.3% (n=9,156 frame) · escalation ladder P(cont|pen≥x): .3→65.7 .5→75.6 .6→79.2 1.0→88.6 (±0.2) · rejection travel med 0.46U / break carry 0.77U · calibrated cells: fast|few 27.9 / rev|many 47.1 / slow|many 46.4 (±0.2) · vote T3 top-vs-bottom-15% spread +16.5±0.5, extreme buckets 32.6/50.3 · POC-cascade-dn cell 62.4% n=85 · WEEKEND-WORKED-CAP brk 33.6% n=12,356 · weekend suppressor 35.6 · gravity: touched→56.4 next-day · Hayden port parity ≥98.5% at the −1-bar anchor.
A reimplementation FROM PICKLES that reproduces S1→S2 must match level_events_v4.csv geometry bit-near (first-touch bars, pen) before proceeding — that file is the ground-truth diff target.

## 5. WHAT IS SPEC-ONLY (too large to ship; regenerate if needed)
bar_relations parquets (38.97M rows: every 5m bar × 20 levels — S1×S2 outer product, ~505MB) · approach_disp.npy (45,481×288 hourly-grain signed displacement matrix; column 273 = drive24, already materialized in M1) · c4_legs.csv (leg census; C4 numbers in docs).
