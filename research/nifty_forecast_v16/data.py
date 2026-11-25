"""Audit the cash labels, reconstruct eligible timestamps and build distinct session targets."""
from collections import defaultdict

from .common import *
from research.nifty_forecast_v15.data import Daily
from research.nifty_forecast_v15 import sessions as v15
from .replay import cohorts

OFF=v15.OFF
CLOSE6=tuple(v15.FOREIGN)
US=('spx','dow','tech')
EU=('ftse','dax','cac')
ASIA=('nikkei','hsi')
SECTOR_NAMES={
  'bank':'niftybank','financial':'niftyfinancialservices','it':'niftyit','energy':'niftyenergy',
  'auto':'niftyauto','defensive':'niftyfmcg','broad':'nifty500','ew':'nifty500equalweight'
}
DOM=('prior_return','prior_gap','prior_rth','rv21','cash5','cash21','breadth5','breadth21','finance','defensive','concentration',
     'vix_level','atm','iv_skew','iv_term','front_basis','same_contract_cash_gap','e_turn','e_impact','overnight_share')
GLOBAL=('spx','dow','tech','ftse','dax','cac','nikkei','hsi','fx','brent','wti','vix_move','dgs10_change','us_breadth5',
        'dollar_gold','us_stock_relative')
MORNING=('gap_visible','cash_first_bar','cash_prefix','cash_prefix_rv','cash_first_hour','open_breadth','open_bank_lead',
         'open_tech_lead','open_dispersion','open_defensive','etf_relative','etf_volume')
SETS={
  'domestic':DOM,'prior_return':('prior_return','rv21'),'domestic_finance':('prior_return','rv21','finance','defensive'),
  'domestic_breadth':('prior_return','rv21','breadth5','breadth21','concentration'),
  'global_equal':('eq6',),'us_single':('spx',),'six_cash':CLOSE6,'global_plus':GLOBAL,
  'global_extended':GLOBAL+('nikkei_partial','hsi_partial','fx_intraday','brent_intraday'),
  'global_only':('us_mean','europe_mean','asia_mean','tech_lead','fx','brent','vix_move'),
  'disagreement':('foreign_sd','us_asia','cross_sign','tech_lead','equity_vix','equity_fx','oil_diverge','us_local','cash_vs_gift'),
  'offshore_prior':v15.DOM+v15.OFF,
}
EXTRA_DAILY={'tech':('IXIX','America/New_York','16:05'),
             'cac':('^FCHI','Europe/Paris','17:40'),
             'fx':('USDINR','Asia/Kolkata','23:59'),
             'brent':('BZUSD','America/New_York','23:59'),
             'wti':('CLUSD','America/New_York','23:59'),
             'gift_day':('SGX_NIFTY','Asia/Kolkata','23:59')}
SECT_COLUMNS=['open','high','low','close']


def official():
    daily=Daily.load()
    p=daily.prices.copy()
    prices={k:[] for k in ['cash',*SECTOR_NAMES]}
    proofs=[]
    names={'cash':'nifty50',**SECTOR_NAMES}
    for day in p.index:
        f=V10/'sources/nse-daily'/f'{day}.csv'
        if not f.exists():
            raise FileNotFoundError(f)
        d=pd.read_csv(f,skipinitialspace=True)
        key=d['Index Name'].str.lower().str.replace(r'[^a-z0-9]','',regex=True)
        d=d.set_index(key)
        assert pd.to_datetime(d['Index Date'],dayfirst=True).dt.strftime('%Y-%m-%d').eq(day).all()
        columns=['Open Index Value','High Index Value','Low Index Value','Closing Index Value']
        for k,name in names.items():
            x=d.reindex([name])[columns].iloc[0]
            prices[k].append((day,*pd.to_numeric(x,errors='coerce').tolist()))
        proofs.append(dict(day=day,file=f.relative_to(ROOT).as_posix(),sha256=sha(f),
                           official=p.at[day,'close'],previous_source='V6 frozen cash chronology'))
    all_prices={k:pd.DataFrame(y,columns=['day',*SECT_COLUMNS]).set_index('day') for k,y in prices.items()}
    a=all_prices['cash']
    assert (a.index==p.index).all() and a.index[0]>=FIRST and a.index[-1]==FREEZE
    x=(a-p).abs().add_prefix('abs_delta_')
    w=a.add_prefix('nse_').join(p.add_prefix('v6_')).join(x)
    assert w.nse_open.notna().all()
    # The original horizon archives have earlier independently registered cash reference prices.
    # Any revised official mark is compared explicitly before either benchmark is used.
    write('cash-opening-reconciliation.csv',w,index=True)
    save('cash-source-audit.json',dict(days=len(a),first=a.index[0],last=a.index[-1],records=proofs,
          same_open=int(x.abs_delta_open.le(.05).sum()),same_close=int(x.abs_delta_close.le(.05).sum()),
          max_open_delta=float(x.abs_delta_open.max()),max_close_delta=float(x.abs_delta_close.max())))
    for k,y in all_prices.items():
        write(f'cash-panel/{k}.csv',y,index=True)
    return daily,all_prices


