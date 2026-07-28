# BRUTE-FORCE ZONE STUDY — DESIGN (parked, 2026-07-23)
**Status: DESIGNED, NOT COMMISSIONED. Nothing runs until Svet says so.**
Governed by V3_CONTRACT.md + CONTRACT_AUDIT.md + the standing rule this design exists to enforce: **the data prunes, the researcher does not.** Every subset at every depth is attempted; cells die only by n-extinction, and every death is logged to the UNDERPOWERED queue for re-run as history grows.

## The five axes (Svet's definition, verbatim in structure)
**Axis 1 — Vantage grid (where price stands relative to the zone).**
Stations: 1.0U / 0.5U / 0.25U outside-near · lower border · 25% inside · midpoint · 75% inside · upper border · 0.25U / 0.5U / 1.0U outside-far — from BOTH approach directions. ≈12 stations × 2 directions = 24 vantages. Every event is re-expressed as a row per vantage it passed through: "standing here, this is what came next."

**Axis 2 — The system's parts (~15, each a conditioning column):**
1 Hayden own-coin · 2 Hayden-BTC · 3 BTC-pi · 4 day-type · 5 yesterday-archetype · 6 brief lean (A6b) · 7 armed-scenario state incl. already-failed flag · 8 Option B book state · 9 week budget used · 10 U-trend · 11 map-v2 level odds at the zone · 12 zone attributes (contact / virgin / stepping-POC / width / confluence) · 13 today's ladder history (ordered holds/breaks) · 14 event calendar (FOMC etc.) · 15 session/clock.
Parts 4/5/6/7/8 require the engine-definition port or forward-fill — a build prerequisite, not a droppable column.

**Axis 3 — The combination ladder, complete.**
All singles (15) → all pairs (105) → all triples (455) → all quadruples (1,365) → … → all fifteen: the full power set, 32,767 stacks. No seeding, no shortlists, no "top-pair" pruning. Climb every rung; log extinction depth per branch.

**Axis 4 — History and future on five timeframes.**
For price AND for every component: the prior **100 bars on 5m, 15m, 1h, 4h, and 1D** (path, states, volume, prior zone interactions) as conditioning features — and the reaction measured **100 bars forward on each of the five frames**, not one fixed window. Five resolution layers on both sides of every event.

**Axis 5 — The reaction as a full profile.**
Per vantage × stack: bounce probability AND bounce-size distribution · penetration-depth distribution · break odds · travel distance · return odds · time-to-resolution — on each forward frame. The give-reaction curve, not a hold/break coin.

## Scale, stated honestly (physics, not scope)
~185k base events → ~4.4M vantage-rows; × 32,767 stacks ≈ 10¹¹ potential cells vs ~10⁵·⁵ events: the n=40 floor will extinguish most branches at depth 4–6. That is the data pruning itself. Compute: multi-hour batch jobs — suited to the GitHub-automation route (Actions runners chewing the ladder, committing registers) or multi-session chat builds. Storage: vantage-row table ~5–15 GB uncompressed; registers in the millions of rows.

## Execution phases (each ends with the scope ledger; check phrase binding)
B0 Prerequisite: port/validate the five engine-internal components (like the pi validation — adopt only on match) or forward-fill from daily briefs.
B1 Vantage-row extraction (5m base) + multi-frame lookback/forward feature build. Eyeball gate on sampled rows before scale.
B2 Ladder depth 1–2 (singles, all pairs) across all vantages × reaction profiles. Full registers + extinction map.
B3 Depth 3–4 (all triples, all quadruples). No seeding.
B4 Depth 5+ until global extinction; publish the extinction frontier.
B5 Forecast layer retrained on the full vantage/multi-frame state; Brier-scored per frame.
B6 Synthesis: the give-reaction atlas. Money candidates leave at the door (own preregs, sealed).

## Deliverables
vantage_rows.parquet (+hashes) · ladder registers per depth (certified + UNDERPOWERED queues) · extinction map · reaction-profile atlas · scored forecasters per frame · closing ledger.
