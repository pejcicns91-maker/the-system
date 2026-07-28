# NEW PROJECT CHARTER — "WHEN TO USE WHICH": TERMINAL + REGIME PROGRAM
*Compilation doc, v0.1 — drop this into the new Claude Project as its founding file. The Daily Pack (brief_engine_v4 + RUN_BRIEF + brief_state.zip) keeps running unchanged in parallel; nothing here touches the daily loop until it earns its way in.*

## MISSION
Build an EdgeFinder-class terminal on validated foundations, and answer the question the whole industry hand-waves: **which strategy works in which market state, and what tells us we're in that state.** Every data family is a screener (opportunities & warnings) until tested; weight is earned through the standard pipeline (pre-registration → placebo → walk-forward → FDR), never assumed.

## STANDING PRINCIPLES (inherited, non-negotiable)
1. Evidence sets weight. Untested = display-only, labeled.
2. Pre-register before measuring. Regime variables specified BEFORE any strategy×regime split is viewed.
3. Placebos + FDR always; walk-forward OOS; FTMO-true costs where trades are implied.
4. Expect nulls. Benchmark of a real winner: π-Cross (+0.245R vs −0.562R, t=4.58). One of those pays for fifty nulls.
5. "Why" is claimed only when a conditioner predicts the failure AND carries a causal story; otherwise the claim stays "when."

## WORKSTREAM 1 — NEW DATA FAMILIES (screener role first, tested second)
| family | source (free) | status |
|---|---|---|
| COT institutional positioning | CFTC weekly public reports (CSV) | first in line — fetch + history build, then registration |
| Retail sentiment | Myfxbook/FXSSI-class free pages | source survey needed; "free but scrappy" |
| Macro panel (GDP/CPI/jobs/rates, G7) | FF actuals forward; history needs one phone-assist (FRED/BLS pages) | forward wired via FF feed; history pending |
| Seasonality | computed from data already held | trivial; needs registration before display-with-implication |
| Put/Call | CBOE free daily | later |
| MCO terminal (56 tools) | already catalogued; 1 certified (π-Cross), rest untested | candidate regime variables, screenshots for access |

## WORKSTREAM 2 — THE REGIME LIBRARY (pre-specified conditioners)
Candidate state variables, to be frozen in the first pre-registration: π-Cross (certified), vol regime (rv14/rv90 bands), trend regime (Donchian position / MA structure), COT positioning extremes, retail-sentiment extremes, risk-on/off composite, carry state, macro-surprise state (FF actual vs forecast), terminal-agreement score. Rule: the library is short and frozen per round; no post-hoc additions inside a round.

## WORKSTREAM 3 — THE META-STUDY: STRATEGY × REGIME
- Subjects: Option B sleeves (FADE, DON-20, DON-55), the validated direction cells (A6b family, E6c, ETH open-state, JPY don20-top), AND the null archive (~140 cells with full histories — condition the failures, not just the winners: when did E6c decay, when does A6b weaken).
- Design: per (strategy, regime-variable) cell — bucket performance by state, Welch + bootstrap + halves + FDR, walk-forward, registered directions where priors exist. Conditional bucket tables with CIs over regression (sample-size honesty); regime DURATION stats included (run lengths, survival-by-age) so scenarios read "trend, day 6 of median 9," not just "trend."
- **PILOT CASE (registered hypothesis on record 2026-07-02, stated before any data was viewed): Hayden MTF-RSI performance conditioned on trend/chop regime. Svet's mechanism claim: positive expectancy concentrates in trending regimes, dies in chop. Primary conditioner: Kaufman efficiency ratio (frozen definition at registration); alternates: Donchian width, MA-slope agreement; secondary conditioners: MCO fear & greed (alternative.me, free full history), MCO time cycles (ONLY with an exact frozen output definition — cycle tools are overfitting machines otherwise). If the split lands as predicted → forward claim registered: "Hayden enabled only when ER > threshold," graded live like π-Cross.**
- Output: the earned "when to use which" table → feeds the terminal's opportunities/warnings screens and, only where validated, strategy on/off switches.

## WORKSTREAM 4 — TERMINAL SURFACES
- Phase A: COT + FF-actuals as display sections inside the daily brief (terminal-lite; no new app).
- Phase B: the visual terminal — treemap/heatmap app with tested/untested tags, armed/fired/near warnings across all Option B components. (BENCHED until A+B research defines contents. Tiers already scoped: Claude artifact = paste-driven; standalone HTML = live crypto confirmed via Binance CORS; non-crypto live needs free API key — under consideration.)
- AI layer: daily Claude read (Track B measuring it), on-demand "why is X moving" queries against terminal data.

## CARRY-OVER LEDGER (from the current project — still owed)
- MT5 export (Svet): GER40 + XAU/XAG history on the FTMO feed → unlocks GER40 brief + Option B metals re-basing.
- CPI/NFP historical dates (Svet, one paste: bls.gov/schedule/news_release/cpi.htm + /empsit.htm) → unparks the calendar cells → only path to news weight.
- Metals band recalibration (research, no inputs needed).
- Pine C-Bridge fix (parked; paste the compile error when wanted).
- Queued registrations: BTC follow-overnight-while-open; FADE-pos-open revisit as frames grow; JPY pre-FOMC inverse; non-crypto A6b redesign; A8c long-history replication.
- Running clocks: Track B (verdict n=60, futility n=30), I-1 forward gate (30 firings), forward log accumulating daily.

## DECISIONS OPEN
1. Confirm COT as first new family.
2. Nominate/veto regime-library candidates before the first meta-study registration.
3. App tier + free API key: still benched by Svet.
