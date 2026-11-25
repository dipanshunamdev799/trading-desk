"""Registered V8 experiments and shared chronological evaluation."""
import warnings
import joblib
from .common import *
from .models import fit, location, predict, Distribution
from research.nifty_forecast_v7.analyze import benchmarks
from research.nifty_forecast_v6.common import V3
from research.nifty_forecast_v3.experiment import available, inner_split


def spec(frame='base',parent='B_NATIVE',**settings):
    return {'frame':frame,'parent':parent,**settings}


GEOMETRY={
    'B_NATIVE':spec(hypothesis='V6 defensive deletion parent'),
    'B_FULL':spec('native','I03_nosize',hypothesis='Full 57-input native parent'),
    'B_ROT':spec('both_changes',hypothesis='Domestic rotation parent with fixed Ridge100'),
    'G_CANON':spec('native','B_FULL',dedup=True,hypothesis='Use a stable canonical column per equivalent affine history'),
    'G_CLUSTER':spec('native','G_CANON',dedup=True,rep='cluster',hypothesis='Balance normalized correlation-cluster weight'),
    'G_ELASTIC':spec('native','G_CLUSTER',dedup=True,rep='cluster',kind='elastic',hypothesis='Cluster-balanced Elastic Net'),
    'G_BAYES':spec('native','G_CLUSTER',dedup=True,rep='cluster_bayes',kind='bayes',hypothesis='Group-aware Gaussian coefficient shrinkage with learned common precision'),
    'G_HIERARCHICAL':spec('native','G_CLUSTER',dedup=True,rep='hierarchical',hypothesis='Compound correlation-cluster and economic family penalties'),
    'G_COV':spec('native','G_CANON',dedup=True,rep='covariance',hypothesis='Shrink coefficients along strongly correlated sector directions'),
    'G_RESID':spec('native','G_CANON',dedup=True,rep='factor_residual',hypothesis='Separate grouped factors and shrunk residuals'),
    'G_REPRESENT':spec('native','G_CANON',dedup=True,rep='representative',hypothesis='Within-cluster representative from centrality and train-only target association'),
    'G_ROT_CLUSTER':spec('both_changes','B_ROT',dedup=True,rep='cluster',hypothesis='Cluster scaling on rotation parent'),
    'G_ROT_COV':spec('both_changes','B_ROT',dedup=True,rep='covariance',hypothesis='Covariance penalty on rotation parent'),
    'G_ROT_ELASTIC':spec('both_changes','G_ROT_CLUSTER',dedup=True,rep='cluster',kind='elastic',hypothesis='Combine cluster-balanced Elastic Net with domestic rotation'),
}

ROTATIONS={
    'R_BANK':spec('bank_change',hypothesis='Bank-financial spread change alone'),
    'R_DEF':spec('def_change',hypothesis='Defensive-cyclical spread change alone'),
    'R_LEVEL':spec('levels',hypothesis='Original spread levels'),
    'R_LEVEL_CHANGE':spec('levels_changes','B_ROT',hypothesis='Add original levels to changes'),
    'R_RESIDUAL':spec('residual','B_ROT',hypothesis='Residualize spreads against NIFTY with lagged beta'),
    'R_NORMAL':spec('normalized','B_ROT',hypothesis='Scale changes by trailing spread volatility'),
    'R_SLOPE':spec('slopes','B_ROT',hypothesis='Smooth 10-session slope of each spread'),
    'R_ACCEL':spec('acceleration','B_ROT',hypothesis='Second five-session differences'),
    'R_SWITCH':spec('switch','B_ROT',hypothesis='Change in signs of relative leadership'),
    'R_EXTREME':spec('extremes','B_ROT',hypothesis='Large normalized changes defined by fixed 1.5 threshold'),
    'R_INTERACT':spec('interactions','B_ROT',hypothesis='Rotation dependence on bandwidth and volatility'),
    'R_LAG1':spec('lag1','B_ROT',hypothesis='One older observed session'),
    'R_LAG5':spec('lag5','B_ROT',hypothesis='Five-session delayed genuine domestic rotation'),
    'R_LAG10':spec('lag10','B_ROT',hypothesis='Ten-session delayed genuine rotation'),
    'R_SMOOTH':spec('average','B_ROT',hypothesis='Ten-session smoothed levels'),
    'R_WRAP':spec('both_changes','B_ROT',roll_group='r_',diagnostic=True,hypothesis='Train-only circular roll of two rotation inputs'),
}

