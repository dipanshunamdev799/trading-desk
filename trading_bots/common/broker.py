"""Broker boundary. Paper fills are explicit simulations; live uses a separate token."""
import os,requests,math


class UnknownSubmission(RuntimeError):pass


class PaperBroker:
    live=False
    def submit(self,intent):
        q=intent['quote'];buy=intent['side']=='BUY';price=q['ask'] if buy else q['bid']
        price=max(.05,price+intent['slippage_points']*(1 if buy else -1))
        qty=min(intent['quantity'],int(q['ask_qty'] if buy else q['bid_qty']))
        qty=qty//intent['lot']*intent['lot']
        fits=price<=intent['limit_price'] if buy else price>=intent['limit_price']
        if qty<=0 or price<=0 or not fits:return {'order_id':'paper-'+intent['id'],'status':'REJECTED','filled_qty':0,'average_price':0,'error':'No simulated limit/depth fill'}
        return {'order_id':'paper-'+intent['id'],'status':'COMPLETE' if qty==intent['quantity'] else 'CANCELLED','filled_qty':qty,'average_price':price,'partial_cancelled':qty<intent['quantity']}
    def poll(self,order):return self.lookup(order)
    def lookup(self,order):
        # A local simulation has no external execution to discover. Never create a
        # fresh fill from an old saved quote after a crash before acknowledgment.
        filled=order.get('applied_qty',0)
        return {'order_id':'paper-'+order['id'],'status':'CANCELLED','filled_qty':filled,
            'average_price':order.get('applied_value',0)/filled if filled else 0,
            'error':'Unacknowledged paper remainder cancelled on recovery; no historical quote replay'}
    def cancel(self,order):return None


class UpstoxBroker:
    live=True
    def __init__(self):
        from app.config import get_settings
        s=get_settings()
        if not s.trading_bots_live_enabled or not s.upstox_trading_token.get_secret_value():raise ValueError('Live adapter requires TRADING_BOTS_LIVE_ENABLED and a separate UPSTOX_TRADING_TOKEN')
        self.http=requests.Session();self.http.headers.update({'Authorization':'Bearer '+s.upstox_trading_token.get_secret_value(),'Content-Type':'application/json'})
        if s.upstox_algo_name:self.http.headers['X-Algo-Name']=s.upstox_algo_name
    def request(self,method,url,**kwargs):
        r=self.http.request(method,url,timeout=(5,10),**kwargs)
        if r.status_code>=400:raise RuntimeError('Broker HTTP '+str(r.status_code)+'; reconcile order state')
        p=r.json()
        if p.get('status')!='success':raise RuntimeError('Broker did not confirm success')
        return p.get('data')
    def submit(self,intent):
        # No automatic retry on any placement error: the server may have accepted it.
        try:
            p=self.request('POST','https://api-hft.upstox.com/v3/order/place',json={'quantity':intent['quantity'],'product':'I','validity':'DAY',
                'price':intent['limit_price'],'tag':intent['id'],'instrument_token':intent['instrument_key'],'order_type':'LIMIT',
                'transaction_type':intent['side'],'disclosed_quantity':0,'trigger_price':0,'is_amo':False,'slice':False})
            ids=p.get('order_ids') or ([p['order_id']] if p.get('order_id') else [])
            if len(ids)!=1:raise UnknownSubmission('Placement needs order-book reconciliation')
            return {'order_id':ids[0],'status':'PENDING','filled_qty':0,'average_price':0}
        except Exception as e:raise UnknownSubmission(type(e).__name__+': placement outcome uncertain; no retry') from e
    def normalized(self,p):
        status=str(p.get('status','')).lower();status={'complete':'COMPLETE','cancelled':'CANCELLED','rejected':'REJECTED'}.get(status,'PENDING')
        return {'order_id':p['order_id'],'status':status,'filled_qty':int(p.get('filled_quantity',0)),'average_price':float(p.get('average_price') or 0),'broker_status':p.get('status'),'broker_payload':p}
    def poll(self,order):return self.normalized(self.request('GET','https://api.upstox.com/v2/order/details',params={'order_id':order['broker_order_id']}))
    def lookup(self,order):
        rows=self.request('GET','https://api.upstox.com/v2/order/retrieve-all')
        found=[r for r in rows if r.get('tag')==order['id']]
        if len(found)>1:raise UnknownSubmission('Multiple broker orders share tag; manual reconciliation required')
        return self.normalized(found[0]) if found else None
    def cancel(self,order):return self.request('DELETE','https://api-hft.upstox.com/v3/order/cancel',params={'order_id':order['broker_order_id']})


def broker_for(config):
    if config['mode']=='paper':return PaperBroker()
    if not config.get('live_activated'):raise ValueError('Live mode has not been explicitly activated')
    return UpstoxBroker()
