# BRUTE-FORCE RUN STATE — checkpoint 2026-07-23 · post-B1-T2 · SELF-CONTAINED PACKAGE
Seed 20260723 everywhere. Contracts binding: V3_CONTRACT.md + CONTRACT_AUDIT.md (included).

## SETUP IN A FRESH SESSION (exact steps)
1. Unzip this package into /home/claude/mm1 (paths inside scripts expect this).
2. Refetch raw 5m data only when a step consumes raw (regen of mf/register, future re-bank):
   `python3 fetch_arch.py BTCUSDT 2017 8` · `ETHUSDT 2017 8` · `SOLUSDT 2020 8` · `XRPUSDT 2018 5`
   Old sha prefixes (BTC 1ac003e9 · ETH 303e70b0 · SOL 75e23943 · XRP d46b9eba) are IRREPRODUCIBLE by construction:
   originals ended mid-2026-07-23 at an unrecorded bar; any refetch appends. DRIFT TEST instead: re-run
   `python3 p2.py {SYM} {NM}` on refetched data sliced to the shipped event range and diff vs shipped p2_events_*.csv.
   Mismatch inside the overlap = vendor drift -> STOP, report.
3. Events (p2_events_*.csv) ARE included — no re-extraction needed.

## COMPLETED
- Map v3 P1–P5 (ledgers + MAP_V3.md) · MAPMONEY 1/1b/3 (results included)
- B1 tranche 1 (5m): bf_vantage_ALL_5m.parquet — 585,176 rows
- B2 depth 0–2: bf_ladder_d012.csv — 76,744 tested / 58,313 certified (sha 6b12f037)
- B2 depth 3–4 (2026-07-23): full grid C(19,3)=969 + C(19,4)=3,876 stacks × station, no seeding, n>=40 floor.
  7,271,277 cells/family · 14,542,554 register rows. BH q=.10 per family over the d3–4 set (per-run, as d0–2):
  bounce 2,663,906 certified (36.6%) · through 4,250,020 (58.4%). Bases: bounce .302 / through .299.
  EXTINCTION HAS NOT BEGUN: 0/969 d3, 0/3876 d4 combos extinct; cells/combo median d3 528, d4 1,482.
  Exact two-sided binom p vectorized; validated vs scipy on 500 seeded cells, max|diff| 3.66e-15.
  Artifacts: bf_ladder_d34_digest.csv (top-200 |rate-base| per family×depth among certified n>=100; sha 267cf43a)
  · bf_extinction_d34.csv (4,845 combos; sha 18e547b7)
  · bf_ladder_d34.parquet 121MB sha 4f477304 — NOT SHIPPED (size law, same as raw data).
    Regenerate deterministically (~5 min): `python3 b3_ladder_d34.py && python3 b3_assemble.py`
  Reading layer only per V3 contract: frequencies with n; d4 stacks are nested/correlated by construction.

- B1 tranche 2 (2026-07-23): multi-frame features on the FROZEN 585,176-row basis -> bf_vantage_ALL_mf.parquet
  (43.3MB, sha a35f4574, NOT SHIPPED under size law; regen: fetch_arch x4 then `python3 b1t2_mf.py`, ~8 min, deterministic).
  57 new cols: fwd fav/adv/end/fnb on 15m/1h/4h/1d (window = 100 F-bars starting AFTER the bar containing
  t_station; <5 bars -> NaN, fnb records length); lookback net100/net20/rng100/pos100/volr/zt100/zlast/lnb on
  5m/15m/1h/4h/1d (w=min(100,avail) completed bars, w<20 -> NaN); fwd5m_trunc flags the 71 tranche-1 rows whose
  5m forward window was cut by the original raw end (trunc_rows.json shipped).
  Coverage: fnb_1d full for 570,147 rows, short 5-99 for 14,488, NaN 541 (the last-100-days tail); all lookback
  windows full except 14,304 early-history 1d rows (w 20-99).
  Verification: 2 seeded rows (one per approach side, 12 features each) reproduced exactly via an independent
  integer-binning path; NaN-policy consistent on all frames; 85.9% of in-zone-station rows show zt100_5m>=1.
  INCIDENT (disclosed): first build was invalid — pandas 3.0 stores ms-resolution datetimes, and a ns-assuming
  conversion put every resampled-frame anchor at end-of-history. Caught by the independent verification BEFORE
  anything shipped; conversion made resolution-proof; full rebuild + re-verify. Nothing downstream consumed it.
