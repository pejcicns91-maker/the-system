# 02 — HAYDEN MASTER BOOK — CHAT BOOTSTRAP
*Read with `00_MASTER_REFERENCE.md`. The full operating contract is `ftmo_pass_rulebook.md` (v1.0). This file is the starter + the one open task + bootstrap prompt. **This is the speed seat: +8 R/mo, median 4 months — at a ~28% headline win rate you must be able to hold.***

---

## 1. WHAT THE MASTER BOOK IS (one paragraph)
The highest-expectancy system in the project: a Heikin-Ashi 4H **reversal** engine (Flip Rider + Confirmed Riders + one surviving short) plus **Donchian breakouts** on crypto and a cross-class daily layer. **984 trades, 14.3/mo, +8.02 R/mo**, positive every year except 2022 (−28R). Campaign at 0.75% ladder: **87% pass, median 4 months, 59% ≤4mo, 74% ≤6mo.** Its cost is psychological: the reversal sleeves win ~28% and live on a few +10R to +46R riders — losing streaks of 8–12 are normal. If you can execute through that mechanically, it is the fastest route.

## 2. ENGINE 1 — CRYPTO 4H REVERSAL (HA REQUIRED — see master §5 law 7)
**Shared machinery on 4H bars:** Heikin-Ashi (haClose=(O+H+L+C)/4; haOpen=avg of prior haOpen/haClose; haHigh/Low = max/min of H/L with haOpen/haClose). **RSI(14) Wilder on haClose.** States: cross >67 → BULL; cross <33 → BEAR; in BULL cross <39 → CHOP; in BEAR cross >61 → CHOP. *Flip* = close transitioning into BULL (mirror BEAR). *Reversal flip* = flip whose last non-chop state was the opposite trend.
- **1A SOL Flip Rider (long):** signal = 4H close flips to BULL; FR = flip bar real High−Low. Entry = **limit at flipClose − 0.25×FR, valid 12h**; cancel if state leaves BULL. Stop = **flip-bar haLow − 0.05×FR**. Exit = stop, or first 4H close with state ≠ BULL.
- **1B SOL Confirmed Rider (long):** on a *reversal flip* at bar F: bars F,F+1,F+2 each have lower HA wick ≤1% of HA body **and** 10 consecutive bars from F stay BULL with no haLow below F's haLow. Confirm bar (≈F+9) → market entry. Stop = F haLow − 0.05×leg (leg = max haHigh F→confirm − F haLow). Exit = stop or state ≠ BULL.
- **1C SOL Confirmed Short:** exact mirror of 1B (upper wicks, haHigh anchor, BEAR, exit on state ≠ BEAR). **The only surviving mechanical short in the project — fragile, smallest sleeve.**
- **1D BTC Confirmed Rider (long):** 1B rules on BTC. (Blind OOS survivor.)
1A/1B can coexist; 1C cannot coexist with 1A/1B by construction.

## 3. ENGINE 2 — CRYPTO 4H BREAKOUT (DON-55, full exit)
SOL/BTC/ETH/XRP, one position/asset. Signal = 4H close > prior-55-bar high (excl. signal bar). Market entry. Stop = entry − 2×ATR(14,4H). Exit = stop or **close of the 48th bar** after entry. (Note: Option B uses the *half-off* variant of this same sleeve — see Combo file for the overlap.)

## 4. ENGINE 3 — CROSS-CLASS DAILY (full exit; long only)
Evaluated on completed daily candles at the ET close.
- **FADE-K5:** XAUUSD, US500, US100, US30, GER40, USDJPY. Signal = `close/close[5] − 1 < −1.0 × (ATR14/close) × √5`. Entry at close, stop entry − 2×ATR14, exit = stop / gap rule / **10th-day** time exit.
- **DON-20:** XAUUSD, XAGUSD, US500, US100. Signal = close > prior-20-day high. Entry/stop as above, exit = stop / gap / **40th-day**.

## 5. SIZING & PROTOCOL (ftmo_pass_rulebook.md §2/§7/§8)
Ladder on phase equity: ≥−3% → **0.75%**; −3..−6% → **0.50%**; <−6% → **0.25%**. Funded = **0.50% constant** *per v1.0* — **but see the warning in §6 below.** `lots = RiskUSD ÷ (stop distance × contract size)`, rounded down. **Aggregate cap 4%** (skip, never trim). **Cap priority:** BTC ConfRider → SOL ConfRider → SOL FlipRider → SOL ConfShort → DON-20 → DON-55 → FADE-K5. **Daily circuit breaker 3%.** Stops are resting platform orders, never widened. Identical sizing every attempt; on breach, log entry-by-entry, re-buy within 7 days, resume.

## 6. TWO OPEN TASKS BEFORE THIS BOOK IS FULLY TRUSTWORTHY
1. **Stats reproduction is OWED.** The integrity rebuild (`integrity_report.md`) was run for **Option B only**. The Master Book's +8.02 R/mo and per-year figures come from the original backtest, not a fresh rebuild. Option B's numbers shifted on rebuild (+2.52 → +2.71); the Master Book's may shift too. **First task: rebuild data per master §3 and reproduce §1 + the §9 stats table of the v1.0 rulebook before trusting the campaign numbers.**
2. **Funded sizing needs the same treatment Option B got.** v1.0 specifies **constant 0.50%** funded — but Option B's verification proved a *constant* 0.50% **breached** the 2022 replay (−12.5%) while a *laddered* 0.50% survived (−8.5%). The Master Book is more volatile than Option B, so constant funded sizing is **suspect**. **Re-run the 2022 chronological equity replay (`replay.py`) for the Master Book at constant 0.50% AND a laddered alternative; pick the survivor before going funded.**

## 7. PERSONALITY CHECK (the reason Option B exists)
The reversal sleeves are death-exit systems: ~28% WR, equity in the tail. Per-year R: 2020 +97 · 2021 +90 · **2022 −28** · 2023 +173 · 2024 +123 · 2025 +94 · 2026 +5. If a 9-loss streak would make you change the rules, this is the wrong seat — run Option B. The validated **SOL 0.618→1.272 flip-candle bracket** (70% WR on SOL, BTC/ETH validation never run) is the bridge: a Hayden-signal sleeve with comfort-book win rate. Validating it on BTC/ETH is a good optional task here.

## 8. INDICATOR
A Pine v6 indicator "SOL 4H — Flip Book + DON-55" was delivered earlier in chat (state machine + sleeves 1A/1B/1C + DON-55 + status table + 10 alertconditions, Once-Per-Bar-Close). Known cosmetic diff: stop-touch markers render at 4H granularity vs the 5m backtest. Re-paste from chat history if needed; a comfort-book alert layer was never built.

## 9. BOOTSTRAP PROMPT (paste as the first message of the Hayden chat)
> Read `00_MASTER_REFERENCE.md`, `02_HAYDEN_bootstrap.md`, and `ftmo_pass_rulebook.md` in project knowledge — together they are the contract. I'm evaluating the Hayden Master Book as my deploy. **Do the two open tasks first:** (1) rebuild data per master §3 and reproduce the v1.0 §1/§9 stats so I know the +8 R/mo and per-year figures survive a fresh rebuild; (2) run the 2022 chronological equity replay at constant 0.50% vs a laddered funded alternative and tell me which survives the −10% line. Engine 1 MUST use Heikin-Ashi (regular candles produce zero confirmations — master law 7). Then summarize the honest campaign distribution and whether the 28%-WR drawdown profile is something I should deploy vs Option B. Optional: validate the SOL 0.618→1.272 flip-candle bracket on BTC/ETH.
