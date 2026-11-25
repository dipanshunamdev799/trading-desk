"""Matched evaluation and max-statistic block uncertainty on exposed history."""
from .common import *
from .engine import cohort_queries
from research.nifty_forecast_v10.analyze import nonoverlap,point
from research.nifty_forecast_v9.analyze import refs
from research.nifty_forecast_v8.analyze import intervals

BATCH=['breadth','memory','overlap','legacy','distribution','ensemble','repair','disjoint','ensemble-exact','international']
ANCHORS=['P_HIST','P_CLUSTER','P_ROT','P_STRUCTURE','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO','V8_MS_WINDOW','V8_MS_ROLL',
         'V6_MONTH_STATE','V6_MONTH_LAG1','V7_M_STATE_SHIFT5','V7_M_STATE_SHIFT21','J9_STATIC','J9_REL_SHRINK','J10_STRUCTURAL_BLEND',
         'J10_HISTORY_SHRINK','NEUTRAL','HISTORY','REVERSION','T_VOL_STUDENT','T_SIGNMAG']
SCORES=['brier','crps','log_loss','mae','median_mae','pinball','train_bucket_brier','abs_return_error','path_risk_abs_error']
STRESS=['P_CLUSTER_EQ','P_ROT_EQ','P_STRUCTURE_EQ','V8_R_RESIDUAL_EQ','V8_W_STRUCT_EMBARGO_EQ','B_ROT_EQ',
        'B_SPARSE_EQ','B_STUD_EQ','B_EQ_SIZE_RISK','M_SPREAD_85','M_USEFULNESS_85','M_DIVERSE_85','P_RECENT_SHRINK','O_ROT_BLOCKMEAN',
        'D_DERIV_RISK','D_EQ_STUDENT','D_EQ_TAIL','D_EQ_SIGNMAG','J11_FIXED_EQ','J11_FIXED_HIST','J11_STACK_CRPS',
        'J11_EQUAL']
SCOPES=['early','later','combined']


def config():
    frames=[];spec={};ledger=[]
    for b in BATCH:
        reg=read(f'{b}-registry.json')
        spec.update({n:{**v,'batch':b} for n,v in reg['models'].items()})
        try:frames.append(pd.read_csv(OUT/f'{b}-predictions.csv'))
        except pd.errors.EmptyDataError:pass
        ledger.extend({'batch':b,**x} for x in read(f'{b}-ledger.json'))
    p=pd.concat(frames,ignore_index=True);assert not p.duplicated(['model','horizon','origin']).any()
    save('registry.json',{'configurations':spec,'attempts':ledger,'chronology':'Frozen 17 November 2026; exposed 2025–2026 research only.'})
    write('all-predictions.csv',p)
    return p,spec,ledger


def groups(p):
    a=refs()
    v9=pd.read_csv(V9/'all-predictions.csv')
    for k,g in v9[v9.model.isin(ANCHORS)].groupby(['cohort','horizon','model']):
        if k[0] in SCOPES[:2]:a[k]=g
    v10=pd.read_csv(V10/'all-predictions.csv')
    for k,g in v10[v10.model.isin(ANCHORS+['BASE_ROTATION','BASE_NATIVE','BASE10','S_ELASTIC','N_EQ_OFFICIAL','C85_RECENT','C85_SPREAD','C85_EARLIEST','D_DERIV_RAW','DATED_FUTURES','DATED_STRADDLE'])].groupby(['cohort','horizon','model']):
        a[k]=g
    for k,g in p.groupby(['cohort','horizon','model']):a[k]=g
    for c,h,n in list(a):
        if c=='early' and ('later',h,n) in a:a['combined',h,n]=pd.concat([a[c,h,n],a['later',h,n]],ignore_index=True)
    return {k:f.sort_values('origin').reset_index(drop=True) for k,f in a.items() if len(f) and 'endpoint' in f}


def support(ledger):
    rows=[]
    for f in ledger:
        if f['status']=='ok' and 'training' in f:
            rows.append({k:f[k] for k in ['horizon','cohort','model','training','fold']}|
              {k:v for k,v in f.get('support',{}).items() if isinstance(v,(int,float))})
    df=pd.DataFrame(rows);write('training-support-by-fold.csv',df)
    full=pd.concat([df,df.assign(cohort='combined')],ignore_index=True)
    return full.groupby(['horizon','cohort','model'])[full.select_dtypes('number').columns.difference(['horizon'])].median().reset_index()


