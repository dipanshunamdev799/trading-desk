"""Resume after an output-schema import fix; preserve initial protocol verbatim."""
from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pandas as pd
from scripts.research_regimes import worker_init,run_tasks
from research.regime_opportunities.framework import OUT,PERIODS,save

def main():
    frozen=json.loads((OUT/'freeze.json').read_text());current={k:hashlib.sha256((ROOT/k).read_bytes()).hexdigest() for k in frozen['source_sha256']}
    changed=[k for k,v in current.items() if v!=frozen['source_sha256'][k]]
    assert changed==['research\\regime_opportunities\\engine.py'],changed
    assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in frozen['inputs'].items())
    save('runtime-amendment.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),reason='Initialworkerfailedbeforewritinganyportfoliorun:outputTRADE_COLUMNSconstantnotimported. Importadded; tradinglogic,definitions,seeds,parametersandselectionunchanged.',
      original_source_sha256=frozen['source_sha256'],execution_source_sha256=current,preserved_protocol_sha256=hashlib.sha256((OUT/'freeze.json').read_bytes()).hexdigest()))
    seeds=frozen['broad_seeds'];regimes=['universal']+[x['regime'] for x in frozen['regime_definitions']];styles=frozen['styles']
    with ProcessPoolExecutor(max_workers=4,initializer=worker_init) as pool:
        development=run_tasks(pool,[(r,s,'development',seeds,False) for r in regimes for s in styles]);d=pd.DataFrame(development);d.to_csv(OUT/'portfolio-development.csv',index=False)
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
                extra.append((record['regime'],record['style'],stage,frozen['extended_seeds'],False));extra.append((record['regime'],record['style'],stage,[],True))
        if extra:pd.DataFrame(run_tasks(pool,extra)).to_csv(OUT/'shortlist-results.csv',index=False)
    save('execution.json',dict(regimes=len(regimes)-1,styles=len(styles),broad_runs=len(development+other),shortlisted=len(short),completed=True))
    print('REGIME_RESEARCH_COMPLETE',flush=True)

if __name__=='__main__':main()
