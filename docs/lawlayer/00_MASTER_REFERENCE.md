# 00 — MASTER REFERENCE (shared across all chats)
*Generated 2026-06-13. This is the shared knowledge base behind three deployable systems. Each system has its own bootstrap file (01 Option B, 02 Hayden, 03 Combo). All four live in this project's knowledge; any new chat in this project can read all of them and can also search past conversations. **Numbers here are reconciled against the committed project files** (`rulebook_v1_1.md`, `ftmo_pass_rulebook.md`, `integrity_report.md`, `config.yaml`, `mco_synthesis.md`) — those files win over older chat summaries wherever they differ.*

---

## 1. THE GOAL
Pass the FTMO $100k 2-Step **Swing** challenge, then trade funded. The work has produced **two independently validated systems** (Hayden Master Book; Option B Comfort Book) and an open question about **combining them**. A second component, **MCO** (More Crypto Online — Elliott Wave levels), is integrated as a **context/display layer only** unless and until a pre-registered study promotes it.

## 2. FTMO RULES (baseline for every campaign sim)
- Phase 1 target **+10%**, Phase 2 target **+5%**.
- Max **daily** loss **−5%** (bucket resets 00:00 Prague = 18:00 ET / 17:00 ET in winter).
- Max **total** loss **−10%** (static, on initial balance).
- Min **4 trading days** per phase. **No time limit.**
- Fee ≈ **$550**, refunded with the first payout of the passing attempt.
- **Swing** account = no news restriction, no weekend-flat requirement (required for crypto holds). **Must be confirmed on the live account before any fee.**
- Verified contract/leverage (ftmo.com symbols API, 2026-06-12; confirm on account): XAUUSD 100 · XAGUSD 5000 · USDJPY 100k (JPY-quote) · US30/GER40/US500/US100 = 1 (GER40 EUR-quote) · BTCUSD 1 · ETHUSD 10 · SOLUSD 100 · XRPUSD 10000. Swing leverage: FX 1:30, metals/indices 1:15, **crypto 1:1**. Residual checks on account: min lot + lot step (assume 0.01; indices may be 0.1), live swap rates.

## 3. DATA REBUILD RECIPE (containers don't persist — regenerate every session)
- **Crypto**: Binance REST klines, **4H**, symbols BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT, 2020-08 → present (~12.8k bars each). 5m also available (floor(t/14400000) to aggregate to 4H; floor to 3600000 for 1H).
- **Cross-class daily**: Yahoo Finance — GC=F→XAUUSD, SI=F→XAGUSD, JPY=X→USDJPY, ^DJI→US30, ^GDAXI→GER40, ^GSPC→US500, ^NDX→US100, from 2014.
- **COT** (research only): CFTC legacy `deacot{YYYY}.zip`, commercial net/OI, 156-week percentile, effective +6 days (Tue data → following Mon). **Metals matching is broken** (GOLD/SILVER pulled an impossible net-long series — wrong contract; FX rows are clean).
- **ATR14** = simple moving average of true range, everywhere.
- Engine reference implementations live in the project: `engine.py` (live signal generator), `bt.py` (backtester with v1.0 conventions), `replay.py` (chronological equity replay), `mco_parse.py` (Discord JSO → `mco_levels.csv`).

## 4. COST & FINANCING MODEL (use for any re-validation)
- Round-trip cost on notional: **non-crypto 0.02% base / 0.05% stress; crypto 0.11% / 0.17%.**
- **Financing convention "variant A"** (the one the original validation used and the documented standard): apply **0.007% per 4H bar to crypto holding bars only**; daily cells charged via the RT cost above, not per-bar financing.
- **Harsh lower bound**: charging daily cells full per-bar financing (6×4H/day) → Option B still **+1.85 R/mo**. System is positive under both interpretations.
- **FTMO-true snapshot** (ftmo.com swaps 2026-06-12: crypto swap ≈ −30%/yr both sides ≈ 0.082%/day; dailies ≈ 0.02%/day; crypto commission 0.065% RT): Option B **+2.11 R/mo**, **+1.89** with the crypto-margin constraint. Swaps float — re-pull monthly.

## 5. THE VALIDATED LAWS (hard-won; do not relitigate without new data + pre-registered gates)
1. **Trade transitions, not states.** Entries fire on state *changes*, not while-in-state.
2. **Death-exit dominates smart exits ~5:1** for the Hayden reversal sleeves (ride to state death / time exit beats every clever TP). Re-bracketing for win rate is a *different objective* (Option B), not an edge improvement.
3. **Adverse selection is real.** Comfortable/deep/predictable limit fills lose; waiting beats anticipating ~2.5×. Deeper fib fills degrade monotonically (0.618→0.5→0.382 WR fell 70→54→44%).
4. **Lower-TF gross edge ≈ 0 before costs** (5m/15m/1H), confirmed ~7 independent ways incl. a second AI's ORB (OOS PF 0.30) and the "BOT GOAT" audit (TV fill-engine inflation + fixed-dollar params riding 2021). The 1H-realign lead turned positive only with time exits but 43–47% WR → parked.
5. **Mechanical shorts are dead** on every asset class and structure tested — raw mirrors, confirmed shorts, COT-gated shorts, and supply-zone shorts (four independent deaths). The lone exception that survives is **SOL Confirmed Short (1C)** inside the Hayden book — fragile, smallest sleeve. Do not improvise new shorts.
6. **Win rate is purchasable; edge is not.** Capping mean-reversion for WR is cheap (~15% of expectancy); capping breakouts is expensive (~50%). Tight TP at crypto costs dies.
7. **HA is structurally required for Engine 1.** On regular candles the confirmation sleeves (1B/1C/1D) produce **zero** signals in 5.8 years, and Flip Rider's holdout flips negative (−0.19 vs HA +0.73). The HA-low stop's *width* (~2× the real-candle low) is load-bearing. Donchian and all of Engine 3 are regular-candle by design.
8. **Barrier geometry is part of the system.** A fixed −5%/−10% (FTMO) vs a 3% EOD + 30% consistency (e.g. The5ers Futures) changes optimal sizing and the whole campaign distribution. Re-run the campaign MC under any new venue's exact rules before switching.

