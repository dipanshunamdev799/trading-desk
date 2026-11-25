"""Source dating, offshore anchor sensitivity and representative forecast falsifications."""
from concurrent.futures import ThreadPoolExecutor

from .common import *
from .acquire import request
from .data import offshore_mark
from .model import Q, fit, history, quantify
from .session_models import load, prepare
from .paths import Paths, JOINT
from research.nifty_forecast_v15.sequential import log_ticks

CALENDAR_DOCS={
 'nse-revised-preopen':'https://nsearchives.nseindia.com/web/mediaattachment/2026-10/FAQs_on_Closing_Auction_Session_CAS_in_the_CM_and_changes_in_FO_Segment_ver3_20261023220345.pdf',
 'nse-cas':'https://www.nseindia.com/static/products-services/closing-auction-session',
 'nse-muhurat-2026':'https://archives.nseindia.com/content/circulars/CMPT77037.pdf',
 'nseix-expiry-monday':'https://www.nseix.com/api/content/circulars/NSEIFSC_TRADE_2056.pdf',
 'nseix-expiry-tuesday':'https://www.nseix.com/api/content/circulars/NSEIFSC_TRADE_2199.pdf',
 'nseix-holidays':'https://www.nseix.com/resources/holidays',
 'nyse':'https://www.nyse.com/trade/hours-calendars',
 'jpx':'https://www.jpx.co.jp/english/corporate/about-jpx/calendar/',
 'hkex':'https://www.hkex.com.hk/-/media/HKEX-Market/Services/Circulars-and-Notices/Participant-and-Members-Circulars/SEHK/2025/ce_SEHK_CT_075_2025.pdf',
 'euronext':'https://www.euronext.com/en/trade/trading-hours-holidays',
 'xetra':'https://www.xetra.com/xetra-en/trading/trading-calendar',
 'lse':'https://www.londonstockexchange.com/securities-trading/trading-access/business-days',
}
# Explicit published 2026 cash closure dates checked against the vendor labels as a sensitivity,
# alongside the original quote-based chronology for both years.
JAPAN=set('01-01 01-02 01-12 02-11 02-23 03-20 04-29 05-04 05-05 05-06 07-20 08-11 09-21 09-22 09-23 10-12 11-03'.split())
HONG_KONG=set('01-01 02-17 02-18 02-19 04-03 04-06 04-07 05-01 05-25 06-19 07-01 10-01 10-19'.split())
US=set('01-01 01-19 02-16 04-03 05-25 06-19 07-03 09-07'.split())
EU={'ftse':set('01-01 04-03 04-06 05-04 05-25 08-31'.split()),'cac':set('01-01 04-03 04-06 05-01'.split()),
    'dax':set('01-01 04-03 04-06 05-01'.split())}


