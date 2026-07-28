#!/usr/bin/env python3
"""score_zones.py — CB12.6 morning forecast step.
Usage: python3 score_zones.py m9b_out.txt ctx.json
ctx.json (AI fills from the brief): {"spot":{"BTC":65555,...},"wk_used":{"BTC":0.62,...},
 "hayden_btc":"Bull","btc_pi":"down","fomc":false}
Reads each CB12| line, scores every wall with hold_morning.pkl (skill 0.329, AUC 0.823,
calibration ±4pp — printed as cal), emits the line with appended per-wall ,CLASS,PHOLD
fields (v6 grammar; 12.5 ignores extras, 12.6 renders them).
CLASS: V virgin (9% historical hold) · W wide-calm family · S stepping-POC · '-'.
"""
import sys, json, pickle, re, datetime
import numpy as np
mdl=pickle.load(open(__file__.rsplit('/',1)[0]+"/hold_morning.pkl","rb"))
clf,enc,CATS,NUMS,BOOLS=mdl['clf'],mdl['enc'],mdl['CATS'],mdl['NUMS'],mdl['BOOLS']
ctx=json.load(open(sys.argv[2]))
out=[]
for ln in open(sys.argv[1]):
    ln=ln.strip()
    if not ln.startswith('CB12|'): continue
    parts=ln.split('|'); nm=parts[1]
    ua=float([p for p in parts if p.startswith('UA:')][0][3:])
    hay=[p for p in parts if p.startswith('CTX:')][0][4:].split(',')[0]
    wknd=datetime.date.today().weekday()>=5
    walls=[]
    for p in parts:
        if re.match(r'W\d+:',p):
            a=p.split(':')[1].split(',')
            walls.append([float(a[0]),float(a[1]),a[2],float(a[3]),a[4]])
    spot=ctx.get('spot',{}).get(nm,np.nan)
    rowsX=[]
    for i,(lo,hi,wm,cc,fl) in enumerate(walls):
        mid=(lo+hi)/2
        above=[w[0] for w in walls if w[0]>hi]; below=[w[1] for w in walls if w[1]<lo]
        feat={'coin':nm,'hayden':hay,'hayden_btc':ctx.get('hayden_btc','na'),'btc_pi':ctx.get('btc_pi','na'),
              'contact':cc,'confl':np.nan,'widthU':(hi-lo)/ua,'ladder_ix':i+1,
              'dnextU':((min(above)-hi)/ua if above else np.nan),'dbehindU':((lo-max(below))/ua if below else np.nan),
              'last_tradedd':np.nan,'wk_used':ctx.get('wk_used',{}).get(nm,np.nan),
              'mo_day':datetime.date.today().day,'u_trend':np.nan,'U':ua,
              'virgin':('V' in fl),'stepPOC':('★' in fl),'above_open':(np.isfinite(spot) and mid>spot),
              'wknd':wknd,'gap':False,'fomc':bool(ctx.get('fomc',False))}
        rowsX.append(feat)
    cats_maps=[{v:i for i,v in enumerate(c)} for c in enc.categories_]
    Xc=np.array([[cats_maps[k].get(str(f[c]),-1) for k,c in enumerate(CATS)] for f in rowsX],dtype=float)
    Xn=np.array([[ (float(f[c]) if f[c]==f[c] else np.nan) for c in NUMS]+[float(bool(f[c])) for c in BOOLS] for f in rowsX],dtype=float)
    P=clf.predict_proba(np.hstack([Xc,Xn]))[:,1]
    wi=0
    for j,p in enumerate(parts):
        if re.match(r'W\d+:',p):
            lo,hi,wm,cc,fl=walls[wi]
            cls='V' if 'V' in fl else ('S' if '★' in fl else ('W' if (hi-lo)/ua>=0.32 else '-'))
            parts[j]=p+f",{cls},{round(float(P[wi])*100)}"
            wi+=1
    out.append('|'.join(parts))
print('\n'.join(out))
