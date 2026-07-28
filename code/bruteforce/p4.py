import numpy as np, pandas as pd, json, hashlib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import brier_score_loss, roc_auc_score
SEED=20260723
T=pd.read_csv("p2_events_ALL.csv")
E=T[T.etype!='RETEST'].copy()
CATS=['coin','side','session','hayden','hayden_btc','btc_pi','origin','etype']
NUMS=['contact','confl','widthU','ladder_ix','dnextU','dbehindU','last_tradedd','distU','speedUh',
      'bars_route','pullbacks','bodyU','relvol','test_no','hrs_since8','wk_used','mo_day','rng_used','u_trend','U']
BOOLS=['virgin','stepPOC','above_open','wknd','gap','fomc']
def frame(X,extra_num=()):
    F=X.copy()
    for b in BOOLS: F[b]=F[b].astype(float)
    cats=[c for c in CATS if c in F and c!='etype' or (c=='etype' and 'etype' in extra_num)]
    cats=[c for c in CATS if c!='etype']
    nums=[c for c in NUMS+list(extra_num) if c in F]
    enc=OrdinalEncoder(handle_unknown='use_encoded_value',unknown_value=-1)
    Xc=enc.fit_transform(F[cats].astype(str))
    Xn=F[nums+BOOLS].apply(pd.to_numeric,errors='coerce').values
    M=np.hstack([Xc,Xn]); names=cats+nums+BOOLS
    mask=[True]*len(cats)+[False]*(len(nums)+len(BOOLS))
    return M,names,mask
def timesplit(X):
    X2=X.assign(_o=pd.to_datetime(X.day).astype('int64'))
    cut=X2.groupby('coin')._o.transform(lambda s: s.quantile(0.8))
    return X2._o<cut
def run(name,X,y,extra=()):
    M,names,mask=frame(X,extra)
    tr=timesplit(X).values; te=~tr
    base=float(y[tr].mean())
    clf=HistGradientBoostingClassifier(random_state=SEED,max_iter=250,learning_rate=0.08,
                                       categorical_features=mask)
    clf.fit(M[tr],y[tr])
    p=clf.predict_proba(M[te])[:,1]
    bm=brier_score_loss(y[te],p); bb=brier_score_loss(y[te],np.full(te.sum(),base))
    skill=1-bm/bb; auc=roc_auc_score(y[te],p) if 0<y[te].mean()<1 else np.nan
    q=pd.qcut(p,10,duplicates='drop')
    cal=pd.DataFrame({'p':p,'y':y[te]}).groupby(q,observed=True).agg(pred=('p','mean'),real=('y','mean'),n=('y','size'))
    return dict(n_train=int(tr.sum()),n_test=int(te.sum()),base_test=round(float(y[te].mean()),3),
                brier_model=round(float(bm),4),brier_base=round(float(bb),4),skill=round(float(skill),3),
                auc=round(float(auc),3),
                calib=[[round(float(r.pred),3),round(float(r.real),3),int(r.n)] for r in cal.itertuples()])
out={}
C=E[E.etype.isin(['TOUCH','PEN','BREAK','TRAV'])].copy(); C['y']=C.etype.isin(['TOUCH','PEN']).astype(int)
out['hold_at_contact']=run('hold',C,C.y.values)
B=E[E.etype.isin(['BREAK','TRAV','EXIT'])].copy()
out['false_break']=run('fb',B,B.false_break.astype(int).values,extra=('depthU',))
out['reach_next_given_break']=run('reach',B,B.reached_next.astype(int).values,extra=('depthU',))
C['y2']=(C.etype.isin(['BREAK','TRAV']) & C.reached_next.fillna(False)).astype(int)
out['break_AND_reach_from_contact']=run('chain',C,C.y2.values)
json.dump(out,open('p4_scores.json','w'),indent=1)
for k,v in out.items():
    print(k,"| n_test",v['n_test'],"base",v['base_test'],"| Brier",v['brier_model'],"vs base",v['brier_base'],"| SKILL",v['skill'],"AUC",v['auc'])
    print("  calib(pred->real):",[(a,b) for a,b,_ in v['calib'][::3]])
print("sha",hashlib.sha256(open('p4_scores.json','rb').read()).hexdigest()[:12])
