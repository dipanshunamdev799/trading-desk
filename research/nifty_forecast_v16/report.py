"""Render the complete V16 research record from archived experiments."""
from .common import *

INDEX={
 'OPENING_GAP_REPRODUCTION_AND_TIMING_AUDIT':'Opening-gap reproduction and timing audit',
 'GLOBAL_INFORMATION_ARRIVAL_MAP':'Global information arrival map',
 'ADVANCED_OPENING_GAP_FORECASTING':'Advanced opening-gap forecasting',
 'OFFSHORE_PRICE_DISCOVERY':'Offshore price discovery',
 'OVERNIGHT_AND_INTRADAY_RETURN_DECOMPOSITION':'Overnight and intraday return decomposition',
 'GAP_ABSORPTION_AND_REVERSAL':'Gap absorption and reversal',
 'CROSS_MARKET_INFORMATION_NETWORKS':'Cross-market information networks',
 'INFORMATION_DECAY_RESEARCH':'Information decay across sessions',
 'CROSS_MARKET_DISAGREEMENT':'Cross-market disagreement',
 'MULTISCALE_DIRECTIONAL_FORECASTING':'Multiscale directional forecasting',
 'SESSION_AWARE_VOLATILITY_INTELLIGENCE':'Session-aware volatility',
 'SESSION_AWARE_PATH_FORECASTING':'Session-aware OHLC paths',
 'STRONG_BASELINE_COMPARISON':'Strong directional baselines',
 'VALIDATION_AND_FALSIFICATION':'Validation and falsification',
 'FORWARD_RESEARCH_LEDGER':'Forward research ledger',
 'COMPLETE_MODEL_COMPARISON':'Complete model comparison',
 'FINAL_RESEARCH_CONCLUSIONS':'Final research conclusions',
 'NEXT_EXPERIMENTS':'Next experiments',
}

AUC='https://www.nseindia.com/static/products-services/equity-market-pre-open'
NSEFF='https://nsearchives.nseindia.com/web/mediaattachment/2026-10/FAQs_on_Closing_Auction_Session_CAS_in_the_CM_and_changes_in_FO_Segment_ver3_20261023220345.pdf'
NSEM='https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf'
CAS='https://www.nseindia.com/static/products-services/closing-auction-session'
V15LINK='../../../nifty_forecast_v15/2026-11-25/run-001/NIFTY_V15_RESEARCH.md'


def csv(name,root=OUT):
    return pd.read_csv(root/name,low_memory=False)


def filt(frame,**kwargs):
    for name,v in kwargs.items():
        frame=frame[frame[name].isin(v) if isinstance(v,(list,tuple,set)) else frame[name].eq(v)]
    return frame


def one(frame,**kwargs):
    r=filt(frame,**kwargs)
    if len(r)!=1:
        raise ValueError(f'Expected one score row for {kwargs}, got {len(r)}')
    return r.iloc[0]


def top(frame,groups,metric,n):
    return frame.sort_values(metric,kind='stable').groupby(groups,sort=False).head(n).sort_values([*groups,metric])


def fmt(x):
    if isinstance(x,(bool,np.bool_)):
        return 'Yes' if x else 'No'
    if pd.isna(x):
        return '—'
    if isinstance(x,(int,np.integer)):
        return f'{x:,}'
    if isinstance(x,(float,np.floating)):
        return f'{x:.6f}'
    return str(x).replace('|','/').replace('\n',' ')


def table(f,cols):
    names={c:c.replace('_',' ') for c in cols} if not isinstance(cols,dict) else cols
    h=['| '+' | '.join(names.values())+' |','| '+' | '.join(['---']*len(names))+' |']
    h.extend('| '+' | '.join(fmt(x) for x in q)+' |' for q in f[list(names)].itertuples(index=False,name=None))
    return '\n'.join(h)


def links(*targets):
    return ' · '.join(f'[{title}]({path})' for title,path in targets)


def report(name,*sections):
    title=INDEX[name]
    (OUT/f'V16_{name}.md').write_text('# V16 '+title+'\n\n'+'\n\n'.join(s.strip() for s in sections if s)+'\n',encoding='utf-8')


def reproduce():
    r=read('v15-opening-reproduction.json')
    k=read('cash-source-audit.json')
    a=csv('v15-replayed-gap-evidence.csv')
    p=filt(a,model='offshore_fresh',metric='brier',target='immediate_open')
    a09=filt(a,model=['domestic_prior','offshore_prior_only','offshore_fresh'],cutoff='09:10',delay=60)
    cal=csv('preopen-clock-validation.csv')
    report('OPENING_GAP_REPRODUCTION_AND_TIMING_AUDIT',
      f"""V16 rebuilt **{r['archived_rows']:,}** V15 forecasts from raw historical data, including all **{r['matched_same_morning']}** same-morning and **{r['matched_next_gap']}** next-opening cases for each parent–candidate comparison. Maximum absolute difference across probabilities, Brier, point/interval estimates, CRPS and log loss was **{max(r['maximum_differences'].values()):.2e}**. The original fit uses penalty 95, up to 160 strictly matured training outcomes and 70% of its estimated ridge location, added to a median-centered empirical log-gap law. The comparison called the domestic baseline in the brief was the previous domestic state with older inherited global risk, FX, oil and US breadth. The pure domestic parent was also rebuilt.""",
      '## The original 09:10 forecasts\n\n'+table(a09,['target','model','parent','metric','n','candidate','control','gain','early_gain','later_gain','family_low21','family_high21']),
      """The domestic opening process begins at 09:00 IST, with indicative index and constituent equilibrium prices disseminated during order entry. The later cash pre-open protocol applies from September 7, 2026. It restricts market orders after 09:05, may close order entry randomly in the final two minutes, and uses matching before continuous trading at 09:15. Under the earlier protocol 09:10 was also inside the pre-open process. The exchange determines eligible constituent opening prices through equilibrium matching, with first regular trades used when a price has yet to be discovered. The benchmark index aggregates NSE-priced constituent stocks using free-float weights. V16 used the official published NIFTY 50 open directly. All 403 official opens and closes agreed with the frozen V6 cash series. The main earlier study uses 08:55 with 08:30 and 08:45 sensitivities. The baseline and replay data trace contains previous domestic state, earlier derivative surface marks and eligible foreign closes. It excludes current-session NIFTY prices, constituent auction prices, indicative prints, and auction breadth at all four replayed clocks. The GIFT variant is a different input test, especially at 09:10, when its prices may already respond to the NSE auction. [NSE pre-open rules](https://www.nseindia.com/static/products-services/equity-market-pre-open) · [2026 protocol history](https://nsearchives.nseindia.com/web/mediaattachment/2026-10/FAQs_on_Closing_Auction_Session_CAS_in_the_CM_and_changes_in_FO_Segment_ver3_20261023220345.pdf) · [NIFTY index methodology](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)""",
      '## Pre-auction forecasts and source-release sensitivity\n\n'+table(p,['cutoff','delay','n','candidate','control','gain','early_gain','later_gain','family_low21','family_high21']),
      """Moving the original model before the auction left the matched scores unchanged at 08:30, 08:45 and 08:55. The 30-, 60-, 180- and 360-minute close-delay variants selected the same input as the original. The additional full-day delay removed the gain. The stronger next-session-gap task stayed weak. The source snapshots are historical reconstructions from dated marks, with explicit delays where original receipt timestamps are missing. The more demanding GIFT and partial Asia tests use completed intraday vendor candles and a separate matched comparison. Normal cash sessions, weekends and special sessions retain their own tags.""",
      '## Snapshot support\n\n'+table(cal,['cutoff','days','eligible_gift']),
      links(('Per-origin exact reproduction','v15-replayed-gap-forecasts.csv.gz'),('Full benchmark replay evidence','v15-replayed-gap-evidence.csv'),
            ('Exact archived laws','v15-replayed-gap-laws.npz'),('Official open reconciliation','cash-opening-reconciliation.csv'),
            ('Timing by source','information-clock.csv.gz'),('Earlier V15 research',V15LINK),('More gap models','V16_ADVANCED_OPENING_GAP_FORECASTING.md')))


