# GRIND BUNDLE — laws and scope (prep 2026-07-23; NOTHING has been run)
Governed by V3_CONTRACT + CONTRACT_AUDIT + graveyard laws. Seed 20260723 everywhere.
Reading layer only: frequencies with n; no verdict words; BH q=.10/family at finalize; n>=40 floor;
extinction logged; 'na' is a category.

## W1 — d5 + t2 extension (grind1.py)
FE base = the 25-column set (19 original + 6 B0). t2 adds quartiles (qcut 4, duplicates-drop
precedent) of 35 lookback columns (net100/net20/rng100/pos100/volr/zt100/zlast x 5 frames);
lnb/fnb are coverage flags, excluded. FE totals 60.
Default phases: A = full d5 over FE25 (53,130 stacks) + B = t2-involving d1-d3
(35 + 1,470 + 31,920). Total 86,555 stacks x 11 stations x 2 families.
PHASE B4 (t2-involving d4 = 474,985 stacks, ~10^9-10^10 cell scale) is REMAINING-BY-PHYSICS:
opt-in via input b4=1; its bulk counts go to 90-day artifacts, only extinction+state commit.
This is stated scope-bounding, not silent narrowing.
Chunking: 200-combo blocks, cursor committed per block -> any cancellation resumes.
Finalize mode = single pass computing exact binomial p (validated vs scipy in-run), BH per
family over the completed set, register parts (<80MB each), digest, extinction map.

## W2 — B5 forecaster (b5.py) — THE PREREG IS IN THE FILE HEADER AND IS BINDING
Walk-forward monthly logistic on the full wide state; Brier + skill vs train-base-rate
constant predictor, per frame (5m/15m/1h/4h/1d) x family x month. No tuning, no refits,
no peeking. Any deviation must be reported, never promoted.

## Environment / vendor law on the runner
The runner REBUILDS raw->mf->wide itself (fetch_arch x4, b1t2_mf, b_join) with pandas
pinned 3.0.2; results cache under key wide-v1. Logs print row counts; the wide table must
show 585,176 rows — anything else is environment/vendor drift: STOP, report, do not grind.
Vendor re-prints in fresh fetches are detected by the established drift protocol back in chat.

## Quota note
GitHub free tier: private repos get 2,000 Actions-minutes/month (a 230-min chunk ~= 4 chunks/mo);
public repos are unlimited but the data files are then public. Your call at repo creation.

## Deliverables back to chat
w1_digest.csv, w1_extinction.csv, out_register/ parts, b5_scores.csv (+ run logs if odd).
Adjudication, map promotion, and any money-test prereg happen in chat, never on the runner.
