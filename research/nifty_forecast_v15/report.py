"""Render V15 reports directly from verified score and source receipts."""
import re

from .common import *
from .data import Daily

HORIZON_WORD={5:'Weekly',21:'Monthly'}


def csv(name,root=OUT):
    return pd.read_csv(root/name,low_memory=False)


def one(frame,**filters):
    for k,v in filters.items():
        frame=frame[frame[k].eq(v)]
    if len(frame)!=1:
        raise ValueError(f'Expected one row for {filters}, got {len(frame)}')
    return frame.iloc[0]


def top(frame,group,metric,n):
    return frame.sort_values(metric,kind='stable').groupby(group,sort=False).head(n).sort_values([*group,metric])


def numeric(x):
    if isinstance(x,(bool,np.bool_)):
        return 'Yes' if x else 'No'
    if pd.isna(x):
        return '—'
    if isinstance(x,(int,np.integer)):
        return f'{x:,}'
    if isinstance(x,(float,np.floating)):
        return f'{x:.6f}'
    return str(x).replace('|','/').replace('\n',' ')


def md_table(frame,columns):
    columns={c:c.replace('_',' ') for c in columns} if not isinstance(columns,dict) else columns
    lines=['| '+' | '.join(columns.values())+' |','| '+' | '.join(['---']*len(columns))+' |']
    for row in frame[list(columns)].itertuples(index=False,name=None):
        lines.append('| '+' | '.join(numeric(x) for x in row)+' |')
    return '\n'.join(lines)


def links(*files):
    return ' '.join(f'[{label}]({ref})' for label,ref in files)


def report(key,title,*paras):
    name=f'V15_{key}.md'
    (OUT/name).write_text('# '+title+'\n\n'+'\n\n'.join(x.strip() for x in paras if x)+'\n',encoding='utf-8')


def reproduction():
    z=read('benchmark-replay.json')
    iv=csv('replay-volatility.csv').groupby(['horizon','model'],as_index=False).agg(origins=('origin','nunique'),mae=('mae','mean'),variance_qlike=('qlike','mean'))
    b=csv('replay-expansion.csv').groupby(['horizon','model'],as_index=False).agg(origins=('origin','nunique'),brier=('brier','mean'),forecast_rate=('p','mean'),actual_rate=('actual','mean'))
    e=csv('replay-endpoint.csv').groupby(['horizon','model'],as_index=False).agg(origins=('origin','nunique'),brier=('brier','mean'),endpoint_crps=('crps','mean'))
    p=csv('replay-path.csv').groupby(['horizon','model','target'],as_index=False).agg(origins=('origin','nunique'),crps=('crps','mean'),coverage80=('coverage80','mean'))
    t=csv('replay-touch.csv').groupby(['horizon','model'],as_index=False).agg(cases=('origin','size'),origins=('origin','nunique'),brier=('brier','mean'))
    report('REPRODUCTION_AND_BASELINES','V15 reproduction and baselines',
      f"""The frozen V14 chain used **2025–2026** and finished on **{FREEZE}**. V15 matched **{z['rows']['volatility']:,}** risk rows, **{z['rows']['expansion']:,}** expansion probabilities, **{z['rows']['path']:,}** replayed joint-path marginals, **{z['rows']['endpoint']:,}** standalone endpoint rows and **{z['rows']['touch']:,}** fixed-barrier outcomes. Maximum numerical differences were {z['maximum_risk_delta']:.1f} for the matched volatility point predictions and {z['maximum_expansion_delta']:.1f} for the expansion probabilities. V14 used 2,048 coherent 21-session OHLC paths at 265 origins, with weekly paths taken from their first five steps. V15 preserves the individual benchmark laws, including the separately fitted point and endpoint models.""",
      '## Volatility\n\n'+md_table(iv,['horizon','model','origins','mae','variance_qlike']),
      '## Expansion\n\n'+md_table(b,['horizon','model','origins','brier','forecast_rate','actual_rate']),
      r"""For horizon H, raw IV uses the chi-square survival probability evaluated at H × (1.25 × trailing H-session annualized RV / ATM IV)² with H degrees of freedom. The historical benchmark uses the most recent 185 prior rows from the fold-month sample, retaining eligible labels that matured before that fold. Its frequency is (events + 0.75) / (observations + 1.50). Weekly and monthly variance levels and event probabilities retain the original basis, definitions and as-of rules.""",
      '## Endpoints\n\n'+md_table(e,['horizon','model','origins','brier','endpoint_crps']),
      '## Joint-path marginals\n\n'+md_table(p,['horizon','model','target','origins','crps','coverage80']),
      'The weekly V13 diffusion range reference of **0.005793** comes from the individually archived V13 diffusion range scores in V14. The monthly Student-GJR range reference comes from independently re-scoring the original V14 joint atoms.',
      '## Fixed-barrier touch\n\n'+md_table(t,['horizon','model','cases','origins','brier']),
      links(('Replay receipt','benchmark-replay.json'),('Archived range replay','replay-path.csv'),
            ('Original V14 research index','../../../nifty_forecast_v14/2026-11-25/run-001/NIFTY_V14_RESEARCH.md'),
            ('CRPS and proper scoring rules','https://doi.org/10.1198/016214506000001437')))


