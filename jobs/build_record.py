#!/usr/bin/env python3
"""build_record.py — LAYER A: THE RECORD (per RECORD_SPEC_v0, signed 2026-07-27).
One row = one bar of one TF of one coin. TF-native. Native units. No thresholds stored.
Outputs -> results/record/: bars_{COIN}_{5m,15m,1h,4h,1D}.parquet, marks_*_{COIN}.parquet,
RECORD_COUNTS.md (reconciliation + sealed probes + named gaps). Cursor-resumable per coin.
Sealed probes (abort on fail): uAbs(SOL,2026-07-22)=2.515 | PWL_ET 73.39 | PDH_UTC 78.88 |
SOL 4h Hayden @2026-07-22 04:00 UTC = Bull | frozen-seam vendor check (detect, never absorb)."""
import pandas as pd, numpy as np, json, os, sys, time, argparse, urllib.request
ET='America/New_York'; COINS=['BTC','ETH','SOL','XRP']
ap=argparse.ArgumentParser(); ap.add_argument('--budget-min',type=float,default=230)
ap.add_argument('--fast',type=int,default=0)  # fast=1: skip tail fetch + seam check (frozen only; local test)
A,_=ap.parse_known_args(); T0=time.time()
OUT='results/record'; os.makedirs(OUT,exist_ok=True); os.makedirs('results/state',exist_ok=True)
SF='results/state/build_record.json'; st=json.load(open(SF)) if os.path.exists(SF) else {'done':[]}
TRUNC=int(os.environ.get('TEST_TRUNC','0'))

def fetch_tail(sym,start_ms,end_ms):
    rows=[];cur=start_ms
    hosts=['https://data-api.binance.vision','https://api.binance.com']
    while cur<end_ms:
        k=None
        for h in hosts:
            try:
                u=f"{h}/api/v3/klines?symbol={sym}&interval=5m&startTime={cur}&endTime={end_ms}&limit=1000"
                k=json.load(urllib.request.urlopen(u,timeout=30)); break
            except Exception: continue
        if not isinstance(k,list) or not k: break
        rows+=k; cur=k[-1][0]+300_000; time.sleep(0.1)
    if not rows: return pd.DataFrame(columns=['dt','o','h','l','c','v'])
    d=pd.DataFrame(rows).iloc[:,:6]; d.columns=['ot','o','h','l','c','v']
    d=d.astype({'o':float,'h':float,'l':float,'c':float,'v':float})
    d['dt']=pd.to_datetime(d.ot,unit='ms',utc=True); return d[['dt','o','h','l','c','v']]

def load5(coin):
    b=pd.read_parquet(f'data/raw/{coin}_5m_frozen_2021-09_2026-07-06.parquet')
    b['dt']=pd.to_datetime(b.dt,utc=True)
    if TRUNC: b=b.tail(TRUNC).reset_index(drop=True)
    if not A.fast:
        seam=b.tail(120)[['dt','o','h','l','c']]
        s_ms=int(seam.dt.iloc[0].timestamp()*1000); e_ms=int((seam.dt.iloc[-1]+pd.Timedelta(minutes=5)).timestamp()*1000)
        chk=fetch_tail(coin+'USDT',s_ms,e_ms)
        m=seam.merge(chk,on='dt',suffixes=('','_v'))
        if len(m)<100 or (np.abs(m.c-m.c_v)>0.01*m.c).any():
            print(f'FAIL vendor-seam {coin}: refetched bars diverge from frozen — STOP, report'); sys.exit(1)
        end=int(pd.Timestamp.now(tz='UTC').floor('5min').timestamp()*1000)
        t=fetch_tail(coin+'USDT',int(b.dt.iloc[-1].timestamp()*1000)+300_000,end)
        b=pd.concat([b,t]).drop_duplicates('dt').sort_values('dt').reset_index(drop=True)
    return b

def rs(df,rule):
    return df.set_index('dt').resample(rule,label='left',closed='left').agg({'o':'first','h':'max','l':'min','c':'last','v':'sum'}).dropna().reset_index()

