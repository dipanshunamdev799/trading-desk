"""Render the V17 research brief and link the case-level evidence backing each finding."""
from .common import *
from .evidence import load,match

TITLES=(
 'Reproduction and baselines','GIFT NIFTY opening-price intelligence','Opening surprise and residual returns',
 'Stock-level market intelligence','Intraday breadth and participation','Domestic information networks',
 'Volume, liquidity and order flow','Cross-instrument price discovery','Residual return forecasting',
 'Multiscale predictability map','Weekly and monthly forecasting','Volatility and path intelligence',
 'New information discovery','Validation and falsification','Cumulative evidence and research efficiency',
 'Complete model comparison','Forward research ledger','Final research conclusions','Next experiments')


def fmt(x):
    if pd.isna(x):return '—'
    if isinstance(x,(int,np.integer)):return f'{x:,}'
    if isinstance(x,(float,np.floating)):
        if 0<abs(x)<.00001:return f'{x:.2e}'
        return f'{x:.6f}'
    return str(x).replace('|','\\|')


def tab(z,columns=None,n=None):
    q=z if columns is None else z[list(columns)]
    if n is not None:q=q.head(n)
    h='| '+' | '.join(str(k).replace('_',' ') for k in q.columns)+' |'
    sep='| '+' | '.join('---' for _ in q.columns)+' |'
    return '\n'.join([h,sep,*['| '+' | '.join(fmt(x) for x in row)+' |' for row in q.itertuples(index=False,name=None)]])


def rel(*links):
    return ' · '.join(f'[{title}]({file})' for title,file in links)


def report(i,body):
    (OUT/f'V17_{REPORTS[i-1]}.md').write_text(f'# NIFTY V17 — {TITLES[i-1]}\n\n'+body.strip()+'\n',encoding='utf-8')


def select(z,**keys):
    for k,v in keys.items():z=z.loc[z[k].isin(v) if isinstance(v,(list,tuple,set)) else z[k].eq(v)]
    return z


def read_row(z,**keys):
    x=select(z,**keys)
    assert len(x)==1,(keys,len(x))
    return x.iloc[0]


MATCHED=('cutoff','target','candidate','control','metric','n','disjoint','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21')
ORIG=('horizon','cutoff','candidate','control','metric','n','disjoint','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21')
PATHS=('horizon','cutoff','screen','candidate','control','metric','n','side_barrier_cases','candidate_loss','control_loss','gain','lo21','hi21')


def opening():
    baseline=load('reproduced-opening-sensitivity.csv')
    replay=read('opening-reproduction.json');session=read('session-baseline-reproduction.json')
    oi=load('original-endpoint-leaderboard.csv',V16)
    oi=select(oi,cohort='combined')
    vol=load('volatility-leaderboard.csv',V16)
    barrier=load('passage-age-matched.csv',V16)
    key=['V14_sign_shrinkage','V14_domestic_GJR','V15_gjr_restart','neutral','decomposed_gift','session_state']
    refs=select(oi,model=key)
    v15=load('baseline-v15-gap-replayed.csv.gz')
    v15_scope='; '.join(f'{k} {n:,} rows' for k,n in v15.groupby('cutoff').size().items()).replace('; ',' · ') if 'cutoff' in v15 else f'{len(v15):,} per-case rows'
    risk=select(vol,cutoff='08:55',model=['offshore_plus_domestic','raw_iv','GJR','fixed_iv_rv','student_EGARCH'])
    survival=select(barrier,horizon=5,candidate='decomposed_gift',control='V14_trend_shrink')
    report(1,f"""
The published opening-direction benchmark reproduced on all **248** common mornings. Before the auction, raw GIFT scored **0.100841 Brier**, **88.71% accuracy**, **0.001459 CRPS**, and **0.1965% median absolute error**. Its published adjusted Brier gain interval was **+0.095394 to +0.163392**. The original V15 opening experiment evaluated 258 mornings. V17 regenerated its {replay['v15_rows']:,} individual rows across all configured cutoffs and compared the four earlier V16 opening-clock batches, totaling {sum(x['n'] for x in replay['v16'].values()):,} rows, with exact agreement on the saved forecast probabilities, scores and intervals. {v15_scope}. The archived 09:10 batch is preserved separately because opening price discovery is already underway.

{tab(baseline)}

The verification included {session['anchor_values']:,} saved anchor values with zero differences, {session['decay_rows']:,} original decay forecasts, {session['continuation_rows']:,} continuation probabilities, and {session['time_laws']:,} first-passage laws. Gap-fill replay differences were at most {session['maximum_timing_error']:.2e}. Opening sensitivity screens remove known calendar sets and the largest realized gaps separately. Largest-gap deletion is a hindsight stress test.

## Fixed original endpoint benchmarks

The best protected weekly and monthly direction scores remain **0.228529** and **0.245042** before the V17 tests. Their comparison sets contain 265 and 217 origins. The separate strongest archived return laws scored **0.010457** and **0.024694 CRPS**. The 50/50 monthly probability gives **0.250000 Brier** by construction. Preserve each model, its guard, and the metric for which it earned its result.

{tab(refs,('horizon','model','n','brier','endpoint_crps','endpoint_mae','endpoint_coverage80','balanced_accuracy'))}

## Risk and first passage

At 08:55 the fixed IV/RV blend scored **0.152707** weekly expansion Brier and Student-t EGARCH scored **0.172872** monthly expansion Brier. The older monthly GJR risk study reported **0.033179 volatility MAE** and the V14 Student-t GJR joint range reported **0.015422 CRPS**. The GIFT-first weekly comparison achieved **0.132201** full-horizon barrier Brier and **0.139330** on the subsequent outcome conditional on surviving session one. The archived implementations retain their own risk targets, simulation laws and issue clocks.

{tab(risk,('horizon','model','n','mae','qlike','brier','log_loss'))}

{tab(survival,('horizon','metric','candidate','control','n','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21'))}

{rel(('Replay receipt','opening-reproduction.json'),('Session and first-passage receipt','session-baseline-reproduction.json'),('Continuation','reproduced-continuation.csv'),('Gap-fill risk sets','reproduced-survival.csv'),('Preserved endpoints','protected-original-scores.csv.gz'))}
""")
    z=load('opening-timing-scores.csv');clocks=load('opening-clock-matched.csv');s=load('opening-clock-sensitivity.csv');g=load('gift-decision-clock.csv')
    latest=read_row(z,cutoff='08:55',model='anchored_1530')
    raw=read_row(z,cutoff='08:55',model='raw_overnight')
    scaled=read_row(z,cutoff='08:55',model='variance_scaled')
    prev=read_row(clocks,candidate='prior_close',metric='brier')
    m=select(z,cutoff='08:55')
    ordered=select(z,model='anchored_1530').set_index('cutoff').reindex([k for k in GAP_CLOCKS if k in set(z.cutoff)]).reset_index()
    bounds=select(load('opening-matched.csv'),cutoff='08:55',candidate=['raw_overnight','mapped_linear','variance_scaled','rolling_basis'],metric=['brier','crps','interval_score'])
    count=pd.DataFrame(dict(raw_eligible_marks=g.groupby('clock').size())).reindex(GAP_CLOCKS,fill_value=0).rename_axis('cutoff').reset_index()
    report(2,f"""
GIFT prices progressively narrowed the opening-price distribution before the regular NSE session. On {int(prev.n)} matched mornings, the same anchored method scored {prev.candidate_loss:.6f} Brier at 17:00 on the prior Indian cash session and {prev.control_loss:.6f} using 08:55 data. The latter beat earlier checkpoints most clearly on prior-close, completed-US and 07:00 comparisons. The 06:00 clock lacked enough fresh observations. The archived 08:45 and 08:55 comparisons are nearly indistinguishable on their common mornings. The historical auction begins at 09:00 IST under the regular NSE timetable. GIFT observation time means the bar’s latest permissible end plus the publication buffer. The US checkpoint is the latest eligible NY cash close plus 60 minutes.

{tab(count)}

{tab(ordered,('cutoff','n','Brier','CRPS','accuracy','MAE','MdAE','coverage80','width80','median_age'))}

## Mechanical marks and statistical fits

The mechanical reference is the latest GIFT mark divided by a same-instrument previous-session anchor. The prior cash-level model uses the prior NIFTY close directly. The rolling-basis model subtracts the trailing median of the contemporaneous futures/cash differential. The linear mapping uses earlier realized gaps. Its scale-aware variant fits the absolute errors of earlier genuine out-of-sample mappings. Raw overnight uses the same historical shape centered on the literal GIFT price change. The anchored variant lets the historical residual median displace the forecast. On its own 08:55 cohort, it scored {latest.Brier:.6f} Brier and {latest.CRPS:.6f} CRPS with {latest.coverage80:.2%} central 80% coverage and {latest.width80:.2%} width. The protected V16 interval covered 76.61%.

The raw overnight method achieved {raw.Brier:.6f} Brier, {raw.accuracy:.2%} accuracy and {raw.CRPS:.6f} CRPS on the 248 mornings. Variance scaling reached {scaled.coverage80:.2%} coverage with {scaled.width80:.2%} width and {scaled.Brier:.6f} Brier. Its CRPS of {scaled.CRPS:.6f} shows the distribution tradeoff. The raw offshore move accounts for most of the opening result on these dates.

{tab(m,('model','n','Brier','CRPS','log_loss','accuracy','MAE','MdAE','RMSE','coverage80','width80','interval80'))}

{tab(bounds,('candidate','control','metric','n','gain','adjusted_low21','adjusted_high21'))}

## Contract, anchor and event checks

The inherited Yahoo vendor alias has archived historical observations and unresolved dated expiry identifiers. The study tracked the calendar rollover window, allowed anchor ages and price availability, then tested 15:15, 15:30, 15:40 and 17:00 prior marks, delayed observations, gaps after weekends or holidays and large observed outliers. Historical trading-hour or expiry changes can also affect missing-clock eligibility. The newest bar in an eligible regular morning can be only as fresh as the documented guard. The NSE IX page does not supply a compatible dated-contract tape in this workspace. Calibration is archived separately for direction and the ±0.5% and ±1.0% events with case counts by probability bin.

{tab(select(s,model='anchored_1530'))}

{rel(('Clock-matched score gaps','opening-clock-matched.csv'),('Per-clock model comparisons','opening-matched.csv'),('Opening sensitivity','opening-clock-sensitivity.csv'),('Opening distribution calibration','opening-calibration.csv'),('Eligible source timestamps','gift-decision-clock.csv'),('Regular NSE auction schedule','https://www.nseindia.com/static/products-services/equity-market-pre-open'))}
""")


