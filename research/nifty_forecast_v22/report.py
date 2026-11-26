"""Write the V22 research reports, comparison figures and artifact index."""
from textwrap import dedent

from .common import *
from .reference import NATIVE_ANCHORS


TITLES=(
    'Reproduction and transfer forensics','International market database','International forecast tasks',
    'Global and country factor decomposition','Transferable market relationships','International market analogues',
    'Cross-market state transitions','India-specific domain adaptation','Internationally informed NIFTY forecasts',
    'International risk and tail intelligence','Transfer validation and falsification','Sample efficiency and transfer limits',
    'Hypothesis registry','Complete model comparison','Forward research ledger','Final research conclusions','Next experiments',
)


def fmt(x):
    if pd.isna(x):
        return '—'
    if isinstance(x,(np.floating,float)):
        return f'{x:.6f}'
    if isinstance(x,(np.integer,int)) and not isinstance(x,bool):
        return f'{x:,}'
    return str(x).replace('|','\\|')


def table(a,cols=None):
    if cols:
        a=a[list(cols)]
    if a.empty:
        return '*The matched comparison has no eligible rows.*'
    labels=[k.replace('_',' ') for k in a.columns]
    top='| '+' | '.join(labels)+' |\n| '+' | '.join('---' for _ in labels)+' |'
    return top+'\n'+'\n'.join('| '+' | '.join(fmt(v) for v in u)+' |' for u in a.itertuples(index=False,name=None))


def link(name,label=None):
    return f'[{label or name}]({name})'


def evidence(*files):
    return '\n\n'+' · '.join(link(f) if isinstance(f,str) else link(*f) for f in files)


def write_report(i,*parts):
    p=OUT/f'V22_{REPORTS[i-1]}.md'
    text='\n\n'.join(dedent(x).strip() for x in parts if x.strip())
    p.write_text(f'# V22 {TITLES[i-1]}\n\n{text}\n\n[Back to the V22 report index](NIFTY_V22_RESEARCH.md)\n',encoding='utf-8')


def score_rows(z,h,clock,models,scope='combined'):
    return z[z.horizon.eq(h)&z.cutoff.eq(clock)&z.scope.eq(scope)&z.model.isin(models)].set_index('model').reindex(models).dropna(how='all').reset_index()


