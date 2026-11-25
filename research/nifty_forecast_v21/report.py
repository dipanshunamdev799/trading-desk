"""Publish the complete V21 research record from the numerical artifacts."""
from functools import lru_cache

from .common import *
from .reference import ANCHOR,DIRECTION
from .reconstruction import MAIN
from research.nifty_forecast_v18.report import tab


@lru_cache(maxsize=None)
def data(name):
    return csv(name)


def select(d,**cols):
    for field,value in cols.items():
        d=d[d[field].isin(value) if isinstance(value,(list,tuple,set)) else d[field].eq(value)]
    return d


def table(d,columns=None,count=30):
    return tab(d,columns,count) if len(d) else 'The selected comparison has no matched cases.'


def links(*names):
    return ' · '.join(f'[{p}]({p})' for p in names)


def report(n,body):
    r=REPORTS[n-1]
    (OUT/f'V21_{r}.md').write_text(f'# V21 {r.replace("_"," ").title()}\n\n'+body.strip()+'\n',encoding='utf-8')


def index_board(**criteria):
    return select(data('index-model-leaderboard.csv'),scope='combined',**criteria)


def tracking():
    return select(data('index-tracking-leaderboard.csv'),scope='matched')


def report_universe():
    pre=read('predecessor-receipt.json')
    q=data('protected-return-cases.csv.gz').groupby(['horizon','cutoff','model'],as_index=False).agg(
        n=('day','size'),active=('active','sum'),brier=('brier','mean'),crps=('crps','mean'),log_loss=('log_loss','mean'))
    v10=data('v10-transfer-replay.csv')
    v10=select(v10,model=('X_ONLY','X_SECTORS','X_POOL','X_RANDOM','X_SHIFT','X_FACTORS'))
    v18=select(data('v18-event-transfer-replay.csv'),horizon=(1,5),stage='after_reaction',
               model=('ordinary_pooled','price_only','sector_issuer_partial_pool','matched_non_event_model','randomized_category'))
    v19=data('v19-stock-transfer-replay.csv')
    vx=select(data('v20-temporal-replay.csv'),model=('same_clock_neutral','direct_specialized','horizon_specific_components','independent_components_control'))
    report(1,f'''The V20 manifest binds **{pre['verified_artifacts']} files and {pre['verified_code']} code files**. V21 re-scored **{pre['exact_return_laws']:,} complete weighted laws** directly from their archived atoms and weights. The native forecasts still use the next-session **09:10 IST** issue clock, with V20’s **08:55** input snapshot. The separate matched pre-auction controls retain the V17 weekly session decomposition and the monthly neutral and GJR laws. The exchange publication allowance used in V20 remains an assumption where historical first timestamps are missing.

{table(q,['horizon','cutoff','model','n','active','brier','crps','log_loss'],16)}

V10 transfer was a shared-coefficient and auxiliary-task experiment. The shifted and randomized tasks approached or beat some genuine transfers, and the monthly sector arm had weak direct NIFTY scores. V19 tested stock-relative and sector-relative delivery signals. Delivery moved the five-session stock rank correlation from about **−0.00318 to +0.00300** when added to price and volume, with very small error changes. Its 21-session sector MAE was **0.030875** compared with **0.030702** for price and turnover. V18’s corporate pooling used firm-event responses, where a price-based control stayed competitive. These failure modes concern the estimated signal before propagation to the index. V20’s dependence-aware temporal pieces also lost to the neutral endpoint distribution, a separate failure at the final index forecast. The post-week GJR component test showed a small cohort-dependent positioning gain with a zero-inclusive interval.

{table(v10,['horizon','cohort','model','n','brier','crps'],24)}

{table(v18,['horizon','model','n','dates','issuers','mae','accuracy'],12)}

{table(v19)}

{table(vx,['model','cohort','n','brier','crps'],10)}

{links('predecessor-receipt.json','protected-return-cases.csv.gz','protected-return-laws.npz','v7-auxiliary-reference.csv','v10-transfer-replay.csv','v18-event-transfer-replay.csv','v19-stock-transfer-replay.csv','v19-sector-transfer-replay.csv','v20-temporal-replay.csv','v20-late-component-reference.csv')}''')
    u=read('universe-receipt.json')
    w=data('weight-snapshot-audit.csv')
    a=w.groupby(['flavor','index_name'],as_index=False).agg(vintages=('month','nunique'),minimum_members=('count','min'),maximum_members=('count','max'),
        mean_reported_sum=('rounded_sum','mean'))
    exceptions=w[w.status.ne('verified weight total')]
    report(2,f'''The frozen observation universe contains **{u['all_cash_security_days']:,} security-date rows** for **{u['all_symbols']:,} dated symbols** across **{u['cash_sessions']} sessions**. V21 reused **{u['cash_sessions']-u['new_cash_files']}** checked cash files and acquired the missing **{u['new_cash_files']}** from the official NSE UDiFF archive. Stable security identifiers, observed series, OHLC, volume and turnover remain traceable to cash files. EQ, BE, BZ, SM and ST rows enter the inventory. The fixed January research cohort selected the **240** highest median-turnover securities with at least **12** traded EQ sessions by January 31. It became eligible in February. The union of that cohort with the source-supported index holdings produced **{u['modeled_symbols']} modeled series**. A security can cease trading or leave an index without disappearing from the historical inventory.

The two official archive families yielded **{u['weight_csv_vintages']} complete monthly NIFTY 50 and Next 50 source vintages**, held under a five-completed-session publication allowance, plus dated holdings reports for several sector indices. The archives contain **{u['dated_rows']:,} parsed constituent-weight rows**. The PDF closing prices matched the cash tape on **{u['pdf_exact_prices']:,} of {u['pdf_price_compares']:,} available comparisons**. The CSVs preserve reported weight, equity capital in rupees and index free-float capitalization. Normalized market caps supply the main weights. Two Next 50 files have less than 99.75% in their rounded weight columns and are separately flagged. The NIFTY 50 plus Next 50 membership union informs broad eligibility. The dated 200 and 500 constituent books, full share and face-value history and daily investible-weight-factor and divisor series remain incomplete.

{table(a,None,16)}

{table(exceptions,['month','index_name','status','count','rounded_sum'],10)}

The target is a cash **price index**. Ordinary dividends stay in the observed price changes. Unit changes are handled with dated split and bonus ratios, including simultaneous changes. Confirmed cash resets and the Tata Motors demerger receive separate audit rows. Missing holdings are carried at the last mark in tracking diagnostics and missing outcomes are excluded from component model fitting. Constituents and issuer group labels follow the latest eligible dated files. Industry mapping and any unclassified names are disclosed. Standalone exchange participant OI stays at the market level. V18 timestamped issuer events and first financial results, V19 delivery and completed bulk/block activity enter only through their own verified or declared eligibility rules.

{links('source-receipt.json','historical-equity-inventory.csv','january-liquidity-universe.csv','universe-receipt.json','dated-weights.csv.gz','weight-snapshot-audit.csv','official-weight-cash-reconciliation.csv.gz','cash-identity-and-actions.csv.gz','equity-panel.npz')} · [NSE Indices monthly archives](https://niftyindices.com/reports/monthly-reports) · [NSE capital-market historical reports](https://betanseapi.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives)''')
    z=tracking()
    selected=select(z,model=(MAIN,'nifty50_monthly_drift_lag0','nifty50_monthly_drift_lag1','nifty50_monthly_drift_lag10',
           'nifty50_guarded_no_action','nifty50_monthly_no_drift','january_equal240','january_liquidity240','january_sector_balanced',
           'january_dated_index_float_cap','sector_equal','sector_simplex','sector_train_pca3','nifty50_without_five_heaviest'))
    main=select(z,model=MAIN).set_index('horizon')
    report(3,f'''The official monthly weight reconstruction uses prior free-float capitalization and compounds each stock’s earlier price moves before computing the next portfolio weight. Under the five-session guard, the daily matched MAE is **{main.loc[1,'mae']*10000:.3f} basis points** on **{int(main.loc[1,'dates'])}** dates, correlation **{main.loc[1,'correlation']:.6f}**. The five-session MAE is **{main.loc[5,'mae']*10000:.3f} basis points** and the 21-session MAE is **{main.loc[21,'mae']*10000:.3f} basis points**. These are tracking errors after component returns have occurred. They measure feasibility of reconstruction before forecasting.

{table(selected,['horizon','model','dates','bias','mae','rmse','tracking_error','annualized_tracking_error','correlation'],45)}

Separate rows show lag zero as an ex-post month-end check, one and ten completed-session timing sensitivities, static monthly weights, unadjusted price returns, and loss of the five highest-weight holdings. Fixed equal, historical liquidity, float-cap snapshot and sector-balanced cohorts are explicit research portfolios. Twelve random January-eligible baskets accompany them. Sector weights from a nonnegative simplex and training-only three-component model are statistical coefficients. The reconstruction fits those coefficients using earlier daily observations only.

The combined split and bonus for Bajaj Finance on June 16, 2025 required a price-unit factor of **one tenth**. The routine multiplies simultaneous dated ratios, following the exchange-confirmed factor of **10**. Tata Motors’ October 14 surviving quote is rebased to the special-session open. Complete daily dummy-leg accounting is unavailable across the spin-off interval. The remaining largest weighted reconstruction error is retained in the dated episode file, including the November 12 listing of the spun-off company. Exact daily membership, divisor and first-publication history would further tighten reconstruction.

{links('index-tracking-leaderboard.csv','index-tracking-cases.csv.gz','daily-index-reconstruction.csv','daily-constituent-weight-coverage.csv','tracking-official-episodes.csv','sector-tracking-weights.csv','tracking-config.json','tracking-and-dependence.png','sources/actions/2025-06-13.pdf','sources/actions/2025-10-07.pdf','sources/actions/2025-11-13.pdf')} · [NSE equity-index methodology](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)''')


