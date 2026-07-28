# MAPMONEY-1 — RESULTS (2026-07-23) · VERDICT: KILL (touch-fade)
Prereg: MAPMONEY1_prereg.md. Contract items in order.

## 1. Prereg vs ran — DEVIATIONS
- Data fetch mechanism: live klines API → Binance Vision monthly archives + API tail (same vendor/data; timeout-driven; hash-logged).
- **Run #1 VOID:** simulation was executed before the port-validation gate was checked (sequencing error). Its output was quarantined unread and is superseded.
- Port bug found & fixed during validation: ON window used same-day (lookahead) — corrected to the completed overnight (prev-wd 17:00→08:00).
- Live m9b defects found & fixed (3 one-liners): 40d fetch truncated prev-month levels → 70d; ON fallback dropped the 00:00–08:00 leg; Hayden re-pinned to its 40d window. After fixes: **port-validation gate PASS, wall-for-wall, all 4 coins.**
- Nothing else deviates. DROPPED: nothing.

## 2. Artifacts (rerun: `python3 mm1.py && python3 analyze.py`, seed 20260723)
- data/{SYM}_5m.csv — BTC 937,919 `1ac003e9…` · ETH 937,919 `303e70b0…` · SOL 625,395 `75e23943…` · XRP 863,520 `d46b9eba…`
- mm1_trades.csv — 15,716 rows, sha256 `469efc9a08404c61…`
- mm1_results.json, mm1_port_validation.json, MAPMONEY1_prereg.md

## 3–4. Headline (FULL history, all data, weekends in) with n and opponents
15,716 trades · WR 54.4% · **mean R frictionless −0.009** (a statistical zero) · **FTMO −0.070/trade, −10.4 R/mo, net −1,100R**. Exits: 6,036 TP · 4,293 stop · 5,387 time.
**Sealed segment vs matched-random placebo (100 sims/cell, FTMO costs):** the fade doesn't just fail — it loses MORE than random entries in 5/8 cells at FDR q=.10: ETH-L p=.0099, ETH-S .0099, SOL-S .0099, BTC-S .0299, XRP-S .0299 (actual net below placebo median in every one). BTC-L .17, SOL-L .55, XRP-L .69 — indistinguishable from random.

## 5. Spot-checks (verify on TradingView; UTC)
- LOSS: ETH long 2024-10-31 12:00 entry 2638.81 → stopped 14:00 at 2580.65, R −1.0
- LOSS (time): BTC long 2017-09-20 14:30 entry 4029.99 → day-end 3864.95, R −0.69
- WIN: ETH long 2019-07-05 20:30 entry 284.48 → TP 291.02 (R +0.46)
- TODAY: SOL long 16:20 UTC at 75.85 (zone-4 touch — the exact trade Svet asked about) → time-exit 75.96, R +0.08 · XRP long 15:05 at 1.1059 → 1.1070, R +0.06

## 6. Decomposition (FTMO mean R) — uniform death, no regime marker
Year: −0.04 to −0.11 every year 2017–2026, no positive year. Hayden: Bull −0.061 / Bear −0.076 / Chop −0.079. Weekday −0.070 = weekend −0.070. Side: L −0.048 / S −0.092 (shorts worse). Contact: ≥50 −0.065 (n 13,521) / <30 −0.095 / 30–49 −0.143 — **weak walls fade worst**, direction consistent with the map. DISC −0.059 → SEAL −0.097 per trade (both dead; no flip to map).

## 7. Money-claim stamp
Touch-fade @0.6U-stop → next wall: **DISCOVERY-tested and SEALED-tested, FAIL both. Status: KILLED at this spec.** Frictionless zero means no cost model rescues it.

## 8. The real finding (raw frequency, uncertified)
Wall touches carry information AGAINST the fade — timed entries underperform random location. That is the P&L shadow of the banked ladder (0.6U penetration → 79% continues). The mirror hypothesis — **touch-continuation / go-with-the-penetration** — is now the motivated candidate. It is NOT tested here and does NOT inherit anything; it requires its own prereg (item for the untested list).

## 9. Downgrades
None required — all contract items produced.