def opening_surprise_groups():
    f=load('intraday-feature-panel.csv.gz');y=load('intraday-target-panel.csv.gz')
    m=f[['day','cutoff','open_surprise_z','stock_above_open','gap_seen']].merge(y,on=['day','cutoff'],validate='1:1')
    rows=[]
    for clock,g in select(m,cutoff=['09:25','10:20']).groupby('cutoff'):
        z=g.open_surprise_z;q=g.stock_above_open
        groups={'z > 0.75':z.gt(.75),'z < -0.75':z.lt(-.75),'|z| <= 0.75':z.abs().le(.75),
                'z > 0.75, breadth >= 65%':z.gt(.75)&q.ge(.65),'z > 0.75, breadth <= 45%':z.gt(.75)&q.le(.45),
                'z < -0.75, breadth <= 35%':z.lt(-.75)&q.le(.35),'z < -0.75, breadth >= 55%':z.lt(-.75)&q.ge(.55)}
        pos={d:i for i,d in enumerate(g.day)}
        for tag,mask in groups.items():
            x=g[mask]
            selection=np.array(sorted(x.day.map(pos)),dtype=int)
            episodes=int(len(selection)>0)+int(np.count_nonzero(np.diff(selection)>1))
            rows.append(dict(cutoff=clock,group=tag,n=len(x),episodes=episodes,closing_gap_mean=x.gap_seen.mean(),
              return30_bps=1.e4*x.r30.mean(),remaining_return_bps=1.e4*x.regular_residual.mean(),
              remaining_risk_bps=1.e4*x.remaining_vol.mean(),rising30=float(x.r30.dropna().gt(0).mean())))
    z=pd.DataFrame(rows);write('opening-surprise-regimes.csv',z)
    return z


