"""Bounded model registry and an identical walk-forward scoring harness."""
import warnings
import joblib
from .common import *
from .features import cached
from .estimators import fit,location,choose,Distribution
from .targets import target_store,transformed,paired_laws,sign_magnitude,buckets
from research.nifty_forecast_v9.run_models import cohort_queries,score_law
from research.nifty_forecast_v3.experiment import available
from research.nifty_forecast_v5.data import load


def cfg(frame='ten',parent='BASE10',**options):return {'frame':frame,'parent':parent,**options}


BASE_MODELS={
 'HISTORY':cfg('five','self',law='history',hypothesis='Last up-to-252 mature endpoint outcomes'),
 'NEUTRAL':cfg('five','HISTORY',law='neutral',hypothesis='Same history magnitudes with fixed half mass for each sign'),
 'REVERSION':cfg('five','HISTORY',law='revert',hypothesis='Fixed contrarian quarter of recent endpoint move with shrunk historical residuals'),
 'BASE5':cfg('five','HISTORY',hypothesis='Four price/risk/breadth plus one residual financial input'),
 'BASE10':cfg('ten','BASE5',hypothesis='Five additional rotation, liquidity and structure inputs'),
 'BASE20':cfg('twenty','BASE10',hypothesis='Expand to 20 prechosen structural fields'),
 'BASE_NATIVE':cfg('native','BASE20',hypothesis='Frozen native market internals, canonical Ridge'),
 'BASE_ROTATION':cfg('rotation','BASE_NATIVE',hypothesis='Full native base plus residualized rotation, common V10 residual rules'),
}
COMPOSITION={}
for budget in [85,126]:
    for role in ['recent','earliest','spread','blocks','balance_vol','balance_trend','balance_rotation','analogues','representative']:
        COMPOSITION[f'C{budget}_{role.upper()}']=cfg(parent='BASE10' if role=='recent' else f'C{budget}_RECENT',budget=budget,selection=role,
              hypothesis=f'Equal {budget}-row training budget with {role} composition')
for w in ['recency','similarity','balance','analogue_recency']:
    COMPOSITION[f'C126_W_{w.upper()}']=cfg(parent='C126_RECENT',budget=126,weight=w,hypothesis='Equal training dates, predetermined mixture of uniform and state/time weights')
for months in [1,2,3]:
    COMPOSITION[f'C85_OMIT_M{months}']=cfg(parent='C85_RECENT',budget=85,omit_month=months,diagnostic=True,
                    hypothesis='Leave one recent fitting month out then refill the same budget from older eligible dates')

OVERLAP={}
for n in [85,126,None]:
    name=str(n or 'MAX')
    for kind in ['plain','phase0','phase1','staggered','overlap_weight','gls','gls_strong','blockmean']:
        OVERLAP[f'O{name}_{kind.upper()}']=cfg(parent='BASE10' if kind=='plain' else f'O{name}_PLAIN',budget=n,overlap=kind,
            hypothesis='Same source eligibility and train budget. Vary only temporal dependence treatment.')

