import { useState } from "react";

// ═══════════════════════════════════════════════════════════════════════════
// M5 — THE LEVEL MAP LOOKUP (2026-07-08)
// Design law: this tool DISPLAYS banked, audited cells. It never synthesizes
// a combined probability that was not measured. Every line: value · n · tier
// · source doc. Tiers: [CAL] calibrated (4×-reproduced) · [CAL-S] stability-
// certified (E gates) · [P] possibility-grade · [FULL] descriptive census.
// Standing audit: any number → "show the date list" → csv + drawn charts.
// ═══════════════════════════════════════════════════════════════════════════

const S={bg:"#101418",card:"#161C22",line:"#2A323B",txt:"#C9D4DE",dim:"#7C8894",hot:"#E8EDF2",g:"#4FB477",a:"#C9A227",r:"#C0504E",b:"#6FA8D6",p:"#9C6FD6"};
const TIER={CAL:S.g,"CAL-S":S.b,P:S.a,FULL:S.dim,PEND:S.r};

const TABLE={ // CALIBRATED_TABLE_v2 — FULL | cert | Bull/Bear/Chop | wkday/wkend
 "rev|few":{f:39.3,c:"31.5→28.5",B:39.1,Be:23.7,Ch:null,wd:33.2,we:51.0},
 "rev|mid":{f:40.4,c:"39.3→40.4",B:35.7,Be:36.3,Ch:45.1,wd:37.5,we:44.6},
 "rev|many":{f:47.1,c:"47.3→45.6",B:52.6,Be:34.1,Ch:47.0,wd:45.2,we:49.9},
 "slow|few":{f:35.0,c:"34.7→35.1",B:45.8,Be:22.0,Ch:null,wd:35.4,we:34.0},
 "slow|mid":{f:39.4,c:"40.5→43.2",B:36.3,Be:41.1,Ch:40.3,wd:39.8,we:38.6},
 "slow|many":{f:46.4,c:"46.3→35.5⚑",B:46.0,Be:38.5,Ch:46.7,wd:44.0,we:51.8},
 "fast|few":{f:27.9,c:"19.7→21.9",B:28.1,Be:21.4,Ch:null,wd:25.1,we:39.5},
 "fast|mid":{f:30.9,c:"31.7→31.9",B:29.0,Be:29.3,Ch:28.9,wd:29.4,we:37.3},
 "fast|many":{f:40.2,c:"41.6→37.0",B:42.1,Be:31.6,Ch:48.3,wd:40.1,we:40.7}};
const TRIPLES={"slow|calm|many":{v:51.8,n:228},"fast|driven|few":{v:27.3,n:231},
 "few|Bear|driven":{v:18.1,n:204},"few|Bear|fast":{v:21.2,n:118}};
const GRAV=[["touched today",56.4],["missed ≤0.03U",42.8],["~0.26U away",32.2],["~0.46U",22.2],["~1.1U",9.8],[">3U","~0"]];
const LEGS=[["≤0.07U",96],["0.11U",91],["0.16U",83],["0.23U",70],["0.36U",53],["0.87U",22]];
const KNOCK={"1":40,"2-4":37,"5+":32};

const Chip=({on,onClick,children,c})=>(<button onClick={onClick} style={{background:on?(c||S.line):"transparent",color:on?S.hot:S.dim,border:`1px solid ${S.line}`,borderRadius:6,padding:"5px 9px",margin:2,fontSize:12,fontFamily:"inherit",cursor:"pointer"}}>{children}</button>);
const Line=({label,val,tier,n,src,warn})=>(
 <div style={{display:"flex",alignItems:"baseline",gap:6,padding:"4px 0",borderBottom:`1px solid ${S.line}22`,fontSize:13}}>
   <span style={{color:warn?S.r:S.txt,flex:1}}>{label}</span>
   <span style={{color:S.hot,fontWeight:700}}>{val}</span>
   {n&&<span style={{color:S.dim,fontSize:10}}>n={n}</span>}
   <span style={{fontSize:9,padding:"1px 5px",borderRadius:3,background:"#0008",color:TIER[tier]||S.dim,border:`1px solid ${TIER[tier]||S.dim}55`}}>{tier}</span>
   <span style={{color:S.dim,fontSize:9}}>{src}</span>
 </div>);
