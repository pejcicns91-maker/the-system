# SOL TradingView Pine Scripts — Indicators A & B

**Companion to the project handoff (`SOL_Engine_Handoff.md`).** These are the two core on-chart indicators (A = structure, B = plan). C and P are not here — they're built later.

**Honest notes before you paste:**
- These are the latest versions from our chat, **reasoned not compiled** (no Pine compiler in the sandbox). If a line throws a red error on paste, send me the exact line and I'll fix it.
- If your live TradingView copies have diverged since, **yours are the source of truth** — diff before overwriting.
- **A is the multi-TF nested *Levels* version** (fixed bar-count windows per TF, outlier-clipped) — **not** the rejected visible-range "Profile + S/R Matrix" variant.
- Both are Pine v6, overlay indicators. They run independently; add **A first**, confirm it loads, then add **B**.

---

## Indicator A — `MTF Volume Structure — Levels [A]`

Multi-TF nested overlay: per-TF profiles via `request.security` across **D / 4H / 1H / 15m / 5m**, drawing nested **POC / VA / HVN / LVN** lines. Fixed bar-count windows per TF (swing-tuned: D≈60, 4H≈120, 1H≈240, 15m≈384, 5m≈288), mean ± 3σ outlier clip, POC-vs-price sanity gate (shows "⚠ data" instead of drawing garbage), skew read, stats table. The per-TF windows are inputs at the top of settings (keep ≤ 595).

