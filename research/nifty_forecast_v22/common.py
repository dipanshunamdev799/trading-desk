"""Frozen scope and research registration for V22."""
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import json
import os

import numpy as np
import pandas as pd

from research.nifty_forecast_v21 import common as v21

ROOT, FIRST, FREEZE, LAST, IST = v21.ROOT, v21.FIRST, v21.FREEZE, v21.LAST, v21.IST
V14, V16, V17, V18, V19, V20, V21 = v21.V14, v21.V16, v21.V17, v21.V18, v21.V19, v21.V20, v21.OUT
V5, V10, V11 = v21.v20.V5, v21.v20.V10, v21.V11
V9 = ROOT/'artifacts/nifty_forecast_v9/2026-11-24/run-001'
SRC=Path(__file__).parent
AREA=ROOT/'artifacts/nifty_forecast_v22'
OUT=Path(os.environ.get('NIFTY_V22_OUT',AREA/'2026-11-26/run-001')).resolve()
assert OUT.is_relative_to(AREA)
BRIEF=Path('C:/Users/ME/.codex/attachments/47e29844-6be4-4581-adc2-537f4418c01f/Pasted text.txt')
HORIZONS=(1,3,5,10,21)
ORIGINAL=(5,21)
EXPECTED={5:(173,92,53),21:(141,76,11)}
SEED=221126
REPORTS=(
 'REPRODUCTION_AND_TRANSFER_FORENSICS','INTERNATIONAL_MARKET_DATABASE','INTERNATIONAL_FORECAST_TASKS',
 'GLOBAL_AND_COUNTRY_FACTOR_DECOMPOSITION','TRANSFERABLE_MARKET_RELATIONSHIPS','INTERNATIONAL_MARKET_ANALOGUES',
 'CROSS_MARKET_STATE_TRANSITIONS','INDIA_SPECIFIC_DOMAIN_ADAPTATION','INTERNATIONALLY_INFORMED_NIFTY_FORECASTS',
 'INTERNATIONAL_RISK_AND_TAIL_INTELLIGENCE','TRANSFER_VALIDATION_AND_FALSIFICATION','SAMPLE_EFFICIENCY_AND_TRANSFER_LIMITS',
 'HYPOTHESIS_REGISTRY','COMPLETE_MODEL_COMPARISON','FORWARD_RESEARCH_LEDGER','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS',
)


def now():
    return pd.Timestamp.now(tz=IST).isoformat()


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def save(name,obj):
    p=OUT/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,allow_nan=False,default=str),encoding='utf-8')


def read(name,root=OUT):
    return json.loads((root/name).read_text(encoding='utf-8-sig'))


def csv(name,root=OUT,**kw):
    return pd.read_csv(root/name,low_memory=False,**kw)


def write(name,z):
    z.to_csv(OUT/name,index=False)


def cash():
    return v21.cash()


def stamp(day,clock,zone=IST):
    return pd.Timestamp(f'{day}T{clock}',tz=zone)


def utc_int(xs):
    return pd.to_datetime(xs,format='mixed',utc=True).as_unit('ns').astype('int64').to_numpy() if isinstance(xs,pd.Index) else pd.to_datetime(xs,format='mixed',utc=True).dt.as_unit('ns').astype('int64').to_numpy()


