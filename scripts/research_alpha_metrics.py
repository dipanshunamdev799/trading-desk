"""Project Alpha metrics and configurable capital feasibility; research proxies only."""
import hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts'/'project_alpha'
CAPITALS=[100000,250000,500000,1000000];RISKS=[.0025,.005]


def dump(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False,default=str),encoding='utf-8')


def metrics(pnl,dates,capital=250000):
    p=np.asarray(pnl,dtype=float);n=len(p)
    if not n:return {'trades':0}
    wins=p[p>0];losses=p[p<0];curve=capital+np.r_[0,np.cumsum(p)];peak=np.maximum.accumulate(curve);dd=peak-curve
    longest=run=0;worst=lossrun=0
    for underwater in dd[1:]>0:run=run+1 if underwater else 0;longest=max(longest,run)
    for value in p:lossrun=lossrun+1 if value<0 else 0;worst=max(worst,lossrun)
    monthly=pd.Series(p,index=pd.to_datetime(dates,utc=True)).groupby(lambda x:x.strftime('%Y-%m')).sum()
    return {'trades':n,'net_total':float(p.sum()),'net_mean':float(p.mean()),'profit_factor':float(wins.sum()/-losses.sum()) if len(losses) else None,
        'profit_factor_status':'finite' if len(losses) else 'no_observed_losses_not_established',
        'win_pct':float((p>0).mean()*100),'average_win':float(wins.mean()) if len(wins) else None,
        'average_loss':float(losses.mean()) if len(losses) else None,
        'realized_avg_win_loss_ratio':float(wins.mean()/-losses.mean()) if len(wins) and len(losses) else None,
        'max_closed_trade_drawdown':float(dd.max()),'max_closed_trade_drawdown_pct':float(np.max(np.divide(dd,peak))*100),
        'max_drawdown_duration_trades':int(longest),'max_consecutive_losses':int(worst),'worst_trade':float(p.min()),'best_trade':float(p.max()),
        'negative_months':int((monthly<0).sum()),'observed_months':len(monthly),'monthly':{k:float(v) for k,v in monthly.items()},
        'illustrative_return_on_initial_capital_pct':float(p.sum()/capital*100),'initial_capital':capital}