def stage_one(boards):
    old=read('predecessor-receipt.json')
    arches=csv('protected-india-return-cases.csv.gz')
    r=arches[arches.cutoff.eq('native_0910')].groupby(['horizon','model'],as_index=False).agg(
        n=('day','size'),brier=('brier','mean'),crps=('crps','mean'))
    cohort=csv('v21-monthly-cohort-reproduction.csv')
    track=csv('v21-protected-tracking.csv').assign(mae_bp=lambda x:1.e4*x.mae)
    write_report(1,
        f"""
        Recomputed Brier, log loss, CRPS, mean and sign probability from {old['weighted_laws']:,} original weighted laws.
        Verified the SHA-256 of {old['verified_files']:,} V21 artifacts and {old['verified_code']:,} V21 source files before reuse.
        The replay uses the exact original weekly and monthly endpoints. Native 09:10 forecasts and rebuilt 08:55 forecasts retain their own clocks.
        """,
        '## Native reference scores',table(r),
        """
        The V21 aggregate monthly correction improved the early cohort and lost ground in the later cohort.
        The table measures V20 smooth5 loss minus V21 aggregate-position loss, so positive gains favor V21.
        """,table(cohort),
        '## Dated constituent reconstruction',
        'V21 lagged monthly constituent weights retained very close arithmetic tracking. These are realized reconstruction errors, in basis points.',
        table(track,('horizon','n','mae_bp') if 'n' in track else ('horizon','mae_bp')),
        """
        ## Transfer forensics

        V5 treated timed global markets as NIFTY predictors. Its 176 inputs included 52 aligned global features and used a timezone guard.
        The dated V5 laws and losses were rescored directly. V9 used nine sector residuals with an earlier 63-session beta and a
        150-name currently selected proxy universe. The rotation-plus-panel result scored 0.304341 Brier in 173 early cases and
        0.233628 in 92 later cases. Its target and universe limited portability.

        V10's weekly pooled research scored 0.271846 Brier versus 0.274024 for its NIFTY-only lane. Its shifted control scored
        0.270443. V18's company-level pooled event MAE was 0.012112 versus 0.011992 for the price-only reference. V21's stock
        pooling reconstructed realized index contributions but added little forecast information after aggregation. Its combined monthly
        market-relative pooled CRPS was 0.054919 versus 0.054781 for randomized auxiliary labels. V22 changes the unit of
        auxiliary supervision to a comparable local-market task, holds out entire countries or regions, and maps observed OHLC
        paths only after their own targets have matured.
        """,evidence('v5-cross-market-recomputed.csv','v9-cross-sectional-research-archive.csv','v10-transfer-replay.csv',
          'v18-event-transfer-replay.csv','v21-transfer-recomputed.csv','v21-monthly-cohort-reproduction.csv','v21-protected-tracking.csv',
          'predecessor-receipt.json','protected-india-return-laws.npz'))
    u=csv('market-universe-audit.csv')
    p=u[u.primary_eligible]
    receipt=read('international-source-receipt.json')
    check=csv('upstox-provider-comparison.csv')
    candidates=u[~u.primary_eligible]
    fred=[r for r in receipt['sources'] if r.get('source','').startswith('Federal Reserve')]
    gap=csv('international-calendar-gaps.csv')
    write_report(2,
        f"""
        The market database covers {FIRST} through {FREEZE}. It contains {int(p.eligible_close.sum()):,} primary price-index marks
        from {len(p)} market jurisdictions and {int(u.eligible_close.sum()):,} marks across primary and additional series.
        Official NSE OHLC was independently reconciled to the V11 close archive on {int(p.loc[p.code.eq('india'),'eligible_close'].iloc[0])} sessions.
        The universe admitted a broad local price index with at least 360 closes and at most 13% missing scheduled sessions. The archive
        has {len(gap):,} explicitly classified missing or vendor-only session records. Local labels retain exchange holidays, scheduled
        half days and time zones from exchange-calendars {receipt['calendar_version']}. A scheduled close plus 60 minutes is the standard
        availability guard for primary markets. It is a conservative reconstruction of information flow and depends on a daily vendor snapshot.
        [NYSE trading hours](https://www.nyse.com/trade/hours-calendars) · [JPX trading hours](https://www.jpx.co.jp/english/equities/trading/domestic/01.html) · [Exchange calendars](https://github.com/gerrymanoim/exchange_calendars)
        """,
        '## Primary price indices',table(p,('market','ticker','currency','exchange','eligible_close','valid_ohlc','missing_close','off_calendar_rows','utc_offsets')),
        """
        ## Return conventions and source comparison

        Price marks are unadjusted local index levels and subsequent returns exclude dividends. Optional USD returns translate the
        local index with matched as-of currency marks. FX, sector and size proxies, VIX, yields, and Brent are context.
        Germany uses the DAX price series. The DAX total-return index, the Ibovespa total-return index, the TOPIX ETF, and US duplicate
        headline and sector indices remain outside the primary label pool. Thailand does not meet the primary data threshold.
        [Official DAX price index](https://stoxx.com/index/daxk/) · [B3 Ibovespa methodology and convention](https://www.b3.com.br/en_us/market-data-and-indices/indices/broad-indices/ibovespa.htm) · [Nasdaq index variants](https://indexes.nasdaq.com/docs/NDX%20Versions.pdf)
        """,
        f"""
        Upstox returned a 13-instrument global catalog and six authenticated daily-candle samples from October 1 through November 17,
        2026. The table compares their displayed session labels with the primary vendor. Source agreement varies substantially,
        particularly for Japan and US levels. The samples retain all discrepancies and were never spliced into the scored primary
        series. All {len(fred)} attempted independent FRED series timed out. Foreign availability is reconstructed from the venue
        clock and historical chart dates. Several venue close series lack an independent point-in-time second feed.
        [Upstox global index catalog documentation](https://upstox.com/developer/api-documentation/announcements/global-instruments/) · [Upstox candle timestamp specification](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [Yahoo Finance world indices](https://finance.yahoo.com/markets/world-indices/)
        """,table(check,('code','n_matched','broker_only','provider_only','close_within_006','median_absolute_close_diff_pct','day_return_correlation')),
        '## Other candidate series and proxies',
        table(candidates,('code','ticker','role','convention','eligible_close','missing_close')),
        evidence('market-universe-audit.csv','international-source-receipt.json','nse-historical-source-chain.json','international-calendar-gaps.csv',
          'upstox-provider-comparison.csv','upstox-provider-pair-cases.csv','upstox-provider-date-offset-diagnostic.csv','international-daily-book.csv.gz'))
    cover=csv('local-task-coverage.csv')
    total=cover.groupby('horizon',as_index=False).sum(numeric_only=True)
    x=csv('international-feature-panel.csv.gz')
    y=csv('international-target-panel.csv.gz')
    defs=read('feature-definitions.json')
    write_report(3,
        f"""
        The panel contains {x.row.nunique():,} timestamped market states and {len(y):,} rows across five horizons.
        Each horizon measures {', '.join(map(str,HORIZONS))} local trading sessions, with the original NIFTY definitions retained
        at five and 21. The starting price is the previous local official close. The endpoint is the last scheduled close of the
        horizon. The target is usable in a fit only after its end session and its publication guard.

        The model issues 20 minutes before ordinary exchange opening. India starts at 08:55 IST, and V22 inputs also qualify for
        the separately scored 09:10 comparator. Intraday venue information after that day's Indian snapshot cannot enter the
        Indian V22 forecast. The pre-open clock and future observation timestamp are archived for every usable task.
        """,
        '## Outcome coverage in the canonical panel',
        table(total,('horizon','rows','return_rows','volatility_rows','ohlc_range_rows','global_rows','residual_rows','usd_rows','reversal_rows','expansion_rows','breadth_rows')),
        """
        Forecast heads cover return location, sign probability from a full law, move magnitude, realized volatility, future range,
        expansion and contraction, reversal, recovery, cross-market divergence, and limited breadth deterioration. Each OHLC law
        starts at the same prior price, preserving endpoint and path geometry. Volatility is annualized RMS log close-to-close
        returns times the square root of 252. The normalized target divides log return by trailing daily RMS volatility times the
        square root of the horizon. Future high minus low is measured relative to the original close.

        A local return and its USD-translated equivalent are separate fields. Dispersion, asynchronous breadth, sector leadership,
        currency, volatility and rates join by published time where supported. Broad participation is proxied locally only where
        a valid dated breadth or sector partner was available. The missingness is explicit, including targets that cross the freeze.
        """,
        'Local feature fields include '+', '.join(defs['local'])+'. Global and contextual fields include '+', '.join(defs['global_fields'])+'.',
        evidence('feature-definitions.json','local-task-coverage.csv','market-issue-clock-receipts.csv.gz','international-feature-panel.csv.gz',
          'international-target-panel.csv.gz','local-observed-paths.npz'))
    dep=csv('international-dependence.csv')
    pca=csv('global-pca-receipts.csv')
    decomp=boards[(boards.scope=='later')&(boards.code!='india')&boards.horizon.isin(ORIGINAL)&boards.model.isin(
        ('local_history','global_factor_only','pooled_with_context','factor_only','factor_and_innovation','loco_transfer','loro_transfer'))]
    decomp=decomp.groupby(['horizon','model'],as_index=False)[['global_mae','innovation_mae','brier','crps']].mean()
    residual=y.loc[y.code.eq('india')&y.cohort.notna()].groupby('horizon').agg(
        returns_available=('ret_log','size'),residual_available=('innovation_log','count'),total_variance=('ret_log','var'),
        residual_variance=('innovation_log','var')).reset_index()
    residual['residual_variance_ratio']=residual.residual_variance/residual.total_variance
    write_report(4,
        """
        Each local outcome includes total local log return, one global equity component, a regional-relative component and a remaining
        local innovation. The economic decomposition uses two shrunken exposures from the last 116 eligible matched daily observations.
        The common baskets exclude India and the evaluated market. Primary labels contribute once per market. ETF context cannot
        multiply a common factor. Europe, North America and Asia Pacific pool by venue region. India’s regional comparison is Asia Pacific.

        Realized international changes between the previous reference availability and the local target maturity are decomposition labels.
        Forecast inputs use only earlier available closes. The PCA comparison fits on earlier foreign returns with a two-day completion
        gap and is an explanatory context block. Strict leave-country and leave-region models use own-market state and FX only.
        """,
        f'The first ex-India PCA component had median earlier-window variance share {pca.first_pc_variance_share.median():.2%} and a median of {pca.paired_days.median():.0f} usable paired training dates.',
        table(dep),table(residual),
        """
        ## Forward prediction of components

        The table averages later held-time errors across foreign jurisdictions. Factor-only return prediction applies the lagged local
        exposure to predicted foreign components. The companion arm adds a shrunken predicted country innovation.
        GIFT and its opening-gap forecast are scored as controls in the Indian residual tests, so a fresh visible offshore move cannot
        independently establish transferable country-specific alpha.
        """,table(decomp),evidence('global-pca-receipts.csv','global-pca-loadings.csv','international-return-correlations-1.csv',
          'international-return-correlations-5.csv','international-return-correlations-21.csv','international-model-leaderboard.csv',
          'india-matched-comparisons.csv.gz'))


