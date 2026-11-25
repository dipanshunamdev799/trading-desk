"""Shared chronology for matched learning curves and model waves."""
import warnings
import joblib
from .common import *
from .models import fit, info, laws, location
from research.nifty_forecast_v8.experiments import frames as v8_frames, queries, row as score_law
from research.nifty_forecast_v3.experiment import available


def spec(frame,parent='P_HIST',**cfg):return {'frame':frame,'parent':parent,**cfg}


def inputs():
    x,_=v8_frames();b=x['base'];state=matrix('state-context.csv',OUT);f=matrix('financial.csv',OUT)
    rot=matrix('rotation.csv',V8);innovation=matrix('innovation.csv',OUT);g=matrix('global-context.csv',OUT)
    sector=matrix('panel.csv',OUT);stock=matrix('proxy.csv',OUT);old=matrix('state.csv',V8)
    cat=lambda a,z:pd.concat([a,z.reindex(a.index)],axis=1)
    small=b[['p_ret5','p_ret21','p_rv21','p_vix','p_trend','i_participation','i_dispersion','i_nifty_it_rel21']]
    x['small']=small;x['small_resid']=cat(small,rot[['r_bank_residual','r_def_residual']]);x['small_state']=cat(x['small_resid'],state[['s_vol','s_trend','s_sync','s_breadth']]);
    x['compact_structure']=cat(x['small_resid'],rot[['m_financial','m_cyclical','m_broad','m_vol_divergence','m_sync','m_concentration','m_rotation_speed']]);
    x['cluster_rot']=cat(x['native'],rot[['r_bank_residual','r_def_residual']]);x['risk_global']=cat(x['small_resid'],g[['q_global_shock']]);
    x['global_side']=cat(x['small_resid'],g[['q_india_diverge','q_corr_change','q_global_shock']]);
    x['bank_level']=cat(small,f[['f_spread']]);x['bank_change']=cat(small,f[['f_change']]);
    for h in [42,63,84]:x[f'bank_resid{h}']=cat(small,f[[f'f_resid{h}']]);
    x['financial_persistence']=cat(small,f[['f_persist','f_accel','f_vol_adjusted']]);
    x['financial_panel']=cat(small,f[['f_resid63','f_psu_private','f_bank_broad','f_dispersion','f_corr_change','f_rank_shift']]);
    x['financial_panel_no_size']=x['financial_panel'].drop(columns='f_psu_private');
    x['financial_trade']=cat(x['financial_panel'],f[['f_insurance_bank','f_etf_tracking','f_fin_etf_tracking']]);
    x['financial_lag']=cat(small,x['financial_panel'].drop(columns=small.columns).shift(5));
    x['financial_reduced']=cat(small.drop(columns='i_nifty_it_rel21'),f[['f_resid63','f_psu_private','f_dispersion']]);
    for suffix in ['level','delta','ar','robust']:x['innovation_'+suffix]=cat(small,innovation.filter(regex=f'_{suffix}$'))
    x['innovation_ar_noglobal']=x['innovation_ar'].drop(columns='z_global_ar')
    x['panel_native']=cat(small,sector);x['panel_proxy']=cat(small,stock.drop(columns='stock_count'));
    x['panel_incr']=cat(x['small_resid'],sector);x['native_nobank']=b.drop(columns=[c for c in b if 'bank' in c or 'financial' in c]);
    slow=cat(state[['s_trend','s_sync','s_breadth','s_rotation_persistence','s_vol']].rolling(21).mean().add_suffix('_slow'),sector[['c_residual_mean','c_common_risk']].rolling(21).mean().add_suffix('_slow'))
    x['monthly_fast']=x['small_state'];x['monthly_slow']=cat(small,slow);x['monthly_fast_slow']=cat(x['small_state'],slow)
    lag=rot[['r_bank_residual','r_def_residual']];lagged=pd.concat([lag.shift(k).add_suffix(f'_lag{k}') for k in [0,5,10,21]],axis=1)
    x['monthly_lags']=cat(x['monthly_slow'],lagged);x['monthly_average_state_lags']=cat(x['monthly_slow'],pd.concat([old.rolling(21).mean().shift(k).add_suffix(f'_lag{k}') for k in [0,5,21]],axis=1));
    x['monthly_slow_plus_state']=cat(x['monthly_slow'],old.rolling(21).mean());
    eligible={'monthly_smooth':old.rolling(21).mean().notna().all(axis=1)&old.rolling(21).mean().shift(21).notna().all(axis=1)}
    return x,eligible


LEARNING={}
for name,frame in [('ROT','both_changes'),('RES','residual'),('SMALL','small_resid'),('HIST','small')]:
    for n in [85,126,189,252,300,'MAX']:
        LEARNING[f'L_{name}_{n}']=spec(frame,'L_HIST_MAX',window=n if n!='MAX' else None,
            law='history' if name=='HIST' else 'empirical',horizons=[5],hypothesis='Matched chronological sample-size curve, common 28-origin residual validation')
