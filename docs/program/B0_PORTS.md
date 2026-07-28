# B0 PORTS — engine components as full-history conditioning series (2026-07-23)
Artifacts: b0_ob55_state.csv · b0_dtype.csv · b0_lean.csv · b0_ydarch.csv · joined b0_states.csv.
Join into the ladder FE happens at the next tranche (B4); until then these are series, not cells.

## A — Option B DON55 state — ADOPTED (gate: MATCH)
Replay of bt.py frozen conventions on the state-zip 4h pkls (proved to BE the S1 frames:
entry/exit bar indices integer-identical). Gate: all 495 DON55 trades vs ob_trades_S1.csv —
entry/stop0/tgt/atr/R exact (<=1e-11), flags exact. Known-unreproduced: R_A column (cost tier
differs from 'stress'; not gate-relevant, flagged). Series: ob55_open / ob55_fired at 08:00 ET
per ob_state semantics, 2020-10 -> 2026-07-23; open-day frac .209, fired .119.

## B — daytype — PROVISIONAL-PORT (two-path gate PASS; no sealed reference exists)
As-of walk-forward replay of forecast(): S truncated to date<d, D to <=d, at0900=True,
engine-native inputs (sess csvs + 1d pkls) + local 1h resample for overnight. Generator =
vectorized reimplementation; validator = the engine's own forecast() (imported, data layer
patched) on 68 seeded coin-days incl. 07-22/23: 68/68 label+U identical. DISCLOSED:
direction_log_v4.csv carries NO dtype column — the sealed logs cannot gate this port.
RECOMMENDATION: add dtype to log_and_grade so future days harden the gate.
Coverage: weekdays post-WARMUP (first non-na 2022-01-11); weekends/early = na.
Dist: normal .938 / QUIET .037 / EXPANSION .025 (structurally rare tails by construction).

## C — lean (A6b chain) — ADOPTED (sealed-log gate 8/8 PASS)
direction() called directly (engine code, zero translation) per coin-day with: NDX prior-day
return from the S1-lineage cache (OBUS100_1d.pkl), on_pos from B, ob_open55 from A;
dxy=None (note-only), is_fomc=False (f4x is note-only; historical FOMC does not alter
dir/strength/basis). Gate: all 8 sealed crypto lines 07-22/23 reproduced exactly.
NDX DRIFT (law): fresh-pull check fired — 1 row, 2026-07-22, |dC| 0.433% (the vendor
re-print you flagged). Detected, reported, NOT absorbed; cache stays the source.
Dist (non-na): down .516 / up .451 / none .033; basis mostly A6b, 261 OB-state days.

## D — yd_arch — DEFINITION-BY-DECISION — RATIFIED by Svet 2026-07-23 (historical written definition supersedes on sight)
No written definition exists in project knowledge (confirmed). Decided rule, logged here:
per UTC day on daily OHLC (weekends in): eff=(C-O)/(H-L); UP if eff>=+0.5, DN if eff<=-0.5,
else CHOP; yd_arch(d)=class of d-1. One parameter (0.5 = close in outer half of range in the
net direction). NOT an engine port. Any competing historical definition supersedes on sight.

## E — armed-scenario state — NOT STARTED (own checkpoint, per order)

## E — armed-scenario state — DONE (construction engine-exact; arming = PROTOCOL-BY-DECISION)
Construction: engine scenarios() logic, self-gated per day by payload-frag string equality vs the
imported engine function — 0 mismatches over 9,094 scenario rows / ~4,712 coin-days (2022-01+ weekdays).
Sealed gate (thin, disclosed: only 2 trackB rows exist): 2026-07-22 SHORT trig 77.50 RND lean-down and
2026-07-23 LONG trig 77.97 PDC (tgt 78.54 = sealed band start) — both exact. ARMING PROTOCOL-BY-DECISION
(2026-07-23, RATIFIED by Svet 2026-07-23; historical written definition supersedes on sight): 15m closes in (09:00 ET, 14:00 ET]; LONG arms close>trig, SHORT
close<trig, FADE close>=trig; armed->failed on close beyond inv; armed->hit on close beyond tgt; no
pre-arm death; no re-arm; all die 14:00 ET. Final-state dist: hit .352 / pending .338 / failed .232 /
armed-at-death .078. Artifacts: b0_scen_defs.csv (sha 2cebe2ee) + b0_scen_events.csv (sha edf00891).
