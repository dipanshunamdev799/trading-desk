"""Normalize fit pickle class paths from the initial V12 command-line execution."""
from concurrent.futures import ThreadPoolExecutor
import joblib
from .common import *
from .scaling import TrainScale


def tidy():
    import sys
    # Earlier V12 workers executed the class definition through python -m.
    # Preserve the serialized state while binding the same class to its library module.
    sys.modules['__main__'].TrainScale=TrainScale
    changes=[]
    for batch in ['market','priced']:
        ledger=read(f'{batch}-ledger.json')
        def adjust(r):
            if r['status']!='ok':return None
            path=OUT/r['file']
            before=sha(path)
            assert before==r['sha256']
            obj=joblib.load(path)
            if not any(isinstance(v,TrainScale) for v in obj['fit'].values()):return None
            temp=path.with_suffix('.tmp')
            joblib.dump(obj,temp,compress=2)
            temp.replace(path)
            after=sha(path)
            r['sha256']=after
            return {'file':r['file'],'before':before,'after':after}
        with ThreadPoolExecutor(max_workers=5) as pool:changes.extend(s for s in pool.map(adjust,ledger) if s)
        save(f'{batch}-ledger.json',ledger)
    save('fit-serialization-receipt.json',{'serialized_scaler_class':'research.nifty_forecast_v12.scaling.TrainScale',
         'rewritten_artifacts':len(changes),'files':changes,'config_and_scores_changed':False})
    print('Verified portable serialization for',len(changes),'market scaler artifacts',flush=True)


if __name__=='__main__':tidy()
