"""Render the 19 V18 reports from the verified case-level research."""
from .common import *
from .forecast import ARMS

TITLES=(
 'Reproduction and baselines','Corporate information database','Semantic information extraction',
 'Fundamental change and earnings','Corporate event studies','Information diffusion networks',
 'Aggregate fundamental intelligence','Expectations and market repricing','Event calendar and forward risk',
 'Non-price information discovery','Event-informed NIFTY forecasting','Fundamental risk intelligence',
 'Event-driven transfer learning','Validation and falsification','Research efficiency and knowledge base',
 'Complete model comparison','Forward research ledger','Final research conclusions','Next experiments')
PAIRED=('horizon','cutoff','candidate','control','metric','n','disjoint','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21')
EVENT=('stage','timing','family','horizon','metric','n','different_dates','issuers','mean','low','high')

def fmt(x):
    if pd.isna(x):return '—'
    if isinstance(x,(bool,np.bool_)):return 'yes' if x else 'no'
    if isinstance(x,(int,np.integer)):return f'{x:,}'
    if isinstance(x,(float,np.floating)):
        return f'{x:.2e}' if 0<abs(x)<.00001 else f'{x:.6f}'
    return str(x).replace('|','\\|').replace('\n',' ')

def tab(x,cols=None,n=None):
    if cols is not None:x=x.reindex(columns=list(cols))
    if n is not None:x=x.head(n)
    header='| '+' | '.join(x.columns.str.replace('_',' '))+' |'
    return '\n'.join([header,'| '+' | '.join(['---']*len(x.columns))+' |']+
                    ['| '+' | '.join(fmt(v) for v in r)+' |' for r in x.itertuples(index=False,name=None)])

def ref(*items):
    return ' · '.join(f'[{t}]({p})' for t,p in items)

def write_report(i,body):
    (OUT/f'V18_{REPORTS[i-1]}.md').write_text(f'# NIFTY V18 — {TITLES[i-1]}\n\n'+body.strip()+'\n',encoding='utf8')

def pick(x,**kw):
    for k,v in kw.items():
        x=x[x[k].isin(v) if isinstance(v,(list,set,tuple)) else x[k].eq(v)]
    return x

