"""Rescore protected V21 laws and reproduce previous transfer-learning diagnostics."""
from .common import *
from research.nifty_forecast_v21.reference import read_laws
from research.nifty_forecast_v20.modeling import weighted_store

NATIVE={5:{'exact_v14':(.228529,.010457),'v18_corporate_native':(.223481,.010318),
           'omit_latest_21_training_origins':(.221693,.010274),'price_reaction':(.223384,.010258),
           'anchor_asymmetry':(.222129,.010167)},
       21:{'exact_v14':(.245042,.024989),'v19_position_native':(.228199,.024010),
           'eight_calendar_day_embargo':(.228088,.024003),'smooth5':(.228602,.023786),
           'anchor_aggregate_position':(.223819,.023184)}}
NATIVE_ANCHORS={5:('anchor_asymmetry','omit_latest_21_training_origins'),21:('anchor_aggregate_position','smooth5')}
PRE={5:('archived_same_clock','archived_joint_GJR'),21:('archived_joint_GJR','archived_same_clock','stock_gaussian_shrink')}


def reproduce():
    inc=lambda d:np.logical_or.reduce([d.horizon.eq(h)&np.where(d.cutoff.eq('native_0910'),d.model.isin(NATIVE[h]),d.model.isin(PRE[h])) for h in ORIGINAL])
    z,book=read_laws(V21,'index-forecast-cases.csv.gz','index-forecast-laws.npz',inc)
    for h in ORIGINAL:
        a=z[z.horizon.eq(h)&z.cutoff.eq('native_0910')]
        for k,(b,c) in NATIVE[h].items():
            d=a[a.model.eq(k)]
            assert len(d)==sum(EXPECTED[h][:2]) and abs(d.brier.mean()-b)<6.e-7 and abs(d.crps.mean()-c)<6.e-7
        if h==21:
            pts=a.pivot(index=['day','cohort'],columns='model',values=['brier','crps'])
            diff=pts.loc[:,(slice(None),'smooth5')].droplevel(1,axis=1)-pts.loc[:,(slice(None),'anchor_aggregate_position')].droplevel(1,axis=1)
            rr=diff.groupby('cohort').mean().reset_index()
            np.testing.assert_allclose(rr.brier,[.01969936722559,-.02289079364977],rtol=0,atol=1.e-10)
            rr['dates']=diff.reset_index().groupby('cohort').day.size().reindex(rr.cohort).to_numpy()
            write('v21-monthly-cohort-reproduction.csv',rr)
    write('protected-india-return-cases.csv.gz',z)
    weighted_store(OUT/'protected-india-return-laws.npz',list(book.values()))
    t=csv('index-tracking-leaderboard.csv',V21)
    w=t[t.model.eq('nifty50_monthly_drift_lag5')&t.scope.eq('matched')].sort_values('horizon')
    np.testing.assert_allclose(w.mae*10000,[.424416,1.383281,4.323498],rtol=0,atol=1.e-4)
    write('v21-protected-tracking.csv',w)
    return z


def prior_cases():
    z=csv('all-predictions.csv',V5,usecols=['model','horizon','stage','split','origin','endpoint','brier','p','outcome','crps'])
    assert z.origin.ge(FIRST).all() and z.endpoint.le(FREEZE).all()
    np.testing.assert_allclose(z.brier,np.square(z.p-z.outcome),rtol=0,atol=1.e-10)
    write('v5-cross-market-recomputed.csv',z.groupby(['horizon','stage','split','model'],as_index=False).agg(
          n=('origin','nunique'),brier=('brier','mean'),crps=('crps','mean')))
    p=csv('combined-cohort-leaderboard.csv',V9)
    write('v9-cross-sectional-research-archive.csv',p)
    for f in ('v10-transfer-replay.csv','v18-event-transfer-replay.csv'):
        write(f,csv(f,V21))
    p=csv('stock-date-scores.csv.gz',V21)
    f=p[p.target.isin(('absolute','market_relative','sector_relative'))&p.model.isin(('history','independent','technical','pooled','random_aux_labels'))]
    e=f.groupby(['horizon','target','model','cohort'],as_index=False).agg(n=('day','size'),stock_cases=('n','sum'),
         brier=('brier','mean'),crps=('crps','mean'),rank=('rank_corr','mean'),mae=('mae','mean'))
    write('v21-transfer-recomputed.csv',e)
    roots=[(V5,'V5_CROSS_MARKET_FEATURES.md'),(V9,'V9_CROSS_SECTIONAL_STRUCTURE.md'),(V10,'V10_STRUCTURED_TRANSFER_LEARNING.md'),
           (V18,'V18_EVENT_DRIVEN_TRANSFER_LEARNING.md'),(V21,'V21_SAMPLE_EFFICIENT_CROSS_SECTIONAL_LEARNING.md')]
    descriptors=[]
    for root,name in roots:
        f=root/name
        s=f.read_text(encoding='utf-8')
        descriptors.append(dict(file=f.relative_to(ROOT).as_posix(),sha256=sha(f),lines=len(s.splitlines())))
    return descriptors


def run():
    manifest=read('manifest.json',V21)
    for root,rows in ((V21,manifest['files']),(ROOT,manifest['code'])):
        for r in rows:
            assert sha(root/r['path'])==r['sha256'],r['path']
    docs=[]
    for loc in [V21/'NIFTY_V21_RESEARCH.md',*sorted(V21.glob('V21_*.md'))]:
        full=loc.read_text(encoding='utf-8')
        docs.append(dict(path=loc.name,sha256=sha(loc),length=len(full.splitlines()),headings=[x for x in full.splitlines() if x.startswith('#')]))
    assert len(docs)==20
    z=reproduce()
    f=prior_cases()
    save('predecessor-receipt.json',dict(v21_manifest_sha256=sha(V21/'manifest.json'),verified_files=len(manifest['files']),
         verified_code=len(manifest['code']),documents=docs,prior_transfer=f,weighted_laws=len(z),
         original_archives=['dated-weights.csv.gz','cash-identity-and-actions.csv.gz','index-tracking-leaderboard.csv']))
    print('Rescored',len(z),'prior weighted laws. V21 artifacts and transfer references verified.',flush=True)


if __name__=='__main__':
    run()