def session_layers():
    p=csv('session-evidence.csv')
    ctl=csv('session-dependence-evidence.csv')
    r=csv('session-feature-receipts.csv')
    rec=csv('session-cash-reconciliation.csv')
    c=r.groupby('stage',as_index=False).agg(session_count=('day','nunique'),four_sectors=('sector_ready','sum'),new_proxies=('added_source_ready','sum'))
    early=ctl[(ctl.checkpoint.eq('pre_open'))&ctl.target.eq('immediate_open')&ctl.model.eq('offshore_fresh')]
    sel=p[(p.model.isin(['offshore_fresh','sector_leadership','sector_etf','sector_placebo']))&
          (p.target.isin(['immediate_open','same_session','weekly_endpoint','monthly_endpoint','next_close','next_open_gap']))]
    summary=pd.concat([sel[sel.checkpoint.eq('pre_open')],sel[sel.checkpoint.eq('opening')&sel.target.isin(['same_session','weekly_endpoint','monthly_endpoint'])],
                      sel[sel.checkpoint.eq('midday')&sel.target.eq('next_open_gap')],
                      sel[sel.checkpoint.eq('near_close')&sel.target.isin(['weekly_endpoint','monthly_endpoint','next_close'])]])
    big=one(early,metric='brier')
    report('INFORMATION_TIMING_AND_SESSIONS','V15 information arrival and Indian market sessions',
        f"""The new offshore close block improved the pre-open immediate opening-gap Brier on **{big.n}** common observations from **{big.parent_score:.6f}** to **{big.score:.6f}**. The gain was {big.gain:.6f}, with the ten-session family-adjusted interval [{big.family_low10:.6f}, {big.family_high10:.6f}] and early/later gains {big.early_gain:.6f}/{big.later_gain:.6f}. The opening gap is the same morning's open relative to the previous official close. The next-session opening gap remains a separately forecast outcome after that morning's gap has occurred. Its denominator is the actual current session close, used to calculate the later label. Prefix forecasts of the actual remaining cash session use the latest eligible cash price.""",
        '## Cutoffs and reconstruction\n\n'+md_table(c,['stage','session_count','four_sectors','new_proxies']),
        f"""IST decisions are 09:10, 10:05, 12:30, 15:10 and 17:00. The last eligible cash bar closes five minutes or more before each intraday decision. Upstox timestamps denote bar starts in this reconstruction. Stable cash OHLC labels come from the frozen daily series. {len(rec):,} full five-minute sessions had an archived end-of-day bar available for reconciliation. {int(rec.gap_points.abs().le(.05+1.e-9).sum()):,} closed within 0.05 index points of the official daily mark. The official close anchors all labels and the 17:00 close-based forecast. Opening, midday and near-close use timestamp-filtered 5-minute cash bars and 25-minute sector, broad-index and ETF bars. Each sector return is measured against the latest same-bar cash index. Intraday market breadth is proxied by participation across sector indices, while authentic equal-weight breadth comes from the stable previous daily observation.""",
        """S&P 500, Dow, Nikkei, Hang Seng, DAX and FTSE use time-zone-converted cash closes, local daylight-saving rules and a 60-minute allowance. Vendor day labels stand in for historical publication receipts. The most recent eligible market close is carried through foreign holidays and weekends. The frozen global-risk, VIX, FX and oil observations retain their inherited earlier-day allowances. EOD NSE option quotes retain their verified earlier-day timestamps at each intraday checkpoint. A genuine intraday option-snapshot update remains untested. The fixed endpoint targets refer to the original previous-close window and also score residual same-session and next-session targets separately.""",
        '## Paired scores\n\n'+md_table(summary,['checkpoint','target','model','parent','n','brier','brier_base','crps','crps_base']),
        """Ridge location estimates used at most 160 earlier matured observations per decision and target. The common centered empirical outcome law isolates location. Sector timing support requires every feature in the stated group to have a usable record at the decision. The placebo permutes training blocks for the sector block and retains the same current inputs. Asian close availability can shift during the Indian session. European and US closes have their own, later clocks. Any gap result applies to the tested morning decision and target.""",
        links(('Session forecasts','session-forecasts.csv.gz'),('Bar clocks by decision','session-feature-receipts.csv'),
              ('Source audit','session-source-audit.json'),('Complete paired session table','session-evidence.csv'),
              ('Session block intervals','session-dependence-evidence.csv'),('Upstox historical candles','https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/'),
              ('NSE cash trading times','https://www.nseindia.com/resources/exchange-communication-holidays')))
    a=read('intraday-acquisition.json')
    ag=pd.DataFrame(a['requests'])
    col='label'
    if col not in ag:
        col=ag.columns[0]
    count=ag.groupby(col,as_index=False).size()
    report('ADDITIONAL_MARKET_INFORMATION','V15 additional Upstox, NSE and global inputs',
       """Daily experiments hold the decision clock fixed and test whether the newest eligible block improves a matched forecast. Domestic revisions use NSE official equal-weight breadth, financial-sector and cyclical/defensive rotation, concentration and synchronization. Liquidity uses ETF activity, traded participation, spread and impact proxies and the intraday variance shape. The derivative block uses the new eligible ATM term point, skew and curvature, futures basis, term structure, same-contract futures changes, unsigned OI concentration, volume-normalized OI and straddles. Offshore inputs separate cross-market equity, volatility, currency, oil, gold ETF and rate changes. Attribution is predictive and conditional on the model and the other blocks. Counterfactuals hold one block stale while retaining the same cash anchor.""",
       '## New authenticated 25-minute requests\n\n'+md_table(count,[col,'size']),
       """NIFTY 500 and FMCG are cap-weighted market and defensive proxies, and NIFTYBEES is an ETF with volume. The 25-minute index sources use bank, financial services, IT and auto series from the V10 archive. Each group uses the actual instrument identifier and source-file hash. Upstox's cached instrument list did not establish an intraday official NIFTY 500 Equal Weight instrument. That benchmark remains in the daily official NSE cohort. Derivatives use trade-filtered EOD data with an explicit mark date earlier than the latest cash session. The term lookup retains the two source expiries, calendar tenor, quality status and interpolation regime. Nearest, interpolated variance and exact-tenor cases are retained. Same-contract changes preserve the prior roll controls.""",
       links(('New authenticated calls','intraday-acquisition.json'),('Quote tenor and lag audit','remaining-tenor-availability.csv'),
             ('Full session source audit','session-source-audit.json'),('Daily availability receipt','data-avail-receipt.json'),
             ('Freshness and ablation results','V15_INCREMENTAL_INFORMATION_VALUE.md')))


def vol_transitions():
    p=csv('volatility-transition-evidence.csv')
    v=csv('volatility-level-evidence.csv')
    q=csv('secondary-paired-evidence.csv')
    refs=p[p.model.isin(['historical','iv_raw'])]
    winners=top(p,['horizon','event'],'brier',3)
    shown=pd.concat([winners,refs]).drop_duplicates(['horizon','event','model']).sort_values(['horizon','event','brier'])
    matches=q[q.category.eq('expansion')&q.event.eq('expand')&q.model.isin(['historical','fixed_75IV25RV','V14_EGARCH_t','iv_offsets_all','iv_level_change','iv_change_only'])]
    report('VOLATILITY_EXPANSION_INTELLIGENCE','V15 volatility transitions and expansion',
        """The five transition targets are a 25% increase in H-session realized volatility, a 50% increase, a 20% contraction, entry into the training-only high-volatility state and elevated volatility across both halves of the future window. The high-volatility threshold is the 75th percentile of earlier matured volatility. High entry uses only eligible initially lower-risk observations, and persistence uses the V14 two-half definition. The extra 50% expansion was fixed before evaluating V15. Volatility magnitude is evaluated separately in annualized units. The same trailing-risk anchor sets expansion and contraction thresholds.""",
        '## Transition scores\n\n'+md_table(shown,['horizon','event','model','n','p','actual_rate','brier','log_loss','brier_gain']),
        '## Paired 25% expansion tests\n\n'+md_table(matches,['horizon','model','n','gain','low10','high10','family_low21','family_high21']),
        '## Volatility point estimates\n\n'+md_table(v.sort_values(['horizon','mae']),['horizon','model','n','forecast_vol','true_vol','mae','qlike']),
        """Raw-IV probability retains the V14 chi-square mapping. The persistence experiment also tests a product of independent chi-square tails over two chunks, a diagnostic approximation. GJR, EGARCH, India VIX, trailing RV, EWMA and simple variance mixtures each enter that same mapping. V15's fixed 75/25 risk event substitute uses H-session RV. The reproduced V13 point mixture uses the older HAR volatility input. Regularized offsets operate on the raw IV log odds, with an intercept-only control. The level-only, change-only, level-and-change, full risk and delayed or permuted controls distinguish calibration from extra information. Weekly full and placebo scores, monthly log loss and probability-versus-frequency gaps remain visible. Magnitude MAE and variance QLIKE can favor separate processes. Every fitted row enforces the earlier maturity cut.""",
        links(('Complete transition leaderboard','volatility-transition-evidence.csv'),('Per-origin probabilities','volatility-transition-scores.csv.gz'),
         ('Volatility levels by origin','volatility-level-scores.csv'),('Fitted transition offsets','volatility-transition-fit-ledger.json'),
         ('Paired uncertainty','secondary-paired-evidence.csv')))


