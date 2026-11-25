"""Exact-origin benchmarks, event diagnostics and dependence-aware score comparisons."""
from .common import *
from .market import MAIN
from research.nifty_forecast_v9.analyze import refs
from research.nifty_forecast_v10.analyze import nonoverlap,point
from research.nifty_forecast_v8.analyze import intervals
from research.nifty_forecast_v9.run_models import cohort_queries

BATCH=['phase','market','priced','ensemble']
SCOPES=['early','later','combined']
PRIMARY=[
 'P_HIST','P_CLUSTER','V8_R_RESIDUAL','V8_W_STRUCT_EMBARGO','V6_MONTH_STATE','V6_MONTH_LAG1','V8_MS_WINDOW','V8_MS_ROLL',
 'J10_STRUCTURAL_BLEND','J10_HISTORY_SHRINK','O_NATIVE_PHASE0','B_CHANGE','V8_W_STRUCT_EMBARGO_EQ','J11_BREADTH_ALL',
 'J11_BREADTH_ALL_HIST','J11_EXCLUDE_B_ROT','NEUTRAL','V12_RV_SCALE','V12_RV_PATH','Q12_RAW',
]
METRICS=['brier','crps','log_loss','mae','median_mae','pinball','train_bucket_brier','path_volatility_mae','absolute_return_error']
STRESS=['V12_IV_SCALE','V12_IV_NEUTRAL','V12_IV_ASYMMETRY','V12_JOINT_IV','V12_JOINT_LOCATION','V12_GLOBAL_SCALE',
        'V12_EVENT_IV','P12_Q_PHYSICAL_MIX','P12_Q_TILT','Q12_RAW','J12_PHASE_MARKET','J12_Q_STACK','J12_STACK_CRPS',
        'PH_NATIVE_PHASE_MIXTURE','PH_NATIVE_00','PH_NATIVE_06','PH_NATIVE_POOLED','PH_ROT_PHASE_MIXTURE']


def gather():
    p=[];model={};ledger=[]
    for b in BATCH:
        r=read(f'{b}-registry.json');model.update({n:{**s,'batch':b} for n,s in r['models'].items()})
        p.append(pd.read_csv(OUT/f'{b}-predictions.csv'))
        ledger.extend({'batch':b,**row} for row in read(f'{b}-ledger.json'))
    a=pd.concat(p,ignore_index=True)
    assert not a.duplicated(['horizon','model','origin']).any()
    write('all-predictions.csv',a)
    save('registry.json',{'configurations':model,'attempts':ledger,'scope':'Frozen exposed 2025–2026 cohorts. Market-price Q laws and their diagnostics are identified separately.'})
    return a,model,ledger


def group_data(p):
    g=refs()
    names=PRIMARY+['P_ROT','J9_STATIC','J9_REL_SHRINK','REVERSION','HISTORY','T_VOL_STUDENT','T_SIGNMAG','O_NATIVE_PHASE1',
                  'O_NATIVE_STAGGERED','M_RECENT_85','M_SPREAD_85','M_EARLIEST_85','V8_R_RESIDUAL_EQ','D_NATIVE_SIGNMAG']
    for source in [V9,V10,V11]:
        a=pd.read_csv(source/'all-predictions.csv')
        for k,x in a[a.model.isin(names)&a.cohort.isin(SCOPES[:2])].groupby(['cohort','horizon','model']):g[k]=x
    for k,x in p.groupby(['cohort','horizon','model']):g[k]=x
    for c,h,k in list(g):
        if c=='early' and ('later',h,k) in g:g['combined',h,k]=pd.concat([g[c,h,k],g['later',h,k]],ignore_index=True)
    return {k:v.sort_values('origin').reset_index(drop=True) for k,v in g.items() if len(v) and 'end' not in k and 'endpoint' in v}


