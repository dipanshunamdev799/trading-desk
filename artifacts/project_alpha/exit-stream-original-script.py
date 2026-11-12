"""Received historical book-snapshot replay; no broker orders or fill claims."""
from collections import Counter
from datetime import datetime,timedelta,timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from alpha_event_engine import stamp
OUT=ROOT/'artifacts'/'project_alpha'
PRIORITY={'ema_trend':0,'donchian':1,'pullback':2}
IST=timezone(timedelta(hours=5,minutes=30))
POLICIES=['ATM','one_step_ITM','one_step_OTM','abs_delta_0.4_0.6','abs_delta_0.6_0.8']
EXITS=['time60','premium20','premium30','premium20_target2R']


def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8')


def parse_quotes(rows):
    result=[]
    for q in rows:
        try:
            source=stamp(q['source_at']);received=stamp(q['received_at']);last=datetime.fromtimestamp(int(q['ltt'])/1000,timezone.utc)
            result.append({**q,'received':received,'source':source,'last_trade':last,
                'provider_last_trade_age_seconds':(source-last).total_seconds(),'source_minus_received_seconds':(source-received).total_seconds()})
        except (KeyError,ValueError,TypeError,OverflowError):continue
    return sorted(result,key=lambda q:q['received'])


def validity(q,lot,mode,depth=True):
    if mode=='verified_exchange_book' and not q.get('book_timestamp_verified'):return 'source_book_timestamp_unverified'
    if abs(q['source_minus_received_seconds'])>1:return 'cross_clock_offset_above_one_second'
    if not 0<=q['provider_last_trade_age_seconds']<=30:return 'last_trade_not_fresh_in_provider_clock'
    try:bid=float(q['bid']);ask=float(q['ask']);bq=float(q['bid_qty']);aq=float(q['ask_qty'])
    except (ValueError,TypeError,KeyError):return 'invalid_book_fields'
    if not all(math.isfinite(x) for x in [bid,ask,bq,aq]) or not 0<bid<=ask:return 'invalid_or_crossed_book'
    if depth:
        if (ask-bid)/((ask+bid)/2)>.02:return 'spread_above_two_percent'
        if min(bq,aq)<lot:return 'insufficient_one_lot_best_depth'
    elif bq<=0:return 'empty_bid_mark'
    return None


def fill(quotes,known,lot,mode,latency,wait,due,side,limit):
    earliest=known+timedelta(milliseconds=latency);deadline=min(earliest+timedelta(milliseconds=wait),due)
    rejected=Counter()
    for q in quotes:
        if q['received']<earliest:continue
        if q['received']>deadline:break
        reason=validity(q,lot,mode)
        if reason:rejected[reason]+=1;continue
        price=float(q['ask'] if side=='BUY' else q['bid'])
        if side=='BUY' and price>limit:rejected['buy_limit_not_marketable']+=1;continue
        if side=='SELL' and price<limit:rejected['sell_limit_not_marketable']+=1;continue
        return q,price,dict(rejected)
    return None,None,dict(rejected)