STRUCTURE={
 'S_GROUPS':cfg('native_rot','S_NATIVE_ROT',rep='groups',hypothesis='Economic family-specific penalty'),
 'S_NATIVE_ROT':cfg('native_rot','BASE_NATIVE',hypothesis='Equivalent native rotation covariates and uniform penalty'),
 'S_HIERARCHY':cfg('native_rot','S_GROUPS',rep='hierarchy',hypothesis='Economic group and training correlation-cluster shrinkage'),
 'S_ELASTIC':cfg('native_rot','S_NATIVE_ROT',rep='cluster_elastic',kind='elastic',hypothesis='Cluster-balanced sparse coefficient fit'),
 'S_BAYES':cfg('ten','BASE10',kind='bayes',hypothesis='Bayesian Ridge with zero-centered coefficient priors'),
 'S_POOL':cfg('native_rot','S_NATIVE_ROT',rep='pool',hypothesis='Share standardized effects within economic-sector groups'),
 'S_RESIDUAL':cfg('native_rot','S_POOL',rep='factor_residual',hypothesis='Group factors plus more strongly shrunk idiosyncratic components'),
 'S_LOWRANK':cfg('twenty','BASE20',rep='lowrank',hypothesis='Project 20 real-time state inputs to five training-only directions'),
 'S_REMOVE_BANK':cfg('no_banks','BASE10',diagnostic=True,hypothesis='Remove residual financial leadership'),
 'S_LAG_ROTATION':cfg('source_lag','BASE10',diagnostic=True,hypothesis='Explicit one-observed-session source lag'),
 'S_COMMON':cfg('common_factor','BASE10',hypothesis='Causal NIFTY common factor component beyond 10-input control'),
 'S_RESID_FACTOR':cfg('residual_factor','BASE10',hypothesis='Active sector residual component beyond 10-input control'),
 'S_STATE_LEVEL':cfg('state_level','BASE10',hypothesis='Observed market-state levels'),
 'S_STATE_LAG':cfg('state_lag','BASE10',hypothesis='Ordinary previous-session states on same dates'),
 'S_STATE_EXPECTED':cfg('state_transition','S_STATE_LAG',hypothesis='Fit compact causal AR(1) transition per state variable'),
 'S_PERSIST':cfg('persistent','BASE10',hypothesis='21-session trailing market-risk and leadership factors'),
 'S_DISTRIBUTED':cfg('distributed','BASE10',alpha=180,hypothesis='Strongly shrunk 0/5/10/21-day rotation lag design'),
}
TARGET={f'T_{kind.upper()}':cfg(parent='T_RAW' if kind!='raw' else 'BASE10',target=kind,common_target=True,
         hypothesis='Compare transform on identical rows and convert to the same endpoint units') for kind in ['raw','log','vol','centered','split','overnight','factor','signmag']}
for name,kind,law in [('STUDENT','raw','student'),('VOL_RISK','vol','risk'),('VOL_STUDENT','vol','student')]:
    TARGET['T_'+name]=cfg(parent='T_VOL' if kind=='vol' else 'T_RAW',target=kind,common_target=True,law=law,
      hypothesis='Conditional location and separately regularized return scale in one law')

NEW={
 'N_EQ_CONTROL':cfg(eligible='breadth_complete',parent='BASE10',hypothesis='Complete official archive breadth comparison parent'),
 'N_EQ_OFFICIAL':cfg('breadth','N_EQ_CONTROL',eligible='breadth_complete',hypothesis='Authentic equal-weight versus cap-weight index relatives'),
 'N_INTRA_CONTROL':cfg(eligible='intraday_complete',parent='BASE10',hypothesis='Same complete synchronized session dates'),
 'N_INTRA_PANEL':cfg('intraday','N_INTRA_CONTROL',eligible='intraday_complete',hypothesis='Four index open/close breadth, synchronization and volatility concentration'),
 'N_DERIV_RAW':cfg('derivatives_raw','BASE10',hypothesis='Lagged official futures/options basis and positioning'),
 'N_DERIV_STRUCT':cfg('derivatives','N_DERIV_RAW',hypothesis='Lagged basis residual and volume-adjusted OI, plus roll magnitude proxy'),
 'N_GLOBAL_RISK':cfg('global','BASE10',target='vol',law='risk',hypothesis='Conservative foreign relative-risk information in a standardized target law'),
 'N_DOM_RISK':cfg('ten','BASE10',target='vol',law='risk',hypothesis='Exact normalized-law parent without global inputs'),
}
NEW['N_GLOBAL_RISK']['parent']='N_DOM_RISK'


