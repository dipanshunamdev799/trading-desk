"""Synchronized traded-instrument snapshots with dated identities and volume proxies."""
from collections import defaultdict
from .common import *


def bar_inventory():
    primary=read('stock-candle-receipt.json')['records']
    extended=read('intraday-extensions-receipt.json')['records']
    fallback=read('stock-recovery-receipt.json')['records'] if (OUT/'stock-recovery-receipt.json').is_file() else []
    archived=[]
    for name in ('bank','finance','it','auto','defensive','broad'):
        k='financial' if name=='finance' else name
        folder=V10/'sources/intraday' if name in ('bank','finance','it','auto') else V15/'sources/market-intraday'
        for f in sorted(folder.glob(k+'-*.json')):
            archived.append(dict(stock=name,file=f.as_posix(),sha256=sha(f),bars=1,begin=FIRST,end=FREEZE,
                                 instrument='NSE_INDEX|'+name,bar_minutes=25))
    by=defaultdict(list)
    for r in [*primary,*extended,*fallback,*archived]:
        if 'file' in r and r.get('bars',0)>0:
            by[r['stock']].append(r)
    return by


def read_bars(records,official=None):
    rows=[]
    for rec in records:
        if sha(OUT/rec['file'])!=rec['sha256']:
            raise ValueError(rec['file'])
        x=pd.DataFrame(read(rec['file'])['data']['candles'],
                        columns=['ts','open','high','low','close','volume','oi'])
        x.ts=pd.to_datetime(x.ts,utc=True).dt.tz_convert(IST)
        x['day']=x.ts.dt.strftime('%Y-%m-%d')
        x['resolution']=rec.get('bar_minutes',5)
        x=x[x.day.between(rec['begin'],rec['end'])]
        if official is not None:
            match=x.day.map(official)
            x=x[match.eq(rec['instrument'].split('|')[-1])]
        rows.append(x)
    if not rows:
        return pd.DataFrame(columns=['ts','open','high','low','close','volume','oi','day','minute'])
    x=pd.concat(rows,ignore_index=True).sort_values('ts')
    x=x[x.day.between(FIRST,FREEZE)&x.low.gt(0)&x.high.ge(x[['open','close']].max(axis=1))&
        x.low.le(x[['open','close']].min(axis=1))&x.volume.ge(0)]
    x=x.loc[x.resolution.eq(x.groupby('day').resolution.transform('min'))].drop_duplicates('ts',keep='first')
    x['minute']=x.ts.dt.hour*60+x.ts.dt.minute
    x=x[x.minute.between(555,925)]
    return x


def action_audit(basket):
    root=OUT/'sources/source-probes'
    instruments=set(basket.stock)
    events=[];ann=[];totals={}
    ca_all={}
    for year in ['2025','2026']:
        p=root/f'corporate-action-{year}.json.gz'
        if p.exists():
            payload=read(p.relative_to(OUT).as_posix())
            totals[f'actions_{year}']=len(payload)
            for row in payload:
                if row.get('symbol') not in instruments:continue
                d=pd.to_datetime(row.get('exDate'),format='%d-%b-%Y',errors='coerce')
                if pd.isna(d):continue
                x=d.strftime('%Y-%m-%d')
                if not FIRST<=x<=FREEZE:continue
                ca_all.setdefault((row['symbol'],x),[]).append(row.get('subject',''))
                events.append(dict(stock=row['symbol'],isin=row.get('isin'),ex_date=x,subject=row.get('subject'),
                                   archived_broadcast=row.get('caBroadcastDate'),archive=p.relative_to(OUT).as_posix()))
        p=root/f'announcements-{year}.json.gz'
        if p.exists():
            payload=read(p.relative_to(OUT).as_posix())
            totals[f'announcements_{year}']=len(payload)
            for r in payload:
                if r.get('symbol') not in instruments:continue
                filing=pd.to_datetime(r.get('an_dt'),format='%d-%b-%Y %H:%M:%S',errors='coerce')
                published=pd.to_datetime(r.get('exchdisstime'),format='%d-%b-%Y %H:%M:%S',errors='coerce')
                if pd.isna(published) or pd.isna(filing):
                    continue
                if published<filing or not FIRST<=published.strftime('%Y-%m-%d')<=FREEZE:
                    continue
                raw=' '.join((str(r.get('desc','')),str(r.get('attchmntText','')))).casefold()
                kinds={'results':int(any(k in raw for k in ('financial results','unaudited financial','audited financial'))),
                   'corp_action':int(any(k in raw for k in ('dividend','split','bonus shares','demerger','subdivision','sub-division'))),
                   'board_schedule':int('board meeting' in raw and any(k in raw for k in ('intimation','schedule','scheduled','notice')))}
                if not any(kinds.values()):continue
                ann.append(dict(stock=r['symbol'],isin=r.get('sm_isin'),filed=filing.tz_localize(IST).isoformat(),
                     disseminated=published.tz_localize(IST).isoformat(),
                     eligible=(published.tz_localize(IST)+pd.Timedelta(minutes=5)).isoformat(),
                     sequence=r.get('seq_id'),category=r.get('desc'),**kinds))
    columns=['stock','isin','ex_date','subject','archived_broadcast','archive']
    write('corporate-actions-audit.csv',pd.DataFrame(events,columns=columns))
    a=pd.DataFrame(ann).drop_duplicates(['stock','sequence']).sort_values('eligible')
    write('announcement-availability.csv.gz',a)
    save('announcement-receipt.json',dict(total_records=totals,basket_actions=len(events),timed_tagged_announcements=len(a),
          clock='First archived exchange dissemination plus five minutes. Filing and exchange dissemination are separate.',
          forecast_payload='Category counts only. Event dates, surprise, eventual outcome and untimestamped ex-dates are not forecast inputs.'))
    return ca_all


