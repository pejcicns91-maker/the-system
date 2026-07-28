# 01 — OPTION B (COMFORT BOOK PLUS) — CHAT BOOTSTRAP
*Read with `00_MASTER_REFERENCE.md`. The full operating contract already exists as `rulebook_v1_1.md`; the rebuild proof is `integrity_report.md`; live config is `config.yaml`. This file is the starter + app plan + bootstrap prompt. **Option B is the agreed default deploy.***

---

## 1. WHAT OPTION B IS (one paragraph)
The mechanized, holdable core of the Skorupinski approach: multi-asset, daily + 4H, limit/close entries with structural stops, and a **half-off-at-+1R → breakeven** exit that converts a low-win-rate edge into a **55.6% win rate** you can actually sit through. ~12.9 trades/month, **+2.71 R/mo** base (**+2.11** at FTMO-true costs, **+1.89** with the crypto-margin constraint). Already data-rebuilt and integrity-checked; funded ladder already verified. The remaining work is the **app** and the **cTrader confirmations**.

## 2. THE THREE SLEEVES (complete spec — fine print in rulebook_v1_1.md §2/§4)
**A — FADE-K5-half (daily dip-buy):** XAUUSD, USDJPY, US30, GER40, US500, US100. Signal at daily close: `close/close[5] − 1 < −1.0 × (ATR14/close) × √5`. Enter long at close; stop = entry − 2×ATR14; **half off at +1R → stop to BE**; remainder exits at stop/BE or **10th-day** time exit. One position/instrument.
**B — DON-20-half (daily breakout):** XAUUSD, XAGUSD, US500, US100. Signal: close > prior-20-day high (excl. signal bar). Same mechanics; **40th-day** time exit.
**C — DON-55-half (4H crypto breakout):** BTCUSD, ETHUSD, SOLUSD, XRPUSD (data = Binance USDT). Signal: 4H close > prior-55-bar high. Stop 2×ATR(14,4H); half at +1R → BE; **48-bar** time exit. **Max 3 concurrent crypto; skip at cap.**

Conventions that make it reproducible: ATR14 = SMA of TR; Donchian excludes signal bar; entry at signal close; **gap rule** (open beyond a level → that leg exits at open); **stop-priority** (stop assumed hit before target in the same bar); time exit = close of Nth bar after entry; re-entry allowed on the exit bar; same instrument may be held by two sleeves (each counts to cap).

## 3. SIZING — LADDER (config.yaml is the source of truth)
Risk/trade = base × ladder fraction on **initial phase balance**: eq ≥ −3% → ×1; −3..−6% → ×2/3; < −6% → ×1/3. **Challenge base 0.75%** (selected; 91% pass / median 8 / 42% ≤6mo) — **1.00%** is the speed dial (85% / median 6 / 55% ≤6mo). `lots = (balance × risk%) ÷ (stop_distance × contract_value)`, rounded **down**. **Aggregate open-risk cap 4%** (distance-to-current-stop; halved+BE legs ≈0). **Daily circuit breaker 3%.** **Crypto margin guard: open crypto notional + new ≤ $95k** (crypto leverage 1:1; ~3% of entries skipped in backtest).
**Funded mode — VERIFIED:** laddered **0.50%** survives 2022 (trough −8.5%, worst day −0.40%); constant 0.50% **breaches** (−12.5%); **0.375%** is the conservative fallback for 2022-grade regimes. Switch to funded mode before the first funded trade.

## 4. VALIDATED NUMBERS (integrity_report.md, base costs, variant A, 2020-09→2026-05)
PLUS 12.9 tr/mo · WR 55.6% · +2.71 R/mo. Sleeve R/mo: FADE +0.64, DON20 +0.63, DON55 +1.43. Sleeve WR: FADE 59.6%, DON20 58.0%, DON55 52.7%. Per-year R: 2020 +27.8 · 2021 +20.1 · **2022 −24.0** · 2023 +56.6 · 2024 +62.1 · 2025 +53.1 · 2026 YTD −8.7. CORE (no crypto) ≈ 5.5 tr/mo, 59% WR, +1.20 R/mo, 1.0% ladder median ~12 mo.

