"""Read-only reconciliation of old issues and a separately timestamped live-input staging lane."""
from concurrent.futures import ThreadPoolExecutor

from .common import *
from .sources import SERIES,schedule,yahoo
from research.nifty_forecast_v16 import acquire as live
from research.nifty_forecast_v21 import forward as previous

FIRST_FORWARD='2026-11-18'


def international_capture(s,at):
    plans=schedule(s,FIRST_FORWARD,at.date().isoformat())
    eligible=plans.loc[plans.available.le(at),['day','market_close','available']]
    if eligible.empty:
        return pd.DataFrame(),dict(code=s.code,status='awaiting a completed local mark')
    last=eligible.day.max()
    values,r=yahoo(s,FIRST_FORWARD,last,'forward/international')
    if values.empty:
        return values,r|dict(last_eligible_session=last,usable_marks=0)
    stamps=pd.to_datetime(values.source_timestamp,format='mixed',utc=True)
    values=values.loc[stamps.le(at)].copy()
    values['observed_timestamp']=stamps[stamps.le(at)]
    duplicates=int(values.day.duplicated().sum())
    values=values.sort_values('observed_timestamp').drop_duplicates('day',keep='last')
    z=eligible.merge(values,on='day',validate='1:1').dropna(subset=['close'])
    return z.assign(code=s.code,captured_at=at.isoformat()),r|dict(last_eligible_session=last,usable_marks=len(z),duplicate_vendor_day=duplicates)


def configuration(clock,short,h,reader,source_file,blocked):
    inputs=['eligible official reference and exact horizon target sessions',*blocked]
    data={'short':short,'horizon':h,'clock':clock,'implementation':reader.relative_to(ROOT).as_posix(),
          'implementation_sha256':sha(reader),'input_requirements':inputs,'historical_source':source_file.relative_to(ROOT).as_posix(),
          'historical_source_sha256':sha(source_file),'classification':'frozen configuration and historical rehearsal',
          'law_integrity':'capture weight and atom file hash when the native law can be truly issued'}
    key=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
    return data|dict(configuration_sha256=key)


