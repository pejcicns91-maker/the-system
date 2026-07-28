# MANUAL 3 — AI HANDOFF (for any successor AI continuing this program)
*2026-07-09. Read LEVEL_MAP_CONTRACT.md + LEVEL_MAP_CONTRACT_v2.md FIRST — they bind you. This file is operational knowledge.*

## WHO YOU WORK FOR
Svet: systematic trader, phone-only, terse voice input. "Go" = execute the next owed item, never offer menus. He audits BY EYE: date lists + real-data charts + TradingView-checkable tickets — never raw stats. He erupts (correctly) at scope-shrinking. Read contract §4: failure modes F1–F9 are YOUR documented failure modes; the auditor checklist §9 will be run against you.

## ENVIRONMENT (as of handoff; verify before trusting)
Workdir `/home/claude/p2b` · 5m pickles `/home/claude/dt/m5/{SYM}USDT_5mv.pkl` (BTC/ETH/SOL/XRP) · U history `/home/claude/se/se_ref_uhist.csv` · witness `/home/claude/v5/v6_witness_days.csv` · project files `/mnt/project/` (Pine sources, brief engine, Option B docs) · deliverables → `/mnt/user-data/outputs/`. pip needs `--break-system-packages`. Key intermediates in workdir: `M1_state.parquet` (THE state table — start here), `approach_disp.npy`+`approach_events.pkl` (288-horizon intensity), `board_v2.csv`, `levels_daily_v2.csv`, `level_events_v4.csv`, `migration_v2.csv`, `c5_days/c6_wear/m2_grid/m4_columns/m7_vote/m85_walls.csv`, `daypaths.npz`.

## KEY CONSTANTS (baked, banked — do not refit casually)
Day window = 8am ET. Zone = level ± band (recorder spec). Deep-break = pen>0.60U (discovered). Thr terciles (vote frame, signed U): 0.0999/0.2303. Drive24 (h≈273 of 288): −0.0268/0.4959. am bins 0-2/3-7/8+. Hayden port: OHLC4, SMA-seeded Wilder RSI-14, 4H UTC bars, 67/33→61/39 state machine, witness anchor = **two 4H closes before 8am ET** (99.07% parity; residual = vendor vintage at crossings). Vote sign map: fast+1/rev−1/slow−1 · calm+1/mid−1 · few+1/many−1 · trend+1/lean−1 · wkday+1/wkend−1 · dens alone/1-2 +1. Escalation ladder & travel medians: in CB9/CB10 source.

## STANDING DEFECTS / OPEN ITEMS (do not lose these)
- **Brief version gap**: Svet expects v6.0 witness-board output; uploaded engine is v5.0 — unresolved.
- **se_ref_vec.csv hash mismatch** — unresolved; vendor-revision law applies (detect, never absorb).
- Parked on Svet: H-Div eye-card confirm · CB10 parity card check · CB4 Pine source · volume Pine source.
- M2c (yday-archetype triples on constellation pairs) — owed, small.
- F battery's T3/T4 audit tickets — sampler gap, owed on request.

## PROPOSALS DRAFTED, NOT RUN (need Svet's signature)
- **M10 Foreshadow Meter**: partial-path archetype matcher (match today's path-so-far, inherit remainder stats) + triangle-gate the PRE-touch 7-dial vote. Materials all banked.
- **F2 — the second battery**: size-gated (engage only on expansion-forecast days: p85/after-trend/vol-cluster), map-spot entries, foreshadow-graded (ladder rungs as entries, priced vs certainty), travel-sized brackets, **three cost rows (frictionless / spot-maker ~4bp / FTMO 13.5bp)**, full Triangle, his red-line on the construction sheet first. Rationale banked: F1 had no size gate, fed the toll on 54% churn days; breakeven ~53% at 2%+ captures.
- **M9b — GitHub automation** (marked, not built): repo with (1) Binance public-API fetcher (~40d 5m ×4 + 1000×4H bars), (2) day-builder lite (levels/zones/gaps/POC-runs/M2 scenario states — pure formulas), (3) the gated Hayden port, (4) archetype assign-only (frozen centroids), (5) m9_emit → CB9 lines, (6) GitHub Actions cron 8:00 ET (TWO cron entries for DST), delivery = repo commit + Telegram/email, (7) **kline hash-log per the vendor-revision law**. Irreducible residues: the TV paste stays manual (no TV input API); the phantom-wick eye-check (see m9_failure_illustration.png) cannot be automated — the runner ships a "verify walls vs chart" reminder.

## HOW TO NOT FAIL HIM (the compressed version of everything)
Declare mode + (b) line BEFORE running. Numbers before prose, always. Full history + era + Hayden + weekend + asset beside every stat, n on every %. Triangle on anything gated. Every delivery ships its date lists and ≥4 drawn charts. Never present owed work as options. Never call stability "out of sample". Never synthesize unmeasured probabilities. When your own output looks wrong — STOP and say so before he does; the confound catches (any-of-N walls, tie-corrupted order, broken placebo) bought more trust than any finding.
