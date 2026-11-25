"""Normalize official market observations and preserve their modeled release vintages."""
import hashlib
import io
import re
import sqlite3
from contextlib import closing
from itertools import chain

from .common import *
from .acquire import raw,sessions

INSTRUMENTS={
    'index_futures':('future_index_long','future_index_short'),
    'stock_futures':('future_stock_long','future_stock_short'),
    'index_calls':('option_index_call_long','option_index_call_short'),
    'index_puts':('option_index_put_long','option_index_put_short'),
    'stock_calls':('option_stock_call_long','option_stock_call_short'),
    'stock_puts':('option_stock_put_long','option_stock_put_short'),
}
PARTICIPANTS=('Client','DII','FII','Pro')
DATE=re.compile(r'as\s+on\s+([A-Za-z]{3,9})\s+(\d{1,2}),\s*(20\d{2})',re.I)

def next_dates(days):
    following=str(pd.Timestamp(days[-1]).date()+pd.offsets.BDay(1)).split(' ')[0]
    return dict(zip(days,[*days[1:],following]))

def release(day,following):
    return f'{following[day]}T08:15:00+05:30'

def participant_file(path,day):
    s=raw(path).decode('utf-8-sig',errors='replace')
    m=DATE.search(s.splitlines()[0])
    if not m:
        raise ValueError('Missing dated report header')
    parsed=pd.Timestamp(f'{m[1]} {m[2]} {m[3]}').date().isoformat()
    if parsed!=day:
        raise ValueError(f'Header date {parsed} differs from file date')
    a=pd.read_csv(io.StringIO(s),skiprows=1,skipinitialspace=True)
    a.columns=[re.sub('[^a-z]+','_',c.lower()).strip('_') for c in a]
    a=a.set_index('client_type')
    a.index=a.index.str.strip()
    a=a.loc[[*PARTICIPANTS,'TOTAL'],list(chain.from_iterable(INSTRUMENTS.values()))]
    a=a.apply(lambda v:pd.to_numeric(v.astype(str).str.strip().str.replace(',',''),errors='raise'))
    if a.isna().any().any() or (a.lt(0)|a.mod(1).ne(0)).any().any() or not a.index.is_unique:
        raise ValueError('Invalid contract counts')
    return a.astype('int64'),s.splitlines()[0][:160]

def participants(days,following):
    rows=[]
    checks=[]
    legacy=csv('participant-open-interest.csv.gz',V18).set_index(['day','participant'])
    compared=0
    gross_checks=0
    for day in days:
        for kind,paths in (
            ('open_interest',(V18/'sources/participants'/f'{day}.csv.gz',OUT/'sources/participant-oi-recovery'/f'{day}.csv.gz')),
            ('traded_volume',(OUT/'sources/participant-volume'/f'{day}.csv.gz',)),
        ):
            p=next((p for p in paths if p.is_file()),None)
            try:
                if p is None:
                    raise ValueError('File unavailable')
                a,header=participant_file(p,day)
                gaps=a.loc[list(PARTICIPANTS)].sum()-a.loc['TOTAL']
                failed=sum(int(a.loc['TOTAL',lo]!=a.loc['TOTAL',sh]) for lo,sh in INSTRUMENTS.values())
                gross_checks+=failed
            except (KeyError,ValueError,TypeError,pd.errors.ParserError,OSError) as e:
                checks.append(dict(day=day,kind=kind,present=p is not None,status=str(e)))
                continue
            for group in PARTICIPANTS:
                if kind=='open_interest' and (day,group) in legacy.index:
                    assert (legacy.loc[day,group][a.columns].astype('int64')==a.loc[group]).all(),(day,group)
                    compared+=1
                for instr,(lo,sh) in INSTRUMENTS.items():
                    l=int(a.loc[group,lo]); s=int(a.loc[group,sh]); g=l+s
                    u=int(a.loc[list(PARTICIPANTS),[lo,sh]].to_numpy().sum())
                    net_balanced=a.loc['TOTAL',lo]==a.loc['TOTAL',sh]
                    detail_balance=int(a.loc[list(PARTICIPANTS),lo].sum()-a.loc[list(PARTICIPANTS),sh].sum())
                    rows.append(dict(day=day,eligible_at=release(day,following),source=p.relative_to(ROOT).as_posix(),kind=kind,
                                     participant=group,instrument=instr,long_contracts=l,short_contracts=s,net_contracts=l-s,
                                     gross_contracts=g,long_short_ratio=l/s if s else np.nan,net_over_gross=(l-s)/g if g else np.nan,
                                     gross_share=g/u if u else np.nan,net_market_share=(l-s)/u if u and abs(detail_balance)/u<=.001 else np.nan,
                                     both_sides_reconcile=int(net_balanced),detail_side_gap=detail_balance,
                                     detail_long_minus_published=int(gaps[lo]),detail_short_minus_published=int(gaps[sh])))
            checks.append(dict(day=day,kind=kind,present=True,status='accepted',header=header,total_imbalances=failed,
                               largest_detail_disagreement=int(gaps.abs().max()),detail_columns_off=int(gaps.ne(0).sum()),
                               prior_accepted=(day,'FII') in legacy.index if kind=='open_interest' else None))
    assert compared==len(legacy)
    assert rows
    audit=pd.DataFrame(checks)
    return pd.DataFrame(rows),audit,dict(v18_categories_exact=compared,instrument_day_balance_failures=gross_checks,
        dates_with_detail_disagreement=int(audit.largest_detail_disagreement.gt(0).sum()),largest_detail_gap=int(audit.largest_detail_disagreement.max()))