def report_components():
    s=data('factor-exposure-receipt.csv')
    c=data('concentration-cases.csv')
    f=s[['raw_variance','market_residual_variance','factor_residual_variance','market_beta_median','sector_beta_median']].median()
    d=c.groupby('horizon',as_index=False).agg(n=('day','size'),weight_eff=('effective_weights','median'),
        expected_eff=('effective_expected_contributors','median'),realized_eff=('effective_realized_contributors','median'),
        gross_signal=('stock_signal_before_aggregation','mean'),net_signal=('net_stock_signal','mean'),
        portfolio_over_asset_variance=('forecast_common_variance_ratio','median'))
    report(4,f'''The factor decomposition fits a shrunk market beta and a sector-relative beta using up to **100 earlier daily observations**. At least **35 paired rows** are required per leg. The empirical market and sector returns serve only as historical labels when fitting. Each future factor in the forecast is estimated or simulated from eligible earlier information. Raw security, market-relative, sector-relative and factor-residual labels are all separate. Names without a dated group fall back to a broad-market grouping. Financial leadership, cyclical and defensive structure, momentum, liquidity and relative volatility are evaluated in the dated designs. Size is proxied by the January liquidity ordering or dated index weights where supported. Authenticated financial-result features cover the available quality and earnings information. No standalone size or quality premium is inferred from undated classifications.

Median trailing diagnostics across the audit dates put raw squared return variation at **{f.raw_variance:.6f}**, after the market term at **{f.market_residual_variance:.6f}**, and after the sector-relative term at **{f.factor_residual_variance:.6f}**. Median market and sector coefficients were **{f.market_beta_median:.4f}** and **{f.sector_beta_median:.4f}**. These are historical exposure diagnostics. The comparison of average absolute stock forecasts with the magnitude of their signed weighted sum shows how much component movement survives aggregation.

{table(d,None,5)}

{links('factor-exposure-receipt.csv','feature-definitions.json','component-panel.npz','stock-leaderboard.csv','market-factor-leaderboard.csv','concentration-cases.csv')}''')
    st=select(data('stock-leaderboard.csv'),scope='combined')
    use=('history','technical','pooled','independent','partial_sector','factor_residual','observed_reaction','random_aux_labels')
    key=['horizon','model','target','dates','stock_cases','rank_corr','mae','rmse','brier','crps','coverage','width']
    show=select(st,model=use,target=('absolute','market_relative','sector_relative'))
    other=select(st,model=('history','pooled','random_aux_labels'),target=('vol_normalized','outperform_market','magnitude','realized_volatility','factor_residual'))
    report(5,f'''Equity forecasts cover absolute return, market-relative return, sector-relative return, volatility-normalized return, probability of outperforming NIFTY, absolute return magnitude, realized volatility and factor-residual return. Marginal Gaussian laws use the archived location and an earlier volatility-based scale. Outperformance uses a separately estimated Bernoulli head. Stocks with missing realized prices retain their issuance eligibility and are absent from that score’s realized comparison. Losses are averaged within date first, giving each tested date one unit of weight. Rank correlation is also calculated within date before averaging. The Brier columns on strictly positive magnitude and volatility outcomes have no directional interpretation. Their comparative scores are MAE, RMSE, CRPS and interval calibration.

{table(show,key,56)}

{table(other,key,34)}

The stock-score archive retains company-group and event-present comparisons, and the calibration table follows both positive absolute returns and positive market-relative returns. A lower marginal CRPS can coexist with worse security ordering when most of the forecast benefit comes from a shared center or scale. The randomly aligned auxiliary model helps test that distinction.

{links('stock-leaderboard.csv','stock-sector-leaderboard.csv','stock-date-scores.csv.gz','stock-sector-date-scores.csv.gz','stock-probability-calibration.csv','equity-forecast-laws.npz','feature-definitions.json')}''')
    arch=select(st,target=('absolute','market_relative'),model=('independent','pooled','sector_pool','partial_sector','partial_company',
          'common_relative','factor_residual','history','technical','random_aux_labels','shifted_company','random_sector','short_pool'))
    mf=data('market-factor-leaderboard.csv')
    fit=data('equity-fit-receipts.csv').groupby('horizon',as_index=False).agg(min_dates=('train_dates','min'),max_dates=('train_dates','max'),
        median_rows=('train_equity_rows','median'),predicted_dates=('day','size'))
    report(6,f'''V21 compared independent equity models, fully pooled coefficients, sector-specific pooling, shared estimates shrunk toward sector and issuer estimates, a separate common plus relative return head, and factor-residual pooling. The simple historical and technical controls use the same dated universe. The random target control permutes issuer outcomes within already-matured dates. It retains the common market shock, exposing gains that survive after genuine issuer alignment has been removed. A five-session feature shift, randomized sectors and a shorter 70-date variant offer distinct negative or instability controls. All equity models use complete outcome dates before the next issue, with at most **135 historical dates** and eight-session coefficient refreshes. A separate date-only index model uses the same information cutoff and a comparable regularized fit.

{table(fit)}

{table(arch,key,52)}

{table(mf,['horizon','cohort','model','n','mae','rmse','crps','rank_corr'],14)}

Pooled observations can reduce per-stock estimation error. The independent comparison and the date-only comparison answer different questions. The former tests security parameters and the latter tests whether that accuracy reaches the index.

{links('equity-fit-receipts.csv','equity-model-config.json','pooled-coefficients-5.json','pooled-coefficients-21.json','stock-leaderboard.csv','market-factor-leaderboard.csv','synthetic-power-summary.csv')}''')
    sectors=data('sector-forecast-leaderboard.csv')
    p=sectors.groupby(['horizon','sector'],as_index=False).apply(
        lambda g:pd.Series({k:np.average(g[k].fillna(0.),weights=g.n) for k in ('sector_crps','stock_to_sector_crps',
          'weighted_return','weighted_risk_share','forward_vol','statistical_weight','mean_relative')}),include_groups=False)
    report(7,f'''The sector lane ranks official sector outcomes using direct chronological forecasts, then compares bottom-up stock-to-sector locations under the same sector innovations. The index reconstruction weights on those sector paths come from the earlier-only daily simplex. Stock-level contribution estimates use the starting dated constituent weights. They preserve a separate unclassified or unmatched component where broad industry groups and official sector definitions diverge. Risk contributions use each simulated covariance with the aggregate portfolio, which can be signed. Sector outperformance is measured from the same simultaneous scenarios.

{table(p,['horizon','sector','sector_crps','stock_to_sector_crps','mean_relative','weighted_return','weighted_risk_share','forward_vol','statistical_weight'],18)}

The dated stock weight file gives the beginning exposure, and the complete joint draws account for the terminal effect of drift without inserting subsequent holdings. These results separate the quality of absolute sector forecasts from the value of weighted sector-relative information. Changing the expected distribution of gains across sectors can have a small aggregate impact when stock-specific errors offset one another.

{links('sector-forecast-leaderboard.csv','sector-contribution-cases.csv.gz','constituent-contribution-cases.csv.gz','joint-simultaneous-laws.npz','sector-tracking-weights.csv','market-factor-leaderboard.csv')}''')