def forensics():
    q=read('forensics-receipt.json')
    x=csv('causal-error-evidence.csv')
    a=x[x.variable.eq('range')]
    shocks=csv('severe-error-inventory.csv')
    sc=csv('scenario-envelope.csv')
    t=csv('endpoint-tail-evidence.csv')
    diag=top(t,['horizon','event'],'brier',2)
    raw=t[t.model.eq('common_raw_iv')]
    out=pd.concat([diag,raw]).drop_duplicates(['horizon','model','event']).sort_values(['horizon','event','brier'])
    report('CAUSAL_FORECAST_ERROR_LEARNING','V15 learning from resolved forecast errors',
       f"""V14's **{q['severe_record_count']}** severe records represent **{q['unique_windows']}** unique horizon–origin windows. The ledger separates unexpected upside/downside, volatility underestimation/overestimation, range errors, overconfident direction, tail misses and barrier errors. Causal error features become eligible only when the original target session is strictly earlier than the current origin. At each origin the experiment fits on up to 120 eligible original forecast errors and uses up to 12 resolved errors for the recent state. Disagreement comes from the original dispersion of volatility and probability models, standardized error histories, analogue diversity, relative feature scales, parameter shifts, and implied versus trailing risk. It compares historical frequency, recent frequency and a nominal threshold, as well as asymmetric and width-only interval corrections and shrunken direction scores.""",
       '## Range diagnostics on identical origins\n\n'+md_table(a,['horizon','task','model','cases','brier','log_loss','coverage','width','interval_score']),
       '## Archived failure families\n\n'+md_table(shocks,['horizon','kind','rows','origins','worst','first','last']),
       """The monthly lower miss was extremely sparse. Brier comparisons on that subset were dominated by predicted false positives. The monthly upper warning and weekly upper warning remain difficult, including against a constant nominal-probability control. Width or asymmetry correction is scored for both coverage and interval loss. V15 retains the larger uncertainty in the central law and keeps stress paths separate.""",
       links(('Failure features and outcome maturation','causal-error-scores.csv.gz'),('All error comparisons','causal-error-evidence.csv'),
          ('Warning model coefficients','causal-error-fit-ledger.json'),('V14 archived negative warning comparison','../../../nifty_forecast_v14/2026-11-25/run-001/failure-warning-matched.csv')))
    report('EXTREME_RISK_AND_SCENARIO_INTELLIGENCE','V15 extreme probabilities and separate scenario paths',
       """The probabilistic comparisons use regular IV diffusion, a 22% path-level Student-t(6) innovation mixture, empirical asymmetry, sign-and-magnitude, a fixed issue-law baseline and a 25% historical tail mixture. Empirical histories are restricted to earlier matured samples and the tail mixture balances consecutive remaining-horizon blocks. PIT- and width-only diagnostics using resolved errors are stored in the causal error study. Absolute terminal extremes are 3% for five sessions and 5% for 21 sessions, alongside 1.5 times the as-of implied horizon scale. Event-rate, Brier and log loss retain separate tail directions. All independent extreme-event counts use merged overlapping episodes.""",
       '## Probabilistic tail comparisons\n\n'+md_table(out,['horizon','event','model','n','p','actual','brier','log_loss']),
       '## Hypothetical OHLC stress paths\n\n'+md_table(sc,['scenario','horizon','endpoint','volatility','range','gap','drawdown']),
       '## Matching against unique serious misses\n\n'+md_table(pd.DataFrame(q['descriptive_matches']),['horizon','n','entire_box','stress_maxima_cover','typical_distance']),
       """Eight explicit hypothetical paths describe repeated upside or downside, sudden volatility expansion, a large opening gap, a market reversal, concentrated leader weakness, sustained high volatility and a foreign repricing. A remaining calendar path is built from daily log steps, explicit opening gaps and stated intraday excursions. The 21-session scenario repeats the initial pattern at a stated attenuation. Scenario distances use the outcome vector of endpoint, annualized volatility, high–low range, largest absolute gap and drawdown, with units fixed in code. Stress maxima coverage tests all five adverse dimensions jointly. Our retrospective envelope leaves severe combinations outside its span and carries no calibrated occurrence probabilities, ranks or percentiles.""",
       links(('Scenario assumptions and OHLC rows','scenario-paths.csv'),('Nearest scenarios by severe window','scenario-severe-error-coverage.csv'),
             ('Complete tail scores','endpoint-tail-scores.csv.gz'),('Extreme-event counts','V15_EPISODE_LEVEL_EVALUATION.md')))


def fixed_and_information():
    q=csv('checkpoint-leaderboard.csv')
    w=csv('original-windows.csv')
    r=csv('matched-window-evidence.csv',)
    r['checkpoint']=r.checkpoint.astype(str)
    core=['frozen','zero_remaining','price_only','historical','iv_restart','gjr_restart','refit','incremental']
    points=q[q.apply(lambda s:s.checkpoint in CHECKPOINTS[s.horizon],axis=1)&q.model.isin(core)]
    picked=points[points.model.isin(['frozen','price_only','iv_restart','gjr_restart','incremental'])]
    sizes=w.groupby('horizon',as_index=False).agg(windows=('origin','size'),fixed_dates=('target','nunique'),calendar_match=('literal_calendar','sum'),
        first_target=('target','min'),last_target=('target','max'))
    mechanical=csv('mechanical-same-law-evidence.csv')
    mechanical=mechanical[((mechanical.horizon.eq(5)&mechanical.checkpoint.isin([0,4])) | (mechanical.horizon.eq(21)&mechanical.checkpoint.isin([0,20])))]
    width=top(q[q.checkpoint.eq(0)],['horizon'],'endpoint_is80',3)
    by=r[r.checkpoint.eq('updated')&r.metric.isin(['brier','endpoint_crps','remaining_return_crps','range_crps','joint_energy','vol_mae'])
          &r.reference.eq('iv_restart')&r.candidate.isin(['historical','gjr_restart','refit','incremental','vol_state','full','hybrid','analogue'])]
    report('FIXED_ENDPOINT_FORECASTING','V15 fixed-endpoint forecasts',
       """The five-session experiment uses checkpoints 0–4. The 21-session experiment scores every daily checkpoint 0–20 and displays 0, 1, 5, 10, 15 and 20 as the registered comparison points. Each origin keeps its original reference price S₀ and the same terminal close Sᴴ throughout. A live-like conditional path uses the actual observed prefix and simulates from Sₜ. The original-horizon return is (Sₜ / S₀) × (Sᴴ / Sₜ) − 1. The remaining-return target is Sᴴ / Sₜ − 1. Whole-window polarity, range and volatility use the previously observed portion, and their remaining-only counterparts score the still-unknown part separately.""",
       '## Window and calendar coverage\n\n'+md_table(sizes,['horizon','windows','fixed_dates','calendar_match','first_target','last_target']),
       """The primary historical comparison uses V14's exact Hth observed-session outcomes. In 16 windows the archive-based schedule visible at issue projected a different calendar date. The literal-calendar sensitivity retains the other 466 windows, and the remaining-tenor forecast uses the schedule visible at the decision. Models never use the realized terminal calendar to select an earlier IV. All seven benchmark classes are represented by the old frozen law, deterministic zero remaining return, empirical history, raw IV and GJR restarts, same-time refit and incremental filtering. The price-only stochastic control anchors to the latest price and uses the issue IV. Lower scores are better except accuracy and coverage, where the relevant benchmark is the realized class balance or nominal coverage.""",
       '## Registered endpoints\n\n'+md_table(picked,['horizon','checkpoint','model','n','brier','endpoint_crps','remaining_return_crps','endpoint_cov80','endpoint_width80']),
       '## Matched updated-window gains versus restarted IV\n\n'+md_table(by,['horizon','candidate','metric','n','model','control','gain','family_low21','family_high21']),
       '## Clean mechanical comparisons under one lognormal law\n\n'+md_table(mechanical,['horizon','checkpoint','model','n','brier','crps','remaining_brier','remaining_crps']),
       '## Interval score leaders at issue\n\n'+md_table(width,['horizon','model','n','endpoint_is80','endpoint_cov80','endpoint_width80']),
       links(('All daily checkpoint scores','checkpoint-leaderboard.csv'),('Literal calendar sensitivity','literal-calendar-leaderboard.csv'),
             ('All matched evidence','matched-window-evidence.csv'),('Fixed timestamps','update-calendar.csv'),
             ('Historical forecast case','historical-fixed-endpoint-updates.png'),('Exact elapsed-time and price-anchor controls','mechanical-same-law-evidence.csv')))
    groups=r[r.checkpoint.eq('updated')&~r.attribution.eq('restart comparison')&~r.attribution.str.startswith('shock')
             &r.metric.isin(['brier','endpoint_crps','vol_mae','range_crps','joint_energy'])]
    simple=groups[groups.metric.isin(['brier','range_crps'])].sort_values(['horizon','attribution','metric'])
    passage=csv('passage-matched-risk-sets.csv')
    passage=passage[passage.group.eq('all surviving')&passage.reference.eq('iv_restart')&passage.metric.isin(['brier','integrated_brier'])]
    report('INCREMENTAL_INFORMATION_VALUE','V15 incremental information by block',
       """The information ladder begins with the immutable earlier law (A), the price-anchored shortened forecast using issue IV (B), raw IV revised at the same clock (C), a domestic risk and location fit using breadth and rotation (D), and the complete eligible domestic, derivatives, foreign and liquidity model (E). A and B differ in the generator as well as elapsed time and known price movement. The exact lognormal decomposition holds the law and issue volatility constant to isolate those two mechanical effects. The other tests use equal decisions, current reference prices, remaining horizons and path draws. A second addition order fits derivatives first, then the full candidate. Within-model stale domestic, stale surface and stale foreign comparisons isolate the role of the newest available block. Randomized training blocks, five-session delays and delay-plus-noise inputs preserve active parent specifications. Model fit location and scale columns can correlate across blocks.""",
       '## Post-issue matched-window gains\n\n'+md_table(simple,['horizon','reference','candidate','attribution','metric','n','gain','early_gain','later_gain','family_low10','family_high10']),
       '## Additional loss comparisons\n\n'+md_table(groups[groups.metric.isin(['vol_mae','joint_energy'])&groups.attribution.isin(['revised raw risk','fresh domestic','fresh surface','fresh foreign','all eligible inputs'])],
                    ['horizon','candidate','attribution','metric','n','gain','family_low21','family_high21']),
       '## Barrier calibration on common surviving risk sets\n\n'+md_table(passage,['horizon','candidate','metric','n','origins','candidate_loss','reference_loss','average_episode_gain','family_low21','family_high21']),
       """The fully refitted nesting uses absolute levels. The full sequential design gives feature groups matched level and revision terms. Their train-only risk-normalized location and realized-scale responses use up to 180 matured observations. Through-time differences in score are reported per original window, so repeated updates receive no added outcome weight. Raw volatility levels, dispersion calibrations and earlier-market timing results have dedicated controls and are tracked as separate objectives.""",
       links(('Matching and ablations','matched-window-evidence.csv'),('Per-update fitted parameters','fitted-update-models.ndjson.gz'),
             ('Overseas timing evidence','V15_INFORMATION_TIMING_AND_SESSIONS.md'),('Surviving barrier rows','sequential-passage.csv.gz')))