def future_contracts(days,following):
    names=['day','business_day','ticker','kind','id','listed_expiry','actual_expiry','close','settlement','underlying','oi','oi_change','volume','lot']
    with pd.read_csv(V12/'sources/nifty-udiff.csv.gz',usecols=names,chunksize=180000,low_memory=False) as f:
        a=pd.concat([ch[ch.ticker.eq('NIFTY')&ch.kind.eq('IDF')&ch.day.isin(days)] for ch in f],ignore_index=True)
    assert not a.duplicated(['day','id']).any() and a.day.eq(a.business_day).all()
    assert (a.lot>0).all() and a.oi.ge(0).all()
    a['oi_contracts']=a.oi/a.lot
    a['oi_change_contracts']=a.oi_change/a.lot
    a['volume_contracts']=a.volume
    a['oi_unit_reconciles']=a.oi.mod(a.lot).eq(0)&a.oi_change.mod(a.lot).eq(0)
    a['eligible_at']=a.day.map(lambda d:release(d,following))
    return a.sort_values(['day','listed_expiry','id']).reset_index(drop=True)

def market_cash(days,following,database):
    def eq_prices(root,n):
        cols=['day','stock','series','isin','close','previous_close','volume','turnover']
        return csv(n,root,usecols=cols)
    mk=pd.concat([eq_prices(V17,'official-equity-daily.csv.gz'),eq_prices(V18,'supplementary-equity-cash.csv.gz')])
    mk=mk[mk.series.eq('EQ')&mk.day.isin(days)].drop_duplicates(['day','stock','series']).reset_index(drop=True)
    old=csv('delivery-statistics.csv.gz',V18)
    seed=set(csv('issuer-seed.csv').stock)
    inventory=[]
    a=[]
    use={'SYMBOL':'stock','SERIES':'series','DATE1':'date_field','PREV_CLOSE':'prev_close','CLOSE_PRICE':'close',
         'TTL_TRD_QNTY':'traded_qty','TURNOVER_LACS':'turnover_lakh','DELIV_QTY':'delivered_qty','DELIV_PER':'delivery_pct'}
    for day in days:
        p=V18/'sources/delivery'/f'{day}.csv.gz'
        if not p.is_file():
            inventory.append(dict(day=day,status='missing',rows=0))
            continue
        d=pd.read_csv(p,compression='gzip',skipinitialspace=True,usecols=list(use),
                      na_values=['-'],low_memory=False).rename(columns=use)
        assert pd.to_datetime(d.date_field,format='%d-%b-%Y').dt.strftime('%Y-%m-%d').eq(day).all(),day
        d=d.drop(columns='date_field').assign(day=day,eligible_at=release(day,following))
        cols=list(use.values())[3:]
        d[cols]=d[cols].apply(pd.to_numeric,errors='coerce')
        d['delivery_pct_recomputed']=d.delivered_qty/d.traded_qty.where(d.traded_qty.gt(0))*100
        d['delivery_percent_match']=d.delivery_pct_recomputed.sub(d.delivery_pct).abs().le(.005001).where(d.delivery_pct.notna())
        d['delivery_value_inr_close_proxy']=d.delivered_qty*d.close
        d['turnover_inr']=d.turnover_lakh*100000
        assert not d.duplicated(['stock','series']).any(),day
        if day==days[0]:
            mode='replace'
        else:
            mode='append'
        d.to_sql('delivery_reports',database,index=False,if_exists=mode)
        inventory.append(dict(day=day,status='accepted',rows=len(d),eq_rows=int(d.series.eq('EQ').sum()),
                              numeric_delivery=int(d.delivered_qty.notna().sum()),percent_failed=int(d.delivery_percent_match.eq(False).sum()),
                              source=p.relative_to(ROOT).as_posix()))
        a.append(d[d.series.eq('EQ')&d.stock.isin(seed)])
    z=pd.concat(a,ignore_index=True).merge(mk.drop(columns='series'),on=['day','stock'],how='left',suffixes=('','_bhav'),validate='1:1')
    x=z.merge(old,left_on=['day','stock'],right_on=['day','symbol'],suffixes=('','_v18'),validate='1:1')
    assert len(x)==len(old)
    for p,q in [('delivered_qty','delivery_qty'),('delivery_pct','delivery_pct_v18'),('traded_qty','traded_qty_v18')]:
        np.testing.assert_allclose(x[p],x[q],equal_nan=True)
    z['price_crosscheck']=z.close.sub(z.close_bhav).abs().le(.01).where(z.close_bhav.notna())
    return z,pd.DataFrame(inventory),mk

