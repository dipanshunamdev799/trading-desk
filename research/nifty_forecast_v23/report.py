"""Build the V23 reports and research index from the verified case tables."""
from textwrap import dedent

from .common import *

TITLES=('Reproduction and benchmarks','Master forecast archive','Forecast information geometry',
        'Distribution component intelligence','Robust forecast aggregation','Model uncertainty and disagreement',
        'Stable predictive relationships','Historical path shape research','International path complementarity',
        'Original horizon forecasting','Forecast calibration research','Simulation precision and numerical audit',
        'Cumulative search risk','Validation and falsification','Complete model comparison','Forward research ledger',
        'Final research conclusions','Next experiments')


def cell(x):
    if pd.isna(x):
        return '—'
    if isinstance(x,(float,np.floating)):
        return f'{x:.6f}'
    if isinstance(x,(int,np.integer)) and not isinstance(x,(bool,np.bool_)):
        return f'{x:,}'
    return str(x).replace('|','\\|')


def table(z, cols=None):
    if cols is not None:
        z=z[list(cols)]
    if z.empty:
        return '*The specified comparison has no eligible rows.*'
    names=[str(k).replace('_',' ') for k in z.columns]
    head=['| '+' | '.join(names)+' |','| '+' | '.join(['---']*len(names))+' |']
    return '\n'.join(head+['| '+' | '.join(cell(p) for p in r)+' |' for r in z.itertuples(index=False,name=None)])


def link(path,label=None):
    return f'[{path if label is None else label}]({path})'


def evidence(*r):
    return ' · '.join(link(v) if isinstance(v,str) else link(*v) for v in r)


def report(i,*contents):
    p=OUT/f'V23_{REPORTS[i-1]}.md'
    content='\n\n'.join(dedent(c).strip() for c in contents if c.strip())
    p.write_text(f'# V23 {TITLES[i-1]}\n\n{content}\n\n[Back to the research index](NIFTY_V23_RESEARCH.md)\n',encoding='utf-8')


def earlier(path):
    return os.path.relpath(path,OUT).replace(os.sep,'/')


def return_slice(z,clock,models,scope='combined'):
    return z[z.clock.eq(clock)&z.model.isin(models)&z.scope.eq(scope)]


def chapter_1_to_3():
    rec=read('predecessor-verification.json')
    q=csv('exact-v22-benchmark-scores.csv')
    report(1,
        f"""
        Replayed {rec['weighted_laws']:,} V22 law summaries from stored weights and recomputed {rec['complete_proper_score_replays']:,}
        original case scores in full. Independently checked the V22 research index, all 17 reports, the preregistration,
        verification receipt, {rec['files']:,} archived files and {rec['code_files']:,} source files against the frozen manifest.
        Weekly and monthly comparisons preserve their literal original target sessions and published information clocks.
        """,
        table(q,('horizon','clock','model','n','mean_up','brier','crps')),
        """
        The brief listed a weekly domestic-only Brier of 0.220368 and CRPS of 0.010121 together. The law records assign them to
        different models. The V20-parent domestic correction, `secondary_location_domestic_only`, scored 0.220368 Brier and
        0.010130 CRPS. The V21-parent domestic correction, `parent_location_domestic_only`, scored 0.222142 Brier and
        0.010121 CRPS. The V20-parent correction beyond GIFT scored 0.220133 Brier and 0.010180 CRPS. The archived monthly neutral
        law assigns exactly 50% up probability at 08:55 and scores 0.250000 Brier and 0.025543 CRPS.
        """,
        '## Protected path and source audit',table(csv('exact-v22-risk-reference.csv')),table(csv('reproduced-v22-source-exclusions.csv')),
        '## Protection against favorable subperiods and foreign-prior placebos',
        table(csv('reproduced-v22-episode-removals.csv')),
        table(csv('reproduced-v22-foreign-prior-placebos.csv'),('horizon','model','n','brier','crps')),
        'V11 exact-law ensemble benchmarks remain in their original archive clock. The 08:55, 09:10, prior-evening and post-open tracks remain separately identifiable.',
        evidence('exact-v22-benchmark-cases.csv.gz','predecessor-verification.json','v11-exact-ensemble-benchmarks.csv',
          (earlier(V22/'NIFTY_V22_RESEARCH.md'),'Original V22 research index')))

    s=read('master-archive-schema.json')
    p=csv('master-archive-coverage.csv')
    led=csv('master-prospective-inventory.csv')
    all_laws=csv('exact-return-law-field-source-map.csv')
    report(2,
        f"""
        Indexed {int(p.inventoried_files.sum()):,} source artifacts and {s['historical_records']:,} bounded forecast or
        outcome-score rows across the recoverable archive. The inventory identifies {s['discovered_distinct_version_model_ids']:,}
        version/model IDs and {s['linked_law_pointers']:,} rows with a law pointer. Many rows share origins, target definitions
        or upstream models. The exact law companion computes positive mass, arithmetic mean, variance and seven quantiles
        for {int(all_laws.n.sum()):,} supported laws directly from their stored atoms. Exported normalized laws additionally
        retain the case-specific scale and location recipe. The oldest V1–V2 records are indexed as provenance because their
        available research books may depend on pre-2025 warm-up data.

        Each normalized row preserves a source file, its zero-based source row, version and any model/configuration key. Explicit
        timestamps, target sessions, training bounds, per-origin losses, eligibility markers, feature information and atom
        pointers are kept when the original saved evidence supplies them. Missing fields remain missing. V13/V14 tables with
        a target type and original price anchor receive a separately identifiable session endpoint from the inherited target
        book. The data dictionary distinguishes the original recorded probability from sign mass computed from atoms.

        Chronological predictions retain a research-exposed selection label. Negative controls, exploratory model variants,
        frozen prospective issues, late diagnostics and unresolved maturities remain visible. Exact duplicate source files
        are aliased by SHA-256. Exact distribution copies on the matched panel are compared after sorting and consolidating
        atom weights. Near copies, forecast-level affine relationships and explicit parent labels are diagnostic evidence.
        """,
        table(p),
        '## Separate prospective inventory',
        table(led,('version','model','classification','horizon','target_last','status')),
        evidence('master-archive-schema.json','master-forecast-source-catalog.csv','master-model-family-registry.csv',
          'exact-return-law-fields.csv.gz','exact-return-law-field-source-map.csv','master-prospective-inventory.csv',
          'forecast-exact-case-duplicates.csv','matched-expert-family-map.csv'))

    g=csv('forecast-geometry-effective-rank.csv')
    pairs=csv('forecast-geometry-pairwise.csv.gz')
    r=pairs[pairs.clock.eq('native_0910')]
    episodes=pairs.groupby(['horizon','clock'],as_index=False).agg(
        pairs=('left','size'),near_law_pairs=('near_equal_laws','sum'),affine_probability_pairs=('approx_affine_p','sum'),
        mean_pairwise_return_error_corr=('error_corr','mean'),mean_crps_corr=('crps_loss_corr','mean'),
        mean_wasserstein=('mean_wasserstein_grid_approx','mean'),extreme_wasserstein=('extreme_wasserstein','mean'))
    a=r[(r.left_family.eq('corporate')|r.right_family.eq('corporate'))&(r.left_family.eq('domestic')|r.right_family.eq('domestic'))]
    b=r[(r.left_family.eq('positioning')|r.right_family.eq('positioning'))&(r.left_family.eq('offshore')|r.right_family.eq('offshore'))]
    alt=pd.concat([a,b]).groupby('horizon',as_index=False).agg(pairs=('left','size'),probability_correlation=('direction_corr','mean'),
             location_correlation=('mean_corr','mean'),return_error_correlation=('error_corr','mean'),crps_loss_correlation=('crps_loss_corr','mean'))
    m=csv('matched-expert-cases.csv.gz',usecols=['law','expert','horizon','clock','day'])
    direct_alias=csv('v10-archived-feature-alias-audit.csv')
    report(3,
        f"""
        Compared {len(m):,} exact case laws across {m.expert.nunique()} distinct archived experts. Probability, expected return,
        dispersion, asymmetry and positive/negative tail probabilities occupy different dimensions. The mean absolute distance
        over 129 quantile levels approximates the first Wasserstein distance. We report the same distances during the
        largest 10% of realized absolute outcomes. That episode definition is diagnostic and was unavailable at forecast time.

        The first eigenvalue and the participation ratio describe the historical correlation matrix. Shared realized outcomes
        contribute mechanically to highly correlated errors. The probability, location and tail matrices show how few
        distinct forecast directions remain after accounting for that limitation. Redundancy-aware forecast weights use
        only matured earlier quantiles. The full-sample geometry never drives historical fit weights.
        """,
        '## Native 09:10 dimensionality',
        table(g[g.clock.eq('native_0910')],('horizon','coordinate','dates','experts','first_share','effective_rank')),
        '## Pairwise relationships and differences in extreme episodes',table(episodes),
        'The weekly corporate versus domestic and monthly positioning versus offshore diagnostic compares the cross-family pairs available at the same native clock.',
        table(alt),
        'Exact-law hashes include atom locations and weights. Affine probability signatures do not prove that two experts share identical source features. '
        'The V10 and V11 controlled input aliases supply direct evidence where the feature provenance is known. In V10, adding three naive ridge copies moved probability by up to 0.061905, while the required canonical controls passed. The simulation audit separately measures variation from atom sampling.',
        table(direct_alias[(direct_alias.method.str.contains('canonical')&direct_alias.required_invariance)|
                           (direct_alias.method.eq('ridge')&direct_alias.variant.eq('three_copies'))],
              ('version','source','method','variant','tests','max_law_delta','max_probability_change','recognized_aliases')),
        evidence('forecast-geometry-effective-rank.csv','forecast-geometry-pairwise.csv.gz','forecast-exact-case-duplicates.csv',
          'range-geometry-pairwise.csv','matched-expert-family-map.csv','matched-expert-laws.npz',
          'v10-archived-feature-alias-audit.csv','v11-archived-affine-and-sentinel-audit.csv'))


