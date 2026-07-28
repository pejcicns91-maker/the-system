import numpy as np, pandas as pd, json, hashlib, sys
np.random.seed(20260723)
COINS={"BTC":"BTCUSDT","ETH":"ETHUSDT","SOL":"SOLUSDT","XRP":"XRPUSDT"}
GRAV=[(0.0,56.4),(0.03,42.8),(0.26,32.2),(0.46,22.2),(1.1,9.8),(3.0,0.5)]
def grav(g): return float(np.interp(min(max(g,0),3.0),[x for x,_ in GRAV],[y for _,y in GRAV]))
def poc_arr(h,l,c,v):
    if len(h)==0: return np.nan
    lo,hi=l.min(),h.max()
    if hi<=lo: return float(c[-1])
    bins=np.linspace(lo,hi,101); mid=(h+l)/2
    ix=np.clip(np.digitize(mid,bins)-1,0,99)
    vv=np.bincount(ix,weights=v,minlength=100)
    a=int(vv.argmax()); return float((bins[a]+bins[a+1])/2)
def wilder_rsi(x,n=14):
    dd=np.diff(x,prepend=x[0]); up=np.where(dd>0,dd,0.); dn=np.where(dd<0,-dd,0.)
    r=np.full(len(x),np.nan)
    if len(x)<n+2: return r
    au,ad=up[1:n+1].mean(),dn[1:n+1].mean(); r[n]=100-100/(1+au/max(ad,1e-12))
    for i in range(n+1,len(x)):
        au=(au*(n-1)+up[i])/n; ad=(ad*(n-1)+dn[i])/n; r[i]=100-100/(1+au/max(ad,1e-12))
    return r
def hayden_state(h4c):  # state machine over ohlc4 rsi, m9b thresholds
    r=wilder_rsi(h4c); cur=0
    for i in range(1,len(r)):
        r0,r1=r[i-1],r[i]
        if np.isnan(r1): continue
        if r1>67 and (np.isnan(r0) or r0<=67): cur=1
        elif r1<33 and (np.isnan(r0) or r0>=33): cur=2
        elif cur==1 and r1<39 and r0>=39: cur=3
        elif cur==2 and r1>61 and r0<=61: cur=3
    return {1:'Bull',2:'Bear',0:'Chop',3:'Chop'}[cur]
LV=['PDH','PDL','PDC','PDPOC','ONH','ONL','ONC','ONPOC','PSH','PSL','PSC','PSPOC',
    'PWH','PWL','PWC','PWPOC','PMH','PML','PMC','PMPOC']

