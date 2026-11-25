"""Versioned, paced paper execution. The frozen research engine stays intact."""
from collections import Counter
from copy import deepcopy
import math

from .catalog import COST,CAPITAL
from .engine import DataBlocked,equity,mark,select,whole_quantity

VERSION='staged-paper-v1'
DEFAULT_POLICY=dict(daily_buy_fraction=.10,max_exposure=.50,max_buy_orders=2,max_position_fraction=.05)


def validate_policy(value):
    result={**DEFAULT_POLICY,**value}
    if set(result)!=set(DEFAULT_POLICY):raise ValueError('Unknown paper allocation setting')
    for key in ('daily_buy_fraction','max_exposure','max_position_fraction'):
        n=result[key]
        if isinstance(n,bool) or not isinstance(n,(float,int)) or not math.isfinite(n) or not 0<n<=1:
            raise ValueError(f'{key} must be greater than zero and at most one')
    n=result['max_buy_orders']
    if isinstance(n,bool) or not isinstance(n,int) or not 1<=n<=20:raise ValueError('max_buy_orders must be an integer from1 to20')
    if result['max_position_fraction']>result['max_exposure']:raise ValueError('A position cannot exceed the portfolio exposure limit')
    return result


def advance_portfolio(books,*,day,offset,opens,closes,scores,instruments,policy,exposure=1.,overlay=False,gate=None):
    """One next-open paper session, with budgets shared across all C2-S books."""
    policy=validate_policy(policy);books=deepcopy(books);fills=[];decisions=[]
    for b in books:mark(b,opens)
    opening_equity=sum(equity(b) for b in books)
    daily_budget=min(CAPITAL,opening_equity)*policy['daily_buy_fraction'];spent=0.;buy_orders=0

    def execute(j,key,side,amount,price,reason,evidence='reference'):
        fills.append(dict(book=j,instrument_key=key,side=side,reference_amount=amount,reference_quantity=amount/price,
            price=price,reason=reason,session=day,gate=evidence,simulated=True,accounting='paced fractional paper convention',real_orders_submitted=0))

    def deferred(j,key,reason,side='BUY'):
        fills.append(dict(book=j,instrument_key=key,side=side,status='DEFERRED',reason=reason,session=day,simulated=True,real_orders_submitted=0))

    def buy(j,key,desired,price,reason,intent=None):
        nonlocal spent,buy_orders
        b=books[j]
        if buy_orders>=policy['max_buy_orders']:return False,'daily_buy_order_limit'
        eq=sum(equity(x) for x in books);held=sum(p['value'] for x in books for p in x['holdings'].values())
        same=sum(x['holdings'].get(key,{}).get('value',0.) for x in books)
        exposure_room=max(0.,eq*policy['max_exposure']-held)
        stock_room=max(0.,eq*policy['max_position_fraction']-same)
        amount=min(desired,b['cash'],daily_budget-spent,exposure_room,stock_room)
        # Costs are paid within amount; cap the pre-cost purchase conservatively.
        if amount<=1e-8:return False,'exposure_or_cash_limit' if exposure_room<=1e-8 else 'position_limit' if stock_room<=1e-8 else 'daily_buy_budget'
        quantity=whole_quantity(amount,price)
        if quantity<=0:return False,'zero_whole_share_size'
        evidence=gate(key,'BUY',intent['quantity'] if intent is not None else quantity) if gate else 'reference'
        if evidence not in ('reference','likely'):
            fills.append(dict(book=j,instrument_key=key,side='BUY',status='DROPPED',reason='fill_not_assumed',gate=evidence,session=day,real_orders_submitted=0));return None,'fill_not_assumed'
        if key not in b['holdings'] and amount<.2*equity(b)/20:return False,'minimum_buy'
        b['cash']-=amount;spent+=amount;buy_orders+=1;b['fees']+=amount*COST
        if key in b['holdings']:
            b['holdings'][key]['value']+=amount*(1-COST);b['holdings'][key]['basis']+=amount
        else:b['holdings'][key]=dict(value=amount*(1-COST),mark=price,basis=amount,entry_session=day)
        execute(j,key,'BUY',amount,price,reason,evidence);return True,''

    # Rank exits and exposure reductions always precede all buys. They do not
    # consume entry budgets, and cash never moves between staggered books.
    positive_resizes=[]
    for j,b in enumerate(books):
        pending=[]
        for intent in b['pending_sells']:
            key=intent['instrument_key'];p=b['holdings'].get(key);price=opens.get(key)
            if p is None:continue
            evidence=gate(key,'SELL',intent['quantity']) if gate else 'reference'
            if not price or not math.isfinite(price) or price<=0 or evidence not in ('reference','likely'):
                pending.append(intent);fills.append(dict(book=j,instrument_key=key,side='SELL',status='PENDING',gate=evidence,session=day));continue
            value=p['value'];b['cash']+=value*(1-COST);b['realized_pnl']+=value*(1-COST)-p['basis'];b['fees']+=value*COST
            del b['holdings'][key];execute(j,key,'SELL',value,price,'rank_exit',evidence)
        b['pending_sells']=pending;eq=equity(b)
        for key,weight in b['pending_resize'].items():
            p=b['holdings'].get(key);price=opens.get(key)
            if not p or not price or not math.isfinite(price) or price<=0:continue
            trade=weight*eq-p['value']
            if trade>=0:
                if trade>1e-8:positive_resizes.append((j,key,trade,price,weight))
                continue
            amount=min(-trade,p['value']);basis=p['basis']*amount/p['value']
            p['value']-=amount;p['basis']-=basis;b['cash']+=amount*(1-COST);b['realized_pnl']+=amount*(1-COST)-basis;b['fees']+=amount*COST
            execute(j,key,'SELL',amount,price,'exposure_resize')
            if p['value']<=1e-10:del b['holdings'][key]
        b['pending_resize']={}
    for j,key,amount,price,weight in positive_resizes:
        accepted,reason=buy(j,key,amount,price,'exposure_resize')
        if accepted is False:books[j]['pending_resize'][key]=weight;deferred(j,key,reason)

    # Rotate first priority between C2-S books so one book cannot consume the
    # daily order budget every time. Limits still apply to the whole strategy.
    for j in sorted(range(len(books)),key=lambda j:(j-offset)%len(books)):
        b=books[j];pending=[];eq=equity(b)
        for intent in b['pending_buys']:
            key=intent['instrument_key'];price=opens.get(key)
            if key in b['holdings']:continue
            if len(b['holdings'])>=20:pending.append(intent);deferred(j,key,'holding_limit');continue
            if not price or not math.isfinite(price) or price<=0:
                fills.append(dict(book=j,instrument_key=key,side='BUY',status='DROPPED',reason='missing_open',session=day));continue
            accepted,reason=buy(j,key,intent['weight']*eq,price,'new_position',intent)
            if accepted is False:pending.append(intent);deferred(j,key,reason)
        b['pending_buys']=pending

    for j,b in enumerate(books):
        mark(b,closes)
        if offset<j:continue
        effective=min(max(0.,exposure),policy['max_exposure'])
        rebalance=(offset-j)%5==0;selection=select(scores,b['holdings'],instruments) if rebalance else None
        eq=equity(b);x=sum(p['value'] for p in b['holdings'].values())/eq
        if selection is not None:
            sells,kept,new=selection
            b['pending_sells']=[dict(instrument_key=k,quantity=whole_quantity(b['holdings'][k]['value'],b['holdings'][k]['mark'])) for k in sells]
            # A new ranking replaces an unfinished stale queue; it does not
            # append duplicates or create an extra daily execution allowance.
            b['pending_buys']=[dict(instrument_key=k,weight=effective/20,quantity=whole_quantity(effective*eq/20,closes[k]),decision_session=day) for k in new]
        else:kept=list(b['holdings'])
        # Underdeployment while an entry queue is being staged is intentional.
        # Do not concentrate the entire exposure target into the few names that
        # have entered so far. Genuine exposure reductions remain available.
        if overlay and (not rebalance or selection is not None) and x>0 and abs(x-effective)>.10 and (x>effective or not b['pending_buys']):
            b['pending_resize']={k:b['holdings'][k]['value']/eq*effective/x for k in kept}
        if selection is None:
            for intent in b['pending_buys']:
                key=intent['instrument_key'];price=closes.get(key)
                if price and math.isfinite(price) and price>0:
                    intent.update(weight=effective/20,quantity=whole_quantity(effective*eq/20,price),decision_session=day)
        for side,queue in (('SELL',b['pending_sells']),('BUY',b['pending_buys'])):
            for intent in queue:
                decisions.append({**intent,'book':j,'side':side,'decision_session':intent.get('decision_session',day),
                    'status':'QUEUED' if intent['quantity']>0 else 'REJECTED','reason':'paced_entries' if intent['quantity']>0 else 'zero_or_negative_qty'})
        if b['cash']<-1e-6 or not math.isfinite(equity(b)):raise DataBlocked('invalid_paced_paper_state')
    return books,fills,decisions,dict(opening_equity=opening_equity,daily_buy_limit=daily_budget,buy_amount=spent,
        buy_orders=buy_orders,max_buy_orders=policy['max_buy_orders'],max_exposure=policy['max_exposure'],
        deferred=Counter(x['reason'] for x in fills if x.get('status')=='DEFERRED'))