def revision_and_shock():
    x=csv('revision-evidence.csv')
    s=csv('shock-response-evidence.csv')
    a=csv('shock-touch-evidence.csv')
    r=x[x.checkpoint.astype(str).eq('all')&x.model.isin(['iv_restart','incremental','refit','domestic','full','vol_state'])]
    r1=r[r.quantity.eq('p_up')]
    r2=r[r.quantity.isin(['endpoint_mean','endpoint_q50','remaining_vol_mean','endpoint_width80','endpoint_q10','endpoint_q90','remaining_range_mean'])]
    p=csv('historical-example-passage.csv')
    p=p[p.forecast_step.eq(1)&p.checkpoint.isin([1,3,5,10,15,20])&p.model.eq('iv_restart')&~p.already_touched]
    report('FORECAST_REVISION_MODELS','V15 how forecasts revise through time',
        """The study compares complete rolling refits, a Bayesian/Kalman-style persistent drift estimate, conservative fixed fractional revisions, a shrunken shock-state drift, and supervised risk-normalized residual corrections. The incremental filter starts with the issued path law's average daily log drift and a small prior variance. It updates from observed standardized close innovations, adding a small process-variance term and pulling the state toward the initial drift. The reported 50/50 blend is a standalone probability check. A predictable revision given earlier information is a conditional forecast diagnostic. The study leaves open long-run and conditional drift.""",
        '## Direction probability revisions\n\n'+md_table(r1,['horizon','model','n','n_origins','old_brier','new_brier','half_update_brier','mean_abs_revision','earlier_level_corr','revision_response_slope']),
        '## Changes in location, tails and width\n\n'+md_table(r2,['horizon','model','quantity','mean_revision','mean_abs_revision','earlier_level_corr','revision_response_slope']),
        '## One-step 2% barrier revisions in the historical example\n\n'+md_table(p,['horizon','checkpoint','asof','side','cdf','actual_by_step']),
        """The response slope regresses the realized target minus the previous expectation on the following revision. A slope near one is consistent with a well-scaled revision in this diagnostic. The earlier-level correlation uses only the forecast quantity available at the preceding decision, and both statistics are descriptive under shared outcome dependence. For range and volatility, the archived errors and coverage compare the previous uncertainty band with fully updated path laws. Each barrier's future probability is evaluated only while the side is still at risk.""",
        links(('Per-update changes','revision-attribution.csv.gz'),('Revision metrics','revision-evidence.csv'),('Historical passage curves','historical-example-passage.csv'),
              ('Original linear filtering paper','https://doi.org/10.1115/1.3662552')))
    cols=['horizon','trigger','model','n','origins','mean_abs_z','continuation','reversal','predicted_continuation',
          'signed_brier','endpoint_crps','vol_mae','range_crps']
    report('SHOCK_VERSUS_PERSISTENCE','V15 shocks versus persistence',
       """Every latest close innovation is standardized relative to the previous path's location and risk. The two-sided CUSUM accumulates signed innovations with a 0.45 per-step allowance. A shock is flagged with absolute standardized innovation above 2.15 or CUSUM magnitude above 2.75. A persistent candidate also needs at least two observed periods, more than 65% sign agreement in up to three recent returns, and corroboration from breadth or financial leadership. These are ex-ante trigger states. They compare a scale-only update, an update with signed continuation or reversal drift, the unchanged restart, and incremental drift/risk filtering.""",
       '## Continuation and remaining-path outcomes\n\n'+md_table(s,cols),
       '## Surviving barrier outcomes by trigger\n\n'+md_table(a,['horizon','trigger','model','cases','touch_brier','integrated_brier']),
       """Continuation means the later remaining-window return shares the sign of the latest observed session. Directional loss uses the conditional remaining return. The same-law risk and range outputs include the observed original-window prefix and are separately checked in the remaining-only score columns. Corroboration is a predictive design assumption. A lasting change in expected returns would require stable improvement over the same-time risk-only control, evidence across disjoint episodes and absence of comparable gains from lagged or randomized input blocks.""",
       links(('Post-shock touch evidence','shock-touch-evidence.csv'),('Conditional trigger outcomes','shock-response-evidence.csv'),
           ('CUSUM states, innovations and latest inputs','joint-update-receipts.json')))