def map_sources():
    q=read('source-clock-specification.json')
    p=read('foreign-intraday-acquisition.json')['records']
    a=pd.DataFrame(p)
    v=a.groupby('series',as_index=False).agg(requests=('series','size'),bar_minutes=('bar_minutes','first'),
        instrument=('instrument','first'),successful=('candles',lambda x:x.fillna(0).gt(0).sum()),bars=('candles','sum'))
    z=pd.DataFrame.from_dict(q['foreign_daily'],orient='index').rename_axis('source').reset_index()
    t=csv('preopen-clock-validation.csv')
    hol=csv('verified-holiday-flag-sensitivity.csv')
    off=csv('official-holiday-gap-sensitivity.csv').groupby('model',as_index=False).agg(n=('day','size'),brier=('brier','mean'),crps=('crps','mean'))
    report('GLOBAL_INFORMATION_ARRIVAL_MAP',
      f"""A forecast snapshot stores the exchange-local date of each completed foreign observation, its assumed publication time in IST, the price-bar timestamp where relevant, the earliest assumed eligibility and the age of the eligible mark. The foreign cash inputs are US, European and Asian observations with distinct clocks. Local time-zone conversion accounts for US and European daylight-saving changes. We distinguish the preceding completed cash session from a valid Asian partial session and from a contemporaneous vendor futures or indicator mark. The snapshot keeps earlier known marks through weekends and missing or confirmed holiday observations. Calendar labels printed at midnight are treated as date labels, with exchange close or vendor roll conventions plus explicit buffers. Historic receipt stamps, where unavailable, remain empty.""",
      '## Completed daily source timing\n\n'+table(z,['source','timezone','assumed_local_close','buffer_minutes','reconstructable_end_of_day_marks']),
      '## Authenticated intraday history added\n\n'+table(v,['series','instrument','bar_minutes','requests','successful','bars']),
      """The US block uses S&P 500, Dow and a vendor US Tech 100 reference, alongside the preserved dated Nasdaq/FRED volatility and Treasury features and a new alignment of archived SPY, RSP, XLF and XLK closes. The ETFs proxy cap weight, equal weight, finance and technology. European rows cover FTSE, DAX and CAC. Asia uses Nikkei and Hang Seng completed closes plus current dated partial marks. GIFT uses its named vendor global series, and FX, Brent and WTI have separate close and timestamp rules. Upstox did not establish a comparable historic intraday Russell, TOPIX, mainland Chinese index or India ADR series in these tested records. The FX and oil daily date labels receive an extra day beyond nominal local midnight. Their eligible intra-market bars have separate clocks and age guards. Missing intervals remain missing. [Global instrument metadata](https://upstox.com/developer/api-documentation/announcements/global-instruments/) · [Historical candle intervals](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/)""",
      f"""The screening sensitivity flagged **{len(hol)}** decision/source rows where selected 2026 vendor date marks fell on published cash-venue closure dates, then reran the factor after dropping those printed dates and carrying the latest verified preceding session. This comparison treats a venue holiday print as a vendor-clock sensitivity. It uses observed earlier vendor dates for 2025 and the published normal-session rules. Nasdaq price changes come from historical ETF closes and can include tracking, distribution and corporate-action effects. Briefed futures contracts, forecasts and authenticated capture timestamps are stored separately from corrected clock assumptions. [NYSE calendar](https://www.nyse.com/trade/hours-calendars) · [JPX calendar](https://www.jpx.co.jp/english/corporate/about-jpx/calendar/) · [HKEX 2026 calendar](https://www.hkex.com.hk/-/media/HKEX-Market/Services/Circulars-and-Notices/Participant-and-Members-Circulars/SEHK/2025/ce_SEHK_CT_075_2025.pdf) · [Euronext calendar](https://www.euronext.com/en/trading/trading-hours-holidays)""",
      '## Holiday handling sensitivity\n\n'+table(off,['model','n','brier','crps']),
      links(('Complete per-source clock map','information-clock.csv.gz'),('Normalized bar hashes','normalized-market-data.json'),
            ('RSP, SPY, XLF and XLK clock','us-etf-information-clock.csv'),('ETF provenance','us-etf-source-receipt.json'),
            ('Calendar receipts','exchange-calendar-receipts.json'),('Checked holiday rows','verified-holiday-flag-sensitivity.csv'),
            ('Provider request receipts','foreign-intraday-acquisition.json')))


def advanced():
    l=filt(csv('session-leaderboard.csv'),exercise='opening_gap',cohort='combined')
    r=csv('session-matched-evidence.csv')
    m=csv('v15-v16-opening-matched.csv')
    a=filt(l,cutoff='08:55')
    names=['neutral','historical','prior_return','domestic','single_US','equal_six','six_cash','asia_partial',
           'gift_raw','gift_calibrated','gift_roll_screened','gift_plus_global','student_location_scale','sign_magnitude',
           'cluster_balanced','shallow_interactions','rich_global_ridge','disagreement']
    b=filt(m,cutoff='08:55',control='V15_offshore_fresh',candidate=['gift_raw','asia_partial','single_US'],metric=['brier','crps'])
    h=filt(r,exercise='opening_gap',cutoff='08:55',control='equal_six',candidate=['gift_raw','gift_roll_screened'],metric=['brier','crps','mae','log_loss'])
    report('ADVANCED_OPENING_GAP_FORECASTING',
      """The opening target is the official NIFTY 50 open divided by the previous official NIFTY 50 close minus one. The consecutive date comes from the frozen NSE cash sequence and is verified independently from archive identity. The primary table scores arithmetic gap returns. The V15 exact benchmark replay preserves its log-return CRPS. Cross-version distribution comparisons transform the original forecast atoms to arithmetic returns before computing the paired loss. Direction accuracy uses a 0.5 probability threshold. Balanced accuracy averages hit rates for up and down. CRPS, absolute median error, root mean square error of the mean and central 80% coverage score magnitude and uncertainty directly.""",
      '## 08:55 pre-auction distributions\n\n'+table(filt(a,model=names).sort_values('brier'),['model','n','brier','log_loss','correct','balanced_accuracy','crps','mae','rmse','covered','width']),
      '## Matched comparison with exact V15 baseline\n\n'+table(b,['candidate','control','metric','n','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21']),
      '## Matched comparison with the simple offshore factor\n\n'+table(h,['candidate','metric','n','candidate_loss','control_loss','gain','early_gain','later_gain','adjusted_low21','adjusted_high21']),
      """Neutral uses symmetric empirical magnitudes. Other baselines include matured historical frequencies and distances, previous domestic state, S&P alone and an equally weighted six-market factor. The larger linear model uses robust train-only imputation, center and scales. Student-t distributional regression forecasts conditional location and scale, while the sign/magnitude system estimates the two tail masses separately. The cluster-balanced fit combines two disjoint date blocks in rotation, and the shallow-interaction model adds a small set of normalized cross-market products. The fit ledger records the terms and eligible labels. Macroeconomic source date checks use the clock map. Reliability is recorded for sign and for ±0.5% and ±1% thresholds, with sparse bins kept visible. Domestic or GIFT plus additional global terms are compared on exact common dates at each deadline.""",
      links(('Leaderboard by clock, cohort and target','session-leaderboard.csv'),('Brier and tail reliability bins','gap-reliability.csv'),
         ('All matched gains and adjusted bounds','session-matched-evidence.csv'),('Replayed V15 on common return units','v15-v16-opening-matched.csv'),
         ('08:55 forecast atoms','opening-0855-laws.npz'),('08:55 per-origin forecasts','opening-0855-scores.csv.gz'),
         ('08:55 fitted parameters','opening-0855-fits.ndjson.gz')))


