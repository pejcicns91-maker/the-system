# M4b — THE CB FAMILY: RESOLVED (2026-07-08)
*Mode BUILD (source analysis + closure) · sources examined: cbridge_cb2_pine.txt (168 lines, full), C_BRIDGE_MANUAL.pdf (revealed: a zip of CB2-manual screenshots, not a CB4 spec).*

## THE FINDING THAT CLOSES THE CLAUSE
**CB2 is not an indicator — it is a renderer.** Line-by-line: it computes zero signals. It takes ONE payload string produced by brief_engine_v4.py and draws it on the TradingView chart: the level lines (PDH/PDL/PDC/ONH/ONL/RND/S08), the range-budget caps (0.70·U and 0.70·p85 around the 08:00 spot), the 08:00/14:00 window guides, and the scenario glyphs (trigger/target/invalidation with the arm-at-15m-close, die-at-14:00 law printed in its panel). Every number it displays originates in the Python engine.

**Therefore the "CB port + parity gate" the contract demands is satisfied by identification, not by porting**: there is nothing to port and nothing to gate — the computational content already lives in Python, and much of it is already in the map (the levels, U). What CB *renders* that the map does not yet hold as columns:
- **p70/p85 range budgets** — engine-defined as the 70th/85th percentiles of K-nearest-neighbor realized ranges (grep-verified, lines 300/449) — computable historically from the same U machinery; a candidate M5 column, named.
- **Day-type call** (EXPANSION/QUIET/normal — trailing-percentile rule, line 301) and **direction call** — engine outputs; their live track record is the FORWARD_REGISTER's jurisdiction, historical reconstruction possible if commissioned.

## CB4 STATUS — SOURCE ABSENT, precisely stated
The project holds no CB4 source: the "manual" is CB2 screenshots. Per your memories CB4 = a superset of CB3 on TradingView — structurally another renderer generation. Two paths, your pick: **(a)** paste the CB4 Pine → I port/verify its payload grammar within a day-turn; **(b)** confirm it renders engine payloads like CB2 → the clause closes as identified, and the engine-field columns above become the real M4b/M5 work.

## INDICATOR CLAUSE — FULL LEDGER AFTER M4+M4b
Hayden 4H state/RSI: **GATED ✓** (99.07%) · H-Div forming: **ported, awaiting your 20-row eye-card** · Volume: **blocked-on-source**, banked 5.9y placebo null as prior · CB2: **renderer, no columns by design** · CB4: **source-requested** · Engine payload fields (p70/p85, day-type, dir): **named M5 candidate columns.**
*A-104. Next owed by name: **M5 — the lookup artifact** (situation in → odds out, every number tiered, every cell convertible to dates+charts).*