LAW={
    'D_STUDENT':spec('both_changes','B_ROT',law='student',hypothesis='Shrink Student df5 scale toward historical risk'),
    'D_RISK':spec('both_changes','B_ROT',law='risk',hypothesis='State-dependent empirical residual weights by trailing volatility'),
    'D_FACTOR':spec('both_changes','B_ROT',law='factor',hypothesis='Pool residuals conditionally on rotation magnitude'),
    'D_QUANTILE':spec('both_changes','B_ROT',dedup=True,rep='cluster',law='quantile',hypothesis='Coherent interpolation of regularized conditional quantile estimates'),
    'D_ELASTIC_RISK':spec('native','G_ELASTIC',dedup=True,rep='cluster',kind='elastic',law='risk',hypothesis='Conditional residual scale on cluster balanced Elastic Net'),
}

ADDITIONS={
    'A_STRUCTURE_LEVEL':spec('structure_level','B_ROT',hypothesis='Economic state levels beyond rotation'),
    'A_STRUCTURE_CHANGE':spec('structure_change','A_STRUCTURE_LEVEL',hypothesis='Use changes jointly with the same original levels'),
    'A_PARTICIPATION':spec('participation','B_ROT',hypothesis='Broad index leadership, rank persistence and participation'),
    'A_RISK_STRUCTURE':spec('risk_structure','B_ROT',hypothesis='Sector correlation, volatility and asymmetry transitions'),
    'A_ETF_ACTIVITY':spec('etf_activity','B_ROT',hypothesis='Relative ETF turnover, volume shock and activity participation'),
    'A_ETF_EXPOSURE':spec('etf_exposure','A_ETF_ACTIVITY',hypothesis='ETF underlying spread and volatility or price impact proxy beyond activity'),
    'A_ETF_GATE':spec('etf_gate','A_ETF_ACTIVITY',hypothesis='Rotation intensity interacts with actual ETF activity'),
    'A_INTRADAY_BASE':spec('both_changes','B_ROT',eligible='intraday',hypothesis='Complete-session matched rotation parent'),
    'A_INTRADAY':spec('intra','A_INTRADAY_BASE',eligible='intraday',hypothesis='Opening, closing, reversal, path variance, asymmetry, range concentration'),
    'A_INTRADAY_STRICT_BASE':spec('both_changes','B_ROT',eligible='intra_strict',hypothesis='Matched parent excluding last-bar discrepancies beyond 10 bp'),
    'A_INTRADAY_STRICT':spec('intra','A_INTRADAY_STRICT_BASE',eligible='intra_strict',hypothesis='Intraday increment on 10-bp reconciliation subset'),
    'A_POSITION':spec('position','B_ROT',hypothesis='NSE lagged positioning beyond domestic rotation'),
    'A_NATIVE_PANEL':spec('panel','B_ROT',hypothesis='Aggregate sector-index common and residual components by date'),
    'A_STOCK_PROXY':spec('stock_proxy','B_ROT',diagnostic=True,hypothesis='Current-selected stock breadth/volume sensitivity'),
}

