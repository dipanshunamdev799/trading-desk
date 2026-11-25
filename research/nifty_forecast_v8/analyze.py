"""Matched scoring, chronological stress, calibration and multiplicity."""
from .common import *
from research.nifty_forecast_v7.analyze import benchmarks
from research.nifty_forecast_v5.analyze import summary
from research.nifty_forecast_v3.experiment import nonoverlap, effective_n
from .reproduce import V7_NAMES

SCORES=['brier','crps','mae']


def registry():
    cfg={};ledger=[];predictions=[];results={}
    for p in sorted(OUT.glob('*-registry.json')):
        name=p.name.removesuffix('-registry.json');plan=read(p.name)
        if 'configurations' not in plan:continue
        cfg.update({k:{**v,'batch':name,'cohort':plan['cohort']} for k,v in plan['configurations'].items()})
        led=read(name+'-ledger.json');ledger.extend({'batch':name,**r} for r in led)
        f=pd.read_csv(OUT/f'{name}-predictions.csv');predictions.append(f);results[name]=len(f)
    data=pd.concat(predictions,ignore_index=True)
    assert not data.duplicated(['cohort','model','horizon','origin']).any()
    save('search-ledger.json',{'configurations':cfg,'fold_attempts':ledger,'batch_prediction_counts':results,
         'exposure':'Historical V1–V8 search. Stress and smoothmatch were adaptive; exact duplicate testing and target rolls are diagnostic.',
         'global_intermediate_fits':read('global-intermediate-ledger.json')})
    return cfg,data


def collect_refs():
    out=benchmarks();v7=pd.read_csv(V7/'all-predictions.csv')
    for name in V7_NAMES:
        out[5,name]=v7[(v7.horizon==5)&(v7.model==name)]
    for name in ['M_STATE_LAG21','M_STATE_SHIFT5','M_STATE_SHIFT21']:
        out[21,'V7_'+name]=v7[(v7.horizon==21)&(v7.model==name)].assign(model='V7_'+name)
    return out


def stats(g, h, name, cohort, classification):
    g=g.sort_values('origin').copy()
    if 'bucket_y' not in g or g.bucket_y.isna().any():g['bucket_y']=np.digitize(g.realized_return,[-.05,-.02,-.005,.005,.02,.05])
    return {'horizon':h,'model':name,'cohort':cohort,'classification':classification,
            'disjoint':len(nonoverlap(g)),'ESS_return_ACF':effective_n(g.realized_return,h),**summary(g)}


def intervals(vectors, calendar, block):
    n=len(calendar);rng=np.random.default_rng(SEED+block);reps=2000
    starts=rng.integers(0,n,(reps,int(np.ceil(n/block))))
    indices=((starts[:,:,None]+np.arange(block))%n).reshape(reps,-1)[:,:n]
    counts=np.array([np.bincount(ix,minlength=n) for ix in indices],dtype=float)
    m=np.column_stack([v.reindex(calendar).to_numpy(float) for v in vectors]);mu=np.nanmean(m,axis=0)
    boot=counts@np.nan_to_num(m)/(counts@np.isfinite(m))
    sd=np.maximum(np.nanstd(boot,axis=0),1.e-12);critical=float(np.nanquantile(np.nanmax(abs(boot-mu)/sd,axis=1),.95))
    return mu-critical*sd,mu+critical*sd,np.nanquantile(boot,.025,axis=0),np.nanquantile(boot,.975,axis=0),critical


