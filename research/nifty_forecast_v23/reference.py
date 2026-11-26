"""Reproduce V22 benchmark laws and audit named differences."""
from .common import *
from .laws import loaded,piece
from research.nifty_forecast_v17.weekly import evaluate

EXPECTED = {
    5: {'exact_v14':(.228529,.010457), 'v18_corporate_native':(.223481,.010318),
        'omit_latest_21_training_origins':(.221693,.010274), 'anchor_asymmetry':(.222129,.010167),
        'secondary_location_beyond_gift':(.220133,.010180), 'secondary_location_domestic_only':(.220368,.010130),
        'parent_location_domestic_only':(.222142,.010121)},
    21: {'exact_v14':(.245042,.024989), 'v19_position_native':(.228199,.024010), 'smooth5':(.228602,.023786),
         'anchor_aggregate_position':(.223819,.023184), 'parent_mixture_foreign_tail':(.223431,.023174)}
}
PARENTS = {
    (5,'native_0910'):('V22/secondary_location_beyond_gift','V22/parent_location_domestic_only'),
    (21,'native_0910'):('V22/parent_mixture_foreign_tail','V22/anchor_aggregate_position'),
    (5,'preauction_0855'):('V22/archived_same_clock','V21/anchor_asymmetry'),
    (21,'preauction_0855'):('V22/archived_same_clock','V22/archived_joint_GJR'),
    (5,'previous_1700'):('V17/clock_structural','V17/fixed_structural_mixture'),
    (21,'previous_1700'):('V17/neutral','V17/fixed_structural_mixture'),
}