def chapter_4_to_7(z):
    c=return_slice(z,'native_0910',['component_location_only','component_iv_gjr_scale_only','component_asymmetry_only','component_sign_only',
         'component_tail_only','component_historical_shape_only','component_coherent_joint','protected_distribution','protected_direction'])
    a=csv('domestic-shape-attribution-leaderboard.csv')
    at=a[a.horizon.eq(21)&a.clock.eq('native_0910')&a.scope.eq('combined')]
    decomp=csv('domestic-shape-brier-decomposition.csv')
    decomp=decomp[decomp.horizon.eq(21)&decomp.clock.eq('native_0910')]
    report(4,
        """
        A coherent law starts with the protected endpoint atoms. Location changes translate the atoms in log-price space.
        Dispersion changes are bounded scoreable stretches informed by the annualized IV or GJR reference at an eligible
        clock. The sign-only intervention changes probability weights within each side. A monotone skew transform preserves
        ordering. Tail-only transport borrows fixed tail mass from an earlier historical law. The combined construction uses
        consistent atoms or a valid complete-law mixture, yielding the mean, median, interval, sign and tails from one law.

        The cleanest result was the monthly domestic historical shape transformed to the original positioning parent's
        log median and interdecile spread. The weekly reference still benefited modestly from changing location.
        """,table(c,('horizon','model','n','brier','crps','coverage80','width80','tail_down_brier','tail_up_brier')),
        """
        ## Attribution of the monthly shape gain

        Reweighting the original parent to the domestic shape's positive mass reproduces the entire Brier improvement
        (the two arms have identical sign probabilities). With the original sign mass restored, the domestic shape has the
        parent's Brier by construction. The supplemental reweighting arm preserves shapes conditional on sign. It slightly
        changes unconditional quantiles as a mathematical consequence. Matching median and interdecile spread is enforced
        for the original shape substitution, with the finite support quantile convention stated in the code.
        """,
        table(at,('model','n','probability','brier','crps','coverage80','width80','log_location','log_scale','asymmetry')),
        'A retrospective algebraic decomposition separates the contribution of the average probability shift from the additional date-varying effect. Against V21, the uniform shift contributes about 0.007592 of the 0.013323 Brier improvement and date-specific changes contribute 0.005731. This decomposition uses realized outcomes for attribution. It does not fit a historical forecasting rule.',
        table(decomp),
        evidence('domestic-shape-attribution-cases.csv.gz','domestic-shape-attribution-intervals.csv','v23-return-laws.npz',
          'original-horizon-matched-comparisons.csv.gz','domestic-shape-brier-decomposition.csv'))

    models=('protected_direction','protected_distribution','equal_models','equal_families','quantile_family_pool','agg_redundancy',
         'agg_loss_mean','agg_loss_robust','agg_minimax_env','agg_bayesian','fixed_20pct_history','fixed_20pct_neutral',
         'uncertainty_guarded_mixture','randomized_fixed_weights','history_only')
    report(5,
        """
        The candidate panel compares distinct historical, domestic, positioning, corporate, risk, breadth, offshore and
        transferred mechanisms with the original same-clock leaders. Cases weight whole probability laws. Equal-family
        weighting fixes total mass across groups and divides it among their deduplicated members. Redundancy-aware weights
        use earlier quantile distances. The robust rule clips mature paired loss excursions. The worst-environment rule
        scores both earlier volatility groups only when each has 18 usable observations. Bayesian weights average a bounded
        Dirichlet pseudo-posterior driven by date-block loss draws. Quantile pooling averages ordered quantiles into a valid
        marginal law. Joint path dependence is scored separately on full OHLC laws.

        Every adaptive fit uses at most 120 earlier complete labels with a minimum of 36. An identical expert over the fit
        history and current support is one vote. Fixed zero-weight, neutral shrinkage, historical shrinkage, equal-weight
        and randomized expert controls all face the same origins. Most pooled laws diluted the strongest native signal.
        The exact V11 ensemble archive supplies an earlier-clock context. Previous 17:00 V17 structural pooling is directly scored on that clock.
        """,
        table(return_slice(z,'native_0910',models),('horizon','model','n','active','brier','crps','log_loss','coverage80','width80')),
        '## Earlier-clock controls and previous ensembles',
        table(return_slice(z,'previous_1700',models[:6]),('horizon','model','n','brier','crps')),
        evidence('ensemble-date-weights.csv.gz','original-horizon-search-adjusted-intervals.csv.gz',
           'v11-exact-ensemble-benchmarks.csv','leakage-and-duplication-checks.json'))
    u=csv('model-uncertainty-cases.csv.gz')
    a=u.groupby(['horizon','clock'],as_index=False).agg(n=('day','size'),families=('family_count','median'),
         typical_within=('within_expert_outcome_var','median'),typical_between=('between_expert_mean_var','median'),
         typical_parameter_se=('probability_parameter_se','median'),mean_family_disagreement=('family_prob_spread','mean'),
         mean_plain_disagreement=('ordinary_prob_spread','mean'))
    b=csv('disagreement-risk-matched-intervals.csv')
    b=b[b.clock.eq('native_0910')&b.model.isin(('model_disagreement','delayed_disagreement'))]
    p=csv('parameter-and-source-uncertainty-summary.csv')
    pp=csv('parameter-uncertainty-warning-intervals.csv')
    report(6,
        """
        The predictive return law measures uncertainty about prices. The total variance of an expert pool is the average
        within-expert outcome variance plus the between-expert variance of conditional means. The weight-model probability
        band measures instability in estimated sign probability across block and weight draws. Its bounds are a conditional
        sensitivity calculation, with no claim to cover full model-specification or source-measurement uncertainty.

        The diagnostic forecast asks whether genuinely different families improve warning of larger future absolute errors,
        range, expansion, adverse tail events and poor probability or distribution scores. The mature-only benchmark
        includes previous volatility, IV, ordinary probability dispersion, estimated parameter instability, the current
        directional probability and feature-distribution distance. The challenger adds family disagreement and training
        period sensitivity. A five-session delayed disagreement variant tests timeliness.
        """,
        table(a),table(b,('horizon','measure','model','n','gain','adjusted_low','adjusted_high')),
        '## Re-estimated coefficients and source perturbations',
        'A separate 64-draw block refit varies the historical regression coefficients. Changing the active memory from 120 to 60 cases and perturbing observed standardized inputs by 0.20 units measure two further sensitivities. The source perturbation is a scenario and preserves the missing-data mask. The return standard deviation and interval width still come from the complete market law.',
        table(p),table(pp,('horizon','clock','model','n','gain','adjusted_low','adjusted_high')),
        'Directional overconfidence and tail misses are evaluated as separate target or calibration outcomes. The adjusted paired evidence does not support disagreement as a dependable volatility-expansion warning at the native clock.',
        evidence('model-uncertainty-cases.csv.gz','disagreement-future-risk-cases.csv.gz','disagreement-future-risk-leaderboard.csv',
          'conditional-calibration.csv.gz','training-period-stability-receipts.csv.gz','simulation-precision-summary.csv',
          'parameter-and-source-uncertainty-cases.csv.gz'))

    sets=['protected_direction','protected_distribution','residual_ordinary_ridge','residual_huber','residual_environment_balanced',
          'residual_hierarchical','residual_worst_environment','residual_delayed_5','residual_block_permuted']
    ss=pd.concat([return_slice(z,'native_0910',sets,s) for s in ('early','later','combined')])
    f=csv('return-residual-coefficient-history.csv.gz')
    co=f[f.clock.eq('native_0910')&f.model.isin(sets)].groupby(['horizon','model'],as_index=False).agg(
      fit_cases=('day','size'),weekly_term=('prior_ret5','median'),vol_term=('trailing_vol','median'),
      position_term=('FII_index_futures_d21','median'),earnings_term=('reaction_mean','median'),
      position_iqr=('FII_index_futures_d21',lambda v:v.quantile(.75)-v.quantile(.25)))
    report(7,
        """
        On exactly the same training origins, the ordinary ridge competes with Huber regression, volatility and positioning
        environment weights, hierarchical shrinkage toward the earlier half, and an incrementally upweighted worst past
        group. Smaller environments receive a regularized fallback. Training transformations and group thresholds use only
        complete earlier cases. Volatility, participation, trend, positioning concentration, corporate activity and the
        global environment also enter the conditional evaluation as origin-observable states.

        V21's monthly aggregate positioning correction gained 0.019699 Brier on the earlier 141 origins against V20 smooth5
        and lost 0.022891 on the later 76. The new robustness arms retain earlier/later rows. Ranking their worst cohort is
        a separate criterion from optimizing a single average. The delayed and block-permuted controls can retain apparent
        skill when too much of the input is shared or when repeatedly assessed periods favor a residual tilt.
        """,
        table(csv('protected-v21-cohort-flip.csv')),table(ss,('horizon','scope','model','n','active','brier','crps','coverage80')),
        table(co),
        evidence('return-residual-coefficient-history.csv.gz','training-period-stability-receipts.csv.gz','conditional-calibration.csv.gz',
          'leave-episodes-out.csv.gz','forecast-pareto-frontier.csv'))


