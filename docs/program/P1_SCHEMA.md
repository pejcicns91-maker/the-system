# MAP V3 — P1 SCHEMA (p1_events_SOL.csv · 21 days · 158 events · sha 6bde49cc4c88cb0b)
One row = one approach event. RETEST rows attach to a parent break via `parent`.

## Event types
STALL (turned ≥0.25U short after entering the 0.25U proximity band) · TOUCH (reached edge, depth <0.1U) · PEN (entered ≥0.1U, came back) · BREAK (5m close beyond far side) · TRAV (break that traveled ≥0.5U beyond) · RETEST (post-break return to the broken edge; up to 3 numbered).
**Amendment queued for P2 (found in eyeballing):** an EXIT type — day opens INSIDE a zone and price closes out through an edge (today's zone-6 down-exit at ~10:45 ET has no row under P1's outside-approach taxonomy). Will carry the full break-outcome block + retests.

## Columns
**Identity:** id · coin · day · t_event (ms UTC) · zone (ladder #) · z_lo/z_hi (prices) · parent (retests)
**Zone (group B):** contact · virgin · stepPOC · members (level names, /-joined) · confl (count) · widthU · ladder_ix · above_open · dnextU / dbehindU (distance to next zone beyond/behind, U) · last_tradedd (days since zone mid last traded, ≤60)
**Approach (group A):** origin (Zn / air / open) · distU · speedUh · bars_route · pullbacks (≥0.15U counter-moves) · bodyU (mean candle body) · relvol (approach vol ÷ 20-day same-hour median) · side (below/above) · test_no · ladder_state (today's prior resolutions this side) · session (asia/eu/us_open/lunch/us_close/evening) · hrs_since8 · wknd · gap
**System (group C):** hayden · wk_used (week range ÷ 26-wk median, approx) · mo_day · rng_used (day range so far ÷ U) · u_trend (14d U slope) · fomc · U — **hayden_btc, btc_pi, daytype, yd_arch, lean = 'na' in P1** (P2 work, see ledger)
**Outcome (group D):** etype · depthU (max penetration) · bounceU + bars_bounce (held cases, 24-bar window) · bars_beyond · travelU · reached_next + bars_next · false_break (back inside ≤6 bars) · eod_locU (close vs zone mid, U) · truncated (day ended mid-event)
**Retest rows (group E):** retest_no · bars_until · repenU (re-penetration of broken edge) · flip (held = closed ≥0.25U onside within 12 bars / failed = closed ≥0.1U back through) · leg2U (travel in 24 bars after resolution)

## Definitions locked during P1 (deviations, disclosed)
1. Cool-off after any event: a new approach on the same zone-side counts only after the away-wick clears 0.5U (post-STALL) / 0.25U (post-touch-class) from the edge — kills oscillation spam (was 311 events of which ~100 duplicate stalls; now 158 clean).
2. Cool-off distance measured by the away-side wick extreme, not the near extreme (v1 silently swallowed later events; fixed).
3. Fetch note: SOL data extended to 14:1x ET today; today is a truncated day, flagged.

## Verified against known tape (2026-07-22/23)
07-22: three probes into zone-6's floor area (10:15 / 14:20 / 21:35 ET, depths 0.20/0.24/0.35U — lows 77.40/77.31/77.04 = the brief's PDL-area and ONL to the cent), all bounced; two stalls under the 78.59 wall (evening rally died 0.05U short — the 78.54 ONH). Today: zone 5 (75.848) wick-tagged at 12:20 ET, low 75.83, bounced — a level-perfect touch. The machine's read matches the chart.
