# MAPMONEY-1b — Wall touch-CONTINUATION money test (pre-registration, 2026-07-23)
**Mirror of MAPMONEY-1. This file precedes all 1b measurement. Contract applies.**

## Mode
MONEY TEST → sealed split (same per-coin 70/30 date cuts as MAPMONEY-1). Hypothesis sources declared: (primary) the pre-existing banked penetration ladder (0.6U → 79% continues), which predates this program; (secondary) MAPMONEY-1's placebo asymmetry. Because the secondary source saw full history, only the sealed segment here carries confirmatory weight; discovery is a read.

## What data it sees
Identical to MAPMONEY-1: the already-fetched, hash-logged Binance 5m full-history files (BTC `1ac003e9…`, ETH `303e70b0…`, SOL `75e23943…`, XRP `d46b9eba…`) and the SAME validated wall series (port gate PASS 2026-07-23). Warmup 35 days. Weekends in.

## Trade specification (locked — the mirror)
- Event: per wall per day, price approaches from outside (same state machine as 1a) and PENETRATES 0.6·uAbs beyond the proximal edge — the banked 79%-continues line.
- Entry: stop-order at proximalEdge ± 0.6U in the approach direction, gap-aware fill. Direction: WITH the move (through the wall).
- Stop: back at the proximal edge. R := 0.6·uAbs.
- Target: proximal edge of the next wall BEYOND the penetrated wall in trade direction; none → no trade (counted).
- One trade per wall per day (first qualifying penetration), one open position per coin, stop-priority on same-bar double-touch, time-exit at the 08:00 ET day boundary.
- Costs: dual rows, identical to 1a (P0; FTMO 0.135% RT + 0.082% per crossed 00:00 UTC).

## Endpoints, gate, null, columns
Identical to MAPMONEY-1: FTMO mean R + R/mo; gate = discovery FTMO mean R > 0 AND sealed ≥ 0 with n≥40 AND sealed placebo p ≤ BH q=.10 over {4 coins × 2 sides}; placebo = 100 matched sims (same stop, TP-distance resampled, same queue and time-exit), seed 20260723; columns = full-history headline + year · Hayden-4H · weekday/weekend · asset · side · contact bucket · virgin. Instability → regime marker. Deviations reported, never promoted. DROPPED section mandatory.
