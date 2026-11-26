"""Run the genuine cutoff under the frozen decision rules, with no backdating."""
from urllib.parse import quote

from .common import *
from .forward import guard_day,ledger,broker,configure,stage,targets,OPEN,NATIVE,STUDY_DAY,END,API,time
from .laws import Law
from research.nifty_forecast_v22 import panel as vp
from research.nifty_forecast_v22 import analogues as old
from research.nifty_forecast_v22.learning import target_block
from research.nifty_forecast_v17 import gift


def local_clock_marks(known):
    marks=[]
    index_extra=[]
    for day,item in sorted(known.items()):
        if day>=STUDY_DAY:
            continue
        base=OUT if item['archive']=='V23' else root_for(int(item['archive'][1:]))
        source=base/item['file']
        assert sha(source)==item['sha256']
        a=pd.read_csv(source,skipinitialspace=True)
        normalized=a['Index Name'].str.casefold().str.replace(' ','',regex=False)
        w=dict(day=day)
        for k in ('niftybank','nifty500','nifty50','nifty500equalweight'):
            z=a.loc[normalized.eq(k),'Closing Index Value']
            w[k]=float(z.iloc[0]) if len(z)==1 else np.nan
        assert abs(w['nifty50']-item['ohlc']['close'])<=.05
        index_extra.append(w)
        marks.append(dict(code='india',day=day,available=stamp(day,END),issue=stamp(day,OPEN),
                          ohlc_valid=True,role='primary',**item['ohlc']))
    return marks,pd.DataFrame(index_extra).set_index('day')


def live_state(known,cutoff):
    tape=csv('international-daily-book.csv.gz',V22)
    foreign=csv('forward/completed-foreign-marks.csv.gz')
    local,extra=local_clock_marks(known)
    z=pd.concat([tape,foreign,pd.DataFrame(local)],ignore_index=True)
    z['available']=pd.to_datetime(z.available,utc=True,format='mixed')
    z['issue']=pd.to_datetime(z.issue,utc=True,format='mixed')
    # No subsequent cash observation is present. The final row is an unobserved origin.
    z=z[z.available.le(cutoff)].copy().sort_values(['code','day'])
    assert z[z.day.gt(FREEZE)].available.le(cutoff).all()
    for key,(_,m) in vp.FX.items():
        if m==-1:
            z.loc[z.code.eq('fx_'+key.lower()),'close']=1./z.loc[z.code.eq('fx_'+key.lower()),'close']
    z['log_close']=np.log(z.close)
    z['r1']=z.groupby('code').log_close.diff()
    z['r5']=z.groupby('code').log_close.diff(5)
    z['rate5']=z.groupby('code').close.diff(5)
    sd=z.groupby('code').r1.transform(lambda s:s.shift().rolling(21,min_periods=16).std())
    z['z1']=(z.r1/sd.clip(.002)).clip(-7,7)
    book={f:{k:vp.earlier_book(a,f) for k,a in z.groupby('code',sort=False)} for f in ('r1','r5','rate5','z1','log_close')}
    catalog=csv('market-universe-audit.csv',V22)
    primary=catalog.loc[catalog.primary_eligible,'code'].to_list()
    a=z[z.code.eq('india')].copy()
    stub=pd.DataFrame([dict(code='india',day=STUDY_DAY,available=stamp(STUDY_DAY,END).tz_convert('UTC'),issue=cutoff.tz_convert('UTC'),
                            ohlc_valid=False,open=np.nan,high=np.nan,low=np.nan,close=np.nan)])
    a=pd.concat([a,stub],ignore_index=True)
    a['ohlc_valid']=a.ohlc_valid.eq(True).to_numpy(dtype=bool)
    pc=csv('global-pca-loadings.csv',V22).set_index('utc_day')
    refs=pd.DataFrame(columns=['cohort_5','cohort_21','end_0_5','return_0_5','end_0_21','return_0_21'])
    call=vp.cash
    original=call()
    extended=pd.concat([original,extra],ignore_index=False).sort_index()
    vp.cash=lambda:extended
    try:
        f,_,_=vp.market_tasks(a,book,primary,pc,refs)
    finally:
        vp.cash=call
    row=f.iloc[-1]
    assert row.day==STUDY_DAY and row.last_local_available_ns<cutoff.value
    return row