def common_indices(labels,anchor,s,state,eligible=None,seed=SEED):
    all_=available(labels,anchor)
    if eligible is not None:all_=all_[eligible.reindex(all_).fillna(False).to_numpy()]
    n=s.get('budget');v=s.get('validation',28)
    if len(all_)<max(85,n or 0):raise ValueError('fewer than registered mature training rows')
    vv=all_[-v:];inner_cutoff=vv[0];inner=all_[labels.loc[all_,'endpoint']<inner_cutoff]
    if len(inner)<38:raise ValueError('fewer than 38 purged inner rows')
    pool=all_.copy()
    if 'omit_month' in s:
        unique=list(dict.fromkeys(all_.str[:7]))[::-1]
        if len(unique)<s['omit_month']:raise ValueError('requested fitting month unavailable')
        omit=unique[s['omit_month']-1];all_=all_[all_.str[:7]!=omit];inner=inner[inner.str[:7]!=omit]
        if len(all_)<(n or 85) or len(inner)<38:raise ValueError('omission prevents required matched budget')
    rule=s.get('selection','recent')
    tr=choose(all_,n,rule,state,anchor,seed);ii=choose(inner,min(n,len(inner)) if n else None,rule,state,inner_cutoff,seed+1)
    assert (labels.loc[tr,'endpoint']<anchor).all() and (labels.loc[ii,'endpoint']<inner_cutoff).all()
    return tr,ii,vv,inner_cutoff,pool


