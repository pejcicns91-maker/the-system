import numpy as np, pandas as pd, json, hashlib
from scipy import stats
T=pd.read_csv("p2_events_ALL.csv")
R=T[T.etype=='RETEST'].copy(); E=T[T.etype!='RETEST'].copy()
C=E[E.etype.isin(['TOUCH','PEN','BREAK','TRAV'])].copy()   # contact events
B=E[E.etype.isin(['BREAK','TRAV','EXIT'])].copy()          # break-class
C['held']=C.etype.isin(['TOUCH','PEN'])
Rv=R[R.flip.isin(['held','failed'])].copy(); Rv['flipped']=Rv.flip=='held'
# graze line from distribution (p25 of contact depth)
d=C.depthU.dropna(); p25,p75=d.quantile(.25),d.quantile(.75)
C['depth_cls']=pd.cut(C.depthU,[-1,p25,p75,99],labels=[f'graze<= {p25:.3f}',f'mid',f'deep>{p75:.3f}'])
def B_(s,q=4,lab=None):
    try: return pd.qcut(s,q,duplicates='drop')
    except Exception: return s
feats={}
for X in (C,B,Rv):
    X['cb']=pd.cut(X.contact,[-1,30,49.5,101],labels=['c<30','c30-49','c>=50'])
    for col,src in [('dq','distU'),('sq','speedUh'),('vq','relvol'),('wq','widthU'),
                    ('nq','dnextU'),('rq','rng_used'),('kq','wk_used'),('uq','u_trend'),('hq','hrs_since8')]:
        if src in X: X[col]=B_(pd.to_numeric(X[src],errors='coerce'))
    X['tn']=pd.cut(pd.to_numeric(X.get('test_no',np.nan),errors='coerce'),[0,1,2,99],labels=['t1','t2','t3+'])
FEATS=['coin','side','session','wknd','hayden','hayden_btc','btc_pi','virgin','stepPOC','cb','gap','fomc','origin','tn','dq','sq','vq','wq','nq','rq','kq','uq','hq','depth_cls','etype']
def marg(X,ycol,feats):
    out={}; base=float(X[ycol].mean()); N=len(X)
    for f in feats:
        if f not in X: continue
        g=X.groupby(f,observed=True)[ycol].agg(['mean','count'])
        out[f]={str(k):[round(float(v['mean']),3),int(v['count'])] for k,v in g.iterrows() if v['count']>0}
    return dict(base=round(base,3),n=N,by=out)
T1={'hold_at_contact':marg(C,'held',FEATS),
    'reach_next_given_break':marg(B,'reached_next',FEATS),
    'false_break':marg(B,'false_break',FEATS),
    'retest_flip':marg(Rv,'flipped',['coin','side','retest_no'])}
T1['depth_quantiles']=[round(float(x),3) for x in d.quantile([.1,.25,.5,.75,.9])]
T1['retest_occurrence']=round(float(R.parent.nunique()/max(1,len(B))),3)
json.dump(T1,open('p3_t1.json','w'),indent=1)
# T2 pairs with FDR per outcome family
def pairs(X,ycol,feats,fam):
    base=X[ycol].mean(); rows=[]
    fs=[f for f in feats if f in X.columns]
    for i in range(len(fs)):
        for j in range(i+1,len(fs)):
            g=X.groupby([fs[i],fs[j]],observed=True)[ycol].agg(['sum','count'])
            for k,v in g.iterrows():
                n=int(v['count']); 
                if n<40: continue
                p=stats.binomtest(int(v['sum']),n,base).pvalue
                rows.append((fam,fs[i],str(k[0]),fs[j],str(k[1]),round(float(v['sum']/n),3),round(float(base),3),n,p))
    return rows