def clocks():
    iso=pd.read_csv(OUT/'information-clock.csv.gz')
    audited=[]
    rules={'spx':US,'dow':US,'tech':US,'nikkei':JAPAN,'hsi':HONG_KONG,**EU}
    for name,dates in rules.items():
        t=iso[name+'_daily_session'].fillna('')
        suspect=t.str.startswith('2026')&t.str[5:].isin(dates)
        z=iso.loc[suspect,['day','cutoff','decision',name+'_daily_session',name+'_daily_release']].copy()
        if len(z):
            for r in z.itertuples(index=False,name=None):
                audited.append(dict(day=r[0],cutoff=r[1],source=name,reported_local_date=r[3],available=r[4],
                                    flag='vendor daily mark on published holiday; test carry-forward'))
    a=pd.DataFrame(audited,columns=['day','cutoff','source','reported_local_date','available','flag'])
    write('verified-holiday-flag-sensitivity.csv',a)
    s=iso[iso.cutoff.isin(CLOCKS[:4])]
    assert s.domestic_day.lt(s.day).all() and s.used_cash_bar_end.isna().all()
    all_checks=0
    for k in iso:
        if k.endswith('_release') or k.endswith('_available') or k.startswith('used_') or k=='domestic_last_quote':
            sub=iso[iso[k].notna()]
            date=pd.to_datetime(sub[k],utc=True,format='mixed')
            decision=pd.to_datetime(sub.decision,utc=True)
            assert date.le(decision).all(),k
            all_checks+=len(sub)
    has=s[s.gift_bar_available.notna()]
    assert has.gift_bar_timestamp.str[:10].eq(has.day).all()
    assert has.gift_anchor_end.str[:10].eq(has.domestic_day).all()
    selected=s.groupby('cutoff').agg(days=('day','size'),eligible_gift=('gift_bar_timestamp','count')).reset_index()
    write('preopen-clock-validation.csv',selected)
    # Re-test the simple prior foreign source after excluding flagged 2026 holiday marks.
    from .data import extra_daily, CLOSE6
    x,y=load()
    market,_=extra_daily()
    z=[]
    for k in CLOSE6:
        f=market[k].copy()
        blocked=f.index.str.startswith('2026') & f.index.str[5:].isin(rules[k])
        f=f[~blocked].copy()
        f['r']=np.log(f.close).diff()
        ats=pd.DatetimeIndex([stamp(d,'08:55') for d in y.index])
        ii=pd.DatetimeIndex(f.available).searchsorted(ats,side='right')-1
        z.append(np.where(ii>=0,f.r.to_numpy()[ii.clip(0)],np.nan))
    xx=x[x.cutoff.eq('08:55')].set_index('day').reindex(y.index)
    simple=xx.eq6.to_numpy()
    clean=np.column_stack(z)
    adj=np.mean(clean,axis=1)
    yy=y.gap.to_numpy()
    times=y.index.to_numpy()
    rows=[]
    for i in np.flatnonzero(y.cohort.ne('').to_numpy()&np.isfinite(simple)&np.isfinite(adj)):
        subset=history(times,times,yy,i,np.isfinite(simple)&np.isfinite(adj))
        if len(subset)<54:continue
        r=yy[subset]
        for name,column in [('raw_date_labels',simple),('official_holiday_carry_forward',adj)]:
            fitted=fit(column[subset,None],r,95)
            pred=.7*fitted.values(column[i,None])+np.quantile(r-np.median(r),Q)
            rows.append(dict(day=times[i],model=name,cohort=y.cohort.iloc[i],**quantify(pred,yy[i])))
    write('official-holiday-gap-sensitivity.csv',pd.DataFrame(rows))
    save('point-in-time-verification.json',dict(passed=True,eligible_clock_checks=all_checks,preauction_days=len(s[s.cutoff.ne('09:10')]),
         source_masked_dates=len(a),records_label='The date-gap variant screens verified 2026 closures, reruns the same model on matching support. Earlier calendar retains vendor observed dates and published normal-session rules.'))
    print('Checked',all_checks,'cash and foreign eligibility timestamps',flush=True)