- Determinism probes closed (all 4 coins): regen vs shipped basis — zero missing rows, all common rows identical
  except 71 tail rows (fwd fields, truncated windows) + 11 all-tail extra hits that stay OUT (frozen basis; they
  enter only at a future re-bank). Drift test PASS on all 4 (exact overlap, zero mismatches); raw shas at refetch:
  BTC ecd13052 ETH 1df68aad SOL d60e5cba XRP 1f96beea (live-tail; drift test is the standing verification).

- B0 ports A-D (2026-07-23): b0_states.csv (sha 871561e7, 11,698 coin-days) joins ob55_open/fired
  (A: ADOPTED, 495/495 exact vs ob_trades_S1; state-zip 4h pkls proved to be the S1 frames; R_A cost
  tier unreproduced, flagged), dtype (B: PROVISIONAL-PORT, two-path 68/68 vs engine code; NO sealed
  dtype lines exist in any log -> recommend logging dtype), lean dir/strength/basis (C: ADOPTED,
  sealed-log 8/8; NDX drift detected 2026-07-22 |dC| .433%, reported not absorbed, cache stays),
  yd_arch (D: DEFINITION-BY-DECISION eff=(C-O)/(H-L) +-0.5 on prior UTC day, pending ratification).
  Scripts b0a_ob55.py / b0b_dtype.py / b0_lean+ydarch inline; full doc B0_PORTS.md. Inputs: state-zip
  pkls+sess (reference copy, read-only) + refetched raw. FE join deferred to next ladder tranche.
  E (armed-scenario) DONE: engine-exact construction (frag self-gate 0/9,094), trackB sealed gate 2/2,
  arming PROTOCOL-BY-DECISION pending ratification; b0_scen_defs.csv 2cebe2ee + b0_scen_events.csv edf00891.

- RATIFIED 2026-07-23: definitions-by-decision #1 (yd_arch eff+-0.5) and #2 (arming protocol);
  historical written definitions supersede on sight.
- FE JOIN (2026-07-23): bf_vantage_ALL_wide.parquet (sha 25ca511e, NOT SHIPPED size law; regen
  `python3 b_join.py` after mf regen) = mf table + 6 B0 categoricals under no-lookahead rules
  (yd_arch UTC-day; ob55 last 08:00-ET snapshot; dtype/lean 09:00-24:00 ET brief day; scen live
  09-14 ET, dead 14-24 ET). ms/ns trap struck a THIRD time (join event times); caught by the
  distribution check, fixed resolution-proof.
- WIDENED LADDER (2026-07-23): all d1-d4 stacks with >=1 new column: 10,240 combos x station x
  2 families -> 12,488,746 cells/family, 24,977,492 rows. BH q=.10/family per-run: bounce
  4,679,961 (37.5%) / through 7,203,664 (57.7%). Extinction STILL zero (0/10,240; d4 cells/combo
  med 1,141). p-val vs scipy 5.0e-15 (200 seeded). Ground-truth spot-checks 2/2 combos exact.
  Artifacts: bf_ladder_b0x.parquet 212MB sha f3df295b NOT SHIPPED (regen: `python3 b4_count.py`
  x2-3 then `b4_p.py` + `b4_write.py`, ~12 min); digest sha 3b7d6b77 + extinction sha 567f81f6 ship.

- GHA BUNDLE PREPPED (2026-07-23, NOTHING RUN): gha_bundle/ — 21 flat files, all <25MB (phone-uploadable).
  W1 = d5-over-FE25 + t2-quartile d1-d3 (86,555 stacks; t2-d4 474,985 stacks opt-in b4=1,
  REMAINING-BY-PHYSICS with artifact-only storage law). W2 = B5 walk-forward forecaster,
  prereg binding in b5.py header. Chunked 200-combo blocks, cursor committed per block, cancel-safe
  resume; finalize mode does p/BH/register. Runner rebuilds raw->wide itself (pandas pinned 3.0.2;
  585,176-row check = env-drift tripwire). SETUP.md = Safari tap-by-tap, no CLI, no tokens. TRANSPORT: gha_bundle.zip ships SEPARATELY
  (57MB, every file <13MB); the living-state zip carries bundle docs/scripts only — its data files
  are byte-copies of root files (rehydrate: copy p2_events_*.csv + bf_vantage_ALL_5m.parquet into
  gha_bundle/). NEVER upload any .zip to GitHub — only the loose files inside gha_bundle.
  Execution and result adjudication return to chat.