def gift():
    a=csv('offshore-anchor-sensitivity.csv')
    q=a.groupby('model',as_index=False).agg(n=('day','size'),brier=('brier','mean'),crps=('crps','mean'),mae=('mae','mean'),
               accuracy=('correct','mean'),reference_basis_points=('prior_basis','median'))
    m=csv('opening-gap-sensitivity.csv')
    d=filt(m,cutoff='08:55',model=['gift_raw','gift_plus_global'],control=['single_US','equal_six','gift_calibrated'],metric='brier')
    lead=filt(csv('session-leaderboard.csv'),exercise='opening_gap',cohort='combined',model=['gift_raw','gift_calibrated','gift_roll_screened','gift_plus_global'])
    audit=read('offshore-roll-and-clock-audit.json')
    report('OFFSHORE_PRICE_DISCOVERY',
      f"""Authenticated Upstox history exposed the GIFT NIFTY vendor alias GLOBAL_INDEX|SGX NIFTY with actual five-minute bars. At 08:55 there were **{audit['morning_marks']}** source-eligible snapshots including training dates. The predictive value tested is the percentage change in that vendor series between an earlier NIFTY reference-day mark ending by 15:30 and the latest eligible current-morning bar. For an index points basis, an approximately stable futures-to-cash relationship cancels when taking that relative change. All signal calculations use the archived offshore prices. The vendor alias carries neither an auditable contract expiry nor a dated switch policy. Raw GIFT scores are therefore a vendor-series experiment. The exercise makes no per-contract fill or returns claim. NSE IX specifies a USD cash-settled futures contract, with a USD multiplier separate from the reported index points. The documented expiry convention changed during 2025, and the November 2, 2026 hours extension covered 03:15 IST through 02:45 IST the next day. The broad month-transition screen leaves out the final seven and first two calendar days, independently of realized marks. [NSE IX contract specification](https://www.nseix.com/markets/about-our-products/equity-derivatives-updated) · [March 2025 expiry revision](https://www.nseix.com/api/content/circulars/NSEIFSC_TRADE_2056.pdf) · [July 2025 expiry revision](https://www.nseix.com/api/content/circulars/NSEIFSC_TRADE_2199.pdf) · [Hours extension](https://www.nseix.com/web/pressrelease/2026-11/PR_CC_03112026_20261103101702.pdf)""",
      '## Deadlines and contractual rollover sensitivity\n\n'+table(lead,['cutoff','model','n','brier','crps','mae','correct','covered']),
      '## Basis anchor alternatives at 08:55\n\n'+table(q.sort_values('brier'),['model','n','brier','crps','mae','accuracy','reference_basis_points']),
      '## Matched exclusions and the broader global addition\n\n'+table(d,['model','control','case_filter','n','loss','base','gain']),
      """To check source timing and changing cash-close protocols, prior futures anchors at 15:15, 15:30 or 15:40, an earlier morning quote and a five-date rolling basis were evaluated on persistent historical support. Eligibility requires the same dated morning, sufficient publication buffer and a fresh bar; a missing bar prevents an implied-gap forecast for that case. The 09:10 alias is eligible for the comparison during NSE price discovery. The primary pre-auction cutoff is 08:55. Spread/carry variation, vendor rolling and exact receipt times remain sources of uncertainty. The simple futures change performed strongly before the auction and the broad foreign block did not consistently improve it. [NSE cash closing-auction protocol](https://www.nseindia.com/static/products-services/closing-auction-session)""",
      links(('Every quote anchor and basis check','offshore-anchor-identity.csv'),('Basis and publication audit','offshore-roll-and-clock-audit.json'),
            ('Futures candle retrieval','foreign-intraday-acquisition.json'),('Forecast-date sensitivity','opening-gap-sensitivity.csv'),
            ('Month and large-event deletion','opening-gap-deletion.csv')))


def domestic_sessions():
    t=csv('session-targets.csv')
    use=t[t.cohort.ne('')&t.cohort.notna()].copy()
    truths=[]
    for name,x in [('combined',use),*list(use.groupby('cohort'))]:
        g=x.gap.to_numpy()
        r=x.regular.to_numpy()
        total=x.one.to_numpy()
        np.testing.assert_allclose(g+r,total,atol=3.e-15,rtol=0)
        vg=np.var(g); vr=np.var(r); vb=np.var(total)
        truths.append(dict(cohort=name,n=len(g),overnight_sd=np.sqrt(vg),regular_sd=np.sqrt(vr),
                           total_sd=np.sqrt(vb),overnight_variance_share=vg/vb,regular_variance_share=vr/vb,
                           cross_variance_share=2*np.mean((g-g.mean())*(r-r.mean()))/vb,correlation=np.corrcoef(g,r)[0,1],
                           same_sign=np.mean(g*r>0),close_same_side=np.mean(g*total>0)))
    tr=pd.DataFrame(truths)
    write('observed-session-variance-split.csv',tr)
    raw=csv('session-leaderboard.csv')
    r=filt(raw,cohort='combined',exercise='pre_session_decay',model=['domestic','eq_fresh','rich_fresh','gift_conditional'],
           target=['gap','regular','firsthour','remaining','one','next_next_close'])
    p=filt(raw,cohort='combined',exercise='after_absorption',model=['cash_prefix','eq_fresh','breadth_after_open','gap_breadth_interaction','foreign_after_gap'],
           target=['regular_after_bar','firsthour_residual','remaining','three','five'])
    report('OVERNIGHT_AND_INTRADAY_RETURN_DECOMPOSITION',
      """Close-to-close log return is the sum of the prior-close-to-official-open gap and the official-open-to-close regular return. The exact arithmetic identity was tested on every eligible morning. The variance decomposition includes the covariance term. At 08:55 the full gap and regular-session component are both unknown. At 09:25 the separate study can use the first completed five-minute bar, its recorded open as the gap proxy and earlier known basis; the 10:20 study additionally uses the first hour and synchronized sector prefix. The after-first-bar target uses the first bar's close and the remaining-session target uses the 10:15 completed cash mark. Foreign arrivals, domestic gap, prior eligible derivatives and observed sector/ETF proxies enter under explicit clocks.""",
      '## Realized variation by component\n\n'+table(tr,['cohort','n','overnight_sd','regular_sd','total_sd','overnight_variance_share','regular_variance_share','cross_variance_share','correlation','same_sign','close_same_side']),
      '## Before the auction\n\n'+table(r,['target','model','n','brier','crps','mae','balanced_accuracy']),
      '## After the first cash bar or hour\n\n'+table(p,['cutoff','target','model','n','brier','crps','mae']),
      """At the morning cutoff foreign information must predict before the official gap is recorded. At 09:25 and 10:20 the fresh-input test instead compares predictions on identical post-observation targets with the observed prefix supplied to both models. Any difference in the return to official close after accounting for the first bar uses the unresolved cash component. The official gap used as a realized target and the first-candle gap used as an observed predictor have separate identities. EOD option surface state enters from the earlier vintage. Authenticated intraday option books are unavailable in this study.""",
      links(('Session outcome components','session-targets.csv'),('Cash bar identity and coverage','cash-bar-identity-audit.csv'),
            ('Matched comparisons and post-auction variants','session-matched-evidence.csv'),('Clock map','information-clock.csv.gz')))

    d=csv('continuation-leaderboard.csv')
    q=csv('gap-fill-leaderboard.csv')
    direct=csv('absorption-matched.csv')
    fill=csv('fill-matched.csv')
    res=read('absorption-receipt.json')
    paths=csv('gap-fill-events.csv')
    core=d[d.model.isin(['history','gap_sign_size','cash_prefix_only','sector_offshore_full'])]
    rawf=paths[paths.cohort.notna()&paths.cohort.ne('')].groupby('touch_fraction',as_index=False).agg(n=('day','size'),
        fill_rate=('touched','mean'),conditional_median_bar=('first_hit',lambda x: x[x.lt(76)].median()))
    report('GAP_ABSORPTION_AND_REVERSAL',
      f"""A session can end on the gap side of the previous close while its intraday return partially retraces the gap. V16 separately tests close-to-close side, open-to-close continuation, remaining-session continuation, the next regular trading day's close-to-close return and first touch of a 50% retracement or full gap fill. Time-to-event scoring uses the authenticated 75-bar five-minute regular session. At 09:25 each case already supplied one bar. At 10:20 it supplied twelve. A level touched by that checkpoint is already resolved and is excluded from the corresponding risk set. The open can be the initial condition, and an untouched level has a right-censored mass at bar 76. The fitted rules use only eligible earlier labels and do not use the final day’s open as a feature before the first bar. The archive contains **{res['n_continuation']:,}** continuation forecast scores and **{res['n_survival']:,}** survival scores.""",
      '## Continuation targets\n\n'+table(core,['cutoff','target','model','n','actual','p','brier','log_loss']),
      '## Full-session realized retracements\n\n'+table(rawf,['touch_fraction','n','fill_rate','conditional_median_bar']),
      '## Forecasts conditional on no touch by the checkpoint\n\n'+table(q,['cutoff','threshold','model','n','actual_fill','forecast_fill','brier','integrated_brier','conditional_abs_minutes','median_ess']),
      '## Matched integrated timing gains\n\n'+table(filt(fill,metric='integrated_brier'),['cutoff','threshold','candidate','n','gain','adjusted_low21','adjusted_high21']),
      """The frequency models compare sign and training-defined gap size buckets, simple continuation and reversal rules, the observed price prefix, and a larger bank/breadth/foreign state. Those tests compare same-time risk sets. First-passage Brier tracks both end-of-session touch and the whole cumulative hitting curve. The time conditioned on a fill is summarized separately in minutes. A gap seen before regular trading and a subsequent intraday trade are separate measurement questions.""",
      links(('Per-origin direction outcomes','session-continuation-scores.csv.gz'),('Survivor and actual time outcomes','first-touch-fill-scores.csv.gz'),
            ('Probability by five-minute bar','gap-fill-time-laws.npz'),('Matched continuation comparisons','absorption-matched.csv'),
            ('Training denominators','gap-fill-training-risks.csv')))