def chapter_8_to_12(z):
    all_risk=csv('path-risk-leaderboard.csv')
    all_risk=all_risk[all_risk.scope.eq('combined')]
    riskcols=('horizon','model','n','rv_mae','range_crps','range_covered','drawdown_crps','expansion_brier',
              'contraction_brier','persistent_direction_brier')
    high=csv('larger-simulation-path-summary.csv')
    compact=high.groupby(['horizon','model','n_draws'],as_index=False).agg(n=('n','max'),range_crps=('range_crps','mean'),
        seed_min_range_crps=('range_crps','min'),seed_max_range_crps=('range_crps','max'),drawdown_crps=('drawdown_crps','mean'),
        expansion_brier=('expansion_brier','mean'),range_coverage=('range_coverage','mean'))
    matches=csv('larger-simulation-path-matched-intervals.csv')
    matches=matches[matches.horizon.eq(21)&matches.metric.eq('range_crps')]
    structure=('same_clock_GJR','same_clock_IV','analogue_india_on_IV_GJR','constant_vol_diffusion','student_t_gjr_same_anchor',
               'india_independent_days','india_state_matched','india_random_same_episodes','india_vol_same_episodes',
               'india_temporally_shuffled','mixed_temporally_shuffled','india_gap_removed','india_no_intraday_excursions',
               'india_constant_scenario_risk','india_realized_donor_norm','india_state_widened')
    report(8,
        """
        The 08:55 experiments preserve each original return window and realized OHLC outcome, and reuse the day's protected
        point volatility forecast for the candidate laws. Weekly candidates scale to the offshore-plus-domestic point reference.
        Monthly candidates scale to the GJR point reference. A common multiplier maps the mean simulated realized volatility
        to the anchor. Each path still has its own sequence of returns, gaps and ranges.

        The structure trials compare the original joint paths, constant-volatility bridges, Student-t GJR paths, contiguous
        domestic analogues, random windows, volatility matches, shuffled intact daily candles and independent daily candles.
        Gap removal keeps close-to-close returns and reassigns the opening move within the session. Removing excursions
        clips the observed high and low to the open and close. A separate law forces every entire scenario to have the same
        realized volatility, and an ablation removes donor volatility variation before re-anchoring. One preset law is 12%
        wider. Donor volatility and realized returns enter only after the complete donor path matures.
        """,
        table(all_risk[all_risk.model.isin(structure)],riskcols),
        """
        Monthly independent days and diffusion are competitive range baselines. In the original 192-draw experiment,
        independent days scored 0.013644 and the constant-volatility diffusion 0.013819 against 0.014230 for state-matched
        domestic windows. The independent-day law's drawdown score differs from the contiguous band's drawdown score.
        Deleting intraday excursions raises the monthly domestic range CRPS from 0.014230 to 0.014815. Constraining every
        path to the same realized variance worsens monthly expansion Brier from 0.198725 to 0.258065. Shuffling sessions
        alters temporal path risk even when the terminal and volatility outcomes largely survive the shuffle.
        """,
        '## Independent high-draw confirmation',
        'The same three generative baselines were regenerated with two separate seeds at 1,024 and 4,096 scenarios across every original origin. Each seed shares shock prefixes across budgets and common shocks between diffusion and Student-t GJR.',
        table(compact),
        'The 4,096-draw test averages the two seeds per date before calculating paired loss intervals. The resulting intervals retain date dependence and do not count multiple draws as extra forecast outcomes.',
        table(matches,('reference','model','block','n','gain','adjusted_low','adjusted_high')),
        evidence('v23-path-cases.csv.gz','path-risk-matched-intervals.csv.gz','path-law-recipes.csv.gz','path-donor-members.csv.gz',
          'larger-simulation-path-cases.csv.gz','larger-simulation-path-matched-intervals.csv'))

    foreign=('india_state_matched','mixed_broad','mixed_strict','mixed_omit_asia','mixed_omit_disputed','mixed_strict_omit_asia',
             'mixed_random_foreign','mixed_vol_only','foreign_only_same_episodes','foreign_only_unmatched_episodes',
             'analogue_india_on_IV_GJR','analogue_global_on_IV_GJR')
    u=csv('foreign-source-agreement.csv')
    f=csv('path-donor-members.csv.gz',usecols=['horizon','day','model','market','source_row','episode','verified_source'])
    verified=f[f.market.ne('india')&f.model.isin(('mixed_strict','mixed_strict_omit_asia'))]
    v=verified.groupby(['horizon','model','market'],as_index=False).agg(donors=('source_row','size'),distinct_paths=('source_row','nunique'),weeks=('episode','nunique'))
    inter=csv('path-risk-matched-intervals.csv.gz')
    m=inter[inter.horizon.eq(21)&inter.reference.eq('india_state_matched')&inter.scope.eq('combined')&
       inter.model.isin(('mixed_broad','mixed_strict','mixed_omit_disputed','mixed_random_foreign'))&inter.metric.isin(
           ('range_crps','drawdown_crps','expansion_brier','upper_range_tail_brier','persistent_direction_brier'))]
    report(9,
        """
        V22's 0.015488 GJR range CRPS fell to 0.014409 from scaled India-only paths and 0.014195 from mixed paths.
        V23 fixes the comparison more tightly. Each Indian origin selects 24 distinct earlier global weeks with one domestic
        window per week. The mixed candidate replaces up to six windows inside those same weeks. Both laws have equal weight
        per episode and the same volatility anchor. The strict arm admits foreign donors only when every daily OHLC bar
        and the opening cash reference agree within 10 basis points across the two vendors. The pure-foreign sensitivity is
        separated when it cannot fill the same 24 weeks. Random foreign paths, volatility-only matches and region exclusions
        use the same construction.

        The independently extracted Upstox histories cover the same bounded interval as Yahoo. Nonlocal dates, suspect
        offsets, stale or missing bars, variant and currency distinctions and the DAX total-return control remain in the
        source audit. FRED close requests timed out and a close-only feed would not verify high/low excursions. Same-day
        broker agreement qualified 355 full five-session and 146 full 21-session donor windows before the Indian issue-time
        test. Source verification is a retrospective provenance audit, with each admitted outcome additionally constrained
        by its historical maturity date.
        [Upstox daily candles and timestamp definition](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) · [FRED S&P 500](https://fred.stlouisfed.org/series/SP500) · [FRED Nikkei 225](https://fred.stlouisfed.org/series/NIKKEI225)
        """,table(u,('code','paired','only_broker','only_primary','within_006','strict_dates','median_close_bps','return_corr')),
        '## Equal-episode results and foreign donor mix',
        table(all_risk[all_risk.model.isin(foreign)],('horizon','model','n','foreign_paths','range_crps','drawdown_crps','upper_range_tail_brier','expansion_brier','persistent_direction_brier')),
        table(v),table(m,('model','metric','n','gain','adjusted_low','adjusted_high')),
        'On the monthly target, the broad mixed library improved range CRPS by about 0.000013 over equal-size India history. '
        'The strict mixed library lost about 0.000306. Expansion and persistence have different rankings, and the paired uncertainty remains wide. '
        'Verified foreign paths can expand the scenario collection even when their inclusion fails the score comparison.',
        evidence('foreign-source-receipts.json','foreign-session-offsets.csv','foreign-full-ohlc-pairs.csv.gz','path-risk-matched-intervals.csv.gz',
          'path-donor-members.csv.gz','path-risk-cohort-deltas.csv.gz'))

    ch=('protected_direction','protected_distribution','component_historical_shape_only','component_coherent_joint',
        'residual_worst_environment','residual_ordinary_ridge','residual_delayed_5','component_location_only','agg_loss_robust',
        'fixed_20pct_neutral','fixed_20pct_history','uncertainty_guarded_mixture','complementary_residual_component')
    a=pd.concat([return_slice(z,'native_0910',ch,k) for k in ('combined','early','later')])
    intervals=csv('original-horizon-search-adjusted-intervals.csv.gz')
    check=intervals[intervals.clock.eq('native_0910')&intervals.model.isin(('component_historical_shape_only','residual_worst_environment',
              'component_location_only'))&intervals.metric.isin(('brier','crps'))&intervals.scope.eq('combined')]
    report(10,
        """
        Every law predicts next-five-session or next-21-session NIFTY cash-close return from the original prior close. The original
        173/92 and 141/76 splits are reproduced at the native and pre-auction clocks. The previous evening study separately
        omits the few origins for which the cash reference was not yet available under the declared guard. Original clocks remain
        distinct in all leaderboards. A candidate's sign, mean, median, expected index, quantiles and tail probabilities are
        computed directly from the same weights.

        The 09:10 weekly worst-environment residual scored 0.218097 Brier versus 0.220133 for V22's protected direction
        leader. The corporate location-only experiment scored 0.010090 CRPS versus 0.010121 for the protected distribution.
        The 09:10 monthly shape substitution reduced Brier to 0.210496 from 0.223431, improved Brier in both original cohorts,
        and reached 0.022911 CRPS against 0.023174. In the later monthly cohort its CRPS rose slightly against that reference.
        The main Brier improvement comes from the new shape's implied sign mass. Full and matched active rows account for
        train-only warm-up fallbacks in the residual and calibration models.
        """,table(a,('horizon','scope','model','n','active','disjoint','brier','crps','log_loss','coverage80')),
        table(check,('horizon','parent','model','metric','block','n','gain','adjusted_low','adjusted_high')),
        evidence('v23-return-cases.csv.gz','v23-return-laws.npz','original-horizon-matched-comparisons.csv.gz',
           'forecast-pareto-frontier.csv','domestic-shape-attribution-leaderboard.csv'))

    k=csv('forecast-calibration-leaderboard.csv')
    k=k[k.clock.eq('native_0910')&k.model.isin(('protected_direction','protected_distribution','component_historical_shape_only',
          'fixed_neutral_sign','fixed_20pct_neutral','calibration_sign_fit','calibration_pit_fit','agg_bayesian'))]
    f=csv('conditional-calibration.csv.gz')
    f=f[f.clock.eq('native_0910')&f.model.isin(('protected_direction','component_historical_shape_only'))&
            f.condition.isin(('family_prob_spread','observed_trailing_vol','positioning_concentration','analogue_effective_n','original cohort'))]
    report(11,
        """
        Sign probabilities are binned in deciles. The tables report observed rate, log loss, Brier reliability, resolution and
        uncertainty. A within-bin remainder captures finite binning effects. The reported diagnostic calibration intercept and slope
        summarize the scored cohort. The recalibrated laws themselves estimate a regularized sign map using earlier mature errors
        and blend it with the original probability. The PIT warp uses only earlier realized randomized ranks and a monotone
        quantile map. Fixed neutral shrinkage and both exact parents provide comparators.

        The support-level randomized PIT uses the interval between strict and inclusive CDF at outcomes. Proper 80% interval
        scores penalize coverage failures, and lower- and upper-tail misses remain separate. Conditional bins use prior rolling
        medians of known volatility, forecast disagreement, positioning, analogue counts, participation and related states.
        Each cell shows its sample size. Sparse conditional rows have correspondingly limited precision.
        """,
        table(k,('horizon','model','n','brier','reliability','resolution','uncertainty','within_bin_remainder',
           'diagnostic_calibration_intercept','diagnostic_calibration_slope','log_loss','coverage80','width80','interval80','tail_down','tail_up')),
        table(f,('horizon','model','condition','group','n','observed','probability','brier','coverage','width','tail_down','tail_up')),
        evidence('calibration-reliability.png','probability-reliability-bins.csv.gz','randomized-pit-histogram.csv.gz',
            'conditional-calibration.csv.gz','forecast-calibration-leaderboard.csv'))

    p=csv('simulation-precision-summary.csv')
    sc=p[p.measure.isin(('probability','high_touch_probability','crps'))]
    n=csv('simulation-paired-gain-noise.csv')
    report(12,
        """
        Eight independent seeds and four scenario counts estimate numerical sampling error against exact finite weighted
        probability laws. Twelve origins per horizon were spread across the original evaluation calendar, for 24 NIFTY
        return dates and 24 joint path dates. Within each seed the models use common random uniforms and nested 256, 1,024,
        4,096 and 16,384 prefixes. A high-side touch is sampled on the same joint path supports as the range. The volume of
        simulations does not create additional realized market outcomes.

        Exact scoring is used wherever the finite empirical law is already saved. Forecast probability noise at 256 draws
        is several percentage points for many individual cases and falls as the count increases. The paired study measures
        how much the finite draw can change the direction or size of an apparent gain. Higher-budget generative robustness
        covers the main three synthetic or independent-day path baselines separately. Statistical and specification uncertainty
        remain after we remove numerical resampling uncertainty.
        """,
        table(sc,('horizon','track','n','measure','trials','mae','p90_abs','rmse','bias')),
        table(n,('horizon','track','n','measure','replicates','exact_gain','gain_error_mae','sign_inversion_rate')),
        evidence('simulation-precision-cases.csv.gz','simulation-paired-gain-noise.csv','simulation-precision-design.json',
          'precision-joint-paths.npz','larger-simulation-path-summary.csv'))