fams=[('hold',C,'held'),('reach',B,'reached_next'),('fb',B,'false_break')]
allrows=[]
for fam,X,y in fams:
    rr=pairs(X,y,[f for f in FEATS if f not in ('etype','depth_cls')],fam)
    ps=[r[8] for r in rr]; m=len(ps)
    if m:
        order=np.argsort(ps); passed=set()
        kmax=0
        for rank,ix in enumerate(order,1):
            if ps[ix]<=0.10*rank/m: kmax=rank
        for rank,ix in enumerate(order,1):
            if rank<=kmax: passed.add(ix)
        for ix,r in enumerate(rr): allrows.append(r+(ix in passed,))
P=pd.DataFrame(allrows,columns=['family','f1','v1','f2','v2','rate','base','n','p','certified'])
P.to_csv('p3_t2_register.csv',index=False)
cert=P[P.certified].copy(); cert['lift']=(cert.rate-cert.base).abs()
# T3: triples seeded by top certified pairs
t3rows=[]
for fam,X,y in fams:
    cf=cert[cert.family==fam].nlargest(15,'lift')
    base=X[y].mean()
    for _,r in cf.iterrows():
        for f3 in ['coin','hayden','wknd','session','cb','btc_pi']:
            if f3 in (r.f1,r.f2) or f3 not in X: continue
            sub=X[(X[r.f1].astype(str)==r.v1)&(X[r.f2].astype(str)==r.v2)]
            g=sub.groupby(f3,observed=True)[y].agg(['sum','count'])
            for k,v in g.iterrows():
                n=int(v['count'])
                if n<40: continue
                p=stats.binomtest(int(v['sum']),n,base).pvalue
                t3rows.append((fam,r.f1,r.v1,r.f2,r.v2,f3,str(k),round(float(v['sum']/n),3),round(float(base),3),n,p))
T3=pd.DataFrame(t3rows,columns=['family','f1','v1','f2','v2','f3','v3','rate','base','n','p'])
if len(T3):
    ps=T3.p.values; m=len(ps); order=np.argsort(ps); kmax=0
    for rank,ix in enumerate(order,1):
        if ps[ix]<=0.10*rank/m: kmax=rank
    ok=np.zeros(m,bool); ok[order[:kmax]]=True; T3['certified']=ok
T3.to_csv('p3_t3_register.csv',index=False)
# transitions: ladder delta to next event same day
E2=E.sort_values(['coin','day','t_event'])
E2['nz']=E2.groupby(['coin','day']).zone.shift(-1)
E2['delta']=(E2.nz-E2.zone)
tr=E2.dropna(subset=['delta']).groupby('etype').delta.value_counts(normalize=True).round(3)
trn=E2.dropna(subset=['delta']).groupby('etype').delta.count()
TRX={et:{str(int(dl)):float(v) for (e2,dl),v in tr.items() if e2==et and abs(dl)<=3} for et in E2.etype.unique() if et in trn}
json.dump({'delta_by_type':TRX,'n_by_type':{k:int(v) for k,v in trn.items()}},open('p3_transitions.json','w'),indent=1)
print("T1 keys:",list(T1.keys()))
print("T2 tests:",len(P),"certified:",int(P.certified.sum()),"underpowered(skipped n<40): implicit")
print("T3 tests:",len(T3),"certified:",int(T3.certified.sum()) if len(T3) else 0)
print("hold base:",T1['hold_at_contact']['base'],"n",T1['hold_at_contact']['n'])
print("reach base:",T1['reach_next_given_break']['base'],"| fb base:",T1['false_break']['base'],"| flip base:",T1['retest_flip']['base'],"n",T1['retest_flip']['n'])
print("graze line p25:",round(float(p25),3),"deep p75:",round(float(p75),3))
print("top certified:")
print(cert.nlargest(12,'lift')[['family','f1','v1','f2','v2','rate','base','n']].to_string(index=False))
for f in ['p3_t1.json','p3_t2_register.csv','p3_t3_register.csv','p3_transitions.json']:
    print(f,hashlib.sha256(open(f,'rb').read()).hexdigest()[:12])
