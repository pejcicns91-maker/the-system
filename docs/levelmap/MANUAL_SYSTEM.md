# MANUAL 2 — WHAT THE LEVEL MAP IS (system architecture & findings)
*2026-07-09. Companion to MANUAL_TRADING.md (usage) and AI_HANDOFF.md (continuation).*

## THE COMMISSION (Svet's words)
"Statistical probabilities of outcomes for each level, based on the scenario it is in — encompassing the other levels, price movement intensity, direction, and all other indicators we have." Delivered as a layered map + lookup + chart bridge.

## THE ARCHITECTURE (data → truth → chart)
1. **DATA**: Binance 5m, 4 coins (BTC/ETH/SOL/XRP), 2021-11→present, 8am-ET day windows, weekends first-class. 20 board levels/day (PD/ON/PS/PW/PM × H/L/C/POC). U = the day-move unit (each coin's normal daily range %).
2. **RECORDERS** (total population, zero judgment): the bar diary (38.97M rows: every 5m bar × every level) → **M1_state.parquet** (135,360 level-days × 70 columns: the full situation per row — intensity at 4 horizons signed, level history, ALL 20 levels' constellation states, day context, outcomes).
3. **STUDIES** (each check-hardened; every stat = full history + era + regime + asset + weekend columns): C-block (gravity, hover, knocks, legs, day-types, wear) · D lattice (dials crossed) · E gates · **F battery (the money test: 0/100 arms — reads work, those constructions don't pay)** · archetypes · **M2 constellation grid** (380 pairs; POC cascades, suppressors) · M3 order (minor axis) · M4 indicators (Hayden gated 99.1%; div ported; combo-only confirmed) · M7 vote · M8 named scenarios · M8.5 walls.
4. **THE PRODUCTS**: **THE_60PCT_BOOK.md** (every ≥60% situation, tiered) · **M8_SCENARIO_REGISTRY.md** (named scenarios) · **level_map_lookup_M5.jsx** (interactive lookup) · **m9_emit.py + CB9** (daily chart bridge) · **CB10** (live at-the-zone computer).

## THE TIER LANGUAGE (on every number)
**[CAL]** calibrated, 4×-reproduced (the thr×am table) · **[CAL-S]** stability-certified (E gates: fast×after-trend 56.1 break; weekend suppressor 35.6) · **[TRI]** triangle-certified — learned-H1→judged-H2 AND the mirror AND full-on-full all agree + placebo (the vote 67%; the escalation ladder; named scenarios) · **[P]** possibility-grade (constellation cells, combos) · **[FULL]** descriptive census. Nothing is quoted above its tier; nothing synthesized.

## THE LAWS THAT PRODUCED IT (why the numbers can be trusted)
Total-population recording · boundaries discovered or (b)-declared · **the Triangle Protocol** (contract v2 §1) on every gated claim · placebo + floors everywhere · instability = regime marker, never averaged away · UNDERPOWERED ≠ killed (annexed) · dual costs on money · no results prose before numbers print · every statistic converts to a date list + drawn charts · one failed eye-check = quarantine.

## THE FINDINGS IN SIX LINES
1. **Contact is forecastable; pre-approach direction is not.** Gravity/hover/magnet/freshness pick tomorrow's zones; the coin only tips once the arrival is visible.
2. **The direction coin is memoryless; resolution DEPTH remembers** — fresh ground breaks deep, worked ground caps (the M8 amendment).
3. **The board talks**: one level's state moves another's odds (POC cascades ±19pp, monthly-low cascades, the weekly-close suppressor) — constellation is real.
4. **Marginal dials aggregate**: nine small dials → a 67% [TRI] vote. Divergence works only in combos (Svet's doctrine, data-confirmed).
5. **The escalation ladder**: through-odds climb smoothly with penetration (0.3U→66% … 1.0U→89%), era-identical — the live mid-fight instrument.
6. **The toll owns small moves**: at 13.5bp, sub-1% brackets need 57–72% path-rates; the game turns humane at 2%+ captures. Where truth is monetizable is a venue question.

## FILE INDEX → PACK_MANIFEST.txt (every file, one line each)
