"""Deterministic long-option research execution primitives. Never sends orders.

Candle mode reports price proxies/bounds. Quote mode requires verified book-event
timestamps and handles missed/partial orders explicitly; a simulated fill is not
proof of market impact or actual broker execution.
"""
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import math

IST=timezone(timedelta(hours=5,minutes=30))


def stamp(value):
    result=value if isinstance(value,datetime) else datetime.fromisoformat(str(value).replace('Z','+00:00'))
    if result.tzinfo is None:raise ValueError('Timezone-aware timestamps required')
    return result


def valid_bar(row):
    try:
        o,h,l,c=(float(row[k]) for k in ['open','high','low','close'])
        return all(math.isfinite(v) for v in [o,h,l,c]) and 0<l<=min(o,c)<=max(o,c)<=h
    except (KeyError,ValueError,TypeError):return False


@dataclass(frozen=True)
class ExitPolicy:
    name:str
    hold_minutes:int=60
    premium_stop:float|None=None
    target_r:float|None=None
    trailing_fraction:float|None=None
    underlying_atr:float|None=None
    structure_stop:bool=False


def policies():
    return [ExitPolicy('time30',30),ExitPolicy('time60',60),ExitPolicy('time120',120),
        ExitPolicy('premium20',premium_stop=.20),ExitPolicy('premium30',premium_stop=.30),
        ExitPolicy('premium20_target1R',premium_stop=.20,target_r=1),
        ExitPolicy('premium20_target2R',premium_stop=.20,target_r=2),
        ExitPolicy('premium30_target2R',premium_stop=.30,target_r=2),
        ExitPolicy('premium20_trail20',premium_stop=.20,trailing_fraction=.20),
        ExitPolicy('underlying1ATR',underlying_atr=1),ExitPolicy('underlying1.5ATR',underlying_atr=1.5),
        ExitPolicy('underlying_prior3bar_structure',structure_stop=True)]