def run():
    manifest=read('manifest.json',V22)
    for root, entries in ((V22,manifest['files']),(ROOT,manifest['code'])):
        for r in entries:
            assert sha(root/r['path'])==r['sha256'],r['path']
    docs=[]
    for p in [V22/'NIFTY_V22_RESEARCH.md',*sorted(V22.glob('V22_*.md'))]:
        m=p.read_text(encoding='utf-8')
        docs.append(dict(file=p.name,sha256=sha(p),lines=len(m.splitlines()),sections=[x for x in m.splitlines() if x.startswith('#')]))
    assert len(docs)==18
    z=csv('india-forecast-cases.csv.gz',V22)
    a,w,e=loaded(V22,'india-forecast-laws.npz')
    assert len(z)==75891 and z.law.to_list()==list(range(len(z)))
    np.testing.assert_allclose(np.add.reduceat(w,e[:-1]),1.,rtol=0,atol=1.e-12)
    np.testing.assert_allclose(np.add.reduceat(a*w,e[:-1]),z['mean'],rtol=0,atol=2.e-12)
    np.testing.assert_allclose(np.add.reduceat(w*(a>0),e[:-1]),z.p,rtol=0,atol=2.e-12)
    p0=[]
    for (h,clock,model),g in z.groupby(['horizon','cutoff','model']):
        if not (clock=='native_0910' and model in EXPECTED[h]) and not (h==21 and clock=='preauction_0855' and model=='archived_same_clock'):
            continue
        book=[]
        for r in g.itertuples(index=False):
            law=piece((a,w,e),r.law)
            ss=evaluate(law.atoms,law.weights,r.actual)
            for k in ('brier','crps','log_loss','p','mean'):
                assert abs(ss[k]-getattr(r,k))<2.e-9,(clock,model,k,r.day)
            book.append(dict(horizon=h,clock=clock,model=model,day=r.day,cohort=r.cohort,rank=r.law,**ss))
        q=pd.DataFrame(book)
        score=q[['brier','crps']].mean()
        if model in EXPECTED[h]:
            np.testing.assert_allclose(score,EXPECTED[h][model],rtol=0,atol=6.e-7)
        else:
            assert np.allclose(g.p,.5,rtol=0,atol=1.e-11)
        p0.append(q)
    exact=pd.concat(p0,ignore_index=True)
    write('exact-v22-benchmark-cases.csv.gz',exact)
    write('exact-v22-benchmark-scores.csv',exact.groupby(['horizon','clock','model'],as_index=False).agg(
        n=('day','size'),mean_up=('p','mean'),brier=('brier','mean'),crps=('crps','mean'),mae=('mae','mean')))
    old=csv('india-protected-same-clock-path-cases.csv.gz',V22)
    new=csv('india-risk-path-comparison-cases.csv.gz',V22)
    risk=pd.concat([old[old.model.eq('same_clock_GJR')],new[new.model.isin(('analogue_india_on_IV_GJR','analogue_global_on_IV_GJR'))]])
    risk=risk.groupby(['horizon','model'],as_index=False).agg(n=('day','size'),range_crps=('range_crps','mean'),drawdown_crps=('drawdown_crps','mean'))
    monthly=risk[risk.horizon.eq(21)].set_index('model')
    np.testing.assert_allclose(monthly.loc[['same_clock_GJR','analogue_india_on_IV_GJR','analogue_global_on_IV_GJR'],'range_crps'],
                                  [.015488,.014409,.014195],rtol=0,atol=6.e-7)
    write('exact-v22-risk-reference.csv',risk)
    q=csv('india-risk-analogue-source-sensitivity.csv',V22)
    g=q.groupby(['horizon','model'],as_index=False).agg(n=('day','size'),range_crps=('range_crps','mean'))
    assert abs(g.loc[g.horizon.eq(21)&g.model.eq('drop_low_agreement_sources'),'range_crps'].iloc[0]-.014260)<6.e-7
    write('reproduced-v22-source-exclusions.csv',g)
    p=z[z.cutoff.eq('native_0910')].pivot(index=['horizon','day'],columns='model',values=['brier','crps'])
    inputs=[(5,'anchor_asymmetry','secondary_location_beyond_gift'),(21,'anchor_aggregate_position','parent_mixture_foreign_tail')]
    rows=[]
    for h,parent,candidate in inputs:
        q0=p.loc[h].dropna(subset=[('brier',parent),('brier',candidate)])
        for metric in ('brier','crps'):
            gain=q0[metric][parent]-q0[metric][candidate]
            k=np.argmax(np.convolve(gain,np.ones(21),'valid'))
            skipped=gain.iloc[k:k+21]
            rows.append(dict(horizon=h,parent=parent,model=candidate,metric=metric,lo=skipped.index[0],hi=skipped.index[-1],
                            omitted_gain=skipped.mean(),remaining_gain=gain.drop(skipped.index).mean(),n=len(gain)))
    write('reproduced-v22-episode-removals.csv',pd.DataFrame(rows))
    q=z[z.cutoff.eq('preauction_0855')&z.model.str.startswith(('adapt_foreign_random','adapt_foreign_prior','adapt_zero_centered','adapt_strong_zero'))]
    write('reproduced-v22-foreign-prior-placebos.csv',q.groupby(['horizon','model'],as_index=False).agg(n=('day','size'),
            brier=('brier','mean'),crps=('crps','mean'),mae=('mae','mean')))
    write('protected-v21-cohort-flip.csv',csv('v21-monthly-cohort-reproduction.csv',V22))
    save('predecessor-verification.json',dict(verified_at=now(), files=len(manifest['files']),code_files=len(manifest['code']),
        weighted_laws=len(z),complete_proper_score_replays=len(exact),documents=docs,manifest_sha256=sha(V22/'manifest.json'),
        audit='The brief combined measures from two different domestic-only model IDs. Verified and archived separately; the native weekly Brier bar is never coupled with the other row’s CRPS.',
        neutral='Recovered V22 pre-auction monthly archived_same_clock law with exactly .5 positive mass. Native references retain their own cutoff.'))
    print('Verified V22',len(z),'law summaries and',len(exact),'full benchmark scores.',flush=True)


if __name__=='__main__':
    run()
