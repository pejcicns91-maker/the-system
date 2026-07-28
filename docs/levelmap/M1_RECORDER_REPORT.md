# M1 — UNIFIED STATE RECORDER: BUILT & ACCEPTED (2026-07-08)
*Mode BUILD (assembly of banked layers into one table) · file: M1_state.parquet.*

## WHAT IT IS
**One row per (asset, day, level) — 135,360 rows, the exact required grid, total population**: touched and untouched days alike, weekends first-class. 70 columns per row:
- **Intensity, direction preserved**: signed approach displacement at 30m / 2h / 6h / 23h (defined on the 45,481 sided events with 24h history; NaN accounted elsewhere — intensity is at-touch by definition).
- **The level's own story**: freshness (days-since-touch), area memory, entries today, penetration, thrust.
- **The constellation — the row every study lacked**: all 20 levels' 12-state configuration that day (side × 5-day cross × freshness), board-above fraction, 5-day cross count, local level density per level.
- **Day context**: yesterday's archetype in both frames (size + shape), yesterday's net/range, Hayden regime, weekend, era.
- **Outcomes**: touch, side, break, continuation, first-touch hour, next-day contact (for untouched rows).
(e) Indicators join only after M4's TradingView parity gate, per contract §1.

## ACCEPTANCE (contract §5, all passed)
Coverage: **135,360 / 135,360 exact**. Raw-bar spot-verification: 6/6 random rows' touch flags match the pickles directly. **M2 parity: the headline constellation cell reproduces from M1 bit-for-bit (n=85, 62.4%; mirror n=108, 62.0% vs base 42.6) → M2 REQUIRES NO CORRECTION** — its grid stands as banked.

## WHAT THIS UNLOCKS
Every remaining phase queries this one table: M2b triples (lit pairs × third dial), M3 order grammar joins onto it, M4 adds indicator columns after parity, M5 reads it live. Coverage gaps to close later, named: intensity for untouched approaches (approach-anchored horizons), partial-path class as an intraday column.
*A-100. Next owed by name: **M2b — triples probe on the ~70 lit constellation pairs**, now one groupby away.*