MONTHLY={
    'M_HIST':spec('m_price','E00',law='history',hypothesis='Mature state-eligible empirical sign frequency and full return law'),
    'M_PRICE':spec('m_price','M_HIST',hypothesis='Price and risk only'),
    'M_ONLY_STATE':spec('m_only_state','M_HIST',hypothesis='Current reconstructed weekly state without price predictors'),
    'M_BOTH':spec('m_both','M_PRICE',hypothesis='Current price and weekly state'),
    'M_LAG_STATE':spec('m_lag_state','M_BOTH',hypothesis='21-session lagged weekly state and current price'),
    'M_LAG_PRICE':spec('m_lag_price','M_BOTH',hypothesis='21-session lagged price and current weekly state'),
    'M_ROLL_STATE':spec('m_both','M_BOTH',roll_group='w_',diagnostic=True,hypothesis='Training-only calendar-preserving state roll'),
    'M_BLOCK_TARGET':spec('m_both','M_BOTH',permute_target=True,diagnostic=True,hypothesis='Deterministic 21-session label block permutation in past partitions'),
    'M_STATE_SMOOTH':spec('m_state_smooth','M_BOTH',hypothesis='Trailing 21-session weekly-state averages'),
    'M_INNOVATION':spec('m_innovation','M_BOTH',hypothesis='Predict monthly outcomes from current state minus 21-session average'),
    'M_PERSIST':spec('m_persist','M_PRICE',hypothesis='Slow rotation, common market level and trailing price trends'),
    'M_REVERT':spec('m_price','M_HIST',fixed_location=-.25,hypothesis='Shrink reversion against prior 21-session NIFTY return'),
    'M_CONTINUE':spec('m_price','M_HIST',fixed_location=.25,hypothesis='Shrink persistence toward prior 21-session NIFTY return'),
    'M_LAG_RETURN':spec('m_lag_return','M_PRICE',hypothesis='Recent non-contemporaneous realized return as simple delayed regime proxy'),
}
for s in MONTHLY.values():s.update(horizons=[21],eligible='monthly')


def frames():
    load=lambda n:matrix(n+'.csv',OUT)
    b=load('base');n=load('native');r=load('rotation');v=load('etf');p=load('positions');intr=load('intraday').reindex(b.index)
    state=load('state');panel=load('panel');stock=load('stock_proxy')
    cat=lambda a,z:pd.concat([a,z.reindex(a.index)],axis=1)
    levels=['r_bank','r_def'];both=['r_bank_change','r_def_change'];rot=cat(b,r[both])
    activity=v[['e_turn','e_shock','e_activity_participation']]
    addon={'native':n,'base':b,'both_changes':rot,'bank_change':cat(b,r[[both[0]]]),'def_change':cat(b,r[[both[1]]]),
           'levels':cat(b,r[levels]),'levels_changes':cat(b,r[levels+both]),
           'interactions':cat(rot,r[['r_breadth_interaction','r_risk_interaction']]),
           'etf_activity':cat(rot,activity),'etf_exposure':cat(rot,v),
           'etf_gate':cat(cat(rot,activity),pd.DataFrame({'e_rotation_x_activity':v.e_activity*(r.r_bank_norm.abs()+r.r_def_norm.abs())})),
           'intra':cat(rot,intr.drop(columns=['close_diff_points','close_diff_bps'])),'position':cat(rot,p),'panel':cat(rot,panel),
           'stock_proxy':cat(rot,stock.drop(columns='proxy_stock_count'))}
    for label,suffix in [('residual','residual'),('normalized','norm'),('slopes','slope'),('acceleration','accel'),('switch','switch'),('extremes','extreme'),('lag1','lag1'),('lag5','lag5'),('lag10','lag10'),('average','average')]:
        addon[label]=cat(b,r[[f'{k}_{suffix}' for k in levels]])
    st=r[['m_financial','m_cyclical','m_broad','m_vol_divergence','m_sync','m_concentration','m_rotation_speed']]
    addon['structure_level']=cat(rot,st)
    addon['structure_change']=cat(addon['structure_level'],st.diff(5).add_suffix('_d5'))
    addon['participation']=cat(rot,r[['m_participation','m_broad','m_leader_persistence']])
    addon['risk_structure']=cat(rot,r[['m_asymmetry','m_transition','m_implied_transition']])
    price=b[['p_ret5','p_ret21','p_rv21','p_vix','p_trend']]
    addon.update({'m_price':price,'m_only_state':state.assign(p_rv21=b.p_rv21.shift(21)),
                  'm_both':cat(price,state),'m_lag_state':cat(price,state.shift(21)),
                  'm_lag_price':cat(price.shift(21),state),'m_state_smooth':cat(price,state.rolling(21).mean()),
                  'm_innovation':cat(price,state-state.rolling(21).mean()),
                  'm_persist':cat(price,cat(r[['r_bank','r_def','m_participation','m_sync']].rolling(21).mean(),panel[['panel_common','panel_volatility']].rolling(21).mean())),
                  'm_lag_return':price.assign(delayed_return=b.p_ret21.shift(21))})
    # p_rv21 is accessed for the distribution API but excluded from the state-only fit.
    addon['m_only_state']=addon['m_only_state'].assign(p_rv21=.01)
    elig={ 'intraday':intr.intraday_rv.notna(), 'intra_strict':intr.close_diff_bps.le(10),
          'monthly':state.notna().all(axis=1)&state.shift(21).notna().all(axis=1)}
    return addon,elig


