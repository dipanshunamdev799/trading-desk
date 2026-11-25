"""Shared scope, paths and registered research decisions for V18."""
import gzip
import json
import os
from pathlib import Path
from research.nifty_forecast_v17.common import (ROOT,V4,V5,V10,V11,V12,V13,V14,V15,V16,IST,
    FIRST,FREEZE,LAST,HORIZONS,EXPECTED,now,sha,np,pd,stamp)

V17=ROOT/'artifacts/nifty_forecast_v17/2026-11-25/run-001'
SRC=Path(__file__).parent
BASE=ROOT/'artifacts/nifty_forecast_v18'
OUT=Path(os.environ.get('NIFTY_V18_OUT',BASE/'2026-11-25/run-001')).resolve()
assert OUT.is_relative_to(BASE)
SEED=181125
N_COMPANIES=240
BAR_DELAY=5
RELEASE_DELAY=10
REPORTS=(
 'REPRODUCTION_AND_BASELINES','CORPORATE_INFORMATION_DATABASE','SEMANTIC_INFORMATION_EXTRACTION',
 'FUNDAMENTAL_CHANGE_AND_EARNINGS','CORPORATE_EVENT_STUDIES','INFORMATION_DIFFUSION_NETWORKS',
 'AGGREGATE_FUNDAMENTAL_INTELLIGENCE','EXPECTATIONS_AND_MARKET_REPRICING','EVENT_CALENDAR_AND_FORWARD_RISK',
 'NON_PRICE_INFORMATION_DISCOVERY','EVENT_INFORMED_NIFTY_FORECASTING','FUNDAMENTAL_RISK_INTELLIGENCE',
 'EVENT_DRIVEN_TRANSFER_LEARNING','VALIDATION_AND_FALSIFICATION','RESEARCH_EFFICIENCY_AND_KNOWLEDGE_BASE',
 'COMPLETE_MODEL_COMPARISON','FORWARD_RESEARCH_LEDGER','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS')

def csv(name,root=OUT,**kw):
    return pd.read_csv(root/name,low_memory=False,**kw)

def save(name,x):
    path=OUT/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(x,indent=2,default=str,allow_nan=False),encoding='utf8')

def read(name,root=OUT):
    p=root/name
    return json.loads(gzip.open(p,'rt',encoding='utf-8').read() if p.suffix=='.gz' else p.read_text(encoding='utf-8-sig'))

def write(name,frame):
    path=OUT/name
    path.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(path,index=False)

def register():
    if (OUT/'registration.json').exists():
        return
    seed=csv('stock-daily-top300-policy.csv',V17).head(N_COMPANIES)
    write('issuer-seed.csv',seed)
    save('registration.json',dict(stamp=now(),historical=[FIRST,FREEZE],forward_max=LAST,seed=SEED,
     scope='All archived announcement records inventoried. The fixed first 240 issuers from V17 January NSE liquidity selection provide the inference universe. Up to 160 were targeted for structured original quarterly documents before seeing scores. All eligible native benchmark rows preserved.',
     timing='10-minute after exchange dissemination; 5-minute completed-bar allowance; financial attachments get their own release clock. Prior 17:00, next 08:55, and V14 exact native guard separate. Labels resolve before actual decision day.',
     budget={'history_days':140,'source_document_max':1280,'bootstrap_draws':1500,'blocks':[5,10,21,42],
             'refit_nulls':23,'event_horizons':[1,3,5,10,21],'return_atoms':128,'predefined_families':7},
     hypotheses=[['Semantic information', 'An explicit favorable or adverse business statement can add to category and count.',
                   'Post-reaction stock and five/21-session NIFTY', 'Next observed open or fixed index clock',
                   'Observed reaction plus category','CRPS and paired squared forecast error','Original timestamp and eligible company','Adjacent-day shift, alternate text rules, block shuffle'],
       ['Fundamental changes','Unexpected levels may differ from changes against prior reported levels.',
        'Stock excess and NIFTY returns and risk','Structured-publication clock then next eligible decision','Price, risk, sector and intensity','Brier, CRPS, MAE','Verified actual current-quarter values and older comparable releases','Strict period guard and historical sector neutral weighting'],
       ['Diffusion and transfer','Related firms may react to an event after the announcing issuer moves.',
        'Held-out issuer and peer excess return','Next available quote and after known first response','Matched non-event and price only','Paired error and cluster intervals','Point-in-time identity, peers, contemporaneous controls','Randomized categories, shifted dates, issuer exclusions'],
       ['Schedule exposure','Known events may add to option-implied risk.', 'NIFTY volatility, expansion, range and barrier touches',
        'Previous 17:00 or next 08:55','ATM IV, prior risk models and path laws','MAE, QLIKE, CRPS, Brier','Published schedule from before issue','Calendar displacement and alternative benchmark'],
       ['Residual and joint laws','Event aggregates may add independently to strong archived distributions.',
        'Original NIFTY windows','Two clocks plus native earlier law guard','V17 structural, V17 component, V14 endpoint, V16/V17 risk','Matched distribution and risk scores','Identical target date and support','Bootstrap, refit-reselection null, duplicate-column and future sentinels']],
     advancement='Require matched gain, agreement across date cohorts, robustness to delayed/shifted input and appropriate strong parents. Report exploratory winners and failures. No protection against cumulative V1–V18 selection.'))

if __name__=='__main__':
    register()