def month_paths(known,cutoff):
    now_state=live_state(known,cutoff)
    h=21
    data=target_block(csv('international-feature-panel.csv.gz',V22),h)
    historical=np.load(V22/'local-observed-paths.npz')['path_21']
    p=pd.to_datetime(data.day).dt.to_period('W-SUN').astype('str').to_numpy()
    codes=data.code.to_numpy();regions=data.region.to_numpy()
    sd=data.raw_daily_sigma.to_numpy()
    labels=data.mature_ns.to_numpy()
    ok=np.isfinite(historical).all(axis=(1,2))&np.isfinite(sd)&(labels<cutoff.value)&(data.issue_ns.to_numpy()>=cutoff.value-330*86_400_000_000_000)
    rows=np.flatnonzero(ok)
    x=data[list(old.STATE_FIELDS)].to_numpy(float)
    cv=now_state[list(old.STATE_FIELDS)].to_numpy(float)
    a,d,n,penalty=old.state_space(x[rows],cv)
    ac=a-a.mean(axis=0);mag=np.abs(data.normalized.to_numpy()[rows]);mag-=mag.mean()
    relevance=np.linalg.solve(ac.T@ac/len(a)+1.75*np.eye(a.shape[1]),ac.T@mag/len(a))
    relevance=1.+1.75*np.minimum(1.,np.abs(relevance)/max(.01,np.median(np.abs(relevance))))
    dist=np.full(len(codes),np.inf)
    dist[rows]=(d*d*relevance).sum(axis=1)/(n.clip(1)*relevance.mean())+penalty
    ind=rows[codes[rows]=='india']
    mixed=old.matches(np.argsort(dist[rows],kind='stable'),rows,codes,regions,p,max_per_week=2,max_per_region=24,n=48)
    india=old.matches(np.arange(len(ind))[::-1],ind,codes,regions,p,max_per_week=2,max_per_region=48,n=48)
    assert len(mixed)>=35 and len(india)>=35 and len(set(codes[mixed]))>=3
    ref=next(r for r in read('forward-ledger.json')['inherited_v19'] if r['horizon']==21 and r['name']=='cash_close_GJR_risk')
    ref_path=root_for(19)/ref['source_artifact']
    assert sha(ref_path)==ref['sha256'] and ref['reference_session']==max(d for d in known if d<STUDY_DAY)
    with np.load(ref_path,allow_pickle=False) as fetched:
        risk_path=fetched['ohlc_log_ticks']*ref['tick']
    anchor=float(old.path_variables(risk_path)['rv'].mean())
    rv=float(now_state.raw_daily_sigma*np.sqrt(252))
    save('forward/live-market-state.json',dict(assembled_at=now(),information_cutoff=cutoff.isoformat(),reference_close=now_state.reference,
         comparison_foreign_marks=int(now_state.foreign_available),input_fields={k:float(now_state[k]) if np.isfinite(now_state[k]) else None
         for k in old.STATE_FIELDS},gjr_anchor=anchor,source_law=ref['source_artifact'],law_sha256=ref['sha256'],local_trailing_rv=rv))
    out=[]
    for key,idx in [('india',india),('mixed',mixed)]:
        w=old.member_weights(idx,np.zeros(len(codes)) if key=='india' else dist,p)
        path=historical[idx].astype(float)*(now_state.raw_daily_sigma/sd[idx])[:,None,None]
        drift=float(w@path[:,-1,3])
        path-=drift*np.arange(1,h+1)[None,:,None]/h
        factor=float(np.clip(anchor/(w@old.path_variables(path)['rv']),.45,2.5))
        path*=factor
        v=old.path_variables(path)
        members=[dict(market=codes[j],origin=data.day[j],target=data.target_day[j],mature_ns=int(labels[j]),weight=float(q)) for j,q in zip(idx,w,strict=True)]
        assert all(r['mature_ns']<cutoff.value for r in members)
        out.append(dict(name=f'V22_architecture_{key}_monthly_path',targets=ref['target_sessions'],returns=v['terminal'],weights=w,
             path=path,source_sha256=ref['sha256'],kind='prospective path forecast with V22 analogue shape and frozen V19 forward GJR anchor',
             members=members,annualized_rv=float(w@v['rv']),forecast_range=float(w@v['range']),p_expansion=float(w@(v['rv']>1.25*rv)),
             source='forward/live-market-state.json',config=dict(anchor=anchor,drift=drift,scale=factor,known_frozen_donors_end=FREEZE)))
    return out


