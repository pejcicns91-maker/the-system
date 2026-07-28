# C4 — ZONE-TO-ZONE LEGS: THE TRAVEL GEOMETRY (2026-07-08)
*Mode MAP · every departure from every zone, full history, weekends in · K=6 (30min-clear) legs headline, K=1 beside · files: c4_legs.csv (214,685 legs at K=6). (b) line as declared pre-run; one design flaw found and flagged below, not hidden.*

## THE CENSUS
After leaving a zone: **76.0% reach the next zone in that direction · 19.4% turn back and re-touch the origin · 4.6% end the window in between.** Invariance is striking: era 76.0/75.9 · weekday/weekend 75.8/76.4 · assets 75.6–76.3. (K=1 grain: 57.6/39.5 — graze-exits return more, as expected.)

## COMPLETION IS A CLEAN FUNCTION OF GAP (the playbook curve)
| edge-to-edge gap | reach next zone | turn back | median time |
|---|---|---|---|
| ≤0.07U | 95–97% | ~1% | 1 bar |
| 0.11U | 91% | 7% | 1 |
| 0.16U | 83% | 15% | 3 |
| 0.23U | 70% | 27% | 6 |
| 0.36U | 53% | 42% | 9 |
| 0.87U | **22%** | 63% | 17 |
Failed legs die earlier the longer the crossing (incompletes-only): near legs that fail reach 73% of the way, mid 51%, far **25%**. Live use is direct: **your target's odds are its distance** — a next zone 0.15U away is nearly free (83–91%); one 0.9U away completes 1-in-4 and the origin re-touch (63%) is the better bet.

## DESTINATION PULL — RESOLVED: NULL (the check's fix)
Matched natural experiment, distance held fixed: P(price travels ≥0.4U in the leg direction) when a real zone sits at ~0.4U = **53.5%** vs when that space is empty = **55.3%** (n=24.5k/17.5k; per-asset ~0, mixed signs). **Zones do not attract price mid-flight — completion is distance, period.** The earlier 5–8pp "hint" was the distance confound; retracted. Consistent with C1's per-bar force null: a zone acts at arrival, not as a magnet in space. **Probe sweep (check-hardening)**: X=0.2→0.6U, zone-at vs empty-at: 82.9/83.3 · 66.4/67.9 · 53.5/55.3 · 43.5/45.8 · 36.1/39.2 — empty equal-or-slightly-ahead at every probe; the null is threshold-free (zones may fractionally SLOW arrival, consistent with dwell). Also named-unreported: exits with no positive-gap destination (deep inside bands) were dropped uncounted — micro-item for the C6/D pass. Ruler-invariance: the K=1 curve shows the same monotone distance law (96%→11%). Residual micro-item: same-bar A/B ties were filed as timeouts — bounded inside the ≤0.07U bins' 0–1% timeout mass, uncounted, named.
*A-92 (amended). C-block remaining: C5 day journeys · C6 cross-day wear.*