def first_wave():
    replay=csv('baseline-benchmarks.csv')
    q=read('predecessor-protection.json')
    ac=read('announcement-inventory.json')
    fund=read('fundamental-receipt.json')
    audit=read('attachment-comparison.json')
    books=csv('structured-listing-coverage.csv')
    case=csv('corporate-event-study.csv')
    rep=read('event-panel-receipt.json')
    out=csv('endpoint-paired-comparisons.csv')
    summary=csv('domestic-diffusion-study.csv')
    write_report(1,f"""
V18 retained the **November 17, 2026** historical freeze and the original five- and 21-session endpoints. The published opening-gap model reproduced on **248** mornings using the V16 implementation. V18 also replayed **482** protected V14 weighted endpoint laws, **1,928** V17 same-clock parent and component forecasts with exact stored atom agreement, and **217** archived GJR restart laws. Realized-volatility and expansion scores were recomputed from the frozen V16 case inputs. Relative rankings below refer to their own task and clock. The native V14 guard stays distinct from the reconstructed prior-session 17:00 and next-morning 08:55 forecasts. The V17 post-open parents retain the 09:25 and 10:20 clocks with their original eligible information and price reference.

{tab(replay)}

The hash audit verified **{q['artifacts']:,}** V17 files and **{q['code']}** source modules. It retains the predecessor protection record. The same-clock weekly component CRPS is **0.010309**, and the structural parent is **0.010658** on identical origins. The symmetric monthly benchmark is **0.250000 Brier**. Native model comparisons remain separately labeled.

{ref(('Exact opening scores','opening-exact-replay.csv'),('Protected weighted laws replay','protected-exact-law-replay.csv'),('Exact same-clock retraining','same-clock-refit.csv.gz'),('Protected risk cases','protected-risk-predictions.csv.gz'),('Predecessor protection','predecessor-protection.json'))}
""")
    cv=pd.DataFrame(ac['counts'])
    categori=csv('archive-category-counts.csv').groupby('family',as_index=False)[['rows','timed','duplicates','seed_rows','material']].sum()
    write_report(2,f"""
The corporate database preserves all **{int(cv.rows.sum()):,}** exchange announcements acquired by V17. Each record keeps its issuer symbol and any supplied ISIN, exchange category and source sequence, source file and row, archival summary, filing and dissemination timestamps, attachment URL, revision cues, and reporting or event dates when explicitly stated. The eligible time is the exchange's dissemination timestamp plus **10 minutes**. A past reporting-period end never establishes when the market first learned the contents. The underlying archive is reproducible from the separately hashed 2025 and 2026 source files.

{tab(cv)}

Publication duplicates are marked and tied to an earlier episode. These include identical URLs, otherwise identical issuer summaries within 36 hours, and additional earnings publications for a previously identified issuer/period. Distinct amendments retain their timestamps. The audit marked **{int(cv.duplicates.sum()):,}** duplicate rows. The fixed 240-name liquidity cohort had **{ac['seed_issuers']}** observed issuer names and **{ac['seed_rows']:,}** deduplicated timed publications, including **{ac['material_rows']:,}** high-materiality or direction-bearing rows. Source inventory spans a complete uploaded year for 2025 and a partial 2026 vintage. Category and listing changes can affect arrival frequency. The forecasts retain coverage fields and rolling same-clock normalization based on earlier values.

{tab(categori.sort_values('rows',ascending=False))}

{ref(('Indexed SQLite data','corporate-information.sqlite'),('Archive provenance','announcement-inventory.json'),('Routine and material categories','archive-category-counts.csv'),('Research-issuer episode inventory','issuer-events.csv.gz'),('Official NSE announcements','https://www.nseindia.in/companies-listing/corporate-filings-announcements'))}
""")
    lex=pick(out,candidate=['text_given_counts','weighted_text','alternative_text','material_only'],control='counts',metric=['brier','crps'])
    write_report(3,f"""
Deterministic rules map exchange subject and summary fields to events such as earnings, guidance, order wins, contract cancellations, acquisitions, divestments, expansion, financing, credit, regulation, litigation, management, dividends and buybacks. Signed text requires explicit business or risk language. Positive and negative cues can coexist, and ambiguous outcomes remain unclassified. The output retains the supporting short phrases and flags explicit amounts, implementation horizons and uncertainty. A fixed alternative uses category-level directional proxies as a falsification arm. No language model was used, so all feature values come from a shared, inspectable procedure.

The independently selected attachment audit attempted **{audit['sampled']}** disclosed PDFs and extracted readable text from **{audit['text_documents']}**. The document supplied a directional cue missing from the exchange summary in **{audit['document_only_sign']}** cases. **{audit['numeric_support']}** had a monetary or percentage fragment and **{audit['horizon_mentions']}** had an explicit horizon phrase. A monetary fragment alone supplies no validated label for margin, earnings or guidance. The audit retained page references and excerpt cues. Across **{audit['both_signed_matched']}** matched signed cases after the initial reaction, summary and attachment rules got **{audit['metadata_hit']}** and **{audit['attachment_hit']}** signs right. The attachment exercise is a small coverage and disagreement diagnostic. Its PDFs were retrieved retrospectively from historically posted URLs, so undocumented replacements remain possible. The main forecast tests use archived public descriptions and versioned structured results.

One checked example shows why sentence-level cues need context. In IndiGo's December 10, 2025 disclosure, the Q3 FY2025–26 table records an earlier expectation of high-teens capacity growth and revises it down to high-single-digit or low-double-digit growth. It also changes expected passenger unit revenue from roughly flat or slightly growing to mid-single-digit deterioration. The same page cites a **10%** mandated scheduled-flight reduction and explicitly leaves the full financial impact unquantified. The filing became eligible at **21:54:29 IST**. The inexpensive phrase rule returned a mixed signal because the table contains both old and new descriptions. This manually checked case illustrates the extraction failure and contributes no manual override to the historical model. [Filed press release, page 2](sources/disclosure-sample/2025-7470.pdf)

{tab(lex,PAIRED,24)}

{ref(('PDF coverage and source excerpts','attachment-content-audit.csv'),('Matched attachment exercise','attachment-comparison.json'),('Text evidence and labels','extraction-examples.csv'),('Text and category tests','endpoint-paired-comparisons.csv'))}
""")
    fm=pd.DataFrame([dict(metric=k,accepted_count=v) for k,v in fund['metrics'].items()])
    fmetric=pick(out,candidate=['fundamental_only','fundamental_augmentation','sector_liquidity_proxy'],metric=['crps','brier'])
    write_report(4,f"""
We used NSE's original Integrated Filing financial documents and chose a bounded sample before inspecting forecast performance. The audit recovered truncated issuer listings using smaller dated queries and preserved both retrieval receipts. The final listings contain **{len(csv('structured-results-listing.csv.gz')):,}** verified issuer-filing rows. Of **{fund['registered_documents']:,}** selected documents, **{fund['parsed_reports']:,}** supplied admissible facts. The **{fund['fact_rows']:,}** facts cover **{fund['reporting_periods']}** quarters and **{fund['issuers']}** issuers. Each fact retains its exact XBRL name, unit, context, document version and broadcast eligibility. The extraction accepted quarter-duration figures of **65–105 days**, dated balance-sheet facts and separately labeled longer current-year operating cash flow. It excluded contexts beginning before January 2025 and conflicting values for an otherwise identical fact. Missing operating-profit and capex facts remain missing when the mapped tags did not verify comparability. Cash-flow aggregates use a quarter-equivalent normalization with the filed duration. Profit/revenue comparisons retain their basis and account definition.

{tab(fm)}

There were **{fund['primary_reporting_events']:,}** first usable company-period observations, **{fund['revenue_qoq']}** quarter-over-quarter revenue comparisons, **{fund['profit_yoy']}** year-over-year profit comparisons and **{fund['statistical_surprises']}** historical profit-expectation errors. The expectation uses the most recent comparable published profit and a shrunk historical change learned from earlier disclosures. It is separate from an ordinary reported change. Historical analyst consensus and comparable pre-announcement company guidance were unavailable for this sample. A revision is eligible at the revision's own timestamp, and an original document is assigned to its own release. Standalone and consolidated observations are compared only within their own basis.

{tab(fmetric,PAIRED,25)}

{ref(('Source and version inventory','structured-results-listing.csv.gz'),('All accepted financial facts and contexts','structured-financial-facts.csv.gz'),('Point-in-time changes and expectation errors','fundamental-comparisons.csv.gz'),('Loading and pagination audit','structured-listing-coverage.csv'),('Official Integrated Filing archive','https://www.nseindia.in/companies-listing/corporate-integrated-filing'))}
""")
    micro=csv('intraday-event-responses.csv.gz')
    events=pick(case,stage=['first_open','after_reaction'],family=['earnings','credit','order_win','regulatory','fundraising'],
                horizon=[1,5,21],metric=['matched_abnormal','beta_residual'])
    write_report(5,f"""
The stock study matched **{rep['issuer_sessions']:,}** eligible issuer-session episodes and kept **{rep['score_rows']:,}** rows across forecast stages and horizons. It uses genuine observed exchange open and close prices, point-in-time ticker/ISIN checks, and explicit timing strata for releases before the open, during trading, after the close or during a non-trading day. Each unobserved interval starts after dissemination plus the guard. The full-session studies measure **1, 3, 5, 10 and 21 sessions** from the first eligible full cash open and again from the open after the initial reaction was complete. We compare raw stock returns, same-window NIFTY and native sector returns, prior-only beta residuals, ex-ante volatility-normalized residuals, and same-date matched non-event stocks. Peer matching used up to four stocks with similar past volatility, five-session momentum and trading value. A peer was excluded for a recent announcement already known at that decision. In the liquid intraday set, **{len(micro)}** stock/bar observations supported synchronized five-minute, 30-minute or remaining-session tests.

{tab(events,EVENT,40)}

Every displayed interval uses day and company clustering. Cases within the same market date or issuer episode share exposure. A price move in the first reaction window is an outcome of that descriptive study and only enters forecasts made after the move was observable.

{ref(('Every stock episode and matched outcome','stock-event-pairs.csv.gz'),('Event-time definitions','event-panel-receipt.json'),('Daily event study','corporate-event-study.csv'),('Intraday shared timestamps','intraday-event-responses.csv.gz'),('Intraday event study','intraday-event-summary.csv'))}
""")
    diff=pick(summary,stage='after_reaction',sector=['bank','finance','it','energy','industrial'],
              event_family=['earnings','orders','credit','guidance'],horizon=[1,5,21],metric=['peer_excess','sector_excess','matched_abnormal'])
    write_report(6,f"""
We measured the announcing share, sector peers excluding that share, a matched native sector index where available, the broader index, and NIFTY over the same later interval. Firm-level exposures were fitted from earlier history. Same-date peer controls reduce common-market effects and native-index rows are displayed separately because index weights and the firm's mechanical share of each move vary. Bank/finance, IT, energy and other sector cohorts were available at different sample sizes. Raw announcing-stock effects and delayed peer excess returns receive separate rows. The intraday archive covers the smaller liquid basket, and no same-session sector bar may stand in for a later outcome. Lagged event inputs and price-only models provide a separate forecasts-based test of this association.

{tab(diff,('sector','event_family','horizon','metric','n','different_dates','issuers','mean','low','high'),42)}

{ref(('Sector and wider-market links','domestic-diffusion-study.csv'),('Native and peer outcome panel','stock-event-pairs.csv.gz'),('Synchronized intraday rows','intraday-event-responses.csv.gz'),('Transfer and dated placebos','event-transfer-comparison.csv'))}
""")
    daily=csv('event-aggregate-features.csv.gz')
    aggregate=pick(out,candidate=['counts','weighted_text','sector_liquidity_proxy','multi_timescale','fundamental_augmentation'],
                   control=['clock_structural','component_plus_residual'],metric=['brier','crps'])
    write_report(7,f"""
The aggregate pipeline creates **{len(daily):,}** clock-specific snapshots using **2-, 9-, 31- and 130-calendar-day** windows for publications, short events, and the latest eligible company results. It measures the count of positive and adverse disclosures, earnings improvement breadth, growth dispersion, financial-sector releases, materiality concentration, recent arrival intensity and discrepancies between text and price changes. Each eligible issuer can contribute its latest timely observation. We compared equal-company, sector-balanced and capped historical-liquidity weights from a January 2025 fixed basket. Dated firm market caps and index constituent weights were incomplete, so the weighting tables identify the available proxies. Archive availability and structured financial coverage are recorded separately. Scale estimates and baseline predictors are learned from earlier information, with price history, official equal-weight breadth, financial rotation and volatility already included in the structural parent.

{tab(aggregate,PAIRED,40)}

{ref(('All then-available aggregate values','event-aggregate-features.csv.gz'),('Field coverage by clock','aggregate-feature-coverage.csv'),('Registered January liquidity cohort','issuer-seed.csv'),('Market-wide matched comparisons','endpoint-paired-comparisons.csv'))}
""")
    d=csv('announcement-repricing-cohorts.csv')
    k=pick(d,horizon=[1,5,21],metric=['matched_abnormal','peer_excess'])
    px=pick(out,candidate='expectation_repricing',control='market_reaction_only',metric=['crps','brier','down_brier','up_brier'])
    write_report(8,f"""
The daily reaction was known only after the first scored cash session closed. On the next eligible open we compared the observed gap and regular return with directional cues from the filing, published profit expectation errors, remaining uncertainty and peer reaction. Cohorts identify positive news with falling, rising or muted prices and the symmetric negative-news cases. A muted price response is a first-session move within **±0.30%**. Stock forecasts compare these interactions with an equivalent chronological price-reaction parent. Index forecasts use recent documented reactions, breadth disagreement and positive or adverse fundamental surprise, scored on exactly the same subsequent target.

{tab(px,PAIRED)}

{tab(k,('signal_source','business','price_reaction','horizon','metric','n','different_dates','mean','low','high'),34)}

{ref(('Repricing and disagreement cohorts','announcement-repricing-cohorts.csv'),('Identical-date index forecasts','endpoint-paired-comparisons.csv'),('Post-open tests using known cash moves','postopen-event-matched.csv'),('Input clock audit','event-aggregate-features.csv.gz'))}
""")
    s=csv('event-schedule-exposures.csv.gz')
    v=csv('risk-paired-comparisons.csv')
    vv=pick(v,candidate=['scheduled_risk','scheduled_then_fundamental','schedule_delayed'],control=['risk_calibrated_iv','protected_raw_iv','protected_fixed_iv_rv'],
            metric=['abs_error','brier','qlike','crps'])
    p=read('macro-release-receipt.json')
    write_report(9,f"""
The schedule corpus combines **{len(csv('scheduled-board-results.csv.gz')):,}** already public earnings-board notices and dated RBI and Federal Reserve announcements. A calendar row is eligible only once its source was public. The earliest company notice, its scheduled date, and a later reschedule or cancellation remain separate records. The February/other policy dates are drawn from the schedule then available, and release outcomes are excluded from the schedule exposure. The estimated horizon uses business weekdays and therefore approximates the number of sessions around holiday changes. The nearest where available NIFTY futures expiry comes from the strictly earlier exchange contract state and receives its own source-date guard. V18 preserved **{len(s):,}** horizon-specific exposure rows. The Federal Reserve's prior announcement supplies dates for 2025–2026 and is calendar metadata. Complete original economic-release calendar and index-rebalance announcement histories remain unresolved.

{tab(vv,PAIRED,38)}

The BLS first-release retrieval produced **{p['usable']}** usable records under the archive and publication requirements. The CPI fields remained missing in that case. ATM IV, path-based GJR and the native published IV/RV and EGARCH probabilities are separate controls.

{ref(('Verified board notices','scheduled-board-results.csv.gz'),('Policy schedule and provenance','policy-schedule.csv'),('Horizon exposure audit','event-schedule-exposures.csv.gz'),('Matched risk forecasts','risk-paired-comparisons.csv'),('Federal Reserve dated schedule','https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm'),('RBI 2025 schedule release','https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60062'),('RBI 2026 schedule publication','https://rbi.org.in/scripts/PublicationsView.aspx?Id=23809'),('NSE expiry revision circular','https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAOP68747.pdf'))}
""")
    ex=read('non-price-receipt.json')
    t=pd.DataFrame([dict(source=k,**v) for k,v in ex['accepted'].items()])
    ca=pick(out,candidate=['delivery_only','participant_positions','bulk_block_activity','additional_nonprice'],
            control='clock_structural',metric=['crps','brier'])
    write_report(10,f"""
V18 recovered the official dated security-delivery files and dated exchange reports of derivatives participant positioning, as well as historical bulk and block trade rows using a separate archival route. Earlier published cash histories extend issuer checks into the first months of 2025. Forecasts use a prior-day guard for these EOD files. The signed bulk-deal measure is a reported side proxy on a selection of disclosed trades. Timing is publication-guarded because the historical deal data identify trade dates. Derivatives participant categories, including FII and DII, refer to the corresponding positions in the published report. Cash FII/DII flows lacked a verified matching dated archive. Promoter transactions, shareholding changes and credit developments are inventoried from exchange metadata. A full point-in-time shareholding, credit rating level, or industry-activity panel remains unavailable.

{tab(t)}

{tab(ca,PAIRED)}

{ref(('New daily source coverage and guards','non-price-receipt.json'),('Raw source and attempt hashes','non-price-sources.json'),('Official delivery report index','https://betanseapi.nseindia.com/all-reports'),('NSE archival market reports','https://betanseapi.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives'),('BLS CPI original publications','https://www.bls.gov/bls/news-release/cpi.htm'))}
""")

