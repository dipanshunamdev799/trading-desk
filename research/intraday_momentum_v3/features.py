"""Availability-time quote features. No event identities or execution claims."""
from dataclasses import dataclass,asdict
from collections import deque
from datetime import datetime,timezone
import hashlib,json,math
import numpy as np


def timestamp(value):
    try:
        if isinstance(value,datetime):return value if value.tzinfo else None
        if isinstance(value,(int,float)) or str(value).isdigit():
            n=float(value);return datetime.fromtimestamp(n/1000 if n>1e11 else n,timezone.utc)
        d=datetime.fromisoformat(str(value).replace('Z','+00:00'));return d if d.tzinfo else None
    except (ValueError,TypeError,OverflowError,OSError):return None


@dataclass(frozen=True)
class Quote:
    key:str
    transport:str
    source_at:datetime
    received_at:datetime
    available_at:datetime
    bids:tuple
    asks:tuple
    last:float|None
    cp:float|None
    volume:float|None
    last_qty:float|None
    last_trade_at:datetime|None
    total_buy:float|None
    total_sell:float|None
    fingerprint:str
    @property
    def valid_book(self):return bool(self.bids and self.asks and self.asks[0][0]>=self.bids[0][0])
    @property
    def mid(self):return (self.bids[0][0]+self.asks[0][0])/2 if self.valid_book else None
    @property
    def spread_bps(self):return (self.asks[0][0]-self.bids[0][0])/self.mid*1e4 if self.valid_book else None
    def fresh(self,at):
        age=(at-self.source_at).total_seconds();receive=(at-self.received_at).total_seconds()
        return self.available_at<=at and 0<=receive<=(2 if self.transport=='ws' else 10) and -1<=age<=(2 if self.transport=='ws' else 10)


def number(value):
    try:
        value=float(value);return value if math.isfinite(value) else None
    except (ValueError,TypeError):return None


def normalize(key,payload,source_at,received_at,transport='ws',committed_at=None):
    source=timestamp(source_at);received=timestamp(received_at)
    if source is None or received is None:return None
    available=max(source,received,committed_at or received)
    if transport=='ws':
        ff=payload.get('fullFeed') or {};f=ff.get('marketFF') or ff.get('indexFF') or payload
        lt=f.get('ltpc') or {};levels=(f.get('marketLevel') or {}).get('bidAskQuote') or []
        bids=[(number(x.get('bidP')),number(x.get('bidQ'))) for x in levels]
        asks=[(number(x.get('askP')),number(x.get('askQ'))) for x in levels]
        last=lt.get('ltp');cp=lt.get('cp');volume=f.get('vtt');qty=lt.get('ltq');ltt=lt.get('ltt');buy=f.get('tbq');sell=f.get('tsq')
    else:
        depth=payload.get('depth') or {}
        bids=[(number(x.get('price')),number(x.get('quantity'))) for x in depth.get('buy',[])]
        asks=[(number(x.get('price')),number(x.get('quantity'))) for x in depth.get('sell',[])]
        last=payload.get('last_price');cp=payload.get('prev_close_price');volume=payload.get('volume');qty=payload.get('last_quantity');ltt=payload.get('last_trade_time');buy=payload.get('total_buy_quantity');sell=payload.get('total_sell_quantity')
    bids=tuple(sorted([(p,q) for p,q in bids if p is not None and q is not None and p>0 and q>0],reverse=True))
    asks=tuple(sorted([(p,q) for p,q in asks if p is not None and q is not None and p>0 and q>0]))
    return Quote(key,transport,source,received,available,bids,asks,number(last),number(cp),number(volume),number(qty),timestamp(ltt),number(buy),number(sell),hashlib.sha256(json.dumps(payload,sort_keys=True,allow_nan=False).encode()).hexdigest())


