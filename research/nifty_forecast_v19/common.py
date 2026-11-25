"""Scope, paths and registered hypotheses for the V19 positioning study."""
import gzip
import json
import os
from pathlib import Path

from research.nifty_forecast_v18.common import (
    ROOT,V4,V5,V10,V11,V12,V13,V14,V15,V16,V17,IST,FIRST,FREEZE,LAST,
    HORIZONS,EXPECTED,now,sha,np,pd,stamp,
)

V18=ROOT/'artifacts/nifty_forecast_v18/2026-11-25/run-001'
SRC=Path(__file__).parent
BASE=ROOT/'artifacts/nifty_forecast_v19'
OUT=Path(os.environ.get('NIFTY_V19_OUT',BASE/'2026-11-25/run-001')).resolve()
assert OUT.is_relative_to(BASE)
SEED=191125
CLOCKS=('previous_1700','preauction_0855')
POST=('09:25','10:20')
REPORTS=(
 'REPRODUCTION_AND_BASELINES','MARKET_POSITIONING_DATABASE','PARTICIPANT_POSITIONING_INTELLIGENCE',
 'DELIVERY_PARTICIPATION_RESEARCH','CROWDING_AND_UNWINDING_RESEARCH','POSITION_PRICE_DIVERGENCE',
 'LARGE_TRANSACTION_RESEARCH','AUTHENTIC_CAPITAL_FLOW_RESEARCH','AGGREGATE_POSITIONING_FACTORS',
 'FUNDAMENTAL_POSITIONING_INTERACTIONS','ORIGINAL_HORIZON_FORECASTING','POSITIONING_AND_RISK_INTELLIGENCE',
 'VALIDATION_AND_FALSIFICATION','HYPOTHESIS_REGISTRY_AND_RESEARCH_EFFICIENCY','COMPLETE_MODEL_COMPARISON',
 'FORWARD_RESEARCH_LEDGER','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS',
)

def read(name,root=OUT):
    p=root/name
    if p.suffix=='.gz':
        with gzip.open(p,'rt',encoding='utf-8') as f:
            return json.load(f)
    return json.loads(p.read_text(encoding='utf-8-sig'))

def csv(name,root=OUT,**kw):
    return pd.read_csv(root/name,low_memory=False,**kw)

def write(name,frame):
    p=OUT/name
    p.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(p,index=False)

def save(name,data):
    p=OUT/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,default=str,allow_nan=False),encoding='utf-8')