def simulate(rows,capital,risk_fraction):
    cash=capital;daily={};weekly={};outcomes=[];skips={};blocked=False
    for r in rows.to_dict('records'):
        dt=pd.Timestamp(r['entry_at']);day=dt.strftime('%Y-%m-%d');week=f'{dt.isocalendar().year}-{dt.isocalendar().week:02d}'
        def reject(reason):skips[reason]=skips.get(reason,0)+1
        if blocked:reject('capital_exhausted');continue
        if daily.get(day,0)<=-capital*.01:reject('daily_loss_gate');continue
        if weekly.get(week,0)<=-capital*.03:reject('weekly_loss_gate');continue
        # Stops/time exits do not guarantee planned risk. Unknown stops use full premium at risk.
        premium=float(r['premium_entry'])*int(r['lot']);stop_loss=r.get('planned_stop_loss_rupees')
        planned=float(stop_loss) if pd.notna(stop_loss) and stop_loss>0 else premium
        planned+=200+5*int(r['lot']) # severe friction allowance plus adverse stop reserve
        budget=max(0,min(capital*risk_fraction,capital*.01+daily.get(day,0),capital*.03+weekly.get(week,0)))
        lots=min(int(budget//planned),int(cash//(premium+200+5*int(r['lot']))))
        if lots<1:reject('minimum_lot_exceeds_risk_or_cash');continue
        net=float(r['severe_net_rupees_per_lot'])*lots
        capital_used=premium*lots;full_premium_shock=-(premium+200+5*int(r['lot']))*lots
        cash+=net;daily[day]=daily.get(day,0)+net;weekly[week]=weekly.get(week,0)+net
        blocked=cash<=0
        outcomes.append({'entry_at':r['entry_at'],'exit_at':r['exit_at'],'day':day,'week':week,'lots':lots,'planned_risk_rupees':planned*lots,
            'premium_capital_used':capital_used,'net':net,'equity':cash,'full_premium_loss_scenario':full_premium_shock,
            'full_premium_scenario_exceeds_daily_limit':-full_premium_shock>capital*.01,
            'realized_loss_exceeds_planned':net<-(planned*lots)})
    return outcomes,skips


def main():
    path=OUT/'exit-trades.csv'
    dump('metrics-protocol.json',{'input':str(path.relative_to(ROOT)),'capitals':CAPITALS,'risk_fractions':RISKS,
       'daily_loss_fraction':.01,'weekly_loss_fraction':.03,'max_simultaneous_positions':1,
       'risk_rule':'Whole lots <=minimum of fixed initial capital risk budget and remaining daily/weekly loss room, divided by planned stop + severe allowance; also require premium cash affordability. Full premium at risk when no defined stop.',
       'model':'All exit and contract configurations disclosed, no choice by results; severe proxy outcomes, closed-trade drawdown only.',
       'monte_carlo':'2000 session-block samples of each observed period, conditional on very small historical sample; no inferred future tail probability.',
       'stress':'Separate deterministic full-premium-loss scenario for each permitted sized trade; not an estimated probability.',
       'acceptance':'No strategy promoted by these metrics; price-proxy execution, insufficient independent sessions and missing forward evidence fail live gates.'})
    x=pd.read_csv(path)
    # Only one path convention for capital accounting; alternate bounds remain in source evidence.
    if 'ambiguity' in x:x=x[x.ambiguity=='adverse_first']
    elif 'path_mode' in x:x=x[x.path_mode=='adverse_first']
    elif 'ambiguity_mode' in x:x=x[x.ambiguity_mode=='adverse_first']
    if 'status' in x:x=x[x.status.isin(['observed_candle_proxy','closed','proxy_closed','observed_proxy'])]
    groupcols=[c for c in ['configuration','config_id','exit_policy','expiry_bucket','strike_rule'] if c in x]
    if not groupcols:raise ValueError('Exit configuration key absent')
    summaries=[];risk=[];curves=[];months=[];mc=[];sized=[]
    for key,g in x.groupby(groupcols,dropna=False):
        label=' / '.join(map(str,key if isinstance(key,tuple) else [key]));g=g.sort_values(['entry_at','exit_at'])
        m=metrics(g.severe_net_rupees_per_lot,g.exit_at);summaries.append({'configuration':label,**m})
        equity=250000
        for r in g.to_dict('records'):
            equity+=r['severe_net_rupees_per_lot'];curves.append({'configuration':label,'exit_at':r['exit_at'],'equity_unit_lot':equity})
        for month,value in m.get('monthly',{}).items():months.append({'configuration':label,'month':month,'net_severe_per_lot':value})
        for capital in CAPITALS:
            for fraction in RISKS:
                rows,skips=simulate(g,capital,fraction)
                rm=metrics([r['net'] for r in rows],[r['exit_at'] for r in rows],capital)
                risk.append({'configuration':label,'capital':capital,'risk_fraction':fraction,'source_trades':len(g),'taken':len(rows),'skipped':skips,
                    'full_premium_scenarios_over_daily_limit':sum(r['full_premium_scenario_exceeds_daily_limit'] for r in rows),**rm})
                for r in rows:sized.append({'configuration':label,'capital':capital,'risk_fraction':fraction,**r})
        daily=g.assign(day=pd.to_datetime(g.exit_at,utc=True).dt.strftime('%Y-%m-%d')).groupby('day').severe_net_rupees_per_lot.sum().to_numpy()
        rng=np.random.default_rng(20261109);drawdowns=[];totals=[]
        for _ in range(2000):
            seq=rng.choice(daily,size=len(daily),replace=True);eq=np.r_[0,seq.cumsum()];dd=np.maximum.accumulate(eq)-eq
            totals.append(float(seq.sum()));drawdowns.append(float(dd.max()))
        mc.append({'configuration':label,'observed_days':len(daily),'conditional_total_pnl_ci95':np.quantile(totals,[.025,.975]).tolist(),
            'conditional_max_drawdown_ci95':np.quantile(drawdowns,[.025,.975]).tolist(),'warning':'Tiny sample; absence of modeled tail loss is not evidence it cannot occur.'})
    pd.DataFrame(summaries).drop(columns=['monthly'],errors='ignore').to_csv(OUT/'metrics-leaderboard.csv',index=False)
    pd.DataFrame(risk).drop(columns=['monthly'],errors='ignore').to_csv(OUT/'risk-feasibility.csv',index=False)
    pd.DataFrame(sized).to_csv(OUT/'risk-trades.csv',index=False);pd.DataFrame(curves).to_csv(OUT/'equity-curves.csv',index=False);pd.DataFrame(months).to_csv(OUT/'monthly-performance.csv',index=False)
    dump('monte-carlo.json',mc)
    summary={'source_rows':len(x),'configurations':len(summaries),'risk_scenarios':len(risk),'total_sized_decisions':len(sized),
       'data_execution':'Five-session actual candle proxies; adverse-first bounds, no verified fills',
       'live_decision':'RESEARCH ONLY','metrics':summaries}
    dump('metrics-summary.json',summary)
    lines=['# Performance metrics and capital feasibility','',f"{len(x)} accepted adverse-first candle-proxy rows, {len(summaries)} exit/contract configurations, {len(risk)} capital/risk scenarios. No winner selected.",
       '', 'Net expectancy, profit factor, average win/loss, realized reward/loss ratio, worst trade, consecutive losses, monthly outcomes, closed-trade drawdown and recovery duration are exported for every configuration. Profit factor is null when no losses occurred, with a status explaining that finite expectancy is not established. Curve reference capital INR250000 is illustrative, not a capital recommendation.',
       '', 'Risk fractions0.25%/0.5%, daily loss gate1%, weekly3% and one simultaneous position are hypotheses from the brief. Whole-lot/cash affordability can cause abstention. Gates act after losses are observed; gaps, missing exits and loss of the full premium can exceed a planned stop and daily limit. Position sizing cannot repair negative expectancy.',
       '', 'No-stop time exits reserve full premium at risk. Defined stops reserve planned loss plus a severe execution allowance; the separate full-premium scenario shows remaining exposure. Capital is fixed for risk budgeting; profits do not increase that budget. No averaging, martingale or doubling is implemented.',
       '', 'Monte Carlo resamples observed daily PnL blocks2000times. It measures uncertainty conditional on only five recent sessions. It is not an estimate of real-world ruin or future risk-limit-breach probability. Full-premium shocks are deterministic stress cases, not assigned empirical frequencies.',
       '', 'Intratrade equity and tick-level MAE/MFE are unsupported by these candle tests. Candle MAE/MFE bounds are provided by exit-trades.csv; cash/percentage drawdown here is measured at closes and can understate mark-to-market losses. Order failure frequency cannot be estimated from simulations; proxy coverage rejection rates are not broker rejection rates.',
       '', 'Outputs: metrics-leaderboard.csv,risk-feasibility.csv,risk-trades.csv,equity-curves.csv,monthly-performance.csv,monte-carlo.json. Account returns remain hypothetical, with asynchronous price proxies and illustrative costs. Historical, forward and execution gates remain unmet.']
    (OUT/'risk-metrics-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='metrics'}))


if __name__=='__main__':main()
