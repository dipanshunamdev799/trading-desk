"""Forensic hypotheses fixed before refits: source groups, size decomposition and stress."""
import joblib,warnings
from scipy.stats import spearmanr
from .common import *
from .reproduce import frames
from .engine import fit,means,predict
from research.nifty_forecast_v3.experiment import available,inner_split
from research.nifty_forecast_v5.models import laws as original_laws

GROUPS={'PRICE_MOM':lambda c:c.startswith('p_ret') or c in ['p_trend','p_acceleration'],
 'PRICE_RISK':lambda c:c.startswith('p_rv') or c in ['p_vix','p_range'],
 'BANKS':lambda c:any(t in c for t in ['i_bank_nifty','i_nifty_financial','i_nifty_psu_bank']),
 'DEFENSIVE':lambda c:any(t in c for t in ['i_nifty_fmcg','i_nifty_pharma','i_idx_NIFTY_HEALTHCARE']),
 'CYCLICAL':lambda c:any(t in c for t in ['i_nifty_auto','i_nifty_metal','i_nifty_energy','i_nifty_realty','i_idx_Nifty_Infra','i_idx_Nifty_Commodities']),
 'IT':lambda c:c.startswith('i_nifty_it'),
 'BROAD':lambda c:any(t in c for t in ['i_idx_Nifty_100','i_idx_Nifty_200','i_idx_Nifty_500','i_idx_Nifty_Next_50']),
 'AGGREGATES':lambda c:c in ['i_participation','i_dispersion','i_acceleration','i_concentration','i_leadership_persistence','i_defensive_cyclical']}
def recompute(full,data,exclude):
    out=full.copy();keys=[k for k in data if not k.startswith(('s_','g_')) and k not in ['nifty_spot','india_vix','niftybees'] and not any(t in k.lower() for t in exclude)]
    sr=pd.concat([data[k].close.reindex(full.index).pct_change(5,fill_method=None) for k in keys],axis=1)
    out['i_participation']=sr.gt(0).sum(axis=1)/sr.notna().sum(axis=1).replace(0,np.nan);out['i_dispersion']=sr.std(axis=1);out['i_acceleration']=out.i_participation.diff(5)
    out['i_concentration']=sr.abs().max(axis=1)/sr.abs().sum(axis=1).replace(0,np.nan);out['i_leadership_persistence']=sr.rank(axis=1).corrwith(sr.shift(5).rank(axis=1),axis=1)
    return out
def build_variants(x,data,ref,top,h):
    full=x[[c for c in x if c.startswith(('p_','i_'))]];size=[c for c in full if any(t in c.lower() for t in ['midcap','smallcap'])]
    out={'F_SIZE_COLS':(full.drop(columns=size),{}),'F_SIZE_AGG':(full.assign(**{c:ref[c] for c in ['i_participation','i_dispersion','i_acceleration','i_concentration','i_leadership_persistence']}),{}),
      'F_SMALL_ONLY':(recompute(full.drop(columns=[c for c in size if 'smallcap' in c.lower()]),data,['smallcap']),{}),
      'F_MID_ONLY':(recompute(full.drop(columns=[c for c in size if 'midcap' in c.lower()]),data,['midcap']),{}),
      'F_SIZE_ORTHO':(full,{'residualize_size':True})}
    for group,fn in GROUPS.items():out['F_NO_'+group]=(ref.drop(columns=[c for c in ref if fn(c)]),{})
    for i,c in enumerate(top[h]):out[f'F_DROP_TOP{i+1}']=(ref.drop(columns=[c]),{'dropped_feature':c})
    for n in [126,189]:out['F_ROLL'+str(n)]=(ref,{'window':n})
    for alpha in [30,300]:out['F_ALPHA'+str(alpha)]=(ref,{'alpha':alpha})
    for p in ['robust','no_clip']:out['F_PRE_'+p]=(ref,{'preprocess':p})
    for lag in [1,2]:
        f=ref.copy();c=[n for n in f if n.startswith('i_')];f[c]=f[c].shift(lag);out['F_INTERNAL_LAG'+str(lag)]=(f,{})
    out['F_ALL_LAG1']=(ref.shift(1),{})
    for regime in ['HIGHVOL','LOWVOL','TREND','SIDEWAYS']:out['F_OMIT_'+regime]=(ref,{'omit':regime})
    # Explicit synthetic1bp time-varying revision, not an invented real provider revision.
    mutated={n:f.copy() for n,f in data.items()}
    for j,(name,f) in enumerate(mutated.items()):
        if name.startswith(('g_','s_')) or name in ['nifty_spot','india_vix','niftybees']:continue
        shock=1+1e-4*np.sin(np.arange(len(f))*2*np.pi/7+j)
        for c in ['open','high','low','close']:f[c]=f[c].to_numpy()*shock
    from research.nifty_forecast_v5.features import build
    from research.nifty_forecast_v5.expansion import variant
    with warnings.catch_warnings():warnings.simplefilter('ignore',pd.errors.PerformanceWarning);fx,_,_=build(mutated,extra=False)
    rr=variant('I03_nosize',fx,mutated);out['F_SYNTH_REV1BP']=(rr[[c for c in rr if c.startswith(('p_','i_'))]],{})
    return out
