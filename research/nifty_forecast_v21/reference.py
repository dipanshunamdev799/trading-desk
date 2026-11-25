"""Replay protected return laws and recompute earlier transfer comparisons."""
from scipy.stats import spearmanr

from .common import *
from research.nifty_forecast_v17.weekly import evaluate
from research.nifty_forecast_v20.modeling import weighted_store as _store

NATIVE = {
    5: {'exact_v14':(.228529,.010457),'v18_corporate_native':(.223481,.010318),
        'omit_latest_21_training_origins':(.221693,.010274),'price_reaction':(.223384,.010258)},
    21:{'exact_v14':(.245042,.024989),'v19_position_native':(.228199,.024010),
        'eight_calendar_day_embargo':(.228088,.024003),'smooth5':(.228602,.023786)},
}
ANCHOR = {5:'price_reaction',21:'smooth5'}
DIRECTION = {5:'omit_latest_21_training_origins',21:'eight_calendar_day_embargo'}
REBUILT = ('archived_same_clock','archived_joint_GJR')


def read_laws(root, case_file, law_file, pred):
    df=csv(case_file,root)
    df=df.loc[pred(df)].copy()
    with np.load(root/law_file,allow_pickle=False) as w:
        a,w0,ends=w['atoms'],w['weights'],w['offsets']
        checked=[]
        book={}
        for row in df.itertuples(index=False):
            i,j=ends[int(row.law):int(row.law)+2]
            values,weights=a[i:j],w0[i:j]
            res=evaluate(values,weights,row.actual)
            for k in ('brier','crps','mean','p','log_loss'):
                assert abs(res[k]-getattr(row,k))<2.e-9,(row.model,row.day,k,res[k],getattr(row,k))
            meta=dict(horizon=row.horizon,day=row.day,origin=row.origin,target_end=row.target_end,cutoff=row.cutoff,
                      cohort=row.cohort,model=row.model,active=row.active,law=len(book),reference_close=row.reference_close)
            checked.append(meta|res)
            book[(row.horizon,row.cutoff,row.model,row.day)]=(values,weights)
    return pd.DataFrame(checked),book


def reference_laws():
    selection=lambda x: np.logical_or.reduce([x.horizon.eq(h)&x.model.isin(v) for h,v in NATIVE.items()])
    native,book=read_laws(V20,'native-mechanism-cases.csv.gz','native-mechanism-laws.npz',selection)
    rebuilt,b=read_laws(V20,'architecture-cases.csv.gz','architecture-laws.npz',lambda x:x.model.isin(REBUILT))
    rebuilt.law+=len(book)
    book.update(b)
    z=pd.concat([native,rebuilt],ignore_index=True)
    for h,v in NATIVE.items():
        for name,(brier,crps) in v.items():
            t=native[native.horizon.eq(h)&native.model.eq(name)]
            assert len(t)==sum(EXPECTED[h][:2]) and abs(t.brier.mean()-brier)<6.e-7 and abs(t.crps.mean()-crps)<6.e-7
    write('protected-return-cases.csv.gz',z)
    _store(OUT/'protected-return-laws.npz',list(book.values()))
    return z


def forensic():
    v10=v20.V10
    h=csv('transfer-predictions.csv',v10,usecols=['horizon','cohort','origin','endpoint','model','p','outcome','realized_return','brier','crps'])
    assert h.origin.ge(FIRST).all() and h.endpoint.le(FREEZE).all()
    np.testing.assert_allclose(np.square(h.p-h.outcome),h.brier,rtol=0,atol=5.e-12)
    write('v10-transfer-replay.csv',h.groupby(['horizon','cohort','model'],as_index=False).agg(n=('origin','nunique'),brier=('brier','mean'),crps=('crps','mean')))
    for label in ('stock','sector'):
        p=csv(f'{label}-transfer-cases.csv.gz',V19)
        np.testing.assert_allclose(p.prediction.sub(p.actual).abs(),p.abs_error,atol=1.e-12)
        assert p.target_end.le(FREEZE).all() and p.latested.lt(p.day).all()
        g=[]
        for (t,m),q in p.groupby(['target','model']):
            def corr(z):
                if z.prediction.nunique()>1 and z.actual.nunique()>1:
                    return spearmanr(z.prediction,z.actual).statistic
                return np.nan
            rank=q.groupby('day').apply(corr,include_groups=False).mean()
            daily=q.groupby('day')[['abs_error','sq_error']].mean()
            g.append(dict(target=t,model=m,dates=q.day.nunique(),case_units=len(q),rank_corr=rank,
                          mae=daily.abs_error.mean(),rmse=np.sqrt(daily.sq_error).mean()))
        z=pd.DataFrame(g).sort_values(['target','model']).reset_index(drop=True)
        base=csv(f'{label}-transfer-leaderboard.csv',V19).sort_values(['target','model']).reset_index(drop=True)
        np.testing.assert_allclose(z[['rank_corr','mae','rmse']],base[['rank_corr','mae','rmse']],rtol=0,atol=1.e-8)
        write(f'v19-{label}-transfer-replay.csv',z)
    e=csv('stock-transfer-predictions.csv.gz',V18)
    np.testing.assert_allclose(e.pred.sub(e.actual).abs(),e.mae,rtol=0,atol=2.e-12)
    assert e.target_end.le(FREEZE).all()
    write('v18-event-transfer-replay.csv',e.groupby(['horizon','stage','model'],as_index=False).agg(
        n=('symbol','size'),dates=('day','nunique'),issuers=('symbol','nunique'),mae=('mae','mean'),mse=('se','mean'),accuracy=('accuracy','mean')))
    a=csv('temporal-cases.csv.gz',V20)
    np.testing.assert_allclose(a.p.sub(a.actual.gt(0)).pow(2),a.brier,rtol=0,atol=2.e-12)
    write('v20-temporal-replay.csv',a.groupby(['model','cohort'],as_index=False).agg(n=('day','size'),brier=('brier','mean'),crps=('crps','mean')))
    k=csv('strong-parent-component-comparisons.csv',V20)
    write('v20-late-component-reference.csv',k)
    v7=ROOT/'artifacts/nifty_forecast_v7/2026-11-24/run-001'
    f=csv('auxiliary-comparison.csv',v7)
    write('v7-auxiliary-reference.csv',f)


def run():
    manifest=read('manifest.json',V20)
    for p,root in [(manifest['files'],V20),(manifest['source_files'],ROOT)]:
        for row in p:
            assert sha(root/row['file'])==row['sha256'],row['file']
    docs=[]
    for f in [V20/'NIFTY_V20_RESEARCH.md',*sorted(V20.glob('V20_*.md'))]:
        s=f.read_text(encoding='utf-8')
        docs.append(dict(file=f.name,sha256=sha(f),lines=len(s.splitlines()),headings=[x for x in s.splitlines() if x.startswith('#')]))
    assert len(docs)==21
    z=reference_laws()
    forensic()
    save('predecessor-receipt.json',dict(manifest_sha256=sha(V20/'manifest.json'),verified_artifacts=len(manifest['files']),
         verified_code=len(manifest['source_files']),documents=docs,exact_return_laws=len(z),
         earlier_comparisons='V7 archived auxiliary, V10 directional transfer, V18 corporate event, V19 stock and sector delivery, V20 dependent temporal and late post-week.'))
    print('Replayed',len(z),'weighted return laws and prior transfer cases',flush=True)


if __name__ == '__main__':
    run()