def chapter_13_to_15(z):
    k=read('cumulative-search-coverage.json')
    p=csv('cumulative-version-coverage.csv')
    s=csv('bounded-refit-reselection-summary.csv')
    ep=csv('cumulative-historical-episode-exposure.csv.gz')
    ep=ep.groupby('month',as_index=False).agg(sources=('source','nunique'),mentions=('mentions','sum')).nlargest(12,'mentions')
    report(13,
        f"""
        The recovered registry covers all {k['versions']} historical versions at the document or source-inventory level.
        It identifies {k['observed_version_model_ids']:,} source-version model IDs, of which {k['ids_with_a_law_pointer']:,}
        or {k['share_of_observed_ids_with_case_law_pointer']:.1%} have at least one recognized case-law pointer. It also
        records {k['registered_records_discovered']:,} recoverable registry entries from {k['registry_bearing_versions']}
        versions and {k['indexed_leader_rows']:,} reported leader rows with visible model and score fields. The denominator of
        actual trials through V22 is unknown. Duplicate mechanisms, adaptive branches, incompletely archived variants and
        repeated episode inspections all contribute to search exposure.

        Four chronological residual blocks and four mixture checks form the representative observed selection family.
        The blocked-residual and persistent-random-feature exercises refit and reselect eight candidates on each of 39
        replicate paths. A separate random mixture family uses authentic earlier experts and a fixed 28% pool weight.
        Each named forecast variant is compared against the archived native directional parent on matching active dates.
        The proportion of positive null winners estimates how often a bounded observed setup can reward noise.
        """,table(p,('version','files_in_catalog','registry_files','records_in_registry','unique_version_model_ids','known_law_ids','date_case_rows')),
        table(s),table(ep),
        'The representative selection experiment tests these specific residual and pooling mechanisms. It does not adjust the historical domestic-shape discovery for every prior research decision.',
        evidence('cumulative-recovered-registrations.csv.gz','cumulative-reported-leaders.csv.gz','cumulative-historical-episode-exposure.csv.gz',
                 'bounded-refit-reselection-cases.csv.gz','bounded-refit-reselection-method.json'))

    r=read('registration.json')
    x=csv('original-horizon-search-adjusted-intervals.csv.gz')
    h=x[x.clock.eq('native_0910')&x.scope.eq('combined')&x.model.isin(('component_historical_shape_only','residual_worst_environment',
              'agg_loss_robust','equal_families'))&x.metric.isin(('brier','crps'))]
    o=csv('leave-episodes-out.csv.gz')
    o=o[o.clock.eq('native_0910')&o.model.isin(('component_historical_shape_only','residual_worst_environment','equal_families'))&
            o.omission_type.ne('month')]
    dated=csv('disjoint-phase-comparisons.csv.gz')
    p=dated[dated.clock.eq('native_0910')&dated.model.eq('component_historical_shape_only')].groupby(['horizon','metric'],as_index=False).agg(
           phases=('phase','size'),positive_phases=('gain',lambda v:v.gt(0).sum()),min_gain=('gain','min'),max_gain=('gain','max'))
    report(14,
        f"""
        Registered {len(r['hypotheses'])} materially distinct hypotheses at {r['registered_at']} before the V23 tests.
        Each specifies a mechanism, target, clock, parent, primary loss, negative control and budget. The data receipts
        enforce strict label maturity. Source measurements, transformations, aggregation weights and residual fits enter
        each historical replay at its decision cutoff. Equivalent laws and columns are checked for copy invariance.
        The source clock poison and the archived case certifications are separate tests.

        Negative controls include exact copies, near-duplicate downweighting, fixed random mixtures, a delayed residual,
        blocked error permutations, conservative historical and neutral mixtures, and same-episode foreign swaps. Bootstrap
        intervals pair dates and use circular blocks of 21 and 42 Indian origins. The simultaneous family limit uses the
        maximum standardized deviation across the tested candidates. Individual disjoint phases, each omitted month and
        omission of the largest realized or most favorable 21-origin episode quantify dependence on particular stretches.
        """,
        table(h,('horizon','parent','metric','model','block','n','gain','low','high','adjusted_low','adjusted_high')),
        table(o,('horizon','model','metric','omission_type','omitted','n','gain_remaining')),
        table(p),
        'The monthly domestic substitution has positive family-adjusted bounds on the direction benchmark in this V23 search family. '
        'The broader comparison against the V21 distribution parent still spans zero. The 11 monthly disjoint outcomes and cumulative '
        'historical selection remain the relevant limits on an independent claim.',
        evidence('registration.json','leakage-and-duplication-checks.json','original-horizon-search-adjusted-intervals.csv.gz',
          'leave-episodes-out.csv.gz','disjoint-phase-comparisons.csv.gz','bounded-refit-reselection-summary.csv'))
    entries=[
        ('Weekly and monthly direction and distribution','original-horizon-leaderboard.csv','Complete metrics by horizon, information clock and original cohort.'),
        ('Same-date parents and active coverage','original-horizon-matched-comparisons.csv.gz','Original outcome matching, active subset and cohort differences.'),
        ('Robust pooling and component evidence','ensemble-date-weights.csv.gz','Earlier fit registry, cases used and per-expert weights.'),
        ('Volatility, expansion, range, drawdown and tails','path-risk-leaderboard.csv','Risk forecasts and protected point/path results.'),
        ('Point-volatility and expansion references','protected-volatility-and-expansion-leaderboard.csv','Legacy point MAE, QLIKE and expansion Brier.'),
        ('Conditional return calibration','conditional-calibration.csv.gz','Full condition with explicit bin coverage and origin counts.'),
        ('Model quality and complexity frontier','forecast-pareto-frontier.csv','Avoid forcing one score or common winner across targets.'),
        ('Dependence-aware uncertainty','original-horizon-search-adjusted-intervals.csv.gz','21/42-day block inference and search-family adjustment.'),
    ]
    a=z[z.scope.eq('combined')]
    top=pd.concat([pd.concat([q.nsmallest(3,'brier'),q.nsmallest(3,'crps')]).drop_duplicates('model')
                   for _,q in a.groupby(['horizon','clock'])],ignore_index=True)
    q=csv('forecast-pareto-frontier.csv')
    q=q[q.on_pareto_frontier&q.clock.eq('native_0910')]
    report(15,
        """
        The original weekly 173/92 and monthly 141/76 cohorts contain 265 and 217 outcomes, with 53 and 11 nonoverlapping
        origins. Inference preserves that calendar. Forecast coverage and the fully active subset are reported separately.
        Each active candidate is measured against a fresh selection of the protected parent's exact same cases.

        The full leaderboards include Brier, log loss, CRPS, accuracy, balanced accuracy, MAE, RMSE, rank correlation,
        variance QLIKE, calibration and tail scores. The Pareto frontier compares Brier, CRPS, absolute 80% coverage error,
        worst-cohort CRPS and an ordinal construction cost. That cost groups fixed controls, fitted calibration, estimated
        weights and multi-component laws. It is a reproducibility aid rather than a monetary or timing cost.
        """,table(pd.DataFrame([(a,link(b),c) for a,b,c in entries],columns=['comparison','file','content'])),
        table(top,('horizon','clock','model','n','disjoint','episodes','brier','crps','log_loss','accuracy','balanced_accuracy','mae','rmse','rank_corr','coverage80','width80')),
        table(q,('horizon','model','brier','crps','coverage_error','worst_cohort_crps','complexity')),
        evidence('path-risk-matched-intervals.csv.gz','path-risk-cohort-deltas.csv.gz','probability-reliability-bins.csv.gz',
          'forecast-calibration-leaderboard.csv','domestic-shape-attribution-leaderboard.csv'))