def build_walls_series(sym):
    df=pd.read_csv(f"data/{sym}_5m.csv")
    for c_ in "ohlcv": df[c_]=df[c_].astype(float)
    df['dt']=pd.to_datetime(df.t,unit='ms',utc=True)
    et=df.dt.dt.tz_convert('America/New_York')
    df['wd']=(et-pd.Timedelta(hours=8)).dt.date
    df['hr']=et.dt.hour
    days=sorted(df.wd.unique())
    G={d:g for d,g in df.groupby('wd')}
    # per-day aggregates
    dayagg={}
    for d in days:
        g=G[d]; a=g.h.values; b=g.l.values; c=g.c.values; v=g.v.values
        on=g[(g.hr>=17)|(g.hr<8)]; ps=g[(g.hr>=8)&(g.hr<17)]
        dayagg[d]={'H':a.max(),'L':b.min(),'C':c[-1],'POC':poc_arr(a,b,c,v),
                   'rng':a.max()-b.min(),
                   'ONH':on.h.max() if len(on) else np.nan,'ONL':on.l.min() if len(on) else np.nan,
                   'ONC':on.c.iloc[-1] if len(on) else np.nan,
                   'ONPOC':poc_arr(on.h.values,on.l.values,on.c.values,on.v.values) if len(on) else np.nan,
                   'PSH':ps.h.max() if len(ps) else np.nan,'PSL':ps.l.min() if len(ps) else np.nan,
                   'PSC':ps.c.iloc[-1] if len(ps) else np.nan,
                   'PSPOC':poc_arr(ps.h.values,ps.l.values,ps.c.values,ps.v.values) if len(ps) else np.nan}
    # week/month aggregates keyed by iso-week / month
    df['iso']=[pd.Timestamp(x).isocalendar()[:2] for x in df.wd]
    df['mon']=[str(x)[:7] for x in df.wd]
    wkagg={k:{'H':g.h.max(),'L':g.l.min(),'C':g.c.iloc[-1],
              'POC':poc_arr(g.h.values,g.l.values,g.c.values,g.v.values)} for k,g in df.groupby('iso')}
    moagg={k:{'H':g.h.max(),'L':g.l.min(),'C':g.c.iloc[-1],
              'POC':poc_arr(g.h.values,g.l.values,g.c.values,g.v.values)} for k,g in df.groupby('mon')}
    isolist=sorted(wkagg); monlist=sorted(moagg)
    h4=df.set_index('dt').resample('4h').agg({'o':'first','h':'max','l':'min','c':'last'}).dropna()
    h4x=((h4.o+h4.h+h4.l+h4.c)/4)
    out={}
    for di in range(35,len(days)):
        d=days[di]; prev=days[di-1]
        V={}
        pa=dayagg[prev]
        V['PDH'],V['PDL'],V['PDC'],V['PDPOC']=pa['H'],pa['L'],pa['C'],pa['POC']
        # ON of day d (17:00 prev-evening .. 08:00) is inside wd==d per m9b
        V['ONH'],V['ONL'],V['ONC'],V['ONPOC']=pa['ONH'],pa['ONL'],pa['ONC'],pa['ONPOC']  # FIX: completed overnight (prev-wd), no lookahead
        V['PSH'],V['PSL'],V['PSC'],V['PSPOC']=pa['PSH'],pa['PSL'],pa['PSC'],pa['PSPOC']
        iso=pd.Timestamp(d).isocalendar()[:2]
        pws=[k for k in isolist if k<iso]
        if pws:
            wk=wkagg[pws[-1]]; V['PWH'],V['PWL'],V['PWC'],V['PWPOC']=wk['H'],wk['L'],wk['C'],wk['POC']
        else:
            V['PWH']=V['PWL']=V['PWC']=V['PWPOC']=np.nan
        m0=str(d)[:7]
        pms=[k for k in monlist if k<m0]
        if pms:
            mo=moagg[pms[-1]]; V['PMH'],V['PML'],V['PMC'],V['PMPOC']=mo['H'],mo['L'],mo['C'],mo['POC']
        else:
            V['PMH']=V['PML']=V['PMC']=V['PMPOC']=np.nan
        rngs=[dayagg[days[j]]['rng'] for j in range(max(0,di-14),di)]
        uAbs=float(np.median(rngs[-14:])) if rngs else np.nan
        yh,yl=pa['H'],pa['L']
        def gapU(v):
            if not np.isfinite(v) or not np.isfinite(uAbs): return 9.9
            if yl<=v<=yh: return 0.0
            return float(min(abs(v-yh),abs(v-yl))/uAbs)
        def am20(v):
            cnt=0
            for j in range(max(0,di-20),di):
                dd2=dayagg[days[j]]
                if dd2['L']<=v<=dd2['H']: cnt+=1
            return cnt
        vals=np.array([V.get(l_,np.nan) for l_ in LV]); okm=np.isfinite(vals)
        order=np.argsort(vals[okm]); names=np.array(LV)[okm][order]; sv=vals[okm][order]
        wid=np.zeros(len(sv),int); w=0
        for j in range(1,len(sv)):
            if sv[j]-sv[j-1]>0.25*uAbs: w+=1
            wid[j]=w
        walls=[]
        for wl in range(w+1):
            m=wid==wl; mem=names[m]; lo,hi=sv[m].min(),sv[m].max()
            cc=grav(min(gapU(V[x]) for x in mem))
            vg=all(am20(V[x])==0 for x in mem)
            walls.append((float(lo),float(hi),float(cc),bool(vg)))
        # hayden as-of d: trailing 40d of 4h ohlc4 strictly before boundary
        bnd=pd.Timestamp(d).tz_localize('America/New_York')+pd.Timedelta(hours=8)
        hseg=h4x[(h4x.index<bnd)&(h4x.index>=bnd-pd.Timedelta(days=40))].values
        hay=hayden_state(hseg) if len(hseg)>20 else 'na'
        out[d]={'walls':walls,'uAbs':uAbs,'hayden':hay}
    return df,days,out