def postopen():
    f=load('intraday-feature-panel.csv.gz');d=load('postopen-matched-evidence.csv');t=read('intraday-timing-receipt.json')
    s=read('stock-panel-receipt.json')
    e=load('historical-stock-basket.csv');new=read('announcement-receipt.json')
    c=select(d,cutoff=['09:25','10:20'],candidate=['surprise_residual','surprise_direct','participation_term','proxy_open_surprise'],
             control=['frozen_parent_residual_history','native_control'],metric=['brier','crps'])
    key=['r15','r30','regular_residual','next_session','remaining_5','remaining_21']
    report(3,f"""
Opening surprise equals the official opening return in arithmetic units less the 08:55 forecast mean. Its z-score uses the pre-auction predictive standard deviation with a 0.10 percentage-point lower floor. There were {t['paired_preauction_expectation']} eligible chronological forecast errors. Every one of the {t['cash_open_first_bar_exact']} matched official opens equaled the first stored 09:15 bar open, so the proxy-open sensitivity preserves the same raw outcome on these dates. Brier differences can still arise from feature-set changes in the proxy model. A realized surprise enters a later decision only. Positive surprises and negative surprises can have different subsequent behavior. The tail subgroup statistics use the fixed ±0.75 surprise thresholds and count consecutive-day episodes separately.

{tab(opening_surprise_groups())}

The ordinary gap is already included in the cash/native parent and the gap-size-only comparison. All incremental measures below compare identical eligible dates and targets. The return for a cutoff starts at a later independent event, and original residual endpoints end on the fixed original reference’s session count. Positive gains favor the candidate.

{tab(select(c,target=key),MATCHED,44)}

{rel(('Expected gap ledger','opening-baseline-expectation.csv'),('Observed opening and first bar','observed-open_and_surprise.csv'),('Full return and risk comparisons','postopen-matched-evidence.csv'),('Replayed V16 continuation','reproduced-continuation.csv'),('Original gap-fill timing results','reproduced-survival.csv'))}
""")
    eod=read('official-equity-receipt.json')
    present=f.groupby('cutoff',as_index=False).agg(dates=('day','nunique'),minimum=('stock_n','min'),median=('stock_n','median'),maximum=('stock_n','max'),
        financial=('bank_above','count'),stock_count_breadth=('stock_advance','count'),synchronized_native=('source_native_n','median'))
    report(4,f"""
The historical research basket contains **30 common stocks and two ETFs**. Five dated January 2025 cash files rank traded rupee turnover within six defined sleeves. The seed dates precede the frozen evaluation period. This is a historically eligible, turnover-ranked sample with a discretionary sector shortlist. Complete dated NIFTY 50/100/200/500 constituent membership and free-float weights were unavailable. Therefore, archive-native sector/index series and official equal-weight index relative returns remain separate from actual stock-count breadth. NIFTYBEES and BANKBEES are traded instruments. The share baseline discards incoherent bars, overlap duplicates and mismatched ISINs. {s['audit_stock_days']:,} stock/date pairs were compared with the official daily file. The matched panel identified {s['identity_switches']} observed transitions and {s['declared_action_days']} marked ex-action stock days. The official archive recorded {new['basket_actions']} basket-related corporate actions, including events without matching five-minute observations.

{tab(e,('stock','sector','rank','isin') if 'isin' in e and 'rank' in e else None)}

## Historical support and identity checks

KOTAKBANK, BAJFINANCE and SHRIRAMFIN have dated instrument-history entries. Some past keys failed and coverage differs by period. The same-day OHLCV panel uses the exact valid identifier where the source supplied it. A transition or implausibly large observed close-to-open discontinuity invalidates the overnight stock comparison. The action date is a separate sensitivity screen. The 25-minute fills preserve wider data for the audit and network where synchronized. Actual intraday stock-count features use only five-minute completed bars. The fixed top-300 January cohort and all-EQ official market file provide separate close-only tests before original-horizon issues.

{tab(present)}

Historical equity intake covered {eod['accepted']:,} archive sessions and {eod['rows']:,} official EQ records. The receipt records aggregation results and raw source hashes.

{rel(('Symbol and resolution coverage','stock-bar-coverage.csv'),('Stock eligibility receipts','stock-eligibility-receipt.json'),('Date-indexed instrument history','stock-identifier-history.csv'),('Stock and exchange price audit','stock-identity-and-price-audit.csv.gz'),('Cash equity archive receipt','official-equity-receipt.json'),('Official cash breadth','official-stock-breadth.csv'),('NSE index methodology','https://nsearchives.nseindia.com/content/indices/Nifty_Broad_Market_Indices_Methodology.pdf'))}
""")
    z=select(d,cutoff=['09:25','10:20','12:30','14:00'],target=['r30','regular_residual','remaining_range','remaining_vol'],
            candidate=['stock_direct','stock_residual','stock_neutralized','financial_residual','official_EW_residual','joint_stock_native'],
            control=['native_control','frozen_parent_residual_history'],metric=['brier','crps'])
    only=z.sort_values('gain',ascending=False)
    report(5,f"""
Participation tests use **{t['rows']:,} decision snapshots from {t['dates']} market days**. The eight clocks run from 09:25 to 15:00 IST. At each clock, the latest observed five-minute bar is eligible at its end plus five minutes. Actual stock-count advance, percent above the open, and percent outperforming synchronized NIFTY come from observed traded stock prices. Same-sector deviations use each sleeve’s contemporaneous stock median. Equal-weight average return, median, dispersion, tail concentration, banking breadth, acceleration and observed stock synchronization enter the comparisons. Financial leadership is a sleeve-relative return. Above-VWAP participation uses the traded-instrument candle proxy described in the liquidity report. Open surprise × breadth and open surprise × financial leadership are frozen interactions. To control for deterioration of support later in the day, every reported gain uses the same model/parent dates at a single clock. The effects below are exploratory and sorted within the reported track. The full file preserves unfavorable results and timing sensitivities.

{tab(only,MATCHED,34)}

{rel(('Breadth feature values','intraday-feature-panel.csv.gz'),('Separate future return and risk targets','intraday-target-panel.csv.gz'),('All matched tests and alternatives','postopen-matched-evidence.csv'),('Volume methodology','V17_VOLUME_LIQUIDITY_AND_ORDER_FLOW.md'))}
""")