def index_headline():
    z=index_board(cutoff='native_0910')
    n=[]
    for h in HORIZONS:
        a=select(z,horizon=h)
        for m,base in (('brier',DIRECTION[h]),('crps',ANCHOR[h])):
            k=a.nsmallest(1,m).iloc[0]; prior=select(a,model=base).iloc[0]
            n.append(dict(horizon=h,metric=m,candidate=k.model,new=k[m],reference=base,prior=prior[m],difference=prior[m]-k[m]))
    return pd.DataFrame(n)


def report_joint_and_sources():
    family=('stock_pooled_joint','stock_independent','stock_history_joint','stock_conditional_joint','stock_gaussian_shrink',
            'stock_dynamic_factor','stock_heavy_factor','stock_factor_heads')
    jj=index_board(cutoff='preauction_0855',model=family)
    mc=data('monte-carlo-convergence-summary.csv')
    report(8,f'''The main joint stock law keeps **256 simultaneous terminal stock scenarios per origin**, with one joint residual vector per draw and the paired historical index tracking-basis error. We also tested conditionally selected residual rows, Gaussian covariance with **25%** diagonal shrinkage, dynamic market/sector factor innovations, Student-t tail scaling, and independent permutations of the same marginal stock atoms. The independence control retains the same individual stock scenario samples and shuffles their alignment. This makes the cost of removing common shocks visible even when the marginal forecasts are identical. Starting constituent weights convert simultaneous simple returns into index endpoint scenarios with implicit buy-and-hold drift. Complete weighted index atoms give the mean, median, up probability, endpoint, quantiles and tails together.

{table(jj,['horizon','model','n','disjoint','brier','crps','coverage80','width80','log_loss'],19)}

The archive includes **482** simultaneous stock/sector issues and paired basis atoms. Convergence checks synthesize **128, 256 and 1,024** draws from the same draw stream and compare average absolute differences. They quantify simulation variation on a fixed set of forecast dates. A nominal 80% interval that misses many outcomes is a visible failure even when its directional score looks competitive.

{table(mc,['horizon','draw_count','compared_to','mean','p_up','q10','q90','std'],8)}

{links('joint-simultaneous-laws.npz','index-forecast-laws.npz','joint-fit-receipts.csv','joint-forecast-config.json','monte-carlo-convergence-cases.csv','monte-carlo-convergence-summary.csv','tracking-and-dependence.png')}''')
    head=index_headline()
    top=select(index_board(),model=('anchor_aggregate_position','anchor_asymmetry','anchor_location','anchor_scale','anchor_bias','anchor_corporate_proxy',
        'anchor_fixed_joint_mixture','sector_direct_joint','stocks_to_sectors','stock_gaussian_shrink','stock_pooled_joint',
        'pooled_market_factor','date_only_ridge','archived_same_clock','archived_joint_GJR',*ANCHOR.values(),*DIRECTION.values()))
    bounds=data('index-search-adjusted-intervals.csv')
    a=select(bounds,model=('stock_gaussian_shrink','anchor_aggregate_position','anchor_asymmetry','anchor_location'),
             scope='combined',metric=('brier','crps'))
    report(9,f'''A common case book scores the original five- and 21-session cohorts at both historical cutoffs. At 08:55 the rebuilt weekly V17 law and archived neutral/GJR monthly laws remain the available benchmarks. At 09:10 the strongest V20 forecast for each metric is kept as an exact weighted reference. V21’s stand-alone candidates use only the earlier pre-auction data when carried into the 09:10 comparison. Hybrid candidates apply a bias, location, scale, asymmetry, market-wide positioning or weighted corporate reaction correction to the exact existing NIFTY law, using only earlier matured errors. The fixed distribution mixture assigns **25%** to the entire bottom-up stock law. Separate stock, sector and common-factor candidates forecast independently of the archived anchor.

{table(head)}

{table(top,['horizon','cutoff','model','n','active','brier','crps','log_loss','coverage80','width80'],65)}

The weekly pure equity and sector laws were below the original weekly anchors. At the pre-auction monthly cutoff the shrunk-covariance stock law improved the direction point estimate over both archived controls. The strongest rebuilt monthly GJR reference remained competitive on full-distribution loss. The most favorable native monthly result adds aggregate positioning to the existing smoothed-positioning law. This tests an additional common-market forecast correction. The size and direction of the remaining uncertainty are recorded on matched dates.

{table(a,['horizon','cutoff','model','reference','metric','n','gain','adjusted_low','adjusted_high'],44)}

{links('index-model-leaderboard.csv','matched-index-comparisons.csv','index-search-adjusted-intervals.csv','index-forecast-cases.csv.gz','index-forecast-laws.npz','joint-forecast-config.json','forecast-law-examples.json')}''')
    c=data('concentration-cases.csv')
    r=data('concentration-regime-results.csv')
    stats=c.groupby('horizon',as_index=False).agg(n=('day','size'),median_weight_top5=('weight_top5','median'),
        median_effective_weights=('effective_weights','median'),median_expected_effective=('effective_expected_contributors','median'),
        median_realized_effective=('effective_realized_contributors','median'),mean_covered_weight=('realized_weight_covered','mean'),
        median_common_share_proxy=('forecast_common_variance_ratio','median'))
    report(10,f'''Concentration is measured in beginning-index weights, predicted signed contributions and subsequent realized signed contributions. Their effective counts use the square of the sum of absolute contributions divided by the sum of squares. Beginning-weight effective count reduces to the inverse Herfindahl index. Realized contribution concentration is an outcome diagnostic. Forward regime thresholds use only earlier observed values. The high state uses the prior **66th percentile** over up to **100** previous origins and needs at least **35**. NIFTY breadth, IV and observed cross-stock synchronization supply separate comparisons.

{table(stats,None,5)}

{table(select(r,cohort='combined'),['horizon','group','regime','n','disjoint','up_rate','average_actual_rv','anchor_brier','pooled_brier','anchor_crps','pooled_crps'],28)}

{table(data('concentration-association.csv'),None,14)}

The five-heavyweight removal, January random baskets and alternate weighting rules probe whether the same information persists under changing constituent exposure. Canceled stock contributions can reduce the expected aggregate signal even when equity forecasts differ materially. Sector dispersion and cross-stock synchronization are also evaluated against conditional realized volatility.

{links('concentration-cases.csv','concentration-regime-results.csv','concentration-association.csv','daily-constituent-weight-coverage.csv','index-tracking-leaderboard.csv','daily-portfolio-risk-features.csv')}''')
    u=select(data('risk-leaderboard.csv'),scope='combined')
    scenarios=('raw_iv','offshore_plus_domestic','GJR','raw_stock_covariance','shrunk_stock_covariance','independent_equity_variance',
               'recent_proxy_volatility','iv_or_gjr_covariance','iv_or_gjr_cross_sectional','iv_or_gjr_cross_sectional_plus_positions')
    b=select(data('risk-paired-block-intervals.csv'),metric=('mae','qlike'),model=('iv_or_gjr_covariance','iv_or_gjr_cross_sectional','iv_or_gjr_cross_sectional_plus_positions'))
    report(11,f'''The portfolio-risk study uses guarded constituent weights and covariance from up to **63 earlier daily rows**. It checks the full quadratic form, diagonal variance, and a shrinkage estimate retaining **80%** full covariance. Correlation, downside semi-volatility, recent index-proxy variance, variance breadth and stock-level volatility forecasts enter the causal risk correction separately from market-wide positioning. This evaluates the archived future realized-volatility target. The dispersion of terminal return scenarios serves a separate purpose.

The protected raw weekly ATM IV **0.037814 MAE**, weekly offshore/domestic **0.036469 MAE**, monthly GJR **0.033179 MAE and 0.199677 QLIKE**, and **0.152707 / 0.172872** expansion Brier anchors are recovered on their original dates. Equity covariance improves over the independence assumption by a substantial margin. The regularized covariance overlay’s best monthly QLIKE point estimate coexists with a worse MAE. Forecasts that borrow the fixed expansion probability receive a separate transition comparison below.

{table(select(u,model=scenarios),['horizon','model','n','active','mae','rmse','qlike'],26)}

{table(select(u,model=('fixed_iv_rv','student_EGARCH','cross_sectional_transition')),['horizon','model','n','active','brier','log_loss'],8)}

{table(b,['horizon','model','reference','metric','n','gain','adjusted_low','adjusted_high'],14)}

{links('risk-leaderboard.csv','risk-comparison-cases.csv.gz','risk-paired-block-intervals.csv','daily-portfolio-risk-features.csv','risk-fit-receipts.csv','bottom-up-volatility-laws.npz','risk-config.json')}''')
    es=select(data('stock-sector-leaderboard.csv'),group=('event_present','event_absent'),target='absolute',model=(
       'technical','counts','semantic_and_surprise','observed_reaction','pooled'))
    prop=data('source-propagation-scoreboard.csv')
    ps=data('sector-aggregate-position-cases.csv.gz').groupby(['horizon','sector'],as_index=False).agg(
        no_position_crps=('without_position_crps','mean'),position_crps=('with_position_crps','mean'))
    report(12,f'''The source comparisons start from the same dated technical and structural information. They introduce filing counts, semantic or financial surprise information, already-observed event reactions, and delivery or transaction activity one block at a time. The matched event-present subset shows whether company effects also emerge near actual releases. A fixed-law test changes only the company locations in the simultaneous stock scenarios, keeping relative dependence and the index-basis atoms. Its signed weights test whether the company improvements reach index contribution forecasts. A separate native weekly mechanism checks the weighted corporate reaction as a residual correction to the archived V20 distribution.

{table(es,['horizon','cohort','model','group','dates','stock_cases','mae','crps','brier'],42)}

{table(prop,['horizon','cohort','model','n','mean_shift','brier','crps'],36)}

The market and risk models give exchange-wide positioning to aggregate or sector heads. The issue-aware stock panel carries IV and official breadth as common features. The following matched sector experiment compares otherwise identical models with and without aggregate positioning.

{table(ps,None,18)}

{links('source-propagation-scoreboard.csv','fixed-joint-source-ablation-cases.csv.gz','sector-aggregate-position-cases.csv.gz','component-event-clock-audit.csv.gz','market-factor-leaderboard.csv','risk-leaderboard.csv','source-propagation-config.json','feature-definitions.json')}''')


