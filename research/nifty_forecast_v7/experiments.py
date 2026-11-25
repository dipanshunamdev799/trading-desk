"""Bounded research batches with one common chronological score harness."""
import warnings
import joblib
from .common import *
from .models import fit, location, laws, Distribution
from .features import LEVELS, CHANGE_BASE
from .reproduce import references
from research.nifty_forecast_v6.analyze import benchmark_frames
from research.nifty_forecast_v3.experiment import available, inner_split


def spec(parent='C_RAW', frame='native', **kwargs):
    return {'parent':parent,'frame':frame,**kwargs}


COMPRESSION = {
    'C_RAW':spec('I03_nosize', hypothesis='Reproduce raw native ridge in V7 engine'),
    'C_DEF':spec(rep='defensive', hypothesis='Downweight six correlated defensive features'),
    'C_BANK_DEF':spec('C_DEF',rep='defense_banks',hypothesis='Also downweight overlapping banks and financial services proxies'),
    'C_NO_DEF':spec(frame='nodef',hypothesis='Remove defensive family completely'),
    'C_DUP':spec(rep='duplicate',diagnostic=True,hypothesis='Add exact copies of six defensive inputs to change Ridge penalty'),
    'C_DUP_BALANCED':spec(rep='duplicate_balanced',diagnostic=True,hypothesis='Normalize each original and its clone by sqrt(2) to restore the original fitted law'),
    'C_PRUNE':spec(rep='prune',hypothesis='Greedy removal above absolute training correlation .90'),
    'C_REPRESENT':spec(rep='representative',hypothesis='Average linkage at .75 similarity and retain cluster medoid'),
    'C_CLUSTER_MEAN':spec(rep='cluster_mean',hypothesis='Sign aligned equal-weight averages on training clusters'),
    'C_CLUSTER_BAL':spec(rep='cluster_balance',hypothesis='Keep features and scale by inverse square root of cluster size'),
    'C_FACTOR_GROUPS':spec(rep='factor_groups',hypothesis='Aggregate fixed economic groups with training sign alignment'),
    'C_PCA':spec(rep='pca',hypothesis='Retain six components of relative-return block with original variance scale'),
    'C_PCA_WHITE':spec('C_PCA',rep='pca_white',hypothesis='Whiten retained PCA eigenvalues'),
    'C_PCA_LW':spec('C_PCA_WHITE',rep='pca_lw',hypothesis='Use Ledoit-Wolf shrunk eigenvalues for whitening'),
    'C_PCA_ROLL':spec('C_PCA',rep='pca_roll',hypothesis='Estimate factor directions on last126 training observations'),
    'C_SPARSE':spec('C_PCA',rep='sparse_pca',hypothesis='Six sparse components with regularized projection'),
    'C_GROUP_LASSO':spec(kind='group_lasso',hypothesis='Group norm penalty plus L2 by economic family'),
    'C_ELASTIC':spec('C_CLUSTER_BAL',rep='cluster_balance',kind='elastic',hypothesis='Soft sparsity with correlated feature groups balanced'),
}

STRUCTURE = {
    'S_SIMPLE':spec('C_NO_DEF','simple',hypothesis='Synchronization and dispersion beyond best V6 Brier representation'),
    'S_NETWORK':spec('C_NO_DEF','network',hypothesis='Spectral rank and network density beyond the V6 Brier representation'),
    'S_LEADERSHIP':spec('C_NO_DEF','leadership',hypothesis='Leadership ranks and breadth beyond V6 Brier representation'),
    'S_LEVEL':spec('C_NO_DEF','level',hypothesis='Prespecified six levels used in the state experiment'),
    'S_STATE':spec('S_LEVEL','state',hypothesis='Changes, normalized state hazard and loading drift beyond corresponding levels'),
    'S_STATE_LAG':spec('S_LEVEL','state_lag',diagnostic=True,hypothesis='Replace current changes with 5-session lag placebo'),
    'S_STATE_ACCEL':spec('S_LEVEL','state_accel',hypothesis='Acceleration alone compared with the identical levels parent'),
    'S_ROTATION':spec('C_NO_DEF','rotation',hypothesis='Financial, defensive and liquidity rotation under global changes'),
}