def forward_report():
    p=read('forward-ledger.json')
    stage=read('forward/staged-configurations.json')
    source=read('forward/pre-cutoff-staging.json')
    watched=read('forward/cutoff-run.json') if (OUT/'forward/cutoff-run.json').exists() else None
    native=read('forward/native-clock-status.json') if (OUT/'forward/native-clock-status.json').exists() else None
    f=[]
    for key in ('original_issues','inherited_v19','inherited_v20'):
        for x in p[key]:
            f.append(dict(version=x['version'],model=x.get('model',x.get('name',x.get('key'))),
                 reference=x['reference_close'],issued=x.get('issued_at',x.get('issued')),first=x['target_sessions'][0],
                 last=x['target_sessions'][-1],outcome=x.get('realized_return'),status=x.get('maturity',x.get('status'))))
    latest=p['sessions'][-1]
    rows=[]
    for x in p['new_issues']:
        rows.append(dict(model=x['model'],clock=x['decision_cutoff'],actual_issue=x['issued_at'],sessions=len(x['target_sessions']),
            end=x['target_sessions'][-1],p_up=x['p_up'],expected_return=x['expected_return'],expected_range=x.get('forecast_range'),
            annualized_volatility=x.get('annualized_rv'),p_expansion=x.get('p_expansion'),
            law=link(x['law_file'],'Weighted law')))
    statuses=pd.DataFrame(stage['configurations'])
    checks=pd.DataFrame(native['rows']) if native else pd.DataFrame()
    source_probe=csv('forward/native-source-readiness.csv')
    taken=watched['status'] if watched else 'opening cutoff watch staged'
    outcome_text='## Genuine V23-time issuances' if rows else '## Prospective issue status'
    detail=table(pd.DataFrame(rows)) if rows else 'The ledger contains no new issue as of its recorded cutoff check.'
    report(16,
        f"""
        At the {p['checked_at']} check, the ledger retains {len(f)} inherited forecasts and {sum(x['outcome'] is not None for x in f)} resolved endpoint.
        The latest certified NIFTY close is {latest['ohlc']['close']:,.2f} from {latest['day']}. There are
        {len(p['sessions'])} certified post-freeze cash sessions, with {source['available_foreign_rows']} completed foreign
        marks and {source['prior_gift_rows']} earlier GIFT bars captured in the separate forward lane. Authenticity is
        based on the cutoff, received source snapshot, exact target sequence, fixed configuration and original weighted law.
        All newly issued horizons have a 2026 endpoint. Same-date 2026 NSE closure handling uses the official cash calendar.
        [NSE capital-market holiday circular](https://archives.nseindia.com/content/circulars/CMTR71775.pdf) · [Upstox intraday candle specification](https://upstox.com/developer/api-documentation/v3/get-intra-day-candle-data/)
        """,
        f'Opening cutoff check status is **{taken}**. The prescribed 08:55 information cutoff and actual issuance timestamp are distinct fields.',
        outcome_text,detail,
        """
        The live analogue paths retain the V22 domestic and mixed retrieval rules and use the already frozen prospective V19
        GJR law for scale. The originally researched historical risk point in V22 remains a separate comparator. Native directional
        variants depend on the exact fresh V14 return parent. That parent requires the V12 phase/market or neutral distribution,
        dated options inputs, and V14 local volatility state. V18, V20, V21 and V22 corrections further require their own exact
        corporate, equity reaction or positioning information. Frozen V19/V20 neutral and risk references already cover the
        new weekly and monthly target calendar.

        The additional forward V14 GJR risk reference replays the original November cached fit and extends its variance
        filter with certified new cash returns. The historical November variance curves reproduced in the state certificate.
        A frozen Student-t close-path law supplies realized-volatility uncertainty and expansion probabilities. This is a
        close-risk continuation and carries its own exact numerical and source receipts.
        """,
        '## Immutable inherited issues',table(pd.DataFrame(f)),
        '## Staged and native-clock checks',table(statuses,('name','horizon','clock','status')),
        'The upstream NSE derivatives archives were fetched and filtered by session, NIFTY instrument and 2026 expiry. Matched near-ATM strike pairs support input readiness. The exact forward-ready V12/V13/V14 model states and overlay recipes remain separate requirements.',
        table(source_probe,('day','status','rows','options','near_atm_matched_expiries')),
        table(checks,('model','horizon','earliest','status')) if len(checks) else 'The native decision checkpoint is staged.',
        evidence('forward-ledger.json','forward/staged-configurations.json','forward/authoritative-reconciliation.json','forward/foreign-receipt.json',
            'forward/pre-cutoff-staging.json','forward/preflight.json','forward/native-source-readiness.json',
            'forward/v14-gjr-state-receipt.json','v14-gjr-conditional-volatility-scores.csv',
            *[p for p in ('forward/cutoff-run.json','forward/opening-capture.json','forward/native-clock-status.json') if (OUT/p).exists()]))


