# MAP V3 — THE ZONE-BEHAVIOR PLAYBOOK (synthesis · 2026-07-23)
Readings only — no verdict words. Governed by V3_CONTRACT.md. Built in one day, five phases, from 185,452 events across the full listing history of BTC/ETH/SOL/XRP, on the validated wall series (port gate PASS). Any money use of anything below requires its own sealed pre-registration — candidates are named in §6 and leave v3 at that door.

## 1. The base tape (n in parentheses; every split available in p3_t1.json)
- Contact with a zone is a coin flip: **50.1% hold** (53,467).
- Breaks rarely travel: **14% reach the next zone** (n 39,362 break events; the 66,237 n belongs to retest_flip — corrected 2026-07-26).
- Breaks come home: **60.2% are back inside within 30 minutes**; ~86% of breaks get retested; after a break the next event is at the **same zone 82%** of the time.
- Broken levels rarely flip into new S/R under a strict criterion: **7.3%** (0.25U onside within 12 bars — the criterion is the measurement).
- Depth at contact: p10/25/50/75/90 = 0.010/0.031/0.072/0.170/0.320U. **Graze class ≤0.031U** (distribution-derived p25) — a quarter of all touches; Svet's "barely there," formalized.

## 2. The zones are not one species (certified, FDR q=.10; all cells in p3_t2/t3 registers)
- **Wide zones (0.32–1.71U) in calm conditions barely resolve as breaks:** EU session 95.7% hold (1,587) · Asia 92.8% (823) · evening 89.2% (2,861) · late-day 94.5% (2,579) · slow approaches 89.3% (3,639) · triple-conditioned peaks: EU × wide × SOL 97.5% (279), Z2-origin × wide × EU 98.1% (108). Width is ex-ante known; part of the effect is mechanical (more ground to close beyond) — both stated.
- **Virgin zones invert the coin:** first touch of a 20-day-untouched zone from close range holds **9.4%** (117). Untouched walls give way; worn walls repel. (Its mirror: virgin × 2–7h into the day → false-break only 45% vs 60% base, n 80 — virgin breaks are more real.)
- **Stepping-POC zones grazed → 92.7% hold** (1,411).
- **Travel becomes readable when the day is already stretched:** breaks fired with day-range >1.28U reach the next zone 37.3% vs 14% base (271) · high-relative-volume breaks toward a near next-zone 34.2% (1,347) · inside-open exits on stretched days 34.0% (285).
- 4,986 pair-cells + 531 triples certified in total; a similar mass sits in the UNDERPOWERED queue (n<40) awaiting more history.

## 3. The forecast layer (held-out future days; p4_scores.json)
- **P(hold | full state): skill +0.363, AUC 0.845, calibrated ±3pp across the range** (says 95% → happens 96.5%). The coin flip dies when the state is read.
- P(reach next | break): skill +0.114, AUC 0.733, calibrated.
- P(break AND reach | contact) — the chained question: skill +0.074, AUC 0.785.
- P(false break | state): **skill +0.034** — whether a break returns is nearly unforecastable; the 60% base is the fact itself.

## 4. How this coheres with everything already banked
The MAPMONEY family (n≈38k trades) found: fade at touch ≈ gross zero; chase −0.10R; break-retest +0.02R gross, killed only by costs. §1 explains all three: touches penetrate (fades bleed), travel is rare (chases starve, 14%), and breaks come home (retests collect — 60%/82%/86%). The map's reading layer and the money graveyard now tell one story from two directions. Right-but-unpaid remains the standing summary: the tape is readable; the registered geometries so far don't clear a 13.5bp toll on a 0.6U risk unit.

## 5. What feeds the daily ritual today (readings, allowed now)
The CB12 cards' three-branches-per-zone can carry calibrated forecast numbers instead of composed ladder odds — as *readings* on the chart layer, clearly sourced (this requires only card-composition changes, no money claim). The graze class formalizes "barely there" tags in daily grading. Nothing else changes; CB12.5 and the system remain untouched per Svet's standing instruction.

## 6. Candidates derived from the map — each LEAVES v3 here (own prereg + sealed gate mandatory)
C1 **Virgin-break continuation:** enter with first-touch breaks of virgin zones (9% hold, realer breaks) — attacks the 14% travel problem at its known exception.
C2 **Wide-calm zone fade:** fade contacts of wide zones in EU/Asia/slow conditions (88–97% hold cells) with geometry sized to the measured bounce distribution.
C3 **Retest-collection at scale:** the +0.02R gross break-retest respecced with map-conditioned selection (stretched-day / high-relvol cells) and cost-aware sizing (bigger R, maker fills).
C4 **Forecast-gated cards:** trade only when P(hold) or P(break-and-reach) clears a calibrated threshold — the model as filter, sealed like any rule.
None are tested. None inherit anything. The words "edge/validated" apply to nothing in this document.

## 7. Artifact index (rerun commands inside each)
p2_events_ALL.csv `fcf1262a…` (185,452) · p3_t1.json `82b968cd…` · p3_t2_register.csv `22b58ca8…` (10,067 tests) · p3_t3_register.csv `1758e98a…` · p3_transitions.json `15dc937e…` · p4_scores.json `99a0b7d0…` · engines p2.py/p3.py/p4.py, seed 20260723 throughout · preregs & ledgers: MAPV3_DESIGN.md, P1_SCHEMA.md, P2_LEDGER.md, P3_READINGS.md, P4_FORECAST.md · contracts: V3_CONTRACT.md, CONTRACT_AUDIT.md.

## 8. CLOSING LEDGER (v3 arc)
**EXAMINED:** design → P1 extractor (eyeball-verified against Svet's own days) → P2 full extraction (EXIT type added from his catch; pi validated before adoption) → P3 marginals/pairs/triples/transitions/graze → P4 scored forecasters (three leaks of one class caught across the arc; all disclosed).
**REMAINING:** daytype/yd_arch/lean columns ('na' — engine-definition port or forward-fill; they cap forecast skill) · inside-edge taps · UNDERPOWERED queue · forward wiring of readings into cards (needs Svet's instruction) · every §6 candidate's money prereg.
**DROPPED:** nothing across all five phases.
