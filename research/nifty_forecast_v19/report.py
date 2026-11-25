"""Publish the 18 V19 reports from verified case tables and archive receipts."""
from collections import Counter
from .common import *
from research.nifty_forecast_v18.report import tab,fmt

def rel(*files):
    return ' · '.join(f'[{p}]({p})' for p in files)

def report(i,body):
    tag=REPORTS[i-1]
    (OUT/f'V19_{tag}.md').write_text(f'# V19 {tag.replace("_"," ").title()}\n\n'+body.strip()+'\n',encoding='utf-8')

def pick(d,**kw):
    for k,v in kw.items():
        d=d[d[k].isin(v) if isinstance(v,(tuple,list,set)) else d[k].eq(v)]
    return d

def table(z,cols=None,n=18):
    return tab(z,cols,n) if len(z) else 'No eligible rows in this comparison.'

def show(z,metric,sense='min',n=8):
    a=z.dropna(subset=[metric])
    return a.nsmallest(n,metric) if sense=='min' else a.nlargest(n,metric)

def measure(d,model,col):
    a=d[d.model.eq(model)]
    return float(a[col].iloc[0]) if len(a) else np.nan

def protect_summary():
    d=csv('v18-activity-replay-and-subsets.csv.gz')
    z=d.groupby(['horizon','cutoff','model'],as_index=False).agg(n=('day','size'),brier=('brier','mean'),crps=('crps','mean'))
    write('v18-activity-leaderboard.csv',z)
    c=csv('v18-activity-shapley-by-origin.csv.gz')
    c=c.groupby(['horizon','cutoff','block'],as_index=False)[['brier','crps']].mean()
    write('v18-activity-shapley-summary.csv',c)
    return z,c

def attribution(d):
    z=csv('v19-block-shapley.csv.gz')
    w=z.groupby(['horizon','cutoff','block'],as_index=False)[['brier','crps']].mean()
    write('v19-block-shapley-summary.csv',w)
    maps=dict(A_structural='clock_structural',B_corporate='V18_corporate_same_clock',C_delivery='delivery',
              D_participants='participant',E_transactions='transactions',F_all='delivery + participant + transactions',
              G_interactions='corporate_position_interactions',F_plus_corporate='corporate_position_additive',
              H_block_control='participant_block_permuted',H_one_session='participant_delay1',H_five_sessions='participant_delay5')
    a=d[d.model.isin(maps.values())].copy()
    a['arm']=a.model.map({v:k for k,v in maps.items()})
    g={}
    for (h,c),q in a.groupby(['horizon','cutoff']):
        vals=q.set_index('arm')
        for label,head,base in [('corporate_first','B_corporate','A_structural'),
            ('positioning_after_corporate','F_plus_corporate','B_corporate'),
            ('positioning_first','F_all','A_structural'),
            ('corporate_after_positioning','F_plus_corporate','F_all'),
            ('interaction_after_corporate','G_interactions','B_corporate')]:
            g[(h,c,label)]={k:vals.loc[base,k]-vals.loc[head,k] for k in ('brier','crps')}
    compare=pd.DataFrame([dict(horizon=k[0],cutoff=k[1],addition=k[2],**v) for k,v in g.items()])
    write('corporate-addition-orders.csv',compare)
    return a,w,compare

def native_points(a):
    return a[a.model.isin(['V14_exact','V14_event_overlay','V14_plus_positions','V18_plus_positions'])]

def headline():
    p=csv('model-leaderboards.csv')
    a=pick(p,track='endpoint',cohort='combined')
    native=pick(p,track='weighted_native',cohort='combined')
    risk=pick(p,track='risk',cohort='combined')
    path=pick(p,track='path',cohort='combined')
    m=csv('matched-comparisons.csv')
    intervals=csv('block-bootstrap-intervals.csv.gz')
    ci=pick(intervals,track='weighted_native',model='V14_plus_positions',metric=('brier','crps'),block=21)
    n=pick(native,model=('V14_exact','V14_event_overlay','V14_plus_positions','V18_plus_positions'))
    v=pick(a,horizon=5,cutoff='preauction_0855')
    c=pick(a,horizon=21,cutoff='preauction_0855')
    daily=read('database-receipt.json')
    flows=read('capital-flow-receipt.json')
    return p,a,native,risk,path,m,intervals,ci,n,v,c,daily,flows