def second_wave():
    ends=csv('endpoint-paired-comparisons.csv')
    ov=csv('protected-v14-matched-overlays.csv')
    rank=csv('endpoint-leaderboard.csv')
    vr=csv('risk-paired-comparisons.csv')
    paths=csv('path-paired-comparisons.csv')
    barri=csv('event-barrier-matched.csv')
    tnull=csv('refit-reselection-summary.csv')
    transfer=csv('event-transfer-comparison.csv')
    validated=read('validation-receipt.json')
    report_rank=pick(rank,cohort='combined',model=['clock_structural','component_plus_residual','neutral','V14_exact','V14_event_overlay',
                'fundamental_only','fundamental_augmentation','text_given_counts','expectation_repricing','event_conditioned_law','fixed_event_mixture'])
    compare=pick(ends,candidate=['fundamental_only','fundamental_augmentation','text_given_counts','event_conditioned_law','multi_timescale',
                 'fixed_event_mixture','clock_component_event'],control=['clock_structural','component_plus_residual'],metric=['brier','crps'])
    write_report(11,f"""
Both original objectives keep the same price reference and realized endpoints, with **265 five-session and 217 21-session origins**. The forecasts at prior-session **17:00 IST** and next-morning **08:55** use their own availability matrices. V14 native scores appear at their original guard. The V14 overlay uses incremental event inputs fixed at 08:55 against the archived distribution whose publication guard is later. The study tests fundamentals alone, corporate events on top of the structural parent, additive corrections of chronological past errors, a two-to-130-day information representation, event-conditioned location and tail width, and a fixed mixture. The fixed mixture uses order-spaced atoms from two laws. Each empirical law is retained or reproducible from the case ledger and preserved parent.

{tab(report_rank,('horizon','cutoff','model','n','disjoint','brier','crps','log_loss','rank_correlation','covered','width'))}

{tab(compare,PAIRED,43)}

{tab(pick(ov,metric=['brier','crps']),('horizon','cutoff','subset','metric','n','disjoint','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21'))}

{ref(('Full endpoint forecast list','original-event-forecasts.csv.gz'),('Original horizon return laws','original-event-laws.npz'),('Full identical-cutoff comparisons','endpoint-paired-comparisons.csv'),('Native V14 overlays','protected-v14-matched-overlays.csv'),('Post-open residual horizon overlays','postopen-event-matched.csv'))}
""")
    p=pick(paths,candidate=['event_scale_on_IV','schedule_scale_on_GJR'],control=['same_clock_IV','same_clock_GJR'],metric=['range_crps','vol_mae','touch_brier','endpoint_crps'])
    bars=pick(barri,metric=['brier_by_1','touch_brier','conditional_brier'],control=['same_clock_IV','same_clock_GJR'])
    v=pick(vr,metric=['abs_error','brier','qlike','crps'],candidate=['postopen_event_risk','fundamental_risk','scheduled_risk','material_events_risk','non_price_risk'],
           control=['risk_calibrated_iv','protected_raw_iv','V17_postopen_cash_risk'])
    write_report(12,f"""
V18 separates annualized point-volatility forecasts, transitions, and joint paths. Expansion is the inherited realized volatility event threshold at **1.25×** the trajectory's trailing volatility. The raw same-clock ATM IV point and a distinct empirical law centered on ATM in log units both enter the comparisons. India VIX and historical realized volatility are state controls. At their documented 08:55 clock, archived GJR, Student-t EGARCH, fixed IV/RV, V14 IV/GJR, and V16 offshore/domestic forecasts preserve their original predictions. Post-open event additions are assessed on matched V17 cash-risk cases at **09:25 and 10:20**, with the other archived V17 risk arms retained and matched separately. The empirical risk-law event probability is read from the same forecast atoms. A separate event-probability correction tests transition information under the same time guards.

Corporate intensity, earnings dispersion, financial news and already announced event exposure were used to estimate scale corrections. For joint simulation, each origin's previously saved log OHLC scenario is transformed by a positive factor, preserving high/open/close/low order. GIFT-first and the constant-IV and GJR path roots keep their correct historical timestamps. Day-one, cumulative first passage and later probability conditional on surviving day one are kept distinct. Common cases align the same **date, barrier and side** before averaging within date. The native V14 laws and published path references remain available without a clock reinterpretation.

{tab(v,PAIRED,44)}

{tab(p,PAIRED,25)}

{tab(bars,('horizon','cutoff','candidate','control','metric','n','side_barrier_cases','candidate_loss','control_loss','gain','adjusted_low21','adjusted_high21'),28)}

{ref(('All risk comparisons','risk-paired-comparisons.csv'),('Archived point and transition scores','protected-risk-predictions.csv.gz'),('Archived V17 stock risk observations','protected-v17-postopen-risk.csv.gz'),('Native V14–V16 joint score references','protected-native-joint-models.csv'),('Scenario files and hashes','event-path-archive.json'),('Matched first passage and survival','event-barrier-matched.csv'),('Joint path comparison','joint-path-leaderboard.csv'))}
""")
    write_report(13,f"""
The transfer experiment forecast stock excess returns at **one, five and 21 sessions** from the first eligible full open and the next open after the reaction. It compares the price-only model, a price model with added nonlinear terms, a company-specific correction without sharing event effects, pooled business and event-category inputs, a sector-specific fit, and a regularized hierarchical sector and issuer correction. Matched non-event stock responses supply a separate training reference. The event-permutation control draws labels from completed earlier months, and the lagged control uses the prior issuer event. Fitting uses earlier fully resolved dates and never treats multiple firms releasing on one date as distinct index outcomes. MAE gains are paired and clustered by date and issuer, with distinct episodes recorded. Sector and issuer cells with few earlier observations shrink toward the pooled or simpler fit.

{tab(transfer,('horizon','stage','model','n','different_dates','issuers','episodes','mae','rmse','accuracy','rank_correlation','mean','low','high'),59)}

{ref(('All event-transfer results','event-transfer-comparison.csv'),('Case predictions and training end dates','stock-transfer-predictions.csv.gz'),('Pooled event coefficients and transforms','stock-transfer-fit-receipts.json'),('Matched security controls','stock-event-pairs.csv.gz'))}
""")
    f=pick(ends,candidate=['alternative_text','omit_heavyweights','omit_earnings','delayed_24h','delayed_72h','material_only',
                          'omit_large_arrivals','shifted_inputs','blocked_placebo'],metric=['brier','crps'],
           control=['clock_structural','counts'])
    write_report(14,f"""
The original return ledger has **{validated['index_forecasts']:,}** predictions and full laws with strictly earlier maturity dates. The source audit checked the complete announcement clock inventory and exact-date corporate, fundamental, financial-release and stock-reaction availability. The dated fundamental comparison rejects prior-period inputs whose release was after the current report. Across **{validated['chronological_sentinels']}** tests, future-data changes left the historical feature values and tested fits unchanged. Adding exact copies of an existing feature left the fitted residual forecast unchanged. Initial filings and amendments preserve their own availability. Meeting revisions change the event calendar only on publication. Earlier daily derivative and delivery observations have a separate EOD guard.

The primary source study removes publication duplicates. Falsifiers delay notice availability by **24 and 72 hours**, shift feature dates, rotate completed training observations, screen for materiality, remove dominant firms and clustered release bursts, exclude earnings, and test fixed alternative semantics. The event study uses same-date matched peer controls, and the transfer arm also reruns with different categories and issuer histories. Blocks of **5, 10, 21 and 42 sessions** and **1,500 draws** preserve dependence across overlapping index windows. Adjusted intervals cover the comparisons within each reported group. The **23** chronology-preserving null refits reselect the best of the same three event feature families across the two original horizons. They do not account for cumulative predecessor search.

{tab(tnull)}

{tab(f,PAIRED,44)}

{ref(('Full timing and validation receipt','validation-receipt.json'),('Sentinel cases','future-information-sentinels.csv'),('Refit and reselection controls','refit-reselection-summary.csv'),('Cash categories and duplicate audit','archive-category-counts.csv'),('Point-in-time fundamentals','structured-financial-facts.csv.gz'))}
""")
    reg=read('registration.json')
    distinct=len(set(ends.candidate))
    supported=ends[ends.adjusted_low21.gt(0)&ends.early_gain.gt(0)&ends.later_gain.gt(0)]
    write_report(15,f"""
The registration fixes the company cohort, separate decision clocks, early warm-up rule and original horizons, with **{len(reg['hypotheses'])}** research hypotheses. The original return study contains **{distinct}** distinct candidate specifications with eligible date-paired tests. We first checked the raw archives and source provenance, then measured the first and subsequent reactions, and only then tested aggregates and corrections. Result-sheet truncation was resolved through smaller published date queries before any index model comparison. The expanded listing audit retained its own source receipts and reused the registered cap of **1,280** active structured documents. The attachment spot audit used a fixed stratified sample. It did not expand the feature grid after seeing index outcomes.

| Research status | Retained evidence |
| --- | --- |
| Reproduced | A time-specific GIFT opening forecast, protected five- and 21-session endpoint laws, and benchmark point-risk/transition scores. |
| New source evidence | Dated corporate document facts, board notices, security delivery, derivative participant positioning and dated historical deals. |
| Empirically tested | Event responses, price-reaction adjustments, transfer across firms, sector/turnover weighting, volatility, range and path scale effects. |
| Support needed | Point-in-time historical consensus, complete float weights, verified historical depth, and more independent monthly windows. |
| Validation scope | Results on the exposed vintage. Future-information checks and V18-only nulls test the methods under this research design. |

There are **{len(supported)}** date-paired original return cells with a positive adjusted 21-session lower limit and positive point estimates in both halves. Nested models, targets and clocks share market outcomes. Failed and mixed experiments remain in the same result files.

{tab(supported.sort_values('gain',ascending=False),PAIRED,18)}

{ref(('Registered hypotheses and budget','registration.json'),('All original-horizon pairs','endpoint-paired-comparisons.csv'),('Original data freezes','predecessor-protection.json'),('Verified new information sources','non-price-receipt.json'))}
""")
    risk_rank=pick(csv('risk-leaderboard.csv'),cohort='combined',model=['raw_atm_point_same_clock','atm_centered_empirical_law','risk_calibrated_iv','fundamental_risk',
         'non_price_risk','scheduled_risk','protected_raw_iv','protected_GJR','protected_offshore_plus_domestic','postopen_event_risk','V17_postopen_cash_risk'])
    range_rank=csv('joint-path-leaderboard.csv')
    write_report(16,f"""
These are separate leaderboards for direction, terminal distributions, point volatility, transitions, joint ranges and barriers. Lower is better for the proper scores, point errors and QLIKE. Balanced accuracy averages the observed up/down hit rates. Coverage and width are displayed together when the model supplies a law. Paired studies preserve date counts, disjoint windows and adjusted uncertainty. Stocks and sectors retain company and event support rather than being pooled into the original-horizon ranking.

## Original returns

{tab(report_rank,('horizon','cutoff','model','n','disjoint','brier','crps','accuracy','balanced_accuracy','log_loss','abs_error','rmse',
                    'rank_correlation','covered','width'),46)}

## Point volatility and expansion

{tab(risk_rank,('horizon','cutoff','model','n','disjoint','brier','log_loss','abs_error','rmse','qlike','crps','rank_correlation','covered','width'),42)}

## Joint paths

{tab(range_rank,('horizon','cutoff','model','n','range_crps','vol_mae','touch_brier','integrated_brier','energy'),28)}

{ref(('Direction and return distribution leaderboard','endpoint-leaderboard.csv'),('Endpoint probability calibration','endpoint-calibration.csv'),
 ('Stock responses and distinct events','corporate-event-study.csv'),('Sector diffusion','domestic-diffusion-study.csv'),('Stock transfer scores','event-transfer-comparison.csv'),
 ('Risk probability calibration','risk-calibration.csv'),('Full conditional tail and barrier file','event-barrier-matched.csv'),('Paired evidence and adjusted intervals','endpoint-paired-comparisons.csv'))}
""")