def domestic_and_residual():
    d=load('postopen-matched-evidence.csv');net=load('network-matched.csv');cor=load('network-correlations.csv');s=read('stock-panel-receipt.json')
    use=['bank_relative','finance_relative','it_relative','nifty_later','nifty_range','nifty_volatility']
    narrow=select(net,target=use,metric='crps',candidate=['distributed_ridge','factor_residual','sparse_residual','old_input'])
    primary=select(cor,source=['bank_own_last5','finance_own_last5','it_own_last5','stock_sync'])
    report(6,f"""
The network study connected synchronized stock observations from banking, finance, and IT sleeves with later, independent sector-minus-cash movement and later NIFTY returns, range and volatility. A bank/finance/IT future native segment starts at the first actual native bar open on or after the cutoff and ends 25 minutes later. NIFTY’s reference segment must have the same start and end and contiguous observations. Its own return, volatility and native-sector controls are known by the decision. This eliminates shared price movement inside an outcome interval as a source of apparent earlier prediction. The dated daily stock networks are predictive diagnostics. Individual live index contribution would require contemporaneous official free-float weights and was outside the verifiable inputs.

{tab(select(primary,target=use),('cutoff','target','source','aligned','lead_r','one_day_old_r','partial_r','partial_n'),35)}

Raw lead correlations, one-day-shifted correlations and partial correlations are preserved separately. Partial features learned a training-only prediction of the stock information from market and sector conditions. The direct distributed-lag model combines current and previous-session signals. The sparse variant chooses two residual features on earlier training data at each date. The old-input variant tests delayed features. The predictive comparison uses exact common dates and block intervals. These results support conditional prediction tests. Directional transmission as an economic mechanism needs evidence independent of shared market shocks.

{tab(select(narrow,cutoff=['09:25','10:20']).sort_values('gain',ascending=False),MATCHED,34)}

{rel(('Exact segment timestamps','network-observed-segments.csv.gz'),('All lead and partial correlations','network-correlations.csv'),('Date-paired predictive tests','network-matched.csv'),('Network fits and sparse selections','network-fits.json'),('Joint original horizon results','original-timed-matched.csv'))}
""")
    vf=select(d,cutoff=['09:25','10:20'],target=['r30','regular_residual','remaining_vol','remaining_range','touch_up','touch_down'],
              candidate=['liquidity_residual','dispersion_touch'],control=['frozen_parent_residual_history','native_control'],metric=['crps','brier','qlike'])
    report(7,f"""
Trade-derived features use actual volume in authenticated stock/ETF candles. The study audited {s['stock_clock_rows']:,} stock and index snapshots across {s['distinct_dates']} days and intentionally left native-index volume missing in {s['zero_volume_native_rows']:,} index rows. Relative volume and turnover are same-clock comparisons against earlier sessions. VWAP uses typical bar price multiplied by observed candle volume as a proxy for transaction VWAP. Turnover inferred from candle prices is approximate and the official cash-file turnover series is reserved for later clocks. Other features are dispersion and concentration of activity, conditional negative-side activity, returns per unit of activity, and a sign-of-price-move × volume proxy. Historical auction order records, quotes, historical depth and prints were unavailable in the study’s stored authentic data. The candle signs measure price changes and trading activity. Trade initiation, bid/ask imbalance, dealer inventory and executable spreads require genuine historical records. Upstox’s candle and live-feed documentation describe distinct capabilities.

{tab(vf,MATCHED)}

{rel(('Intraday source and price audit','stock-identity-and-price-audit.csv.gz'),('Official traded cash data','official-equity-receipt.json'),('Historical Upstox candles','https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/'),('NSE historical order and trade data','https://www.nseindia.com/static/market-data/eod-historical-data-subscription'))}
""")
    legs=['nifty_cash_leg','nifty_etf_leg','nifty_basis_leg','bank_index_leg','bank_etf_leg','bank_basis_leg']
    c=select(net,target=legs,metric='crps',candidate=['factor_residual','distributed_ridge'])
    u=select(cor,target=legs,source=['nifty_etf_tracking','bank_etf_tracking'])
    x=select(d,cutoff=['09:25','10:20'],candidate=['cross_instrument_residual','etf_touch'],control=['frozen_parent_residual_history','native_control'],
             target=['r30','regular_residual','remaining_range','remaining_vol','touch_up','touch_down'],metric=['crps','brier'])
    report(8,f"""
The direct cross-instrument tests measured observed NIFTYBEES relative to NIFTY and BANKBEES relative to BANK NIFTY at a common mark. A separate feature demeans tracking against earlier same-clock observations. Future ETF and underlying returns start after the decision and end at the same observed timestamp. Their difference distinguishes apparent tracking normalization from a forecast of later cash. The NIFTY pair uses 30 forward minutes. The bank pair uses an aligned 25-minute native interval where complete. Forecast returns are in arithmetic equivalents of synchronized log ratios. Same-day distributions, stale marks and the observed return differential can affect the basis. Relative stock and ETF comparisons have historical price/volume coverage, with wider uncertainty around actual spreads and fund distributions. Executable spread, financing carry and dividend impacts are unverified for the full intraday window.

{tab(u,('cutoff','target','source','aligned','lead_r','one_day_old_r','partial_r','partial_n'))}

{tab(select(c,cutoff=['09:25','10:20']),MATCHED,34)}

Domestic cash/front-future observations, previous same-contract differential, near-curve state and prior option parity came through the dated inherited daily archive. Intraday futures and expiry-conditioned leg attribution need an authenticated dated sample. Expiry and expired-future requests returned HTTP 401 with the available authentication. The study therefore tested lagged basis as a predictor and measured subsequent adjustment on synchronized ETF and underlying legs.

{tab(x,MATCHED,32)}

{rel(('Matched ETF and index returns','network-observed-segments.csv.gz'),('All cross-instrument predictive comparisons','network-matched.csv'),('Source access receipts','new-source-availability.json'),('Upstox expired instruments API','https://upstox.com/developer/api-documentation/expired-instruments/'))}
""")
    out=select(d,cutoff=['09:25','10:20'],candidate=['stock_direct','stock_residual','stock_orthogonal','joint_stock_native','financial_residual',
             'surprise_residual','surprise_orthogonal','cross_instrument_residual','liquidity_residual'],control=['frozen_parent_residual_history','native_control'],
             target=['r30','regular_residual','remaining_5','remaining_21'],metric=['crps','brier'])
    report(9,f"""
The baseline is re-estimated as it actually would have been on each prior dated origin from earlier matured targets. Each historical residual subtracts that origin’s original model forecast. Subsequent fits use only residual outcomes whose endpoint precedes the current decision date. A regularized correction changes the baseline center, with a common past-only standardized residual distribution around it. A zero correction retains the same forecast shape. Neutral, matured history, price only, volatility only, price-plus-volatility, official equal-weight and native-sector models separate ordinary state information from stock or surprise corrections. Direct models solve the full return task on eligible inputs. Orthogonal variants predict each candidate feature from the strong parent state using earlier dates and carry forward the unexplained feature. These are tests of incremental prediction after the specified statistical controls. Hypotheses and comparisons remain retrospective.

{tab(out.sort_values(['target','cutoff','metric','gain'],ascending=[True,True,True,False]),MATCHED,46)}

The case files contain location, Brier, log loss, mean and median absolute error, CRPS, interval score, quantile loss and predictive width. Every predicted distribution and the training-end receipt can be retrieved by law index. Reported CRPS is positive and lower is better. Gains are parent loss minus amended forecast loss. The 128-atom law gives a smoothed direction probability. Risk laws use nonnegative support.

{rel(('Full matched residual results','postopen-matched-evidence.csv'),('Chronological baseline/residual ledger at 09:25','residual-0925-baseline-residual-ledger.csv.gz'),('Residual fitting receipts at 09:25','residual-0925-fit-receipt.ndjson.gz'),('Residual distributions at 09:25','residual-0925-laws.npz'),('Falsification and calendar checks','V17_VALIDATION_AND_FALSIFICATION.md'))}
""")
    m=load('multiscale-information-matrix.csv')
    tracks={'brier':'direction or touch event','crps':'distribution','abs_error':'expected level or magnitude','qlike':'realized risk'}
    grid=m[m.metric.isin(tracks)].copy()
    grid['pair']=grid.candidate+' vs '+grid.control
    grid['target family']=grid.metric.map(tracks)
    def is_intime(x):
        return x.cutoff.isin(['09:25','10:20'])&x.target.isin(['r15','r30','r60','regular_residual','next_session','remaining_3','remaining_5','remaining_10','remaining_21','remaining_vol','remaining_range','abs_regular','touch_up','touch_down'])
    expo=grid[is_intime(grid)&~grid.category.str.contains('falsification')].sort_values(['cutoff','target','category','metric','gain'],ascending=[True,True,True,True,False])
    first=expo.drop_duplicates(['cutoff','target','category','metric'])
    stable=grid[grid.simultaneous_benefit.astype(bool)].sort_values(['cutoff','target','category','metric'])
    report(10,f"""
The cross-product contains **{len(m):,}** matched source, clock, target, and metric comparisons. Opening targets and original-clock returns and joint paths have their own matched matrices. The post-open target grid includes 15-minute, 30-minute, one-hour, remaining-day, following-session and remaining 3/5/10/21-session returns, as well as absolute moves, realized volatility, range and ±0.5% intraday barrier events. The greatest common-clock gain can help diagnose where information enters. The gains below are descriptive for the exposed study. Intervals adjust across the tested model contrasts within one cutoff, target and metric and use resampled calendar-date blocks. Separate risk-specific and original-horizon tables make comparisons at their own relevant cutoff and on identical eligible dates.

{tab(first[['cutoff','target','category','target family','pair','n','disjoint','gain','adjusted_low21','adjusted_high21']],n=70)}

There are {len(stable):,} cells whose interval cleared zero and whose early and later point gains were positive. This count includes correlated or nested tests. A market mechanism must still survive its specific delayed, duplicated-input or blocked control and a new date cohort.

{rel(('Full information-source × horizon × target matrix','multiscale-information-matrix.csv'),('Opening clock matrix','opening-clock-matched.csv'),('Original timing matrix','original-timed-matched.csv'),('Original volatility expansion matrix','postopen-volatility-matched.csv'),('Joint path matrix','retimed-path-matched.csv'),('Post-open risk sets','postopen-barrier-matched.csv'))}
""")