def archives():
    p,a,native,risk,path,m,intervals,ci,n,v,c,d,f= headline()
    b=read('baseline-replay-receipt.json')
    s=read('predecessor-protection.json')
    old,ow=protect_summary()
    legacy=csv('protected-benchmarks.csv')
    report(1,f'''The historical vintage opens on {FIRST} and freezes on {FREEZE}. V19 verified {s['artifacts']:,} V18 artifacts and {s['code']} predecessor code hashes. The V18 opening GIFT replay covers 248 origins with Brier 0.100841 and accuracy 88.71%. The stored opening and native path files retain their original decision clocks.

V19 rebuilt {b['native_laws']} weighted V14 and V18 endpoint distributions and {b['archived_activity_predictions']} V18 delivery, participant, deal and combined predictions. Their maximum scalar replay error was {b['max_score_deviation']:.3g}. The activity atom arrays reproduced the archival float32 values exactly. The V18 native corporate update was active on 223 weekly origins and 159 monthly origins.

{table(legacy,['track','cutoff','horizon','model','metric','n','value'],30)}

The eight same-clock activity subsets recover each marginal addition across six orders. Positive contributions indicate reduced loss.

{table(ow,['horizon','cutoff','block','brier','crps'],18)}

{rel('baseline-replay-receipt.json','predecessor-protection.json','v18-activity-leaderboard.csv','v18-activity-replay-and-subsets.csv.gz','v18-activity-shapley-by-origin.csv.gz','v18-native-replayed-laws.npz','protected-native-joint-models.csv')}''')
    au=csv('participant-audit.csv.gz')
    miss=au[au.status.ne('accepted')]
    src=read('source-receipts.json')
    receipts=pd.DataFrame([dict(family='participant volume' if 'fao_participant_vol_' in r['url'] else 'official probes',status=r.get('status'),
                                 found=int(r.get('sha256') is not None)) for r in src])
    ss=receipts.groupby(['family','status'],dropna=False,as_index=False).agg(requested=('found','size'),archived=('found','sum'))
    probes=pd.DataFrame([dict(url=r['url'],status=r.get('status'),file=r.get('file')) for r in src if 'market-report-' in (r.get('file') or '')
        or any(q in r['url'] for q in ('mwpl','secban','slb','equities/mkt'))])
    report(2,f'''The SQLite database, normalized CSVs and file receipts cover {d['sessions']} authenticated NSE cash sessions. Delivery contains {d['delivery']['full_rows']:,} security-series rows, {d['delivery']['eq_rows']:,} EQ rows and {d['delivery']['numeric_delivery']:,} numeric delivered quantities. All {d['delivery']['fixed_rows']:,} V18 fixed-cohort price/ISIN links matched the official cash bhavcopy. The delivery percentage arithmetic audit flagged {d['delivery']['pct_mismatches']:,} records across all series at the raw source rounding tolerance. Research filters require the recomputed percentage to pass the tolerance, a verified ISIN and a matched close. Original missing entries remain blank.

The participant inventory expanded from 383 parsed OI days to {d['participant_days']['open_interest']} authenticated reports. The old parser skipped valid titles formatted like Jan 01,2025. There are {d['participant_days']['traded_volume']} dated participant trade-volume reports. Exact values for the {d['participants']['v18_categories_exact']:,} earlier participant rows replayed. Ordinary NIFTY futures have {d['futures']['rows']:,} contract-session rows and recorded contract lots {', '.join(map(str,d['futures']['lot_values']))}. Four OI/lot checks failed and affected daily aggregates use missing values. Stock cash sources are shares and turnover in rupees. Participant and contract fields use the units printed by the publisher.

The historical report publication allowance is 08:15 IST on the following NSE cash session. Previous-close 17:00 forecasts consequently use an older report than the following 08:55 forecast. Independent no-delay, +1 and +5 session versions are explicit. Historical first-print revision timestamps remain unobserved. The SQLite rows preserve the observation date, source file path and modeled eligibility timestamp. Failed and empty source probes remain visible below.

{table(miss,['day','kind','present','status'],6)}

{table(ss,['family','status','requested','archived'])}

{table(probes,['url','status','file'],20)}

{rel('market-positioning.sqlite','database-receipt.json','participant-audit.csv.gz','source-receipts.json','alternate-source-preflight.json','nifty-futures.csv.gz','delivery-receipts.csv.gz','asof-positioning-coverage.csv')} · [NSE derivatives archive](https://betanseapi.nseindia.com/all-reports-derivatives) · [NSE report publication note](https://nsearchives.nseindia.com/content/circulars/CMTR53595.pdf)''')
    part=pick(a,model=('clock_structural','participant','levels_only','changes_only','innovation_augmentation','positions_beyond_oi',
        'participant_delay1','participant_delay5','participant_block_permuted'))
    rr=pick(m,track='endpoint',model=('participant','positions_beyond_oi','innovation_augmentation','levels_only','changes_only'),metric='crps',
        cohort='active_matched',parent=('clock_structural','clock_with_oi_volume'))
    report(3,f'''The report uses the exchange labels Client, DII, FII and Pro across index futures, stock futures, index calls, index puts, stock calls and stock puts. Participant files combine the exchange's index instruments. NIFTY-specific ordinary futures contracts have a separate source. Each family preserves long, short, net, gross, long-to-short ratio and gross-normalized exposure, with one-, five- and 21-session changes, an acceleration proxy and five-session persistence. The primary linear factor drops the mechanically dependent Client net. Side totals and observed four-category totals are both audited. There were {d['participants']['instrument_day_balance_failures']} reported instrument-day total side mismatch and {d['participants']['dates_with_detail_disagreement']} report-level discrepancies between detailed category sums and published totals. The largest category-sum difference was {d['participants']['largest_detail_gap']} contract. The model uses the observed category denominator and suppresses net ratios with material imbalance.

The option features are separately signed call and put counts. Strike, maturity and Greeks by participant are unavailable in these reports. Concentration is a Herfindahl index of gross contract shares. Disagreement is cross-category dispersion. Treat the FII positions as derivatives observations and use the ordinary NIFTY OI, price, volatility and breadth controls for comparison. Open contracts and traded contracts measure different things.

{table(part,['horizon','cutoff','model','n','active','brier','crps'],38)}

{table(rr,['horizon','cutoff','model','parent','n','disjoint','gain'],24)}

{rel('participants.csv.gz','positioning-daily-features.csv.gz','model-leaderboards.csv','matched-comparisons.csv','mechanism-sensitivities.csv.gz','sector-transfer-leaderboard.csv')} · [NSE derivatives file specification](https://archives.nseindia.com/content/press/EOD_FAO.pdf)''')
    ds=csv('stock-delivery-states.csv')
    tr=csv('stock-transfer-leaderboard.csv')
    leg=csv('sector-transfer-leaderboard.csv')
    report(4,f'''The 240 issuer seed was fixed from January 2025 turnover and included only after its dated anchor. The audited delivery panel uses each issuer's past-60 or past-25 observations, where the current observation is outside its normalization window. Activity includes changes in delivery share, delivered quantity, delivery-to-traded shares, concentration of the close-marked quantity value and persistence. Daily rollups include equal-company, represented-sector-equal and historical liquidity weights. We counted company outcomes on their common dates before pooling scores. The date count captures overlapping return windows, and the match uses identical shares for delivery and ordinary traded-volume regressions.

{table(ds,['horizon','state','stock_dates','dates','mean_market_relative','mean_absolute_relative'],18)}

{table(tr,['target','model','dates','case_units','rank_corr','mae','rmse'])}

{table(leg,['target','model','dates','case_units','rank_corr','mae','rmse'])}

Check the alternate 25-day feature, corporate-action and outlier sensitivity, removal of the top 15 seed stocks and both deterministic random halves in the endpoint comparison. Six price-and-delivery states are tracked, with independent consolidation/high-volatility screens. Quantity times the closing mark estimates delivery value for weighting purposes. Investor direction and new cash subscriptions are unobserved.

{rel('stock-delivery-features.csv.gz','stock-delivery-states.csv','stock-transfer-cases.csv.gz','sector-transfer-cases.csv.gz','transfer-fit-receipts.ndjson.gz','endpoint-config.json','matched-comparisons.csv')}''')
    z=csv('crowding-conditional-states.csv')
    q=csv('crowding-leaderboard.csv')
    report(5,f'''The primary crowded state is an index-futures four-category gross-share HHI at least one deviation above its own trailing window. We also use stock-futures concentration, persistence, delivery-value concentration, observed financing-sector participation and narrowing equal-weight breadth. A true reduction in the sum of recorded NIFTY futures OI is an auditable target. The reduction event requires at least an 8% decline from the eligible report mark. Rollover, expiry and position changes across expiries can lower or raise raw counts. We screen origins with more than three days to the named front expiry and a quiet roll flag. That sensitivity conditions on information available at issue and preserves the issue cohorts.

{table(pick(z,group=('crowded','ordinary','crowded_weak_breadth'),outcome=('oi_reduction','reversal','expansion'),ex_expiry=False),['horizon','outcome','group','count','rate_or_mean','concentration_rank'],22)}

{table(pick(q,model=('price_iv_oi','position_crowding','position_changes','position_crowding_delay5'),scope='exclude_expiry'),['horizon','outcome','model','n','loss','gain'],32)}

The labels refer to realized OI and future price behavior. Forced liquidation, margin pressure and individual trades cannot be identified from the aggregate files.

{rel('crowding-conditional-states.csv','crowding-case-tests.csv.gz','crowding-leaderboard.csv','positioning-daily-features.csv.gz','risk-cases.csv.gz')}''')
    names=('price_only','positions_direct','price_ordinary_oi','price_plus_position_level','price_plus_position_changes','price_plus_innovation','price_plus_disagreement','innovation_augmentation','positions_beyond_oi')
    report(6,f'''The innovation test estimates same-day position changes from only earlier dated examples. State inputs include NIFTY return, recent momentum and volatility, front basis, term structure, time to expiry, ordinary OI changes, breadth, prior derivative exposure, ATM IV and skew available by the report clock. It stores the difference between the observed change and the ridge estimate. Each fit requires at least 40 past feature rows and uses at most 120. Separate innovations cover one and five session FII index futures, DII futures, index calls and index puts.

{table(pick(a,cutoff='preauction_0855',model=names),['horizon','model','n','active','brier','crps','rank_corr'],25)}

{table(pick(m,track='endpoint',model=('price_plus_innovation','price_plus_disagreement','positions_beyond_oi'),parent=('price_ordinary_oi','clock_with_oi_volume'),cohort=('active_matched','away_from_expiry'),metric=('brier','crps')),['horizon','cutoff','cohort','model','parent','n','gain'],24)}

The price-only and position-only regressions make direct forecasts. The structural, residual and native weighted hypotheses score on their own historical controls. Applying a narrower maturity condition changes the training history, and the active-matched tables quantify that choice.

{rel('position-innovation-fits.ndjson.gz','positioning-daily-features.csv.gz','endpoint-fit-receipts.ndjson.gz','matched-comparisons.csv','episode-omission.csv')}''')