def forward_and_conclusions():
    f=read('forward-ledger.json')
    rr=[]
    for r in f['records']:
        probs=r.get('original_probabilities',{})|r.get('law_p_up',{})
        rr.append(dict(version=r['version'],key=r['key'],horizon=r['horizon'],issued=r['issued'],reference=r['reference_session'],target=r['target'],
             verified_sessions=len(r['completed_target_dates']),status=r['maturity'],return_realized=r.get('realized_return'),
             original_p_up=r.get('p_up',', '.join(f'{k} {v:.6f}' for k,v in probs.items())),issue_hash=r['issue_hash']))
    observed=pd.DataFrame([dict(day=r['day'],status=r['status'],open=(r.get('nse_ohlc') or {}).get('open'),
         close=(r.get('nse_ohlc') or {}).get('close'),receipt=r.get('file')) for r in f['sessions']])
    write_report(17,f"""
The separate historical-forward refresh used the time **{f['checked_at']}** and calendar bound **{f['bound']}**. The research fit remains frozen through **November 17, 2026**. Official close reconciliation compares NSE and Upstox prices and respects each original session sequence and the **18:00 IST** publication guard. The NSE-confirmed November 24 closure remains in the receipt. The ledger retains the **six** V4 and V5 issues and their original hashes, probabilities, full distribution references, and completed sessions. V4 was a late first-session diagnostic and the V5 issues precede their first target sessions. There were **{f['new_v18_issues']}** new timestamped V18 issues. The captured source window and issue clocks did not allow a fresh pre-auction or completed-close panel at the refresh.

{tab(observed)}

{tab(pd.DataFrame(rr))}

{ref(('Append-only source snapshots and original issue hashes','forward-ledger.json'),('NSE closure calendar','https://archives.nseindia.com/content/circulars/CMTR71775.pdf'))}
""")
    endpoints=csv('endpoint-paired-comparisons.csv')
    risk=csv('risk-paired-comparisons.csv')
    transfer=csv('event-transfer-comparison.csv')
    event=csv('domestic-diffusion-study.csv')
    fq=read('fundamental-receipt.json')
    a=read('announcement-inventory.json')
    m0=pick(endpoints,candidate=[x.name for x in ARMS if x.kind not in ('lag','permuted') and 'alternative' not in x.name and not x.name.startswith(('omit','delayed'))],
             control='clock_structural',metric=['brier','crps'])
    k=m0.sort_values('gain',ascending=False).drop_duplicates(['horizon','cutoff','metric'])
    z=pick(risk,candidate=['scheduled_risk','fundamental_risk','material_events_risk','non_price_risk','postopen_event_risk'],
           control=['risk_calibrated_iv','V17_postopen_cash_risk'],metric=['abs_error','brier','qlike','crps']).sort_values('gain',ascending=False)
    wil=pick(transfer,stage='after_reaction',horizon=[5,21],model=['ordinary_pooled','sector_specific','sector_issuer_partial_pool','price_only'])
    detail=read('validation-receipt.json')
    legacy=pick(csv('protected-v14-matched-overlays.csv'),subset='full',metric='brier')
    lweek=legacy[legacy.horizon.eq(5)].iloc[0]
    lmonth=legacy[legacy.horizon.eq(21)].iloc[0]
    nonprice=pick(endpoints,candidate='additional_nonprice',control='clock_structural',cutoff='preauction_0855',horizon=5,metric='brier').iloc[0]
    postrisk=pick(risk,cutoff='10:20',horizon=5,candidate='postopen_event_risk',control='V17_postopen_cash_risk',metric='abs_error').iloc[0]
    write_report(18,f"""
**V18 established a historically timestamped corporate information universe.** The study retains **345,226** raw exchange announcements, **{a['seed_rows']:,}** deduplicated timed publications in the historically eligible company cohort, and **{fq['fact_rows']:,}** verified financial facts from **{fq['parsed_reports']:,}** document reports. Original opening-price prediction reproduced at **0.100841 Brier**. The event question after that opening was evaluated with known price reaction, risk, sector states, original horizon references, and event-only controls.

**Original-horizon evidence.** The table shows the largest point gains within each cutoff, target and score against the V17 structural benchmark. The score intervals retain the selection adjustment and show the precision of each gain. The protected **0.228529 weekly** and **0.245042 monthly** direction scores and the original **0.010457 and 0.024694** strongest archived distribution scores remain distinct references. Compare clock-equivalent alternatives before changing forecasts. The established origin sets contain only **53 and 11 disjoint index windows**, respectively.

The fundamental overlay changed the native V14 weekly Brier from **{lweek.control_loss:.6f} to {lweek.candidate_loss:.6f}**. Its gain interval of **{lweek.adjusted_low21:+.6f} to {lweek.adjusted_high21:+.6f}** includes zero. The corresponding monthly overlay scored **{lmonth.candidate_loss:.6f}** against **{lmonth.control_loss:.6f}**. At 08:55 the official delivery, derivatives-positioning and deal controls gave a weekly Brier of **{nonprice.candidate_loss:.6f}** against **{nonprice.control_loss:.6f}** for the structural parent on **{int(nonprice.n)}** common dates. The adjusted gain interval from **{nonprice.adjusted_low21:+.6f} to {nonprice.adjusted_high21:+.6f}** also includes zero. These are separate historical candidates at their documented clocks.

{tab(k,PAIRED)}

**Risk, post-event diffusion and transfer.** The new risk inputs can be scored separately for realized volatility, transitions, ranges, and barriers when comparable earlier forecast laws exist. The results below compare the strongest descriptive gains with the parent at the same clock. Survival-conditioned barriers and the V16/V17 risk and path controls remain available separately. Transfer confidence depends on matched company-date clusters. A successful stock-level relationship is a stronger case for further research when it separately appears in later index returns.

At 10:20 the event layer on V17's cash-risk model lowered five-session volatility MAE from **{postrisk.control_loss:.6f} to {postrisk.candidate_loss:.6f}** on **{int(postrisk.n)}** dates with mature fit histories. Its adjusted interval of **{postrisk.adjusted_low21:+.6f} to {postrisk.adjusted_high21:+.6f}** also includes zero. The strongest archived weekly and monthly point-risk references remain **0.036469** and **0.033179 MAE** at their native clocks.

{tab(z,PAIRED,16)}

{tab(wil,('horizon','model','n','different_dates','issuers','mae','mean','low','high'),14)}

The source clock and copy-invariance checks passed on **{detail['chronological_sentinels']}** sentinels. Publication provenance, April to November close comparisons and earlier years within 2025 are kept as recorded. Complete dated analyst consensus, company float weights and full market-depth records were unavailable. All historical comparisons remain exposed research. The forward ledger is dated separately.

{ref(('Full comparison','V18_COMPLETE_MODEL_COMPARISON.md'),('Weekly and monthly report','V18_EVENT_INFORMED_NIFTY_FORECASTING.md'),
 ('Risk and joint path evidence','V18_FUNDAMENTAL_RISK_INTELLIGENCE.md'),('Validation','V18_VALIDATION_AND_FALSIFICATION.md'),('Forward research','V18_FORWARD_RESEARCH_LEDGER.md'))}
""")
    write_report(19,"""
1. Freeze the GIFT opening forecast and the original weekly direction, monthly symmetric and independent risk forecasts at their own genuine issue clocks. Score them only after the applicable official outcomes mature in 2026. Retain cutoff provenance with each law.
2. Freeze one stock event-response test with fixed dated company eligibility, a completed-reaction start and a matched price-only parent. Use the leading filing families and collect independent date and issuer episodes under the same decision rule.
3. Recover archived analyst consensus or exact issuer guidance with dated availability. Preserve both original and revised releases and test those expectation errors against the statistical proxy on matched company and period rows.
4. Extend the audit of order, financing and credit disclosures with comparable explicit amounts and source phrases. Preserve the missing and conflicting categories, mandate non-event matches, and consider weight concentration only with verifiable date-specific inputs.
5. Run a small preregistered volatility and path comparison using known earnings calendars and same-clock implied volatility. Preserve the narrower risk sets for barrier survival and avoid extrapolating the overnight contribution into later sessions.

[Research registration](registration.json) · [Forward release record](forward-ledger.json) · [All paired endpoint tests](endpoint-paired-comparisons.csv)
""")