def transfer_and_analogues(boards,intervals,w):
    mean=boards[boards.code.ne('india')&boards.scope.eq('later')&boards.horizon.isin(ORIGINAL)].groupby(['horizon','model'],as_index=False)[
           ['brier','crps','rv_mae','qlike','range_mae','expansion_brier']].mean()
    arm=['local_persistence','local_own_only','loco_transfer','loro_transfer','partial_country','dominant_excluded',
         'country_shuffle','date_block_null','delayed_transfer','low_rank_shared','mechanism_momentum_reversal','mechanism_drawdown_recovery',
         'mechanism_volatility_clustering','mechanism_synchronization_relative','mechanism_breadth_leadership']
    ii=intervals[intervals.horizon.isin(ORIGINAL)&intervals.scope.eq('later')&intervals.reference.eq('local_persistence')&
         intervals.model.isin(['loco_transfer','loro_transfer','partial_country'])&intervals.metric.isin(('brier','rv_mae','expansion_brier'))]
    co=csv('transfer-coefficient-stability.csv')
    q=co[co.model.eq('loco_transfer')&co.horizon.isin(ORIGINAL)&co.feature.isin(('mom5','vol_level','vol_ratio','drawdown'))&
         co['head'].isin(('location','volatility','expansion'))]
    write_report(5,
        """
        V22 estimates transferable relationships from each market's own mature target. The common model minimizes date-balanced
        ridge loss, with one unit of aggregate fitting weight per available origin date. Test blocks are ten UTC calendar days.
        The last 255 days of eligible pooled training and up to 190 days of eligible local rows drive identical forecasting blocks.
        Every training window finishes before the beginning of its test block. A rank-two map shares estimated structure across
        four return heads. Partial pooling shrinks local slopes toward foreign coefficients while the local intercept is
        fitted on the local window. The contextual pooled rows may see earlier labels from the evaluated foreign market and are
        interpretable as chronological pooling. LOCO and LORO are the strict geography experiments.

        Five mechanism fits test momentum and reversal, drawdown and recovery, volatility clustering, synchronization and relative
        strength, and breadth and leadership. The table shows later country-average scores. Each negative control retains the original
        decision dates. Date-country shuffling permutes responses within a date. The core time control moves blocks of date-level
        common responses. Delayed transfer evaluates five-session-old state inputs. The concentration control omits the United
        States, Japan and Germany from training.
        """,
        table(mean[mean.model.isin(arm)]),
        '## Matched date-level contrasts against persistence',
        'The gain is reference minus challenger loss. Adjusted bounds account for the compared families within that horizon and metric. Negative countries count markets where the challenger increased the loss.',
        table(ii,('horizon','model','metric','observed_origins','n','gain','adjusted_low','adjusted_high','negative_countries','countries_observed')),
        '## Coefficient variation',
        table(q,('horizon','feature','head','n_entities','median','iqr','sign_agreement_country','sign_agreement_time','near_zero_fraction')),
        evidence('international-model-leaderboard.csv','international-matched-country-region.csv.gz','international-matched-date-intervals.csv.gz',
            'transfer-coefficient-stability.csv','international-coefficient-history.csv.gz'))
    atlas=csv('analogue-law-atlas.csv')
    a=csv('analogue-risk-cases.csv.gz')
    n=a.groupby(['horizon','model'],as_index=False).agg(n=('day','size'),terminal_crps=('terminal_crps','mean'),
       rv_mae=('rv_mae','mean'),range_crps=('range_crps','mean'),drawdown_crps=('drawdown_crps','mean'),expand_brier=('expand_brier','mean'))
    d=atlas.groupby(['horizon','model'],as_index=False).agg(mean_ess=('ess','mean'),mean_origin_dates=('dates','mean'),
         mean_episodes=('weeks','mean'),mean_regions=('regions','mean'),mean_largest_episode=('max_week_weight','mean'),
         max_single_episode=('max_week_weight','max'),mean_largest_region=('max_region_weight','mean'))
    law=int(atlas.loc[atlas.horizon.eq(21)&atlas.model.eq('mixed_metric')].sort_values('day').iloc[-1].law)
    example=atlas[atlas.law.eq(law)].iloc[0]
    ex=csv('analogue-law-members.csv.gz')
    ex=ex[ex.law.eq(law)].sort_values('weight',ascending=False).head(8)
    direct=w[w.cutoff.eq('native_0910')&w.scope.eq('combined')&
         ((w.horizon.eq(5)&w.model.eq(NATIVE_ANCHORS[5][0]))|(w.horizon.eq(21)&w.model.eq(NATIVE_ANCHORS[21][0])))]
    write_report(6,
        f"""
        The retrieval atlas contains {len(atlas):,} weighted path laws and {int(atlas.members.sum()):,} mapped empirical OHLC scenarios.
        Market-state matching uses earlier normalized trend, drawdown, level and change of volatility, efficiency, relative strength,
        breadth and sector proxies, cross-market dispersion, synchronization, VIX and global state. Nearest, covariance-shrunken
        Mahalanobis, regularized magnitude-metric, four-factor, trailing path, and sector-weighted distance are distinct arms.
        Their location and scaling statistics use eligible source states only. Random retrieval and a volatility-only India match
        are explicit controls.

        Source paths must have entirely matured before the target Indian issue. A mapped path divides every relative log OHLC
        mark by its own earlier daily RMS volatility and multiplies by India's earlier volatility. The method retains each entire
        local path, its internal OHLC ordering and terminal sign. The diversity rule takes at most two windows per global calendar
        week, at most one per country within that week, and at most 24 of 48 from a foreign region. Equal week mass limits repetition.
        The uncapped control retains closest neighbours without these limits. We report the realized region weight with Kish effective mass.
        """,
        '## Analogue comparison across the original NIFTY dates',table(n),
        'The strongest direct native distribution benchmarks below cover the same original outcomes. The standalone analogue laws use 08:55 information.',
        table(direct,('horizon','model','n','brier','crps')),
        '## Diversity and effective number of analogues',table(d),
        f'For the {example.day} 21-session mixed metric forecast, the most heavily weighted retrieved histories are shown below. Eligibility is certified through the underlying UTC maturity field.',
        table(ex,('market','region','origin','endpoint','episode','weight','distance','mapped_terminal')),
        """
        The foreign stress arm retrieves extreme complete eligible histories. Its mass provides historical stress illustrations and
        is intentionally excluded from ordinary forecasting conclusions. The ranked pure-return evidence includes the random and
        domestic-history controls, so any claimed analogue advantage must exceed a similar eligible retrieval procedure.
        """,evidence('analogue-law-atlas.csv','analogue-law-members.csv.gz','analogue-observed-path-laws.npz','analogue-risk-cases.csv.gz',
           'india-forecast-cases.csv.gz'))