def cross_market():
    table0=csv('session-leaderboard.csv')
    m=csv('session-matched-evidence.csv')
    net=filt(table0,exercise=['sector_network','etf_transmission'],cohort='combined',
             model=['domestic','targeted_block','targeted_stale','direct_foreign_ETF','delayed_foreign_ETF','ETF_only'])
    net_g=filt(m,exercise='etf_transmission',candidate='direct_foreign_ETF',control='domestic',metric=['brier','crps'])
    learned=filt(table0,exercise='ETF_NIFTY_link',cohort='combined',
                 model=['domestic','additive_ETFs','foreign_sector_stack','ETF_disagreement'])
    report('CROSS_MARKET_INFORMATION_NETWORKS',
      """The stage-one targets are the next official IT, bank, financial-services, energy and broad-index open versus their own prior official close, their daily relative return versus NIFTY, and NIFTY regular-session realized risk. Foreign mapping uses technology, genuine XLF/XLK traded sector proxies, S&P/Dow, Asian participation, VIX, Treasury levels, USD/INR and Brent/WTI. The targeted model compares equal availability with domestic-only and its own delayed block. The ETF refinement uses archived SPY, RSP, XLF and XLK from Nasdaq through their exchange time zone with a one-hour publication allowance. It tests a US-equity return plus FX proxy, finance versus technology, and equal-weight minus cap-weight. Observations across markets are assayed for predictive association.""",
      '## Sector and realized risk models\n\n'+table(net,['exercise','target','model','n','brier','crps','mae','balanced_accuracy']),
      '## Dedicated ETF block versus domestic predictors\n\n'+table(net_g,['target','metric','n','candidate_loss','control_loss','gain','early_gain','later_gain','adjusted_low21','adjusted_high21']),
      '## Feeding earlier fitted sector forecasts into NIFTY models\n\n'+table(learned,['target','model','n','brier','crps','mae','balanced_accuracy']),
      """The downstream stack's historical and current sector predictions are each built at their own past or current decision, using only sector labels already matured at that point. The domestic and direct-ETF benchmarks use the same target and dates. Complete intermediate returns and future foreign observations never enter the issue-time prediction layer. The IT and financial links can help with specific open targets without providing matching improvement after domestic price discovery or for the longer NIFTY endpoints.""",
      links(('ETF provenance and market-local clocks','us-etf-source-receipt.json'),('Sector scores','network-sectors-scores.csv.gz'),
            ('NIFTY direct and sector stack forecasts','network-nifty-scores.csv.gz'),('Matched gains and intervals','session-matched-evidence.csv')))

    z=filt(m,exercise='pre_session_decay',metric=['brier','crps'],candidate=['eq_fresh','eq_lag1','eq_lag2','eq_lag5','eq_lag17','eq_smooth','gift_conditional'])
    combined=filt(table0,exercise='pre_session_decay',cohort='combined',
                model=['domestic','eq_fresh','eq_lag1','eq_lag2','eq_lag5','eq_lag17','eq_smooth','gift_conditional'])
    post=filt(m,exercise='after_absorption',candidate=['eq_fresh','foreign_after_gap','rich_fresh'],metric='crps',
                 target=['remaining','regular_after_bar','firsthour_residual','five','next_gap'])
    r=filt(m,exercise='pre_session_decay',candidate=['us_fresh','us_stale','europe_fresh','europe_stale','asia_fresh','asia_stale'],metric='brier',
        target=['gap','regular','one','five','twentyone'])
    report('INFORMATION_DECAY_RESEARCH',
      """The primary decay grid fixes the 08:55 forecast clock across the same-morning gap, first hour, remaining cash session, same-day close, next-session return, and original three-, five-, ten- and 21-session endpoints. It compares the current eligible equal-market factor, versions delayed by 1, 2 or 5 NSE sessions, a 17-session block displacement, a three-session smooth, and the domestic-only reference. The 09:25 and 10:20 follow-up conditions the parent on the actual observed prefix. The 17:00 target keeps next opening and next close distinct. Forecast times remain tied to each comparison; a lag comparison is evaluated on identical cases. International regions receive distinct completed-session and stale-control contrasts.""",
      '## Fixed-clock information across horizons\n\n'+table(combined,['target','model','n','brier','crps','balanced_accuracy','covered']),
      '## Paired fresh, delayed and smoothed gains\n\n'+table(filt(z,metric='brier'),['target','candidate','control','n','gain','early_gain','later_gain','adjusted_low21','adjusted_high21']),
      '## Matched after opening and after the first hour\n\n'+table(post,['cutoff','target','candidate','control','n','gain','adjusted_low21','adjusted_high21']),
      '## Regional availability and age\n\n'+table(r,['target','candidate','control','n','gain','adjusted_low21','adjusted_high21']),
      """The close-to-close target includes the overnight component, so a modest close-to-close gain can arise mainly from the better opening distribution. The remaining cash-session return is separately scored after its reference price has been observed. Original five- and 21-session support matches the frozen earlier/later cohorts. The adjusted confidence bands reflect the reported V16 comparisons on this panel.""",
      links(('All decay regressions by cutoff and target','session-leaderboard.csv'),('Per-case 08:55 forecasts','decay-0855-scores.csv.gz'),
            ('Post-opening 09:25 forecasts','decay-0925-scores.csv.gz'),('10:20 forecasts','decay-1020-scores.csv.gz'),
            ('Matched decay evidence','session-matched-evidence.csv')))

    disagreement=filt(m,exercise=['pre_session_decay','after_absorption','ETF_NIFTY_link','opening_gap'],
        candidate=['disagreement','ETF_disagreement','gift_disagreement'],
        metric=['brier','crps'],target=['gap','regular','remaining','one','five','twentyone'])
    report('CROSS_MARKET_DISAGREEMENT',
      """Disagreement features include dispersion and sign agreement in the six-market basket, relative strength of US and Asian closes, technology against the broad market, the equity–volatility and equity–FX interactions, oil versus equity changes, global versus prior domestic return, and the offshore futures signal minus the global average. The ETF follow-up measures technology versus finance and domestic official breadth versus US equal-weight/cap-weight market spread. Medians and normalizing scales come from the matured fitting sample. The power products and signed relative values are prespecified continuous measures rather than thresholds picked by the best future score. Feature comparisons keep the price and risk anchor fixed, including once the cash gap is observable.""",
      '## Disagreement versus average, additive and GIFT baselines\n\n'+table(disagreement,
         ['exercise','cutoff','target','candidate','control','metric','n','gain','early_gain','later_gain','adjusted_low21','adjusted_high21']),
      """The candidate rows offer tests of conditional associations at different times and outcome lengths. Regime claims require agreement across early and later cohorts and across closed-session, fresh-Asia and delayed-input controls. The overnight level from offshore futures remains a demanding parent for judging whether market disagreements add direction or finer gap magnitude.""",
      links(('Full risk and direction scores','session-matched-evidence.csv'),('Joint risk transition results','volatility-matched.csv'),
         ('Global feature and session receipts','information-clock.csv.gz')))


