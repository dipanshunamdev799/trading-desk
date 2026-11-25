"""Frozen scope, reproducible registration and artifact helpers for NIFTY V21."""
from pathlib import Path
import hashlib
import json
import os

import numpy as np
import pandas as pd

from research.nifty_forecast_v20 import common as v20

ROOT, FIRST, FREEZE, LAST, IST = v20.ROOT, v20.FIRST, v20.FREEZE, v20.LAST, v20.IST
V11, V14, V16, V17, V18, V19, V20 = (v20.V11, v20.V14, v20.V16, v20.V17, v20.V18, v20.V19, v20.OUT)
SRC = Path(__file__).parent
AREA = ROOT / 'artifacts/nifty_forecast_v21'
OUT = Path(os.environ.get('NIFTY_V21_OUT', AREA / '2026-11-25/run-001')).resolve()
assert OUT.is_relative_to(AREA)
BRIEF = Path('C:/Users/ME/.codex/attachments/2d331772-a59b-4b17-a948-69391a189cf0/Pasted text.txt')
HORIZONS = (5, 21)
EXPECTED = {5: (173, 92, 53), 21: (141, 76, 11)}
SEED = 211125
SEED_END = '2025-01-31'
SECTORS = dict(bank='niftybank', finance='niftyfinancialservices', it='niftyit', auto='niftyauto',
               energy='niftyenergy', consumer='niftyfmcg', health='niftypharma', materials='niftymetal')
REPORTS = (
    'REPRODUCTION_AND_PRIOR_TRANSFER_FORENSICS','HISTORICAL_EQUITY_UNIVERSE','INDEX_RETURN_RECONSTRUCTION',
    'MARKET_SECTOR_AND_STOCK_FACTOR_DECOMPOSITION','CROSS_SECTIONAL_RETURN_FORECASTING',
    'SAMPLE_EFFICIENT_CROSS_SECTIONAL_LEARNING','SECTOR_CONTRIBUTION_FORECASTING','JOINT_EQUITY_RETURN_DISTRIBUTIONS',
    'TOP_DOWN_VERSUS_BOTTOM_UP','CONCENTRATION_AND_DIVERSIFICATION','BOTTOM_UP_RISK_FORECASTING',
    'INFORMATION_SOURCE_SPECIALIZATION','SAMPLE_EFFICIENCY_AND_POWER','VALIDATION_AND_FALSIFICATION',
    'HYPOTHESIS_REGISTRY','COMPLETE_MODEL_COMPARISON','FORWARD_RESEARCH_LEDGER','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS',
)


def now():
    return pd.Timestamp.now(tz=IST).isoformat()


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(name, data):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, default=str, allow_nan=False), encoding='utf-8')


def read(name, root=OUT):
    return json.loads((root / name).read_text(encoding='utf-8-sig'))


def csv(name, root=OUT, **kwargs):
    return pd.read_csv(root / name, low_memory=False, **kwargs)


def write(name, data):
    data.to_csv(OUT / name, index=False)


def cash():
    x = csv('official-index-closes.csv', V11).rename(columns={'Unnamed: 0': 'day'}).set_index('day').loc[FIRST:FREEZE]
    assert len(x) == 466 and x.nifty50.notna().all() and x.index.is_unique and x.index.is_monotonic_increasing
    return x