def india_and_risk(boards,intervals,w):
    risk_codes=('local_persistence','local_own_only','loco_transfer','loro_transfer','partial_country',
                'country_shuffle','mechanism_volatility_clustering','mechanism_drawdown_recovery')
    names=('rv_mae','qlike','expansion_brier','contraction_brier','reversal_brier','recovery_brier','divergence_brier','breadth_deterioration_brier')
    later=boards[boards.scope.eq('later')&boards.code.ne('india')&boards.model.isin(risk_codes)].groupby(
                 ['horizon','model'],as_index=False)[list(names)].mean()
    i=intervals[intervals.scope.eq('later')&intervals.horizon.isin(ORIGINAL)&intervals.metric.isin(names[2:])&
       intervals.reference.eq('local_own_only')&intervals.model.isin(('loco_transfer','loro_transfer'))]
    write_report(7,
        """
        We used an observed past state and the next completed local window. Expansion means a realized-volatility ratio above
        1.25, contraction a ratio below 0.80. Momentum reversal is scored only when the preceding standardized five-session trend
        is at least 0.35 in magnitude. Recovery is scored after a standardized drawdown below −0.55. Divergence is a local
        innovation larger than 0.8 horizon-volatility units in a previously synchronized state. Breadth deterioration is an
        available proxy moving down by more than 0.60 normalized units. Those event-specific opportunity sets remain explicit.

        The simplest forecasting law uses trailing volatility and local historical event frequency. The pooled, held-country and
        held-region conditional heads use earlier state variables and clamp event probabilities to the declared finite range.
        The partial-country model shrinks local conditional coefficients toward foreign estimates. Tables use causal filtering
        and fully matured responses. Cross-country breadth history is visibly thinner than cash OHLC or volatility history.
        """,
        '## Later equal-country transition results',table(later),
        '## Matched date-level gains against the own-market ridge',table(i,('horizon','metric','model','observed_origins','countries_observed',
              'negative_countries','gain','low','high','adjusted_low','adjusted_high')),
        'The risk gains concentrate in realized-volatility MAE and monthly expansion or contraction. Country-specific recovery, reversal and breadth remain sensitive to the opportunity cohort, comparison metric and geography.',
        evidence('international-model-leaderboard.csv','international-matched-date-intervals.csv.gz','local-task-coverage.csv','international-leave-global-episode-out.csv.gz'))
    adaptation=w[w.scope.eq('combined')&w.cutoff.eq('preauction_0855')&w.model.str.startswith('adapt_')]
    fit=csv('india-adaptation-fit-receipts.csv.gz')
    ac=w[w.scope.eq('combined')&w.cutoff.eq('native_0910')&w.model.isin(
        ('parent_location_domestic_only','parent_location_international_only','parent_location_offshore_only',
         'parent_location_combined','parent_location_beyond_gift','secondary_location_domestic_only','secondary_location_beyond_gift',
         'parent_mixture_foreign_tail','parent_mixture_transfer'))]
    write_report(8,
        """
        India-specific adaptation used identical 60- and 120-origin samples at each available Indian date. Each row is chosen by
        exact maturity time and is already complete at forecast issue. Zero-centered, ordinary-strength and strong ridge fits
        anchor the comparison. A historical India prior uses an older preceding window where 45 mature rows exist. The international
        initialization uses standardized foreign coefficients mapped back to local feature units. The random prior uses the same
        foreign samples with within-date country labels permuted. A foreign-only law, hierarchical partial pooling, the domestic
        residual law, and complete-law mixtures supply separate designs.

        India retains guarded corporate reactions, financial rotation, official equal-weight breadth, participant positions and
        concentration, dated constituent weights and earlier constituent contribution forecasts, ATM IV and trailing realized
        volatility. The compared foreign prior requires only comparable market covariates. Residual overlays also combine a
        visible GIFT quote proxy and its opening-gap model. The 08:55 availability and the original issue-time cohort remain explicit.
        """,
        table(adaptation,('horizon','model','n','coverage','brier','crps','mae','rank_corr','coverage80')),
        f'The fixed-budget archive contains {len(fit):,} fits. All the reported foreign prior training outcomes precede the Indian cutoff.',
        '## Domestic versus international residual attribution',
        table(ac,('horizon','model','n','active','brier','crps','mae','rmse')),
        'Compare foreign-prior rows directly with zero-centered and randomized-prior rows at the same budget. Compare a foreign residual overlay with an otherwise identical India-plus-offshore overlay before attributing a gain to geographic transfer.',
        evidence('india-adaptation-fit-receipts.csv.gz','india-residual-fit-receipts.csv.gz','india-return-leaderboard.csv',
              'india-matched-comparisons.csv.gz'))
    lead=w[w.scope.eq('combined')&w.cutoff.eq('native_0910')]
    pick=pd.concat([pd.concat([g.nsmallest(6,'brier'),g.nsmallest(6,'crps')]).drop_duplicates('model')
                    for _,g in lead.groupby('horizon')])
    v=csv('india-matched-comparisons.csv.gz')
    choose={5:('secondary_location_beyond_gift','parent_location_domestic_only','parent_location_offshore_only',
               'parent_location_international_only','parent_scale_only','parent_asymmetry_only','parent_sign_only','parent_historical_shrinkage'),
            21:('parent_mixture_foreign_tail','parent_location_beyond_gift','parent_location_international_only','parent_scale_only',
                'parent_asymmetry_only','parent_sign_only','parent_historical_shrinkage')}
    attr=pd.concat([v[v.horizon.eq(h)&v.cutoff.eq('native_0910')&v.reference.eq(NATIVE_ANCHORS[h][0])&
               v.model.isin(choose[h])&v.metric.isin(('brier','crps'))&v.scope.isin(('combined','early','later','active_matched'))]
                for h in ORIGINAL],ignore_index=True)
    attr=attr.pivot_table(index=['horizon','model','scope','n'],columns='metric',values='gain').reset_index()
    write_report(9,
        """
        Weekly return is close to close over five eligible NSE cash sessions in the original research calendar, from the prior NIFTY
        cash close. The monthly definition uses 21 sessions and the same prior-close convention. The five-session population has
        173 early and 92 late origins. The 21-session population has 141 early and 76 late origins.

        Every coherent candidate probability, arithmetic expected return, median, quantile, interval and terminal tail probability
        comes from the same normalized atom weights. Location shifts use log-price units and carry the full empirical distribution.
        Dispersion and signed asymmetry are separate interventions. Sign recalibration changes positive and negative mass while
        retaining within-sign shapes. A historic distribution and the alternative law enter through true mixtures. The foreign
        tail mixture uses twelve percent tail-only analogue mass translated to the archived parent log location.

        Native weekly gains are small and mostly coincide with corporate, domestic or already visible offshore information. The
        selected weekly directional overlay beats the original V20 Brier score in this retrospective sample, and the winner for
        CRPS is a domestic residual fit. The monthly distribution has a small gain when sharing tail mass with a foreign law. Both
        gains have intervals that span zero. The native and pre-auction comparisons have separately preserved benchmark instances.
        """,
        '## Best native candidates across Brier and CRPS',table(pick,('horizon','model','n','active','brier','crps','log_loss','accuracy',
        'balanced_accuracy','mae','rmse','coverage80','width80')),
        '## Incremental skill against the protected V21 distribution parent',
        'Gain is parent loss minus candidate loss. An active estimate replays the parent on the same subset. Early and later rows retain their original benchmark populations.',
        table(attr,('horizon','model','scope','n','brier','crps')),
        evidence('india-return-leaderboard.csv','india-matched-comparisons.csv.gz','india-forecast-cases.csv.gz','india-forecast-laws.npz',
                 'india-probability-calibration.csv','india-search-adjusted-intervals.csv.gz'))
    risk=csv('india-risk-and-tail-leaderboard.csv')
    pt=risk[risk.scope.eq('combined')&risk.track.eq('point')]
    path=risk[risk.scope.eq('combined')&risk.track.ne('point')].copy()
    path['risk_mae']=path.rv_mae.fillna(path.vol_mae)
    path['expansion']=path.expand_brier.fillna(path.expansion_brier)
    path['contraction']=path.contract_brier.fillna(path.contraction_brier)
    path['range_cover']=path.range_covered.fillna(path.range_coverage80)
    ri=csv('india-risk-matched-intervals.csv')
    subset=ri[ri.model.eq('analogue_global_on_IV_GJR')&ri.metric.isin(('range_crps','drawdown_crps','rv_mae','expand_brier'))]
    vendor=csv('india-risk-analogue-source-sensitivity.csv')
    removed=', '.join(k.replace('_',' ').title() for k in vendor.excluded_sources.dropna().iloc[0].split())
    sensitivity=vendor.groupby(['horizon','model'],as_index=False).agg(n=('day','size'),range_crps=('range_crps','mean'),
        drawdown_crps=('drawdown_crps','mean'),effective_members=('effective_members','mean'))
    write_report(10,
        """
        The protected point-risk benchmarks reproduced exactly within rounding. Weekly ATM IV obtained 0.037814 MAE, offshore
        and domestic features 0.036469 MAE, and the IV/RV transition probability 0.152707 Brier. Monthly GJR obtained 0.033179 MAE and
        0.199677 variance QLIKE. Monthly Student EGARCH expansion scored 0.172872 Brier. The original native monthly Student-t GJR
        distribution scored 0.015422 range CRPS. Its separately replayed 08:55 GJR path reference scored 0.015488.

        The GARCH transfer trial evaluates five causal volatility parameter triplets and averages them using earlier performance.
        Date-balanced foreign risk, India-only risk and partially pooled variance forecasts are scored. IV or GJR anchored point
        hybrids retain the protected expansion probability unless explicitly recalibrated. The calibrated path arms rescale every
        OHLC trajectory consistently, including the heavy-tail monotone mapping. Path ranges, high and low touches, drawdown, tails
        and expansion and contraction are all recomputed from those same empirical weights. Expansion and contraction events use
        the protected V14 trailing reference, with exact V16 realized-volatility and V20 same-clock range checks.
        """,
        '## Point-risk leaderboard',table(pt,('horizon','model','n','vol_mae','qlike','expand_brier','p_expand','actual_expand')),
        '## Complete risk paths at 08:55',
        table(path,('horizon','track','model','n','risk_mae','range_crps','drawdown_crps','expansion','contraction','range_cover')),
        """
        Monthly volatility-scaled mixed analogues scored 0.014195 range CRPS, versus 0.014409 for scaled India-only historical paths
        and 0.015488 for the matched 08:55 parent. At five sessions, the strongest same-clock IV range model scored 0.005768 versus
        0.006155 from the foreign mixture. The almost identical weekly IV-anchored volatility MAE replicates the anchor's scale,
        while the monthly gains reflect measured differences in the path distribution. The multi-model adjusted intervals retain
        uncertainty. The extreme-episode tail law stays a stress scenario.
        """,
        table(subset,('horizon','reference','metric','n','gain','low','high','adjusted_low','adjusted_high')),
        '## Broker disagreement sensitivity',
        f'Reweighting the same matched paths after removing {removed} tests the strongest provider discrepancies. '
        'Those primary indices agreed within 0.06 price units on fewer than 10% of the overlapping Upstox daily sample. '
        'Surviving paths are rebalanced across weeks and rescaled to the same Indian volatility reference. This sensitivity '
        'describes dependence on the affected paths in the final laws. The earlier matching metric and retrieval candidate pool are fixed.',
        table(sensitivity),
        evidence('india-risk-and-tail-leaderboard.csv','india-risk-matched-intervals.csv','india-protected-native-path-benchmarks.csv',
          'india-calibrated-risk-ohlc-laws.npz','india-calibrated-risk-path-recipes.csv.gz','india-garch-pooling-receipts.csv.gz',
          'india-risk-analogue-source-sensitivity.csv'))


