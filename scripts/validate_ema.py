from pathlib import Path
import sys,json,time,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from research.ema_validation.engine import *

def random_masks(q,seed):
    rng=np.random.default_rng(seed);u=rng.random((len(q['p']['dates']),len(q['p']['symbols'])))
    result={}
    for rs_on in [0,1]:
        pool=q['pool']&(q['rs'] if rs_on else True);source=q['ema']&pool;mask=np.zeros_like(source)
        for t in q['cols']:
            d=t-1;ids=np.flatnonzero(pool[:,d]);k=int(source[:,d].sum())
            if k>len(ids):raise AssertionError('Random opportunity pool too small')
            if k:mask[ids[np.argsort(u[d,ids],kind='stable')[:k]],d]=True
        assert np.array_equal(mask[:,q['cols']-1].sum(axis=0),source[:,q['cols']-1].sum(axis=0))
        result[rs_on]=mask
    return result

def main():
    OUT.mkdir(parents=True,exist_ok=True);seed_dir=OUT/'random_paths';seed_dir.mkdir(exist_ok=True)
    q=prepare();cache_correlations(q);seeds=list(range(120260001,120261001))
    freeze={'created_utc':datetime.now(timezone.utc).isoformat(),'client_date':'2026-11-12','seeds':seeds,'config':q['cfg'],
      'stages':{'two_year':['2024-11-10','2026-11-10'],'final_reset':['2026-05-10','2026-11-10']},
      'definition_document_sha256':hashlib.sha256((ROOT/'research/ema_validation/DESIGN.md').read_bytes()).hexdigest(),
      'engine_sha256':hashlib.sha256((ROOT/'research/ema_validation/engine.py').read_bytes()).hexdigest(),
      'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OLD/'daily-panel.npz',OLD/'panel-index.json',OLD/'universe.json',OLD/'frozen-finalists.json',ROOT/'artifacts/swing_diagnosis/audit-dividend-corrected.npz',ROOT/'research/swing_diagnosis/portfolio.py']},
      'random_matching':'Exact EMA eligible opportunity count per completed signal date; independent portfolio paths can produce different realized trades/exposure. Shared uniform keys across all factor cells, no future executed-count matching.',
      'rs_ablation_scope':'Remove RS eligibility only; frozen momentum ranking remains.',
      'contamination':'All historical dates already inspected. Conditional randomization does not correct strategy discovery.',
      'journal_columns':TRADE_COLUMNS,'reason_codes':REASONS}
    if (OUT/'freeze.json').exists():
        old=json.loads((OUT/'freeze.json').read_text())
        for k in ['engine_sha256','definition_document_sha256','inputs','config','seeds']:assert old[k]==freeze[k],k
    else:save('freeze.json',freeze)
    save('calendar.json',{'dates':[str(d) for d in q['p']['dates']],'symbols':q['p']['symbols'],'sectors':q['p']['sector']})
    def execute(mask,rs,random,seed):
        packed={};rows=[]
        for gate in [0,1]:
            cell=('B' if gate else 'D') if random else ('A' if gate else 'C')
            entry=mask&(q['gate'][None,:] if gate else True);order=orders(q,entry)
            for stage,(start,end) in freeze['stages'].items():
                r=simulate(q,order,start,end);label=f'{cell}_rs{rs}_{stage}'
                row=dict(seed=seed,cell=cell,rs_filter=rs,stage=stage,**r['metrics']);row['rejections']=json.dumps(row['rejections']);rows.append(row)
                for k in ['equity','cash','utilization','positions','trades','cols']:packed[label+'_'+k]=r[k]
        return rows,packed
    rows=[];pack={}
    for rs in [0,1]:
        a,b=execute(q['ema']&q['pool']&(q['rs'] if rs else True),rs,False,0);rows+=a;pack.update(b)
    np.savez_compressed(OUT/'deterministic_paths.npz',**pack);pd.DataFrame(rows).to_csv(OUT/'deterministic-results.csv',index=False)
    timer=time.perf_counter();allrows=[]
    for i,seed in enumerate(seeds):
        target=seed_dir/f'{seed}.npz';summary=seed_dir/f'{seed}.json'
        if target.exists() and summary.exists():allrows+=json.loads(summary.read_text());continue
        masks=random_masks(q,seed);pack={};rows=[]
        for rs in [0,1]:
            a,b=execute(masks[rs],rs,True,seed);rows+=a;pack.update(b)
        np.savez_compressed(target,**pack);summary.write_text(json.dumps(clean(rows),allow_nan=False));allrows+=rows
        if (i+1)%25==0:print('RANDOM_SEEDS',i+1,'/1000',f'{time.perf_counter()-timer:.1f}s',flush=True)
    pd.DataFrame(allrows).to_csv(OUT/'random-results.csv',index=False)
    save('execution.json',dict(seeds=len(seeds),random_runs=len(allrows),deterministic_runs=8,all_opportunity_counts_matched=True,elapsed_seconds=time.perf_counter()-timer))
    print('VALIDATION_RUNS_COMPLETE',flush=True)

if __name__=='__main__':main()
