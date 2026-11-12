from pathlib import Path
import sys,json,time,hashlib,functools
from datetime import datetime,timezone
from concurrent.futures import ProcessPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.regime_opportunities.framework import OUT,PERIODS,build,save
from research.regime_opportunities.engine import simulate
from research.ema_validation.engine import prepare,cache_correlations,orders
from research.swing_diagnosis.common import clean

Q=None;INPUT=None
def worker_init():
    global Q,INPUT
    Q=prepare();cache_correlations(Q)
    with np.load(OUT/'portfolio-inputs.npz') as a:INPUT={k:a[k].copy() for k in a.files}
    Q['ranks']=list(INPUT['ranks'])

@functools.lru_cache(maxsize=64)
def uniform(seed):return np.random.default_rng(seed).random((len(Q['cols']),len(Q['p']['symbols'])))

@functools.lru_cache(maxsize=64)
def random_mask(style,seed):
    entry=INPUT['entry_'+style];mask=np.zeros_like(entry);u=uniform(seed)
    for j,t in enumerate(Q['cols']):
        d=t-1;pool=np.flatnonzero(Q['pool'][:,d]);k=int(entry[:,d].sum())
        if k:mask[pool[np.argsort(u[j,pool],kind='stable')[:k]],d]=True
    assert np.array_equal(mask[:,Q['cols']-1].sum(axis=0),entry[:,Q['cols']-1].sum(axis=0))
    return mask

def job(task):
    regime,style,stage,seeds,stress=task;folder=OUT/'portfolio_jobs';folder.mkdir(exist_ok=True)
    suffix='stress' if stress else 'broad' if len(seeds)==64 else 'extended';key=f'{regime}-{style}-{stage}-{suffix}'
    path=folder/(key+'.json');archive=folder/(key+'.npz')
    if path.exists() and archive.exists():return json.loads(path.read_text())
    gate=INPUT['mask_'+regime];entry=INPUT['entry_'+style];start,end=PERIODS[stage];rows=[];packed={}
    for seed in [0]+seeds:
        if style=='buyhold10' and seed:continue
        mask=(entry if seed==0 else random_mask(style,seed))&gate[None,:]
        r=simulate(Q,orders(Q,mask),start,end,cost=2 if stress else 1,slip_bps=10 if stress else 5,hold_only=style=='buyhold10')
        row=dict(regime=regime,style=style,stage=stage,seed=seed,scenario='double_fees10bps' if stress else 'baseline',**r['metrics']);row['rejections']=json.dumps(clean(row['rejections']));rows.append(clean(row))
        for k in ['equity','cash','utilization','positions','trades','cols']:packed[f'{seed}_{k}']=r[k]
    np.savez_compressed(archive,**packed);path.write_text(json.dumps(rows,allow_nan=False));return rows

def run_tasks(pool,tasks):
    rows=[];pending={pool.submit(job,t):t for t in tasks};timer=time.perf_counter()
    for i,f in enumerate(as_completed(pending)):
        rows+=f.result()
        if (i+1)%20==0 or i+1==len(tasks):print('PORTFOLIO_JOBS',i+1,'/',len(tasks),f'{time.perf_counter()-timer:.1f}s',flush=True)
    return rows

def main():
    OUT.mkdir(exist_ok=True,parents=True);q,market,tri,states,definitions=build()
    seeds=list(range(261112001,261112065));styles=['buyhold10','momentum','meanreversion','EMA','MACD','support'];regimes=['universal']+list(states)
    sources=[ROOT/'research/regime_opportunities/DESIGN.md',*sorted((ROOT/'research/regime_opportunities').glob('*.py')),Path(__file__)]
    frozen=dict(created_utc=datetime.now(timezone.utc).isoformat(),client_date='2026-11-12',regime_definitions=definitions,styles=styles,periods=PERIODS,broad_seeds=seeds,extended_seeds=list(range(261112001,261113001)),
      source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
      inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'artifacts/swing_discovery/daily-panel.npz',ROOT/'artifacts/swing_diagnosis/audit-dividend-corrected.npz',OUT/'portfolio-inputs.npz']},
      contamination='All2024–2026datespreviouslyresearched. Longindexregimesnewlycomputedretrospective, notunknownmarket history. Stockmulti-cycleinferenceunavailable.',
      priority='Fixed completed-date+historicalISINhash, shared acrossallstylesandrandomcontrols, noRSeligibility ormomentumranking.',random_matching='Exact completed-dayrawopportunitycounts; realizedtrades/exposurecanvarywith independentcash/holding paths.64seedcontextbroad,1000fortraining-onlyshortlistedcombos.')
    if (OUT/'freeze.json').exists():
        old=json.loads((OUT/'freeze.json').read_text());assert old['source_sha256']==frozen['source_sha256'];assert old['inputs']==frozen['inputs']
    else:save('freeze.json',frozen)
    from research.regime_opportunities.forward import run
    run(q,market,tri,states,definitions)
    with ProcessPoolExecutor(max_workers=4,initializer=worker_init) as pool:
        development=run_tasks(pool,[(r,s,'development',seeds,False) for r in regimes for s in styles])
        d=pd.DataFrame(development);d.to_csv(OUT/'portfolio-development.csv',index=False)
        chosen=json.loads((OUT/'training-regime-shortlist.json').read_text())['regimes'];short=[]
        for regime in chosen:
            g=d[(d.regime==regime)&d.style.ne('buyhold10')];null=g[g.seed.ne(0)].groupby('style').total_return_pct.mean();actual=g[g.seed.eq(0)].copy();actual['random_mean_return_pct']=actual['style'].map(null);actual['advantage']=actual.total_return_pct-actual.random_mean_return_pct
            actual['eligible']=(actual.total_return_pct>0)&(actual.n_trades>=20)&(actual.max_drawdown_pct<=15)&(actual.advantage>0)
            actual=actual.sort_values(['eligible','advantage'],ascending=False);row=actual.iloc[0].to_dict();row['selection_basis']='Developmentonly; regime selectedfromstockforwardopportunities independentlyofentry performance. Rejecteddiagnosticifnoeligibleentry.';short.append(row)
        save('frozen-combinations.json',dict(combinations=short,frozen_before_validation_portfolio_results=True,meaning='Trainingonlyhypotheses, notvalidatedwinners. Nochoicefromfinalresults.'))
        other=run_tasks(pool,[(r,s,stage,seeds,False) for stage in ['validation','final','two_year'] for r in regimes for s in styles]);pd.DataFrame(development+other).to_csv(OUT/'portfolio-results.csv',index=False)
        extra=[]
        for record in short:
            for stage in PERIODS:
                extra.append((record['regime'],record['style'],stage,list(range(261112001,261113001)),False));extra.append((record['regime'],record['style'],stage,[],True))
        if extra:pd.DataFrame(run_tasks(pool,extra)).to_csv(OUT/'shortlist-results.csv',index=False)
    save('execution.json',dict(regimes=len(regimes)-1,styles=len(styles),broad_runs=len(development+other),shortlisted=len(short),completed=True))
    print('REGIME_RESEARCH_COMPLETE',flush=True)

if __name__=='__main__':main()
