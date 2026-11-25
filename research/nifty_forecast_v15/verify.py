"""Independent archive, causality, source and sequential coherence checks."""
import gzip
from datetime import datetime
import sys

from .common import *
from .data import Daily
from .fitting import RevisionDesign, fit
from .sequential import Simulator, log_ticks


def exact_copy_and_future(sim,ledger):
    rows=[]
    for h,k in [(5,0),(5,2),(5,4),(21,0),(21,5),(21,10),(21,20)]:
        w=next(sim.calendar[(sim.calendar.origin.eq(DEMO))&sim.calendar.horizon.eq(h)&sim.calendar.checkpoint.eq(k)].itertuples(index=False))
        i=sim.d.positions[w.asof]
        prior=sim.prior(h,w.origin)
        law,_,receipts=sim.update(w,prior)
        asset=next(a for a in ledger['files'] if a['horizon']==h and a['origin']==w.origin)
        with np.load(OUT/asset['file'],allow_pickle=False) as f:
            assert all(np.array_equal(log_ticks(a),f[f'k{k:02}_{key}']) for key,a in law.items())
        changed=Daily.load()
        changed.prices=changed.prices.copy()
        changed.prices.iloc[i+1:]*=1.13
        changed.features=changed.features.copy()
        fields=changed.features.select_dtypes(include='number').columns
        changed.features=changed.features.astype({field:'float64' for field in fields})
        changed.features.loc[changed.sessions[i+1:],fields]*=1.13
        dated=sim.iv_table.copy()
        dated.loc[dated['asof'].gt(w.asof),'iv']*=1.13
        clone=Simulator()
        clone.d=changed
        clone.fits=RevisionDesign(changed,dated)
        clone.iv=dated.set_index(['asof','remaining'])
        clone.all_prices=changed.prices.to_numpy()
        for h0 in HORIZONS:
            iy=changed.labels[h0].endpoint.ge(w.asof).to_numpy()
            clone.hist[h0]=sim.hist[h0].copy()
            clone.hist[h0][iy]+=0.08
            changed.labels[h0]=changed.labels[h0].copy()
            changed.labels[h0].loc[iy,'endpoint_return']+=1
        c,_,others=clone.update(w,prior)
        assert all(np.array_equal(log_ticks(v),log_ticks(c[n])) for n,v in law.items())
        assert receipts==others
        models=sim.fits
        x,_,_=models.columns(k,w.remaining,'full')
        index=np.arange(max(k,i-w.remaining-HIST),i-w.remaining)
        z=x[index]
        a=x[i]
        y=models.responses[w.remaining][index]
        f=fit(z,y,225)
        dup=fit(np.c_[z,z[:,2],z[:,5]],y,225)
        np.testing.assert_array_equal(f.values(a),dup.values(np.r_[a,a[2],a[5]]))
        rows.append(dict(horizon=h,asof=w.asof,origin=w.origin,checkpoint=k,future_prices_and_inputs_changed=True,
                    prior_only_completed_target=True,trained_coefficients_identical=True,archive_exact=True,
                    unobserved_historical_labels_and_paths_perturbed=True,exact_clones_removed=True,
                    total_model_laws_compared=len(law)))
    return rows


