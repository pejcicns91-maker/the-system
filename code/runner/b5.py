# W2 B5 — forecaster on the full wide state, Brier-scored per frame. PREREG (binding, in README):
# walk-forward by calendar month of t_station; train = all months < m (warmup >= 12 months),
# test = month m; model = sklearn LogisticRegression(C=1.0, max_iter=200, class prior free),
# seed 20260723; features = station + FE25 one-hot ('na' is a level) + 35 t2 numerics
# (median-imputed on TRAIN only, standardized on TRAIN only); targets per frame F in
# {5m,15m,1h,4h,1d}: bounce_F=(fav_F>=.25)&(adv_F<.25), through_F=(adv_F>=.6) on rows where
# both fields exist; baseline = train-set base rate (constant predictor). Brier + skill
# (1 - Brier/Brier_base) per (frame, family, month). No peeking, no refits, no tuning.
import numpy as np, pandas as pd, json, os, time, argparse, hashlib
ap = argparse.ArgumentParser(); ap.add_argument("--budget-min", type=float, default=230)
A = ap.parse_args()
np.random.seed(20260723)
from sklearn.linear_model import LogisticRegression
SF = "b5_state.json"; OUTF = "b5_scores.csv"
V = pd.read_parquet("bf_vantage_ALL_wide.parquet")
ts = pd.to_datetime(V.t_station, unit="ms", utc=True)
V["month"] = ts.dt.strftime("%Y-%m")
FE25 = ['station','coin','etype','zone','virgin','cb_','wq_','session','wknd','hayden','hayden_btc','btc_pi',
        'origin','tn_','dq_','sq_','vq_','rq_','kq_','uq_','yd_arch','ob55','dtype','lean','scen_state','scen_failed']
# rebuild the binned cats exactly as the ladder does
for col, q in [('dq_','distU'),('sq_','speedUh'),('vq_','relvol'),('wq_','widthU'),
               ('rq_','rng_used'),('kq_','wk_used'),('uq_','u_trend')]:
    try: V[col] = pd.qcut(pd.to_numeric(V[q], errors='coerce'), 4, duplicates='drop').astype(str)
    except Exception: V[col] = "na"
V['cb_'] = pd.cut(V.contact, [-1,30,49.5,101], labels=['c<30','c30-49','c>=50']).astype(str)
V['tn_'] = pd.cut(pd.to_numeric(V.test_no, errors='coerce'), [0,1,2,99], labels=['t1','t2','t3+']).astype(str)
for c in FE25: V[c] = V[c].astype(str).fillna("na")
T2 = [f"{b}_{f}" for b in ['net100','net20','rng100','pos100','volr','zt100','zlast']
      for f in ['5m','15m','1h','4h','1d']]
X_cat = pd.get_dummies(V[FE25], dtype=np.float32)
X_num = V[T2].astype(np.float32)
FR = {'5m': ('fwd_favU','fwd_advU'), '15m': ('fav_15m','adv_15m'), '1h': ('fav_1h','adv_1h'),
      '4h': ('fav_4h','adv_4h'), '1d': ('fav_1d','adv_1d')}
months = sorted(V.month.unique())
st = json.load(open(SF)) if os.path.exists(SF) else {"mi": 12}
mi = st["mi"]; t0 = time.time()
res = pd.read_csv(OUTF).to_dict("records") if os.path.exists(OUTF) else []
while mi < len(months) and (time.time()-t0)/60 < A.budget_min:
    m = months[mi]
    tr = (V.month < m).values; te = (V.month == m).values
    for fr, (fc, ac) in FR.items():
        fav = V[fc].values; adv = V[ac].values
        ok = np.isfinite(fav) & np.isfinite(adv)
        for fam, y in [("bounce", (fav >= .25) & (adv < .25)), ("through", adv >= .6)]:
            trm = tr & ok; tem = te & ok
            if trm.sum() < 5000 or tem.sum() < 50: continue
            med = np.nanmedian(X_num.values[trm], axis=0)
            Xtr = np.hstack([X_cat.values[trm], np.where(np.isfinite(X_num.values[trm]), X_num.values[trm], med)])
            Xte = np.hstack([X_cat.values[tem], np.where(np.isfinite(X_num.values[tem]), X_num.values[tem], med)])
            mu = Xtr.mean(0); sd = Xtr.std(0) + 1e-9
            Xtr = (Xtr-mu)/sd; Xte = (Xte-mu)/sd
            ytr = y[trm].astype(int); yte = y[tem].astype(int)
            clf = LogisticRegression(C=1.0, max_iter=200, random_state=20260723)
            clf.fit(Xtr, ytr)
            p = clf.predict_proba(Xte)[:, 1]
            base = ytr.mean()
            br = float(np.mean((p-yte)**2)); brb = float(np.mean((base-yte)**2))
            res.append(dict(month=m, frame=fr, family=fam, n_test=int(tem.sum()),
                            brier=round(br,5), brier_base=round(brb,5),
                            skill=round(1-br/brb,4) if brb>0 else np.nan, base=round(base,4)))
    mi += 1
    pd.DataFrame(res).to_csv(OUTF, index=False)
    json.dump({"mi": mi}, open(SF, 'w'))
    print(f"month {m} done ({mi}/{len(months)}) {(time.time()-t0)/60:.1f}min", flush=True)
if mi >= len(months):
    R = pd.DataFrame(res)
    agg = R.groupby(["frame","family"]).apply(lambda g: pd.Series(dict(
        months=len(g), med_skill=g.skill.median(), pos_months=(g.skill>0).mean()))).round(4)
    print("B5 COMPLETE"); print(agg.to_string())
    print("sha", hashlib.sha256(open(OUTF,'rb').read()).hexdigest()[:12])
else:
    print("chunk done; resume next run")
