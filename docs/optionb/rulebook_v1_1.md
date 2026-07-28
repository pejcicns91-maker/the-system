# OPTION B (COMFORT BOOK PLUS) — RULEBOOK v1.1

*2026-06-12. Supersedes v1.0. Adds: half-off mechanics formalized, funded-ladder verification (PASSED), base risk 0.75% (adjustable), MCO context layer doctrine, cTrader VERIFY checklist. This document is the operating contract. Never change rules mid-attempt; changes only between attempts, version-numbered.*

---

## 1. ACCOUNT & MISSION

FTMO 100k, 2-step **Swing** challenge (Swing type assumed OK — **VERIFY in cTrader before first fee**). Phase 1 +10%, Phase 2 +5%, max daily loss −5% (resets 00:00 Prague), max total loss −10% (static on initial balance), min 4 trading days/phase, no time limit. Fee ~$550, refunded with first payout.

## 2. THE THREE SLEEVES

### Sleeve A — FADE-K5-half (daily dip-buy)
- Instruments: XAUUSD, USDJPY, US30, GER40, US500, US100
- **Signal** at daily close: `close/close[5] − 1 < −1.0 × (ATR14/close) × √5`
- Enter long at signal close. Initial stop = entry − 2×ATR14.
- At +1R (entry + 2×ATR14): close half, move stop to breakeven (entry).
- Remainder exits at stop/BE, or time exit at close of the **10th trading day** after entry.
- One position per instrument.

### Sleeve B — DON-20-half (daily breakout)
- Instruments: XAUUSD, XAGUSD, US500, US100
- **Signal** at daily close: close > highest high of prior 20 days (excluding signal bar).
- Same mechanics: stop 2×ATR14, half at +1R → BE, time exit close of **40th day**.
- One position per instrument.

### Sleeve C — DON-55-half (4H crypto breakout)
- Instruments: BTCUSD, ETHUSD, SOLUSD, XRPUSD (FTMO symbols; data = Binance USDT)
- **Signal** at 4H close: close > highest high of prior 55 4H bars (excluding signal bar).
- Stop 2×ATR(14, 4H), half at +1R → BE, time exit close of **48th 4H bar**.
- **Max 3 concurrent crypto positions** — skip new signals at cap.

## 3. SIZING — THE LADDER (adjustable, version-controlled)

Risk per trade = base × ladder fraction, on **initial phase balance**:

| Phase equity | Fraction | At base 0.75% | At base 1.00% |
|---|---|---|---|
| ≥ −3% | 1 | 0.75% | 1.00% |
| −3% > eq ≥ −6% | 2/3 | 0.50% | 0.667% |
| < −6% | 1/3 | 0.25% | 0.333% |