def queries(h,cohort):
    if cohort=='primary':return benchmarks()[h,'I03_nosize'].copy()
    if cohort=='diagnostic':
        q=benchmarks()[21,'I03_nosize'].copy();label=matrix(f'labels-{h}.csv').loc[q.origin]
        q['endpoint']=label.endpoint.to_numpy();q['realized_return']=label['return'].to_numpy();return q
    prior=pd.read_csv(V3/'predictions.csv');q=prior[(prior.model=='B00_empirical')&(prior.horizon==h)&(prior.split=='development_exposed')].copy()
    native=matrix('native-reference.csv');q=q[q.origin.isin(native.index)]
    q['trend']=np.where(native.p_ret21.reindex(q.origin)>0,'UP','DOWN');q['global_risk']='NA'
    return q


def row(h,fold,name,r,d,ref,cohort):
    summary=d.stats(ref)
    return {'horizon':h,'cohort':cohort,'fold':fold,'model':name,'origin':r.origin,'endpoint':r.endpoint,
            'regime':r.regime,'trend':r.trend,'global_risk':r.global_risk,'reference_close':ref,
            **d.score(r.realized_return),**summary['quantiles'],'expected_price':summary['expected_endpoint'],
            'expected_abs':summary['expected_absolute_return'],'endpoint_std':summary['endpoint_return_std'],
            'p_below_minus2':float(d.w[d.a<-.02].sum()),'p_above_plus2':float(d.w[d.a>.02].sum())}


def block_permute(y,h):
    seq=[y[i:i+h] for i in range(0,len(y),h)]
    order=np.random.default_rng(SEED+h).permutation(len(seq))
    return np.concatenate([seq[j] for j in order])


def cutoff_dates(y,index,cutoff,s,eligible):
    gap=s.get('embargo',0);train_cutoff=index[max(0,index.get_loc(cutoff)-gap)]
    train=available(y,train_cutoff)
    if eligible is not None:train=train[eligible.loc[train]]
    if len(train)<s.get('min_train',100):raise ValueError('Insufficient mature eligible training dates')
    valid=train[-s.get('residual_window',42):]
    inner_cutoff=index[max(0,index.get_loc(valid[0])-gap)]
    inner=train[y.loc[train,'endpoint']<inner_cutoff]
    if 'window' in s:inner=inner[-s['window']:];train=train[-s['window']:]
    if len(inner)<s.get('min_inner',60):raise ValueError('Insufficient purged inner-fit dates')
    assert y.loc[train,'endpoint'].max()<train_cutoff and y.loc[inner,'endpoint'].max()<inner_cutoff
    return train,inner,valid,train_cutoff,inner_cutoff