def register():
    if (OUT / 'registration.json').exists():
        return
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'MISSION.md').write_bytes(BRIEF.read_bytes())
    hypotheses = [
        ('Dated archive reconstruction','Official monthly weights may track the price index after drift','Official monthly membership/weight files and exchange cash','Daily and 5/21 tracking RMSE','Equal and liquidity baskets','Corporate-action and no-drift sensitivity','50 verified NIFTY 50 weights and matching close','22 vintage months and two archive series','Prefer dated-weight investable observations and report tracking breaks'),
        ('Constrained sectors','A low-dimensional causal fit may reconstruct the index','Official sector index histories','Tracking RMSE at 1/5/21 sessions','Equal sector mixture','Earlier-only estimated simplex versus fixed','At least 60 dated daily returns','One stable simplex fit plus training-only factors','Compare extrapolation and scope by cohort'),
        ('Market decomposition','Most stock variation may lie in market and sector terms','Daily cash and dated memberships','Date-level explained variance','Market-only beta','Shuffled sector labels','60 prior paired observations per fit','One shrinking exposure design','Measure weighted cancellation of security residuals'),
        ('Equity pooling','Pooled observations can improve shared financial relationships','Eligible OHLC, turnover and structure','Stock CRPS, RMSE and date-rank IC','Historical/no-transfer and individual ridge','Randomized relative labels and shifted features','45 fully matured target days','Seven primary sharing models','Continue only if component performance or estimation improves'),
        ('Equity law calibration','Matured residuals may calibrate absolute and active return uncertainty','Equity labels and prior daily volatility','Absolute, relative, normalized, sign, magnitude and risk','Symmetric empirical history','Training-only chronological scale and grouping controls','Finite paired outcomes and at least 30 return observations','Compact Gaussian or empirical marginal laws','Test whether component gains survive aggregation'),
        ('Sector contributions','Sector or stock-derived predictions may add distinct index content','Dated index sectors and pooled stock returns','Sector/relative CRPS and aggregate contribution','Official sector historical law','Stock-to-sector vs direct sector vs constant drift','Mature sector labels and matched date support','One causal ridge by weighting lane','Require agreement with strong index parent'),
        ('Common market','Pooled absolute exposures may estimate the common target better','Stock absolute/relative models, official market state','Index Brier and CRPS','Matched NIFTY-only historical and archived V20','Shifted auxiliary features and common-only arm','Exact original 265/217 dates','One factor model, one NIFTY-only ridge, two nulls','Retain only evidence beyond common exposure'),
        ('Joint dependence','Paired historical factors and residuals restore diversification risk','Joint terminal stock or sector errors','Index CRPS, variance and interval coverage','Strong empirical parent and unconditional joint covariance','Independent, shrunk, Gaussian and heavy-tail controls','Matured return vectors with reported missing weights','128/256/1024 scenarios and several covariance families','Prioritize calibration over visual complexity'),
        ('Bottom-up versus direct','Aggregation may improve forecasts when component effects survive','Weekly and monthly stock/sector forecasts','Index Brier, log loss and CRPS','V20 metric leaders at 09:10 and archived 08:55','Equal complexity direct and historical aggregation','Exact target date and complete law','Fixed top-down, sector, stock, factor and mixture arms','Insist on matched performance and historical uncertainty'),
        ('Index residual','Pooled summaries may forecast errors of a strong parent','Earlier errors from exact V20 distributions','Index Brier and CRPS','Unchanged direct parent','Bias, scale, asymmetry and fixed mixture','At least 45 matured parent forecasts','One chronological capped ridge per mechanism','Compare location and scale separately'),
        ('Concentration','Focus of leadership may change forecast usefulness','Dated weights, synchronized stock moves and breadth','Index or volatility error by causal regime','Breadth, rotation, IV','Random subsets and removal of heavyweight securities','Transparent matched count and earlier thresholds','One regime map with fixed thresholds','Require robust group effects before gating'),
        ('Portfolio risk','Covariance and downside risk may add to IV/GJR','Equity returns, covariance and official IV/GJR','Realized vol MAE and QLIKE','Raw ATM, V16 combined, monthly GJR','Diagonal covariance and parent-only','Official realized risk and exact source clock','Small covariance set and one shrink overlay','Test even when direction fails'),
        ('Source specialization','Corporate information may act locally, positioning through the common factor','Timestamped issuer events, surprises, delivery and aggregate positions','Equity and sector score, index residual and risk','Matched technical plus direct parent','Counts, observed reaction and delays','Published clocks before issue. No imputed stock participant positions','Limited family ablation','Require gain after matching eligible dates'),
        ('Sample efficiency','Shared estimation helps with idiosyncratic noise, but common noise limits it','Synthetic grouped factor processes and archived case losses','Test error, parameter RMSE and power','Direct date-only estimation','No shared beta, sector cancellation and spurious regime','Same train/test dates for all arms','300 simulations per controlled design','Distinguish rows, dates and disjoint index windows'),
        ('Forward eligibility','Research issue clocks and live inputs can be rehearsed exactly','Archived issue laws, market calendar and availability receipts','Completeness and maturity','Existing V4–V20 issues','No after-cutoff reissue','Exact historical implementation and time guard','One prospective ledger and readiness audit','Issue only verifiable references within calendar scope'),
    ]
    names = ('name','mechanism','inputs','target_metric','strong_reference','negative_control','minimum','budget','follow_up')
    save('registration.json', dict(registered_at=now(), history=[FIRST, FREEZE], forward_end=LAST,
         decision_clocks=['08:55 IST pre-auction','09:10 IST native anchor'], seed_policy=SEED_END,
         universe='January cash turnover cohort. Monthly exchange membership kept under a release guard.',
         historical_exposure='All frozen outcomes were research-exposed.', seed=SEED, horizons=HORIZONS,
         cohorts=EXPECTED, hypotheses=[dict(zip(names, x), cutoff='08:55 inputs, same-window 09:10 native comparisons where stated') for x in hypotheses]))


if __name__ == '__main__':
    register()