def paths_and_passage():
    q=csv('update-only-leaderboard.csv')
    data=pd.DataFrame(read('joint-update-receipts.json'))
    e=data.groupby('horizon',as_index=False).agg(checkpoints=('origin','size'),particle_min=('particle_ess','min'),
                      particle_median=('particle_ess','median'),analogue_min=('analogue_ess','min'),analogue_median=('analogue_ess','median'),
                      analogue_count_max=('analogue_count','max'),hybrid_prior_median=('hybrid_prior_fraction','median'))
    models=['frozen','iv_restart','gjr_restart','particle','hybrid','vol_state','analogue','historical']
    z=csv('passage-leaderboard.csv')
    paired=csv('passage-matched-risk-sets.csv')
    ordering=csv('first-passage-ordering-evidence.csv')
    orders=ordering[ordering.model.isin(['iv_restart','gjr_restart','analogue','hybrid'])]
    rows=[]
    for (h,m),x in orders.groupby(['horizon','model']):
        row=dict(horizon=h,model=m)
        for c in ['order_brier','no_additional_brier']:
            zz=x[x[c].notna()]
            row[c]=np.average(zz[c],weights=zz['count'])
            row[c+'_n']=int(zz['count'].sum())
        rows.append(row)
    ordout=pd.DataFrame(rows)
    report('CONDITIONAL_PATH_UPDATING','V15 conditional path updating',
       """Every updated law joins the exact observed prefix to a simulated remaining path. A path has O/H/L/C per session and preserves relative price continuity between its current anchor and all future closes. This makes endpoint, realized volatility, high, low, range, drawdown, rebound and touch probabilities jointly determined. Known highs and lows impose a floor on whole-window range throughout each sequence. Simulated columns quantify the remaining period separately. The original frozen dated law is accessed by hash and continues to supply the no-update baseline.""",
       '## Restart, condition and hybrid comparisons\n\n'+md_table(q[q.model.isin(models)].sort_values(['horizon','range_crps']),
             ['horizon','model','origins','range_crps','range_cov80','range_width80','remaining_range_crps','vol_crps','drawdown_crps','joint_energy']),
       '## Particle and analogue concentration\n\n'+md_table(e,['horizon','checkpoints','particle_min','particle_median','analogue_min','analogue_median','analogue_count_max','hybrid_prior_median']),
       """The particle likelihood weights paths by standardized observed close-prefix distance and realized prefix variance. Effective sample size is 1 / Σw² before any tempering, relative to 2,048 original particles. The low-ESS fallback adds uniform support below 24. A hybrid chooses a fixed ESS-bound share of conditional original paths and fills the remainder with restarted IV/GJR paths. Analogue fitting uses up to 210 already-resolved original windows, matches prefix behavior and starting risk, scales the remaining analogous path by current IV and gives the matched empirical distribution mixed uniform support. Empirical blocks use matched remaining-horizon length. IV diffusion, GJR refiltering and the blended risk state restart from current market levels. The energy score compares normalized endpoint, range, risk and drawdown jointly using shared path draws and a paired approximation.""",
       links(('Encoded joint forecast law manifest','joint-update-archive.json'),('Concentration receipts','joint-update-receipts.json'),
             ('Whole and remaining path scores','sequential-scores.csv.gz'),('Historical fixed-endpoint chart','historical-fixed-endpoint-updates.png')),
       '![Historical fixed target forecast revisions](historical-fixed-endpoint-updates.png)')
    cols=['horizon','stage','group','model','n','origins','actual','p','brier','integrated_brier','passage_log_loss']
    q0=z[z.model.isin(models)&(z.group.eq('fixed thresholds')|z.group.eq('opposite after hit'))]
    qs=paired[paired.group.eq('opposite after hit')&paired.reference.eq('iv_restart')&paired.metric.eq('integrated_brier')]
    counts=read('sequential-score-counts.json')
    report('SEQUENTIAL_FIRST_PASSAGE','V15 first passage, survival and opposite barriers',
       f"""The five fixed upper and lower barrier pairs are 0.5%, 1%, 2%, 3% and 5% from the initial close. The four IV-relative pairs use the issue-time volatility scale multiplied by 0.5, 1.0, 1.5 and 2.0. **{counts['passage']:,}** eligible model rows score only levels untouched by the decision. **{counts['resolved_side_checkpoints_excluded']:,}** previously resolved side checkpoints were removed from the risk sets before comparing models. The initial historical laws supply unconditional passage from the current price. Empirical analogue reweighting supplies conditional historical passage and the earlier fixed law can be conditioned on survival through the current step. Order has four outcomes for upper, lower, ambiguous same-candle, and neither. An opening outside a barrier can establish the first hit when both levels occur within a daily candle. The original resolved order is pinned at later checkpoints.""",
       '## Touch and integrated time Brier\n\n'+md_table(q0,cols),
       '## Opposite-barrier timing compared with raw restart\n\n'+md_table(qs,['horizon','candidate','n','origins','candidate_loss','reference_loss','average_episode_gain','family_low21','family_high21']),
       '## First-order and no additional hit\n\n'+md_table(ordout,['horizon','model','order_brier_n','order_brier','no_additional_brier_n','no_additional_brier']),
       """The time target is the first event within the remaining window, with the no-event mass at remaining H + 1. Integrated Brier averages the squared errors of the touch CDF at each remaining session. The event-time log loss uses the probability mass at the correct session or at the censoring category. Expected time given a hit is reported separately, with the corresponding subset count. Because that subset is selected by actual touch and forecast probability, it complements the proper all-at-risk score. Score weights for known ordering and for no additional hit after both levels are visited are excluded. The previous resolved side is handled separately from the probability of touching the opposite side.""",
       links(('All first-touch rows','sequential-passage.csv.gz'),('Matched risk sets and bootstrap','passage-matched-risk-sets.csv'),
             ('Timing conditional on a hit','conditional-time-given-touch.csv'),('Survival curve example','historical-example-passage.csv'),
             ('First order and additional hits','sequential-order.csv.gz')))


def direction_and_comparison():
    ref=csv('cross-vintage-endpoint-leaderboard.csv')
    z=csv('endpoint-mechanism-evidence.csv')
    prob=csv('endpoint-probability-mechanism-evidence.csv')
    r=csv('checkpoint-leaderboard.csv')
    u=csv('cross-vintage-matched-uncertainty.csv')
    top_new=top(ref[ref.version.eq('V15 joint laws')&~ref.model.eq('zero_remaining')],['horizon'],'brier',5)
    legacy=ref[ref.version.eq('Protected reference systems')].sort_values(['horizon','brier'])
    keep=legacy[~legacy.model.str.contains('shift|permute|noise',case=False)]
    selected=pd.concat([keep,top_new]).sort_values(['horizon','version','brier'])
    m=csv('matched-window-evidence.csv')
    cases=r[r.model.isin(['price_only','iv_restart','full','gjr_restart','incremental'])]
    post=cases[cases.checkpoint.gt(0)&cases.apply(lambda s:s.checkpoint in CHECKPOINTS[s.horizon],axis=1)]
    report('DIRECTIONAL_FORECAST_DISCOVERY','V15 directional and return-distribution discovery',
       """Original five- and 21-session issue performance is evaluated separately from updates. The reference table keeps V8 residualized rotation, V11 official breadth, V12 phase-zero risk rescaling, V13 all-phase IV mixtures, V14 weekly probability shrinkage, V14 domestic location plus GJR dispersion, and neutral/historical controls. Archived earlier relationships are compared on the common origin dates specific to each reference, so historical availability and subset sizes remain visible. V15 tests pure location replacement at fixed IV, pure fitted-risk scale at zero drift, scale plus trained location, moment-matched empirical asymmetry, a conditional sign-and-magnitude law, and probability shrinkage. Those pieces estimate different features of a forecast.""",
       '## Issue-time endpoints across vintages\n\n'+md_table(selected,['horizon','version','model','origins','p_up','brier','log_loss','endpoint_crps','balanced_accuracy']),
       '## Issue-time mechanism decomposition\n\n'+md_table(z[z.checkpoint.eq(0)].sort_values(['horizon','brier']),
                       ['horizon','model','n','p','brier','log_loss','crps','pinball']),
       '## Standalone probability shrinkage\n\n'+md_table(prob[prob.checkpoint.isin([0,1,4,20])],['horizon','checkpoint','model','n','brier','log_loss']),
       '## Updated whole and remaining endpoint scores\n\n'+md_table(post,['horizon','checkpoint','model','n','brier','endpoint_crps','remaining_brier','remaining_return_crps']),
       """When the realized price moves far from S₀, the original-window final sign often becomes easier for every model. The remaining direction Brier and CRPS isolate the unresolved component around Sₜ. Under a price-anchored sign threshold, dispersion and asymmetry can change probabilities even when the mean remains similar. The exact neutral, zero-return, and price-only rows serve different purposes and retain individual score columns.""",
       links(('All original references on common origins','cross-vintage-endpoint-leaderboard.csv'),
         ('All endpoint mechanism forecasts','endpoint-mechanism-scores.csv.gz'),('Search-adjusted issue comparisons','cross-vintage-matched-uncertainty.csv'),
         ('Same-time remaining-return comparisons','matched-window-evidence.csv')))
    v=csv('volatility-level-evidence.csv')
    vp=csv('volatility-transition-evidence.csv')
    p=csv('passage-leaderboard.csv')
    early=top(ref[ref.origins.ge(ref.horizon.map({5:265,21:217}))],['horizon'],'brier',4)
    late=top(ref[ref.origins.ge(ref.horizon.map({5:265,21:217}))],['horizon'],'endpoint_crps',4)
    rd=top(r[r.checkpoint.eq(0)&~r.model.eq('zero_remaining')],['horizon'],'range_crps',4)
    q=pd.concat([top(v,['horizon'],'mae',3),top(v,['horizon'],'qlike',3)]).drop_duplicates(['horizon','model'])
    passage=top(p[p.stage.eq('updated') & p.group.eq('all surviving')&~p.model.eq('zero_remaining')],['horizon'],'integrated_brier',5)
    touch=top(p[p.stage.eq('issue')&p.group.eq('fixed thresholds')&~p.model.eq('zero_remaining')],['horizon'],'brier',5)
    foc=m[m.checkpoint.eq('updated')&m.metric.isin(['endpoint_crps','remaining_return_crps','brier','remaining_brier'])&m.reference.eq('iv_restart')]
    foc=top(foc,['horizon','metric'],'model',4)
    cal=top(r[r.checkpoint.eq(0)&~r.model.eq('zero_remaining')],['horizon'],'endpoint_is80',5)
    report('COMPLETE_MODEL_COMPARISON','V15 objective-by-objective comparison',
       """The comparisons below use the frozen research-exposed sample. Each row is a specific target, model and support. Reading each objective separately preserves the distinct winners. Metric-specific origin counts and cross-vintage exact matching are in the linked artifacts. Gain in paired tables is control loss minus candidate loss. The normalized multivariate energy score, coverage, calibration, mean forecasts, mean biases, and per-origin distribution metrics are available in the larger tables.""",
       '## Original weekly and monthly direction\n\n'+md_table(early,['horizon','model','origins','brier','log_loss','correct','balanced_accuracy']),
       '## Original weekly and monthly return distributions\n\n'+md_table(late,['horizon','model','origins','endpoint_crps','endpoint_pinball','endpoint_mae','endpoint_cov80','endpoint_width80']),
       '## Volatility levels and expansion\n\n'+md_table(q,['horizon','model','n','mae','qlike'])+'\n\n'+
          md_table(top(vp[vp.event.eq('expand')],['horizon'],'brier',4),['horizon','model','n','brier','log_loss','p','actual_rate']),
       '## Trading ranges and coherent joint scores\n\n'+md_table(rd,['horizon','model','origins','range_crps','range_cov80','range_width80','range_is80','joint_energy']),
       '## Barrier touch at issue\n\n'+md_table(touch,['horizon','model','origins','n','brier','log_loss','integrated_brier'] if 'log_loss' in touch else ['horizon','model','origins','n','brier','integrated_brier','passage_log_loss']),
       '## First passage during updates\n\n'+md_table(passage,['horizon','model','origins','n','brier','integrated_brier','passage_log_loss']),
       '## Fixed-endpoint and sequential gain on matched windows\n\n'+md_table(foc,['horizon','metric','candidate','n','model','control','gain','family_low21','family_high21']),
       '## Interval calibration at original issue\n\n'+md_table(cal,['horizon','model','n','endpoint_cov50','endpoint_cov80','endpoint_width80','endpoint_pinball','endpoint_is80']),
       links(('Incremental block comparison','V15_INCREMENTAL_INFORMATION_VALUE.md'),('Disjoint phases and adjusted uncertainty','V15_EPISODE_LEVEL_EVALUATION.md'),
          ('Volatility transitions','V15_VOLATILITY_EXPANSION_INTELLIGENCE.md'),('Calibration, raw and joint losses','checkpoint-leaderboard.csv'),
          ('Full cross-vintage comparison','cross-vintage-endpoint-leaderboard.csv'),('All first-passage comparisons','passage-leaderboard.csv')))


