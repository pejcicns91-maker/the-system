# LEDGER — sequenced stop x target from episode grain — 2026-07-29 17:01:10.995096+00:00
cells (incl. ALL4/ALL rollups): 6,240 · file sorted n_dec descending · no floors, no pruning
recon BTC ATRp fade: outcomes 594,684 == eligible x geoms 594,684 PASS · na 4,968
recon BTC ATRp rt: outcomes 519,912 == eligible x geoms 519,912 PASS · na 4,464
recon BTC STRUCT fade: outcomes 258,720 == eligible x geoms 258,720 PASS · na 7,792
recon BTC STRUCT rt: outcomes 226,624 == eligible x geoms 226,624 PASS · na 6,432
recon ETH ATRp fade: outcomes 589,068 == eligible x geoms 589,068 PASS · na 5,184
recon ETH ATRp rt: outcomes 511,704 == eligible x geoms 511,704 PASS · na 4,428
recon ETH STRUCT fade: outcomes 255,904 == eligible x geoms 255,904 PASS · na 8,208
recon ETH STRUCT rt: outcomes 222,800 == eligible x geoms 222,800 PASS · na 6,592
recon SOL ATRp fade: outcomes 580,500 == eligible x geoms 580,500 PASS · na 4,212
recon SOL ATRp rt: outcomes 514,152 == eligible x geoms 514,152 PASS · na 3,852
recon SOL STRUCT fade: outcomes 253,008 == eligible x geoms 253,008 PASS · na 6,864
recon SOL STRUCT rt: outcomes 224,592 == eligible x geoms 224,592 PASS · na 5,632
recon XRP ATRp fade: outcomes 580,104 == eligible x geoms 580,104 PASS · na 4,428
recon XRP ATRp rt: outcomes 511,236 == eligible x geoms 511,236 PASS · na 4,068
recon XRP STRUCT fade: outcomes 254,208 == eligible x geoms 254,208 PASS · na 5,584
recon XRP STRUCT rt: outcomes 224,432 == eligible x geoms 224,432 PASS · na 4,592

## whole-population grid — fade · ATR-prior ruler (ALL4 x ALL families)
p_win_dec:
tgt_k    0.25   0.50   0.75   1.00   1.50   2.00
stop_k                                          
0.10    0.285  0.148  0.088  0.052  0.020  0.008
0.20    0.428  0.246  0.149  0.089  0.034  0.013
0.30    0.529  0.327  0.208  0.127  0.050  0.020
0.50    0.667  0.466  0.317  0.205  0.083  0.034
0.75    0.787  0.616  0.460  0.319  0.141  0.060
1.00    0.864  0.734  0.593  0.444  0.217  0.098
EV_R @13.5bp:
tgt_k    0.25   0.50   0.75   1.00   1.50   2.00
stop_k                                          
0.10   -0.279 -0.389 -0.533 -0.712 -0.966 -1.118
0.20   -0.176 -0.281 -0.432 -0.608 -0.853 -1.001
0.30   -0.124 -0.222 -0.367 -0.543 -0.798 -0.943
0.50   -0.057 -0.125 -0.265 -0.444 -0.728 -0.890
0.75    0.011 -0.012 -0.120 -0.296 -0.617 -0.819
1.00    0.051  0.071  0.007 -0.143 -0.487 -0.737
EV_R @4.5bp:
tgt_k    0.25   0.50   0.75   1.00   1.50   2.00
stop_k                                          
0.10   -0.094 -0.203 -0.347 -0.526 -0.780 -0.932
0.20   -0.083 -0.187 -0.338 -0.514 -0.759 -0.907
0.30   -0.062 -0.159 -0.303 -0.480 -0.735 -0.880
0.50   -0.019 -0.087 -0.226 -0.405 -0.689 -0.851
0.75    0.037  0.014 -0.094 -0.269 -0.590 -0.793
1.00    0.070  0.091  0.027 -0.123 -0.466 -0.717
ambiguous n (same-bar incl. entry-bar rule):
tgt_k   0.25  0.50  0.75  1.00  1.50  2.00
stop_k                                    
0.10    4704  4128  4050  4032  4015  4013
0.20    2287  1520  1382  1354  1329  1325
0.30    1719   856   695   653   622   615
0.50    1490   517   339   281   240   231
0.75    1405   409   220   160   114   104
1.00    1386   373   173   109    58    48