def eligible_mark(rows,date,cut,max_age,ref=False):
    out=[]
    for b in rows:
        st=pd.Timestamp(b[0]).tz_convert(IST)
        end=st+pd.Timedelta(minutes=5)
        avail=end+pd.Timedelta(minutes=5)
        guard=end if ref else avail
        if st.date().isoformat()==date and guard<=cut and (cut-end).total_seconds()<=60*max_age and b[4]>0:
            out.append((end,avail,float(b[4])))
    return max(out) if out else None


def opening(cutoff,known):
    stage=read('forward/pre-cutoff-staging.json')
    origin=stage['latest_cash']
    pre=stage['previous_gift_receipt']
    assert pre.get('file') and sha(OUT/pre['file'])==pre['sha256']
    prev=eligible_mark(read(pre['file'])['candles'],origin,stamp(origin,'15:30'),25,True)
    suffix=quote(stage['gift_key'],safe='')+'/minutes/5'
    bars,r=broker('gift-morning',API.replace('historical-candle/','historical-candle/intraday/')+suffix,cutoff)
    current=eligible_mark(bars,STUDY_DAY,cutoff,20)
    if current is None or prev is None:
        return None,r|dict(eligible_previous=bool(prev),eligible_morning=bool(current),
                            reason='the 08:55 model requires both dated GIFT bars with original guards')
    old_table=csv('gift-decision-clock.csv',root_for(17))
    t=old_table[old_table.clock.eq('08:55')&old_table.return_1530.notna()&old_table.day.le(FREEZE)].sort_values('day').tail(160)
    assert len(t)>=gift.MIN
    expected=np.log(current[2]/prev[2])
    atoms=np.expm1(expected+np.quantile(t.gap-t.return_1530,gift.Q))
    r.update(eligible_previous=True,eligible_morning=True,selected_prior_bar_end=prev[0].isoformat(),
             selected_prior_close=prev[2],selected_morning_bar_end=current[0].isoformat(),selected_morning_model_availability=current[1].isoformat(),
             selected_morning_close=current[2],reference_official_close=known[origin]['ohlc']['close'])
    return dict(name='V17_GIFT_0855_anchored_opening_gap',targets=[STUDY_DAY],returns=atoms,weights=np.ones(len(atoms))/len(atoms),
                kind='V17 opening-gap forecast using original 15:30 anchor and 08:55 buffer',source=r['file'],source_sha256=r['sha256'],
                config=dict(train_n=len(t),last_mature=t.day.iloc[-1],prior_reference_bar=prev[0].isoformat(),
                            current_bar=current[0].isoformat(),source_model_sha256=sha(Path(gift.__file__)))),r


def sleep_until(edge):
    while True:
        second=(edge-pd.Timestamp(now())).total_seconds()
        if second<=0:
            return
        time.sleep(min(20,second))


def emit(items,cut,known,configuration):
    refs=targets(STUDY_DAY)
    old_issues=read('forward/issued.json')['issues'] if (OUT/'forward/issued.json').exists() else []
    new=[]
    for rec in items:
        if any(a['model']==rec['name'] and a['target_sessions']==rec['targets'] for a in old_issues):
            continue
        at=pd.Timestamp(now())
        if not cut<=at<=cut+pd.Timedelta(seconds=configuration['preauction_processing_seconds']):
            break
        assert rec['targets']==refs[:len(rec['targets'])] and rec['targets'][-1]<=LAST
        law=Law.build(rec['returns'],rec['weights'])
        aid=rec['name']
        path=OUT/f'forward/laws/{aid}.npz';path.parent.mkdir(parents=True,exist_ok=True)
        payload=dict(atoms=rec['returns'],weights=rec['weights'])
        if 'path' in rec:
            p=rec['path']
            assert np.all(p[:,:,1]>=np.maximum(p[:,:,0],p[:,:,3])-1.e-8)
            assert np.all(p[:,:,2]<=np.minimum(p[:,:,0],p[:,:,3])+1.e-8)
            payload['ohlc_log_relative']=p
            write(f'forward/laws/{aid}-donors.csv',pd.DataFrame(rec['members']))
        if 'close_log_returns' in rec:
            payload['close_log_returns']=rec['close_log_returns']
            payload['annualized_volatility']=rec['realized_volatility']
        np.savez_compressed(path,**payload)
        a=law.quantiles([.1,.5,.9])
        date=max(q for q in known if q<STUDY_DAY)
        details={k:v for k,v in rec.items() if k not in ('name','returns','weights','path','members','targets','close_log_returns','realized_volatility')}
        seen=pd.Timestamp(now())
        key_config=hashlib.sha256(json.dumps(rec['config'],sort_keys=True,default=str).encode()).hexdigest()
        new.append(dict(model=aid,decision_cutoff=cut.isoformat(),issued_at=seen.isoformat(),target_sessions=rec['targets'],
             reference_session=date,reference_close=known[date]['ohlc']['close'],n_atoms=len(law.atoms),
             law_file=path.relative_to(OUT).as_posix(),law_sha256=sha(path),configuration_sha256=key_config,
             architecture_sha256=sha(Path(__file__)),p_up=law.positive(),expected_return=law.moments()[0],q10=a[0],median=a[1],q90=a[2],**details))
    if new:
        save('forward/issued.json',dict(issues=old_issues+new,captured_at=now()))
    ledger()
    return new


