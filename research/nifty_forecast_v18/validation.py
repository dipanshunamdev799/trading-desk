"""Date and information-quality assertions covering source tables and historical forecasts."""
import sqlite3
from .common import *
from .aggregate import load_inputs,build,COUNT,TEXT,FUND,SCHEDULE
from .forecast import build_clock,field_matrix,available,fit_shift
from research.nifty_forecast_v17 import weekly

def archive_check():
    with sqlite3.connect(OUT/'corporate-information.sqlite') as db:
        n,lo,hi,missing,duplicate=db.execute("""select count(*), min(substr(release,1,10)),max(substr(release,1,10)),
             sum(eligible is null),sum(duplicate) from announcements""").fetchone()
        t=db.execute("""select count(*) from announcements
           where eligible is not null and datetime(release,'+10 minutes')<>eligible""").fetchone()[0]
        broken=db.execute("""select count(*) from announcements a left join announcements b on a.episode_id=b.record_id
          where a.duplicate=1 and (b.record_id is null or b.release>a.release or a.symbol<>b.symbol)""").fetchone()[0]
    assert n==345226 and lo>=FIRST and hi<=FREEZE and t==0 and broken==0
    f=csv('structured-financial-facts.csv.gz')
    assert f.period_end.between(FIRST,FREEZE).all()
    assert f.period_start.dropna().ge(FIRST).all()
    assert f.eligible.ge(f.release).all()
    q=csv('fundamental-comparisons.csv.gz')
    prior_cols=['prior_quarter_public','prior_year_public']
    for k in prior_cols:
        ok=q[k].notna()
        assert q.loc[ok,k].lt(q.loc[ok,'eligible']).all(),k
    return dict(announcement_rows=n,duplicates=int(duplicate),untimed=int(missing),financial_facts=len(f),published_comparisons=len(q))

def sentinel():
    e,f,s,b,p,t,ex=load_inputs()
    cases=[]
    for clock in ('previous_1700','preauction_0855','09:25','10:20'):
        for day in ('2026-05-12','2026-09-16'):
            window=t[t.cutoff.eq(clock)&t.day.le(day)].sort_values('day').tail(38)
            row=window.iloc[-1]
            cut=row.decision.replace('T',' ')[:19]
            a,z=build(e,f,s,b,p,window,ex)
            e1=e.copy()
            f1=f.copy()
            s1=s.copy()
            b1=b.copy()
            p1=p.copy()
            fcut=f1.eligible.gt(cut)
            ecut=e1.eligible.gt(cut)
            scut=s1.decision.gt(cut)
            bcut=b1.public_by.gt(cut)
            f1.loc[fcut,'statistical_surprise']=17.
            e1.loc[ecut,'text_sign']=27
            s1.loc[scut,'reaction_regular']=6.
            b1.loc[bcut,'scheduled']=day
            p1.loc[p1.public_by.gt(cut),'date']=day
            a1,z1=build(e1,f1,s1,b1,p1,window,ex)
            pd.testing.assert_frame_equal(a,a1,check_exact=True)
            pd.testing.assert_frame_equal(z,z1,check_exact=True)
            cases.append(dict(scope='all eligible aggregates and schedule exposures',clock=clock,day=day,
              columns=len(a.columns)+len(z.columns),redacted_future_rows=int(fcut.sum()+ecut.sum()+scut.sum()+bcut.sum())))
    for clock in ('previous_1700','preauction_0855'):
        for h in HORIZONS:
            f,y=build_clock(clock,h)
            dates=f.index.to_numpy()
            cutoff=f.decision.str[:10].to_numpy()
            actual=y['original'+str(h)].to_numpy(float)
            end=y['end_original'+str(h)].fillna('9999-12-31').to_numpy()
            for day in ('2026-05-12','2026-09-16'):
                i=int(f.index.searchsorted(day))
                feat=field_matrix(f,COUNT+TEXT+FUND+SCHEDULE)
                future=feat.copy()
                future[i+1:]=71.
                state=weekly.chronology(f,weekly.ORIGINAL_BASE,actual,end,cutoff)
                muted=actual.copy()
                held=(end>=cutoff[i])&np.isfinite(actual)
                muted[held]=.36-muted[held]
                tf=f.copy()
                tf.loc[f.index>dates[i],list(weekly.ORIGINAL_BASE)]=75.
                state2=weekly.chronology(tf,weekly.ORIGINAL_BASE,muted,end,cutoff)
                assert state[i]==state2[i]
                tr=available(dates,end,i,actual,cutoff)
                loc,model,t0=fit_shift(feat,actual-state,i,tr)
                changed,m,t1=fit_shift(future,muted-state2,i,tr)
                np.testing.assert_array_equal(t0,t1)
                assert loc==changed
                clone=np.column_stack((feat,feat[:,0],feat[:,0]))
                repeated,_,_=fit_shift(clone,actual-state,i,tr)
                assert repeated==loc
                cases.append(dict(scope=f'{h}-session residual forecasts and exact-column clones',clock=clock,day=day,
                           columns=feat.shape[1],redacted_future_rows=int(held.sum())))
    z=pd.DataFrame(cases)
    write('future-information-sentinels.csv',z)
    return len(z)

