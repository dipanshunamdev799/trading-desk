"""Matched forecast metrics, overlap-aware inference and source/label sentinels."""
from collections import defaultdict
from scipy.stats import spearmanr

from .common import *
from .forecast import matrix,matured,shift,book_panel,POSITION,coverage
from .features import CROWD
from research.nifty_forecast_v17 import weekly
from research.nifty_forecast_v17.gift import score
from research.nifty_forecast_v16.model import fit
from research.nifty_forecast_v18 import forecast as prior

LENGTHS=(5,10,21,42)
DRAWS=1500
METRICS={'endpoint':('brier','log_loss','crps','abs_error','sq_error'),
         'weighted_native':('brier','log_loss','crps','abs_error','sq_error'),
         'risk':('qlike','abs_error','brier','crps','contraction_brier','high_entry_brier'),
         'path':('endpoint_crps','range_crps','high_crps','low_crps','drawdown_crps','brier','log_loss','energy',
                 'endpoint_mae','range_mae','vol_mae','vol_crps','variance_qlike','touch_brier','integrated_brier'),
         'postopen_risk':('brier','qlike','crps','abs_error'),
         'postopen_endpoint':('brier','crps','abs_error')}

def disjoint(d):
    last=''
    n=0
    for day,end in d[['day','target_end']].drop_duplicates().sort_values('day').itertuples(index=False,name=None):
        if day>last:
            n+=1
            last=end
    return n

def independent_cases():
    paths={'endpoint':'endpoint-cases.csv.gz','weighted_native':'native-residual-cases.csv.gz','risk':'risk-cases.csv.gz',
           'path':'joint-path-cases.csv.gz','postopen_endpoint':'postopen-cases.csv.gz','postopen_risk':'postopen-risk-cases.csv.gz'}
    for tag,p in paths.items():
        z=csv(p)
        if tag=='weighted_native':
            z['abs_error']=z.mae
            z['sq_error']=z.squared_error
        if tag=='path':
            z['p']=z.p_up
            z['actual']=z.actual_endpoint
            z['mean']=z.endpoint_mean
            z['covered']=z.endpoint_coverage80
            z['width']=z.endpoint_width80
            z['correct']=z.accuracy
        if tag=='postopen_endpoint':
            target_h={'remaining_5':5,'remaining_21':21,'r30':0,'regular_residual':0}
            z['horizon']=z.target.map(target_h)
        else:
            z['target']='original'
        if 'active' not in z:z['active']=1
        if 'parent' not in z:z['parent']=z.model
        yield tag,z

def balanced(g):
    if 'p' in g:
        if len(g['p'].dropna())!=len(g):
            return np.nan
        y=g.actual.gt(0)
        if 'event' in g and g.event.notna().all():
            y=g.event.astype(bool)
        t=g.p.ge(.5)
        k=(t.eq(y)).groupby(y).mean()
        return k.mean() if len(k)==2 else np.nan
    return np.nan