def wilder(vals,per=14):
    d=pd.Series(vals).diff(); up=d.clip(lower=0).to_numpy(); dn=(-d).clip(lower=0).to_numpy()
    a=np.full(len(vals),np.nan); b=np.full(len(vals),np.nan)
    if len(vals)<=per: return np.full(len(vals),np.nan)
    a[per]=np.nanmean(up[1:per+1]); b[per]=np.nanmean(dn[1:per+1])
    for i in range(per+1,len(vals)):
        a[i]=(a[i-1]*(per-1)+up[i])/per; b[i]=(b[i-1]*(per-1)+dn[i])/per
    return 100-100/(1+np.divide(a,b,out=np.full(len(vals),np.inf),where=b!=0))

def hayden(df):
    rsi=wilder(((df.o+df.h+df.l+df.c)/4).to_numpy())
    stt=np.zeros(len(df),np.int8)
    for i in range(1,len(df)):
        p=stt[i-1]; r0,r1=rsi[i-1],rsi[i]; s=p
        if np.isnan(r1) or np.isnan(r0): stt[i]=p; continue
        if r1>67 and r0<=67: s=1
        elif r1<33 and r0>=33: s=2
        elif p==1 and r1<39 and r0>=39: s=0
        elif p==2 and r1>61 and r0<=61: s=0
        stt[i]=s
    lab=np.array(['Chop','Bull','Bear'])[stt]
    bis=np.zeros(len(stt),int)
    for i in range(1,len(stt)): bis[i]=bis[i-1]+1 if stt[i]==stt[i-1] else 0
    return lab,rsi,bis

def divflags(close,r):
    n=len(close); c=close.to_numpy(); bull=np.zeros(n,bool); bear=np.zeros(n,bool)
    pl=np.zeros(n,bool); ph=np.zeros(n,bool)
    pl[1:-1]=(c[1:-1]<c[:-2])&(c[1:-1]<c[2:]); ph[1:-1]=(c[1:-1]>c[:-2])&(c[1:-1]>c[2:])
    lpl=lph=-1
    for i in range(n):
        if pl[i]:
            if lpl>=0 and c[i]<c[lpl] and r[i]>r[lpl]: bull[min(i+1,n-1)]=True
            lpl=i
        if ph[i]:
            if lph>=0 and c[i]>c[lph] and r[i]<r[lph]: bear[min(i+1,n-1)]=True
            lph=i
    return bull,bear

def dials(df):
    df=df.copy(); df['rsi']=wilder(df.c.to_numpy())
    bull,bear=divflags(df.c,df['rsi'].to_numpy()); df['div_bull']=bull; df['div_bear']=bear
    df['rng']=df.h-df.l; df['rng_med20']=df.rng.rolling(20).median().shift(1); df['rng_x']=df.rng/df.rng_med20
    r0=df.rng.replace(0,np.nan)
    df['body_frac']=(df.c-df.o).abs()/r0; df['uw_frac']=(df.h-df[['o','c']].max(axis=1))/r0
    df['lw_frac']=(df[['o','c']].min(axis=1)-df.l)/r0; df['close_pos']=(df.c-df.l)/r0
    hh=df.h>df.h.shift(1); ll=df.l<df.l.shift(1)
    df['hl_tok']=np.select([hh&~ll,~hh&ll,hh&ll],['up','down','outside'],default='inside')
    df['volr']=df.v.rolling(20).mean()/df.v.rolling(100).mean()
    df['atr14']=(pd.concat([df.h-df.l,(df.h-df.c.shift()).abs(),(df.l-df.c.shift()).abs()],axis=1).max(axis=1)).rolling(14).mean()
    return df