- **Challenge base: 0.75%** (user-selected). Bootstrap at 0.75%: **91% of attempts pass, median 8 months, 42% within 6.** At 1.00%: 85% pass, median 6 months, 55% within 6. Both validated — the dial trades speed for survival. Change only between attempts; log the version.
- Risk = entry→stop distance. `lots = (balance × risk%) ÷ (stop_distance × contract value per point)`, **rounded down** to broker lot step.
- **Aggregate open-risk cap 4%**: sum over open positions of distance-to-**current**-stop risk (halved+BE positions count ≈0). Skip new signals at cap.
- **Daily circuit breaker 3%**: if realized losses since 00:00 Prague reach 3%, no new entries until reset. (Keeps worst day far from FTMO's −5%; worst observed day in 2021–2025 funded replay: −1.04%.)

### Funded mode — VERIFIED 2026-06-12
- Base **0.50%** with the same ladder. 2022 full-year mark-to-market replay: **trough −8.5%, worst day −0.40%, survives the −10% line** — but the 1.5% margin is thin. **FLAG:** in a 2022-grade regime, consider the conservative option **base 0.375%** (replay trough −7.6%).
- Constant 0.50% (no ladder, the v1.0 plan) **breached** in the same replay (trough −12.5%). The ladder is not optional in funded mode.
- Other years at funded ladder 0.50%: 2021 +9.8%, 2023 +22.8%, 2024 +26.1%, 2025 +22.9%.

## 4. EXECUTION CONVENTIONS (the fine print that makes results reproducible)

1. **ATR14** = simple moving average of true range.
2. Donchian highs **exclude the signal bar**.
3. Entry at the close of the signal bar (market order at/near close).
4. **Gap rule**: if the next open is beyond stop/BE/target, that leg exits at the open (worse fill honored).
5. **Stop priority**: if stop and target are both touchable in the same bar, assume the stop hit first (worse case).
6. Same-bar sequence after a gap-open through the target: half off at open → stop to BE → if low ≤ BE that bar, remainder out at BE.
7. **Time exit** = at the close of the Nth bar after the entry bar (N = 10/40/48 per sleeve).
8. **Re-entry allowed on the exit bar** if it independently qualifies as a signal.
9. One position per instrument per sleeve; the same instrument may be held by two sleeves simultaneously (e.g. XAUUSD FADE + DON20) — each counts toward the 4% cap.
10. If a signal fires but the ladder/cap/circuit-breaker blocks it: **skipped, not queued.**
11. Weekend/holiday bars don't exist in daily data; "10 trading days" means 10 bars.
12. Crypto trades 24/7 — 4H bars are UTC-aligned (00/04/08/12/16/20).

## 5. COST & FINANCING MODEL (for any future re-validation)

- Round-trip cost on notional: non-crypto 0.02% base / 0.05% stress; crypto 0.11% / 0.17%.
- Financing 0.007% per 4H bar **applied to crypto holding bars only** ("variant A" — this matches the original validation; see integrity report). A harsher run charging dailies 6×4H-bar financing per day still nets +1.85 R/mo — the system is positive under both interpretations, but live daily-CFD swap should be monitored against this band.

## 6. MCO CONTEXT LAYER — DOCTRINE

- Role: **display/tag only.** MCO 3-horizon synthesis (6-month / 1-month / 1-week bias + zones) is shown next to Option B signals. A crypto signal inside/above MCO support = "confluence" tag; against bias = "counter-MCO" tag. **Tags never gate entries, sizing, or selection.**
- Refresh: re-export the Discord channel → run `mco_parse.py`. Terminal (https://terminal.mcoglobal.live/) is a Streamlit app, screen-only, no API — password rotates monthly, kept in `.env` as `MCO_TERMINAL_PASSWORD`.
- **Upgrade path (pre-registered, §4 of handoff):** MCO may become a filter ONLY if, on Aug-2024→present crypto signals: (a) it improves meanR at both cost levels, (b) holdout-consistent, (c) ≥2 of 3 assets agree. Until that study passes, any urge to skip a signal "because MCO is bearish" is a rule violation.

## 7. cTRADER VERIFY CHECKLIST (before first fee)

- [ ] Account type = **Swing** (no news/weekend restrictions)
- [ ] Contract size / value-per-point for all 11 symbols (config.yaml placeholders: XAUUSD 100/lot, XAGUSD 5000, USDJPY 100k JPY-quote, indices 1, GER40 EUR-quote, BTC/ETH 1, SOL 10, XRP 1000 — **all marked verify:true**)
- [ ] Lot step + minimum lot per symbol (rounding direction = down)
- [ ] Actual swap/financing rates vs §5 band
- [ ] Crypto available on the 100k swing account
- [ ] Daily-loss timer confirmed 00:00 Prague

## 8. OPERATING PROCEDURE (daily)

1. After NY close (and per 4H close for crypto): run `python engine.py` (or `--refresh` to refetch data). Update `equity_pct` in config (include floating PnL).
2. Place new entries with printed lots; set stop; set alert at +1R for the half-off.
3. Manage open book per printed lines (half target / BE / bars to time exit).
4. Log every trade (entry, stop, lots, ladder state, MCO tag) — the log is the audit trail for change control.
5. **Phase 5 gate: one full paper month before paying the first $550 fee. Non-negotiable.**

## 9. CHANGE CONTROL

Any rule, sizing, or instrument change: written here first, version bumped, effective only at the next attempt boundary. MCO promotion requires the §6 study to pass. Open research items (SOL flip-candle bracket on BTC/ETH, COT metals quarantine, sealed CL=F/HG=F) remain parked and out of scope for live trading.

---
## ADDENDUM 2026-06-12 — FTMO specs verified online (confirm on account)
Source: ftmo.com live symbols API. Contract sizes: XAUUSD 100, XAGUSD 5000, USDJPY 100k(JPY), indices 1 (GER40 EUR), BTC 1, **ETH 10, SOL 100, XRP 10000** (3 placeholders corrected — would have caused 10× crypto oversizing). Crypto confirmed tradeable (BTC/ETH/SOL/XRP active). **Swing leverage: FX 1:30, metals/indices 1:15, crypto 1:1.** New rule: crypto margin guard — sum of open crypto notional + new ≤ $95k; engine enforces (backtest: 3% of entries skipped, peak need $94k). FTMO-true costs (crypto swap −30%/yr both sides ≈0.082%/day; dailies ≈0.02%/day; crypto comm 0.065% RT): **PLUS +2.11 R/mo; +1.89 with margin constraint** — between prior base (+2.71) and harsh (+1.85) cases. Swaps float; re-pull monthly. Residual cTrader checks: min lot/step only (assumed 0.01; indices may be 0.1) + Swing-type confirmation.
