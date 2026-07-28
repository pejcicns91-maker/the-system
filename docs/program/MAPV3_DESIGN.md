# MAP V3 — DESIGN (2026-07-23) · the zone-behavior reading study
**Mode:** READING study — no seal, mining unrestricted (charter rule 4). Governed by V3_CONTRACT.md + CONTRACT_AUDIT.md.
**Data it sees:** Binance 5m full listing history, 4 coins, weekends in (the hash-logged files already fetched: BTC `1ac003e9…` ETH `303e70b0…` SOL `75e23943…` XRP `d46b9eba…`) + the validated wall series (port gate PASS 2026-07-23).
**Columns it emits:** every table = full-history headline + regime splits per contract §5.

## 1. Unit of study — the APPROACH EVENT
One row every time price comes at a zone. Event taxonomy (each is a row, typed):
- **STALL** — approach that turns ≥0.25U short of the edge without touching
- **TOUCH** — reaches the edge, penetration <0.1U
- **PENETRATION** — enters ≥0.1U, exits back the way it came (max depth recorded)
- **BREAK** — 5m close beyond the far side of the zone
- **TRAVERSE** — break that then travels ≥0.5U beyond
- **RETEST** — after a BREAK, first return to the broken edge from the far side (sub-record attached to its parent break; second/third retests numbered)
Estimated volume: ~100–300k events across history.

## 2. Feature groups (recorded per event — nothing optional)
**A. Approach ("where from, what intensity")**
origin zone id / day-open / mid-air · distance traveled in U · speed (U/hr) · bars en route · path shape (straight / grind / staircase via pullback count) · mean body size on approach (U) · relative volume on approach (vs 20-day same-hour median) · direction (from above/below) · test number today (1st/2nd/Nth) · today's prior ladder state (which zones already held/broke, ordered) · session (Asia/EU/US-open/lunch/US-close) · hours since 08:00 · weekday/weekend · overnight-gap flag
**B. Zone**
member levels (composition) · confluence count · contact score · virgin flag · stepping-POC tag · width in U · zone index in day's ladder · above/below day open · distance to next zone beyond (U) · distance to next zone behind (U) · days since zone level last traded
**C. System state**
Hayden-4H (own coin) · Hayden-4H BTC (for alts) · BTC-pi trend · day-type (EXPANSION/QUIET/normal, where derivable) · yesterday archetype (where derivable) · brief lean + strength (reconstructed A6b) · armed-scenario state incl. scenario-failed-already flag · week budget used % · month day · today's range used vs U · U-trend (14d U slope) · FOMC/event-proximity flag
**D. Outcome (the whole response, not hold/break)**
resolved type (stall/touch/pen/break) · max penetration depth (U) · bounce distance if held (U) · bars to bounce · time spent beyond if broke · travel beyond (U) · **reached next zone? (bool + bars to reach)** · false-break flag (back inside ≤6 bars) · close-of-day location vs zone
**E. Retest sub-record (new layer — exists nowhere yet)**
did retest occur · bars until retest · retest from which side · level flipped? (held as opposite role) · re-penetration depth (U) · second-leg travel after retest (U, signed) · retest count that day

## 3. Analysis tiers (breadth-honest given combinatorics)
- **T1 marginals:** every feature × every outcome, alone. Full tables, n everywhere.
- **T2 certified pairs:** all feature-pairs × key outcomes (hold %, reach-next %, retest-flip %, false-break %); FDR q=.10 at certification; UNDERPOWERED cells queued.
- **T3 triples:** only where T2 survivors intersect and n≥40.
- **Transition matrix:** zone→zone daily movement probabilities, conditioned per T2 survivors.

## 4. Forecast layer (the "what happens at zone 4" machine)
Chained conditionals: state = (position in ladder, today's event history, approach features, system state) → distribution over next events {hold here, reach next zone, retest-flip, reverse}. Scored with Brier + skill-vs-base-rate on held-out days (calibration split is for SCORING honesty only — it is not a money seal). Any unscored number is labeled UNSCORED per contract §7.

## 5. Build phases (each ends with the scope ledger)
- **P1** Event extractor + row schema on ONE coin, 20 sampled days → schema doc + spot-checkable event list (TV-verifiable timestamps) → Svet eyeballs before scale-up.
- **P2** Full extraction, 4 coins, full history → events_{COIN}.csv + schema.json + hashes.
- **P3** T1/T2 tables + transition matrix → tier files + certified-pair register.
- **P4** Forecast chains + calibration report.
- **P5** Synthesis: MAP_V3.md — the conditional playbook (readings only, no verdict words). Geometry candidates derived from it get their own money preregs (leave v3 at that point).

## 6. Acceptance checks Svet can run
Any event row → coin/date/time/prices printable for TradingView eyeball. Any table → n visible, splits beside headline. Paste the V3 CHECK paragraph at any step → full ledger before anything proceeds.

## DEVIATIONS / DROPPED
None at design time. (Day-type & yesterday-archetype derivability for deep history is flagged as a P2 risk: if not reconstructable for early years, those columns carry 'na' for that span — that will be surfaced in the ledger, not silently.)