- B5 ADJUDICATED (2026-07-24, runner output b5_scores.csv, 95 months 2018-09..2026-07, 950 rows,
  prereg followed): Brier skill vs base-rate, median (positive-month frac) — 5m: bounce .0565 (95/95),
  through .0992 (95/95); 15m: .0533 (.99) / .0683 (.98); 1h: .0233 (.83) / .0356 (.84);
  4h: ~.000 (.47-.54) = null; 1d: -.027/-.027 (.19-.25) = model UNDERPERFORMS base at 1d.
  Era decomposition stable (no regime flip; horizon gradient, not a regime marker). Caveats logged:
  row correlation within events; reaction-shape skill != money (right-but-unpaid law); no conflict
  with the direction-unforecastable verdict (these are approach-conditioned reaction shapes).
  STATUS: reading-layer finding; NOT promoted; any money use requires its own sealed prereg through
  the v1.2 chain (independence vs Option B first).

- W1 ADJUDICATED (2026-07-24, runner finalize #13): 145,347,303 cells/family over d1-d3(t2)+d5(FE25);
  register regenerable from committed out_counts (storage law). CERT RATES THIN MONOTONICALLY:
  bounce 86.6/70.1/51.0/29.0% and through 92.1/83.5/71.0/50.9% at d1/d2/d3/d5 — certification decay
  is the real frontier. EXTINCTION HAS STILL NOT BEGUN: 0/53,130 d5 combos extinct; min cells/combo
  204, p10 1,022, med 2,340 — the n>=40 floor sits far deeper than the design guessed (d7+ territory).
  t2 columns carry: 802/1,202 digest rows t2-involving; e.g. beyond_1.0 x recent-zone-touch
  (q_zlast_5m<=4) x range-quartiles -> through .991-.992 (n 107-127, base .299). Reading layer only;
  nested stacks correlated; per-run BH within this set. b4 phase (t2-d4, 474,985 combos) remains
  opt-in REMAINING. GHA loop proven end-to-end: grind -> finalize -> chat adjudication.

- B6 ATLAS BUILT (2026-07-24): ATLAS.html (0.49MB, phone single-file, filterable) + atlas_cells.csv
  (sha e070bcee, 2,781 rows: 528 parsimony-deduped stacks + 2,253 certified singles, 11 stations).
  Selection stated in atlas_build.py header: spine=d0; singles=all certified d1 n>=40; stacks=top-12
  per station x family per source among certified n>=100 from d012-d2/d34/b0x/w1-digest; dedup drops
  deeper cells within .010 of a shallower subset; cap 24. Spot-verified 3/3 rows vs source registers.
  Carries bases, B5 skill strip, frontier line, reading-layer banner. w1 layer limited to committed
  digest (full per-station w1 extraction possible from repo counts on request — stated, not dropped).

- W2 WAVE OPENED (2026-07-24, spec W2_SPEC.md pre-authorized D1-D6, logged; interpretations D-A..D-H
  in w2.py header). INCIDENT — INTEGRITY BREACH, contained: four w2part_*.parquet + a derived
  bf_w2cols.parquet of UNKNOWN PROVENANCE were found in the working dir (alien naming scheme w2_*,
  timeline impossible for this session's code; ladder refused them via pattern mismatch — "L1 combos 0").
  QUARANTINED to ./quarantine/, never entered any register. All five sealed artifacts re-verified
  against declared shas (d012 6b12f037 · b0_states 871561e7 · atlas_cells e070bcee · ob55 5dacf2ab ·
  d34 4f477304) — contamination bounded, program record intact. Environment treated as untrusted for
  unexplained files henceforth: provenance check (naming + schema) added before any part reuse.
  CLEAN REBUILD: SOL extracted fresh from audited w2.py (116 cols, my naming verified, 102s);
  D2 sample published (w2_sample_SOL.csv; TV check: SOL 1h bear regular div 4 bars before
  2026-07-21 08:10 UTC). D-A validation prints on SOL pass. REMAINING in-wave: BTC/ETH/XRP extraction
  (~2 min each) -> assembly -> L1/L2 in chat -> D4 check -> runner handover (L3+, B5, atlas merge).
  D6 yml handover DEFERRED one step until clean extraction completes end-to-end.

- W2 PROGRESS (2026-07-24 cont.): PROVENANCE RULE PERMANENT (Svet-ratified): any part/table reuse
  requires naming+schema provenance check; unknown-provenance files quarantine on sight. D2 gate
  PASSED (Svet chart-confirmed the SOL 1h bear div). INCIDENT #2, contained: D-A validation FAILED
  for the EMA(20) machine (0.615-0.636 vs shipped hayden states) -> real machine found in mm1.py
  (Wilder-RSI ohlc4, 67/33 entry, 39/61 decay), ported verbatim, D-A VALIDATED 1.000/1.000/0.997/1.000,
  all four coins re-extracted (EMA-based SOL part quarantined). Also disclosed: the in-extraction D-A
  check had silently skipped on a wrong path — earlier "prints pass" claim was wrong, corrected.
  Wave state: extraction COMPLETE (4 parts, provenance-guarded; bf_w2cols 110+ cols); L1 105 combos +
  L2 11,760 combos DONE in-chat, 4 families; D4 check: mean incremental lift +.269..+.381 per family
  -> L3 AUTHORIZED (new-involving triples, runner-scale). Storage law for L3: counts to cache+artifacts,
  commits = state + finalize outputs only. B5-W2 (sparse) + atlas merge queue behind L3 register (stated).

- W2 LADDER FINALIZED (2026-07-26, local streaming finalize w2fin2.py after runner-memory diagnosis):
  m=428,041,894 cells/family over L1(105)+L2(11,760)+L3(700,910) new-involving combos, 4 families.
  Exact BH q=.10/family via atom-safe histogram bracket + sliver enumeration; t* = bounce .04093 /
  through .06155 / b50 .02558 / fastres .07246. scipy equivalence: max |dp| 1.33e-15 over 31 sampled
  cells (sampling thinner than planned 200 due to sub-sliced paths — noted, not hidden).
  Artifacts: w2_digest.csv sha 34dfccfd / w2_extinction.csv sha 2ec4008d / w2_summary.csv sha 62f03882.
  FINDINGS (frequencies with n, reading layer): (1) EXTINCTION HAS BEGUN — first in the program:
  12/11,760 L2 combos and 1,890/700,910 L3 combos extinct (min cells 0) — the na-heavy trajectory
  columns thin the floor where W1 never did (0 extinct through d5). (2) cert thins with depth:
  bounce 67.8/51.5/40.9%, through 81.1/69.5/61.5, b50 41.6/32.4/25.5, fastres 86.0/78.6/72.4 at d1/d2/d3.
  (3) digest 831 rows, 100% w2-involving by construction; flavor: edge|TRAV x dtype-trajectory dominance
  -> bounce .962 (n 104-106, base .302); beyond_1.0|XRP x flat 1d-component slope words -> through 1.000
  (n 100-116, base .299 — perfect rates at n~100 flagged, possibility language only); edge|TRAV x
  hay_4h dominance -> b50 .913 (n 173, base .193); out_0.25|STALL x clustered 5m bull-divs -> fastres
  .009 vs base .540 (inversion reading). Correlated nested stacks; wave-BH; hay fast variants remain
  labeled uncertified per spec D1. REMAINING in-wave: B5-W2 sparse rerun (runner, implementation owed)
  + atlas merge w2 layer (needs per-station certified extraction pass from counts — digest alone is
  top-200 global, stated bound). fin2 caches pruned; counts live in public repo + local symlink.

- B5-W2 HANDED OFF (2026-07-26): continuation moved to a separate chat per Svet. B5_HANDOFF.md
  written into the living zip — binding prereg (families/frames/encoding/sparse/seed), environment
  facts (public repo, runner slice-loop law, 4GB local limits, pandas ns trap), guardrails (frozen
  systems list, reading-layer language, provenance rule, echo-back for destructive). b5.py recovered
  from bundle into the zip as the frozen W1 prereg; W2_SPEC.md reconstructed verbatim from the
  received spec document (upload had been cleaned — noted as reconstruction). Atlas w2-layer merge
  remains queued, unclaimed by the handoff.

- ATLAS W2 MERGE COMPLETE (2026-07-26): full per-station certified extraction pass over the w2
  register (32-range sweep, exact t* applied, top-3,000/family/range candidates, per-file string
  resolution over 3,236 fids). Curation per W2_SPEC: top-12 per station x family x source w2 among
  certified n>=100 -> 409 rows; 11/44 buckets legitimately thin (<12 certified above lift floor .046
  — stated bound). Parsimony dedup vs existing atlas dropped 25 -> 384 w2 rows kept. Merged
  atlas_cells.csv: 3,165 rows, sha 30412444 (supersedes e070bcee). ATLAS.html v2 rendered (0.56MB):
  4 families with bases (b50 .193, fastres .540), w2 source filter, updated frontier line
  (extinction begun). SPOT-VERIFY 3/3 PASS (rate/n/station/cert recomputed from counts vs t*).
  Intermediates pruned. W2 wave locally COMPLETE except B5-W2 (handed off to separate chat).

- PROVENANCE INCIDENT CLOSED WITH PROOF (2026-07-26, via B5 chat): certified table regenerated in the
  continuation environment reproduces sealed bases EXACTLY (b50 .1929915102, fastres .5395282787,
  delta 0.00e+00, provenance_ok True, 117 cols, 585,176 rows). The quarantined alien table's fastres
  mean was .5397 — it could never have produced the sealed base. Alien lineage now disproven by
  content, not just timeline. B5-W2 runner handover issued by the continuation chat under the
  persistence law (slice-loop, per-month driver saves, state+scores-only commits); Svet executing.

- QUARANTINE EXTENDED + DOC CORRECTIONS (2026-07-26, Svet-approved): six further alien-lineage
  artifacts found loose in the pack by the B5 chat's full-absorption pass and moved to ./quarantine/
  (w2_cols.parquet, w2_ring1.parquet, w2_ext_ring1.csv, w2_extract.py, w2_ladder.py,
  w2_sample_SOL20d.csv) — moved, never deleted. Source-level disproof now on record: w2_extract.py's
  perbar_slopes emits 7 chars (differences between 8 segment means) vs W2_SPEC/D-D's 8; its pivots,
  hayden transition order, relation rule and w2_hyconf semantics all diverge from the certified chain.
  NOTE my earlier L1=105/L2=11,760 fingerprint argument was NOT diagnostic (alien ladder is 60+105 too,
  identical by construction) — the decisive tests are column naming in w2_digest (0 w2_-prefixed) and
  the fastres base (.5397 alien vs .5395282787 sealed). CORRECTED: MAP_V3.md + P3_READINGS.md quoted
  reach-next 14% with n 66,237 (that n is retest_flip); true n 39,362. atlas_data.json regenerated
  (was stale at 2,781 cells/2 families; now 3,165/4). Unresolved, flagged not rewritten: docs say
  ~86% retest ("parent coverage") vs artifact retest_occurrence .677 — needs the source computation.
  B5 chat's C10 (531 vs 537 triples) and C3 (b4_assemble broken) did NOT verify: register shows
  531 certified True of 559 rows, and b4_assemble defines out at line 24.

## RESUME ORDER (each step ends with the scope ledger; "V3 CHECK" phrase binding)
1. Program CLOSED AT d5 (Svet, 2026-07-24). Recorded gap, not hidden: the registered 'until extinction' stopping rule never triggers at feasible compute (d5 min branch 204 cells; floor bites ~d8+; full power set 33.5M stacks). d6+, t2-d4, t2-d5+ NOT run — parked without a chosen stopping rule. Reopen only on explicit instruction with a new rule. Other open doors unchanged: full w1 extraction · money candidates via sealed prereg (independence vs Option B first). 2. Then: B6 atlas synthesis; any money candidate leaves via its own sealed prereg.
2. B4: depth 5+ until extinction; publish the frontier (d4 shows none yet — frontier is deeper).
3. B5: forecaster on full state (t2 columns now available), Brier per frame. 4. B6: the give-reaction atlas.
Run from /home/claude/mm1. Register queries: read bf_ladder_d34.parquet; t2 features: bf_vantage_ALL_mf.parquet (regen either if absent).