ADVANCED = {
    'A_BAL_RIDGE':spec(rep='cluster_balance',alpha=300,hypothesis='Stronger penalty with cluster normalization'),
    'A_PCA_BAYES':spec('C_PCA_WHITE',rep='pca_white',kind='bayes',hypothesis='Bayesian coefficient shrinkage on compressed inputs'),
    'A_PCA_HUBER':spec('C_PCA_WHITE',rep='pca_white',kind='huber',hypothesis='Robust conditional location on compressed inputs'),
    'A_PCA_GAM':spec('C_PCA_WHITE',rep='pca_white',kind='gam',hypothesis='Regularized quadratic spline basis'),
    'A_PCA_FOREST':spec('C_PCA_WHITE',rep='pca_white',kind='forest',hypothesis='Shallow forest on compressed location inputs'),
    'A_PCA_BOOST':spec('C_PCA_WHITE',rep='pca_white',kind='boost',hypothesis='Shallow histogram boosting on compressed inputs'),
    'A_PCA_RESID':spec('C_PCA_WHITE',rep='pca_white',kind='residual_boost',hypothesis='Fit a shrunk nonlinear correction to factor Ridge residuals'),
    'A_PCA_EXPERTS':spec('C_PCA_WHITE',rep='pca_white',kind='experts',hypothesis='Shrink volatility experts toward pooled model'),
    'A_PCA_INTERACT':spec('C_PCA_WHITE',rep='pca_white',kind='interaction',hypothesis='Two fixed low-dimensional interactions'),
}

DISTRIBUTIONS = {
    'D_SPARSE':spec('C_NO_DEF','nodef',law='student',hypothesis='Student df5 law on the strongest V6 Brier representation'),
    'D_RISK':spec('C_NO_DEF','nodef',law='risk_scaled',hypothesis='Scale residuals with current trailing risk relative to past validation risk'),
    'D_QUANTILE':spec('C_PCA_WHITE',rep='pca_white',law='quantile',hypothesis='Fit five direct quantiles in compressed design'),
    'D_ETF_STUDENT':spec('V6_CRPS','noauto_volume',law='student',hypothesis='Student regularization of V6 distribution lead input set'),
}

LIQUIDITY = {
    'L_ETF':spec('C_NO_DEF','nodef_etf',hypothesis='Add five genuine ETF volume ratios without defensive duplication'),
    'L_DAILY':spec('C_NO_DEF','daily',hypothesis='Opening versus closing behavior and ETF activity change from the same historical sessions'),
    'L_POSITION':spec('C_NO_DEF','position',hypothesis='Lagged archive futures basis/OI and options positioning'),
    'L_INTRADAY_BASE':spec('C_NO_DEF','nodef',eligible='intraday',hypothesis='Identical date availability as complete-session intraday treatment'),
    'L_INTRADAY':spec('L_INTRADAY_BASE','intraday',eligible='intraday',hypothesis='Complete-session intraday volatility and opening/closing behavior'),
    'L_STOCK_PROXY':spec('C_NO_DEF','stock',diagnostic=True,hypothesis='Current liquid-stock basket sensitivity with survivorship exposure'),
}