def read_bars(inventory):
    groups=defaultdict(list)
    proof=[]
    for r in inventory['records']:
        if r.get('candles',0)<=0 or 'file' not in r:
            continue
        z=pd.DataFrame(read(r['file'])['data']['candles'],columns=['t','open','high','low','close','volume','oi'])
        z.t=pd.to_datetime(z.t,utc=True).dt.tz_convert(IST)
        z=z[z.t.dt.strftime('%Y-%m-%d').between(FIRST,FREEZE)]
        groups[r['series']].append(z)
        proof.append(dict(series=r['series'],file=r['file'],sha256=r['sha256'],n=len(z),duration=r['bar_minutes']))
    result={}
    for k,series in groups.items():
        t=pd.concat(series,ignore_index=True).sort_values('t').drop_duplicates('t')
        good=(t.high>=t[['open','close']].max(axis=1))&(t.low<=t[['open','close']].min(axis=1))&(t.low>0)
        ret=t.loc[good].set_index('t')
        interval=5 if k=='gift' else 25
        if k in ('nikkei','hsi'):
            valid=(ret.index.day_of_week<5)
            # Normal Asia sessions, including lunch gaps. Late auction values can still enter via the completed daily source.
            wall=np.array(ret.index.strftime('%H:%M'))
            valid&=(wall>='05:30')&(wall<='12:00') if k=='nikkei' else (wall>='07:00')&(wall<='13:40')
            ret=ret.loc[valid]
        ret['last_possible_end']=ret.index+pd.Timedelta(minutes=interval)
        source_delay=15 if k in ('nikkei','hsi') else 5
        ret['available']=ret.last_possible_end+pd.Timedelta(minutes=source_delay)
        result[k]=ret
        write(f'sources/normalized/{k}-bars.csv.gz',ret,index=True)
    save('normalized-market-data.json',dict(records=proof,retained={k:len(v) for k,v in result.items()}))
    return result


def extra_daily():
    panel,receipt=v15.foreign()
    for key,(symbol,zone,time) in EXTRA_DAILY.items():
        p=V5/'sources'/f'g_{symbol}.json'
        z=pd.DataFrame(read(p.name,p.parent)['rows']).sort_values('day').drop_duplicates('day').set_index('day').loc[FIRST:FREEZE].copy()
        if key not in {'fx','brent','wti','gift_day'}:
            z=z.loc[pd.DatetimeIndex(z.index).day_of_week<5].copy()
        z['r']=np.log(z.close).diff()
        # FX, fossil fuel and GIFT daily records have vendor roll/date labels. Use a whole extra day beyond nominal local midnight.
        delay=24*60 if key in {'fx','brent','wti','gift_day'} else 60
        z['available']=[pd.Timestamp(f'{d}T{time}:00',tz=zone).tz_convert(IST)+pd.Timedelta(minutes=delay) for d in z.index]
        panel[key]=z
        receipt[key]=dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),timezone=zone,assumed_local_close=time,
                          buffer_minutes=delay,reconstructable_end_of_day_marks=len(z))
    return panel,receipt