## 6. THE GRAVEYARD (tested, dead — don't rebuild)
- All intraday signal systems (5m/15m/1H ORB, EMA-cross bots): gross edge zero, dies at costs.
- All mechanical short systems except Hayden 1C.
- Fib **retrace trading** (5m deep-zone): failed pre-registered BTC/ETH validation (asymmetry inverted). The fib **confirmation gate** is validated; retrace *trading* is not.
- **Bernd Skorupinski recreation**: COT H1 failed on clean FX (pooled −0.35%, IS/HO sign flip); COT gate does not rescue shorts; supply-zone shorts dead; demand-zone longs weak-positive but N=46/11yr at 30% WR (RR3 arithmetic). Verdict: the *copyable* layer ≈ the already-validated book with worse measured numbers; his edge residue (discretion, selectivity, ~20 parallel accounts, course income) is non-copyable. This is **why Option B exists** — it IS the copyable core, mechanized, with better numbers.
- COT metals cells: quarantined (wrong-contract match). Seasonality + valuation pillars: never tested.

## 7. SEALED INSTRUMENTS — DO NOT TOUCH
**CL=F (crude oil), HG=F (copper)** prices have never been used in this project. They are reserved as untouched out-of-sample validation instruments for any future system. COT for them is already downloaded. Do not backtest on their price series until a system is otherwise final and needs a blind test.

## 8. CHANGE-CONTROL DOCTRINE (applies to all three systems)
No rule, parameter, instrument, or sizing change during a live attempt — ever. New ideas → research → pre-registered gates + untouched validation data → enter a rulebook only as a version increment **between** attempts. **A signal is skipped, never queued.** MCO promotion to a filter requires its §6 study (see Option B bootstrap) to pass first. **One full paper month precedes the first $550 fee — non-negotiable.**

## 9. FILE INVENTORY (project knowledge)
- `ftmo_pass_rulebook.md` — Hayden Master Book, decision-complete v1.0.
- `rulebook_v1_1.md` — Option B (Comfort Book PLUS), decision-complete, supersedes v1.0 for Option B.
- `integrity_report.md` — Option B data rebuild + stats reproduction (PASSED) + funded-ladder verification (PASSED).
- `config.yaml` — live config: sleeves, ladder, caps, verified contract sizes, costs, MCO block.
- `engine.py` / `bt.py` / `replay.py` — live generator / backtester / equity replay.
- `mco_parse.py` → `mco_levels.csv`; `mco_synthesis.md` — MCO 3-horizon synthesis (SOL-only export).
- `mco_terminal_map.md`, `MCO_Terminal_.pdf`, `MCO_Valuation_Screener.pdf` — MCO terminal references.
- `directional_analysis.md/.pdf`, `mco_validation_study.md` — supporting analyses.
- `gate_table.csv`, `ic_table.csv`, `ic_grid_full.csv`, `agreement.csv/agreement_2.csv` — research grids (COT/zones era).
- `fetch_data.py` — data fetch helper.
- Parquet/pickle artifacts referenced by chats: sol/btc/eth/xrp 4h+5m, cot, portfolio (SOL Hayden), trades_long, multi_trades (BTC ConfRider), don_book (DON-55 ×4), xclass_book (Engine 3), comfort_books.pkl, best_cfg.pkl. (Regenerate via the recipe in §3 if absent.)

## 10. THE TWO SYSTEMS AT A GLANCE
| | **Hayden Master Book** | **Option B (Comfort PLUS)** |
|---|---|---|
| Engine | HA 4H reversal (Flip/Confirmed Riders + 1C short) + Donchian | Daily dip-buy + daily breakout + 4H crypto breakout, all half-off-at-+1R |
| Trades/mo | 14.3 | 12.9 |
| Win rate | ~27–45% (sleeve-dependent; 28% headline) | 55.6% |
| R/mo (base) | +8.02 | +2.71 (+2.11 FTMO-true) |
| Campaign (0.75% ladder) | 87% pass, median **4 mo**, 59% ≤4mo, 74% ≤6mo | 91% pass, median **8 mo**, 42% ≤6mo |
| Campaign (1.0% ladder) | — (0.75% is its seat) | 85% pass, median **6 mo**, 55% ≤6mo |
| Personality | Fast, hard to hold (death-exit drawdowns) | Slower, holdable (wins feel like wins) |
| Shared exposure | SOL/BTC (Eng1) + SOL/BTC/ETH/XRP (DON-55) | SOL/BTC/ETH/XRP (DON-55-half) |

**Critical overlap fact for the Combo:** DON-55 on the four cryptos appears in *both* books — Hayden runs it to death/time-exit, Option B runs the half-off variant. Combining is not "add the two campaigns"; it is "merge trade streams, dedupe the shared crypto, pick one exit per shared sleeve, apply one 4% cap, re-sim." See `03_COMBO_bootstrap.md`.