def evidence_and_validation():
    out=csv('original-windows.csv')
    extremes=csv('extreme-event-frequency.csv',V14)
    ex=extremes[extremes.cohort.eq('combined')&extremes.event.isin(['upper_fixed','lower_fixed','range_fixed','gap_fixed','persist_up','persist_down','expand'])]
    head=[]
    for h,z in out.groupby('horizon'):
        z=z.sort_values('target')
        end='';j=0
        for u in z.itertuples(index=False):
            if u.origin>=end:
                j+=1
                end=u.target
        head.append(dict(horizon=h,rolling=z.origin.nunique(),fixed_targets=z.target.nunique(),greedily_disjoint=j,
                         early=int(z.cohort.eq('early').sum()),later=int(z.cohort.eq('later').sum()),updates=len(z)*h,
                         calendar_match=int(z.literal_calendar.sum())))
    p=csv('disjoint-phase-evidence.csv')
    p=p[p.reference.eq('iv_restart')&p.candidate.isin(['refit','incremental','vol_state','domestic','analogue'])&p.metric.isin(['brier','range_crps'])]
    p['positive']=p.gain.gt(0)
    pg=p.groupby(['horizon','checkpoint','candidate','metric'],as_index=False).agg(phases=('phase','nunique'),
                smallest_n=('n','min'),largest_n=('n','max'),positive_phases=('positive','sum'),worst_gain=('gain','min'),best_gain=('gain','max'))
    j=csv('leave-group-out-evidence.csv')
    j=j[j.reference.eq('iv_restart')&j.candidate.isin(['refit','incremental','vol_state','analogue'])&j.metric.isin(['brier','range_crps'])]
    jj=j.groupby(['horizon','checkpoint','candidate','metric','deletion_type'],as_index=False).agg(
          exclusions=('gain','size'),gain_min=('gain','min'),gain_max=('gain','max'))
    f=csv('refit-reselection-evidence.csv')
    c=read('validation-receipt.json')
    report('EPISODE_LEVEL_EVALUATION','V15 market-window and episode evidence',
        """Chronological origin and unique fixed endpoint counts describe forecast coverage. After aligning matched methods at the exact checkpoint, the comparison collapses updates within each original window. Fixed-date groups retain the target's shared realized value. Phase-indexed disjoint comparisons use calendar/trading order and label windows (origin, target]. Resampling uses 1,500 paired circular block draws at lengths of 5, 10, 21 and 42 original windows. At 10 and 21, bands use the maximum absolute standardized bootstrap deviation inside the registered comparison family, metric and checkpoint. Fixed-date clusters, disjoint calendar buckets, paired source cohorts and leave-month/event-out results quantify sensitivity. The benchmark history through V14 remains exposed.""",
        '## Dependence units\n\n'+md_table(pd.DataFrame(head),['horizon','rolling','fixed_targets','greedily_disjoint','early','later','updates','calendar_match']),
        '## Distinct extreme episodes\n\n'+md_table(ex,['horizon','event','eligible','count','distinct_episodes','positive_disjoint','eligible_disjoint']),
        '## Disjoint phase sensitivity\n\n'+md_table(pg,['horizon','checkpoint','candidate','metric','phases','smallest_n','largest_n','positive_phases','worst_gain','best_gain']),
        '## Deleting target months and overlapping extreme episodes\n\n'+md_table(jj,['horizon','checkpoint','candidate','metric','deletion_type','exclusions','gain_min','gain_max']),
        links(('Complete original windows','original-windows.csv'),('Per-endpoint and grouped scores','endpoint-cluster-evidence.csv.gz'),
              ('All phases','disjoint-phase-evidence.csv'),('All deletions','leave-group-out-evidence.csv'),
              ('Dependence-aware comparisons','matched-window-evidence.csv'),('V14 independent episode definitions','../../../nifty_forecast_v14/2026-11-25/run-001/distinct-extreme-episodes.csv')))
    report('VALIDATION_AND_FALSIFICATION','V15 chronology and falsification',
        f"""Verified **{c['forecast_windows']:,}** archived fixed windows, **{c['fixed_target_identity']:,}** cutoff/target identities, **{c['updated_joint_laws']:,}** updated joint laws, **{c['fitted_ledger_checks']:,}** fit receipts, **{c['strict_option_source_rows']:,}** tenor-availability rows and **{c['order_rows']:,}** order rows. {c['checked_shapes']:,} sampled saved laws independently passed shape, price positivity and OHLC bounds after all laws were checked at generation. The archive check verified {c['immutable_frozen_files_hashed']:,} distinct immutable V14 scenario files plus SHA-256 for every V15 joint archive. {c['predecessor_protection']['files']:,} predecessor file hashes match. The valid scope starts in 2025. A fit's latest label end precedes the decision's cash as-of session. Training-only scales, medians, support deduplication and bootstrap pair matching all retain the same chronology.""",
        '## Sentinel tests\n\n'+md_table(pd.DataFrame(c['causal_future_and_copy_checks']),['horizon','checkpoint','asof','future_prices_and_inputs_changed',
                       'unobserved_historical_labels_and_paths_perturbed','trained_coefficients_identical','exact_clones_removed','archive_exact','total_model_laws_compared']),
        '## Block-shuffled refit and reselection\n\n'+md_table(f,['horizon','origins','refitted_draws','candidate_slots','selected_observed','null_max_mean','null_max_q95','monte_carlo_tail']),
        """The refit null permutes contiguous training blocks of the additional feature groups, refits standardized ridge slopes and reselects among four issue/update slots. It uses a 19-origin grid and 32 randomized fits per horizon. The Monte Carlo result is a diagnostic. Ordinary paired intervals, sensitivity to block length, dependency and selection-adjusted bands retain their own columns. Delayed, stale, randomized and noisy update models use the original as-of baseline. Exact-copy invariance is checked after perturbing unavailable historical targets, market features, maturities and future cash observations. The V15 search adjustments do not account for all choices across V1–V15.""",
        links(('Verification receipt','validation-receipt.json'),('Pre-score registration','registration.json'),('Immutable predecessor receipt','protected-receipt.json'),
              ('Refit null realized paths','refit-reselection-null.csv.gz'),('All first-passage shape and risk set counts','sequential-score-counts.json')))


