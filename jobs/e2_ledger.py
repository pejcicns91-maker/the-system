#!/usr/bin/env python3
"""e2_ledger.py — THE LEDGER QUESTION from the shipped episode tables (Svet's order, 2026-07-28).
Sequenced stop x target table from episode_exc: per level family (PD/ON/PS/PW/PM) x approach
side x entry basis (fade-at-touch, retest-entry) x coin. WIN = favorable excursion reaches the
target STRICTLY BEFORE adverse reaches the stop, read off the excursion staircases; equal
timestamps = the same 5m bar = AMBIGUOUS, a counted third outcome, never guessed; neither
reached by window end = NEITHER, counted. Grids swept under TWO EX-ANTE RULERS:
 ATR-prior = the PRIOR day's ATR14 (the stored atr14_1d includes the current day's range —
   a lookahead as a stop denominator — so the ruler is shift(1), derived at query time,
   deviation from the stored column NAMED; record untouched);
 STRUCTURAL = the corridor (the level grid as its own ruler, ex-ante at entry): stop as a
   fraction of the gap behind the position, target as a fraction of the gap ahead; 1.0 = the
   corridor mark itself.
COSTS: round-trip tolls attached as parameters at 13.5bp (the program's historical taker toll)
and 4.5bp (spot-maker ~ 1/3 FTMO friction, per PACK3) — per-episode cost in R = toll*price/stop,
averaged over decided; EV per decided trade in R = (sum R_win - n_loss)/n_dec - mean_cost_R.
Ambiguous and neither are EXCLUDED from EV and shown beside it. n on every cell; no floors,
no pruning; file sorted n_dec descending. Cross-coin consistency on pooled rows = how many of
the 4 coins share the pooled EV sign at each toll. Trade language legal under v1.1: computed
from EPISODE grain, entry/stop/target and their ORDER measured.
Ships -> results/ledger/: ledger_cells.parquet + LEDGER.md. Also (runner only) appends
contract v1.2 QUESTION LEDGER + writes docs/newproject/QUESTION_LEDGER.md — Svet's order;
running this job is the signature. Deterministic, no RNG. Counts only; verdicts are Svet's."""
import pandas as pd, numpy as np, json, os, sys, time, argparse, hashlib, subprocess

ap = argparse.ArgumentParser(); ap.add_argument('--budget-min', type=float, default=230)
A_, _ = ap.parse_known_args(); T0 = time.time()
COINS = ['BTC','ETH','SOL','XRP']
EPD, OUT = 'results/episodes', 'results/ledger'
os.makedirs(OUT, exist_ok=True)
INF = np.int64(2**62)
SK_ATR = [0.10,0.20,0.30,0.50,0.75,1.00]; TK_ATR = [0.25,0.50,0.75,1.00,1.50,2.00]
SK_ST  = [0.25,0.50,0.75,1.00];           TK_ST  = [0.25,0.50,0.75,1.00]
GEOMS = [('ATRp', a, b) for a in SK_ATR for b in TK_ATR] + [('STRUCT', a, b) for a in SK_ST for b in TK_ST]
NG_ATR, NG_ST = len(SK_ATR)*len(TK_ATR), len(SK_ST)*len(TK_ST)
TOLL_HI, TOLL_LO = 0.00135, 0.00045