def deal_tables(days,following,mk):
    deal=csv('bulk-block-events.csv.gz',V18)
    d=pd.DataFrame({'day':deal.day,'stock':deal.BD_SYMBOL.str.strip(),'category':deal.file.str.split('_',n=1).str[0],
          'file':deal.file,'side':deal.BD_BUY_SELL.str.strip().str.upper().str[0],
          'quantity':pd.to_numeric(deal.BD_QTY_TRD.astype(str).str.replace(',',''),errors='coerce'),
          'price':pd.to_numeric(deal.BD_TP_WATP.astype(str).str.replace(',',''),errors='coerce'),
          'counterparty_hash':deal.BD_CLIENT_NAME.fillna('').map(lambda s:hashlib.sha256(s.strip().upper().encode()).hexdigest()[:20])})
    assert d.day.isin(days).all()
    d=d.dropna(subset=['quantity','price','stock'])
    keys=['day','stock','category','quantity','price']
    q=d.drop_duplicates(keys+['side','counterparty_hash']).copy()
    q['reported_consideration']=q.quantity*q.price
    q['signed_reported_leg']=q.reported_consideration*q.side.map({'B':1.,'S':-1.})
    q['eligible_at']=q.day.map(lambda d:release(d,following))
    values=q.groupby(keys,as_index=False).agg(buys=('side',lambda x:int(x.eq('B').sum())),sells=('side',lambda x:int(x.eq('S').sum())),
        legs=('side','size'),reported_consideration=('reported_consideration','sum'),signed_reported_leg=('signed_reported_leg','sum'))
    values['same_size_price_pairs']=np.minimum(values.buys,values.sells).where(values.category.eq('block'),0)
    values['matched_block_once_proxy']=values.reported_consideration-values.same_size_price_pairs*values.quantity*values.price
    refs=mk[['day','stock','close','previous_close','turnover','isin']]
    values=values.merge(refs,on=['day','stock'],how='left',validate='m:1')
    values['share_of_day_turnover']=values.matched_block_once_proxy/values.turnover.where(values.turnover.gt(0))
    values['premium_to_close']=values.price/values.close.where(values.close.gt(0))-1
    values['premium_to_previous_close']=values.price/values.previous_close.where(values.previous_close.gt(0))-1
    values['eligible_at']=values.day.map(lambda d:release(d,following))
    archives=pd.DataFrame([dict(month=p.name[-15:-8],file=p.relative_to(ROOT).as_posix(),
        category=p.name.split('_')[0],records=len(json.loads(raw(p))['data'])) for p in sorted((V18/'sources/deals').glob('*.gz'))])
    return q,values,archives,dict(raw=len(deal),parsed=len(d),deduplicated=len(q))

