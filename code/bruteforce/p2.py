import numpy as np, pandas as pd, json, hashlib
np.random.seed(20260723)
import sys
SYM=sys.argv[1]; NM=sys.argv[2]
src=open('mm1.py').read()
head=src[:src.index('def run_coin')]
# extend wall builder: keep member names + stepping-POC flag
head=head.replace("walls.append((float(lo),float(hi),float(cc),bool(vg)))",
"""walls.append((float(lo),float(hi),float(cc),bool(vg),[str(x) for x in mem],bool(set(mem)&runs)))""")
head=head.replace("        walls=[]\n","""        runs=set()
        for pre,key in (('PD','POC'),('PS','PSPOC')):
            vv=[dayagg[days[j]][key] for j in range(di-4,di)]
            vv=[x for x in vv if np.isfinite(x)]
            if len(vv)>=4 and (all(np.diff(vv)>0) or all(np.diff(vv)<0)): runs.add(pre+'POC')
        walls=[]
""")
exec(head)

import os
BCTX={}
if os.path.exists('btc_ctx.csv') and NM!='BTC':
    for ln in open('btc_ctx.csv'):
        a=ln.strip().split(',')
        if len(a)==3: BCTX[a[0]]=(a[1],a[2])
fomc=set(json.load(open('/mnt/project/fomc_dates.json')) if __import__('os').path.exists('/mnt/project/fomc_dates.json') else [])
df,days,W=(lambda r:(r[0],r[1],r[2]))(build_walls_series(SYM))
G={d:g.reset_index(drop=True) for d,g in df.groupby('wd')}
# per-day per-hour mean bar volume -> rolling 20d median per hour
vh=df.groupby(['wd','hr']).v.mean().unstack()
vh20=vh.rolling(20,min_periods=5).median().shift(1)
# day ranges + U series for trends/budgets
dayH=df.groupby('wd').h.max(); dayL=df.groupby('wd').l.min()
dayrng=dayH-dayL
_wtd={}
for iso_,gg in df.groupby('iso'):
    cmx=gg.groupby('wd').h.max().cummax(); cmn=gg.groupby('wd').l.min().cummin()
    for d_ in cmx.index: _wtd[d_]=float(cmx[d_]-cmn[d_])
Ur=dayrng.rolling(14).median().shift(1)
df['iso']=[pd.Timestamp(x).isocalendar()[:2] for x in df.wd]
wkrng=df.groupby('iso').apply(lambda g:g.h.max()-g.l.min())
wk26=wkrng.rolling(26,min_periods=8).median().shift(1)

allw=sorted(W)
samp=allw
PI={}
if NM=='BTC':
    dc=df.groupby('wd').c.last()
    ma1=dc.rolling(111).mean(); ma2=dc.rolling(350).mean()*2
    for d_ in dc.index:
        if np.isfinite(ma1.get(d_,np.nan)) and np.isfinite(ma2.get(d_,np.nan)):
            PI[str(d_)]='down' if ma1[d_]<ma2[d_] else 'up'
    tv=PI.get(sorted(PI)[-1],'na')
    print('PI validation: engine says down | formula says',tv, '->', 'ADOPTED' if tv=='down' else 'REJECTED->na')
    if tv!='down': PI={}
S=0.25; PROX=0.25; STALLR=0.25; FB=6; BW=24

