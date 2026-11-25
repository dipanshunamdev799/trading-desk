"""Exact V18 point-leader and activity replays on immutable case-level inputs."""
import itertools
import math

from .common import *
from research.nifty_forecast_v18 import forecast as previous
from research.nifty_forecast_v17 import weekly
from research.nifty_forecast_v17.gift import score

BLOCKS={'delivery':previous.EXTRA[:3],'participant':previous.EXTRA[3:5],'deals':previous.EXTRA[5:8]}

def replays():
    saved=csv('original-event-forecasts.csv.gz',V18).set_index(['horizon','cutoff','day','model'])
    native=csv('protected-v14-event-overlays.csv.gz',V18).set_index(['horizon','origin','model'])
    prep=csv('original-clock-forecasts.csv.gz',V17).set_index(['horizon','cutoff','day','model'])
    law14=weekly.load_legacy()
    stored=np.load(V17/'original-clock-laws.npz',allow_pickle=False)['atoms'].astype(float)
    v18law=np.load(V18/'original-event-laws.npz',allow_pickle=False)['atoms']
    subs=[tuple(c) for n in range(4) for c in itertools.combinations(BLOCKS,n)]
    cases=[]
    portions=[]
    legacy=[]
    pred=[]
    checks=[]
    for h in HORIZONS:
        for c in CLOCKS:
            f,y=previous.build_clock(c,h)
            dates=f.index.to_numpy()
            origin=f.origin.to_numpy()
            ends=y['end_original'+str(h)].fillna('9999-12-31').to_numpy()
            cutoff=f.decision.str[:10].to_numpy()
            actual=y['original'+str(h)].to_numpy()
            cohort=y['cohort_'+str(h)]
            idx=np.flatnonzero(cohort.notna())
            assert len(idx)==EXPECTED[h]
            mean=weekly.chronology(f,weekly.ORIGINAL_BASE,actual,ends,cutoff)
            errors=actual-mean
            with_fund=previous.field_matrix(f,previous.FUND+previous.COUNT)
            x={names:previous.field_matrix(f,tuple(k for g in names for k in BLOCKS[g])) for names in subs if names}
            past_native=np.full(len(dates),np.nan)
            for i in idx:
                _,r,w=law14[(h,origin[i])]
                past_native[i]=actual[i]-np.log1p(w@r)
            for i in idx:
                day=dates[i]
                old=prep.loc[(h,c,day,'clock_structural')]
                ar=stored[int(old.law)]
                t=previous.available(dates,ends,i,actual,cutoff)
                args=dict(horizon=h,cutoff=c,day=day,origin=origin[i],target_end=ends[i],
                          cohort=cohort.iloc[i],last_mature=max(ends[t]))
                costs={}
                for names in subs:
                    shift,fit,_=previous.fit_shift(x[names],errors,i,t,limit=.009 if h==5 else .014) if names else (0.,None,t)
                    shifted=ar+shift
                    v=score(shifted,actual[i])
                    costs[names]=v
                    model=' + '.join(names) if names else 'structural'
                    cases.append(args|dict(model=model,shift=shift,**v))
                    key={('delivery',):'delivery_only',('participant',):'participant_positions',
                         ('deals',):'bulk_block_activity',tuple(BLOCKS):'additional_nonprice'}.get(names)
                    if key:
                        orig=saved.loc[(h,c,day,key)]
                        checks.append(max(abs(orig[k]-v[k]) for k in ('brier','crps','log_loss','mean')))
                        np.testing.assert_array_equal(shifted.astype(np.float32),v18law[int(orig.law)])
                v=score(ar,actual[i])
                checks.append(abs(old.crps-v['crps']))
                # Average marginal contribution over all six addition sequences. This is predictive attribution.
                for block in BLOCKS:
                    gains={k:0. for k in ('brier','crps')}
                    for names in subs:
                        if block in names:continue
                        after=tuple(q for q in BLOCKS if q==block or q in names)
                        fac=math.factorial(len(names))*math.factorial(2-len(names))/6.
                        for k in gains:gains[k]+=fac*(costs[names][k]-costs[after][k])
                    portions.append(args|dict(block=block,**gains))
                if c=='preauction_0855':
                    exp,values,weights=law14[(h,origin[i])]
                    assert exp==ends[i]
                    shift,mature,u=previous.fit_shift(with_fund,past_native,i,t,limit=.012)
                    for model,delta in [('V14_exact',0.),('V14_event_overlay',shift)]:
                        arr=(1+values)*np.exp(delta)-1
                        v=weekly.evaluate(arr,weights,np.expm1(actual[i]))
                        old0=native.loc[(h,origin[i],model)]
                        for k in ('p','brier','crps','mean'):checks.append(abs(v[k]-old0[k]))
                        adapted=int(model=='V14_event_overlay' and mature is not None)
                        assert adapted==old0.adapted
                        legacy.append(args|dict(model=model,cutoff='native_v14_guard',adapted=adapted,
                                              law_shift=delta,law_index=len(pred),**v))
                        pred.append((arr,weights))
            print('Replayed V18 activity and attribution',h,c,flush=True)
    assert max(checks)<2.e-8,max(checks)
    write('v18-activity-replay-and-subsets.csv.gz',pd.DataFrame(cases))
    write('v18-activity-shapley-by-origin.csv.gz',pd.DataFrame(portions))
    z=pd.DataFrame(legacy)
    assert z[z.model.eq('V14_event_overlay')&z.horizon.eq(5)].adapted.sum()==223
    write('v18-native-exact-replay.csv',z)
    offsets=np.r_[0,np.cumsum([len(a) for a,w in pred])]
    np.savez_compressed(OUT/'v18-native-replayed-laws.npz',atoms=np.concatenate([a for a,w in pred]),
                        weights=np.concatenate([w for a,w in pred]),offsets=offsets)
    a=csv('baseline-benchmarks.csv',V18)
    b=csv('original-clock-forecasts.csv.gz',V17)
    month=b[b.horizon.eq(21)&b.model.eq('neutral')].groupby('cutoff').crps.agg(['mean','size'])
    for c,r in month.iterrows():
        a.loc[len(a)]=['neutral_distribution',c,21,'neutral','crps',int(r['size']),r['mean']]
    q=csv('retimed-path-scores.csv.gz',V17)
    k=q[q.horizon.eq(21)&q.cutoff.eq('preauction_0855')&q.model.eq('same_clock_GJR')]
    a.loc[len(a)]=['protected_distribution','08:55',21,'V15_GJR_restart','brier',len(k),k.brier.mean()]
    write('protected-benchmarks.csv',a)
    write('protected-native-joint-models.csv',csv('protected-native-joint-models.csv',V18))
    save('baseline-replay-receipt.json',dict(
        archived_activity_predictions=len(checks)-len(z)*4-2*sum(EXPECTED.values()),max_score_deviation=max(checks),
        checked_scalar_values=len(checks),native_laws=len(z),weekly_adapted=223,
        monthly_adapted=int(z[z.model.eq('V14_event_overlay')&z.horizon.eq(21)].adapted.sum()),
        activity_exact='Float32 atom arrays agreed case by case with the stored V18 laws for each individual family and their union.',
        activity_all_subsets=len(cases),attribution='Eight matched subsets. All six addition orders are averaged for each origin.',
        opening_proof='V18 exact 248-case GIFT replay preserved with immutable predecessor manifest.'))

def protect():
    m=read('manifest.json',V18)
    for group,base in [('files',V18),('source_files',ROOT)]:
        for x in m[group]:
            assert sha(base/x['file'])==x['sha256'],x['file']
    save('predecessor-protection.json',dict(v18_manifest=sha(V18/'manifest.json'),artifacts=len(m['files']),code=len(m['source_files']),
           prior_chain=read('predecessor-protection.json',V18)))
    print('Verified V18 immutable',len(m['files']),'files',flush=True)

if __name__=='__main__':
    import sys
    {'replay':replays,'protect':protect}[sys.argv[1]]()
