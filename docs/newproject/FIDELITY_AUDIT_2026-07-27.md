# FIDELITY AUDIT — how true to Svet's desire the project has been
2026-07-27 · Basis: CB13_CONTINUATION_v3_2026-07-24.zip (72 files incl. nested post_B6 zip + brief_state.zip) and BRUTEFORCE_COMPLETE.zip (80 files). Coverage: every .md/.txt/.py/.pine read literally start-to-EOF; every .csv/.parquet/.json/.pkl ingested programmatically in full (row counts, schemas, content checks); all 3 PNGs viewed; nested zips inventoried and diffed. Nothing skimmed. The one thing not re-read byte-for-byte: files inside the nested post_B6 zip that are byte-older copies of files already read in the outer packs (diffed by name/size; unique content listed in §A.4).

THE DESIRE BEING AUDITED AGAINST (as defined by Svet in the instruction-design chat):
per-bar, per-timeframe, per-component human-style READINGS around drawn zones — the sequence of readings, not triggered signals; full granularity kept; days overlaid to find through-lines; frozen parameters treated as variables, never as verdict machinery.

---

## VERDICT (one paragraph)
The program is execution-honest and design-unfaithful. The population dimension of the ask survived everywhere: all four coins, full listing history, weekends in, 185,452 events, 585,176 vantage rows, no sampling, n beside every number, deviations disclosed, bugs voided and rerun. The granularity dimension died everywhere, always at the same step: the moment "bars" and "readings" became a formal object (a table schema, a feature list, an outcome definition), they became scalars, short words, or binaries — at design time, inside the preregs themselves, so every downstream scope ledger passed honestly while the ask was already gone. No table in either pack stores a single bar-by-bar record of anything. The sequential axis The System needs has never existed in this program.

---

## §1 — ORDERED vs BUILT, axis by axis (BRUTEFORCE_DESIGN.md is the order of record)

**Axis 1 — "vantage grid... every event re-expressed as a row per vantage it passed through."**
Ordered as ~24 vantages both directions. Built (b1_vantage.py): 11 fixed stations, direction folded into orientation. Each station keeps ONE forward summary (fwd_favU, fwd_advU, fwd_endU over the next ≤100 5m bars). Partial fidelity: a discretized, 11-point sample of "standing at every bar," with the path between stations discarded.

**Axis 2 — "the system's parts (~15), each a conditioning column."**
Built as ordered — but as snapshots. 19 base FE columns (b2), +6 B0 columns (b4), = 25. Components entered as their value at event time. Faithful to the letter of Axis 2; the per-bar reading idea was never in this axis's wording, which is where it got lost.

**Axis 3 — "the combination ladder, complete... no seeding."**
Fully faithful, and then some: d0–d5 + widened + W1 + W2 = 428,041,894 cells/family at the W2 finalize, exact binomial p, exact BH q=.10, scipy-validated to 1e-15, extinction honestly logged. This is the axis the machinery was built for, and it consumed the program.

**Axis 4 — "the prior 100 bars on 5m/15m/1h/4h/1D (path, states, volume, prior zone interactions) as conditioning features — and the reaction measured 100 bars forward on each frame."**
THE COLLAPSE. Built (b1t2_mf.py): per frame, the 100-bar lookback becomes 7 scalars — net100, net20, rng100, pos100, volr, zt100, zlast — and the 100-bar forward becomes 3 scalars — fav, adv, end (+fnb length). ~1,000 bars of context per row → 57 numbers. The bar sequences are computed transiently and stored nowhere. The design's own phrase "as conditioning features" licensed this at design time; no contract caught it because every contract checked execution against the design, not the design against the words. CB13's own PASTE_BLOCK later admits: "Axis 4 was half-run: price got the 100-bar multi-frame treatment, the components never did" — and even price's "treatment" was 7 scalars.
W2 (the completion wave) gave components their journeys as: swing word = last 4 pivot tokens (HH/HL/LH/LL), slope word = 96 bars → 8 U/F/D characters, relation vs price {confirm/bear_div/bull_div/mixed}, 4 scalars (age, flips, dom, prev). ≈9 symbols per 100-bar journey. The ladder then reduced further (D-F): last-2 swings, last-3 slope segments. Frames per component (D1): most components 1D only (dtype, lean, yd_arch, ob55, pi), hayden 4h+1D (+uncertified 15m/1h variants), scen 15m only. "Per bar per TF per component" became "a couple of words per component on one or two frames."