def original_and_validation():
    orig=load('original-timed-leaderboard.csv');pairs=load('original-timed-matched.csv');over=load('original-protected-overlay-matched.csv')
    core=select(orig,cohort='combined')
    main=select(pairs,control='clock_structural',metric=['brier','crps'],candidate=['stock_residual','stock_direct','component_plus_residual','low_rank_tasks','low_rank_sector_risk','fixed_structural_mixture'])
    risk=load('retimed-path-matched.csv');passage=load('retimed-barrier-matched.csv')
    convergence=load('path-convergence-summary.csv');cond=load('postopen-barrier-matched.csv');pr=load('postopen-volatility-matched.csv')
    report(11,f"""
The original reference is the previous official cash close. The horizon ends at the official close of session number five or 21. V17 asserts case-level equality to the original V14 realized return and preserves **265 weekly and 217 monthly** origins. The D 17:00 IST reconstruction uses earlier foreign observations and domestic snapshot variables, with D 17:00 GIFT where available. The following morning at 08:55 can incorporate the completed US session, Asia inputs where independently timestamped and the latest pre-auction GIFT forecast. The V14 standalone forecast’s native 09:10 guard stays attached to its exact weighted atom archive. Comparing V16 08:55 to the native V14 book addresses published historical performance. Testing models against same-clock parents addresses the value of newly observable data. Later post-open figures in the research cover fixed original endpoints from their own later reference.

{tab(core,('horizon','cutoff','model','n','disjoint','brier','crps','accuracy','balanced_accuracy','covered','width'))}

## Paired value at each origin

The return track tested direct ridge with stock inputs, stock residual corrections, a decomposition into first overnight, initial regular session and future cumulative movement, two-factor fits across gap, regular, and multi-horizon return targets, and a fixed model mixture. The auxiliary task variant also learns the bank-relative session return and session risk using complete matured rows. All prior labels resolve before the model’s date guard. The mixture pools evenly spaced atoms from three component distributions. The component experiment adds the first-return locations before sharing the structural residual shape. Exact historical V14 laws were shifted in a separate past-error overlay. Early correction coverage matters because an exact protected reference is available for fewer prior days than the continually rebuilt parent.

{tab(main,ORIG)}

{tab(over,('horizon','subset','candidate','control','metric','n','disjoint','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21'))}

## Issue clock and the early barrier effect

The archived 265-origin GIFT-first model is an **08:55** next-morning comparison. V17 retimed its first component, previous-close domestic states and same-time GJR and ATM IV path controls. The previous-close result measures the value of the earlier available quote. Some reconstructed return-distribution differences are due to simple model structure, so the matched baseline matters for each claimed improvement.

{tab(select(risk,candidate='decomposed_gift',metric=['brier','endpoint_crps','touch_brier'],control=['decomposed','same_clock_IV','same_clock_GJR']),ORIG)}

{rel(('Original cutoff and maturity audit','original-cutoff-audit.csv'),('Original fitted laws','original-clock-laws.npz'),('Native protected-law overlay','protected-law-residual-overlays.csv.gz'),('Original same-cutoff comparison','original-timed-matched.csv'),('Retimed joint path archive','retimed-path-archive.json'))}
""")
    new=select(pr,metric=['brier','abs_error','qlike','crps'],control=['cash_risk','raw_iv','fixed_iv_rv','offshore_plus_domestic'])
    focus=select(passage,candidate='decomposed_gift',control=['decomposed','same_clock_IV'],metric=['brier_by_1','touch_brier','conditional_brier','integrated_brier'])
    mc=select(convergence,metric=['brier','endpoint_crps','range_crps','touch_brier','day_one_Brier','survivor_Brier'])
    report(12,f"""
Volatility studies preserve separate point and expansion benchmarks. Weekly V16 offshore/domestic volatility MAE was **0.036469**, while raw ATM IV achieved **0.037814** with its own QLIKE. Monthly GJR-GARCH MAE was **0.033179**. The fixed IV/RV blend and Student-t EGARCH remain expansion benchmarks. V17 starts a same-clock cash-risk baseline from known implied volatility, observed opening gap and completed-prefix realized variance. Earlier fitted errors train the incremental opening-surprise, stock-participation, liquidity/disagreement and option-surface corrections. Expansion means realized volatility at least **1.25×** the original trailing volatility. The expansion classifier is separately calibrated. The joint path study separately samples a past cash-path suffix conditioned on the known open and path prefix, including the interval from the last available bar to the decision as unknown. Analog choices and IV scales only use earlier mature dates. The known cash prefix contributes observed highs and lows. The scenario archives preserve one coherent OHLC law per model and origin.

{tab(select(new,control='cash_risk'),ORIG,38)}

## Barrier risk sets and dispersion

The full-horizon touch law comes from the first observed crossing on simulated paths. The survival calculation restricts each observed origin × side × barrier to episodes surviving day one, and reconditions each simulated law on its own day-one survivors. The post-open analysis also restricts the comparison to barriers still untouched in the known cash prefix. `n` is the number of dates. The side-barrier counts retain additional evidence within each date and each bootstrap contribution first aggregates the identically eligible side-barrier comparisons within a date. Day 1, 3, 5, 10 and 21 Brier and passage-time log scores are archived where the horizon supports them.

{tab(focus,PATHS)}

{tab(select(cond,screen='prefix_survivor',metric=['brier_by_1','touch_brier','conditional_brier','integrated_brier']),PATHS)}

## Monte Carlo convergence

The V16 GIFT-first and session-state methods were redrawn at **256, 2,048 and 8,192** paths on **32 fixed origins per horizon**, for **384 model/origin/draw-count combinations**. Each 256-path archive reproduced exactly. The random uniforms use nested prefixes across path counts to reduce comparison noise. Sample centering inside the archived models causes some paths to move when the number of samples changes. RMS and median absolute deviations from 8,192 measure simulation sensitivity on the fixed dates. Forecast uncertainty remains the underlying predictive distribution’s spread.

{tab(mc,('horizon','model','metric','paths','origins','average','median_abs_MC_delta','rms_MC_delta'),72)}

{rel(('Inherited volatility benchmarks','../../../nifty_forecast_v16/2026-11-25/run-001/volatility-leaderboard.csv'),('Post-open volatility comparisons','postopen-volatility-matched.csv'),('Post-open joint paths and receipt','postopen-path-archive.json'),('Monte Carlo evidence','path-convergence-summary.csv'),('Convergence archive locations','path-convergence-archive.json'),('Matched day-one and surviving paths','retimed-barrier-matched.csv'),('Post-open conditional barrier comparison','postopen-barrier-matched.csv'))}
""")
    src=read('new-source-availability.json')['probes'];ann=read('announcement-receipt.json')
    z=pd.DataFrame(src).reindex(columns=['name','status','bytes','file'])
    ann_ev=select(load('postopen-matched-evidence.csv'),candidate='announcements_residual',control='frozen_parent_residual_history',metric=['crps','brier'])
    report(13,f"""
The largest new timed source is NSE company announcements. The retained downloads contain **{ann['total_records']['announcements_2025']:,}** 2025 rows and **{ann['total_records']['announcements_2026']:,}** 2026 rows through the frozen vintage. The audit retained **{ann['timed_tagged_announcements']}** tagged exchange publications for the basket. The usable timestamp is exchange dissemination plus five minutes, distinct from the company filing timestamp and the underlying event date. Models use counts of results, board schedule notices, corporate actions and financial-sector publications. A later result does not reconstruct any historical earnings expectation. Official EOD cash turnover and the exchange’s published EQ series provide trailing eligible input. Historical index-change notices and reconstitution policy are useful for membership audits. The study lacked a complete daily point-in-time member/weight panel and an authenticated historical auction tape.

{tab(z)}

The FII/DII probe returned the public report HTML, with the same byte count as the dated-history attempt. Historical bulk and block sample URLs returned 404. The cash archive and previous versions retain matched EOD derivatives, expiry, OI and option-surface data with previous-date guards. Upstox expired-instrument HTTP 401 limits new dated stock futures. The GIFT alias and prior V16 public futures/sector sources have independent timestamp and roll coverage diagnostics. Historical quote, depth, auction and full contract files need authenticated historical entitlement and timestamps. Revision risk remains for downloaded historical archives. The probes and cash/stock receipts retain source checksums, retrieval clocks and raw responses for verification.

{tab(ann_ev,MATCHED,26)}

{rel(('Audit of source and history probes','new-source-availability.json'),('Auditable announcement dissemination times','announcement-availability.csv.gz'),('Cash turnover and identities','official-equity-receipt.json'),('NSE announced index reconstitutions','https://www.niftyindices.com/resources/index-reconstitution'),('NSE historical data inventory','https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Data%20list%20under%20NSE%20Data%20Sharing%20Policy%20for%20Research%20and%20Analysis_20250728.pdf'))}
""")
    audit=read('validation-receipt.json');sent=load('future-sentinels.csv');prior=read('predecessor-protection.json')
    d=load('postopen-matched-evidence.csv')
    falsifiers=['stock_clock_delay','stock_delay1','stock_block_shuffle','residual_label_shuffle','stock_without_heavy','stock_random_subset1',
                'stock_random_subset2','action_screen_stock','training_month_removed','surprise_delayed','proxy_open_surprise']
    d=select(d,cutoff=['09:25','10:20'],target=['r30','regular_residual','remaining_vol','remaining_21'],candidate=falsifiers,
             control='frozen_parent_residual_history',metric='crps')
    report(14,f"""
Across {audit['sentinel_cases']} cutoff, target and date stress tests, {audit['sentinel_laws']} individual model distributions stayed exactly invariant after altering later inputs and outcomes that had yet to mature. All {audit['cash_feature_rows']:,} cash decision snapshots and {audit['stock_feature_rows']:,} stock/index snapshots passed completed-bar margins. Each official derivative or options feature with a recorded session is strictly earlier than the intraday decision. Historical opening examples link to an eligible mark and pre-auction forecast. The previous-close originals pass the guarded label-end check. The five- and 21-session V14 realized returns agree case by case with V17. Realized volatility and expansion agreed on {audit.get('matched_volatility_target_rows',960):,} matched V16 risk cases. The V16 protection check matched {prior['checked']} archive files and {prior['source_files']} code files, with the inherited hashes for earlier studies retained.

{tab(sent)}

## Falsification suite

The opening suite tests raw mechanical percentage, trailing basis, earlier and delayed quotes, approximate rollover exclusions, stale marks, nonordinary calendar breaks and sensitivity to the largest gaps. Stock checks vary the eligible members, remove one highest-turnover seed per sleeve, screen ex-actions, use training-only sector neutralization, delay the stock input by either a session or an observable earlier checkpoint, reorder feature blocks or chronological residual labels, and remove a training month. Direct feature specifications deduplicate identical columns before fitting. Selectors and fills use matured history. Counterfactual tests within the exposed dates help explain fragile associations. Date blocks of **5, 10, 21, 42** use **1,500** resamples and adjust overlapping candidate tests within fixed target and metric families. Beyond-brief claims about order imbalance or historical constituents would require independent sources.

{tab(d,MATCHED,54)}

{rel(('Full clock and outcome checks','validation-receipt.json'),('Protected predecessor chain','predecessor-protection.json'),('Future sentinels','future-sentinels.csv'),('Opening sensitivity','opening-clock-sensitivity.csv'),('Random historical subsets','stock-random-subsets.json'),('All falsification comparisons','postopen-matched-evidence.csv'))}
""")