def assemble():
    m=pd.read_csv(OUT/'historical-stock-basket.csv')
    days=matrix('cash-panel/cash.csv',V16)
    full=pd.read_csv(OUT/'official-equity-daily.csv.gz',usecols=['day','stock','isin','open','close','previous_close','volume','turnover'],low_memory=False)
    valid=full[full.stock.isin(m.stock)].sort_values(['stock','day']).drop_duplicates(['stock','day'])
    date_set=set(days.index); prev_dates=dict(zip(days.index[1:],days.index[:-1]))
    corp=action_audit(m)
    sources=bar_inventory()
    listed=m.set_index('stock').to_dict('index')
    all_c=listed|{k:dict(sector='native',rank=0) for k in ['bank','finance','it','auto','energy','defensive','broad']}
    outputs=[];audit=[];coverage=[]
    for sym,u in all_c.items():
        sec=u['sector']
        official=valid[valid.stock.eq(sym)].set_index('day') if sec!='native' else None
        if official is not None and sym not in ('NIFTYBEES','BANKBEES'):
            identity=official['isin']
        else:
            # ETF bars are bound to the broker-listed ISIN; use NSE when both files cover the day.
            identity=None if official is None or not len(official) else official['isin']
        q=read_bars(sources.get(sym,[]),identity) if sym in sources else pd.DataFrame()
        if not len(q):continue
        groups=dict(tuple(q.groupby('day',sort=True)))
        for day,g in groups.items():
            if day not in date_set or g.minute.iloc[0]!=555:continue
            g=g.sort_values('minute')
            minute=g.minute.to_numpy()
            interval=int(g.resolution.iloc[0])
            o=g.open.to_numpy(float)
            c=g.close.to_numpy(float)
            vol=g.volume.to_numpy(float)
            if minute[0]!=555:continue
            hi=g.high.to_numpy(float);lo=g.low.to_numpy(float)
            volume=np.cumsum(vol)
            value=np.cumsum(vol*(hi+lo+c)/3.)
            days_old=prev_dates.get(day)
            prev=groups.get(days_old)
            old_isin=official.at[days_old,'isin'] if official is not None and days_old in official.index else None
            curr_isin=official.at[day,'isin'] if official is not None and day in official.index else None
            same=curr_isin==old_isin or sec=='native'
            p0=float(prev.close.iloc[-1]) if prev is not None and len(prev)>=350//int(prev.resolution.iloc[0]) and same else np.nan
            if np.isfinite(p0) and (abs(np.log(o[0]/p0))>.17 and sec!='native'):p0=np.nan
            if official is not None and day in official.index:
                op=float(official.at[day,'open'])
                late=float(official.at[day,'close'])
                au=corp.get((sym,day),[])
                audit.append(dict(day=day,stock=sym,sector=sec,isin=curr_isin,previous_isin=old_isin,corporate_action=int(bool(au)),
                    action_subject=' | '.join(au),identity_switch=int(pd.notna(curr_isin)&pd.notna(old_isin)&(not same)),
                    official_open=op,vendor_open=o[0],overnight_return_available=int(np.isfinite(p0)),
                    open_log_difference=np.log(o[0]/op),close_log_difference=np.log(c[-1]/late),
                    official_volume=official.at[day,'volume'],vendor_bar_volume=volume[-1],bars=len(g)))
            tr=np.diff(np.log(np.r_[o[0],c]))
            cumulative_sq=np.cumsum(tr*tr)
            for time in SESSION_CLOCKS+('17:00',):
                dt=stamp(day,time)
                if time=='17:00':
                    n=len(g)
                    if n!=375//interval:continue
                else:
                    mi=dt.hour*60+dt.minute-5
                    n=max(0,(mi-555)//interval)
                if n==0 or n>len(g) or not np.array_equal(minute[:n],555+interval*np.arange(n)):
                    continue
                j=n-1
                bar_end=g.ts.iloc[j]+pd.Timedelta(minutes=interval)
                assert bar_end+pd.Timedelta(minutes=5)<=dt
                b5=float(tr[j])
                b15=float(tr[j-2:j+1].sum()) if j>=2 else np.nan
                b30=float(tr[j-5:j+1].sum()) if j>=5 else np.nan
                traded=float(volume[j])
                vwap=float(value[j]/traded) if traded>0 and sec!='native' else np.nan
                log_day=np.log(c[j]/p0) if p0>0 else np.nan
                outputs.append(dict(day=day,cutoff=time,stock=sym,sector=sec,rank=u['rank'],
                       cutoff_bar_end=bar_end.isoformat(),decision=dt.isoformat(),recorded_open=o[0],last_close=c[j],past_bars=n,
                       interval_minutes=interval,lastbar=b5,date_active=int(same),known_gap=np.log(o[0]/p0) if p0>0 else np.nan,ret_day=log_day,ret_open=np.log(c[j]/o[0]),
                       last5=b5 if interval==5 else np.nan,last15=b15 if interval==5 else np.nan,last30=b30 if interval==5 else np.nan,rv=np.sqrt(cumulative_sq[j]),range=np.log(hi[:n].max()/lo[:n].min()),
                       volume=traded if sec!='native' else np.nan,candle_rupee_turnover=value[j] if sec!='native' else np.nan,
                       candle_vwap=vwap,vwap_deviation=np.log(c[j]/vwap) if vwap>0 else np.nan,
                       date_ex_action=int((sym,day) in corp)))
        coverage.append(dict(stock=sym,sector=sec,source_rows=len(q),official_days=int(len(official)) if official is not None else None,
                             distinct_days=len(groups),files=len(sources.get(sym,[]))))
    f=pd.DataFrame(outputs).sort_values(['stock','cutoff','day']).reset_index(drop=True)
    assert f.cutoff_bar_end.lt(f.decision).all()
    gg=f.groupby(['stock','cutoff'],sort=False)
    base=gg.volume.transform(lambda t:t.shift(1).rolling(20,min_periods=10).median())
    tv=gg.candle_rupee_turnover.transform(lambda t:t.shift(1).rolling(20,min_periods=10).median())
    f['relative_volume']=np.log(np.maximum(f.volume,.5)/np.maximum(base,.5)).clip(-3.5,3.5)
    f['relative_turnover']=np.log(np.maximum(f.candle_rupee_turnover,.5)/np.maximum(tv,.5)).clip(-3.5,3.5)
    f['return_per_volume']=f.ret_open.abs()/(1+np.exp(f.relative_turnover))
    f['activity_sign_proxy']=f.ret_open*np.exp(f.relative_volume.clip(-1.5,1.5))
    a=pd.DataFrame(audit)
    write('stock-identity-and-price-audit.csv.gz',a)
    write('stock-bar-coverage.csv',pd.DataFrame(coverage))
    write('stock-snapshots.csv.gz',f)
    save('stock-panel-receipt.json',dict(stock_clock_rows=len(f),distinct_dates=f.day.nunique(),traded_symbols=f[f.sector.ne('native')].stock.nunique(),
      audit_stock_days=len(a),identity_switches=int(a.identity_switch.sum()),declared_action_days=int(a.corporate_action.sum()),
      zero_volume_native_rows=int(f[f.sector.eq('native')].volume.isna().sum()),native_symbols=f[f.sector.eq('native')].stock.nunique(),
      data_clock='Complete consecutive 09:15 five-minute primary or 25-minute archive prefix. At least five minutes after bar end. Native index volume is deliberately missing.',
      price_metadata='Returns in native vendor units. An official identifier transition or observed large discontinuity invalidates the close-to-open stock comparison. Authentic scheduled ex-actions separately flagged.'))
    print('Made',len(f),'strict traded and native snapshots',flush=True)

if __name__=='__main__':
    assemble()