def validation_and_registry(w,inter):
    bands=csv('india-search-adjusted-intervals.csv.gz')
    n=csv('representative-blocked-refit-summary.csv')
    o=csv('india-episode-omission.csv.gz')
    choices=('secondary_location_beyond_gift','parent_location_domestic_only','parent_mixture_foreign_tail')
    b=bands[bands.cutoff.eq('native_0910')&bands.scope.eq('combined')&bands.block.eq(21)&bands.model.isin(choices)&
            bands.metric.isin(('brier','crps'))].copy()
    b=b[((b.horizon.eq(5)&b.model.ne('parent_mixture_foreign_tail'))|(b.horizon.eq(21)&b.model.eq('parent_mixture_foreign_tail')))]
    a=o[o.cutoff.eq('native_0910')&o.type.str.startswith('largest')&o.model.isin(choices)&
         ((o.horizon.eq(5)&o.model.ne('parent_mixture_foreign_tail'))|(o.horizon.eq(21)&o.model.eq('parent_mixture_foreign_tail')))]
    gates=read('leakage-and-duplication-controls.json')
    lead=w[w.scope.eq('combined')&w.cutoff.eq('native_0910')&w.kind.eq('protected')].groupby('horizon',as_index=False).agg(n=('n','max'),disjoint=('disjoint','max'))
    write_report(11,
        f"""
        Historical validation uses chronological blocks, whole-country and whole-region exclusion, a fixed July 1, 2026 later
        partition for the international task, and the original India cohorts. Within-date label permutations retain common dates.
        Other controls use date-block randomization, stale foreign inputs, own-market models, common-factor-only prediction,
        highly concentrated market removal, random retrieval, and a duplicated standardized series test. A mechanical feature
        copy changed predictions by {gates['duplicate_factor_max_difference']:.2e}. Injecting an extreme future feature changed
        earlier certified lookups by {gates['future_feature_poison_max_change']:.2e}. Every archived analogue member had a fully
        matured outcome at the recorded decision cutoff.

        Dependence is handled by aggregating international paired losses within dated blocks and by bootstrapping consecutive
        Indian origins. India also reports every disjoint phase, high and low regime slices, global episode and calendar month
        omissions, and the deletion of the largest favorable and largest absolute market blocks. The issue-time rule excludes labels
        whose maturity is equal to the cutoff. The direct foreign and local comparison has the same local feature family.
        """,table(lead),
        '## Native 21-origin block bootstrap for selected claims',table(b,('horizon','reference','model','metric','n','gain','low','high',
             'adjusted_low','adjusted_high')),
        '## Influence of the largest episodes',table(a,('horizon','model','metric','type','omitted','n','removed_gain','remaining_gain')),
        """
        ## Representative refit and reselection stress test

        For each horizon, four simpler residual variants were fit on the original chronological data and independently
        refit on 24 blocked training-label permutations. Each draw reselects the strongest member by its own paired score.
        The representative null can be centered below zero when an arbitrary correction degrades a strong parent. A small tail
        fraction against that null can accompany a negative absolute improvement, as illustrated by monthly MAE.
        Bootstrap and permutation evidence apply to the tested arms and these research-exposed dates. They cannot undo the
        accumulated search through V1–V22.
        """,table(n),
        evidence('leakage-and-duplication-controls.json','international-matched-date-intervals.csv.gz','international-leave-global-episode-out.csv.gz',
            'india-search-adjusted-intervals.csv.gz','india-disjoint-phase-results.csv.gz','india-episode-omission.csv.gz','india-regime-sensitivity.csv.gz',
            'representative-blocked-refit-reselection.csv','representative-blocked-refit-design.json'))
    d=csv('international-dependence.csv')
    a=csv('synthetic-transfer-sample-efficiency.csv')
    design=read('synthetic-transfer-design.json')
    sims=a[a.foreign_markets.eq(19)&a.train_local_origins.eq(60)]
    fit=csv('international-fit-receipts-21.csv')
    q=fit[fit.model.eq('loco_transfer')&fit.holdout.eq('india')]
    negatives=inter[inter.horizon.isin(ORIGINAL)&inter.scope.eq('later')&inter.reference.eq('local_persistence')&
             inter.model.isin(('loco_transfer','loro_transfer'))&inter.metric.isin(('brier','rv_mae','expansion_brier'))]
    write_report(12,
        f"""
        Twenty cash indices provide country-specific labels, with substantial shared shocks across
        the observations. A representative 21-session ex-India fit used median {q.n_rows.median():,.0f} eligible market rows across
        {q.n_dates.median():.0f} distinct origin dates and {q.n_global_weeks.median():.0f} global weeks. The eigenvalue participation
        ratio in the table describes cross-market dimensionality. It is an estimate of effective factor breadth and is not a
        count of independent Indian forward outcomes.

        The original 265 weekly and 217 monthly NIFTY origins yield only 53 and 11 disjoint windows. Overlap, related market regimes
        and the reuse of the same historical outcomes further limit inference. Coefficient medians, interquartile range and sign
        stability document parameter uncertainty. Negative transfer counts the markets whose later loss rose against the matched
        reference. Distribution uncertainty in India remains the paired and dependence-adjusted interval width.
        """,table(d),table(negatives,('horizon','model','metric','observed_origins','n','gain','negative_countries','countries_observed','adjusted_low','adjusted_high')),
        f"""
        ## Controlled simulation

        The six settings model stable shared slopes, separate country slopes, a shared shock with zero predictable return,
        temporarily shared slopes, structural reversal, and an unrelated India. The generator uses correlated equity features,
        46% common residual variance, and overlapping 5- or 21-session outcomes. Test windows are disjoint and use the real
        evaluation counts. The two local budgets use 60 or 120 observed origins. We vary the foreign count from one to eight to
        nineteen and refit four estimators per trial. The full experiment has {design['aggregate_replicates']:,} synthetic
        trials. The representative table uses 60 local origins and 19 foreign markets. Positive gain means lower MSE than ordinary
        zero-centered shrinkage. These are synthetic operating characteristics. Conclusions on NIFTY rely on the empirical study.
        """,
        table(sims,('horizon','data_generator','model','test_mse','parameter_rmse','mean_gain_vs_ordinary_shrink',
              'p10_gain_vs_ordinary_shrink','p90_gain_vs_ordinary_shrink','fraction_beating_ordinary_shrink')),
        evidence('synthetic-transfer-sample-efficiency.csv','synthetic-transfer-design.json','international-dependence.csv',
           'transfer-coefficient-stability.csv','international-fit-receipts-21.csv','india-search-adjusted-intervals.csv.gz'))
    registry=read('registration.json')
    statuses=('Feasible with coverage and vendor limits','Stable common dependence, weak innovation gains','Return transfer inconclusive',
              'Monthly conditional risk improves in several markets','Standalone return loses to protected direct laws',
              'Larger distinct episode representation with lower concentration','Monthly volatility and transition benefit',
              'Small and unstable fixed-budget transfer gains','Domestic or offshore complement dominates weekly',
              'Retrospective candidates only','Monthly range promising, point anchors retained','Earlier results reproduced',
              'Finite date clusters and meaningful synthetic negative transfer','Historical rehearsal and source staging complete')
    f=pd.DataFrame(registry['hypotheses']).assign(outcome=statuses)
    f.insert(0,'id',np.arange(1,len(f)+1))
    write('hypotheses-and-dispositions.csv',f)
    write_report(13,
        f"""
        Registered {len(f)} primary hypotheses at {registry['registered_at']}, before the initial V22 model and outcome evaluation.
        Each registry entry records the mechanism, markets, information cutoff, horizons, prior anchor, score, falsification,
        eligibility, finite candidate budget and criteria for deeper testing. The table shows study outcomes. The complete registry
        preserves the original commitments separately from the final dispositions.

        A comparable task was feasible with a traceable venue calendar and explicit coverage gaps. Stable volatility dependence
        transferred better than return direction. The ordinary shrinkage and common-factor-preserving control results capped the
        directional research. Subsequent work concentrated on analogues, volatility, drawdown, range and the information in
        complete distributions. All history through November 17 remains research-exposed.
        """,
        table(f,('id','name','strong_parent','metric','negative_control','eligibility','budget','outcome')),
        evidence('registration.json','hypotheses-and-dispositions.csv','representative-blocked-refit-summary.csv'))