def forward_report():
    f=read('forward-ledger.json')
    outcomes=pd.DataFrame(f['sessions'])
    items=pd.DataFrame(f['records'])
    items['completed']=items.completed_target_dates.str.len()
    items['slot']=items.apply(lambda r:r.key if r.version=='V5' else f'V4 {r.horizon}-session late diagnostic',axis=1)
    issues=items[['version','slot','horizon','issued','reference_session','reference_close','target','completed','maturity','realized_return']]
    maturity=[]
    for a in f['records']:
        for m,z in a['scores'].items():
            maturity.append(dict(version=a['version'],slot=a['key'],target=a['target'],model=m,**z))
    extra='## Resolved model scores\n\n'+md_table(pd.DataFrame(maturity),['version','slot','target','model','p','brier','crps','log_loss','mae']) if maturity else None
    report('FORWARD_RESEARCH_LEDGER','V15 immutable forward research ledger',
       f"""At **{f['checked_at']}** the independent refresh matched **{len(outcomes)}** completed NIFTY 50 sessions from authenticated Upstox and the official NSE daily index archive. The historical November 17 vintage is preserved as a separate replay. NSE and Upstox values matched exactly at the verified closing marks. The refresh also archives India VIX, NIFTY Bank and NIFTY 500 payloads separately. November 24 is an NSE trading holiday. The expected publication guard is 18:00 IST on the original target date, followed by reconciliation of the complete originally named session sequence.""",
       '## Reconciled closes after the historical freeze\n\n'+md_table(outcomes,['day','upstox_open','upstox_high','upstox_low','upstox_close','nse_close','delta','status']),
       '## Original immutable target slots\n\n'+md_table(issues,['version','slot','horizon','issued','reference_session','reference_close','target','completed','maturity','realized_return']),
       extra,
       """V4 issued after the first target session began and qualifies as a late diagnostic. V5 preserved four experimental laws before its first target session opened. V15 resolves each original forecast only after its own endpoint is published with the original session list intact. The November 18 V4 issue chain and V5 frozen issue file retain their original hashes. The V15 October path case is historical, and this ledger tracks the immutable preexisting V4 and V5 submissions.""",
       links(('Authenticated refresh, chain hashes and original forecast probabilities','forward-ledger.json'),
         ('NSE 2026 trading holidays','https://archives.nseindia.com/content/circulars/CMTR71775.pdf')))


def architecture():
    cal=csv('update-calendar.csv')
    counts=read('sequential-score-counts.json')
    report('EXPERIMENTAL_FORECAST_ARCHITECTURE','V15 experimental forecast architecture',
      f"""The research pipeline stores {len(cal):,} historical decision records, {counts['scores']:,} per-law score rows and {counts['passage']:,} eligible first-passage rows. A fixed forecast holds the same outcome and original reference price until maturity. Data alignment and observation, the mathematical distribution, falsification and validation are independently reproducible stages. Decisions preserve timestamps and input revisions.""",
      """1. Market state pulls the verified latest cash return, official equal-weight breadth, rotations, liquidity, option-implied levels and international risk observations through the availability audit.
2. The endpoint layer preserves the strongest prior forecasts and produces new same-time restarted, directional shrinkage, normalized return-location and full fitted laws.
3. The volatility layer experiments with earlier ATM IV, forecast tenor, same-horizon history, GJR states, anchored hybrids, EGARCH references and transition recalibration.
4. The conditional path layer joins observed OHLC to complete forecast suffixes, then calculates the endpoint, risk, range, extrema, drawdown, rebound and touch outcomes on the same atoms.
5. The updating layer includes immutable, price-only, risk-only, domestic, full, partial-observation, particle, analogue and lagged/permuted/noisy controls.
6. Scenario research archives explicit price paths, assumptions and case similarity scores independently of forecast weights.
7. Evidence records matched and adjusted skill, data sufficiency, known outcomes, clock receipts, benchmark support and dependence-sensitive uncertainty.""",
      """The integrated objects are the 25 new joint OHLC laws per decision and the original frozen V14 joint baseline. Standalone event probabilities, earlier standalone endpoint laws, probability blends, separate point risk fits and the scenario envelope have distinct sources and evaluation. The evidence favors method selection by target where gains survive common-coverage and dependence checks. Model selection in the historical archive remains research-exposed.""",
      links(('Pre-score joint registrations','registration.json'),('Decision and target ledger','update-calendar.csv'),('Law archive','joint-update-archive.json'),
            ('Fitted model receipts','fitted-update-models.ndjson.gz'),('Validation receipts','validation-receipt.json')))