def cash_bars():
    cash,hashes,_=v15.candles((V13/'sources/upstox').glob('nifty-5m-*'),5)
    nine={}; info={'nifty':hashes}
    for name in v15.SECTORS:
        root=V10/'sources/intraday' if name in v15.SECTORS[:4] else V15/'sources/market-intraday'
        nine[name],info[name],_=v15.candles(root.glob(f'{name}-*'),25)
    return cash,nine,info


def eligible(z,clock,field='available'):
    t=z[field].searchsorted(clock,side='right')-1
    if t<0:
        return None
    return z.iloc[t]


def age_minutes(t,end):
    return float((t-end)/pd.Timedelta(minutes=1))


def offshore_mark(b,day,prev,clock):
    day_stamp=stamp(day,clock)
    ref_end=stamp(prev,'15:30')
    a=eligible(b,ref_end,'last_possible_end')
    cur=eligible(b,day_stamp)
    if a is None or cur is None:
        return None
    if a.name.strftime('%Y-%m-%d')!=prev or cur.name.strftime('%Y-%m-%d')!=day:
        return None
    a_age=age_minutes(ref_end,a.last_possible_end)
    c_age=age_minutes(day_stamp,cur.last_possible_end)
    if a_age>25 or c_age>20:
        return None
    delay10=eligible(b,day_stamp-pd.Timedelta(minutes=10))
    late=eligible(b,day_stamp-pd.Timedelta(minutes=25))
    return dict(ref=a,now=cur,delay10=delay10,delay25=late,age=c_age,ref_age=a_age)


