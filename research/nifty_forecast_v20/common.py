"""V20 scope and experiment registration."""
import gzip
import json
import os
from pathlib import Path

from research.nifty_forecast_v19.common import (
    ROOT,V4,V5,V10,V11,V12,V13,V14,V15,V16,V17,V18,IST,FIRST,FREEZE,LAST,
    EXPECTED,now,sha,np,pd,stamp,
)

V19=ROOT/'artifacts/nifty_forecast_v19/2026-11-25/run-001'
SRC=Path(__file__).parent
AREA=ROOT/'artifacts/nifty_forecast_v20'
OUT=Path(os.environ.get('NIFTY_V20_OUT',AREA/'2026-11-25/run-001')).resolve()
assert OUT.is_relative_to(AREA)
BRIEF=Path('C:/Users/ME/.codex/attachments/fbe65f8a-9b21-49c0-ad9a-c56a6e9e3e96/Pasted text.txt')
CLOCKS=('previous_1700','preauction_0855')
NATIVE='native_0910'
HORIZONS=(5,21)
LIFETIMES=(1,2,3,5,7,10,15,21)
INCREMENTS=((0,1),(1,3),(3,5),(5,10),(10,15),(15,21))
COMPONENTS=((0,5),(5,10),(10,15),(15,21))
AGES=('fresh','lag1','lag3','lag5','lag10','lag21','smooth5')
Q=(np.arange(96)+.5)/96
SEED=201125
REPORTS=(
 'REPRODUCTION_AND_TIMING_AUDIT','CUMULATIVE_INFORMATION_REGISTRY','PREDICTIVE_INFORMATION_LIFETIMES',
 'MONTHLY_POSITIONING_MECHANISMS','WEEKLY_CORPORATE_INFORMATION_MECHANISMS','HORIZON_SPECIALIZED_MODELS',
 'TEMPORAL_RETURN_DECOMPOSITION','INFORMATION_COMPLEMENTARITY','STRUCTURAL_RESIDUAL_CORRECTIONS',
 'CORRECTION_ACTIVATION_RESEARCH','HORIZON_SPECIALIZED_RISK_MODELS','PREDICTABILITY_AND_INFORMATION_LIMITS',
 'ADDITIONAL_INFORMATION_DISCOVERY','EXPERIMENTAL_FORECASTING_FRAMEWORK','VALIDATION_AND_FALSIFICATION',
 'HYPOTHESIS_REGISTRY_AND_SEARCH_EFFICIENCY','COMPLETE_MODEL_COMPARISON','FORWARD_RESEARCH_LEDGER',
 'FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS',
)

def read(name,root=OUT):
    p=root/name
    if p.suffix=='.gz':
        with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)
    return json.loads(p.read_text(encoding='utf-8-sig'))

def csv(name,root=OUT,**kw):
    return pd.read_csv(root/name,low_memory=False,**kw)

def write(name,d):
    p=OUT/name
    p.parent.mkdir(parents=True,exist_ok=True)
    d.to_csv(p,index=False)

def save(name,d):
    p=OUT/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,indent=2,allow_nan=False,default=str),encoding='utf-8')

def receipt(name,rows):
    with gzip.open(OUT/name,'wt',encoding='utf-8') as f:
        for r in rows:f.write(json.dumps(r,default=str,allow_nan=False)+'\n')