def candle_replay(trade, option_bars, underlying_bars, policy, ambiguity='adverse_first'):
    """Process bars sequentially; ambiguous intrabar stops/targets get two bounds.

    Underlying invalidation is known only at trigger-bar close and exits at the
    following option open. Premium resting-order thresholds use candle proxies.
    Full exit-bar extrema are excursion bounds because within-bar paths are unknown.
    """
    if ambiguity not in ('adverse_first','favorable_first'):raise ValueError('Unknown ambiguity mode')
    entry=stamp(trade['entry_at']);local=entry.astimezone(IST);cutoff=local.replace(hour=15,minute=10,second=0,microsecond=0)
    base={'policy':policy.name,'entry_at':entry.isoformat(),'ambiguity_mode':ambiguity,'execution_evidence':'candle_proxy',
          'events':[],'ambiguity_count':0,'cutoff_truncated':entry+timedelta(minutes=policy.hold_minutes)>cutoff}
    def reject(reason,at=None):
        return {**base,'status':'unsupported_'+reason,'unresolved_position':bool(base['events']),
                'last_supported_at':at.isoformat() if at else None,'reserved_until':cutoff.isoformat() if base['events'] else entry.isoformat()}
    if entry.second or entry.microsecond or local.minute%5 or not local.replace(hour=9,minute=15,second=0,microsecond=0)<=entry<cutoff:
        return reject('entry_time')
    row=option_bars.get(entry)
    if row is None or not valid_bar(row) or float(row.get('volume',0))<=0:return reject('entry_bar')
    opened=float(row['open']);due=min(entry+timedelta(minutes=policy.hold_minutes),cutoff)
    stop=opened*(1-policy.premium_stop) if policy.premium_stop is not None else None
    target=opened*(1+policy.premium_stop*policy.target_r) if policy.target_r is not None else None
    underlying_stop=None
    direction=int(trade['direction'])
    if policy.underlying_atr is not None:
        atr=float(trade['signal_atr']);underlying_stop=float(trade['signal_spot'])-direction*policy.underlying_atr*atr
        if not math.isfinite(atr) or atr<=0:return reject('ATR')
    if policy.structure_stop:underlying_stop=float(trade['signal_structure_stop'])
    if underlying_stop is not None:
        u=underlying_bars.get(entry)
        if u is None or not valid_bar(u):return reject('underlying_entry')
        if direction*(float(u['open'])-underlying_stop)<=0:return reject('underlying_already_invalidated')
    base['events'].append({'at':entry.isoformat(),'kind':'ENTRY_CANDLE_OPEN_PROXY','price':opened})
    premium_peak_close=opened;lowest=opened;highest=opened;pending_underlying=False;bar_count=0
    at=entry
    while at<due:
        row=option_bars.get(at)
        if row is None:return reject('missing_bar',at)
        if not valid_bar(row):return reject('invalid_bar',at)
        if float(row.get('volume',0))<=0:return reject('zero_volume_bar',at)
        o,h,l,c=(float(row[k]) for k in ['open','high','low','close']);end=at+timedelta(minutes=5);bar_count+=1
        price=None;reason=None;out_at=end
        if pending_underlying:price=o;reason='underlying_stop_next_open';out_at=at
        elif stop is not None and o<=stop:price=o;reason='premium_stop_gap_open';out_at=at
        elif target is not None and o>=target:price=target;reason='target_gap_limit_proxy';out_at=at
        else:
            # Extrema can happen on either side of an unknown within-bar exit.
            lowest=min(lowest,l);highest=max(highest,h)
            stop_hit=stop is not None and l<=stop;target_hit=target is not None and h>=target
            if stop_hit and target_hit:
                base['ambiguity_count']+=1
                price=stop if ambiguity=='adverse_first' else target
                reason='ambiguous_stop_first' if ambiguity=='adverse_first' else 'ambiguous_target_first'
            elif stop_hit:price=stop;reason='premium_stop_intrabar_proxy'
            elif target_hit:price=target;reason='target_intrabar_proxy'
        if price is None and end>=due:price=c;reason='session_cutoff' if due==cutoff and base['cutoff_truncated'] else 'time_exit'
        if price is not None:
            lowest=min(lowest,price);highest=max(highest,price)
            base['events'].append({'at':out_at.isoformat(),'kind':reason,'price':price,
                                   'trigger_interval_start':at.isoformat(),'trigger_interval_end':end.isoformat()})
            lot=int(trade['lot']);gross=(price-opened)*lot;stt_rate=.0015 if local.date().isoformat()>='2026-04-01' else .001
            return {**base,'status':'observed_candle_proxy','unresolved_position':False,'exit_at':out_at.isoformat(),
                    'premium_entry':opened,'premium_exit':price,'exit_reason':reason,'lot':lot,'bars_observed':bar_count,
                    'gross_rupees_per_lot':gross,'sale_stt_rupees_per_lot':price*lot*stt_rate,
                    'illustrative_net_rupees_per_lot':gross-price*lot*stt_rate-2*lot-100,
                    'severe_net_rupees_per_lot':gross-price*lot*stt_rate-5*lot-200,
                    'mae_candle_bound_points':max(0,opened-lowest),'mfe_candle_bound_points':max(0,highest-opened),
                    'mae_candle_bound_rupees':max(0,opened-lowest)*lot,'mfe_candle_bound_rupees':max(0,highest-opened)*lot,
                    'holding_minutes':(out_at-entry).total_seconds()/60,'initial_premium_stop':opened*(1-policy.premium_stop) if policy.premium_stop else None,
                    'underlying_stop':underlying_stop,'target_premium':target}
        base['events'].append({'at':end.isoformat(),'kind':'BAR_CLOSE_OBSERVED','close':c})
        if underlying_stop is not None:
            u=underlying_bars.get(at)
            if u is None or not valid_bar(u):return reject('underlying_bar',at)
            touched=float(u['low'])<=underlying_stop if direction==1 else float(u['high'])>=underlying_stop
            if touched:
                pending_underlying=True
                base['events'].append({'at':end.isoformat(),'kind':'UNDERLYING_INVALIDATION_CONFIRMED','level':underlying_stop})
        if policy.trailing_fraction is not None:
            # A closed bar may raise the next bar's stop. No intrabar high/low ordering is assumed.
            premium_peak_close=max(premium_peak_close,c);stop=max(stop or 0,premium_peak_close*(1-policy.trailing_fraction))
        at=end
    raise AssertionError('A positive holding window must resolve or be unsupported')