def rotated(x,s,random_seed):
    if 'rotate' not in s:return x
    frame=x.copy();cols=[c for c in frame if c not in ['p_ret5','p_ret21','p_rv21']]
    if isinstance(s['rotate'],int):frame[cols]=np.roll(frame[cols],s['rotate'],axis=0)
    else:
        chunks=np.array_split(frame[cols].to_numpy(),max(2,len(frame)//21));g=np.random.default_rng(random_seed)
        frame[cols]=np.concatenate([chunks[i] for i in g.permutation(len(chunks))])
    return frame


def fit_laws(s,x,y,store,state,positions,h,anchor,tr,ii,vv,query,pool,seed=SEED):
    kind=s.get('target','raw');method=s.get('law','empirical')
    yt=y.loc[pool[-252:],'return'].to_numpy();a=x.loc[query];array,context=transformed(store,kind,tr);inner,ictx=transformed(store,kind,ii)
    ia=store.index.get_indexer(tr);ib=store.index.get_indexer(ii);iv=store.index.get_indexer(vv)
    model=fit(s,rotated(x.loc[tr],s,seed),array[ia],positions.loc[tr].to_numpy(),h,state,anchor)
    small=fit(s,rotated(x.loc[ii],s,seed+1),inner[ib],positions.loc[ii].to_numpy(),h,state,vv[0])
    residual=inner[iv]-location(small,x.loc[vv]);pred=location(model,a)
    if kind=='factor':residual[:,0]+=(ictx['factor_beta']-context['factor_beta'])*residual[:,1]
    if method=='history':ds=[Distribution(yt)]*len(query)
    elif method=='neutral':ds=[Distribution(np.r_[-np.maximum(abs(yt),1e-9),np.maximum(abs(yt),1e-9)])]*len(query)
    elif method=='revert':
        ret=f'p_ret{h}';col=x[ret] if ret in x else x.p_ret21;err=y.loc[vv,'return'].to_numpy()+.25*col.loc[vv].to_numpy()
        ds=[Distribution(np.r_[err-.25*x,yt],np.r_[np.full(len(err),.65/len(err)),np.full(len(yt),.35/len(yt))]) for x in col.loc[query]]
    elif kind=='signmag':ds=sign_magnitude(model,x,y,tr,query)
    else:ds=paired_laws(context,kind,store,query,pred,residual,yt,method,store.loc[vv,'vol_scale'].to_numpy())
    stability=float(np.mean(np.var(location(model,a,member=True),axis=0)))
    return model,small,residual,ds,stability,context


def eligible_target(store):
    return store[['raw','log','vol_scale','conditional_offset','first','tail','overnight','session','future_factor']].notna().all(axis=1)


def run(batch,config=None,custom=None):
    collections={'base':BASE_MODELS,'composition':COMPOSITION,'overlap':OVERLAP,'structure':STRUCTURE,'target':TARGET,'new':NEW}
    specs=config if config is not None else collections[batch]
    if (OUT/f'{batch}-registry.json').exists():raise FileExistsError(batch)
    assert read('reproduction.json')['passed']
    save(f'{batch}-registry.json',{'registered_at':now(),'configurations':specs,'seed':SEED,
          'code_hashes':{n:sha(SRC/n) for n in ['experiments.py','estimators.py','targets.py']}})
    x,masks,state=cached();price=matrix('price.csv');raw,_=load();broad=raw['idx_Nifty_500'].close
    if custom:
        custom_frames,custom_masks=custom
        x.update(custom_frames)
        for name,series in custom_masks.items():masks[name]=series
    positions=pd.Series(np.arange(len(price)),index=price.index);logs=[];scored=[];samples=[];cache=[]
    model_folder=OUT/'models';model_folder.mkdir(exist_ok=True)
    for h in sorted({h for s in specs.values() for h in s.get('horizons',[5,21])}):
        y=matrix(f'labels-{h}.csv');query=cohort_queries(h);store=target_store(h,y,price,broad);good=eligible_target(store)
        for (cohort,fold),g in query.groupby(['split','fold'],sort=False):
            anchor=g.origin.min()
            for name,s in specs.items():
                if h not in s.get('horizons',[5,21]):continue
                log={'batch':batch,'horizon':h,'cohort':cohort,'fold':fold,'cutoff':anchor,'model':name}
                try:
                    frame=x[s['frame']];mask=masks[s['eligible']] if 'eligible' in s else pd.Series(True,index=frame.index)
                    if s.get('common_target'):mask=mask&good
                    q=g[mask.loc[g.origin].to_numpy()]
                    if not len(q):raise ValueError('no eligible common query origins')
                    tr,ii,vv,inner_cutoff,pool=common_indices(y,anchor,s,state,mask)
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter('always')
                        m,m0,err,ds,var,context=fit_laws(s,frame,y,store,state,positions,h,anchor,tr,ii,vv,q.origin,pool)
                    path=model_folder/f'{batch}-{h}-{cohort}-{fold}-{name}.joblib'
                    joblib.dump({'model':m,'inner_model':m0,'training':list(tr),'inner':list(ii),'validation':list(vv),'pool':list(pool[-252:]),
                                 'query':list(q.origin),'residuals':err,'target_context':context},path,compress=3)
                    cuts=np.quantile(y.loc[pool[-252:],'return'],[.10,.30,.50,.70,.90])
                    for r,law in zip(q.itertuples(),ds):
                        scored.append({**score_law(h,fold,name,r,law,float(price.close.loc[r.origin]),cohort),**buckets(law,r.realized_return,cuts)})
                        if batch in ['base','target','informationlaws','finalcurve'] or name in ['O126_GLS','O85_GLS','S_ELASTIC','C85_SPREAD']:
                            cache.append({'model':name,'horizon':h,'cohort':cohort,'origin':r.origin,'endpoint':r.endpoint,
                                          'atoms':law.a.tolist(),'weights':law.w.tolist()})
                    actual=m['basis']@m['beta'][1:]
                    for n,c in zip(m['scale'].cols,actual[:,0]):samples.append({'horizon':h,'cohort':cohort,'fold':fold,'model':name,
                                   'feature':n,'first_component_standardized_coefficient':c})
                    log.update(status='ok',query_count=len(q),training=len(tr),inner_fit=len(ii),valid=len(vv),inner_cutoff=inner_cutoff,
                               latest_endpoint=y.loc[tr,'endpoint'].max(),inner_latest_endpoint=y.loc[ii,'endpoint'].max(),
                               artifact=path.relative_to(OUT).as_posix(),sha256=sha(path),training_metrics=m['metadata'],
                               inner_metrics=m0['metadata'],phase_prediction_variance=var,warnings=[str(w.message)[:300] for w in caught])
                except Exception as exc:log.update(status='unestimated',reason=f'{type(exc).__name__}: {exc}')
                logs.append(log)
        print(batch,h,len(scored),'scores;',sum(l['status']!='ok' for l in logs),'unestimated folds',flush=True)
    write(f'{batch}-predictions.csv',pd.DataFrame(scored));write(f'{batch}-coefficients.csv',pd.DataFrame(samples));save(f'{batch}-ledger.json',logs)
    if cache:(OUT/f'{batch}-laws.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in cache),encoding='utf-8')


if __name__=='__main__':
    import sys
    run(sys.argv[1])
