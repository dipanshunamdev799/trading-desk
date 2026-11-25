"""Reproduce event-research parents from their original dated data and forecast laws."""
from .common import *
from research.nifty_forecast_v17 import weekly
from research.nifty_forecast_v17.gift import score
from research.nifty_forecast_v17.common import Q,MIN,HIST

CLOCKS=('previous_1700','preauction_0855')

def refit_weekly():
    frame=csv('original-feature-panel.csv.gz',V17)
    target=csv('original-target-panel.csv',V17).set_index('day')
    a=csv('original-clock-forecasts.csv.gz',V17)
    stock=csv('official-stock-breadth.csv',V17).set_index('day')
    rows=[]
    with np.load(V17/'original-clock-laws.npz',allow_pickle=False) as law:
        stored=law['atoms']
    for clock in CLOCKS:
        f=frame[frame.cutoff.eq(clock)].set_index('day').reindex(target.index)
        dates=f.decision.str[:10].to_numpy()
        w=stock.reindex(f.origin)[list(weekly.STOCK_DAILY)];w.index=f.index
        f=f.join(w)
        for h in HORIZONS:
            y=target['original'+str(h)].to_numpy()
            end=target['end_original'+str(h)].fillna('9999-12-31').to_numpy()
            loc=weekly.chronology(f,weekly.ORIGINAL_BASE,y,end,dates)
            gap=weekly.chronology(f,weekly.ORIGINAL_BASE+('expected_gap',),target.gap.to_numpy(),target.end_gap.to_numpy(),dates)
            rth=weekly.chronology(f,weekly.ORIGINAL_BASE+weekly.PRE_STOCK,target.initial_rth.to_numpy(),target.end_initial_rth.to_numpy(),dates)
            rem=weekly.chronology(f,weekly.ORIGINAL_BASE+weekly.STOCK_DAILY,y-target.gap.to_numpy()-target.initial_rth.to_numpy(),end,dates)
            n=0
            for i in np.flatnonzero(target['cohort_'+str(h)].notna()):
                ids=np.flatnonzero((end<dates[i])&(np.arange(len(y))<i)&np.isfinite(y))[-HIST:]
                assert len(ids)>=MIN
                s=y[ids]
                shape=np.quantile(s-np.median(s),Q)
                iv=f.iv_prev.iloc[i]*np.sqrt(h/252)
                if np.isfinite(iv) and np.std(s)>0:
                    shape*=np.clip(iv/np.std(s),.55,1.65)
                g=f.expected_gap.iloc[i]
                for name,center in [('clock_structural',loc[i]),('component_plus_residual',(g if np.isfinite(g) else gap[i])+rth[i]+rem[i])]:
                    rhs=shape+(center if np.isfinite(center) else loc[i])
                    tolerance=2.e-13
                    prior=a[a.horizon.eq(h)&a.cutoff.eq(clock)&a.day.eq(f.index[i])&a.model.eq(name)].iloc[0]
                    np.testing.assert_array_equal(stored[int(prior.law)],rhs.astype('float32'))
                    out=score(rhs,y[i]);assert abs(out['crps']-prior.crps)<tolerance
                    assert abs(out['brier']-prior.brier)<tolerance
                    rows.append(dict(day=f.index[i],origin=prior.origin,cutoff=clock,horizon=h,model=name,**out))
                n+=1
            assert n==EXPECTED[h]
    write('same-clock-refit.csv.gz',pd.DataFrame(rows))
    return rows