for length in [28,42]:
    for alpha in [100,150]:
        LEARNING[f'L_DESIGN_V{length}_A{alpha}']=spec('both_changes','L_ROT_MAX',residual_window=length,alpha=alpha,horizons=[5],
          hypothesis='Same features and expanding history, change residual and regularization rules only')

BASE={
    'P_HIST':spec('small',law='history',hypothesis='Mature empirical reference'),
    'P_NATIVE':spec('base',hypothesis='Native 51-column Ridge'),
    'P_ROT':spec('residual','P_NATIVE',hypothesis='V8 residualized rotation under common V9 fitting rules'),
    'P_STRUCTURE':spec('structure_change','P_ROT',hypothesis='V8 structural changes under common rules'),
    'P_CLUSTER':spec('cluster_rot','P_ROT',kind='elastic',rep='cluster',dedup=True,hypothesis='Canonical cluster-balanced Elastic Net with rotation'),
    'P_LIQ':spec('etf_activity','P_ROT',hypothesis='Domestic plus normalized ETF activity'),
    'P_REVERT':spec('small','P_HIST',fixed_multiplier=-.25,hypothesis='Simple conservative price reversion'),
    'P_MOMENTUM':spec('small','P_HIST',fixed_multiplier=.25,hypothesis='Simple conservative price continuation'),
    'P_COMPACT':spec('small_resid','P_HIST',hypothesis='Compact native price, breadth and residualized rotation'),
}
ADAPT={
    'T_EW90':spec('small_resid','P_COMPACT',kind='ew',half_life=90,hypothesis='Recency-weighted expanding Ridge'),
    'T_EW45':spec('small_resid','P_COMPACT',kind='ew',half_life=45,hypothesis='More rapid EW adaptation'),
    'T_KALMAN':spec('small_resid','P_COMPACT',kind='kalman',hypothesis='Shrunk dynamic coefficient random walk with matured outcomes'),
    'T_KALMAN_SLOW':spec('small_resid','T_KALMAN',kind='kalman',process=.00004,hypothesis='Lower coefficient process variance'),
    'T_STATIC_BLEND':spec('small_resid','P_COMPACT',kind='blend',hypothesis='Equal 126-date and expanding conditional locations'),
    'T_CHANGE_WINDOW':spec('small_resid','T_STATIC_BLEND',kind='trigger',hypothesis='Causal feature-shift triggered short/long fit mix'),
    'T_RECENT126':spec('small_resid','P_COMPACT',window=126,hypothesis='Fixed rolling 126, no fallback to expanding'),
    'T_EXPERT_PARENT':spec('small_state','P_COMPACT',hypothesis='State-informed comparison without segmentation'),
    'T_VOL_EXPERT':spec('small_state','T_EXPERT_PARENT',kind='expert',gate='s_vol',hypothesis='Shrunk volatility gated experts'),
    'T_TREND_EXPERT':spec('small_state','T_EXPERT_PARENT',kind='expert',gate='s_trend',hypothesis='Shrunk trend gated experts'),
    'T_BREADTH_EXPERT':spec('small_state','T_EXPERT_PARENT',kind='expert',gate='s_breadth',hypothesis='Shrunk breadth gated experts'),
    'T_STUDENT':spec('small_resid','P_COMPACT',law='student',hypothesis='Student-t conditional residual law'),
    'T_RISK_STUDENT':spec('small_resid','T_STUDENT',law='student_scale',hypothesis='Volatility-dependent Student-t scale'),
    'T_RISK_LAW':spec('small_resid','P_COMPACT',law='risk',hypothesis='Same-regime reweighted residuals'),
    'T_GLOBAL_DIRECT':spec('global_side','P_COMPACT',hypothesis='Compact divergence and shock additions'),
    'T_GLOBAL_LAW':spec('risk_global','T_GLOBAL_LOCATION',law='global_risk',hypothesis='Global shock-conditioned empirical residual weights'),
    'T_GLOBAL_LOCATION':spec('risk_global','P_COMPACT',hypothesis='Same predictors without global scale conditioning'),
}
INFORMATION={}
for frame in ['bank_level','bank_change','bank_resid42','bank_resid63','bank_resid84','financial_persistence',
              'financial_panel','financial_panel_no_size','financial_trade','financial_lag','financial_reduced']:
    INFORMATION['F_'+frame.upper()]=spec(frame,'F_BASE',hypothesis='Financial incremental or timing control on compact price/state parent')