CONTRACT = 'docs/newproject/PHASE_CONTRACT_v1.md'
V11_SHA = '2bd4318705e72bdade59377a95f5de183a1bfc18c695f3a3d00a5ca26b97ba54'
V12_APPEND = """
## v1.2 — QUESTION LEDGER (Svet's order in chat, 2026-07-28; running e2_ledger.py = the signature)
Svet's destination questions are tracked in docs/newproject/QUESTION_LEDGER.md with status
ANSWERED / PARTIAL / NOT-YET. Every shipment's report carries the ledger block with statuses
as of that shipment; statuses are proposed by shipments and stand only until Svet's word.
A shipment that advances no ledger question says so. Adding a question = Svet's word, one line.
"""
LEDGER_MD = """# QUESTION LEDGER — Svet's destination questions (v1.2 law; statuses as of 2026-07-28 e2 shipment)
L1 The stop x target x situation ledger: which geometries, in which situations, clear costs —
   sequenced from episode grain. — PARTIAL: family x side x basis situations ANSWERED under the
   ATR-prior and corridor rulers at the swept grids, costs at 13.5/4.5bp (results/ledger/);
   component-conditioned situations await the B/C episode re-run.
L2 C2's tie: unconditionable market vs too-blunt outcome. — NOT-YET (decided by B/C vs episode outcomes).
L3 Trend-day vs range-day: which day-label candidate earns the name, and the two conditionals
   (sweep-and-reverse | range-day; pullback-continuation | trend-day). — PARTIAL (daychar tables
   shipped per candidate under three rulers; verdict open).
L4 Do component readings — alone, at offsets, paired — condition episode outcomes? — NOT-YET.
L5 The Daily Analyst: morning packet -> levels, scenarios, odds. — NOT-YET (the destination).
Note on the old verdict "geometry isn't there": L1 is its re-trial at swept parameters under two
ex-ante rulers at episode grain; the frozen 0.6U stop is one point inside these grids, not a law.
"""

def docs_step():
    if not os.environ.get('GITHUB_ACTIONS'):
        print('local run: contract v1.2 + ledger doc not written (runner only).'); return
    cur = open(CONTRACT,'rb').read()
    if hashlib.sha256(cur).hexdigest() != V11_SHA:
        if V12_APPEND.strip() in cur.decode('utf-8'):
            print('contract already at v1.2; ledger doc refresh only.')
        else:
            print('CONTRACT DRIFT: bytes are neither v1.1 nor v1.2 — never overwritten. STOP.'); sys.exit(1)
    else:
        open(CONTRACT,'ab').write(V12_APPEND.encode()); print('contract appended -> v1.2')
    open('docs/newproject/QUESTION_LEDGER.md','w').write(LEDGER_MD)
    try:
        subprocess.run(['git','config','user.name','job-bot'], check=True)
        subprocess.run(['git','config','user.email','bot@none'], check=True)
        subprocess.run(['git','add', CONTRACT, 'docs/newproject/QUESTION_LEDGER.md'], check=True)
        subprocess.run(['git','commit','-m','docs: contract v1.2 QUESTION LEDGER (Svet order 2026-07-28) [skip ci]'], check=True)
        subprocess.run(['git','push'], check=True)
        print('DOCS COMMITTED: contract v1.2 + QUESTION_LEDGER.md')
    except subprocess.CalledProcessError as e:
        print(f'DOCS COMMIT FAILED ({e}) — named, not silent; ledger build continues.')

def fam(mk): return mk[:2]