def summarize(g,spec,stats):
    output=[];buckets=[];calibration=[]
    target={('early',5):173,('later',5):92,('combined',5):265,('early',21):141,('later',21):76,('combined',21):217}
    for (c,h,n),a in g.items():
        s=spec.get(n,{});m,q=point(a)
        for field in ['abs_return_error','path_risk_abs_error']:
            if field in a and a[field].notna().all():m[field]=a[field].mean()
        info={'cohort':c,'horizon':h,'model':n,'coverage':len(a)==target[c,h],'family':s.get('batch','frozen'),
              'diagnostic':s.get('diagnostic',False) or 'SHIFT' in n,'parent':s.get('parent'),
              'budget':s.get('budget')}
        output.append({**info,**m});calibration.extend({**info,**b} for b in q)
        if 'train_bucket0_p' in a:
            for j in range(6):
                observed=a.train_bucket_actual.eq(j)
                pred=a[f'train_bucket{j}_p']
                buckets.append({**info,'bucket':j,'n':len(a),'expected':pred.mean(),'actual':observed.mean(),'brier':((pred-observed)**2).mean()})
    m=pd.DataFrame(output).merge(stats,on=['horizon','cohort','model'],how='left')
    write('leaderboard.csv',m.sort_values(['horizon','cohort','brier']))
    write('training-return-buckets.csv',pd.DataFrame(buckets));write('calibration-bins.csv',pd.DataFrame(calibration))
    return m


def all_compares(g,spec):
    # Convert dates to arrays once. Calculate differences only on equal-basis realized endpoints.
    index={k:a.origin.to_numpy() for k,a in g.items()}
    views={k:{c:a[c].to_numpy() for c in a.columns} for k,a in g.items()}
    contrasts=[];stress=[];sets={c:[] for c in SCOPES};broken=[]
    for key,a in views.items():
        c,h,n=key
        if n not in spec:continue
        parent=spec[n].get('parent')
        for baseline in dict.fromkeys([parent]+ANCHORS):
            key2=c,h,baseline
            if key2 not in views or baseline==n:continue
            b=views[key2]
            origins,i,j=np.intersect1d(index[key],index[key2],assume_unique=True,return_indices=True)
            if not len(i):continue
            if not np.array_equal(a['endpoint'][i],b['endpoint'][j]) or not np.allclose(a['realized_return'][i],b['realized_return'][j],atol=1e-12,rtol=0):
                broken.append({'horizon':h,'cohort':c,'model':n,'baseline':baseline,'matched_rows':len(i)});continue
            for score in SCORES:
                if score not in a or score not in b:continue
                av=a[score][i];bv=b[score][j]
                if not (np.isfinite(av).all() and np.isfinite(bv).all()):continue
                gain=bv-av
                row={'cohort':c,'horizon':h,'model':n,'baseline':baseline,'is_parent':parent==baseline,
                     'metric':score,'n':len(i),'gain':float(gain.mean()),'candidate':float(av.mean()),'control':float(bv.mean())}
                contrasts.append(row)
                if h==5 and score in ['brier','crps'] and len(i)>=35:
                    sets[c].append((row,pd.Series(gain,index=origins)))
                if n in STRESS and score in ['brier','crps'] and baseline in [parent,'J10_STRUCTURAL_BLEND','J10_HISTORY_SHRINK','NEUTRAL']:
                    ends=a['endpoint'][i]
                    for phase in range(h):
                        keep=[];step=phase
                        while step<len(origins):
                            keep.append(step);step=max(step+1,np.searchsorted(origins,ends[step]))
                        if keep:stress.append({**row,'test':'disjoint phase','level':phase,'n':len(keep),'gain':float(gain[keep].mean())})
                    month=np.asarray([d[:7] for d in origins])
                    for label in np.unique(month):
                        keep=month!=label
                        if np.any(keep):stress.append({**row,'test':'leave query month','level':label,'n':int(keep.sum()),'gain':float(gain[keep].mean())})
                    if len(gain)>10:
                        for k in [1,3,5,10]:
                            stress.append({**row,'test':'remove best origins','level':k,'n':len(gain)-k,'gain':float(np.sort(gain)[:-k].mean())})
    audit={}
    for c,ls in sets.items():
        dates=index[c,5,'NEUTRAL'].tolist();audit[c]={'contrasts':len(ls),'origins':len(dates),'critical':{}}
        for size in [5,10,15]:
            a,b,lo,hi,k=intervals([x for _,x in ls],dates,size);audit[c]['critical'][size]=k
            for j,(r,_) in enumerate(ls):
                r[f'low{size}']=a[j];r[f'high{size}']=b[j]
                if size==10:r['unadjusted_low10']=lo[j];r['unadjusted_high10']=hi[j]
    save('comparison-uncertainty.json',{'scope':audit,'comparisons_excluded_for_outcome_mismatch':broken,
              'procedure':'2000 shared circular block resamples. Maximum standardized error across all weekly paired Brier and CRPS contrasts in the scope.',
              'monthly':'Matched point estimates and disjoint sensitivity. Tight interval estimates not reported.'})
    frame=pd.DataFrame(contrasts);write('matched-comparisons.csv',frame);write('stress-comparisons.csv',pd.DataFrame(stress))
    write('incremental-comparisons.csv',frame[frame.is_parent])
    return frame


