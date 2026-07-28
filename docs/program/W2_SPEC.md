# W2 — COMPONENT-TRAJECTORY WAVE (the unfinished half of the order) · spec 2026-07-24
**Pre-authorization: Svet pasting this spec = GO for every phase below. All foreseeable forks are decided here (D1–D6). Do not ask questions whose answers are in this file. Stop only for a contract violation, a result-changing ambiguity NOT covered by D1–D6, or anything destructive. V3_CONTRACT + CONTRACT_AUDIT binding; scope ledger every phase; deviations same-message; seed 20260723; ms/ns guard mandatory (three prior incidents).**

## What this wave is
W1 gave price its 100-bar multi-frame history and it produced the atlas's best cell. **No system component ever got the same treatment** — they entered as snapshots. W2 extracts every component's trailing journey and crosses it through the proven ladder, per zone, per vantage. This is Axis 4 completed as Svet stated it.

## Inputs
Existing wide vantage table (regen if absent, per RUN_STATE) · raw 5m per drift law · B0 component series (already ported & validated: dtype, lean, yd_arch, ob55, scen; hayden own/BTC and pi from the p2 pipeline).

## W2-E — Extraction (the missing fuel — SHAPES, not just summaries)
Svet's drawing is the spec: the components' curves themselves, related to price's curve, are the conditions.
For each component × each applicable frame, over the trailing 100 bars ending at the event:
**(a) Shape words:** the last 4 swing points encoded HH/HL/LH/LL (e.g. "LH-LH") + an 8-segment slope profile (each segment U/F/D → e.g. "UUUDDFDD"). Price itself gets the same encoding per frame.
**(b) Relation columns (the overlay):** every component-shape vs price-shape → {confirm, bear_div, bull_div, mixed}, per frame — divergence as a first-class measured column for EVERY component (generalizing the certified RSIDIV reading, +6–12pp). Component-vs-component relations for the Hayden family.
**(c) Scalar descriptors (kept, complementary):** state_age · flips · dom_share · path class · prev_state · days_in_state.
**Components (D1 frames):** hayden_own & hayden_btc → {4h, 1D} · **hayden_15m & hayden_1h → native frames (NEW, ratified — same state machine on faster bars, labeled uncertified variants)** · **div_events → per frame: count/recency/direction of RSI-price divergences in the window (NEW, ratified)** · scen_state → {15m} · btc_pi, dtype, lean, yd_arch, ob55 → {1D}. Numerics quartiled, categoricals native, na a category. Estimated ~120–160 columns; the ladder machinery absorbs it.
**Eyeball gate, non-blocking (D2):** publish a 20-day SOL sample of the new columns (incl. one visible divergence with its TV timestamp), then PROCEED; Svet veto = rollback, not pre-wait.

## W2-L — Ladder
Same machinery, UNION table (all existing FE + W2 columns), **new-involving stacks only** (widened-run precedent): singles -> pairs -> triples per station x outcome families, n>=40 floor, BH q=.10 per family per run, extinction + underpowered queues logged.
**D3 — outcome families:** the existing two (bounce, through) **plus two profile extensions this wave**: b50 (bounce >=0.5U) and fastres (resolved <=12 bars) — closing the "in what way" gap.
**D4 — stopping rule:** decision #3 governs — a ring closes when curated mean incremental lift < .010. Expected frontier ~ d3 by W1 precedent; if d3 still clears .010, run d4 and re-test the rule; never run a ring past a failed rule check.

## W2-B5 — Forecasters (the payoff)
**D5: yes, rerun B5** on the W2-augmented table, all frames, walk-forward monthly, Brier vs base. Publish the new skill strip beside W1s. If skill improves, the model file is a deliverable (Svet wires it into the daily cards via the main chat).

## W2-A — Atlas merge
Regenerate ATLAS.html with source tag w2, same curation (top-12 per station x family x source, parsimony .010, certified n>=100), 3-row spot-verification against registers, stated bounds for anything digested rather than fully extracted.

## Runner
Phases W2-E -> L1 -> L2 -> L3(-> L4 per D4) -> B5 -> Atlas, chunked and cursor-resumable in gha_state (grind pattern). **D6:** grind.yml is currently finalize-only — hand Svet the restored dispatch YAML as paste-ready text (one file edit, phone-style instructions, b4-style inputs with numeric defaults, no "false" strings), single task name **w2**, budget default 330. Heavy rings on the runner; extraction may run in-chat if it fits, else as the first runner chunk.

## Deliverables & ledger
w2 join parquet + per-file sha + row counts · ladder registers + digest + extinction map · B5 scores + model artifact · merged atlas · updated RUN_STATE with this spec logged, decisions D1-D6 recorded, and the closing scope ledger (EXAMINED / REMAINING / DROPPED — "nothing" or itemized). Acceptance = Svet can pull any digest rows coin/date/time and see it on TradingView, and every % carries n.
