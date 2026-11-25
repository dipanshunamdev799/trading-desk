"""Run the frozen cash-stock intraday experiment, never an application bot."""
from dataclasses import replace
from datetime import datetime
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.intraday_momentum.data import OUT,load_sessions,sha,dump
from research.intraday_momentum.signals import make_signals
from research.intraday_momentum.engine import catalog,run,summarize,block_bootstrap

PERIODS={'development':('2024-11-14','2025-08-31'),'validation':('2025-09-01','2026-02-28'),
         'final':('2026-03-01','2026-11-13'),'full':('2024-11-14','2026-11-13'),
         'last_year':('2025-11-14','2026-11-13')}


def native(x):
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,(pd.Timestamp,datetime)):return x.isoformat()
    if isinstance(x,dict):return {k:native(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [native(v) for v in x]
    return x


def write_csv(path,rows):
    rows=native(rows)
    for row in rows:
        for key,v in row.items():
            if isinstance(v,(dict,list)):row[key]=json.dumps(v,sort_keys=True)
    pd.DataFrame(rows).to_csv(path,index=False)


def stable_fingerprint(value):
    """Ignore clock-only metadata; code, inputs and numeric results stay frozen."""
    clean={k:v for k,v in native(value).items() if k not in ('generated_at','study_fingerprint')}
    return hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def freeze_json(path,value):
    """Allow identical replay, never silently replace a different frozen study."""
    path=Path(path);value=native(value)
    if path.exists():
        old=json.loads(path.read_text(encoding='utf-8'))
        if stable_fingerprint(old)!=stable_fingerprint(value):
            raise RuntimeError('Refusing to overwrite changed frozen artifact '+str(path)+
                '; use a new versioned study directory with its frozen input manifests')
        # Preserve the original timestamp and exact file bytes: the selection
        # manifest contains the hash of this file, not just its stable payload.
        return old
    dump(path,value)
    return value


def passes_paper_gate(final,stress,uncertainty):
    """A positive average-sized trade cannot excuse a losing funded stress run."""
    return bool(final['trades']>=50 and final['active_days']>=30 and
        (final['mean_net_bps_per_trade'] or 0)>0 and
        (final.get('total_return') or 0)>0 and
        (stress.get('mean_net_bps_per_trade') or 0)>0 and
        (stress.get('total_return') or 0)>0 and
        uncertainty.get('total_return_ci95',[0])[0]>0)


def validate_acquisition(plan,acquisition,plan_sha):
    if acquisition.get('plan_sha256')!=plan_sha:
        raise RuntimeError('Acquisition manifest belongs to a different plan')
    planned={j['id'] for j in plan['jobs']};observed=[j['id'] for j in acquisition['jobs']]
    if len(observed)!=len(set(observed)) or set(observed)!=planned:
        raise RuntimeError('Acquisition job set is incomplete, duplicated or differs from plan')
    failures=[x for x in acquisition['jobs'] if x['status']!='ok']
    if failures:raise RuntimeError(f'{len(failures)} acquisition jobs still incomplete; retry before strategy returns')


def resolution_markdown(audit):
    lines=['','## Fixed-entry one-minute audit','']
    chosen=audit.get('chosen',0);matched=audit.get('matched',0)
    if not chosen:
        return lines+['No development-selected trades were available for the fixed chronological audit.']
    statuses=Counter(r.get('status','unknown') for r in audit.get('rows',[]))
    lines.append(f'The first {chosen} chronological development trades of the already-selected rule were chosen; '
                 f'**{matched}/{chosen}** have matched one-minute source paths. Statuses: '+
                 ', '.join(f'{k}={v}' for k,v in sorted(statuses.items()))+'.')
    differences=[r['net_pnl_difference'] for r in audit.get('rows',[])
                 if r.get('status')=='matched' and r.get('net_pnl_difference') is not None]
    if differences:
        lines+=['',f'For those fixed entries and quantities, summed one-minute minus five-minute net P&L is '
                    f'₹{sum(differences):,.2f}. This is an exit-resolution diagnostic, not a one-minute portfolio return.']
    lines+=['','Different exits can change subsequent entries. Unmatched or missing source paths are disclosed, '
            'not treated as agreement. This audit does not certify spreads, depth, queue position or actual fills.']
    return lines


def extension_markdown(summary):
    lines=['','## Descriptive 8→10 / 10→12 extension events','',
        'First completed morning qualification per stock-day/threshold/direction with RVOL≥1.5, including gappers. '
        'The race starts at the raw next open: extension is two percentage points of daily return from the prior close; '
        'the competing reversal is 1% against that entry. These are price paths, not trade returns.']
    groups=summary.get('groups',[])
    if not groups:
        return lines+['','No qualifying event groups are available; no extension probability is inferred.']
    lines+=['','| Daily-return step | Direction | Horizon | Qualified | Races | Extension first | Reversal first | Neither | Excluded: overshot / missing / censored | Ambiguous |',
            '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    def outcome(group,key):
        rate=group.get(key.replace('_first','')+'_rate')
        return str(group.get(key,0))+(' (—)' if rate is None else f' ({rate:.1%})')
    for g in groups:
        sign=-1 if g['direction']=='down' else 1
        step=f"{sign*g['threshold']*100:.0f}%→{sign*g['extension_daily_return']*100:.0f}%"
        excluded=f"{g.get('already_at_extension',0)} / {g.get('missing_next_open',0)} / {g.get('censored',0)}"
        lines.append(f"| {step} | {g['direction']} | {g['horizon']} | {g['qualifications']} | {g['race_count']} | "
            f"{outcome(g,'extension_first')} | {outcome(g,'reversal_first')} | {outcome(g,'neither')} | {excluded} | {g.get('ambiguous_count',0)} |")
    lines+=['','Rates use observed race outcomes only. An entry already at/beyond the extension level is excluded, '
        'along with missing entries and censored paths; qualifying-price overshoot flags remain in the event CSV/JSON. '
        'Ambiguous first-touch candles count reversal first. Thresholds, horizons and stocks from the same session '
        'are dependent observations. Rates are conditional on the acquired cohort. Chronological split summaries are in report.json.']
    return lines


def code_hashes():
    names=['data.py','engine.py','signals.py','costs.py','events.py','units.py','resolution.py','PROTOCOL.md','SOURCES.md']
    return {name:sha(ROOT/'research/intraday_momentum'/name) for name in names}


def partition(records,signals,calendar,first,last):
    return ([r for r in records if first<=r['day']<=last],
            [s for s in signals if first<=pd.Timestamp(s['known_at']).date().isoformat()<=last],
            [d for d in calendar if first<=d<=last])


def fingerprints(records):
    h=hashlib.sha256()
    for r in sorted(records,key=lambda r:(r['day'],r['key'])):
        h.update(json.dumps({k:r[k] for k in ('day','key','prev_close','adv')},sort_keys=True).encode())
        h.update(np.ascontiguousarray(r['bars'].to_numpy(float)).tobytes())
        h.update(np.ascontiguousarray(r['rvol'].to_numpy(float)).tobytes())
    return h.hexdigest()


def main(out=OUT):
    out=Path(out);plan=json.loads((out/'jobs-plan.json').read_text())
    acquisition=json.loads((out/'acquisition-manifest.json').read_text())
    validate_acquisition(plan,acquisition,sha(out/'jobs-plan.json'))
    frozen=code_hashes();records=load_sessions(plan,out)
    calendar=[d for d in plan['calendar'] if plan['start']<=d<=plan['end']]
    signals=[]
    for i,r in enumerate(records):
        for s in make_signals(r['bars'],r['prev_close'],r['rvol']):signals.append(dict(**s,key=r['key'],symbol=r['symbol']))
        if i%500==0:print(f'Signals: {i}/{len(records)} complete candidate sessions.',flush=True)
    manifest=dict(protocol='intraday-stock-momentum-v1',plan_sha256=sha(out/'jobs-plan.json'),
        acquisition_sha256=sha(out/'acquisition-manifest.json'),code=frozen,runner_sha256=sha(Path(__file__)),
        data_sha256=fingerprints(records),candidate_sessions=len(records),signals=len(signals),
        calendar_sessions=len(calendar),periods=PERIODS,generated_at=datetime.now().astimezone().isoformat(),
        environment=dict(python=sys.version.split()[0],numpy=np.__version__,pandas=pd.__version__),
        storage='Primary Upstox prices read from PostgreSQL; all experiment outputs local',real_orders_submitted=0)
    manifest['study_fingerprint']=stable_fingerprint(manifest)
    manifest=freeze_json(out/'research-manifest.json',manifest)
    # Selection is written before any validation or final portfolio is evaluated.
    dev_records,dev_signals,dev_cal=partition(records,signals,calendar,*PERIODS['development'])
    dev=[];dev_runs={};failed=[]
    for cfg in catalog():
        try:
            result=run(dev_records,dev_signals,dev_cal,cfg);m=summarize(result)
            dev.append(dict(strategy=cfg.name,**m));dev_runs[cfg.name]=result
        except ValueError as exc:failed.append(dict(strategy=cfg.name,stage='development',reason=str(exc)))
    eligible=[m for m in dev if m['trades']>=50 and (m['mean_net_bps_per_trade'] or 0)>0 and not m['strategy'].startswith('exhaustion8')]
    eligible.sort(key=lambda m:(-m['mean_net_bps_per_trade'],-m['max_drawdown'],m['strategy']))
    selected=eligible[0]['strategy'] if eligible else None
    selection=dict(selected=selected,criterion='Positive mean development net bps per trade, >=50 closed development trades; highest mean bps, then smaller end-of-day drawdown, then ID; exhaustion excluded',
        development_only=True,development_rows=dev,failed=failed,manifest_sha256=sha(out/'research-manifest.json'))
    selection=freeze_json(out/'development-selection-frozen.json',selection)
    print('Development selection frozen:',selected,flush=True)
    if selected:
        from research.intraday_momentum.resolution import audit
        resolution=audit(dev_runs[selected]['trades'],records,out)
    else:resolution=dict(status='NO_DEVELOPMENT_CANDIDATE',chosen=0,matched=0)
    all_results={};rows=[];all_trades=[];daily=[];stress_rows=[];selected_result=None
    for short in (False,True):
        for original in catalog():
            cfg=replace(original,allow_short=short)
            print('Portfolio',cfg.name,flush=True)
            try:result=run(records,signals,calendar,cfg)
            except ValueError as exc:
                failed.append(dict(strategy=cfg.name,stage='full',reason=str(exc)));continue
            if not short and cfg.name in dev_runs:
                before=dev_runs[cfg.name]['trades'];prefix=[t for t in result['trades'] if t['session']<=PERIODS['development'][1]]
                if before!=prefix:raise AssertionError('Future calendar changes development trades: '+cfg.name)
            all_results[cfg.name]=result
            category='diagnostic_unverified_short_eligibility' if short else ('diagnostic_exhaustion' if cfg.mechanism=='exhaustion8' else 'primary_long_only')
            for period,(first,last) in PERIODS.items():rows.append(dict(strategy=cfg.name,category=category,period=period,**summarize(result,first,last)))
            all_trades.extend(result['trades']);daily.extend(dict(strategy=cfg.name,**d) for d in result['daily'])
            err=sum(t['net_pnl'] for t in result['trades'])-(result['daily'][-1]['equity']-cfg.capital)
            if abs(err)>.001:raise AssertionError('Cashflow reconciliation '+cfg.name)
            if any(d['trades']>3 for d in result['daily']):raise AssertionError('Daily cap')
            if not short:
                try:
                    stressed=run(records,signals,calendar,replace(cfg,slippage_bps=25))
                    for period,(first,last) in PERIODS.items():stress_rows.append(dict(strategy=cfg.name,slippage_bps=25,period=period,**summarize(stressed,first,last)))
                except ValueError as exc:
                    failed.append(dict(strategy=cfg.name,stage='stress25',reason=str(exc)))
                    for period in PERIODS:stress_rows.append(dict(strategy=cfg.name,slippage_bps=25,period=period,
                        status='FAILED_EXECUTION_INPUT',total_return=None,mean_net_bps_per_trade=None))
            if cfg.name==selected:selected_result=result
    uncertainty=None;extra_stress=[];paper_candidate=False;assessment=[]
    if selected_result:
        cfg=next(c for c in catalog() if c.name==selected)
        final=summarize(selected_result,*PERIODS['final'])
        uncertainty=block_bootstrap(selected_result,*PERIODS['final'])
        stress=next(m for m in stress_rows if m['strategy']==selected and m['period']=='final')
        for label,changed in [('zero_slippage_diagnostic',replace(cfg,slippage_bps=0)),
                              ('one_bar_latency',replace(cfg,entry_delay_bars=1)),
                              ('quarter_participation',replace(cfg,participation=.0025))]:
            try:
                r=run(records,signals,calendar,changed)
                extra_stress.append(dict(scenario=label,**summarize(r,*PERIODS['final'])))
            except ValueError as exc:extra_stress.append(dict(scenario=label,status='FAILED_EXECUTION_INPUT',reason=str(exc)))
        paper_candidate=passes_paper_gate(final,stress,uncertainty)
        if final['trades']<50:assessment.append('Fewer than 50 final closed trades')
        if final['active_days']<30:assessment.append('Fewer than 30 final traded sessions')
        if (final['mean_net_bps_per_trade'] or 0)<=0:assessment.append('Final mean net expectancy not positive')
        if (final.get('total_return') or 0)<=0:assessment.append('Funded final return is not positive')
        if (stress['mean_net_bps_per_trade'] or 0)<=0:assessment.append('Does not survive 25bps/side stress')
        if (stress.get('total_return') or 0)<=0:assessment.append('Funded final return is not positive under 25bps/side stress')
        if uncertainty.get('total_return_ci95',[0])[0]<=0:assessment.append('20-session-block final-return uncertainty includes zero or worse')
    elif selected:assessment.append('The development-selected model has unresolved full-window execution inputs; no final performance claimed')
    else:assessment.append('No primary model met the preregistered development-only eligibility rule')
    report=dict(manifest=manifest,selection=selection,summary=rows,stress=stress_rows,failed=failed,resolution_audit=resolution,
        final_uncertainty=uncertainty,additional_selected_stress=extra_stress,
        paper_candidate=paper_candidate,assessment=assessment,
        registered_control=dict(name='cross4_control',status='NOT_TESTED_DATA_COVERAGE',reason='An 8% daily-extreme acquisition superset cannot test a 4% control without look-ahead conditioning'),
        limitations=['Dated October2024 fund-holdings cohort is a fixed cohort proxy, not all Indian stocks or a reconstituted historical index',
          'Unavailable historical members, missing regular sessions and insufficient RVOL remain explicit in the source/load audits; complete-case prices do not establish universal availability',
          'Candle OHLCV cannot reconstruct active orders, historical spread/depth, queue priority, circuits, or broker intraday eligibility',
          'Short portfolios are diagnostic; historical short-sale eligibility and forced-close/auction costs are unverified',
          'Current basic-plan brokerage and tax estimates are modeled historically; 10/25bps slippage is an assumption',
          'Known capital-action/dividend exdates excluded; the NSE action calendar was extended through 13 November 2026, but source histories are not certified exhaustively',
          'Split/bonus price and volume units are restored locally; original Upstox PostgreSQL candles remain unchanged. The unit audit covers 57 event dates across 56 companies; 41 companies require restoration during the study. It includes 112 company-day checks against three NSE bhavcopies; maximum sampled price residual is 5.89bp and volume residual 1.99bp. This limited certification does not validate every bar or historical action',
          'Five-minute same-bar stop/target ambiguity uses stop-first; exit liquidity and within-bar gaps remain uncertain',
          'Future entry-bar flatness is not an admission filter; historical circuits, opening queue priority and available executable depth remain unverified',
          'Drawdown uses end-of-day cash equity; transient intraday path drawdown can be worse',
          'Calendar appeared in earlier research: held-out results are pseudo-out-of-sample, not a new live forward track record',
          'No leverage in primary results; scaling capital or leverage does not establish an edge'],
        verification=dict(synthetic_tests='See tests/test_intraday_momentum*.py',real_orders_submitted=0))
    try:
        from research.intraday_momentum.events import make_events,summarize_events
        events=make_events(records);report['extension_events']=summarize_events(events)
        report['extension_events_by_period']={k:summarize_events([e for e in events if first<=e['day']<=last]) for k,(first,last) in PERIODS.items()}
        write_csv(out/'extension-events.csv',events)
    except ImportError:report['extension_events']={'status':'NOT_IMPLEMENTED'}
    if code_hashes()!=frozen or sha(Path(__file__))!=manifest['runner_sha256']:
        raise AssertionError('Research code/protocol/runner changed during run')
    dump(out/'report.json',native(report));write_csv(out/'summary.csv',rows);write_csv(out/'stress.csv',stress_rows)
    write_csv(out/'trades.csv',all_trades);write_csv(out/'daily-equity.csv',daily)
    write_report(out,report,all_results)
    print('Study complete. Selected:',selected,'Paper-candidate gate:',paper_candidate,flush=True)
    return report


def write_report(out,report,results):
    selection=report['selection']['selected']
    lines=['# Morning stock momentum research','',
        '**Research only. No intraday bot was created or started.**','',
        'Study: 14 November 2024–13 November 2026. Dated 500-stock fund cohort; prior-only liquidity, as-of-time ≥8% movers, same-clock RVOL, VWAP and next-open entries. ₹10 lakh cash, up to three trades/day across all stocks, one position at a time.',
        '',f'Development-selected primary rule: **{selection or "none qualified"}**. Paper-candidate evidence gate: **{report["paper_candidate"]}**.',
        '', 'Selection uses positive development mean net bps/trade with ≥50 development trades; no validation/final replacement is selected.',
        '', '| Rule | Dev trades | Dev return | Validation return | Final trades | Final return | Final PF | Final net bps/trade | Final EOD drawdown | Final 25bps return |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    primary=[m for m in report['summary'] if m['period']=='development' and m['category']=='primary_long_only']
    primary.sort(key=lambda m:-(m['mean_net_bps_per_trade'] if m['mean_net_bps_per_trade'] is not None else -1e9))
    def pct(x):return '—' if x is None else f'{x:.2%}'
    for d in primary:
        name=d['strategy'];v=next(m for m in report['summary'] if m['strategy']==name and m['period']=='validation')
        f=next(m for m in report['summary'] if m['strategy']==name and m['period']=='final')
        s=next(m for m in report['stress'] if m['strategy']==name and m['period']=='final')
        pf='—' if f['profit_factor'] is None else f"{f['profit_factor']:.2f}"
        bp='—' if f['mean_net_bps_per_trade'] is None else f"{f['mean_net_bps_per_trade']:.2f}"
        lines.append(f"| {name} | {d['trades']} | {pct(d['total_return'])} | {pct(v['total_return'])} | {f['trades']} | {pct(f['total_return'])} | {pf} | {bp} | {pct(f['max_drawdown'])} | {pct(s['total_return'])} |")
    lines+=['','## Interpretation','']+['- '+x for x in report['assessment']]
    lines+=resolution_markdown(report['resolution_audit'])
    lines+=extension_markdown(report.get('extension_events',{}))
    if report['failed']:
        lines+=['','## Unresolved execution cases','', 'These runs failed explicitly rather than inventing an exit or dropping a losing trade:','',
                '```json',json.dumps(report['failed'],indent=2),'```']
    lines+=['','Baseline includes 10bps adverse slippage each side and estimated Indian intraday fees. Stress applies 25bps each side and reruns the full execution model. All 12 families/stops and short/exhaustion diagnostics are in summary.csv; these tables are ordered by development evidence.','',
        '## Data and execution limits','']+['- '+x for x in report['limitations']]
    lines+=['','## Reproduce','', '```powershell',r'.\.venv\Scripts\python.exe -m research.intraday_momentum.data plan',r'.\.venv\Scripts\python.exe -m research.intraday_momentum.data acquire',r'.\.venv\Scripts\python.exe scripts\run_intraday_momentum.py','```','',
            'Do not regenerate a frozen plan in an existing run directory. Source data/imports go only to primary Upstox candles in PostgreSQL. Protocols, source metadata, rankings, trade logs and results remain local.']
    (out/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,1,figsize=(12,8),layout='constrained',sharex=True)
    for name,result in results.items():
        if 'long_short_diagnostic' in name or name.startswith('exhaustion8'):continue
        dates=pd.to_datetime([x['session'] for x in result['daily']]);equity=np.array([x['equity'] for x in result['daily']])
        color=None;weight=2.5 if name==selection else 1.;alpha=1 if name==selection else .5
        axes[0].plot(dates,equity/1e5,label=name,lw=weight,alpha=alpha)
        axes[1].plot(dates,(equity/np.maximum.accumulate(np.r_[1e6,equity])[1:]-1)*100,lw=weight,alpha=alpha)
    axes[0].set_ylabel('Equity (₹ lakh)');axes[1].set_ylabel('End-of-day drawdown (%)')
    for ax in axes:
        ax.axvline(pd.Timestamp('2025-09-01'),color='black',ls='--',alpha=.4)
        ax.axvline(pd.Timestamp('2026-03-01'),color='black',ls='--',alpha=.4);ax.grid(alpha=.2)
    axes[0].legend(fontsize=7,ncol=2);fig.suptitle('Morning stock momentum — research cash portfolios, after modeled costs')
    fig.savefig(out/'equity-and-drawdown.png',dpi=150);plt.close(fig)


if __name__=='__main__':main()
