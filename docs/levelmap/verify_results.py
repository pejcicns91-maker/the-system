#!/usr/bin/env python3
"""verify_results.py — the pass/fail harness for the Level Map reproduction pack.
Run from the pack root (expects ./data and ./derived). Asserts the headline numbers
from the shipped derived layers. A reimplementation should first diff its own
S1/S2 output against derived/level_events_v4.csv, then pass this."""
import numpy as np, pandas as pd, sys, os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'derived')
ok=[]; 
def chk(name,val,target,tol):
    p=abs(val-target)<=tol
    ok.append(p); print(('PASS' if p else 'FAIL')+f'  {name}: {val:.2f} (target {target}±{tol})')
M1=pd.read_parquet(f'{D}/M1_state.parquet')
chk('coverage level-days',len(M1),135360,0)
E=M1[M1.side.notna()]
chk('sided events w/ history',E.i23h.notna().sum(),45481,0)
chk('all-sided brk base %',E.brk.mean()*100,42.4,0.3)
for x,t in ((0.3,65.7),(0.5,75.6),(0.6,79.2),(1.0,88.6)):
    g=E[E.pen_U>=x]; chk(f'ladder pen>={x}',(g.cont.mean()*100),t,0.4)
# travel (needs signed eow — from M1? not stored; use docs targets via events file fields if present)
st=E.s*E.thr30_U
thr=np.where(st<=0.0999,'rev',np.where(st<=0.2303,'slow','fast'))
am=pd.cut(E.am20_n,[-1,2,7,25],labels=['few','mid','many']).astype(str)
# contest frame for calibrated cells
C=E[(E.pen_U>0.30)&(E.pen_U<=0.60)]  # approximation of band frame at event grain
# calibrated cells verified on the canonical frame stored numbers instead:
V=pd.read_csv(f'{D}/m7_vote.csv').merge(E[['a','d','level','brk']],on=['a','d','level'])
qlo,qhi=V.V.quantile(.15),V.V.quantile(.85)
chk('vote top15-bottom15 spread',(V.brk[V.V>=qhi].mean()-V.brk[V.V<=qlo].mean())*100,16.5,0.8)
G=pd.read_csv(f'{D}/m2_grid.csv')
cell=G[(G.A=='PSPOC')&(G.state=='bl|xdn|f2')&(G.B=='PDPOC')&(G.out=='brk_dn')]
chk('POC-cascade-dn dev pp',cell.dev.iloc[0],19.4,0.5); chk('cascade n',cell.n.iloc[0],85,0)
wk=E[(~E.wk)&(E.days_since_touch.between(2,5))]
chk('WEEKEND-WORKED-CAP brk %',wk.brk.mean()*100,33.6,0.4)
chk('weekend suppressor brk %',E[~E.wk].brk.mean()*100,35.6,0.4)
A=M1[M1.touched==True]
chk('gravity touched→tomorrow %',M1[M1.touched==True].next_day_touch.mean()*100,56.4,0.6)
print('\n%d/%d PASS'%(sum(ok),len(ok)))
sys.exit(0 if all(ok) else 1)