def multiscale():
    l=csv('original-endpoint-leaderboard.csv')
    comb=filt(l,cohort='combined')
    matched=csv('multiscale-matched.csv')
    comp=filt(matched,candidate=['decomposed','decomposed_gift','session_state','multitask','fixed_mixture'],
             control=['historical_iv','V14_sign_shrinkage','V14_domestic_GJR','V15_gjr_restart'],metric=['brier','endpoint_crps'])
    subset=csv('path-gift-common-support.csv')
    subset=filt(subset,control='decomposed',metric=['brier','endpoint_crps'])
    n=csv('session-leaderboard.csv')
    stages=filt(n,cohort='combined',exercise='pre_session_decay',model=['domestic','eq_fresh','gift_conditional','network_stack'],
                target=['one','two','three','five','ten','twentyone'])
    report('MULTISCALE_DIRECTIONAL_FORECASTING',
      """At the fixed 08:55 cutoff before the first opening auction, the decomposition estimates the first gap, the first regular-session return and the remaining four or twenty sessions from separate matured labels. Sampled historical joint residuals preserve correlation across components. The GIFT variant forecasts the first gap from the eligible futures mark and estimates residual gap width on earlier paired cases. Its coverage diagnostic compares originals with an eligible quote and excludes fallback dates on both sides. Subsequent gaps, sessions, financial leadership and global risk states are drawn from already resolved coherent historical blocks rather than future observations. The state layer updates variance with the initial IV/GJR state and simulated innovations. For the multitask branch, gap, regular return, 1-, 3-, 5- and 21-session endpoints and a volatility ratio share a rank-two map reconstructed from labeled samples that all completed before the decision. The fixed mixture selects complete simulated paths from the historical IV, direct domestic and decomposed-GIFT laws.""",
      '## Common original endpoints\n\n'+table(filt(comb,model=['V14_sign_shrinkage','V14_domestic_GJR','V14_regime_state_joint','V15_gjr_restart',
                         'neutral','matured_historical','historical_iv','direct_domestic','direct_global','decomposed','decomposed_gift','session_state','multitask','fixed_mixture']),
                         ['horizon','model','n','brier','log_loss','endpoint_crps','endpoint_coverage80','endpoint_width80','balanced_accuracy']),
      '## Matched gains and uncertainty\n\n'+table(comp,['horizon','candidate','control','metric','n','gain','early_gain','later_gain','adjusted_low21','adjusted_high21']),
      '## Genuine GIFT coverage and isolated gap substitution\n\n'+table(subset,['horizon','candidate','control','metric','n','control_loss','candidate_loss','gain','adjusted_low21','adjusted_high21']),
      '## Cohort-specific direction probes by horizon\n\n'+table(stages,['target','model','n','brier','crps','balanced_accuracy']),
      """The first-session mechanism carries most of the measured opening information. Short multi-session aggregates can retain that component. Stronger archived original-weekly and monthly direction models remain the primary tests of long-horizon gains. Forecasting a later session conditional on an observed first gap is evaluated in the post-opening research, at a separately stated clock.""",
      links(('All original cohort comparisons','original-endpoint-leaderboard.csv'),('Exact quote-support ablation','path-gift-common-support.csv'),
            ('All paired tests','multiscale-matched.csv'),('GJR and model-state ledger','path-fit-ledger.json'),
            ('Model score rows','original-endpoint-scores.csv.gz')))


def volatility_and_paths():
    v=csv('volatility-leaderboard.csv')
    r=csv('volatility-preserved-references.csv')
    p=csv('volatility-matched.csv')
    w=filt(p,cutoff='08:55',metric='brier',candidate=['offshore_risk','gift_risk','global_disagreement','offshore_plus_domestic'],
           control=['raw_iv','fixed_iv_rv','student_EGARCH'])
    after=filt(p,cutoff=['09:25','10:20'],metric=['brier','mae'],candidate=['gap_plus_global','gap_global_breadth','gap_only_adjustment'],
               control='price_seen_risk_only')
    report('SESSION_AWARE_VOLATILITY_INTELLIGENCE',
      """The transition target is a 25% rise in annualized close-to-close realized volatility relative to the trailing H-session level. The preserved frequency, raw IV, 75/25 IV/RV and Student-t EGARCH forecasts are re-evaluated at the exact V15 original origins. The point model decomposes log close-to-close risk into squared overnight gaps, squared regular returns and their cross term. Adjustments to log odds retain the raw-IV probability as an offset. The 09:25 and 10:20 price-seen control replaces a share of expected overnight variance with already observed opening information. It conservatively caps the variance adjustment. Models adding offshore volatility, disagreement, GIFT magnitude and later cash features are compared on the same target and eligibility. MAE measures volatility level, QLIKE measures the realized-to-forecast variance ratio, and proper transition probability loss is scored independently.""",
      '## Exact frozen expansion references\n\n'+table(r,['horizon','model','n','rate','forecast_rate','brier','log_loss']),
      '## Before the auction\n\n'+table(filt(v,cutoff='08:55').sort_values(['horizon','brier']),['horizon','model','n','realized','volatility','mae','qlike','brier','log_loss','night_mae','regular_mae']),
      '## Direct offshore transition gains against strong controls\n\n'+table(w,['horizon','candidate','control','n','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21']),
      '## Revisions after the gap is observed\n\n'+table(after,['horizon','cutoff','candidate','metric','n','gain','adjusted_low21','adjusted_high21']),
      """The benchmark transition rankings favor the fixed blend weekly and Student-t EGARCH monthly. The best level, expansion or calibration model can differ. Post-auction risk revision results begin after the issue studied for the original endpoint. Monthly risk regimes remain strongly dependent across overlapping windows.""",
      links(('Original V15 benchmark replay','volatility-preserved-references.csv'),('Dated volatility forecasts and component outcomes','volatility-scores.csv.gz'),
            ('Complete model-specific loss ranks','volatility-leaderboard.csv'),('Matched adjustments and uncertainty','volatility-matched.csv'),
            ('Matured risk fit parameters','volatility-fit-ledger.json')))

    pts=csv('joint-path-leaderboard.csv')
    b=csv('passage-age-matched.csv')
    focus=filt(b,candidate=['decomposed_gift','session_state'],control=['V14_trend_shrink','V14_trend_persistent'],
               metric=['brier_by_1','brier_by_3','brier_by_5','touch_brier','integrated_brier','conditional_brier'])
    keep=['V14_constant_iv','V14_iv_scaled_blocks','V14_gjr_student','V14_gjr_iv','V14_trend_shrink','V14_trend_persistent',
          'V15_iv_restart','V15_gjr_restart','decomposed','decomposed_gift','session_state','multitask','fixed_mixture']
    r=csv('joint-path-matched.csv')
    rng=filt(r,candidate=['session_state','decomposed_gift'],control=['V14_gjr_student','V15_iv_restart','decomposed'],metric=['range_crps','vol_mae','energy'])
    report('SESSION_AWARE_PATH_FORECASTING',
      """Each joint law generates a whole open, high, low and close path relative to the original official close. Overnight and regular increments have separate predicted locations and first-gap uncertainty, preserving empirical signed covariance. Shifts preserve the candle constraints by maintaining excursions around the adjusted open and close. Future daily volatility evolves with simulated return and an earlier IV/GJR state. Foreign and financial leadership are modeled through joint draws of earlier resolved state blocks. The same ensemble produces the endpoint, highs, lows, range, volatility, barriers, drawdown and rebound. Energy is a normalized four-dimensional score for endpoint, range, volatility and drawdown. Every joint model generated **256** atoms per each of **482** original windows. Archived V14 and V15 joint laws, including both predecessor barrier leaders, are re-scored on the same reference and target.""",
      '## Joint marginals and proper scores\n\n'+table(filt(pts,model=keep),['horizon','model','n','range_crps','range_coverage80','vol_mae','touch_brier','integrated_brier','drawdown_crps','energy']),
      '## Age of the barrier benefit\n\n'+table(focus,['horizon','candidate','control','metric','n','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21']),
      '## Matched risk and range tests\n\n'+table(rng,['horizon','candidate','control','metric','n','gain','adjusted_low21','adjusted_high21']),
      """Passage probabilities come from the cumulative first occurrence on each path. We use five fixed up/down barrier pairs from 0.5% to 5%. The barrier probability test at day one, later cumulative tests and the event-by-end score all use the same root. The conditional table scores only realized survivors that remained untouched after session one, conditioning each law on the corresponding survival event. An early hit remains resolved. The improvement concentrated in first-session timing, while the range and residual monthly horizon remained difficult. Side-level survival counts, numerical monotonicity checks and archive hashes are preserved.""",
      links(('Path archive format and hashes','path-archive.json'),('All per-origin joint marginal scores','path-scores.csv.gz'),
            ('First touch and after-day-one survival','path-passage-scores.csv.gz'),('By-session comparison','passage-by-session.csv'),
            ('Matched timing gains','passage-age-matched.csv'),('Common surviving barrier support','passage-conditional-support.csv'),('Previous exact joint laws',V15LINK)))


