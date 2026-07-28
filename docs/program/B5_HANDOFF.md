# B5_HANDOFF.md — finish B5-W2 in this chat. BINDING. Read fully before any action.
# Written 2026-07-26 by the session that ran the W2 wave. Svet's standing operating
# rules apply on top of this document; where they conflict, Svet's chat wins.

## MISSION (the whole mission — nothing else)
Implement, run, and score **B5-W2**: the walk-forward forecaster rerun on the
W2-augmented table, per W2_SPEC.md section "W2-B5" (D5). Deliver the skill strip
beside W1's, log to RUN_STATE.md, return the updated living zip. Then stop.
You are NOT asked to: analyze beyond the required numbers, rerun the ladder,
re-finalize, touch the atlas, propose trades, or modify anything live.

## STATE YOU INHERIT (verified 2026-07-26)
- W2 extraction / ladder L1+L2+L3 / exact finalize: COMPLETE. m=428,041,894 cells/fam,
  t* = bounce .04093, through .06155, b50 .02558, fastres .07246 (BH q=.10, wave-set).
  Artifacts w2_digest/extinction/summary.csv (shas 34dfccfd / 2ec4008d / 62f03882).
- Everything lives in the PUBLIC repo: https://github.com/pejcicns91-maker/Cb13
  (clone --depth 1; if checkout times out mid-clone, `git restore --source=HEAD :/`).
  Contains: "gha bundle.zip" (NOTE THE SPACE — `unzip -n "gha bundle.zip"`) with
  fetch_arch.py / b1t2_mf.py / b_join.py / b5.py and inputs; w2.py; w2_counts/ (the
  full register counts); w2_state.json (phase may read stale "L3 699400" — IGNORE,
  the ladder is done; counts on disk are the only cursor, never a state file).
- b5.py = W1's forecaster. ITS HEADER IS THE FROZEN PREREG: same model family, same
  params, same walk-forward monthly protocol, same Brier-vs-base scoring. Replicate
  it exactly; ONLY the feature set changes.
- b5_scores.csv (W1 baseline) is in the repo — the comparison target.
  W1 headline: 5m skill .0565/.0992 (bounce/through), 95/95 positive months; 4h null; 1d negative.

## PREREG FOR B5-W2 (decided HERE — do not re-open)
1. PRIMARY: families bounce + through, all five frames (5m/15m/1h/4h/1d) — apples-to-apples
   with W1. SECONDARY (optional, separate table, never blended): b50, fastres.
2. FEATURES = W1's exact feature set PLUS the W2 columns encoded as:
   - relation cols (*_rel, hay_cross_1d, dv_last_*): one-hot (<=4 levels each)
   - shape words: PER-POSITION decomposition, never raw words — each *_sw word ->
     up to 4 positional token cols (4 levels: HH/HL/LH/LL/na), each *_sl word ->
     8 positional cols (3 levels: U/F/D/na). No column with >8 one-hot levels.
   - scalars (*_age, *_flips, *_dom, *_prev, dv_bull_*, dv_bear_*, dv_ago_*):
     quartiled then one-hot, na its own level.
3. Sparse matrices mandatory (scipy CSR; pandas get_dummies(sparse=True) or hashing
   is NOT allowed — deterministic explicit columns only). Seed 20260723 everywhere.
4. Table build: wide table via bundle scripts (cached on runner under key w2-v1-),
   W2 columns via `python w2.py --coin BTC` etc. then the assembly path (parts ->
   bf_w2cols.parquet). Provenance rule is PERMANENT: before reusing ANY part/table,
   check naming+schema (`psw_5m` present, nothing starts with `w2_`, 100-140 cols);
   unknown-provenance files -> quarantine, never absorb, report same message.
5. Deliverables: b5w2_scores.csv (month x frame x family, Brier skill vs base) +
   a comparison strip vs b5_scores.csv (per frame x family: W1 skill, W2 skill,
   delta, % positive months — frequencies with n, NO verdict words) + model file
   only if skill improves (D5) + RUN_STATE.md entry + rebuilt living zip via
   present_files. Skill improving or not are both valid endings; a null closes the
   wave exactly as a positive does.

## HOW TO RUN IT (hard-won; do not rediscover these the expensive way)
- Local box: 4GB RAM, 1 core, ~19GB effective disk quota. Full-table sparse fits do
  NOT fit locally. Build + unit-test the encoder locally on one coin slice; the full
  fit goes to the RUNNER (16GB, 4 cores, unlimited minutes — repo is public).
- Runner persistence law: NEVER end-of-job-only saves. Three ~5h runs died to
  cancellation exactly at the last step. Use the proven slice-loop yml pattern
  (see .github/workflows/grind.yml in the repo): a for-loop of
  `python <driver> --budget-min 26` followed by git add/commit/push of state+scores
  EVERY slice, `|| true` on every git line, `if: always()` where applicable.
  Commit only small files (state json + scores csv). Driver must be cursor-resumable
  with the cursor derived from committed outputs where possible.
- pandas 3.0 datetime trap (struck 4x): always
  `.to_numpy(dtype="datetime64[ns]").astype("int64")` — never .view, never raw
  .astype on datetime columns.
- pip on this box: `--break-system-packages`.
- GitHub yml gotchas that already burned runs: no `${{ }}` inside `{}` one-line
  `with:` maps (expand to multi-line); workflow_dispatch inputs are unreliable —
  hardcode behavior, don't branch on inputs.
- Svet is phone-only (Safari), terse, and has been through nine circles of runner
  hell already. Full-file pastes only (never "edit line 12"), tap-by-tap
  instructions, one thing per message, batch results.

## GUARDRAILS (the "don't hurt the project" clauses)
- FROZEN, never touched by this chat: Option B / rule v1.2 / sizing, brief_engine
  and all brief protocol files, brief_state.zip and any living-state pack zip,
  the level-behavior map, w2_counts semantics, prior registers and their shas.
- Reading layer only: report frequencies with n. No verdict words, no promotion,
  no "edge", no trading suggestions. Anything that looks alive is a CANDIDATE and
  goes no further than a sentence saying so.
- No silent scope changes. Any deviation from this doc or the prereg is surfaced
  in the same message it happens.
- Destructive/irreversible (deleting repo content, overwriting living-state zips,
  superseding manifest entries): echo back the exact order in plain words, wait
  for one yes. Everything else inside this mission: just do it and show results.
- If something in the repo or environment contradicts this document, STOP and say
  so — do not reconcile silently. RUN_STATE.md in the living zip is the project's
  memory; append, never rewrite.

## ACCEPTANCE
Svet receives: b5w2_scores.csv, the W1-vs-W2 comparison strip, RUN_STATE.md entry,
updated BRUTEFORCE_COMPLETE.zip. Wave then CLOSES with the scope ledger
(EXAMINED / REMAINING / DROPPED — itemized or "nothing"). The atlas w2-layer merge
remains a separately queued item unless Svet says otherwise in that chat.