def run_coin(nm,sym):
    df,days,W=build_walls_series(sym)
    trades=[]
    G={d:g for d,g in df.groupby('wd')}
    for d in sorted(W):
        wd=W[d]; walls=wd['walls']; U=wd['uAbs']
        if not np.isfinite(U) or U<=0 or d not in G: continue
        g=G[d]; o=g.o.values; h=g.h.values; l=g.l.values; c=g.c.values; ts=g.t.values
        n=len(g)
        st=[]  # per wall: side state -1 below, 1 above, 0 inside; traded flag
        for (lo,hi,cc,vg) in walls:
            p0=o[0]
            st.append([-1 if p0<lo else (1 if p0>hi else 0), False])
        pos=None; skipped_busy=0; skipped_notp=0
        for i in range(n):
            # manage open position
            if pos is not None:
                sd,ent,stp,tp,ei,widx=pos
                stop_hit = (h[i]>=stp) if sd=='S' else (l[i]<=stp)
                tp_hit   = (l[i]<=tp) if sd=='S' else (h[i]>=tp)
                if i>ei or True:
                    if stop_hit:
                        trades.append(dict(coin=nm,day=str(d),t_entry=int(ts[ei]),t_exit=int(ts[i]),side=sd,entry=ent,exit=stp,R=-1.0,widx=widx,res='stop')); pos=None
                    elif tp_hit:
                        r=abs(ent-tp)/(0.6*U)
                        trades.append(dict(coin=nm,day=str(d),t_entry=int(ts[ei]),t_exit=int(ts[i]),side=sd,entry=ent,exit=tp,R=r if False else (ent-tp)/(0.6*U) if sd=='S' else (tp-ent)/(0.6*U),widx=widx,res='tp')); pos=None
            # update wall states / entries
            for k,(lo,hi,cc,vg) in enumerate(walls):
                side,traded=st[k]
                if side==-1 and h[i]>=lo:
                    if not traded:
                        st[k][1]=True
                        if pos is None:
                            tpc=[w2[1] for w2 in walls if w2[1]<lo]
                            if tpc:
                                ent=max(o[i],lo)*1.0; ent=max(ent,lo)
                                ent=lo if o[i]<lo else o[i]
                                stp=lo+0.6*U; tp=max(tpc)
                                # same-bar: stop priority
                                if h[i]>=stp:
                                    trades.append(dict(coin=nm,day=str(d),t_entry=int(ts[i]),t_exit=int(ts[i]),side='S',entry=ent,exit=stp,R=(ent-stp)/(0.6*U),widx=k,res='stop'))
                                elif l[i]<=tp:
                                    trades.append(dict(coin=nm,day=str(d),t_entry=int(ts[i]),t_exit=int(ts[i]),side='S',entry=ent,exit=tp,R=(ent-tp)/(0.6*U),widx=k,res='tp'))
                                else:
                                    pos=('S',ent,stp,tp,i,k)
                            else: skipped_notp+=1
                        else: skipped_busy+=1
                    st[k][0]= 0 if l[i]<hi else 0
                    st[k][0]= 1 if l[i]>hi else 0
                elif side==1 and l[i]<=hi:
                    if not traded:
                        st[k][1]=True
                        if pos is None:
                            tpc=[w2[0] for w2 in walls if w2[0]>hi]
                            if tpc:
                                ent=hi if o[i]>hi else o[i]
                                stp=hi-0.6*U; tp=min(tpc)
                                if l[i]<=stp:
                                    trades.append(dict(coin=nm,day=str(d),t_entry=int(ts[i]),t_exit=int(ts[i]),side='L',entry=ent,exit=stp,R=(stp-ent)/(0.6*U),widx=k,res='stop'))
                                elif h[i]>=tp:
                                    trades.append(dict(coin=nm,day=str(d),t_entry=int(ts[i]),t_exit=int(ts[i]),side='L',entry=ent,exit=tp,R=(tp-ent)/(0.6*U),widx=k,res='tp'))
                                else:
                                    pos=('L',ent,stp,tp,i,k)
                            else: skipped_notp+=1
                        else: skipped_busy+=1
                    st[k][0]= -1 if h[i]<lo else 0
                else:
                    if side==0:
                        if c[i]<lo: st[k][0]=-1
                        elif c[i]>hi: st[k][0]=1
            if i==n-1 and pos is not None:
                sd,ent,stp,tp,ei,widx=pos
                r=((ent-c[i]) if sd=='S' else (c[i]-ent))/(0.6*U)
                trades.append(dict(coin=nm,day=str(d),t_entry=int(ts[ei]),t_exit=int(ts[i]),side=sd,entry=ent,exit=c[i],R=r,widx=widx,res='time'))
                pos=None
        # attach day meta to trades of this day
        for t in trades:
            if t['day']==str(d) and 'hayden' not in t:
                t['hayden']=wd['hayden']; t['U']=U
                lo,hi,cc,vg=walls[t['widx']]
                t['contact']=cc; t['virgin']=vg
    return pd.DataFrame(trades),W

res={}; allt=[]
for nm,sym in COINS.items():
    tdf,W=run_coin(nm,sym)
    allt.append(tdf)
    # port validation for 2026-07-23
    d=[k for k in W if str(k)=='2026-07-23']
    if d:
        wd=W[d[0]]
        res[nm+'_port']={'uAbs':round(wd['uAbs'],5),'walls':[(round(a,4),round(b,4),round(c,0)) for a,b,c,_ in wd['walls']]}
    print(nm,"trades",len(tdf),flush=True)
T=pd.concat(allt,ignore_index=True)
T.to_csv("mm1_trades.csv",index=False)
json.dump(res,open("mm1_port_validation.json","w"),indent=1)
print("saved",len(T))