## 5. MCO — SECOND COMPONENT (context layer; corrected facts)
- The Discord export `MORECR_1.JSO` is **SOL-only**: 63 posts (60 SOL + ratio/combined), 2024-08-31→2026-06-07. (The earlier "~330 multi-asset" description was wrong; does not affect Option B stats.) BTC/ETH horizons require exporting their channels and re-running `mco_parse.py`.
- Current SOL synthesis (see `mco_synthesis.md`): **bearish across all three horizons** (6mo / 1mo / 1wk) until price reclaims **$73.18+** and prints a 5-wave advance; major-low target band **$43–63**.
- **Terminal:** https://terminal.mcoglobal.live/ — Streamlit, **screen-only, no API/export**. Password **rotates monthly**, stored as `MCO_TERMINAL_PASSWORD` in `.env` (never hardcode). Refresh of structured levels = re-export Discord → `mco_parse.py` → `mco_levels.csv`.
- **Doctrine (hard rule):** MCO is **display/tag only**. A crypto signal inside/above MCO support tags *confluent*; against bias tags *counter-MCO*. **Tags never gate entries, sizing, or selection.** Acting on "MCO is bearish so I'll skip" is a change-control violation.
- **Upgrade path (pre-registered):** MCO may become a filter ONLY if, on Aug-2024→present crypto signals: (a) improves meanR at both cost levels, (b) holdout-consistent, (c) ≥2 of 3 assets agree. Until that study passes, it stays a layer.

## 6. THE APP — build order (recommended stack: Claude Code project)
- **Phase 1 — Signal engine** (core value): daily job after NY close → Sleeve A/B signals; 4H job → Sleeve C. Output per signal: instrument, entry, stop, **lots from current ladder state**, half-off/BE/time-exit instructions. Trade log (SQLite/JSON). (`engine.py` already drafts this.)
- **Phase 2 — FTMO tracker:** equity input, ladder state machine, distance-to-daily/total barriers, phase progress, attempt + fee ledger.
- **Phase 3 — MCO panel:** `mco_parse.py` → levels table; live Binance prices vs zones; confluence tags (display only).
- **Phase 4 — MCO validation study** (§5 gates) → promote to filter only on pass.
- **Phase 5 — Alerts + paper month:** Telegram/email alerts; **one full paper month before the first fee.**
- v0 alternative (taste only): claude.ai React artifact dashboard — Binance API is browser-fetchable (crypto live), Yahoo isn't (manual daily inputs). Fine for a demo; Claude Code is the real build.

## 7. USER ACTION ITEMS
1. **cTrader VERIFY** (rulebook_v1_1.md §7): Swing account type; min lot + lot step per symbol (contract sizes already verified online — confirm); live swap rates vs the §4 band; crypto tradeable on the 100k swing account; daily timer = 00:00 Prague.
2. Confirm base: **0.75%** (default) vs **1.00%** (faster, thinner margin).
3. Decide stack: Claude Code (recommended) vs React artifact (taste).

## 8. BOOTSTRAP PROMPT (paste as the first message of the Option B chat)
> Read `00_MASTER_REFERENCE.md`, `01_OPTION_B_bootstrap.md`, `rulebook_v1_1.md`, `integrity_report.md`, and `config.yaml` in project knowledge — together they are the contract. I'm deploying Option B and building its app. Start by: (1) rebuilding data per master §3 and re-confirming the integrity_report stats so nothing drifted; (2) building the Phase-1 signal engine from `engine.py` (daily Sleeve A/B after NY close, 4H Sleeve C, printing lots from ladder state + half-off/BE/time-exit lines + MCO tags as display-only); (3) then Phase 2 tracker. Hold all change-control and MCO gates exactly as written. My cTrader answers: [Swing Y/N, lot step]. Base: [0.75% / 1.00%]. Stack: [Claude Code / React].
