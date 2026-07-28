# FTMO PASS CAMPAIGN — RULEBOOK v1.0
**Account:** FTMO $100k, 2-Step, **Swing** type (mandatory — weekend crypto holds + news holds)
**Challenge sizing:** 0.75% laddered · **Funded sizing:** 0.50% constant
**Campaign expectation (Monte Carlo, month-block):** 87% of attempts pass both phases · median 4 months to funded · P(≤4 mo) 59% · P(≤6 mo) 74% · expected burned fees ≈ $90 (fee refunded with first payout of the passing attempt)

Nothing in this document is optional. Every situation is pre-decided. If a situation arises that this document does not cover: take no action, flatten nothing, and resolve it before the next signal — then add the case under Change Control.

---

## 1. PLATFORM SETUP (one-time, before first attempt)

1. Confirm account type = **Swing** (no weekend/news restrictions).
2. In cTrader, open Symbol Info and record **contract size, min volume, volume step** for every instrument below. Do not trade an instrument until its contract size is recorded.
3. Instrument map (backtest proxy → FTMO symbol):

| Book name | FTMO symbol (verify) | Engine |
|---|---|---|
| SOL | SOLUSD | 1, 2 |
| BTC | BTCUSD | 1, 2 |
| ETH | ETHUSD | 2 |
| XRP | XRPUSD | 2 |
| Gold (GC=F) | XAUUSD | 3 (both cells) |
| Silver (SI=F) | XAGUSD | 3 (DON-20) |
| S&P 500 (^GSPC) | US500 | 3 (both cells) |
| Nasdaq 100 (^NDX) | US100 | 3 (both cells) |
| Dow (^DJI) | US30 | 3 (FADE-K5) |
| DAX (^GDAXI) | GER40 | 3 (FADE-K5) |
| USDJPY (JPY=X) | USDJPY | 3 (FADE-K5) |

4. Charts: crypto 4H bars on **UTC boundaries** (00/04/08/12/16/20). Daily cells evaluated on completed daily candles at **17:00 ET**.
5. TradingView alert layer installed (separate deliverable) for all 4H signals; daily cells are a manual 17:00 ET checklist.

---

## 2. SIZING ENGINE

**Risk unit (challenge):** ladder on *phase equity* (current equity ÷ phase starting balance − 1, including floating PnL):
- Phase equity ≥ −3% → risk **0.75%** of phase starting balance per trade
- −3% > phase equity ≥ −6% → risk **0.50%**
- Phase equity < −6% → risk **0.25%**

**Risk unit (funded):** **0.50%** constant. Everything else identical.

**Lot calculation:** `lots = RiskUSD ÷ (stop distance in price × contract size)`, rounded **down** to the volume step.
*Example (SOL):* $100k account, full ladder → Risk $750. Entry $150.00, stop $145.35 → distance $4.65. Contract 100 SOL → 750 ÷ (4.65 × 100) = 1.61 → **1.61 lots**.

**Aggregate open-risk cap: 4.0%.** Sum of initial risk of all open positions. A new signal that would push the total above 4.0% is **skipped permanently** (never queued, never entered late).

**Cap priority** when simultaneous signals compete for remaining budget (same bar close):
BTC ConfRider → SOL ConfRider → SOL FlipRider → SOL ConfShort → DON-20 daily → DON-55 crypto → FADE-K5.

