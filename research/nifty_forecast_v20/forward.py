"""Refresh completed cash sessions and freeze eligible research-only references."""
from urllib.parse import urlencode
import hashlib
import requests
from scipy.special import gamma
from .common import *
from research.nifty_forecast_v16 import acquire as source
from research.nifty_forecast_v19 import acquire as public
from research.nifty_forecast_v14.volatility import fit_garch,filter_garch
from research.nifty_forecast_v17.weekly import evaluate
from research.nifty_forecast_v4.distributions import Distribution

def reconciliation():
    source.OUT=OUT
    source.save=save
    source.forward()
    refresh=read('forward-ledger.json')
    # Keep the published V19 result and its exact corroborating quote receipt.
    old=read('forward-ledger.json',V19)
    checked=pd.Timestamp(refresh['checked_at'])
    frames={x['day']:x for x in refresh['sessions']}
    known={}
    for x in old['sessions']:
        if x['status']=='verified':
            z=x['nse_ohlc']
            loc=V19/x['file']
            assert sha(loc)==x['sha256']
            newer=frames.get(x['day'],{})
            assert newer.get('nse_ohlc',z)==z
            known[x['day']]=dict(day=x['day'],ohlc=z,file=x['file'],archive='V19',sha256=x['sha256'])
    for x in refresh['sessions']:
        if x['status']=='verified':
            known[x['day']]=dict(day=x['day'],ohlc=x['nse_ohlc'],file=x['file'],archive='V20',sha256=x['sha256'])
    v5=read('experimental-forecasts.json',V5)['forecasts']
    rnew=[]
    for r in old['records']:
        z=r.copy()
        current=[d for d in sorted(known) if r['reference_session']<d<=r['target_sessions'][-1]]
        z['completed_target_dates']=[d for d in z['target_sessions'] if d in known]
        if r['realized_return'] is None and checked>=stamp(r['target_sessions'][-1],'18:00') and current==r['target_sessions']:
            close=known[current[-1]]['ohlc']['close']
            value=close/r['reference_close']-1
            if r['version']=='V5':
                p=v5[r['key']]
                s=Distribution(p['atoms'],p['weights']).score(value)
                z.update(maturity='resolved on original target',realized_return=value,official_close=close,
                    resolutions_at=checked.isoformat(),scores={r['key']:{k:s[k] for k in ('p','brier','crps','log_loss')}})
        rnew.append(z)
    prior=read('forward/new-issues.json',V19)
    append=[]
    for row in prior['records']:
        assert sha(V19/row['file'])==row['sha256']
        b=row.copy()
        dates=b['target_sessions']
        seen=[d for d in dates if d in known]
        b['known_target_sessions']=seen
        b['frozen_in']='V19'
        b['maturity']='pending verified endpoint'
        if seen==dates and checked>=stamp(dates[-1],'18:00'):
            close=np.array([b['reference_close'],*[known[i]['ohlc']['close'] for i in dates]])
            actual=close[-1]/close[0]-1
            r=np.sqrt(252*np.square(np.diff(np.log(close))).mean())
            b.update(maturity='resolved',realized_return=float(actual),realized_annualized_vol=float(r))
            if b['name']=='monthly_neutral_reference':
                with np.load(V19/b['file'],allow_pickle=False) as s:
                    b['scores']=evaluate(s['arithmetic_returns'],s['weights'],actual)
        append.append(b)
    save('forward-refresh-receipt.json',refresh)
    return dict(checked_at=refresh['checked_at'],sessions=list(known.values()),records=rnew,
      v4_issue_hash=old['v4_sha256'],v5_issue_hash=old['v5_sha256'],v19_issue_file_sha256=sha(V19/'forward/new-issues.json'),
      inherited_v19_research=append)