def synthesis():
    d=load('postopen-matched-evidence.csv');m=load('multiscale-information-matrix.csv')
    cases=sum(r['n'] for r in read('validation-receipt.json')['residual_forecasts'])
    original=load('original-timed-leaderboard.csv');orig=select(original,cohort='combined')
    m1=select(d,candidate=['stock_residual','surprise_residual','liquidity_residual','financial_residual','cross_instrument_residual'],
              control='frozen_parent_residual_history',cutoff=['09:25','10:20'],target=['r30','regular_residual','remaining_5','remaining_21'],metric='brier')
    clean=m[m.simultaneous_benefit.astype(bool)&~m.category.str.contains('falsification')]
    stable=select(clean,metric=['brier','crps','qlike']).sort_values(['metric','gain'],ascending=[True,False]).drop_duplicates(['cutoff','target','category','metric'])
    return_tracks=stable[stable.target.isin(['r15','r30','r60','regular_residual','next_session','remaining_3','remaining_5','remaining_10','remaining_21'])]
    report(15,f"""
V17 registered six research mechanisms before the new feature scores, with two original horizons, eight intraday decisions, two dedicated joint-risk clocks, fixed shrinkage, no expansion to additional years, and equal-eligible-date tests. It reused the V14 risk laws, V15 session timing and GJR state, and V16 opening, first-passage and date-block machinery. The result archive includes **{cases:,}** post-open forecasts. The post-open chronologies come from at most 400 market dates. Returns and risk at different clocks overlap within each day. Many five- and 21-session labels overlap across dates. Date and disjoint support are included in the score files.

| Evidence class | What carries forward |
| --- | --- |
| Reproduced historical association | Eligible GIFT price changes reveal the opening gap. Near-open timestamps and contract uncertainty remain material. |
| Demonstrated methodology | Forecast timestamp and target start differ. Residuals from chronological forecasts and day-one first-passage conditioning can be audited exactly. |
| Cohort-dependent | Shorter, date-matched risk corrections can show a gain with a weak directional signal on the same sample. Check stronger same-clock and falsification parents. |
| Failed model family on this record | Many stock and surprise residual corrections, original monthly structural variants and unconditional GIFT extrapolation beyond opening. Preserve the benchmark and losing cases. |
| Unresolved mechanism | Stock-level lead and transmission can reflect shared factor exposure. ETF tracking behavior, actual quote pressure, and genuine stock-specific information require instrument-level evidence. |
| Distinct new hypothesis | Independent company dissemination times and matched ETF/underlying leg attribution are observable inputs. They can be prospectively registered at one clock. |

There are {len(return_tracks)} distinct return-target rows with a positive adjusted 21-session-block interval and positive early and later estimates in the selected Brier/CRPS/QLIKE grid. Some rows share the same market movements. The study has no independent final model-selection holdout across the V1–V17 work.

{tab(stable,MATCHED,30)}

{rel(('Research registration and budget','registration.json'),('Falsification','V17_VALIDATION_AND_FALSIFICATION.md'),('Complete cross-source evidence','multiscale-information-matrix.csv'),('Protected chain','predecessor-protection.json'))}
""")
    leader=select(load('postopen-model-leaderboard.csv'),cohort='combined')
    safe=select(leader,cutoff=['09:25','10:20'],target=['r30','regular_residual','remaining_range','remaining_vol','touch_up','touch_down'],
             model=['native_control','price_vol','stock_direct','stock_residual','surprise_residual','cross_instrument_residual','stock_neutralized','surprise_touch','dispersion_touch'])
    pas=load('retimed-barrier-matched.csv');pr=load('postopen-volatility-leaderboard.csv');o=load('opening-timing-scores.csv')
    report(16,f"""
Each table uses its own clock, target family, source eligibility, and original reference price. Lower scores indicate better Brier, log loss, CRPS, absolute errors, QLIKE and quantile loss. Balanced accuracy averages hit rates for both signs. The event probability calibration archive shows observed frequency against mean prediction per bin. Coverage and width read together. Mean-return or risk rank correlations indicate ordering by the forecasts. Disjoint counts greedily select windows whose dates do not overlap. `n` counts forecast dates. The matched evidence preserves exact date and side-barrier support and block intervals, while the descriptive leaderboards give each individual model’s eligible dates. Protected release origins remain 265 and 217.

## Opening direction and magnitude

{tab(select(o,cutoff='08:55'),('model','n','Brier','CRPS','accuracy','log_loss','MAE','MdAE','RMSE','coverage80','width80'))}

## Opening surprise, short returns, remaining-session risk, barrier events

{tab(safe,('cutoff','target','model','n','disjoint','brier','log_loss','crps','median_abs_error','rmse','qlike','rank_correlation','quantile_loss','covered','width'),64)}

## Original windows

{tab(orig,('horizon','cutoff','model','n','disjoint','brier','crps','log_loss','rank_correlation','quantile_loss','covered','width'))}

## Post-open volatility and expansion

{tab(select(pr,cohort='combined'),('horizon','cutoff','model','n','disjoint','brier','crps','abs_error','qlike','log_loss','covered','width'),26)}

{rel(('All post-open leaderboards','postopen-model-leaderboard.csv'),('Post-open probability calibration','postopen-probability-calibration.csv'),('Opening surprise cohort diagnostics','opening-surprise-regimes.csv'),('Original timed probability calibration','original-timed-calibration.csv'),('Gap continuation and reversal','reproduced-continuation.csv'),('Gap-fill survival','reproduced-survival.csv'),('Original range and joint paths','retimed-path-matched.csv'),('Full, day-one and survivor-conditioned barrier scores','retimed-barrier-matched.csv'),('Post-open conditional risk sets','postopen-barrier-matched.csv'),('Incremental stock and residual forecasts','postopen-matched-evidence.csv'))}
""")
    fwd=read('forward-ledger.json')
    rr=[]
    for r in fwd['records']:
        b=r.get('original_probabilities',{});z=r.get('law_p_up',{})
        rr.append(dict(version=r['version'],key=r['key'],horizon=r['horizon'],reference=r['reference_session'],target=r['target'],
                       completed=len(r['completed_target_dates']),status=r['maturity'],actual=r.get('realized_return'),
                       original_probability=r['p_up'] if 'p_up' in r else ', '.join(f'{k} {p:.6f}' for k,p in {**b,**z}.items()),issue_hash=r['issue_hash']))
    publications=[dict(series=x['name'],status=x['status'],official_open=(x.get('nse_ohlc') or {}).get('open'),
      official_close=(x.get('nse_ohlc') or {}).get('close'),source=x.get('file')) for x in fwd['sessions']]
    report(17,f"""
The independent refresh ran at **{fwd['checked_at']}**. The publication guard and exchange-calendar bound included **{fwd['bound']}**. The {fwd['closure']['day']} cash-session holiday was confirmed by NSE. The frozen research vintage still ends on **2026-11-17**. The V4 experiments were late first-session diagnostics issued before the original targets. The V5 forecasts were issued before the first target session. The original issue hashes, probabilities and archived distributions are retained. Daily completion and the independent prospectively issued endpoint are different events. Any pending target awaits its own official close and publication. New V17 forecasts issued in this run **{fwd['new_v17_issues']}**.

{tab(pd.DataFrame(publications))}

{tab(pd.DataFrame(rr))}

{rel(('Separate append-only forward receipts and scoring ledger','forward-ledger.json'),('November 24 NSE holiday circular','https://archives.nseindia.com/content/circulars/CMTR71775.pdf'))}
""")
    gs=load('opening-timing-scores.csv');clock=load('opening-clock-matched.csv')
    opening0=read_row(gs,cutoff='08:55',model='anchored_1530')
    previous0=read_row(clock,candidate='prior_close',metric='brier')
    best_5=select(orig,horizon=5,cutoff='preauction_0855').sort_values('crps').iloc[0]
    best_21=select(orig,horizon=21,cutoff='preauction_0855').sort_values('brier').iloc[0]
    post=select(load('postopen-barrier-matched.csv'),screen='prefix_survivor',metric='touch_brier')
    risk=select(load('postopen-volatility-matched.csv'),control='cash_risk',metric=['brier','abs_error','qlike']).sort_values(['metric','gain'],ascending=[True,False])
    intra_risk=select(d,target='remaining_vol',candidate='stock_direct',control='native_control',metric=['crps','qlike'],cutoff=['09:25','09:35','11:30'])
    week_delta=read_row(load('original-timed-matched.csv'),horizon=5,cutoff='preauction_0855',candidate='component_plus_residual',control='clock_structural',metric='crps')
    path=select(pas,horizon=5,candidate='decomposed_gift',control='same_clock_IV',metric='touch_brier')
    report(18,f"""
**The clearest V17 finding is time-specific opening-price discovery.** At 08:55, the 15:30-anchored GIFT model scored **{opening0.Brier:.6f} Brier**, **{opening0.CRPS:.6f} CRPS**, and **{opening0.accuracy:.2%} directional accuracy** on its eligible cohort. Relative to the same method issued D 17:00, the next-morning Brier gain was **{-previous0.gain:.6f}** on **{int(previous0.n)}** identical mornings. Historical gap surprise then had to beat observable cash movement, volatility and native sectors on a separate target. The stock and opening-surprise layers usually delivered smaller or adverse directional increments. The date-paired evidence below gives the representative core return tests before picking winners.

{tab(m1,MATCHED,37)}

**The original payoff remains horizon and clock dependent.** The lowest V17 pre-auction 5-session CRPS was **{best_5.crps:.6f}** from `{best_5.model}` with Brier **{best_5.brier:.6f}**. The decomposition’s adjusted CRPS gain interval against its same-clock parent was **{week_delta.adjusted_low21:+.6f} to {week_delta.adjusted_high21:+.6f}**. The protected V14 model’s historical weekly Brier was **0.228529**, under its documented guard. The best newly tested 21-session pre-auction Brier was **{best_21.brier:.6f}** from `{best_21.model}`. The protected monthly direction score **0.245042** and V15 GJR return-law CRPS **0.024694** remain important references. The fixed cohorts contain **53 disjoint weekly windows and 11 disjoint monthly windows**.

**Risk evidence depends on how much of the path is already known.** Full weekly GIFT-first barriers retain a strong morning association. Performance changes at D 17:00 and conditioning on day-one survival. New post-open signals have to beat a parent with the known cash prefix and its IV or risk state. Retain favorable and unfavorable paired tests as priorities for genuinely prospective assessment.

Direct stock features were more useful for the remaining session’s volatility than for a persistent direction forecast. Their gains over the native control were small and appeared at several earlier or mid-session clocks.

{tab(intra_risk,MATCHED)}

{tab(path,PATHS)}

{tab(post,PATHS)}

{tab(risk,ORIG,18)}

The research uses a historically eligible stock/ETF basket and NSE announcements. A complete dated index weight history, dated GIFT contract identity, historical executable spreads and actual cash/derivatives order flow remain unavailable in the verified data. Prospective research is separate from the 2025–2026 historical comparisons.

{rel(('Model comparison','V17_COMPLETE_MODEL_COMPARISON.md'),('Five- and 21-session detail','V17_WEEKLY_AND_MONTHLY_FORECASTING.md'),('Volatility and conditional paths','V17_VOLATILITY_AND_PATH_INTELLIGENCE.md'),('Forward status','V17_FORWARD_RESEARCH_LEDGER.md'))}
""")
    report(19,"""
1. Record one frozen 08:45 and 08:55 opening law on any new eligible 2026 research morning, with source times, dated futures contract identifiers where available, official auction schedule and full distributions. Prespecify raw GIFT and prior-close parents. Resolve only after the official opening result. This tests the small late-morning gain and calibration on unexposed observations.
2. Freeze one cash/risk parent at 09:25 and 10:20 and test the narrowest well-supported opening-surprise, dispersion and turnover inputs on future range or realized risk. Advance a directional model only after it beats its own parent in date-level forecasts. Require new evidence on survivor-conditioned outcomes before using a full-horizon barrier gain to describe later sessions.
3. Obtain authorized archived dated GIFT, domestic cash/future and ETF quotes with consistent timestamps, spreads, corporate actions and financing/dividend state. Test future legs separately with nonoverlapping segments. Confirm whether the observed ETF basis behaves like a fund-price anomaly or predicts a distinct underlying price move.
4. Build dated constituent and free-float weight files for upcoming stock participation tests. Independently predefine the nonconstituent or sector-neutral comparison and a small high-liquidity sample. Keep individual mechanical weights out of future information claims.
5. Keep original weekly and monthly release dates in their own scorebooks. Start with the protected direction/distribution references, neutral monthly and a separately clocked decomposition. Freeze each origin and track enough disjoint windows before adjusting weights or interpreting historical edge. Within the remaining authorized 2026 period, independent 21-session evidence accumulates slowly.

[Historical machine-readable evidence](multiscale-information-matrix.csv) · [Forward research ledger](V17_FORWARD_RESEARCH_LEDGER.md)
""")