def track_tables(books):
    summary=[];cal=[]
    key=['horizon','cutoff','target','model']
    for tag,z in books:
        for n,v in [('combined',z),('early',z[z.cohort.eq('early')]),('later',z[z.cohort.eq('later')])]:
            for (h,c,t,m),g in v.groupby(key):
                yrows=g.drop_duplicates('day')
                row=dict(track=tag,horizon=h,cutoff=c,target=t,cohort=n,model=m,n=len(g),
                         active=int(g.active.fillna(0).sum()),disjoint=disjoint(yrows))
                for k in set(METRICS[tag])|{'correct','covered','width','interval_score','quantile_loss','range_coverage80','range_width80',
                                           'range_interval80','vol_coverage80','contraction_brier','high_entry_brier','p'}:
                    if k in g and g[k].notna().any():row[k]=g[k].mean()
                if 'p' in g and g.p.notna().all() and 'actual' in g:
                    observed=g['event'].astype(bool) if 'event' in g and g.event.notna().all() else g.actual.gt(0)
                    row['accuracy']=g.p.ge(.5).eq(observed).mean()
                    row['balanced_accuracy']=balanced(g)
                if 'sq_error' in row:row['rmse']=np.sqrt(row['sq_error'])
                if 'actual' in g and 'mean' in g and g['mean'].nunique()>1:
                    tmp=g[['actual','mean']].dropna()
                    if len(tmp)>3 and tmp.actual.nunique()>1:row['rank_corr']=spearmanr(tmp.actual,tmp['mean']).statistic
                summary.append(row)
                if n=='combined' and 'p' in g and g.p.notna().any() and 'actual' in g:
                    event=g['event'] if 'event' in g and g.event.notna().any() else g.actual.gt(0).astype(int)
                    s=g.assign(truth=event,bin=pd.cut(g.p,np.linspace(0,1,6),include_lowest=True))
                    for b,r in s.groupby('bin',observed=True):
                        cal.append(dict(track=tag,horizon=h,cutoff=c,target=t,model=m,probability_bin=str(b),
                                        n=len(r),probability=r.p.mean(),observed=r.truth.mean()))
    write('model-leaderboards.csv',pd.DataFrame(summary))
    write('probability-calibration.csv',pd.DataFrame(cal))

def references(tag,h,sub):
    names=set(sub.model)
    rows=[]
    for m,g in sub.groupby('model'):
        p=g.parent.iloc[0]
        if p!=m and p in names:
            rows.append((m,p))
        if tag=='endpoint' and m not in ('neutral','component_plus_residual','V18_nonprice_same_clock','V18_corporate_same_clock'):
            refs=('component_plus_residual','V18_corporate_same_clock') if h==5 else ('neutral','V18_nonprice_same_clock')
            rows.extend((m,q) for q in refs if q in names)
        if tag=='risk' and m in ('crowding_on_price','innovation_on_price','combined_positioning_risk','delivery_on_price','deals_on_price'):
            r=('protected_offshore_plus_domestic','protected_fixed_iv_rv') if h==5 else ('protected_GJR','protected_student_EGARCH')
            rows.extend((m,q) for q in r if q in names)
        if tag=='path' and m in ('position_on_IV','position_on_GJR'):
            rows.extend((m,q) for q in ('same_clock_IV','same_clock_GJR','same_clock_GIFT_first') if q in names)
        if tag=='path' and m=='same_clock_GJR' and 'same_clock_IV' in names:rows.append((m,'same_clock_IV'))
    return list(dict.fromkeys(rows))

def plural_draws(n,b,rng):
    k=int(np.ceil(n/b))
    starts=rng.integers(n,size=(DRAWS,k,1))
    return ((starts+np.arange(b))%n).reshape(DRAWS,-1)[:,:n]

def boot(intervals,family):
    order=sorted({d for _,s in intervals for d in s.index})
    loc={d:i for i,d in enumerate(order)}
    v=np.full((len(order),len(intervals)),np.nan)
    for col,(_,s) in enumerate(intervals):
        v[[loc[d] for d in s.index],col]=s.to_numpy()
    rng=np.random.default_rng(SEED+family)
    center=np.nanmean(v,axis=0)
    z=[]
    for b in LENGTHS:
        samples=plural_draws(len(order),b,rng)
        runs=[]
        # Cap intermediate allocations on the largest comparison groups.
        for start in range(0,DRAWS,100):
            q=v[samples[start:start+100]]
            denom=np.isfinite(q).sum(axis=1)
            runs.append(np.divide(np.nansum(q,axis=1),denom,out=np.full(denom.shape,np.nan,float),where=denom>0))
        bs=np.vstack(runs)
        lim=np.nanquantile(bs,[.025,.975],axis=0)
        sd=np.nanstd(bs,axis=0)
        denom=np.where(sd>1.e-12,sd,np.inf)
        deviations=np.abs((bs-center)/denom)
        maximum=np.nanmax(deviations,axis=1)
        crit=np.nanquantile(maximum,.95)
        j=crit*sd
        for (row,_),lo,hi,a,e in zip(intervals,lim[0],lim[1],center-j,center+j):
            z.append(row|dict(block=b,low=lo,high=hi,adjusted_low=a,adjusted_high=e,adjustment_models=len(intervals)))
    return z