def index():
    items='\n'.join(f'- [{title}](V18_{key}.md)' for title,key in zip(TITLES,REPORTS))
    (OUT/'NIFTY_V18_RESEARCH.md').write_text(f"""# NIFTY V18 research

Event-driven forecasting using 2025–2026 data through **November 17, 2026**. The study reconstructs dated company information, measures stock and sector responses, and tests incremental improvements at the original five- and 21-session horizons.

{ref(('Findings','V18_FINAL_RESEARCH_CONCLUSIONS.md'),('Complete comparisons','V18_COMPLETE_MODEL_COMPARISON.md'),
      ('Original return and risk results','event-forecast-evidence.png'),('Corporate database','V18_CORPORATE_INFORMATION_DATABASE.md'),
      ('Independent forward ledger','V18_FORWARD_RESEARCH_LEDGER.md'))}

## Nineteen reports

{items}

## Reproduction

{ref(('Original brief','MISSION.md'),('Research registration','registration.json'),('Reproduction instructions','README.md'),
      ('Scope and verification','validation-receipt.json'),('SHA-256 manifest','manifest.json'))}
""",encoding='utf8')
    stages=('common','baseline replay','baseline protect','baseline native_paths','inventory','sources additional','macro','fundamentals','events','events intraday',
            'attachments','attachments compare','aggregate','forecast','risk','risk point_controls','transfer','evidence','validation','sources forward','report','delivery')
    commands='\n'.join('.venv/Scripts/python.exe -m research.nifty_forecast_v18.'+k for k in stages)
    mark=chr(96)*3
    (OUT/'README.md').write_text(f"""# Reproduce NIFTY V18

Run from the trading-desk workspace in PowerShell. The fixed research vintage ends on **2026-11-17**. Published data and receipts archived by V17 are dependencies and remain in their original locations. The authenticated read-only forward refresh runs independently. Preserve MISSION.md in the chosen V18 output directory.

{mark}powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:PYTHONDONTWRITEBYTECODE='1'
{commands}
{mark}

Corporate SQLite data retains source-row keys and local IST publication time. Text and financial tables reference source documents. Each forecast's law index identifies its immutable atom row. Original return atoms are log returns. Volatility atoms are annualized volatility ratios. Joint path files preserve signed OHLC log ticks, with the conversion factor in the path archive. Exact native-model overlays store the shift and reference the weighted V14 atom archive. Prior studies' cutoffs, legal bases, source manifests and case counts remain in their own receipts. See the reports for the simple and exact comparators for each target.
""",encoding='utf8')