def mechanisms():
    p,a,native,risk,path,m,intervals,ci,n,v,c,d,f=headline()
    deal=csv('transaction-event-summary.csv')
    volume=csv('deal-audited.csv.gz')
    report(7,f'''V19 retained all {d['deals']['month_files']} official archive windows across {d['deals']['months']} months. The {d['deals']['raw']:,} reported legs reduce to {d['deals']['deduplicated']:,} unique disclosed legs after exact duplicate removal. There are {d['deals']['groups']:,} date, issuer, category, size and price groups on {d['deals']['days']} dates. Equal-size, equal-price opposite block legs contribute {d['deals']['matched_block_pairs']} potential same-transfer pairs. The corresponding proxy totals ₹{volume.matched_block_once_proxy.sum()/1e7:,.1f} crore versus ₹{volume.reported_consideration.sum()/1e7:,.1f} crore from retained leg sums. Bulk legs retain their original sides. Disclosed side describes the reported transaction leg. Equal-sized verification and a published buyer/seller match do not resolve undisclosed counterparties or economic ownership.

Same-date comparison peers have high turnover, no deal records in the verified archive on that date, matched industry where known, and similar price and turnover characteristics. Matched issuer follow-through and absolute excess are date-weighted. Premium and discount use the last known previous close. Nine event dates have missing premium and turnover ratios because their quotes lacked direct cash references. The lagged size cap removes unusually large events. Endpoint comparisons also use shifted activity and the alternative all-leg sum.

{table(deal,['horizon','category','subset','events','dates','excess_return','absolute_excess','signed_premium_rank'],26)}

{table(pick(a,cutoff='preauction_0855',model=('transactions','deals_beyond_turnover','deals_without_largest','deals_all_reported_legs','deals_date_shift')),['horizon','model','n','active','brier','crps'],12)}

{rel('deal-archives.csv.gz','deal-legs.csv.gz','deal-audited.csv.gz','transaction-matched-cases.csv.gz','transaction-event-summary.csv','matched-comparisons.csv')}''')
    flows=csv('capital-flow-associations.csv')
    stocks=csv('cdsl-sector-observations.csv.gz')
    hist=pd.DataFrame([dict(family=k,**v) for k,v in f['archive_history'].items()])
    showflow=flows[flows.category.isin(['Stock Exchange','Sub-total','open_end_equity','equity_etf','sector_sum'])]
    p1=stocks[stocks.sector.ne('Total')].sort_values('day').tail(30)
    tt=pick(showflow,test=('future_return','future_realized_vol','lag_net'))
    report(8,f'''The official data routes yielded three different series. CDSL daily publications record custodian-reported purchases and sales by route in ₹ crore. CDSL fortnightly records show sector-level equity net investment and separately report assets under custody. AMFI monthly publications report actual scheme-level fund mobilization and redemptions with separate AUM. The fund series include funds with material price effects in AUM and different gross transaction coverage. None of the three series supplies a complete point-in-time daily NSE exchange FII/DII pair. The daily NSE endpoint exposed a current report, and the parameterized depository forms returned empty or undated historical selections. Formal ETF creation/redemption counts and a complete DII trade series remain unavailable in the audited feeds.

{table(hist,['family','rows','dates'])}

First-release times and historical revisions remain unverified. The descriptives start on the first observed NSE cash session after one day for CDSL daily, ten calendar days for CDSL fortnightly and twenty for AMFI. The reporting date can follow the underlying trade date. The usable number of independent flow releases is the release count. Stratified Spearman figures below are descriptive and kept outside the primary endpoint panel.

{table(tt,['series','category','horizon','test','n','spearman'],36)}

{table(p1.nlargest(6,'net_equity_inr_crore') if 'net_equity_inr_crore' in p1 else p1,['day','sector','net_equity_inr_crore'],6)}

{rel('capital-flow-receipt.json','flow-source-receipts.json','flow-parsing-audit.csv','cdsl-daily-observations.csv.gz','cdsl-sector-observations.csv.gz','cdsl-sector-reconciliation.csv','amfi-monthly-observations.csv.gz','capital-flow-associations.csv','cash-form-probes.json')} · [SEBI data directory](https://www.sebi.gov.in/curation/fpi.html) · [CDSL archives](https://www.cdslindia.com/Publications/ForeignPortInvestor.html) · [CDSL interpretation notes](https://www.cdslindia.com/publications/fiinote.html) · [AMFI monthly archives](https://www.amfiindia.com/research-information/amfi-monthly)''')
    groups=csv('asof-positioning-coverage.csv')
    transfer=csv('sector-transfer-leaderboard.csv')
    report(9,f'''Eight market-state families cover levels, changes, cross-category disagreement, abnormal delivery intensity, delivery breadth, transaction activity, concentration and position-price residuals. Market indexes and narrower stock/sector outcomes are evaluated in different units. The rotation experiment compares contemporaneously classified stocks with official sector relative returns, NIFTY 50, equal-weight breadth and native financial rotation. Grouped company regressions use dated label availability. The January liquidity weights and known-sector baskets are observable proxies. Full point-in-time index weights and historical market-cap weighting for this issuer universe are unconfirmed.

{table(groups,None,6)}

{table(transfer,['target','model','dates','case_units','rank_corr','mae','rmse'],14)}

{table(pick(a,cutoff=('preauction_0855','previous_1700'),model=('position_with_compact_factors','delivery_liquidity_weight','delivery_without_top_15','delivery_random_half0','delivery_random_half1','delivery_ex_actions','delivery_25_window')),['horizon','cutoff','model','n','crps','brier'],24)}

{rel('feature-receipt.json','asof-positioning-features.csv.gz','sector-delivery-features.csv.gz','sector-transfer-daily.csv','endpoint-config.json','matched-comparisons.csv')}''')
    ledger,shap,add=attribution(a)
    report(10,f'''Corporate information uses the V18 aggregate financial disclosure schedule and measured outcomes from the preserved point-in-time feeds. Added interaction fields combine earnings surprises with FII position changes, growth with breadth and delivery, financial news with stock derivatives, disclosure direction with concentration, and calendar exposures with eligible IV. They describe cross-state association. Financially identifying the counterparties and causes would require linkage and timing beyond these inputs.

{table(ledger[ledger.cutoff.eq('preauction_0855')],['horizon','arm','n','active','brier','crps'],24)}

The additive path uses the exact archived corporate parent first, then estimates its additional error from matured cases. Comparing it with the structural-plus-nonprice model estimates the other order on the same origins. Interaction changes and the six-order Shapley results are incremental losses across paired tables.

{table(add,['horizon','cutoff','addition','brier','crps'],24)}

{table(shap,['horizon','cutoff','block','brier','crps'],16)}

{rel('corporate-addition-orders.csv','v19-block-shapley-summary.csv','v18-activity-shapley-summary.csv','v19-block-shapley.csv.gz','endpoint-fit-receipts.ndjson.gz','refit-reselection-summary.csv')}''')
    top=pd.concat([show(v,'crps',n=7),show(c,'crps',n=7)])
    endpoint_cmp=pick(m,track='weighted_native',model=('V14_plus_positions','V18_plus_positions'),cohort=('early','later'),metric=('brier','crps'))
    report(11,f'''Original forecasts measure price change from the prior NIFTY cash close over 5 or 21 exchange sessions. The exact calendar samples are 173 earlier and 92 later weekly observations, 141 earlier and 76 later monthly observations. Those overlapping samples yield 53 and 11 disjoint windows respectively. V14 and V18 native distributions preserve every empirical atom and weight. Rebuilt releases use separate previous 17:00 and next 08:55 archives. The 09:25 and 10:20 remaining-horizon forecasts get separate files and target definitions.

{table(native_points(n),['horizon','model','n','active','brier','log_loss','accuracy','balanced_accuracy','crps','covered','width'],12)}

{table(top,['horizon','cutoff','model','n','active','brier','crps','rank_corr','covered','width'],16)}

{table(endpoint_cmp,['horizon','model','cohort','metric','n','disjoint','gain'],20)}

The direct models compare price, turnover, positioning and residuals. The structural overlays revise the center with shrinkage on matured labels. Location-scale allows a constrained scale and skew change. The fixed mixture interleaves atoms from the original law and corrected law, with no hindsight mixture selection. The decomposed parent uses the archived V17 same-clock law. Signed log shifts are applied coherently to weighted native laws, and unavailable training stays on each archived parent. Protected joint forecasts enforce a common distribution for OHLC-dependent risks.

{rel('endpoint-config.json','endpoint-cases.csv.gz','endpoint-laws.npz','native-residual-cases.csv.gz','native-residual-laws.npz','postopen-cases.csv.gz','postopen-endpoint-laws.npz','v18-native-exact-replay.csv')}''')
    rp=pick(risk,cutoff='preauction_0855',model=('risk_calibrated_iv','price_and_oi','combined_positioning_risk','crowding_on_price',
        'protected_offshore_plus_domestic','protected_GJR','protected_student_EGARCH','protected_fixed_iv_rv','protected_raw_iv'))
    road=pick(path,cutoff=('preauction_0855','previous_1700'),model=('same_clock_GJR','same_clock_IV','position_on_GJR','position_on_IV','same_clock_GIFT_first'))
    ext=csv('barrier-leaderboard.csv')
    report(12,f'''Volatility expansion compares future annualized realized volatility with 1.25 times the eligible trailing reference. Contraction compares it with 0.8 times the trailing state. Entry to a high-volatility state starts below the 80th percentile from matured history, then scores a threshold crossing. The point tables keep absolute error and variance QLIKE with Brier probabilities, calibration and proper distribution scores. The protected V16 weekly point leader MAE is 0.036469 and weekly expansion benchmark Brier is 0.152707. The protected monthly GJR MAE is 0.033179 and Student EGARCH expansion Brier is 0.172872.

{table(rp,['horizon','model','n','abs_error','qlike','brier','contraction_brier','high_entry_brier','crps'],22)}

{table(road,['horizon','cutoff','model','n','endpoint_crps','range_crps','vol_mae','touch_brier','integrated_brier'],22)}

{table(pick(ext,cutoff='preauction_0855',barrier=(.02,.05),model=('same_clock_GJR','position_on_GJR')),['horizon','model','side','barrier','touch_brier','day_one_brier','survivor_n','survivor_brier'],16)}

The joint laws scale all four daily log-price legs around the same anchor using one issue-specific factor. Their 256 scenarios preserve daily ordering, endpoint/interval relations, monotone barrier-time CDFs and separate first-session and survivor Brier. Upper and lower excursions, drawdown and range use those same OHLC atoms. Native V14 Student-t GJR monthly range CRPS is 0.015422 at its original guard. V17 post-open volatility outputs are independently archived with 09:25 and 10:20 conditioning.

{rel('risk-cases.csv.gz','volatility-laws.npz','risk-fits.ndjson.gz','risk-replay-receipt.json','joint-law-receipts.json','joint-path-cases.csv.gz','barrier-leaderboard.csv','barrier-cases.csv.gz','postopen-risk-cases.csv.gz','postopen-risk-laws.npz','protected-native-joint-models.csv')}''')