def quote_fill(intent,quotes,latency_ms=250,timeout_ms=2000,max_age_ms=1000,allow_partial=False):
    """Indicative marketable-limit fill from one eligible source book observation.

    No passive queue fills, no assumed book replenishment and no broker calls.
    Partial quantity is returned explicitly and the unfilled remainder cancelled.
    """
    decision=stamp(intent['known_at']);earliest=decision+timedelta(milliseconds=latency_ms);deadline=earliest+timedelta(milliseconds=timeout_ms)
    qty=int(intent['quantity']);lot=int(intent['lot']);side=intent['side'];limit=float(intent['limit_price']);rejections=[]
    if qty<=0 or lot<=0 or qty%lot or side not in ('BUY','SELL'):raise ValueError('Whole-lot order and side required')
    for q in sorted(quotes,key=lambda q:stamp(q['received_at'])):
        received=stamp(q['received_at']);source=stamp(q['source_at'])
        if received<earliest or received>deadline:continue
        if q['instrument_key']!=intent['instrument_key']:continue
        if not q.get('book_timestamp_verified') or q.get('market_status')!='NORMAL_OPEN':rejections.append('unverified_book_or_market');continue
        if not 0<=(received-source).total_seconds()*1000<=max_age_ms:rejections.append('stale_or_future_book');continue
        bid=float(q['bid']);ask=float(q['ask'])
        if not 0<bid<=ask:rejections.append('invalid_book');continue
        price=ask if side=='BUY' else bid;depth=int(q['ask_qty'] if side=='BUY' else q['bid_qty'])
        if (side=='BUY' and price>limit) or (side=='SELL' and price<limit):rejections.append('limit_not_marketable');continue
        available=max(0,depth//lot*lot)
        if available<qty and not allow_partial:rejections.append('insufficient_full_depth');continue
        filled=min(qty,available)
        if not filled:rejections.append('no_whole_lot_depth');continue
        return {'status':'FILLED_PROXY' if filled==qty else 'PARTIAL_CANCELLED_PROXY','filled_quantity':filled,
                'cancelled_quantity':qty-filled,'price':price,'fill_at':received.isoformat(),'source_at':source.isoformat(),
                'remaining_position_quantity':filled if side=='BUY' else qty-filled,'rejections':rejections,'execution_evidence':'verified_book_replay_proxy'}
    return {'status':'MISSED','filled_quantity':0,'cancelled_quantity':qty,'price':None,'rejections':rejections,'execution_evidence':'unsupported_or_unfilled'}


def quote_exit(intent,quotes,stop_price=None,target_price=None,latency_ms=250,max_age_ms=1000):
    """Exit trigger uses observable bid; stop exit may gap beyond its threshold.

    The decision is made at first trigger observation, then quote_fill applies
    latency to later observations. At expiry of a replay without eligible quotes,
    the outcome remains unresolved rather than manufactured at a stale price.
    """
    due=stamp(intent['due_at']);ordered=sorted(quotes,key=lambda q:stamp(q['received_at']))
    for q in ordered:
        at=stamp(q['received_at']);source=stamp(q['source_at'])
        if at<stamp(intent['entry_at']) or q['instrument_key']!=intent['instrument_key']:continue
        if not q.get('book_timestamp_verified') or q.get('market_status')!='NORMAL_OPEN' or not 0<=(at-source).total_seconds()*1000<=max_age_ms:continue
        bid=float(q.get('bid',0));ask=float(q.get('ask',0))
        if not 0<bid<=ask:continue
        reason='stop' if stop_price is not None and bid<=stop_price else 'target' if target_price is not None and bid>=target_price else 'time' if at>=due else None
        if reason:
            order={**intent,'known_at':at.isoformat(),'side':'SELL','limit_price':0.01}
            result=quote_fill(order,ordered,latency_ms=latency_ms,max_age_ms=max_age_ms,allow_partial=True)
            return {**result,'exit_reason':reason,'trigger_at':at.isoformat(),'stop_gap_per_unit':max(0,stop_price-result['price']) if stop_price is not None and result['price'] is not None and reason=='stop' else 0}
    return {'status':'UNRESOLVED_NO_VALID_EXIT_QUOTE','filled_quantity':0,'remaining_position_quantity':intent['quantity'],'execution_evidence':'unsupported'}