def chapter_17_to_18(z):
    p=csv('domestic-shape-attribution-leaderboard.csv')
    s=p[p.clock.eq('native_0910')&p.horizon.eq(21)&p.scope.eq('combined')].set_index('model')
    extra=s.loc['parent_with_domestic_sign_mass']
    f=csv('larger-simulation-path-summary.csv')
    k=f[f.horizon.eq(21)&f.n_draws.eq(4096)].groupby('model').range_crps.mean()
    curr=read('forward-ledger.json')
    report(17,
        f"""
        The main return discovery is the native monthly domestic shape substitution. It holds the V21 positioning median
        and its interdecile scale fixed in log-return units. The imported shape moves mean positive mass from 57.92%
        to 54.91% and scores 0.210496 instead of 0.223431 Brier against the strongest protected directional model.
        The 21- and 42-origin adjusted intervals against that parent exclude zero within the tested V23 family. Against the
        V21 distribution parent the Brier interval includes zero. CRPS of 0.022911 is an average improvement with mixed
        cohort performance and wider uncertainty. Shape-induced sign reweighting of the unchanged positioning law reproduces
        the full Brier gain and scores {extra.crps:.6f} CRPS in the separate diagnostic. The equal-family and other broad
        aggregates generally weaken the strongest archived directional laws. The weekly improvements remain smaller and
        sensitive to training composition.

        Foreign paths failed to beat the equal-episode India-only library under the strict source requirement. The broad
        mixed result was effectively tied. At the common monthly GJR level, independent Indian daily paths and simple
        generative bridges competed strongly on range. The 4,096-scenario two-seed mean range CRPS is
        {k.loc['india_independent_days']:.6f} for independent Indian days, {k.loc['constant_vol_diffusion']:.6f} for constant
        diffusion and {k.loc['student_t_gjr_same_anchor']:.6f} for Student-t GJR. The previously observed V22 improvement
        over the GJR parent is easiest to explain as a range-distribution improvement at a good volatility anchor.
        Serial order and intraday excursions affect different path targets. The Indian comparison still has only 11
        nonoverlapping monthly return outcomes.

        Probability disagreement and high-variance forecasts remain useful descriptive outputs, with limited evidence
        of an incremental warning of future forecast failures. Model estimation uncertainty, within-law market uncertainty
        and numerical resampling noise have separate receipts. The research-exposed history and cumulative selection
        prevent promotion to an independently confirmed return edge. The forward ledger records
        {len(curr['new_issues'])} genuinely issued new laws at its latest bounded clock check.
        """,
        evidence('native-monthly-shape-comparison.png','monthly-range-mechanisms.png',
            (f'V23_{REPORTS[13]}.md','Falsification'),(f'V23_{REPORTS[15]}.md','Forward research ledger')))
    report(18,
        """
        ## Freeze a monthly sign-mass comparison

        Keep the native V21 positioning law, the V22 foreign-tail direction reference, the domestic shape substitution
        and the simpler sign reweighting as a single small prospective comparison. Retain the exact anchor median and
        dispersion, the same signed law conventions, original cutoff, reference and target sessions. Use Brier and log
        loss for direction, CRPS and coverage for the full law, and paired nonoverlapping blocks for evaluation.

        ## Test the simplest competing ranges

        At a common GJR risk estimate compare the incumbent 08:55 GJR path, equal-episode India history, independent
        Indian days and a constant-volatility bridge. Retain the protected expansion reference. Examine gap and close
        behavior separately from range and barrier metrics. Use the two high-budget seeds and exact finite case scoring
        where appropriate. An additional foreign library should first establish genuinely incremental skill over domestic paths.

        ## Improve forward input reliability

        Capture the complete dated options information and guarded source marks for native V14, retain the corresponding
        V12 and V13 intermediate laws and record every required feature receipt. Extend forward outcomes only through
        an authorized complete 2026 target sequence. Earlier issue laws remain tied to their original timestamps.
        """,
        evidence('domestic-shape-attribution-cases.csv.gz','larger-simulation-path-summary.csv',
                 (f'V23_{REPORTS[15]}.md','Authentic issue and source status')))