def build():
    d,prices=official()
    x=d.features.copy()
    p=prices['cash']
    dates=p.index
    day_gap=np.log(p.open/p.close.shift())
    day_rth=np.log(p.close/p.open)
    x['prior_return']=(day_gap+day_rth)
    x['prior_gap']=day_gap
    x['prior_rth']=day_rth
    ext,external=extra_daily()
    ib=read_bars(read('foreign-intraday-acquisition.json'))
    intraday,sector,source_files=cash_bars()
    receipts=[]; day_data=[]; targets=[]; local=[]; fill_obs=[]
    slices={5:{},21:{}}
    wins=pd.read_csv(V15/'original-windows.csv')
    for w in wins.itertuples(index=False):
        slices[w.horizon][w.origin]=(w.target,w.cohort)
    for i,day in enumerate(dates):
        if not i: continue
        prev=dates[i-1]
        nextday=dates[i+1] if i+1<len(dates) else None
        row=p.loc[day]
        old=p.at[prev,'close']
        y=dict(day=day,origin=prev,previous_close=old,official_open=row.open,official_close=row.close,
               gap=day_gap.loc[day],regular=day_rth.loc[day],one=np.log(row.close/old),label_gap=day,label_regular=day,label_one=day)
        if nextday:
            y.update(next_gap=day_gap.loc[nextday],label_next_gap=nextday,next_next_close=np.log(p.at[nextday,'close']/row.close),
                     label_next_next_close=nextday)
        for h,name in [(2,'two'),(3,'three'),(5,'five'),(10,'ten'),(21,'twentyone')]:
            if i+h-1<len(dates):
                target=dates[i+h-1]
                if h in slices and prev in slices[h]:
                    assert slices[h][prev][0]==target
                    y['cohort_'+name]=slices[h][prev][1]
                y[name]=np.log(p.at[target,'close']/old)
                y['label_'+name]=target
        for name in SECTOR_NAMES:
            t=prices[name]
            today,prior=t.at[day,'open'],t.at[prev,'close']
            oc=t.at[day,'close']
            if np.isfinite([today,prior,oc]).all() and min(today,prior,oc)>0:
                y[name+'_gap']=np.log(today/prior)
                y[name+'_rth']=np.log(oc/today)
                y[name+'_relative']=np.log(oc/prior)-y['one']
                for z0 in ('gap','rth','relative'):
                    y['label_'+name+'_'+z0]=day
        ca=intraday.get(day)
        full=ca is not None and len(ca)==75 and list(ca.index.strftime('%H:%M'))==list(pd.date_range(stamp(day,'09:15'),periods=75,freq='5min').strftime('%H:%M'))
        valid=ca is not None and len(ca)>=12 and ca.index[0].strftime('%H:%M')=='09:15'
        special=day in {'2025-10-21','2026-11-08'} or not valid
        if valid:
            first=ca.close.iloc[0]
            a=ca[ca.end<=stamp(day,'10:15')]
            if len(a)==12:
                hour=a.close.iloc[-1]
                y.update(firsthour=np.log(hour/row.open),label_firsthour=day,
                         firsthour_residual=np.log(hour/first),label_firsthour_residual=day,
                         remaining=np.log(row.close/hour),label_remaining=day,
                         regular_after_bar=np.log(row.close/first),label_regular_after_bar=day)
            if full:
                r=np.diff(np.log(np.r_[ca.open.iloc[0],ca.close]))
                y.update(session_risk=np.sqrt(r@r),label_session_risk=day)
                for theta in (.5,1.):
                    root=row.open+(old-row.open)*theta
                    levels=ca.low<=root if row.open>old else ca.high>=root
                    hits=np.flatnonzero(levels.to_numpy())
                    if row.open==old:
                        first_hit=0
                    else:
                        first_hit=int(hits[0]+1) if len(hits) else 76
                    fill_obs.append(dict(day=day,touch_fraction=theta,trigger_level=root,initial_gap=y['gap'],
                                         touched=int(first_hit<76),first_hit=first_hit,grid_bars=len(ca),cohort=cohorts(np.array([day]))[0]))
        y['cash_regular_grid']=int(full)
        y['cash_morning_eligible']=int(valid and not special)
        y['regular_weekday']=int(pd.Timestamp(day).weekday()<5 and not special)
        y['cohort']=cohorts(np.array([day]))[0]
        targets.append(y)
        for clk in CLOCKS:
            dec=stamp(day,clk)
            cc=clk=='17:00'
            domestic_day=day if cc else prev
            data=x.loc[domestic_day,list(dict.fromkeys(DOM+OFF+('dgs10_change','vix_move','gold_etf_risk','us_shock')))].to_dict()
            rs=dict(day=day,cutoff=clk,decision=dec.isoformat(),domestic_day=domestic_day,domestic_last_quote=stamp(domestic_day,'16:45').isoformat(),
                    domestic_v14_option_day=x.at[domestic_day,'option_day'])
            data.update(day=day,cutoff=clk,gift_roll_guard=int(pd.Timestamp(day).day<=2 or (pd.Timestamp(day).days_in_month-pd.Timestamp(day).day)<=6),
                        regular_morning=y['cash_morning_eligible'],weekday_morning=y['regular_weekday'])
            data['dollar_gold']=data['gold_etf_risk']
            data['us_stock_relative']=data['us_shock']
            for k,f in ext.items():
                q=eligible(f,dec)
                data[k]=float(q.r) if q is not None and np.isfinite(q.r) else np.nan
                rs[k+'_daily_session']=q.name if q is not None else None
                rs[k+'_daily_release']=q.available.isoformat() if q is not None else None
                rs[k+'_daily_receipt']=None
                rs[k+'_age_hours']=age_minutes(dec,q.available)/60 if q is not None else None
            for k in ('nikkei','hsi','fx','brent','spx','us_tech'):
                z=ib.get(k)
                if z is None: continue
                q=eligible(z,dec)
                rs[k+'_bar_timestamp']=q.name.isoformat() if q is not None else None
                rs[k+'_bar_available']=q.available.isoformat() if q is not None else None
                if q is None: continue
                if k in ('nikkei','hsi'):
                    b=eligible(ext[k],dec)
                    # An active partial session requires a fresh mark from today and a separate earlier complete session.
                    if b is not None and q.name.strftime('%Y-%m-%d')==day and b.name<day and age_minutes(dec,q.last_possible_end)<=60:
                        data[k+'_partial']=np.log(q.close/b.close)
                        rs[k+'_used_partial']=1
                elif k in ('fx','brent'):
                    b=eligible(z,stamp(prev,'15:30'),'last_possible_end')
                    if b is not None and b.name.strftime('%Y-%m-%d')==prev and q.name.strftime('%Y-%m-%d')==day and age_minutes(dec,q.last_possible_end)<=75:
                        data[k+'_intraday']=np.log(q.close/b.close)
            if 'gift' in ib:
                g=offshore_mark(ib['gift'],day,prev,clk)
            else:
                g=None
            if g:
                anchor,current=g['ref'],g['now']
                data.update(gift_proxy=np.log(current.close/anchor.close),gift_basis_ref=np.log(anchor.close/old),gift_age=g['age'])
                rs.update(gift_bar_timestamp=current.name.isoformat(),gift_bar_end=current.last_possible_end.isoformat(),
                          gift_bar_available=current.available.isoformat(),gift_anchor_bar=anchor.name.isoformat(),
                          gift_anchor_end=anchor.last_possible_end.isoformat(),gift_anchor_prior_cash=old,
                          gift_prior_mark=float(anchor.close),gift_morning_mark=float(current.close),gift_roll_guard=data['gift_roll_guard'],
                          gift_basis_points=float(anchor.close-old),gift_historical_receipt=None)
                for q0,s0 in [(g['delay10'],'10'),(g['delay25'],'25')]:
                    if q0 is not None and q0.name.strftime('%Y-%m-%d')==day:
                        data['gift_delay_minutes_'+s0]=np.log(q0.close/anchor.close)
                        rs['gift_delayed_'+s0+'_available']=q0.available.isoformat()
            if clk in ('09:25','10:20','17:00') and valid and not special:
                q=ca[ca.end<=dec-pd.Timedelta(minutes=5)]
                if len(q):
                    data['gap_visible']=np.log(ca.open.iloc[0]/old)
                    data['cash_first_bar']=np.log(ca.close.iloc[0]/ca.open.iloc[0])
                    data['cash_prefix']=np.log(q.close.iloc[-1]/ca.open.iloc[0])
                    data['cash_prefix_rv']=float(np.sqrt(np.square(np.diff(np.log(np.r_[ca.open.iloc[0],q.close]))).sum()))
                    rs['used_cash_bar_end']=q.end.iloc[-1].isoformat()
                    if len(q)>=12:
                        data['cash_first_hour']=np.log(q.close.iloc[11]/ca.open.iloc[0])
                    ret={}
                    for sk,pan in sector.items():
                        if day not in pan:
                            continue
                        b=pan[day][pan[day].end<=dec-pd.Timedelta(minutes=5)]
                        if not len(b):
                            continue
                        ref=q[q.end.le(b.end.iloc[-1])]
                        if not len(ref):
                            continue
                        ret[sk]=np.log(b.close.iloc[-1]/b.open.iloc[0])-np.log(ref.close.iloc[-1]/ca.open.iloc[0])
                        rs['used_'+sk+'_bar_end']=b.end.iloc[-1].isoformat()
                        if sk=='etf':
                            data['etf_volume']=np.log1p(b.vol.sum())
                    if all(k in ret for k in ('bank','financial','it','auto')):
                        z0=np.array([ret[k] for k in ['bank','financial','it','auto']])
                        data.update(open_breadth=(z0>0).mean(),open_bank_lead=z0[:2].mean()-z0[2:].mean(),
                                    open_tech_lead=z0[2]-z0[:2].mean(),open_dispersion=z0.std(),
                                    open_defensive=ret.get('defensive',np.nan)-ret['auto'],etf_relative=ret.get('etf',np.nan))
            row6=np.array([data[k] for k in CLOSE6],float)
            data['eq6']=row6.mean() if np.isfinite(row6).all() else np.nan
            data['foreign_sd']=row6.std() if np.isfinite(row6).all() else np.nan
            data['cross_sign']=float(abs(np.sign(row6).mean())) if np.isfinite(row6).all() else np.nan
            for keys,k in [(US,'us_mean'),(EU,'europe_mean'),(ASIA,'asia_mean')]:
                data[k]=sum(data[s] for s in keys)/len(keys)
            data['us_asia']=data['us_mean']-data['asia_mean']
            data['tech_lead']=data['tech']-data['spx']
            data['equity_vix']=data['eq6']*data['vix_move']
            data['equity_fx']=data['eq6']*data['fx']
            data['oil_diverge']=data['brent']-data['eq6']
            data['us_local']=data['spx']-data['prior_return']
            data['cash_vs_gift']=data.get('gift_proxy',np.nan)-data['eq6']
            data['gap_scaled']=data.get('gap_visible',np.nan)/(max(.035,data['atm'])/np.sqrt(252))
            data['gap_finance']=data.get('gap_visible',np.nan)*data.get('open_bank_lead',np.nan)
            data['gap_broad']=data.get('gap_visible',np.nan)*data.get('open_breadth',np.nan)
            data['abs_gap_scaled']=abs(data['gap_scaled'])
            data['foreign_after_gap']=data['eq6']-data.get('gap_visible',np.nan)
            if clk in CLOCKS[:4]:
                assert 'used_cash_bar_end' not in rs and domestic_day<day
            for f,t in rs.items():
                if t is not None and (f.endswith('_release') or f.endswith('_available') or f.startswith('used_') or f=='domestic_last_quote'):
                    assert pd.Timestamp(t)<=dec,(day,clk,f,t)
            day_data.append(data)
            receipts.append(rs)
        if valid:
            local.append(dict(day=day,regular=bool(not special),open_0915=float(ca.open.iloc[0]),official_open=float(row.open),
                              official_close=float(row.close),bars=len(ca),day_of_week=pd.Timestamp(day).day_name(),verified_75=bool(full)))
    write('decision-features.csv.gz',pd.DataFrame(day_data))
    write('information-clock.csv.gz',pd.DataFrame(receipts))
    write('session-targets.csv',pd.DataFrame(targets))
    write('cash-bar-identity-audit.csv',pd.DataFrame(local))
    write('gap-fill-events.csv',pd.DataFrame(fill_obs))
    save('source-clock-specification.json',dict(foreign_daily=external,
         foreign_intraday={'gift':'5-minute close + five minute buffer, same dated morning, age <=20 minutes; previous 15:30 anchor age <=25 minutes',
           'nikkei':'25-minute candle start + 25m + 15m reference latency. Normal local trading, partial today only within one hour.',
           'hsi':'25-minute candle start + 25m + 15m reference latency. Normal local trading, partial today only within one hour.',
           'fx_oil':'25-minute candle start + 25m + 5m. Same date and max 75m age. Return against previous close-time mark.',
           'spx_us_tech':'Observed interval inventory. Prior local daily close used for US models.'},
         domestic_bar_files=source_files,macro_source_files=[(V12/'external-publication-alignment.csv').relative_to(ROOT).as_posix(),
            (V13/'foreign-risk-clock.csv').relative_to(ROOT).as_posix(),(V14/'supplemental-clock.csv').relative_to(ROOT).as_posix()],
         no_receipt='Provider response arrival in 2026 is archived separately. Recorded bar time plus conservative delay is a historical estimate.',
         expiry_guard='Predeclare exclusion of final seven and first two calendar days each month. Contract IDs unavailable in the Upstox continuous alias.'))
    a=pd.DataFrame(day_data)
    print('Prepared',len(targets),'cash outcome days and',len(receipts),'timestamped forecasts;',
          a[a.cutoff.eq('08:55')].gift_proxy.notna().sum(),'eligible GIFT marks at 08:55',flush=True)

if __name__=='__main__':
    build()