def remaining_reports(boards,w,inter):
    family=[
        ('International direction and distributions','international-model-leaderboard.csv','Country-level and chronological model comparisons with Brier, log loss, CRPS, accuracy, balanced accuracy, MAE, RMSE, rank, interval coverage and risk.'),
        ('Country and region generalization','international-matched-country-region.csv.gz','Matched loss by market and by held-out region, with the opportunity count for each event.'),
        ('International mechanisms and uncertainty','international-matched-date-intervals.csv.gz','Date-weighted comparisons, negative countries, raw and family-adjusted block limits.'),
        ('Historical analogue retrieval','analogue-law-atlas.csv','Membership, distinct dates, weeks and regions, Kish effective count, and weights.'),
        ('Standalone analogue paths','analogue-risk-cases.csv.gz','Terminal, point and tail/path outcomes from the retrieved OHLC scenarios.'),
        ('India adaptation','india-adaptation-fit-receipts.csv.gz','Exact local budgets, pool maturity, penalties and local or foreign priors.'),
        ('Original NIFTY direction and coherent distributions','india-return-leaderboard.csv','Both horizons and clocks, early, later, combined, and active results.'),
        ('Matched NIFTY effects','india-matched-comparisons.csv.gz','Both protected reference families, active coverage, explicit paired comparisons.'),
        ('Volatility and market risk','india-risk-and-tail-leaderboard.csv','Protected point and path risk versus new hybrids at same definitions.'),
        ('Tail and path results','india-risk-path-comparison-cases.csv.gz','Calibrated range, drawdown, move/touch tails, expansion and contraction.'),
    ]
    book=pd.DataFrame([{'comparison':a,'evidence':link(b),'coverage':c} for a,b,c in family])
    base=w[w.scope.eq('combined')&w.cutoff.eq('native_0910')]
    alt=w[w.scope.eq('combined')&w.cutoff.eq('preauction_0855')]
    show=pd.concat([pd.concat([f.nsmallest(3,'brier'),f.nsmallest(3,'crps')]).drop_duplicates('model')
                   for _,f in pd.concat([base,alt]).groupby(['horizon','cutoff'])],ignore_index=True)
    write_report(14,
        """
        The original 265 weekly and 217 monthly forecasts are retained on the exact same Indian calendar, with 173/92 and
        141/76 early/later outcomes and 53/11 disjoint windows. Forecasts with limited eligibility are scored both with their
        declared fallback on the original population and on their active dates against the parent replayed on those dates.
        Model coverage and realized opportunity coverage are both observable.

        Brier, log loss, CRPS, mean absolute and squared error, hit and balanced accuracy, rank correlation, reliability bins,
        interval calibration and forecast coverage accompany the return distributions. QLIKE scores variance ratios in the risk
        lane. Independence-aware intervals and episode omission are paired by forecast day. The refit and reselection experiment
        probes recent variant selection and the historical record remains exposed to V1–V22 research.
        """,
        '## Evidence index',table(book),
        '## Best in each retrospective clock and horizon',
        table(show,('horizon','cutoff','model','n','active','brier','crps','mae','rmse','accuracy','balanced_accuracy','rank_corr','coverage80','width80')),
        evidence('international-probability-calibration.csv','india-probability-calibration.csv','india-search-adjusted-intervals.csv.gz',
             'india-risk-matched-intervals.csv','representative-blocked-refit-summary.csv'))

    f=read('forward-ledger.json')
    receipts=read('forward-input-receipts.json')
    st=read('forward/staged-model-configurations.json')
    originals=f['original_issues']+f['inherited_v19']+f['inherited_v20']
    status=[]
    for o in originals:
        issued=o.get('issued',o.get('issue_timestamp',o.get('as_of')))
        target=o['target_sessions']
        ver=o['version']
        name=o.get('model',o.get('name',o.get('key')))
        state=o.get('status',o.get('maturity'))
        done=o.get('completed_target_dates',o.get('confirmed_sessions',[]))
        status.append(dict(version=ver,model=name,issued=issued,first_target=target[0],last_target=target[-1],observed=len(done),total=len(target),
                       status=state,realized_return=o.get('realized_return')))
    s=pd.DataFrame(st['rows'])
    latest=next(x for x in f['sessions'] if x['day']==st['prior_cash'])
    verified=sum(bool(x.get('verified')) for x in receipts['participant'])
    write_report(15,
        f"""
        As of {f['as_of'].replace('T',' ',1)}, {len(f['sessions'])} post-November 17 cash sessions are certified from the official NSE
        archive with the broker comparison or a preserved predecessor receipt. The latest certified NIFTY close is
        {latest['ohlc']['close']:,.2f} on {latest['day']}. Captured {receipts['n_eligible_international']} completed foreign marks
        from {receipts['n_foreign_markets']} markets and {verified} verified NSE participant OI/volume files. Source time and
        publication guards govern foreign eligibility. These captures live exclusively in the forward lane.

        The ledger carries {len(originals)} immutable issues from the applicable earlier versions. {sum(x.get('realized_return') is not None for x in originals)}
        has a realized endpoint. The November 26 V5 weekly target requires the full original official sequence after cash close,
        including reconciliation of the November 24 exchange holiday. Later inherited targets retain their recorded session schedules.
        The research panel has {len(s)} frozen configurations and historical rehearsal entries. V22 has {len(f['new_issues'])}
        new prospective forecasts at this capture.
        """,
        '## Issues retained and authoritative settlement',table(pd.DataFrame(status)),
        '## Frozen operational panel',table(s[['short','horizon','clock','status','next_cutoff']]),
        """
        The next chart opening snapshot is due at 08:55 IST on the earliest eligible cash day. The native directional snapshot
        follows at 09:10. Both were ahead of the capture. The opening model needs a freshly time-stamped GIFT quote or exact
        continuous bar. The native V14 return engine needs the genuine prior domestic and options state for the live date.
        The weekly overlays require the same V14 parent plus eligible corporate releases, prior reactions and already matured
        errors. The monthly overlays require the same native parent plus correctly aged participant series and the exact
        consecutive-session smoothing. Existing symmetric and risk issues provide prospective observations when they mature.

        Prior issue hashes, configuration hashes, historical source hashes, native clocks and exact target sessions are in the
        ledger. Historical rehearsals have their own designation. Reconciliation uses official values only after the original
        full sequence becomes available. A later native capture needs a verified December 2026 endpoint to qualify.
        """,
        evidence('forward-ledger.json','forward-input-receipts.json','forward/reconciliation-native.json',
            ('forward/staged-model-configurations.json','Staged models and immutable hashes'),
            ('forward/eligible-foreign-completed-sessions.csv.gz','Completed foreign observations after the freeze')))

    best5=base[base.horizon.eq(5)].nsmallest(1,'brier').iloc[0]
    best21=base[base.horizon.eq(21)].nsmallest(1,'crps').iloc[0]
    risk=csv('india-risk-and-tail-leaderboard.csv')
    v0=risk[risk.horizon.eq(21)&risk.model.eq('same_clock_GJR')&risk.scope.eq('combined')].range_crps.iloc[0]
    v1=risk[risk.horizon.eq(21)&risk.model.eq('analogue_global_on_IV_GJR')&risk.scope.eq('combined')].range_crps.iloc[0]
    w0=risk[risk.horizon.eq(5)&risk.model.eq('same_clock_IV')&risk.scope.eq('combined')].range_crps.iloc[0]
    w1=risk[risk.horizon.eq(5)&risk.model.eq('analogue_global_on_IV_GJR')&risk.scope.eq('combined')].range_crps.iloc[0]
    later=inter[inter.scope.eq('later')&inter.horizon.eq(21)&inter.model.eq('loro_transfer')&inter.reference.eq('local_persistence')]
    v2=later[later.metric.eq('rv_mae')].iloc[0]
    write_report(16,
        f"""
        V22 found a transferable risk relationship and a useful research candidate for the shape of monthly NIFTY paths.
        The later 21-session leave-region model lowered realized-volatility MAE versus trailing volatility by
        {v2.gain:.6f} on the market-balanced dates. The direction reference remains the neutral or protected direct law.
        Mixed-country paths mapped to Indian GJR volatility produced monthly range CRPS {v1:.6f} versus {v0:.6f} for
        the same 08:55 GJR path reference, a {1-v1/v0:.2%} reduction in average loss. Weekly range CRPS was {w1:.6f}
        versus {w0:.6f} for the 08:55 IV reference. Monthly GJR and the established weekly IV and offshore/domestic
        point volatility references retain their lead on their principal measures.

        The top weekly retrospective directional result was {best5.brier:.6f} Brier versus the protected V20
        0.221693, while the best new weekly CRPS improvement came from a domestic residual overlay. The monthly V21 parent
        scored 0.223819 Brier and 0.023184 CRPS. The twelve-percent foreign tail mixture scored {best21.brier:.6f}
        and {best21.crps:.6f}. Both directions and distribution gains are small against paired uncertainty. Monthly range
        has a larger measured gain, with a search-adjusted interval that includes zero. The volatility-matched India-only
        path already accounts for a meaningful share of the range difference.

        Direct foreign forecasts and standalone analogue return laws were generally weaker than the strongest protected direct
        NIFTY laws. Simple regularization, shared date effects, offshore information and domestic variables explain some
        apparent transfer gains. Foreign history adds comparable episodes and improves estimation of some risk relationships.
        The Indian evidence still consists of 53 weekly and 11 monthly nonoverlapping outcomes. Feed disagreements, exposure
        to prior model searches, and the availability of only a limited historical period are material constraints.

        Keep the previous forward anchors frozen. V22's monthly risk-path shape and tail mixture have reproducible laws and
        matched historical evidence. Their forward performance remains open while the panel is staged for authentic morning
        captures.
        """,
        evidence(('international-transfer-later.png','International directional and risk comparison'),
          ('nifty-range-analogue-comparison.png','Same-clock NIFTY range evidence'),
          (f'V22_{REPORTS[9]}.md','Risk evidence'),(f'V22_{REPORTS[10]}.md','Falsification'),(f'V22_{REPORTS[14]}.md','Forward ledger')))
    write_report(17,
        """
        ## One prospective monthly path comparison

        Preserve the 08:55 GJR reference, the volatility-scaled India history law and the fixed mixed foreign metric law. Generate
        complete weighted OHLC arrays from the contemporaneously captured inputs. Track monthly range CRPS and drawdown CRPS,
        expansion and contraction reliability, and the 80% interval width and coverage. Score shared targets in blocks. Use the
        historical absolute threshold and fixed scale transform recorded in V22.

        ## One small directional falsification

        Freeze the existing V20 weekly Brier parent, the V21 distribution parent, the India-plus-visible-GIFT residual correction,
        and the single predeclared foreign tail mixture for the monthly candidate. Keep only authentic snapshots and complete original
        2026 target windows. Compare gain from the external component with exactly the same domestic and offshore inputs. Once real
        observations accrue, compare chronology, deterioration or calibration by uncertainty regime.

        ## Verify market venue agreement before expanding auxiliary supervision

        Start with independently licensed daily closes, venue sessions and explicit release times for markets with the largest
        V22 source discrepancies. Refit the narrow volatility block with those usable markets and date weights. Evaluate the
        closest foreign analogue on the same origin and archive counts by country and crisis episode. Require sustained gain
        beyond ordinary shrinkage and discovery controls before considering larger architectures or additional directional features.

        ## Improve sparse breadth and uncertainty evaluation

        Use dated local equal-weight or advancer series only where a comparable published market definition exists. Compare against
        an unchanged OHLC transition control. Preserve simulations where country heterogeneity and regime reversals harmed transfer.
        Extend the actual evaluation only with newly observable nonoverlapping NIFTY windows within the authorized research scope.
        """,
        evidence((f'V22_{REPORTS[14]}.md','Next eligible verified cutoff'),(f'V22_{REPORTS[10]}.md','Registered falsification evidence'),
                'hypotheses-and-dispositions.csv'))