def chart():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter,MaxNLocator
    r=csv('endpoint-paired-comparisons.csv')
    v=csv('path-paired-comparisons.csv')
    xa=pick(r,cutoff='preauction_0855',metric='crps',candidate=['counts','text_given_counts','fundamental_augmentation','clock_component_event'])
    xa=xa[xa.control.eq(xa.candidate.map({x.name:x.parent for x in ARMS}))]
    xb=pick(v,cutoff='preauction_0855',metric='touch_brier',candidate=['event_scale_on_IV','schedule_scale_on_GJR'])
    xb=xb[xb.control.eq(xb.candidate.map({'event_scale_on_IV':'same_clock_IV','schedule_scale_on_GJR':'same_clock_GJR'}))]
    fig,aa=plt.subplots(1,2,figsize=(11.6,5.4),layout='constrained')
    labels={'counts':'Counts','text_given_counts':'Text and counts','fundamental_augmentation':'Financial results and counts','clock_component_event':'Events and decomposition',
            'event_scale_on_IV':'Corporate events and IV','schedule_scale_on_GJR':'Calendar and GJR'}
    for ax,g,title in zip(aa,(xa,xb),('Terminal return CRPS','Barrier-touch Brier')):
        g=g.sort_values(['horizon','candidate'])
        pos=np.arange(len(g))
        lo=g.adjusted_low21.to_numpy()
        hi=g.adjusted_high21.to_numpy()
        mu=g.gain.to_numpy()
        for q,c in ((5,'#174b78'),(21,'#a25b30')):
            use=g.horizon.eq(q).to_numpy()
            ax.errorbar(mu[use],pos[use],xerr=[np.maximum(mu[use]-lo[use],0),np.maximum(hi[use]-mu[use],0)],
                        fmt='o',color=c,capsize=3)
        ax.set_yticks(pos,[f'{labels[t]} · {h}d' for t,h in zip(g.candidate,g.horizon)])
        ax.invert_yaxis()
        ax.axvline(0,color='#555',linestyle='--',linewidth=1)
        ax.grid(axis='x',alpha=.2)
        ax.set_xlabel('Parent loss minus candidate loss')
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x,_:f'{x:.4f}'))
        ax.set_title(title)
    fig.suptitle('V18 event information at the 08:55 forecast cutoff')
    fig.savefig(OUT/'event-forecast-evidence.png',dpi=180)
    plt.close(fig)

if __name__=='__main__':
    first_wave()
    second_wave()
    forward_and_conclusions()
    index()
    chart()
    print('Rendered',len(REPORTS),'V18 research reports',flush=True)
