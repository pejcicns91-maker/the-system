# B2 tranche: ladder depth 1-2 over vantage rows (5m frame), reaction profile per cell.
import numpy as np, pandas as pd, hashlib, json
from scipy import stats
V=pd.concat([pd.read_parquet(f"bf_vantage_{c}_5m.parquet") for c in ["BTC","ETH","SOL","XRP"]],ignore_index=True)
V.to_parquet("bf_vantage_ALL_5m.parquet",index=False)
V['bounce']=(V.fwd_favU>=0.25)&(V.fwd_advU<0.25)
V['through']=V.fwd_advU>=0.6
for col,q in [('dq','distU'),('sq','speedUh'),('vq','relvol'),('wq','widthU'),('rq','rng_used'),('kq','wk_used'),('uq','u_trend')]:
    try: V[col]=pd.qcut(pd.to_numeric(V[q],errors='coerce'),4,duplicates='drop')
    except Exception: V[col]=np.nan
V['cb']=pd.cut(V.contact,[-1,30,49.5,101],labels=['c<30','c30-49','c>=50'])
V['tn']=pd.cut(pd.to_numeric(V.test_no,errors='coerce'),[0,1,2,99],labels=['t1','t2','t3+'])
FE=['coin','etype','zone','virgin','cb','wq','session','wknd','hayden','hayden_btc','btc_pi','origin','tn','dq','sq','vq','rq','kq','uq']
def ladder(Y,fam):
    out=[]; base=V[Y].mean()
    g=V.groupby('station',observed=True)[Y].agg(['mean','count'])   # depth 0: station alone
    for k,r in g.iterrows():
        if r['count']>=40: out.append((fam,0,'station',str(k),'-','-',round(r['mean'],3),round(base,3),int(r['count']),np.nan))
    for f in FE:   # depth 1: station x feature
        gg=V.groupby(['station',f],observed=True)[Y].agg(['sum','count'])
        for k,r in gg.iterrows():
            n=int(r['count'])
            if n<40: continue
            p=stats.binomtest(int(r['sum']),n,base).pvalue
            out.append((fam,1,'station',str(k[0]),f,str(k[1]),round(r['sum']/n,3),round(base,3),n,p))
    for i in range(len(FE)):   # depth 2: station x feature x feature (full, no seeding)
        for j in range(i+1,len(FE)):
            gg=V.groupby(['station',FE[i],FE[j]],observed=True)[Y].agg(['sum','count'])
            for k,r in gg.iterrows():
                n=int(r['count'])
                if n<40: continue
                p=stats.binomtest(int(r['sum']),n,base).pvalue
                out.append((fam,2,f'station|{FE[i]}',f'{k[0]}|{k[1]}',FE[j],str(k[2]),round(r['sum']/n,3),round(base,3),n,p))
    return out
rows=ladder('bounce','bounce')+ladder('through','through')
L=pd.DataFrame(rows,columns=['family','depth','f1','v1','f2','v2','rate','base','n','p'])
for fam in L.family.unique():   # BH within family over tested cells
    m=L[(L.family==fam)&L.p.notna()]
    ps=m.p.values; order=np.argsort(ps); kmax=0
    for rank,ix in enumerate(order,1):
        if ps[ix]<=0.10*rank/len(ps): kmax=rank
    ok=np.zeros(len(ps),bool); ok[order[:kmax]]=True
    L.loc[m.index,'certified']=ok
L.to_csv("bf_ladder_d012.csv",index=False)
print("vantage ALL:",len(V),"| ladder cells tested:",int(L.p.notna().sum()),"certified:",int(L.certified.fillna(False).sum()))
print("bounce base:",round(V.bounce.mean(),3),"through base:",round(V.through.mean(),3))
st=V.groupby('station',observed=True).agg(bounce=('bounce','mean'),through=('through','mean'),n=('bounce','size')).round(3)
print(st.to_string())
top=L[(L.certified==True)&(L.depth==2)].assign(lift=lambda x:(x.rate-x.base).abs()).nlargest(8,'lift')
print(top[['family','v1','f2','v2','rate','base','n']].to_string(index=False))
print("sha",hashlib.sha256(open('bf_ladder_d012.csv','rb').read()).hexdigest()[:12])