def figures(boards):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    bg='#fbfcfe';ink='#202938';muted='#58677b';teal='#18776d';amber='#c6743b'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':'none','axes.labelcolor':ink,
                        'xtick.color':muted,'ytick.color':ink,'text.color':ink,'figure.facecolor':bg,'axes.facecolor':bg})
    a=boards[boards.scope.eq('later')&boards.code.ne('india')&boards.horizon.isin(ORIGINAL)].groupby(['horizon','model'])[['brier','rv_mae']].mean()
    names=['Hold out country','Hold out region','Partial pooling','Date-block null']
    keys=['loco_transfer','loro_transfer','partial_country','date_block_null']
    fig,axes=plt.subplots(1,2,figsize=(11,4.6),layout='constrained',sharey=True)
    for ax,col,title in zip(axes,('brier','rv_mae'),('Direction Brier','Realized-volatility MAE')):
        for offset,h,colr in ((-.17,5,teal),(.17,21,amber)):
            q=a.loc[h,col]
            gain=100*(q['local_persistence']-q.reindex(keys))/q['local_persistence']
            ax.barh(np.arange(len(keys))+offset,gain,.31,color=colr,label=f'{h} sessions')
        ax.set_yticks(np.arange(len(keys)),labels=names)
        ax.axvline(0,color='#a6b3bd',lw=1.2)
        ax.grid(axis='x',color='#e4e9ee',lw=.8)
        ax.set_axisbelow(True)
        ax.set_xlabel('Loss reduction vs local persistence (%)')
        ax.set_title(title,loc='left',fontweight='bold',fontsize=12,pad=12)
    axes[0].invert_yaxis()
    axes[1].legend(frameon=False,loc='lower right',bbox_to_anchor=(1,-.27),ncol=2)
    fig.suptitle('International transfer on later market dates',x=.07,ha='left',fontsize=17,fontweight='bold')
    fig.savefig(OUT/'international-transfer-later.png',dpi=155,facecolor=bg)
    plt.close(fig)

    z=csv('india-risk-and-tail-leaderboard.csv')
    z=z[z.scope.eq('combined')].set_index(['horizon','model'])
    fig,axes=plt.subplots(1,2,figsize=(10.7,3.9),layout='constrained')
    for ax,h,anchor in zip(axes,ORIGINAL,('same_clock_IV','same_clock_GJR')):
        k=[anchor,'analogue_india_on_IV_GJR','analogue_global_on_IV_GJR']
        vals=z.loc[h,'range_crps'].loc[k].to_numpy()
        ax.barh(np.arange(3),1.e4*vals,color=['#7c8796',amber,teal],height=.48)
        ax.set_yticks(np.arange(3),labels=('08:55 protected path','Scaled India-only paths','Scaled mixed-country paths'))
        ax.invert_yaxis()
        ax.set_xlim(0,1.2*max(1.e4*vals))
        ax.bar_label(ax.containers[0],labels=[f'{v:.2f}' for v in vals*1.e4],padding=5)
        ax.grid(axis='x',color='#e4e9ee')
        ax.set_axisbelow(True)
        ax.set_xlabel('Range CRPS (basis points)')
        ax.set_title(f'{h} sessions',loc='left',fontweight='bold')
    fig.suptitle('NIFTY high–low range forecasts at 08:55 IST',x=.04,ha='left',fontsize=16,fontweight='bold')
    fig.savefig(OUT/'nifty-range-analogue-comparison.png',dpi=155,facecolor=bg)
    plt.close(fig)


