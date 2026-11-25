"""Refresh only prospective market outcomes and freeze small predeclared research references."""
from .common import *
from .acquire import grab,raw
from research.nifty_forecast_v16 import acquire as reference
from research.nifty_forecast_v14.volatility import fit_garch,filter_garch
from research.nifty_forecast_v15.sequential import RandomPanel,TICK,garch_paths,log_ticks,numpy_zip
from research.nifty_forecast_v15.scores import profile

HOLIDAY_URL=reference.DOCS['nse-2026-holidays']

def certified_snapshot(day):
    market='forward/alternate-market-receipts.json'
    up='forward/certification-probes.json'
    if not (OUT/market).is_file() or not (OUT/up).is_file():
        return None
    ir,stat=read(market)[:2]
    quote,full=read(up)[:2]
    if not all(x.get('sha256') for x in (ir,stat,quote,full)):
        return None
    def payload(r):
        p=OUT/r['file']
        assert sha(p)==r['sha256']
        return json.loads(raw(p))
    a=payload(ir)
    q=payload(stat)
    ru=payload(quote)
    fu=payload(full)
    nse=next(r for r in a['data'] if r['index']=='NIFTY 50')
    mark=next(r for r in q['marketState'] if r['market']=='Capital Market' and r['index']=='NIFTY 50')
    candle=next(r['live_ohlc'] for r in ru['data'].values() if r['instrument_token']=='NSE_INDEX|Nifty 50')
    last=next(r for r in fu['data'].values() if r['instrument_token']=='NSE_INDEX|Nifty 50')
    dates=(pd.Timestamp(a['timestamp']).date().isoformat(),pd.Timestamp(mark['tradeDate']).date().isoformat(),
           pd.to_datetime(candle['ts'],unit='ms',utc=True).tz_convert(IST).date().isoformat(),
           pd.to_datetime(int(last['last_trade_time']),unit='ms',utc=True).tz_convert(IST).date().isoformat())
    if mark['marketStatus']!='Closed' or any(x!=day for x in dates):
        return None
    fields=('open','high','low','close')
    nse_ohlc={k:float(nse['last' if k=='close' else k]) for k in fields}
    if not all(abs(candle[k]-nse_ohlc[k])<=.05 and abs(last['ohlc'][k]-nse_ohlc[k])<=.05 for k in fields):
        return None
    if abs(mark['last']-nse_ohlc['close'])>.05 or abs(last['last_price']-nse_ohlc['close'])>.05:
        return None
    return dict(day=day,nse_ohlc=nse_ohlc,upstox_ohlc=[candle[k] for k in fields],file=ir['file'],sha256=ir['sha256'],
                method='NSE matched closed market state and all-index snapshot, Upstox authenticated day OHLC and full quote',
                sources=[{k:r[k] for k in ('url','received','file','sha256')} for r in (ir,stat,quote,full)])