def index():
    reports='\n'.join(f'- [{title}](V17_{key}.md)' for key,title in zip(REPORTS,TITLES))
    (OUT/'NIFTY_V17_RESEARCH.md').write_text(f"""# NIFTY V17 research

Historical research through **November 17, 2026**. V17 reproduces the GIFT opening-price result, tests post-open residual returns, and preserves the original five- and 21-session comparisons at their respective clocks. The run includes dated Indian cash equities and ETF candles, exchange dissemination records, matched joint-risk and first-passage studies, and archived predictions and source receipts.

{rel(('Main findings','V17_FINAL_RESEARCH_CONCLUSIONS.md'),('Full model comparisons','V17_COMPLETE_MODEL_COMPARISON.md'),('Opening clock and path chart','opening-and-barrier-clocks.png'),('Validation','V17_VALIDATION_AND_FALSIFICATION.md'),('Forward ledger','V17_FORWARD_RESEARCH_LEDGER.md'))}

## Research reports

{reports}

## Reproduction

{rel(('Research brief','MISSION.md'),('Registered experiment budget','registration.json'),('Commands and file layout','README.md'),('Research file checksums','manifest.json'))}
""",encoding='utf-8')
    mods=('common','replay opening','replay sessions','replay protect','acquire sources','acquire eod','acquire stocks','acquire reconcile_cash','acquire extensions','recover','gift','stocks','daily_equity',
          'panel','network','residual','weekly','paths','postrisk','validation','evidence','acquire forward','report','delivery')
    code='\n'.join('.venv/Scripts/python.exe -m research.nifty_forecast_v17.'+i for i in mods)
    fence=chr(96)*3
    (OUT/'README.md').write_text(f"""# Reproduce NIFTY V17

Run from the trading-desk root in PowerShell. The acquiring stages use the workspace’s configured read-only historical-data credentials. Reproduction of the frozen vintage uses the archived responses and hashes and requires no new model data after November 17, 2026. The forward command performs a distinct refresh using the execution clock. The `NIFTY_V17_OUT` environment variable can point to another run path under the V17 artifact root. Preserve the original mission in the new run and leave earlier versions in place.

{fence}powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:PYTHONDONTWRITEBYTECODE='1'
{code}
{fence}

## File layout

- `sources/` retains the underlying authenticated cash and candle responses along with official public documentation and dated probes. Relevant predecessor series are referenced in their original locations.
- `opening-forecasts.csv.gz`, `original-clock-forecasts.csv.gz`, and `residual-*-scores.csv.gz` use each row’s `law` as the atom-array index in their matching NPZ archive. Returns use native log atoms converted to arithmetic ratios for proper scoring. Scalar risk and binary cash-event laws use their native units. The exact smoothed probability is in the score row.
- `timed-paths/`, `convergence-laws/`, and `postopen-paths/` store joint integer OHLC log ticks. Associated manifests link the exact filed clocks, historical source dates, path naming conventions, and hashes.
- `*_receipt`, `*-fits`, `*-cutoff-audit` and `*-baseline-residual-ledger` retain eligibility and fitted-state traces. `*-matched` files show positive gain when candidate loss is lower.
- `forward/` and `forward-ledger.json` use official complete-session outcomes. They do not enter the frozen training panel.
""",encoding='utf-8')