const Card=({title,children})=>(<div style={{background:S.card,border:`1px solid ${S.line}`,borderRadius:10,padding:12,marginBottom:12}}>
 <div style={{fontSize:13,fontWeight:700,color:S.hot,marginBottom:6}}>{title}</div>{children}</div>);

export default function Lookup(){
 const[thr,setThr]=useState("slow");const[drv,setDrv]=useState("mid");const[am,setAm]=useState("many");
 const[side,setSide]=useState("below");const[hy,setHy]=useState("Bull");const[i4,setI4]=useState("agree");
 const[wk,setWk]=useState("wkday");const[yd,setYd]=useState("churn");const[kn,setKn]=useState("1");
 const[casc,setCasc]=useState("none");const[dt,setDt]=useState("normal");const[div,setDiv]=useState(0);const[rsi,setRsi]=useState("mid");
 const cell=TABLE[`${thr}|${am}`];
 const regv=hy==="Bull"?cell.B:hy==="Bear"?cell.Be:cell.Ch;
 const trip=TRIPLES[`${thr}|${drv}|${am}`]||TRIPLES[`${am}|${hy}|${drv==="driven"?"driven":thr}`];
 const bearTrip=(am==="few"&&hy==="Bear")?(drv==="driven"?TRIPLES["few|Bear|driven"]:thr==="fast"?TRIPLES["few|Bear|fast"]:null):null;
 return(
 <div style={{background:S.bg,minHeight:"100vh",padding:14,fontFamily:"ui-monospace,Menlo,monospace",color:S.txt}}>
  <div style={{fontSize:10,letterSpacing:2,color:S.dim}}>LEVEL MAP · M5 LOOKUP · EVERY NUMBER BANKED · NOTHING SYNTHESIZED</div>
  <div style={{fontSize:19,fontWeight:700,color:S.hot,margin:"4px 0 10px"}}>Situation in → banked odds out</div>

  <Card title="YOUR SITUATION (tap it in)">
   <div style={{fontSize:11,color:S.dim}}>30-min thrust</div>
   {["rev","slow","fast"].map(x=><Chip key={x} on={thr===x} onClick={()=>setThr(x)}>{x}</Chip>)}
   <div style={{fontSize:11,color:S.dim,marginTop:4}}>24h drive</div>
   {["calm","mid","driven"].map(x=><Chip key={x} on={drv===x} onClick={()=>setDrv(x)}>{x}</Chip>)}
   <div style={{fontSize:11,color:S.dim,marginTop:4}}>area last 20d</div>
   {["few","mid","many"].map(x=><Chip key={x} on={am===x} onClick={()=>setAm(x)}>{x==="few"?"fresh":x==="many"?"worn":"mid"}</Chip>)}
   <div style={{fontSize:11,color:S.dim,marginTop:4}}>approach · regime · intraday-4H · day</div>
   {["below","above"].map(x=><Chip key={x} on={side===x} onClick={()=>setSide(x)}>from {x}</Chip>)}
   {["Bull","Bear","Chop"].map(x=><Chip key={x} on={hy===x} onClick={()=>setHy(x)}>{x}</Chip>)}
   {["agree","flipped"].map(x=><Chip key={x} on={i4===x} onClick={()=>setI4(x)}>4H {x}</Chip>)}
   {["wkday","wkend"].map(x=><Chip key={x} on={wk===x} onClick={()=>setWk(x)}>{x}</Chip>)}
   <div style={{fontSize:11,color:S.dim,marginTop:4}}>brief day-type call</div>
   {["normal","EXPANSION","QUIET"].map(x=><Chip key={x} on={dt===x} onClick={()=>setDt(x)} c={x==="EXPANSION"?S.a+"44":x==="QUIET"?S.b+"44":undefined}>{x}</Chip>)}
   <div style={{fontSize:11,color:S.dim,marginTop:4}}>yesterday was · knocks so far · constellation · div-forming</div>
   {["churn","lean","parked","trend"].map(x=><Chip key={x} on={yd===x} onClick={()=>setYd(x)}>{x}</Chip>)}
   {Object.keys(KNOCK).map(x=><Chip key={x} on={kn===x} onClick={()=>setKn(x)}>{x} knocks</Chip>)}
   <div/>
   {[["none","no constellation state"],["pocdn","POC-stack ↓ (below PSPOC, crossed-dn, stale)"],["pocup","POC-stack ↑"],["mldn","monthly-low ↓ cascade"],["wcsupp","parked above PWC (suppressor)"]].map(([k,l])=><Chip key={k} on={casc===k} onClick={()=>setCasc(k)} c={S.p+"44"}>{l}</Chip>)}
   <div/>
   {[[0,"no div"],[1,"bull div forming"],[2,"bear div forming"]].map(([k,l])=><Chip key={k} on={div===k} onClick={()=>setDiv(k)}>{l}</Chip>)}
   {["lo","mid","hi"].map(x=><Chip key={x} on={rsi===x} onClick={()=>setRsi(x)}>RSI {x}</Chip>)}
  </Card>

  <Card title="IN THE BAND (0.30–0.60U past the edge) — P(continue through)">
   <Line label={`certified cell: ${thr} × ${am==="few"?"fresh":am==="many"?"worn":"mid"} — FULL history`} val={cell.f+"%"} tier="CAL" src="A-81/tbl_v2"/>
   <Line label="frozen check beside (H1→H2)" val={cell.c} tier="CAL" src="A-81"/>
   <Line label={`in ${hy}`} val={regv==null?"thin cell — don't read":regv+"%"} tier="CAL" src="tbl_v2" warn={hy==="Bear"}/>
   <Line label={wk+(wk==="wkend"?" (thrust read inverts)":"")} val={(wk==="wkday"?cell.wd:cell.we)+"%"} tier="CAL" src="tbl_v2"/>
   {TRIPLES[`${thr}|${drv}|${am}`]&&<Line label={`measured triple ${thr}×${drv}×${am}`} val={TRIPLES[`${thr}|${drv}|${am}`].v+"%"} n={TRIPLES[`${thr}|${drv}|${am}`].n} tier="P" src="D-lattice"/>}
   {bearTrip&&<Line label="deep fade corner (fresh×Bear stacked)" val={bearTrip.v+"%"} n={bearTrip.n} tier="P" src="D-lattice"/>}
   {yd==="trend"&&<Line label="after a TREND day, contested touches die" val="−7.3pp" tier="P" src="D/E: era-fragile"/>}
   <div style={{fontSize:10,color:S.dim,marginTop:4}}>Lines shown side-by-side by design — measured cells only, never multiplied.</div>
  </Card>

  {dt==="EXPANSION"&&<Card title="DAY-TYPE [TRI]"><Line label="EXPANSION forecast: walls give way" val="63.6%" n={2668} tier="CAL-S" src="INT-II triangle"/><Line label="…with fast thrust" val="70.2%" n={943} tier="P" src="4/4 E✓"/><Line label="note: fade corners weaken today; weekend suppressor largely overridden" val="" tier="P" src="audit"/></Card>}
  {dt==="QUIET"&&<Card title="DAY-TYPE [TRI]"><Line label="QUIET forecast: walls hold" val="69.2%" n={4150} tier="CAL-S" src="INT-II"/><Line label="…on a weekend" val="84.2% hold" n={1118} tier="P" src="4/4 E✓"/><Line label="small dials matter MORE today (vote spread 20 vs 14)" val="" tier="FULL" src="audit"/></Card>}
  <Card title="BREAK READ — P(ends through, pen>0.6U); base 42.4%">
   {yd==="trend"&&thr==="fast"&&<Line label="★ fast thrust × after-trend" val="56.1%" n={770} tier="CAL-S" src="E: +14.0→+13.1, 4/4"/>}
   {wk==="wkend"&&<Line label="weekend suppressor" val="35.6%" n={12392} tier="CAL-S" src="E: −8.0→−6.1, regime-uniform"/>}
   {casc==="pocdn"&&<Line label="POC cascade ↓: daily POC from above" val="62.4%" n={85} tier="P" src="M2 grid, 4/4 E✓"/>}
   {casc==="pocup"&&<Line label="POC cascade ↑: daily POC from below" val="62.0%" n={108} tier="P" src="M2, 4/4 E✓"/>}
   {casc==="mldn"&&<Line label="monthly-low cascade: PDL/ONL from above" val="60%" n={"105/108"} tier="P" src="M2, 4/4 E✓ · dial-robust (M2b)"/>}
   {casc==="wcsupp"&&<Line label="parked-above-PWC: upside session breaks REFUSE" val="24–25%" n={"136/107"} tier="P" src="M2, 4/4 E✓ · dial-robust"/>}
   {casc==="pocdn"&&div===1&&<Line label="…but bull-div forming brakes the cascade" val="50.0%" n={26} tier="P" src="M4 combo — tiny n, flag" warn/>}
   {i4==="flipped"&&hy==="Bear"&&side==="below"&&<Line label="intraday 4H freshly flipped Bull, upside touch" val="48.8%" n={324} tier="P" src="M4: 4/4 E✓"/>}
   <Line label={`knock count today: ${kn}`} val={KNOCK[kn]+"% ends-through"} tier="FULL" src="C3 ruler-invariant · hammering = fade-lean"/>
   {rsi==="lo"&&side==="above"&&<Line label="oversold 4H RSI, downside approach" val="+4.0pp" tier="P" src="M4 sweep"/>}
   {div>0&&casc!=="pocdn"&&<Line label="divergence standalone" val="±1pp — carries nothing alone" tier="FULL" src="M4: your combo-only doctrine confirmed"/>}
  </Card>

  <Card title="TARGET & TRAVEL — distance is the law">
   {LEGS.map(([g,p])=><Line key={g} label={`next zone ${g} away`} val={p+"% reached"} tier="FULL" src="C4 ±0.5pp all regimes"/>)}
   <div style={{fontSize:10,color:S.dim}}>Rejections travel 0.5–1.1U back · breaks carry ~0.5–0.7U on · far crossings that fail die 25% of the way · re-touch of origin is base case past ~0.5U · no mid-flight pull (null, swept).</div>
  </Card>

  <Card title="ZONES-IN-PLAY TOMORROW (contact — the forecastable layer)">
   {GRAV.map(([g,p])=><Line key={g} label={g} val={p+"%"} tier="FULL" src="C1 gravity"/>)}
   <div style={{fontSize:10,color:S.dim}}>Boosters: hover ~4× at any radius [FULL C2] · stepping POC 76–82% [B re-adj] · PW life 46→13%, PM 36→9% [C6] · weekends stickier +5–12 [FULL] · contact is regime-neutral [D].</div>
  </Card>

  <div style={{background:S.card,border:`1px solid ${S.r}`,borderRadius:10,padding:12}}>
   <div style={{fontSize:12,fontWeight:700,color:S.r}}>THE LAWS OF THIS TOOL</div>
   <div style={{fontSize:11,color:S.txt,marginTop:4}}>
   Reactions are memoryless — read the arrival, never the zone's biography (C3·C6·P4, three-times proven). Contact is where forecast lives. Direction before the approach forms ≈ coin flip. Nothing here is autopilot: the complete battery (186,208 trades, all cells × both directions × 5 triggers) passed 0 of ~100 arms — the map is eyes; Option B v1.2 remains the only money system. Constellation cells and combos are possibility-tier until gated. Any number on this card converts to a date list + drawn charts on demand ("show the date list for X"). Forward register judges everything.
   </div>
  </div>
 </div>);
}