FALSIFICATION = {
    'F_DEF126':spec('C_DEF',rep='defensive',window=126,hypothesis='Shorter training history'),
    'F_DEF189':spec('C_DEF',rep='defensive',window=189,hypothesis='Intermediate training history'),
    'F_DEF_EMBARGO':spec('C_DEF',rep='defensive',embargo=3,hypothesis='Move outer and inner endpoint cutoffs three observed sessions earlier'),
    'F_DEF_JOINT':spec('C_DEF','joint_perturb',rep='defensive',hypothesis='One common five-percent correlated-feature scale perturbation at query time'),
    'F_DEF_LAG':spec('C_DEF','def_lag',rep='defensive',hypothesis='Shift defensive block back one trading session'),
    'F_NO_BANKS':spec('C_DEF','nobanks',rep='defensive',hypothesis='Remove financial and banking group'),
    'F_NO_CYC':spec('C_DEF','nocycs',rep='defensive',hypothesis='Remove cyclical group'),
    'F_DEF_REV':spec('C_DEF','revision',rep='defensive',hypothesis='Synthetic one-basis-point sector source perturbation'),
    'F_LABEL_ROLL':spec('C_DEF',rep='defensive',roll_target=3,diagnostic=True,hypothesis='Circular training-target displacement of three horizons'),
    'M_STATE_BASE':spec('C_RAW','m_price',eligible='state',horizons=[21],hypothesis='Date matched price-only monthly control'),
    'M_STATE':spec('M_STATE_BASE','m_state',eligible='state',horizons=[21],hypothesis='Reconstruct V6 weekly-state mechanism, complete state cohort'),
    'M_STATE_LAG5':spec('M_STATE','m_lag5',eligible='state',horizons=[21],hypothesis='Causal five-session delayed weekly state'),
    'M_STATE_LAG21':spec('M_STATE','m_lag21',eligible='state',horizons=[21],hypothesis='Causal 21-session delayed weekly state'),
    'M_STATE_SHIFT5':spec('M_STATE','m_state',eligible='state',roll_state=5,diagnostic=True,horizons=[21],hypothesis='Training-only circular input-state roll by five'),
    'M_STATE_SHIFT21':spec('M_STATE','m_state',eligible='state',roll_state=21,diagnostic=True,horizons=[21],hypothesis='Training-only circular input-state roll by 21'),
    'M_STATE_126':spec('M_STATE','m_state',eligible='state',window=126,horizons=[21],hypothesis='Shorter monthly state training'),
    'M_PERSIST':spec('C_NO_DEF','persist',horizons=[21],hypothesis='Slow breadth/correlation/volatility factors and shrunk Student law',law='student'),
}


def all_frames():
    native,volume,defensive = references()
    struct = matrix('market-structure.csv',OUT);liq = matrix('liquidity.csv',OUT)
    intraday = matrix('intraday-features.csv',OUT).drop(columns='close_difference_points').reindex(native.index)
    glob = matrix('global-reference.csv')
    state = matrix('state-features.csv');low = native.drop(columns=defensive)
    price = native[['p_ret5','p_ret21','p_rv21','p_vix']]
    attach = lambda a, b: pd.concat([a,b],axis=1)
    levels = struct[CHANGE_BASE]
    dynamic = struct[[c+'_change5' for c in CHANGE_BASE]+['loading_drift','p_high_corr_next']]
    rotated = struct[['financial_spread','defensive_dispersion']].diff(5).assign(global_relative_change=glob.x_india_relative.diff(5),etf_activity_change=liq.l_etf_delta5)
    lag = native.copy();lag[defensive] = lag[defensive].shift()
    result = {'native':native,'nodef':low,'noauto_volume':attach(native.drop(columns='i_nifty_auto_rel21'),volume),
            'simple':attach(low,struct[['mean_corr','corr_dispersion','rv_sync']]),
            'network':attach(low,struct[['lambda_share','effective_rank','network_density','loading_drift']]),
            'leadership':attach(low,struct[['participation','concentration','leader_persistence','breadth_relative']]),
            'level':attach(low,levels),'state':attach(attach(low,levels),dynamic),
            'state_lag':attach(attach(low,levels),dynamic.shift(5)),
            'state_accel':attach(attach(low,levels),struct[[c+'_accel' for c in CHANGE_BASE]]),
            'rotation':attach(low,rotated),'persist':attach(low,struct[['participation_persist','correlation_persist','vol_sync_persist']]),
            'nodef_etf':attach(low,volume),'daily':attach(low,liq.filter(regex='^l_')),
            'position':attach(low,liq.filter(regex='^d_')),'intraday':attach(low,intraday),
            'stock':attach(low,liq[['proxy_dispersion','proxy_participation','proxy_volume']]),
            'm_price':price,'m_state':attach(price,state),'m_lag5':attach(price,state.shift(5)),
            'm_lag21':attach(price,state.shift(21)),'joint_perturb':native,'def_lag':lag,
            'revision':matrix('native-revision-1bp.csv',OUT)}
    from research.nifty_forecast_v6.forensics import GROUPS
    for name,group in [('nobanks','BANKS'),('nocycs','CYCLICAL')]:
        result[name]=native.drop(columns=[c for c in native if GROUPS[group](c)])
    eligibility = {'intraday':intraday.notna().all(axis=1),'state':state.notna().all(axis=1)&state.shift(21).notna().all(axis=1)}
    return result,eligibility


