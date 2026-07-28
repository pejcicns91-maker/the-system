# C5 — DAY JOURNEYS: THE FIVE WAYS A DAY WALKS THE BOARD (2026-07-08)
*Mode MAP · every calendar day × the whole 20-zone board, full history, weekends in · 7 mechanical features (zones visited, episodes at the declared K=6 ruler, revisits, range, |net|, wander ratio, concentration) · k=5 shown; frozen E1-fit→E2 shares within 2pp on every type · files: c5_days.csv.*

## THE VOCABULARY (shares stable E1/E2)
| type | share | signature (medians) | plain reading |
|---|---|---|---|
| k1 tight churner | **31.7%** | 9 zones, 38 entries, range 1.1U, net 0, wander 9.7 | small cage, endless recycling of the same zones |
| k2 broad churner | 25.4% | 12 zones, 42 entries, range 1.8U, net 0 | walks most of the board, ends nowhere |
| k0 leaning day | 20.4% | 9 zones, 22 entries, range 2.1U, net −0.35 | wide, mildly directional |
| k4 parked day | 16.1% | 6 zones, 21 entries, concentration 0.30 | camps at one structure |
| **k3 trend day** | **6.4%** | 11 zones, 22 entries, **range 4.0U, \|net\| 1.8, wander 4.9** | crosses the board efficiently |

## PERSISTENCE — the regime seed
Churn/parked shapes do NOT repeat (lifts 0.8–1.15×; tomorrow is a fresh draw). **Trend days DO: P(trend tomorrow | trend today) = 13.3% vs 6.4% base — 2.1× lift.** Trendiness clusters in time; churn doesn't. Weekend column: tight-churn over-represented (34% weekend share), trend days under (20%) — the weekend regime again. This is the first board-native regime signal: 57% of all days are churners where fade-logic lives, and the rare trend state announces itself by having just happened.
## CHECK-HARDENING (post-audit fixes)
**k=7 (owed from launch)**: families persist at finer grain; the trend type sharpens — 4.0% share, range 4.5U, **persistence lift 2.60×**. Resolution-invariant.
**Transition matrix (k=5, today→tomorrow %)**: churners circulate among churn (~31–35% into tight-churn from everywhere); **after a trend day the modal tomorrow is a PARKED day (35.3%)**, then leaning (27.4%) — trend resolves into camping at new structure, almost never into broad churn (7.2%). A usable morning prior.
**Named open axes (my reductions, visible)**: sequence ORDER of zone visits discarded by the 7-feature summary; direction folded (|net| — up/down trend days merged). Both live in c5_days-adjacent raw data for a future pass; not silently gone.
*A-93 (amended). Remaining: C6 cross-day wear → then the D lattice.*
