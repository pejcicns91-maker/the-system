# OPTION B — RULEBOOK v1.2 (supersedes v1.1 for the DON-55 sleeve only)
**THE RULE (one line):** A DON-55 signal is **SKIPPED** when, at the entry bar's close, (a) BTC is in π-downtrend (111d SMA / 350d SMA ≤ 1, prior daily close) AND (b) the same asset's Hayden 4H state ≠ Bull (HA Wilder-RSI-14 machine: Bull >67 / Bear <33 / Chop exits 39-61, as of last completed 4H bar). A signal is skipped, never queued. All other Option B rules, sleeves, sizing, ladder, and caps are unchanged.

## EVIDENCE CHAIN (each step gated, in order)
1. **Pilot Q3 (registered):** D55 entries in Hayden-Bull +0.282R vs −0.023R not-Bull — Welch .036, placebo .037, CI [+0.01,+0.58], halves +0.50/+0.18, FDR pass (HAYDEN_PILOT_prereg/RESULTS).
2. **Independence vs π (queued → run 2026-07):** effect survives stratification — CMH within-π Δ = +0.39R, p=.004. The action is concentrated in π-down: Bull +0.21 vs not-Bull **−0.42R** (n=44, CI [+0.26,+1.02], p=.001). π-up split not significant (p=.36) → NOT part of the rule.
3. **Per-asset:** poison subset negative on 4/4 (SOL −0.44, BTC −0.30, ETH −0.68, XRP −0.22; n=10-13 each — individually tiny, sign-unanimous, pooled significant).
4. **Book impact (historical):** 495→451 trades (−9%), meanR +0.200→+0.260, totalR +98.9→+117.4, maxDD 19.0→13.5R, worst month −5.7→−4.8R, yearly uplift ≥0 every year; structurally inert in π-up years.
5. **Funded-ladder replay (Law-8 gate, chronological mark-to-market, ladder+caps, same data both books):** 2022 trough −10.4%→**−9.8% (breach→survives)**; 2021 end +5.2→+8.1%; 2023 +18.0→+18.3%; 2024/2025 identical; **2026 YTD −5.0%→−0.1%** (trough −5.9→−1.4). Worst-day never near the −5% line.

## ⚠ SEPARATE MATERIAL FINDING — DATA-VERSION DEPENDENCE OF THE BANKED CLEARANCE
On current Yahoo data, the **unfiltered** book breaches 2022 at the 0.50 ladder (−10.4% vs banked −8.5% thin-pass). The gold/silver back-revision has invalidated the banked funded-ladder margin independently of this rule change. Consequences: (a) the **0.375% ladder base remains cleared on both books** and is the conservative default until re-verification; (b) the **MT5 export re-base is now load-bearing**, not housekeeping — the full clearance must be re-run on broker-true data before the first paid attempt.

## FORWARD CLAIM (registered)
**F-v1.2:** on new DON-55 signals from 2026-07-03, the skipped subset (π-down ∧ not-Bull) underperforms taken signals; graded at n≥15 skips. The v4.2 engine prints every skip, so grading is automatic from the daily ritual.

## ACTIVATION CHECKLIST
☑ Independence study · ☑ per-asset decomposition · ☑ book impact · ☑ funded-ladder replay (delta basis) · ☐ **MT5 re-base + full clearance re-run (required before first paid attempt; rule may run in paper/monitoring immediately)** · ☐ one full paper month (standing doctrine) · ☐ Svet sign-off on this document.
**Engine:** brief_engine_v4.py now prints v4.2 — skipped signals appear as `DON55:SYM[SKIP v1.2: pi-down & H:not-Bull]`.


## SIZING DECISION — LOCKED 2026-07-03 (Svet)
**Ladder base = 0.375% risk/trade, BOTH phases (challenge and funded), steps 0.375/0.25/0.125 at −3%/−6%.** Evidence at this setting on the v1.2 book (S1 data, full ladder+caps replay): 2021 +5.6% · **2022 −8.3% (worst case, 1.7% margin to the −10% floor)** · 2023 +17.5% · 2024 +17.3% · 2025 +16.3% · 2026 YTD −0.5%. Worst single day across six years: **−0.81%** — the daily −5% line is never approached. Challenge-phase note: the prior 0.75% challenge base **breaches 2022 on S1 (−11.5%)**, as does the scaled 0.5625% (−10.7%) — both are retired; uniform 0.375 passes +10% targets in trending years (2023/24/25 all exceed +16%) and survives 2022-grade regimes to retry without a new fee. The 0.50 funded ladder remains archived as viable-but-thin (−9.8%, 0.2% margin) and may only be revisited on ≥12 months of forward data. No second data source is obtainable (Stooq/Dukascopy/MT5 all inaccessible) — S1 self-consistency plus the freeze-forward cache is the operative guarantee.
