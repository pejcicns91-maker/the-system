import numpy as np, pandas as pd, glob, hashlib, os
import pyarrow as pa, pyarrow.parquet as pq
Z=np.load("b0x_num.npz"); p_b,p_t,cb,ct=Z['p_b'],Z['p_t'],Z['cb'],Z['ct']
base_b,base_t,maxdiff,dep,n_=float(Z['base_b']),float(Z['base_t']),float(Z['maxdiff']),Z['dep'],Z['n_']
NB=len(glob.glob("ckpt_b0x/blk_*.parquet"))
schema=pa.schema([('family',pa.string()),('depth',pa.int8()),('f1',pa.string()),('v1',pa.string()),
                  ('f2',pa.string()),('v2',pa.string()),('rate',pa.float64()),('base',pa.float64()),
                  ('n',pa.int64()),('p',pa.float64()),('certified',pa.bool_())])
w=pq.ParquetWriter("bf_ladder_b0x.parquet",schema,compression='zstd'); digest=[]
kk={'bounce':None,'through':None}
for fam,pp,cc,bb in [('bounce',p_b,cb,base_b),('through',p_t,ct,base_t)]:
    off=0
    for i in range(NB):
        B=pd.read_parquet(f"ckpt_b0x/blk_{i:03d}.parquet")
        s=slice(off,off+len(B)); off+=len(B)
        kv=(B.kb if fam=='bounce' else B.kt).to_numpy(np.int64)
        D=pd.DataFrame({'family':fam,'depth':B.depth.astype(np.int8),'f1':B.f1,'v1':B.v1,'f2':B.f2,'v2':B.v2,
                        'rate':np.round(kv/n_[s],3),'base':round(bb,3),'n':n_[s],'p':pp[s],'certified':cc[s]})
        w.write_table(pa.Table.from_pandas(D,schema=schema,preserve_index=False))
        dd=D[(D.certified)&(D.n>=100)].assign(lift=lambda x:(x.rate-x.base).abs())
        if len(dd): digest.append(dd.nlargest(min(800,len(dd)),'lift'))
        del B,D,dd
    print(fam,"written",flush=True)
w.close()
DG=pd.concat(digest,ignore_index=True)
DG=pd.concat([DG[(DG.family==f)&(DG.depth==d)].nlargest(200,'lift') for f in ['bounce','through'] for d in [1,2,3,4]],ignore_index=True)
DG.drop(columns=['lift']).to_csv("bf_ladder_b0x_digest.csv",index=False)
E=pd.concat([pd.read_parquet(f"ckpt_b0x/ext_{i:03d}.parquet") for i in range(NB)],ignore_index=True)
E['extinct']=E.cells==0; E.to_csv("bf_extinction_b0x.csv",index=False)
tot=len(n_)
print("=== widened-ladder assembly complete ===")
print(f"bases b {base_b:.3f} t {base_t:.3f} | cells/family {tot:,} | register rows {2*tot:,}")
for d in [1,2,3,4]:
    m=dep==d
    print(f"d{d}: cells {int(m.sum()):,} | cert b {int(cb[m].sum()):,} t {int(ct[m].sum()):,}")
print(f"cert total: b {int(cb.sum()):,} ({cb.mean():.1%}) t {int(ct.sum()):,} ({ct.mean():.1%})")
print(f"combos {len(E)} | extinct {int(E.extinct.sum())} | cells/combo med d4 {E[E.depth==4].cells.median():.0f}")
print(f"p-val vs scipy (200 seeded): {maxdiff:.2e}")
for f in ["bf_ladder_b0x.parquet","bf_ladder_b0x_digest.csv","bf_extinction_b0x.csv"]:
    print(f,f"{os.path.getsize(f)/1e6:.1f}MB sha",hashlib.sha256(open(f,'rb').read()).hexdigest()[:12])