def match_published_close(ledger,snapshot):
    """Use the dated current-session candle if the broker history is still one session behind."""
    if snapshot is None:
        return
    ref=snapshot['day']
    checked=pd.Timestamp(ledger['checked_at']).tz_convert(IST)
    if checked<stamp(ref,'18:00'):
        return
    nse=next((r for r in ledger['sessions'] if r['day']==ref and r.get('nse_ohlc')),None)
    if nse is None:
        return
    cols=('open','high','low','close')
    reference_ohlc=[nse['nse_ohlc'][k] for k in cols]
    if any(abs(a-b)>.05 for a,b in zip(reference_ohlc,snapshot['upstox_ohlc'])):
        return
    assert sha(OUT/nse['file'])==nse['sha256']
    if nse['status']!='verified':
        nse.update(status='verified',upstox_ohlc=snapshot['upstox_ohlc'],
                   matched_via='Published NSE daily OHLC and dated authenticated Upstox one-day OHLC and full quote',
                   alternate_quote_sources=snapshot['sources'])
    known={r['day']:r['nse_ohlc']['close'] for r in ledger['sessions'] if r['status']=='verified'}
    source=reference.events(V4/'prospective-ledger.jsonl')
    for r in ledger['records']:
        sessions=r['target_sessions']
        r['completed_target_dates']=[d for d in sessions if d in known]
        if r['version']!='V4' or r['realized_return'] is not None or sessions[-1]!=ref:
            continue
        actual=[d for d in sorted(known) if r['reference_session']<d<=ref]
        if actual!=sessions:
            continue
        old=next(k for k in source if k['hash']==r['issue_hash'] and k['kind']=='FORECAST')
        reference.verify_files(old)
        frozen=old['payload']['forecasts'][str(r['horizon'])]
        assert frozen['target_sessions']==sessions and frozen['reference_close']==r['reference_close']
        y=known[ref]/r['reference_close']-1
        binary={}
        for name,p in frozen['binary_probabilities'].items():
            direction=int(y>0)
            binary[name]=dict(p=p,brier=(p-direction)**2,log_loss=-float(np.log(max(p if direction else 1-p,1.e-6))),
                              correct=bool((p>=.5)==direction))
        scores={}
        for name,x in frozen['distributions'].items():
            vals=reference.Distribution(x['atoms'],x['weights']).score(y)
            scores[name]={k:vals[k] for k in ('brier','log_loss','crps','p','predicted_mean')}
        r.update(maturity='resolved on original target',official_close=known[ref],realized_return=y,
                 scores=scores,binary_scores=binary,resolution_at=now(),resolution_method=nse.get('matched_via','Both official daily archives'),
                 outcome_source=dict(file=nse['file'],sha256=nse['sha256']))