## whole-population grid — fade · STRUCTURAL ruler (corridor)
EV_R gross (before toll):
tgt_k    0.25   0.50   0.75   1.00
stop_k                            
0.25    0.605  1.045  1.070  0.980
0.50    0.215  0.423  0.445  0.435
0.75    0.114  0.257  0.281  0.273
1.00    0.064  0.179  0.202  0.191
EV_R @13.5bp:
tgt_k    0.25   0.50   0.75   1.00
stop_k                            
0.25   -1.262 -0.789 -0.676 -0.681
0.50   -0.759 -0.561 -0.506 -0.483
0.75   -0.582 -0.454 -0.410 -0.397
1.00   -0.528 -0.403 -0.368 -0.364
mean stop in ATR-prior units (cross-ruler line):
tgt_k    0.25   0.50   0.75   1.00
stop_k                            
0.25    0.073  0.090  0.094  0.095
0.50    0.114  0.144  0.152  0.153
0.75    0.149  0.192  0.203  0.206
1.00    0.184  0.240  0.253  0.257

## whole-population grid — rt · ATR-prior ruler (ALL4 x ALL families)
p_win_dec:
tgt_k    0.25   0.50   0.75   1.00   1.50   2.00
stop_k                                          
0.10    0.307  0.170  0.099  0.059  0.026  0.012
0.20    0.460  0.280  0.171  0.103  0.047  0.021
0.30    0.569  0.371  0.238  0.149  0.068  0.029
0.50    0.715  0.527  0.372  0.250  0.121  0.055
0.75    0.826  0.681  0.532  0.391  0.210  0.101
1.00    0.898  0.798  0.679  0.545  0.332  0.176
EV_R @13.5bp:
tgt_k    0.25   0.50   0.75   1.00   1.50   2.00
stop_k                                          
0.10   -0.203 -0.259 -0.436 -0.636 -0.864 -1.034
0.20   -0.105 -0.161 -0.329 -0.523 -0.744 -0.913
0.30   -0.051 -0.105 -0.264 -0.449 -0.686 -0.869
0.50    0.015 -0.003 -0.130 -0.309 -0.575 -0.786
0.75    0.063  0.097  0.024 -0.127 -0.409 -0.668
1.00    0.094  0.169  0.159  0.059 -0.202 -0.503
EV_R @4.5bp:
tgt_k    0.25   0.50   0.75   1.00   1.50   2.00
stop_k                                          
0.10   -0.017 -0.072 -0.249 -0.448 -0.677 -0.847
0.20   -0.011 -0.067 -0.235 -0.428 -0.649 -0.818
0.30    0.012 -0.042 -0.200 -0.385 -0.623 -0.806
0.50    0.053  0.036 -0.091 -0.270 -0.536 -0.747
0.75    0.088  0.123  0.051 -0.100 -0.383 -0.641
1.00    0.113  0.188  0.178  0.079 -0.181 -0.482
ambiguous n (same-bar incl. entry-bar rule):
tgt_k   0.25  0.50  0.75  1.00  1.50  2.00
stop_k                                    
0.10    1995  1748  1714  1707  1707  1706
0.20     662   375   330   323   321   320
0.30     496   171   126   117   113   112
0.50     432    90    45    36    33    31
0.75     409    72    30    21    16    13
1.00     406    69    27    18    12     9

## whole-population grid — rt · STRUCTURAL ruler (corridor)
EV_R gross (before toll):
tgt_k    0.25   0.50   0.75   1.00
stop_k                            
0.25    0.929  1.367  1.641  1.819
0.50    0.305  0.521  0.631  0.683
0.75    0.139  0.285  0.346  0.385
1.00    0.074  0.186  0.220  0.264
EV_R @13.5bp:
tgt_k    0.25   0.50   0.75   1.00
stop_k                            
0.25   -0.660 -0.433 -0.170 -0.048
0.50   -0.598 -0.481 -0.378 -0.359
0.75   -0.540 -0.462 -0.401 -0.381
1.00   -0.481 -0.420 -0.388 -0.358
mean stop in ATR-prior units (cross-ruler line):
tgt_k    0.25   0.50   0.75   1.00
stop_k                            
0.25    0.040  0.037  0.036  0.036
0.50    0.069  0.064  0.063  0.063
0.75    0.094  0.089  0.087  0.087
1.00    0.118  0.112  0.110  0.110