def run():
    acc = {}   # (coin,family,side,basis,ruler,a,b) -> counters
    def bump(k, field, v=1):
        c = acc.setdefault(k, {'win':0,'loss':0,'amb':0,'nei':0,'na':0,'sumRwin':0.0,'sumcb':0.0,'sumsat':0.0,'nsat':0})
        c[field] += v
    recon = []
    for coin in COINS:
        t_c = time.time()
        E = pd.read_parquet(f'{EPD}/episodes_{coin}.parquet',
            columns=['wdate','mark','price','t0','corridor_up_price','corridor_dn_price'])
        A = pd.read_parquet(f'results/layerb/anchors_{coin}.parquet',
            columns=['wdate','mark','price','t0','open_side'])
        D = pd.read_parquet(f'results/record/bars_{coin}_1D.parquet', columns=['wdate','atr14_1d'])
        D['wdate'] = D.wdate.astype(str); D = D.sort_values('wdate')
        D['atr_prior'] = D.atr14_1d.shift(1)   # EX-ANTE ATR ruler (deviation from stored same-day column, named)
        E = E.merge(A, on=['wdate','mark','price','t0'], validate='1:1')
        E = E.merge(D[['wdate','atr_prior']], on='wdate', how='left')
        X = pd.read_parquet(f'{EPD}/episode_exc_{coin}.parquet',
            columns=['wdate','mark','t0','basis','side','seq','px','at']).sort_values(
            ['wdate','mark','t0','basis','side','seq'])
        meta = E.set_index(['wdate','mark','t0'])
        n_el = {'ATRp':{'fade':0,'rt':0},'STRUCT':{'fade':0,'rt':0}}
        for (wd, mk, t0v, basis), g in X.groupby(['wdate','mark','t0','basis'], sort=False):
            m_ = meta.loc[(wd, mk, t0v)]
            m = float(m_.price); osd = int(m_.open_side)
            d = osd if basis == 'fade' else -osd
            fv = g[g.side == 'fav']; av = g[g.side == 'adv']
            fex = (d*(fv.px.to_numpy() - m)); fat = fv['at'].values.astype('datetime64[ns]').astype(np.int64)
            aex = (-d*(av.px.to_numpy() - m)); aat = av['at'].values.astype('datetime64[ns]').astype(np.int64)
            if not (np.all(np.diff(fex) > 0) and np.all(np.diff(aex) > 0)):
                print(f'FATAL: non-monotone staircase {coin} {wd} {mk} {basis}'); sys.exit(1)
            fam_, side_ = fam(mk), ('from_above' if osd == 1 else 'from_below')
            atr = float(m_.atr_prior) if pd.notna(m_.atr_prior) else np.nan
            cu, cd = m_.corridor_up_price, m_.corridor_dn_price
            ahead  = (cu - m) if d == 1 else (m - cd) if d == -1 else np.nan
            behind = (m - cd) if d == 1 else (cu - m)
            ahead  = float(ahead) if pd.notna(ahead) else np.nan
            behind = float(behind) if pd.notna(behind) else np.nan
            ok_atr = np.isfinite(atr); ok_st = np.isfinite(ahead) and np.isfinite(behind)
            if ok_atr: n_el['ATRp'][basis] += 1
            if ok_st:  n_el['STRUCT'][basis] += 1
            entry_at = fat[0]   # the basis's entry bar (touch bar / retest-touch bar)
            for ruler, a, b in GEOMS:
                k = (coin, fam_, side_, basis, ruler, a, b)
                if ruler == 'ATRp':
                    if not ok_atr: bump(k,'na'); continue
                    s_thr, t_thr = a*atr, b*atr
                else:
                    if not ok_st: bump(k,'na'); continue
                    s_thr, t_thr = a*behind, b*ahead
                i = int(np.searchsorted(aex, s_thr)); j = int(np.searchsorted(fex, t_thr))
                tstop = aat[i] if i < len(aat) else INF
                ttgt  = fat[j] if j < len(fat) else INF
                first = min(tstop, ttgt)
                if first == INF: bump(k,'nei')
                elif first == entry_at or tstop == ttgt:
                    # entry-bar rule: any resolution on the entry bar is same-bar with the
                    # entry moment itself -> the third outcome (the touch splits the bar)
                    bump(k,'amb')
                elif ttgt < tstop:
                    bump(k,'win'); bump(k,'sumRwin', t_thr/s_thr); bump(k,'sumcb', m/s_thr)
                    if ok_atr: bump(k,'sumsat', s_thr/atr); bump(k,'nsat')
                else:
                    bump(k,'loss'); bump(k,'sumcb', m/s_thr)
                    if ok_atr: bump(k,'sumsat', s_thr/atr); bump(k,'nsat')
        recon.append((coin, dict(n_el)))
        print(f'{coin}: bases fade/rt ATRp {n_el["ATRp"]["fade"]:,}/{n_el["ATRp"]["rt"]:,} · '
              f'STRUCT {n_el["STRUCT"]["fade"]:,}/{n_el["STRUCT"]["rt"]:,} · {round((time.time()-t_c)/60,2)}min')

    # pooled rollups: coin ALL4 and family ALL (additive counters -> exact pooling)
    def rollup(rows, pos, label):
        out = {}
        for k, c in rows.items():
            kk = list(k); kk[pos] = label; kk = tuple(kk)
            o = out.setdefault(kk, {'win':0,'loss':0,'amb':0,'nei':0,'na':0,'sumRwin':0.0,'sumcb':0.0,'sumsat':0.0,'nsat':0})
            for f in o: o[f] += c[f]
        return out
    allc = dict(acc); allc.update(rollup(acc, 0, 'ALL4'))
    allc.update(rollup(allc, 1, 'ALL'))

    rows = []
    for k, c in allc.items():
        nd = c['win'] + c['loss']
        p = c['win']/nd if nd else np.nan
        mR = c['sumRwin']/c['win'] if c['win'] else np.nan
        mc_hi = TOLL_HI*c['sumcb']/nd if nd else np.nan
        mc_lo = TOLL_LO*c['sumcb']/nd if nd else np.nan
        gross = (c['sumRwin'] - c['loss'])/nd if nd else np.nan
        msat = c['sumsat']/c['nsat'] if c['nsat'] else np.nan
        rows.append(k + (nd, c['win'], c['loss'], c['amb'], c['nei'], c['na'], p, mR,
                         gross, mc_hi, mc_lo,
                         (gross - mc_hi) if nd else np.nan, (gross - mc_lo) if nd else np.nan, msat))
    L = pd.DataFrame(rows, columns=['coin','family','side','basis','ruler','stop_k','tgt_k',
        'n_dec','n_win','n_loss','n_amb','n_nei','n_na','p_win_dec','mean_R_win',
        'ev_R_gross','cost_R_135bp','cost_R_45bp','ev_R_135bp','ev_R_45bp','mean_stop_atr'])
    assert not L.duplicated(['coin','family','side','basis','ruler','stop_k','tgt_k']).any()
    # cross-coin consistency on pooled rows
    kcols = ['family','side','basis','ruler','stop_k','tgt_k']
    pc = L[L.coin.isin(COINS)].copy()
    for col, out in (('ev_R_135bp','agree4_135'), ('ev_R_45bp','agree4_45')):
        pooled = L[L.coin == 'ALL4'][kcols + [col]].rename(columns={col: 'pooled'})
        j = pc[kcols + ['coin', col]].merge(pooled, on=kcols)
        j['ag'] = ((j[col] > 0) == (j.pooled > 0)) & np.isfinite(j[col]) & np.isfinite(j.pooled)
        ag = j.groupby(kcols, as_index=False).ag.sum().rename(columns={'ag': out})
        L = L.merge(ag, on=kcols, how='left')
    L = L.sort_values('n_dec', ascending=False).reset_index(drop=True)
    L.to_parquet(f'{OUT}/ledger_cells.parquet', compression='zstd', index=False)

    # reconciliation: per coin/ruler/basis: outcomes sum == eligible x n_geoms; na == ineligible x n_geoms
    lines = [f'# LEDGER — sequenced stop x target from episode grain — {pd.Timestamp.now(tz="UTC")}',
             f'cells (incl. ALL4/ALL rollups): {len(L):,} · file sorted n_dec descending · no floors, no pruning']
    ok_all = True
    base = L[L.coin.isin(COINS) & (L.family != 'ALL')]
    for coin, nl in recon:
        for ruler, ng in (('ATRp', NG_ATR), ('STRUCT', NG_ST)):
            for basis in ('fade','rt'):
                sub = base[(base.coin==coin)&(base.ruler==ruler)&(base.basis==basis)]
                got = int((sub.n_win+sub.n_loss+sub.n_amb+sub.n_nei).sum())
                exp = nl[ruler][basis]*ng
                ok = got == exp; ok_all &= ok
                lines.append(f'recon {coin} {ruler} {basis}: outcomes {got:,} == eligible x geoms {exp:,} '
                             f'{"PASS" if ok else "FAIL"} · na {int(sub.n_na.sum()):,}')
    # page-one views into the md (the file carries the read; parquet carries every cell)
    PA = L[(L.coin=='ALL4') & (L.family=='ALL')]
    def piv(basis, ruler, col):
        return PA[(PA.basis==basis)&(PA.ruler==ruler)].pivot_table(
            index='stop_k', columns='tgt_k', values=col, aggfunc='first').round(3).to_string()
    for basis in ('fade','rt'):
        lines.append(f'\n## whole-population grid — {basis} · ATR-prior ruler (ALL4 x ALL families)')
        lines.append('p_win_dec:\n' + piv(basis,'ATRp','p_win_dec'))
        lines.append('EV_R @13.5bp:\n' + piv(basis,'ATRp','ev_R_135bp'))
        lines.append('EV_R @4.5bp:\n' + piv(basis,'ATRp','ev_R_45bp'))
        lines.append('ambiguous n (same-bar incl. entry-bar rule):\n' + PA[(PA.basis==basis)&(PA.ruler=='ATRp')].pivot_table(index='stop_k',columns='tgt_k',values='n_amb',aggfunc='first').to_string())
        lines.append(f'\n## whole-population grid — {basis} · STRUCTURAL ruler (corridor)')
        lines.append('EV_R gross (before toll):\n' + piv(basis,'STRUCT','ev_R_gross'))
        lines.append('EV_R @13.5bp:\n' + piv(basis,'STRUCT','ev_R_135bp'))
        lines.append('mean stop in ATR-prior units (cross-ruler line):\n' + piv(basis,'STRUCT','mean_stop_atr'))
    pos135 = L[(L.coin=='ALL4')&(L.ev_R_135bp>0)]
    pos45  = L[(L.coin=='ALL4')&(L.ev_R_45bp>0)]
    lines.append(f'\n## cost-clearing scan (pooled cells, incl. family cells)')
    lines.append(f'cells EV>0 @13.5bp: {len(pos135)} (of {len(L[L.coin=="ALL4"])}) · with 4/4 coin agreement: {int((pos135.agree4_135==4).sum())}')
    lines.append(f'cells EV>0 @4.5bp:  {len(pos45)} · with 4/4 coin agreement: {int((pos45.agree4_45==4).sum())}')
    top = pos135[pos135.agree4_135==4].sort_values('n_dec',ascending=False).head(15)
    if len(top):
        lines.append('page-one of the 4/4-consistent cost-clearing cells (by n_dec):')
        lines.append(top[['family','side','basis','ruler','stop_k','tgt_k','n_dec','n_amb','n_nei','p_win_dec','ev_R_gross','ev_R_135bp','ev_R_45bp','agree4_135']].to_string(index=False))
    neg = L[(L.coin=='ALL4')&(L.ev_R_135bp<0)&(L.agree4_135==4)]
    lines.append(f'cells EV<0 @13.5bp with 4/4 agreement (the consistent do-not corners): {len(neg)}')
    tpc = L[L.coin.isin(COINS)].sort_values('n_dec',ascending=False).head(12)
    lines.append('\nlargest per-coin cells (n_dec desc):')
    lines.append(tpc[['coin','family','side','basis','ruler','stop_k','tgt_k','n_dec','n_amb','p_win_dec','ev_R_135bp']].to_string(index=False))
    lines.append('conventions: WIN = favorable >= target strictly before adverse >= stop, off the exc staircases; '
                 'equal 5m timestamps = AMBIGUOUS (third outcome, counted); ENTRY-BAR RULE: any resolution on the entry bar is same-bar with the entry moment (the touch splits the bar) and is also the third outcome — the touch bar\'s bounce-side extreme can predate the touch, so scoring it decided would be a within-bar guess; neither by window end = NEITHER; '
                 'ATRp ruler = PRIOR-day ATR14 (stored atr14_1d includes the current day — lookahead as a stop '
                 'denominator — so shift(1) derived at query time; record untouched; one-word swap re-runs U or '
                 'same-day ATR); STRUCT ruler = corridor gaps ex-ante (1.0 = the corridor mark); costs = round-trip '
                 'toll x price / stop per episode, tolls 13.5bp (historical taker) and 4.5bp (spot-maker ~ 1/3 FTMO), '
                 'parameters attached; EV in R per decided trade, amb/nei excluded and shown. Verdicts are Svet\'s.')
    open(f'{OUT}/LEDGER.md','w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:2])); print(f'recon: {"ALL PASS" if ok_all else "FAIL"}')
    if not ok_all: sys.exit(1)
    return L

docs_step()
L = run()
print(f'total {round((time.time()-T0)/60,2)} min · deterministic, no RNG')