INFORMATION['F_BASE']=spec('small','P_HIST',hypothesis='Compact financially unaugmented reference')
INFORMATION['F_CLUSTER']=spec('financial_panel','F_FINANCIAL_PANEL',alpha=170,dedup=True,hypothesis='Canonical features plus stronger shrinkage on richer correlated financial block')
INFORMATION['F_REMOVAL']=spec('native_nobank','P_NATIVE',hypothesis='Remove individual banking and financial feature family')
for kind in ['level','delta','ar','robust','ar_noglobal']:
    INFORMATION['I_'+kind.upper()]=spec('innovation_'+kind,'I_LEVEL' if kind!='level' else 'F_BASE',hypothesis='Historical innovation alternatives to identical indicator levels')
INFORMATION.update({'X_NATIVE_PANEL':spec('panel_native','F_BASE',hypothesis='Date-grouped native residual panel'),
                    'X_ROT_PANEL':spec('panel_incr','P_COMPACT',hypothesis='Native residual panel beyond compact rotation'),
                    'X_STOCK_PROXY':spec('panel_proxy','F_BASE',diagnostic=True,hypothesis='Later-selected panel, survivorship-exposed proxy')})

MONTHLY={
   'M_FAST':spec('monthly_fast','P_COMPACT'), 'M_SLOW':spec('monthly_slow','M_FAST'), 'M_FAST_SLOW':spec('monthly_fast_slow','M_SLOW'),
   'M_DISTRIBUTED':spec('monthly_lags','M_SLOW',alpha=160), 'M_MULTITASK':spec('monthly_lags','M_DISTRIBUTED',kind='multitask',alpha=160),
   'M_STATE_LAGS':spec('monthly_average_state_lags','M_SLOW_MATCH',eligible='monthly_smooth'),
   'M_SMOOTH':spec('monthly_slow_plus_state','M_SLOW_MATCH',eligible='monthly_smooth'),
   'M_SLOW_MATCH':spec('monthly_slow','M_SLOW',eligible='monthly_smooth'),
}
for key in MONTHLY:MONTHLY[key].update(horizons=[21],hypothesis='Month-scale representation and matched state availability')
for shift in [-42,-21,-10,-5,5,10,21,42,63]:
    MONTHLY[f'M_SHIFT_{shift:+d}']=spec('monthly_slow_plus_state','M_SMOOTH',horizons=[21],eligible='monthly_smooth',roll=shift,diagnostic=True,hypothesis='Predeclared train-only phase shift')
for order in [1,2,3]:MONTHLY[f'M_PERM_{order}']=spec('monthly_slow_plus_state','M_SMOOTH',horizons=[21],eligible='monthly_smooth',permutation=order,diagnostic=True,hypothesis='Preserve within-block dependence while permuting training state blocks')


def cohort_queries(h):
    info=[]
    for old,new in [('early','early'),('primary','later')]:
        g=queries(h,old).assign(split=new)
        info.append(g)
    result=pd.concat(info,ignore_index=True).sort_values('origin')
    assert result.origin.is_unique
    return result


def indices(y,cutoff,s,elig=None):
    tr=available(y,cutoff)
    if elig is not None:tr=tr[elig.loc[tr].to_numpy()]
    length=s.get('window');n=s.get('residual_window',28)
    if len(tr)<max(85,length or 0):raise ValueError('Insufficient mature history for registered fit length')
    vv=tr[-n:];bound=vv[0];ii=tr[y.loc[tr,'endpoint']<bound]
    if len(ii)<40:raise ValueError('Insufficient purged inner training dates')
    if length:tr=tr[-length:];ii=ii[-length:]
    assert (y.loc[tr,'endpoint']<cutoff).all() and (y.loc[ii,'endpoint']<bound).all()
    return tr,ii,vv,bound