def volatility_paths(returns):
    ans=fit_garch(returns,np.zeros_like(returns),('egarch','student','none',None,True))
    ans['next_variance']=float(filter_garch(returns,np.zeros_like(returns),ans,ans['initial'])[-1])
    rng=np.random.default_rng(SEED)
    nu=ans['nu']
    innovations=rng.standard_t(nu,size=(1536,21))*np.sqrt((nu-2)/nu)
    abs_expect=2*np.sqrt(nu-2)*gamma((nu+1)/2)/((nu-1)*np.sqrt(np.pi)*gamma(nu/2))
    logv=np.full(len(innovations),np.log(ans['next_variance']))
    paths=np.empty_like(innovations)
    for i in range(21):
        h=innovations[:,i]
        paths[:,i]=np.exp(.5*logv)*h/100
        logv=np.clip((1-ans['beta'])*ans['mu']+ans['beta']*logv+ans['alpha']*(abs(h)-abs_expect)+ans['leverage']*h,-5,5)
    return paths,ans

def live_iv(level,h,day):
    public.OUT=OUT
    fetched=[]
    values=[]
    with requests.Session() as sess:
        sess.headers['Authorization']='Bearer '+source.token()
        for expiry in ('2026-12-01','2026-12-08'):
            query=urlencode({'instrument_key':'NSE_INDEX|Nifty 50','expiry_date':expiry})
            r=public.grab('https://api.upstox.com/v2/option/chain?'+query,f'forward/atm-{expiry}.json.gz','json',session=sess)
            fetched.append(r)
            if not r.get('file'):continue
            d=json.loads(public.raw(OUT/r['file'])).get('data',[])
            eligible=[x for x in d if x.get('expiry')==expiry and abs(float(x.get('underlying_spot_price',0))/level-1)<.002]
            for p in sorted(eligible,key=lambda x:abs(x['strike_price']-level))[:3]:
                k=[p.get(a,{}).get('option_greeks',{}).get('iv') for a in ('call_options','put_options')]
                if all(isinstance(v,(int,float)) and 3<v<100 for v in k) and abs(p['strike_price']/level-1)<.0125:
                    values.append((expiry,float(p['strike_price']),np.median(k)/100))
                    break
    if len(values)!=2:return fetched,None
    t=np.array([(pd.Timestamp(exp)-pd.Timestamp(day)).days for exp,_,_ in values])
    v=np.array([x[2] for x in values])
    if not t[0]<=h<=t[1]:return fetched,None
    var=float(np.interp(h,t,t*v*v)/h)
    return fetched,(np.sqrt(var),values)