def run():
    at=pd.Timestamp(now()).tz_convert(IST)
    assert FREEZE<at.date().isoformat()<=LAST
    old=read('forward-ledger.json',V21)
    live.OUT=OUT
    live.save=lambda name,obj:save('forward/reconciliation-native.json' if name=='forward-ledger.json' else name,obj)
    live.forward()
    current=read('forward/reconciliation-native.json')
    marks={}
    origin={'V19':V19,'V20':V20,'V21':V21,'V22':OUT}
    for r in old['sessions']:
        assert sha(origin[r['archive']]/r['file'])==r['sha256']
        marks[r['day']]=r
    for s in current['sessions']:
        if s['status']!='verified':
            continue
        day=s['day']
        if day in marks:
            assert marks[day]['ohlc']==s['nse_ohlc']
        marks[day]=dict(day=day,archive='V22',ohlc=s['nse_ohlc'],file=s['file'],sha256=s['sha256'])
    legacy=[]
    for before,after in zip(old['original_issues'],current['records'],strict=True):
        for field in ('version','key','issue_hash','target_sessions','reference_close','issued'):
            assert before[field]==after[field]
        take=after if before['realized_return'] is None and after['realized_return'] is not None else before
        legacy.append(dict(take,completed_target_dates=[d for d in take['target_sessions'] if d in marks]))
    immutable=[]
    for version in ('V19','V20'):
        root=origin[version]
        saved=read('forward/new-issues.json',root)['records']
        trials=[previous.settle(marks,r,version,at.isoformat()) for r in saved]
        public=old['inherited_'+version.lower()]
        for old_r,new_r in zip(public,trials,strict=True):
            for k in ('target_sessions','reference_close','source_artifact'):
                assert old_r[k]==new_r[k]
        immutable.append(trials)
    launch=[]
    for version in range(4,22):
        root=ROOT/f'artifacts/nifty_forecast_v{version}'
        for p in sorted(root.rglob('*')):
            if p.name in ('prospective-ledger.jsonl','experimental-forecasts.json','forward-ledger.json','new-issues.json'):
                launch.append(dict(version=version,path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
    assert {4,5,15,16,17,18,19,20,21}.issubset({o['version'] for o in launch})
    previous.OUT=OUT
    days=sorted(marks)
    with ThreadPoolExecutor(max_workers=7) as pool:
        pp=pool.map(previous.participant_probe,days)
        staging=[r for group in pp for r in group]
        eligible_markets=[s for s in SERIES if s.exchange not in (None,'NSE') and s.role=='primary'
                          and s.code!='thailand']
        other=list(pool.map(lambda s:international_capture(s,at),eligible_markets))
    prices=pd.concat([df for df,_ in other if not df.empty],ignore_index=True)
    assert prices.day.gt(FREEZE).all() and prices.available.le(at).all()
    write('forward/eligible-foreign-completed-sessions.csv.gz',prices)
    save('forward-input-receipts.json',dict(captured=at.isoformat(),participant=staging,international=[r for _,r in other],
          n_eligible_international=len(prices),n_foreign_markets=prices.code.nunique(),research_isolation='Forward inputs are never read by a retrospective model.'))
    cash_day=days[-1]
    # 2026 exchange dates were already frozen by the inherited ledgers. Use the same published holidays.
    from research.nifty_forecast_v20 import forward as inherited
    initial=immutable[1][0]['target_sessions']
    d0=initial[0]
    pnl=V21/'index-forecast-cases.csv.gz'
    law_path=V21/'index-forecast-laws.npz'
    refs=csv('protected-india-return-cases.csv.gz')
    risk=csv('protected-point-risk-cases.csv.gz',V20)
    for h in ORIGINAL:
        native='09:10'
        keys={5:('exact_v14','v18_corporate_native','omit_latest_21_training_origins','anchor_asymmetry'),
              21:('exact_v14','v19_position_native','smooth5','anchor_aggregate_position')}[h]
        source_modules={'exact_v14':'research/nifty_forecast_v14',
                        'v18_corporate_native':'research/nifty_forecast_v18','omit_latest_21_training_origins':'research/nifty_forecast_v20',
                        'anchor_asymmetry':'research/nifty_forecast_v21','v19_position_native':'research/nifty_forecast_v19',
                        'smooth5':'research/nifty_forecast_v20','anchor_aggregate_position':'research/nifty_forecast_v21'}
        for k in keys:
            base=ROOT/source_modules[k]
            candidates=sorted(base.glob('*.py'))
            mod=next((x for name in ('forecast.py','weekly.py','modeling.py','distribution.py','architecture.py') for x in candidates if x.name==name),candidates[0])
            reasons=['native V14 path state reconstructed with eligible newly completed domestic and option data']
            if k!='exact_v14' and h==5:
                reasons+=['V18 timestamp-qualified issuer releases and completed price reactions, or exact V20 training-window omission']
            if k!='exact_v14' and h==21:
                reasons+=['08:55-eligible participant holdings history and exact prior-session smoothing']
            cfg=configuration(native,k,h,mod,pnl,reasons)
            hist=refs[refs.horizon.eq(h)&refs.cutoff.eq('native_0910')&refs.model.eq(k)].sort_values('day').iloc[-1]
            due=stamp(d0,native)
            stage='cutoff still ahead at source capture' if at<due else 'cutoff elapsed without complete native input snapshot'
            cfg.update(status=stage,initial_research_cutoff=due.isoformat(),historical_probability=hist.p,historical_crps=hist.crps,
                       rehearsal_day=hist.day,rehearsal_target=hist.target_end,rehearsal_law=int(hist.law),
                       rehearsal_law_sha256=sha(OUT/'protected-india-return-laws.npz'),unmodified_archive_law=law_path.relative_to(ROOT).as_posix())
            launch_day=next((d for d in initial if stamp(d,native)>at),None)
            cfg['next_cutoff']=stamp(launch_day,native).isoformat() if launch_day else None
            # An original monthly tenor started later can extend into 2027. Check the frozen month-end date list.
            cfg['allowed_for_new_issue']=bool(launch_day and (h==5 or launch_day<=d0))
            launch.append(cfg)
        if h==5:
            inherited_ref=next(x for x in immutable[1] if x.get('model')=='weekly_symmetric')
            fn,checksum=V20/inherited_ref['law'],inherited_ref['law_sha256']
            label,code='weekly_symmetric',Path(inherited.__file__)
        else:
            inherited_ref=next(x for x in immutable[0] if x.get('name')=='monthly_neutral_reference')
            fn,checksum=V19/inherited_ref['file'],inherited_ref['sha256']
            label,code='monthly_neutral_reference',ROOT/'research/nifty_forecast_v19/forward.py'
        assert sha(fn)==checksum
        cfg=configuration('previous_1700',label,h,code,fn,[])
        cfg.update(status='existing original neutral law retained',target_sessions=inherited_ref['target_sessions'],original_source_sha256=checksum)
        launch.append(cfg)
        for k in (('raw_iv','fixed_iv_rv') if h==5 else ('GJR','student_EGARCH')):
            f=risk[risk.horizon.eq(h)&risk.model.eq(k)].sort_values('day').iloc[-1]
            cfg=configuration('08:55',k,h,ROOT/'research/nifty_forecast_v16/volatility.py',V20/'protected-point-risk-cases.csv.gz',
                         ['verified prior option IV or cash GJR state plus trailing realized volatility definition'])
            cfg.update(status='historical exact replay and related evening V20 risk issues archived',rehearsal_day=f.day,
                       rehearsal_risk=f.pred_vol,rehearsal_expansion_p=f.p)
            launch.append(cfg)
    open_model=configuration('08:55','GIFT opening gap',1,ROOT/'research/nifty_forecast_v17/gift.py',V21/'forward-readiness.csv',
                             ['properly timestamped same-session GIFT bar and exact prior official close'])
    open_model['status']='no eligible morning GIFT snapshot captured'
    open_model['next_cutoff']=next((stamp(d,'08:55').isoformat() for d in initial if stamp(d,'08:55')>at),None)
    launch.append(open_model)
    save('forward/staged-model-configurations.json',dict(as_of=now(),prior_cash=cash_day,rows=[r for r in launch if 'short' in r]))
    save('forward-ledger.json',dict(as_of=now(),data_cutoff=at.isoformat(),training_cutoff=FREEZE,sessions=[marks[k] for k in days],
         original_issues=legacy,inherited_v19=immutable[0],inherited_v20=immutable[1],new_issues=[],
         archive_receipts=[r for r in launch if 'version' in r],staged_model_count=sum('short' in r for r in launch),
         rule='Freeze prior issues exactly. Resolve only with authoritative complete original sessions. Dated prospective features and original law files are required to issue. Never issue a window beyond 2026.',
         source_separation='All live samples reside in the forward subdirectory. None were eligible inputs to any historical fit.'))
    print('Forward',len(days),'official cash sessions,',len(prices),'eligible foreign closes,',len(legacy)+sum(map(len,immutable)),
          'preserved forecasts',flush=True)


if __name__=='__main__':
    run()
