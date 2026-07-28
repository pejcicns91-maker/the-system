#!/usr/bin/env python3
"""run_day.py — THE ONE MORNING COMMAND (system v2.1, hardened 2026-07-15).
Attach DAILY_UPLOAD.zip + your brief_state.zip, say "run the day".
Steps: 1) deps  2) the brief (clock-aware flag)  3) rebuild+return the state zip
       4) today's CB11 wall payloads (self-fetched, day-type handed from the brief)."""
import subprocess, sys, os, re, datetime

# 1) dependency self-install
try:
    import yfinance  # noqa
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','yfinance','--break-system-packages','-q'])

here = os.path.dirname(os.path.abspath(__file__))
print("="*60); print("THE SYSTEM — MORNING RUN"); print("="*60)

# 2) the brief
brief_out = ''
b = os.path.join(here, 'brief_engine_v4.py')
if os.path.exists(b):
    print("\n--- 1. THE BRIEF (Option B · regime · day-type · budgets) ---")
    try:
        import zoneinfo
        now_et = datetime.datetime.now(zoneinfo.ZoneInfo('America/New_York'))
    except Exception:
        now_et = datetime.datetime.utcnow() - datetime.timedelta(hours=4)
    flag = ['--at0900'] if now_et.hour >= 9 else []
    if not flag:
        print(f"[clock] {now_et:%H:%M} ET — before 9: pre-9 mode (no --at0900); Yahoo-settle risk accepted")
    r = subprocess.run([sys.executable, b] + flag, capture_output=True, text=True)
    brief_out = r.stdout if r.returncode == 0 else ''
    print(brief_out if brief_out else f"brief failed: {r.stderr[-800:]}\n(attach brief_state.zip and rerun)")
else:
    print("\n[brief_engine_v4.py not found beside this script — attach your brief kit]")

# 3) the living state, handed back (the ENGINE writes ./brief_state.zip in its own format)
src = 'brief_state.zip' if os.path.exists('brief_state.zip') else os.path.join(here, 'brief_state.zip')
if os.path.exists(src):
    out = '/mnt/user-data/outputs/brief_state.zip' if os.path.isdir('/mnt/user-data/outputs') else src
    if os.path.abspath(src) != os.path.abspath(out):
        import shutil; shutil.copy(src, out)
    print(f"\n*** UPDATED brief_state.zip -> {out} — SAVE THIS COPY; it is the living state. ***")
else:
    print("\n[engine did not produce brief_state.zip — check the brief step above]")

# 4) CB11 payloads (fresh-fetched; day-type handed over from the brief automatically)
print("\n--- 2. CB11 CHART PAYLOADS (paste your coin's line into CB11) ---")
dts = re.findall(r'CB2\|(\w+)\|[^\n]*?\|type:(\w+)', brief_out)
dtmap = ','.join(f'{a}:{t}' for a, t in dts if a in ('BTC','ETH','SOL','XRP'))
dtarg = ['--dtype', dtmap] if dtmap else []
r = subprocess.run([sys.executable, os.path.join(here, 'm9b_daily.py')] + dtarg,
                   capture_output=True, text=True, timeout=900)
print(r.stdout if r.stdout.strip() else f"m9b fetch failed: {r.stderr[-300:]}")

print("\n--- 3. AT THE CHART ---")
print("CB11 draws the walls; set ARMED WALL # as price approaches one;")
print("live thrust/drive/wear, the vote, the escalation ladder. Eyes decide.")
print("Option B trades what's mechanical. The forward register scores all.")
print("\n--- 4. AI: NOW WRITE THE MORNING READ + ZONE PLANS (CB12_PROTOCOL.md) ---")
print("Per coin: 3-6 sentence read · S-fields per shortlisted wall · N nuance line · OVR flag.")
print("Append S/N/OVR to the payload lines above and hand the finished CB12 lines to the user.")