def offshore():
    a,y=load()
    path=OUT/'sources/normalized/gift-bars.csv.gz'
    b=pd.read_csv(path)
    for k in ['t','available','last_possible_end']:
        b[k]=pd.to_datetime(b[k],utc=True).dt.tz_convert(IST)
    b=b.set_index('t').sort_index()
    q=pd.read_csv(OUT/'information-clock.csv.gz')
    q=q[q.cutoff.eq('08:55')].set_index('day')
    bias_cases=[];scores=[];m=0
    names=['prior_1515','prior_1530','prior_1540','earlier_quote_buffer','prior_basis_median5','vendor_daily_lag']
    x=a[a.cutoff.eq('08:55')].set_index('day').reindex(y.index)
    for i,d in enumerate(y.index):
        prev=y.origin.loc[d]
        dec=stamp(d,'08:55')
        mark=offshore_mark(b,d,prev,'08:55')
        row=dict(day=d,cohort=y.cohort.iloc[i],roll_guard=int(x.gift_roll_guard.iloc[i]),prev_cash=y.previous_close.iloc[i])
        row['vendor_daily_lag']=x.gift_day.iloc[i]
        if mark:
            cur=mark['now']
            row['vendor_mark']=float(cur.close)
            row['actual_cash_open']=y.official_open.iloc[i]    # Audit outcome only.
            row['signal_stamp']=cur.name.isoformat()
            row['signal_eligible']=cur.available.isoformat()
            row['cash_basis_observed']=float(mark['ref'].close-y.previous_close.iloc[i])
            row['earlier_quote_buffer']=x.gift_delay_minutes_25.iloc[i]
            for at in ('15:15','15:30','15:40'):
                cutoff=stamp(prev,at)
                j=b.last_possible_end.searchsorted(cutoff,side='right')-1
                if j>=0:
                    z=b.iloc[j]
                    if z.name.strftime('%Y-%m-%d')==prev and (cutoff-z.last_possible_end).total_seconds()<=1200:
                        label='prior_'+at.replace(':','')
                        row[label]=float(np.log(cur.close/z.close))
                        row[label+'_anchor']=z.last_possible_end.isoformat()
            assert cur.available<=dec
            m+=1
        bias_cases.append(row)
    df=pd.DataFrame(bias_cases).set_index('day')
    df['prior_basis_median5']=np.log(df.vendor_mark/df.prev_cash)-np.log1p(df.cash_basis_observed.rolling(5,min_periods=3).median()/df.prev_cash)
    # The rolling basis uses only prior Indian cash closes and earlier vendor afternoon marks.
    yy=y.gap.to_numpy(float)
    dt=y.index.to_numpy()
    for name in names:
        xx=df[name].to_numpy(float)
        for i in np.flatnonzero(np.isfinite(xx)&y.cohort.ne('').to_numpy()):
            h=history(dt,dt,yy,i,np.isfinite(xx))
            if len(h)<54:
                continue
            if name=='vendor_daily_lag':
                md=fit(xx[h,None],yy[h],95)
                loc=float(.7*md.values(xx[i,None]))
                delta=yy[h]-np.median(yy[h])
            else:
                loc=xx[i]
                delta=yy[h]-xx[h]
                delta-=np.median(delta)
            a=np.quantile(delta,Q)+loc
            scores.append(dict(day=dt[i],cohort=y.cohort.iloc[i],model=name,baseline='prior_1530',
               prior_basis=df.cash_basis_observed.iloc[i],metadata_roll_guard=df.roll_guard.iloc[i],
               last_training_end=dt[h[-1]],n_train=len(h),**quantify(a,yy[i])))
    table=pd.DataFrame(scores)
    write('offshore-anchor-identity.csv',df,index=True)
    write('offshore-anchor-sensitivity.csv',table)
    save('offshore-roll-and-clock-audit.json',dict(morning_marks=m,contract_metadata='Underlying is NSE IX NIFTY index futures. Vendor alias lacks identifiable expiry/roll tags.',
       auditable_quote_units='Vendor index points. Futures are cash-settled in USD, contract multiplier applies separately.',
       expiry_change_links=[CALENDAR_DOCS['nseix-expiry-monday'],CALENDAR_DOCS['nseix-expiry-tuesday']],
       basis_explanation='Same vendor price change from an observed prior near-close mark discounts stable basis. Alternative prior marks, rolling basis and broad month-boundary exclusions supply robustness tests.',
       market_hours='NSE IX changed to 03:15–02:45 IST effective 2026-11-02. Actual vendor bar receipt is absent. Fresh stamp and margin are verified per date.'))
    print('Audited',m,'GIFT snapshots and',len(scores),'basis variant scores',flush=True)


