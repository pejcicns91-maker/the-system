# EPISODE SPEC v0 — the outcome layer at full sequence (SIGNED: Svet's go in chat, 2026-07-28)
Governed by rules 1–10, PHASE_CONTRACT v1.1, RECORD_SPEC v0. Joints 1/2/3/5 approved as designed; joint 4 amended by Svet's word: the alternating-excursion ladder ships as a third table in v0 — stop×target ORDER questions must be answerable from shipped tables, same-bar ambiguity counted, never guessed. Built by jobs/e1_episodes.py; situation-language only — this layer is what makes trade language legal later.

## 1. WHAT ONE ROW IS
One row of EPISODES = one level-touch episode: the ordered story of one ET period mark's first touch of the day, from the touch bar to the end of its 08:00→08:00 ET window, told on 5m bars in raw dollars and UTC timestamps.
Key: (coin, wdate, mark, price, t0) — IDENTICAL to the Layer-B anchors (b2_offsets (b)-line: anchor = first 5m bar whose range contains the ET mark, per coin-day). Episodes EXTEND the anchors; the anchors file is untouched and joins 1:1 by key. Nothing about the touch definition is new.

## 2. ROW COUNTS, MULTIPLIED OUT
EPISODES = the anchor population exactly: BTC 16,657 · ETH 16,507 · SOL 16,242 · XRP 16,237 = **65,643 rows**, one per anchor, zero added, zero dropped. 37 columns ≈ 2.4M cells.
EPISODE_PATH (long) = one row per (episode × other same-day ET mark first-tagged in the window). Ceiling 19/episode; actual count is a ship-time output, reconciled and printed.
EPISODE_EXC (long, the joint-4 ladder) = one row per new running-extreme event per entry basis: every time the running favorable or running adverse excursion strictly extends, one row (side, raw extreme price, bar timestamp). Two bases: fade-at-touch (always) and enter-at-retest (iff a retest exists). This event sequence is threshold-free and COMPLETE for order questions: for any stop distance s and target distance t, first-hit times are read off the staircases; equal timestamps = the same 5m bar = AMBIGUOUS, a counted third outcome, never a coin flip. Actual row count is a ship-time output, reconciled per episode.
Named sub-populations (facts, not filters — all rows ship): never-traded-beyond 154 (0.2%) · touch-on-day-open ~28%/coin (same-day approach fields null) · no-retest · held-to-close · final-partial-day truncations · gap-through exceptions (listed one by one) · same-bar both-sides event pairs (entry-bar structural pairs counted separately from interior pairs).

## 3. THE THREE TABLES
**EPISODES** (wide, fixed schema) — one row per anchor.
**EPISODE_PATH** (long) — the level grid as its own ruler: key · seq · path_mark · path_price · first_tag_at, time order.
**EPISODE_EXC** (long) — the excursion ladder: key · basis (fade|rt) · seq · side (fav|adv) · px · at.
Adding a story fact later = adding a column (S2); adding a grid or a basis = adding rows.