def poc_va(seg,frac=0.70):
    if seg.empty: return np.nan,np.nan,np.nan
    lo,hi=seg.l.min(),seg.h.max(); bw=(hi-lo)/100 or 1e-9
    mid=((seg.h+seg.l)/2); b=((mid-lo)/bw).clip(0,99).astype(int)
    vv=np.bincount(b,weights=seg.v,minlength=100); p=int(vv.argmax()); tot=vv.sum()
    L=R=p; acc=vv[p]
    while acc<frac*tot and (L>0 or R<99):
        le=vv[L-1] if L>0 else -1; re=vv[R+1] if R<99 else -1
        if re>=le and R<99: R+=1; acc+=vv[R]
        elif L>0: L-=1; acc+=vv[L]
        else: break
    return lo+(p+0.5)*bw, lo+L*bw, lo+(R+1)*bw  # POC, VAL, VAH

def pivots(df,k):
    h=df.h.to_numpy(); l=df.l.to_numpy(); n=len(df)
    ish=np.ones(n,bool); isl=np.ones(n,bool)
    for j in range(1,k+1):
        ish[:j]=False; ish[-j:]=False; isl[:j]=False; isl[-j:]=False
        ish[j:n-j]&=(h[j:n-j]>h[:n-2*j])&(h[j:n-j]>=h[2*j:]) if False else (h[j:n-j]>np.roll(h,j)[j:n-j])&(h[j:n-j]>np.roll(h,-j)[j:n-j])
        isl[j:n-j]&=(l[j:n-j]<np.roll(l,j)[j:n-j])&(l[j:n-j]<np.roll(l,-j)[j:n-j])
    out=[]
    for i in np.nonzero(ish)[0]: out.append(('H',k,float(h[i]),df.dt.iloc[i],df.dt.iloc[min(i+k,n-1)]))
    for i in np.nonzero(isl)[0]: out.append(('L',k,float(l[i]),df.dt.iloc[i],df.dt.iloc[min(i+k,n-1)]))
    return out