**Axis 5 — "the reaction as a full profile: bounce probability AND bounce-size distribution · penetration-depth distribution · break odds · travel · return odds · time-to-resolution — the give-reaction curve, not a hold/break coin."**
Collapsed at the ladder: outcomes = bounce (fav≥.25U & adv<.25U) and through (adv≥.6U) — two binaries; W2 added b50 and fastres — two more. No distribution was ever laddered or stored per cell. Mitigation: the vantage table keeps fav/adv/end continuous per row, so per-cell distributions are RECOVERABLE by re-query — thrown away from the outputs, not from the raw. CB13's briefing already confessed this axis ("caught only when the user asked — OPEN").

**Nowhere in any design doc:** the overlay (days stacked), through-lines (recurring sequences), sequence matching, or a per-bar record of any kind. The closest artifacts to the desire are queue entries: "Path study — bar-by-bar 100-bar windows clustered into recurring approach shapes; specced in words, not run" and "Route study / W3 corridor — words only." The old program knew the gap and parked it.

---

## §2 — THE FROZEN-CONSTANT INVENTORY (parameters that became verdict-bearing without ever being varied)
The 0.6U example is real and is not alone. None of the following were swept in any study; several directly determine the money verdicts:

| constant | value | role | where |
|---|---|---|---|
| stop distance / R-unit | 0.6·uAbs | stop AND risk unit in ALL THREE money tests | mm1/1b/3 preregs |
| break line | edge ± 0.6U | entry trigger (1b), B-line (mm3), card break-trigger | preregs, START_HERE |
| target | next wall's proximal edge | variable distance vs FIXED 0.6U risk → structural R:R lottery (the 0.5-RR trades) | all three engines |
| bounce threshold | 0.25U fav, <0.25U adv | the "bounce" binary | b2 onward |
| through threshold | 0.6U adv | the "through" binary | b2 onward |
| false-break window | 6 bars (30 min) | the 60.2% headline | p2.py |
| flip criterion | 0.25U onside within 12 bars | the 7.3% flip headline | p2.py |
| cool-off | 0.5U post-stall / 0.25U post-touch | event population itself (311→158 in P1) | p2.py |
| proximity band / stall reversal | 0.25U / 0.25U | what counts as an approach | p2.py |
| wall cluster radius | 0.25·uAbs | zone construction (Svet says locked — fine) | mm1/m9b |
| retest cap | 3 per parent | retest layer depth | p2.py |
| forward window | 100 bars; station search 289 bars | reaction horizon | b1 |
| time exit | 08:00 ET boundary | money-test exits (5,387 of 15,716 mm1 exits are 'time') | preregs |
| one-trade-per-wall-per-day, one position per coin, stop-priority | conventions | trade population | preregs |
| queue/model constants | K=75/K=40 KNN, 2×ATR OB stops, LR C=1.0, HGB lr=.08 | forecasters/ports | engines |

The 0.6U stop was justified by citing "the banked 79%-continues line" — recycling P(continue | penetration ≥ 0.6U) as a risk-unit choice, a category error: a continuation probability says nothing about optimal stop width. MAPMONEY-3's own results name the untested fixes (wider R so the 13.5bp toll shrinks in R-terms; day-type gating; maker fills) — none were ever run. V3_CONTRACT rule 2 explicitly banned unmeasured constants defining geometry; the money preregs then hard-coded 0.6U with a "banked" citation, satisfying the letter and violating the point. Conclusion the packs support: "geometry isn't there" as recorded means "not at exactly this one frozen geometry, after ~13.5bp, at these thresholds." Nothing more.

---

## §3 — LIVE DEFECTS FOUND IN THIS PASS (beyond the design question)
1. **The ~86% retest number is wrong vs its own artifact.** p3_t1.json retest_occurrence = 0.677. "~86% of breaks get retested" appears in MAP_V3.md, P3_READINGS.md, START_HERE v6 composition laws, and on live daily cards tagged [bank]. RUN_STATE flags it "unresolved, flagged not rewritten" — yet it still feeds cards every morning.
2. **CB13 ships the stale atlas.** 04_KNOWLEDGE/atlas_cells.csv = 2,781 rows, 2 families (built 07-24); the BF pack holds the superseding 3,165-row, 4-family v2 (built 07-26). The daily ritual's "atlas brain" cites the old one.
3. **W2's forecast verdict is premature.** w2_state.json ends at phase "finalize"→b5; no b5w2 scores exist in either pack; the run was 478/950 fits at last report with 4h and 1d never run — yet one chat's handoff already graded W2 "closed; forecast negative." Even if the partial 5m result holds, the blanket verdict outran the data — the satisficing pattern, inside the record itself.
4. **"LOST" that isn't.** The research chat's inventory declared mm1/mm1b/mm3 trade files lost; all three are alive in CB13/03_EVIDENCE and verified this pass: 15,716 / 4,492 / 13,946 rows, headline means reproduced (−0.0089 / −0.099 / +0.0227).
5. **w1_summary divergence.** CB13's copy carries "d4 not_run" rows and a reconstruction note; the BF copy dropped them. Minor, but the packs disagree about what a summary contains.
6. **B5-W2 negative can't be interpreted even when complete** — it tested component journeys only after the word/scalar compression, so it cannot distinguish "journeys carry nothing" from "the encoding destroyed the information." The new project's per-bar record is the only way to break that tie.

