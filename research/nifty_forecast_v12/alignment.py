"""Align published expiries and causal EOD features to planned trading-session endpoints."""
import requests
from .common import *
from research.nifty_forecast_v9.run_models import cohort_queries

HOLIDAYS={
  2025:'02-26 03-14 03-31 04-10 04-14 04-18 05-01 08-15 08-27 10-02 10-22 11-05 12-25',
  2026:'01-26 03-03 03-26 03-31 04-03 04-14 05-01 05-28 06-26 09-14 10-02 10-20 11-10 11-24 12-25',
}
# Announced dates only enter an in-progress historical forecast after announcement.
AMENDMENTS=[('2026-01-12','2026-01-15',False,'https://nsearchives.nseindia.com/content/circulars/CMTR72260.pdf'),
            ('2026-01-16','2026-02-01',True,'https://nsearchives.nseindia.com/content/circulars/CMTR72349.pdf'),
            ('2025-09-22','2025-10-21',True,'https://nsearchives.nseindia.com/content/circulars/CMTR70319.pdf')]
ANNUAL={
  2025:'https://nsearchives.nseindia.com/content/circulars/CMTR65587.pdf',
  2026:'https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf',
}
FOMC={
  2025:'01-29 03-19 05-07 06-18 07-30 09-17 10-29 12-10',
  2026:'01-28 03-18 04-29 06-17 07-29 09-16 10-28 12-09',
}
RBI={
 '2025-03-26':('2025-04-09 2025-06-06 2025-08-06 2025-10-01 2025-12-05 2026-02-06',
               'https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60062'),
 '2026-03-23':('2026-04-08 2026-06-05 2026-08-05 2026-10-07 2026-12-04',
               'https://www.rbi.org.in/Scripts/FS_PressRelease.aspx?prid=62422'),
}


def calendar(origin):
    dates=pd.date_range(pd.Timestamp(origin)+pd.Timedelta(days=1),'2026-12-31')
    holidays={f'{y}-{day}' for y,items in HOLIDAYS.items() for day in items.split()}
    added={'2026-11-08'}  # Muhurat Trading already stated in the 2026 circular.
    for received,date,opened,_ in AMENDMENTS:
        if received>origin:continue
        if opened:added.add(date)
        else:holidays.add(date)
    return [d for x in dates if (d:=x.date().isoformat()) in added or (x.weekday()<5 and d not in holidays)]


def term_iv(g,target,allow_nearest=True):
    lower=g[g.dte.le(target)].tail(1)
    upper=g[g.dte.ge(target)].head(1)
    if not lower.empty and not upper.empty:
        a,b=lower.iloc[0],upper.iloc[0]
        dt=b.dte-a.dte
        if dt==0:return float(a.atm_iv),a.expiry,b.expiry,'exact'
        if b.total_variance>=a.total_variance:
            w=(target-a.dte)/dt
            var=(1-w)*a.total_variance+w*b.total_variance
            return float(np.sqrt(var*365/target)),a.expiry,b.expiry,'interpolated'
        return float('nan'),a.expiry,b.expiry,'nonmonotone total variance'
    if allow_nearest and len(g):
        q=g.iloc[np.argmin(abs(g.dte.to_numpy()-target))]
        return float(q.atm_iv),None,None,'nearest annualized IV'
    return np.nan,None,None,'unbracketed'