def conclusions():
    lead=csv('checkpoint-leaderboard.csv')
    paths=csv('passage-matched-risk-sets.csv')
    m=csv('matched-window-evidence.csv')
    iv=csv('volatility-transition-evidence.csv')
    vq=csv('secondary-paired-evidence.csv')
    iq=csv('session-dependence-evidence.csv')
    tide=one(iq,checkpoint='pre_open',target='immediate_open',metric='brier',model='offshore_fresh')
    prior=csv('replay-endpoint.csv').groupby('horizon')[['brier','crps']].mean()
    path_ref=csv('replay-path.csv')
    monthly_prior_crps=path_ref[path_ref.horizon.eq(21)&path_ref.target.eq('endpoint_return')].crps.mean()
    frames=[]; rev=[]; good=[]
    for h in HORIZONS:
        choice=lead[lead.horizon.eq(h)&lead.checkpoint.eq(0)&~lead.model.isin(['frozen','zero_remaining','full_delayed','full_noise','full_permuted',
                         'full_stale_surface','full_stale_global','domestic_stale'])]
        direction=choice.loc[choice.brier.idxmin()]
        cdf=choice.loc[choice.endpoint_crps.idxmin()]
        frames.append(dict(horizon=h,original_brier_model=direction.model,original_brier=direction.brier,
                   protected_v14_brier=prior.at[h,'brier'],original_crps_model=cdf.model,original_crps=cdf.endpoint_crps,
                   protected_v14_crps=prior.at[h,'crps'] if h==5 else monthly_prior_crps))
        for k in ([0,4] if h==5 else [0,20]):
            px=one(lead,horizon=h,checkpoint=k,model='iv_restart')
            pr=one(lead,horizon=h,checkpoint=k,model='price_only')
            fr=one(lead,horizon=h,checkpoint=k,model='frozen')
            rev.append(dict(horizon=h,checkpoint=k,frozen_brier=fr.brier,price_only_brier=pr.brier,raw_iv_brier=px.brier,
                            raw_iv_remaining_brier=px.remaining_brier,raw_iv_remaining_crps=px.remaining_return_crps))
        z=iv[iv.horizon.eq(h)&iv.event.eq('expand')]
        best=z.loc[z.brier.idxmin()]
        base=one(z,model='iv_raw')
        hist=one(z,model='historical')
        uq=one(vq,category='expansion',horizon=h,event='expand',model=best.model) if best.model!='iv_raw' else None
        row=dict(horizon=h,historical_brier=hist.brier,raw_iv_brier=base.brier,best_brier=best.brier,best_model=best.model,
                 best_log_loss=best.log_loss,raw_iv_log_loss=base.log_loss,raw_iv_gain=base.brier-best.brier,
                 family_low21=uq.family_low21 if uq is not None else 0.,family_high21=uq.family_high21 if uq is not None else 0.)
        good.append(row)
    p=paths[paths.group.eq('all surviving')&paths.reference.eq('iv_restart')&paths.metric.eq('integrated_brier')]
    path=top(p,['horizon'],'candidate_loss',2)
    risk=top(m[m.checkpoint.eq('updated') & m.reference.eq('iv_restart')&m.metric.isin(['brier','remaining_return_crps','range_crps','vol_mae'])],
             ['horizon','metric'],'model',2)
    report('FINAL_RESEARCH_CONCLUSIONS','V15 research conclusions',
       f"""Forecasts improved as newly realized price moved the current anchor toward the original endpoint. The most consistent evidence is for updating what is already known and for explicitly targeting risk. Additional regressions must improve the same-time control. Direction, residual returns, volatility, range, and time-to-event conclusions answer separate questions, with monthly inference constrained by **11** greedily disjoint windows. At weekly issue, the delayed-plus-noise placebo scored Brier 0.246351, ahead of the best substantive new weekly model. No independent directional edge is established by the frozen 2025–2026 replay.""",
       '## Original weekly and monthly direction and CRPS\n\n'+md_table(pd.DataFrame(frames),['horizon','original_brier_model','original_brier','protected_v14_brier',
                         'original_crps_model','original_crps','protected_v14_crps']),
       '## Mechanical progress versus prediction of the remaining return\n\n'+md_table(pd.DataFrame(rev),['horizon','checkpoint','frozen_brier','price_only_brier',
                         'raw_iv_brier','raw_iv_remaining_brier','raw_iv_remaining_crps']),
       '## 25% expansion and honest same-vintage controls\n\n'+md_table(pd.DataFrame(good),['horizon','historical_brier','raw_iv_brier','best_model','best_brier','raw_iv_log_loss',
                         'best_log_loss','raw_iv_gain','family_low21','family_high21']),
       f"""The clearest timestamp-specific return result was the immediate NIFTY opening gap. On {tide.n} common mornings, the offshore block moved Brier from {tide.parent_score:.6f} to {tide.score:.6f}. The 21-session family interval for this gain was [{tide.family_low21:.6f}, {tide.family_high21:.6f}]. This is a distinct intraday target and diagnostic reconstruction with conservative release assumptions. Sector, breadth, derivatives and foreign revisions produce varying results at the original endpoint. Same-time changes to risky paths can help range, risk, and timing scores without enhancing the original directional probability.""",
       '## Best post-issue matched point estimates and uncertainty\n\n'+md_table(risk,['horizon','metric','candidate','n','model','control','gain','family_low21','family_high21']),
       '## Surviving first-passage time forecasts\n\n'+md_table(path,['horizon','candidate','n','origins','candidate_loss','reference_loss','average_episode_gain','family_low21','family_high21']),
       """The historical error casebook and scenario tests map important failure modes and the limited independent tail evidence. The same-target replay and conditional path tools are reproducible, with separated point-risk, event, joint path and standalone endpoint evidence. Further prospectively timestamped comparisons are the required test for realized research gains.""",
       links(('Complete model comparison','V15_COMPLETE_MODEL_COMPARISON.md'),('Episode sensitivity','V15_EPISODE_LEVEL_EVALUATION.md'),
             ('Immutable forward ledger','V15_FORWARD_RESEARCH_LEDGER.md'),('Historical illustrative case','historical-fixed-endpoint-updates.png')))
    report('NEXT_EXPERIMENTS','V15 next experiments',
       """1. Register a prospective shadow comparison of frozen, price-only, fresh IV and GJR paths at original issue and a small set of fixed target checkpoints. Score all matured archived forecasts and accumulate disjoint outcome weeks.
2. Test weekly raw-IV and the fixed IV/RV event mapping on the same authenticated option-tenor support. Test monthly GJR/EGARCH contraction, expansion and high-risk persistence with the existing chronological probability rules. Retain log-loss and calibration alongside Brier.
3. Freeze the offshore opening-gap comparison. Archive actual release timestamps and sampled foreign holidays for point-in-time checks. Recheck direction of the pre-open gap and its calibration independently of weekly or monthly prediction.
4. Collect genuinely timestamped intraday option books and breadth before revisiting their contribution to midday revisions. Compare same-contract revisions, trade filters and stale marks.
5. Preserve one range and one passage path model plus a simple restart. Audit opposite-barrier timing and conditional exposure after actual hits, using only historical survivors at each step.
6. Stress test unusual scenarios with overlapping extremes grouped by common episode. Keep late or incomplete forward records distinct and retain all frozen issues and their model specifications.""",
       links(('Forward maturity and outcome receipts','V15_FORWARD_RESEARCH_LEDGER.md'),('Research limits','V15_FINAL_RESEARCH_CONCLUSIONS.md')))


def index():
    names=[]
    order=('REPRODUCTION_AND_BASELINES','FIXED_ENDPOINT_FORECASTING','INCREMENTAL_INFORMATION_VALUE','FORECAST_REVISION_MODELS',
           'INFORMATION_TIMING_AND_SESSIONS','SHOCK_VERSUS_PERSISTENCE','CONDITIONAL_PATH_UPDATING','VOLATILITY_EXPANSION_INTELLIGENCE',
           'CAUSAL_FORECAST_ERROR_LEARNING','EXTREME_RISK_AND_SCENARIO_INTELLIGENCE','SEQUENTIAL_FIRST_PASSAGE',
           'DIRECTIONAL_FORECAST_DISCOVERY','ADDITIONAL_MARKET_INFORMATION','EPISODE_LEVEL_EVALUATION',
           'EXPERIMENTAL_FORECAST_ARCHITECTURE','VALIDATION_AND_FALSIFICATION','COMPLETE_MODEL_COMPARISON',
           'FORWARD_RESEARCH_LEDGER','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS')
    for name in order:
        f=OUT/f'V15_{name}.md'
        title=f.read_text(encoding='utf-8').splitlines()[0].removeprefix('# ')
        names.append(f'- [{title}]({f.name})')
    (OUT/'NIFTY_V15_RESEARCH.md').write_text(f"""# NIFTY V15 research

The historical research freeze is **{FREEZE}**. The archive contains **265 five-session** and **217 21-session** windows, with **5,882** original and subsequent cutoff states. Each update preserves the original terminal outcome and cash reference. Same-time comparisons and direction, path and risk scoreboards are evaluated separately.

[Research conclusions](V15_FINAL_RESEARCH_CONCLUSIONS.md) · [Complete scoreboard](V15_COMPLETE_MODEL_COMPARISON.md) · [Historical fixed-endpoint chart](historical-fixed-endpoint-updates.png) · [Forward maturity](V15_FORWARD_RESEARCH_LEDGER.md)

## Required reports

{chr(10).join(names)}

## Reproduction and archive

[Reproduction commands](README.md) · [Registered specifications](registration.json) · [Original mission](MISSION.md) · [Validation](validation-receipt.json) · [Hashes](manifest.json)
""",encoding='utf-8')
    story="""# Reproduce V15

Run from the trading-desk repository in PowerShell with the existing Python environment and archived market sources. The authenticated acquisition commands expect the read-only Upstox access already configured by the workspace. The protected archive manifests are read-only. Sources and results remain inside this V15 run. To replay into an isolated run, set NIFTY_V15_OUT under artifacts/nifty_forecast_v15 first and copy the mission to that run.

"""
    modules=['replay scores','replay protect','sources intraday','sources forward','data','sequential','scores','sessions',
             'volatility','forensics','mechanisms','mechanical','evidence','comparisons','demo','verify','report','delivery']
    commands=chr(10).join('.venv/Scripts/python.exe -m research.nifty_forecast_v15.'+m for m in modules)
    story+=chr(96)*3+'powershell\n'+"$env:OPENBLAS_NUM_THREADS='1'\n$env:PYTHONDONTWRITEBYTECODE='1'\n"+commands+chr(10)+chr(96)*3+chr(10)
    story+="""
The main score job evaluates all forecast checkpoints and eligible barrier survivors. Path archives store integer log OHLC ratios against the latest cash close. Reconstruct each updated joint law by converting the ticks using the manifest scale and multiplying by the cash-anchor ratio, then prepending the realized OHLC history from the original issue. The frozen law uses the immutable prior NPZ and the model key recorded in every per-window receipt. Some weak and earlier systems have shorter support. Interpret metrics from common-origin comparisons and refer to the checkpoint codes for the corresponding remaining horizon.

Archived research definitions retain the exact 2025–2026 domain and the November 17 frozen timeline. The additional completed-session refresh is timestamped separately and can be run again without changing the historical evidence. Prospective score status derives from the original issue, original session list and authoritative outcome.
"""
    (OUT/'README.md').write_text(story,encoding='utf-8')


def run():
    from .mechanisms import auxiliary
    auxiliary()
    reproduction()
    session_layers()
    vol_transitions()
    forensics()
    fixed_and_information()
    revision_and_shock()
    paths_and_passage()
    direction_and_comparison()
    evidence_and_validation()
    architecture()
    forward_report()
    conclusions()
    index()
    print('Wrote all 20 research reports and the reproducible index',flush=True)


if __name__=='__main__':
    run()
