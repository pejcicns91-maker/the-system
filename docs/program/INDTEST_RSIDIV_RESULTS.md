# INDTEST-RSIDIV — RESULTS (2026-07-21)
Prereg: INDTEST_RSIDIV_prereg.md. Mode: DISCOVERY. Data: Binance 1h full listing history → 2026-07-21 (BTC/ETH 78,129 bars from 2017-08; XRP 71,925 from 2018-05; SOL 52,075 from 2020-08), weekends included. Regime columns: asset · year · Hayden-4H · weekday/weekend(ET). Seed 20260721.

## 1. ACCURACY — full-history headline (rule 1), h=24 bars, all signals
| asset | arm | side | N | hit24 | base | Δpp | p(binom) | FDR |
|---|---|---|---|---|---|---|---|---|
| BTC | B 5/5 | bull | 500 | .620 | .520 | +10.0 | 1e-5 | PASS |
| BTC | B 5/5 | bear | 580 | .519 | .479 | +3.9 | .061 | fail |
| ETH | B 5/5 | bull | 438 | .596 | .515 | +8.1 | 7e-4 | PASS |
| ETH | B 5/5 | bear | 540 | .546 | .485 | +6.1 | .004 | PASS |
| SOL | B 5/5 | bull | 350 | .614 | .494 | +12.1 | 1e-5 | PASS |
| SOL | B 5/5 | bear | 397 | .610 | .504 | +10.5 | 3e-5 | PASS |
| XRP | B 5/5 | bull | 384 | .599 | .487 | +11.2 | 1e-5 | PASS |
| XRP | B 5/5 | bear | 405 | .637 | .512 | +12.5 | 0 | PASS |
| all | A 47/1 | both | 20–35/cell | .37–.72 | — | — | — | **UNDERPOWERED** (floor 40) |

Non-overlap sensitivity (≥24h gap between counted signals, post-hoc, reported not promoted): rates essentially unchanged (e.g. BTC bull .610 n=410; XRP bear .645 n=346). The effect is not an overlap artifact.

## 2. REGIME DECOMPOSITION (rules 2–3), ARM-B pooled hit24
- **Year:** 2017 .513 · 2018 .602 · 2019 .642 · 2020 .522 · 2021 .573 · 2022 .612 · 2023 .588 · 2024 .595 · 2025 .588 · 2026 .601 — stable, no dead era.
- **Hayden:** Bull .571 (n=1180) · Bear .590 (1111) · Chop .626 (430) · UNTAGGED .588 (873) — mild Chop tilt (+5.5pp vs Bull), raw frequency only; candidate conditional, not a flip.
- **Weekday .591 / Weekend .577** — no split.
Verdict on stability: uniform reading signal; no regime marker required.

## 3. MONEY — exact engine replica (2×ATR SL, 6R TP3-only, SL-priority, one-trade queue), GROSS
| asset|arm | n | WR (BE 14.3%) | netR | placebo med (100 sims) | pctile | p |
|---|---|---|---|---|---|---|
| BTC B | 491 | .138 | −15 | +29 | .20 | .41 |
| ETH B | 467 | .178 | +114 | +50.5 | .90 | .21 |
| SOL B | 310 | .155 | +26 | +26.5 | .48 | .97 |
| XRP B | 240 | .158 | +26 | +19 | .56 | .89 |
| BTC A | 61 | .115 | −12 | +3 | .21 | .43 |
| ETH A | 64 | .219 | +34 | +6 | .94 | .13 |
| **SOL A** | **49** | **.265** | **+42** | **+4 (1000 sims)** | **.983** | **.035** |
| XRP A | 45 | .111 | −10 | +4 | .26 | .53 |

Random entries with the same 6R/1R geometry are net-positive gross on these assets (long-drift + geometry). No ARM-B cell beats its matched placebo; BTC sits below it. Costs are minor here (2×ATR risk = 1.9–3.4% of price → FTMO RT cost ≈ 0.03–0.05R/trade) — cost is not the killer; absence of edge over random is.

**SOL ARM-A engine:** sole FDR survivor; re-tested at 1000 placebo reps, p=.035, holds but marginal. n=49 → PROMISING-UNDERPOWERED per the HF-iii precedent. Not a finding; eligible for FORWARD_REGISTER grading only, no capital.

## 4. VERDICTS
1. **As a 1h money system (as shipped or 5/5): DEAD vs matched baselines.** Right-but-unpaid reproduced: ~59% pooled 24h reading accuracy, zero placebo-beating P&L. Master-Reference Law 4 stands.
2. **As a reading signal (ARM-B): ALIVE, uncertified.** Confirmed regular RSI divergence at 5/5 shifts 24h directional odds +6–12pp over base, both sides, 7/8 cells FDR-pass, stable across years/Hayden/weekends. Same evidentiary tier as map-v2 conditioners pre-money-test. Candidate input for the reading layer only.
3. **Shipped config 47/1: UNDERPOWERED everywhere** (accuracy) — re-queued, not killed. Its SOL engine cell is the one spark, forward-queue only.

## 5. HONESTY LEDGER
- Defect found & fixed mid-run: first engine pass capped race scans at 5000 bars and halted on a mid-history timeout, truncating XRP-B to 17 trades; rerun uncapped (240 trades). Capped numbers discarded.
- The 16 accuracy cells are cross-asset correlated (same market hours); FDR treats them as independent — effective evidence ≈ 1–2 assets' worth. Sign consistency across 4 assets × 9 years is the stronger fact.
- Engine placebo resolution 100 sims (survivor re-run at 1000). Binomial test ignores residual clustering; non-overlap sensitivity covers it.
- Hidden bull/bear divergences, trend filters (EMA/Supertrend/HTF), and 4H timeframe: NOT tested. Promotion of anything here requires sealed split + v1.2 chain; nothing promotes today.

Files: indtest_cells.csv (all horizons), indtest_signals.csv (per-signal, regime-tagged), engine_trades_fix.csv, engine_fix.json.
