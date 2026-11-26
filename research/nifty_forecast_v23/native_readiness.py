"""Authenticate the published NIFTY index-option inputs needed by the native panel."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from zipfile import ZipFile, BadZipFile

import requests

from .common import *
from .forward import guard_day,STUDY_DAY,CALENDAR
from research.nifty_forecast_v22.sources import UA


FIELD=('TradDt','BizDt','FinInstrmTp','FinInstrmId','TckrSymb','XpryDt','FininstrmActlXpryDt',
       'StrkPric','OptnTp','OpnPric','HghPric','LwPric','ClsPric','LastPric','SttlmPric','OpnIntrst','TtlTradgVol')


def archive_options(mark):
    day=mark['day'];cut=day.replace('-','')
    name=f'BhavCopy_NSE_FO_0_0_0_{cut}_F_0000.csv.zip'
    url=f'https://nsearchives.nseindia.com/content/fo/{name}'
    row=dict(day=day,reference=mark['ohlc']['close'],sent_at=now(),url=url)
    try:
        ans=requests.get(url,headers=UA,timeout=(7,18))
        row.update(status=ans.status_code,received_at=now(),server_date=ans.headers.get('Date'))
        if not ans.ok:
            return row
        with ZipFile(BytesIO(ans.content)) as js:
            assert len(js.namelist())==1
            with js.open(js.namelist()[0]) as file:
                a=pd.read_csv(file,low_memory=False,usecols=lambda k:k in FIELD)
        xp='FininstrmActlXpryDt' if 'FininstrmActlXpryDt' in a else 'XpryDt'
        a[xp]=pd.to_datetime(a[xp],errors='coerce',format='mixed').dt.strftime('%Y-%m-%d')
        a.TradDt=pd.to_datetime(a.TradDt,errors='coerce',format='mixed').dt.strftime('%Y-%m-%d')
        b=a[a.TckrSymb.eq('NIFTY')&a.TradDt.eq(day)&a[xp].between(day,LAST)].copy()
        assert len(b)>0 and b.TradDt.eq(day).all()
        file=f'forward/native-inputs/NIFTY-FO-{day}.csv.gz'
        write(file,b)
        options=b[b.OptnTp.isin(('CE','PE'))]
        use=options[options.ClsPric.gt(0)&options.OpnIntrst.gt(0)].copy()
        lev=row['reference']
        use['dist']=(use.StrkPric/lev-1).abs()
        combos=use.groupby([xp,'StrkPric']).OptnTp.nunique()
        paired={tuple(p) for p in combos[combos.eq(2)].index}
        use=use[[tuple(k) in paired for k in zip(use[xp],use.StrkPric,strict=True)]]
        front=use.loc[use.dist.le(.018),xp].drop_duplicates().sort_values().tolist()
        return row|dict(file=file,sha256=sha(OUT/file),response_sha256=hashlib.sha256(ans.content).hexdigest(),rows=len(b),
                     options=len(options),near_atm_matched_expiries=len(front),near_atm_dates=front,
                     lapsed_identity_missing=False,published_session=day)
    except (requests.RequestException,ValueError,KeyError,BadZipFile,AssertionError) as e:
        return row|dict(error=type(e).__name__)


def run():
    at=guard_day()
    ledger=read('forward-ledger.json')
    assert at.date().isoformat()==STUDY_DAY
    prior=[r for r in ledger['sessions'] if r['day']<STUDY_DAY][-5:]
    with ThreadPoolExecutor(max_workers=5) as pool:
        caps=list(pool.map(archive_options,prior))
    candidate_sources=[
      ('Weekly V14 return law','V12 native phase mixture and group-balanced density, fresh V13 09:10-clipped snapshot, local V14 GJR and implied curve.'),
      ('Monthly V14 return law','Exact V12 neutral input, V14 178-origin domestic design, earlier ATM/term/relative sector design and fitted GJR state.'),
      ('V18 and V20 weekly overlays','Fresh exact V14 law and timestamped issuer events with eligible cash reactions and matching feature transformations.'),
      ('V19, V20, V21 monthly positioning','Fresh exact V14 parent and verifiable earlier NSE participant features through the declared release lag.'),
      ('V22 domestic and foreign-tail laws','Fresh exact V21 distribution parent, with the corresponding domestic and international ingredients.'),
    ]
    code=[]
    for v,n in ((12,'ensemble.py'),(12,'alignment.py'),(13,'evaluate.py'),(14,'endpoint.py'),(14,'volatility.py'),
                (18,'forecast.py'),(20,'native.py'),(21,'reconstruction.py'),(22,'india.py')):
        f=ROOT/f'research/nifty_forecast_v{v}/'/n
        if f.is_file():
            code.append(dict(version=v,path=f.relative_to(ROOT).as_posix(),sha256=sha(f)))
    write('forward/native-source-readiness.csv',pd.DataFrame(caps))
    save('forward/native-source-readiness.json',dict(checked_at=now(),calendar=CALENDAR,authenticated_options=caps,source_code=code,
         dependencies=[dict(family=k,requirements=v) for k,v in candidate_sources],
         qualification='Qualified raw option-source dates are upstream evidence. Native candidate issuance also requires an exact newly dated V12–V14 state replay and corresponding overlay snapshot.'))
    print('Native diagnostic captured',sum('file' in q for q in caps),'dated official derivatives books.',flush=True)


if __name__=='__main__':
    run()
