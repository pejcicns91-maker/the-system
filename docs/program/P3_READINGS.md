# MAP V3 — P3 READINGS (2026-07-23) · frequencies only, no verdict words
Inputs: p2_events_ALL.csv (185,452 events, sha `fcf1262a…`). Artifacts: p3_t1.json `82b968cd…` · p3_t2_register.csv `22b58ca8…` (10,067 tests) · p3_t3_register.csv `1758e98a…` · p3_transitions.json `15dc937e…`. Rerun: `python3 p3.py`.

## Base rates (full history, weekends in — every split available in p3_t1.json)
- **Hold at contact: 50.1%** (n 53,467 contact events). Note: map-v2's 56.4 gravity number is a different event definition (level-gap odds); both stand under their own definitions.
- **A break reaches the next zone only 14.0%** of the time (n 39,362 break events; 66,237 is the retest_flip n — corrected 2026-07-26).
- **False break — back inside within 30 minutes: 60.2%** of all breaks.
- **Broken-level flip (holds as new S/R within 12 bars at 0.25U): 7.3%** of resolved retests. Strict criterion, stated; it is the measurement, not a judgment.
- Depth at contact: p10/25/50/75/90 = 0.010/0.031/0.072/0.170/0.320 U. **Graze line (distribution-derived, = p25): ≤0.031U** — Svet's "barely there" class, now formal.
- Retest of a broken edge occurs for ~86% of breaks (parent coverage).

## Transition layer (what the NEXT event's zone is, same day)
STALL → next event at an adjacent zone 77.8% (stalls hand off) · TOUCH → 51.8% same zone again · PEN → 55.8% adjacent · **BREAK → 82.2% same zone next** (the tape comes back to the broken wall) · EXIT → 88.1% same zone. The ladder is sticky: after violence, the same wall is usually the next appointment — coherent with the 60% false-break and 86% retest rates.

## Certified conditionals (T2: 10,067 tests, BH-FDR q=.10; top by lift, n shown)
- **Wide zones (0.32–1.71U) barely ever resolve as breaks:** hold 87–96% across EU session (95.7%, n 1,587), Asia (92.8%, n 823), evening (89.2%, n 2,861), late-day hours (94.5%, n 2,579), slow approaches (89.3%, n 3,639). Width is ex-ante known; the effect is real and partly mechanical (more ground to close beyond) — both said.
- **Virgin zones invert:** first arrival at a 20-day-untouched zone from close range holds only **9.4%** (n 117) / 10.0% via a Z6 origin (n 40 — at the floor, queued). Untouched walls, when finally reached, mostly give way.
- **Stepping-POC zones hold 92.7% when grazed** (n 1,411, T1 view).
- 4,986 pair-cells certified in total; ~5,000 more skipped at the n<40 floor (UNDERPOWERED queue, re-runnable as history grows). T3: 531 triples certified from pair-survivor seeds (register on file).

## Tautology guard (deviation, disclosed)
Depth-class was initially allowed as a conditioning feature and produced circular "certified" cells (a graze cannot be a break by construction); it was removed from T2/T3 conditioning and kept only as a descriptive outcome axis. Registers regenerated; the first T2 register hash (`283fc294…`) is superseded by `22b58ca8…`.

## SCOPE LEDGER
**EXAMINED:** T1 marginals across all features × 4 outcome families · graze subclass (measured) · T2 full pair grid with FDR · T3 seeded triples · transition deltas by event type.
**REMAINING:** daytype/yd_arch/lean columns (still 'na', engine-definition port pending) · inside-edge taps · UNDERPOWERED queue (n<40 cells) · P4 forecast chains + Brier scoring · P5 synthesis into MAP_V3.md · any money spec built on these readings (leaves v3, own prereg).
**DROPPED:** nothing.
**Assumption flags:** flip criterion (0.25U/12 bars) and false-break window (6 bars) are P1-disclosed definitions; graze line is distribution-derived, not chosen.
