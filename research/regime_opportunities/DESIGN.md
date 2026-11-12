# Market regimes before entry signals

Frozen12November2026 before new regime outcome calculations. No earlier study is
modified. Dates already researched remain contaminated. Index-only2016–2026 data
permit multi-cycle tests; stock/portfolio inference is restricted to the dated
2024cohort from11Nov2024–9Nov2026. Historical sector/breadth/removed-stock data are
not invented. Earlier2024-selected stock prices are warmup, not long-cycle proof.

Three different questions have separate tables/tests:
1. Known market state predicts subsequent NIFTY50/500 TRI return.
2. State predicts equal-stock economic returns, breadth of positive stock outcomes,
   or stock-average return minus NIFTY TRI. Aggregate at signal date for inference;
   companies on one date are not independent market events.
3. State improves a fixed entry mechanism under a real limited-cash portfolio,
   compared with the same universal mechanism and opportunity-matched random entry.

Regime axes are independent overlapping labels, never a Cartesian intersection
search. Numeric reference thresholds are fixed, not optimized. Vol20/vol60 uses
sample std of completed NIFTY simple returns: expansion>1.2, contraction<.8.
High/low vol20 uses prior252session median. ADX14Wilder>=25strong,<20weak.
Trend bull is close>EMA200 and EMA50>EMA200; bear both below; mixed otherwise.
Efficiency60=abs(close-close60ago)/sum(abs dailychange60): high>=.3,low<=.15.
Breadth20/50/200=eligible observed companies above their SMA-seeded EMA: broad>=.7,
narrow<=.3, require>=80%validcoverage. Breadth50change20sessions>=.10improving,
<=-.10deteriorating. Sectorrotation proxy uses Bank/IT/Pharma officialTRI:
60returnspread>its prior252median, or leadingsector differs from20sessions ago.
Momentum persistence20positive-dayfraction>=.65up,<=.35down.
Market meanreversion z=(NIFTYclose-EMA20)/ATR14: oversold<=-2,overbought>=2.
Cross-sectional daily stockreturnstd averaged20sessions above/below its prior252
median labels high/lowdispersion. Median60stock/NIFTYreturncorrelation above/below
its prior252median labels high/lowcorrelation. Expansion transition firston-day;
persistent expansion age>=5observed sessions. Squared-returnlag1autocorrelation60
>0clustered,<=0unclustered. NIFTYabs(open/priorclose-1)>1%frequency20>=.2highgaps,
<.2lowgaps. Median stock(currentvolume/meanprior20volume)>=1.25highparticipation,
<=.75lowparticipation. All features known after current completed close. Unknown
features produce unavailable labels, never default low/bear. No thresholds are
selected from final evaluation.

Index chronology:2017–2020development (2016warmup),2021–2022validation,
2023–9Nov2024transfer, then old2024–2026diagnostic. Stock chronology remains
development11Nov2024–9Nov2025,validation10Nov2025–9May2026,final10May–9Nov2026.
Forward horizons5/10/20observed sessions. Close-to-close indexTRI and stockeconomic
returns are opportunity diagnostics, not executable P&L. Primary nonoverlapping
dates use a fixed global20session grid, same grid for all regimes. Secondary
all-date contrasts use shared20session calendar blocks3000draws; horizons/windows
overlap and are not called independent. Correct BH across regime/endpoint tests
within each chronology; simultaneous calendar-resampling preserves stock co-moves.
Regime event counts/durations/maxrun and pooled events separated by>=20off-sessions
are reported; a low episode count vetoes robust claims regardless of trade counts.

Six fixed portfolio entry/holding models, without an RS eligibility filter:
- buyhold10: unconditional eligible opportunity, hold10sessions without protective
  target/stop; ATR-based quantity/cashcaps retained. It is a holding benchmark,
  not the same realized loss cap as protective strategies. Fixed full-period
  stockbuyhold and publishedTRI controls also reported separately.
- momentum: close crosses above the prior20sessionhigh(excluding current candle).
- meanreversion: first completed RSI14cross below30.
- EMA:20/50bullish cross.
- MACD:12/26/9bullish signal-line cross.
- support: rejection of latest strict2left/2rightconfirmed pivotlow within.5ATR,
  bullishcandle and lowerwick>=25%range; pivot released only after rightbars.
The five protective strategies share2ATR stop, fee-aware2R target,10sessioncap.
Common fundedRs1m,0.5%plannedstoprisk,20%name/30%sectorcaps,10positions,
1%prior20medianvolume,Rs5croreprior20medianturnover,correlation>.8past60reject,
5bpsfills,corrected same-daytax/dividends. Nointerest/leverage. Candidate priority
is a fixed deterministic hash of date+historicalISIN, removing the earlier momentum
ranking confound. Same ranking for every entry/control. Dividend ex-datecash,
historical volume units and gap/stopfirst assumptions remain explicit limitations.
Doublefees/10bps is prespecified stress for frozen training-only shortlists.

For every protective strategy/state,64commonseeds match the actual completed-day
raw opportunity count without replacement from the same eligible pool, same gate,
same ranking and funded constraints. Actual fills/holding/exposure may differ;
do not force matches using future exits. Buyhold10's all-pool entry has a degenerate
randomnull (same entire eligible set), reported explicitly rather than100fake
independent draws. No seedselected. Preserve all summary and compact paths/journals.

Before validation portfolio outcomes are read, select up to3regimes solely from
development stock10session forward-return contrast, requiring>=20on-dates and
>=3pooledevents (20offsessionseparation). Choose at most one protective entry per
such regime using development account return minus randommean, positive netreturn,
>=20trades and DD<=15%. If none qualify, retain rejected diagnostic representatives
and do not label them promising. Freeze exact choices/reasons; then evaluate
validation/final/fullpaths. Shortlists receive up to1000commonseedcontrols and
coststress, without new threshold/entry selection. All other comparison rows are
descriptive multi-test diagnostics, not freshly selected OOS strategies.

The original2024cohort has future-completeness selection and cannot certify all
historical constituents. Multi-cycle index findings cannot be automatically
transferred to stock-level/portfolio edges. Robust requires positive reservedtime
netrandom/benchmarkadvantage with adjusted uncertainty and enough independent
events, not merely positive full-period return. No deployment/paperworker changes.
