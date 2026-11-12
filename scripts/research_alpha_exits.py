"""Predeclared exit/stop sensitivity on exact recent option candles; no tuning."""
from collections import Counter
from dataclasses import asdict
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import research_directional_lab as lab
from alpha_event_engine import candle_replay,policies,stamp

OLD=ROOT/'artifacts'/'directional_research'
PHASE2=ROOT/'artifacts'/'directional_research_phase2'
OUT=ROOT/'artifacts'/'project_alpha'
PRIORITY={'ema_trend':0,'donchian':1,'pullback':2}


def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8')


def bootstrap(rows):
    # Only five sessions. This interval is descriptive, not a promotion gate.
    sessions=['2026-11-02','2026-11-03','2026-11-04','2026-11-05','2026-11-06']
    if not rows:return [None,None]
    counts=np.array([sum(r['session']==day for r in rows) for day in sessions])
    pnl=np.array([sum(r['illustrative_net_rupees_per_lot'] for r in rows if r['session']==day) for day in sessions])
    rng=np.random.default_rng(20261109);indices=rng.integers(0,5,(3000,5));den=counts[indices].sum(axis=1);valid=den>0
    return np.quantile(pnl[indices].sum(axis=1)[valid]/den[valid],[.025,.975]).tolist()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    selection=json.loads((PHASE2/'option-intraday-selection-frozen.json').read_text())
    specs=policies();input_paths=[PHASE2/'option-intraday-selection-frozen.json',OLD/'nifty-upstox-5minute.json',Path(__file__),ROOT/'scripts'/'alpha_event_engine.py',ROOT/'scripts'/'test_alpha_event_engine.py']
    input_paths+=sorted((PHASE2/'option-intraday-candles').glob('*.json'))
    save('exit-preregister.json',{'experiment_id':'ALPHA-EXIT-001','status':'RESEARCH_ONLY','source_window':['2026-11-02','2026-11-06'],
        'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths},
        'exit_policies':[asdict(p) for p in specs],'contract_policies':['nearest_nonexpiry_day/ATM','nearest_nonexpiry_day/one_step_ITM','month_end_proxy/ATM','month_end_proxy/one_step_ITM'],
        'router':'One position globally per configuration. EMA then Donchian then pullback if simultaneous. Choose priority signal before checking future premium coverage; no fallback after observing an unavailable selected outcome.',
        'bounds':['adverse_first','favorable_first'],'selection':'All48 fixed exit/contract configurations and both path modes disclosed; no winner selected.',
        'entry':'Frozen next-five-minute option candle open; option first-trade time is unknown.',
        'stop_semantics':'Premium stop resting threshold proxy; gaps exit at open below stop. Underlying ATR/structure stop confirmed at trigger-bar close and translated to following option open. Missing/future unavailable prices leave position unresolved/reserved until session cutoff.',
        'trailing':'Stop raises only after prior option candle close; current candle high never moves its own stop.',
        'costs':'Dated saleSTT. Illustrative2premiumpts+INR100 and severe5pts+INR200 perroundtrip; not complete actual fee/spread reconstruction.',
        'mae_mfe':'Whole holding/exit-candle extrema are excursion bounds, not exact tick excursions after an intrabar exit.',
        'quotes':'Verified source-book quote mode separately tested with syntheticfixtures; actual premium history lacks verified depth/ticks.',
        'limitations':'Only5already-inspected sessions, repeated correlatedpolicies, historical-selection exposure. No execution-quality backtest or statistical edge claim.'})
    nifty,audit=lab.load_data();features=lab.features(nifty)
    under={r['ts'].to_pydatetime():r for r in features[['ts','open','high','low','close']].to_dict('records')}
    signal_context={}
    for _,group in features.groupby('day'):
        for i,r in enumerate(group.to_dict('records')):
            prior=group.iloc[max(0,i-2):i+1]
            signal_context[(r['ts']+pd.Timedelta(minutes=5)).to_pydatetime()]={'signal_atr':float(r['atr']),'signal_spot':float(r['close']),
                'structure_long':float(prior.low.min()),'structure_short':float(prior.high.max())}
    candles={}
    for path in sorted((PHASE2/'option-intraday-candles').glob('*.json')):
        raw=json.loads(path.read_text())['candles'];table={}
        for r in raw:
            at=stamp(r[0]);assert at not in table,'Duplicate option bar'
            table[at]=dict(zip(['open','high','low','close','volume','oi'],r[1:]))
        candles['NSE_FO|'+path.stem]=table
    ledgers=[];events=[];summaries=[];checks=0
    buckets=sorted({(r['expiry_bucket'],r['strike_rule']) for r in selection})
    for bucket,strike in buckets:
        chosen=[r for r in selection if r['expiry_bucket']==bucket and r['strike_rule']==strike]
        chosen.sort(key=lambda r:(stamp(r['entry_at']),PRIORITY[r['strategy'].split('|')[0]],r['strategy']))
        for policy in specs:
            configuration=f'{bucket}|{strike}|{policy.name}'
            for bound in ['adverse_first','favorable_first']:
                busy_until=None;last_signal=None;accepted=[];statuses=Counter()
                for ordinal,row in enumerate(chosen):
                    entry=stamp(row['entry_at']);sid=f"{row['strategy']}|{row['entry_at']}"
                    base={'configuration':configuration,'expiry_bucket':bucket,'strike_rule':strike,'exit_policy':policy.name,'ambiguity_mode':bound,
                          'signal_id':sid,'source_strategy':row['strategy'],'session':row['session'],'entry_at':entry.isoformat(),'direction':int(row['direction']),
                          'instrument_key':row['instrument_key'],'token':row['token'],'expiry':row['expiry'],'strike':row['strike'],'option_type':row['option_type'],'lot':int(row['lot'])}
                    if last_signal==entry:result={'status':'rejected_higher_priority_signal'}
                    else:
                        last_signal=entry
                        if busy_until is not None and entry<busy_until:result={'status':'rejected_existing_position'}
                        elif row['status']!='selected':result={'status':'rejected_'+row['status']}
                        else:
                            context=signal_context.get(entry)
                            if context is None:result={'status':'unsupported_signal_context'}
                            else:
                                trade={**row,**context,'signal_structure_stop':context['structure_long'] if int(row['direction'])==1 else context['structure_short']}
                                result=candle_replay(trade,candles.get(row['instrument_key'],{}),under,policy,bound)
                    result_events=result.pop('events',[])
                    record={**base,**result};statuses[record['status']]+=1
                    for event in result_events:events.append({'configuration':configuration,'ambiguity_mode':bound,'signal_id':sid,**event})
                    if record['status']=='observed_candle_proxy':
                        exit_at=stamp(record['exit_at']);busy_until=exit_at
                        assert exit_at.date()==entry.date() and exit_at.astimezone(entry.tzinfo).hour*60+exit_at.astimezone(entry.tzinfo).minute<=910;checks+=1
                        assert abs(record['gross_rupees_per_lot']-(record['premium_exit']-record['premium_entry'])*record['lot'])<1e-8;checks+=1
                        assert record['holding_minutes']<=policy.hold_minutes and record['holding_minutes']>=0;checks+=1
                        assert int(record['lot'])==int(row['lot']) and row['universe_date']<row['session']<row['expiry'];checks+=1
                        record['premium_capital_rupees']=record['premium_entry']*record['lot']
                        record['planned_stop_loss_rupees']=record['premium_entry']*policy.premium_stop*record['lot'] if policy.premium_stop else None
                        record['planned_stop_is_loss_guarantee']=False
                        accepted.append(record)
                    elif result.get('unresolved_position'):busy_until=stamp(result['reserved_until'])
                    ledgers.append(record)
                mean=lambda key:float(np.mean([r[key] for r in accepted])) if accepted else None
                summaries.append({'configuration':configuration,'expiry_bucket':bucket,'strike_rule':strike,'exit_policy':policy.name,'ambiguity_mode':bound,
                    'potential_signals':len(chosen),'observed_trades':len(accepted),'sessions_with_trade':len(set(r['session'] for r in accepted)),
                    'gross_mean_rupees_per_lot':mean('gross_rupees_per_lot'),'illustrative_net_mean_rupees_per_lot':mean('illustrative_net_rupees_per_lot'),
                    'severe_net_mean_rupees_per_lot':mean('severe_net_rupees_per_lot'),'holding_mean_minutes':mean('holding_minutes'),
                    'mae_mean_bound_rupees':mean('mae_candle_bound_rupees'),'mfe_mean_bound_rupees':mean('mfe_candle_bound_rupees'),
                    'ambiguous_trades':sum(r['ambiguity_count']>0 for r in accepted),'cutoff_truncated_trades':sum(r['cutoff_truncated'] for r in accepted),
                    'status_counts':dict(statuses),'net_descriptive_ci95':bootstrap(accepted),'decision':'RESEARCH_ONLY'})
    df=pd.DataFrame(ledgers);df.to_csv(OUT/'exit-trades.csv',index=False)
    pd.DataFrame(events).to_csv(OUT/'exit-events.csv',index=False)
    pd.DataFrame([{k:v for k,v in r.items() if k!='status_counts'} for r in summaries]).to_csv(OUT/'exit-summary.csv',index=False)
    save('exit-summary.json',{'configurations':len(specs)*len(buckets),'path_modes':2,'summaries':summaries,'trade_assertions_passed':checks,
        'source_signal_count':17,'source_policy_attempts':68,'underlying_input_audit':audit,'quote_execution_history_supported':False,'no_winner_selected':True})
    # Independent persisted portfolio chronology: no overlap, bounded session, all outcomes retained.
    for _,g in df[df.status=='observed_candle_proxy'].groupby(['configuration','ambiguity_mode']):
        g=g.sort_values('entry_at');entry=pd.to_datetime(g.entry_at,utc=True);exit=pd.to_datetime(g.exit_at,utc=True)
        assert (entry.iloc[1:].reset_index(drop=True)>=exit.iloc[:-1].reset_index(drop=True)).all();checks+=1
    save('exit-verification.json',{'trade_assertions_passed':checks,'configurations':len(specs)*len(buckets),'policy_outcome_rows':len(df),
        'observed_proxy_rows':int((df.status=='observed_candle_proxy').sum()),'synthetic_regression_command':'.venv/Scripts/python.exe scripts/test_alpha_event_engine.py',
        'source_hashes':json.loads((OUT/'exit-preregister.json').read_text())['input_sha256']})
    lines=['# Project Alpha: event engine and exit research','',
        'The engine adds deterministic entry/exit events, conservative stop translation, unknown-price states and single-position routing. All48 predefined exit/contract configurations and both intrabar path bounds are disclosed. No configuration was selected using these results.',
        '', 'The actual option sample contains only17 underlying signals across five already-inspected sessions, repeated across contract and exit policies. The test is a descriptive engineering/exit sensitivity panel, not an independent strategy discovery or an execution-quality backtest.',
        '', '## Rules and execution boundaries',
        '- Entry is the exact next option candle open for the frozen underlying signal. The option first-trade time within that candle is unknown.',
        '- A single router prioritizes EMA, Donchian, then pullback. It holds at most one position per tested configuration; same-time lower-priority signals and later overlapping signals are logged as rejections.',
        '- Premium stops20/30%, fixed1R/2R targets, trailing20%, underlying1/1.5ATR and prior-three-bar structure invalidation, and30/60/120-minute exits are tested in a small fixed slate. All trades close by15:10;120-minute holds can be cut short.',
        '- Premium gaps exit at the worse observed open. A stop price does not guarantee the loss. If stop and target occur in one candle, adverse-first and favorable-first outcomes bound the path assumption; neither is asserted executable.',
        '- Trailing stops update only after the preceding candle close. Underlying threshold touches become known at bar close and translate into the following option open; the option exit can gap substantially.',
        '- Missing/invalid/zero-volume bars after entry leave the position unresolved and reserve capacity until session cutoff. No stale or fabricated exit is added. Full-day/future candle volume is an ex-post evidence check, not an entry-time liquidity oracle.',
        '- MAE/MFE use full exit-bar extrema and are labeled candle bounds. They may include movements after a modeled intrabar exit and cannot identify exact entry/exit efficiency.',
        '- Both net scenarios include dated sale STT plus the same illustrative non-STT fee/execution allowances used in phase2:2premiumpoints+INR100 or5points+INR200. These are not actual historical bid/ask costs. [NSE STT circular](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf).',
        '', '## All adverse-first results', '|Expiry|Strike|Exit policy|N|Mean gross INR|Mean illustrative net INR|Mean severe net INR|Ambiguous trades|Unresolved|', '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for r in summaries:
        if r['ambiguity_mode']!='adverse_first':continue
        n=r['observed_trades'];fmt=lambda value:f'{value:.2f}' if value is not None else 'NA'
        unresolved=sum(v for k,v in r['status_counts'].items() if k.startswith('unsupported_'))
        lines.append(f"|{r['expiry_bucket']}|{r['strike_rule']}|{r['exit_policy']}|{n}|{fmt(r['gross_mean_rupees_per_lot'])}|{fmt(r['illustrative_net_mean_rupees_per_lot'])}|{fmt(r['severe_net_mean_rupees_per_lot'])}|{r['ambiguous_trades']}|{unresolved}|")
    lines+=['', 'The favorable-first ledger and paired path outcomes remain available for every configuration. Five sessions cannot support stop/target optimization, tail-risk estimation or a promotion gate. No exit is declared best, and differences are not adjusted for all prior strategy research.',
        '', '## Quote mode and unsupported history',
        'alpha_event_engine.quote_fill requires verified source-book and received timestamps, healthy market state, noncrossed depth, a marketable limit, whole-lot depth, latency and deadline checks. Missing fills remain missed; permitted partial fills report both filled and cancelled quantities, without assuming replenishment. quote_exit evaluates observed bid triggers, then applies latency to a later eligible book. A gap below a stop exits at the observed worse bid; no valid later quote leaves the position unresolved.',
        '', 'Fourteen synthetic regression fixtures test ambiguous paths, stop gaps, delayed underlying invalidation, causal trailing, unavailable bars, session truncation, latency/limits, depth/partial accounting, invalid/stale/future books, strict-versus-frame snapshot evidence, predecision limits, missing exit quotes and cutoff timing. Fixtures are not market trades. Actual captured historical quote/depth coverage is audited separately and replayed in exit-stream-report.md with explicit timestamp-quality limitations.',
        '', f'Verification: {checks} trade/source/portfolio assertions passed. The ledger contains every source-policy decision, including rejections and unsupported outcomes. exit-preregister.json freezes policy definitions and source hashes; exit-events.csv gives timestamped events; exit-trades.csv contains exact contract and price/cost evidence.']
    (OUT/'exit-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'configurations':len(specs)*len(buckets),'path_modes':2,'outcome_rows':len(df),'observed_proxy_rows':int((df.status=='observed_candle_proxy').sum()),'checks':checks}))


if __name__=='__main__':main()