def build_coin(coin,b0,pi_tab,btc_h4):
    S=load5(coin); S['et']=S.dt.dt.tz_convert(ET); S['wdate']=(S.et-pd.Timedelta(hours=8)).dt.date
    frames={'5m':S[['dt','o','h','l','c','v']].copy(),'15m':rs(S,'15min'),'1h':rs(S,'1h'),'4h':rs(S,'4h')}
    # day frame (8-8 ET)
    G=S.groupby('wdate'); day=G.agg(o=('o','first'),h=('h','max'),l=('l','min'),c=('c','last'),v=('v','sum')).reset_index()
    full=G.size(); day=day[day.wdate.isin(full[full>=276].index)].reset_index(drop=True)  # complete windows only (DST 276-300)
    day['rng']=day.h-day.l; day['uabs']=day.rng.rolling(14).median().shift(1)
    # dials per TF
    for k in frames: frames[k]=dials(frames[k])
    # relvol on 5m (same-tod 20d median), vectorized
    f5=frames['5m']; f5['et']=f5.dt.dt.tz_convert(ET); f5['tod']=f5.et.dt.strftime('%H:%M'); f5['wdate']=(f5.et-pd.Timedelta(hours=8)).dt.date
    med=f5.groupby('tod')['v'].transform(lambda s: s.rolling(20,min_periods=10).median().shift(1))
    f5['relvol']=f5.v/med
    f5['wknd']=f5.et.dt.dayofweek>=5; f5['hrs_since_08']=((f5.et-pd.Timedelta(hours=8)).dt.hour+ (f5.et-pd.Timedelta(hours=8)).dt.minute/60)
    sb=pd.cut(f5.et.dt.hour,[-1,1,7,10,13,16,19,23],labels=['asia','eu','us_open','lunch','us_close','evening','asia2'])
    f5['session']=sb.astype(str).replace({'asia2':'asia'})
    frames['5m']=f5.drop(columns=['et','tod'])
    # hayden native TFs
    for k in ['15m','1h','4h']:
        lab,rsiH,bis=hayden(frames[k]); frames[k]['hy_state']=lab; frames[k]['hy_rsi']=rsiH; frames[k]['hy_bars_in']=bis
        frames[k]['hy_rsi_slope']=pd.Series(rsiH).diff()
    if coin!='BTC':
        frames['4h']=frames['4h'].merge(btc_h4.rename(columns={'hy_state':'btc_state','hy_rsi':'btc_rsi'})[['dt','btc_state','btc_rsi']],on='dt',how='left')
    frames['5m']['wdate']=f5['wdate']
    for k in ['15m','1h','4h']:
        frames[k]['wdate']=(frames[k].dt.dt.tz_convert(ET)-pd.Timedelta(hours=8)).dt.date
    # 1D rows
    d3=[];d4=[]
    c5=frames['5m'][['wdate','c']].copy(); 
    for w,g in c5.groupby('wdate'):
        if w not in set(day.wdate): d3.append((w,np.nan)); continue
        op=float(day.loc[day.wdate==w,'o'].iloc[0]); s=np.sign(g.c.to_numpy()-op); s=s[s!=0]
        d3.append((w,int((np.diff(s)!=0).sum())))
    d3=pd.DataFrame(d3,columns=['wdate','d3_opencross'])
    f15=frames['15m']
    for w,g in f15.groupby('wdate'):
        up=((g.h>g.h.shift())&(g.l>g.l.shift())).to_numpy(); dn=((g.h<g.h.shift())&(g.l<g.l.shift())).to_numpy()
        def run(a):
            m=cur=0
            for x in a:
                cur=cur+1 if x else 0; m=max(m,cur)
            return m
        d4.append((w,max(run(up),run(dn))))
    d4=pd.DataFrame(d4,columns=['wdate','d4_ladder'])
    h4=frames['4h'][['dt','hy_state']].copy()
    anch=[]
    for w in day.wdate:
        t=pd.Timestamp(str(w),tz='UTC')+pd.Timedelta(hours=4)
        row=h4[h4.dt==t]
        anch.append(row.hy_state.iloc[0] if len(row) else 'na')
    D=day.copy(); D['hayden_daily_anchor']=anch
    D['d1_eff']=(D.c-D.o).abs()/D.rng.replace(0,np.nan)
    D['atr14_1d']=(pd.concat([D.h-D.l,(D.h-D.c.shift()).abs(),(D.l-D.c.shift()).abs()],axis=1).max(axis=1)).rolling(14).mean()
    D['d2_rng_u']=D.rng/D.uabs; D['d2_rng_atr']=D.rng/D.atr14_1d.shift(0); D['d2_rng_pct']=D.rng/D.o
    D=D.merge(d3,on='wdate',how='left').merge(d4,on='wdate',how='left')
    D['d7_yd_arch_today']=np.select([ (D.c-D.o)/D.rng.replace(0,np.nan)>=0.5, (D.c-D.o)/D.rng.replace(0,np.nan)<=-0.5],['UP','DN'],default='CHOP')
    D['wd']=pd.to_datetime(D.wdate.astype(str))
    pi_tab2=pi_tab.copy(); pi_tab2['wd']=pd.to_datetime(pi_tab2.d.astype(str))+pd.Timedelta(days=1)
    D=D.merge(pi_tab2[['wd','pi_state','pi_gap']],on='wd',how='left').drop(columns=['wd'])
    bb=b0[b0.coin==coin].copy(); bb['wdate']=pd.to_datetime(bb.date).dt.date
    D=D.merge(bb[['wdate','dtype','lean_dir','lean_strength','yd_arch','yd_eff','ob55_open','ob55_fired']],on='wdate',how='left')
    D=D.rename(columns={'dtype':'d5_dtype','ob55_fired':'d6_ob55_fired'})
    # marks: periods (ET + UTC conventions), pivots, VA, scen
    def periods(conv):
        u=S.set_index('et' if conv=='ET' else 'dt'); out=[]
        days=sorted(set(D.wdate))
        for w in days:
            if conv=='ET':
                a=pd.Timestamp(str(w),tz=ET); m5=pd.Timedelta(minutes=5)
                segs={'PD':u.loc[a-pd.Timedelta(days=1)+pd.Timedelta(hours=8):a+pd.Timedelta(hours=8)-m5],
                      'ON':u.loc[a-pd.Timedelta(days=1)+pd.Timedelta(hours=17):a+pd.Timedelta(hours=8)-m5],
                      'PS':u.loc[a-pd.Timedelta(days=1)+pd.Timedelta(hours=8):a-pd.Timedelta(days=1)+pd.Timedelta(hours=17)-m5]}
                wk=pd.Timestamp(str(w),tz=ET); mon=(wk-pd.Timedelta(days=wk.weekday())).normalize()
                segs['PW']=u.loc[mon-pd.Timedelta(days=7):mon-m5]
                m0=wk.normalize().replace(day=1); segs['PM']=u.loc[m0-pd.DateOffset(months=1):m0-m5]
            else:
                a=pd.Timestamp(str(w),tz='UTC'); m5=pd.Timedelta(minutes=5)
                segs={'PD':u.loc[a-pd.Timedelta(days=1):a-m5]}
                mon=(a-pd.Timedelta(days=a.weekday())).normalize(); segs['PW']=u.loc[mon-pd.Timedelta(days=7):mon-m5]
                m0=a.normalize().replace(day=1); segs['PM']=u.loc[m0-pd.DateOffset(months=1):m0-m5]
            for nm,seg in segs.items():
                if seg.empty: continue
                p,val,vah=poc_va(seg)
                out+= [(str(w),conv,nm+'H',float(seg.h.max())),(str(w),conv,nm+'L',float(seg.l.min())),
                       (str(w),conv,nm+'C',float(seg.c.iloc[-1])),(str(w),conv,nm+'POC',float(p))]
        return out
    MP=pd.DataFrame(periods('ET')+periods('UTC'),columns=['wdate','conv','name','price'])
    PV=[]
    for k in [2,3,5]:
        for tfk in ['15m','1h','4h']:
            for kind,kk,px,t,tc in pivots(frames[tfk],k): PV.append((tfk,kind,kk,px,t,tc))
    PV=pd.DataFrame(PV,columns=['tf','kind','k','price','pivot_dt','confirm_dt'])
    VA=[]
    et2=S.set_index('et')
    wks=pd.period_range(S.et.min().normalize(),S.et.max(),freq='W-MON')
    for per,lab_ in [(pd.period_range(S.et.min(),S.et.max(),freq='W'),'week'),(pd.period_range(S.et.min(),S.et.max(),freq='M'),'month')]:
        for p in per:
            a=p.start_time.tz_localize(ET); b_=p.end_time.tz_localize(ET)
            seg=et2.loc[a:b_]
            if len(seg)<50: continue
            pc,val,vah=poc_va(seg); VA.append((lab_,str(p),float(pc),float(val),float(vah)))
    VA=pd.DataFrame(VA,columns=['period','tag','poc','val','vah'])
    scen=pd.read_parquet('data/state/b0_scen_defs.parquet'); sc=scen[scen.coin==coin].copy()
    for k,df in frames.items():
        df.drop(columns=[c for c in ['rng_med20'] if c in df],errors='ignore').to_parquet(f'{OUT}/bars_{coin}_{k}.parquet',compression='zstd',index=False)
    D.to_parquet(f'{OUT}/bars_{coin}_1D.parquet',compression='zstd',index=False)
    MP.to_parquet(f'{OUT}/marks_periods_{coin}.parquet',compression='zstd',index=False)
    PV.to_parquet(f'{OUT}/marks_pivots_{coin}.parquet',compression='zstd',index=False)
    VA.to_parquet(f'{OUT}/marks_va_{coin}.parquet',compression='zstd',index=False)
    sc.to_parquet(f'{OUT}/marks_scen_{coin}.parquet',compression='zstd',index=False)
    return {'coin':coin,'5m':len(frames['5m']),'15m':len(frames['15m']),'1h':len(frames['1h']),'4h':len(frames['4h']),'1D':len(D),
            'marks_periods':len(MP),'pivots':len(PV),'va':len(VA),'span':f"{S.dt.min()} -> {S.dt.max()}"}