def freeze_panel(ledger):
    file='forward/new-issues.json'
    if (OUT/file).is_file():
        return read(file)['records']
    current=pd.Timestamp(now()).tz_convert(IST)
    ref=current.date().isoformat()
    if ref!='2026-11-25' or current.hour<16:
        return []
    row=next((r for r in ledger['sessions'] if r['day']==ref and r['status']=='verified'),None)
    if row is None:
        row=certified_snapshot(ref)
        if row is None:
            return []
    mark=float(row['nse_ohlc']['close'])
    holidays={'2026-11-24','2026-12-25'}
    future=[d.date().isoformat() for d in pd.bdate_range('2026-11-26','2026-12-31') if d.date().isoformat() not in holidays]
    assert len(future)>=21 and future[20]=='2026-12-24'
    doc=grab(HOLIDAY_URL,'forward/nse-calendar.pdf')
    if doc.get('sha256') is None:
        # The prior immutable V12 research copy contains the same exchange notice.
        original=V12/'sources/docs/nse-2026-calendar.pdf'
        assert original.is_file()
        target=OUT/'forward/nse-calendar.pdf'
        target.write_bytes(original.read_bytes())
        doc.update(file='forward/nse-calendar.pdf',sha256=sha(target),archived_predecessor=original.relative_to(ROOT).as_posix())
    from pypdf import PdfReader
    content=' '.join(' '.join(p.extract_text().split()) for p in PdfReader(OUT/doc['file']).pages)
    assert 'December 25,2026' in content.replace(', ', ',') or '25-Dec-2026' in content or 'Christmas' in content
    original=csv('original-target-panel.csv',V17)
    x=original.dropna(subset=['original21','end_original21'])
    hist=np.expm1(x.loc[x.end_original21.le(FREEZE),'original21'].to_numpy(float))[-140:]
    magnitudes=np.quantile(np.abs(hist),(np.arange(64)+.5)/64)
    neutral=np.r_[-magnitudes[::-1],magnitudes]
    assert (neutral>0).sum()==64
    k='forward/monthly-neutral-law.npz'
    np.savez_compressed(OUT/k,arithmetic_returns=neutral,weights=np.ones(128)/128)
    source={'file':row['file'],'sha256':row['sha256'],'upstox_match':row['upstox_ohlc'],'nse_match':row['nse_ohlc'],
            'method':row.get('method','NSE signed daily series independently matched against Upstox historical candles'),
            'sources':row.get('sources',[])}
    nse_history=csv('official-index-closes.csv',V11).set_index('Unnamed: 0').nifty50.dropna().loc[FIRST:FREEZE]
    live=pd.Series({r['day']:r['nse_ohlc']['close'] for r in ledger['sessions'] if r['status']=='verified' and FREEZE<r['day']<=ref})
    live.loc[ref]=mark
    expected=[d.date().isoformat() for d in pd.bdate_range('2026-11-18',ref) if d.date().isoformat() not in holidays]
    assert sorted(live.index)==expected
    post=pd.concat([nse_history,live]).sort_index()
    assert post.iloc[-1]==mark and post.index.is_unique
    fund=100*np.diff(np.log(post.to_numpy(float)))
    spec=('gjr','student','none',None,True)
    g=fit_garch(fund,np.zeros_like(fund),spec)
    g['next_variance']=float(filter_garch(fund,np.zeros_like(fund),g,g['initial'])[-1])
    atoms=RandomPanel.create(ref,256)
    out=[]
    for h in HORIZONS:
        arr=garch_paths(atoms,h,g)
        tt=log_ticks(arr)
        label=f'forward/gjr-risk-{h}.npz'
        z=profile(np.exp(tt*TICK)[None,...],np.empty((0,4)),h,1.)
        vol=z['vol'][0]
        numpy_zip(OUT/label,dict(ohlc_log_ticks=tt))
        out.append(dict(name='cash_close_GJR_risk',horizon=h,target_sessions=future[:h],file=label,sha256=sha(OUT/label),
                        distribution='256 equal-weight coherent OHLC log tick paths anchored to the official index close',tick=TICK,seed=atoms.seed,
                        model_config=g,training_sessions=len(post),training_end=ref,training_start=post.index[0],
                        annualized_rv=dict(zip(['p10','p50','p90'],np.quantile(vol,[.1,.5,.9]).tolist()))))
    n=dict(name='monthly_neutral_reference',horizon=21,target_sessions=future[:21],file=k,sha256=sha(OUT/k),
           direction_p_up=.50,count=len(neutral),training_windows=len(hist),training_end=x.end_original21.max(),
           method='Equal weights on a symmetrized distribution of historical 21-session arithmetic return magnitudes, 140 mature windows',
           endpoint_return=dict(zip(['p10','p50','p90'],np.quantile(neutral,[.1,.5,.9]).tolist())))
    issued=pd.Timestamp(now()).tz_convert(IST)
    if issued>=stamp(future[0],'08:55'):
        return []
    panel=[{**r,'reference_session':ref,'reference_close':mark,'issued_at':issued.isoformat(),
            'cutoff':'after certified Nov 25 cash close','classification':'prospective research reference',
            'first_target_session':future[0],'target_session':r['target_sessions'][-1],
            'status':'pending first eligible target session'} for r in [n,*out]]
    save(file,dict(records=panel,close_source=source,holiday_source=doc,issued_at=issued.isoformat(),
                   requested_references_not_issued={
                    'opening GIFT, native V14, native V18':'The next scheduled premarket guard has not occurred at the time of this freeze.',
                    'monthly directional and V19 positioning':'Registration requires supporting matched evidence before a positioning forecast is issued.',
                    'IV':'No authenticated current options-chain snapshot was assembled for the same issue time.'}))
    return panel

def main():
    import sys
    reference.OUT=OUT
    reference.save=save
    if '--reuse-refresh' not in sys.argv or not (OUT/'forward-ledger.json').is_file():
        reference.forward()
    z=read('forward-ledger.json')
    z.pop('new_v16_issues',None)
    try:
        records=freeze_panel(z)
    except (KeyError,ValueError,AssertionError,OSError) as problem:
        z['new_issue_blocker']=f'{type(problem).__name__}: {problem}'
        records=[]
    z['new_v19_issues']=len(records)
    z['new_references']=records
    extra=certified_snapshot('2026-11-25')
    if extra:
        z['same_day_reference_source']=extra
        match_published_close(z,extra)
    z['historical_freeze']=FREEZE
    z['resolution_rule']='Preserve original distributions, classifications and dates. After 18:00 IST on the original last date, score only the complete reconciled session sequence. A dated authenticated Upstox day/full quote can verify an available NSE daily bar when broker history still lacks the date.'
    save('forward-ledger.json',z)
    print('Forward ledger archived with',len(z['records']),'legacy forecasts,',
          sum(r['realized_return'] is not None for r in z['records']),'resolutions and',len(records),'new frozen references',flush=True)

if __name__=='__main__':
    main()