def matched(books):
    rows=[];bootstraps=[];episode=[]
    primary={
        'endpoint':{'brier','crps'},'weighted_native':{'brier','crps'},'risk':{'abs_error','qlike','brier','contraction_brier','high_entry_brier'},
        'path':{'range_crps','endpoint_crps','touch_brier','integrated_brier'},
        'postopen_endpoint':{'brier','crps'},'postopen_risk':{'brier','qlike'}}
    for j,(tag,z) in enumerate(books):
        for (h,c,t),a in z.groupby(['horizon','cutoff','target']):
            sets=defaultdict(list)
            spans={}
            by={k:v.set_index('day').sort_index() for k,v in a.groupby('model')}
            for m,p in references(tag,h,a):
                f=by[m];g=by[p]
                idx=f.index.intersection(g.index)
                assert f.loc[idx,'target_end'].eq(g.loc[idx,'target_end']).all()
                assert f.loc[idx,'cohort'].eq(g.loc[idx,'cohort']).all()
                f=f.loc[idx];g=g.loc[idx]
                active=f.active.eq(1)&g.active.eq(1)
                expiry=f.expiry_guard.eq(1)&g.expiry_guard.eq(1) if 'expiry_guard' in f else active
                for alias,e in [('combined',np.ones(len(f),bool)),('active_matched',active),
                                ('early',f.cohort.eq('early')),('later',f.cohort.eq('later')),('away_from_expiry',expiry&active)]:
                    if alias=='away_from_expiry' and ('expiry_guard' not in f or not expiry.any()):continue
                    for k in METRICS[tag]:
                        if k not in f:continue
                        ii=idx[e&f[k].notna()&g[k].notna()]
                        if not len(ii):continue
                        x=f.loc[ii,k];y=g.loc[ii,k]
                        d=y-x
                        dated=tuple(ii)
                        if dated not in spans:
                            spans[dated]=disjoint(f.loc[ii].reset_index()[['day','target_end']])
                        n=spans[dated]
                        val=dict(track=tag,horizon=h,cutoff=c,target=t,model=m,parent=p,metric=k,cohort=alias,
                                 n=len(ii),active=int(active.loc[ii].sum()),disjoint=n,
                                 candidate=x.mean(),reference=y.mean(),gain=d.mean())
                        rows.append(val)
                        if alias=='active_matched' and k in primary[tag] and len(ii)>=25:
                            sets[k].append((val,d))
                            block=d.groupby(np.arange(len(d))//21).agg(['sum','size'])
                            after=(d.sum()-block['sum'])/(len(d)-block['size'])
                            worst=int(np.argmin(after))
                            episode.append(val|dict(remaining_gain=after.iloc[worst],removed_from=ii[worst*21],
                                 removed_to=ii[min(len(d)-1,worst*21+20)],removed_n=int(block['size'].iloc[worst])))
            for q,(k,g) in enumerate(sets.items()):
                bootstraps.extend(boot(g,100*j+9*int(h)+13*q+sum(ord(x) for x in c+t)))
    write('matched-comparisons.csv',pd.DataFrame(rows))
    write('block-bootstrap-intervals.csv.gz',pd.DataFrame(bootstraps))
    write('episode-omission.csv',pd.DataFrame(episode))

def nulls():
    sample=csv('refit-null-cases.csv.gz')
    ap=csv('endpoint-cases.csv.gz')
    ap=ap[ap.cutoff.eq('preauction_0855')]
    w=[]
    for stat in ('brier','crps'):
        archive=sample.groupby(['seed','horizon','arm'])[stat+'_gain'].mean()
        finals=archive.groupby('seed').max()
        p=ap.groupby(['horizon','model'])[stat].mean().unstack()
        real=pd.concat([(p.clock_structural-p[k]).rename(k) for k in ('participant','delivery') if k in p],axis=1)
        if 'corporate_position_interactions' in p:
            real['interactions']=p.V18_corporate_same_clock-p.corporate_position_interactions
        best=float(real.max().max())
        w.append(dict(metric=stat,observed_best=best,rotations=len(finals),null_median=finals.median(),null_95=finals.quantile(.95),
                     exceedances=int(finals.ge(best).sum()),finite_reselection_tail=(1+int(finals.ge(best).sum()))/(1+len(finals))))
    write('refit-reselection-nulls.csv',sample.groupby(['seed','horizon','arm'],as_index=False)[['brier_gain','crps_gain']].mean())
    write('refit-reselection-summary.csv',pd.DataFrame(w))

def sensitivity():
    panel=csv('asof-positioning-features.csv.gz')
    old=csv('endpoint-cases.csv.gz')
    s=np.load(OUT/'endpoint-laws.npz',allow_pickle=False)['log_return_atoms']
    sent=[];extra=[]
    own=('FII_index_futures_own_ratio','DII_index_futures_own_ratio','Pro_index_futures_own_ratio',
         'FII_stock_futures_own_ratio','FII_index_calls_own_ratio','FII_index_puts_own_ratio')
    for clock in CLOCKS:
        for h in HORIZONS:
            f,y=book_panel(clock,h,panel)
            day=f.index.to_numpy(); dec=f.decision.str[:10].to_numpy()
            labels=y['original'+str(h)].to_numpy(float)
            ends=y['end_original'+str(h)].fillna('9999-12-31').to_numpy()
            mask=y['cohort_'+str(h)].notna().to_numpy()
            axis=np.flatnonzero(mask)
            mu=weekly.chronology(f,weekly.ORIGINAL_BASE,labels,ends,dec)
            error=labels-mu
            org=old[old.cutoff.eq(clock)&old.horizon.eq(h)&old.model.eq('clock_structural')].set_index('day')
            x=matrix(f,POSITION)
            own_a=matrix(f,own+CROWD)
            complete=np.isfinite(x[:,:10]).all(axis=1)&f.open_interest_observed.eq(1).to_numpy()
            for i in axis:
                t=matured(day,ends,labels,i,dec)
                embargo_day=dec[max(0,i-5)]
                exp=t[ends[t]<embargo_day]
                closed=t[complete[t]] if complete[i] else t[:0]
                parent=s[int(org.loc[day[i],'law'])].astype(float)
                for name,z,j in [('own_gross_normalization',own_a,t),('five_session_embargo',x,exp),('complete_reporting_only',x,closed)]:
                    q,m,u=shift(z,error,i,j,.009 if h==5 else .014)
                    e=score(parent+q,labels[i])
                    before=score(parent,labels[i])
                    extra.append(dict(day=day[i],horizon=h,cutoff=clock,cohort=y['cohort_'+str(h)].iloc[i],
                          target_end=ends[i],last_mature=max(ends[u]) if len(u) else None,model=name,active=int(m is not None),shift=q,
                          brier=e['brier'],crps=e['crps'],brier_gain=before['brier']-e['brier'],crps_gain=before['crps']-e['crps']))
                if i not in axis[np.linspace(0,len(axis)-1,9,dtype=int)]:continue
                d,m,u=shift(x,error,i,t,.009 if h==5 else .014)
                clone=np.column_stack([x,x[:,0],x[:,2]])
                q,r,v=shift(clone,error,i,t,.009 if h==5 else .014)
                assert abs(d-q)<1.e-12 and np.array_equal(u,v)
                future=np.arange(len(x))>i
                bad=x.copy()
                bad[future]=1.e15
                bad_labels=error.copy()
                bad_labels[(ends>=dec[i])|future]=-1.e12
                val,_,_=shift(bad,bad_labels,i,t,.009 if h==5 else .014)
                assert val==d
                simulated=f.copy()
                future_clock=f.decision.gt(f.decision.iloc[i]).to_numpy()
                simulated.loc[future_clock,'prior_ret5']=1.e14
                mutated_y=labels.copy()
                mutated_y[ends>=dec[i]]=1.e19
                new=weekly.chronology(simulated.iloc[:i+1],weekly.ORIGINAL_BASE,mutated_y[:i+1],ends[:i+1],dec[:i+1])
                assert abs(new[-1]-mu[i])<=1.e-12
                sent.append(dict(cutoff=clock,horizon=h,day=day[i],last_mature=max(ends[u]) if len(u) else None,
                                 exact_copy_delta=abs(d-q),poisoned_future_delta=abs(val-d),mutated_structural_delta=abs(new[-1]-mu[i])))
    write('mechanism-sensitivities.csv.gz',pd.DataFrame(extra))
    write('future-information-sentinels.csv',pd.DataFrame(sent))

def derived():
    barrier=csv('barrier-cases.csv.gz')
    a=barrier.groupby(['horizon','cutoff','model','side','barrier'],as_index=False).agg(
        cases=('day','size'),touch_rate=('actual_touch','mean'),touch_brier=('touch_brier','mean'),
        day_one_brier=('brier_by_1','mean'),integrated_brier=('integrated_brier','mean'),
        survivor_brier=('conditional_brier','mean'),survivor_n=('conditional_brier','count'),
        event_time_log=('event_time_log','mean'))
    write('barrier-leaderboard.csv',a)
    for d in ('stock','sector'):
        s=csv(d+'-transfer-daily.csv')
        k=s.groupby(['target','model'],as_index=False).agg(dates=('day','nunique'),case_units=('n','sum'),
           rank_corr=('rank_correlation','mean'),mae=('mae','mean'),rmse=('rmse','mean'))
        write(d+'-transfer-leaderboard.csv',k)
    c=csv('crowding-case-tests.csv.gz')
    d=c[c.model.eq('price_iv_oi')].set_index(['horizon','day','outcome']).score
    l=c.join(d.rename('reference'),on=['horizon','day','outcome'])
    l['gain']=l.reference-l.score
    for tag,q in [('all',l),('exclude_expiry',l[l.expire_filter.eq(1)])]:
        a=q.groupby(['horizon','outcome','model'],as_index=False).agg(n=('day','nunique'),loss=('score','mean'),gain=('gain','mean'))
        a['scope']=tag
        if tag=='all':out=a
        else:out=pd.concat([out,a],ignore_index=True)
    write('crowding-leaderboard.csv',out)

def main():
    books=list(independent_cases())
    track_tables(books)
    matched(books)
    nulls()
    sensitivity()
    derived()
    replay=read('baseline-replay-receipt.json')
    sent=csv('future-information-sentinels.csv')
    e=csv('endpoint-cases.csv.gz')
    q=e.source_release.notna()
    assert e.loc[q,'source_release'].le(e.loc[q,'decision']).all()
    assert e.last_mature.lt(e.decision.str[:10]).all()
    for h in HORIZONS:
        n=e[e.horizon.eq(h)&e.cutoff.eq('preauction_0855')&e.model.eq('neutral')]
        assert len(n)==EXPECTED[h] and disjoint(n)==({5:53,21:11}[h])
    save('validation-receipt.json',dict(asof=now(),clock_session_guards=len(e),future_information_sentinels=len(sent),
          chronology_training_rows=len(e),source_receipts_v18=read('predecessor-protection.json')['artifacts'],
          max_replay_error=replay['max_score_deviation'],disjoint={'weekly':53,'monthly':11},
          search_adjustment='Circular moving-block resampling and familywise max standardized deviation. All paired primary comparisons within each reported horizon, cutoff, metric and target group enter the adjustment.',
          baseline_scope='Original windows overlap. Nested negative-control reselects representative V19 families and cannot correct cumulative V1–V19 search on the same dates.',
          order_of_testing='Source scope and hypothesis registry frozen first. Outcomes, borrowed models and anchored time limits retain chronological provenance.'))
    print('Matched scores, uncertainty and chronological sentinels archived',flush=True)

if __name__=='__main__':
    main()

