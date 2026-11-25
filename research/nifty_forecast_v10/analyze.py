"""Match endpoints, summarize proper scores, and measure bounded search risk."""
from hashlib import sha256
from .common import *
from .experiments import cohort_queries
from research.nifty_forecast_v9.analyze import refs
from research.nifty_forecast_v8.analyze import intervals
from research.nifty_forecast_v3.experiment import effective_n


SCORES=['brier','crps','log_loss','mae','median_mae','pinball','coverage50','coverage80','width50','width80','train_bucket_brier','bucket_brier']
FROZEN=['V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO','V8_MS_WINDOW','V8_MS_ROLL','V8_M_STATE_SMOOTH',
        'V6_MONTH_STATE','V6_MONTH_LAG1','V6_BRIER','V6_CRPS','V7_M_STATE_SHIFT5','V7_M_STATE_SHIFT21',
        'P_HIST','P_CLUSTER','P_ROT','J9_STATIC','J9_REL_SHRINK']
BATCHES=['base','composition','overlap','structure','target','new','datedderivatives','informationlaws','transfer','covariance','finalcurve','mixture']


def nonoverlap(frame):
    frame=frame.sort_values('origin');orig=frame.origin.to_numpy();end=frame.endpoint.to_numpy();take=[]
    i=0
    while i<len(orig):
        take.append(i);i=max(i+1,np.searchsorted(orig,end[i],side='left'))
    return frame.iloc[take]


def predictions():
    p=[];spec={};ledger=[]
    for n in BATCHES:
        registry=read(f'{n}-registry.json')['configurations']
        spec.update({k:{**v,'batch':n} for k,v in registry.items()})
        p.append(pd.read_csv(OUT/f'{n}-predictions.csv'))
        ledger.extend(dict(batch=n,**{k:v for k,v in r.items() if k!='batch'}) for r in read(f'{n}-ledger.json'))
    result=pd.concat(p,ignore_index=True)
    assert not result.duplicated(['cohort','horizon','model','origin']).any()
    return result,spec,ledger


def references():
    controls=refs()
    for (c,h,n),g in pd.read_csv(V9/'all-predictions.csv').groupby(['cohort','horizon','model']):
        if c in ['early','later'] and (n in FROZEN or n.startswith('L_ROT_')):controls[c,h,n]=g
    return {k:g for k,g in controls.items() if len(g) and {'p','realized_return','endpoint'}.issubset(g)}


def point(g):
    p=g.p;label=g.outcome;selected=p.ge(.5);entry={'n':len(g),'disjoint':len(nonoverlap(g)),
        'outcome_ACF_ESS':effective_n(g.realized_return,int(g.horizon.iloc[0])),
        'accuracy':(selected==label).mean(),'base_rate':label.mean(),'mean_p':p.mean(),
        'balanced_accuracy':np.mean([np.mean(selected[label==v]==v) for v in [0,1] if (label==v).any()])}
    for name in SCORES:
        if name in g and g[name].notna().all():entry[name]=g[name].mean()
    if 'squared_error' in g and g.squared_error.notna().all():entry['rmse']=np.sqrt(g.squared_error.mean())
    if 'predicted_mean' in g and g.predicted_mean.notna().all():entry['mean_signed_error']=(g.predicted_mean-g.realized_return).mean()
    entry['ECE']=0.;bins=[]
    for lo,hi in [(0,.35),(.35,.45),(.45,.55),(.55,.65),(.65,1.000001)]:
        a=g[p.ge(lo)&p.lt(hi)]
        if len(a):
            v=a.p.mean();y=a.outcome.mean();bins.append({'low':lo,'high':min(hi,1.),'n':len(a),'forecast':v,'observed':y})
            entry['ECE']+=len(a)*abs(y-v)/len(g)
    return entry,bins


def group_data(p):
    r=references();sources={k:'frozen reference' for k in r}
    for k,g in p.groupby(['cohort','horizon','model']):r[k]=g;sources[k]='V10'
    for c in ['early','later']:
        for h in [5,21]:
            idx=set(cohort_queries(h).query('split==@c').origin)
            for key,g in list(r.items()):
                if key[:2]==(c,h):r[key]=g[g.origin.isin(idx)]
    for c,h,n in list(r):
        if c=='early' and ('later',h,n) in r:
            r['combined',h,n]=pd.concat([r[c,h,n],r['later',h,n]],ignore_index=True)
            sources['combined',h,n]=sources[c,h,n]
    return {k:g.sort_values('origin').set_index('origin',drop=False) for k,g in r.items() if len(g)},sources