def register():
    if (OUT/'registration.json').is_file():
        return
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'MISSION.md').write_bytes(BRIEF.read_bytes())
    h=[
        ('Comparable markets','One broad local price index per market can support harmonized tasks','Official India, verified vendor/FRED global','1, 3, 5, 10, 21 local sessions','Cash OHLC and calendar','Coverage and agreement','Reject total-return series from primary, audit duplicates','At least 360 close marks, explicit local clock','Fixed country inventory','Retain eligibility only if a valid tenor can be audited'),
        ('Global vs local risk','Date-balanced global exposures can remove duplicated market shocks','Leave-India-out global and regional equity states','Daily and original 5/21','Local cash return','Realized residual variance and predictive CRPS','Region exclusion and training-only PCA','At least 70 earlier paired dates','Economic factors and one PCA reference','Compare residual forecast beyond already visible GIFT'),
        ('Repeated predictive mechanisms','Direction and volatility laws may share slopes across markets','One broad index per country or market jurisdiction','All local horizons','Own-market ridge','Brier, CRPS, risk MAE','Country alignment permutation, shifted inputs','At least 45 matured past dates per target','Single ridge family plus measured country deviations','Require agreement beyond local and shift controls'),
        ('Country and region generalization','Country success may depend on exposure to its own region','Chronological global panel','All local horizons','Own-market ridge','Negative transfer and paired CRPS','Hold out entire country or region','Matured timestamps before the local issue','One walk-forward held-region design','Inspect dependence and failures by regime'),
        ('International analogue distributions','Comparable risk states may recur outside India','Broad markets and same-date domestic states','Original 5/21 and risk','Historical India, V21','NIFTY CRPS, interval and tail scores','Random windows, volatility conditioning, unconstrained neighbours','45 mature windows, usable volatility and date caps','Nearest, Mahalanobis, ridge-metric and path baselines','Advance only with diversity and a matched advantage'),
        ('Global episode diversification','Simultaneous crises should not dominate analogue weights','Observed weekly UTC episodes and region','Original 5/21','Unrestricted international ancestors','Kish effective count and forecasting loss','Uncapped versus fixed episode and regional weights','At least five represented episodes','Fixed cap and date weights','Preserve the multiplicity diagnostics'),
        ('Transferable transitions','Risk transitions may generalize better than directional ones','Local cash returns and prior ex-India state','1/3/5/10/21 risk, range and state transitions','Local persistence and conditioned frequency','Expansion/contraction Brier, realized MAE','Date-aligned random labels, market-state-only baseline','Earlier filtered states, no smoothed regimes','One shared conditional law and one partially pooled transition','Advance stable risk effects with calibrated comparisons'),
        ('India parameter prior','International coefficients may help at a fixed India training budget','Matched local dates; imported global coefficients','Original 5/21','V21, zero and historical priors','Brier and CRPS','Same India sample, ordinary ridge, random/shifted country targets','45 or 60/120 fully matured local rows','Two training budgets and one hierarchical ridge','Require a benefit beyond coefficient shrinkage'),
        ('Domestic complement','Indian corporate and positioning states can complement transferred information','V20 domestic snapshot and V21 constituent events, plus foreign factors','Original 5/21','V20/V21 native laws','Brier, CRPS and conditional calibration','Matched domestic-only regime fit','Certified dated input or parent fallback','One domestic overlay and one external addition','Check early/later stability and source clock'),
        ('Strong-parent residual','Chronological errors of V21 may be predictable beyond baseline','Exact native V21 law and pooled or analogue estimates','Original 5/21','Archived same-clock V20/V21','CRPS/Brier','Bias, ordinary regularization, phase-paired nulls','At least 45 previously frozen forecast errors','Location, scale, asymmetry, sign and fixed mixtures','Inspect score component and omit favorable weeks'),
        ('International risk laws','Transferred dispersion and risk tails may improve IV or GJR','Global normalized OHLC innovations and Indian IV/GJR','Original 5/21','Protected point/transition/range anchors','Risk MAE, QLIKE, range CRPS and tails','Pure local history and fixed risk scale','Coherent OHLC, separated risk/terminal point targets','Empirical paths and compact heavy-tail and EWMA shrinkage','Require matched risk and tail calibration'),
        ('Shared previous failure mechanisms','Duplicated global factors and complex pooling can cause misleading gains','V5, V9, V10, V18, V21','Historical replay','Archived controls','Exact reproduction and residual scores','Clock checks, synthetic negative transfer','Verified archives with fixed score definitions','One archive replay per prior transfer family','Document which mechanisms are newly tested'),
        ('Sample and power','More markets improve parameter estimates if relationships are stable','Synthetic shared and country-specific outcomes, real date clusters','Original 5/21 and all source markets','India-only and no-signal controls','Parameter RMSE, gain and effective size','Global shock, instability and India exclusion','Expose assumptions and original cohort counts','240 replications per declared design','Separate simulated gains from market evidence'),
        ('Prospective eligibility','A forward forecast requires native live inputs and a genuine timestamp','Official NSE, eligible Upstox, archived risk and directional laws','Original 5 and 21, opening and risk','V4–V21 archived issues','Legitimate maturity and source audit','Original issuance hash and exact date list','Actual cutoff, complete local calendar; no 2027 targets','One staged research panel and live guarded execution where feasible','Issue only feasible, reproducible laws'),
    ]
    keys=('name','mechanism','markets','horizon','strong_parent','metric','negative_control','eligibility','budget','follow_up')
    save('registration.json',dict(registered_at=now(),scope=[FIRST,FREEZE],forward_limit=LAST,seed=SEED,horizons=HORIZONS,
          historical_exposure='All historical periods remain research-exposed',cohorts=EXPECTED,
          hypotheses=[dict(zip(keys,r),cutoff='Own exchange pre-open, original India 08:55 or native 09:10 with guarded inputs') for r in h]))


if __name__=='__main__':
    register()
