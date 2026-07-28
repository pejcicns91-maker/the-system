# M8.5 — DYNAMIC WALLS + COMPOSITION (2026-07-09)
*Mode MAP + triangle · walls = level values merged at r∈{0.15,0.25,0.35}U (swept) · 11.8k–21.2k wall-touches per radius · files: m85_walls.csv.*

## DEFECT CAUGHT & CORRECTED BEFORE SHIPPING (logged)
The first pass read "W/M-containing walls give way +3–5pp" (4/4, E✓, triangle-agreeing) — and my own size table exposed it as an **any-of-N artifact**: "wall broke = any member broke" inflates mechanically with member count (size 1→3+: 42.6→53.0 is arithmetic, not market), and W/M walls carry MORE touched members inside the same 3+ class (median 4 vs 3). Controlled properly:
- **Exact sizes 3/4/5**: WM vs all-daily differences shrink to −1.2 / −2.6 / −3.4 (sign FLIPS).
- **Per-member break rate** (the clean metric): WM 40.7 vs daily 42.3 — triangle +0.6 / −4.2 / −1.5, legs disagree in sign.
**VERDICT: wall composition is a NULL.** A wall containing a weekly/monthly member reacts like an all-daily wall once counting is honest. The uncontrolled +3–5pp would have entered the Book as a fake dial; the confound check killed it first.

## WHAT STANDS FROM M8.5
1. **The wall recording layer itself** — the durable deliverable: per-day wall objects at three radii (m85_walls.csv), retiring M3's coincident-line attribution defect and giving M9's bridge its natural drawing unit (walls, not 20 overlapping lines).
2. **Count-of-lines re-confirmed null at wall grain** (per-member rates flat by size) — third confirmation of the P4b band result.
3. Composition: null, filed with its date list like any verdict.

## THE LESSON, BANKED
Any-of-N outcomes on variable-size groups are a standing trap — added to the auditor checklist as a named check: *"is the outcome definition monotone in group size by construction?"*
*A-107. Next owed by name: **M9 — the TradingView bridge** (M5 payload line from Python + extended CB renderer; walls as the drawing unit).*
