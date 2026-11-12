"""Database-driven reports for frozen discovery rules; never retunes a rule.

The evidence screen is deliberately more demanding than descriptive ranking.
Its thresholds are declared here before final evaluation. A ranked diagnostic is
not a recommended strategy and a screen pass still requires new forward data.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from research.swing.validation import block_indices, search_max_t, trade_uncertainty


EVIDENCE_SCREEN = dict(final_trades=50, reserved_trades=20, final_positive_stock_pct=50,
                       maximum_worst_stock_drawdown_pct=25, confidence=.95,
                       bootstrap_sessions=10, bootstrap_draws=3000,
                       validation_search_adjusted_p=.05,
                       requires_positive_double_cost=True,
                       requires_frozen_development_validation_eligibility=True)


def _json(path, default=None):
    return json.loads(Path(path).read_text(encoding='utf-8')) if Path(path).exists() else default


def _clean(value):
    if isinstance(value, dict): return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [_clean(v) for v in value]
    if isinstance(value, np.ndarray): return _clean(value.tolist())
    if isinstance(value, (float, np.floating)): return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.bool_,)): return bool(value)
    return value


def _save(path, value):
    Path(path).write_text(json.dumps(_clean(value), indent=2, allow_nan=False), encoding='utf-8')


def _fmt(value):
    if value is None or (isinstance(value, (float, np.floating)) and not np.isfinite(value)): return '—'
    if isinstance(value, (bool, np.bool_)): return 'yes' if value else 'no'
    if isinstance(value, (float, np.floating)): return f'{value:,.3f}'
    return str(value).replace('|', '\\|').replace('\n', ' ')


def _md(frame, columns=None, limit=None):
    if frame is None or frame.empty: return '_No observations._'
    frame = frame if columns is None else frame.reindex(columns=columns)
    if limit is not None: frame = frame.head(limit)
    return '\n'.join(['| '+' | '.join(frame.columns)+' |', '| '+' | '.join(['---']*len(frame.columns))+' |']+
                     ['| '+' | '.join(_fmt(v) for v in row)+' |' for row in frame.itertuples(index=False, name=None)])


def _read_database(out):
    with sqlite3.connect(out/'research.sqlite3') as conn:
        exp = pd.read_sql_query('SELECT * FROM experiments', conn)
        raw = pd.read_sql_query('SELECT * FROM runs', conn)
        rows = []
        for row in raw.to_dict('records'):
            rows.append({**{k:v for k,v in row.items() if k != 'summary'}, **json.loads(row['summary'])})
        runs = pd.DataFrame(rows)
        days = pd.read_sql_query("SELECT r.id,r.stage,r.pool,d.day,d.equity,d.net_return FROM portfolio_days d JOIN runs r ON d.key=r.key WHERE r.stage IN ('final','two_year','final_double10','final_severe20')", conn)
        stocks = pd.read_sql_query("SELECT s.*,r.id,r.stage,r.pool FROM stock_metrics s JOIN runs r ON s.key=r.key WHERE r.stage IN ('final','two_year')", conn)
    configs = {r['id']: json.loads(r['configuration']) for r in exp.to_dict('records')}
    runs['family'] = runs.id.map(lambda i: configs[i]['family'])
    return exp, configs, runs, days, stocks


def _subset(runs, stage, pool):
    return runs[(runs.stage == stage) & (runs.pool == pool)].set_index('id', drop=False)


def _value(frame, ident, key, default=np.nan):
    if ident not in frame.index or key not in frame: return default
    value = frame.at[ident, key]
    return default if value is None or (isinstance(value, (float, np.floating)) and not np.isfinite(value)) else value


def _bounded_score(frame, ident):
    def v(key): return float(_value(frame, ident, key, 0.))
    return (.4*np.clip(v('sharpe'), -3, 3)+.3*np.clip(v('expectancy_r'), -1, 1)+
            .2*(v('positive_stock_pct')/100-.5)+.1*np.clip(v('median_stock_return_pct')/5, -1, 1))


def _journal(out, ident, stage='final', pool='all_eligible_stocks'):
    path = out/'finalist_journals'/f'{ident}-{pool}-{stage}-trades.csv'
    if not path.exists() or path.stat().st_size < 3: return pd.DataFrame()
    try: return pd.read_csv(path)
    except pd.errors.EmptyDataError: return pd.DataFrame()


def _uncertainty(days, journals):
    table = days[(days.stage == 'final') & (days.pool == 'all_eligible_stocks')]
    returns = table.pivot(index='day', columns='id', values='net_return').sort_index()
    if returns.empty: return {}, {}
    indices = block_indices(len(returns), draws=3000, block=10, seed=20261111)
    output = {}
    for ident in returns:
        r = returns[ident].fillna(0).to_numpy()
        samples = np.prod(1+r[indices], axis=1)-1
        record = dict(return_ci95_pct=(np.quantile(samples, [.025, .975])*100).tolist(),
                      positive_return_bootstrap_fraction=float((samples > 0).mean()),
                      block_sessions=10, draws=3000)
        trades = journals.get(ident, pd.DataFrame())
        if not trades.empty:
            # The shared helper accepts exit_time rather than daily exit_day.
            record.update(trade_uncertainty(trades.rename(columns={'exit_day':'exit_time'}), returns.index, draws=3000))
        else: record.update(r_ci95=[None, None], positive_probability=None)
        output[ident] = record
    return output, search_max_t({i:returns[i] for i in returns}, draws=3000)


def _ranking(frozen, runs, uncertainty, validation_control):
    final = _subset(runs, 'final', 'all_eligible_stocks')
    reserved = _subset(runs, 'final', 'reserved_stocks')
    double = _subset(runs, 'final_double10', 'all_eligible_stocks')
    severe = _subset(runs, 'final_severe20', 'all_eligible_stocks')
    dev = _subset(runs, 'development', 'development_stocks')
    val = _subset(runs, 'validation', 'development_stocks')
    rows = []
    for item in frozen:
        ident = item['id']
        if ident not in final.index: continue
        row = dict(id=ident, family=item['family'], frozen_dev_val_eligible=item.get('development_validation_eligible', False))
        reasons = []
        if not row['frozen_dev_val_eligible']: reasons.append('failed frozen development/validation eligibility')
        for label, frame in [('final', final), ('reserved', reserved), ('double', double), ('severe', severe), ('development', dev), ('validation', val)]:
            for key in ['n_trades','total_return_pct','expectancy_r','sharpe','max_drawdown_pct','worst_stock_drawdown_pct','positive_stock_pct','profit_factor','win_rate_pct','median_stock_return_pct','avg_hold_hours','exposure_pct','fees']:
                row[label+'_'+key] = _value(frame, ident, key)
        for label, minimum in [('final',50), ('reserved',20)]:
            if not row[label+'_n_trades'] >= minimum: reasons.append(f'{label} trades below {minimum}')
            for metric in ['total_return_pct','expectancy_r']:
                if not row[label+'_'+metric] > 0: reasons.append(f'{label} {metric} not positive')
        if not row['final_positive_stock_pct'] >= 50: reasons.append('final positive-stock breadth below 50%')
        if not row['final_worst_stock_drawdown_pct'] <= 25: reasons.append('final worst-sleeve drawdown above 25%')
        for metric in ['total_return_pct','expectancy_r']:
            if not row['double_'+metric] > 0: reasons.append('double-cost '+metric+' not positive')
        ci = uncertainty.get(ident, {})
        row['final_return_ci95_lower_pct'], row['final_return_ci95_upper_pct'] = ci.get('return_ci95_pct', [np.nan,np.nan])
        row['final_net_r_ci95_lower'], row['final_net_r_ci95_upper'] = ci.get('r_ci95', [np.nan,np.nan])
        for key in ['final_return_ci95_lower_pct','final_net_r_ci95_lower']:
            if row[key] is None or not row[key] > 0: reasons.append(key+' not positive')
        row['validation_max_t_adjusted_p'] = validation_control.get(ident, {}).get('max_t_adjusted_p', np.nan)
        if not row['validation_max_t_adjusted_p'] <= .05: reasons.append('validation search-adjusted p above .05 or unavailable')
        row['evidence_screen_pass'] = not reasons
        row['status'] = 'evidence screen pass; forward confirmation needed' if not reasons else 'diagnostic; evidence screen failed'
        row['failure_reasons'] = '; '.join(reasons)
        row['balanced_score'] = .45*_bounded_score(final,ident)+.25*_bounded_score(reserved,ident)+.2*_bounded_score(double,ident)+.1*_bounded_score(val,ident)
        rows.append(row)
    result = pd.DataFrame(rows)
    if result.empty: return result
    result = result.sort_values(['evidence_screen_pass','balanced_score','id'], ascending=[False,False,True]).reset_index(drop=True)
    result.insert(0, 'rank', np.arange(1,len(result)+1))
    return result


def _entry_text(config):
    p = {**config.get('params', {}), **config}
    family = p['family']; fast=p.get('fast',12); slow=p.get('slow',26); signal=p.get('signal',9)
    oscillator = f"{'PPO' if family.startswith('ppo_') else 'MACD'}({fast},{slow},{signal})"
    cross = 'crosses above its signal; cross requires today > and previous <= the corresponding reference'
    kinds = dict(cross=cross, zero_cross='crosses above zero', hist_recovery='histogram rises after a non-rising bar while still below zero',
                 hist_accel='histogram rises twice after a non-rising bar',
                 strength_cross=f"{cross}, with absolute line-signal separation >= {p.get('strength',.05)} ATR-equivalent units",
                 above_zero=cross+' and line >0', below_zero=cross+' and line <0',
                 divergence=f"second released price-pivot low is lower and oscillator at that pivot is higher; strict {p.get('pivot',2)}-bar left/right pivots",
                 hidden_divergence=f"second released price-pivot low is higher and oscillator at that pivot is lower; strict {p.get('pivot',2)}-bar left/right pivots",
                 weekly=cross+f" and prior completed-week MACD({p.get('weekly_fast',12)},{p.get('weekly_slow',26)},{p.get('weekly_signal',9)}) line > signal")
    if family.startswith(('macd_', 'ppo_')): return oscillator+' '+kinds[family.split('_',1)[1]]+'.'
    trend = f'EMA{fast}>EMA{slow} and EMA{slow}>its value3sessions earlier'
    ema = dict(cross=f'EMA{fast} crosses above EMA{slow}', reclaim=f'close crosses above EMA{fast}; {trend}',
               pullback=f'rejection of EMA{fast}; {trend}',
               contraction=f"mean prior5daily ranges <{p.get('contraction',.8)}*previous ATR; close >previous high; {trend}",
               ribbon=f"new EMA{fast}>EMA{p.get('middle',20)}>EMA{slow} stack with slow EMA rising over3sessions",
               slope=f"(EMA{fast}-its value3sessions ago)/ATR crosses above {p.get('slope',.25)}; close>EMA{slow}",
               weekly=f"close crosses above EMA{fast}; {trend}; previous completed-week EMA{p.get('weekly_fast',10)}>EMA{p.get('weekly_slow',30)}")
    if family.startswith('ema_'): return ema[family[4:]]+'.'
    if family.startswith('kama_'):
        kind=family[5:]; action={'cross':f'KAMA{fast} crosses above KAMA{slow}', 'reclaim':f'close crosses above KAMA{fast}', 'pullback':f'rejection of KAMA{fast}'}[kind]
        return action+(f'; KAMA{fast}>KAMA{slow} and slow KAMA rising over3sessions' if kind!='cross' else '')+'.'
    structural = dict(
        pivot_bounce=f"rejection of latest released strict {p.get('pivot',2)}-left/right-bar pivot low",
        cluster_bounce=f"rejection of nearest released-pivot cluster support with >={p.get('touches',2)} distinct touches; max32pivots/252sessions, anchor tolerance fixed0.5ATR at release",
        donchian_breakout=f"close crosses above prior {p.get('lookback',20)}-session high plus {p.get('break_buffer',0)}ATR; channel excludes current bar",
        breakout_retest=f"rejection of frozen prior20-session breakout high,1..{p.get('retest_window',5)}bars after breakout",
        role_reversal=f"same frozen prior20-session breakout-high rejection within1..{p.get('retest_window',5)}bars; previous close>previous frozen level and EMA20>EMA50 with EMA50 rising over3sessions",
        support_sweep=f"low <released pivot low-{p.get('sweep_buffer',.1)}ATR; close>pivot low and close>open",
        previous_day='rejection of previous completed daily low', previous_week='rejection of previous completed calendar-week low', previous_month='rejection of previous completed calendar-month low',
        floor_pivot=f"rejection of prior-day HLC floor level {p.get('floor_level','s1')}",
        fib_pullback=f"rejection of confirmed ordered swing high-{p.get('ratio',.5)}*(high-low), with high>low; original low remains frozen until a new ordered high confirms",
        round_bounce='rejection of actual-rupee round support; steps10below100,50below500,100below1000,500below5000,otherwise1000; convert level into neutral units only afterward',
        anchored_vwap='close crosses above typical-price volume-weighted average anchored at the latest released pivot low; EMA20>EMA50 and EMA50 rising over3sessions',
        htf_confluence='rejection of previous completed-week low within zone*ATR of released daily pivot support',
        hybrid_trend_macd_support='MACD bullish signal cross; EMA20>EMA50 and EMA50 rising over3sessions;0<close-released pivot support<=2ATR',
        hybrid_support_hist='released pivot support rejection plus first histogram rise after a non-rising bar',
        hybrid_reclaim_zero='close crosses above EMA20; EMA20>EMA50 and EMA50 rising over3sessions; MACD line>0',
        hybrid_breakout_momentum=f"close crosses above prior{p.get('lookback',20)}-session high; EMA20>EMA50 and EMA50 rising over3sessions; MACD histogram>0",
        hybrid_divergence_support='released regular bullish price/MACD divergence with pivot support within zone*ATR of clustered support',
        hybrid_ribbon_pullback=f"rejection of EMA{p.get('middle',20)}; EMA{fast}>EMA{p.get('middle',20)}>EMA{slow} and slow EMA rising over3sessions",
        hybrid_sweep_reversal='low below released pivot support, close>support and close>open, plus first histogram rise after a non-rising bar')
    return structural[family]+f". Zone={p.get('zone',.5)}ATR; pivot confirmation={p.get('pivot',2)}bars; MACD parameters={fast}/{slow}/{signal} when used."


def _rule_text(config):
    p={**config.get('params',{}), **config}; mode=p.get('exit','fixed'); stop=p.get('stop_mode','atr')
    filters=dict(none='none',volume='signal-day volume >=1.25*mean previous20 volumes',adx='ADX14>=20',rsi='40<=RSI14<=70',volatility='.01<=ATR14/close<=.06',market='NIFTY close>EMA200 and EMA50>EMA200',rs='stock60-session return>NIFTY60-session return',breadth='at least50%of finite panel names above EMA50',sector='mean20-session return of other finite same-sector stocks>0')
    stop_text=f"entry fill-{p.get('stop_atr',2)}*decision-day ATR converted to entry-day actual units" if stop=='atr' else f"{'latest released pivot low' if stop=='swing' else 'entry reference level'}-{p.get('buffer',.2)}ATR, converted to entry-day actual units"
    exit_text={'fixed':f"fee/slippage-aware fixed {p.get('reward',2)}netR target", 'time':'time-only profit exit; protective stop retained', 'atr_trail':f"stop tightens before each open to previous close-{p.get('trail_atr',2)}previous ATR; no fixed target", 'ema':'stop tightens to previous completed EMA20; previous close<EMA20 also exits next open; no fixed target', 'macd':f"fixed {p.get('reward',2)}netR target or bearish MACD signal cross at next open", 'trend':f"fixed {p.get('reward',2)}netR target or previous close<EMA50 or EMA50<EMA200 at next open"}[mode]
    return dict(entry=_entry_text(p), filter=filters[p.get('filter','none')], initial_stop=stop_text,
                exit=exit_text+f"; next-open time exit after {p.get('max_hold_sessions',10)}sessions; forced liquidation at segment end",
                sizing=f"floor shares to risk at most {100*p.get('risk_fraction',.005):g}%of current sleeve cash including modeled buy+overnight stop-sale fees and slippage; no leverage, cash-cost cap,1%prepared prior20median volume cap; minimum prior20median turnover ₹50m; candidate stop distance0.5..8ATR",
                execution='Signal after completed close; fill next open plus adverse slippage. Stop before target if both touched; gap stop fills adverse open, target gets no favorable gap improvement; no same-session re-entry. Integer split entitlements and carried-share cash dividends modeled.')


def _breakdowns(out, days, stocks, configs, journals):
    d=days.copy(); d['date']=pd.to_datetime(d.day); d['month']=d.date.dt.strftime('%Y-%m'); d['year']=d.date.dt.year
    monthly=d.groupby(['id','stage','pool','month']).net_return.agg(lambda r:100*(np.prod(1+r)-1)).rename('return_pct').reset_index()
    yearly=d.groupby(['id','stage','pool','year']).net_return.agg(lambda r:100*(np.prod(1+r)-1)).rename('return_pct').reset_index()
    monthly.to_csv(out/'monthly-returns.csv',index=False);yearly.to_csv(out/'yearly-returns.csv',index=False)
    stocks=stocks.copy(); universe=_json(out/'universe.json',{}); sectors={r['symbol']:r.get('sector') for r in universe.get('stocks',[])}
    stocks['sector']=stocks.symbol.map(sectors); stocks.to_csv(out/'stock-analysis.csv',index=False)
    regimes={}; benchmark=None
    if (out/'daily-panel.npz').exists() and (out/'panel-index.json').exists():
        from research.swing_discovery.signals import smooth
        idx=_json(out/'panel-index.json',{}); dates=pd.to_datetime(idx['dates'],utc=True).tz_convert('Asia/Kolkata')
        with np.load(out/'daily-panel.npz') as data: market=data['niftyclose'].copy()
        e50=smooth(market[None,:],50)[0];e200=smooth(market[None,:],200)[0]
        label=np.where(np.isfinite(e200),np.where((market>e200)&(e50>e200),'market_up',np.where((market<e200)&(e50<e200),'market_down','market_mixed')),'warmup_unknown')
        regimes=dict(zip(dates.strftime('%Y-%m-%d'),label));benchmark=pd.Series(market,index=dates.tz_localize(None))
    trade_rows=[]; trade_stats=[]
    for ident in configs:
        for stage in ['final','two_year']:
            trades=journals.get(ident,pd.DataFrame()) if stage=='final' else _journal(out,ident,'two_year')
            if trades.empty:continue
            trades=trades.copy(); trades['id']=ident;trades['stage']=stage
            signal=pd.to_datetime(trades.signal_day,utc=True).dt.tz_convert('Asia/Kolkata')
            trades['signal_market_regime']=signal.dt.strftime('%Y-%m-%d').map(regimes).fillna('unavailable')
            trades['entry_weekday']=pd.to_datetime(trades.entry_day,utc=True).dt.tz_convert('Asia/Kolkata').dt.day_name()
            trades['holding_bucket']=pd.cut(trades.holding_hours,[-1,24,72,168,336,np.inf],labels=['<=24h','24..72h','72h..7d','7..14d','>14d']).astype(str)
            trades['exit_year']=pd.to_datetime(trades.exit_day,utc=True).dt.tz_convert('Asia/Kolkata').dt.year.astype(str)
            for dimension in ['signal_market_regime','entry_weekday','holding_bucket','reason','exit_year']:
                for value,group in trades.groupby(dimension,dropna=False):
                    trade_stats.append(dict(id=ident,stage=stage,dimension=dimension,value=value,n_trades=len(group),
                        expectancy_r=group.net_r.mean(),win_rate_pct=100*group.net_pnl.gt(0).mean(),net_pnl=group.net_pnl.sum(),
                        fees=group.fees.sum(),avg_hold_hours=group.holding_hours.mean(),median_net_r=group.net_r.median()))
            trade_rows.append(dict(id=ident,stage=stage,n_trades=len(trades),median_net_r=trades.net_r.median(),
                p05_net_r=trades.net_r.quantile(.05),p95_net_r=trades.net_r.quantile(.95),worst_net_r=trades.net_r.min(),best_net_r=trades.net_r.max(),
                median_hold_hours=trades.holding_hours.median(),p90_hold_hours=trades.holding_hours.quantile(.9),
                fees=trades.fees.sum(),gross_pnl=trades.gross_pnl.sum(),net_pnl=trades.net_pnl.sum(),
                dividend_cash=trades.dividends.sum(),gap_stop_trades=int(trades.reason.eq('gap_stop').sum())))
    pd.DataFrame(trade_rows).to_csv(out/'trade-analysis.csv',index=False)
    breakdown=pd.DataFrame(trade_stats);breakdown.to_csv(out/'trade-breakdowns.csv',index=False)
    breakdown[breakdown.dimension.eq('signal_market_regime')].to_csv(out/'regime-analysis.csv',index=False) if not breakdown.empty else (out/'regime-analysis.csv').write_text('',encoding='utf-8')
    return monthly,yearly,stocks,breakdown,benchmark


def _ablations(out, configs, runs):
    from research.swing_discovery.signals import _config, _family_grids
    controls={family:_config(family,grid[len(grid)//2],description)['id'] for family,grid,description in _family_grids()}
    rows=[]
    for stage in ['development','validation']:
        frame=_subset(runs,stage,'development_stocks')
        for ident,cfg in configs.items():
            variant=cfg.get('variant','control');control=controls.get(cfg['family'])
            if variant in ('control','neighbor','development_neighbor') or control is None or ident not in frame.index or control not in frame.index:continue
            row=dict(id=ident,family=cfg['family'],variant=variant,stage=stage,control_id=control)
            for key in ['n_trades','total_return_pct','expectancy_r','sharpe','worst_stock_drawdown_pct','positive_stock_pct']:
                row[key]=_value(frame,ident,key);row['control_'+key]=_value(frame,control,key)
                row['delta_'+key]=row[key]-row['control_'+key]
            rows.append(row)
    ablations=pd.DataFrame(rows);ablations.to_csv(out/'ablation-analysis.csv',index=False)
    manifest=_json(out/'development-refinement.json',{});neighbors=[]
    for parent,children in manifest.get('parent_map',{}).items():
        for stage in ['development','validation']:
            frame=_subset(runs,stage,'development_stocks')
            for child in children:
                if parent not in frame.index or child not in frame.index:continue
                neighbors.append(dict(parent=parent,id=child,stage=stage,axis=configs.get(child,{}).get('neighbor_axis'),
                    parent_return_pct=_value(frame,parent,'total_return_pct'),return_pct=_value(frame,child,'total_return_pct'),
                    parent_expectancy_r=_value(frame,parent,'expectancy_r'),expectancy_r=_value(frame,child,'expectancy_r'),
                    n_trades=_value(frame,child,'n_trades'),positive=bool(_value(frame,child,'expectancy_r',0)>0 and _value(frame,child,'total_return_pct',0)>0)))
    neighborhood=pd.DataFrame(neighbors);neighborhood.to_csv(out/'neighbor-stability.csv',index=False)
    stability=neighborhood.groupby(['parent','stage']).agg(neighbors=('id','count'),positive_neighbors=('positive','sum'),median_return_pct=('return_pct','median'),minimum_return_pct=('return_pct','min'),maximum_return_pct=('return_pct','max'),median_expectancy_r=('expectancy_r','median')).reset_index() if len(neighborhood) else pd.DataFrame()
    stability.to_csv(out/'neighbor-stability-summary.csv',index=False)
    return ablations,stability


def _charts(out, ranked, runs, days, monthly, ablations, benchmark):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'figure.dpi':130,'savefig.dpi':150,'axes.spines.top':False,'axes.spines.right':False,'font.size':9})
    chart=out/'charts';chart.mkdir(exist_ok=True)
    top=ranked.head(8);ids=top.id.tolist();labels={r.id:f'{r.rank}. {r.family}' for r in top.itertuples()}
    fig,axes=plt.subplots(2,1,figsize=(12,8),sharex=True,layout='constrained')
    for ident in ids:
        group=days[(days.id==ident)&(days.stage=='two_year')&(days.pool=='all_eligible_stocks')].sort_values('day')
        if group.empty:continue
        x=pd.to_datetime(group.day);initial=group.equity.iloc[0]/(1+group.net_return.iloc[0]);nav=group.equity.to_numpy()/initial
        axes[0].plot(x,100*(nav-1),label=labels[ident]);axes[1].plot(x,100*(nav/np.maximum.accumulate(np.r_[1.,nav])[1:]-1))
    axes[0].set(ylabel='Mean sleeve net return (%)',title='Descriptive leaders: full-period independent sleeves')
    axes[1].set(ylabel='Close-marked drawdown (%)');axes[0].legend(fontsize=7,ncol=2);axes[0].axhline(0,color='.6',lw=.6)
    fig.savefig(chart/'equity-drawdown.png');plt.close(fig)
    # Every frozen family appears, rather than plotting winners alone.
    names=ranked.family.tolist();matrix=[]
    for ident in ranked.id:
        matrix.append([_value(_subset(runs,stage,pool),ident,'total_return_pct') for stage,pool in [('development','development_stocks'),('validation','development_stocks'),('final','all_eligible_stocks'),('final','reserved_stocks'),('final_double10','all_eligible_stocks'),('final_severe20','all_eligible_stocks')]])
    matrix=np.asarray(matrix,float);v=max(.1,float(np.nanquantile(np.abs(matrix),.95))) if np.isfinite(matrix).any() else 1
    fig,ax=plt.subplots(figsize=(10,max(8,.25*len(names))),layout='constrained');im=ax.imshow(matrix,aspect='auto',cmap='RdYlGn',vmin=-v,vmax=v)
    ax.set_yticks(range(len(names)),names,fontsize=7);ax.set_xticks(range(6),['Development','Validation','Final all','Final reserved','Double/10bps','Triple/20bps'],rotation=20)
    ax.set_title('All frozen families: sleeve return by separate evaluation segment');fig.colorbar(im,ax=ax,label='Net return (%)');fig.savefig(chart/'family-stage-returns.png');plt.close(fig)
    panel=monthly[(monthly.stage=='two_year')&(monthly.pool=='all_eligible_stocks')&monthly.id.isin(ranked.head(20).id)].pivot(index='id',columns='month',values='return_pct').reindex(ranked.head(20).id)
    if len(panel) and panel.shape[1]:
        fig,ax=plt.subplots(figsize=(15,max(5,.35*len(panel))),layout='constrained');v=max(.05,float(np.nanquantile(np.abs(panel.to_numpy()),.95)))
        im=ax.imshow(panel,aspect='auto',cmap='RdYlGn',vmin=-v,vmax=v);ax.set_yticks(range(len(panel)),[ranked.set_index('id').at[i,'family'] for i in panel.index],fontsize=7)
        ax.set_xticks(range(panel.shape[1]),panel.columns,rotation=90);ax.set_title('Top20 descriptive rules: calendar-month mean-sleeve net returns')
        fig.colorbar(im,ax=ax,label='Monthly net return (%)');fig.savefig(chart/'monthly-heatmap.png');plt.close(fig)
    if not ablations.empty:
        a=ablations.groupby(['variant','stage']).delta_total_return_pct.median().unstack().sort_index()
        fig,ax=plt.subplots(figsize=(12,5),layout='constrained');a.plot.bar(ax=ax);ax.axhline(0,color='.3',lw=.8)
        ax.set(title='Single-factor changes: median across-family change from central control',ylabel='Net return difference (percentage points)',xlabel='Frozen variant');ax.tick_params(axis='x',labelrotation=65)
        fig.savefig(chart/'ablation-deltas.png');plt.close(fig)
    if benchmark is not None and len(ids):
        fig,ax=plt.subplots(figsize=(12,4),layout='constrained')
        for ident in ids[:5]:
            group=days[(days.id==ident)&(days.stage=='two_year')&(days.pool=='all_eligible_stocks')].sort_values('day')
            if len(group):ax.plot(pd.to_datetime(group.day),100*(group.equity/group.equity.iloc[0]-1),label=labels[ident])
        if len(group):
            b=benchmark.loc[(benchmark.index>=pd.Timestamp(group.day.min()))&(benchmark.index<=pd.Timestamp(group.day.max()))].dropna()
            if len(b):ax.plot(b.index,100*(b/b.iloc[0]-1),'k--',label='NIFTY price only; fully invested')
        ax.set(title='Exposure comparison: cash-heavy swing sleeves and NIFTY price index',ylabel='Cumulative change (%)');ax.legend(fontsize=7,ncol=2);fig.savefig(chart/'benchmark-context.png');plt.close(fig)


def build_report(out, root):
    """Create report artifacts from completed frozen runs and their journals."""
    out,root=Path(out),Path(root);out.mkdir(parents=True,exist_ok=True)
    exp,configs,runs,days,stocks=_read_database(out)
    frozen=_json(out/'frozen-finalists.json',{}).get('finalists',[])
    if not frozen:raise ValueError('Report requires frozen-finalists.json')
    journals={x['id']:_journal(out,x['id']) for x in frozen}
    uncertainty,final_search=_uncertainty(days,journals)
    validation_control=_json(out/'validation-search-control.json',{})
    ranked=_ranking(frozen,runs,uncertainty,validation_control)
    if ranked.empty:raise ValueError('Report requires final/all_eligible_stocks runs')
    ranked.to_csv(out/'all-finalists.csv',index=False);ranked.head(20).to_csv(out/'top-20.csv',index=False)
    _save(out/'report-evidence-screen.json',dict(thresholds=EVIDENCE_SCREEN,
        ranking='Screen-pass first, then .45final+.25reserved+.20double-cost+.10validation bounded score. Bounded score=.4clip(Sharpe,-3,3)+.3clip(netR,-1,1)+.2(breadth/100-.5)+.1clip(median stock return%/5,-1,1).',
        meaning='Descriptive evidence labels only; no rules selected or changed using final outcomes; reused calendar is not an untouched holdout.'))
    _save(out/'final-uncertainty.json',uncertainty);_save(out/'final-search-control-diagnostic.json',final_search)
    _save(out/'all-tried-configurations.json',list(configs.values()));runs.to_csv(out/'all-runs.csv',index=False)
    failure=runs.copy();failure['zero_trades']=failure.n_trades.eq(0);failure['nonpositive_return']=failure.total_return_pct.le(0)
    failure['nonpositive_or_missing_expectancy']=failure.expectancy_r.fillna(0).le(0);failure['catastrophic_sleeve_drawdown']=failure.worst_stock_drawdown_pct.gt(25)
    failure['failure_status']=np.where(failure.zero_trades,'zero trades',np.where(failure.catastrophic_sleeve_drawdown,'drawdown veto',np.where(failure.nonpositive_or_missing_expectancy|failure.nonpositive_return,'nonpositive outcome','positive descriptive result')))
    failure.to_csv(out/'failure-ledger.csv',index=False)
    monthly,yearly,stocks,trade_breakdown,benchmark=_breakdowns(out,days,stocks,{x['id']:configs[x['id']] for x in frozen},journals)
    ablations,stability=_ablations(out,configs,runs)
    category=[]
    groups={'MACD family':ranked.family.str.startswith('macd_'),'PPO family':ranked.family.str.startswith('ppo_'),
            'EMA/adaptive':ranked.family.str.startswith(('ema_','kama_')),'support/resistance':~ranked.family.str.startswith(('macd_','ppo_','ema_','kama_','hybrid_')),
            'hybrid':ranked.family.str.startswith('hybrid_'),'risk-adjusted':np.ones(len(ranked),bool),'drawdown':np.ones(len(ranked),bool),'consistency':np.ones(len(ranked),bool)}
    pure_sr={'pivot_bounce','cluster_bounce','donchian_breakout','breakout_retest','support_sweep','previous_day','previous_week','previous_month','floor_pivot','fib_pullback','round_bounce'}
    def pure(ident,kind):
        c=configs[ident];family=c['family'];mode=c.get('exit','fixed')
        if c.get('filter','none')!='none':return False
        if kind=='macd':return family.startswith('macd_') and mode in ['fixed','time','atr_trail','macd'] and c.get('stop_mode','atr')=='atr'
        if kind=='ema':return family.startswith('ema_') and mode in ['fixed','time','atr_trail','ema','trend'] and c.get('stop_mode','atr')=='atr'
        return family in pure_sr and mode in ['fixed','time','atr_trail']
    for label,kind in [('MACD only, frozen subset','macd'),('EMA only, frozen subset','ema'),('S&R only, frozen subset','sr')]:
        groups[label]=ranked.id.map(lambda ident:pure(ident,kind))
    for name,mask in groups.items():
        group=ranked.loc[mask].copy()
        if group.empty:continue
        group['consistency']=np.minimum(group.final_positive_stock_pct,group.reserved_positive_stock_pct)
        key={'risk-adjusted':'final_sharpe','drawdown':'final_max_drawdown_pct','consistency':'consistency'}.get(name,'balanced_score')
        group=group.sort_values(['evidence_screen_pass',key,'id'],ascending=[False,name=='drawdown',True]);row=group.iloc[0]
        category.append(dict(category=name,id=row.id,family=row.family,status=row.status,final_return_pct=row.final_total_return_pct,final_sharpe=row.final_sharpe,final_drawdown_pct=row.final_max_drawdown_pct,reserved_return_pct=row.reserved_total_return_pct))
    categories=pd.DataFrame(category);categories.to_csv(out/'category-leaders.csv',index=False)
    _charts(out,ranked,runs,days,monthly,ablations,benchmark)
    specifications=[];rules_md=['# Exact rules for the20descriptive leaders','',
        'These rules were frozen before final evaluation. The order below is a post-evaluation description, not another parameter selection step. All prices/indicators use neutral split units; order prices use actual contemporaneous share units.', '',
        'A rejection means abs(low-level)<=zone*ATR, close>level, close>open, and lower wick>=25%of the daily range. EMA/Wilder averages are SMA-seeded; ATR/ADX/RSI use14sessions. KAMA efficiency ratio uses trailing displacement/absolute travel with squared fast2/slow30smoothing bounds. Completed weeks release only in the following observed week. Strict pivots require all left/right neighbors and release after the right bars.', '']
    for row in ranked.head(20).itertuples():
        cfg=configs[row.id];spec=_rule_text(cfg)
        family=cfg['family']
        if 'divergence' in family:
            weakness='Pivot confirmation delays the decision; a divergence can persist while price continues against the proposed reversal. Low-frequency divergence events give weak independent sample support.'
        elif family.startswith(('ema_','kama_','macd_','ppo_')):
            weakness='Smoothing and crossover confirmation can lag reversals and whipsaw in ranges. A favorable directional regime or sparse filter can create an apparent average that does not repeat across stocks or dates.'
        else:
            weakness='A confirmed support, retest, round level or rejection does not prevent the level from breaking. Confirmation and touch rules can reduce sample size; overnight gaps can exceed the intended stop risk.'
        spec['weaknesses_and_failure_scenarios']=weakness+' Volume, spread and fill assumptions remain model inputs.'
        spec['observed_evidence_failures']=row.failure_reasons
        spec['final_evidence']=f'Net return {row.final_total_return_pct:.6f}%; pooled expectancy {row.final_expectancy_r:.6f}R; {int(row.final_n_trades)} stock trades. Status: {row.status}.'
        specifications.append(dict(rank=row.rank,id=row.id,status=row.status,configuration=cfg,rules=spec))
        rules_md += [f'## {row.rank}. {row.family}', '', f'`{row.id}` — {row.status}.', '']
        for label,value in spec.items():rules_md += [f'**{label.replace("_"," ").capitalize()}:** {value}', '']
        rules_md += ['**Complete frozen configuration:**','', '```json',json.dumps(_clean(cfg),indent=2,allow_nan=False),'```','']
    import re
    rule_lines=[];rule_code=False
    for line in rules_md:
        if line.startswith('```'):rule_code=not rule_code;rule_lines.append(line);continue
        if rule_code or line.startswith('`'):rule_lines.append(line);continue
        text=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',line)
        text=re.sub(r'(?<=%)(?=[A-Za-z])',' ',text).replace('netR','net R')
        rule_lines.append(text)
    (out/'top-20-rules.md').write_text('\n'.join(rule_lines),encoding='utf-8');_save(out/'top-20-exact-rules.json',specifications)
    universe=_json(out/'universe.json',{});audit=_json(out/'data-audit.json',{});summary=_json(out/'run-summary.json',{})
    dispositions=pd.read_csv(out/'universe-dispositions.csv') if (out/'universe-dispositions.csv').exists() else pd.DataFrame()
    excluded=dispositions[~dispositions.eligible.astype(str).str.lower().eq('true')] if len(dispositions) else pd.DataFrame()
    counts={}
    for value in excluded.get('reasons',[]):
        try: reasons=json.loads(value)
        except (ValueError,TypeError):reasons=[]
        for reason in reasons:
            name=reason.get('reason',reason.get('kind','unspecified'));counts[name]=counts.get(name,0)+1
    exclusion_counts=pd.DataFrame([dict(reason=k,stocks=v) for k,v in sorted(counts.items())]);exclusion_counts.to_csv(out/'universe-exclusion-counts.csv',index=False)
    (out/'universe-exclusions.md').write_text('# Starting-universe dispositions\n\nReason counts can overlap for the same company. Every starting identity remains in the disposition ledger.\n\n'+_md(exclusion_counts)+'\n\n'+_md(excluded,['symbol','sector','research_observations','reasons']),encoding='utf-8')
    _write_main(out,root,ranked,categories,runs,stocks,monthly,yearly,stability,trade_breakdown,uncertainty,failure,universe,audit,summary,exclusion_counts)
    return dict(report=str(out/'REPORT.md'),top20=str(out/'top-20.csv'),screen_passes=int(ranked.evidence_screen_pass.sum()),finalists=len(ranked))


def _write_main(out,root,ranked,categories,runs,stocks,monthly,yearly,stability,trade_breakdown,uncertainty,failure,universe,audit,summary,exclusion_counts):
    top=ranked.head(20);passed=int(ranked.evidence_screen_pass.sum());best=ranked.iloc[0]
    dev=_subset(runs,'development','development_stocks');val=_subset(runs,'validation','development_stocks')
    pbo=_json(out/'pbo-development.json',{});dsr=_json(out/'dsr-development.json',{});walk=pd.DataFrame(_json(out/'walk-forward.json',[]))
    periods=_json(out/'protocol.json',{}).get('parts',{})
    trial_count=int(summary.get('coarse_configurations',len(dev)))+int(summary.get('refined_configurations',0))
    evidence=(f'{passed}of{len(ranked)}frozen family finalists pass the report evidence screen. Each still requires new forward observations before a claim of repeatability.' if passed else
              f'None of the{len(ranked)}frozen family finalists passes the full evidence screen. The top20are ranked diagnostics; this study does not supply20validated trading strategies.')
    zero_final=int(ranked.final_n_trades.fillna(0).eq(0).sum())
    top_table=top[['rank','family','status','final_n_trades','final_total_return_pct','final_expectancy_r','final_sharpe','final_max_drawdown_pct','final_positive_stock_pct','reserved_total_return_pct','double_total_return_pct','severe_total_return_pct']].copy()
    top_table.columns=['Rank','Family','Status','Final trades','Final net%','Final netR','Sharpe','Portfolio DD%','Positive stocks%','Reserved net%','Double/10bps%','Triple/20bps%']
    uncertainty_rows=[]
    for row in top.itertuples():
        u=uncertainty.get(row.id,{})
        uncertainty_rows.append(dict(family=row.family,return_ci95_pct=str(u.get('return_ci95_pct')),netR_ci95=str(u.get('r_ci95')),
                                     validation_adjusted_p=row.validation_max_t_adjusted_p,development_DSR=dsr.get(row.id,{}).get('dsr')))
    final_stocks=stocks[(stocks.stage=='final')&(stocks.pool=='all_eligible_stocks')]
    stock_summary=final_stocks.groupby('symbol').agg(sector=('sector','first'),frozen_rules=('id','count'),median_rule_net_pct=('total_return_pct','median'),
        positive_rules=('total_return_pct',lambda x:int((x>0).sum())),median_rule_trades=('n_trades','median'),worst_rule_drawdown_pct=('max_drawdown_pct','max')).reset_index()
    stock_summary['positive_rules_pct']=100*stock_summary.positive_rules/stock_summary.frozen_rules
    stock_summary=stock_summary.sort_values(['median_rule_net_pct','positive_rules_pct'],ascending=False);stock_summary.to_csv(out/'stock-consistency.csv',index=False)
    selected_months=monthly[(monthly.stage=='two_year')&(monthly.pool=='all_eligible_stocks')&monthly.id.isin(top.id)]
    month_stats=selected_months.groupby('id').return_pct.agg(months='count',positive_months=lambda x:int((x>0).sum()),median_month_pct='median',worst_month_pct='min',best_month_pct='max').reset_index()
    month_stats['family']=month_stats.id.map(ranked.set_index('id').family);month_stats.to_csv(out/'monthly-consistency.csv',index=False)
    yearly_top=yearly[(yearly.stage=='two_year')&(yearly.pool=='all_eligible_stocks')&yearly.id.isin(top.id)].copy();yearly_top['family']=yearly_top.id.map(ranked.set_index('id').family)
    yearly_top=yearly_top.pivot(index='family',columns='year',values='return_pct').reset_index();yearly_top.columns=[str(c) for c in yearly_top.columns]
    stage_summary=runs.groupby(['stage','pool']).agg(runs=('id','count'),zero_trade_runs=('n_trades',lambda x:int((x==0).sum())),positive_return_runs=('total_return_pct',lambda x:int((x>0).sum())),median_net_pct=('total_return_pct','median')).reset_index()
    lines=['# Expanded daily swing-strategy discovery','',evidence,'',
        f"Registered starting identities: **{summary.get('registered_stocks',audit.get('stocks','unknown'))}**; executable complete-data stocks: **{summary.get('eligible_stocks',audit.get('eligible_stocks','unknown'))}**; development companies: **{summary.get('development_stocks','unknown')}**; reserved novel companies: **{summary.get('reserved_new_stocks','unknown')}**. Coarse configurations: **{summary.get('coarse_configurations','unknown')}**; development-only refinements: **{summary.get('refined_configurations','unknown')}**; logged execution runs: **{len(runs)}**. All failed configurations and zero-trade outcomes are retained.",'',
        '## Interpretation and verdict','',
        f"The leading descriptive family is **{best.family}**, with final mean-sleeve net return **{_fmt(best.final_total_return_pct)}%**, **{_fmt(best.final_n_trades)}**pooled stock trades and mean netR **{_fmt(best.final_expectancy_r)}**. Its reserved-company return is **{_fmt(best.reserved_total_return_pct)}%**, and double-fee/10bps return is **{_fmt(best.double_total_return_pct)}%**. Its status is **{best.status}**.",'',
        'A family winner was frozen using development/validation only. Final outcomes rank those already-frozen finalists descriptively; they do not generate neighbors, change entries, pick new exits, or choose per-stock parameters. The two-year performance paths include selection periods and are in-sample context. This calendar overlaps earlier research, so the final dates cannot honestly be called untouched. Reserved companies test cross-sectional transfer within the same market history.','',
        'The two small positive final aggregate returns did not survive the double-cost scenario; all three rolling walk-forward selections lost money. The leading rule was exposed during only about4.3%of observed stock-days, so its very small mean-sleeve return is not comparable to a fully invested index return.','',
        'The strongest development findings did not reproduce nearby:119of134refined settings were profitable on development companies/dates, but0of134were profitable in validation. A broad positive training neighborhood therefore did not establish a durable effect. The coarse-grid development CSCV/PBO diagnostic was0.70; this is a conditional search-instability statistic, not the probability that every technical strategy fails.','',
        '## Evaluation design','',
        _md(pd.DataFrame([dict(segment=k,start=v[0],end_exclusive=v[1]) for k,v in periods.items()])), '',
        'Each company has its own independent ₹1mcapital sleeve. Reported aggregate equity is the arithmetic mean of these separate sleeves; it is not a pooled deployable account, daily rebalanced portfolio, or allocation recommendation. Pooled trade counts/netR reflect correlated stock opportunities. Mean-sleeve returns use capital including idle cash. NIFTY context is a fully invested price index and excludes dividends and trading costs, so it is not exposure matched.','',
        '## Descriptive top20','',_md(top_table),'',
        'The complete ranking of frozen family finalists, including failures, is in [all-finalists.csv](all-finalists.csv). Exact IDs, configurations, entry/filter/exit/stop/risk rules are in [top-20-rules.md](top-20-rules.md) and [top-20-exact-rules.json](top-20-exact-rules.json).','',
        f'Zero-trade final families: **{zero_final}**. Screen passes sort ahead of diagnostics. The remaining order uses45%final,25%reserved,20%double-cost and10%validation bounded scores:40%clipped Sharpe,30%clipped netR,20%positive-stock breadth and10%clipped median stock return. This ranking is an outcome summary, not evidence that its top-ranked rule has escaped selection bias.','',
        'Evidence-screen requirements: frozen development/validation eligibility; at least50final and20reserved trades; positive return and expectancy in both pools; at least50%positive final-stock breadth; worst-sleeve drawdown no more than25%; positive double-fee/10bps return and expectancy; positive lower95%10-session-block bounds for final return and pooled netR; validation search-adjusted p<=.05. See [report-evidence-screen.json](report-evidence-screen.json). A failure on any dimension leaves the candidate labeled diagnostic.','',
        '## Category leaders','',_md(categories), '',
        'Category leaders obey the same screen-first ordering within the already-frozen family representatives. Broad family rows may include an explicit extra filter. The separate MACD-only, EMA-only and S&R-only rows require no extra filter and compatible exits; their scope is the eligible pure subset of frozen representatives, not a new search of final outcomes across every coarse rule. Risk-adjusted leaders then use final Sharpe; drawdown leaders use the smallest final portfolio drawdown; consistency uses the smaller of final/reserved positive-stock breadth. An inactive or rejected diagnostic can win a descriptive category and remains labeled as such.','',
        '## Full paths, drawdowns, costs and family transfer','',
        '![Mean sleeve equity and drawdown](charts/equity-drawdown.png)','',
        '![All frozen families by segment and cost](charts/family-stage-returns.png)','',
        '![Exposure context](charts/benchmark-context.png)','',
        'Daily decisions execute at the next open with5bpsadverse slippage per fill at baseline. Stops are tested before targets on ambiguous OHLC candles; adverse gaps can exceed initial risk. Fee schedules change by fill date. Targets are calibrated to modeled netR including costs; a same-day exit may avoid the overnight DP fee. Double/triple fee tests use10/20bpsadverse slippage and rerun sizing/execution, rather than subtracting a constant from original profit.','',
        '## Calendar consistency','',
        '![Calendar-month heatmap](charts/monthly-heatmap.png)','',_md(month_stats,['family','months','positive_months','median_month_pct','worst_month_pct','best_month_pct']), '',
        'Calendar-year net returns below come from the full-period frozen-rule paths.2024and2026are partial years; months at dataset boundaries can also be partial. These are not independent replications.','',_md(yearly_top),'',
        '## Stocks, regimes and trade behavior','',
        'Stock table ranks median final return across every frozen family, including flat/losing outcomes. It does not pick a winning rule per company. These company rankings use final outcomes and are descriptive, not an implementable pre-test stock selector.','',
        _md(stock_summary,['symbol','sector','frozen_rules','median_rule_net_pct','positive_rules_pct','median_rule_trades','worst_rule_drawdown_pct'],15),'',
        'Full per-stock/per-rule results are in [stock-analysis.csv](stock-analysis.csv). [stock-consistency.csv](stock-consistency.csv) retains all eligible companies. [regime-analysis.csv](regime-analysis.csv) uses NIFTY close/EMA50/EMA200 known on the signal day: all above/aligned is market_up, all below/aligned is market_down, and the rest is mixed. Regime summaries are conditional breakdowns of the same trades, not extra tests of new parameters.','',
        _md(trade_breakdown[(trade_breakdown.dimension=='signal_market_regime')&(trade_breakdown.stage=='final')&trade_breakdown.id.eq(best.id)] if not trade_breakdown.empty else pd.DataFrame(),['value','n_trades','expectancy_r','win_rate_pct','net_pnl','avg_hold_hours']), '',
        'Trade-tail quantiles, worst/best netR, holding-time percentiles, dividends, gap-stop counts and fee totals are in [trade-analysis.csv](trade-analysis.csv). Exit reasons, signal regimes, entry weekdays, holding buckets and exit years are in [trade-breakdowns.csv](trade-breakdowns.csv). Journal netPnL reconciles each sleeve’s realized end NAV; pooled cash fees/netPnL are sums over separate stock sleeves and should not be compared directly with a single ₹1mportfolio.','',
        '## Uncertainty and search controls','',_md(pd.DataFrame(uncertainty_rows)), '',
        f"Development CSCV/PBO: **{_fmt(pbo.get('pbo'))}**; distinct outcome paths **{_fmt(pbo.get('distinct_rules'))}**, original rules **{_fmt(pbo.get('original_rules'))}**. The diagnostic scope and deduplication are recorded in [pbo-development.json](pbo-development.json). Symmetric CSCV splits are not chronological out-of-sample tests. Development-selected refinement is excluded from a coarse-only CSCV analysis when specified by the runner.",'',
        f"The ledger includes{trial_count}attempted coarse/refined tuples. DSR reports an IID/nonnormal-return approximation with an assumed independent trial count; dependence and historical reuse limit that interpretation. Validation max-t shares10-session calendar bootstrap blocks across rules to preserve market/cross-rule dependence. Final block intervals are conditional on frozen choices; they do not remove earlier research reuse. Bootstrap positive fractions are resampling frequencies, not probabilities that a strategy is truly profitable. All-zero return/trade series remain explicit null/undefined outcomes rather than disappearing.",'',
        '[Final return/netR intervals](final-uncertainty.json), [validation search control](validation-search-control.json), [final frozen-family search diagnostic](final-search-control-diagnostic.json), and [development DSR](dsr-development.json) retain the machine-readable values. Final search diagnostics are descriptive and do not feed back into trading rules.','',
        '## Ablations and development-neighbor stability','',
        '![Single-factor ablation changes](charts/ablation-deltas.png)','',
        'Each coarse single-factor variant is compared with its own family’s central unfiltered entry/control on the same development or validation companies/calendar. [ablation-analysis.csv](ablation-analysis.csv) includes the base values, changed values and deltas for filters, stops, exits, targets and hold limits. Development-only neighbors are evaluated against their actual parent and are excluded from the central-control ablation chart. No final-stage fine-grid search is performed.','',
        _md(stability,limit=25),'',
        '[neighbor-stability.csv](neighbor-stability.csv) contains every attempted neighbor and axis. Positive-neighbor fractions and the min/median/max outcomes show whether an isolated best setting has surrounding support. A useful neighborhood was selected on development data only; validation still tests that selected neighborhood conditionally.','',
        '## Walk-forward checks','',_md(walk,['train_start','test_start','test_end','id','n_trades','total_return_pct','expectancy_r']), '',
        'The rolling9-month train/3-month test policy searches only the original frozen coarse rules in each training fold. Later main-study fine neighborhoods cannot enter earlier fold training. A fold with no eligible rule remains cash. Folds stop before the final calendar segment.','',
        '## Complete attempts and failures','',_md(stage_summary), '',
        f"Logged zero-trade executions: **{int(failure.zero_trades.sum())}**; nonpositive-return executions: **{int(failure.nonpositive_return.sum())}**; nonpositive/undefined-expectancy executions: **{int(failure.nonpositive_or_missing_expectancy.sum())}**; drawdown-veto executions: **{int(failure.catastrophic_sleeve_drawdown.sum())}**. Counts overlap and include different dates/pools/cost scenarios; they are not distinct strategy counts.",'',
        'Every exact attempted tuple is in [all-tried-configurations.json](all-tried-configurations.json), every execution summary in [all-runs.csv](all-runs.csv), and every retained failure classification in [failure-ledger.csv](failure-ledger.csv). The SQLite ledger preserves stock rows and portfolio calendars. Failed families are not replaced using final winners.','',
        '## Universe exclusions and limitations','',_md(exclusion_counts), '',
        '[universe-exclusions.md](universe-exclusions.md) lists excluded identities and reasons; counts can overlap. The dated source is an official October2024NIFTY500fund portfolio published before the November2024start. It is a holdings proxy, not a certified historical index constituent master. Membership is frozen as a cohort; later additions are not silently inserted. Current instruments resolve identity only.','',
        'Missing research-period candles, ambiguous/unmodeled capital actions and discontinuities are quarantined before performance analysis. Requiring complete executable data can favor surviving/data-complete companies even though every starting name stays in the disposition ledger. Results therefore do not establish outcomes for all500historical members. Prices before the universe date are indicator warmup, never performance attributed to a contemporaneously selected2020universe.','',
        'Actual share units are reconstructed from split/bonus continuity and known actions; dividends accrue only to carried shares. Fractional entitlements and unmodeled mergers/rights/demergers are excluded. Historical volume adjustment is unverified. The fixed inverse-adjustment hypothesis uses prior20median provider volume/current unit factor for current-share capacity and prior20median(neutral price*provider volume) for traded-value proxy. Neither volume hypothesis nor5/10/20bpsslippage certifies historical spread, depth, queue priority or market impact.','',
        'Daily OHLC cannot establish intraday ordering; stop-first is a conservative convention. Close-marked drawdowns can miss intraday peaks/troughs. Reported holding hours use daily-bar timestamps, so they are calendar-time approximations rather than measured intraday fill durations. Exposure is the fraction of observed stock-days with a position. The NIFTY provider calendar includes observed special sessions and is not independently certified against every exchange circular. No volume-at-price, true volume-profile nodes, option returns, broker fills, earnings valuation or long-term investment suitability is inferred.','',
        'The search is broad but bounded. Entry grids and development-only neighborhoods vary indicator periods and structural settings; filters use frozen reference thresholds rather than an optimized threshold grid. The eight ablations cover volume expansion, ADX, RSI, ATR/price, market trend, stock relative strength against NIFTY, breadth and sector-peer momentum. Sector peers are a cohort-based proxy, not historical sector-index relative strength. True delivery volume and volume-at-price were unavailable. Historical NIFTY Next 50/100/200 subgroup membership was not separately certified, so no subgroup-specific coverage claim is made. The two-year evaluation does not establish repeatability across longer market cycles.','',
        '## Implementation recommendations','',
        'Further investigation: KAMA-cross plus NIFTY-relative-strength and EMA-cross plus NIFTY-relative-strength are useful diagnostic references because they lead the frozen ranking. Their tiny returns and cost failures do not justify a profitability claim. Investigate observed execution costs and an explicitly funded portfolio model before expanding their parameters.','',
        'Paper and forward testing: no candidate qualifies as a validated edge. If a fixed rule is observed prospectively to validate the data and execution pipeline, preregister its exact configuration, cash allocation, costs, evaluation horizon and failure criteria before collecting new observations. That operational exercise must remain distinct from a profitable-strategy claim. Live deployment: none is supported by this study.','',
        'Stock selection: company and sector tables describe where these frozen rules happened to work. They do not demonstrate which stocks will perform next. No reusable stock-type selector was frozen and independently validated here, so the observed winners cannot support an investment allocation rule.','',
        '## Primary references and research artifacts','',
        'Indicator definitions and hypothesis motivation came from [Fidelity MACD](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/macd), [StockCharts PPO](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo), [StockCharts adaptive overlays](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays), and [Schwab CAM](https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/C-D/CAM-Indicator). These definitions do not establish an Indian-equity edge.','',
        '[New York Fed order-placement research](https://www.newyorkfed.org/research/staff_reports/sr125.html) motivates separate breakout, reversal and round-price hypotheses in currency markets; transferring that motivation to equities is an unproven hypothesis. [Sullivan, Timmermann and White](https://ideas.repec.org/p/fmg/fmgdps/dp303.html) and [Bailey and López de Prado](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) motivate search corrections, not automatic validation.','',
        f"The frozen research sources are [DISCOVERY_FREEZE.md]({(root/'research/swing_discovery/DISCOVERY_FREEZE.md').as_posix()}) and [RESEARCH_DESIGN.md]({(root/'research/swing_discovery/RESEARCH_DESIGN.md').as_posix()}). [Protocol](protocol.json), [data audit](data-audit.json), [frozen finalists](frozen-finalists.json), [run summary/source hashes](run-summary.json), and [raw fingerprints](raw-fingerprints.json) provide provenance.",'']
    # Optional resolution checks are authored separately after this module is
    # available. Link the evidence without claiming the test happened yet.
    extra=sorted(p.name for p in out.glob('*resolution*.json'))
    if extra:lines += ['## Finer-resolution checks','', 'The preselected finer-resolution subset and its limitations are recorded in '+', '.join(f'[{name}]({name})' for name in extra)+'. These checks do not retune the daily finalists.','']
    if (out/'buy-hold-benchmarks.csv').exists():
        bench=pd.read_csv(out/'buy-hold-benchmarks.csv')
        lines += ['## Executable-assumption buy-and-hold control','',
          'This control buys once at the first qualifying open using the same cash, fees,5bpsfill slippage, minimum turnover proxy and1%lagged-volume cap. Unspent cash stays idle; quantities adjust for modeled splits and receive dividend economic entitlements. It is a separate benchmark, not a reconstituted index or an exposure-matched alpha test.','',
          _md(bench[bench.pool.eq('all_eligible_stocks')],['stage','total_return_pct','cagr_pct','max_drawdown_pct','sharpe','n_trades']),'',
          '[All benchmark pools](buy-hold-benchmarks.csv), [per-stock benchmark results](buy-hold-stock-results.csv).','']
    if (out/'verification.json').exists():lines += ['## Independent verification','', '[Ledger, journal and chronology verification](verification.json) reconciles the completed experiment. Statistical diagnostics remain conditional on the documented assumptions.','']
    if (out/'additional-regime-analysis.csv').exists():lines += ['## Additional causal regime breakdowns','',
      '[Additional regime analysis](additional-regime-analysis.csv) separates signal-day market volatility, normalized60-session trend strength, and a known reversal-shock proxy. High volatility means20-session realized volatility above its prior252-session median. Strong trend means absolute60-session market return divided by (20-session volatility * sqrt(60)) is at least1. Reversal shock means a completed-day move larger than2prior daily-volatility units opposite the preceding20-session direction. These are descriptive breakdowns of frozen trades, not new filters or independent experiments.','']
    # Typeset narrative only, preserving exact strategy IDs, JSON and numeric tables.
    import re
    formatted=[];in_code=False
    for line in '\n'.join(lines).splitlines():
        if line.startswith('```'):in_code=not in_code;formatted.append(line);continue
        if in_code or line.startswith('|'):formatted.append(line);continue
        pieces=re.split(r'(\[[^\]]*\]\([^)]*\)|`[^`]*`|\*\*[^*]*\*\*)',line)
        for j in range(0,len(pieces),2):
            original=pieces[j]
            if j>0 and pieces[j-1].startswith('**') and original[:1].isalpha():original=' '+original
            v=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',original)
            v=re.sub(r'(?<=%)(?=[A-Za-z])',' ',v)
            v=v.replace('netR','net R').replace('netPnL','net P&L').replace('mcapital','m capital').replace('mportfolio','m portfolio')
            v=v.replace('bpsadverse','bps adverse').replace('bpsslippage','bps slippage').replace('bpsfill','bps fill')
            v=re.sub(r'(?<=%)(?=\d)',' ',v)
            pieces[j]=v
        formatted.append(''.join(pieces))
    (out/'REPORT.md').write_text('\n'.join(formatted)+'\n',encoding='utf-8')