def main():
    import os
    days=sessions()
    following=next_dates(days)
    t,checks,n=participants(days,following)
    futures=future_contracts(days,following)
    print('Balanced participant report discovery',checks.groupby(['kind','status']).size().to_dict(),flush=True)
    temp=OUT/'market-positioning.sqlite.partial'
    if temp.is_file():
        temp.unlink()
    with closing(sqlite3.connect(temp)) as db:
        db.execute('PRAGMA journal_mode=OFF')
        stock,delivery,mk=market_cash(days,following,db)
        legs,deals,archives,nd=deal_tables(days,following,mk)
        tables={'participants':t,'participant_audit':checks,'nifty_futures':futures,'delivery_fixed_issuers':stock,
                'delivery_receipts':delivery,'deal_legs':legs,'deal_audited':deals,'deal_archives':archives}
        for name,z in tables.items():
            z.to_sql(name,db,index=False,if_exists='replace')
            write(name.replace('_','-')+'.csv.gz',z)
        db.execute('CREATE UNIQUE INDEX delivery_day_stock ON delivery_reports(day,stock,series)')
        db.execute('CREATE UNIQUE INDEX participant_day_contract ON participants(day,kind,instrument,participant)')
        db.execute('CREATE INDEX delivery_issuer ON delivery_fixed_issuers(isin,day)')
        db.execute('CREATE INDEX deal_issuer ON deal_audited(stock,day)')
        assert db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
        db.commit()
    os.replace(temp,OUT/'market-positioning.sqlite')
    save('database-receipt.json',dict(asof=now(),first=days[0],last=days[-1],sessions=len(days),release_guard='08:15 IST next NSE cash session, assumed conservative for historical files',unit='Participant counts are exchange contract counts across instruments of differing lot size. Cash quantities measured in shares, consideration in INR, delivery value a close proxy.',
       participants=n,participant_days={k:int(x.day.nunique()) for k,x in t.groupby('kind')},
       futures=dict(rows=len(futures),days=futures.day.nunique(),lot_values=sorted(futures.lot.unique().tolist()),unreconciled=int((~futures.oi_unit_reconciles).sum())),
       delivery=dict(full_rows=int(delivery.rows.sum()),eq_rows=int(delivery.eq_rows.sum()),numeric_delivery=int(delivery.numeric_delivery.sum()),
                     pct_mismatches=int(delivery.percent_failed.sum()),fixed_rows=len(stock),positive_id=int(stock['isin'].notna().sum()),
                     close_crosscheck=int(stock.price_crosscheck.eq(True).sum()),close_disagreements=int(stock.price_crosscheck.eq(False).sum())),
       deals=nd|dict(days=deals.day.nunique(),groups=len(deals),months=archives.month.nunique(),month_files=len(archives),
                    matched_block_pairs=int(deals.same_size_price_pairs.sum())),source_context='Source file paths and report vintages are available by record. Historical revision times were not captured.'))
    print('Saved audited positioning SQLite and normalized feature inputs',flush=True)

if __name__=='__main__':
    main()