def strong():
    a=csv('original-endpoint-leaderboard.csv')
    f=csv('multiscale-matched.csv')
    leaders=filt(a,cohort='combined')
    include=('neutral','matured_historical','prev_momentum','prev_mean_reversion','historical_iv','direct_domestic','direct_global','fixed_mixture',
             'V8_R_RESIDUAL','J11_BREADTH_ALL','V12_NATIVE_RV','V13_IV_all_phase','V14_sign_shrinkage','V14_domestic_GJR','V14_regime_state_joint',
             'V15_iv_restart','V15_gjr_restart','session_state','decomposed_gift')
    b=filt(leaders,model=include).sort_values(['horizon','brier'])
    c=filt(f,metric='brier',candidate=['neutral','matured_historical','prev_momentum','prev_mean_reversion','historical_iv','direct_domestic','direct_global',
           'decomposed_gift','session_state','fixed_mixture'],control=['V14_sign_shrinkage','V14_domestic_GJR'])
    archive=csv('session-leaderboard.csv')
    intro=filt(archive,exercise='opening_gap',cutoff='08:55',cohort='combined',
                  model=['neutral','historical','prior_return','domestic','single_US','equal_six','gift_raw','gift_calibrated'])
    report('STRONG_BASELINE_COMPARISON',
      """The primary weekly references are the historical V14 weekly sign-shrinkage Brier 0.228529 and return CRPS 0.010457. The primary monthly references are the V14 domestic location/GJR Brier 0.245042 and V15 restarted-GJR CRPS 0.024694. Neutral symmetric sign gives Brier 0.250000. We also score a matured empirical frequency and distribution, lagged momentum and mean reversion applied to centered joint paths, domestic rotation and official breadth, simple additive global and domestic state and fixed mixture. The protected V8 residualized rotation and V11, V12 and V13 comparators retain their documented coverage. Pre-auction single-US and simple equal-global returns are shown alongside the GIFT price-change rule.""",
      '## Simple same-morning baselines\n\n'+table(intro.sort_values('brier'),['model','n','brier','crps','log_loss','correct','balanced_accuracy']),
      '## Original weekly and monthly benchmarks on available cases\n\n'+table(b,['horizon','model','n','brier','endpoint_crps','log_loss','accuracy','balanced_accuracy']),
      '## Direction gain over the strongest earlier directional references\n\n'+table(c,['horizon','candidate','control','n','candidate_loss','control_loss','gain','early_gain','later_gain','adjusted_low21','adjusted_high21']),
      """Earlier standalone probabilities may have different empirical support and score distributions from the coherent path benchmarks. The protected historical benchmark results remain comparable on matched dates. The core forward assumption remains that all outcomes after the original decision must be forecast or integrated out.""",
      links(('Original cohort-level leaderboard','original-endpoint-leaderboard.csv'),('Original endpoint scores','original-endpoint-scores.csv.gz'),
            ('Matched original-horizon uncertainty','multiscale-matched.csv'),('Frozen V15 model ranking',V15LINK)))


def validation_and_forward():
    p=read('point-in-time-verification.json')
    s=read('no-future-and-copy-verification.json')
    pred=read('predecessor-protection.json')
    n=csv('refit-reselection-null.csv')
    v=csv('opening-gap-deletion.csv')
    k=csv('opening-gap-sensitivity.csv')
    q=filt(csv('session-matched-evidence.csv'),exercise='opening_gap',cutoff='08:55',metric='brier',
           candidate=['without_spx','without_dow','without_nikkei','without_hsi','without_dax','without_ftse',
                      'shuffled_foreign','noisy_foreign','gift_delay10','gift_delay25','gift_roll_screened'])
    agg=filt(v,cutoff='08:55',model='gift_raw')
    agg=agg.groupby(['control','deletion'],as_index=False).agg(cases=('omitted','size'),lowest_Brier_gain=('brier_gain','min'),
                                                             highest_Brier_gain=('brier_gain','max'),lowest_CRPS_gain=('crps_gain','min'))
    b=filt(k,cutoff='08:55',model='gift_raw',control='equal_six',metric='brier')
    report('VALIDATION_AND_FALSIFICATION',
      f"""V16 independently checked **{p['eligible_clock_checks']:,}** eligibility timestamps in the decision panels, including earlier domestic quote times, foreign session marks, intraday closes and delayed GIFT controls. The pre-auction tape is separate from the during-auction 09:10 observation. The same-morning audit covers official label identity, exchange-clock changes, minute bar end-plus-buffer, holidays, missing or nonstandard sessions, the expiry guard, alternative prior reference marks, large gaps and month deletions. The largest status risks for GIFT are the absence of per-contract IDs and historical quote-receipt timestamps. The chronological training masks require every model outcome to finish before the decision trading date. Priors, scalers, shrinkage, rank truncation and calibration estimate from earlier labeled data. At issue the monthly 21-session residual model cannot see any realized future gap, sector return or offshore price.""",
      '## Alternate age, source removal, noise and shuffled controls\n\n'+table(q,['candidate','control','n','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21']),
      '## Calendar and unusual-gap cuts for the raw vendor signal\n\n'+table(b,['case_filter','n','loss','base','gain']),
      '## Influence of omitted dates\n\n'+table(agg,['control','deletion','cases','lowest_Brier_gain','highest_Brier_gain','lowest_CRPS_gain']),
      '## Pre-registered shared endpoints and future-state checks\n\n'+table(pd.DataFrame(s['cases']),
          ['horizon','origin','decision','archive_equal','future_unchanged','fit_equal','clone_exact','laws']),
      '## Representative re-fit and re-selection with shuffled foreign blocks\n\n'+table(n,
          ['target','n_origins','challengers','refit_draws','observed_best','null_median','null_95','null_tail']),
      f"""The refit null uses earlier labels, fixed domestic anchors, 23 thinned dates and 39 block-shuffled refits, reselecting among three models per draw. The gap result is bounded by that discrete test design and all historical research exposures. Pairwise comparisons use {BOOT:,} circular block resamples at lengths {', '.join(map(str,BLOCKS))}. The 10- and 21-session adjusted bands use the maximum standardized contrast within each recorded family. Across the 482 original endpoint dates, **53** weekly and **11** monthly windows were disjoint. Verification reloaded **{pred['v15_artifacts']}** V15 artifact hashes and **{pred['v15_code']}** unchanged V15 source files, preserving V15’s earlier receipt of **{pred['earlier_verified_by_v15']['files']:,}** hashes. The comparisons remain exposed to choices accumulated across V1–V16.""",
      links(('Decision timestamp verification','point-in-time-verification.json'),('Future perturbation checks','no-future-and-copy-verification.json'),
            ('V15 protection','predecessor-protection.json'),('Null fit outputs','refit-null-forecasts.csv.gz'),('Open-gap date sensitivities','opening-gap-deletion.csv'),
            ('Validation and archive integrity receipt','validation-receipt.json')))

    ledger=read('forward-ledger.json')
    obs=[]
    for z in ledger['sessions']:
        d=z.get('nse_ohlc') or {}
        u=z['upstox_ohlc']
        obs.append(dict(day=z['day'],status=z['status'],source_status=z.get('http_status'),
                        official_open=d.get('open'),official_close=d.get('close'),upstox_close=u[-1] if u else None))
    rec=pd.DataFrame(ledger['records'])
    maturity=rec.realized_return.notna().sum()
    rec['sessions_verified']=rec.completed_target_dates.str.len()
    report('FORWARD_RESEARCH_LEDGER',
      f"""The independent refresh at **{ledger['checked_at']}** covered completed cash sessions through the calendar bound **{ledger['bound']}**. Authenticated Upstox read-only historical snapshots for NIFTY 50, India VIX, Bank NIFTY and NIFTY 500 are archived. Official NSE index reports independently verify the complete cash OHLC fields. November 24 was an NSE cash market holiday for Guru Nanak Jayanti. The archive records its status explicitly regardless of missing provider rows. No historical window in the November 17 main vintage uses these observations. [NSE capital market holiday circular](https://archives.nseindia.com/content/circulars/CMTR71775.pdf)""",
      '## Authoritatively reconciled dated bars\n\n'+table(pd.DataFrame(obs),
       ['day','status','source_status','official_open','official_close','upstox_close']),
      f'## Original locked target slots, {maturity} matured\n\n'+table(rec,
         ['version','key','horizon','issued','reference_session','reference_close','target','sessions_verified','maturity','realized_return']),
      """The V4 late diagnostics target November 25 and December 17. Their issue comes after the original opening process on November 18. Four V5 forecasts are frozen before their first target session and target November 26 and December 18. The original files retain their verified issue and prediction hashes. A valid resolution requires the original session sequence, completed target, official cash close and a publication guard at 18:00 IST. A search of archived issue records located these six forecasts as genuine prior issues. The V16 historical clocks are reconstructions and the V16 forward issuance count is zero.""",
      links(('Authentication, forecast hashes and status','forward-ledger.json'),('V15 original immutable tracking','../../../nifty_forecast_v15/2026-11-25/run-001/V15_FORWARD_RESEARCH_LEDGER.md')))