**Daily circuit breaker:** if realized losses since the last 18:00 ET reset reach **3.0%**, no new entries until the next 18:00 ET reset (FTMO's daily bucket resets 00:00 Prague = 18:00 ET). Open positions and their stops are untouched.

**Stops:** hard stop order placed in platform at entry, at the computed level, every trade, no exceptions. Stops are **never widened**. Time/state exits are market orders at the triggering close.

---

## 3. ENGINE 1 — CRYPTO 4H REVERSAL (4 sleeves)

**Shared machinery (computed on 4H bars):**
- Heikin-Ashi: haClose = (O+H+L+C)/4; haOpen = (prior haOpen + prior haClose)/2; haHigh = max(H, haOpen, haClose); haLow = min(L, haOpen, haClose).
- RSI(14), Wilder smoothing, computed on **haClose**.
- States: cross above 67 → **BULL**. Cross below 33 → **BEAR**. In BULL, cross below 39 → CHOP. In BEAR, cross above 61 → CHOP.
- *Flip* = any 4H close that transitions the state into BULL (or BEAR for shorts).
- *Reversal flip* = flip where the last non-chop state was the opposite trend (bear→bull, or chop→bull with last non-chop = bear; mirror for shorts).

### Sleeve 1A — SOL Flip Rider (long)
- **Signal:** 4H close flips state to BULL. FR = flip bar's real High − Low.
- **Entry:** limit order at `flipClose − 0.25 × FR`, valid 12 hours from flip close. Unfilled after 12h → cancel, no trade.
- **Skip rule:** if state has already left BULL by the time of fill, the trade is invalid (in practice: cancel the limit the moment a 4H close exits BULL).
- **Stop:** `flip bar haLow − 0.05 × FR`.
- **Exit:** stop, or market at the **first 4H close with state ≠ BULL**.

### Sleeve 1B — SOL Confirmed Rider (long)
- **Setup:** a *reversal flip* to BULL on bar F.
- **Wick rule:** bars F, F+1, F+2 each have lower HA wick ≤ 1% of HA body (|haClose−haOpen|). All three must pass.
- **Duration rule:** 10 consecutive 4H bars starting at F remain in BULL with **no haLow below bar F's haLow**.
- **Confirm:** the bar where both rules are complete (typically F+9). One confirmation max per flip.
- **Entry:** market at confirm bar close.
- **Stop:** `bar F haLow − 0.05 × leg`, leg = (highest haHigh from F through confirm bar) − bar F haLow.
- **Exit:** stop, or market at first 4H close with state ≠ BULL.

### Sleeve 1C — SOL Confirmed Short
Exact mirror of 1B (upper wicks, haHigh anchor, state BEAR, exit on state ≠ BEAR).

### Sleeve 1D — BTC Confirmed Rider (long)
Identical rules to 1B, on BTC.

*Note: 1A/1B can be open simultaneously (same state). 1C cannot coexist with 1A/1B by construction (opposite states).*

---

## 4. ENGINE 2 — CRYPTO 4H BREAKOUT (DON-55)

**Instruments:** SOL, BTC, ETH, XRP. One position per asset; no re-entry while open.
- **Signal:** 4H close > highest **high** of the prior 55 4H bars (excluding the signal bar).
- **Entry:** market at signal close.
- **Stop:** entry − 2 × ATR(14) (ATR = 14-bar simple average of true range, 4H).
- **Exit:** stop, or market at the close of the **48th bar after entry** (8 days), whichever first.
- After exit, the next qualifying close starts a new trade.

---

## 5. ENGINE 3 — CROSS-CLASS DAILY (2 cells)

Evaluated once daily at **17:00 ET** on completed daily candles. One position per cell per instrument; both cells may hold the same instrument concurrently (cap governs).

### Cell A — FADE-K5 (dip-buy, long only)
**Instruments:** XAUUSD, US500, US100, US30, GER40, USDJPY.
- **Signal:** `close / close[5 days ago] − 1 < −1.0 × (ATR14/close) × √5` (daily ATR).
- **Entry:** market at daily close. **Stop:** entry − 2 × ATR(14, daily).
- **Exit:** stop; **gap rule** — if a day opens beyond the stop, exit at the open; otherwise market at the close of the **10th day** after entry.

### Cell B — DON-20 (breakout, long only)
**Instruments:** XAUUSD, XAGUSD, US500, US100.
- **Signal:** daily close > highest high of the prior 20 days.
- **Entry/Stop:** as Cell A. **Exit:** stop, gap rule, or close of the **40th day**.

---

## 6. DAILY OPERATING ROUTINE (~10–15 min/day)

1. **4H alerts (push, 24/7):** on alert, verify the signal on chart, compute lots, place order + stop. Flip Rider limits get a 12h expiry.
2. **17:00 ET:** run the Engine-3 checklist (11 instruments, 2 conditions each), place any entries + stops, execute any due time-exits.
3. **State-death exits:** when a 4H close exits the state for an open Engine-1 position, close at market within 30 minutes.
4. **18:00 ET:** daily reset — circuit breaker clears, log the day (trades, equity, phase equity, ladder tier).
5. **Weekends:** crypto engines run normally (Swing account). Daily cells: no bars, no actions.

---

## 7. EDGE CASES — ALL PRE-DECIDED

1. **Signal seen late:** 4H signals — if the next 4H bar has already closed, skip (exception: Flip Rider limit may still be placed within its 12h validity). Daily signals — enter within 4h of the 17:00 ET evaluation or skip.
2. **At the 4% cap:** skip the new signal permanently. Never trim an open position to make room.
3. **Two Engine-1 longs + cap:** allowed; they are separate trades with separate stops.
4. **Gap through a stop (crypto/indices open):** exit at first available price. Accept it. Never average down.
5. **Stop and exit-condition same bar:** stop takes priority (assume the worse fill).
6. **Platform outage / data gap:** no new entries that bar/day; existing stops remain in platform (this is why stops are always resting orders).
7. **Near phase target (e.g., +9.5%):** no behavior change. Same size, same rules, until the platform confirms the phase is passed.
8. **Phase passed mid-position:** positions carry into Verification only if FTMO transfers them; otherwise they are closed by FTMO — either way, take no manual action.
9. **Min 4 trading days:** satisfied naturally (~14 trades/mo). Never manufacture a trade for it.
10. **News (CPI/FOMC):** Swing account — hold through, no exceptions, no pre-news flattening.
11. **DST weeks:** the 17:00 ET evaluation time governs; crypto UTC boundaries are unaffected.
12. **Missed time-exit:** execute at market immediately upon noticing.

---

## 8. ATTEMPT & CAMPAIGN PROTOCOL

1. **Identical sizing every attempt.** A blown attempt changes nothing about the next one. No revenge sizing, no "safer" sizing.
2. **On breach:** stop, log the attempt (entry-by-entry), purchase the next challenge within 7 days, resume.
3. **Campaign budget:** 3 fees (~$1,650) pre-committed. Expected spend ≈ $90; the budget exists so a tail outcome doesn't end the campaign emotionally.
4. **Definition of success:** flawless execution of this document. Pass timing is a distribution (59% ≤4 mo, 74% ≤6 mo); execution is a choice.
5. **On passing Phase 2:** switch to funded mode (0.50% constant) **before** the first funded trade. Request payouts early and often — the fee refund arrives with the first one.

---

## 9. STATS SHEET (verified backtest, 0.20% RT crypto / 0.02–0.05% RT non-crypto, conservative)

| Sleeve | N | meanR | Notes |
|---|---|---|---|
| SOL Flip Rider | 82 | +1.17 | win 28%, median stop 3.1%, max +46R |
| SOL ConfRider | 33 | +1.35 | the 2022 earner |
| SOL ConfShort | 21 | +0.47 | fragile; smallest sleeve |
| BTC ConfRider | 28 | +2.28 | blind OOS survivor |
| DON-55: SOL/BTC/ETH/XRP | 114/118/119/105 | +0.53/+0.51/+0.35/+0.35 | XRP validated untouched |
| DON-20: XAU/XAG/US500/US100 | 53/57/54/56 | +0.90/+0.59/+0.67/+0.61 | reserve-validated |
| FADE-K5: XAU/JPY/US30/GER40/US500/US100 | 96/53/88/87/89/84 | +0.16/+0.16/+0.13/+0.12/+0.30/+0.26 | reserve-validated |

**Master book:** 984 trades, 14.3/mo, **+8.02 R/mo**, per-year R: 2020 +97, 2021 +90, **2022 −28**, 2023 +173, 2024 +123, 2025 +94, 2026 +5 (YTD).

---

## 10. KNOWN FAILURE MODES & CAVEATS

- **The 2022 mode:** when all asset classes fall together, an all-long book bleeds (−28R year in the data). The ladder + restart protocol is the designed answer. Shorts tested dead everywhere; do not improvise them.
- **MC optimism:** cap-skips aren't modeled; real numbers sit somewhat below the menu. The Donchian sleeves win ~32% — losing streaks of 8–12 are normal and expected.
- **Data proxies:** non-crypto cells were built on Yahoo daily (futures/cash proxies) at padded costs; crypto on Binance vs FTMO CFD. The FX leg (USDJPY) is the weakest-validated — if any cell is ever cut for live divergence, it's that one first.
- **Execution drift:** entries are modeled at bar closes. Fill within 30 min of the triggering close; beyond that, see Edge Case 1.

---

## 11. CHANGE CONTROL

No parameter, instrument, or rule changes during a live attempt — ever. New ideas go to research, get pre-registered gates and untouched validation data, and enter this document only as a version increment between attempts. The system's edge includes its stability.

*v1.0 — locked at 0.75% ladder.*
