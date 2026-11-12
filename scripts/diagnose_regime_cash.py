from pathlib import Path
import sys,json,inspect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import research.regime_opportunities.engine as engine
from scripts import research_regimes as core
from research.regime_opportunities.framework import OUT,PERIODS,save
from research.ema_validation.engine import orders

def main():
    core.worker_init();source=inspect.getsource(engine.simulate)
    # Diagnostic only: retain the infeasible path to measure the original failure;
    # never use its returns as a capital-compliant result or change frozenengine.
    source=source.replace("raise AssertionError('Cash/position invariant')","pass")
    namespace=vars(engine).copy();exec(source,namespace);diagnostic=namespace['simulate'];rows=[]
    frozen=json.loads((OUT/'freeze.json').read_text())
    for stage in ['development','two_year']:
        regime='persistent_up';style='momentum';gate=core.INPUT['mask_'+regime]
        for seed in frozen['extended_seeds']:
            r=diagnostic(core.Q,orders(core.Q,core.random_mask(style,seed)&gate[None,:]),*PERIODS[stage])
            if r['cash'].min() < -1e-6:
                ix=int(np.argmin(r['cash']));day=int(r['cols'][ix]);t=r['trades'];closing=t[t[:,3]==day]
                row=dict(regime=regime,style=style,stage=stage,seed=seed,min_cash=float(r['cash'].min()),day=str(core.Q['p']['dates'][day].date()),equity_at_min=float(r['equity'][ix]),closing_trades=closing.tolist(),closing_symbols=[core.Q['p']['symbols'][int(s)] for s in closing[:,0]],invalid_path_not_for_inference=True)
                rows.append(row);print(json.dumps(row),flush=True)
    save('cash-invariant-diagnosis.json',dict(invalid_runs=rows,reason='Originalcashlimitreservesentryfeesbutnotallfuturefixedsellingfees. Ifoneverysmallresidualpositionissold,itsproceedsmaynotcoverfixedsellfeeswhileallothercashisdeployed. Verifyrecordedtrades; noaffectedsimulationpromoted.',
      treatment='Preservefailedseedanddiagnostictrace. Failedpathsarenotvalid fundedreturns; no frozenparameters or initialresearchmodified.'))
    print('CASH_DIAGNOSIS_COMPLETE',len(rows),flush=True)

if __name__=='__main__':main()
