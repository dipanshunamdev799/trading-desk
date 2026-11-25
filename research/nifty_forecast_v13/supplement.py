"""Bounded follow-up for distinct gold and Nasdaq volatility inputs."""
import io
import sys
from urllib.parse import quote

import requests

from .common import *
from .volatility import maturity, ridge_risk, GLOBAL

ASSETS={'gold_proxy':'NSE_EQ|INF204KB17I5','sector_sample':'NSE_INDEX|Nifty Bank','etf_sample':'NSE_EQ|INF204KB14I2'}


def run():
    sys.path.insert(0,str(ROOT/'backend'))
    from app.config import get_settings
    token=get_settings().upstox_analytics_token
    dest=OUT/'sources/upstox'
    requests_log=[]
    extra={}
    for label,key in ASSETS.items():
        if label=='gold_proxy':
            unit='days/1';first='2025-01-01'
        else:
            unit='minutes/5';first='2026-11-01'
        uri=f'https://api.upstox.com/v3/historical-candle/{quote(key,safe="")}/{unit}/{FREEZE}/{first}'
        target=dest/(label+'.json')
        record=dict(name=label,source=uri,start=first,end=FREEZE)
        try:
            if not target.exists():
                res=requests.get(uri,headers={'Authorization':'Bearer '+token},timeout=10)
                record['http']=res.status_code
                res.raise_for_status()
                target.write_bytes(res.content)
            a=pd.DataFrame(loads(target)['data']['candles'],columns=['stamp','open','high','low','close','volume','oi'])
            stamp=pd.to_datetime(a.stamp,utc=True).dt.tz_convert('Asia/Kolkata')
            a['date']=stamp.dt.strftime('%Y-%m-%d')
            a['minute']=stamp.dt.hour*60+stamp.dt.minute
            assert a.date.between(first,FREEZE).all()
            if label=='gold_proxy':
                extra['gold_etf_risk']=np.sqrt(252*np.log(a.sort_values('date').set_index('date').close).diff().pow(2).rolling(15,min_periods=10).mean())
            else:
                expected=np.arange(555,930,5)
                record['complete_normal_grids']=sum(np.array_equal(np.sort(f.minute),expected) for _,f in a.groupby('date'))
            record.update(rows=len(a),sha256=sha(target),path=target.relative_to(OUT).as_posix())
        except (requests.RequestException,KeyError,ValueError) as exc:
            record['unavailable']=type(exc).__name__
        requests_log.append(record)
    uri='https://fred.stlouisfed.org/graph/fredgraph.csv?id=VXNCLS&cosd=2025-01-01&coed=2026-11-17'
    r={'name':'nasdaq_implied','source':uri}
    try:
        file=OUT/'sources/VXNCLS-2025-26.csv'
        if not file.exists():
            response=requests.get(uri,timeout=9)
            r['http']=response.status_code
            response.raise_for_status()
            data=pd.read_csv(io.BytesIO(response.content),index_col=0)
            assert data.index.min()>='2025-01-01' and data.index.max()<=FREEZE
            file.write_bytes(response.content)
        data=pd.read_csv(file,index_col=0)
        if 'VXNCLS' in data:
            extra['vxn']=pd.to_numeric(data.VXNCLS,errors='coerce').dropna().div(100)
        r.update(rows=len(data),sha256=sha(file),path=file.relative_to(OUT).as_posix())
    except (ValueError,requests.RequestException) as exc:
        r['unavailable']=type(exc).__name__
    requests_log.append(r)
    save('supplemental-sources.json',requests_log)
    rows=[]; fit_notes=[]; clocks=[]
    for h in HORIZONS:
        y=matrix(f'targets-{h}.csv',OUT)
        x=matrix(f'features-{h}.csv',OUT).copy()
        x['iv_primary']=x.iv_nearest if h==5 else x.iv_bracket
        for k,s in extra.items():
            idx=s.index[s.notna()].to_numpy()
            i=idx.searchsorted(x.index,side='left')-1
            x[k]=pd.Series(np.where(i>=0,idx[np.maximum(0,i)],None),index=x.index).map(s)
            clocks.extend(dict(horizon=h,series=k,origin=d,source=idx[j],clock='earlier date, 23:00 UTC for U.S. closes') for d,j in zip(x.index,i) if j>=0)
        if not extra:
            continue
        for d in y.index[y.cohort.notna()]:
            t=maturity(y,d)[-180:]
            for m,fields in [('gold_nasdaq_risk',['iv_primary']+list(extra)),
                             ('global_iv_plus_new_sources',['iv_primary']+GLOBAL+list(extra))]:
                values,receipt=ridge_risk(x.loc[t],x.loc[[d]],y.loc[t,'volatility'],fields,m,np.random.default_rng(SEED+h))
                rows.append(dict(horizon=h,origin=d,model=m,prediction=float(values[0])))
                fit_notes.append(dict(horizon=h,origin=d,model=m,training=len(t),max_endpoint=y.loc[t,'endpoint'].max(),**receipt))
    if rows:
        write('supplemental-volatility.csv',pd.DataFrame(rows),index=False)
        write('supplemental-clock.csv',pd.DataFrame(clocks),index=False)
    save('supplemental-fits.json',fit_notes)


if __name__=='__main__':
    run()
