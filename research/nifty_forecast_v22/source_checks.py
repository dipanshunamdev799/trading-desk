"""Reconcile bounded Upstox daily bars against the primary Yahoo vendor marks."""
from .common import *


def run():
    z=csv('international-daily-book.csv.gz',usecols=['code','day','open','high','low','close','ohlc_valid'])
    by=[('GSPC','us'),('N225','japan'),('HSI','hong_kong'),('FTSE','uk'),('FCHI','france'),('GDAXI','dax_total')]
    all_rows=[];scores=[];lags=[]
    for symbol,k in by:
        rec=OUT/f'sources/upstox/{symbol}.json'
        if not rec.is_file():
            scores.append(dict(code=k,ticker=symbol,status='Upstox bar sample unavailable'))
            continue
        candles=json.loads(rec.read_text(encoding='utf-8'))['candles']
        d=pd.DataFrame([(x[0][:10],x[0],*x[1:5]) for x in candles],
                       columns=['day','upstox_stamp','broker_open','broker_high','broker_low','broker_close']).sort_values('day')
        assert d.day.between('2026-10-01',FREEZE).all() and not d.day.duplicated().any()
        va=z[z.code.eq(k)].dropna(subset=['close']).sort_values('day')
        t=d.merge(va,on='day',how='outer',indicator=True).sort_values('day')
        t=t[t.day.ge('2026-10-01')].copy()
        t['code']=k;t['symbol']=symbol
        t['diff_close']=t.close-t.broker_close
        t['diff_return']=t.close.pct_change(fill_method=None)-t.broker_close.pct_change(fill_method=None)
        delta=t.diff_close
        b=t[t._merge.eq('both')].copy()
        ret=b.close.pct_change(fill_method=None);broker=b.broker_close.pct_change(fill_method=None)
        joint=ret.notna()&broker.notna()
        locations=np.abs(b[['open','high','low','close']].to_numpy()-b[['broker_open','broker_high','broker_low','broker_close']].to_numpy())
        result=dict(code=k,ticker=symbol,status='paired vendor comparison',calendar_label='Displayed same cash session date',
               broker_rows=len(d),provider_rows=int(t.close.notna().sum()),n_matched=len(b),broker_only=int(t._merge.eq('left_only').sum()),
               provider_only=int(t._merge.eq('right_only').sum()),close_within_006=int(delta.abs().le(.06).sum()),
               all_ohlc_within_006=int(np.sum(locations.max(axis=1)<=.06)),median_absolute_close_diff=delta.abs().median(),
               median_absolute_close_diff_pct=float((b.diff_close.abs()/b.close*100).median()),day_return_correlation=ret.corr(broker),
               direction_agreement=float((ret[joint].gt(0)==broker[joint].gt(0)).mean()),raw_broker_sha256=sha(rec),
               same_type='total-return context' if k=='dax_total' else 'price-index candidate')
        scores.append(result)
        for shift in range(-2,3):
            lags.append(dict(code=k,matched_rows=len(b),paired_session_shift=shift,
                 return_correlation=ret.corr(broker.shift(shift)),
                 median_absolute_close_error=(b.close-b.broker_close.shift(shift)).abs().median()))
        all_rows.append(t)
    if all_rows:
        write('upstox-provider-pair-cases.csv',pd.concat(all_rows,ignore_index=True))
    write('upstox-provider-comparison.csv',pd.DataFrame(scores))
    write('upstox-provider-date-offset-diagnostic.csv',pd.DataFrame(lags))
    print('Reconciled bounded Upstox samples for',len(all_rows),'series; raw vendor differences retained.',flush=True)


if __name__=='__main__':
    run()
