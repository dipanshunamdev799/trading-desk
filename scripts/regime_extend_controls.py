from pathlib import Path
import sys,json
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pandas as pd
from scripts.research_regimes import worker_init,run_tasks
from research.regime_opportunities.framework import OUT,PERIODS,save

def main():
    frozen=json.loads((OUT/'freeze.json').read_text());short=json.loads((OUT/'frozen-combinations.json').read_text())['combinations'];styles=sorted(set(x['style'] for x in short))
    save('universal-extension-design.json',dict(styles=styles,reason='Universal1000seedcomparators forpairedgateinteractionofthealreadyfrozendevelopmentcombinations. Noadditionalregime/entrychoice.',seeds=frozen['extended_seeds']))
    with ProcessPoolExecutor(max_workers=4,initializer=worker_init) as pool:rows=run_tasks(pool,[('universal',s,stage,frozen['extended_seeds'],False) for s in styles for stage in PERIODS])
    pd.DataFrame(rows).to_csv(OUT/'universal-extended-results.csv',index=False);print('UNIVERSAL_EXTENSION_COMPLETE',flush=True)

if __name__=='__main__':main()