def index():
    starts=[
        '# NIFTY V22 research',
        'International market learning, transferable predictive relationships and historical market analogues.',
        'Historical vintage January 1, 2025 through November 17, 2026. Original weekly and monthly NIFTY outcomes use five and 21 exchange sessions. The forward ledger has its own observation cutoff.',
        'The clearest result is the improvement in the monthly 08:55 high–low range distribution after scaling foreign empirical paths to India’s GJR volatility. Weekly range and standalone foreign direction failed to beat the strongest direct references. Paired uncertainty remains material.',
        '## The 17 reports',
    ]
    starts.append('\n'.join(f'{i+1}. [{title}](V22_{name}.md)' for i,(name,title) in enumerate(zip(REPORTS,TITLES))))
    starts+=['## Primary artifacts',
              '\n'.join('- '+link(f,label) for f,label in [('MISSION.md','Original research brief'),('README.md','Reproduction instructions'),
               ('india-return-leaderboard.csv','NIFTY return leaderboard'),('india-risk-and-tail-leaderboard.csv','NIFTY risk and tail leaderboard'),
               ('international-model-leaderboard.csv','International leaderboard'),('india-forecast-laws.npz','Coherent weighted NIFTY return laws'),
               ('forward-ledger.json','Machine-readable forward ledger'),('manifest.json','Artifact integrity manifest'),
               ('international-transfer-later.png','International transfer figure'),('nifty-range-analogue-comparison.png','Monthly and weekly range figure')])]
    earlier=[
        '- V1 · '+link(os.path.relpath(ROOT/'NIFTY_FORECAST_2026-11-17.md',OUT).replace(os.sep,'/'),'Original forecast experiment')+
        ' · '+link(os.path.relpath(ROOT/'NIFTY_LEARNED_WEIGHTS_2026-11-17.md',OUT).replace(os.sep,'/'),'Learned weights'),
        '- V2 · '+link(os.path.relpath(ROOT/'NIFTY_TWO_YEAR_2026-11-17.md',OUT).replace(os.sep,'/'),'Two-year experiment')+
        ' · '+link(os.path.relpath(ROOT/'NIFTY_WEEK_MONTH_2026-11-17.md',OUT).replace(os.sep,'/'),'Weekly and monthly research'),
    ]
    for n in range(3,22):
        name=f'NIFTY_V{n}_RESEARCH.md'
        root=ROOT/name
        if root.is_file():
            path=root
        else:
            candidates=sorted((ROOT/f'artifacts/nifty_forecast_v{n}').glob(f'*/*/{name}'))
            path=candidates[-1]
        earlier.append(f'- V{n} · '+link(os.path.relpath(path,OUT).replace(os.sep,'/'),f'V{n} research report'))
    starts+=['## Earlier versions','\n'.join(earlier)]
    (OUT/'NIFTY_V22_RESEARCH.md').write_text('\n\n'.join(starts)+'\n',encoding='utf-8')
    (OUT/'README.md').write_text(dedent(r"""
        # Reproduce V22

        Run from the trading-desk workspace with the established virtual environment. The run uses only artifact-verified 2025–2026
        observations and stores source snapshots under this V22 directory. By default, the scripts reuse retained daily vendor
        responses. Source acquisition requires network access and an existing read-only Upstox credential for broker checks.

        ```powershell
        $env:PYTHONDONTWRITEBYTECODE = '1'
        $env:OPENBLAS_NUM_THREADS = '1'
        $v22Python = '.\.venv\Scripts\python.exe'
        $env:NIFTY_V22_CALENDAR_DEPS = Join-Path $env:TEMP 'nifty-v22-calendar-deps'
        & $v22Python -m pip install --target $env:NIFTY_V22_CALENDAR_DEPS --no-deps exchange-calendars==4.13.3 pyluach korean-lunar-calendar toolz
        $v22Steps = @('common','sources','source_checks','reference','panel','learning','analogues','india','risk','power','evidence')
        foreach ($step in $v22Steps) {
            & $v22Python -W ignore::RuntimeWarning -m ("research.nifty_forecast_v22." + $step)
            if ($LASTEXITCODE -ne 0) { throw "Stopped in V22 module $step" }
        }
        & $v22Python -m research.nifty_forecast_v22.report
        & $v22Python -m research.nifty_forecast_v22.verify
        ```

        The archived forward receipts supply the ledger report during reproduction. To refresh the forward lane during an eligible
        2026 date, run `& $v22Python -m research.nifty_forecast_v22.forward` before regenerating reports and verification. It preserves
        the original issuances and captures newly available dated input receipts at the actual clock.

        Return-law arrays contain concatenated arithmetic-return atoms and weights. Zero-based offsets delimit each law. The
        matching case CSV provides the law ID, reference close, target end and exact cutoff. The analogue atlas links a case to
        weighted scenario locations, source maturity and the corresponding `p5` or `p21` OHLC array. International model
        archive columns describe an affine map of its stored normalized return support from the matched horizon file.

        [Report index](NIFTY_V22_RESEARCH.md)
        """).strip()+'\n',encoding='utf-8')


def run():
    boards=csv('international-model-leaderboard.csv')
    inter=csv('international-matched-date-intervals.csv.gz')
    w=csv('india-return-leaderboard.csv')
    stage_one(boards)
    transfer_and_analogues(boards,inter,w)
    india_and_risk(boards,inter,w)
    validation_and_registry(w,inter)
    remaining_reports(boards,w,inter)
    figures(boards)
    index()
    print('Wrote',len(REPORTS),'V22 reports and two figures.',flush=True)


if __name__=='__main__':
    run()
