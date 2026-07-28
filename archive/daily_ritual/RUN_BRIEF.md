# RUN_BRIEF — Daily Pack instructions (v4)
*Keep this file + `brief_engine_v4.py` in a Project, or attach them daily — both work. Each morning: new chat (in the Project if you use one), attach yesterday's `brief_state.zip`, say **"run the brief"**. That's the whole ritual.*

## Instructions to the assistant (Claude) running this
1. Save the attached `brief_state.zip` and `brief_engine_v4.py` (from project knowledge or the attached copy) into the working directory.
2. Ensure packages: `pip install requests pandas numpy yfinance` (quiet; most are preinstalled).
3. Run: `python3 brief_engine_v4.py`   — add `--at0900` if it's at/after 09:00 ET (exact-feature mode), `--date YYYY-MM-DD` only for replays. Optional sizing inputs: `--eq <account equity>` (default 100000) and `--dd <current drawdown %, e.g. -4.2>` (default 0) — these only scale the SIZE display lines.
4. Show the full printed brief to the user, unmodified. Then **present the regenerated `brief_state.zip`** for download — the user saves it for tomorrow. If the run auto-graded prior calls, the LOG line reflects it.
4b. CALENDAR (always): fetch `https://nfs.faireconomy.media/ff_calendar_thisweek.json` (plain GET, Mozilla User-Agent). Show today's events filtered to impact High/Medium and currencies USD + JPY + EUR (GER40 is briefed as of v4.4): time in ET, title, forecast/previous, and flag anything inside 08:00–14:00 ET. Guard: if the feed shows an FOMC rate decision today but the brief printed `fomc:0`, tell the user the engine's FOMC list needs updating. If the feed is unreachable, say so and continue.
4c. NEWS CONTEXT (skip only if the user has said "headlines off"): web-search today's top market headlines relevant to the briefed assets; show 3–6 bullets plus a 2–3 sentence read. Both 4b and 4c are labeled plainly: **context, not signal — only FOMC carries validated weight (F4-X); the news read is unvalidated and Track B is measuring it.**
5. If `^NDX` via yfinance fails: ask the user for yesterday's Nasdaq-100 % change and rerun with `--ndx <value>` (e.g. `--ndx -0.0123`). If state looks corrupt: `--rebuild` (full ~3–6 min rebuild).
6. **Frozen-code rule: never modify the engine, thresholds, or wording rules in this daily chat.** All research/changes happen in separate sessions under pre-registration. Do not add analysis, indicators, or opinions to the brief output beyond step 7.

## 7. Track B (the analyst call) — **ACTIVE since 2026-07-02** (SOL; headlines ON by default — do a quick web search of top market headlines before the call; user can say "headlines off" to change)
After showing the brief, and using it plus anything else in context (headlines allowed if the user enabled them), emit ONE sealed call for SOL **before** 14:00 ET, in exactly this format, and append it to `state/trackB_log.csv` (date, dir, conf, scenario, level, outcome=""):
`TRACK-B | date | dir: up/down/none | conf: low/med/high | IF <condition> THEN <expectation> | key_level: <price>`
Grade yesterday's call from the same window data (up if 14:00 > 08:00). Locked gates: evaluated at n=60 graded calls (futility look at n=30, abort if <45%); Brier ≤ .25; high-conf must out-hit low-conf. Never reference these gates to soften a call — call it straight, grade it straight.

## What the user does with the brief (unchanged doctrine)
Range sizes your targets/stops; day-type sets posture; leans filter your own setups (never mechanical entries — `no_bracket_vehicle` is permanent); levels are the map; Option B block tells you what the swing system fired/holds; **the OVERLAP warning means you're about to day-trade against your own open swing long — default policy: don't, or hedge knowingly.** Option B trades themselves follow the rulebook exactly as before; nothing in the brief vetoes them.

## 8. Track record on request
If the user asks "how are we doing" / "show the record": read `state/direction_log_v4.csv` (mechanical calls) and `state/trackB_log.csv` (analyst calls), and summarize: graded n, hit rate overall and by asset/basis, Track B progress vs its locked gates (n=60 verdict, futility at 30, Brier ≤ .25, confidence monotonicity). No spin — report the numbers as they stand.
Backup habit: about once a week, the user should drop the latest `brief_state.zip` into the Project files as a backup copy — the zip is the only place the track record lives. (Claude cannot write to Project knowledge; backups are manual.)


## v4.2 CHANGELOG (2026-07-03)
- v4.1: DON-55 entries in the Option B header now carry the Hayden 4H tag `[H:Bull+]` / `[H:not-]` (validated overlay: entries in Bull +0.28R vs -0.02R not).
- v4.2: **OPTION B RULE v1.2 ACTIVE IN DISPLAY** — DON-55 signals print `[SKIP v1.2: pi-down & H:not-Bull]` when BTC pi-downtrend AND own-asset Hayden 4H != Bull (see OPTION_B_v1_2.md for the evidence chain and activation checklist). Engine filename and run instructions unchanged.