def summary(g,registry,ledger):
    rows=[];bucket=[];cal=[];info=[]
    target={('early',5):173,('later',5):92,('combined',5):265,('early',21):141,('later',21):76,('combined',21):217}
    for r in ledger:
        if r['status']!='ok' or 'support' not in r:continue
        info.append({**{k:r[k] for k in ['model','horizon','cohort','fold','training','member_location_sd','member_coefficient_sd']},**r['support']})
    write('phase-training-support.csv',pd.DataFrame(info))
    for (c,h,n),a in g.items():
        s=registry.get(n,{})
        base={'horizon':h,'cohort':c,'model':n,'family':s.get('batch','frozen'),'full_scope':len(a)==target[c,h],
              'diagnostic':s.get('diagnostic',False) or n.startswith(('Q12','V7_M_STATE_SHIFT','V8_MS_ROLL')),
              'parent':s.get('parent')}
        scores,bins=point(a)
        for name in ['path_volatility_mae','absolute_return_error']:
            if name in a and a[name].notna().all():scores[name]=a[name].mean()
        if 'p_below_minus2' in a:
            gap=(a.realized_return<-.02).astype(float)
            scores['fixed_down2_tail_brier']=float(((a.p_below_minus2-gap)**2).mean())
            scores['fixed_down2_forecast_mass']=float(a.p_below_minus2.mean())
            scores['fixed_down2_observed']=float(gap.mean())
        rows.append({**base,**scores})
        cal.extend({**base,**r} for r in bins)
        if 'train_bucket_cut0' in a:
            for j in range(6):
                actual=a.train_bucket_actual.eq(j);f=a[f'train_bucket{j}_p']
                bucket.append({**base,'bucket':j,'n':len(a),'probability':f.mean(),'observed':actual.mean(),'brier':((actual-f)**2).mean()})
    result=pd.DataFrame(rows)
    write('leaderboard.csv',result.sort_values(['horizon','cohort','brier']))
    write('calibration-bins.csv',pd.DataFrame(cal));write('training-bucket-calibration.csv',pd.DataFrame(bucket))
    for h,label in [(5,'weekly'),(21,'monthly')]:
        select=result[result.horizon.eq(h)&~result.diagnostic]
        for score,stem in [('brier','probability'),('crps','distribution')]:
            write(f'{label}-{stem}-ranking.csv',select.sort_values(['cohort','full_scope',score],ascending=[True,False,True]))
    scale=result[result.path_volatility_mae.notna()|result.absolute_return_error.notna()]
    write('volatility-and-movement-ranking.csv',scale.sort_values(['horizon','cohort','path_volatility_mae','absolute_return_error']))
    return result


def disjoint(origins,ep,phase):
    j=phase
    keep=[]
    while j<len(origins):
        keep.append(j)
        j=max(j+1,np.searchsorted(origins,ep[j]))
    return keep


def comparison(g,reg):
    arrays={k:{c:v[c].to_numpy() for c in v} for k,v in g.items()}
    contrast=[];stress=[];bad=[]
    weekly={c:[] for c in SCOPES}
    magnitudes={c:[] for c in SCOPES}
    for k,a in arrays.items():
        c,h,n=k
        if n not in reg:continue
        parent=reg[n].get('parent')
        for ref in dict.fromkeys([parent]+PRIMARY):
            if (c,h,ref) not in arrays or ref==n:continue
            b=arrays[c,h,ref]
            days,l,r=np.intersect1d(a['origin'],b['origin'],assume_unique=True,return_indices=True)
            if not len(days):continue
            if not np.array_equal(a['endpoint'][l],b['endpoint'][r]) or not np.allclose(a['realized_return'][l],b['realized_return'][r],atol=1e-12,rtol=0):
                bad.append({'horizon':h,'cohort':c,'model':n,'baseline':ref,'matched_rows':len(days)})
                continue
            ep=a['endpoint'][l]
            units=len(disjoint(days,ep,0))
            for metric in METRICS:
                if metric not in a or metric not in b:continue
                la,lb=a[metric][l],b[metric][r]
                if not(np.isfinite(la).all() and np.isfinite(lb).all()):continue
                gain=lb-la
                t={'horizon':h,'cohort':c,'model':n,'baseline':ref,'is_parent':ref==parent,'metric':metric,
                   'n':len(days),'disjoint':units,'candidate':la.mean(),'control':lb.mean(),'gain':gain.mean()}
                contrast.append(t)
                if h==5 and len(days)>=35 and metric in ['brier','crps']:weekly[c].append((t,pd.Series(gain,index=days)))
                if h==5 and len(days)>=35 and metric in ['path_volatility_mae','absolute_return_error']:
                    magnitudes[c].append((t,pd.Series(gain,index=days)))
                if n not in STRESS or metric not in ['brier','crps'] or ref not in [parent,'NEUTRAL','J11_EXCLUDE_B_ROT','O_NATIVE_PHASE0']:continue
                for phase in range(h):
                    keep=disjoint(days,ep,phase)
                    if keep:stress.append({**t,'test':'disjoint evaluation phase','level':phase,'n':len(keep),'gain':gain[keep].mean()})
                months=np.array([d[:7] for d in days])
                for date in np.unique(months):
                    keep=months!=date
                    if np.any(keep):stress.append({**t,'test':'leave evaluation month','level':date,'n':keep.sum(),'gain':gain[keep].mean()})
                for count in [1,3,5,10]:
                    if len(gain)>count:stress.append({**t,'test':'remove best origins','level':count,'n':len(gain)-count,
                                                      'gain':np.sort(gain)[:-count].mean()})
    def bands(family):
        audit={}
        for c,values in family.items():
            days=arrays[c,5,'NEUTRAL']['origin'].tolist()
            audit[c]={'contrasts':len(values),'calendar_dates':len(days),'max_t':{}}
            for block in [5,10,15]:
                with np.errstate(divide='ignore',invalid='ignore'):
                    lo,hi,p_lo,p_hi,k=intervals([d for _,d in values],days,block)
                audit[c]['max_t'][str(block)]=k
                for j,(row,_) in enumerate(values):
                    row.update({f'low{block}':lo[j],f'high{block}':hi[j]})
                    if block==10:row.update(pointwise_low10=p_lo[j],pointwise_high10=p_hi[j])
        return audit
    audit=bands(weekly)
    risk_audit=bands(magnitudes)
    a=pd.DataFrame(contrast)
    write('matched-comparisons.csv',a)
    write('incremental-value.csv',a[a.is_parent])
    write('phase-and-episode-stress.csv',pd.DataFrame(stress))
    save('paired-uncertainty.json',{'scopes':audit,'risk_and_magnitude_scopes':risk_audit,'source_mismatch_rejections':bad,
        'method':'2,000 shared circular block draws by scope. Separate maxima for weekly Brier/CRPS and annualized path-volatility/absolute-move error contrasts with at least 35 exact origins.',
        'monthly':'Disjoint phase and deletion metrics. No tight sampling intervals inferred from 11 disjoint windows.'})
    return a