class FeatureBuffer:
    def __init__(self):self.data={}
    def add(self,q):
        ident=(q.key,q.transport);d=self.data.setdefault(ident,deque(maxlen=5000))
        if d and q.available_at<d[-1].available_at:return 'out_of_order_availability'
        if d and q.source_at==d[-1].source_at and q.fingerprint==d[-1].fingerprint:return 'duplicate_source_payload'
        if d and q.source_at<d[-1].source_at:return 'out_of_order_source'
        d.append(q)
        while d and (q.available_at-d[0].available_at).total_seconds()>1800:d.popleft()
        return 'accepted'
    def at(self,key,transport,at):
        d=[q for q in self.data.get((key,transport),[]) if q.available_at<=at]
        if not d:return None
        current=d[-1]
        if not current.valid_book or not current.fresh(at):return None
        d=[q for q in d if q.valid_book and q.fresh(q.available_at)]
        def previous(seconds):
            target=at.timestamp()-seconds
            found=next((q for q in reversed(d) if q.available_at.timestamp()<=target and q.valid_book),None)
            return found if found and found.fresh(datetime.fromtimestamp(target,timezone.utc)) else None
        p60=previous(60);p300=previous(300);p5=previous(5)
        recent=[q for q in d if 0<=(at-q.available_at).total_seconds()<=10 and q.valid_book and q.fresh(q.available_at)]
        def imbalance(q,n):
            b=sum(x[1] for x in q.bids[:n]);a=sum(x[1] for x in q.asks[:n]);return (b-a)/(b+a) if b+a else None
        # Equal weight per observed second, not per burst of feed messages.
        buckets={int(q.available_at.timestamp()):q for q in recent}
        imbs=[imbalance(q,5) for q in buckets.values()];imbs=[v for v in imbs if v is not None]
        observed_buckets=set(buckets)
        v60=current.volume-p60.volume if p60 and current.volume is not None and p60.volume is not None and current.volume>=p60.volume else None
        pastvol=[]
        for end in (60,120,180,240,300):
            a=previous(end);b=previous(end+60)
            if a and b and a.volume is not None and b.volume is not None and a.volume>=b.volume:pastvol.append(a.volume-b.volume)
        spreads=[q.spread_bps for q in d if 0<=(at-q.available_at).total_seconds()<=60 and q.valid_book]
        earlier=[q for q in d if 10<(at-q.available_at).total_seconds()<=30 and q.valid_book]
        supported_before=float(np.median([sum(x[1] for x in q.bids[:5]) for q in earlier])) if earlier else None
        current_bid=sum(x[1] for x in current.bids[:5]);current_ask=sum(x[1] for x in current.asks[:5])
        return dict(key=key,at=at.isoformat(),transport=transport,source_at=current.source_at.isoformat(),received_at=current.received_at.isoformat(),
            available_at=current.available_at.isoformat(),mid=current.mid,spread_bps=current.spread_bps,imbalance1=imbalance(current,1),imbalance5=imbalance(current,5),
            imbalance_mean10=float(np.mean(imbs)) if imbs else None,imbalance_std10=float(np.std(imbs)) if imbs else None,
            support_up_fraction=sum(v>.2 for v in imbs)/len(imbs) if imbs else None,support_down_fraction=sum(v<-.2 for v in imbs)/len(imbs) if imbs else None,
            support_seconds10=len(observed_buckets),return5_bps=(current.mid/p5.mid-1)*1e4 if p5 else None,
            return60_bps=(current.mid/p60.mid-1)*1e4 if p60 else None,return300_bps=(current.mid/p300.mid-1)*1e4 if p300 else None,
            daily_return=current.mid/current.cp-1 if current.cp and current.cp>0 else None,
            volume60=v60,volume_acceleration=v60/float(np.median(pastvol)) if len(pastvol)>=5 and np.median(pastvol)>0 and v60 is not None else None,
            median_spread60=float(np.median(spreads)) if spreads else None,bid_depth5=current_bid,ask_depth5=current_ask,
            bid_depth_drop_from_prior20=1-current_bid/supported_before if supported_before else None,
            prior_high300=max((q.mid for q in d if 5<(at-q.available_at).total_seconds()<=300 and q.valid_book),default=None),
            prior_low300=min((q.mid for q in d if 5<(at-q.available_at).total_seconds()<=300 and q.valid_book),default=None),
            mid_min3=min((q.mid for q in recent if (at-q.available_at).total_seconds()<=3),default=None),
            mid_max3=max((q.mid for q in recent if (at-q.available_at).total_seconds()<=3),default=None),
            observed_seconds3=len({int(q.available_at.timestamp()) for q in recent if (at-q.available_at).total_seconds()<=3}),
            low60=min((q.mid for q in d if 0<=(at-q.available_at).total_seconds()<=60 and q.valid_book),default=None),
            high60=max((q.mid for q in d if 0<=(at-q.available_at).total_seconds()<=60 and q.valid_book),default=None),
            observation_count10=len(recent),reused_asof_value=at>current.available_at,
            warning='Snapshot persistence/replenishment proxies only, not cancellations, aggressor flow or fills')
