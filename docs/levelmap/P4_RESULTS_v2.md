# LEVEL MAP — P4 RESULTS v2 (COMPLETE; supersedes v1) — carried S/R book, full taxonomy (2026-07-07)
*Adds to v1 the owed items: full event-atom revisits, band UNITS, censoring-corrected survival, calibrated-cell transport, weekend selection audit. v1's death-boundary finding stands unchanged. Reproduce: p4b_build.py → p4b_analysis.py. Sanity: pen_U bit-parity with the v1 sweep on all 44,530 events.*

## SURVIVAL, censoring-corrected (KM; naive consumed-only in brackets)
DAILY: median **6d** [5] · S(30) 23% · S(90) 14% · **S(365) 9%** — a tenth of daily zones survive a year untested. PW: median 15d [12] · S(365) 14%. PM: median **50d** [32 — naive understated 56%] · S(90) 40% · **S(365) 25%**. Censored: 7/10/17%.

## REVISIT REACTIONS — full taxonomy: carried geometry ≈ fresh geometry
Branch shares skew to breaks (revisit-day composition, per v1): HOLD 9.3 / SWEEP 23.5 / CONTEST 17.5 / **BREAK 49.7%** (n=33,434 sided). But per-branch travel transports almost exactly [fresh map in brackets]: HOLD eow −0.71 [−0.79] · SWEEP −0.48 [−0.49] · CONTEST −0.20 [−0.13] · BREAK +0.52 [+0.59]; fav/adv 4h likewise (BREAK fav 0.91/adv 0.46). **An old zone reacts with the same geometry as a fresh one.**

## CALIBRATED-CELL TRANSPORT (observation, not a gate; thr cuts reused from A-81 as registered)
The thr×am contested-band cells applied to carried-zone revisits — a third, population-out-of-sample test: **weighted |carried − calibrated-H2| = 3.40pp** (cells n=162–1,585). Corners: fast|few **18.9** (cal 21.9, n=1,585) · reversing|many 39.5 (45.6, n=162). The structure transports nearly intact. Note: slow|many carried = 42.4, closer to H1's 46.3 than H2's collapsed 35.5 — suggesting the gate's one flagged cell was the anomaly of that half, not of the cell; observation only.

## BAND UNITS (overlap-merge, zero-parameter; n=10,060 units)
At UNIT grain, resolution is flat in band size: Pcont 40.5 / 38.9 / 41.3 / 40.9% for size 1/2/3-4/5+ (n=4,301/2,451/1,511/1,795). **Corrects v1's raw per-zone read**: the BREAK-rises-with-n_band pattern was zone-counting inside congested areas, not unit behavior. Union widths 0.09→0.14U; 5+ bands carry old members (age_max med 19d).

## WEEKEND AUDIT
Weekend-consumed seeds (25%, age-exact/payload-less) are unselected: PW/PM mix 61 vs 58%, formed-in-trend 55/55%, age med 12 vs 10d — the payload gap is benign.

## STATUS
P4 fully done; spec outputs #1–#5 complete; row 36 closed with a calibrated tier that now stands on three populations. Remaining named follow-ons: v6-independence study (needs brief kit) · gated tradeability test.
*Files: level_map_p4b_pack.zip = revisit_events_full.csv · band_events.csv · carried_book_v2.csv · p4b_build.py · p4b_analysis.py. A-83.*
