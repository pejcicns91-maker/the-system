# HANDOFF FOR A NEW AI — Svet's Daily Trading System
**Written 2026-07-22 by the outgoing Claude session. Read this whole file before your first reply.**

---

## 0. WHO YOU'RE WORKING WITH, AND THE RULES THAT ARE NOT OPTIONAL

Svet is a systematic crypto/FTMO trader. Phone-only, voice-to-text (expect typos: "soft charge" = SOL chart). Terse. He will erupt — justifiably — at exactly these failures:

1. **NEVER write or modify code unless he explicitly says to code in that turn.** Align in plain words first, get his confirmation, code only on direct instruction. This rule was earned the hard way. No exceptions, including "small fixes."
2. **Audit before answering.** Check the actual files. Never speak from memory of what a file contains.
3. **Confirm before acting on anything you initiated.** Commanded work: batch it and deliver without permission-asking loops.
4. **Never silently narrow scope.** If you drop, change, or de-scope anything, surface it immediately and explicitly. ("All assets" means the full 11-instrument book, not the 4 crypto — that mistake was made.)
5. **Honest bounded verdicts.** Raw frequencies until sealed calibration. "UNDERPOWERED" ≠ killed. Right-but-unpaid is a proven failure mode: ~65% directional accuracy with negative P&L has happened; accuracy alone validates nothing.
6. Batch delivery, one question per message max, no filler, no "would you like me to…" chains.

## 1. THE PACK YOU RECEIVED

The zip (`SVET_FULL_PACK_2026-07-22.zip`) contains:
- `SYSTEM/` — the complete system pack (docs, engines, protocols, Pine scripts) incl. this session's additions
- `brief_state.zip` — **THE LIVING STATE. Critical, see §2.**
- `DAILY_UPLOAD/` — the 9-file daily run pack (what he attaches each morning)
- `payloads/`, `research/`, `mockups/` — this session's outputs
- This file, duplicated inside.

Read, in order, before doing anything: `SYSTEM/PROJECT_HANDOFF_MANIFEST.md`, `SYSTEM/MANIFEST_AMENDMENTS.md` (live vs superseded), `SYSTEM/00_MASTER_REFERENCE.md` (graveyard laws bind all work), `SYSTEM/RUN_BRIEF.md`, `SYSTEM/CB12_PROTOCOL.md`.

## 2. STATE — HANDLE WITH CARE

`brief_state.zip` is append-only and is the ONLY place the live track record exists. His saved copy is the living state; any copy in project knowledge is a stale snapshot.

**Fork warning:** On 2026-07-22 no living state was attached, so the ritual ran from the SEED copy. The zip in this pack is that fork. It contains **Track B entry #1**: `2026-07-22, down, low, "IF SOL holds below 77.50 into the afternoon THEN grind toward 77.00-76.50", 77.50, ungraded`. If Svet ever surfaces an older living zip with prior Track B history, reconcile explicitly — never double-log, never regrade. Recovery rule: always extract a fresh copy of the original zip into a new directory; never re-run against a mutated working dir.

## 3. THE DAILY RITUAL ("run the brief")

He attaches `DAILY_UPLOAD` files + `brief_state.zip` and says "run the brief." Then:

1. Save everything into one working dir. `pip install yfinance --break-system-packages` (PEP 668 env), verify import.
2. `python3 run_day.py` (after 09:00 ET it applies `--at0900` semantics; brief engine v4.4 + M9b wall-builder with Binance endpoint fallbacks). If caches corrupt: `--rebuild`.
3. **Show the full printed brief unmodified.** No summarizing it away.
4. Calendar: fetch `https://nfs.faireconomy.media/ff_calendar_thisweek.json`, filter today · USD/JPY/EUR · High/Medium, flag anything in the 08:00–14:00 ET window. FOMC guard.
5. Headlines: web-search, 3–6 bullets + 2–3 sentence read, labeled **context-not-signal**.
6. **Track B (sealed, before 14:00 ET):** one SOL directional call, exact format `TRACK-B | date | dir | conf | IF…THEN… | key_level`. Append to `state/trackB_log.csv` (header: date,dir,conf,scenario,level,outcome). Grade yesterday's call if present. Re-zip state.
7. Compose the CB12.4 payloads (§4) per coin, per CB12_PROTOCOL: morning read 3–6 plain sentences per coin, N-line, OVR from day-type. If nothing is unusual, say so — never manufacture insight.
8. **Always return the updated `brief_state.zip`** via outputs + the payload lines, each coin's line clearly separated (he pastes per-coin; don't make him fish parts out of one blob).
9. Standing intraday offer: "recheck {coin}" re-derives that coin's plan from live price.

Option B (live money, never modify casually): FADE-K5 / DON-20 / DON-55, rule v1.2 (skip DON-55 when BTC pi-downtrend AND own-asset Hayden-4H ≠ Bull). Sizing 0.375%, ladder 0.375/0.25/0.125 at −3/−6. FTMO 2-Step Swing $100k. **If a day-plan opposes an open Option B position, the payload MUST carry the overlap warning ("you are LONG X — don't short your own book").** Promotion of anything into live rules only via the v1.2 chain: independence test → book impact → funded-ladder replay → version increment.

