#!/usr/bin/env python3
"""m9_emit.py — CB9 payload emitter (M9 bridge, 2026-07-09).
Usage: python3 m9_emit.py [YYYY-MM-DD]   (default: latest date in board)
Emits one CB9 line per asset. Day-specific data only; era-proof constants are baked in the CB9 Pine.
Fields: CB9|{asset}|{date}|U:{U%}|CTX:{reg},{yday},{wk}|SCN:{active scenario codes}|Wn:{lo},{hi},{D|WM},{contact%},{tags}
Contact% = banked C1 gravity-curve lookup on yesterday's closest gap; ★=stepping POC (run>=3); V=virgin member (dst>20); WW=worn wall (PW/PM member ptd-proxy dst<=5 with 3+ area visits)."""
import sys, numpy as np, pandas as pd

BASE='/home/claude/p2b'
LV=['PDH','PDL','PDC','PDPOC','ONH','ONL','ONC','ONPOC','PSH','PSL','PSC','PSPOC','PWH','PWL','PWC','PWPOC','PMH','PML','PMC','PMPOC']
GRAV=[(0.0,56.4),(0.03,42.8),(0.26,32.2),(0.46,22.2),(1.1,9.8),(3.0,0.5)]  # banked C1

def grav_pct(gap):
    if gap<=0: return 56.4
    xs=[g for g,_ in GRAV]; ys=[p for _,p in GRAV]
    return float(np.interp(min(gap,3.0),xs,ys))

def main(date=None):
    mig=pd.read_csv(f'{BASE}/migration_v2.csv')
    LD=pd.read_csv(f'{BASE}/levels_daily_v2.csv')
    SU=pd.concat([pd.read_csv(f'{BASE}/day_level_summary_v2_{a}.csv') for a in ['BTC','ETH','SOL','XRP']]).rename(columns={'window_d':'d'})
    C4=pd.read_csv(f'{BASE}/m4_columns.csv')  # st4h at last touch per level-day (regime source: latest available)
    DP=pd.read_csv(f'{BASE}/daypath_meta.csv')[['a','d','FA_U_k10']]
    dates=sorted(LD.d.unique()); d=date or dates[-1]
    di=dates.index(d); dprev=dates[di-1]
    YD={0:'lean',1:'churn',2:'churn',3:'trend',4:'parked'}
    for a in ['BTC','ETH','SOL','XRP']:
        Ld=LD[(LD.a==a)&(LD.d==d)].set_index('level').reindex(LV)
        vals=Ld.uU.iloc[0]
        V=mig[(mig.a==a)&(mig.d==d)].set_index('level').value.reindex(LV)
        u=Ld.uU.iloc[0]
        # yesterday context
        Sp=SU[(SU.a==a)&(SU.d==dprev)].set_index('level').reindex(LV)
        gap_y=Sp.min_dist_U.fillna(9.9)
        # regime: last known st4h (from most recent touch row), yday archetype, weekend
        st=C4[(C4.a==a)&(C4.d<=dprev)].sort_values('d').st4h_lab.dropna()
        reg=st.iloc[-1] if len(st) else 'NA'
        ydrow=DP[(DP.a==a)&(DP.d==dprev)]
        yd=YD.get(int(ydrow.FA_U_k10.iloc[0]),'na') if len(ydrow) else 'na'
        wk='wkend' if pd.Timestamp(d).weekday()>4 else 'wkday'
        # POC stepping runs (3-day same-direction)
        runs={}
        for poc in ('PDPOC','ONPOC','PSPOC'):
            vv=mig[(mig.a==a)&(mig.level==poc)&(mig.d<=d)].sort_values('d').value.tail(4).values
            runs[poc]=len(vv)>=4 and (all(np.diff(vv)>0) or all(np.diff(vv)<0))
        # cascade scenario states (M2 grammar, at-open)
        pcs=mig[(mig.a==a)&(mig.level=='PDC')&(mig.d<=d)].sort_values('d').value.tail(5).values
        def state(lvl):
            av=V[lvl]
            if not np.isfinite(av) or len(pcs)<5: return 'na'
            above=pcs>av; side='ab' if above[-1] else 'bl'
            cross='no' if all(above==above[-1]) else ('xup' if above[-1] else 'xdn')
            return side+'|'+cross
        scn=[]
        if state('PSPOC')=='bl|xdn': scn.append('POC-CASC-DN')
        if state('PSPOC')=='ab|xup': scn.append('POC-CASC-UP')
        if state('PML')=='bl|xdn': scn.append('ML-CASC')
        if state('PWC')=='ab|no': scn.append('WC-SUPP')
        # walls at r=0.25
        order=np.argsort(V.values); sv=V.values[order]
        wid=np.zeros(20,int); w=0
        for j in range(1,20):
            if sv[j]-sv[j-1]>0.25*u: w+=1
            wid[j]=w
        dtl='na'
        try:
            DT=pd.read_csv(f'{BASE}/mint2_states.csv'); r=DT[(DT.a==a)&(DT.d==d)]
            if len(r): dtl=f'{r.dtype.iloc[0]}'
        except Exception: pass
        parts=[f'CB9|{a}|{d}',f'U:{Ld.uU.iloc[0]/V["PDC"]*100:.2f}' if np.isfinite(V['PDC']) else 'U:na', f'UA:{Ld.uU.iloc[0]:.6g}',
               f'CTX:{reg},{yd},{wk},{dtl}', 'SCN:'+('/'.join(scn) if scn else 'none')]
        for wl in range(w+1):
            m=wid==wl; mem=[LV[order[j]] for j in range(20) if m[j]]
            lo,hi=sv[m].min(),sv[m].max()
            wm='WM' if any(x[:2] in ('PW','PM') for x in mem) else 'D'
            g=min(gap_y[x] for x in mem)
            c=grav_pct(g)
            tags=[]
            if any(runs.get(x,False) for x in mem): tags.append('★')
            if all(Ld.days_since_touch[x]>20 for x in mem if np.isfinite(Ld.days_since_touch[x])): tags.append('V')
            parts.append(f'W{wl+1}:{lo:.6g},{hi:.6g},{wm},{c:.0f},{"".join(tags) or "-"}')
        print('|'.join(parts))

if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else None)