def align():
    official=matrix('official-index-closes.csv',V11)
    origins=matrix('price.csv').index
    table=pd.read_csv(OUT/'surface-quality.csv',low_memory=False)
    accepted=table[table.iv_status.eq('accepted')]
    groups={(d,m):g.sort_values('dte') for (d,m),g in accepted.groupby(['day','method'])}
    lookup={(d,e,m):law for (d,e,m),law in bundle_entries(OUT/'option-density-atoms.npz')}
    schedules={d:calendar(d) for d in origins}
    p={h:matrix(f'labels-{h}.csv') for h in [5,21]}
    mapping={};archive=[];bundle=[];rows=[]
    for origin in origins:
        location=official.index.get_loc(origin)
        for h in [5,21]:
            planned=schedules[origin][h-1]
            actual=p[h].at[origin,'endpoint']
            actual=actual if isinstance(actual,str) else None
            origin_days=(pd.Timestamp(planned)-pd.Timestamp(origin)).days
            for mode,method,lag,rule in [
                 ('TRADE','TRADE',1,'nearest'),('LAG2','TRADE',2,'nearest'),('LAG5','TRADE',5,'nearest'),
                 ('SAME_CLOSE','TRADE',0,'nearest'),('LIQUID','LIQUID',1,'nearest'),('SETTLEMENT','SETTLEMENT',1,'nearest'),
                 ('RATE_ZERO','RATE_ZERO',1,'nearest'),('RATE_HIGH','RATE_HIGH',1,'nearest'),
                 ('SMOOTH','SMOOTH',1,'nearest'),('TRUNCATED','TRUNCATED',1,'nearest'),
                 ('FUTURE_FORWARD','FUTURE_FORWARD',1,'nearest'),('LONGER','TRADE',1,'longer'),
                 ('BRACKET','TRADE',1,'bracket'),('NATURAL','TRADE',1,'natural')]:
                assert location>=lag
                day=official.index[location-lag]
                elapsed=(pd.Timestamp(origin)-pd.Timestamp(day)).days
                target=origin_days+elapsed
                z=groups.get((day,method))
                row={'horizon':h,'origin':origin,'decision_cut':'inherited next-session 09:10 IST; risk source lagged to before origin','option_source_day':day,
                     'source_lag_sessions':lag,'version':mode,'planned_endpoint':planned,'actual_endpoint_for_scoring':actual,
                     'target_dte_at_source':target,'target_dte_at_origin':origin_days,
                     'planned_matches_actual':None if actual is None else planned==actual}
                if z is None:
                    rows.append({**row,'status':'no eligible reconstructed expiries'});continue
                alive=z[z.expiry.gt(origin)]
                g=alive
                if rule=='longer':g=g[g.dte.ge(target+4)]
                if rule=='natural':g=g[g.expiry.eq(planned)]
                if g.empty:
                    rows.append({**row,'status':'alignment unavailable'});continue
                selected=g.iloc[np.argmin(abs(g.dte.to_numpy()-target))]
                if abs(selected.dte-target)>(15 if h==5 else 30):
                    rows.append({**row,'status':'nearest expiry too far'});continue
                iv,lo,hi,status=term_iv(alive,target,allow_nearest=rule!='bracket')
                if rule=='bracket' and status not in ['exact','interpolated']:
                    rows.append({**row,'status':status,'lower_expiry':lo,'upper_expiry':hi});continue
                iv7,*_=term_iv(z,7);iv30,*_=term_iv(z,30)
                expiry=selected.expiry
                source_law=lookup.get((day,expiry,method))
                qlaw=None
                if source_law is not None and rule!='bracket':
                    if rule=='natural':
                        # Directly observe the older absolute strike/forward law on the exactly
                        # scheduled expiry; score its subset only where the actual endpoint agrees.
                        atoms=(1+source_law.a)*selected.forward/official.nifty50.loc[origin]-1.
                    else:
                        # Explicit shape/tenor approximation. Forward carry rescales in log terms;
                        # this transformation does not identify a law at the target maturity.
                        k=np.sqrt(origin_days/float(selected.dte))
                        carry=np.log(selected.forward/selected.spot)*origin_days/selected.dte
                        atoms=np.expm1(np.log1p(source_law.a)*k+carry)
                    qlaw=Distribution(atoms,source_law.w)
                rows.append({**row,'status':'ok','expiry':expiry,'source_dte':selected.dte,'maturity_gap_days':selected.dte-target,
                  'actual_expiry_gap_days':None if actual is None else (pd.Timestamp(expiry)-pd.Timestamp(actual)).days,
                  'natural_planned':expiry==planned,'natural_realized':None if actual is None else expiry==actual,
                  'lower_expiry':lo,'upper_expiry':hi,'bracket_status':status,
                  'iv_nearest':selected.atm_iv,'iv_bracket':iv,'iv7':iv7,'iv30':iv30,'iv_term':iv30-iv7,
                  'iv_target_total_sd':float(selected.atm_iv*np.sqrt(origin_days/365.)),
                  'atm_straddle':selected.atm_straddle,'straddle_horizon_scaled':float(selected.atm_straddle*np.sqrt(origin_days/selected.dte)),
                  'iv_skew':selected.skew_down_minus_up,'iv_curvature':selected.curvature,
                  'parity_mad_fraction':selected.parity_mad_fraction,'option_forward_basis':selected.forward_basis,
                  'future_parity_gap':selected.future_parity_gap,'density_available':qlaw is not None,
                  'density_external_mass':selected.external_mass,'density_forward_skew':selected.implied_skew_moment,
                  'density_priced_down5':selected.density_five_pct_down})
                if qlaw is not None:
                    archive.append(qlaw);bundle.append((h,mode,origin,planned))
    m=pd.DataFrame(rows)
    write('horizon-alignment.csv',m)
    save('market-density-alignment.json',pack_bundle('laws/aligned-Q.npz',bundle,archive))
    save('calendar-audit.json',{'calendar_sources':ANNUAL,'amendments':AMENDMENTS,
         'calendar_note':'Planned endpoints use published weekday/holiday rules and as-known special-session notices. Histories label actual endpoints independently. Incomplete notice coverage appears as planned/realized disagreement.',
         'natural_subset':'Exact listed versus scheduled date, additionally actual target agreement in retrospective scoring.',
         'volume_and_timing':'One observed archive-session lag by default; no forward-filling gaps. The same-close source variant is diagnostic.'})
    print('Aligned',sum(m.status.eq('ok')),'market snapshots and',len(archive),'priced shape/expiry laws',flush=True)


