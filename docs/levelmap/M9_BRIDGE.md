# M9 — THE TRADINGVIEW BRIDGE (2026-07-09)
*Mode BUILD · brain in Python, face on the chart, nothing stale · files: m9_emit.py (emitter), CB9_level_map.pine (renderer), m9_payloads_2026-07-06.txt (real example lines, all four coins).*

## HOW IT WORKS (CB2's proven pattern, extended)
1. **Python emits** — `python3 m9_emit.py [date]` → one CB9 line per asset carrying ONLY day-specific data: today's **walls** (r=0.25 merge, the M8.5 layer — boxes, not 20 overlapping lines), each with composition (WM/D), **contact odds** (banked gravity lookup on yesterday's closest gap), and tags (★ stepping-POC magnet, V virgin ground); the day context (4H regime, yesterday's archetype, weekend); and **active named scenarios** evaluated at-open (POC-CASC up/down, ML-CASC, WC-SUPP).
2. **Pine renders** — paste the line into CB9's input: wall boxes heat-colored by contact odds (green ≥50%, amber 30–50, grey cold), purple borders on W/M-containing walls, per-wall labels, context/scenario panel with a STALE warning if the date isn't today.
3. **Era-proof constants live IN the Pine, baked** (they cannot go stale by definition — every one triangle- or 4×-certified): the escalation ladder, travel medians, the confluence-vote rows, the certified weekend/after-trend cells, the scenario odds, the target-distance curve, and the law line.

## THE DIVISION OF LABOR (why nothing rots)
Day-specific truth = payload (regenerated each morning by the same ritual as the brief). Timeless truth = baked constants (change only when a future gate changes them — a Pine update event, rare and deliberate). The chart never holds a number that can silently age.

## INSTALL (one-time, 2 minutes)
TradingView → Pine editor → paste CB9_level_map.pine → Add to chart → open settings → paste your asset's line from the emitter output. Daily: rerun the emitter, repaste. (Same muscle memory as CB2.)

## HONEST GAPS, NAMED
Hover-boost and PW/PM life-day decay not yet in the contact% (v2 emitter fields, listed) · the live at-touch VOTE needs intra-day inputs the payload can't carry — the Pine shows the vote's certified ladder instead and your eyes supply the dials · CB4 grammar unification pending your CB4 source.
*A-108. **CONTRACT v2 §2: M6 ✓ M7 ✓ M8 ✓ M8.5 ✓ M9 ✓ — the commissioned sequence is COMPLETE.** Parked on your side: div eye-card · CB4 source · volume Pine · M2c. The forward register now judges the Book live.*