def null_tests():
    import copy
    f,y=load()
    x=prepare(y,f[f.cutoff.eq('08:55')].set_index('day').reindex(y.index))
    days=y.index.to_numpy()
    results=[];draws=[]
    for target in ['gap','five','twentyone']:
        actual=y[target].to_numpy(float)
        feature_groups=[['prior_return','rv21','breadth5','finance','eq6'],['prior_return','rv21','breadth5','finance','eq6','foreign_sd','us_asia'],
             ['prior_return','rv21','breadth5','finance','eq6','tech_lead','nikkei_partial','hsi_partial']]
        labels=y['label_'+target].fillna('9999-12-31').to_numpy()
        col='cohort' if target=='gap' else 'cohort_'+target
        valid=np.flatnonzero(y[col].ne('')&np.isfinite(actual))
        chosen=valid[np.linspace(0,len(valid)-1,23,dtype=int)]
        gain=np.zeros((40,len(chosen),3))
        for which,fs in enumerate(feature_groups):
            z=x[fs].to_numpy(float)
            mask=np.arange(len(fs))>=4
            for j,k in enumerate(chosen):
                take=history(days,labels,actual,k)
                tr=actual[take]
                hist=tr-np.median(tr)
                base=fit(z[take,:4],tr,95)
                p0=float((.70*base.values(z[k,:4])+hist>0).mean())
                a0=(p0-(actual[k]>0))**2
                for loop in range(40):
                    rr=np.random.default_rng(SEED+k*31+loop*1301) if loop else None
                    fitted=fit(z[take],tr,95,rr,mask)
                    pr=float((.70*fitted.values(z[k])+hist>0).mean())
                    gain[loop,j,which]=a0-(pr-(actual[k]>0))**2
                    draws.append(dict(target=target,origin=y.origin.iloc[k],decision=days[k],draw=loop,slot=which+1,
                                      randomized=bool(rr),same_time_Brier_gain=gain[loop,j,which]))
        aggregate=gain.mean(axis=1).max(axis=1)
        results.append(dict(target=target,n_origins=len(chosen),challengers=3,refit_draws=len(aggregate)-1,
                      observed_best=aggregate[0],null_median=float(np.median(aggregate[1:])),
                      null_95=float(np.quantile(aggregate[1:],.95)),
                      null_tail=(1+int(np.sum(aggregate[1:]>=aggregate[0])))/len(aggregate)))
    write('refit-null-forecasts.csv.gz',pd.DataFrame(draws))
    write('refit-reselection-null.csv',pd.DataFrame(results))

    cases=[];a=read('path-archive.json')
    m=Paths()
    for h in HORIZONS:
        can=[v for v in a['files'] if v['horizon']==h]
        for ratio in (0,.50,.88):
            unit=can[int((len(can)-1)*ratio)]
            i=m.pos[unit['day']]
            h=unit['horizon'];base_day=unit['origin']
            law,params,simulated=m.make(i,h,base_day)
            clone=copy.copy(m)
            # The latest anchor close at c[i] and current decision features at i are kept.
            for k in ('gap','rth','local','c','state','dom','global_x','gift','risk'):
                arr=getattr(clone,k).copy()
                start=i+1 if k in ('c','state','dom','global_x','gift','risk') else i
                arr[start:]+=0.181
                setattr(clone,k,arr)
            changed,fit_controls,other=clone.make(i,h,base_day)
            assert params==fit_controls
            assert np.array_equal(simulated,other)
            with np.load(OUT/unit['file'],allow_pickle=False) as f0:
                assert all(np.array_equal(log_ticks(law[k]),log_ticks(changed[k])) for k in JOINT)
                assert all(np.array_equal(log_ticks(law[k]),f0[k]) for k in JOINT)
            xx=m.global_x[max(0,i-151):i-21]
            yy=m.gap[max(0,i-151):i-21]
            ff=fit(xx,yy,100)
            dup=fit(np.column_stack([xx,xx[:,0],xx[:,4]]),yy,100)
            value=m.global_x[i]
            np.testing.assert_array_equal(ff.values(value),dup.values(np.r_[value,value[0],value[4]]))
            cases.append(dict(horizon=h,origin=base_day,decision=unit['day'],archive_equal=True,future_unchanged=True,
                              fit_equal=True,clone_exact=True,laws=len(JOINT)))
    save('no-future-and-copy-verification.json',dict(passed=True,cases=cases,tests=len(cases),law_checks=len(cases)*len(JOINT)))
    print('Future-state and duplicate sentinel verified',len(cases)*len(JOINT),'complete laws',flush=True)


def docs():
    with ThreadPoolExecutor(max_workers=4) as pool:
        q=list(pool.map(lambda i:request(i[0],i[1],None,'sources/calendar'),CALENDAR_DOCS.items()))
    save('exchange-calendar-receipts.json',q)

if __name__=='__main__':
    import sys
    {'clock':clocks,'offshore':offshore,'null':null_tests,'docs':docs}[sys.argv[1]]()