def run():
    cfg,p=registry();write('all-predictions.csv',p);refs=collect_refs();summary_rows=[];comparisons=[];vectors=[];increments=[];stress=[];conditions=[]
    old=pd.read_csv(V7/'all-predictions.csv');meta=refs[5,'T_ROT_DOMESTIC'].set_index('origin');x=matrix('rotation.csv',OUT);n=matrix('native.csv',OUT);globe=matrix('global.csv',OUT)
    structure=matrix('market-structure.csv',V7);etf=matrix('etf.csv',OUT)
    selectors={'trend_sign':(n.p_ret21>0),'market_breadth':(structure.participation>=.5),
               'financial_strength':(x.m_financial>0),'defensive_leadership':(x.r_def>0),
               'global_strength':(globe.x_global_mean>0),'rotation_intensity':(x.r_bank_norm.abs()+x.r_def_norm.abs()>=2),
               'ETF_activity':(etf.e_activity>0),'recent_large_index_move':(n.p_ret5.abs()>=.02)}
    systems={(c,h,m):g.sort_values('origin') for (c,h,m),g in p.groupby(['cohort','horizon','model'])}
    for (h,m),g in refs.items():summary_rows.append(stats(g,h,m,'primary','frozen reference'))
    for (cohort,h,name),g in systems.items():
        s=cfg[name];diagnostic=s.get('diagnostic',False) or s.get('perturb',False) or name.endswith('_REVISION') or cohort=='diagnostic'
        cls='diagnostic control' if diagnostic else 'research-exposed follow-up' if s['batch'] in ['stress','smoothmatch'] else 'research-exposed candidate'
        if cohort=='early':cls='earlier exposed cohort'
        if h==21 and name.startswith(('MS_','M_')) and not diagnostic:cls='monthly persistence experiment'
        summary_rows.append({**stats(g,h,name,cohort,cls),'parent':s.get('parent'),'batch':s['batch'],
                             'family':s.get('frame'),'estimator':s.get('kind','ridge/complete law'),'representation':s.get('rep','raw')})
        gi=g.set_index('origin');parent=s.get('parent');control=systems.get((cohort,h,parent),refs.get((h,parent)) if cohort=='primary' else None)
        if control is not None:
            same=gi.index.intersection(control.origin);bg=control.set_index('origin').loc[same];zg=gi.loc[same]
            if len(same):
                for m in SCORES:increments.append({'horizon':h,'cohort':cohort,'model':name,'parent':parent,'metric':m,'n':len(same),'gain':float((bg[m]-zg[m]).mean())})
                if cohort=='primary' and name in ['R_RESIDUAL','B_ROT','A_STRUCTURE_CHANGE','A_ETF_ACTIVITY','A_ETF_GATE','A_INTRADAY','A_INTRADAY_STRICT','A_NATIVE_PANEL','G_MEDIATE5','G_CONDITIONAL5','G_MEDIATE21','MS_MATCH_NOW','M_STATE_SMOOTH']:
                    groups={k:v.reindex(same).dropna() for k,v in selectors.items()}
                    groups['historical_volatility_regime']=zg.regime
                    groups['reversal_realized']=((n.p_ret21.reindex(same)>0)!=(zg.realized_return>0))
                    for key,mask in groups.items():
                        for val,where in mask.groupby(mask):
                            ix=where.index;view=zg.loc[ix].reset_index();gain=bg.loc[ix,'brier']-zg.loc[ix,'brier']
                            leave=[gain[zg.loc[ix,'fold']!=month].mean() for month in view.fold.unique() if (view.fold!=month).any()]
                            conditions.append({'horizon':h,'model':name,'parent':parent,'condition':key,'value':val,'n':len(ix),
                                'disjoint':len(nonoverlap(view)),'brier_gain':gain.mean(),'CRPS_gain':(bg.loc[ix,'crps']-zg.loc[ix,'crps']).mean(),
                                'leave_month_gain_min':min(leave) if leave else None,'leave_month_gain_max':max(leave) if leave else None,
                                'coverage80':view.coverage80.mean(),'width80':view.width80.mean(),
                                'interpretation':'after-outcome diagnostic' if key=='reversal_realized' else 'descriptive slice, no independent significance'})
        if cohort!='primary':continue
        for (bh,base),b in refs.items():
            if h!=bh:continue
            idx=gi.index.intersection(b.origin);bg=b.set_index('origin').loc[idx];zg=gi.loc[idx]
            if not len(idx):continue
            np.testing.assert_allclose(zg.realized_return,bg.realized_return,atol=1e-12)
            assert np.array_equal(zg.endpoint,bg.endpoint)
            for metric in SCORES:
                difference=bg[metric]-zg[metric];gain=float(difference.mean())
                entry={'horizon':h,'model':name,'baseline':base,'metric':metric,'n':len(idx),'gain':gain}
                comparisons.append(entry)
                if h==5:vectors.append((entry,difference))
                if metric not in ['brier','crps'] or base not in ['T_ROT_DOMESTIC','T_ELASTIC_EMBARGO','V6_MONTH_LAG1','V7_M_STATE_LAG21']:continue
                subsets=[]
                for month in zg.fold.unique():subsets.append(('leave_month',month,difference[zg.fold!=month]))
                for count in [1,3,5,10]:subsets.append(('remove_top_gain',count,difference.sort_values().iloc[:-count]))
                for phase in range(min(5,h)):
                    chosen=nonoverlap(zg.reset_index().iloc[phase:]).origin
                    subsets.append(('disjoint_phase',phase,difference.loc[chosen]))
                for test,key,d in subsets:
                    if len(d):stress.append({**entry,'kind':test,'omission_or_phase':key,'n':len(d),'gain':float(d.mean())})
    info={}
    for block in [5,10,15]:
        lo,hi,rawlo,rawhi,critical=intervals([d for _,d in vectors],meta.index,block);info[block]=critical
        for j,(entry,_) in enumerate(vectors):
            entry[f'simultaneous95_block{block}']=[float(lo[j]),float(hi[j])]
            if block==10:entry['unadjusted95']=[float(rawlo[j]),float(rawhi[j])]
    save('search-adjusted-uncertainty.json',{'weekly_family':len(vectors),'repetitions':2000,'block_critical_values':info,
        'method':'Shared circular origin-block bootstrap and max standardized centered contrast. Weekly primary only. Full history exposed. Monthly CIs withheld.'})
    save('metrics.json',summary_rows);save('comparisons.json',comparisons)
    write('benchmark-comparison.csv',pd.DataFrame(comparisons));write('parent-increments.csv',pd.DataFrame(increments))
    write('conditional-slices.csv',pd.DataFrame(conditions));write('stress-results.csv',pd.DataFrame(stress))
    m=pd.DataFrame([{k:v for k,v in r.items() if not isinstance(v,list)} for r in summary_rows]);primary=m[m.cohort=='primary']
    spans=pd.DataFrame(stress)
    ranges=spans[(spans.kind=='leave_month')&(spans.baseline=='T_ROT_DOMESTIC')&(spans.metric=='brier')].groupby(['horizon','model']).gain.agg(['min','max']).reset_index().rename(columns={'min':'leave_month_min_Brier_gain','max':'leave_month_max_Brier_gain'})
    primary=primary.merge(ranges,on=['horizon','model'],how='left')
    for score,control in [('brier','T_ROT_DOMESTIC'),('crps','T_ELASTIC_EMBARGO')]:
        c=pd.DataFrame(comparisons);mx=c[(c.metric==score)&(c.baseline==control)][['horizon','model','gain','simultaneous95_block10']].rename(columns={'gain':score+'_gain_vs_V7','simultaneous95_block10':score+'_adjusted95'})
        primary=primary.merge(mx,on=['horizon','model'],how='left')
    write('direction-leaderboard.csv',primary.sort_values(['horizon','brier']));write('distribution-leaderboard.csv',primary.sort_values(['horizon','crps']))
    write('other-cohorts.csv',m[m.cohort!='primary'].sort_values(['cohort','horizon','brier']))
    print('Scored',len(p),'predictions,',len(systems),'model/horizon/cohort cells,',len(comparisons),'matched reference contrasts',flush=True)


if __name__=='__main__':run()