def main():
    a=archive_check()
    original=csv('original-event-forecasts.csv.gz',usecols=['day','decision','last_mature','origin','horizon','cutoff','law','model'])
    assert original.last_mature.lt(original.decision.str[:10]).all()
    assert not original.duplicated(['day','horizon','cutoff','model']).any()
    assert original.groupby(['horizon','cutoff']).day.nunique().unstack().eq(pd.Series(EXPECTED),axis=0).all().all()
    with np.load(OUT/'original-event-laws.npz',allow_pickle=False) as z:
        assert z['atoms'].shape==(len(original),128) and np.isfinite(z['atoms']).all()
    stock=csv('stock-event-pairs.csv.gz',usecols=['decision','source_eligible','reported_fundamental_available','target_end','day'])
    assert stock.source_eligible.le(stock.decision).all()
    subset=stock[stock.reported_fundamental_available.notna()]
    assert subset.reported_fundamental_available.le(subset.decision).all()
    assert stock.day.le(stock.target_end).all()
    sr=csv('event-schedule-exposures.csv.gz')
    clocks=csv('event-aggregate-features.csv.gz',usecols=['day','cutoff','decision_local','non_price_max_day'])
    ok=clocks.non_price_max_day.notna()
    assert clocks.loc[ok,'non_price_max_day'].lt(clocks.loc[ok,'decision_local'].str[:10]).all()
    k=sr.merge(clocks,on=['day','cutoff'],validate='m:1')
    ok=k.last_notice.notna()
    assert k.loc[ok,'last_notice'].le(k.loc[ok,'decision_local']).all()
    if 'known_front_expiry_source_day' in k:
        ok=k.known_front_expiry_source_day.notna()
        assert k.loc[ok,'known_front_expiry_source_day'].lt(k.loc[ok,'decision_local'].str[:10]).all()
    # Paired strong references are exact scored rows, verified independently by the inherited implementation.
    v=csv('baseline-benchmarks.csv')
    reproduced=(.100841,.228529,.245042,.024694,.036469,.033179,.152707,.172872,.010658,.010309)
    assert set(reproduced).issubset(set(v.value.round(6)))
    n=sentinel()
    b=read('predecessor-protection.json')
    save('validation-receipt.json',dict(archive=a,chronological_sentinels=n,exact_copy_invariance=True,index_forecasts=len(original),
       matched_stock_rows=len(stock),schedule_exposures=len(k),protected_horizons=EXPECTED,verified_v17_hashes=b['artifacts'],
       holdout='No untouched post-freeze outcome was used for these estimates. All original historical outcomes are research-exposed.',
       notice='The future-information tests alter data after each eligible cutoff, then rebuild earlier aggregate values and origin fits. Refit-and-reselection controls use only block-rotated earlier training observations.'))
    print('Validated source clocks and',n,'future-information/clone tests',flush=True)

if __name__=='__main__':
    main()