def replay(row,quotes,mode,exit_policy,latency,wait):
    decision=stamp(row['entry_at']);due=min(stamp(row['exit_at']),decision.astimezone(IST).replace(hour=15,minute=10,second=0,microsecond=0))
    lot=int(row['lot']);base={'entry_at':decision.isoformat(),'execution_mode':mode,'latency_ms':latency,'max_quote_wait_ms':wait,
        'exit_policy':exit_policy,'quote_execution_evidence':'received_frame_snapshot_proxy' if mode=='frame_snapshot' else 'verified_book_required',
        'events':[]}
    prior=[q for q in quotes if q['received']<=decision and not validity(q,lot,mode)]
    if not prior:return {**base,'status':'rejected_no_valid_decision_quote','unresolved_position':False}
    anchor=prior[-1]
    if (decision-anchor['received']).total_seconds()>2:return {**base,'status':'rejected_decision_quote_older_than_two_seconds','unresolved_position':False}
    limit=math.ceil(float(anchor['ask'])*1.005/.05)*.05
    entered,price,entry_rejections=fill(quotes,decision,lot,mode,latency,wait,due,'BUY',limit)
    if entered is None:return {**base,'status':'missed_entry','entry_quote_rejections':entry_rejections,'unresolved_position':False}
    at=entered['received'];dispatch=due-timedelta(milliseconds=latency+wait)
    stop=price*(.7 if exit_policy=='premium30' else .8) if exit_policy!='time60' else None
    target=price*1.4 if exit_policy=='premium20_target2R' else None
    base.update(premium_entry=price,lot=lot,entry_fill_at=at.isoformat(),entry_limit=limit,decision_ask=float(anchor['ask']),
        premium_capital_rupees=price*lot,entry_quote_rejections=entry_rejections,initial_stop_premium=stop,target_premium=target,
        planned_stop_loss_rupees=(price-stop)*lot if stop is not None else None,planned_stop_is_loss_guarantee=False)
    base['events'].append({'at':at.isoformat(),'kind':'ENTRY_ASK_SNAPSHOT_PROXY','price':price,'source_at':entered['source_at']})
    trigger=dispatch;reason='scheduled_time_dispatch';last_valid=None
    for q in quotes:
        if q['received']<at:continue
        if q['received']>=dispatch:break
        if validity(q,lot,mode,depth=False):continue
        last_valid=q;bid=float(q['bid'])
        if stop is not None and bid<=stop:trigger=q['received'];reason='premium_stop_observed_bid';break
        if target is not None and bid>=target:trigger=q['received'];reason='target_observed_bid';break
    base['events'].append({'at':trigger.isoformat(),'kind':reason,'stop_premium':stop,'target_premium':target})
    exited,closed,exit_rejections=fill(quotes,trigger,lot,mode,latency,wait,due,'SELL',.05)
    if exited is None:
        marks=[q for q in quotes if at<=q['received']<=due and not validity(q,lot,mode,depth=False)]
        last=marks[-1] if marks else None
        return {**base,'status':'unresolved_no_valid_exit_quote','unresolved_position':True,'reserved_until':due.isoformat(),
                'exit_quote_rejections':exit_rejections,'last_observed_bid':float(last['bid']) if last else None,
                'last_observed_at':last['received'].isoformat() if last else None,'full_premium_loss_stress_rupees':price*lot}
    finished=exited['received'];marks=[float(q['bid']) for q in quotes if at<=q['received']<=finished and not validity(q,lot,mode,depth=False)]
    gross=(closed-price)*lot;stt=closed*lot*(.0015 if decision.date().isoformat()>='2026-04-01' else .001)
    base['events'].append({'at':finished.isoformat(),'kind':'EXIT_BID_SNAPSHOT_PROXY','price':closed,'source_at':exited['source_at']})
    return {**base,'status':'observed_bid_ask_snapshot_proxy','unresolved_position':False,'exit_at':finished.isoformat(),
        'exit_reason':reason,'premium_exit':closed,'gross_rupees_per_lot':gross,'sale_stt_rupees_per_lot':stt,
        'illustrative_net_rupees_per_lot':gross-stt-100,'severe_net_rupees_per_lot':gross-stt-2*lot-200,
        'cost_semantics':'Bid/ask already includes quoted spread. Base addsdatedsaleSTT+INR100otherfees allowance; severe adds2pointsimpact+INR200otherfees. No doublecountedspread or fullyverifiedtotalfeeclaim.',
        'observed_bid_mae_lower_bound_rupees':max(0,price-min(marks or [closed]))*lot,
        'observed_bid_mfe_lower_bound_rupees':max(0,max(marks or [closed])-price)*lot,
        'holding_minutes':(finished-at).total_seconds()/60,'exit_quote_rejections':exit_rejections,
        'stop_gap_per_unit':max(0,stop-closed) if stop is not None and reason=='premium_stop_observed_bid' else 0,
        'exit_dispatch_seconds_before_due':(due-trigger).total_seconds(),
        'entry_source_minus_received_seconds':entered['source_minus_received_seconds'],'exit_source_minus_received_seconds':exited['source_minus_received_seconds']}