def report_validation():
    synth=data('synthetic-power-summary.csv')
    a=select(synth,assets=128,model=('date_only','shared_pool','partial_sector'))
    v=select(data('stock-leaderboard.csv'),target='absolute',scope='combined',model='pooled')
    e=data('equity-fit-receipts.csv').groupby('horizon',as_index=False).agg(
        train_rows_median=('train_equity_rows','median'),distinct_dates_median=('train_dates','median'),training_issuers_median=('training_assets','median'))
    report(13,f'''V21 scored **{int(v.stock_cases.sum()):,} absolute equity cases** across the two original horizons. They belong to **265** weekly and **217** monthly market dates. Within horizon there are **53** and **11** non-overlapping outcomes, respectively. The panel’s company rows can help estimate shared coefficients. Their common shocks, overlapping outcome windows and related sectors limit what they contribute to learning a broad-market effect. Weight concentration and the stock-to-index variance ratio are reported alongside nominal company counts.

{table(v,['horizon','dates','stock_cases','rank_corr','mae','crps'],6)}

{table(e,None,6)}

The simulation uses **300 replications per design**, **8, 32 and 128** securities, **eight groups**, **53 or 11** distinct training windows, and **128** synthetic test dates. It varies shared slopes, offsetting sector slopes, common shocks, correlated issuer noise and spurious training relationships. Neutral, date-only, pooled and partial-sector estimates see the same simulated dates. The oracle forecast RMSE focuses on the difference from the simulated conditional mean rather than the irreducible realized noise. The estimates apply to the declared simulation only.

{table(a,['horizon','scenario','market_windows','model','index_rmse','oracle_rmse','coef_rmse','better_share'],40)}

{links('synthetic-power-summary.csv','synthetic-power-cases.csv.gz','synthetic-power-config.json','concentration-cases.csv','equity-fit-receipts.csv','index-search-adjusted-intervals.csv')}''')
    val=read('validation-receipt.json')
    n=data('null-refit-summary.csv')
    z=select(data('episode-removal-sensitivity.csv.gz'),cutoff='native_0910',
             type=('largest_gain_21_origins','largest_market_21_origins'),model=('anchor_aggregate_position','anchor_asymmetry','stock_gaussian_shrink'))
    p=select(data('matched-index-comparisons.csv'),cutoff='native_0910',model=('anchor_aggregate_position','anchor_asymmetry'),
             scope=('early','later'),metric=('brier','crps'))
    report(14,f'''The validation checked **{val['event_clock_rows']:,}** event clocks and **{val['forecast_clock_rows']:,}** issued model-case training times against the historical snapshot. All feature preprocessing and target membership use earlier eligible data. The future-label sentinel perturbs unobservable targets. Named feature deduplication and identical expert-law invariance are tested. Weight timing, corporate actions, January eligible random baskets, dominant holdings, missing security weight and randomly assigned sector controls are individually preserved. The dependence lane includes independent, Gaussian, factor, historical conditional, heavy-tail and sample-size controls.

The paired gain intervals use **1,200 circular bootstraps with 21-session blocks**. They adjust within each tested clock, model family and metric. This adjustment does not cover the adaptive V1–V21 research program. The null study runs **23** representative chronological refits and reselects among **four** residual designs with the input history block-permuted. Its observed variant is a small, purpose-matched test with the same refit procedure. The broader leaderboard remains historical and exposed.

{table(n)}

{table(p,['horizon','reference','model','metric','scope','n','active','disjoint','gain'],18)}

{table(z,['horizon','reference','model','metric','type','omitted','n','omitted_gain','remaining_gain'],26)}

The full disjoint-phase record and all calendar-month removals accompany the separate earliest/later tests. Covered dates and changes in tracking error survive in the machine files.

{links('validation-receipt.json','null-refit-cases.csv','null-refit-summary.csv','episode-removal-sensitivity.csv.gz','disjoint-outcome-phases.csv.gz','index-search-adjusted-intervals.csv','index-tracking-leaderboard.csv','component-event-clock-audit.csv.gz')}''')
    r=read('registration.json')
    h=pd.DataFrame(r['hypotheses'])
    report(15,f'''V21 began with **{len(h)} primary hypotheses** registered at **{r['registered_at']}**. The study first tests whether dated weights reconstruct historical price returns, then checks whether the separate stock and sector outcomes improve on simple controls, and then measures how much component information reaches the index. The dependent laws use a small set of fixed designs. The classification and risk lanes remain informative when a weighted direction forecast fails. The full registered record preserves cutoffs, quality minima, references, negative controls, budgets and criteria for follow-up.

{table(h,['name','target_metric','strong_reference','negative_control','minimum','budget','follow_up'],18)}

{links('registration.json','MISSION.md','equity-model-config.json','tracking-config.json','joint-forecast-config.json','synthetic-power-config.json','validation-receipt.json')}''')


