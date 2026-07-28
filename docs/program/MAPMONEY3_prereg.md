# MAPMONEY-3 — Wall BREAK→RETEST money test (pre-registration, 2026-07-23)
**Untested-list item 3 — Svet's own card grammar ("break, wait, enter the pullback"). Contract applies. This file precedes all measurement.**

## Mode
MONEY TEST → sealed split, same per-coin 70/30 cut dates as MAPMONEY-1 (loaded, not recomputed). Hypothesis sources: Svet's standing retrace rule + the banked 0.6U/79% line + the 1/1b synthesis (entry PRICE, not direction, was the killer). Sealed segment carries the confirmatory weight.

## What data it sees
Identical to MAPMONEY-1/1b: hash-logged Binance 5m full history (BTC `1ac003e9…`, ETH `303e70b0…`, SOL `75e23943…`, XRP `d46b9eba…`) + the SAME validated wall series (gate PASS). Warmup 35 days, weekends in.

## Trade specification (locked)
- Per wall per day. Break side edgeX = the wall edge in the direction of travel (up-break: hi; down-break: lo; single-price walls: the level). **B-line = edgeX ± 0.6·uAbs** in break direction.
- BREAK event: a 5m bar CLOSES beyond B. No entry on the break (no chasing).
- RETEST entry: from the next bar on, a resting limit at **B**; first return touch fills (gap-aware: better-than-B opens fill at the open). Direction = WITH the break. Limit expires at the 08:00 ET day boundary.
- Stop: at edgeX (back through the broken edge). R := 0.6·uAbs.
- Target: proximal edge of the next wall beyond, in break direction; none → no trade (counted).
- One trade per wall per day; one open position per coin; stop-priority; time-exit at day boundary. Costs dual: P0; FTMO 0.135% RT + 0.082% per crossed 00:00 UTC.

## Endpoints, gate, null, columns
Identical to 1/1b: FTMO mean R + R/mo; gate = discovery FTMO >0 AND sealed ≥0 (n≥40) AND sealed placebo p ≤ BH q=.10 over {4 coins × 2 sides}; placebo = 100 matched sims (same stop, TP-dist resampled, same queue/expiry), seed 20260723; columns = full-history headline + year · Hayden · weekday/weekend · asset · side · contact bucket · virgin. Instability → regime marker. Deviations reported; DROPPED mandatory.
