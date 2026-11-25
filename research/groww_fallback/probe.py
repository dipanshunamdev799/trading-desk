"""Read-only entitlement check. Token and account identifiers never enter output."""
import base64,json,os
from datetime import datetime,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/groww_fallback'
DATA_PATHS=frozenset(('/v1/live-data/quote','/v1/live-data/ltp'))


def token_metadata(token):
    result={'present':bool(token),'claims_verified':False}
    try:
        value=token.split('.')[1];claims=json.loads(base64.urlsafe_b64decode(value+'='*(-len(value)%4)))
        expiry=datetime.fromtimestamp(claims['exp'],timezone.utc)
        result.update(expiry_ist=expiry.astimezone(ZoneInfo('Asia/Kolkata')).isoformat(),expired=expiry<=datetime.now(timezone.utc))
    except (ValueError,KeyError,TypeError,IndexError,OverflowError):result['expiry_ist']=None
    return result


class DataProbe:
    def __init__(self,token,session=None):
        if not token or token!=token.strip() or token.lower().startswith('bearer '):raise ValueError('Missing or malformed local Groww token')
        self.session=session or requests.Session()
        self.session.headers.update({'Authorization':'Bearer '+token,'X-API-VERSION':'1.0','Accept':'application/json'})
    def check(self,path,parameters):
        if path not in DATA_PATHS:raise ValueError('Only allowlisted market-data GET requests are supported')
        try:
            r=self.session.get('https://api.groww.in'+path,params=parameters,timeout=20,allow_redirects=False)
            try:p=r.json()
            except ValueError:p={}
            if not isinstance(p,dict):p={}
            q=p.get('payload') if isinstance(p.get('payload'),dict) else {}
            # Whitelist response metadata; do not print raw errors, headers,
            # redirect locations, profile data or transport exception strings.
            result=dict(path=path,http_status=r.status_code,status=p.get('status'),accepted=r.status_code==200 and p.get('status')=='SUCCESS')
            if path.endswith('/quote') and result['accepted']:
                depth=q.get('depth') or {}
                result.update(bid_levels=len(depth.get('buy',[])),ask_levels=len(depth.get('sell',[])),has_volume=q.get('volume') is not None,
                    has_last_trade_time=q.get('last_trade_time') is not None,has_quote_timestamp=q.get('timestamp') is not None)
            return result
        except requests.RequestException as exc:return dict(path=path,accepted=False,error_type=type(exc).__name__)


def main():
    token=os.getenv('GROWW_ACCESS_TOKEN') or dotenv_values(ROOT/'.env.groww.local').get('GROWW_ACCESS_TOKEN')
    metadata=token_metadata(token or '');checks=[]
    if token and not metadata.get('expired'):
        c=DataProbe(token)
        checks=[c.check('/v1/live-data/quote',{'exchange':'NSE','segment':'CASH','trading_symbol':'RELIANCE'}),
                c.check('/v1/live-data/ltp',{'segment':'CASH','exchange_symbols':'NSE_RELIANCE'})]
    result=dict(checked_at=datetime.now(timezone.utc).isoformat(),credential=metadata,checks=checks,
        market_data_access_verified=bool(checks) and all(x['accepted'] for x in checks),fallback_enabled=False,
        postgres_writes=0,orders_submitted=0,scheduling_enabled=False,
        interpretation='Only market-data entitlement was tested. A403 alone does not identify the exact missing permission. User reports a free API token; official free plan excludes live data.')
    OUT.mkdir(parents=True,exist_ok=True);target=OUT/'capability-audit.json';tmp=target.with_suffix('.tmp')
    tmp.write_text(json.dumps(result,indent=2),encoding='utf-8');tmp.replace(target)
    print(json.dumps(result,indent=2));return result


if __name__=='__main__':main()