def forecast_examples():
    from research.nifty_forecast_v20.modeling import sample_law
    u=data('index-forecast-cases.csv.gz')
    cards=[]
    with np.load(OUT/'index-forecast-laws.npz',allow_pickle=False) as y:
        atoms,weights,end=y['atoms'],y['weights'],y['offsets']
        for h in HORIZONS:
            x=select(u,horizon=h,cutoff='native_0910')
            d=x.day.max()
            xs=select(x,day=d,model=(ANCHOR[h],DIRECTION[h],'stock_pooled_joint','anchor_aggregate_position','anchor_asymmetry'))
            for r in xs.itertuples(index=False):
                i,j=end[r.law:r.law+2];a,w=atoms[i:j],weights[i:j]
                qq=np.array([.05,.10,.25,.50,.75,.90,.95]);v=sample_law(a,w,qq)
                cards.append(dict(classification='frozen historical case',day=d,reference_close=r.reference_close,
                    cutoff=r.cutoff,horizon=h,target_session=r.target_end,model=r.model,p_up=float(w@(a>0)),expected_return=float(w@a),
                    median=float(v[3]),expected_endpoint=float(r.reference_close*(1+w@a)),interval_80=[float(v[1]),float(v[-2])],
                    return_quantiles=dict(zip(qq.astype(str),v.tolist())),endpoint_quantiles=dict(zip(qq.astype(str),(r.reference_close*(1+v)).tolist())),
                    p_below_minus2=float(w@(a<-.02)),p_above_plus2=float(w@(a>.02)),law_index=r.law))
    save('forecast-law-examples.json',dict(law='index-forecast-laws.npz',sha256=sha(OUT/'index-forecast-laws.npz'),cases=cards))