def training(ledger):
    data=[]
    for f in ledger:
        if f['status']!='ok' or 'training_metrics' not in f:continue
        t=f['training_metrics']
        data.append({**{k:f.get(k) for k in ['batch','horizon','cohort','fold','model','training','inner_fit','valid','phase_prediction_variance','cutoff']},
                     **{k:v for k,v in t.items() if isinstance(v,(int,float))},'phase_sizes':'|'.join(map(str,t.get('phase_sample_sizes',[])))})
    a=pd.DataFrame(data);write('training-information-by-fold.csv',a)
    keys=['model','horizon','cohort']
    keyset=[c for c in a.select_dtypes(include='number') if c!='horizon']
    b=pd.concat([a,a.assign(cohort='combined')]).groupby(keys)[keyset].median().reset_index()
    write('training-information-medians.csv',b)
    return b


def fingerprint(p,spec):
    prev_config=pd.read_csv(V9/'historical-config-inventory.csv')
    prev_vec=pd.read_csv(V9/'historical-prediction-fingerprints.csv')
    for n,s in spec.items():
        digest=sha256(json.dumps({k:v for k,v in s.items() if k!='batch'},sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
        s['configuration_fingerprint']=digest
    rows=[]
    for (h,n),g in p.groupby(['horizon','model']):
        z=g.sort_values('origin')[['origin','endpoint','p','predicted_mean','predicted_median']].copy()
        for k in ['p','predicted_mean','predicted_median']:z[k]=z[k].round(10)
        rows.append({'model':n,'horizon':h,'n':len(z),'fingerprint':sha256(z.to_csv(index=False).encode()).hexdigest()})
    f=pd.DataFrame(rows);write('V10-prediction-fingerprints.csv',f)
    save('search-inventory.json',{'prior_registry_exact':int(prev_config.config_hash.nunique()),'prior_prediction_fingerprints':int(prev_vec.prediction_fingerprint.nunique()),
         'V10_registered_configs':len(spec),'V10_config_hashes':len({s['configuration_fingerprint'] for s in spec.values()}),
         'V10_scored_model_horizons':len(f),'V10_distinct_vector_hashes':int(f.fingerprint.nunique()),
         'claim':'Counts preserve previous and current inventories. Different vector schemas and windows prevent asserting a de-duplicated cumulative total.'})


def compare(groups,spec):
    comparisons=[];stress=[];incompatible=[];vectors={'early':[],'later':[],'combined':[]}
    standard=['HISTORY','NEUTRAL','REVERSION','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO','V8_MS_WINDOW',
              'V8_MS_ROLL','V6_MONTH_STATE','V6_MONTH_LAG1','V7_M_STATE_SHIFT5','V7_M_STATE_SHIFT21',
              'P_HIST','P_CLUSTER','J9_STATIC','J9_REL_SHRINK']
    for (c,h,n),g in groups.items():
        if n not in spec:continue
        parent=spec[n].get('parent');all_controls=list(dict.fromkeys([parent]+standard))
        for control in all_controls:
            b=groups.get((c,h,control))
            if b is None or n==control:continue
            idx=g.index.intersection(b.index)
            if len(idx)<1:continue
            a=g.loc[idx];b=b.loc[idx]
            if not a.endpoint.eq(b.endpoint).all() or not np.allclose(a.realized_return,b.realized_return,atol=1e-12,rtol=0):
                incompatible.append({'model':n,'control':control,'cohort':c,'horizon':h,'n':len(idx)})
                continue
            disjoint=len(nonoverlap(a.reset_index(drop=True)))
            for metric in ['brier','crps','log_loss','mae']:
                if metric not in b or not b[metric].notna().all() or not a[metric].notna().all():continue
                d=b[metric]-a[metric];record={'model':n,'baseline':control,'is_parent':control==parent,'cohort':c,
                        'horizon':h,'metric':metric,'n':len(idx),'disjoint_test_windows':disjoint,'gain':d.mean(),
                        'candidate':a[metric].mean(),'control':b[metric].mean()}
                comparisons.append(record)
                if h==5 and len(idx)>=35 and metric in ['brier','crps']:vectors[c].append((record,d))
                if metric not in ['brier','crps'] or control not in [parent,'HISTORY','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO','V8_MS_WINDOW']:continue
                if 'fold' in a:
                    for date in a.origin.str[:7].unique():
                        sub=d[a.origin.str[:7]!=date]
                        if len(sub):stress.append({**record,'test':'leave_query_month','key':date,'n':len(sub),'gain':sub.mean()})
                for k in [1,3,5,10]:
                    if len(d)>k:stress.append({**record,'test':'delete_best_origins','key':k,'n':len(d)-k,'gain':d.sort_values().iloc[:-k].mean()})
                for phase in range(h):
                    phase_dates=nonoverlap(a.iloc[phase:].reset_index(drop=True)).origin
                    if len(phase_dates):stress.append({**record,'test':'disjoint_evaluation_phase','key':phase,'n':len(phase_dates),'gain':d.loc[phase_dates].mean()})
    uncertainty={}
    for c,ds in vectors.items():
        keys=groups[c,5,'HISTORY'].origin.tolist()
        uncertainty[c]={'comparison_count':len(ds),'calendar_origins':len(keys),'critical_values':{}}
        for size in [5,10,15]:
            a,b,l,u,q=intervals([d for _,d in ds],keys,size);uncertainty[c]['critical_values'][size]=q
            for j,(row,_) in enumerate(ds):
                row[f'block{size}_adjusted_low']=a[j];row[f'block{size}_adjusted_high']=b[j]
                if size==10:row['block10_unadjusted_low']=l[j];row['block10_unadjusted_high']=u[j]
    save('paired-uncertainty.json',{'method':'2,000 shared circular block draws, max |standardized centered loss gain|',
         'scope':uncertainty,'monthly':'Point estimates and disjoint phases only. Small number of disjoint windows limits inference.','excluded_return_mismatches':incompatible})
    table=pd.DataFrame(comparisons);write('matched-comparisons.csv',table)
    write('incremental-information.csv',table[table.is_parent].sort_values(['cohort','horizon','metric','gain'],ascending=[True,True,True,False]))
    write('temporal-and-disjoint-stress.csv',pd.DataFrame(stress))
    return table


def summaries(groups,sources,spec,support,comparison):
    scores=[];calibration=[];buckets=[]
    full={('early',5):173,('later',5):92,('combined',5):265,('early',21):141,('later',21):76,('combined',21):217}
    for (c,h,n),g in groups.items():
        a,b=point(g.reset_index(drop=True));s=spec.get(n,{});kind='diagnostic' if s.get('diagnostic') or 'SHIFT' in n else 'retrospective'
        base={'cohort':c,'horizon':h,'model':n,'source':sources[c,h,n],'classification':kind,'batch':s.get('batch','reference'),
              'full_scope':len(g)==full[c,h],'parent':s.get('parent'),'registered_budget':s.get('budget')}
        scores.append({**base,**a});calibration.extend({**base,**r} for r in b)
        if 'train_bucket_brier' in g:
            for j in range(6):
                p=g[f'train_bucket{j}_p'];truth=g.train_bucket_actual.eq(j)
                buckets.append({**base,'bucket':j,'count':len(g),'mean_probability':p.mean(),'observed':truth.mean(),
                    'component_Brier':((truth-p)**2).mean(),'conditioning':'Train-specific 10/30/50/70/90 percentiles'})
    t=pd.DataFrame(scores).merge(support,on=['model','horizon','cohort'],how='left')
    write('leaderboard.csv',t.sort_values(['horizon','cohort','brier']))
    write('calibration-bins.csv',pd.DataFrame(calibration));write('training-return-buckets.csv',pd.DataFrame(buckets))
    full_case=t[t.full_scope&t.classification.eq('retrospective')];w=full_case[full_case.horizon.eq(5)]
    write('weekly-probability.csv',w[w.cohort.eq('combined')].sort_values('brier'))
    write('weekly-distribution.csv',w[w.cohort.eq('combined')].sort_values('crps'))
    write('earlier-leaderboard.csv',full_case[full_case.cohort.eq('early')].sort_values(['horizon','brier']))
    write('later-leaderboard.csv',full_case[full_case.cohort.eq('later')].sort_values(['horizon','brier']))
    write('monthly-leaderboard.csv',t[t.horizon.eq(21)].sort_values(['cohort','full_scope','brier'],ascending=[True,False,True]))
    write('small-sample-leaderboard.csv',t[t.registered_budget.le(126)&t.classification.eq('retrospective')].sort_values(['horizon','cohort','brier']))
    curves=t[t.batch.eq('finalcurve')].copy()
    cols=['model','horizon','cohort','n','training','overlap_effective_count','brier','crps','coverage80','width80','registered_budget']
    matched=comparison[comparison.model.str.startswith('LC_')&comparison.is_parent]
    write('learning-curves.csv',curves[cols].sort_values(['horizon','cohort','registered_budget','model']))
    write('learning-curve-matched.csv',matched.sort_values(['horizon','cohort','metric','model']))
    front=[];stable=[]
    for h in [5,21]:
        a=full_case[full_case.horizon.eq(h)].pivot(index='model',columns='cohort',values=['brier','crps','ECE','training','df','parameters'])
        for n in a.index:
            er=a.loc[n];row={'model':n,'horizon':h,'early_brier':er.get(('brier','early')),'later_brier':er.get(('brier','later')),
                'early_crps':er.get(('crps','early')),'later_crps':er.get(('crps','later')),'ECE':er.get(('ECE','combined')),
                'training':er.get(('training','combined')),'complexity':er.get(('df','combined'))}
            if pd.isna(row['complexity']):row['complexity']=er.get(('parameters','combined'))
            row['Brier_gap']=abs(row['early_brier']-row['later_brier'])
            delta=comparison[(comparison.model.eq(n))&comparison.horizon.eq(h)&comparison.cohort.eq('combined')&
                comparison.baseline.eq('HISTORY')&comparison.metric.eq('brier')]
            row['adjusted_lower_gain']=delta.block10_adjusted_low.iloc[0] if len(delta) else np.nan
            stable.append(row)
        z=pd.DataFrame(stable);z=z[z.horizon.eq(h)]
        dims=['early_brier','later_brier','early_crps','later_crps','ECE','training','complexity','Brier_gap']
        if h==5:dims+=['adjusted_lower_gain']
        z=z.dropna(subset=dims);v=z[dims].to_numpy(copy=True)
        if h==5:v[:,-1]*=-1
        for i,r in enumerate(z.to_dict('records')):
            if not np.any(np.all(v<=v[i]+1e-11,axis=1)&np.any(v<v[i]-1e-11,axis=1)):front.append(r)
    write('temporal-stability-leaderboard.csv',pd.DataFrame(stable).sort_values(['horizon','Brier_gap']))
    write('research-pareto.csv',pd.DataFrame(front))
    return t


def run():
    p,s,l=predictions();write('all-predictions.csv',p)
    fingerprint(p,s);save('experiment-registry.json',{'configurations':s,'attempts':l,'exposure':'Exposed 2025–2026 outcomes. Raw post-freeze acquisition stays in refresh.'})
    grouped,sources=group_data(p);support=training(l);comparison=compare(grouped,s)
    table=summaries(grouped,sources,s,support,comparison)
    print('Analyzed',len(p),'predictions;',len(comparison),'matched contrasts;',len(table),'ranked slices',flush=True)


def finish_rankings():
    p=pd.read_csv(OUT/'all-predictions.csv');reg=read('experiment-registry.json')
    grouped,sources=group_data(p);support=pd.read_csv(OUT/'training-information-medians.csv')
    comparison=pd.read_csv(OUT/'matched-comparisons.csv')
    table=summaries(grouped,sources,reg['configurations'],support,comparison)
    print('Analyzed',len(p),'predictions;',len(comparison),'matched contrasts;',len(table),'ranked slices',flush=True)


if __name__=='__main__':
    import sys
    (finish_rankings if '--finish-rankings' in sys.argv else run)()