def register():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'registration.json').is_file():return
    (OUT/'MISSION.md').write_bytes(BRIEF.read_bytes())
    design=[
      ('Opening absorption','A tradable offshore price may primarily inform the first cash repricing','Offshore GIFT','Cumulative and incremental','08:55','Cash price state','CRPS','Aged offshore price, late components','One regularized fit per cell','Advance only with matched late-window or first-session separation'),
      ('Global transfer','Foreign returns can map to early or late Indian returns','Global equity','All windows','17:00 and 08:55','Cash price state','CRPS','Session delays','Shared lifetime design','Check sign away from major shocks'),
      ('Structural persistence','Rotation and breadth can describe distinct durations of market state','Domestic, financial, equal weight, stock breadth','All windows','Same-clock','Cash price state','CRPS','Different components, dated breadth','Four frozen families','Keep components that improve on matched strong parents'),
      ('Corporate lifetime','The effect of filing intensity, information and reactions may be front-loaded','Corporate publications and structured financials','All windows and weekly native','08:55 inputs at 09:10 native or matched 17:00/08:55','Exact V14 and cash price state','Brier and CRPS','Bias, vintaged delays and rotated information','Fixed count, semantic, structured and schedule groups','Compare conditional asymmetry and high-activity dates'),
      ('Positioning lifetime','Persistent exposures may inform future sessions after the first week','NSE participant reports','All windows and monthly native','Strictly eligible report time','Exact V14 and cash price state','CRPS and Brier','Measure segments after session five, lags 1/3/5/10/21','One matched grid and a bounded native group analysis','Check later origins and native bias'),
      ('Position surprises','Regime-conditioned historical analogues may explain ordinary exposure changes','NSE participant OI and ordinary futures','Monthly and its late pieces','Next-session 08:15 release guard','Ordinary changes and exact V14','CRPS','Compare raw and analogue innovation on identical dates','One 15-neighbor causal specification','Require stable addition beyond changes'),
      ('Positioning instability','Participant loadings and market state may change between cohorts','Index FII, DII, Pro, gross, concentration, volume, stock futures and options','Monthly original','09:10 native','Exact V14','Brier and CRPS','Training-window, expiry and episode omission','Two training windows, causal strata','Advance only with positive dispersion-aware gains'),
      ('Other activity','Delivery and disclosed deals may encode different durations','Historical NSE delivery and deal archives','Cumulative and incremental','Next-session release guard','Cash price state','CRPS','Delayed data and ordinary turnover proxy','Two simple families','Require improvement in both subperiods'),
      ('Implied versus realized risk','Risk may persist even if return direction fades','ATM IV, surface, historical volatility and prior intraday state','Realized risk and terminal laws','Exact 17:00/08:55','IV/GJR, cash price','QLIKE and range CRPS','Compare location-only, scale-only and delays','Fixed risk and 256 coherent scenarios per origin','Qualify direction and risk separately'),
      ('Authentic flow lifetimes','Confirmed and provisional flows differ in trade date and vintage','Exchange, depository and public fund sources','Matched release windows','Documented availability or conservative descriptive lag','Cash history','CRPS or coverage','Response-date versus release-date','One aggregate per authenticated route','Require dated support and data novelty'),
      ('Horizon specialization','Shared market states can benefit from different horizon outputs','Five registered structural groups','Original 5 and 21','08:55','Same-clock V17/neutral','Brier and CRPS','Equal-complexity matched shared/separate fit','Seven architectures with one shared training policy','Require robustness after search adjustment'),
      ('Temporal joint law','Early and late returns can be estimated with different information while retaining dependence','Structural, corporate and positioning','Four monthly components and endpoint','08:55','Direct same-clock estimator','CRPS','Independent residual resampling and zero component correction','Four components, one rank-two fit','Measure whether late gains survive'),
      ('Complementarity','Feature groups can duplicate or conflict under estimation','Native market, corporate, positioning, delivery and risk','Original 5 and 21','08:55','Same-clock V17','Brier and CRPS','Exact feature and expert copy','32 fixed subset evaluations with joint attribution','Advance only stable incremental blocks'),
      ('Residual laws','Location, mass, scale and tails can be modified coherently','V14/V18 laws and V20 causal corrections','Original 5 and 21','09:10 native','Exact parent and bias-only','Brier and CRPS','Zero, bias removal, fixed weight, full coverage','Fixed transforms and one chronological weight','Measure active and full population separately'),
      ('Activation','A narrow decision rule may trade off coverage and expected loss','Announcement, concentration, IV, distance and disagreement','Original 5 and 21','09:10 native','Exact parent','Brier and CRPS','Always-on and fixed fractional correction','One prior-rank rule and one regularized reliability model','Demand gains including fallback and matched dates'),
      ('Predictability limits','Serial dependence and changing training episodes reduce power','Forecast errors and auxiliary sector/stock data','Original weekly/monthly and lifetime cells','Identical cutoff','Exact parent','Detectable paired effect','Clustered draws, all phases, training block omission','1000 power simulations and 23 representative null refits','Translate uncertainty into new dated data needs'),
    ]
    cols=('hypothesis','rationale','family','target','cutoff','parent','primary_metric','negative_control','budget','follow_up')
    save('registration.json',dict(registered_at=now(),scope=[FIRST,FREEZE],max_forward=LAST,seed=SEED,
        prediction_horizons=HORIZONS,discovery_horizons=LIFETIMES,increments=INCREMENTS,ages=AGES,
        exact_cohorts={5:[173,92,265,53],21:[141,76,217,11]},
        train=dict(ridge=160,min_mature_labels=45,max_mature_labels=140,selection='Strictly before the local decision day'),
        uncertainty=dict(lifetime_draws=600,main_draws=1500,blocks=[5,10,21,42],representative_refits=23),
        exploratory='All frozen NIFTY outcomes have been research-exposed. Several tables study the dynamics of the same outcome paths.',
        hypotheses=[dict(zip(cols,row)) for row in design]))

if __name__=='__main__':
    register()