---

## §4 — WHAT WAS DONE FAITHFULLY (the other side, on the record)
Full population everywhere; weekends always in; no sampling anywhere; n beside every rate; UNDERPOWERED re-queued, never concluded; every deviation disclosed in-message; three outcome-leaks of one class caught and removed; two engine bugs voided WITH quarantined-unread outputs and clean reruns; vendor drift detected and never absorbed; DON55 port gated 495/495 exact to 1e-11; hayden machine D-A validated 1.000/1.000/0.997/1.000 after an honest failed first attempt; alien-lineage files quarantined and disproven by content (fastres .5397 vs sealed .5395282787); everything deterministic and regenerable with recorded commands and one seed. Execution honesty is genuinely high — which is exactly why the loss stayed invisible: the ledgers audited the run against the design, and the design was already the collapsed object.

---

## §A — INVENTORY LEDGER (verified counts)

### A.1 BRUTEFORCE_COMPLETE.zip — 80 files, ~63MB uncompressed
Docs (18, all read to EOF): RUN_STATE.md (project memory, 18.2K) · BRUTEFORCE_DESIGN · MAPV3_DESIGN · P1_SCHEMA · P2_LEDGER · P3_READINGS (n-corrected) · P4_FORECAST · MAP_V3 (n-corrected) · MAPMONEY1/1b/3 preregs + 1/3 results · B0_PORTS · B5_HANDOFF · W2_SPEC · V3_CONTRACT · CONTRACT_AUDIT.
Code (24, all read to EOF): fetch_arch.py (Binance Vision monthly + API tail, sha-logged) · mm1.py (wall builder + hayden machine + fade engine) · p2.py (event extractor, exec-patches mm1 head) · p3.py (T1/T2/T3/transitions) · p4.py (HGB forecasters) · b1_vantage.py · b1t2_mf.py (the Axis-4 scalars) · b_join.py (B0 join, no-lookahead rules) · b2_ladder.py · b3_ladder_d34.py + b3_assemble.py · b4_count/p/write/assemble.py · b5.py (frozen W1 prereg) · w2.py (475 lines: shape/relation/scalar encoders + rings + finalize gate) · w2fin.py (superseded) · w2fin2.py (bucket finalize) · atlas_build.py · atlasw2.py · b0a_ob55.py · b0b_dtype.py · b0e_scen.py · 4 pycache (structural).
Data (verified): bf_vantage_ALL_5m.parquet 585,176×28 (station counts: edge 72,134 … beyond_1.0 16,079) · bf_ladder_d012.csv 76,766 · d34_digest 800 · b0x_digest 1,134 · extinction d34 4,845 / b0x 10,240 · w1_digest 1,202 · w1_extinction 86,555 · w2_digest 831 · w2_extinction 712,775 · w2_summary 12 (428,041,894 cells/family; cert counts match RUN_STATE) · b5_scores 950 (medians reproduce: 5m .0565/.0992 at 95/95; 4h ~0; 1d −.028/−.027) · b0_ob55_state 8,478 · b0_dtype 6,208 · b0_lean 6,208 · b0_ydarch 11,694 · b0_states 11,698 · b0_scen_defs/events 9,094 each · p3_t1.json (retest_occurrence .677) · p3_t2 9,814 · p3_t3 559 · p3_transitions · p4_scores.json · atlas_cells.csv 3,165 (families: through 1,572 / bounce 1,396 / fastres 123 / b50 74; sources d012 2,058 / b0x 567 / w2 384 / d34 80 / w1 76) · atlas_data.json 3,165 cells, built 07-26 · ATLAS.html 556K self-contained · fin_bases / fin_tstar2 (exact, match RUN_STATE to 10dp) · w2_state.json (phase finalize) · w2_sample_SOL.csv 11 rows (clean D2 sample) · trunc_rows.json (71 rows). No alien-lineage files present in this pack version.