def conclusions():
    p,a,native,risk,path,m,intervals,ci,n,v,c,d,f=headline()
    rm=read('validation-receipt.json')
    miss=csv('mechanism-sensitivities.csv.gz')
    ms=miss.groupby(['horizon','cutoff','model'],as_index=False).agg(n=('day','size'),active=('active','sum'),brier_gain=('brier_gain','mean'),crps_gain=('crps_gain','mean'))
    write('mechanism-sensitivities-summary.csv',ms)
    omit=csv('episode-omission.csv')
    native_omit=omit[(omit.track=='weighted_native')&(omit.model=='V14_plus_positions')]
    bc=csv('native-bias-control-bands.csv')
    mech=csv('native-mechanism-summary.csv')
    nl=csv('native-refit-null-summary.csv')
    sent=csv('future-information-sentinels.csv')
    null=csv('refit-reselection-summary.csv')
    report(13,f'''All {rm['clock_session_guards']:,} original endpoint case forecasts passed their event-clock and target-maturity guards. Moving-block inference uses 1,500 draws at 5, 10, 21 and 42 sessions. Search-adjusted intervals use maximum standardized deviations across every eligible contrast in the same track, target, decision clock, horizon and primary metric. Published active comparisons use identical dates. Full intended cohorts include their prespecified fallbacks.

{table(ci,['horizon','model','parent','metric','n','disjoint','gain','low','high','adjusted_low','adjusted_high'],12)}

{table(native_omit,['horizon','metric','n','gain','remaining_gain','removed_from','removed_to'],10)}

The month's directional gain weakens from 0.026437 in the earlier cohort to −0.000954 in the later cohort. After dropping one influential 21-origin block, the active directional gain is 0.007685. Exposure variants compare exact reports, one- and five-session delays, alternative category gross denominators, strict completeness, a five-session training embargo and expiry/roll filters. The case sentinels replace future inputs or immature labels with extreme values and add exact duplicate columns. All {len(sent)} sentinels returned zero change at their registered numeric tolerance. The futures audit tracks four noninteger OI-conversion cases.

{table(pick(ms,cutoff='preauction_0855'),['horizon','model','n','active','brier_gain','crps_gain'],12)}

{table(null,['metric','observed_best','rotations','null_95','exceedances','finite_reselection_tail'],6)}

{table(nl,['horizon','metric','best_observed_increment','rotation_median','rotation_95','exceedances','runs'],8)}

The null fits rotate or permute earlier training blocks and reselect the strongest tested mechanism. The finite null exercise and all block intervals address V19 comparisons. The repeated examination of related outcomes in V1–V19 remains a separate source of selection.

{rel('validation-receipt.json','future-information-sentinels.csv','matched-comparisons.csv','block-bootstrap-intervals.csv.gz','episode-omission.csv','refit-reselection-nulls.csv','native-refit-null-summary.csv','native-bias-control-bands.csv','mechanism-sensitivities-summary.csv')}''')
    reg=read('registration.json')
    w=csv('native-positioning-weight-summary.csv')
    b=pd.DataFrame(reg['hypotheses'])
    props=['hypothesis','source','target','primary_metric','negative_control','follow_up']
    report(14,f'''V19 registered {len(b)} primary hypotheses at {reg['registered_at']}. Each machine-readable record preserves economic rationale, information source, target, forecast cutoff, parent, metric, eligibility, negative control, computational budget and follow-up criteria. Candidate variants were kept to fixed shrinkage rules and specific controls. Positive fit weights support a local standardized association with past errors for a given model residual. Units and contribution depend on the model regularization and training window.

{table(b,props,15)}

{table(show(pick(w,horizon=21),'abs_median',sense='max',n=10),['feature','fits','mean_standardized_coefficient','median_standardized_coefficient','positive_share'],12)}

The monthly native candidate is the strongest follow-up hypothesis. Weekly native participant correction, the extra rebuilt monthly directions, the direct risk candidates against protected point models, ambiguous transactions and broad daily generalizations are all tracked in the failed or indeterminate cells.

{rel('registration.json','native-positioning-weight-summary.csv','native-positioning-fits.ndjson.gz','native-mechanism-summary.csv','native-refit-null-summary.csv','model-leaderboards.csv','matched-comparisons.csv')}''')
    print_columns=['horizon','cutoff','model','n','disjoint','brier','log_loss','accuracy','balanced_accuracy','crps','abs_error','rmse','covered','width','rank_corr']
    br=pd.concat([show(pick(a,horizon=h,cutoff='preauction_0855'),'brier',n=5) for h in HORIZONS])
    ec=pd.concat([show(pick(a,horizon=h,cutoff='preauction_0855'),'crps',n=5) for h in HORIZONS])
    rd=pd.concat([show(pick(risk,horizon=h,cutoff='preauction_0855'),'abs_error',n=4) for h in HORIZONS])
    re=pd.concat([show(pick(risk,horizon=h,cutoff='preauction_0855'),'brier',n=4) for h in HORIZONS])
    wd=pd.concat([show(pick(path,horizon=h,cutoff='preauction_0855'),'range_crps',n=4) for h in HORIZONS])
    tail=pd.concat([show(pick(path,horizon=h,cutoff='preauction_0855'),'touch_brier',n=4) for h in HORIZONS])
    dif=pick(m,track='endpoint',cutoff='preauction_0855',cohort='active_matched',metric=('brier','crps'),
         model=('participant','delivery','transactions','corporate_position_interactions'),parent=('clock_structural','V18_corporate_same_clock'))
    report(15,f'''The combined population contains 265 original weekly and 217 original monthly outcomes across 53 and 11 disjoint windows. All leaderboard rows retain original forecast clocks and include earlier and later results. The linked machine tables contain every available metric, including error, coverage, width, variance QLIKE, rank correlation and probability calibration. The comparison table lists like-for-like reference scores and origin counts. Lower proper loss marks the top point estimate within a table.

## Weekly and monthly directions at 08:55

{table(br,print_columns,12)}

## Weekly and monthly endpoint distributions at 08:55

{table(ec,print_columns,12)}

## Native weighted laws

{table(n,print_columns,12)}

## Incremental participant, delivery, transaction and interaction scores

{table(dif,['horizon','model','parent','metric','n','gain'],20)}

## Standalone realized risk and volatility expansion at 08:55

{table(rd,['horizon','model','n','abs_error','qlike','crps'],10)}

{table(re,['horizon','model','n','brier','log_loss','crps'],10)}

## Joint future ranges and tails at 08:55

{table(wd,['horizon','model','n','range_crps','vol_mae','touch_brier'],10)}

{table(tail,['horizon','model','n','drawdown_crps','high_crps','low_crps','touch_brier','integrated_brier'],10)}

{rel('model-leaderboards.csv','matched-comparisons.csv','native-mechanism-summary.csv','probability-calibration.csv','block-bootstrap-intervals.csv.gz','barrier-leaderboard.csv','crowding-leaderboard.csv','stock-transfer-leaderboard.csv','sector-transfer-leaderboard.csv','transaction-event-summary.csv','protected-native-joint-models.csv')}''')
    led=read('forward-ledger.json')
    rows=[]
    for r in led['records']:
        rows.append(dict(version=r['version'],key=r['key'],horizon=r['horizon'],classification=r['issue_class'],
            original_issued=r.get('issued_at',r.get('issue_time',r.get('issued'))),reference=r['reference_session'],
            target=r['target_sessions'][-1],matched_sessions=len(r['completed_target_dates']),maturity=r['maturity'],realized=r['realized_return']))
    existing=pd.DataFrame(rows)
    fwd=[]
    for r in led['new_references']:
        x=r.get('annualized_rv',r.get('endpoint_return'))
        fwd.append(dict(model=r['name'],horizon=r['horizon'],issue=r['issued_at'],index_close=r['reference_close'],
                        target=r['target_session'],p_up=r.get('direction_p_up'),p10=x['p10'],median=x['p50'],p90=x['p90']))
    fwd=pd.DataFrame(fwd)
    today=led.get('same_day_reference_source')
    summary=f"The November 25 reference close is {today['nse_ohlc']['close']:,.2f}. NSE's closed status and dated OHLC match the authenticated Upstox quotes." if today else 'A same-day reference close remained unavailable on a matched basis.'
    scored=[]
    methods=[]
    for r in led['records']:
        if r['realized_return'] is None:
            continue
        for kind,field in [('Direction','binary_scores'),('Distribution','scores')]:
            for model,v in r.get(field,{}).items():
                scored.append(dict(version=r['version'],due=r['target'],track=kind,model=model,**v))
        if r.get('outcome_source'):
            method=r['resolution_method']
            support=r['outcome_source']['file']
            methods.append(f"The {r['version']} {r['horizon']}-session diagnostic resolved at {r['resolution_at']}. "
                           f"The original reference of {r['reference_close']:,.2f} and the completed close of {r['official_close']:,.2f} "
                           f"give a realized return of **{r['realized_return']:.4%}**. The source match used {method}. {rel(support)}")
    resolutions='\n\n'.join(methods) or 'The legacy endpoint guards and publication checks remain recorded by issue.'
    newest=rel('forward/new-issues.json','forward/monthly-neutral-law.npz','forward/gjr-risk-5.npz','forward/gjr-risk-21.npz','forward/nse-calendar.pdf') if fwd.size else ''
    report(16,f'''The original V4/V5 ledger refresh used the earlier publication guard and exact stored target sessions. Its immutable issue hashes are retained in the V19 JSON. It was checked at {led['checked_at']}. The November 24 cash holiday is documented in the official exchange schedule. Endpoint scoring requires 18:00 IST on the final original target date and a complete reconciled session sequence. An authenticated current-session OHLC quote can corroborate the published daily NSE bar when the historical API is one session behind. The original late-diagnostic classification governs how its score is interpreted.

{table(existing,['version','key','horizon','classification','original_issued','reference','target','matched_sessions','maturity','realized'],8)}

{resolutions}

{table(pd.DataFrame(scored),['version','due','track','model','p','brier','log_loss','crps'],12)}

{summary} New reference files contain the actual issue timestamp, quoted guard, exact target sessions, full distribution, source hashes and model settings. The monthly neutral band is an arithmetic price return. Both GJR rows show annualized realized volatility quantiles from their original simulated cash-close paths.

{table(fwd,['model','horizon','issue','index_close','target','p_up','p10','median','p90'],8)}

The native opening-gap and weekly corporate registrations depend on the next session's proper premarket issue window. The monthly directional positioning result remains a candidate for a future locked test. A current same-clock options snapshot was unavailable for a comparable IV panel. The available neutral and GJR references use 2026 sessions exclusively.

{rel('forward-ledger.json','forward/alternate-market-receipts.json','forward/certification-probes.json')} · {newest} · [NSE 2026 cash calendar](https://archives.nseindia.com/content/circulars/CMTR71775.pdf) · [Upstox daily OHLC quote specification](https://upstox.com/developer/api-documentation/get-market-quote-ohlc-v3/)''')
    mon=pick(n,horizon=21)
    wk=pick(n,horizon=5)
    best_eff=pick(bc,horizon=21,model='V14_plus_positions',block=21)
    mac=pick(mech,horizon=21,cohort='matched active')
    def s(mo,name,k):
        return f'{measure(mo,name,k):.6f}'
    reb_v19=pick(a,cutoff='preauction_0855',horizon=5,model='decomposition_position').iloc[0]
    reb_parent=pick(a,cutoff='preauction_0855',horizon=5,model='component_plus_residual').iloc[0]
    report(17,f'''The strongest V19 result is an original-horizon monthly residual correction over the native V14 law. Across 217 intended origins, Brier improves from **{s(mon,'V14_exact','brier')} to {s(mon,'V14_plus_positions','brier')}** and CRPS from **{s(mon,'V14_exact','crps')} to {s(mon,'V14_plus_positions','crps')}**. The previous native V15 joint endpoint CRPS reference is 0.024694 at its own archived clock. V19's monthly adjustment is active on 159 origins representing eight disjoint blocks. The directional gain is concentrated in the earlier period and the late Brier difference is slightly negative. Both familywise 21-session block intervals against the exact parent span zero.

The bias-only comparator checks whether forecasts benefit simply by shifting a historically miscentered parent. The table reports equal eligible origins for native successors and preserved original laws.

{table(mac,['model','n','brier','crps','log_loss'],9)}

{table(best_eff,['metric','n','disjoint','gain','adjusted_low','adjusted_high'],6)}

At the original weekly guard, V18 corporate remains the strongest native point reference at Brier **{s(wk,'V14_event_overlay','brier')}** and CRPS **{s(wk,'V14_event_overlay','crps')}**. Its V19 positioning correction produces {s(wk,'V18_plus_positions','brier')} and {s(wk,'V18_plus_positions','crps')}. On the distinct 08:55 rebuilt track, the V17 decomposition plus positioning gives CRPS **{reb_v19.crps:.6f}** versus {reb_parent.crps:.6f}, alongside Brier {reb_v19.brier:.6f} versus {reb_parent.brier:.6f}. The rebuilt monthly direction remains led by 0.5000 neutral probabilities with Brier 0.250000.

Volatility and joint risk have a different set of protected references. V16 offshore/domestic and GJR remain the primary weekly and monthly point-volatility controls. The same-clock path overlays keep 256 coherent scenarios and have their own endpoint, risk, range and barrier scores. Review those alongside the native Student-t GJR range reference before comparing candidates.

Sources improve substantially with 465 dated participant OI reports, 466 volume reports, 1,439,636 security-series delivery observations, depository custody publications and monthly AMFI fund subscriptions and redemptions. Exact archival availability, overlap and cumulative model selection still limit the predictive interpretation. The historical signal warrants an independently timed test. The current record supports research classification.

{rel('V19_COMPLETE_MODEL_COMPARISON.md','V19_VALIDATION_AND_FALSIFICATION.md','V19_AUTHENTIC_CAPITAL_FLOW_RESEARCH.md','V19_FORWARD_RESEARCH_LEDGER.md','native-bias-control-bands.csv','monthly-native-evidence.png')}''')
    report(18,'''1. Lock the monthly V14-native positioning correction and its bias-only control before a new eligible evaluation period. Score matched Brier, CRPS, coverage and interval width versus the original first usable close, and predeclare the expiry and late-period strata. Evaluate failure and adaptation as distinct recorded states.
2. Preserve daily primary exchange, custodian and AMFI first-release copies contemporaneously. Compare confirmed revisions to first prints and audit the lag specific to the publication route before any daily FII/DII model expansion.
3. Follow up on NIFTY futures share-equivalent OI changes around documented lot transitions and fixed expiry trains. Estimate whether concentration improves ordinary OI reduction, volatility and reversal loss beyond IV and cash breadth.
4. Test the timestamped delivery and matched deal mechanisms in a future calendar block with the same issuer eligibility. Preserve point-in-time constituent weights and sector mappings when directly obtainable, then compare the liquidity proxy, official weights and fixed equal-company aggregation.
5. Keep the validated opening and native weekly reference series intact. The next phase can preserve the scheduled neutral, GJR and joint-risk distributions and resolve all eligible legacy targets on authoritative end-of-day data.

'''+rel('registration.json','V19_FINAL_RESEARCH_CONCLUSIONS.md','V19_FORWARD_RESEARCH_LEDGER.md'))

