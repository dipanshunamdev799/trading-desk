"""Quote-depth conservative bounds; never broker-certified fills or orders."""
from math import floor
from research.intraday_momentum.costs import fees


def depth_walk(levels,quantity,fraction=.1):
    if quantity<=0 or not 0<fraction<=1:raise ValueError('Invalid quantity/participation')
    remaining=quantity;cost=0.;filled=0
    for price,displayed in levels:
        take=min(remaining,floor(displayed*fraction))
        cost+=take*price;filled+=take;remaining-=take
        if remaining==0:break
    return dict(requested=quantity,modeled_available=filled,unfilled=remaining,price_bound=cost/filled if filled else None,
        status='FULL_DEPTH_BOUND' if not remaining else 'PARTIAL_DEPTH_BOUND' if filled else 'NO_DEPTH',not_a_fill=True)


def proposed_size(quote,side,equity,risk_room,stop_fraction,volume60,metadata_ok,account_ok):
    if not metadata_ok:return {'accepted':False,'reason':'metadata_eligibility_unverified'}
    if not account_ok:return {'accepted':False,'reason':'account_segment_unverified'}
    if not quote.valid_book:return {'accepted':False,'reason':'invalid_book'}
    if not volume60 or volume60<=0:return {'accepted':False,'reason':'missing_past_volume'}
    if not .003<=stop_fraction<=.01:return {'accepted':False,'reason':'stop_out_of_bounds'}
    px=quote.asks[0][0] if side==1 else quote.bids[0][0]
    qty=min(floor(equity/px),floor(volume60*.01),floor(risk_room/(px*(stop_fraction+.001))))
    enter='BUY' if side==1 else 'SELL';leave='SELL' if side==1 else 'BUY'
    while qty>0:
        w=depth_walk(quote.asks if side==1 else quote.bids,qty)
        if w['unfilled']:qty=w['modeled_available'];continue
        entry=w['price_bound']*(1+side*.0001);stop=entry*(1-side*stop_fraction)
        charge=fees(enter,entry,qty)['total']+fees(leave,stop,qty)['total']
        if entry*qty+fees(enter,entry,qty)['total']<=equity and qty*entry*(stop_fraction+.0002)+charge<=risk_room:break
        qty-=1
    if not qty:return {'accepted':False,'reason':'cash_risk_or_depth_size_zero'}
    return dict(accepted=True,quantity=qty,entry_bound=entry,stop=stop,target=entry*(1+side*min(.015,max(.0075,1.5*stop_fraction))),
        expected_fee_rupees=charge,spread_bps=quote.spread_bps,extra_impact_bps_side=1,fill_assumption='10% displayed depth; quote bound, not fill',unfilled=0)


def first_available(quotes,at,transport):
    # Earliest next observation at/after assumed latency; never a future best price.
    return next((q for q in quotes if q.transport==transport and q.available_at>=at and q.fresh(q.available_at)),None)


def markout(entry,exit,side,quantity,extra_bps=1):
    if entry.key!=exit.key or entry.transport!=exit.transport:return {'status':'INCOMPARABLE'}
    a=depth_walk(entry.asks if side==1 else entry.bids,quantity)
    b=depth_walk(exit.bids if side==1 else exit.asks,quantity)
    if a['unfilled'] or b['unfilled']:return {'status':'UNRESOLVED_OR_PARTIAL','entry':a,'exit':b}
    ep=a['price_bound']*(1+side*extra_bps/1e4);xp=b['price_bound']*(1-side*extra_bps/1e4)
    charges=fees('BUY' if side==1 else 'SELL',ep,quantity)['total']+fees('SELL' if side==1 else 'BUY',xp,quantity)['total']
    return dict(status='QUOTED_BOUND_ONLY',entry_bound=ep,exit_bound=xp,fees=charges,net_pnl=side*(xp-ep)*quantity-charges,
        net_bps=(side*(xp-ep)*quantity-charges)/(ep*quantity)*1e4,spread_already_embedded=True,extra_bps_side=extra_bps)