def breadth_conditions(groups):
    state=matrix('selection-states.csv',V10)
    b=matrix('matrices/BREADTH.csv',OUT)
    rr=matrix('matrices/rotation.csv',V10)
    flags={'narrow_rise':rr.p_ret5.gt(0)&b.b5_50.lt(0),'broad_rise':rr.p_ret5.gt(0)&b.b5_50.gt(0),
           'rising_participation':b.b5_500.gt(0),'high_volatility':state.s_vol.gt(state.s_vol.rolling(63,min_periods=20).median().shift()),
           'bank_rotation_positive':state.s_bank.gt(0)}
    rows=[]
    for h in [5,21]:
        for c in SCOPES:
            base=groups[c,h,'B_ROT'].set_index('origin')
            for n in ['B_ROT_EQ','B_PERSIST','B_FIN_INTERACT','L_EQ_CONC','P_ROT_EQ','P_CLUSTER_EQ']:
                a=groups[c,h,n].set_index('origin')
                for key,flag in flags.items():
                    for k in [False,True]:
                        ix=a.index.intersection(base.index)
                        ix=ix[flag.reindex(ix).eq(k)]
                        if not len(ix):continue
                        aa=a.loc[ix];bb=base.loc[ix]
                        rows.append({'horizon':h,'cohort':c,'model':n,'state':key,'condition':k,'n':len(ix),
                           'outcome_up_fraction':aa.outcome.mean(),'mean_return':aa.realized_return.mean(),
                           'expected_abs':aa.expected_abs.mean(),'Brier_gain_vs_B_ROT':(bb.brier-aa.brier).mean(),
                           'CRPS_gain_vs_B_ROT':(bb.crps-aa.crps).mean()})
    write('breadth-mechanism-slices.csv',pd.DataFrame(rows))


def frontier(m,compare):
    front=[];curves=[]
    for h in [5,21]:
        a=m[m.horizon.eq(h)&m.coverage&~m.diagnostic]
        metrics=a.pivot(index='model',columns='cohort',values=['brier','crps','ECE','training','df']).dropna(subset=[('brier','early'),('brier','later'),('crps','early'),('crps','later')])
        dims=[('brier','early'),('brier','later'),('crps','early'),('crps','later'),('ECE','combined')]
        z=metrics[dims].to_numpy();rows=[]
        for j,n in enumerate(metrics.index):
            if np.any(np.all(z<=z[j]+1e-12,axis=1)&np.any(z<z[j]-1e-12,axis=1)):continue
            r=metrics.loc[n];rows.append({'horizon':h,'model':n,'early_brier':r['brier','early'],'later_brier':r['brier','later'],
                         'early_crps':r['crps','early'],'later_crps':r['crps','later'],'ECE':r['ECE','combined'],'median_train':r['training','combined'],'df':r['df','combined']})
        front.extend(rows)
        v=metrics.dropna(subset=[('training','combined'),('df','combined')])
        dims2=dims+[('training','combined'),('df','combined')]
        z=v[dims2].to_numpy()
        for j,n in enumerate(v.index):
            if np.any(np.all(z<=z[j]+1e-12,axis=1)&np.any(z<z[j]-1e-12,axis=1)):continue
            r=v.loc[n]
            curves.append({'horizon':h,'model':n,'earlier_brier':r['brier','early'],'later_brier':r['brier','later'],
              'earlier_crps':r['crps','early'],'later_crps':r['crps','later'],'ECE':r['ECE','combined'],
              'median_train':r['training','combined'],'df':r['df','combined']})
    write('pareto.csv',pd.DataFrame(front));write('pareto-efficiency.csv',pd.DataFrame(curves))
    c=compare[compare.model.str.startswith('M_')&compare.is_parent];write('memory-exact-budget-comparisons.csv',c)


def run():
    p,s,ledger=config();g=groups(p);stats=support(ledger);summary=summarize(g,s,stats)
    compare=all_compares(g,s);frontier(summary,compare);breadth_conditions(g)
    print(len(p),'forecasts',len(compare),'exact comparisons',len(s),'models',flush=True)


if __name__=='__main__':run()
