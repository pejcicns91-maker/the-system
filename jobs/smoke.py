# SMOKE — proves the runner loop end-to-end + the drift law. Reads the pack's core tables,
# asserts the sealed counts, writes results/smoke_report.txt. Any FAIL = environment/vendor
# drift: STOP and report in chat. Accepts --budget-min for interface compatibility (unused).
import pandas as pd, argparse, os
ap = argparse.ArgumentParser(); ap.add_argument("--budget-min", type=float, default=10)
A, _ = ap.parse_known_args()
os.makedirs("results", exist_ok=True)
checks = []
def chk(name, val, exp):
    ok = (val == exp); checks.append((name, val, exp, ok))
    print(("PASS" if ok else "FAIL"), name, f"{val:,}", "expected", f"{exp:,}", flush=True)
for c in ["BTC", "ETH", "SOL", "XRP"]:
    chk(f"raw {c} 5m bars", len(pd.read_parquet(f"data/raw/{c}_5m_frozen_2021-09_2026-07-06.parquet")), 509720)
chk("M1_state level-days", len(pd.read_parquet("data/state/M1_state.parquet")), 135360)
chk("vantage rows", len(pd.read_parquet("data/state/bf_vantage_ALL_5m.parquet")), 585176)
chk("level_events", len(pd.read_parquet("data/events/level_events_v4.parquet")), 64291)
chk("battery trades", len(pd.read_parquet("data/results/battery_trades.parquet")), 186208)
ok = all(x[3] for x in checks)
open("results/smoke_report.txt", "w").write("\n".join(
    f"{'PASS' if o else 'FAIL'} {n}: {v:,} (expected {e:,})" for n, v, e, o in checks)
    + f"\nverdict: {'ALL PASS' if ok else 'DRIFT - STOP AND REPORT'}\n")
print("SMOKE", "ALL PASS" if ok else "DRIFT - STOP, report in chat", flush=True)
raise SystemExit(0 if ok else 1)