### A.2 CB13_CONTINUATION_v3 — 72 files, ~32MB
00 README · 01_DAILY_SYSTEM: START_HERE (runbook + v6 composition laws) · RUN_BRIEF (v4 ritual + Track B gates) · AI_HANDOFF (constants, defects, failure modes F1–F9 referenced) · CB12_PROTOCOL · CB12_6_DESIGN · CONTRACT_AUDIT · DAILY_README · run_day.py · brief_engine_v4.py (805 lines: KNN day-type, weekly KNN, Option B replay, direction rules, scenarios, drift-guard, sizing) · m9b_daily.py (self-fetching wall builder, 3 fixes annotated) · m9_emit.py (older CB9 emitter, /home/claude/p2b paths = legacy) · score_zones.py + hold_morning.pkl (CATS coin/hayden/hayden_btc/btc_pi; 11 NUMS; 6 BOOLS — ex-ante only) · CB12_6_copilot (chart) · CB12_6a (pane) · CB12_copilot.pine (scenario voice) · cb12_4 payload examples 07-22/23/24.
03_EVIDENCE: all Map-v3/MAPMONEY docs (byte-identical to BF except older P3/MAP_V3 n-attribution) + mm1_trades 15,716 · mm1b_trades 4,492 · mm3_trades 13,946 · mm results jsons · port validation · p1_events_SOL 158×61 (RETEST 53/STALL 36/BREAK 24/TOUCH 24/PEN 16/TRAV 5) · INDTEST_RSIDIV prereg+results (divergence reading +6–12pp, 7/8 FDR; money dead vs placebo) · 3 PNGs (system map; fade-vs-chase R distributions; MAPMONEY chart illustration).
04_KNOWLEDGE: ATLAS.html + atlas_cells.csv 2,781 (STALE) + MAP_V3 (older n).
05/06: V3_CONTRACT · CB13_PLAN_and_REMAINING (Path/Route/W3 queued as words) · INCOMING_FINDINGS_PROTOCOL · W2_SPEC (older typographic variant) · PASTE_BLOCK.
brief_state.zip: 33 files — per-asset 1d/4h pkls + sess csvs (S1 lineage) · direction_log_v4.csv 27 rows (graded outcomes present; no dtype column, as flagged) · trackB_log.csv 3 rows (2 graded no-trigger, 1 open) · wk_forecasts.csv W30 frozen ×4.

### A.3 Nested BRUTEFORCE_COMPLETE_post_B6.zip (inside CB13/08) — 81 files
= the outer BF pack as of 07-24, PLUS the four per-coin p2_events CSVs (BTC 50,004 / ETH 50,256 / SOL 35,206 / XRP 49,986 — the full event ledgers ARE in Svet's possession) and gha_bundle/ (grind1.py, w1_grind.yml, w2_b5.yml, SETUP.md, README_GRIND.md, b0 csvs, bundle scripts). MISSING vs outer (post-B6 work): W2 wave outputs, atlasw2, w2fin*, B5_HANDOFF, fin_* files, v2 atlas.

### A.4 What exists in NO pack (relevant absences)
Any bar-level table (bar_relations 39M rows — other chat, "in NO zip") · bf_vantage_ALL_mf / _wide / bf_w2cols / ladder full parquets (size law, regenerable) · b5w2 scores/model · the level-map program's M1_state/board_v2/etc. (paths reference /home/claude/p2b — a dead workdir) · Option B rulebooks/bt.py/ob_trades_S1 (referenced at /mnt/project, not shipped) · p2_events_ALL merged file (per-coin copies exist).

---

## §5 — WHAT CARRIES INTO THE SYSTEM (machinery, behind re-validation gates) vs WHAT DOES NOT
CARRIES (rule 8: re-check, then reuse): fetch_arch data pipe + drift law · the zone/wall builder (Svet's locked logic, port-gated wall-for-wall) · the hayden state machine (mm1 verbatim, D-A 1.000) · p2's event state machine as a component (events become anchors inside the per-bar record, not the record) · B0 component series with their honesty labels (dtype PROVISIONAL — no sealed reference exists; yd_arch and scenario arming are ratified decisions, not recoveries) · exact-binomial + exact-BH machinery · the runner slice-loop pattern · the atlas single-file phone rendering pattern · the daily ritual chassis (packet → engine → payload → Pine) as the Daily Analyst's delivery skeleton · hold_morning.pkl as a baseline forecaster to beat.
DOES NOT CARRY as knowledge: every ladder cell, digest, atlas rate, banked constant, graveyard verdict, and the v6 composition laws (chase ban, fade rules, virgin rules, homecoming/retest lines) — all downstream of frozen-geometry tests and event-level summaries; LEGACY-UNVERIFIED until re-derived from the per-bar base layer.

## §6 — THE ONE-LINE ANSWER
Effort was maximal, honesty was high, and the aim was off by one axis: the program brute-forced the combinatorial dimension to 428 million cells while the temporal dimension — the sequence of readings your System is made of — was compressed to 57 scalars and nine-character words at design time and never stored once.