def run():
    if (OUT/'forensic-registry.json').exists():raise FileExistsError('Forensics already registered')
    x,price,labels,data,allframes=frames();ref=allframes['I03_nosize'][[c for c in allframes['I03_nosize'] if c.startswith(('p_','i_'))]]
    top={};featuremeta=[]
    for h in [5,21]:
        a=joblib.load(V5/'models'/f'h{h}-2026-07-I03_nosize.joblib')['model'];cols=a['scale'].cols;coef=a['estimator'].coef_
        top[h]=[c for c,v in sorted(zip(cols,coef),key=lambda z:abs(z[1]),reverse=True)[:6]]
    # Register all34? actual count recorded, not guessed.
    variants={h:build_variants(x,data,ref,top,h) for h in [5,21]}
    save('forensic-registry.json',{'registered_at':now(),'top_selection':'Absolute standardized coefficient from original July refit, trained only before first outer origin; no outer outcome ranking',
        'top_features':top,'groups':list(GROUPS),'configurations':{n:{'parameters':p,'columns':list(f.columns)} for n,(f,p) in variants[5].items()},
        'paired_size_design':'I00; columns-only removal; aggregate-only recomputation; I03 both; separate mid/small removal; size residualization',
        'permutation':'Within each query month, common5-session circular block shift for whole family; diagnostic only, not causal forecasts',
        'nulls':'Three fixed block-preserving training-label rolls,3H/7H/11H; no candidate selection',
        'source_revision':'Actual V3/V5 overlap audit plus explicitly synthetic1bp time-varying input perturbation, no fabricated real revision',
        'code_hashes':{p.name:sha(p) for p in SRC.glob('*.py')}})
    old=pd.read_csv(V5/'all-predictions.csv');old=old[old.split=='outer_exposed'];records=[];ledger=[];permutations=[];diagnostics=[];negative=[]
    (OUT/'models').mkdir(exist_ok=True)
    for h in [5,21]:
        queries=old[(old.horizon==h)&(old.model=='I03_nosize')]
        for fold,g in queries.groupby('fold'):
            cutoff=g.origin.min();ix=available(labels[h],cutoff);ii,vv=inner_split(labels[h],ix)
            source=joblib.load(V5/'models'/f'h{h}-{fold}-I03_nosize.joblib');s=source['model']['scale'];est=source['model']['estimator'];z=s.transform(ref.loc[ix]);coef=est.coef_
            fullsource=joblib.load(V5/'models'/f'h{h}-{fold}-I00.joblib')['model'];scols=[c for c in fullsource['scale'].cols if 'midcap' in c.lower() or 'smallcap' in c.lower()]
            for c,b in zip(s.cols,coef):
                ar=ref.loc[ix,c].to_numpy();yr=labels[h].loc[ix,'return'].to_numpy();ic=float(spearmanr(ar,yr,nan_policy='omit').statistic)
                diagnostics.append({'horizon':h,'fold':fold,'feature':c,'standardized_coefficient':float(b),'train_rank_ic':ic if np.isfinite(ic) else None,'n_train':len(ix),'prediction_change_median_replacement':float(abs(b)*np.mean(abs(z[:,s.cols.index(c)])))})
            cor=ref.loc[ix].corr();size_info=[]
            for c in [c for c in x if 'midcap' in c.lower() or 'smallcap' in c.lower()]:
                vals=x.loc[ix,c];cc=vals.corr(ref.loc[ix].iloc[:,0])
                corr=ref.loc[ix].corrwith(vals).abs();size_info.append({'feature':c,'observed_training':int(vals.notna().sum()),'missing_fraction':float(vals.isna().mean()),'entered_original_full_model':c in scols,
                    'max_abs_correlation_to_retained':float(corr.max()) if corr.notna().any() else None,'raw_std':float(vals.std()) if vals.notna().any() else None})
            save(f'forensic-details/h{h}-{fold}.json',{'size_inputs':size_info,'original_full_columns':fullsource['scale'].cols,'nosize_columns':s.cols,'covariance_condition':float(np.linalg.cond(np.corrcoef(z,rowvar=False)+np.eye(z.shape[1])*1e-8)),
                'max_abs_standardized_retained':float(np.max(abs(z))),'training_clipped_fraction':float(np.mean(abs(z)>=5)),'training_cutoff':cutoff})
            for name,(xx,params) in variants[h].items():
                trainix=ix[-params['window']:] if 'window' in params else ix;innerix=ii[-params['window']:] if 'window' in params else ii
                if 'omit' in params:
                    om=params['omit'];high=ref.p_rv21>ref.loc[ix,'p_rv21'].median();trend=abs(ref.p_ret21)>ref.p_rv21*np.sqrt(21)
                    excluded={'HIGHVOL':high,'LOWVOL':~high,'TREND':trend,'SIDEWAYS':~trend}[om];trainix=trainix[~excluded.loc[trainix].to_numpy()]
                    # Inner threshold is fitted only before inner validation.
                    hi=ref.p_rv21>ref.loc[ii,'p_rv21'].median();ex={'HIGHVOL':hi,'LOWVOL':~hi,'TREND':trend,'SIDEWAYS':~trend}[om];innerix=innerix[~ex.loc[innerix].to_numpy()]
                try:
                    if len(trainix)<80 or len(innerix)<60:raise ValueError('Too few observations after registered regime exclusion')
                    spec={'kind':'ridge',**params};inner=fit(spec,xx.loc[innerix],labels[h],vv[0]);res=labels[h].loc[vv,'return'].to_numpy()-means(inner,xx.loc[vv]);model=fit(spec,xx.loc[trainix],labels[h],cutoff);pred=predict(model,xx.loc[g.origin],res)
                    path=OUT/'models'/f'h{h}-{fold}-{name}.joblib';joblib.dump({'model':model,'residual':res,'inner_training':list(innerix),'inner_validation':list(vv),'cutoff':cutoff},path,compress=3)
                    ledger.append({'id':f'V6-H{h}-{fold}-{name}','horizon':h,'fold':fold,'model':name,'status':'ok','train_n':len(trainix),'inner_n':len(innerix),'last_endpoint':str(labels[h].loc[trainix,'endpoint'].max()),'cutoff':cutoff,'inner_last_endpoint':str(labels[h].loc[innerix,'endpoint'].max()),'inner_first':vv[0],'artifact':str(path.relative_to(ROOT)),'sha256':sha(path)})
                    for row,d in zip(g.itertuples(),pred):records.append({'horizon':h,'fold':fold,'model':name,'origin':row.origin,'endpoint':row.endpoint,'regime':row.regime,'trend':row.trend,'global_risk':row.global_risk,**d.score(row.realized_return)})
                except Exception as e:ledger.append({'horizon':h,'fold':fold,'model':name,'status':'failed','reason':type(e).__name__+':'+str(e)[:200]})
            for group,fn in GROUPS.items():
                q=allframes['I03_nosize'].loc[g.origin].copy();cols=[c for c in q if fn(c)];q[cols]=np.roll(q[cols].to_numpy(),5,axis=0);pred=original_laws(source['model'],q,{},source['residual'])
                for row,d in zip(g.itertuples(),pred):permutations.append({'horizon':h,'fold':fold,'group':group,'origin':row.origin,'kind':'DIAGNOSTIC_FAMILY_PERMUTATION',**d.score(row.realized_return)})
            for block in [3,7,11]:
                li=labels[h].copy();li.loc[ii,'return']=np.roll(li.loc[ii,'return'].to_numpy(),block*h);inner=fit({'kind':'ridge'},ref.loc[ii],li,vv[0]);res=np.roll(labels[h].loc[vv,'return'].to_numpy(),block*h)-means(inner,ref.loc[vv]);lf=labels[h].copy();lf.loc[ix,'return']=np.roll(lf.loc[ix,'return'].to_numpy(),block*h);model=fit({'kind':'ridge'},ref.loc[ix],lf,cutoff);pred=predict(model,ref.loc[g.origin],res)
                for row,d in zip(g.itertuples(),pred):negative.append({'horizon':h,'fold':fold,'block_shift_multiple':block,'origin':row.origin,**d.score(row.realized_return)})
            print('Forensics',h,fold,'failed',sum(r['status']=='failed' for r in ledger),flush=True)
    pd.DataFrame(records).to_csv(OUT/'forensic-predictions.csv',index=False);save('forensic-ledger.json',ledger);pd.DataFrame(permutations).to_csv(OUT/'group-permutation.csv',index=False);pd.DataFrame(diagnostics).to_csv(OUT/'feature-influence.csv',index=False);pd.DataFrame(negative).to_csv(OUT/'block-null-predictions.csv',index=False)
    print('Forensics complete',len(variants[5]),'variants',len(records),'rows',flush=True)
if __name__=='__main__':run()
