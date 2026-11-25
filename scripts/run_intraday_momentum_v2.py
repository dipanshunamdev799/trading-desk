"""Frozen 2025/26 cash-equity experiments. No trading-bot capabilities."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dataclasses import replace
from datetime import datetime
from collections import Counter,defaultdict
import hashlib
import json
import math
import platform
import numpy as np
import pandas as pd

from research.intraday_momentum import data as base
from research.intraday_momentum_v2.data import OUT
from research.intraday_momentum_v2.strategy import catalog,features,signals,run,summarize
from scripts.run_intraday_momentum import freeze_json,validate_acquisition,native,write_csv

PERIODS={'development':('2025-01-01','2025-09-30'),'validation':('2025-10-01','2026-03-31'),
         'evaluation':('2026-04-01','2026-11-13'),'full':('2025-01-01','2026-11-13')}


def hashes():
    files=list((ROOT/'research/intraday_momentum_v2').glob('*.py'))+list((ROOT/'research/intraday_momentum_v2').glob('*.md'))
    files += [ROOT/'research/intraday_momentum'/f for f in ('data.py','units.py','engine.py','costs.py','resolution.py')]
    files += [Path(__file__),ROOT/'scripts/run_intraday_momentum.py']
    return {str(f.relative_to(ROOT)):base.sha(f) for f in sorted(files)}


def market_data():
    with base.connection() as c:
        c.execute("SELECT ts,open,high,low,close,volume FROM public.candles WHERE instrument_key=%s AND interval='5minute' AND source='upstox' AND ts>='2024-12-01' AND ts<'2026-11-14' ORDER BY ts",(base.NIFTY,))
        frames,reasons=base._regular_frames(c.fetchall())
        c.execute("SELECT (ts AT TIME ZONE 'Asia/Kolkata')::date,high,low,close FROM public.candles WHERE instrument_key=%s AND interval='1day' AND source='upstox' AND ts>='2024-07-01' AND ts<'2026-11-14' ORDER BY ts",(base.NIFTY,))
        daily=pd.DataFrame(c.fetchall(),columns=['day','high','low','close']).drop_duplicates('day',keep='last').set_index('day')
    daily.index=daily.index.astype(str);prev=daily.close.shift();tr=np.maximum(daily.high-daily.low,np.maximum(abs(daily.high-prev),abs(daily.low-prev)))
    lagvol=tr.rolling(20,min_periods=15).mean().shift()/prev
    return {d:dict(return_=None,**{'return':b.close.to_numpy()/float(prev.loc[d])-1},lag_vol=float(lagvol.loc[d]))
            for d,b in frames.items() if d in prev.index and np.isfinite(prev.loc[d])},dict(reasons)


def expanded_summary(result,first,last):
    m=summarize(result,first,last)
    t=[t for t in result['trades'] if first<=t['session']<=last];d=[d for d in result['daily'] if first<=d['session']<=last]
    positive=[x['net_pnl'] for x in t if x['net_pnl']>0];negative=[x['net_pnl'] for x in t if x['net_pnl']<0]
    notionals=[x['entry_price']*x['quantity'] for x in t]
    m.update(gross_bps_per_trade=float(np.mean([x['gross_before_slippage']/n*10000 for x,n in zip(t,notionals)])) if t else None,
        avg_win=float(np.mean(positive)) if positive else None,avg_loss=float(np.mean(negative)) if negative else None,
        payoff_ratio=float(np.mean(positive)/-np.mean(negative)) if positive and negative else None,
        worst_trade=min((x['net_pnl'] for x in t),default=None),worst_day=min((x['return_fraction'] for x in d),default=None),
        zero_trade_days=sum(x['trades']==0 for x in d),trades_per_calendar_day=len(t)/len(d) if d else 0,
        holding_minutes_mean=float(np.mean([x['holding_minutes'] for x in t])) if t else None,
        holding_minutes_p90=float(np.quantile([x['holding_minutes'] for x in t],.9)) if t else None,
        top5_profit_concentration=sum(sorted(positive,reverse=True)[:5])/sum(positive) if positive else None,
        fee_components={k:sum(x[z][k] for x in t for z in ('entry_fee_components','exit_fee_components')) for k in ('brokerage','exchange_ipft','sebi','gst','stt','stamp')},
        exposure_fraction=sum(x['holding_minutes'] for x in t)/(len(d)*355) if d else None,
        modeled_fill_rate=len(t)/len([r for r in result['rejections'] if first<=r['day']<=last]) if any(first<=r['day']<=last for r in result['rejections']) else None,
        partial_fill_evidence='UNAVAILABLE_FROM_CANDLES',funding_cost=0,leverage=1)
    return m


def uncertainty(result):
    d=[d for d in result['daily'] if PERIODS['evaluation'][0]<=d['session']<=PERIODS['evaluation'][1]]
    x=np.array([d['return_fraction'] for d in d]);n=len(x)
    if n<20:return {'status':'INSUFFICIENT'}
    rng=np.random.default_rng(731);starts=rng.integers(0,n,(2000,math.ceil(n/20)));ix=(starts[:,:,None]+np.arange(20))%n
    samples=x[ix.reshape(2000,-1)[:,:n]];returns=np.prod(1+samples,axis=1)-1
    return dict(ci95=np.quantile(returns,[.025,.975]).tolist(),familywise_lower=float(np.quantile(returns,.05/12)),
        method='2000 circular20session blocks; common seed/calendar across candidates; Bonferroni12 one-sided lower tail',
        limitation='Conditional on exposed retrospective sample; no fresh forward inference')


def segments(results):
    rows=[]
    for result in results.values():
        if result['config']['direction']!=1:continue
        groups=defaultdict(list)
        for t in result['trades']:
            f=t['signal_features'];clock=pd.Timestamp(t['decision_at']).strftime('%H:%M')
            buckets={'time':'morning' if clock<'11:30' else 'midday','market_direction':'up' if f['market_return']>=0 else 'down',
                'market_volatility':'high' if f['market_vol']>=.015 else 'low' if f['market_vol']<.008 else 'normal',
                'liquidity':'ADV>=100crore' if f['adv']>=1e9 else 'ADV<100crore','price':'>=500' if f['raw_price']>=500 else '<500',
                'sector':f['sector'],'gap':'gap>=2%' if abs(f['gap'])>=.02 else 'intraday_built',
                'rvol':'>=3' if f['rvol']>=3 else '<3','trend_efficiency':'trend' if f['efficiency']>=.5 else 'range' if f['efficiency']<.25 else 'mixed',
                'entry_stage':'<3%' if abs(f['move'])<.03 else '3-5%' if abs(f['move'])<.05 else '>=5%'}
            for dim,value in buckets.items():groups[(dim,value)].append(t)
        for (dim,bucket),ts in groups.items():
            rows.append(dict(strategy=result['name'],dimension=dim,bucket=bucket,trades=len(ts),sessions=len({x['session'] for x in ts}),
                net_pnl=sum(x['net_pnl'] for x in ts),mean_net_bps=float(np.mean([x['net_pnl']/(x['entry_price']*x['quantity'])*1e4 for x in ts])),
                sparse=len({x['session'] for x in ts})<30,selection_use=False))
    return rows


def main():
    plan=json.loads((OUT/'jobs-plan.json').read_text());acq=json.loads((OUT/'acquisition-manifest.json').read_text())
    validate_acquisition(plan,acq,base.sha(OUT/'jobs-plan.json'))
    frozen=hashes();records=base.load_sessions(plan,OUT);market,market_audit=market_data()
    missing=Counter(r['day'] for r in records if r['day'] not in market)
    records=[r for r in records if r['day'] in market];calendar=[d for d in plan['calendar'] if plan['start']<=d<=plan['end']]
    byday=defaultdict(list)
    for r in records:r['_features']=features(r);byday[r['day']].append(r)
    events=[]
    for i,(day,rs) in enumerate(sorted(byday.items())):
        groups=defaultdict(list)
        for r in rs:groups[r['sector']].append(r)
        for r in rs:
            peers=[p['_features']['move'] for p in groups[r['sector']] if p['key']!=r['key']]
            peer=np.mean(np.vstack(peers),axis=0) if len(peers)>=3 else None
            events.extend(signals(r,market[day],peer))
        if i%50==0:print('Signal days:',i,'/',len(byday),'events',len(events),flush=True)
    datahash=hashlib.sha256()
    for r in records:
        datahash.update((r['day']+r['key']+str(r['prev_close'])).encode());datahash.update(r['bars'].to_numpy(float).tobytes());datahash.update(r['rvol'].to_numpy(float).tobytes())
    datahash.update(json.dumps(market,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else str(x),sort_keys=True).encode())
    manifest=dict(generated_at=datetime.now().astimezone().isoformat(),plan_sha256=base.sha(OUT/'jobs-plan.json'),acquisition_sha256=base.sha(OUT/'acquisition-manifest.json'),
        code=frozen,data_sha256=datahash.hexdigest(),records=len(records),calendar_days=len(calendar),signals=len(events),periods=PERIODS,
        missing_market_candidates=dict(missing),market_audit=market_audit,python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,real_orders_submitted=0)
    freeze_json(OUT/'research-manifest.json',manifest);write_csv(OUT/'signals.csv',events)
    configs=catalog();primary=configs[:12];dev=[];devruns={};failed=[]
    devcal=[d for d in calendar if d<=PERIODS['development'][1]]
    for cfg in primary:
        try:
            r=run(records,events,devcal,cfg);devruns[cfg.name]=r;m=expanded_summary(r,*PERIODS['development']);dev.append(dict(strategy=cfg.name,**m))
        except ValueError as exc:failed.append(dict(strategy=cfg.name,stage='development',reason=str(exc)))
    eligible=[r for r in dev if r['trades']>=100 and r['active_days']>=60 and (r['mean_net_bps_per_trade'] or 0)>0 and r['total_return']>0 and (r['profit_factor'] or 0)>=1.1 and r['max_drawdown']>=-.15]
    eligible.sort(key=lambda r:(-r['mean_net_bps_per_trade'],-r['max_drawdown'],r['strategy']))
    selected=eligible[0]['strategy'] if eligible else None
    selection=dict(selected=selected,development_only=True,development=dev,failed=failed,manifest_sha256=base.sha(OUT/'research-manifest.json'))
    freeze_json(OUT/'development-selection-frozen.json',selection);print('Development choice frozen:',selected,flush=True)
    # A fixed path-resolution audit is predeclared regardless of profitability.
    from research.intraday_momentum_v2.resolution import audit
    chosen=devruns.get('H1-F-main-long')
    resolution=audit(chosen['trades'] if chosen else [],records,OUT/'resolution-audit',primary[0])
    if selected and selected!='H1-F-main-long':
        resolution['selected_extra']=audit(devruns[selected]['trades'],records,OUT/'selected-resolution-audit',next(c for c in primary if c.name==selected))
    results={};metrics=[];stress=[];bootstrap={};extra=[]
    for cfg in configs:
        print('Portfolio:',cfg.name,flush=True)
        try:
            r=run(records,events,calendar,cfg);results[cfg.name]=r
            if cfg.name in devruns:
                assert [t for t in r['trades'] if t['session']<=PERIODS['development'][1]]==devruns[cfg.name]['trades'],'Development prefix changed'
            assert abs(sum(t['net_pnl'] for t in r['trades'])-(r['daily'][-1]['equity']-cfg.capital))<.001
            for period,bounds in PERIODS.items():metrics.append(dict(strategy=cfg.name,period=period,category='primary' if cfg in primary else 'short_diagnostic' if cfg.direction<0 else 'control',**expanded_summary(r,*bounds)))
            if cfg in primary:
                bootstrap[cfg.name]=uncertainty(r)
                for bps in (5,25):
                    sr=run(records,events,calendar,replace(cfg,slippage_bps=bps))
                    for period,bounds in PERIODS.items():stress.append(dict(strategy=cfg.name,scenario=f'{bps}bps_side',period=period,**expanded_summary(sr,*bounds)))
                for label,changes in [('one_bar_latency',{'delay':1}),('quarter_participation',{'participation':.0025}),('capital_5lakh',{'capital':500000}),('capital_20lakh',{'capital':2000000})]:
                    try:
                        rr=run(records,events,calendar,replace(cfg,**changes))
                        for period,bounds in PERIODS.items():extra.append(dict(strategy=cfg.name,scenario=label,period=period,**expanded_summary(rr,*bounds)))
                    except ValueError as exc:extra.append(dict(strategy=cfg.name,scenario=label,status='UNRESOLVED',reason=str(exc)))
        except ValueError as exc:failed.append(dict(strategy=cfg.name,stage='full_or_stress',reason=str(exc)))
    decisions=[]
    for cfg in configs:
        ms=[m for m in metrics if m['strategy']==cfg.name];status='INCONCLUSIVE';reasons=[];statpass=False
        if not ms:reasons=['Unresolved execution/data input']
        else:
            full=next(m for m in ms if m['period']=='full');ev=next(m for m in ms if m['period']=='evaluation');val=next(m for m in ms if m['period']=='validation')
            if full['trades']<30 or full['active_days']<20:status='INCONCLUSIVE';reasons=['Fewer than30full-windowtrades or20independent active sessions; inadequate evidence']
            elif full['total_return']<=0 or (full['mean_net_bps_per_trade'] or 0)<=0:status='REJECTED';reasons=['Nonpositive full-window funded return or net expectancy under frozen assumptions']
            elif cfg.direction<0:status='FORWARD_DATA_REQUIRED';reasons=['Dated historical short eligibility unavailable; diagnostic only']
            elif cfg not in primary:reasons=['Nonselectable control; cannot promote after inspection']
            elif cfg.name!=selected:reasons=['Not selected by frozen development gate']
            else:
                st=next((m for m in stress if m['strategy']==cfg.name and m['scenario']=='25bps_side' and m['period']=='evaluation'),{})
                chunks=np.array_split([d for d in results[cfg.name]['daily'] if PERIODS['evaluation'][0]<=d['session']<=PERIODS['evaluation'][1]],3)
                chunkpositive=sum(np.prod([1+d['return_fraction'] for d in chunk])-1>0 for chunk in chunks)
                selected_extra=[x for x in extra if x['strategy']==cfg.name and x.get('period','evaluation')=='evaluation' and x['scenario'] in ('one_bar_latency','quarter_participation')]
                statpass=all(m['total_return']>0 and (m['mean_net_bps_per_trade'] or 0)>0 and (m['profit_factor'] or 0)>=1.1 for m in (val,ev)) and ev['trades']>=75 and ev['active_days']>=50 and ev['max_drawdown']>=-.15 and (ev['worst_day'] or 0)>=-.02 and (ev['top5_profit_concentration'] or 1)<=.5 and chunkpositive>=2 and st.get('total_return',-1)>0 and bootstrap[cfg.name].get('familywise_lower',-1)>0 and len(selected_extra)==2 and all(x.get('total_return',-1)>0 for x in selected_extra)
                status='FORWARD_DATA_REQUIRED' if statpass else 'INCONCLUSIVE'
                reasons=['Statistical gate '+('passed' if statpass else 'not passed')+'; historical execution eligibility and calibrated spread/depth still unavailable']
        decisions.append(dict(strategy=cfg.name,status=status,statistical_gate=statpass,reasons=reasons))
    decisions.append(dict(strategy='H3-order-book-increment',status='FORWARD_DATA_REQUIRED',reasons=['No post-freeze forward live depth sample; no historical reconstruction']))
    report=dict(manifest=manifest,selection=selection,metrics=metrics,stress=stress,additional_selected_stress=extra,bootstrap=bootstrap,
        decisions=decisions,failed=failed,resolution_audit=resolution,qualified=[],fresh_forward_observations=0,
        conclusion='NO STRATEGY QUALIFIED',limits=['All dates research-exposed; no fresh out-of-sample evidence','Fixed liquid100 cohort; no all-NSE inference','Candle fills/partial fills and MIS/circuits unverified','All-in friction scenarios not live-calibrated; no separate spread double count','Peer proxy uses dated industry labels, not a historical sector index','Complete-session coverage is conditional; short special sessions excluded','Conditional bootstrap does not undo prior research exposure'])
    if hashes()!=frozen:raise RuntimeError('Frozen research code changed during run')
    base.dump(OUT/'report.json',native(report));write_csv(OUT/'metrics.csv',metrics);write_csv(OUT/'stress.csv',stress);write_csv(OUT/'capacity-and-latency.csv',extra)
    write_csv(OUT/'trades.csv',[t for r in results.values() for t in r['trades']]);write_csv(OUT/'rejections.csv',[t for r in results.values() for t in r['rejections']]);write_csv(OUT/'daily-equity.csv',[dict(strategy=r['name'],**d) for r in results.values() for d in r['daily']]);write_csv(OUT/'segments.csv',segments(results))
    render(report,results)
    print('COMPLETE:',report['conclusion'],flush=True)


def render(report,results):
    lines=['# V2 retrospective backtest','',report['conclusion'],'',
        'Only2025–2026performance. Fixed pre2025liquid100cohort; ₹10lakh, noleverage, max3sharedentries/day. Baseline10bps/side ALL-IN friction plus fees; not calibrated live execution. All dates previously research-exposed.',
        '',f"Development-selected: {report['selection']['selected']}. Fresh forward observations:0.",'',
        '| Strategy | Dev return | Val return | Eval return | Full trades | Full return | PF | Net bps | EOD DD | Eval25bps |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    rows=sorted([m for m in report['metrics'] if m['period']=='full' and m['category']=='primary'],key=lambda m:-m['total_return'])
    for f in rows:
        name=f['strategy'];dev=next(m for m in report['metrics'] if m['strategy']==name and m['period']=='development');val=next(m for m in report['metrics'] if m['strategy']==name and m['period']=='validation');ev=next(m for m in report['metrics'] if m['strategy']==name and m['period']=='evaluation');st=next((m for m in report['stress'] if m['strategy']==name and m['period']=='evaluation' and m['scenario']=='25bps_side'),{})
        pf='NA' if f['profit_factor'] is None else f"{f['profit_factor']:.2f}";bp='NA' if f['mean_net_bps_per_trade'] is None else f"{f['mean_net_bps_per_trade']:.2f}"
        lines.append(f"| {name} | {dev['total_return']:.2%} | {val['total_return']:.2%} | {ev['total_return']:.2%} | {f['trades']} | {f['total_return']:.2%} | {pf} | {bp} | {abs(f['max_drawdown']):.2%} | {st.get('total_return',float('nan')):.2%} |")
    lines+=['','## Limits','']+['- '+x for x in report['limits']]
    lines+=['','## Resolution audit','',json.dumps({k:v for k,v in report['resolution_audit'].items() if k!='rows'},indent=2),
            '', 'Full primary/control/short diagnostics and segments are in metrics.csv/segments.csv; signals/rejections/trades preserve chronology. Failed runs: '+json.dumps(report['failed'])]
    (OUT/'BACKTEST_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    decision=['# Final decision','',report['conclusion'],'','No execution bot or forward simulated trader created. A recorder is not a strategy validation.','',
        '| Rule | Classification | Reason |','|---|---|---|']
    decision += [f"| {d['strategy']} | {d['status']} | {'; '.join(d['reasons'])} |" for d in report['decisions']]
    (OUT/'FINAL_DECISION.md').write_text('\n'.join(decision)+'\n',encoding='utf-8')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(12,7),layout='constrained')
    for f in rows:
        r=results[f['strategy']];ax.plot(pd.to_datetime([d['session'] for d in r['daily']]),[d['equity']/1e5 for d in r['daily']],label=r['name'])
    for day in ('2025-10-01','2026-04-01'):ax.axvline(pd.Timestamp(day),ls='--',color='black',alpha=.4)
    ax.set(title='V2 primary portfolios — exposed retrospective data, modeled costs',ylabel='Cash equity (₹ lakh)');ax.grid(alpha=.2);ax.legend(fontsize=7,ncol=3);fig.savefig(OUT/'equity.png',dpi=150);plt.close(fig)


if __name__=='__main__':main()