def event_stats(g):
    m=pd.read_csv(OUT/'event-origin-states.csv')
    names=['V12_STAT','V12_HIST','V12_EVENT_HISTORY','V12_EVENT_RV','V12_EVENT_IV','V12_EVENT_IV_INCREMENT','V12_IV_SCALE',
           'V12_JOINT_IV','P12_Q_PHYSICAL_MIX']
    rows=[]
    for h in [5,21]:
        for coh in SCOPES:
            event=m[m.horizon.eq(h)&(True if coh=='combined' else m.cohort.eq(coh))]
            for n in names:
                if (coh,h,n) not in g:continue
                a=g[coh,h,n].set_index('origin',drop=False)
                for kind,group in event.groupby('event'):
                    for flag in [False,True]:
                        dates=a.index.intersection(group[group.active.eq(flag)].origin)
                        if not len(dates):continue
                        q=a.loc[dates];d=nonoverlap(q.reset_index(drop=True))
                        row={'horizon':h,'cohort':coh,'model':n,'event':kind,'event_active':flag,'n':len(q),'disjoint':len(d),
                            'brier':q.brier.mean(),'crps':q.crps.mean(),'mean_return':q.realized_return.mean(),
                            'positive_rate':q.outcome.mean(),'coverage80':q.coverage80.mean(),
                            'path_volatility_mae':q.path_volatility_mae.mean() if 'path_volatility_mae' in q else np.nan}
                        for base in ['V12_HIST','V12_EVENT_HISTORY','V12_STAT','V12_IV_SCALE']:
                            b=g[coh,h,base].set_index('origin')
                            same=q.index.intersection(b.index)
                            if len(same):
                                row[f'{base}_brier_gain']=(b.loc[same,'brier']-q.loc[same,'brier']).mean()
                                row[f'{base}_crps_gain']=(b.loc[same,'crps']-q.loc[same,'crps']).mean()
                        rows.append(row)
    write('event-conditioned-scores.csv',pd.DataFrame(rows))