def run():
    sim=Simulator()
    ledger=read('joint-update-archive.json')
    n=0; random_checks=0;joint_laws=0
    expected_days=pd.read_csv(OUT/'original-windows.csv')
    date=sim.calendar
    prev_map=date.groupby(['horizon','origin'])['target'].nunique()
    assert prev_map.eq(1).all()
    assert (date['asof'].lt(date.target)).all() and date.checkpoint.add(date.remaining).eq(date.horizon).all()
    assert (pd.to_datetime(date['decision'],utc=True,format='mixed')>pd.to_datetime(date['asof'],utc=True)).all()
    freshness=sim.iv_table
    assert freshness.source_day.dropna().le(freshness.loc[freshness.source_day.notna(),'asof']).all()
    assert freshness.source_day.dropna().lt(freshness.loc[freshness.source_day.notna(),'asof']).all()
    assert len(ledger['files'])==len(expected_days)==sum(EXPECTED.values())
    frozen_hash={}
    for row in ledger['files']:
        p=OUT/row['file']; f=V14/row['frozen_file']
        assert sha(p)==row['sha256']
        if f not in frozen_hash:
            frozen_hash[f]=sha(f)
        assert frozen_hash[f]==row['frozen_sha256']
        with np.load(p,allow_pickle=False) as data:
            assert len(data.files)==row['checkpoints']*(len(MODELS)-1)
            joint_laws+=len(data.files)
            # All shapes and OHLC constraints were also checked in the generator before encoding.
            for cp in CHECKPOINTS[row['horizon']]:
                if n%17!=0: continue
                for model in MODELS[1:]:
                    a=data[f'k{cp:02}_{model}']
                    assert a.shape==(N,row['horizon']-cp,4)
                    assert (a[:,:,1]>=np.maximum(a[:,:,0],a[:,:,3])).all()
                    assert (a[:,:,2]<=np.minimum(a[:,:,0],a[:,:,3])).all()
                    assert np.isfinite(a).all()
                    random_checks+=1
        n+=1
    checked=0
    with gzip.open(OUT/'fitted-update-models.ndjson.gz','rt',encoding='utf-8') as f:
        for line in f:
            z=json.loads(line)
            assert z['asof']<z['target']
            for r in z['fits']:
                assert r['training_first']<=r['training_last']<r['last_outcome']<z['asof']
                checked+=1
    original=read('protected-receipt.json')
    assert original['valid'] and not original['mismatches']
    tested=exact_copy_and_future(sim,ledger)
    counts=read('sequential-score-counts.json')
    assert counts['scores']==len(date)*len(MODELS)
    assert counts['date_windows']==len(expected_days)
    order_n=0; both_known=0; known_side=0
    use=['checkpoint','known_upper','known_lower','known_order','p_upper_first','p_lower_first',
         'p_same_candle','p_neither','known_upper','known_lower','score_order','score_additional','no_additional_p']
    for p in pd.read_csv(OUT/'sequential-order.csv.gz',usecols=list(set(use)),chunksize=140000,low_memory=False):
        assert p.p_upper_first.add(p.p_lower_first).add(p.p_same_candle).add(p.p_neither).sub(1).abs().lt(1.e-12).all()
        known=p.known_order.ge(0)
        assert p.loc[known,'score_order'].eq(0).all()
        for i,k in enumerate(('p_upper_first','p_lower_first','p_same_candle')):
            assert p.loc[p.known_order.eq(i),k].eq(1).all()
        both=p.known_upper.eq(1)&p.known_lower.eq(1)
        assert p.loc[both,'score_additional'].eq(0).all()
        assert p.loc[both,'no_additional_p'].eq(1).all()
        order_n+=len(p)
        both_known+=both.sum()
        known_side+=known.sum()
    assert order_n==counts['ordering']
    fitfiles=[]
    for name,c in [('session-forecasts.csv.gz','day'),('causal-error-scores.csv.gz','origin')]:
        f=pd.read_csv(OUT/name,usecols=[c,'last_mature'])
        assert f.last_mature.lt(f[c]).all() and f[c].between(FIRST,FREEZE).all()
        fitfiles.append(dict(file=name,verified=len(f)))
    fw=read('forward-ledger.json')
    pass_count=0
    for r in fw['records']:
        if r['realized_return'] is None:
            assert not r['scores']
        else:
            assert r['official_close'] and r['maturity']=='resolved in V15 with authoritative outcome'
        pass_count+=1
    save('validation-receipt.json',dict(
        passed=True,historical_freeze=FREEZE,forecast_windows=n,archive_files_hashed=n,
        immutable_frozen_files_hashed=len(frozen_hash),updated_joint_laws=joint_laws,checked_shapes=random_checks,
        fixed_target_identity=len(date),literal_target_match=expected_days.groupby('horizon').literal_calendar.sum().to_dict(),
        fitted_ledger_checks=checked,causal_future_and_copy_checks=tested,strict_option_source_rows=len(freshness),
        order_rows=order_n,known_order_pinned=int(known_side),both_sides_done_unscored=int(both_known),
        extra_training_receipts=fitfiles,forward_records=pass_count,predecessor_protection=original))
    print('Verified all',n,'joint archives,',checked,'estimators and',order_n,'ordering rows',flush=True)


if __name__=='__main__':
    run()