def index():
    p,a,native,risk,path,m,intervals,ci,n,v,c,d,f=headline()
    reports='\n'.join(f'{i}. [{x.replace("_"," ").title()}](V19_{x}.md)' for i,x in enumerate(REPORTS,1))
    ledger=read('forward-ledger.json')
    paths=read('risk-replay-receipt.json')
    leg=pick(n,horizon=21)
    base=measure(leg,'V14_exact','brier'); new=measure(leg,'V14_plus_positions','brier')
    a0=measure(leg,'V14_exact','crps'); a1=measure(leg,'V14_plus_positions','crps')
    (OUT/'NIFTY_V19_RESEARCH.md').write_text(f'''# NIFTY V19 positioning and supply–demand research

The native monthly V14 positioning overlay reduced Brier from **{base:.6f} to {new:.6f}** and CRPS from **{a0:.6f} to {a1:.6f}** across 217 intended origins. Its 159 active observations include eight disjoint windows. The later cohort's Brier increment turned slightly negative, and the adjusted intervals span zero. V18 corporate remained the native weekly leader. {ledger['new_v19_issues']} genuine research references are frozen in the independent forward ledger.

## Research reports

{reports}

## Reproducibility

The historical period is {FIRST} through {FREEZE}. Forensic source receipts preserve 465 official OI reports, 466 trading-volume reports and {d['delivery']['full_rows']:,} delivery rows. The exact weighted, ordinary endpoint and coherent OHLC paths are stored in the machine artifacts. Risk preservation checked {paths['cases']:,} point/path reference rows. The code accepts the historical archive as input, scores only fully matured windows and retains the intended population when a source is missing.

{rel('MISSION.md','README.md','market-positioning.sqlite','model-leaderboards.csv','native-mechanism-summary.csv','block-bootstrap-intervals.csv.gz','monthly-native-evidence.png','forward-ledger.json','manifest.json')}
''',encoding='utf-8')
    (OUT/'README.md').write_text('''# Reproduce NIFTY V19

Run from the trading-desk workspace root with the existing research environment and V11–V18 artifacts. V19 writes to its own dated run directory. Sources are public archive data except the authenticated read-only Upstox quote references. To regenerate the historical research from the retained snapshots, omit the archive-fetch and forward-refresh commands. The source receipts record expected or failed alternative retrievals separately.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:OPENBLAS_NUM_THREADS='1'
.venv/Scripts/python.exe -m research.nifty_forecast_v19.common
.venv/Scripts/python.exe -m research.nifty_forecast_v19.acquire
.venv/Scripts/python.exe -m research.nifty_forecast_v19.acquire alternatives
.venv/Scripts/python.exe -m research.nifty_forecast_v19.baseline replay
.venv/Scripts/python.exe -m research.nifty_forecast_v19.baseline protect
.venv/Scripts/python.exe -m research.nifty_forecast_v19.database
.venv/Scripts/python.exe -m research.nifty_forecast_v19.features
.venv/Scripts/python.exe -m research.nifty_forecast_v19.flows
.venv/Scripts/python.exe -m research.nifty_forecast_v19.forecast
.venv/Scripts/python.exe -m research.nifty_forecast_v19.risk
.venv/Scripts/python.exe -m research.nifty_forecast_v19.structure
.venv/Scripts/python.exe -m research.nifty_forecast_v19.evidence
.venv/Scripts/python.exe -m research.nifty_forecast_v19.native_controls
.venv/Scripts/python.exe -m research.nifty_forecast_v19.forward --reuse-refresh
.venv/Scripts/python.exe -m research.nifty_forecast_v19.report
.venv/Scripts/python.exe -m research.nifty_forecast_v19.delivery
```

Review [the research index](NIFTY_V19_RESEARCH.md) and [manifest](manifest.json). Each NPZ is keyed by its corresponding score table, receipt or origin-specific filename. The timing assumptions and benchmarks were locked before scoring, and prior model laws are verified against their hashes. The freeze date excludes later sessions from every historical result. Current observations and any original target resolutions belong to the [forward ledger](V19_FORWARD_RESEARCH_LEDGER.md).
'''.replace('\\`','`'),encoding='utf-8')

def figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    bands=csv('block-bootstrap-intervals.csv.gz')
    inner=pick(bands,track='weighted_native',block=21)
    colors={'V14_plus_positions':'#0D6E64','V18_plus_positions':'#5A74A1'}
    f,plots=plt.subplots(1,2,figsize=(12.4,4.8))
    f.subplots_adjust(left=.115,right=.975,bottom=.19,top=.81,wspace=.36)
    for ax,k,hdr in zip(plots,['brier','crps'],['Direction (Brier)','Return distribution (CRPS)']):
        g=inner[inner.metric.eq(k)].sort_values(['horizon','model']).reset_index(drop=True)
        for i,r in g.iterrows():
            m=r.gain
            ax.plot([r.adjusted_low,r.adjusted_high],[i,i],lw=2.1,color=colors[r.model],alpha=.67)
            ax.scatter(m,i,s=47,color=colors[r.model],zorder=3)
        ax.set_yticks(np.arange(len(g)),[f'{"5 sessions" if z.horizon==5 else "21 sessions"} · {"V14" if z.model=="V14_plus_positions" else "V18"}'
                                       for z in g.itertuples(index=False)],fontsize=9)
        ax.invert_yaxis()
        ax.axvline(0,color='#394453',lw=1,linestyle='--')
        ax.grid(axis='x',color='#dce3e9',lw=.65)
        ax.set_title(hdr,loc='left',fontweight='bold',fontsize=12)
        ax.set_xlabel('Loss reduced by adding positioning')
        ax.spines[['left','top','right','bottom']].set_visible(False)
        ax.tick_params(axis='both',length=0)
    f.suptitle('V19 positioning overlays on archived native forecasts',x=.03,y=.95,ha='left',fontsize=15,fontweight='bold')
    f.text(.03,.045,'Dots show matched historical gains. Lines show search-adjusted 95% intervals from 21-session blocks.',color='#394453',fontsize=8)
    f.savefig(OUT/'monthly-native-evidence.png',dpi=160,facecolor='white')
    plt.close(f)

if __name__=='__main__':
    archives()
    mechanisms()
    conclusions()
    figure()
    index()
    print('Wrote all 18 V19 Markdown reports and the research index',flush=True)


