# MAP V3 — P4 FORECAST LAYER (2026-07-23) · all numbers scored on held-out future days
Model: gradient boosting on the FULL state (every feature, certified or not — per the P4 commitment), trained on each coin's first 80% of days, scored on the last 20% (a scoring split, not a money seal). Artifact: p4_scores.json sha `99a0b7d0…` · rerun `python3 p4.py`, seed 20260723.

## The four forecasters (Brier skill vs naive base rate; calibration = predicted → realized)
1. **Hold-at-contact — the map forecasts.** Base 50.0% (a coin flip). Model Brier 0.159 vs 0.250 → **skill +0.363, AUC 0.845**, n_test 10,708. Calibration: when it says 10% it happens 8%; says 31% → 27%; says 67% → 70%; **says 95% → 96.5%**. The zone question stops being a coin flip when the state is read.
2. **Reach-the-next-zone given a break.** Base 12%. Skill +0.114, AUC 0.733, calibrated through the top decile (36% predicted → 34% realized), n 7,905. Travel is partly readable at break time.
3. **Break-AND-reach straight from contact (the chained "will it get to zone 4 from here").** Base 5.8%. Skill +0.074, AUC 0.785; top decile 24% predicted → 19% realized (slightly hot, said). The chain forecasts, modestly.
4. **False-break within 30 min.** Base 61.2%. **Skill +0.034, AUC 0.599** — barely above the base rate. Reading: WHETHER a break comes back is close to unforecastable from this state; the 60% base itself is the tradeable-shaped fact, not its conditioning.

## Leak caught (deviation, disclosed — third of its class, the guard works)
First fb run scored AUC 1.0: `bars_beyond` was in the feature set and mechanically encodes the outcome (≤6 bars beyond ≡ false break). Removed; honest run above. depthU is retained only where it is known at forecast time (at-break models).

## What the layer now supports (readings, no verdicts)
A live approach can be scored in real time: P(hold) calibrated to ±3pp across the whole range; if break, P(return) ≈ the sticky 60% with little refinement; P(travel to next) low and partly readable. Composed: the "three branches per zone" of the daily cards can carry measured, calibrated numbers instead of composed ones — pending P5 packaging and, for any money use, a sealed spec of its own.

## SCOPE LEDGER
**EXAMINED:** four scored forecasters on full state · time-forward scoring · calibration tables · leak audit.
**REMAINING:** daytype/yd_arch/lean columns still 'na' (their absence caps skill; engine-port pending) · UNDERPOWERED T2 queue · P5 synthesis (MAP_V3.md + wiring calibrated numbers into the daily card pipeline as readings) · any money spec (leaves v3, own prereg, sealed).
**DROPPED:** nothing. **Assumption flags:** model family & fixed hyperparameters (declared, untuned); split ratio 80/20 (declared).