rows=[]; rid=0
for d in samp:
    wd=W[d]; walls=wd['walls']; U=wd['uAbs']
    if not np.isfinite(U) or U<=0 or d not in G: continue
    g=G[d]; o=g.o.values; h=g.h.values; l=g.l.values; c=g.c.values; v=g.v.values; ts=g.t.values; hrs=g.hr.values
    n=len(g); et0=pd.to_datetime(ts[0],unit='ms',utc=True).tz_convert('America/New_York')
    prevd=allw[allw.index(d)-1] if allw.index(d)>0 else None
    pclose=G[prevd].c.iloc[-1] if prevd in G else o[0]
    gapfl=abs(o[0]-pclose)>0.25*U
    iso=pd.Timestamp(d).isocalendar()[:2]
    wku=wkrng.get(iso,np.nan); wk_used=float(_wtd.get(d,np.nan)/wk26.get(iso,np.nan)) if np.isfinite(wk26.get(iso,np.nan)) else np.nan
    utr=float((Ur.get(d,np.nan)-Ur.get(allw[max(0,allw.index(d)-14)],np.nan))/Ur.get(d,np.nan)) if np.isfinite(Ur.get(d,np.nan)) else np.nan
    hay=wd['hayden']; fomcf=str(d) in fomc
    ladder={}; testno={}
    def zone_of(px):
        for k,(lo,hi,*_) in enumerate(walls):
            if lo-0.1*U<=px<=hi+0.1*U: return k
        return -1
    def sess(hr):
        return 'asia' if hr<3 else 'eu' if hr<8 else 'us_open' if hr<11 else 'lunch' if hr<13 else 'us_close' if hr<17 else 'evening'
    # EXIT: day-open-inside episodes (P2 amendment)
    for k,(lo,hi,cc,vg,mem,step) in enumerate(walls):
        if not (lo<=o[0]<=hi): continue
        for xdir in (-1,1):  # -1 exit down through lo, +1 exit up through hi
            edge=lo if xdir==-1 else hi
            jb=None
            for i2 in range(n):
                if (c[i2]<edge if xdir==-1 else c[i2]>edge): jb=i2; break
            if jb is None: continue
            nb2=[w2[1] for w2 in walls if w2[1]<lo] if xdir==-1 else [w2[0] for w2 in walls if w2[0]>hi]
            nxt=(max(nb2) if xdir==-1 and nb2 else (min(nb2) if nb2 else np.nan))
            trav=0.0; reach=False; bn=np.nan; jj=jb; fb=False; beyond=0
            while jj<n:
                trav=max(trav,(edge-l[jj]) if xdir==-1 else (h[jj]-edge))
                inside=(c[jj]>edge) if xdir==-1 else (c[jj]<edge)
                if not inside: beyond+=1
                if np.isfinite(nxt) and not reach and ((l[jj]<=nxt) if xdir==-1 else (h[jj]>=nxt)): reach=True; bn=jj-jb
                if inside and jj<=jb+FB: fb=True; break
                if inside: break
                jj+=1
            mid=(lo+hi)/2
            rows.append(dict(id=rid,coin=NM,day=str(d),t_event=int(ts[jb]),zone=k+1,z_lo=lo,z_hi=hi,
                contact=cc,virgin=vg,stepPOC=step,members="/".join(mem),confl=len(mem),widthU=(hi-lo)/U,
                ladder_ix=k+1,above_open=mid>o[0],dnextU=np.nan,dbehindU=np.nan,last_tradedd=np.nan,
                origin='inside_open',distU=np.nan,speedUh=np.nan,bars_route=np.nan,pullbacks=np.nan,bodyU=np.nan,relvol=np.nan,
                side='inside',exit_dir=('dn' if xdir==-1 else 'up'),test_no=1,ladder_state='-',
                session=sess(hrs[jb]),hrs_since8=round((jb*5)/60,2),wknd=pd.Timestamp(d).weekday()>=5,gap=gapfl,
                hayden=hay,hayden_btc=(hay if NM=='BTC' else BCTX.get(str(d),('na','na'))[0]),
                btc_pi=(PI.get(str(d),'na') if NM=='BTC' else BCTX.get(str(d),('na','na'))[1]),
                daytype='na',yd_arch='na',lean='na',
                wk_used=round(wk_used,3) if np.isfinite(wk_used) else np.nan,mo_day=int(str(d)[8:10]),
                rng_used=round((h[:jb+1].max()-l[:jb+1].min())/U,3),u_trend=round(utr,3) if np.isfinite(utr) else np.nan,fomc=fomcf,U=U,
                etype='EXIT',depthU=np.nan,bounceU=np.nan,bars_bounce=np.nan,bars_beyond=beyond,
                travelU=round(trav/U,3),reached_next=reach,bars_next=bn,false_break=fb,
                eod_locU=round((c[-1]-mid)/U,3),truncated=jj>=n-1))
            pid=rid; rid+=1
            jr=jj; rcount=0
            while jr<n and rcount<3:
                hitc=(h[jr]>=edge) if xdir==-1 else (l[jr]<=edge)
                if hitc:
                    rcount+=1
                    rep=0.0; flip='na'; kk=jr
                    for kk in range(jr,min(jr+12,n)):
                        rep=max(rep,(h[kk]-edge) if xdir==-1 else (edge-l[kk]))
                        if (c[kk]<=edge-0.25*U if xdir==-1 else c[kk]>=edge+0.25*U): flip='held'; break
                        if (c[kk]>edge+0.1*U if xdir==-1 else c[kk]<edge-0.1*U): flip='failed'; break
                    e2=min(kk+BW,n-1)
                    leg=((edge-l[kk:e2+1].min()) if xdir==-1 else (h[kk:e2+1].max()-edge))/U
                    rows.append(dict(id=rid,coin=NM,day=str(d),t_event=int(ts[jr]),etype='RETEST',parent=pid,
                        zone=k+1,side='inside',retest_no=rcount,bars_until=jr-jb,
                        repenU=round(rep/U,3),flip=flip,leg2U=round(leg,3),U=U))
                    rid+=1; jr=kk+1
                else: jr+=1
    for k,(lo,hi,cc,vg,mem,step) in enumerate(walls):
        nb=[w2[0] for w2 in walls if w2[0]>hi]; na_=[w2[1] for w2 in walls if w2[1]<lo]
        dnext_up=(min(nb)-hi)/U if nb else np.nan; dnext_dn=(lo-max(na_))/U if na_ else np.nan
        # last day the zone mid traded
        mid=(lo+hi)/2; lastt=np.nan
        for back in range(1,61):
            j=allw.index(d)-back
            if j<0: break
            dd=allw[j]
            if dd in dayH.index and dayL[dd]<=mid<=dayH[dd]: lastt=back; break
        for side in (-1,1):  # -1 approach from below, 1 from above
            edge=lo if side==-1 else hi; far=hi if side==-1 else lo
            i=0
            while i<n:
                # find start: price outside on this side
                if (c[i]<edge if side==-1 else c[i]>edge):
                    anc=i; ext=l[i] if side==-1 else h[i]
                    j=i+1; prox=False; best=1e18; besti=i; ev=None
                    while j<n:
                        ext=min(ext,l[j]) if side==-1 else max(ext,h[j])
                        dedge=(edge-h[j]) if side==-1 else (l[j]-edge)
                        if dedge<best: best=dedge; besti=j
                        if dedge<=PROX*U: prox=True
                        touched=(h[j]>=edge) if side==-1 else (l[j]<=edge)
                        if touched: ev=('T',j); break
                        if prox and dedge>=best+STALLR*U: ev=('S',besti); break
                        j+=1
                    if ev is None: break
                    typ,je=ev
                    tno=testno.get((k,side),0)+1; testno[(k,side)]=tno
                    pass
                    dist=abs(edge-ext)/U; bars=je-anc; spd=dist/max(bars*5/60,1e-9)
                    seg=slice(anc,je+1)
                    pull=int((np.abs(np.diff(c[seg]))>0.15*U).sum())
                    body=float(np.abs(c[seg]-o[seg]).mean()/U)
                    vmed=vh20.loc[d].get(hrs[je],np.nan) if d in vh20.index else np.nan
                    rvol=float(v[seg].mean()/vmed) if np.isfinite(vmed) and vmed>0 else np.nan
                    oz=zone_of(ext) if anc>0 else -9
                    base=dict(id=rid,coin=NM,day=str(d),t_event=int(ts[je]),
                        zone=k+1,z_lo=lo,z_hi=hi,contact=cc,virgin=vg,stepPOC=step,members="/".join(mem),confl=len(mem),
                        widthU=(hi-lo)/U,ladder_ix=k+1,above_open=mid>o[0],dnextU=dnext_up if side==-1 else dnext_dn,
                        dbehindU=dnext_dn if side==-1 else dnext_up,last_tradedd=lastt,
                        origin=('open' if anc==0 else (f"Z{oz+1}" if oz>=0 else 'air')),distU=round(dist,3),
                        speedUh=round(spd,3),bars_route=bars,pullbacks=pull,bodyU=round(body,4),relvol=round(rvol,3) if np.isfinite(rvol) else np.nan,
                        side=('below' if side==-1 else 'above'),test_no=tno,
                        ladder_state=",".join(f"Z{z+1}:{s_}" for (z,s2),s_ in ladder.items() if s2==side) or "-",
                        session=sess(hrs[je]),hrs_since8=round((je*5)/60,2),wknd=pd.Timestamp(d).weekday()>=5,gap=gapfl,
                        hayden=hay,hayden_btc=(hay if NM=='BTC' else BCTX.get(str(d),('na','na'))[0]),btc_pi=(PI.get(str(d),'na') if NM=='BTC' else BCTX.get(str(d),('na','na'))[1]),daytype='na',yd_arch='na',lean='na',
                        wk_used=round(wk_used,3) if np.isfinite(wk_used) else np.nan,mo_day=int(str(d)[8:10]),
                        rng_used=round((h[:je+1].max()-l[:je+1].min())/U,3),u_trend=round(utr,3) if np.isfinite(utr) else np.nan,fomc=fomcf,U=U)
                    if typ=='S':
                        base.update(etype='STALL',depthU=0.0,bounceU=np.nan,bars_bounce=np.nan,bars_beyond=np.nan,
                                    travelU=np.nan,reached_next=False,bars_next=np.nan,false_break=False,eod_locU=round((c[-1]-mid)/U,3),truncated=False)
                        rows.append(base); rid+=1
                        i=je+1
                        while i<n and (((edge-l[i]) if side==-1 else (h[i]-edge))<0.5*U): i+=1
                        continue
                    # touched: escalate
                    depth=0.0; broke=False; jb=je; jj=je
                    while jj<n:
                        depth=max(depth,(h[jj]-edge) if side==-1 else (edge-l[jj]))
                        if (c[jj]>far if side==-1 else c[jj]<far): broke=True; jb=jj; break
                        back=(c[jj]<edge-0.1*U) if side==-1 else (c[jj]>edge+0.1*U)
                        if back: break
                        jj+=1
                    if not broke:
                        rt='TOUCH' if depth<0.1*U else 'PEN'
                        je2=min(jj,n-1); b_end=min(je2+BW,n-1)
                        bounce=((edge-l[je2:b_end+1].min()) if side==-1 else (h[je2:b_end+1].max()-edge))/U
                        base.update(etype=rt,depthU=round(depth/U,3),bounceU=round(bounce,3),bars_bounce=b_end-je2,
                                    bars_beyond=np.nan,travelU=np.nan,reached_next=False,bars_next=np.nan,false_break=False,
                                    eod_locU=round((c[-1]-mid)/U,3),truncated=jj>=n-1)
                        rows.append(base); rid+=1; ladder[(k,side)]='H'
                        i=max(jj,je)+1
                        while i<n and (((edge-l[i]) if side==-1 else (h[i]-edge))<0.25*U): i+=1
                        continue
                    # broke
                    trav=0.0; reach=False; bn=np.nan; jj=jb; fb=False; beyond=0
                    nxt=(min(nb) if side==-1 and nb else (max(na_) if side==1 and na_ else np.nan))
                    while jj<n:
                        trav=max(trav,(h[jj]-far) if side==-1 else (far-l[jj]))
                        inside=(c[jj]<far) if side==-1 else (c[jj]>far)
                        if not inside: beyond+=1
                        if np.isfinite(nxt) and not reach and ((h[jj]>=nxt) if side==-1 else (l[jj]<=nxt)): reach=True; bn=jj-jb
                        if inside and jj<=jb+FB: fb=True; break
                        if inside: break
                        jj+=1
                    etyp='TRAV' if trav>=0.5*U else 'BREAK'
                    base.update(etype=etyp,depthU=round(depth/U,3),bounceU=np.nan,bars_bounce=np.nan,
                                bars_beyond=beyond,travelU=round(trav/U,3),reached_next=reach,bars_next=bn,
                                false_break=fb,eod_locU=round((c[-1]-mid)/U,3),truncated=jj>=n-1)
                    rows.append(base); pid=rid; rid+=1; ladder[(k,side)]='B'
                    # retest sub-events
                    jr=jj; rcount=0
                    while jr<n and rcount<3:
                        hitc=(l[jr]<=far) if side==-1 else (h[jr]>=far)
                        if hitc:
                            rcount+=1
                            rep=0.0; flip='na'; kk=jr; leg=0.0
                            for kk in range(jr,min(jr+12,n)):
                                rep=max(rep,(far-l[kk]) if side==-1 else (h[kk]-far))
                                if (c[kk]>=far+0.25*U if side==-1 else c[kk]<=far-0.25*U): flip='held'; break
                                if (c[kk]<far-0.1*U if side==-1 else c[kk]>far+0.1*U): flip='failed'; break
                            e2=min(kk+BW,n-1)
                            leg=((h[kk:e2+1].max()-far) if side==-1 else (far-l[kk:e2+1].min()))/U
                            rows.append(dict(id=rid,coin=NM,day=str(d),t_event=int(ts[jr]),etype='RETEST',parent=pid,
                                zone=k+1,side=('below' if side==-1 else 'above'),retest_no=rcount,bars_until=jr-jb,
                                repenU=round(rep/U,3),flip=flip,leg2U=round(leg,3),U=U))
                            rid+=1; jr=kk+1
                        else: jr+=1
                    i=jj+1; continue
                i+=1
T=pd.DataFrame(rows)
T.to_csv(f"p2_events_{NM}.csv",index=False)
print("days",len(samp),"events",len(T),"| types:",T.etype.value_counts().to_dict())
print("sha",hashlib.sha256(open(f'p2_events_{NM}.csv','rb').read()).hexdigest()[:16])
if NM=='BTC':
    with open('btc_ctx.csv','w') as f:
        for d_ in samp: f.write(f"{d_},{W[d_]['hayden']},{PI.get(str(d_),'na')}\n")
print(T[T.day=='2026-07-22'][['zone','side','etype','t_event','depthU','travelU','reached_next','flip' if 'flip' in T else 'etype']].head(20).to_string() if len(T[T.day=='2026-07-22']) else "no 07-22 rows")