## 4. CB12.4 — THE TRADE COPILOT (current TradingView layer)

Script: `SYSTEM/CB12_4_copilot.txt` (add alongside CB12.2b which remains the fallback). Philosophy, learned over many painful iterations:
- **Lines are TRADES, not forecasts.** Each numbered trade (①②③, hue-coded) owns an entry ZONE, stop ZONE, TP zone(s), and its trajectory drawn from its own entry to its own TP.
- **Retrace grammar:** the break is never the entry; the retest of the broken level is. A "breaks down" row says WAIT; the next row is the retest entry.
- **Zero canned sentences in Pine.** Every table word ships in the payload, written fresh each morning by you. The script only renders.
- Table = trade cards: badge + WHEN | bold ACTION (entry · stop · TPs · odds) + WHY line. The row whose price band contains live price lights up, moves by itself, and fires a TV alert on change. Lighting is stateless (a latched stop-out option was offered, not yet requested).
- Voice calibration (he rejected all of these: "76% fade if push", "if slapped", "else 44%", over-compressed grids): the target voice is his own card — *"Possible short entry in area 158–159, confident target 155, possible 152, stop past 161 — careful of sweeps; if it fails past 161, wait for the pullback to xyz."* Actions + prices + odds + one-line reasons. Numbers only from banked stats.

**Payload grammar** (one line per coin):
```
CB12|{COIN}|{date}|UA:{u_abs}|CTX:{regime,..}|HDR:{header text}
|W{n}:{lo},{hi},{comp},{contact},{flag}
|T{n}:{short|long},{entryLo},{entryHi},{stopLo},{stopHi},{tp1},{tp2|-},{solid|dot|dash}
|G{k}:{badge 1/2/3/i}~{WHEN}~{ACTION}~{WHY}~{bandLo}:{bandHi}   ("-" = never lit; no "|" or "~" inside text)
|N:{one sentence}|OVR:{none|EXPANSION|QUIET}
```
Worked example: `payloads/CB12_4_SOL_payload.txt` (2026-07-22). Banked numbers for composing odds (era-proof): penetration ladder .3U→66 / .4U→71 / .5U→76 / .6U→79 / .8U→85 / 1.0U→89% through; day-type EXPANSION breaks 64% (×fast 70.2%), QUIET holds 69% (weekend 84.2%); VOTE 3+ reject → 67%; weekend breaks 36%; target-reach .16U→83 / .36U→53 / .87U→22%. Composed confidences are labeled reads, not certifications. brkPx convention ≈ zone edge + 0.6U.

## 5. RESEARCH LAW (binding)

No measurement without pre-registration. Placebo/matched baselines + BH-FDR q=.10 mandatory. Discovery ≠ findings; sealed split reserved for money tests and unconditional claims (refit on full history after a pass; regime-flip FAIL → map the flip, don't graveyard). Every quoted stat = FULL HISTORY headline + regime decomposition beside it (per-era, per-Hayden, per-asset, weekday/weekend); instability = REGIME MARKER, promoted as conditional. Every study launch states mode, data seen, regime columns in the message body. Standing verdicts: no day-frame edge (202 cells); intraday direction unforecastable; range forecastable (weekly .53 VALIDATED); all lower-TF gross edge ≈ 0 (Law 4). Never stack correlated filters without an independence study. Scenarios arm on 15m closes, die 14:00 ET.

## 6. OPEN ITEMS (surface, don't resurrect silently)

- **② question unanswered:** when a short's stop level breaks UP and price retraces into it — long with the break, or short again? CB12.4 currently renders short-again per his card. Ask when relevant.
- Lit-row latching (day-persistent stop-out state): offered, not requested.
- BTC/ETH/XRP CB12.4 trade cards: not yet composed (SOL only). Due next brief.
- 2026-07-22 brief facts if he returns same-day: SOL Track B down/low/77.50 sealed; BTC open DON55 long (overlap warning live); Trump speaks 15:00 ET (outside window).
- RSIDIV indicator test (2026-07-21, registered): reading signal ALIVE uncertified (+6–12pp @24h, 7/8 cells FDR, stable all regimes); money DEAD vs matched placebo; his 47/1 config UNDERPOWERED except SOL engine spark (49 trades, p=.035 @1000 reps) — **parked, NOT on FORWARD_REGISTER** by his instruction. Files in `research/`.
- se_ref_vec.csv hash mismatch (S8-4 SITUATION line silently skips); v5/v6 brief witness gap; XAU/XAG band recal pending (queue item 6); queue items 2–8 in the manifest await "Go".
- brief_state living-copy question: see §2 fork warning.

## 7. FIRST-CONTACT CHECKLIST FOR YOU

1. Read the five files in §1 before answering anything substantive.
2. If he says "run the brief": §3, exactly. If state zip is missing, STOP and ask for it (do not fork again silently — say what happened on 07-22).
3. Match his voice: short, direct, no cheerleading. Deliver, don't narrate.
4. When unsure between two readings of his ask, give your best one-line interpretation and ask ONE question — never five.
5. And again, because it is the rule he repeated three times in caps: **do not code unless told to code.**
