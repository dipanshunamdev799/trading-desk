"""Acquire dated global marks and reconcile them to exchange-local session clocks."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from urllib.parse import quote
import gzip
import sys

import requests

from .common import *

UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36'}
YAHOO='https://query1.finance.yahoo.com/v8/finance/chart/'
FRED='https://fred.stlouisfed.org/graph/fredgraph.csv'
UPSTOX_LIST='https://assets.upstox.com/market-quote/instruments/exchange/global.json.gz'


@dataclass(frozen=True)
class Series:
    code: str
    market: str
    region: str
    ticker: str
    exchange: str | None
    zone: str
    currency: str
    role: str='primary'
    convention: str='local price index'
    buffer: int=60


SERIES=(
    Series('india','India','South Asia','NIFTY 50','NSE','Asia/Kolkata','INR'),
    Series('us','United States','North America','^GSPC','XNYS','America/New_York','USD'),
    Series('canada','Canada','North America','^GSPTSE','XTSE','America/Toronto','CAD'),
    Series('mexico','Mexico','North America','^MXX','XMEX','America/Mexico_City','MXN'),
    Series('uk','United Kingdom','Europe','^FTSE','XLON','Europe/London','GBP'),
    Series('france','France','Europe','^FCHI','XPAR','Europe/Paris','EUR'),
    Series('germany','Germany','Europe','^GDAXIP','XETR','Europe/Berlin','EUR'),
    Series('spain','Spain','Europe','^IBEX','XMAD','Europe/Madrid','EUR'),
    Series('italy','Italy','Europe','FTSEMIB.MI','XMIL','Europe/Rome','EUR'),
    Series('swiss','Switzerland','Europe','^SSMI','XSWX','Europe/Zurich','CHF'),
    Series('netherlands','Netherlands','Europe','^AEX','XAMS','Europe/Amsterdam','EUR'),
    Series('japan','Japan','Asia Pacific','^N225','XTKS','Asia/Tokyo','JPY'),
    Series('hong_kong','Hong Kong','Asia Pacific','^HSI','XHKG','Asia/Hong_Kong','HKD'),
    Series('china','Mainland China','Asia Pacific','000001.SS','XSHG','Asia/Shanghai','CNY'),
    Series('korea','South Korea','Asia Pacific','^KS11','XKRX','Asia/Seoul','KRW'),
    Series('taiwan','Taiwan','Asia Pacific','^TWII','XTAI','Asia/Taipei','TWD'),
    Series('singapore','Singapore','Asia Pacific','^STI','XSES','Asia/Singapore','SGD'),
    Series('australia','Australia','Asia Pacific','^AXJO','XASX','Australia/Sydney','AUD'),
    Series('indonesia','Indonesia','Asia Pacific','^JKSE','XIDX','Asia/Jakarta','IDR'),
    Series('malaysia','Malaysia','Asia Pacific','^KLSE','XKLS','Asia/Kuala_Lumpur','MYR'),
    Series('thailand','Thailand','Asia Pacific','^SET.BK','XBKK','Asia/Bangkok','THB'),
    Series('brazil','Brazil','Latin America','^BVSP','BVMF','America/Sao_Paulo','BRL','sensitivity','local total-return index'),
    Series('dax_total','Germany','Europe','^GDAXI','XETR','Europe/Berlin','EUR','context','local gross total-return index'),
    Series('euro50','Eurozone','Europe','^STOXX50E','XETR','Europe/Berlin','EUR','context'),
    Series('ndx','United States','North America','^NDX','XNAS','America/New_York','USD','context'),
    Series('dow','United States','North America','^DJI','XNYS','America/New_York','USD','context'),
    Series('russell','United States','North America','^RUT','XNYS','America/New_York','USD','context'),
    Series('us_equal','United States','North America','RSP','XNYS','America/New_York','USD','context','ETF raw price'),
    Series('us_finance','United States','North America','XLF','XNYS','America/New_York','USD','context','ETF raw price'),
    Series('us_technology','United States','North America','XLK','XNYS','America/New_York','USD','context','ETF raw price'),
    Series('uk_mid','United Kingdom','Europe','^FTMC','XLON','Europe/London','GBP','context'),
    Series('topix','Japan','Asia Pacific','^TOPX','XTKS','Asia/Tokyo','JPY','context'),
    Series('topix_etf','Japan','Asia Pacific','1306.T','XTKS','Asia/Tokyo','JPY','context','ETF raw price'),
    Series('china300','Mainland China','Asia Pacific','000300.SS','XSHG','Asia/Shanghai','CNY','context'),
    Series('aus_finance','Australia','Asia Pacific','^AXFJ','XASX','Australia/Sydney','AUD','context'),
    Series('vix','United States','North America','^VIX','XNYS','America/New_York','USD','context','implied risk index',90),
    Series('us10y','United States','North America','^TNX','XNYS','America/New_York','USD','context','yield level',120),
    Series('brent','Global','Global','BZ=F',None,'America/New_York','USD','context','vendor continuous commodity front',1440),
    Series('dollar','Global','Global','DX-Y.NYB',None,'America/New_York','USD','context','USD basket',1440),
)
FX={
 'EUR':('EURUSD=X',1),'GBP':('GBPUSD=X',1),'AUD':('AUDUSD=X',1),'CAD':('CAD=X',-1),
 'JPY':('JPY=X',-1),'HKD':('HKD=X',-1),'CNY':('CNY=X',-1),'KRW':('KRW=X',-1),'TWD':('TWD=X',-1),
 'SGD':('SGD=X',-1),'INR':('INR=X',-1),'CHF':('CHF=X',-1),'MXN':('MXN=X',-1),'IDR':('IDR=X',-1),
 'MYR':('MYR=X',-1),'THB':('THB=X',-1),'BRL':('BRL=X',-1),
}
SERIES+=tuple(Series('fx_'+k.lower(),k,'FX',v[0],None,'UTC',k,'context','USD per local currency after conversion',720) for k,v in FX.items())
BY_CODE={s.code:s for s in SERIES}
CHECKS={'us':'SP500','ndx':'NASDAQ100','dow':'DJIA','japan':'NIKKEI225','vix':'VIXCLS','us10y':'DGS10'}
DOCS={
 'upstox_global':'https://upstox.com/developer/api-documentation/announcements/global-instruments/',
 'upstox_history':'https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/',
 'nyse':'https://www.nyse.com/trade/hours-calendars','jpx':'https://www.jpx.co.jp/english/equities/trading/domestic/01.html',
 'calendars':'https://github.com/gerrymanoim/exchange_calendars','dax_price':'https://stoxx.com/index/daxk/',
 'b3_total':'https://www.b3.com.br/en_us/market-data-and-indices/indices/broad-indices/ibovespa.htm',
 'ndx_price':'https://indexes.nasdaq.com/docs/NDX%20Versions.pdf',
}


def calendars():
    dep=Path(os.environ.get('NIFTY_V22_CALENDAR_DEPS',Path(os.environ.get('TEMP','.' ))/'nifty-v22-calendar-deps'))
    if dep.is_dir():
        sys.path.insert(0,str(dep))
    import exchange_calendars
    return exchange_calendars


def yahoo(s,first,last,folder):
    fp=OUT/f'{folder}/yahoo/{s.code}.json.gz'
    request=YAHOO+quote(s.ticker,safe='')
    params=dict(interval='1d',period1=int(pd.Timestamp(first,tz='UTC').timestamp()),
                period2=int((pd.Timestamp(last,tz='UTC')+pd.Timedelta(days=1)).timestamp()))
    meta=dict(code=s.code,source='Yahoo Finance daily historical chart',requested_first=first,requested_last=last,ticker=s.ticker)
    if fp.is_file():
        body=json.loads(gzip.decompress(fp.read_bytes()))
        if body['requested_first']==first and body['requested_last']==last:
            return pd.DataFrame(body['observations']),body['receipt']|dict(file=fp.relative_to(OUT).as_posix(),sha256=sha(fp))
    receipt=meta|dict(sent=now())
    try:
        r=requests.get(request,params=params,headers=UA,timeout=(8,16))
        receipt|=dict(url=r.url,status=r.status_code,received=now(),server_date=r.headers.get('Date'))
        if not r.ok:
            return pd.DataFrame(),receipt
        v=r.json()['chart']['result'][0];attrs=v['meta'];t=v['timestamp'];x=v['indicators']['quote'][0]
        assert attrs.get('symbol')==s.ticker,attrs.get('symbol')
        zone=attrs.get('exchangeTimezoneName') or s.zone
        iso=pd.to_datetime(t,unit='s',utc=True)
        x=pd.DataFrame({**x,'source_timestamp':iso.astype(str),'day':iso.tz_convert(zone).strftime('%Y-%m-%d')})
        x=x[x.day.between(first,last)].copy()
        receipt|=dict(provider_currency=attrs.get('currency'),provider_timezone=zone,provider_type=attrs.get('instrumentType'),
                      exchange=attrs.get('fullExchangeName'),long_name=attrs.get('longName'),response_sha256=hashlib.sha256(r.content).hexdigest(),rows=len(x))
        assert attrs.get('currency')==s.currency or s.code.startswith('fx_') or s.convention in ('yield level','USD basket'),receipt
        fp.parent.mkdir(parents=True,exist_ok=True)
        trimmed=json.dumps(meta|dict(receipt=receipt,observations=json.loads(x.to_json(orient='records',double_precision=15))),allow_nan=False)
        fp.write_bytes(gzip.compress(trimmed.encode('utf-8'),mtime=0))
        return x,receipt|dict(file=fp.relative_to(OUT).as_posix(),sha256=sha(fp))
    except (requests.RequestException,TypeError,ValueError,KeyError,IndexError,AssertionError) as e:
        return pd.DataFrame(),receipt|dict(error=type(e).__name__)


def fred(job):
    key,ticker=job
    p=OUT/f'sources/fred/{ticker}.csv'
    q=dict(code=key,series=ticker,source='Federal Reserve Bank of St. Louis',url=FRED,first=FIRST,last=FREEZE,sent=now())
    try:
        if p.is_file():
            z=pd.read_csv(p)
            q.update(status='retained')
        else:
            r=requests.get(FRED,params=dict(id=ticker,cosd=FIRST,coed=FREEZE),headers=UA,timeout=(8,18))
            q.update(received=now(),status=r.status_code,url=r.url,server_date=r.headers.get('Date'))
            if not r.ok:return pd.DataFrame(),q
            z=pd.read_csv(BytesIO(r.content))
            assert ticker in z and z.iloc[:,0].between(FIRST,FREEZE).all()
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(r.content)
        out=pd.DataFrame(dict(day=z.iloc[:,0],independent=pd.to_numeric(z[ticker],errors='coerce'))).dropna()
        return out,q|dict(file=p.relative_to(OUT).as_posix(),sha256=sha(p),rows=len(out))
    except (requests.RequestException,ValueError,KeyError,AssertionError) as e:
        return pd.DataFrame(),q|dict(error=type(e).__name__)


def schedule(s,first=FIRST,last=FREEZE):
    if s.exchange=='NSE':
        days=pd.Index(cash().loc[first:last].index)
        b=pd.DatetimeIndex(days)
        op=(b+pd.Timedelta(hours=9,minutes=15)).tz_localize(IST).tz_convert('UTC')
        hours=np.where(b.dayofweek>=5,21*60,15*60+30)
        close=(b+pd.to_timedelta(hours,unit='m')).tz_localize(IST).tz_convert('UTC')
    elif s.exchange:
        ex=calendars().get_calendar(s.exchange,start=FIRST,end=LAST)
        z=ex.schedule.loc[first:last]
        days=z.index.strftime('%Y-%m-%d')
        op=pd.DatetimeIndex(z.open)
        close=pd.DatetimeIndex(z.close)
    else:
        return None
    # Membership in a schedule certifies a scheduled session, not that the vendor delivered a valid bar.
    return pd.DataFrame(dict(day=days,market_open=op,market_close=close,available=close+pd.Timedelta(minutes=s.buffer),
                             issue=op-pd.Timedelta(minutes=20),utc_close_hour=close.hour,
                             local_close=close.tz_convert(s.zone).strftime('%H:%M'),
                             local_utc_offset=close.tz_convert(s.zone).strftime('%z')))


def align(z,s):
    z=z.copy()
    if z.empty:
        z=pd.DataFrame(columns=['day','source_timestamp','open','high','low','close','volume'])
    z=z.sort_values('source_timestamp').drop_duplicates('day',keep='last')
    columns=['open','high','low','close','volume']
    for c in columns:
        z[c]=pd.to_numeric(z[c],errors='coerce')
    z.loc[z.close.le(0),'close']=np.nan
    ok=z[['open','high','low','close']].gt(0).all(axis=1)&z.high.ge(z[['open','low','close']].max(axis=1))&z.low.le(z[['open','high','close']].min(axis=1))
    z['ohlc_valid']=ok
    c=schedule(s)
    extra=[]
    if c is None:
        b=pd.to_datetime(z.day,utc=True)
        z['available']=b+pd.Timedelta(days=1,minutes=s.buffer)
        z['market_close']=b+pd.Timedelta(days=1)
        z['issue']=pd.NaT
        z['market_open']=pd.NaT
        z['utc_close_hour']=0
        z['local_close']='modeled end of UTC date'
        z['local_utc_offset']='+0000'
    else:
        extra=sorted(set(z.day)-set(c.day))
        z=c.merge(z,how='left',on='day',validate='1:1')
    z['ohlc_valid']=z.ohlc_valid.eq(True)
    detail=dict(code=s.code,market=s.market,region=s.region,ticker=s.ticker,role=s.role,exchange=s.exchange,
               zone=s.zone,currency=s.currency,convention=s.convention,eligible_close=int(z.close.notna().sum()),expected_sessions=len(z),
               valid_ohlc=int(z.ohlc_valid.sum()),missing_close=int(z.close.isna().sum()),off_calendar_rows=len(extra),
               first=z.day.min() if len(z) else None,last=z.day.max() if len(z) else None,
               modeled_guard_minutes=s.buffer,utc_offsets=','.join(sorted(z.local_utc_offset.dropna().unique())))
    return z.assign(code=s.code,market=s.market,region=s.region,role=s.role),detail,extra


def india():
    official=cash().nifty50
    rows=[];records=[]
    for day in official.index:
        p=V10/f'sources/nse-daily/{day}.csv'
        book=pd.read_csv(p,skipinitialspace=True)
        line=book[book['Index Name'].str.strip().str.casefold().eq('nifty 50')]
        assert len(line)==1 and pd.to_datetime(line.iloc[0]['Index Date'],dayfirst=True).strftime('%Y-%m-%d')==day
        a=line.iloc[0]
        z={k:float(a[v]) for k,v in zip(('open','high','low','close','volume'),
              ('Open Index Value','High Index Value','Low Index Value','Closing Index Value','Volume'))}
        assert abs(z['close']-official.loc[day])<=.05
        rows.append(dict(day=day,source_timestamp=day+'T15:30:00+05:30',**z))
        records.append(dict(day=day,file=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
    save('nse-historical-source-chain.json',dict(rows=len(rows),files=records,value_check='Independent V11 frozen close comparison'))
    return pd.DataFrame(rows),dict(code='india',source='Official NSE daily index archives reconciled against V11',file='nse-historical-source-chain.json',
                  sha256=sha(OUT/'nse-historical-source-chain.json'),status='verified',rows=len(rows))


def probe_upstox():
    from research.nifty_forecast_v15.sources import token,API
    records=[]
    p=OUT/'sources/upstox/global-instruments.json'
    try:
        r=requests.get(UPSTOX_LIST,headers=UA,timeout=15)
        r.raise_for_status()
        data=json.loads(gzip.decompress(r.content))
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        records.append(dict(source='Upstox global instrument catalog',url=UPSTOX_LIST,status=r.status_code,rows=len(data),
                             file=p.relative_to(OUT).as_posix(),sha256=sha(p),received=now()))
        auth=token()
        if not auth:
            return records
        for s in data:
            key=s.get('instrument_key')
            if not key or s.get('trading_symbol') not in ('^GSPC','^N225','^HSI','^FTSE','^FCHI','^GDAXI'):
                continue
            url=API+quote(key,safe='')+'/days/1/'+FREEZE+'/2026-10-01'
            try:
                ans=requests.get(url,headers=UA|{'Authorization':'Bearer '+auth},timeout=12)
                row=dict(source='Upstox read-only dated check',code=s.get('trading_symbol'),url=url,status=ans.status_code,received=now())
                values=ans.json().get('data',{}).get('candles',[]) if ans.ok else []
                if values:
                    shape=[x for x in values if '2026-10-01'<=x[0][:10]<=FREEZE]
                    fn=f'sources/upstox/{s["trading_symbol"][1:]}.json'
                    save(fn,dict(candles=shape,key=key))
                    row|=dict(file=fn,sha256=sha(OUT/fn),rows=len(shape))
                records.append(row)
            except (ValueError,requests.RequestException) as e:
                records.append(dict(source='Upstox read-only dated check',code=s.get('trading_symbol'),url=url,error=type(e).__name__))
    except (requests.RequestException,ValueError,AttributeError,ImportError) as e:
        records.append(dict(source='Upstox global probe',url=UPSTOX_LIST,error=type(e).__name__))
    return records


def run():
    register()
    with ThreadPoolExecutor(max_workers=7) as pool:
        j=pool.map(lambda s:yahoo(s,FIRST,FREEZE,'sources'),SERIES[1:]); all_data=[india(),*j]
        independent=dict(zip(CHECKS,pool.map(fred,CHECKS.items())))
        broker=pool.submit(probe_upstox).result()
    rows=[];pos=[];loss=[];sources=[];cross=[]
    for s,(d,rec) in zip(SERIES,all_data,strict=True):
        z,meta,extra=align(d,s)
        rows.append(z)
        pos.append(meta)
        sources.append(rec)
        loss.extend(dict(code=s.code,day=day,kind='off-calendar vendor observation') for day in extra)
        loss.extend(dict(code=s.code,day=day,kind='scheduled mark missing') for day in z.loc[z.close.isna(),'day'])
        if s.code in independent:
            f,r=independent[s.code]
            sources.append(r)
            if not f.empty:
                m=z[['day','code','close']].dropna().merge(f,on='day',validate='1:1').assign(delta=lambda x:x.close-x.independent)
                m['closes_match']=m.delta.abs().le(.06 if s.code!='us10y' else .01)
                cross.append(m)
    tape=pd.concat(rows,ignore_index=True)
    assert tape.day.between(FIRST,FREEZE).all() and not tape.duplicated(['code','day']).any()
    write('international-daily-book.csv.gz',tape)
    z=pd.DataFrame(pos)
    z['primary_eligible']=z.role.eq('primary')&z.eligible_close.ge(360)&z.missing_close.le(.13*z.expected_sessions)
    write('market-universe-audit.csv',z)
    write('international-calendar-gaps.csv',pd.DataFrame(loss))
    if cross:
        write('independent-close-checks.csv',pd.concat(cross,ignore_index=True))
    else:
        write('independent-close-checks.csv',pd.DataFrame(columns=['day','code','close','independent','delta','closes_match']))
    save('international-source-receipt.json',dict(captured=now(),scope=[FIRST,FREEZE],sources=sources+broker,docs=DOCS,
          calendar_version=calendars().__version__,eligibility='At least 360 closes and at most 13% missing in the bounded local calendar',
          timing='Scheduled close plus guard approximates historical data availability. Timestamped daily candles mark the session, not a historical receipt. Missing scheduled rows are preserved.',
          return_convention='Unadjusted local price index. Ibovespa and DAX total-return are separately labeled. ETF raw prices, FX, futures, and risk indicators are state inputs.'))
    print('Market acquisition:',int(z.primary_eligible.sum()),'comparable primary markets,',int(z.eligible_close.sum()),'eligible close marks',flush=True)
    print(z.loc[z.primary_eligible,['code','eligible_close','missing_close','valid_ohlc']].to_string(index=False),flush=True)


if __name__=='__main__':
    run()