def comparison():
    all0=csv('session-leaderboard.csv')
    q=filt(all0,cohort='combined')
    morning=filt(q,exercise='opening_gap',cutoff='08:55')
    tabs=[]
    for desc,f,stat in [
        ('Opening gap direction',morning,'brier'),('Opening-gap distribution and magnitude',morning,'crps'),
        ('Next opening gap',filt(q,exercise=['pre_session_decay','after_close'],cutoff='08:55',target='next_gap'),'brier'),
        ('Regular-session return',filt(q,exercise='pre_session_decay',target='regular'),'crps'),
        ('Single-session endpoint',filt(q,exercise='pre_session_decay',target='one'),'brier')]:
        ranked=top(f,['target'],stat,5)
        tabs.append('## '+desc+'\n\n'+table(ranked,['target','model','n','disjoint','brier','crps','mae','rmse','log_loss','balanced_accuracy','covered']))
    e=filt(csv('original-endpoint-leaderboard.csv'),cohort='combined')
    e=e[e.n.eq(e.horizon.map(EXPECTED))]
    end1=top(e,['horizon'],'brier',5);end2=top(e,['horizon'],'endpoint_crps',5)
    vol=filt(csv('volatility-leaderboard.csv'),cutoff='08:55')
    p=csv('joint-path-leaderboard.csv')
    s=csv('continuation-leaderboard.csv')
    t=csv('gap-fill-leaderboard.csv')
    report('COMPLETE_MODEL_COMPARISON',
      """Targets have their own loss units, support and historical comparisons. Leaders below use the corresponding coverage and objective. Current-session return after an observed opening prefix remains in its own experiment. Some earlier endpoint systems cover a subset of original windows. The full tables retain their usable dates, earlier/later and combined cohorts, calibration, matched alternatives, block uncertainty, dependence checks and failure controls.""",
      *tabs,
      '## Gap continuation and reversal\n\n'+table(top(s,['cutoff','target'],'brier',2),['cutoff','target','model','n','brier','log_loss','actual']),
      '## Gap-fill survivors\n\n'+table(top(t,['cutoff','threshold'],'integrated_brier',2),['cutoff','threshold','model','n','brier','integrated_brier','conditional_abs_minutes']),
      '## Original five- and 21-session direction\n\n'+table(end1,['horizon','model','n','brier','log_loss','accuracy','balanced_accuracy']),
      '## Weekly and monthly endpoint distributions\n\n'+table(end2,['horizon','model','n','endpoint_crps','endpoint_mae','endpoint_coverage80','endpoint_width80']),
      '## Volatility expansion\n\n'+table(top(vol,['horizon'],'brier',4),['horizon','model','n','brier','log_loss','mae','qlike','expansion_rate','forecast_rate']),
      '## Range and joint path leaders\n\n'+table(top(p,['horizon'],'range_crps',5),['horizon','model','n','range_crps','range_coverage80','range_width80','energy']),
      '## Barrier touch and cumulative time-to-event\n\n'+table(top(p,['horizon'],'touch_brier',5),['horizon','model','n','touch_brier','integrated_brier','drawdown_crps','energy']),
      links(('Full session targets and eligibility','session-leaderboard.csv'),
         ('All matched decay gains','session-matched-evidence.csv'),('All original endpoint controls','original-endpoint-leaderboard.csv'),
         ('Original direction adjusted gains','multiscale-matched.csv'),('First-touch conditional results','passage-age-matched.csv'),
         ('Volatility matched scores','volatility-matched.csv'),('All path scores','joint-path-leaderboard.csv')))


