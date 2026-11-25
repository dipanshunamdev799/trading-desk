# Frozen candidate definitions

Shared universe/data/risk/selection in RESEARCH_PLAN.md. Return r=close/previous
close−1; RVOL same-clock previous20 exchange sessions (min10). VWAP is cumulative
typicalOHLC×volume proxy. OR=first3complete5m candles09:15..09:30. Positive
last-bar volume/range, valid features and next-open9:35..13:30 required. Reject
missing context or stop distance outside its specified interval. No future
daily extremes or volume in decisions. Score=abs(r)×min(RVOL,10), tie key.
Primary long only; diagnostic shorts mirror signs/highs/lows and reserve1x
cash collateral. Historical broker short eligibility UNVERIFIED.

H1 early ignition:2%<=r<=5%;close>ORhigh×1.0005 and prior3barhigh;
last3barreturn>=0.3%;close>VWAP, distance<=1.5%; close location in latest candle
>=70%;RVOL>=2;NIFTYsame-clockreturn>=−0.25%,stockoutperformance>=1.5pp.
First qualification per stock/day. Entries9:35..11:30.

H2 controlled pullback:running intraday peak dailyreturn2..6%; latestclose
dailyreturn>=1%; drawdown from earlier running peak0.3..1.2%;atleast one
negative body in prior3bars; latestclose>priorbarhigh;close>VWAP;
currentvolume>=1.2×medianprior3volume;RVOL>=1.5;NIFTY>=−0.25%.
Entries09:45..13:30. Recurring qualifications allowed; portfolio no-reentry.

H4 persistent extreme:6..12%dailyreturn;>=3%rise from09:15open; positive
last3barreturn>=0.3%;closebreaksprior3barhigh;close>VWAP,distance<=2%;
drawdownfromrunninghigh<=0.8%;RVOL>=2;NIFTY>=−0.25%.
Entries10:00..13:30. This tests intraday-built strength/persistence, not v1's
first8/10%mover rule. No historical circuit proximity feature is fabricated.

H5 failed-downside-breakout long reversal:priorbarlow<ORlow;priorclose>=ORlow;
latestclose>priorbarhigh;−5%<=dailyreturn<=−0.5%;RVOL>=1.5;
last3barreturn>0;outperformancevsNIFTY>=0. Firsteligiblefrom09:45..13:30.
The mirror diagnostic short is failed upside breakout. These are separate
directional tests, not universally executable short trades.

Exit F:fixed0.5%stop,1%target,60min; no early momentum exit.
Exit S:stop at prior3barlow minus0.1%ofdecisionclose; distance0.3..1.2%;
target2R bounded0.75..2%;90min. After two consecutive completedcloses below
their as-ofVWAP AND negative3barreturn, exit nextopen.
Exit A:initialstop1.5×completedbarATR14 (session-local simple TR mean with
minimum3 completed observations during warmup), distance0.3..1.2%;2%target,120min.
After completedclose>=entry+initialR, activate trailingstop for followingbar
at max(oldstop,completedclose−1.5×as-ofATR14). Never use currentbarhigh to
raise a stop before testing that bar's low. Same momentum-failure exit as S.
All stops/targets anchored actual entry with precommitted distance/fractions.

Nonselectablecontrols:H1-F price-only removes RVOL>=2 but retains RVOL data
availability/ranking;H1-F no-market removes both NIFTYconditions;H1-F peer
confirmation adds >=0.2%mean same-clockreturn from >=3 other same-industry
cohortmembers;H2-S no-failure removes the momentum-failure exit. These are
specific ablations; no general inference that removed inputs are useless.
V1baselines cross8/cross10+RVOL1.5+VWAP,1%stop/1%target/60min,09:30..11:30,
on this SAME independent cohort and2025–26period, with common v2cost/risk.

Invalidate economic hypothesis if netexpectancy/fundedreturns negative or
stress destroys edge; classify sparse/conflicting samples inconclusive.
H3 depth candidate is not simulated until timestamped book observations exist.
It will compare matched price-only,price+volume,andprice+volume+depth features
on identical candidate times, anchored to post-freeze forward data.