def main():
    from research.nifty_forecast_v16 import session_models as opening
    f,y=opening.load()
    x=opening.prepare(y,f[f.cutoff.eq('08:55')].set_index('day').reindex(y.index))
    e=opening.Engine(x,y)
    e.run('opening_gap','gap',[s for s in opening.opening_specs(True) if s.name=='gift_raw'])
    p=pd.DataFrame(e.rows)
    o=csv('opening-0855-scores.csv.gz',V16)
    a=p.merge(o[o.model.eq('gift_raw')],on=['day','cutoff','model'],suffixes=('','_original'),validate='1:1')
    assert len(a)==len(p)==248
    for k in ['p_up','brier','crps','mae']:
        np.testing.assert_allclose(a[k],a[k+'_original'],rtol=0,atol=5e-14)
    write('opening-exact-replay.csv',p)
    rows=refit_weekly()
    old=weekly.load_legacy()
    exact=[]
    for h in HORIZONS:
        t=csv(f'targets-{h}.csv',V14).set_index('day')
        for (hh,d),(end,atoms,w) in old.items():
            if hh!=h:continue
            y=t.at[d,'endpoint_return']
            exact.append(dict(horizon=h,origin=d,target_date=end,model='V14_sign_shrinkage' if h==5 else 'V14_domestic_GJR',
                              **weekly.evaluate(atoms,w,y)))
    q=pd.DataFrame(exact)
    write('protected-exact-law-replay.csv',q)
    assert q.groupby('horizon').size().to_dict()==EXPECTED
    ep=csv('original-endpoint-leaderboard.csv',V16)
    vol=csv('volatility-scores.csv.gz',V16)
    np.testing.assert_allclose(np.abs(vol.pred_vol-vol.actual_vol),vol.mae,rtol=0,atol=1e-14)
    np.testing.assert_allclose(np.square(vol.p-vol.actual_expand),vol.brier,rtol=0,atol=1e-14)
    lines=[]
    def note(track,clock,h,model,metric,s):
        lines.append(dict(track=track,cutoff=clock,horizon=h,model=model,metric=metric,n=len(s),value=float(np.mean(s))))
    note('opening','08:55',1,'V16_GIFT','brier',p.brier);note('opening','08:55',1,'V16_GIFT','accuracy',p.correct)
    for h in HORIZONS:
        k=q[q.horizon.eq(h)]
        for metric in ('brier','crps'):
            note('protected_return','native_v14_guard',h,k.model.iloc[0],metric,k[metric])
    p18=pd.DataFrame(rows)
    for (h,c,m),g in p18.groupby(['horizon','cutoff','model']):
        note('same_clock_refit',c,h,m,'crps',g.crps)
    # Score the protected V15 restarted law from archived log-tick joint paths.
    from research.nifty_forecast_v15.sequential import TICK
    from research.nifty_forecast_v16.paths import distance_crps
    archives=read('retimed-path-archive.json',V17)['files']
    tape=csv('targets-21.csv',V14).set_index('day')
    s=[]
    for r in archives:
        if r['horizon']!=21:continue
        with np.load(V17/r['file'],allow_pickle=False) as z:
            law=z['preauction_0855_same_clock_GJR']
            atom=np.expm1(law[:,-1,3]*TICK)
        s.append(distance_crps(atom,tape.at[r['origin'],'endpoint_return']))
    note('protected_distribution','08:55',21,'V15_GJR_restart','crps',s)
    note('symmetric','all',21,'equal_probability','brier',np.full(EXPECTED[21],.25))
    for h,k,m in [(5,'mae','offshore_plus_domestic'),(21,'mae','GJR'),(5,'brier','fixed_iv_rv'),(21,'brier','student_EGARCH'),(5,'mae','raw_iv')]:
        b=vol[vol.horizon.eq(h)&vol.cutoff.eq('08:55')&vol.model.eq(m)]
        assert len(b)==EXPECTED[h],(h,m)
        note('protected_risk','08:55',h,m,k,b[k])
    z=pd.DataFrame(lines)
    write('baseline-benchmarks.csv',z)
    print('Baseline replay',len(p),'GIFT forecasts,',len(q),'exact weighted laws,',len(rows),'same-clock refits, and',len(s),'GJR laws',flush=True)

def native_paths():
    r=csv('joint-path-leaderboard.csv',V16)
    controls=['V14_gjr_student','V14_gjr_iv','V14_trend_shrink','V15_gjr_restart','session_state','decomposed_gift']
    r=r[r.model.isin(controls)].copy()
    r['timing']='Archived native guard per source manifest'
    write('protected-native-joint-models.csv',r)
    print('Retained native joint score summaries',len(r),flush=True)

def protect():
    m=read('manifest.json',V17)
    for k in m['files']:
        assert sha(V17/k['file'])==k['sha256'],k['file']
    for k in m['source_files']:
        assert sha(ROOT/k['file'])==k['sha256'],k['file']
    save('predecessor-protection.json',dict(v17_manifest=sha(V17/'manifest.json'),artifacts=len(m['files']),code=len(m['source_files']),
                      prior_chain=read('predecessor-protection.json',V17)))
    print('Verified V17 manifest and',len(m['files']),'frozen artifact hashes',flush=True)

if __name__=='__main__':
    import sys
    {'replay':main,'protect':protect,'native_paths':native_paths}[sys.argv[1]]()