## cost-clearing scan (pooled cells, incl. family cells)
cells EV>0 @13.5bp: 139 (of 1248) · with 4/4 coin agreement: 92
cells EV>0 @4.5bp:  388 · with 4/4 coin agreement: 168
page-one of the 4/4-consistent cost-clearing cells (by n_dec):
family       side basis ruler  stop_k  tgt_k  n_dec  n_amb  n_nei  p_win_dec  ev_R_gross  ev_R_135bp  ev_R_45bp  agree4_135
   ALL from_above  fade  ATRp    1.00   0.25  23406   1386  12208   0.863667    0.079584    0.050988   0.070052           4
   ALL from_above    rt  ATRp    0.75   0.25  22206    409   9907   0.825768    0.101024    0.063097   0.088382           4
   ALL from_above    rt  ATRp    1.00   0.25  20629    406  11487   0.897717    0.122146    0.093715   0.112669           4
   ALL from_below  fade  ATRp    1.00   0.25  17889    989   9243   0.865895    0.082369    0.053160   0.072633           4
   ALL from_below    rt  ATRp    0.75   0.25  15903    334   8380   0.813243    0.084324    0.045433   0.071360           4
   ALL from_above  fade  ATRp    1.00   0.50  15070    373  21557   0.733776    0.100664    0.071195   0.090841           4
   ALL from_above    rt  ATRp    0.75   0.50  15031     72  17419   0.681325    0.135542    0.096822   0.122636           4
   ALL from_below    rt  ATRp    1.00   0.25  14735    327   9555   0.884832    0.106040    0.076872   0.096317           4
   ALL from_above    rt  ATRp    1.00   0.50  12984     69  19469   0.798444    0.197666    0.168605   0.187979           4
   ALL from_below  fade  ATRp    1.00   0.50  11557    176  16388   0.740071    0.110106    0.080065   0.100093           4
   ALL from_below    rt  ATRp    0.75   0.50  10722     91  13804   0.665734    0.109557    0.069629   0.096247           4
   ALL from_below    rt  ATRp    1.00   0.50   9231     80  15306   0.779656    0.169483    0.139451   0.159473           4
    ON from_above  fade  ATRp    0.75   0.25   8860    252   3271   0.787020    0.049360    0.011379   0.036700           4
   ALL from_above    rt  ATRp    1.00   0.75   8475     27  24020   0.679056    0.188348    0.158586   0.178427           4
    ON from_above  fade  ATRp    1.00   0.25   8181    246   3956   0.862975    0.078719    0.050210   0.069216           4
cells EV<0 @13.5bp with 4/4 agreement (the consistent do-not corners): 956

largest per-coin cells (n_dec desc):
coin family       side basis ruler  stop_k  tgt_k  n_dec  n_amb  p_win_dec  ev_R_135bp
 SOL    ALL from_above  fade  ATRp     0.2   0.25   8336    345   0.422505   -0.149372
 ETH    ALL from_above  fade  ATRp     0.2   0.25   8257    647   0.423762   -0.188418
 SOL    ALL from_above  fade  ATRp     0.1   0.25   8203    837   0.278069   -0.225180
 BTC    ALL from_above  fade  ATRp     0.2   0.25   8118    605   0.437793   -0.203592
 ETH    ALL from_above  fade  ATRp     0.3   0.25   8089    479   0.522562   -0.137167
 SOL    ALL from_above  fade  ATRp     0.3   0.25   8060    247   0.525682   -0.103316
 ETH    ALL from_above  fade  ATRp     0.1   0.25   7922   1296   0.284650   -0.286137
 SOL    ALL from_above  fade  ATRp     0.1   0.50   7917    759   0.147278   -0.315313
 BTC    ALL from_above  fade  ATRp     0.3   0.25   7916    440   0.537266   -0.141448
 XRP    ALL from_above  fade  ATRp     0.2   0.25   7797    690   0.429396   -0.161532
 BTC    ALL from_above  fade  ATRp     0.1   0.25   7777   1290   0.288415   -0.366748
 SOL    ALL from_above  fade  ATRp     0.2   0.50   7683    241   0.251855   -0.219285
conventions: WIN = favorable >= target strictly before adverse >= stop, off the exc staircases; equal 5m timestamps = AMBIGUOUS (third outcome, counted); ENTRY-BAR RULE: any resolution on the entry bar is same-bar with the entry moment (the touch splits the bar) and is also the third outcome — the touch bar's bounce-side extreme can predate the touch, so scoring it decided would be a within-bar guess; neither by window end = NEITHER; ATRp ruler = PRIOR-day ATR14 (stored atr14_1d includes the current day — lookahead as a stop denominator — so shift(1) derived at query time; record untouched; one-word swap re-runs U or same-day ATR); STRUCT ruler = corridor gaps ex-ante (1.0 = the corridor mark); costs = round-trip toll x price / stop per episode, tolls 13.5bp (historical taker) and 4.5bp (spot-maker ~ 1/3 FTMO), parameters attached; EV in R per decided trade, amb/nei excluded and shown. Verdicts are Svet's.