def register():
    if (OUT/'registration.json').is_file():
        return
    write('issuer-seed.csv',csv('issuer-seed.csv',V18))
    cols=['hypothesis','rationale','source','target','cutoff','parent','primary_metric','eligibility','negative_control','budget','follow_up']
    hypotheses=[
        ['Participant position levels','Position balance may describe a persistent state','NSE participant OI','Original 5 and 21 sessions','17:00 and 08:55','Archived V17 structural','Brier and CRPS','Authenticated next-session eligible reports','Drop dependent Client nets and separate instrument families','One shrinkage level','Positive matched gains across cohorts'],
        ['Position changes versus levels','Recent changes may convey more information than levels','Date-verified net balance and gross counts','Original 5 and 21 sessions and rotation','Same-clock','Price, breadth, and ordinary NIFTY futures OI','CRPS and paired squared error','Exact day and source coverage','One- and five-session delays, then blocked nulls','1, 5 and 21 observed-session changes','Matched benefit over levels and OI'],
        ['Position-price innovation','A new move in exposures may differ from its historical price-based conditional expectation','Causal ridge residual with basis, expiry and OHLC state','Original returns and magnitude','Same-clock','Ordinary positioning, then structural','CRPS and MAE','Earlier covariates and residual training only','Variance normalization alternative and shifted predictors','Maximum 120 history rows per fit','Stable incremental contribution over raw positions'],
        ['Crowding and contraction proxy','Cross-participant concentration may change dispersion or subsequent reduction in open interest','Count-based HHI, training-only ranks and known expiry','Volatility, reversal, future NIFTY futures OI reduction','Same-clock','Price momentum, IV and OI','Brier and QLIKE','Positive denominators and known expiry','Expiry and rollover exclusions, date episodes','One main crowding screen per instrument','Matched effect outside expiry and dominant episodes'],
        ['Delivery activity','Delivered share participation may differ from ordinary traded activity','Full NSE security-delivery reports and cash archive','Stock-relative and original NIFTY returns','Morning following eligible publication','Traded volume, turnover, and native state','CRPS, Brier and paired stock error','Point-in-time company identifiers and positive price','Alternative windows, ex-action screens, and random eligible subsets','25/60 prior observations and a fixed basket','Matched gains in more than one cohort'],
        ['Delivery breadth and rotation','Broad delivery changes may convey sector leadership','NSE delivery and dated native sector indexes','5- and 21-session sector excess and index returns','Same-clock','Price, traded breadth, turnover and official equal weight','MAE, Brier and CRPS','Company and membership proxy coverage disclosed','Sector weighting and top-name removal','Equal company, sector, liquidity and available cap proxy','Sector predictive gains beyond market state'],
        ['Large deals','Unusual disclosed transactions may precede different relative returns or risk','NSE historical bulk and block windows','Issuer relative returns, sector rotation and index risk','Next cash session with publication guard','Matched high-turnover controls','Paired excess return and CRPS','Authenticated dated archive window','Date shifts, exact duplicate and size exclusions','One primary matched event study and one alternative grouping','Event and parent comparison beyond matched turnover'],
        ['Institutional cash activity','Authentic cash trades or custodian-reported equity activity may carry separate information','Official dated source only','5- and 21-session original returns and risk','Conservative separate release clock','Price and derivatives positioning','Brier, CRPS and QLIKE','Documented units and vintage, no synthetic filling','Verify arithmetic and test chronological delay','One aggregate per authentic series','Estimable matched increments and coverage'],
        ['Fundamental and position interaction','Positioning may condition the future behavior after corporate developments','V18 published fundamentals and genuine positioning measurements','Original 5 and 21 sessions','Identical-cutoff','Structural, corporate, and each separate information block','Brier and CRPS','Same dates and as-of data','Alternative addition orders, block rotation and delayed inputs','Eight delivery-positioning-transaction subsets and two interaction models','Increment through both addition orders and comparable cohorts'],
        ['Native and decomposition residuals','A candidate should improve calibrated existing predictive laws','Exact V14/V18 weighted laws and V17 decomposition','Original endpoint distributions','Original native guard or matched rebuilt cutoff','Verified exact archived distributions','Brier and CRPS','Fully matured historical forecast errors','Neutral correction, empirical shape and episode omissions','No more than two adjustments per protected parent','Positive adjusted directional and distribution evidence'],
        ['Positioning-informed risk laws','Crowding and activity may add to IV beyond price history','Audited positioning, delivery and risk states','Point volatility, transitions, range and barrier risks','Prior 17:00, 08:55 and independent post-open risk','Archived IV, GJR, EGARCH, V16 and V17 laws','MAE, QLIKE, CRPS and Brier','Same reference price and actual outcome','Delay, expiry exclusions and comparison to IV-only','256 archived OHLC scenarios per origin','Improvement in coherent laws or clearly labeled standalone forecasts'],
    ]
    save('registration.json',dict(registered_at=now(),scope=[FIRST,FREEZE],forward_max=LAST,seed=SEED,
        hypotheses=[dict(zip(cols,row)) for row in hypotheses],
        academic_scope='Outcomes have been examined across V1–V18. Tests remain retrospective, including when intervals account for overlap and multiple V19 contrasts.',
        publication_guard='An archived EOD report is modeled as eligible by 08:15 IST on the next exchange session. Compare an additional one- and five-session delay. Genuine filing timestamps independently control cash or corporate observations.',
        budget=dict(bootstrap_draws=1500,block_lengths=[5,10,21,42],null_refits=23,
          intended_cohorts={5:{'early':173,'later':92,'combined':265,'disjoint':53},
                            21:{'early':141,'later':76,'combined':217,'disjoint':11}},
          fixed_delivery_issuers=240,source_days='Every eligible 2025–2026 archived session',
          endpoint_law_atoms=128,path_atoms=256),
        forward_candidates=['Original GIFT gap at its genuine pre-auction issue time','Original native weekly model and corporate overlay if their guard is reached during active research','Neutral monthly law anchored to a certified cash close','IV/GJR risk reference if same-cutoff current inputs exist','Positioning candidate only if justified, preregistered and frozen before its actual target interval']))

if __name__=='__main__':
    register()
