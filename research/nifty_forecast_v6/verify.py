"""Numerical, chronology, provenance and preservation checks for the V6 study."""
import argparse, warnings, joblib
from .common import *
from .engine import validate, Distribution, cross_abs

def run(require_replay=False, require_reports=False):
    checks=[]
    def check(name,fn):
        fn();checks.append({'name':name,'passed':True});print('PASS',name,flush=True)
    def require(value):
        if not value:raise AssertionError('Verification condition failed')
    preserved=read('prior-preservation.json')['files']
    check('all '+str(len(preserved))+' prior V1–V5 files unchanged',lambda:require(all((ROOT/p).is_file() and sha(ROOT/p)==v for p,v in preserved.items())))
    check('exact named V5/V4 reconstruction',lambda:require(read('reproduction.json')['passed'] and len(read('reproduction.json')['fold_vectors'])==81))
    ref=read('reference-engine-verification.json')
    check('336 prequential outer parent forecasts exactly reconstructed',lambda:require(ref['passed'] and ref['outer_records']==336 and ref['max_probability_difference']<=1e-12))
    manifest=read('dataset-manifest.json')
    check('frozen dataset hashes',lambda:require(all(sha(OUT/p)==v for p,v in manifest['files'].items())))
    x=pd.read_csv(OUT/'native-reference.csv',index_col=0);labs={h:pd.read_csv(OUT/f'labels-{h}.csv',index_col=0) for h in [1,3,5,10,15,21]}
    check('403 native origins and 57 reference inputs',lambda:require(x.shape==(403,57) and x.index.is_monotonic_increasing and x.index.is_unique))
    check('2025–2026 feature/label scope',lambda:[scope([*l.index,*l.endpoint.dropna()]) for l in labs.values()])
    price=pd.read_csv(OUT/'price.csv',index_col=0)
    def alignment():
        close=price.close if 'close' in price else price.iloc[:,0]
        for h,l in labs.items():
            for origin,r in l.dropna(subset=['return','endpoint']).iterrows():
                np.testing.assert_allclose(r['return'],close.loc[r.endpoint]/close.loc[origin]-1,atol=1e-12)
                require(close.index.get_loc(r.endpoint)-close.index.get_loc(origin)==h)
    check('all six horizon endpoints and return labels',alignment)
    ledger=[]
    for n in ['forensic-ledger.json','model-ledger.json','monthly-ledger.json','monthly-followup-ledger.json','weekly-followup-ledger.json','prequential-ledger.json','mediation-ledger.json']:ledger.extend(read(n))
    def chronology():
        for r in ledger:
            if r.get('status')=='failed':continue
            require(r['last_endpoint']<r['cutoff'])
            if 'inner_last_endpoint' in r:require(r['inner_last_endpoint']<r['inner_first']<r['cutoff'])
    check('every fitted batch has mature/purged training labels',chronology)
    check('model hashes match recorded ledgers',lambda:require(all(sha(ROOT/r['artifact'])==r['sha256'] for r in ledger if 'artifact' in r)))
    def denied():
        idx=labs[5].index[(labs[5].endpoint<'2026-06-30') & labs[5]['return'].notna()][:20];a=x.loc[idx].copy();yy=labs[5].loc[idx,'return'].to_numpy()
        cases=[]
        b=a.copy();b['next_week_return']=0.;cases.append((b,labs[5],'2026-06-30','UNREGISTERED_FEATURE_COLUMN'))
        b=a.copy();b['p_disguised_oracle']=0.;cases.append((b,labs[5],'2026-06-30','UNREGISTERED_FEATURE_COLUMN'))
        b=a.copy();b.attrs['available_at']={a.columns[0]:['2030-01-01T00:00:00+05:30']*len(a)};cases.append((b,labs[5],'2026-06-30','FUTURE_FEATURE_AVAILABILITY'))
        bad=labs[5].copy();bad.loc[idx[0],'endpoint']='2026-06-30';cases.append((a,bad,'2026-06-30','UNMATURED_OR_EMBARGO_VIOLATION'))
        for b,l,c,error in cases:
            try:validate(b,yy,l,c)
            except ValueError as exc:require(error in str(exc))
            else:raise AssertionError('Guard failed: '+error)
        try:scope(['2024-12-31'])
        except ValueError:pass
        else:raise AssertionError('Out-of-scope date accepted')
    check('oracle aliases, unavailable features, unmatured endpoints and pre2025 data rejected',denied)
    def future_invariance():
        from .features import deep_features
        from .reproduce import frames
        from research.nifty_forecast_v5.features import build
        from research.nifty_forecast_v5.expansion import variant
        xx,_,_,data,_=frames();mutated={n:f.copy() for n,f in data.items()};cut='2026-04-01'
        for n,f in mutated.items():
            cols=[c for c in ['open','high','low','close'] if c in f];f.loc[f.index>cut,cols]*=1.123
        with warnings.catch_warnings():
            warnings.simplefilter('ignore');new,_,_=build(mutated,extra=False);a=variant('I03_nosize',new,mutated)
            np.testing.assert_allclose(a.reindex(x.index).loc[:cut,x.columns],x.loc[:cut],atol=1e-12,rtol=1e-12,equal_nan=True)
            deep=deep_features(mutated,x.index);old=pd.read_csv(OUT/'deep-features.csv',index_col=0)
            np.testing.assert_allclose(deep.loc[:cut],old.loc[:cut],atol=1e-10,rtol=1e-10,equal_nan=True)
        require(all(min(f.index)>='2025-01-01' for f in data.values() if len(f)))
    check('mutating future source prices leaves past native/evolution features unchanged',future_invariance)
    cached=[json.loads(line) for line in (OUT/'prequential-laws.jsonl').read_text().splitlines()]
    def cached_laws():
        require(len(cached)==964)
        for r in cached:
            a=np.asarray(r['atoms']);w=np.asarray(r['weights']);require(abs(w.sum()-1)<1e-10 and (w>=0).all())
            np.testing.assert_allclose(w[a>0].sum(),r['p'],atol=1e-12)
            np.testing.assert_allclose(w@a,r['mean'],atol=1e-12)
    check('all 964 parent laws have coherent probabilities and means',cached_laws)
    def learned_weights():
        for r in read('mixture-weight-ledger.json'):
            require(.1<=r['I03_weight']<=.9 and 0<=r['sign_beta']<=.75)
            dates=r['training_forecast_origins'];require(len(dates)<=42)
            for origin in dates:
                entries=[z for z in cached if z['horizon']==r['horizon'] and z['origin']==origin]
                require(len(entries)==2 and all(z['endpoint']<r['cutoff'] for z in entries))
    check('coherent mixture weights learned only from resolved past forecasts',learned_weights)
    def scoring():
        a=Distribution([-.02,-.004,.013,.04],[.1,.2,.3,.4]);b=Distribution([-.04,.006,.03],[.3,.4,.3]);y=-.007
        brute=float(a.w@abs(a.a-y)-.5*np.sum(a.w[:,None]*a.w[None,:]*abs(a.a[:,None]-a.a[None,:])))
        np.testing.assert_allclose(a.score(y)['crps'],brute,atol=1e-12)
        np.testing.assert_allclose(cross_abs(a,b),np.sum(a.w[:,None]*b.w[None,:]*abs(a.a[:,None]-b.a[None,:])),atol=1e-12)
        stats=a.stats();require(stats['p_up']==float(a.w[a.a>0].sum()))
    check('weighted CRPS and cross-distribution distance match brute-force formulas',scoring)
    pred=pd.read_csv(OUT/'all-predictions.csv')
    def output_alignment():
        require(len(pred)==11164 and not pred.duplicated(['horizon','model','origin']).any())
        for h,g in pred.groupby('horizon'):
            l=labs[h].reindex(g.origin)
            np.testing.assert_allclose(g.realized_return,l['return'],atol=1e-12)
            require((g.endpoint.to_numpy()==l.endpoint.to_numpy()).all())
            np.testing.assert_allclose(g.brier,(g.p-(g.realized_return>0))**2,atol=1e-12)
        require(((pred.p>=0)&(pred.p<=1)).all())
        require((pred.width50>=0).all() and (pred.width80>=pred.width50).all())
    check('all 11164 primary outputs have unique aligned targets and nested interval widths',output_alignment)
    def distributions():
        audit=read('distribution-audit.json');require(audit['passed'] and audit['rows']==11164 and audit['max_score_difference']<=1e-12 and audit['retained_laws']==276)
        full=pd.read_csv(OUT/'full-endpoint-predictions.csv');keys=['horizon','model','origin'];a=full.sort_values(keys);b=pred.sort_values(keys)
        np.testing.assert_allclose(a.p_up,b.p,atol=1e-12)
        np.testing.assert_allclose(a[[f'bucket{i}_p' for i in range(7)]].sum(axis=1),1.,atol=1e-12)
        require((np.diff(a[['q05','q10','q25','q50','q75','q90','q95']],axis=1)>=0).all())
        require(full.path_breach_probability.isna().all() and full.future_realized_volatility.isna().all())
    check('all complete endpoint laws recovered coherently; ordered quantiles; path risks not invented',distributions)
    def comparisons():
        d=read('strong-benchmark-comparisons.json');require(len(d)==3240)
        require(all(r['simultaneous95'] is None for r in d if r['horizon']==21))
        require(all(r['n']<=92 if r['horizon']==5 else r['n']<=76 for r in d))
        require(len(read('metrics.json'))==135)
    check('matched search families and withheld monthly confidence intervals',comparisons)
    def archives():
        for folder in ['source-at-model-batch','source-at-forensic-batch']:
            records=read(folder+'/archive-checks.json')
            require(all(v['exact'] and sha(OUT/folder/name)==v['wanted'] for name,v in records.items()))
    check('exact source versions archived for original fitted batches',archives)
    def retained_failures():
        failed=[r for r in read('experiment-registry.json') if r.get('status')=='failed'];require(len(failed)==6)
        null=read('monthly-expanded-nulls-metrics.json');require(any(r['model']=='DIAGNOSTIC_STATE' and r['brier']<.178345 for r in null))
        require(all('not passed' in r['status'] for r in read('leaderboards.json') if r['horizon']==21 and r['model'] in ['M_WEEKSTATE','M2_STATE_LAG1']))
    check('six non-estimable fits and failed monthly mechanism retained',retained_failures)
    def common_horizons():
        d=pd.read_csv(OUT/'intermediate-horizon-predictions.csv');reference=set(pred[(pred.horizon==21)&(pred.model=='M_WEEKSTATE')].origin)
        require(len(d)==608 and all(set(g.origin)==reference for _,g in d.groupby(['horizon','model'])))
    check('10/15-session diagnostics preserve the same 76 origins',common_horizons)
    if require_replay:check('fresh-folder full numerical replay',lambda:require(read('replay-verification.json')['passed']))
    if require_reports:
        names=['WINNER_FORENSICS','INDIAN_INTERNALS_DEEP_DIVE','MARKET_STATE_EVOLUTION','GLOBAL_INCREMENTAL_RESEARCH','MODEL_ARCHITECTURES','COHERENT_DISTRIBUTIONS','MONTHLY_RESEARCH','CONDITIONAL_FORECASTING','VALIDATION_AND_LEAKAGE_AUDIT','COMPLETE_MODEL_COMPARISON','SIGNAL_RANKING','FINAL_RESEARCH_DECISION','NEXT_EXPERIMENTS']
        check('all thirteen reports delivered',lambda:require(all((OUT/f'V6_{n}.md').is_file() and (OUT/f'V6_{n}.md').stat().st_size>900 for n in names)))
        def report_hashes():
            manifest=read('report-manifest.json');require(len(manifest['reports'])==13)
            require(all(sha(OUT/n)==v for n,v in manifest['reports'].items()))
            require(sha(ROOT/'NIFTY_V6_RESEARCH.md')==manifest['root_index_sha256'])
        check('report and root-index hashes match the delivery manifest',report_hashes)
    save('verification.json',{'completed_at':now(),'passed':True,'checks':checks,'require_replay':require_replay,'require_reports':require_reports,'prior_file_count':len(preserved)})
    print('Verified',len(checks),'checks',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--require-replay',action='store_true');parser.add_argument('--require-reports',action='store_true');args=parser.parse_args();run(args.require_replay,args.require_reports)
