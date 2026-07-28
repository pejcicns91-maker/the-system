# COMPONENTS.md — what each part of the old program actually is (EXPLAINER, v3)
2026-07-27 · Purpose: give Svet a plain-words understanding of every component the two packs contain or cite — what it reads, where it came from, how it was derived, whether U touches it, whether it was ever validated. NO decisions requested here. Decisions come after this doc contains nothing you can't explain back. Ask or correct by number.

Origin tags: YOURS = your concept/indicator · PORT = your live engine's logic reproduced and gate-checked · AI-DECISION = invented by an AI and ratified by you on the record · AI-BUILT = constructed by a research AI inside a study.

---

## A. Definitions in hand (code in the packs)

**01 · Hayden 4H — own coin.** Your regime light: Bull / Bear / Chop on the 4H chart. Derived: RSI-14 (Wilder) on the candle's OHLC-average; Bull when RSI crosses above 67, Bear below 33, decays back to Chop through 61/39. Origin: YOURS, ported verbatim from mm1.py. U: clean. Validated: 1.000 agreement with the shipped live series (0.997 on SOL).

**02 · Hayden 4H — BTC.** The same light run on BTC while you trade an alt — "what's the leader's regime." Origin: YOURS/PORT. U: clean. Validated: same machine as 01.

**03 · Hayden fast — 15m & 1h.** The same machine on faster bars, giving the regime light a short-term version. Origin: AI-BUILT during W2 (explicitly labeled uncertified — never gate-checked against anything live). U: clean. Validated: no.

**04 · BTC pi-cycle.** A slow macro switch: the 111-day average vs 2× the 350-day average of BTC daily closes; "up" or "down" plus how far apart they sit. Origin: public indicator your live engine adopted; PORT. U: clean. Validated: matched the live engine's state on the check date; 97% history coverage.

**05 · Day-type + range forecast.** Each morning, a nearest-neighbors model looks at yesterday's stats across all four coins and says what kind of day to expect — EXPANSION / QUIET / normal — plus a forecast range. Derived: KNN over standardized daily features, K=75, walk-forward. Origin: AI-BUILT (brief engine). U: the magnitude side is U-family (everything is relative to trailing range). Validated: two-path reproduction 68/68; but no sealed log exists to grade its historical calls — honestly marked PROVISIONAL in B0.

**06 · Lean chain.** The brief's daily directional lean: a fixed ladder of rules (SOL fades yesterday's Nasdaq; an ETH order-book state rule; a JPY rule for BTC; DXY and FOMC as notes). Origin: AI-BUILT from earlier studies, running live in the brief. U: clean (sign-based rules). Validated: reproduced 8/8 against sealed brief lines; the underlying edges are LEGACY-UNVERIFIED like everything else.

**07 · yd_arch.** A one-word label for yesterday: UP day, DOWN day, or CHOP — judged by how much of yesterday's range the close captured (≥half up = UP, ≤−half = DN, else CHOP). Origin: AI-DECISION — no historical definition existed anywhere, so one was proposed and you ratified it 2026-07-23, with "any competing historical definition supersedes on sight." U: clean (a ratio of yesterday's own candle). Validated: can't be — it's a definition, not a recovery.

**08 · Option B book state.** Not the strategy — just what the book *is* at any moment: which sleeves are open or fired today, overlap flag. Candidate context dial only; Option B itself stays live and untouched, and whether its state enters The System is your call. Origin: PORT, gated 495/495 trades exact. U: clean (Donchian + ATR mechanics).

**09 · Armed-scenario states.** The brief's if-then cards as a state machine: a card arms when a 15-minute close crosses its trigger between 09:00 and 14:00 ET, then hits its target, fails at its invalidation, or dies at 14:00. Origin: card *construction* is PORT (engine-exact, 0 mismatches over 9,094); the *arming rules* are AI-DECISION, ratified 2026-07-23 on a thin 2-row gate. U: triggers are price levels; mostly clean.