```pinescript
//@version=6
indicator("MTF Volume Structure — Levels [A]", "MTF·VS", overlay=true, max_lines_count=500, max_labels_count=200, max_bars_back=600)

gP = "Profile"
bins  = input.int(48, "Bins", minval=12, maxval=120, group=gP)
vaPct = input.float(0.70, "Value area %", minval=0.5, maxval=0.95, step=0.05, group=gP)
swStr = input.int(10, "Swing strength (L/R bars)", minval=2, maxval=50, group=gP, tooltip="Used only for the drawn swing markers")

gL = "Lookback per timeframe (bars) — swing-tuned"
lenD   = input.int(60,  "Daily (context)", minval=20, maxval=595, group=gL, tooltip="~2-3 months")
lenH4  = input.int(120, "4H (swing)",      minval=20, maxval=595, group=gL, tooltip="~3 weeks")
lenH1  = input.int(240, "1H (active)",     minval=20, maxval=595, group=gL, tooltip="~10 days")
lenM15 = input.int(384, "15m",             minval=20, maxval=595, group=gL, tooltip="~4 days")
lenM5  = input.int(288, "5m",              minval=20, maxval=595, group=gL, tooltip="~1 day")

gS = "Robustness"
outK     = input.float(3.0, "Outlier clip (×σ)", minval=1.5, maxval=6.0, step=0.5, group=gS, tooltip="Bars beyond this many std-devs of price are excluded — kills bad prints")
sanityLo = input.float(0.5, "POC must be ≥ price ×", minval=0.05, maxval=0.95, step=0.05, group=gS)
sanityHi = input.float(2.0, "POC must be ≤ price ×", minval=1.1, maxval=10.0, step=0.1, group=gS)

gN = "HVN / LVN (drawn on D / 1H / 5m)"
hvnMult = input.float(1.4, "HVN ≥ mean ×", minval=1.05, step=0.05, group=gN)
lvnMult = input.float(0.6, "LVN ≤ mean ×", minval=0.1, maxval=0.95, step=0.05, group=gN)

gD = "Display"
showVA    = input.bool(true, "Value-area bands", group=gD)
showNodes = input.bool(true, "HVN/LVN markers", group=gD)
showPiv   = input.bool(true, "Swing markers", group=gD)
labOff    = input.int(8, "Label offset (bars)", minval=0, group=gD)
tPos      = input.string("right", "Table", options=["right","left","top right","top left","bottom right","bottom left"], group=gD)

gMX = "Multi-exchange (crypto, optional)"
useAgg = input.bool(false, "Use aggregated symbol for the profile", group=gMX)
aggSym = input.string("", "Aggregated symbol (e.g. CRYPTO:SOLUSD)", group=gMX)

gTF = "Timeframes"
sD   = input.bool(true, "D",   inline="d",  group=gTF)
sH4  = input.bool(true, "4H",  inline="h4", group=gTF)
sH1  = input.bool(true, "1H",  inline="h1", group=gTF)
sM15 = input.bool(true, "15m", inline="m15",group=gTF)
sM5  = input.bool(true, "5m",  inline="m5", group=gTF)

gC = "Colors"
cD  = input.color(#ffb300, "D",   group=gC)
cH4 = input.color(#ff7043, "4H",  group=gC)
cH1 = input.color(#29b6f6, "1H",  group=gC)
cM15= input.color(#66bb6a, "15m", group=gC)
cM5 = input.color(#b0bec5, "5m",  group=gC)

color cBg = color.new(color.black, 30)
color cHd = color.new(color.gray, 25)

f_pos(string s) =>
    s=="left" ? position.middle_left : s=="top right" ? position.top_right : s=="top left" ? position.top_left : s=="bottom right" ? position.bottom_right : s=="bottom left" ? position.bottom_left : position.middle_right

f_levels(simple int nb, float vap, simple int len, float kSig, float hvnM, float lvnM) =>
    int n = len
    float poc = na
    float vah = na
    float val = na
    float hh  = na
    float ll  = na
    float tot = 0.0
    float hvn1 = na
    float hvn2 = na
    float lvn1 = na
    float lvn2 = na
    if barstate.islast
        float amin = na
        float amax = na
        float sum = 0.0
        float ssq = 0.0
        int cnt = 0
        for k = 0 to n - 1
            float hk = high[k]
            float lk = low[k]
            float ck = close[k]
            if not na(hk) and not na(lk) and not na(ck)
                amin := na(amin) ? lk : math.min(amin, lk)
                amax := na(amax) ? hk : math.max(amax, hk)
                float src = (hk + lk + ck) / 3.0
                sum := sum + src
                ssq := ssq + src * src
                cnt := cnt + 1
        if cnt > 0 and not na(amin) and not na(amax) and amax > amin
            float mean = sum / cnt
            float vrc = math.max(0.0, ssq / cnt - mean * mean)
            float sd = math.sqrt(vrc)
            float loB = math.max(amin, mean - kSig * sd)
            float hiB = math.min(amax, mean + kSig * sd)
            if hiB <= loB
                loB := amin
                hiB := amax
            ll := loB
            hh := hiB
            float bs = (hiB - loB) / nb
            arrV = array.new_float(nb, 0.0)
            for k = 0 to n - 1
                float hk = high[k]
                float lk = low[k]
                float ck = close[k]
                float vk = volume[k]
                if not na(hk) and not na(lk) and not na(ck) and not na(vk)
                    float src = (hk + lk + ck) / 3.0
                    if src >= loB and src <= hiB
                        int bi = int((src - loB) / bs)
                        bi := bi < 0 ? 0 : (bi > nb - 1 ? nb - 1 : bi)
                        array.set(arrV, bi, array.get(arrV, bi) + vk)
            int pocBin = 0
            float pocVol = -1.0
            for i = 0 to nb - 1
                float v = array.get(arrV, i)
                tot := tot + v
                if v > pocVol
                    pocVol := v
                    pocBin := i
            poc := loB + (pocBin + 0.5) * bs
            float meanV = tot / nb
            float target = tot * vap
            float acc = pocVol
            int lo = pocBin
            int hi = pocBin
            while acc < target and (lo > 0 or hi < nb - 1)
                float loV = lo > 0 ? array.get(arrV, lo - 1) : -1.0
                float hiV = hi < nb - 1 ? array.get(arrV, hi + 1) : -1.0
                if hiV >= loV
                    hi := hi + 1
                    acc := acc + (hiV > 0 ? hiV : 0.0)
                else
                    lo := lo - 1
                    acc := acc + (loV > 0 ? loV : 0.0)
            vah := loB + (hi + 1) * bs
            val := loB + lo * bs
            float h1v = -1.0
            float h2v = -1.0
            int   h1b = -1
            int   h2b = -1
            float l1v = 1e18
            float l2v = 1e18
            int   l1b = -1
            int   l2b = -1
            for i = 1 to nb - 2
                float v  = array.get(arrV, i)
                float vm = array.get(arrV, i - 1)
                float vp = array.get(arrV, i + 1)
                bool isMax = v >= vm and v >= vp
                bool isMin = v <= vm and v <= vp
                if isMax and v > meanV * hvnM and i != pocBin
                    if v > h1v
                        h2v := h1v
                        h2b := h1b
                        h1v := v
                        h1b := i
                    else if v > h2v
                        h2v := v
                        h2b := i
                if isMin and v < meanV * lvnM
                    if v < l1v
                        l2v := l1v
                        l2b := l1b
                        l1v := v
                        l1b := i
                    else if v < l2v
                        l2v := v
                        l2b := i
            hvn1 := h1b >= 0 ? loB + (h1b + 0.5) * bs : na
            hvn2 := h2b >= 0 ? loB + (h2b + 0.5) * bs : na
            lvn1 := l1b >= 0 ? loB + (l1b + 0.5) * bs : na
            lvn2 := l2b >= 0 ? loB + (l2b + 0.5) * bs : na
    [poc, vah, val, hh, ll, tot, hvn1, hvn2, lvn1, lvn2]

var line[]  Lpoc  = array.new_line()
var line[]  Lva   = array.new_line()
var line[]  Lnode = array.new_line()
var label[] Llab  = array.new_label()
var table   T     = table.new(f_pos(tPos), 7, 6, border_width=1, frame_width=1, frame_color=color.new(color.gray,40))

f_delAll() =>
    if array.size(Lpoc) > 0
        for i = 0 to array.size(Lpoc) - 1
            line.delete(array.get(Lpoc, i))
        array.clear(Lpoc)
    if array.size(Lva) > 0
        for i = 0 to array.size(Lva) - 1
            line.delete(array.get(Lva, i))
        array.clear(Lva)
    if array.size(Lnode) > 0
        for i = 0 to array.size(Lnode) - 1
            line.delete(array.get(Lnode, i))
        array.clear(Lnode)
    if array.size(Llab) > 0
        for i = 0 to array.size(Llab) - 1
            label.delete(array.get(Llab, i))
        array.clear(Llab)

f_lvl(bool show, bool sane, bool nodes, float poc, float vah, float val, float h1, float h2, float l1, float l2, color c, int w, string tag, int xL, int xR, int lx) =>
    if show and sane and not na(poc)
        array.push(Lpoc, line.new(xL, poc, xR, poc, color=c, width=w, extend=extend.left))
        array.push(Llab, label.new(lx, poc, tag + " POC " + str.tostring(poc, format.mintick), style=label.style_none, textcolor=c, size=size.small, textalign=text.align_left))
        if showVA and not na(vah) and not na(val)
            array.push(Lva, line.new(xL, vah, xR, vah, color=color.new(c,40), width=1, style=line.style_dotted, extend=extend.left))
            array.push(Lva, line.new(xL, val, xR, val, color=color.new(c,40), width=1, style=line.style_dotted, extend=extend.left))
        if nodes and showNodes
            if not na(h1)
                array.push(Lnode, line.new(xL, h1, xR, h1, color=color.new(c,15), width=2, extend=extend.left))
                array.push(Llab, label.new(lx, h1, tag + " HVN", style=label.style_none, textcolor=color.new(c,15), size=size.tiny, textalign=text.align_left))
            if not na(h2)
                array.push(Lnode, line.new(xL, h2, xR, h2, color=color.new(c,45), width=1, extend=extend.left))
            if not na(l1)
                array.push(Lnode, line.new(xL, l1, xR, l1, color=color.new(c,15), width=1, style=line.style_dashed, extend=extend.left))
                array.push(Llab, label.new(lx, l1, tag + " LVN", style=label.style_none, textcolor=color.new(c,15), size=size.tiny, textalign=text.align_left))
            if not na(l2)
                array.push(Lnode, line.new(xL, l2, xR, l2, color=color.new(c,45), width=1, style=line.style_dashed, extend=extend.left))

f_rowA(int r, string tf, color c, bool sane, float poc, float vah, float val, float h1, float l1, float hh, float ll) =>
    table.cell(T, 0, r, tf, text_color=c, bgcolor=cBg, text_size=size.tiny)
    if not sane
        table.cell(T, 1, r, "⚠ data", text_color=color.orange, bgcolor=cBg, text_size=size.tiny)
        table.cell(T, 2, r, "—", text_color=color.gray, bgcolor=cBg, text_size=size.tiny)
        table.cell(T, 3, r, "—", text_color=color.gray, bgcolor=cBg, text_size=size.tiny)
        table.cell(T, 4, r, "—", text_color=color.gray, bgcolor=cBg, text_size=size.tiny)
        table.cell(T, 5, r, "—", text_color=color.gray, bgcolor=cBg, text_size=size.tiny)
        table.cell(T, 6, r, (na(hh) or na(ll)) ? "—" : str.tostring(ll,format.mintick)+"–"+str.tostring(hh,format.mintick), text_color=color.gray, bgcolor=cBg, text_size=size.tiny)
    else
        float sk = (na(vah) or na(val) or vah == val) ? na : (poc - val) / (vah - val)
        string skS = na(sk) ? "—" : (sk > 0.66 ? "hi" : sk < 0.33 ? "lo" : "mid")
        table.cell(T, 1, r, na(poc) ? "—" : str.tostring(poc, format.mintick), text_color=color.white, bgcolor=cBg, text_size=size.tiny)
        table.cell(T, 2, r, (na(vah) or na(val)) ? "—" : str.tostring(val,format.mintick)+"–"+str.tostring(vah,format.mintick), text_color=color.silver, bgcolor=cBg, text_size=size.tiny)
        table.cell(T, 3, r, skS, text_color=color.white, bgcolor=cBg, text_size=size.tiny)
        table.cell(T, 4, r, na(h1) ? "—" : str.tostring(h1, format.mintick), text_color=color.aqua, bgcolor=cBg, text_size=size.tiny)
        table.cell(T, 5, r, na(l1) ? "—" : str.tostring(l1, format.mintick), text_color=color.fuchsia, bgcolor=cBg, text_size=size.tiny)
        table.cell(T, 6, r, (na(hh) or na(ll)) ? "—" : str.tostring(ll,format.mintick)+"–"+str.tostring(hh,format.mintick), text_color=color.gray, bgcolor=cBg, text_size=size.tiny)

string volSym = useAgg and aggSym != "" ? aggSym : syminfo.tickerid
[pocD,vahD,valD,hhD,llD,totD,hvnD1,hvnD2,lvnD1,lvnD2]                 = request.security(volSym, "D",   f_levels(bins, vaPct, lenD,  outK, hvnMult, lvnMult))
[pocH4,vahH4,valH4,hhH4,llH4,totH4,hvnH41,hvnH42,lvnH41,lvnH42]       = request.security(volSym, "240", f_levels(bins, vaPct, lenH4, outK, hvnMult, lvnMult))
[pocH1,vahH1,valH1,hhH1,llH1,totH1,hvnH11,hvnH12,lvnH11,lvnH12]       = request.security(volSym, "60",  f_levels(bins, vaPct, lenH1, outK, hvnMult, lvnMult))
[pocM15,vahM15,valM15,hhM15,llM15,totM15,hvnM151,hvnM152,lvnM151,lvnM152] = request.security(volSym, "15", f_levels(bins, vaPct, lenM15, outK, hvnMult, lvnMult))
[pocM5,vahM5,valM5,hhM5,llM5,totM5,hvnM51,hvnM52,lvnM51,lvnM52]       = request.security(volSym, "5",   f_levels(bins, vaPct, lenM5,  outK, hvnMult, lvnMult))

float price = close
bool saneD   = not na(pocD)   and not na(hhD)   and not na(llD)   and hhD>llD     and pocD>=price*sanityLo  and pocD<=price*sanityHi
bool saneH4  = not na(pocH4)  and not na(hhH4)  and not na(llH4)  and hhH4>llH4   and pocH4>=price*sanityLo  and pocH4<=price*sanityHi
bool saneH1  = not na(pocH1)  and not na(hhH1)  and not na(llH1)  and hhH1>llH1   and pocH1>=price*sanityLo  and pocH1<=price*sanityHi
bool saneM15 = not na(pocM15) and not na(hhM15) and not na(llM15) and hhM15>llM15 and pocM15>=price*sanityLo and pocM15<=price*sanityHi
bool saneM5  = not na(pocM5)  and not na(hhM5)  and not na(llM5)  and hhM5>llM5   and pocM5>=price*sanityLo  and pocM5<=price*sanityHi

phc = ta.pivothigh(swStr, swStr)
plc = ta.pivotlow(swStr, swStr)
plotshape(showPiv and not na(phc), title="Swing High", style=shape.triangledown, location=location.abovebar, color=color.new(color.gray,30), size=size.tiny, offset=-swStr)
plotshape(showPiv and not na(plc), title="Swing Low",  style=shape.triangleup,   location=location.belowbar, color=color.new(color.gray,30), size=size.tiny, offset=-swStr)

if barstate.islast
    f_delAll()
    int xR = bar_index
    int xL = bar_index - 1
    int lx = bar_index + labOff
    f_lvl(sD,   saneD,   true,  pocD,   vahD,   valD,   hvnD1,  hvnD2,  lvnD1,  lvnD2,  cD,  3, "D",   xL, xR, lx)
    f_lvl(sH4,  saneH4,  false, pocH4,  vahH4,  valH4,  na, na, na, na,                 cH4, 2, "4H",  xL, xR, lx)
    f_lvl(sH1,  saneH1,  true,  pocH1,  vahH1,  valH1,  hvnH11, hvnH12, lvnH11, lvnH12, cH1, 2, "1H",  xL, xR, lx)
    f_lvl(sM15, saneM15, false, pocM15, vahM15, valM15, na, na, na, na,                 cM15,1, "15m", xL, xR, lx)
    f_lvl(sM5,  saneM5,  true,  pocM5,  vahM5,  valM5,  hvnM51, hvnM52, lvnM51, lvnM52, cM5, 1, "5m",  xL, xR, lx)
    table.cell(T, 0, 0, "TF",    text_color=color.white, bgcolor=cHd, text_size=size.tiny)
    table.cell(T, 1, 0, "POC",   text_color=color.white, bgcolor=cHd, text_size=size.tiny)
    table.cell(T, 2, 0, "VA",    text_color=color.white, bgcolor=cHd, text_size=size.tiny)
    table.cell(T, 3, 0, "Skew",  text_color=color.white, bgcolor=cHd, text_size=size.tiny)
    table.cell(T, 4, 0, "HVN",   text_color=color.white, bgcolor=cHd, text_size=size.tiny)
    table.cell(T, 5, 0, "LVN",   text_color=color.white, bgcolor=cHd, text_size=size.tiny)
    table.cell(T, 6, 0, "Range", text_color=color.white, bgcolor=cHd, text_size=size.tiny)
    f_rowA(1, "D",   cD,  saneD,   pocD,   vahD,   valD,   hvnD1,  lvnD1,  hhD,   llD)
    f_rowA(2, "4H",  cH4, saneH4,  pocH4,  vahH4,  valH4,  na,     na,     hhH4,  llH4)
    f_rowA(3, "1H",  cH1, saneH1,  pocH1,  vahH1,  valH1,  hvnH11, lvnH11, hhH1,  llH1)
    f_rowA(4, "15m", cM15,saneM15, pocM15, vahM15, valM15, na,     na,     hhM15, llM15)
    f_rowA(5, "5m",  cM5, saneM5,  pocM5,  vahM5,  valM5,  hvnM51, lvnM51, hhM5,  llM5)
```