def figures():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    bg='#fbfcfe';ink='#252e3c';slate='#697a8c';teal='#157767';orange='#b45d34';light='#e1e8ee'
    plt.rcParams.update({'figure.facecolor':bg,'axes.facecolor':bg,'text.color':ink,'axes.labelcolor':ink,
                         'axes.edgecolor':'none','xtick.color':slate,'ytick.color':ink,'font.family':'DejaVu Sans','font.size':10})
    a=csv('domestic-shape-attribution-leaderboard.csv')
    x=a[a.horizon.eq(21)&a.clock.eq('native_0910')&a.scope.eq('combined')].set_index('model')
    keys=['unchanged_direction_parent','unchanged_distribution_parent','domestic_shape_full','parent_with_domestic_sign_mass']
    labels=['V22 direction parent','V21 positioning parent','Domestic shape','Parent with domestic sign mass']
    fig,axs=plt.subplots(1,2,figsize=(11.4,4.0),layout='constrained',sharey=True)
    for ax,field,title in zip(axs,('brier','crps'),('Direction Brier','Return distribution CRPS')):
        y=x.loc[keys,field].to_numpy()
        ax.barh(np.arange(len(y)),y,color=[slate,slate,teal,orange],height=.52)
        ax.set_yticks(np.arange(len(y)),labels)
        ax.bar_label(ax.containers[0],labels=[f'{q:.6f}' for q in y],padding=4)
        ax.set_xlim(0,max(y)*1.25)
        ax.grid(axis='x',color=light)
        ax.set_axisbelow(True)
        ax.set_title(title,loc='left',fontweight='bold',pad=10)
    axs[0].invert_yaxis()
    fig.suptitle('Monthly NIFTY forecasts at 09:10 IST',fontweight='bold',fontsize=16)
    fig.savefig(OUT/'native-monthly-shape-comparison.png',dpi=158)
    plt.close(fig)
    p=csv('path-risk-leaderboard.csv')
    q=p[p.scope.eq('combined')&p.horizon.eq(21)].set_index('model')
    keys=['same_clock_GJR','india_state_matched','mixed_broad','mixed_strict','india_independent_days',
          'constant_vol_diffusion','student_t_gjr_same_anchor']
    labels=['Protected GJR path','India, matched episodes','Mixed, same episodes','Verified mixed, same episodes',
            'Independent Indian days','Constant-volatility bridge','Student-t GJR bridge']
    x=q.loc[keys,'range_crps'].to_numpy()*1.e4
    fig,ax=plt.subplots(figsize=(9.2,4.4),layout='constrained')
    ax.barh(np.arange(len(x)),x,color=[slate,orange,orange,orange,teal,teal,teal],height=.53)
    ax.set_yticks(np.arange(len(x)),labels);ax.invert_yaxis();ax.set_xlim(0,max(x)*1.2)
    ax.bar_label(ax.containers[0],labels=[f'{v:.2f}' for v in x],padding=4)
    ax.set_title('NIFTY monthly high–low range at 08:55 IST',loc='left',fontsize=15,fontweight='bold',pad=12)
    ax.set_xlabel('Range CRPS (basis points)')
    ax.grid(axis='x',color=light);ax.set_axisbelow(True)
    fig.savefig(OUT/'monthly-range-mechanisms.png',dpi=158)
    plt.close(fig)
    f=csv('probability-reliability-bins.csv.gz')
    fig,axs=plt.subplots(1,2,figsize=(9.3,4.3),layout='constrained',sharex=True,sharey=True)
    for h,ax in zip(HORIZONS,axs):
        p=f[f.horizon.eq(h)&f.clock.eq('native_0910')]
        for id,label,col in [('protected_direction','Protected direction',slate),('component_historical_shape_only','Domestic shape',teal)]:
            q=p[p.model.eq(id)]
            ax.plot(q.forecast,q.observed,color=col,lw=1,alpha=.7)
            ax.scatter(q.forecast,q.observed,s=12+1.2*q.n,color=col,alpha=.8,label=label,edgecolor=bg,linewidth=.5,zorder=5)
        ax.plot([0,1],[0,1],ls='--',color=slate,lw=1,alpha=.5)
        ax.set_xlim(0,1);ax.set_ylim(0,1)
        ax.set_title(f'{h} sessions',loc='left',fontweight='bold')
        ax.set_xlabel('Forecast probability')
        ax.grid(color=light)
        ax.set_axisbelow(True)
    axs[0].set_ylabel('Observed positive frequency')
    axs[1].legend(frameon=False,loc='lower right',fontsize=8)
    fig.suptitle('Historical reliability · point size reflects bin count',fontweight='bold',fontsize=15)
    fig.savefig(OUT/'calibration-reliability.png',dpi=158)
    plt.close(fig)


