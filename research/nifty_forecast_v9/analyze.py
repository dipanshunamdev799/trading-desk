"""Matched cohorts, selection statistics, Pareto fronts and uncertainty."""
from .common import *
from research.nifty_forecast_v8.analyze import collect_refs, intervals
from research.nifty_forecast_v6.common import V3, V4
from research.nifty_forecast_v5.analyze import summary
from research.nifty_forecast_v3.experiment import nonoverlap, effective_n
from .run_models import cohort_queries


def refs():
    out={('later',h,n):g for (h,n),g in collect_refs().items()}
    v8=pd.read_csv(V8/'all-predictions.csv')
    for n in ['R_RESIDUAL','A_STRUCTURE_LEVEL','A_STRUCTURE_CHANGE','W_STRUCT_EMBARGO','G_ROT_ELASTIC','MS_WINDOW','MS_ROLL','M_STATE_SMOOTH','E_HIST','E_FULL_ROT','E_SMALL_126']:
        for (c,h),g in v8[v8.model==n].groupby(['cohort','horizon']):out[('later' if c=='primary' else c,h,'V8_'+n)]=g
    v3=pd.read_csv(V3/'predictions.csv');v3=v3[v3.split=='development_exposed']
    d4=pd.read_csv(V4/'distribution-predictions.csv');d4=d4[d4.split=='development_exposed']
    for h in [5,21]:
        allowed=set(cohort_queries(h).query('split=="early"').origin)
        for name in ['B00_empirical','M05_lgbm','A00_sector','Z_neutral']:
            g=v3[(v3.horizon==h)&(v3.model==name)&v3.origin.isin(allowed)]
            if len(g):out['early',h,'V4_'+name]=g
        for name in ['D02_student_shrunk','D03_residual_shrunk']:
            g=d4[(d4.horizon==h)&(d4.model==name)&d4.origin.isin(allowed)]
            if len(g):out['early',h,'V4_'+name]=g
    return out


def specs():
    p=[];reg={};led=[]
    for path in sorted(OUT.glob('*-registry.json')):
        name=path.name.removesuffix('-registry.json');d=read(path.name)
        if 'configuration' not in d:continue
        data=pd.read_csv(OUT/f'{name}-predictions.csv');p.append(data)
        reg.update({k:{**v,'batch':name} for k,v in d['configuration'].items()});led.extend({'batch':name,**r} for r in read(f'{name}-ledger.json'))
    save('experiment-registry.json',{'specifications':reg,'attempts':led,'reproduction':'Separate exact replays and inherited controls',
         'exposure':'All V9 fits are retrospective. Timing and sample size put ahead of point ranking.'})
    return pd.concat(p,ignore_index=True),reg,led


def metrics(z):
    g=z.copy().sort_values('origin')
    if 'bucket_y' not in g or g.bucket_y.isna().any():g['bucket_y']=np.digitize(g.realized_return,[-.05,-.02,-.005,.005,.02,.05])
    h=int(g.horizon.iloc[0]);return {'horizon':h,'disjoint':len(nonoverlap(g)),'ESS':effective_n(g.realized_return,h),**summary(g)}