# shared inputs
b0=pd.read_parquet('data/state/b0_states.parquet')
# BTC first (pi + btc_h4 shared)
res=[]
Bf=load5('BTC'); B4=dials(rs(Bf,'4h')); lab,rsiH,bis=hayden(B4); B4['hy_state']=lab; B4['hy_rsi']=rsiH
B1=rs(Bf,'1D'); B1['ma111']=B1.c.rolling(111).mean(); B1['ma350x2']=2*B1.c.rolling(350).mean()
pi_tab=pd.DataFrame({'d':B1.dt.dt.date,'pi_state':np.where(B1.ma111>B1.ma350x2,'up','down'),'pi_gap':B1.ma111/B1.ma350x2-1})
for coin in COINS:
    if coin in st['done']: print(coin,'already done; skip'); continue
    if (time.time()-T0)/60 > A.budget_min-8: print('budget reached; resume next run'); break
    r=build_coin(coin,b0,pi_tab,B4); res.append(r); st['done'].append(coin); json.dump(st,open(SF,'w'))
    print('DONE',r,flush=True)
# sealed probes on SOL (run when SOL present)
if os.path.exists(f'{OUT}/bars_SOL_1D.parquet'):
    D=pd.read_parquet(f'{OUT}/bars_SOL_1D.parquet'); u=D.loc[D.wdate.astype(str)=='2026-07-22','uabs']
    MP=pd.read_parquet(f'{OUT}/marks_periods_SOL.parquet')
    pwl=MP[(MP.wdate=='2026-07-22')&(MP.conv=='ET')&(MP.name=='PWL')].price
    pdh=MP[(MP.wdate=='2026-07-22')&(MP.conv=='UTC')&(MP.name=='PDH')].price
    H=pd.read_parquet(f'{OUT}/bars_SOL_4h.parquet'); H['dt']=pd.to_datetime(H.dt,utc=True)
    hy=H.loc[H.dt==pd.Timestamp('2026-07-22 04:00',tz='UTC'),'hy_state']
    probes=[('uabs SOL 07-22',float(u.iloc[0]) if len(u) else np.nan,2.515,0.003),
            ('PWL_ET',float(pwl.iloc[0]) if len(pwl) else np.nan,73.39,0.02),
            ('PDH_UTC',float(pdh.iloc[0]) if len(pdh) else np.nan,78.88,0.02)]
    ok=all(abs(v-t)<=tol for _,v,t,tol in probes) and len(hy) and hy.iloc[0]=='Bull'
    for n,v,t,tol in probes: print(('PASS' if abs(v-t)<=tol else 'FAIL'),n,v,'target',t)
    print(('PASS' if len(hy) and hy.iloc[0]=='Bull' else 'FAIL'),'SOL 4h Hayden @07-22 04Z =',hy.iloc[0] if len(hy) else 'missing')
    lines=[f"# RECORD_COUNTS — built {pd.Timestamp.now(tz='UTC')}",""]+[str(r) for r in res]+[
    "","SEALED PROBES: "+("ALL PASS" if ok else "FAIL — record NOT trusted, report in chat"),
    "NAMED GAPS: relvol first ~20d na · divergence port uncertified (H-Div source unread) · fast-Hayden 15m/1h carry historical uncertified label · b0 joins (d5_dtype/lean/ob55/yd) end at their build date, na beyond · uhist-U absent (vintage) · non-crypto DON-20/FADE-K5 absent · session blocks + VA-70% + pivot-k∈{2,3,5} are declared (b)-lines.",
    "CONVENTIONS: marks_periods carries BOTH ET-8-8 and UTC windows, conv-tagged. Distances derived by join, never stored. No thresholds stored anywhere."]
    open(f'{OUT}/RECORD_COUNTS.md','w').write('\n'.join(lines))
    if not ok: sys.exit(1)
print('RECORD BUILD',' COMPLETE' if len(st['done'])==4 else f" partial ({st['done']}) — run again to resume")