def report_finish():
    head=index_headline()
    q=index_board()
    score=pd.concat([g.nsmallest(4,m).assign(ranked_by=m) for _,g in q.groupby(['horizon','cutoff']) for m in ('brier','crps')])
    report(16,f'''All endpoint rows share the original **173 / 92 / 265 weekly** and **141 / 76 / 217 monthly** comparison cohorts. These represent **53** and **11** non-overlapping windows. Metric and source roles remain visible at each original forecast cutoff. Every leaderboard points to a separately archived case file and, where available, its law. The date-level stock tables describe prediction of security and sector targets. Index gains are evaluated on the index itself.

{table(head)}

{table(score,['horizon','cutoff','ranked_by','model','n','active','disjoint','brier','crps','log_loss','accuracy','balanced_accuracy','mae','rmse','rank_corr','coverage80','width80'],36)}

{links('stock-leaderboard.csv','stock-probability-calibration.csv','sector-forecast-leaderboard.csv','market-factor-leaderboard.csv','index-tracking-leaderboard.csv','index-model-leaderboard.csv','matched-index-comparisons.csv','index-search-adjusted-intervals.csv','index-probability-calibration.csv','risk-leaderboard.csv','synthetic-power-summary.csv','forecast-law-examples.json')}''')
    f=read('forward-ledger.json')
    s=read('forward-input-receipts.json')
    legacy=pd.DataFrame([dict(version=x['version'],key=x['key'],issued=x['issued'],target=x['target_sessions'][-1],
                              realized=x['realized_return'],status=x['maturity']) for x in f['original_issues']])
    references=pd.DataFrame([dict(version=x['version'],model=x.get('model',x.get('name')),issued=x['issued_at'],horizon=x['horizon'],
        target=x['target_sessions'][-1],status=x['status'],available_targets=len(x['confirmed_sessions'])) for x in f['inherited_v19']+f['inherited_v20']])
    report(17,f'''V21 refreshed **{len(f['sessions'])} certified cash-index outcomes** after the historical freeze, preserving the authoritative close and capture hash for each. It collected **{sum(k['family']=='postfreeze_cash' and 'file' in k for k in s['captures'])} completed post-freeze equity cash archives** in a separate folder. A V21 read-only replay produced additional dated delivery receipts. The close verified by V19 for November 25 continues to support the original V4 five-session late diagnostic, **25,387.40 to 25,819.25**, a **+1.7010%** return with the original **70.84% and 68.05%** up probabilities. The remaining legacy records mature on their own target sequences.

{table(legacy,None,8)}

{table(references,None,9)}

Existing evening references cover weekly and monthly neutral returns, weekly raw and blended ATM IV, weekly and monthly cash GJR and monthly Student-t EGARCH. The November 25 participant open-interest and volume files have dated staged receipts. The next original morning decision requires an authentic 08:55 source snapshot and, for the native laws, the 09:10 parent built with current eligible market inputs. The readiness registry lists the exact dependencies separately for GIFT, V14, V18, V19 and both V20 corrections. An original-clock replay of each candidate on the frozen past is recorded as a historical rehearsal. The latest V21 run carries the prepared reference panel and records **{len(f['new_issues'])} newly issued forecasts**. The stage-one results support continued collection of common-risk and positioning tests under the same issue guard.

{table(data('forward-readiness.csv'),None,8)}

{links('forward-ledger.json','forward-refetch-receipt.json','forward-input-receipts.json','forward-native-rehearsal.csv','forward-readiness.csv')} · [Official 2026 cash-market calendar](https://archives.nseindia.com/content/circulars/CMTR71775.pdf)''')
    tr=select(tracking(),model=MAIN).set_index('horizon')
    raw=index_board(cutoff='preauction_0855',horizon=21).set_index('model')
    native=index_board(cutoff='native_0910',horizon=21).set_index('model')
    ab=index_board(cutoff='native_0910',horizon=5).set_index('model')
    gauss=raw.loc['stock_gaussian_shrink'];v=raw.loc['archived_joint_GJR'];m=native.loc['anchor_aggregate_position'];a=ab.loc['anchor_asymmetry']
    sides=select(data('matched-index-comparisons.csv'),cutoff='native_0910',horizon=21,model='anchor_aggregate_position',reference=ANCHOR[21],scope=('early','later'))
    ci=select(data('index-search-adjusted-intervals.csv'),cutoff='native_0910',scope='combined',
              metric=('brier','crps'),model=('anchor_aggregate_position','anchor_asymmetry'))
    ci=pd.concat([select(ci,horizon=5,model='anchor_asymmetry',reference='price_reaction'),
                  select(ci,horizon=21,model='anchor_aggregate_position',reference='smooth5')])
    report(18,f'''**Dated weights reconstructed the realized index closely.** The newly recovered 22 dated constituent snapshots tracked cash NIFTY daily within **{tr.loc[1,'mae']*10000:.3f} basis points MAE**, with **{tr.loc[1,'correlation']:.6f}** correlation on matched dates. This establishes a much stronger index-contribution measurement than the earlier liquidity-basket proxy. Index forecasts still depend on future market returns, individual returns and shared risk. Strong realized tracking creates room to measure those errors directly.

**Pooled estimation reduced some security forecast errors.** It helped against many independent stock models, while date-level ranks stayed small and randomized stock alignment remained competitive. Pure stock and sector forecasts trailed the native directional anchors. The pre-auction shrunk-covariance stock model had **{gauss.brier:.6f} Brier and {gauss.crps:.6f} CRPS**, versus **0.250000** neutral Brier and the same-clock GJR **{v.crps:.6f} CRPS**. This leaves a limited earlier-clock result with explicit covariance and benchmark dependence.

**The best native monthly point result stayed anchored to the index and aggregate positioning.** It reached **{m.brier:.6f} Brier and {m.crps:.6f} CRPS**. Weekly native asymmetry reached **{a.crps:.6f} CRPS** and the prior V20 training-omission model still led weekly Brier. The monthly adjustment’s gain is concentrated in the earlier group. Its later group gave back both direction and distribution improvements. The table preserves those signs and the complete-population paired bands. The monthly result is based on **11** disjoint windows. Study-wide historical research exposure and adjustment limits still govern interpretation.

{table(head)}

{table(sides,['scope','reference','metric','n','active','disjoint','gain'],6)}

{table(ci,['horizon','model','reference','metric','n','gain','adjusted_low','adjusted_high'],6)}

**Cross-stock dependence was consequential.** Independently aligned stock paths sharply under-covered actual index outcomes. Preserving joint shocks is essential for uncertainty, even when point forecasts add little. Equity covariance supplied a competitive monthly variance-loss point estimate after anchoring to GJR, while the archived MAE and volatility-transition controls were stronger. The genuine forward files give these results a route to testing on newly accrued dates under their original issue rules.

{links('V21_INDEX_RETURN_RECONSTRUCTION.md','V21_JOINT_EQUITY_RETURN_DISTRIBUTIONS.md','V21_TOP_DOWN_VERSUS_BOTTOM_UP.md','V21_COMPLETE_MODEL_COMPARISON.md','V21_VALIDATION_AND_FALSIFICATION.md','V21_FORWARD_RESEARCH_LEDGER.md')}''')
    report(19,'''1. Capture original-clock data snapshots for the weekly V20 anchors and the 21-session V19/V20 positioning anchors. Retain the supported evening forecasts in the same ledger under their actual timestamps.
2. Prospectively compare the aggregate positioning overlay, unmodified smoothed law and neutral/GJR controls after the live source and parent checks have passed. Predefine the later-cohort and non-overlapping windows.
3. Use newly archived month-end weights as released and target the daily constituent, divisor and corporate-action transitions still responsible for the largest reconstruction discrepancies. Capture the actual publication time at download.
4. Preserve the shrunk-covariance pre-auction stock law and its independent control on the same timestamps. Increase scenario draws for probability comparisons where Monte Carlo variation is similar to the observed difference.
5. Continue work on dated company results and distinct within-sector targets. For every proposed gain, test the matched issuer-randomization control and its effect on weighted index contributions.

'''+links('registration.json','V21_FINAL_RESEARCH_CONCLUSIONS.md','V21_FORWARD_RESEARCH_LEDGER.md'))


def figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    a=data('daily-index-reconstruction.csv').dropna(subset=[MAIN,'sector_simplex','actual'])
    b=index_board(cutoff='preauction_0855')
    fig,axes=plt.subplots(1,2,figsize=(12,5.5),gridspec_kw={'width_ratios':[1.10,1.]})
    fig.subplots_adjust(left=.085,right=.965,top=.82,bottom=.23,wspace=.27)
    x=axes[0]
    for col,color,label in [('sector_simplex','#de8453','Statistical sector mix'),(MAIN,'#205c83','Dated constituent weights')]:
        x.scatter(100*a.actual,100*a[col],s=14,color=color,alpha=.55,label=label,linewidth=.03)
    limits=[-5.8,5.8]
    x.plot(limits,limits,color='#506175',linestyle='--',linewidth=.8)
    x.set(xlim=limits,ylim=limits,xlabel='Official daily NIFTY return (%)',ylabel='Reconstructed return (%)')
    x.set_title('Realized index reconstruction',loc='left',fontweight='bold',fontsize=12)
    x.legend(frameon=False,loc='upper left',fontsize=8)
    x=axes[1]
    bars=[('stock_pooled_joint','#205c83','Joint historical shocks'),('stock_independent','#de8453','Independent asset shocks'),
          ('stock_gaussian_shrink','#73a49d','Shrunk covariance')]
    ticks=np.arange(2)
    for j,(model,c,label) in enumerate(bars):
        v=select(b,model=model).set_index('horizon').coverage80.reindex(HORIZONS)
        container=x.bar(ticks+(j-1)*.22,100*v,.20,color=c,label=label)
        x.bar_label(container,fmt='%.1f%%',padding=3,fontsize=8,color='#182b3a')
    x.axhline(80,color='#506175',linestyle='--',linewidth=.8,label='Nominal coverage')
    x.set_xticks(ticks,['5 sessions','21 sessions']);x.set_ylim(0,99);x.set_ylabel('Actual returns inside the 80% interval (%)')
    x.set_title('Coverage of stock-based forecasts',loc='left',fontweight='bold',fontsize=12)
    x.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,-.125),ncol=2,fontsize=8)
    for x in axes:
        x.grid(axis='y',color='#e7ebef',linewidth=.7)
        x.set_axisbelow(True)
        x.spines[['top','right']].set_visible(False)
    fig.suptitle('NIFTY V21 · Tracking accuracy and cross-stock dependence',fontsize=16,fontweight='bold',x=.066,ha='left')
    fig.text(.070,.055,'Matched frozen-vintage observations. Tracking uses realized constituent returns. Forecast coverage uses only eligible inputs.',fontsize=8.5,color='#40546a')
    fig.savefig(OUT/'tracking-and-dependence.png',dpi=160,facecolor='white')
    plt.close(fig)


