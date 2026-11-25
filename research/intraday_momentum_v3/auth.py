"""Diagnose GET market authorization, retaining no tokens or redirect URIs."""
import asyncio,base64,json
from urllib.parse import urlparse
from .common import OUT,now,client,dump


def safe_token_metadata(token):
    result=dict(present=bool(token),whitespace=token!=token.strip(),has_bearer_prefix=token.lower().startswith('bearer '))
    try:
        part=token.split('.')[1];claims=json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4)))
        result['local_decode']='UNVERIFIED_JWT_METADATA_ONLY'
        for k in ('iat','exp','nbf'):
            if isinstance(claims.get(k),(int,float)):
                result[k+'_utc']=__import__('datetime').datetime.fromtimestamp(claims[k],__import__('datetime').timezone.utc).isoformat()
        result['expired_by_local_clock']=claims.get('exp',float('inf'))<=now().timestamp()
    except Exception:result['local_decode']='OPAQUE_OR_UNDECODABLE'
    return result


def authorize(c):
    """Both routes are documented; require successful broker auth and WSS host."""
    attempts=[]
    for path in ('/v3/feed/market-data-feed/authorize','/v3/feed/market-data-feed'):
        try:
            r=c.session.get(c.BASE_URL+path,timeout=c.timeout,allow_redirects=False)
            result={'path':path,'status_code':r.status_code}
            uri=None
            if r.status_code==200:
                p=r.json();uri=(p.get('data') or {}).get('authorized_redirect_uri')
            elif r.status_code in (301,302,303,307,308):uri=r.headers.get('Location')
            else:
                try:
                    result['error_codes']=[e.get('errorCode') for e in r.json().get('errors',[]) if isinstance(e,dict)]
                    if 'UDAPI100058' in result['error_codes']:
                        result['documented_reason']='No segments for these users are active. Manual reactivation is recommended from Upstox app/web.'
                except Exception:pass
            attempts.append(result)
            if uri and urlparse(uri).scheme=='wss' and (urlparse(uri).hostname or '').endswith('.upstox.com'):
                return uri,attempts
        except Exception as exc:attempts.append({'path':path,'error_type':type(exc).__name__})
    return None,attempts


async def probe_socket(uri):
    import websockets,time,uuid
    from upstox_ws_v3 import UpstoxMarketDataWSV3
    result={'connection':'UNVERIFIED'}
    try:
        async with websockets.connect(uri,open_timeout=15,ping_interval=20,max_size=4*1024*1024) as ws:
            result['connection']='VERIFIED';result['modes']={}
            for mode in ('full','full_d30'):
                await ws.send(json.dumps({'guid':uuid.uuid4().hex,'method':'sub' if mode=='full' else 'change_mode','data':{'mode':mode,'instrumentKeys':['NSE_EQ|INE002A01018']}}).encode())
                until=time.monotonic()+5;levels=[];frames=0
                while time.monotonic()<until:
                    try:raw=await asyncio.wait_for(ws.recv(),max(.01,until-time.monotonic()))
                    except asyncio.TimeoutError:break
                    p=UpstoxMarketDataWSV3.decode_protobuf(raw) if isinstance(raw,bytes) else json.loads(raw);frames+=1
                    for f in p.get('feeds',{}).values():
                        if f.get('requestMode')==mode:
                            levels.append(len(f.get('fullFeed',{}).get('marketFF',{}).get('marketLevel',{}).get('bidAskQuote',[])))
                result['modes'][mode]={'frames':frames,'max_levels':max(levels,default=0),'entitlement':'OBSERVED' if max(levels,default=0)>=(30 if mode=='full_d30' else 5) else 'UNVERIFIED'}
    except Exception as exc:result['error_type']=type(exc).__name__
    return result


def main():
    c=client();result={'checked_at':now().isoformat(),'credential':safe_token_metadata(c.token),'method':'Read-only GET; no credential rotation or account changes'}
    try:
        q=c.get_full_market_quotes_v3(['NSE_EQ|INE002A01018']);result['rest_quote']={'status':'VERIFIED','instruments':len(q)}
    except Exception as exc:result['rest_quote']={'error_type':type(exc).__name__,'status_code':getattr(exc,'status_code',None)}
    # Whitelist entitlement fields in memory; never archive profile PII.
    try:
        r=c.session.get(c.BASE_URL+'/v2/user/profile',timeout=c.timeout,allow_redirects=False);p=r.json()
        if r.status_code==200:
            d=p.get('data') or {};result['account_entitlement']={k:d.get(k) for k in ('is_active','exchanges','products')}
        else:result['account_entitlement']={'status_code':r.status_code,'error_codes':[e.get('errorCode') for e in p.get('errors',[]) if isinstance(e,dict)]}
    except Exception as exc:result['account_entitlement']={'error_type':type(exc).__name__}
    uri,attempts=authorize(c);result['authorization']=attempts
    result['socket']=asyncio.run(probe_socket(uri)) if uri else {'status':'AUTHORIZATION_UNAVAILABLE'}
    inactive=any('UDAPI100058' in a.get('error_codes',[]) for a in attempts)
    result['interpretation']='Read endpoint accepted; socket test separate' if uri else 'Broker reports no active account segments (UDAPI100058), before any socket subscription; not an expired-token or subscription-cap diagnosis' if inactive else 'Both documented feed routes rejected or unavailable; broker-side cause unconfirmed'
    result['required_intervention']='Account owner must check/reactivate NSE equity segment/account in Upstox app/web, then rerun this probe; contact Upstox if account shows active but code persists. Do not rotate the shared Analytics Token automatically.' if inactive else None
    dump(OUT/'auth-audit.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