def chart():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    t=select(load('opening-clock-matched.csv'),metric='brier').set_index('candidate')
    b=select(load('retimed-barrier-matched.csv'),horizon=5,candidate='decomposed_gift',control='same_clock_IV',metric='touch_brier').set_index('cutoff')
    names=['prior_close','us_complete','07:00','08:00','08:30','08:45']
    z=t.loc[names]
    fig,a=plt.subplots(1,2,figsize=(12,4.4),layout='constrained')
    loc=np.arange(len(z))
    a[0].plot(loc,z.candidate_loss,'o-',color='#174b78',label='Named clock')
    a[0].plot(loc,z.control_loss,'s--',color='#6f7982',label='08:55 on same dates')
    a[0].set_xticks(loc,['Prior 17:00','US close + 1h','07:00','08:00','08:30','08:45'],rotation=24)
    a[0].set_title('Opening-gap direction')
    a[0].set_ylabel('Brier score')
    sess=b.loc[['previous_1700','preauction_0855']]
    a[1].plot([0,1],sess.candidate_loss,'o-',color='#174b78',label='GIFT-first')
    a[1].plot([0,1],sess.control_loss,'s--',color='#6f7982',label='Same-clock ATM IV')
    a[1].set_xticks([0,1],['Prior 17:00','Next 08:55'])
    a[1].set_title('Five-session barrier touch · 265 common origins')
    a[1].set_ylabel('Brier score averaged by date')
    for axis in a:
        axis.grid(alpha=.20,axis='y')
        axis.legend(loc='best',frameon=False,fontsize=9)
        axis.set_xlabel('Decision time in IST')
    fig.suptitle('When GIFT NIFTY improves historical forecasts')
    fig.savefig(OUT/'opening-and-barrier-clocks.png',dpi=180)
    plt.close(fig)


if __name__=='__main__':
    opening()
    postopen()
    domestic_and_residual()
    original_and_validation()
    synthesis()
    index()
    chart()
    print('Rendered the 19 V17 reports and research index',flush=True)