def issue(ledger):
    p=OUT/'forward/new-issues.json'
    if p.exists():return read('forward/new-issues.json')['records']
    today=pd.Timestamp(now()).tz_convert(IST)
    day=today.date().isoformat()
    if day!='2026-11-25' or today.hour<18:return []
    seen={r['day']:r for r in ledger['sessions']}
    if day not in seen:return []
    a=seen[day]
    ref=float(a['ohlc']['close'])
    old=read('forward/new-issues.json',V19)
    t=next(r['target_sessions'] for r in old['records'] if r['horizon']==21)
    assert t[0]=='2026-11-26' and t[4]=='2026-12-02' and t[-1]=='2026-12-24' and t[-1]<=LAST
    f=csv('original-target-panel.csv',V17)
    y=np.expm1(f.loc[f.end_original5.le(FREEZE),'original5'].dropna().to_numpy())[-140:]
    q=np.quantile(abs(y),(np.arange(64)+.5)/64)
    ret=np.r_[-q[::-1],q]
    neutral='forward/weekly-symmetric.npz'
    (OUT/'forward').mkdir(exist_ok=True)
    np.savez_compressed(OUT/neutral,arithmetic_returns=ret,weights=np.ones(len(ret))/len(ret))
    specs=[dict(model='weekly_symmetric',target_sessions=t[:5],horizon=5,
        law=neutral,law_sha256=sha(OUT/neutral),p_up=.5,
        q10=float(np.quantile(ret,.10)),median=0.,q90=float(np.quantile(ret,.90)),train_n=len(y),
        configuration={'model':'Symmetric empirical magnitudes','calibration':'140 frozen fully mature five-session returns'})]
    c=csv('official-index-closes.csv',V11).set_index('Unnamed: 0').nifty50.loc[FIRST:FREEZE]
    live=pd.Series({k:v['ohlc']['close'] for k,v in seen.items() if FREEZE<k<=day})
    c=pd.concat([c,live]).sort_index()
    assert c.iloc[-1]==ref
    r=100*np.diff(np.log(c.to_numpy()))
    paths,fit_=volatility_paths(r)
    vol=np.sqrt(252*np.square(paths).mean(axis=1))
    trailing=float(np.sqrt(252*np.square(r[-21:]/100).mean()))
    path='forward/student-egarch-21.npz'
    np.savez_compressed(OUT/path,log_daily=paths,annualized_volatility=vol,weights=np.ones(len(vol))/len(vol))
    specs.append(dict(model='monthly_student_t_egarch_expansion',target_sessions=t,horizon=21,
        law=path,law_sha256=sha(OUT/path),transition_threshold=1.25*trailing,p_expansion=float((vol>=1.25*trailing).mean()),
        q10=float(np.quantile(vol,.10)),median=float(np.median(vol)),q90=float(np.quantile(vol,.90)),train_n=len(r),
        configuration=dict(fit_|{'calibration':'Close-only EGARCH-t re-estimation anchored to the post-close information set','seed':SEED})))
    sources,atm=live_iv(ref,7,day)
    save('forward/options-probes.json',sources)
    if atm:
        v,notes=atm
        # Raw IV and the IV/RV blend each anchor a standalone volatility law, distinct from the pre-auction native models.
        rv=np.sqrt(252*np.square(np.lib.stride_tricks.sliding_window_view(r/100,5)).mean(axis=1))
        scale_hist=np.quantile(rv/max(np.median(rv),.02),Q)
        for name,center in [('cash_close_ATM_IV',v),('cash_close_IV_RV_blend',.75*v+.25*trailing)]:
            proj=center*scale_hist
            path=f'forward/{name}.npz'
            np.savez_compressed(OUT/path,annualized_volatility=proj,weights=np.ones(len(Q))/len(Q))
            specs.append(dict(model=name,target_sessions=t[:5],horizon=5,law=path,law_sha256=sha(OUT/path),
                q10=float(np.quantile(proj,.10)),q90=float(np.quantile(proj,.90)),median=float(np.median(proj)),annualized_point=center,
                configuration=dict(blend_weights=[.75,.25] if name.endswith('blend') else [1,0],valid_quoted_ATM=notes,
                    formula='Total variance interpolation between current authenticated call/put ATM marks. Empirical volatility shape.')))
    issued=pd.Timestamp(now()).tz_convert(IST)
    if not issued<stamp(t[0],'08:55'):
        return []
    out=[]
    for b in specs:
        k=hashlib.sha256(json.dumps(b['configuration'],sort_keys=True,default=str).encode()).hexdigest()
        out.append(b|dict(configuration_hash=k,issued_at=issued.isoformat(),information_cutoff=issued.isoformat(),
            reference_session=day,reference_close=ref,first_target=t[0],target=b['target_sessions'][-1],
            issue_class='prospective research at cash-close/evening clock',matched_benchmark='Eligible historical/neutral and IV/GJR families at their own clocks'))
    save('forward/new-issues.json',dict(records=out,close_source=a,
        operation='Evening research reference. V14, V18, native V19 positioning and offshore opening retain their own morning guards. Monthly neutral and both GJR laws were already genuinely frozen in V19.'))
    return out

if __name__=='__main__':
    z=reconciliation()
    z['new_issues']=issue(z)
    z['scope']='Historical vintage fixed at 2026-11-17. Original forecasts kept immutable. Forward outcomes and forecasts have distinct hashes.'
    save('forward-ledger.json',z)
    print('V20 forward as-of',z['checked_at'],'legacy resolutions',sum(r['realized_return'] is not None for r in z['records']),
          'prior research references',len(z['inherited_v19_research']),'new references',len(z['new_issues']),flush=True)