def score_row(h,fold,name,r,law,reference):
    s = law.stats(reference)
    y = r.realized_return
    return {'horizon':h,'fold':fold,'model':name,'origin':r.origin,'endpoint':r.endpoint,'regime':r.regime,
            'trend':r.trend,'global_risk':r.global_risk,'reference_close':reference,**law.score(y),**s['quantiles'],
            'expected_endpoint':s['expected_endpoint'],'median_endpoint':s['median_endpoint'],
            'expected_absolute_return':s['expected_absolute_return'],'magnitude_mae':abs(s['expected_absolute_return']-abs(y)),
            'expected_rv':None,'endpoint_std':s['endpoint_return_std'],'p_return_below_minus2':float(law.w[law.a<-.02].sum()),
            'p_abs_return_above_2':float(law.w[abs(law.a)>.02].sum())}


def evaluate(batch,specs,frames,eligibility):
    plan = OUT/f'{batch}-registry.json'
    if plan.exists():raise FileExistsError('Replay in a fresh directory')
    save(plan.name,{'registered_at':now(),'configurations':specs,'exposure':'2025–2026 historical research',
                    'fit_code_sha256':sha(SOURCE/'models.py'),'batch_code_sha256':sha(SOURCE/'experiments.py'),
                    'reason':'Fixed family tests registered before new results for this batch. All dates exposed by prior research.'})
    refs = benchmark_frames();price = matrix('price.csv');results=[];ledger=[]
    models_dir = OUT/'models';models_dir.mkdir(exist_ok=True)
    for h in sorted({h for s in specs.values() for h in s.get('horizons',[5,21])}):
        label = matrix(f'labels-{h}.csv')
        test = refs[21 if h in [10,15] else h,'I03_nosize'].reset_index()
        test['endpoint'] = label.loc[test.origin,'endpoint'].to_numpy()
        test['realized_return'] = label.loc[test.origin,'return'].to_numpy()
        for fold,group in test.groupby('fold'):
            for name,config in specs.items():
                if h not in config.get('horizons',[5,21]):continue
                record={'horizon':h,'fold':fold,'model':name,'batch':batch,'cutoff':group.origin.min()}
                rows=group
                try:
                    x=frames[config['frame']]
                    cutoff=group.origin.min();embargo=config.get('embargo',0)
                    train_cutoff=x.index[max(0,x.index.get_loc(cutoff)-embargo)]
                    dates=available(label,train_cutoff)
                    if 'eligible' in config:
                        mask=eligibility[config['eligible']];dates=dates[mask.loc[dates]];rows=group[mask.loc[group.origin].to_numpy()]
                    if len(dates)<100 or len(rows)==0:raise ValueError('Insufficient strictly eligible train/query observations')
                    inner,validation=inner_split(label,dates)
                    inner_cutoff=x.index[max(0,x.index.get_loc(validation[0])-embargo)]
                    inner=inner[label.loc[inner,'endpoint']<inner_cutoff]
                    if 'window' in config:
                        dates=dates[-config['window']:];inner=inner[-config['window']:]
                    if len(inner)<60:raise ValueError('Fewer than 60 purged inner fit observations')
                    assert label.loc[dates,'endpoint'].max()<train_cutoff and label.loc[inner,'endpoint'].max()<inner_cutoff
                    y=label.loc[dates,'return'].to_numpy();y_inner=label.loc[inner,'return'].to_numpy();y_val=label.loc[validation,'return'].to_numpy()
                    train=x.loc[dates].copy();train_inner=x.loc[inner].copy();query=x.loc[rows.origin].copy()
                    if 'roll_target' in config:
                        lag=config['roll_target']*h;y=np.roll(y,lag);y_inner=np.roll(y_inner,lag);y_val=np.roll(y_val,lag)
                    if 'roll_state' in config:
                        cols=[c for c in x if c.startswith('w_')];lag=config['roll_state'];train[cols]=np.roll(train[cols],lag,axis=0);train_inner[cols]=np.roll(train_inner[cols],lag,axis=0)
                    if config['frame']=='joint_perturb':
                        cols=references()[2];mean=train[cols].mean();query[cols]=mean+1.05*(query[cols]-mean)
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter('always')
                        inner_model=fit(config,train_inner,y_inner)
                        residual=y_val-location(inner_model,x.loc[validation])
                        model=fit(config,train,y)
                        forecast=laws(model,query,residual,x.loc[validation,'p_rv21'].to_numpy())
                    path=models_dir/f'{name}-{h}-{fold}.joblib'
                    joblib.dump({'model':model,'inner_model':inner_model,'training':list(dates),'inner':list(inner),
                                 'validation':list(validation),'residual':residual,'query':list(rows.origin)},path,compress=3)
                    scores=[score_row(h,fold,name,r,d,float(price.loc[r.origin,'close'])) for r,d in zip(rows.itertuples(),forecast)]
                    results.extend(scores)
                    record.update(status='ok',train_n=len(dates),inner_n=len(inner),query_n=len(scores),
                                  train_cutoff=train_cutoff,last_endpoint=label.loc[dates,'endpoint'].max(),
                                  inner_cutoff=inner_cutoff,inner_last_endpoint=label.loc[inner,'endpoint'].max(),
                                  input_features=model['transform'].shape[0],transformed_features=model['transform'].shape[1],
                                  artifact=str(path.relative_to(OUT)),sha256=sha(path),warnings=[str(w.message)[:250] for w in caught])
                except Exception as exc:
                    record.update(status='failed',reason=f'{type(exc).__name__}: {exc}')
                ledger.append(record)
            print(batch,h,fold,'rows',len(results),'failures',sum(r['status']=='failed' for r in ledger),flush=True)
    pd.DataFrame(results).to_csv(OUT/f'{batch}-predictions.csv',index=False)
    save(f'{batch}-ledger.json',ledger)


def run(only=None):
    frames,eligible=all_frames()
    for name,specs in [('compression',COMPRESSION),('structure',STRUCTURE),('distribution',DISTRIBUTIONS),
                       ('advanced',ADVANCED),('liquidity',LIQUIDITY),('falsification',FALSIFICATION),
                       ('intermediate',{k:{**v,'horizons':[10,15]} for k,v in {'H_NATIVE':C_REF,'H_PCA':COMPRESSION['C_PCA_WHITE'],'H_STATE':STRUCTURE['S_STATE'],'H_STUDENT':DISTRIBUTIONS['D_SPARSE']}.items()})]:
        if only is None or only==name:evaluate(name,specs,frames,eligible)


C_REF = COMPRESSION['C_NO_DEF']

if __name__=='__main__':
    import sys
    run(sys.argv[1] if len(sys.argv)>1 else None)
