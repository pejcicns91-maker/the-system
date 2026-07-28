# CB12.6 — DESIGN (2026-07-23, words only; no code until Svet says code)
Boundary first: CB cards are the READING + judgment layer. Option B stays untouched. Nothing here is a sized money rule; the four money candidates (virgin-break, wide-calm fade, conditioned retest, forecast-gating) stay in the sealed-prereg queue. Cards may carry calibrated readings because readings are allowed; "validated/edge" words remain banned on them.

## WHAT IS ADDED
1. **Zone classes on the chart.** Every wall gets a class badge from the map: V = virgin (first touch in 20d → held only 9% historically) · W = wide-calm (89–97% hold cells) · S = stepping-POC (93% hold when grazed) · plain. You see which walls are load-bearing and which are paper before price arrives.
2. **Calibrated numbers.** Where the P4 forecaster covers a zone, the card prints its calibrated P(hold) tagged `cal` (±3pp honest). Where it doesn't, the banked constants remain, tagged `bank`. Two sources, always labeled, never blended.
3. **The homecoming line.** Every break branch carries the return context by default: ~60% back inside ≤30m · same wall is the next event 82% · retest ~86%. The break card's first branch is "it comes back," not "it runs."
4. **Graze class.** Touches ≤0.031U are grazes: they don't count as tests in card logic, lit-row logic, or Track-B grading. Your "barely there" is now a formal grading rule.
5. **Forecast step in the morning pipeline** (when built): after walls, today's zones are scored through the trained model → pHold lands in the payload automatically.

## WHAT IS ADJUSTED
1. **Chase cards are banned — permanently.** The break-candle entry never appears again (−0.10R gross, proven). Every break routes to the retest entry only (+0.02R gross, the sole surviving geometry). The retrace grammar goes from preference to law of composition.
2. **Virgin walls flip roles.** Never fade targets. First touch of a V wall composes as a break-watch (9% hold), with the retest of it as the entry if it goes.
3. **Fades become selective.** Fade cards are written only where a certified high-hold cell applies (wide × calm session × slow approach etc.), with the cell's rate and n printed on the card. No more fading uniform "56%" walls.
4. **Default break expectation inverts.** Old cards implied travel; the tape says 14% travel. Travel becomes the minority branch, return the default.
5. **Payload grammar v6:** adds per-wall `F:{pHold},{class}` and a `R:` return-context line. Everything else (T cards, G rows for 12.6a, W walls, N, OVR) carries over from 12.4/12.5.

## WHAT CB12.6 (the script) DOES
Keeps 12.5 exactly: no table, right-side labels, time-locked 09:00→09:00, one paste box for all assets, auto-switch by symbol. Adds: class glyph + cal-pHold badge on each zone; optional zone coloring by pHold instead of contact heat; retest-entry boxes as the only entry geometry on break branches; homecoming note at a broken edge. CB12.6a (later) = the table assistant with the WHEN/DO rows.

## HOW WE ARE BETTER OFF
Yesterday you looked at five identical purple boxes and composed odds. With 12.6 you look at classed walls (paper vs load-bearing), calibrated probabilities that have been right within 3 points on ten thousand unseen events, a structural ban on the two entries that lost ~₿20k-trades' worth of testing, the only paying geometry as the default plan, break events pre-loaded with their most likely future (return), and grading that stops punishing grazes. Same one-paste ritual, same phone, better eyes.

## NOT IN 12.6 (explicit)
No auto-trading · no forecaster-gated sizing (that's C4, sealed gate first) · engine columns (day-type/lean/archetype) still pending B0 · the brute-force atlas feeds 12.7, not 12.6.

## BUILD ORDER (on "code it", stepwise)
1. Payload grammar v6 + tomorrow's payloads composed under the new laws (no script change needed to start — 12.5 renders unknown fields harmlessly)
2. Forecast scorer into the daily zip (model + one call in run_day)
3. CB12.6 Pine (12.5 + badges/coloring/homecoming)
4. 12.6a table assistant.