def index():
    n=read('universe-receipt.json')
    steps=('common','acquire','reference','universe','reconstruction','panel','learning','joint','risk','power','specialization','evidence','forward','report','verify')
    body='# Reproduce V21\n\nRun from the trading-desk root using the existing project environment. The forward module intentionally refreshes separately observed inputs and outcomes.\n\n'
    body+='```powershell\n$env:PYTHONDONTWRITEBYTECODE = "1"\n$env:OPENBLAS_NUM_THREADS = "1"\n'
    body+='\n'.join('.venv/Scripts/python.exe -m research.nifty_forecast_v21.'+k for k in steps)+'\n```\n\n'
    body+='The [research index](NIFTY_V21_RESEARCH.md) links the exact reports and the [manifest](manifest.json) binds reproducible data and code.\n'
    (OUT/'README.md').write_text(body,encoding='utf-8')
    ordered='\n'.join(f'{i}. [{name.replace("_"," ").title()}](V21_{name}.md)' for i,name in enumerate(REPORTS,1))
    (OUT/'NIFTY_V21_RESEARCH.md').write_text(f'''# NIFTY V21 bottom-up forecasting and index reconstruction

The frozen history uses **{FIRST} through {FREEZE}**. The archive contains **{n['weight_csv_vintages']} monthly constituent snapshots**, **{n['modeled_symbols']} modeled equity series** and the exact original five- and 21-session NIFTY forecast cohorts. The forward ledger records separately acquired post-freeze outcomes and authentic issue times.

[Findings](V21_FINAL_RESEARCH_CONCLUSIONS.md) · [Tracking](V21_INDEX_RETURN_RECONSTRUCTION.md) · [Model comparison](V21_COMPLETE_MODEL_COMPARISON.md) · [Forward ledger](V21_FORWARD_RESEARCH_LEDGER.md)

## Research reports

{ordered}

## Reproduction

{links('README.md','MISSION.md','registration.json','tracking-and-dependence.png','forecast-law-examples.json','source-receipt.json','verification.json','manifest.json')}
''',encoding='utf-8')


if __name__=='__main__':
    forecast_examples()
    report_universe()
    report_components()
    report_joint_and_sources()
    report_validation()
    report_finish()
    figure()
    index()
    print('Published all 19 requested V21 reports',flush=True)