def market_observables():
    a=pd.read_csv(OUT/'horizon-alignment.csv')
    disagreements=pd.read_csv(OUT/'expectations-vs-statistics.csv')
    summary=[];q_effect=[];alignment=[];tail=[]
    for h in [5,21]:
        q=cohort_queries(h);y=matrix(f'labels-{h}.csv');f=matrix(f'features/{h}-TRADE.csv',OUT)
        one=a[a.horizon.eq(h)].merge(q[['origin','split','endpoint','realized_return']],on='origin',validate='many_to_one')
        for version,z in one.groupby('version'):
            for scope in SCOPES:
                u=z if scope=='combined' else z[z.split.eq(scope)]
                ok=u[u.status.eq('ok')];valid=ok[ok.density_available.eq(True)]
                alignment.append({'horizon':h,'version':version,'cohort':scope,'queries':len(u),'valid_iv':len(ok),'valid_density':len(valid),
                    'exact_listed_actual':int(ok.natural_realized.eq(True).sum()),'planned_equals_actual':int(u.planned_matches_actual.eq(True).sum()),
                    'bracketed_monotone':int(ok.bracket_status.isin(['exact','interpolated']).sum()),
                    'median_abs_gap_days':ok.maturity_gap_days.abs().median(),'p90_abs_gap':ok.maturity_gap_days.abs().quantile(.90),
                    'nonmonotone_brackets':int(ok.bracket_status.eq('nonmonotone total variance').sum())})
        z=one[one.version.eq('TRADE')&one.status.eq('ok')].set_index('origin')
        z['realized_vol']=y.volatility.reindex(z.index);z['rv_forecast']=f.rv21
        z['absolute_return']=z.realized_return.abs()
        z['realized_down']=z.realized_return.le(0).astype(int)
        z['realized_down5']=z.realized_return.lt(-.05).astype(int)
        for scope in SCOPES:
            u=z if scope=='combined' else z[z.split.eq(scope)]
            direct=[('iv_nearest','realized_vol'),('iv_bracket','realized_vol'),('rv_forecast','realized_vol'),
                    ('straddle_horizon_scaled','absolute_return'),('iv_target_total_sd','absolute_return')]
            related=[('iv_term','realized_vol'),('iv_skew','realized_down'),('density_priced_down5','realized_down5'),
                     ('iv_nearest','realized_return')]
            for field,target in direct+related:
                d=u[[field,target]].dropna()
                if len(d)<8:continue
                is_direct=(field,target) in direct
                summary.append({'horizon':h,'cohort':scope,'market_feature':field,'target':target,'n':len(d),
                    'mean_feature':d[field].mean(),'mean_target':d[target].mean(),'mean_error':(d[field]-d[target]).mean() if is_direct else np.nan,
                    'mae':(d[field]-d[target]).abs().mean() if is_direct else np.nan,'spearman':d[field].corr(d[target],method='spearman')})
        r=disagreements[disagreements.horizon.eq(h)].copy()
        r['d_p']=r.priced_positive_mass-r.stat_positive
        r['d_location']=r.priced_mean-r.stat_mean
        r['d_width']=r.priced_std-r.stat_std
        r['d_tail']=r.priced_left5-r.stat_left5
        r['d_absolute']=r.priced_abs-r.stat_abs
        r['d_q10']=r.priced_q10-r.stat_q10
        r['d_q90']=r.priced_q90-r.stat_q90
        r['actual_sign']=r.realized_return.gt(0).astype(int)
        r['surprise']=r.realized_return-r.stat_mean
        r['actual_down5']=r.realized_return.lt(-.05).astype(float)
        for scope in SCOPES:
            u=r if scope=='combined' else r[r.cohort.eq(scope)]
            for field,baseline,target in [('priced_left5','stat_left5','actual_down5'),('priced_positive_mass','stat_positive','actual_sign')]:
                s=u[[field,baseline,target]].dropna()
                if not len(s):continue
                tail.append({'horizon':h,'cohort':scope,'event':target,'n':len(s),'priced_mass':s[field].mean(),
                             'statistical_mass':s[baseline].mean(),'realized_frequency':s[target].mean(),
                             'priced_as_realized_brier':((s[field]-s[target])**2).mean(),
                             'statistical_brier':((s[baseline]-s[target])**2).mean()})
            for field,target in [('d_p','actual_sign'),('d_location','surprise'),('d_width','realized_vol'),('d_tail','actual_down5'),
                                 ('d_absolute','realized_abs'),('d_q10','surprise'),('d_q90','surprise')]:
                x=u[[field,target]].dropna()
                q_effect.append({'horizon':h,'cohort':scope,'gap':field,'target':target,'n':len(x),
                                 'average_gap':x[field].mean(),'spearman':x[field].corr(x[target],method='spearman')})
    write('alignment-coverage.csv',pd.DataFrame(alignment))
    write('observable-priced-risk.csv',pd.DataFrame(summary))
    write('statistical-and-priced-gap-diagnostics.csv',pd.DataFrame(q_effect))
    write('priced-raw-event-calibration.csv',pd.DataFrame(tail))


def robustness(s):
    found=[]
    for h in [5,21]:
        a=s[s.full_scope&~s.diagnostic&s.horizon.eq(h)]
        p=a.pivot(index='model',columns='cohort',values=['brier','crps','ECE'])
        k=[('brier','early'),('brier','later'),('crps','early'),('crps','later'),('ECE','combined')]
        b=p[k].dropna()
        data=b.to_numpy()
        for j,n in enumerate(b.index):
            a=data[j]
            if np.any(np.all(data<=a+1e-12,axis=1)&np.any(data<a-1e-12,axis=1)):continue
            found.append({'horizon':h,'model':n,'early_brier':a[0],'later_brier':a[1],'early_crps':a[2],'later_crps':a[3],'combined_ECE':a[4]})
    write('cohort-pareto.csv',pd.DataFrame(found))


def run():
    p,registry,ledger=gather();g=group_data(p)
    stats=summary(g,registry,ledger);contrasts=comparison(g,registry)
    event_stats(g);market_observables();robustness(stats)
    print(len(p),'predictions;',len(contrasts),'paired contrasts;',len(registry),'registered candidates',flush=True)


if __name__=='__main__':run()