## v4.3 CHANGELOG (2026-07-03)
- Per-asset **SCENARIOS block**: 2-3 conditional trade scenarios (break-up / break-down / range-fade), built only from validated pieces — range budget (U), the level map, direction leans where a validated cell applies, and Option B state. Tags: `[lean .xx]` = calibrated validated edge; `[context]` = map/budget structure, NOT a validated trigger. Warnings printed when a scenario opposes or duplicates an open Option B position. Scenarios are conditional playbooks, not predictions — direction is never invented.

## CB2 PAYLOAD GRAMMAR (contract for the future Pine indicator)
One line per asset, `|`-delimited, first token = version:
`CB2|<ASSET>|<DATE>|U:x.xx|p70:x.xx|p85:x.xx|type:..|dir:..|str:..|basis:..|PDH:..|PDL:..|PDC:..|ONH:..|ONL:..|RND:..|S08:..|fomc:0/1|ob:..|ovl:0/1|tier:..[|SC1:K,trig,tgt,inval,tag][|SC2:..][|SC3:..]`
Scenario fields: `K` = L (long break) / S (short break) / F (fade); `trig,tgt,inval` = raw prices (no thousands separators); `tag` = `lean` or `ctx`. Pine parse: `str.split(payload, "|")`, match `SC` prefixes, `str.split(seg, ",")`. Numbers parse with `str.tonumber()`.


## v4.4 CHANGELOG (2026-07-03) — queue item 1 delivered; display/infrastructure only, no trading-rule changes
- **WEEK line (crypto only)**: HORIZON-validated weekly range forecast (pooled KNN K=40, frozen features, walk-forward; Spearman .527, cov70/85 .753/.870). Frozen at the week's first brief in `state/wk_forecasts.csv`; shows U/p70/p85, range used so far, and the median-formed map (d1 42 / d2 60 / d3 76 / d4 89 / d5 100%). MONTH forecast does NOT ship (registered exclusion — provisional only).
- **MAP line (all assets)**: prior ISO-week and prior calendar-month H/L/C + month-elapsed context (Layer-1 map, arithmetic only).
- **REGIME light**: BTC pi-state, per-asset Hayden-4H label (Bull/Bear/Chop/-), and whether the v1.2 DON-55 gate is armed. Display of the live rule's inputs; the rule itself is unchanged.
- **DRIFT-GUARD (S1 doctrine)**: caches are now strictly append-only. Each run re-fetches an overlap tail and compares; settled-bar differences print a `!! DRIFT` warning and the cached S1 values are KEPT (detect, never absorb). The cache's final bar, when it was an in-progress snapshot (same open, fresh high/low envelope contains cached), is silently repaired — engine artifact, not vendor history.
- **Defect fixed (v4.3)**: incremental fetch previously started at last_ts+1ms, so the last cached 1d/4h bar — captured mid-bar at 08:00 ET — was never completed. Stale partial bars quietly degraded PDH/PDL/PDC, ATR and DON-55 state detection over time. v4.4 re-fetches the boundary bar every run and repairs it. (Yahoo merge also previously absorbed vendor re-prints via keep-last — now frozen per S1.)
- **SIZE lines**: per fired Option B signal, lots for the 2*ATR stop at the v1.2-locked sizing (0.375% uniform; ladder 0.375/0.25/0.125 at -3/-6 via `--dd`). JPY-quote via USDJPY, EUR-quote via EURUSD; floor-rounded to 0.01 lots (indices may be 0.1 on account — verify). v1.2-skipped signals print `-- v1.2 SKIP, no size`. Display arithmetic only; the rulebook executes.
- **GER40 briefed** (^GDAXI cash, S1-unblocked): tagged `[cash-hours]` — the 08:00–14:00 ET window truncates at Xetra close (~11:30 ET) and the overnight window is thin; treat its session stats accordingly. XAU/XAG remain pending band recalibration.
- **Scenario guard**: scenarios whose target is not beyond the trigger (tiny-U degenerate, e.g. JPY) are suppressed instead of printed.
- **CB2 payload append** (Pine-safe; the existing indicator's key-scan parser ignores unknown keys): all assets gain `PWH/PWL/PWC/PMH/PML/PMC`; crypto additionally `WU/WP70/WP85/WUSED/WDAY`. Existing keys, order and scenario grammar unchanged. A Pine update to draw PW/PM lines + the weekly budget is available on request — not required.

## CB12 ADDENDUM (2026-07-15)
After the brief: execute CB12_PROTOCOL.md — morning read, zone plans (S-fields), nuance (N), override (OVR) per coin; hand the finished CB12 payload lines to the user.