def evaluate(batch,specs,inputs,eligibility,cohort='primary'):
    registry=f'{batch}-registry.json'
    if (OUT/registry).exists():raise FileExistsError(f'{batch} already registered')
    save(registry,{'registered_at':now(),'cohort':cohort,'configurations':specs,'seed':SEED,
                   'source':{p.name:sha(p) for p in [SRC/'models.py',SRC/'experiments.py']}})
    models=OUT/'models';models.mkdir(exist_ok=True)
    out=[];ledger=[];price=matrix('price.csv').close
    for h in sorted({h for s in specs.values() for h in s.get('horizons',[5,21])}):
        y=matrix(f'labels-{h}.csv');q=queries(h,cohort)
        for fold,g in q.groupby('fold'):
            cutoff=g.origin.min()
            for name,s in specs.items():
                if h not in s.get('horizons',[5,21]):continue
                detail={'batch':batch,'horizon':h,'model':name,'fold':fold,'cohort':cohort,'cutoff':cutoff}
                try:
                    x=inputs[s['frame']];eligible=eligibility.get(s.get('eligible'));test=g if eligible is None else g[eligible.loc[g.origin].to_numpy()]
                    if test.empty:raise ValueError('No eligible query origins')
                    tr,ii,vv,tc,ic=cutoff_dates(y,x.index,cutoff,s,eligible)
                    a=x.loc[tr].copy();b=x.loc[ii].copy();z=x.loc[test.origin].copy()
                    yt=y.loc[tr,'return'].to_numpy();yi=y.loc[ii,'return'].to_numpy();yv=y.loc[vv,'return'].to_numpy()
                    if s.get('perturb'):
                        cols=[c for c in z if c.startswith(('r_','i_'))];mean=a[cols].mean();z[cols]=mean+1.05*(z[cols]-mean)
                    if s.get('roll_group'):
                        cols=[c for c in a if c.startswith(s['roll_group'])];shift=21 if h==21 else 7
                        a[cols]=np.roll(a[cols],shift,axis=0);b[cols]=np.roll(b[cols],shift,axis=0)
                    if s.get('permute_target'):yt=block_permute(yt,h);yi=block_permute(yi,h);yv=block_permute(yv,h)
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter('always')
                        m=fit(s,a,yt);m0=fit(s,b,yi)
                        innovation=yv-location(m0,x.loc[vv]);risk=x.loc[vv,'p_rv21'].to_numpy()
                        rotation=x.loc[vv,'r_bank_change'].to_numpy() if 'r_bank_change' in x else np.zeros(len(vv))
                        if s.get('law')=='history':result=[Distribution(yt[-252:])]*len(z)
                        elif 'fixed_location' in s:
                            beta=s['fixed_location'];res=yv-beta*x.loc[vv,'p_ret21'].to_numpy();result=[]
                            for value in z.p_ret21:
                                atoms=np.r_[beta*value+res,yt[-252:]];w=np.r_[np.full(len(res),.65/len(res)),np.full(min(252,len(yt)),.35/min(252,len(yt)))];result.append(Distribution(atoms,w))
                        else:result=predict(m,z,innovation,risk,rotation)
                    model_file=models/f'{batch}-{h}-{fold}-{name}.joblib'
                    joblib.dump({'model':m,'inner':m0,'training':list(tr),'inner_dates':list(ii),'validation':list(vv),
                                 'queries':list(test.origin),'residual':innovation},model_file,compress=3)
                    for origin,law in zip(test.itertuples(),result):out.append(row(h,fold,name,origin,law,float(price.loc[origin.origin]),cohort))
                    detail.update(status='ok',training_n=len(tr),inner_n=len(ii),n=len(test),train_cutoff=tc,inner_cutoff=ic,
                                  last_endpoint=y.loc[tr,'endpoint'].max(),inner_last_endpoint=y.loc[ii,'endpoint'].max(),
                                  artifact=str(model_file.relative_to(OUT)),sha256=sha(model_file),warnings=[str(w.message)[:220] for w in caught],
                                  metadata=m['metadata'])
                except Exception as exc:detail.update(status='failed',error=f'{type(exc).__name__}: {exc}')
                ledger.append(detail)
        print(batch,h,len(out),'forecasts',sum(r['status']=='failed' for r in ledger),'unestimated fits',flush=True)
    write(f'{batch}-predictions.csv',pd.DataFrame(out));save(f'{batch}-ledger.json',ledger)


def run(wave):
    x,eligible=frames()
    batches={'geometry':GEOMETRY,'rotation':ROTATIONS,'distribution':LAW,'additional':ADDITIONS,'monthly':MONTHLY}
    if wave in batches:evaluate(wave,batches[wave],x,eligible)
    else:raise ValueError(wave)


if __name__=='__main__':
    import sys
    run(sys.argv[1])
