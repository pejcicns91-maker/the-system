# INDTEST-RSIDIV — Pre-registration (2026-07-21)
**Subject:** "RSI Divergence Entry Engine [trade_w_samet]" Pine v6 script, as pasted by Svet 2026-07-21. Question: does it have accuracy/edge on 1h?

**Standing prior (declared before data):** Master-Reference Validated Law 4 — lower-TF (5m/15m/1H) gross edge ≈ 0, confirmed ~7 independent ways. This study is a permitted relitigation only because it is new logic + pre-registered gates. Prior probability of pass: low. Prior failures are priors, not exclusions.

## Mode
DISCOVERY. Event-study accuracy + exact trade-engine replica. The money layer is reported as discovery P&L only — NOT a sealed money claim. If (and only if) any cell passes FDR here, the next gate is a sealed split confirmation per the two-claim sealing rule, then the v1.2 promotion chain. Nothing here touches Option B.

## What data it sees
Binance spot 1h klines, FULL listing history → 2026-07-21, BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT, weekends included (24/7). UTC bars; ET used for weekday/weekend tags (project day convention). Endpoint fallback chain per M9b practice. This is a fresh full fetch (research-side), not the S1 daily cache.

## Regime columns emitted (rule 2/3 compliance)
Every statistic ships full-history headline PLUS: per-asset · per-year · weekday/weekend (ET) · Hayden-4H state (Bull/Bear/Chop/None) joined from hayden_state_{COIN}.csv by 4h-floor timestamp; bars outside Hayden coverage tagged UNTAGGED. Instability across splits → REGIME MARKER (promoted as conditional), not failure — provided the cell is alive at all under FDR.

## Arms (both under one FDR family)
- **ARM-A (as shipped):** lbL=47, lbR=1, RSI 14 close, range gate barssince(found[1]) ∈ [5,60], regular bull+bear only (hidden OFF by default), trend filter OFF, ATR14 (RMA), SL = 2.0×ATR, TP3 = 6R, TP3-only wins, SL-priority on same-bar double-touch, entry at signal-bar close, exits checked from next bar, one trade at a time, no same-bar re-entry.
- **ARM-B (tooltip-standard):** identical except lbL=5, lbR=5.
Pine semantics replicated exactly: strict pivots, valuewhen(…,1) previous-pivot logic incl. the [1]-shift on the range gate, mutual-exclusion of simultaneous buy/sell.

## Endpoints
1. **Accuracy (primary):** signal-level directional hit rate of close-to-close forward return at h = 24 bars (primary), h ∈ {4,12,48} secondary. All confirmed signals counted (no one-trade suppression).
2. **Money (discovery):** engine-replica win rate vs 14.29% breakeven (6R:1R), net R, PF, avg R/trade; plus per-signal 6R-vs-1R race ignoring the queue (secondary).

## Nulls / baselines
- Hit rates: exact binomial vs the asset's own full-history base rate at that horizon (bear side vs down-rate). Overlapping-horizon dependence noted as a caveat; it inflates significance, so it cannot rescue a null.
- Engine: 100 matched sims — same entry count, uniform random bars, same one-at-a-time queue and 2×ATR/6R geometry — empirical percentile of actual net R.

## Multiplicity
BH-FDR q=0.10 over the family: {4 assets} × {bull, bear} × {ARM-A, ARM-B} on the h=24 accuracy test, plus {4 assets} × {2 arms} engine-vs-placebo = 40 cells. Sample floor ≥40 events per cell for a gated verdict; below → UNDERPOWERED (re-queued, never killed).

## Deviations
Any deviation from this file is reported, never promoted. Timeout (unresolved race at data end / >5000-bar scan) reported as OPEN, excluded from WR, count disclosed.