def make_index():
    a=['# NIFTY V23 research','Robust forecast intelligence, distribution decomposition and model uncertainty.',
       'The historical study uses the 2025–2026 tape through November 17. It preserves the original five- and 21-session NIFTY targets and the source clocks. The forward lane uses separately recorded actual timestamps.',
       'The strongest return finding is lower monthly Brier from a domestic historical shape at the V21 positioning median and dispersion. At a fixed monthly GJR risk anchor, simple independent Indian days and diffusion provide strong range controls. Strict source-verified foreign paths failed to improve on equal domestic episodes.',
       '## The 18 reports','\n'.join(f'{i+1}. {link(f"V23_{name}.md",title)}' for i,(name,title) in enumerate(zip(REPORTS,TITLES))),
       '## Forecast and evidence archives','\n'.join('- '+link(p,t) for p,t in [
          ('MISSION.md','Original V23 brief'),('README.md','Reproduction and forward capture'),
          ('registration.json','Pre-registered hypotheses'),('master-archive-schema.json','Versioned archive map'),
          ('original-horizon-leaderboard.csv','NIFTY direction and distribution leaderboard'),
          ('path-risk-leaderboard.csv','Risk and path leaderboard'),('v23-return-laws.npz','Complete weighted return laws'),
          ('forward-ledger.json','Machine-readable forward ledger'),('manifest.json','Integrity manifest'),
          (earlier(V22/'NIFTY_V22_RESEARCH.md'),'V1–V22 report links in the V22 index')])]
    (OUT/'NIFTY_V23_RESEARCH.md').write_text('\n\n'.join(a)+'\n',encoding='utf-8')
    (OUT/'README.md').write_text(dedent(r"""
        # Reproduce the V23 research

        Run from the trading-desk workspace with the existing virtual environment and frozen V1–V22 inputs. The V22 calendar
        environment is used for completed foreign forward marks. Historical modeling reads only the November 17 vintage.

        ```powershell
        $env:PYTHONDONTWRITEBYTECODE = '1'
        $env:OPENBLAS_NUM_THREADS = '1'
        $v23Python = '.\.venv\Scripts\python.exe'
        $steps = @('common','reference','archive','law_index','geometry','paths','forecast','evidence','parameter_uncertainty','precision','search_risk','attribution')
        foreach ($step in $steps) {
            & $v23Python -W ignore -m ("research.nifty_forecast_v23." + $step)
            if ($LASTEXITCODE -ne 0) { throw "V23 failed in $step" }
        }
        & $v23Python -W ignore -m research.nifty_forecast_v23.attribution paths
        & $v23Python -W ignore -m research.nifty_forecast_v23.report
        & $v23Python -W ignore -m research.nifty_forecast_v23.verify
        ```

        The archived Upstox/Yahoo source audit is held in the V23 source receipts, raw snapshots and paired-bar files.
        To re-acquire those bounded daily bars, run `research.nifty_forecast_v23.sources` before rerunning `paths`.
        Broker acquisition uses read-only market data and the existing Upstox credential. It does not expose the token.

        The forward lane is clock-bound. The commands `forward stage`, `forward dry-run` and `forward watch` are the
        one-run November 26 capture sequence and must be invoked before that morning cutoff to capture a new issue.
        `forward settle` refreshes the ledger only after verified original targets are available. Replaying the reports
        uses the saved forward receipts. Changes to native candidate state require a new authentic decision record.
        Run `research.nifty_forecast_v23.gjr_continuation` for the historical V14 GJR risk replay and live state preflight.

        A return-law NPZ stores atoms and weights concatenated with zero-based offsets. The case CSV identifies the law
        and exact target. The source map records log versus arithmetic support from earlier versions. The joint path arrays
        store log-relative OHLC. For exact reproduction use the library, donor order, clock, anchor and recipe.

        [Research index](NIFTY_V23_RESEARCH.md)
        """).strip()+'\n',encoding='utf-8')


def run(only_forward=False):
    if only_forward:
        forward_report()
        chapter_17_to_18(None)
        return
    z=csv('original-horizon-leaderboard.csv')
    chapter_1_to_3()
    chapter_4_to_7(z)
    chapter_8_to_12(z)
    chapter_13_to_15(z)
    forward_report()
    chapter_17_to_18(z)
    figures()
    make_index()
    print('Wrote',len(REPORTS),'V23 reports and three figures.',flush=True)


if __name__=='__main__':
    import sys
    run('forward' in sys.argv[1:])