def main():
    source=OUT/'stream-selection.json';raw=json.loads(source.read_text());rows=[]
    for row in raw:
        if 'policy' in row:rows.append(row)
        else:
            for policy in POLICIES:rows.append({**row,'policy':policy})
    paths=[source,Path(__file__),ROOT/'scripts'/'alpha_event_engine.py',ROOT/'scripts'/'test_alpha_event_engine.py']+sorted(OUT.glob('stream-quotes-*.json'))
    save('exit-stream-preregister.json',{'experiment_id':'ALPHA-STREAM-EXIT-001','input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        'contract_policies':POLICIES,'exit_policies':EXITS,'latency_ms':[250,1000],'max_quote_wait_ms':[2000,5000],
        'modes':['verified_exchange_book','frame_snapshot'],'router':'EMA>Donchian>pullback,oneglobalpositionperconfiguration,no fallback after a missing selected outcome; all missing-chain signals expanded across allpolicies',
        'entry':'Mostrecentvalidpredecisionask(max2secondsold)+0.5% marketablelimit, roundedup0.05; firstvalidquotedaskafterlatencybeforedeadlineandfixedexit,onefulldatedlotbestdepth.',
        'exit':'Observedbidpremiumstop20/30%or2Rtarget; timeexit dispatch latency+waitbudget beforeoriginalexit, fillsmustoccurbydue<=15:10. Sellmarketablelimitfloor0.05; gapscanexceedplannedstop.',
        'freshness':'Chronology solelylocalreceived_at. Frame_snapshot requiresabs(source−received)<=1s asfixedclocktolerance;LTTage=providerframe_time−providerLTT in[0,30]s. Thisisnotclockcalibration.',
        'quality':'Spread<=2%,one-lotbestdepth,finitepositiveuncrossedprices; nofreshquote meansmissedentryorunresolvedopenposition. Verifiedexchangemode additionallyrequiresbook_timestamp_verifiedtrue; neverpromoteframeclocktoexchangebooktime.',
        'costs':'Actualobservedask/bidincludesquotedspread;netdeductsdatedsaleSTT+INR100otherfeeallowance,severeadds2premiumptsimpact+INR200allowance. Totalfeesandinfrastructurereliabilityremainunverified.',
        'limitations':'Smallretrospectivecapturewindow,price-stateframesnotexchangebookevents,noqueueoractualmarketimpactfills,noindependentprospectiveevidence;allpoliciesreportedandnowinnerselected.'})
    quotes={};offsets=[];provider_ages=[];strict_verified=0;source_rows=0
    for path in sorted(OUT.glob('stream-quotes-*.json')):
        parsed=parse_quotes(json.loads(path.read_text()));quotes[path.name]=parsed
        source_rows+=len(parsed);offsets.extend(q['source_minus_received_seconds'] for q in parsed);provider_ages.extend(q['provider_last_trade_age_seconds'] for q in parsed);strict_verified+=sum(bool(q.get('book_timestamp_verified')) for q in parsed)
    ledgers=[];events=[];summaries=[];checks=0
    for policy in POLICIES:
        selected=sorted([r for r in rows if r['policy']==policy],key=lambda r:(stamp(r['entry_at']),PRIORITY[r['strategy'].split('|')[0]],r['strategy']))
        for exit_policy in EXITS:
            for latency in [250,1000]:
                for wait in [2000,5000]:
                    configuration=f'{policy}|{exit_policy}|lat{latency}|wait{wait}'
                    for mode in ['verified_exchange_book','frame_snapshot']:
                        busy=None;last=None;accepted=[];statuses=Counter()
                        for row in selected:
                            entry=stamp(row['entry_at']);base={'configuration':configuration,'contract_policy':policy,'exit_policy':exit_policy,'latency_ms':latency,'max_quote_wait_ms':wait,
                                'execution_mode':mode,'source_strategy':row['strategy'],'session':row['session'],'entry_at':entry.isoformat(),'direction':row['direction'],
                                'instrument_key':row.get('instrument_key'),'lot':row.get('lot'),'expiry':row.get('expiry'),'strike':row.get('strike'),'delta':row.get('delta'),'iv':row.get('iv'),'chain_observed_at':row.get('chain_observed_at')}
                            if entry==last:result={'status':'rejected_higher_priority_signal'}
                            else:
                                last=entry
                                if busy is not None and entry<busy:result={'status':'rejected_existing_position'}
                                elif row['status']!='selected':result={'status':'rejected_'+row['status']}
                                else:
                                    name=f"stream-quotes-{str(row['instrument_key']).split('|')[-1]}-{row['session']}.json"
                                    result=replay(row,quotes.get(name,[]),mode,exit_policy,latency,wait)
                            record={**base,**result};record_events=record.pop('events',[]);statuses[record['status']]+=1
                            events.extend({'configuration':configuration,'execution_mode':mode,'source_strategy':row['strategy'],'entry_at':entry.isoformat(),**e} for e in record_events)
                            if record['status']=='observed_bid_ask_snapshot_proxy':
                                busy=stamp(record['exit_at']);accepted.append(record)
                                assert stamp(record['entry_fill_at'])>=entry+timedelta(milliseconds=latency);checks+=1
                                assert busy<=stamp(row['exit_at']) and busy.date()==entry.date();checks+=1
                                assert abs((record['premium_exit']-record['premium_entry'])*int(record['lot'])-record['gross_rupees_per_lot'])<1e-8;checks+=1
                                assert mode=='frame_snapshot' or strict_verified>0;checks+=1
                            elif result.get('unresolved_position'):busy=stamp(result['reserved_until'])
                            ledgers.append(record)
                        mean=lambda col:float(np.mean([r[col] for r in accepted])) if accepted else None
                        summaries.append({'configuration':configuration,'contract_policy':policy,'exit_policy':exit_policy,'latency_ms':latency,'max_quote_wait_ms':wait,'execution_mode':mode,
                            'potential_signals':len(selected),'observed_proxy_trades':len(accepted),'sessions_with_trade':len(set(r['session'] for r in accepted)),
                            'gross_mean_rupees_per_lot':mean('gross_rupees_per_lot'),'illustrative_net_mean_rupees_per_lot':mean('illustrative_net_rupees_per_lot'),
                            'severe_net_mean_rupees_per_lot':mean('severe_net_rupees_per_lot'),'holding_mean_minutes':mean('holding_minutes'),
                            'status_counts':dict(statuses),'decision':'RESEARCH_ONLY'})
    df=pd.DataFrame(ledgers);df.to_csv(OUT/'exit-stream-trades.csv',index=False);pd.DataFrame(events).to_csv(OUT/'exit-stream-events.csv',index=False)
    for _,g in df[df.status=='observed_bid_ask_snapshot_proxy'].groupby(['configuration','execution_mode']):
        g=g.sort_values('entry_fill_at');e=pd.to_datetime(g.entry_fill_at,utc=True);x=pd.to_datetime(g.exit_at,utc=True)
        assert (e.iloc[1:].reset_index(drop=True)>=x.iloc[:-1].reset_index(drop=True)).all();checks+=1
    pd.DataFrame([{k:v for k,v in r.items() if k!='status_counts'} for r in summaries]).to_csv(OUT/'exit-stream-summary.csv',index=False)
    dist=lambda a:{'min':float(min(a)),'p01':float(np.quantile(a,.01)),'median':float(np.median(a)),'p99':float(np.quantile(a,.99)),'max':float(max(a))} if a else None
    result={'configurations':80,'modes':2,'source_selection_rows':len(raw),'expanded_policy_opportunities':len(rows),'quote_rows':source_rows,'strict_verified_book_rows':strict_verified,
        'source_minus_received_offset_seconds':dist(offsets),'provider_frame_minus_LTT_seconds':dist(provider_ages),'summaries':summaries,'assertions_passed':checks,
        'observed_proxy_rows':int((df.status=='observed_bid_ask_snapshot_proxy').sum()),'no_winner_selected':True}
    save('exit-stream-summary.json',result)
    lines=['# Project Alpha: actual received book-snapshot replay','',
        f"Source selection has{len(raw)}records, expanded to{len(rows)}explicit contract-policy opportunities. {source_rows}received book snapshots; {strict_verified} have a verified exchange-book event timestamp. Eighty fixed contract/exit/latency/wait configurations and two quality modes are disclosed, with no selected winner.",
        '', '**Strict exchange-book execution is unsupported.** The frame_snapshot mode replays actual historical bid/ask states observed at local receipt, not verified exchange-book events or actual broker fills. This is stronger price evidence than OHLC, but it is still a provisional execution proxy.',
        '', '## Timing and model assumptions',
        '- Received timestamps determine information availability and order chronology. Provider frame clocks lead local receipt in some records. A fixed±1second crossclock tolerance is an explicit research assumption, not calibrated clock synchronization.',
        '- Last-trade age uses provider frame timestamp minus provider LTT (same clock), requiring0–30seconds. Receipt/source offset distribution is reported rather than silently corrected.',
        '- Entry uses the most recent valid predecision ask, no older than2seconds, to set a0.5% marketablelimit, roundedup0.05. Execution uses the first qualifying ask after250/1000ms latency within2/5seconds, with2%maxspread and one full dated lot at best bid/ask.',
        '- Stops20/30% and an optional20%stop/2Rtarget trigger on an observed bid, then apply the same latency and quote deadline. A gap can realize more than planned stop loss. No valid exit leaves the position unresolved; a loss is not replaced with zero.',
        '- Scheduled time exit is dispatched(latency+waitbudget)seconds before the original fixed60-minute exit; actual holding time is reported. No fill is accepted after the fixed due time or15:10cutoff.',
        '- One-position routing uses EMA>Donchian>pullback priority. Missing-chain signals remain rejected opportunities. No new entry is admitted while an earlier position is unresolved.',
        '- Ask-to-bid P&L already includes observed spread. Base net adds dated saleSTT andINR100other-feeallowance. Severe net adds2premiumpointsimpact andINR200other-feeallowance. These are sensitivities, not fully verified historical charges.',
        '- Observed bid MAE/MFE are lower bounds on full-path excursions between snapshots. Repeated frames do not establish liquidity replenishment, queue priority, fill probability or market impact.',
        '', '## Frame-snapshot results:250ms latency /2second quote wait',
        '|Contract policy|Exit|N|Sessions|Gross INR|Base net INR|Severe net INR|Unresolved|', '|---|---|---:|---:|---:|---:|---:|---:|']
    for r in summaries:
        if r['execution_mode']!='frame_snapshot' or r['latency_ms']!=250 or r['max_quote_wait_ms']!=2000:continue
        fmt=lambda v:f'{v:.2f}' if v is not None else 'NA'
        lines.append(f"|{r['contract_policy']}|{r['exit_policy']}|{r['observed_proxy_trades']}|{r['sessions_with_trade']}|{fmt(r['gross_mean_rupees_per_lot'])}|{fmt(r['illustrative_net_mean_rupees_per_lot'])}|{fmt(r['severe_net_mean_rupees_per_lot'])}|{r['status_counts'].get('unresolved_no_valid_exit_quote',0)}|")
    lines+=['','Allotherlatency/waitcombinationsandstrict-mode rejections are exported. The captured window is small, selected rules were already studied on overlapping dates, and missing-chain/quote coverage is nonrandom. Positive proxy means, if any, do not establish a repeatable or executable edge.',
        '', 'Clock offset distribution (source minus receipt seconds): '+json.dumps(result['source_minus_received_offset_seconds']),
        '', f"Verification:{checks}price/timing/nonoverlap assertions passed. Full contracts, quotedprices, limits, rejectioncauses, unresolvedcapitalrisk and exactevents are retained in exit-stream-trades.csv and exit-stream-events.csv. No actual orders were sent."]
    (OUT/'exit-stream-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['summaries']}))


if __name__=='__main__':main()
