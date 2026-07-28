# C2 — TIME-AT-DISTANCE: WHERE PRICE PARKS, PER FAMILY (2026-07-08)
*Mode MAP · every bar × every zone, full history, weekends in · placebo per class · frozen check = E1-fit vs E2 occupancy-shape correlation · files: c2_dwell_multi.csv (dwell at 7 radii 0.05–0.5U — no single cut exists), c2_occ.npz. Choices visible: C1's K=7 families as frame, ±2U axis, 0.05U display bins, radius GRID (a sweep, not a threshold), quartiles for dose display.*

## FAMILY DWELL PROFILES (share of the family's time: near edge ≤0.25U / on the 0.35–0.85U shelf / beyond 1U) — era shape corr 0.96–0.998, all stable
Data-derived location stats per family (peak | q25 | median | q75, U from edge — no hand bands):
- **k1 break**: peak **+0.03** | −0.42 | −0.02 | +0.28 — glued to the edge, HALF its time inside/beyond.
- **k5 sweep**: peak **+0.03** | −0.17 | +0.13 | +0.48 — edge-hugging, shallower penetration than the break.
- **k3 near-miss**: peak **+0.63** | +0.53 | +0.88 | +1.33 — the family's own mass names its shelf: it peaks 0.63U off the edge. (Third independent appearance of the ~0.6 constant — inside as the break boundary, outside as the stall shelf.)
- **k2 walked-away**: peak +0.88, mass drifting out. **k4 runaway**: q25 +0.68 → far. **k0/k6 spectators**: k6 spends literally no time within 2U.

## WHICH ZONES ORGANIZE PARKING (occupancy real/placebo at the edge → at 1U)
ON **3.3×** → PD 2.6× → PS 1.8× → PW 1.2× ≈ PM 1.2× (all inverting to <1× at 1U). Fresh overnight/day zones dominate where price parks; the weekly/monthly gradient is diluted by their many spectator days (caveat: conditional-on-near profiles would sharpen — queued as a D-lattice cut, not silently done).

## HOVER → ENGAGE — now threshold-free (radius sweep 0.05→0.5U, untouched-today n=71,047)
At EVERY radius: hovering marks the zone. Dwellers vs non-dwellers, P(touch tomorrow): 45.4 vs 13.5 (r=0.05) · 44.2 vs 12.7 (0.10) · 41.8 vs 10.7 (0.20) · 39.3 vs 8.9 (0.30) · 34.8 vs 6.4 (0.50); top-dose quartile ~46–51% across the whole sweep. No cut needed — **any leaning on a zone, at any measured radius, roughly quadruples its next-day contact odds**; the finding is a curve, not a category. (Top-quartile regime columns at r=0.10: E1 46.7/E2 51.3, weekday 44.3/weekend 52.5, assets 43–56.)
*A-90. Next: C3 multi-touch (does a zone crack or harden with each hit) — episode grain, touches_v2 files are built for exactly this.*