---

## Indicator B — `MTF Volume Story — Swing Plan [B]`

Swing read built on A's engine (day-trade → 2–3 week). **BIAS** from 4H fair value + multi-day POC migration; active range from 1H; Daily = context only. Live **volume-at-price geometry classifier** (neck-between-shelves vs on-a-shelf, etc.), **smart targets** (skips any level closer than max(2×ATR, 0.8%); measured-move fallback), **WAIT-FOR** entry zone, **IF/THEN** bias flip, and alerts (entry-zone-reached / bias-change / invalidation). Reads as a plan, not a "do it now."

```pinescript
//@version=6
indicator("MTF Volume Story — Swing Plan [B]", "MTF·PLAN", overlay=true, max_lines_count=50, max_labels_count=50, max_bars_back=400)

gP = "Profile"
bins  = input.int(48, "Bins", minval=12, maxval=120, group=gP)
vaPct = input.float(0.70, "Value area %", minval=0.5, maxval=0.95, step=0.05, group=gP)
swStr = input.int(10, "Swing strength (L/R bars)", minval=2, maxval=50, group=gP)
outK  = input.float(3.0, "Outlier clip (×σ)", minval=1.5, maxval=6.0, step=0.5, group=gP)

gL = "Lookback (bars) — swing-tuned"
lenD  = input.int(60,  "Daily (context)", minval=20, maxval=395, group=gL)
len4H = input.int(120, "4H (bias)",       minval=20, maxval=395, group=gL)
len1H = input.int(240, "1H (active)",     minval=20, maxval=395, group=gL)
len5M = input.int(288, "5m (fine)",       minval=20, maxval=395, group=gL)

gTgt = "Targets"
atrMult = input.float(2.0, "Min target = ATR ×", minval=0.5, maxval=10, step=0.5, group=gTgt)
minPct  = input.float(0.8, "…or % of price (floor)", minval=0.1, maxval=5, step=0.1, group=gTgt, tooltip="A level closer than this to the entry is skipped as a target")

gM = "POC migration"
migLen  = input.int(288, "Bars per period", minval=20, maxval=395, group=gM, tooltip="One 'day' in bars: 288 = 24h crypto on 5m, ~78 = US-stock RTH on 5m")
migKeep = input.int(10, "Periods tracked", minval=3, maxval=30, group=gM)

gT = "Display"
tPos = input.string("left", "Table", options=["right","left","top right","top left","bottom right","bottom left"], group=gT)

gMX = "Multi-exchange (crypto, optional)"
useAgg = input.bool(false, "Use aggregated symbol", group=gMX)
aggSym = input.string("", "Aggregated symbol", group=gMX)

color cBg = color.new(color.black, 30)
color cHd = color.new(color.gray, 25)

f_pos(string s) =>
    s=="left" ? position.middle_left : s=="top right" ? position.top_right : s=="top left" ? position.top_left : s=="bottom right" ? position.bottom_right : s=="bottom left" ? position.bottom_left : position.middle_right
f_fp(float x) =>
    na(x) ? "—" : str.tostring(x, format.mintick)
f_near(float lv, float bnd) =>
    not na(lv) and not na(bnd) and math.abs(close - lv) <= bnd
f_nextAbove(float[] a, float fromLvl, float minD) =>
    float best = na
    if array.size(a) > 0
        for i = 0 to array.size(a) - 1
            float v = array.get(a, i)
            if v >= fromLvl + minD
                best := na(best) ? v : math.min(best, v)
    best
f_nextBelow(float[] a, float fromLvl, float minD) =>
    float best = na
    if array.size(a) > 0
        for i = 0 to array.size(a) - 1
            float v = array.get(a, i)
            if v <= fromLvl - minD
                best := na(best) ? v : math.max(best, v)
    best

f_levels(simple int nb, float vap, simple int len, float kSig) =>
    int n = len
    float poc = na
    float vah = na
    float val = na
    float hvn1 = na
    float lvn1 = na
    if barstate.islast
        float amin = na
        float amax = na
        float sum = 0.0
        float ssq = 0.0
        int cnt = 0
        for k = 0 to n - 1
            float hk = high[k]
            float lk = low[k]
            float ck = close[k]
            if not na(hk) and not na(lk) and not na(ck)
                amin := na(amin) ? lk : math.min(amin, lk)
                amax := na(amax) ? hk : math.max(amax, hk)
                float src = (hk + lk + ck) / 3.0
                sum := sum + src
                ssq := ssq + src * src
                cnt := cnt + 1
        if cnt > 0 and not na(amin) and not na(amax) and amax > amin
            float mean = sum / cnt
            float vrc = math.max(0.0, ssq / cnt - mean * mean)
            float sd = math.sqrt(vrc)
            float loB = math.max(amin, mean - kSig * sd)
            float hiB = math.min(amax, mean + kSig * sd)
            if hiB <= loB
                loB := amin
                hiB := amax
            float bs = (hiB - loB) / nb
            arrV = array.new_float(nb, 0.0)
            for k = 0 to n - 1
                float hk = high[k]
                float lk = low[k]
                float ck = close[k]
                float vk = volume[k]
                if not na(hk) and not na(lk) and not na(ck) and not na(vk)
                    float src = (hk + lk + ck) / 3.0
                    if src >= loB and src <= hiB
                        int bi = int((src - loB) / bs)
                        bi := bi < 0 ? 0 : (bi > nb - 1 ? nb - 1 : bi)
                        array.set(arrV, bi, array.get(arrV, bi) + vk)
            int pocBin = 0
            float pocVol = -1.0
            float tot = 0.0
            for i = 0 to nb - 1
                float v = array.get(arrV, i)
                tot := tot + v
                if v > pocVol
                    pocVol := v
                    pocBin := i
            poc := loB + (pocBin + 0.5) * bs
            float meanV = tot / nb
            float target = tot * vap
            float acc = pocVol
            int lo = pocBin
            int hi = pocBin
            while acc < target and (lo > 0 or hi < nb - 1)
                float loV = lo > 0 ? array.get(arrV, lo - 1) : -1.0
                float hiV = hi < nb - 1 ? array.get(arrV, hi + 1) : -1.0
                if hiV >= loV
                    hi := hi + 1
                    acc := acc + (hiV > 0 ? hiV : 0.0)
                else
                    lo := lo - 1
                    acc := acc + (loV > 0 ? loV : 0.0)
            vah := loB + (hi + 1) * bs
            val := loB + lo * bs
            float h1v = -1.0
            int   h1b = -1
            float l1v = 1e18
            int   l1b = -1
            for i = 1 to nb - 2
                float v  = array.get(arrV, i)
                float vm = array.get(arrV, i - 1)
                float vp = array.get(arrV, i + 1)
                if v >= vm and v >= vp and i != pocBin and v > h1v
                    h1v := v
                    h1b := i
                if v <= vm and v <= vp and v < l1v
                    l1v := v
                    l1b := i
            hvn1 := h1b >= 0 ? loB + (h1b + 0.5) * bs : na
            lvn1 := l1b >= 0 ? loB + (l1b + 0.5) * bs : na
    [poc, vah, val, hvn1, lvn1]

// volume-at-price geometry for the active (1H) profile
f_geom(simple int nb, simple int len, float kSig, float hvnM, float lvnM) =>
    int n = len
    float hvnUp = na
    float hvnDn = na
    float lvnUp = na
    float lvnDn = na
    int atCode = 1
    if barstate.islast
        float amin = na
        float amax = na
        float sum = 0.0
        float ssq = 0.0
        int cnt = 0
        for k = 0 to n - 1
            float hk = high[k]
            float lk = low[k]
            float ck = close[k]
            if not na(hk) and not na(lk) and not na(ck)
                amin := na(amin) ? lk : math.min(amin, lk)
                amax := na(amax) ? hk : math.max(amax, hk)
                float src = (hk + lk + ck) / 3.0
                sum := sum + src
                ssq := ssq + src * src
                cnt := cnt + 1
        if cnt > 0 and not na(amin) and not na(amax) and amax > amin
            float mean = sum / cnt
            float vrc = math.max(0.0, ssq / cnt - mean * mean)
            float sd = math.sqrt(vrc)
            float loB = math.max(amin, mean - kSig * sd)
            float hiB = math.min(amax, mean + kSig * sd)
            if hiB <= loB
                loB := amin
                hiB := amax
            float bs = (hiB - loB) / nb
            arrV = array.new_float(nb, 0.0)
            for k = 0 to n - 1
                float hk = high[k]
                float lk = low[k]
                float ck = close[k]
                float vk = volume[k]
                if not na(hk) and not na(lk) and not na(ck) and not na(vk)
                    float src = (hk + lk + ck) / 3.0
                    if src >= loB and src <= hiB
                        int bi = int((src - loB) / bs)
                        bi := bi < 0 ? 0 : (bi > nb - 1 ? nb - 1 : bi)
                        array.set(arrV, bi, array.get(arrV, bi) + vk)
            float tot = 0.0
            for i = 0 to nb - 1
                tot := tot + array.get(arrV, i)
            float meanV = tot / nb
            float pr = close
            int pBin = int((pr - loB) / bs)
            pBin := pBin < 0 ? 0 : (pBin > nb - 1 ? nb - 1 : pBin)
            float atVol = array.get(arrV, pBin)
            atCode := atVol > meanV * hvnM ? 2 : atVol < meanV * lvnM ? 0 : 1
            for i = 1 to nb - 2
                float v  = array.get(arrV, i)
                float vm = array.get(arrV, i - 1)
                float vp = array.get(arrV, i + 1)
                float bp = loB + (i + 0.5) * bs
                bool isMax = v >= vm and v >= vp and v > meanV * hvnM
                bool isMin = v <= vm and v <= vp and v < meanV * lvnM
                if isMax
                    if bp > pr
                        hvnUp := na(hvnUp) ? bp : math.min(hvnUp, bp)
                    if bp < pr
                        hvnDn := na(hvnDn) ? bp : math.max(hvnDn, bp)
                if isMin
                    if bp > pr
                        lvnUp := na(lvnUp) ? bp : math.min(lvnUp, bp)
                    if bp < pr
                        lvnDn := na(lvnDn) ? bp : math.max(lvnDn, bp)
    [hvnUp, hvnDn, lvnUp, lvnDn, atCode]

f_pocSimple(simple int lb, simple int nb, float kSig) =>
    float amin = na
    float amax = na
    float sum = 0.0
    float ssq = 0.0
    int cnt = 0
    float poc = na
    for k = 0 to lb - 1
        float hk = high[k]
        float lk = low[k]
        float ck = close[k]
        if not na(hk) and not na(lk) and not na(ck)
            amin := na(amin) ? lk : math.min(amin, lk)
            amax := na(amax) ? hk : math.max(amax, hk)
            float src = (hk + lk + ck) / 3.0
            sum := sum + src
            ssq := ssq + src * src
            cnt := cnt + 1
    if cnt > 0 and not na(amin) and not na(amax) and amax > amin
        float mean = sum / cnt
        float vrc = math.max(0.0, ssq / cnt - mean * mean)
        float sd = math.sqrt(vrc)
        float loB = math.max(amin, mean - kSig * sd)
        float hiB = math.min(amax, mean + kSig * sd)
        if hiB <= loB
            loB := amin
            hiB := amax
        float bs = (hiB - loB) / nb
        arrV = array.new_float(nb, 0.0)
        for k = 0 to lb - 1
            float hk = high[k]
            float lk = low[k]
            float ck = close[k]
            float vk = volume[k]
            if not na(hk) and not na(lk) and not na(ck) and not na(vk)
                float src = (hk + lk + ck) / 3.0
                if src >= loB and src <= hiB
                    int bi = int((src - loB) / bs)
                    bi := bi < 0 ? 0 : (bi > nb - 1 ? nb - 1 : bi)
                    array.set(arrV, bi, array.get(arrV, bi) + vk)
        int pb = 0
        float pv = -1.0
        for i = 0 to nb - 1
            float v = array.get(arrV, i)
            if v > pv
                pv := v
                pb := i
        poc := loB + (pb + 0.5) * bs
    poc

string volSym = useAgg and aggSym != "" ? aggSym : syminfo.tickerid
[pocD,vahD,valD,hvnD,lvnD]      = request.security(volSym, "D",   f_levels(bins, vaPct, lenD,  outK))
[poc4H,vah4H,val4H,hvn4H,lvn4H] = request.security(volSym, "240", f_levels(bins, vaPct, len4H, outK))
[poc1H,vah1H,val1H,hvn1H,lvn1H] = request.security(volSym, "60",  f_levels(bins, vaPct, len1H, outK))
[poc5M,vah5M,val5M,hvn5M,lvn5M] = request.security(volSym, "5",   f_levels(bins, vaPct, len5M, outK))
[hvnUp,hvnDn,lvnUp,lvnDn,atCode] = request.security(volSym, "60", f_geom(bins, len1H, outK, 1.4, 0.6))

float price = close

bool newDay = time("D") != time("D")[1]
var float[] dpoc = array.new_float()
if newDay and barstate.isconfirmed
    float p = f_pocSimple(migLen, 24, outK)
    if not na(p)
        array.push(dpoc, p)
        if array.size(dpoc) > migKeep
            array.shift(dpoc)
string migDir = "building…"
if array.size(dpoc) >= 3
    float first = array.get(dpoc, 0)
    float last  = array.get(dpoc, array.size(dpoc) - 1)
    int ups = 0
    int downs = 0
    for i = 1 to array.size(dpoc) - 1
        if array.get(dpoc, i) > array.get(dpoc, i - 1)
            ups := ups + 1
        else if array.get(dpoc, i) < array.get(dpoc, i - 1)
            downs := downs + 1
    migDir := (ups > downs and last > first) ? "up" : (downs > ups and last < first) ? "down" : "flat"

phc = ta.pivothigh(swStr, swStr)
plc = ta.pivotlow(swStr, swStr)
var float ph1 = na
var float ph0 = na
var float pl1 = na
var float pl0 = na
if not na(phc)
    ph0 := ph1
    ph1 := phc
if not na(plc)
    pl0 := pl1
    pl1 := plc
string struc = "mixed"
if not na(ph1) and not na(ph0) and not na(pl1) and not na(pl0)
    struc := (ph1 > ph0 and pl1 > pl0) ? "up" : (ph1 < ph0 and pl1 < pl0) ? "down" : "mixed"

var string state   = "Range — fade edges"
var int    stateBar = bar_index
if barstate.isconfirmed
    string ns = state
    if (migDir == "up" or struc == "up") and not na(poc4H) and price > poc4H
        ns := "Uptrend — buy dips"
    else if (migDir == "down" or struc == "down") and not na(poc4H) and price < poc4H
        ns := "Downtrend — sell rips"
    else
        ns := "Range — fade edges"
    if ns != state
        state := ns
        stateBar := bar_index

lv = array.new_float()
if not na(poc1H)
    array.push(lv, poc1H)
if not na(vah1H)
    array.push(lv, vah1H)
if not na(val1H)
    array.push(lv, val1H)
if not na(hvn1H)
    array.push(lv, hvn1H)
if not na(lvn1H)
    array.push(lv, lvn1H)
if not na(poc4H)
    array.push(lv, poc4H)
if not na(vah4H)
    array.push(lv, vah4H)
if not na(val4H)
    array.push(lv, val4H)
if not na(hvn4H)
    array.push(lv, hvn4H)
if not na(poc5M)
    array.push(lv, poc5M)
if not na(hvn5M)
    array.push(lv, hvn5M)
float res1 = na
float res2 = na
float sup1 = na
float sup2 = na
if array.size(lv) > 0
    for i = 0 to array.size(lv) - 1
        float v = array.get(lv, i)
        if v > price
            res1 := na(res1) ? v : math.min(res1, v)
        if v < price
            sup1 := na(sup1) ? v : math.max(sup1, v)
    for i = 0 to array.size(lv) - 1
        float v = array.get(lv, i)
        if v > price and (na(res1) or v > res1)
            res2 := na(res2) ? v : math.min(res2, v)
        if v < price and (na(sup1) or v < sup1)
            sup2 := na(sup2) ? v : math.max(sup2, v)

// ---- smart targets ----
float atr = ta.atr(14)
float minDist = math.max(nz(atr, price * 0.003) * atrMult, price * minPct / 100.0)
float mmUnit = (not na(vah1H) and not na(val1H) and vah1H > val1H) ? (vah1H - val1H) : nz(atr, price * 0.005) * 10
float upT1 = f_nextAbove(lv, price, minDist)
float upT2 = na(upT1) ? na : f_nextAbove(lv, upT1, minDist)
float upMM = price + mmUnit
float dnT1 = f_nextBelow(lv, price, minDist)
float dnT2 = na(dnT1) ? na : f_nextBelow(lv, dnT1, minDist)
float dnMM = price - mmUnit
float brUpN = f_nextAbove(lv, na(res1) ? price : res1, minDist)
float brUp  = na(brUpN) ? (na(res1) ? price : res1) + mmUnit : brUpN
float brDnN = f_nextBelow(lv, na(sup1) ? price : sup1, minDist)
float brDn  = na(brDnN) ? (na(sup1) ? price : sup1) - mmUnit : brDnN

// ---- structure read (volume-at-price) ----
bool hUp = not na(hvnUp)
bool hDn = not na(hvnDn)
bool lUp = not na(lvnUp)
bool lDn = not na(lvnDn)
string sread = "—"
if atCode == 0 and hUp and hDn
    sread := "Thin NECK between shelves " + f_fp(hvnDn) + " / " + f_fp(hvnUp) + " (double-dist) — pivot. Expect a move to one shelf; fade a shelf toward the opposite. Middle = transit, not a target."
else if atCode == 2 and lUp and lDn
    sread := "On an acceptance SHELF, thin air both sides (" + f_fp(lvnDn) + " / " + f_fp(lvnUp) + ") — balanced now; fast break once it clears either edge."
else if atCode == 2
    sread := "On acceptance (HVN) — fair value, two-sided chop. Low directional edge; wait for departure."
else if atCode == 0
    sread := "In a thin zone — transitional. Likely picks a shelf: " + (hDn ? f_fp(hvnDn) : "—") + " below / " + (hUp ? f_fp(hvnUp) : "—") + " above."
else if hUp and hDn
    sread := "Between shelves " + f_fp(hvnDn) + " (sup) / " + f_fp(hvnUp) + " (res) — rotate; target the opposite shelf, not the middle."
else if hUp
    sread := "HVN above at " + f_fp(hvnUp) + " — magnet/resistance; pulled up but expect rotation there. Thin support below."
else if hDn
    sread := "HVN below at " + f_fp(hvnDn) + " — support/launchpad." + (lUp ? " Thin above " + f_fp(lvnUp) + " → fast if broken." : "")
else
    sread := (lUp ? "Thin above " + f_fp(lvnUp) + " (fast up if broken). " : "") + (lDn ? "Thin below " + f_fp(lvnDn) + " (trapdoor)." : "No clear shelves nearby.")

// ---- plan ----
float band = (not na(vah1H) and not na(val1H)) ? (vah1H - val1H) * 0.08 : price * 0.002
string bias = ""
string waitFor = ""
string trig = ""
string tgt = ""
string stop = ""
string ifThen = ""
float invalLevel = na
if state == "Uptrend — buy dips"
    bias := "UP — buy pullbacks (above 4H fair value " + f_fp(poc4H) + ")"
    waitFor := na(sup1) ? "pullback to support" : (na(sup2) ? "pullback near " + f_fp(sup1) : "pullback into " + f_fp(math.min(sup1,sup2)) + "–" + f_fp(math.max(sup1,sup2)))
    trig := "bullish reaction / holds"
    tgt := na(upT1) ? "mm " + f_fp(upMM) : f_fp(upT1) + " → " + f_fp(na(upT2) ? upMM : upT2) + "  (mm " + f_fp(upMM) + ")"
    invalLevel := na(sup2) ? sup1 : sup2
    stop := "below " + f_fp(invalLevel)
    ifThen := "IF accept below " + f_fp(invalLevel) + " → flips DOWN; target " + f_fp(val4H)
else if state == "Downtrend — sell rips"
    bias := "DOWN — sell bounces (below 4H fair value " + f_fp(poc4H) + ")"
    waitFor := na(res1) ? "bounce to resistance" : (na(res2) ? "bounce near " + f_fp(res1) : "bounce into " + f_fp(math.min(res1,res2)) + "–" + f_fp(math.max(res1,res2)))
    trig := "rejection"
    tgt := na(dnT1) ? "mm " + f_fp(dnMM) : f_fp(dnT1) + " → " + f_fp(na(dnT2) ? dnMM : dnT2) + "  (mm " + f_fp(dnMM) + ")"
    invalLevel := na(res2) ? res1 : res2
    stop := "above " + f_fp(invalLevel)
    ifThen := "IF accept above " + f_fp(invalLevel) + " → flips UP; target " + f_fp(vah4H)
else
    float midR = (not na(sup1) and not na(res1)) ? (sup1 + res1) / 2 : na
    float fadeT = (not na(poc1H) and not na(sup1) and not na(res1) and poc1H > sup1 and poc1H < res1) ? poc1H : midR
    bias := "RANGE — rotational (no swing bias)"
    waitFor := "edges: long near " + f_fp(sup1) + " · short near " + f_fp(res1) + " (no mid-range trade)"
    trig := "reaction at the edge"
    tgt := "to mid " + f_fp(fadeT)
    invalLevel := na
    stop := "beyond the edge you fade"
    ifThen := "IF accept > " + f_fp(res1) + " → up-break (→ " + f_fp(brUp) + "); < " + f_fp(sup1) + " → down-break (→ " + f_fp(brDn) + ")"

// ---- alerts ----
bool inZone = false
if state == "Uptrend — buy dips"
    inZone := f_near(sup1, band) or f_near(sup2, band)
else if state == "Downtrend — sell rips"
    inZone := f_near(res1, band) or f_near(res2, band)
else
    inZone := f_near(sup1, band) or f_near(res1, band)
bool zoneEnter = inZone and not inZone[1]
bool stChanged = state != state[1]
bool invalHit = not na(invalLevel) and ta.cross(close, invalLevel)
alertcondition(zoneEnter, "Entry zone reached", "MTF Plan: price reached the entry zone")
alertcondition(stChanged, "Bias change", "MTF Plan: swing bias changed")
alertcondition(invalHit, "Invalidation hit", "MTF Plan: invalidation level touched")

// ---- table ----
var table T = table.new(f_pos(tPos), 2, 10, border_width=1, frame_width=1, frame_color=color.new(color.gray,40))
if barstate.islast
    color biasC = state == "Uptrend — buy dips" ? color.lime : state == "Downtrend — sell rips" ? color.red : color.silver
    string ctx = na(pocD) ? "—" : (price > pocD ? "above Daily POC " + f_fp(pocD) : "below Daily POC " + f_fp(pocD))
    table.cell(T,0,0,"BIAS",      text_color=color.white,  bgcolor=cHd, text_size=size.small, text_halign=text.align_left)
    table.cell(T,1,0,bias,        text_color=biasC,        bgcolor=cHd, text_size=size.small, text_halign=text.align_left)
    table.cell(T,0,1,"STRUCTURE", text_color=color.white,  bgcolor=cBg, text_size=size.small, text_halign=text.align_left)
    table.cell(T,1,1,sread,       text_color=color.aqua,   bgcolor=cBg, text_size=size.small, text_halign=text.align_left)
    table.cell(T,0,2,"WAIT FOR",  text_color=color.white,  bgcolor=cBg, text_size=size.small, text_halign=text.align_left)
    table.cell(T,1,2,waitFor,     text_color=color.yellow, bgcolor=cBg, text_size=size.small, text_halign=text.align_left)
    table.cell(T,0,3,"trigger",   text_color=color.gray,   bgcolor=cBg, text_size=size.tiny, text_halign=text.align_left)
    table.cell(T,1,3,trig,        text_color=color.silver, bgcolor=cBg, text_size=size.tiny, text_halign=text.align_left)
    table.cell(T,0,4,"target",    text_color=color.gray,   bgcolor=cBg, text_size=size.small, text_halign=text.align_left)
    table.cell(T,1,4,tgt,         text_color=color.aqua,   bgcolor=cBg, text_size=size.small, text_halign=text.align_left)
    table.cell(T,0,5,"stop",      text_color=color.gray,   bgcolor=cBg, text_size=size.tiny, text_halign=text.align_left)
    table.cell(T,1,5,stop,        text_color=color.orange, bgcolor=cBg, text_size=size.tiny, text_halign=text.align_left)
    table.cell(T,0,6,"IF / THEN", text_color=color.white,  bgcolor=cBg, text_size=size.small, text_halign=text.align_left)
    table.cell(T,1,6,ifThen,      text_color=color.fuchsia,bgcolor=cBg, text_size=size.small, text_halign=text.align_left)
    table.cell(T,0,7,"value mig", text_color=color.gray,   bgcolor=cBg, text_size=size.tiny, text_halign=text.align_left)
    table.cell(T,1,7,migDir + " · struct " + struc, text_color=color.silver, bgcolor=cBg, text_size=size.tiny, text_halign=text.align_left)
    table.cell(T,0,8,"held",      text_color=color.gray,   bgcolor=cBg, text_size=size.tiny, text_halign=text.align_left)
    table.cell(T,1,8,str.tostring(bar_index - stateBar) + " bars", text_color=color.silver, bgcolor=cBg, text_size=size.tiny, text_halign=text.align_left)
    table.cell(T,0,9,"context",   text_color=color.gray,   bgcolor=cBg, text_size=size.tiny, text_halign=text.align_left)
    table.cell(T,1,9,ctx,         text_color=color.silver, bgcolor=cBg, text_size=size.tiny, text_halign=text.align_left)
```

---

### Using them
- Add **A**, confirm it loads clean, then add **B**. B recomputes its own D/4H/1H/5m, so it runs standalone too.
- **Crypto:** leave B's *Bars per period* at 288 (24h on 5m); multi-exchange optional (point at an aggregated ticker). **Stocks:** set it to ~78 (RTH day on 5m).
- POC migration needs a few days of chart history to fill — it shows "building…" until then.
- ⚠️ Per the engine findings: if any earlier copy of A had a ★ "high-conviction" (HTF-POC) tag, that edge did **not** replicate on larger data — treat it as cosmetic. These versions don't include it.
