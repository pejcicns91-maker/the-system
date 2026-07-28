# START HERE — DAILY BRIEF RUNBOOK
**You are an AI. Svet uploaded this zip and said something like "run the brief." This file tells you exactly what to do. Read all of it first. Everything you need is inside this zip.**

## THE LOOP (one file in, one file out)
Svet uploads THIS zip each morning → you run the steps below → you return (a) the brief and payload lines in chat, (b) **this same zip, regenerated with updated state**, which he uploads tomorrow. Never lose that loop: the state inside is the only live track record.

## RULES (non-negotiable)
1. **Never write or modify code unless Svet explicitly says to code.** The run commands below are not "coding" — executing them is your job. Changing any script is coding.
2. Be terse. No filler, no cheerleading, max one question per message.
3. Show the full printed brief **unmodified**. Do not summarize it away.
4. `brief_state.zip` is append-only. Extract fresh, never re-run against a mutated dir, never double-log, never regrade a graded call.
5. If anything fails or gets skipped, say so explicitly. Silent scope-drops are the cardinal sin.
6. Honest bounded language: composed odds are reads, not certifications. If nothing is unusual today, say so — never manufacture insight.

## STEP 1 — SETUP
Extract this zip to a working directory. Then:
```
pip install yfinance --break-system-packages
python3 -c "import yfinance"      # verify
```

## STEP 2 — RUN
```
python3 run_day.py
```
(Engine v4.4 + M9b wall-builder; Binance endpoint fallbacks are built in. After 09:00 ET it runs in --at0900 mode automatically. If caches error: `python3 run_day.py --rebuild`, ~3–6 min.)
Print the ENTIRE brief output to Svet, unmodified, plus the CB2/CB9 machine lines it emits.

## STEP 3 — CALENDAR
Fetch `https://nfs.faireconomy.media/ff_calendar_thisweek.json` (User-Agent header needed). Filter: today's date (America/New_York) · countries USD/JPY/EUR · impact High/Medium. Flag anything between 08:00–14:00 ET as in-window. Note FOMC yes/no.

## STEP 4 — HEADLINES
Web-search overnight crypto/macro tape. Deliver 3–6 bullets + a 2–3 sentence read, labeled **context, not signal**.

## STEP 5 — TRACK B (sealed SOL call, must be logged BEFORE 14:00 ET)
One directional call for SOL, exact format:
`TRACK-B | YYYY-MM-DD | dir: up/down | conf: low/med/high | IF <condition> THEN <expectation> | key_level: <price>`
Then: open `state/trackB_log.csv` (header `date,dir,conf,scenario,level,outcome`). **Grade yesterday's row first** if its outcome is blank (did the IF/THEN resolve? fill outcome: hit / miss / no-trigger). Append today's row with outcome blank. This is sealed — once appended, never edited.

## STEP 6 — CB12.4 PAYLOADS (one line per coin: BTC, ETH, SOL, XRP)
The TradingView script (reference copy in `cb12_4/CB12_4_copilot.txt`) renders whatever you write. **All words come from you, fresh, today.** Worked example from 2026-07-22: `cb12_4/CB12_4_SOL_payload_EXAMPLE.txt`.

