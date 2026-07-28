# 03 — COMBO (HAYDEN × OPTION B) — CHAT BOOTSTRAP
*Read with `00_MASTER_REFERENCE.md`, plus `ftmo_pass_rulebook.md` (Hayden) and `rulebook_v1_1.md` + `integrity_report.md` (Option B). This chat answers ONE question two ways: **should the two systems run independently, together, or not combined at all** — decided by simulation, not preference.*

---

## 1. THE KEY INSIGHT (read this first — it reframes the task)
The two books are **mostly the same signals with different exits.** Decompose:
- **Shared signals (identical entries):** FADE-K5 (XAU/JPY/US30/GER40/US500/US100), DON-20 (XAU/XAG/US500/US100), DON-55 crypto (SOL/BTC/ETH/XRP).
  - Option B runs these with the **half-off-at-+1R → BE** exit (→ 55.6% WR, +2.71 R/mo).
  - Hayden runs the *same entries* with the **full death/time exit** (→ lower WR, higher per-trade R).
- **Unique to Hayden:** **Engine 1** — the HA 4H **reversal** sleeves (1A Flip Rider, 1B/1D Confirmed Riders, 1C Confirmed Short) on SOL/BTC. This is the only genuinely *additive*, non-overlapping alpha — the source of the +10R..+46R tail and most of the +8 R/mo headline.

**Therefore the real combo is two knobs, not "two systems summed":**
1. **Exit style on the shared sleeves:** half-off (comfort/WR) vs full (Hayden/+R) vs a per-sleeve mix.
2. **Engine 1 on/off:** add the reversal tail (and its correlated SOL/BTC exposure) on top.
"Win-rate-weighted blend" = Option B base (half-off shared sleeves) **+ Engine 1 reversal tail**. That is the leading hypothesis. Measure it; don't assume it.

## 2. TWO DEPLOYMENT MODES TO TEST
**Mode I — Independent / sequential (one account):** deploy one book; the other is documented and only swapped **between attempts** (change-control allows this, never mid-attempt). Already covered by files 01/02; the combo value here is the **switch rule** — e.g. "start Option B; if a 2022-grade crypto regime is flagged, the next attempt uses CORE (no crypto)."
**Mode I′ — Independent / parallel (two accounts):** two separate $100k challenges, one book each, **no shared barrier**. Double the fee/capital, but the books diversify across accounts. Deliverable: the **joint distribution** — P(at least one funded by month X), P(both), expected total fees — from the two existing single-book campaign sims run jointly.
**Mode II — Together (one blended account):** merge into a single risk object. This is the analytically hard one and the centerpiece (§3).

## 3. MODE II — COMBINED-LEDGER METHODOLOGY (do this exactly)
1. **Regenerate both trade streams on equal footing** from the §3 master recipe: Option B via `bt.py` (half-off); Hayden via its rules (Engine 1 HA reversal + full-exit shared sleeves). Same window (2020-09→2026-05), same cost model (variant A base; also FTMO-true).
2. **Dedupe the shared sleeves — no double-counting.** For each shared signal you keep **exactly one position**, with **one chosen exit** (half-off OR full). Never hold the same instrument/signal twice. Build the combined config as: {shared sleeves at exit-style X} ∪ {Engine 1 reversal, on/off}.
3. **One risk frame across everything:** a single **4% aggregate open-risk cap**, single **daily 3% circuit breaker**, single **max-3-concurrent-crypto** and **crypto-margin guard ($95k notional)** spanning Engine 1 + DON-55. Use Hayden's cap-priority order, with Engine 1 sleeves slotted by their priority.
4. **Chronological merge → one equity curve.** Sort all kept trades by entry time; apply the ladder to the *combined* phase equity (this is where correlation bites — simultaneous crypto longs from Engine 1 + DON-55 draw on the same barrier).
5. **Campaign Monte Carlo (monthly block bootstrap)** on the merged stream, under FTMO barriers, at challenge base 0.75% and 1.0%. Report pass rate, median months, ≤6mo, and breach modes.
6. **Funded replay** (`replay.py`): chronological 2022 mark-to-market at laddered 0.50% (and 0.375%). The combo adds Engine-1 crypto risk to a book whose Option-B-only 2022 was −24R / funded trough −8.5% — **the combo's 2022 trough is the make-or-break number.**

## 4. PRE-REGISTERED GATES (decide before the numbers print)
The blended single-account combo (Mode II) **replaces** a single-book deploy ONLY if **all** hold:
- (a) **Pass rate ≥ max(individual)** OR **median months < min(individual)** — at breach risk no higher than the better book.
- (b) **2022 funded replay survives** the −10% line at laddered 0.50% with margin ≥ Option B's (trough not worse than −8.5%).
- (c) **No regime** in the per-year replay where the combo breaches while *both* individual books survive (correlation must not create a new failure).
- (d) Combined-stream stats are a genuine reproduction (trade-stream merge audited, no duplicate fills on shared signals).
If (a)–(d) fail, the verdict is **run independently** (Mode I default = Option B; Mode I′ if the user wants two accounts), and that is a legitimate, documented outcome — not a failure to find a clever answer.

## 5. LEADING HYPOTHESIS & PRIOR
Best expected single-account config: **Option B (half-off shared sleeves) + Engine 1 reversal tail.** Rationale: half-off gives the holdable 55% WR base; Engine 1 adds an *uncorrelated-in-regime* tail (it earned +21R in 2022 while the breakout/fade sleeves bled −24R — the reversal engine is the natural 2022 hedge). The risk is crypto-correlation into one barrier during a 2022-grade down-leg, which §3 step 6 + gate (b)/(c) exist to catch. **Counter-prior:** Engine 1's 28% WR may drag the *felt* experience below what made Option B chosen in the first place — track combined WR and max losing streak as first-class outputs, not afterthoughts.

## 6. WHAT TO PRODUCE
- A combined-config comparison table: {Option B alone} vs {Hayden alone} vs {Mode II blend variants: exit-style × Engine1 on/off} — each with trades/mo, WR, R/mo, max losing streak, campaign pass/median/≤6mo, 2022 funded trough.
- The Mode I′ joint distribution (two accounts).
- A one-line recommendation keyed to the §4 gates, plus the **switch rule** for Mode I.
- If a blend passes: a `rulebook_combo.md` v1.0 with the deduped sleeve list, single risk frame, and cap-priority — same decision-complete format as the other two rulebooks.

## 7. BOOTSTRAP PROMPT (paste as the first message of the Combo chat)
> Read `00_MASTER_REFERENCE.md`, `03_COMBO_bootstrap.md`, `ftmo_pass_rulebook.md`, `rulebook_v1_1.md`, and `integrity_report.md` — together they are the contract. Question: should Hayden and Option B run **independently, together, or not combined**? Note the §1 insight: the books mostly share signals and differ by exit; the only additive Hayden piece is Engine 1 reversal. Do this: (1) regenerate BOTH trade streams on equal footing per master §3; (2) build Mode II via the §3 combined-ledger method — dedupe shared sleeves to one position/one exit, single 4% cap + circuit breaker + crypto-margin guard across Engine 1 + DON-55, chronological merge, campaign MC + 2022 funded replay; (3) also compute Mode I′ (two separate accounts) joint distribution; (4) judge against the §4 pre-registered gates and recommend. Track combined win rate and max losing streak as first-class outputs. If a blend passes the gates, write `rulebook_combo.md`. Hold all change-control rules; do not touch sealed CL=F/HG=F.
