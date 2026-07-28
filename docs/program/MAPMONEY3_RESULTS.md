# MAPMONEY-3 — RESULTS (2026-07-23) · VERDICT: money gate FAIL — but first ALIVE gross signal in the family
Prereg: MAPMONEY3_prereg.md. Contract items in order. **Includes the MAPMONEY-1b AMENDMENT (§A).**

## 1. Prereg vs ran — DEVIATIONS (one, material, disclosed)
**Bug found mid-run and fixed:** target selection could pick a wall sitting between the broken edge and the entry (behind the entry) → thousands of instant negative "TP" exits. First MAPMONEY-3 pass and the ORIGINAL MAPMONEY-1b run were both affected; both were rerun with the target constrained strictly beyond the ENTRY level (spec-intent clarification, logged). All numbers below are from the fixed engines. Nothing else deviates. DROPPED: nothing.

## 2. Artifacts (rerun: `python3 mm3.py && python3 analyze_c.py`, seed 20260723)
mm3_trades.csv — 13,946 rows, sha256 `9ed25569d2f759be…` · mm3_results.json · mm1b_trades.csv (fixed) — 4,492 rows `b427f83c61535aa3…` · same data hashes as MAPMONEY-1.

## 3–4. Headline (FULL history) with n and opponents
13,946 trades · WR 61.6% · **frictionless mean R +0.023 — the first gross-positive number in the wall-money family** · FTMO −0.039/trade (avg cost ≈ 0.062R), net −542R. Exits: 5,747 TP · 3,109 stop · 5,090 time. Same-bar break→retest entries: 17.5% (the "instant retest" share — most entries are genuine pullbacks).
**Sealed vs placebo (100 sims, FTMO):** actual ABOVE placebo median in 6/8 cells; FDR-significant OUTPERFORMANCE in **XRP-S (p=.0099, pct 1.00, sealed net +8.1R after FTMO costs, n=549)** and **BTC-S (p=.0299, pct .99)**. No cell significantly worse than random — first time in the family.

## 5. Spot-checks (UTC, verify on chart)
- LOSS: ETH long 2025-04-10 12:05 entry 1596.63 → stopped 15:15 at 1541.65, R −1.0
- WIN: ETH short 2019-12-18 13:30 entry 120.945 → TP 120.61 same bar, R +0.14
- (1a/1b spot-checks stand for the shared wall series.)

## 6. Decomposition — stable, no dead pocket
Gross (P0) mean R by year: negative only 2017 (−0.051); positive or flat every year 2018–2026 (+0.003…+0.052). DISC +0.019 / **SEAL +0.032** — improves out of sample. Hayden: Bull +0.028 / Bear +0.023 / Chop +0.010. Contact ≥50 best (+0.031, n 8,648) — **strong walls retest best**, consistent with the map. Sides: L +0.027 / S +0.017 gross, but the SHORT side carries the placebo outperformance. FTMO: −0.031…−0.053 everywhere — the cost line is the sole killer.

## 7. Money-claim stamp
Break→retest @B, stop at edge, next-wall target: **DISCOVERY FAIL and SEALED FAIL on the registered FTMO gate (net negative). Status: NOT tradeable as specced. DISCOVERY-grade structural finding: gross-positive, sealed-stable, placebo-beating (short side FDR-pass).** The words "validated/edge" do not apply.

## 8. Synthesis across the family (n≈38,000)
Fade −0.009 gross → chase −0.099 gross → **retest +0.023 gross.** Entry price was the whole game, exactly as the 1/1b synthesis predicted: the retest recovers ~0.12R/trade over the chase and crosses zero. What still fails is a 13.5bp cost on a 0.6U-risk unit. The motivated next specs (each needs its own prereg): wider R (deeper retest band → cost shrinks in R), short-side-only with the day-type/EXPANSION gate, or maker-fee execution. None inherit anything from today.

## 9. Downgrades
None beyond the disclosed rerun — all items produced.

---
## §A — MAPMONEY-1b AMENDMENT (supersedes MAPMONEY1b_RESULTS.md numbers)
Fixed engine: 4,492 trades · WR 48.7% · gross −0.099 · FTMO −0.159 · worse-than-random in 5/8 sealed cells · uniform across segments (DISC −0.161 / SEAL −0.155). **Verdict unchanged: KILLED.** The original file's exact figures (WR 37.4%, −0.143 gross) were bug-inflated and are void; the kill stands on the corrected numbers.