## 4. EPISODES COLUMN CENSUS (raw dollars + UTC timestamps; no thresholds stored; distances and labels by subtraction or join, never duplicated)
KEY (5): coin · wdate · mark · price · t0. Everything the anchor stores (open_side, pen, rev_after, closeback, atr1d, uabs, play_atr) stays in anchors_ and arrives by the 1:1 join — never copied.
SETUP (9): approach_local_close (last 5m close before t0; null = opened into it) · prior_mark_name / prior_mark_price / prior_mark_at (most recent pre-t0 bar tagging a different-PRICE same-day ET mark; on a multi-mark bar the mark nearest in price to this episode's mark, names at that price joined by '+'; null = none) · tie_count (marks at EXACTLY this price — parameter-free; radius-confluence stays a query-time label with parameters) · corridor_up_name / corridor_up_price · corridor_dn_name / corridor_dn_price (nearest same-day ET marks strictly above/below; names at the corridor price joined by '+'; gap widths = subtraction, not columns).
ORDERED STORY (12): first_trade_beyond_at · first_close_beyond_at · bounce_ext_price / bounce_ext_at (bounce-side extreme BEFORE first_close_beyond; whole window if never closed beyond) · max_cont_price / max_cont_at (extreme beyond, from first_trade_beyond to window end) · retest_touch_at (first tag of the mark after first_close_beyond) · retest_ext_price / retest_ext_at (extreme against the break, retest touch → reclaim close inclusive, or window end) · reclaim_close_at (first close back on the original side after retest touch; null = held to window end) · travel_after_price / travel_after_at (continuation-side extreme from retest touch to window end).
ENTRY BASES (8): fade_mae_price/at · fade_mfe_price/at · rt_mae_price/at · rt_mfe_price/at — the ladder's endpoints, kept for join-free reads; each MUST equal its basis's terminal staircase value (internal gate).
CLOSE/FRAME (3): day_close_price · day_end_at · bars_in_window.

## 5. CONVENTIONS (named, not parameters)
Tag = bar h ≥ price ≥ l. Beyond = STRICTLY past the mark on the far side of open_side (inherited). Close-beyond / reclaim = close STRICTLY past. Story grain = 5m, the record's finest. Excursion event = the running extreme strictly extends; the entry bar seeds one fav and one adv event by construction (structural pair, counted separately). SAME-BAR LAW: facts on one 5m bar carry equal timestamps; seq breaks equal-at ties by a stated fixed order (adv before fav; path by name) that carries NO within-bar meaning; every order-question resolving inside one bar is AMBIGUOUS and counted. NULL LAW: null = the stage never happened, populations named, never padded. GRID LAW: corridor and PATH use the same-day ET period marks — the anchors' own grid; pivots/VA/scenario marks join at query time. Retest is defined off first CLOSE beyond; the trade-beyond variant is a re-query of BARS, which remain complete. Window end = last 5m bar of the wdate + 5min; the final partial day truncates there, counted.

## 6. WHAT IS THROWN AWAY
Nothing. Anchors, BARS, MARKS untouched; every label (broke, held, failed, deep, fast) derivable at query time with its parameters attached; anchor outcomes (pen, rev_after, closeback) must be REPRODUCED by this build, not replaced; longer horizons = query-time join to the following days' bars — the window is inherited from the anchor's day frame, not a new constant.

## 7. ACCEPTANCE (full population; any FAIL stops the ship)
a) EPISODES rows == anchors rows per coin; key join 1:1, zero orphans either side;
b) Gate A — anchors reproduced: pen, rev_after, closeback, open_side, t0 recomputed per the b2 algorithm from the record match the stored anchors for every row (≤1e-9);
c) Gate B — episode↔anchor reconcile: |price − max_cont_price| == pen and post-extreme reversal == rev_after for every row; the only licensed exceptions are gap-through days (a pre-t0 bar sits entirely beyond the mark — price crossed with no containing bar), each counted and LISTED with its gap bar, never absorbed;
d) Gate C — sign(day_close_price − price) vs sign(day open − price) reproduces closeback for every row;
e) Gate D — internal: MAE/MFE columns == EXC terminal extremes per basis; every timestamp inside [t0, day_end_at]; rt basis exists iff retest_touch_at exists; per-episode event counts sum to EXC table length;
f) Svet's eyes: the worked example (BTC · 2024-08-05 · PDC 51340.00) printed in the REPORT, narrated from the shipped row;
g) storage: results/episodes/ · parquet zstd per coin · append-only · REPORT.md with expected-vs-actual and every named population counted. Counts only; verdicts are Svet's.

## 8. SEQUENCE AFTER GATE
Re-run the B/C machinery against episode outcomes (outcome-agnostic — swap the weight vectors). Only after that may stop×target×situation cells speak trade language (v1.1) — and order questions answer from EPISODE_EXC, ambiguity counted. Triples stay locked behind Svet's signed design (contract item 3).
