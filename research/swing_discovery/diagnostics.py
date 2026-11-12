"""Search-aware statistical diagnostics; never a replacement for fresh evidence."""
from __future__ import annotations
from itertools import combinations
from statistics import NormalDist
import math
import numpy as np
import pandas as pd
from research.swing.validation import block_indices,search_max_t

def deflated_sharpe(returns,trial_sharpes,n_trials):
    """Bailey/Lopez de Prado2014 daily-unit DSR, with explicit IID limitation."""
    r=np.asarray(returns,float);r=r[np.isfinite(r)]
    if len(r)<3 or r.std(ddof=1)<1e-14:
        return {'dsr':None,'reason':'insufficient_variation','n_observations':len(r)}
    sd=r.std(ddof=1);sr=r.mean()/sd;z=r-r.mean();scale=np.sqrt(np.mean(z*z))
    skew=float(np.mean(z**3)/scale**3);kurt=float(np.mean(z**4)/scale**4)
    candidates=np.asarray(trial_sharpes,float);candidates=candidates[np.isfinite(candidates)]
    spread=float(candidates.std(ddof=1)) if len(candidates)>1 else 0.
    n=max(1,int(n_trials));gamma=.5772156649015329;normal=NormalDist()
    threshold=0. if n==1 else spread*((1-gamma)*normal.inv_cdf(1-1/n)+gamma*normal.inv_cdf(1-1/(n*math.e)))
    variance=1-skew*sr+(kurt-1)*sr*sr/4
    probability=normal.cdf((sr-threshold)*np.sqrt(len(r)-1)/np.sqrt(variance)) if variance>0 else None
    return {'dsr':probability,'daily_sharpe':float(sr),'expected_max_null_daily_sharpe':float(threshold),
      'n_trials_assumed':n,'n_observations':len(r),'skewness':skew,'kurtosis':kurt,
      'assumptions':'IID nonnormal-return Sharpe approximation; full attempted trial count treated as independent conservative scenario. Serial dependence and historical reuse are not removed; common-calendar bootstrap is reported separately.'}

def pbo_cscv(development_returns,blocks=6):
    """Development-only CSCV/PBO; symmetric folds are not chronological OOS."""
    frame=pd.DataFrame(development_returns).fillna(0)
    if blocks%2 or len(frame)<blocks*5 or frame.shape[1]<2:
        return {'pbo':None,'reason':'insufficient_calendar_or_rules'}
    original_count=frame.shape[1]
    # Repeated MACD/PPO or flat outcomes are not independent ranking trials.
    keep=[];seen=set()
    for c in frame:
        signature=np.round(frame[c].to_numpy(float),12).tobytes()
        if signature not in seen:seen.add(signature);keep.append(c)
    frame=frame[keep]
    if frame.shape[1]<2:
        return {'pbo':None,'reason':'identical_development_outcomes','original_rules':original_count,'distinct_rules':len(keep)}
    x=frame.to_numpy(float);parts=np.array_split(np.arange(len(x)),blocks);rows=[]
    def sharpes(indices):
        v=x[indices];sd=v.std(axis=0,ddof=1)
        return np.divide(v.mean(axis=0),sd,out=np.zeros(v.shape[1]),where=sd>1e-14)
    for chosen in combinations(range(blocks),blocks//2):
        tr=np.concatenate([parts[i] for i in chosen]);te=np.concatenate([parts[i] for i in range(blocks) if i not in chosen])
        ins=sharpes(tr);outs=sharpes(te);winner=int(np.argmax(ins))
        # Mid-ranks for tied test Sharpes prevent arbitrary column-order bias.
        value=outs[winner];rank=(np.sum(outs<value)+.5*np.sum(outs==value))/(len(outs))
        rank=float(np.clip(rank,1/(2*len(outs)),1-1/(2*len(outs))))
        rows.append({'train_blocks':list(chosen),'winner':str(frame.columns[winner]),'in_sample_daily_sharpe':float(ins[winner]),
          'test_daily_sharpe':float(value),'test_relative_rank':rank,'logit':float(np.log(rank/(1-rank)))})
    return {'pbo':float(np.mean([r['logit']<=0 for r in rows])),'blocks':blocks,'symmetric_splits':len(rows),
      'original_rules':original_count,'distinct_rules':len(keep),
      'folds':rows,'limitation':'Only development returns; nonchronological diagnostic of search instability, not a deployable walk-forward policy or evidence from the reserved final period.'}

def portfolio_metrics(equity,trades_count=0):
    nav=pd.Series(equity,dtype=float);initial=1_000_000.;r=nav/nav.shift().fillna(initial)-1
    peak=np.maximum.accumulate(np.r_[initial,nav.to_numpy()])[1:];dd=float(np.max(1-nav.to_numpy()/peak))
    total=float(nav.iloc[-1]/initial-1);days=max(1,(nav.index[-1]-nav.index[0]).days+1)
    cagr=(1+total)**(365.25/days)-1 if 1+total>0 else -1.
    sd=r.std(ddof=1);down=np.sqrt(np.mean(np.minimum(r.to_numpy(),0)**2))
    return {'total_return_pct':total*100,'cagr_pct':cagr*100,'max_drawdown_pct':dd*100,
      'sharpe':float(r.mean()/sd*np.sqrt(252)) if sd>0 else None,
      'sortino':float(r.mean()/down*np.sqrt(252)) if down>0 else None,
      'calmar':cagr/dd if dd>0 else None,'n_trades':int(trades_count)}

def pooled_expectancy_ci(trades,dates,draws=3000):
    from research.swing.validation import trade_uncertainty
    return trade_uncertainty(trades,dates,draws=draws)

def summarize_run(result):
    stock=result['stock_metrics'];n=int(stock.n_trades.sum());wins=int(stock.winning_trades.sum());loses=int(stock.losing_trades.sum())
    out=portfolio_metrics(result['equity'],n)
    out.update(stock_count=len(stock),positive_stock_pct=float(stock.total_return_pct.gt(0).mean()*100),
      median_stock_return_pct=float(stock.total_return_pct.median()),mean_stock_return_pct=float(stock.total_return_pct.mean()),
      worst_stock_drawdown_pct=float(stock.max_drawdown_pct.max()),
      expectancy_r=float(stock.sum_r.sum()/n) if n else None,win_rate_pct=100*wins/n if n else None,
      profit_factor=float(stock.winning_pnl.sum()/stock.losing_pnl.sum()) if stock.losing_pnl.sum()>0 else None,
      avg_win=float(stock.winning_pnl.sum()/wins) if wins else None,
      avg_loss=-float(stock.losing_pnl.sum()/loses) if loses else None,
      exposure_pct=float(stock.exposure_pct.mean()),fees=float(stock.fees.sum()),
      avg_hold_hours=float((stock.avg_hold_hours.fillna(0)*stock.n_trades).sum()/n) if n else None)
    return out

def development_score(summary,min_trades=100):
    """Hard sample/drawdown veto before a modest, interpretable ranking score."""
    if summary.get('n_trades',0)<min_trades or summary.get('worst_stock_drawdown_pct',100)>25:
        return -1e9
    # No metric can offset a veto. Negative candidates remain negative diagnostics.
    sr=summary.get('sharpe') or 0;exp=summary.get('expectancy_r') or 0
    return float(.4*np.clip(sr,-3,3)+.3*np.clip(exp,-1,1)+.2*(summary.get('positive_stock_pct',0)/100-.5)
      +.1*np.clip(summary.get('median_stock_return_pct',0)/5,-1,1))
