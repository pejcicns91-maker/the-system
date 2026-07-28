# MAPMONEY-1b — RESULTS (2026-07-23) · VERDICT: KILL (touch-continuation)
Prereg: MAPMONEY1b_prereg.md. Contract items in order.

## 1. Prereg vs ran — DEVIATIONS
None. Same data files, same validated wall series, same sealed cut dates as MAPMONEY-1 (loaded from mm1_results.json, not recomputed). DROPPED: nothing.

## 2. Artifacts (rerun: `python3 mm1b.py && python3 analyze_b.py`, seed 20260723)
mm1b_trades.csv — 4,874 rows, sha256 `2571b0c2bf6ce4b5…` · mm1b_results.json · data hashes as in MAPMONEY-1.

## 3–4. Headline (FULL history) with n and opponents
4,874 trades · WR 37.4% · **frictionless mean R −0.143** — genuinely negative before any cost · FTMO −0.202/trade, net −983R, −9.3 R/mo. Exits: 2,278 TP · 1,116 stop · 1,480 time.
**Sealed vs matched-random placebo (100 sims, FTMO):** worse than random in **7/8 cells** at FDR q=.10 (BTC-L/S, ETH-S, SOL-L/S, XRP-L/S all p≤.03; ETH-L p=.13). Entering 0.6U into a push, at the wall, is a systematically bad price.

## 5. Spot-checks (UTC, verify on chart)
- LOSS: ETH long 2026-01-13 22:10, entry 3362.48 → stopped same bar 3308.86, R −1.0
- WIN(t): BTC long 2017-09-23 10:55, entry 3780 → day-end 3798, R +0.07
- Plus MAPMONEY-1's checks stand for the shared wall series.

## 6. Decomposition — uniform death, one underpowered ember
Every year 2017–2026 negative (−0.13 to −0.30). Hayden: Bull −0.228 / Bear −0.193 / Chop −0.133. Weekday −0.200 ≈ weekend −0.211. Sides: L −0.158 / S −0.241. DISC −0.206 / SEAL −0.192 — stable death, no regime flip to map. Contact buckets: ≥50 −0.181 (n 4,205) · <30 −0.379 · **30–49 = +0.025 on n=75 → UNDERPOWERED ember, logged, not a finding.**

## 7. Money-claim stamp
Touch-continuation @0.6U trigger, stop at edge, next-wall target: **DISCOVERY FAIL, SEALED FAIL. KILLED at this spec.** Frictionless-negative means no cost or sizing model rescues it.

## 8. The synthesis (the actual product of 1 + 1b)
At n≈20,600 combined: **both directions lose at the wall.** The fade loses because touches continue (the ladder is real); the continuation loses because the confirmation price is 0.6U too late and the next wall is too far (the graveyard's entry-geometry law, and the SD program's breakout holdout, reproduced a third time independently). The map reads the tape correctly and neither naive monetization pays — "right-but-unpaid" is now demonstrated at industrial scale on the wall object itself. Any further wall-money attempt must attack the ENTRY PRICE (e.g., the retest-after-break geometry — untested-list item 3), not the direction.

## 9. Downgrades
None — all items produced.