def cash_futures():
    data=pd.read_csv(OUT/'sources/nifty-udiff.csv.gz',low_memory=False)
    f=data[data.kind.eq('IDF')&data.volume.gt(0)&data.close.gt(0)&data.expiry.gt(data.day)].copy()
    market=matrix('official-index-closes.csv',V11)
    rows=[];prior=None
    for day,g in f.groupby('day',sort=True):
        g=g.sort_values('expiry').drop_duplicates('expiry')
        if len(g)<2:continue
        a,b=g.iloc[0],g.iloc[1]
        if prior is None:
            same=np.nan;roll=False
        else:
            d,old=prior
            available=old[old.id.eq(a.id)&old.lot.eq(a.lot)]
            same=np.log(a.close/available.close.iloc[0])-np.log(a.spot/available.spot.iloc[0]) if len(available) else np.nan
            roll=a.id!=old.id.iloc[0]
        term=(pd.Timestamp(b.expiry)-pd.Timestamp(a.expiry)).days
        rows.append({'day':day,'front_expiry':a.expiry,'front_id':int(a.id),'front_basis':np.log(a.close/a.spot),
                     'curve_30d':np.log(b.close/a.close)*30/max(5,term),'roll_event':int(roll),
                     'same_contract_cash_gap':same,'front_volume_share':a.volume/g.volume.sum(),
                     'front_oi_change_over_volume':a.oi_change/max(1,a.volume*a.lot),
                     'contracts_traded':len(g)})
        prior=day,g
    frames=pd.DataFrame(rows).set_index('day').reindex(market.index)
    write('futures-observed.csv',frames,index=True)
    return frames


def publication_sources():
    urls={
      'nse-2025-calendar':ANNUAL[2025],'nse-2026-calendar':ANNUAL[2026],
      'fomc-schedule-2025-26':'https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm',
      'rbi-2025-schedule':RBI['2025-03-26'][1],'rbi-2026-schedule':RBI['2026-03-23'][1],
      'india-vix-methodology':'https://nsearchives.nseindia.com/web/sites/default/files/inline-files/India_VIX_comp_meth.pdf',
      'index-review-calendar':'https://www.niftyindices.com/resources/index-rebalancing-schedule',
      **{f'nse-amendment-{d}':u for _,d,_,u in AMENDMENTS},
    }
    rows=[]
    for k,url in urls.items():
        try:
            r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=5)
            log={'name':k,'source':url,'http_status':r.status_code,'retrieved':now()}
            if r.ok:
                p=OUT/'sources/docs'/(k+('.pdf' if 'pdf' in url else '.html'))
                p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(r.content)
                log.update(path=p.relative_to(OUT).as_posix(),sha256=sha(p))
        except requests.RequestException as e:log={'name':k,'source':url,'unavailable':str(type(e).__name__)}
        rows.append(log)
    save('publication-source-receipts.json',rows)


def refresh():
    from research.nifty_forecast_v9 import acquire
    d=OUT/'refresh';d.mkdir(parents=True,exist_ok=True)
    acquire.OUT=d
    acquire.save=lambda k,v:save('refresh/'+k,v)
    acquire.write=lambda k,v,index=False:write('refresh/'+k,v,index=index)
    acquire.run()
    summary=read('acquisition.json',d)
    current=pd.read_csv(d/'acquired-candles.csv')
    new=sorted(current.loc[current.instrument.eq('nifty_spot')&current.day.gt(FREEZE),'day'].unique())
    previous=read('refresh-summary.json',V11)['dates']
    save('refresh-summary.json',{'closed_sessions':new,'additional_vs_V11':sorted(set(new)-set(previous)),
          'completed_bound':summary['chosen_completed_boundary'],'validated_records':len(current),
          'official_checks':summary['official_crosscheck'],'frozen_through':FREEZE})


if __name__=='__main__':
    import sys
    {'align':align,'sources':publication_sources,'refresh':refresh,'futures':cash_futures}[sys.argv[1]]()