def run():
    p,reg,ledger=specs();write('all-predictions.csv',p);assert not p.duplicated(['horizon','cohort','model','origin']).any()
    ref=refs();groups={key:g.copy() for key,g in p.groupby(['cohort','horizon','model'])}
    by=[];cmp=[];vectors={'early':[],'later':[]};inc=[];stress=[];regimes=[]
    state=matrix('state-context.csv',OUT);thresholds=state.rolling(63,min_periods=20).median().shift();slice_context={
       'volatility_high':state.s_vol>thresholds.s_vol,'uptrend':state.s_trend>0,'broad_participation':state.s_breadth>.5,
       'concentrated':state.s_concentration>thresholds.s_concentration,'global_stress':state.s_global_vol>0,
       'financial_spread_positive':state.s_bank>0,'high_liquidity':state.s_liquidity>0}
    for (cohort,h,n),g in ref.items():by.append({'cohort':cohort,'model':n,'status':'frozen reference',**metrics(g)})
    for (cohort,h,n),g in groups.items():
        meta=reg[n];state_desc='diagnostic' if meta.get('diagnostic') else 'retrospective';by.append({'cohort':cohort,'model':n,'status':state_desc,'batch':meta['batch'],'parent':meta['parent'],**metrics(g)})
        a=g.set_index('origin').sort_index();parent=meta['parent'];b=groups.get((cohort,h,parent),ref.get((cohort,h,parent)))
        if b is not None and n!=parent:
            common=a.index.intersection(b.origin);b=b.set_index('origin').loc[common]
            for metric in ['brier','crps','mae']:
                if len(common):inc.append({'cohort':cohort,'horizon':h,'model':n,'parent':parent,'metric':metric,'n':len(common),'gain':(b[metric]-a.loc[common,metric]).mean()})
            if n in ['P_ROT','P_STRUCTURE','P_CLUSTER','T_EW90','T_KALMAN','F_BANK_RESID63','F_FINANCIAL_PANEL','I_AR','T_GLOBAL_LAW','X_ROT_PANEL','J9_GLOBAL_GATE','J9_REL_SHRINK']:
                for key,series in slice_context.items():
                    mask=series.reindex(common).dropna()
                    for label,group in mask.groupby(mask):
                        z=a.loc[group.index];control=b.loc[group.index]
                        regimes.append({'cohort':cohort,'horizon':h,'model':n,'parent':parent,'slice':key,'state':bool(label),'n':len(z),
                                        'disjoint':len(nonoverlap(z.reset_index())),'Brier_gain':(control.brier-z.brier).mean(),
                                        'CRPS_gain':(control.crps-z.crps).mean(),'coverage80':z.coverage80.mean(),'width80':z.width80.mean()})
        candidates={key:g for key,g in ref.items() if key[:2]==(cohort,h)}
        if (cohort,h,'P_HIST') in groups:candidates[cohort,h,'P_HIST']=groups[cohort,h,'P_HIST']
        for (_,_,base),control in candidates.items():
            common=a.index.intersection(control.origin)
            if not len(common) or n==base:continue
            b=control.set_index('origin').loc[common];z=a.loc[common]
            np.testing.assert_allclose(b.realized_return,z.realized_return,atol=1e-12)
            np.testing.assert_array_equal(b.endpoint,z.endpoint)
            for metric in ['brier','crps','mae']:
                delta=b[metric]-z[metric];entry={'cohort':cohort,'horizon':h,'model':n,'baseline':base,'metric':metric,'n':len(delta),'gain':float(delta.mean())}
                cmp.append(entry)
                if h==5 and cohort in vectors and len(delta)>=35:vectors[cohort].append((entry,delta))
                if base not in ['P_HIST','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO','V8_MS_WINDOW'] or metric=='mae':continue
                parts=[]
                for month in z.fold.unique():parts.append(('leave_month',month,delta[z.fold!=month]))
                for k in [1,3,5,10]:parts.append(('omit_best',k,delta.sort_values().iloc[:-k]))
                for phase in range(5):parts.append(('disjoint_phase',phase,delta.loc[nonoverlap(z.reset_index().iloc[phase:]).origin]))
                for kind,key,d in parts:
                    if len(d):stress.append({**entry,'test':kind,'phase_or_period':key,'n':len(d),'gain':float(d.mean())})
    u={}
    for cohort,ls in vectors.items():
        dates=sorted(groups[cohort,5,'P_HIST'].origin)
        u[cohort]={'contrasts':len(ls),'n':len(dates),'block_critical_values':{}}
        for size in [5,10,15]:
            lo,hi,plo,phi,k=intervals([d for _,d in ls],dates,size);u[cohort]['block_critical_values'][size]=k
            for j,(r,_) in enumerate(ls):
                r[f'adjusted95_block{size}']=[float(lo[j]),float(hi[j])]
                if size==10:r['raw95_block10']=[float(plo[j]),float(phi[j])]
    save('uncertainty.json',{'method':'2,000 shared circular block draws with max standardized deviations. Separate weekly cohort families. No CIs for small monthly windows or 4-observation refresh.',**u})
    save('benchmark-comparisons.json',cmp);write('benchmark-comparisons.csv',pd.DataFrame(cmp));write('parent-increments.csv',pd.DataFrame(inc));write('stability.csv',pd.DataFrame(stress));write('conditional-calibration.csv',pd.DataFrame(regimes))
    combined=[]
    for (cohort,h,n),e in groups.items():
        if cohort!='early' or ('later',h,n) not in groups:continue
        l=groups['later',h,n];target=(173,92) if h==5 else (141,76)
        if (len(e),len(l))!=target:continue
        g=pd.concat([e,l]);detail=metrics(g)
        combined.append({**detail,'model':n,'status':'diagnostic' if reg[n].get('diagnostic') else 'retrospective','early_Brier':e.brier.mean(),'late_Brier':l.brier.mean(),
                         'early_CRPS':e.crps.mean(),'late_CRPS':l.crps.mean(),'abs_Brier_cohort_gap':abs(e.brier.mean()-l.brier.mean())})
    union=pd.DataFrame(combined);front=[]
    for h,g in union[union.status=='retrospective'].groupby('horizon'):
        v=g[['early_Brier','late_Brier','early_CRPS','late_CRPS']].to_numpy()
        for i,r in enumerate(g.to_dict('records')):
            if not np.any(np.all(v<=v[i]+1e-12,axis=1)&np.any(v<v[i]-1e-12,axis=1)):front.append(r)
    write('combined-cohort-leaderboard.csv',union.sort_values(['horizon','brier']));write('temporal-pareto.csv',pd.DataFrame(front))
    save('metrics.json',by);m=pd.DataFrame([{k:v for k,v in r.items() if not isinstance(v,(list,dict))} for r in by]);
    write('direction-leaderboard.csv',m.sort_values(['cohort','horizon','brier']));write('distribution-leaderboard.csv',m.sort_values(['cohort','horizon','crps']))
    lb=pd.DataFrame(stress);main=lb[(lb.test=='leave_month')&(lb.metric=='brier')&(lb.baseline=='P_HIST')].groupby(['cohort','horizon','model']).gain.agg(['min','max']).reset_index()
    write('temporal-stability-leaderboard.csv',m.merge(main,on=['cohort','horizon','model'],how='left').sort_values(['cohort','horizon','min'],ascending=[True,True,False]))
    rel=pd.read_csv(OUT/'reliability-targets.csv');rstats=[];slices=[]
    for (cohort,h),g in rel.groupby(['cohort','horizon']):
        ready=g[g.gate_available].copy();raw={'cohort':cohort,'horizon':h,'n':len(g),'assessed':len(ready)}
        for a,b in [('predicted_brier','actual_brier'),('predicted_crps','actual_crps'),('predicted_correctness','actual_correct'),('predicted_interval_coverage','actual_coverage80'),('mahalanobis','actual_brier'),('expert_p_disagreement','actual_brier'),('parameter_uncertainty','actual_crps')]:
            raw[f'IC_{a}']=float(ready[a].corr(ready[b],method='spearman')) if len(ready)>3 else None
        raw['dom_vol_mae']=abs(ready.predicted_dom_vol-ready.realized_vol).mean();raw['global_vol_mae']=abs(ready.predicted_global_vol-ready.realized_vol).mean()
        rstats.append(raw)
        slice_defs={'all_assessed':np.ones(len(ready),bool),'selected':ready.selected,'abstain':~ready.selected,
                    'unfamiliar':ready.mahalanobis>ready.ood_threshold,'familiar':ready.mahalanobis<=ready.ood_threshold}
        rr=groups[cohort,h,'P_ROT'].set_index('origin')
        bullish=rr.p.reindex(ready.origin).to_numpy()>=.5;slice_defs['selected_bullish']=ready.selected&bullish;slice_defs['selected_bearish']=ready.selected&~bullish
        for name,mask in slice_defs.items():
            f=ready[mask];p0=rr.loc[f.origin].reset_index()
            if len(f):slices.append({'cohort':cohort,'horizon':h,'selection':name,'n':len(f),'coverage_of_cohort':len(f)/len(g),
                             'disjoint':len(nonoverlap(p0)),'accuracy':f.actual_correct.mean(),'brier':f.actual_brier.mean(),'crps':f.actual_crps.mean(),
                             'matched_history_Brier':f.history_brier.mean(),'matched_history_CRPS':f.history_crps.mean(),'interval80_coverage':f.actual_coverage80.mean()})
    write('reliability-comparison.csv',pd.DataFrame(rstats));write('selective-performance.csv',pd.DataFrame(slices))
    # Compare dependence between the expert predictions and their errors in the identical cohorts.
    pairs=[]
    for h in [5,21]:
        for c in ['early','later']:
            frames=[g.assign(key=n) for (cohort,hh,n),g in (ref|groups).items() if h==hh and c==cohort and (n.startswith('P_') or n.startswith('V8_') or n in ['I03_nosize','T_ROT_DOMESTIC','V6_BRIER'])]
            df=pd.concat(frames);df['error']=df.predicted_mean-df.realized_return
            for key in ['p','error','brier','crps']:
                cor=df.pivot_table(index='origin',columns='key',values=key).corr(min_periods=20)
                for i,a in enumerate(cor.columns):
                    for b in cor.columns[i+1:]:pairs.append({'horizon':h,'cohort':c,'metric':key,'a':a,'b':b,'corr':cor.loc[a,b]})
    write('prediction-and-error-correlations.csv',pd.DataFrame(pairs))
    print('Analyzed',len(p),'forecast rows,',len(groups),'cohort/horizon/model cells,',len(cmp),'matched contrasts',flush=True)


if __name__=='__main__':run()
