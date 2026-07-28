# M3 — VISIT-ORDER GRAMMAR (2026-07-08)
*Mode MAP · 64,291 touched level-days → within-day first-touch sequences · 40,398 clean transitions after the defect fix · null = within-day permutation of the visited set ×15 (order beyond composition only) · files: m3_order.csv.*

## DEFECT CAUGHT & FIXED BEFORE SHIPPING (logged)
v1 broke on simultaneity: price opens AT yesterday's close, so several levels "first-touch" together at bar 0 and my sort broke ties in arbitrary fixed order — manufacturing impossible cells. Fix: the opening cluster (bars 0–1) collapses to one unordered ORIGIN node; grammar runs on distinct-bar transitions only; multi-level tie groups flagged. (Also logged: a column named `gt` collided with a pandas method and silently nulled one check — caught, bracket-fixed.)

## FINDING 1 — THE GRAMMAR IS NEGATIVE, AND IT'S GEOMETRY
No favored "secret routes" exist above chance. What exists is a suppression grammar, all top cells ×0.12–0.28 of expected: after one extreme, the *opposite same-scale extreme* almost never comes next (PSL→PSH ×0.12, PDL→PDH ×0.19, PSH→PSL ×0.24), and ladder-skips against the path are equally rare (PDH→ONH ×0.16, PDL→ONL ×0.18). This is the distance law wearing sequence clothes: **you visit what's near; days rarely re-cross their whole range.** Order carries almost no information beyond composition + geometry — the spec's owed axis is now measured, and it measures small.

## FINDING 2 — WHERE PRICE CAME FROM barely moves what happens next (distance-controlled)
Prev-level effects on break-at-B, within gap terciles, top cells (all 4/4, era-consistent): ONPOC→PDPOC from below, near: **+9.2pp** (E1 +11.6/E2 +6.7) — the POC-stack momentum again, now visible in sequence form · PSL→PDL from above, near: −8.1 (E2-heavier) · ONH→PSH from below: +6.6. Everything else ±2–4pp. Beside M2's ±14–19pp configuration effects, the itinerary is a minor axis: **the map's memory lives in the board's configuration, not in the visit order** — one more face of the memoryless-reaction law.
*A-102. Merge integrity verified (coincident-value levels share values correctly). Next owed by name: **M4 — the indicator port + TradingView parity gate** (CB4, RSI divergence, volume), the clause dropped once and never again.*
