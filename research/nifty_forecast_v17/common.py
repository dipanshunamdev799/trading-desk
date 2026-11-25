"""Paths and pre-registered experiments for the frozen V17 study."""
import gzip
import json
import os
from pathlib import Path
from research.nifty_forecast_v16.common import ROOT, V4, V5, V6, V8, V10, V11, V12, V13, V14, V15, sha, now, pd, np

V16=ROOT/'artifacts/nifty_forecast_v16/2026-11-25/run-001'
SRC=Path(__file__).parent
BASE=ROOT/'artifacts/nifty_forecast_v17'
OUT=Path(os.environ.get('NIFTY_V17_OUT',BASE/'2026-11-25/run-001')).resolve()
if not OUT.is_relative_to(BASE):
    raise ValueError('V17 results belong under its artifact directory')
FIRST='2025-01-01'
FREEZE='2026-11-17'
LAST='2026-12-31'
IST='Asia/Kolkata'
GAP_CLOCKS=('prior_close','us_complete','06:00','07:00','08:00','08:30','08:45','08:55')
SESSION_CLOCKS=('09:25','09:35','09:55','10:20','11:30','12:30','14:00','15:00')
PATH_COUNTS=(256,2048,8192)
SEED=171125
HIST=140
MIN=44
BOOT=1500
EXPECTED={5:265,21:217}
HORIZONS=(5,21)
Q=(np.arange(128)+.5)/128

SEEDS=('2025-01-02','2025-01-08','2025-01-15','2025-01-22','2025-01-29')
SLEEVES={
 'bank':(6,('HDFCBANK','ICICIBANK','SBIN','AXISBANK','KOTAKBANK','INDUSINDBK','FEDERALBNK','IDFCFIRSTB')),
 'finance':(4,('BAJFINANCE','BAJAJFINSV','JIOFIN','SBICARD','SHRIRAMFIN','CHOLAFIN')),
 'it':(5,('INFY','TCS','HCLTECH','TECHM','WIPRO','PERSISTENT','COFORGE')),
 'energy':(5,('RELIANCE','ONGC','BPCL','IOC','GAIL','NTPC','POWERGRID')),
 'auto':(5,('MARUTI','M&M','BAJAJ-AUTO','EICHERMOT','TVSMOTOR','ASHOKLEY','HEROMOTOCO')),
 'defensive':(5,('ITC','HINDUNILVR','NESTLEIND','TATACONSUM','DABUR','BRITANNIA','GODREJCP')),
}
CONTRACT_HTTP='https://api.upstox.com/v2/expired-instruments/'
REPORTS=(
 'REPRODUCTION_AND_BASELINES','GIFT_OPENING_PRICE_INTELLIGENCE','OPENING_SURPRISE_AND_RESIDUAL_RETURNS',
 'STOCK_LEVEL_MARKET_INTELLIGENCE','INTRADAY_BREADTH_AND_PARTICIPATION','DOMESTIC_INFORMATION_NETWORKS',
 'VOLUME_LIQUIDITY_AND_ORDER_FLOW','CROSS_INSTRUMENT_PRICE_DISCOVERY','RESIDUAL_RETURN_FORECASTING',
 'MULTISCALE_PREDICTABILITY_MAP','WEEKLY_AND_MONTHLY_FORECASTING','VOLATILITY_AND_PATH_INTELLIGENCE',
 'NEW_INFORMATION_DISCOVERY','VALIDATION_AND_FALSIFICATION','CUMULATIVE_EVIDENCE_AND_RESEARCH_EFFICIENCY',
 'COMPLETE_MODEL_COMPARISON','FORWARD_RESEARCH_LEDGER','FINAL_RESEARCH_CONCLUSIONS','NEXT_EXPERIMENTS')

def read(name,root=OUT):
    p=root/name
    if p.suffix=='.gz':
        with gzip.open(p,'rt',encoding='utf-8') as f:
            return json.load(f)
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(name,df,index=False):
    p=OUT/name
    p.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(p,index=index)

def save(name,x):
    p=OUT/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,default=str,allow_nan=False),encoding='utf-8')

def stamp(day,clock):
    return pd.Timestamp(f'{day}T{clock}:00',tz=IST)

def matrix(name,root=OUT):
    return pd.read_csv(root/name,index_col=0,low_memory=False)

def register():
    if (OUT/'registration.json').exists():
        return
    save('registration.json',dict(registered_at=now(),scope=[FIRST,FREEZE],forward_end=LAST,
      budget=dict(stock_count=30,cash_seed_dates=SEEDS,clocks=SESSION_CLOCKS,gap_clocks=GAP_CLOCKS,
                  history=HIST,minimum_train=MIN,draws=BOOT,block_lengths=[5,10,21,42],atoms=128,
                  monte_carlo_atoms=PATH_COUNTS,mc_sample=32,seed=SEED),
      stock_selection={'sleeves':SLEEVES,'rule':'Rank within predeclared sleeve on mean exchange traded INR turnover over five January 2025 EQ files, determine eligible ISIN, freeze before April evaluation.'},
      hypotheses=[
       ['Offshore price discovery','Official opening gap',GAP_CLOCKS,'Dated GIFT bars','Raw prior-mark change and V16','CRPS,Brier','historically eligible quotes','expiry guard, stale mark, alternate anchor, delay, extreme exclusion'],
       ['Surprise conditional on the observed gap','15m,30m,60m,remaining,next,remaining five and 21','Every post-auction clock','08:55 OOS gap law and observable cash open','Gap, price and RV','CRPS,Brier','cash and offshore point-in-time match','lagged surprise, shuffled residual'],
       ['Stock breadth and liquidity','Residual price, range, realized risk, touches','Post-auction clocks','eligible stock and native OHLCV','Native price/sector, official EW and RV','CRPS,Brier,MAE,QLIKE','aligned stock panel with genuine volume','dominant exclusion, random subset, timestamp delay, exact clone'],
       ['Related instruments and networks','Later cash and sector movement, range','Aligned post-auction and prior sessions','observed ETF/F&O quotes, volume and sector innovations','recent cash/sector/VWAP/risk','MAE,CRPS','known matching mark time','stale, matched future windows, source-specific limits'],
       ['Original returns','Five and twenty-one sessions','Prior 17:00, next 08:55 and separate post-open','eligible stock state, GIFT and original V14 law','Strongest archived V14 direction and V15/V16 distribution','Brier,CRPS','identical reference/endpoints','sentinel, matured residuals, direct forecast and placebo'],
       ['Joint risk and Monte Carlo','Range, 25% vol expansion, first session, terminals and survival','Original and post-gap','ATM IV, GJR, stock and surprise','V13–V16 references','MAE,QLIKE,CRPS,time Brier','fixed common date/support','common seeds at 256/2048/8192 and data uncertainty']
      ],
      advancement='Use matched value over a strong simple parent across time cohorts. Retain failed and inconclusive tests. Follow-up only on meaningful diagnostics; historical outcomes are research-exposed.',
      maturity='Labels must resolve before the row fit, all stock and risk transforms learned from earlier dates, current target starts at first regular bar open at or after the decision.',
      exposure='This targeted V17 registration and paired uncertainty cannot account for cumulative V1–V17 selection.'))
if __name__=='__main__':
    register()