**10 · Zones/walls + per-bar geometry.** The spine. Twenty levels from prior day / overnight / prior session / prior week / prior month (each's High, Low, Close, POC), merged into zones when they sit close together; zones carry contact history, virgin status (untouched ≥20 days), stepping-POC runs, width class. Origin: YOURS (the locked logic), engine-ported wall-for-wall. U: ONE U lives here — the merge radius is 0.25·U, so zone membership breathes with trailing volatility. Your call whether the lock covers that radius or it becomes a swept parameter. Validated: port-gated against the live engine.

**11 · Cascade scenario states.** Chart-pattern if-thens from the wall builder: e.g. "5m close under the overnight POC after holding above it → POC-cascade-down toward the midline." Origin: AI-BUILT (m9b/m9_emit grammar). U: trigger levels are prices; clean-ish. Validated: never tested as predictions — they're constructions.

**12 · Week budget + weekly forecast.** How much of a normal week's range has been used by mid-week, plus a pooled nearest-neighbors forecast of the week's full range. Origin: AI-BUILT; the weekly-range forecastability claim was the old program's strongest validated finding — now LEGACY-UNVERIFIED like the rest. U: U-family by construction (ranges vs trailing medians).

**13 · Prior week / month map.** Last week's and last month's H/L/C as standing levels, plus how far into the month we are. Origin: standard structure, YOURS by adoption. U: clean (absolute prices).

**14 · U + U-trend.** The unit itself: the median of the last 14 daily ranges, and whether it's rising or falling. In the new record it exists only as a DERIVED column (rule 10) — never the stored measurement. Origin: program convention from the earliest chats. Validated: never tested against alternative rulers — the core fault you named.

**15 · Range-used.** How much of today's expected range is already spent. U-family by definition; stored native (price range) with the ratio derived.

**16 · Relative volume.** Two ratios: this bar's volume vs the 20-day median for the same time of day (relvol), and short-mean vs long-mean volume (volr). Origin: AI-BUILT. U: clean (pure ratios). Validated: as inputs only, never alone.

**17 · RSI divergence events.** Price makes a new pivot high but RSI doesn't (bearish), or new pivot low and RSI doesn't (bullish) — per frame, with counts and recency. Origin: YOURS conceptually; AI-BUILT extraction. U: clean. Validated: the one indicator test that PASSED its reading gate — divergence presence shifted outcomes +6–12pp, 7/8 cells FDR-certified (money version died to costs like everything else).

**18 · Session/clock context.** Which session (Asia/EU/US-open/lunch/US-close/evening), hours since 08:00, weekday/weekend, opening gap, FOMC days. Origin: convention. U: clean.

**19 · Day ladder history.** What already happened today: which zones were tested, held, broke, in what order, and each zone's test count. In the new design this becomes a query-time LABEL layer (thresholds leave the record). U as previously built: saturated — every "held/broke" call used U thresholds; will be re-derived ruler-free.

**20 · W2 encodings.** The old program's compressed "story words" for component journeys (last-4 swing tokens, 8-letter slope word, confirm/diverge relation, a few scalars). Kept only as DERIVED columns beside the per-bar raw — they are the collapse artifact, useful as compact summaries, never the record. Origin: AI-BUILT. Validated: internally gated; predictive value unresolved (test incomplete and run through the compression).

---

## B. Cited by the packs, definitions NOT inside them
What the packs *say* about each, honestly — full explanation impossible until a source arrives. All are AI-BUILT in the level-map chat unless noted.

**21 · The 7-dial vote.** A thumbs poll taken around a level touch: several dials each vote ±1 (approach speed, day calmness, how many zones were tested, trend vs lean day, weekday, wall density); 3+ votes against → the certified "reject" corner (67.4% reject was the claim). Sign map survives in AI_HANDOFF; the dials' constructions live in CB9/CB10 Pine, absent here. U: at least the speed/calm dials were U-tercile-based.
**22 · Thrust classes.** The approach-speed dial behind the vote: fast / slow / reversal arrival at a level, cut at fixed terciles of signed U-per-hour. Construction absent. U: saturated.
**23 · Drive24.** A day-momentum dial: roughly where price sits now vs 24 hours ago, in U, cut at terciles. Construction absent. U: saturated.
**24 · Wear / worn-wall.** How "used" a wall is — walls touched often behaving differently than fresh ones ("worn-wall 63%" was a headline). Source dead-pathed. U: thresholds unknown.
**25 · Escalation ladder + travel medians.** The claim that the deeper price pushes into a zone, the likelier it finishes through — a rung-by-rung table (0.2U→~60% … 1.0U→~89%), plus typical travel distances. Source in CB9/CB10. U: saturated (rungs are U).
**26 · Approach intensity.** A 288-bar profile of how forcefully price came into the day. Dead-pathed array. U: likely.
**27 · Day-path archetypes.** Ten clustered day shapes (lean/churn/trend/parked families) with frozen centroids; yesterday's archetype as context. Centroids absent. U: clustering ran on normalized paths — U-family.
**28 · Density dial / constellations.** How crowded the board is (walls near each other) and which level-pairs sit in play. Definitions absent. U: proximity presumably U-based.
**29 · CB4.** Named once among parked source items. I don't know what it is — you may. What is it?
**30 · Option B rulebook v1.2.** The governing document of the live system (behavior is visible in the engine; the doc itself isn't in the packs). Context: Option B stays as-is; the doc matters only if its state (08) enters The System.

---

Standing note on all of section A's "validated" tags: validation there means *the machinery reproduces its source* — port gates, agreement scores. Whether any component's reading carries information about price is exactly what The System's per-bar record exists to measure, from scratch, under rule 8. Nothing on this page is pre-trusted.

---
## RESOLVED BY THE 2026-07-22 PACK (definitions recovered — section B is no longer blind)
21 vote · 22 thrust · 23 drive24 · 24 wear(am20) · 25 escalation ladder · 26 approach intensity (i30m/i2h/i6h/i23h columns, matrix spec'd) · 27 archetypes (k-means on real 288-bar paths; daypaths.npz) · 28 density/constellation (12-state grammar, M2 grid) — full constructions now in PACK3_INSIGHTS_2026-07-27.md and REPRODUCTION_GUIDE.md. 29 CB4: resolved — renderer generation, no signal content, no source exists (clause closed by identification). 30 Option B rulebook: in hand (v1.0/1.1/1.2). Correction to 10: the zone band is 0.04·uU half-width and the wall merge radius was SWEPT {0.15/0.25/0.35}U in M8.5, canonical 0.25 — one of the few honestly-varied parameters in the history.