def native_check():
    at=guard_day()
    due=stamp(STUDY_DAY,NATIVE)
    cfg=configure()
    known=read('forward/native-source-readiness.json')
    option_books=sum('file' in a for a in known['authenticated_options'])
    state_ok=(OUT/'forward/v14-gjr-state-receipt.json').is_file()
    # The risk state and upstream books are not the native return law.
    unresolved=('Newly dated exact V12 phase/neutral and V13 predictive laws are unavailable in the verified forward book. '
                'The native V14 return features and complete V18/V20/V21/V22 overlay inputs have not passed exact replay.')
    runs=[dict(model=x['name'],horizon=x['horizon'],earliest=due.isoformat(),
               status='native issue blocked' if at>=due else 'native decision ahead',
               reasons=[unresolved])
          for x in cfg['configurations'] if x['clock']==NATIVE]
    save('forward/native-clock-status.json',dict(checked_at=at.isoformat(),clock=due.isoformat(),rows=runs,
          verified_option_books=option_books,verified_cash_risk_state=state_ok,verified_native_return_laws=0))
    print('Native input gates recorded for',len(runs),'model configurations at',at.isoformat(),flush=True)


def run(mode):
    if mode=='native-check':
        return native_check()
    if not (OUT/'forward/pre-cutoff-staging.json').exists():
        stage()
    known=ledger()
    cfg=configure()
    cut=stamp(STUDY_DAY,OPEN)
    begin=guard_day()
    prepared=[]
    errors=[]
    if begin<cut:
        try:
            prepared=month_paths(known,cut)
        except (ValueError,KeyError,IndexError,AssertionError,FileNotFoundError) as e:
            errors.append(dict(model='month path models',error=type(e).__name__,detail=str(e)[:190]))
        from .gjr_continuation import forward_risk
        try:
            prepared.append(forward_risk(known,cut))
        except (ValueError,KeyError,IndexError,AssertionError,FileNotFoundError) as e:
            errors.append(dict(model='V14 monthly GJR risk',error=type(e).__name__,detail=str(e)[:190]))
    if mode=='dry-run':
        save('forward/preflight.json',dict(checked_at=now(),cutoff=cut.isoformat(),reproducible_candidates=[p['name'] for p in prepared],errors=errors,
                                          issued=0))
        print('Prospective path preflight',len(prepared),'complete models',errors,flush=True)
        return
    if begin>=cut:
        save('forward/cutoff-run.json',dict(cutoff=cut.isoformat(),checked_at=now(),status='cutoff elapsed before acquisition',new_issues=0,errors=errors))
        return native_check()
    print('Prepared',len(prepared),'path and risk laws, watching for the actual 08:55 cash-market cutoff.',flush=True)
    sleep_until(cut-pd.Timedelta(seconds=54))
    receipts=[]
    for attempt in range(2):
        try:
            entry,r=opening(cut,known)
            receipts.append(r)
            if entry:
                prepared.append(entry)
                break
        except (ValueError,KeyError,AssertionError,FileNotFoundError) as e:
            errors.append(dict(model='GIFT opening',error=type(e).__name__,detail=str(e)[:190]))
        if attempt==0:
            sleep_until(cut-pd.Timedelta(seconds=21))
    save('forward/opening-capture.json',dict(cutoff=cut.isoformat(),checked_at=now(),attempts=receipts,errors=errors))
    sleep_until(cut)
    issued=emit(prepared,cut,known,cfg)
    save('forward/cutoff-run.json',dict(cutoff=cut.isoformat(),checked_at=now(),status='genuine issue window observed',
          new_issues=len(issued),models=[v['model'] for v in issued],errors=errors))
    print('Genuinely issued',len(issued),'research laws at the morning clock.',flush=True)
    sleep_until(stamp(STUDY_DAY,NATIVE))
    native_check()