Grammar (single line, `|`-separated; no `|` or `~` inside free text):
```
CB12|{COIN}|{date}|UA:{u_abs}|CTX:{regime,..}|HDR:{short header: zone position, week budget}
|W{n}:{lo},{hi},{comp},{contact},{flag}                         ← copy from the M9b output
|T{n}:{short|long},{entryLo},{entryHi},{stopLo},{stopHi},{tp1},{tp2|-},{solid|dot|dash}
|G{k}:{badge 1/2/3/i}~{WHEN}~{ACTION}~{WHY}~{bandLo}:{bandHi}   ← "-" band = never lit
|N:{one plain sentence of today's nuance}|OVR:{none|EXPANSION|QUIET}
```
Composition rules:
- **Trades, not forecasts.** Each T = a real trade: entry ZONE, stop ZONE, TP(s). 1–3 trades per coin.
- **Retrace entries, never chases.** A level breaking is not an entry; the retest of the broken level is. Pattern: one G row "X breaks → WAIT, don't chase the break candle", next G row "retest zone → SHORT/LONG it · stop · TP".
- Voice = Svet's card: *"Possible short entry in area 158–159, confident target 155, possible 152, stop past 161 — careful of sweeps; if it fails past 161, wait for the pullback to xyz."* Actions + prices + odds + one-line reasons. No jargon ("fade", "slapped"), no bare percentages without a reason, no over-compression.
- G bands: price ranges that light the row when price is inside (top-down first match). Give every actionable row a band; info rows get "-".
- Odds only from banked constants (era-proof): penetration ladder .3U→66 / .4U→71 / .5U→76 / .6U→79 / .8U→85 / 1.0U→89% through · day-type: EXPANSION breaks 64% (×fast 70), QUIET holds 69% (weekend 84) · 3+ vote reject 67% · weekend breaks 36% · target-reach .16U→83 / .36U→53 / .87U→22%. Break-trigger convention ≈ zone edge + 0.6U. Label composed numbers as reads.
- OVR from the brief's day-type (normal → none). N = one honest sentence tying tape/headlines/regime to the plan.
- **Overlap rule:** if the brief shows an open Option B position (ob: field / "open at 08:00") opposing a day-plan direction, the N line MUST warn: "you are LONG {coin} in Option B — don't short your own book; hedge knowingly or skip."
- Per coin also print a 3–6 sentence plain morning read in chat.

## STEP 7 — RETURN THE ZIP
Re-zip the state (`zip brief_state.zip state/trackB_log.csv` etc. — run_day.py already regenerates most of it; make sure your Track B append is inside). Then rebuild THIS whole pack (same structure, updated `brief_state.zip`, this README unchanged) and give it to Svet as a downloadable file named `SVET_DAILY_RUN.zip`, plus each coin's payload line clearly separated in chat. Tell him: "tomorrow, upload this new zip."

## KNOWN OPEN ITEMS (mention only if relevant)
- State history is a fork started 2026-07-22 (prior living zip was never located). Track B entry #1 = 2026-07-22 SOL down/low/77.50.
- Unanswered design question: when a short's stop level breaks UP, is the retest a LONG with the break or a re-SHORT? Current convention: re-short, per Svet's card. Ask if it matters that day.
- BTC/ETH/XRP received CB12.2-grammar payloads on 07-22 but not yet CB12.4 trade cards — you compose them fresh today anyway.
- XAU/XAG not briefed (band recalibration pending). GER40/US indices/JPY: levels + scenarios come from the engine; no CB12.4 cards for them (TradingView copilot is crypto-only).
- Intraday: "recheck {coin}" = re-derive that coin's plan from live price, same grammar.

## AUDIT CONTRACT
CONTRACT_AUDIT.md in this pack is binding. When Svet pastes "AUDIT: prove it — full contract." deliver all nine items, no negotiation.

## CB12.6 (added 2026-07-23) — MORNING STEPS CHANGE
After m9b: build ctx.json from the brief ({"spot":{...S08 per coin},"wk_used":{...WUSED/WU},"hayden_btc","btc_pi","fomc"}) then run `python3 score_zones.py <m9b_out> ctx.json` → v6 wall lines with ,CLASS,PHOLD per wall (model: hold_morning.pkl, skill 0.329 AUC 0.823, tag numbers `cal`). Paste target is CB12_6_copilot.txt (12.5 still renders v6 lines, ignoring extras).
COMPOSITION LAWS v6 (binding): NO chase cards ever (break-candle entry banned, −0.10R proven). Every break branch = retest entry only. Virgin (V) walls are never fade targets — compose as break-watch (9% historical hold), retest-after is the entry. Fade cards only at certified high-hold cells (wide/calm etc.), print rate+n. Every break card carries the homecoming line (~60% back ≤30m · retest ~86% · same wall next 82%). Grazes (≤0.031U) don't count as tests in cards, lit-rows, or Track-B grading. cal vs bank tags mandatory on all odds. Full design: CB12_6_DESIGN.md.