def synthesis():
    a=csv('v15-v16-opening-matched.csv')
    g=one(a,cutoff='08:55',candidate='gift_raw',control='V15_offshore_fresh',metric='brier')
    gc=one(a,cutoff='08:55',candidate='gift_raw',control='V15_offshore_fresh',metric='crps')
    gf=filt(csv('session-leaderboard.csv'),exercise='opening_gap',cutoff='08:55',cohort='combined')
    row=one(gf,model='gift_raw')
    z=one(gf,model='gift_roll_screened')
    b=csv('passage-age-matched.csv')
    wk=one(b,horizon=5,candidate='decomposed_gift',control='V14_trend_shrink',metric='touch_brier')
    day1=one(b,horizon=5,candidate='decomposed_gift',control='V14_trend_shrink',metric='brier_by_1')
    cc=one(b,horizon=5,candidate='decomposed_gift',control='V14_trend_shrink',metric='conditional_brier')
    dec=csv('session-matched-evidence.csv')
    d=filt(dec,exercise='pre_session_decay',candidate='gift_conditional',metric='brier',
           target=['gap','firsthour','regular','one','two','three','five','ten','twentyone','next_next_close']).copy()
    d['order']=d.target.map(dict(gap=0,firsthour=1,regular=2,one=3,next_next_close=4,two=5,three=6,five=7,ten=8,twentyone=9))
    d=d.sort_values('order')
    original=csv('original-endpoint-leaderboard.csv')
    p=filt(original,cohort='combined',model=['V14_sign_shrinkage','V14_domestic_GJR','V15_gjr_restart','session_state','decomposed_gift','prev_mean_reversion'])
    report('FINAL_RESEARCH_CONCLUSIONS',
      f"""The original V15 opening-gap effect survived moving the decision before the NSE opening-price discovery process. Its score was unchanged at 08:30, 08:45 and 08:55, and delaying its completed foreign closes by an extra calendar day removed the gain. The strongest new directional evidence is the GIFT NIFTY vendor futures-change benchmark before the auction. At 08:55 on **{g.n}** matched mornings it improved Brier from **{g.control_loss:.6f} to {g.candidate_loss:.6f}** and arithmetic CRPS from **{gc.control_loss:.6f} to {gc.candidate_loss:.6f}**, with a 21-session family-adjusted Brier gain interval of **[{g.adjusted_low21:.6f}, {g.adjusted_high21:.6f}]**. Directional accuracy for the point-in-time vendor probability was **{row.correct:.2%}**, and after the broad rollover exclusion its score was **{z.brier:.6f}** on **{z.n}** mornings. Its actual calculation uses a prior futures mark and conservatively completed morning bars. Exact contract mapping and original delivery receipts remain unknown. Directly adding a broader global block to the GIFT signal generally lowered performance.""",
      f"""The GIFT-first model improved weekly barrier-touch Brier at original issue from **{wk.control_loss:.6f} to {wk.candidate_loss:.6f}** at **{wk.n}** origins, with an adjusted gain interval of **[{wk.adjusted_low21:.6f}, {wk.adjusted_high21:.6f}]**. The day-one improvement was larger, from **{day1.control_loss:.6f} to {day1.candidate_loss:.6f}**. For levels still untouched after day one, Brier was **{cc.control_loss:.6f} versus {cc.candidate_loss:.6f}**, with [{cc.adjusted_low21:.6f}, {cc.adjusted_high21:.6f}] gain bounds. Forecasting when the first hit happens and which side the market finally closes on remain separate. Pre-open foreign sector signals were most effective at their respective intermediate Indian opens. Later relative and regular-session outcomes were harder. The later cash return in the gap direction was only about one half of cases. Volatility expansion retained the established weekly fixed-blend and monthly Student-t EGARCH Brier leads.""",
      '## Decay of a fitted GIFT contribution compared with domestic predictors\n\n'+table(d,
                 ['target','n','control_loss','candidate_loss','gain','adjusted_low21','adjusted_high21']),
      '## Original weekly and monthly results\n\n'+table(p,['horizon','model','n','brier','endpoint_crps','log_loss','balanced_accuracy']),
      """Evidence is strongest for a morning opening-gap forecast and early passage probabilities. Five- and 21-session original-issue directional gains remain unestablished against the strongest archived predictors. The archive tracks the completed refresh and only the original forward benchmark issues. The historical score confidence bands quantify this replay and require independent prospective validation.""",
      links(('Full objective-specific leaderboards','V16_COMPLETE_MODEL_COMPARISON.md'),('Exact original-gap audit','V16_OPENING_GAP_REPRODUCTION_AND_TIMING_AUDIT.md'),
            ('Offshore basis and rollover sensitivity','V16_OFFSHORE_PRICE_DISCOVERY.md'),('Forward status','V16_FORWARD_RESEARCH_LEDGER.md'),
            ('Opening-gap and information decay figure','opening-gap-and-decay.png')))

    report('NEXT_EXPERIMENTS',
      """1. Freeze 08:30 and 08:55 prospective forecasts with vendor receipt times, quote-staleness handling, the single-US and V15 controls, and a tagged GIFT instrument. Register cutoff and evaluation support before each outcome.
2. Obtain timestamped per-expiry NSE IX NIFTY futures histories. Match old and new expiries across vendor roll periods and preserve clean, auditable basis and contract choice.
3. Capture auction indicative indices after 09:00 separately. Compare forecast information that predated the auction with information observed during opening equilibrium formation.
4. Freeze the simple pre-auction futures forecast for first-session barrier passage. Evaluate whether it improves a matched risk-set forecast after the first touch or first cash bar.
5. Continue the fixed-blend weekly and Student-t EGARCH monthly volatility-transition experiments, with expansion, risk-point accuracy and calibration scored separately.
6. Continue only a compact multiscale comparator with the immutable strongest weekly and monthly endpoint references and disjoint forward windows. Assess later session information after the cash gap using genuinely timestamped observations.""",
      links(('Validation caveats and falsifications','V16_VALIDATION_AND_FALSIFICATION.md'),('Existing locked forward issue status','V16_FORWARD_RESEARCH_LEDGER.md')))


def draw_chart():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    r=csv('v15-v16-opening-matched.csv')
    k=filt(r,candidate='gift_raw',control='V15_offshore_fresh',metric='brier').sort_values('cutoff')
    d=filt(csv('session-matched-evidence.csv'),exercise='pre_session_decay',candidate='gift_conditional',metric='brier')
    keys=['gap','regular','one','next_next_close','three','five','ten','twentyone']
    labels=['Opening\ngap','Regular\nsession','Same-day\nclose','Next\nsession','3\nsessions','5\nsessions','10\nsessions','21\nsessions']
    z=d.set_index('target').loc[keys]
    fig,ax=plt.subplots(1,2,figsize=(12,4.6),layout='constrained')
    idx=np.array([0,15,25,40])
    ax[0].axvline(30,linestyle=':',color='#666',linewidth=1,label='09:00 auction starts')
    ax[0].plot(idx,k.control_loss,'o-',label='V15 offshore model on matched mornings',color='#6b7280')
    ax[0].plot(idx,k.candidate_loss,'o-',label='GIFT price-change model',color='#174987')
    ax[0].set_xticks(idx,k.cutoff)
    ax[0].set_xlabel('Decision time (IST)')
    ax[0].set_ylabel('Opening-gap Brier score')
    ax[0].set_title('Opening-gap forecasts by decision time')
    ax[0].legend(loc='best',frameon=False,fontsize=8)
    v=z.gain.to_numpy()
    e=np.stack([v-z.adjusted_low21.to_numpy(),z.adjusted_high21.to_numpy()-v])
    ax[1].errorbar(np.arange(len(keys)),v,yerr=e,fmt='o',capsize=3,color='#174987')
    ax[1].axhline(0,color='#6b7280',linewidth=1)
    ax[1].set_xticks(np.arange(len(keys)),labels,fontsize=8)
    ax[1].set_ylabel('Brier gain vs domestic, with adjusted interval')
    ax[1].set_title('Information carried into later outcomes')
    for a in ax:
        a.grid(alpha=.2,axis='y')
    fig.suptitle('NIFTY V16 historical research through November 17, 2026')
    fig.savefig(OUT/'opening-gap-and-decay.png',dpi=180)
    plt.close(fig)


def index():
    order='\n'.join(f'- [{title}](V16_{name}.md)' for name,title in INDEX.items())
    (OUT/'NIFTY_V16_RESEARCH.md').write_text(f"""# NIFTY V16 research

The main historical vintage ends on **{FREEZE}**. V16 independently replays the V15 opening-gap discovery, tests pre-auction timestamps and authenticated GIFT observations, and follows the information through the Indian regular session and original five- and 21-session endpoints.

[Findings](V16_FINAL_RESEARCH_CONCLUSIONS.md) · [Model comparisons](V16_COMPLETE_MODEL_COMPARISON.md) · [Opening and decay chart](opening-gap-and-decay.png) · [Immutable forward ledger](V16_FORWARD_RESEARCH_LEDGER.md)

## Research reports

{order}

## Reproduction

[Commands](README.md) · [Original brief](MISSION.md) · [Experiment registration](registration.json) · [Validation](validation-receipt.json) · [Manifest](manifest.json)
""",encoding='utf-8')
    mods=['common','acquire sources','acquire intraday','acquire forward','replay gap','replay protect',
          'data','session_models opening','session_models decay','transmission','absorption','volatility','paths',
          'validation clock','validation offshore','validation docs','validation null','evidence','extra_comparisons','report','delivery']
    code='\n'.join('.venv/Scripts/python.exe -m research.nifty_forecast_v16.'+k for k in mods)
    fence=chr(96)*3
    (OUT/'README.md').write_text(f"""# Reproduce the V16 research

Run the following commands from the trading-desk root in PowerShell with the existing configured read-only Upstox analytics credential. The dated outputs remain under the V16 root. Set NIFTY_V16_OUT within artifacts/nifty_forecast_v16 for a different run and place a copy of the mission there. Preserve the saved receipts and fixed data files when reproducing the frozen historical results. The forward command deliberately refreshes separately using the execution timestamp.

{fence}powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:PYTHONDONTWRITEBYTECODE='1'
{code}
{fence}

Session distribution files archive the row-indexed log-return atoms. The row's law field gives the atom-array position. Per-case metrics use arithmetic ratios except for the direct archived V15 log-return reproduction and realized risk outcomes. The joint archives contain integer OHLC log ticks relative to the original official cash close, with separate simulated state diagnostics. The path manifest records the scale and predecessor pointers. The separate forward ledger preserves exact original target dates and issue hashes.
""",encoding='utf-8')


def run():
    reproduce()
    map_sources()
    advanced()
    gift()
    domestic_sessions()
    cross_market()
    multiscale()
    volatility_and_paths()
    strong()
    validation_and_forward()
    comparison()
    synthesis()
    draw_chart()
    index()
    print('Rendered all 18 reports and the research index',flush=True)

if __name__=='__main__':
    run()