def fit_variant(s,x,y,tr,ii,vv,q,aux=None):
    a=x.loc[tr].copy();b=x.loc[ii].copy();t=x.loc[q]
    if 'roll' in s or 'permutation' in s:
        cols=[c for c in a if c.startswith('w_')]
        for frame in [a,b]:
            if 'roll' in s:frame[cols]=np.roll(frame[cols],s['roll'],axis=0)
            else:
                chunks=[v for v in np.array_split(frame[cols].to_numpy(),max(2,len(frame)//21))]
                rng=np.random.default_rng(SEED+s['permutation']);frame[cols]=np.concatenate([chunks[k] for k in rng.permutation(len(chunks))])
    m=fit(s,a,y.loc[tr,'return'].to_numpy(),aux.loc[tr] if aux is not None else None)
    m0=fit(s,b,y.loc[ii,'return'].to_numpy(),aux.loc[ii] if aux is not None else None)
    res=y.loc[vv,'return'].to_numpy()-location(m0,x.loc[vv]);risk=x.loc[vv,'p_rv21'].to_numpy()
    if 'fixed_multiplier' in s:
        coef=s['fixed_multiplier'];err=y.loc[vv,'return'].to_numpy()-coef*x.loc[vv,'p_ret21'].to_numpy();pool=m['pool']
        from .models import Distribution
        weights=np.r_[np.full(len(err),.65/len(err)),np.full(len(pool),.35/len(pool))]
        ds=[Distribution(np.r_[coef*v+err,pool],weights) for v in t.p_ret21]
    else:ds=laws(m,t,res,risk,x.loc[vv,'q_global_shock'].to_numpy() if 'q_global_shock' in x else None)
    return m,m0,res,ds


def run(batch,specs=None, custom=None):
    choices={'learning':LEARNING,'base':BASE,'adapt':ADAPT,'information':INFORMATION,'monthly':MONTHLY}
    if specs is None:specs=choices[batch]
    if not read('reproduction.json')['passed']:raise RuntimeError('Frozen reference reproduction must pass')
    if (OUT/f'{batch}-registry.json').exists():raise FileExistsError(batch)
    save(f'{batch}-registry.json',{'at':now(),'seed':SEED,'configuration':specs,'source':{n:sha(SRC/n) for n in ['run_models.py','models.py']}})
    x,eligible=inputs();price=matrix('price.csv').close
    ledger=[];data=[];coef=[];cache=[]
    (OUT/'models').mkdir(exist_ok=True)
    for h in sorted({h for s in specs.values() for h in s.get('horizons',[5,21])}):
        y=matrix(f'labels-{h}.csv');q=cohort_queries(h)
        if custom is not None:y,q,price=custom[h]
        aux=None
        if h==21 and any(s.get('kind')=='multitask' for s in specs.values()):
            aux=pd.concat([matrix(f'labels-{k}.csv')['return'].rename(str(k)) for k in [1,3,5,10,15,21]],axis=1)
            for k in [1,3,5,10,15]:
                other=matrix(f'labels-{k}.csv');assert (other.endpoint.loc[y.endpoint.notna()]<=y.endpoint.dropna()).all()
        for (cohort,fold),g in q.groupby(['split','fold'],sort=False):
            anchor=g.origin.min()
            for name,s in specs.items():
                if h not in s.get('horizons',[5,21]):continue
                log={'model':name,'horizon':h,'cohort':cohort,'fold':fold,'cutoff':anchor,'parent':s['parent']}
                try:
                    z=x[s['frame']];mask=eligible.get(s.get('eligible'));rows=g if mask is None else g[mask.reindex(g.origin).fillna(False).to_numpy()]
                    if rows.empty:raise ValueError('No common eligible test dates')
                    tr,ii,vv,bound=indices(y,anchor,s,mask)
                    with warnings.catch_warnings(record=True) as cautions:
                        warnings.simplefilter('always');m,m0,res,ds=fit_variant(s,z,y,tr,ii,vv,rows.origin,aux if s.get('kind')=='multitask' else None)
                    path=OUT/'models'/f'{batch}-{h}-{cohort}-{fold}-{name}.joblib';joblib.dump({'fit':m,'inner':m0,'tr':list(tr),'ii':list(ii),'vv':list(vv),'res':res,'q':list(rows.origin)},path,compress=3)
                    for r,d in zip(rows.itertuples(),ds):
                        data.append(score_law(h,fold,name,r,d,float(price.loc[r.origin]),cohort))
                        if batch=='base':cache.append({'horizon':h,'cohort':cohort,'origin':r.origin,'endpoint':r.endpoint,'model':name,'atoms':d.a.tolist(),'weights':d.w.tolist()})
                    names,betas,intercept=info(m)
                    coef.extend({'model':name,'horizon':h,'cohort':cohort,'fold':fold,'cutoff':anchor,'feature':n,'coefficient':v,'intercept':intercept} for n,v in zip(names,betas))
                    log.update(status='ok',n=len(rows),train_n=len(tr),inner_n=len(ii),last_endpoint=y.loc[tr,'endpoint'].max(),
                               inner_cutoff=bound,inner_last_endpoint=y.loc[ii,'endpoint'].max(),model_file=path.relative_to(OUT).as_posix(),sha256=sha(path),
                               warnings=[str(v.message)[:220] for v in cautions],change_index=m.get('shift'),short_weight=m.get('short_weight'))
                except Exception as exc:log.update(status='unestimated',reason=f'{type(exc).__name__}: {exc}')
                ledger.append(log)
        print(batch,h,len(data),'predictions and',sum(r['status']=='unestimated' for r in ledger),'unestimated fits',flush=True)
    write(f'{batch}-predictions.csv',pd.DataFrame(data));write(f'{batch}-coefficients.csv',pd.DataFrame(coef));save(f'{batch}-ledger.json',ledger)
    if cache:(OUT/'expert-laws.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in cache),encoding='utf-8')


if __name__=='__main__':
    import sys
    run(sys.argv[1])
