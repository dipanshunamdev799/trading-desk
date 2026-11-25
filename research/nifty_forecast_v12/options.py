"""Audit the native UDiFF archives, reconstruct liquid-strike marks and price densities."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from zipfile import ZipFile

from scipy.ndimage import gaussian_filter1d
from scipy.optimize import isotonic_regression
from scipy.special import ndtr
from scipy.stats import norm

from .common import *

COLS=['TradDt','BizDt','TckrSymb','FinInstrmTp','FinInstrmId','XpryDt','FininstrmActlXpryDt','StrkPric','OptnTp',
      'OpnPric','HghPric','LwPric','ClsPric','LastPric','PrvsClsgPric','SttlmPric','UndrlygPric','OpnIntrst',
      'ChngInOpnIntrst','TtlTradgVol','TtlNbOfTxsExctd','NewBrdLotQty','SsnId']
NAMES=['day','business_day','ticker','kind','id','listed_expiry','actual_expiry','strike','side','open','high','low',
       'close','last','previous','settlement','underlying','oi','oi_change','volume','trades','lot','session']


def raw_path(doc,day):
    home=V5/'sources/fo'
    local=home/f'{day}.zip'
    if local.is_file():return local
    origin=Path(doc.get('source_path','_'))
    if origin.is_file():return origin
    raise FileNotFoundError(day)


def raw_one(task):
    p,spot=task;d=p.stem;o=json.loads(p.read_text(encoding='utf-8'))
    raw=raw_path(o,d)
    actual=sha(raw)
    expected=o.get('sha256_zip',o.get('zip_sha256'))
    if expected:assert actual==expected,raw
    with ZipFile(raw) as z:
        assert len(z.namelist())==1
        with z.open(z.namelist()[0]) as stream:
            all_=pd.read_csv(stream,usecols=COLS,low_memory=False)
    a=all_.loc[all_.TckrSymb.eq('NIFTY'),COLS].copy()
    a.columns=NAMES
    a['expiry']=a.actual_expiry.fillna(a.listed_expiry)
    assert a.day.eq(d).all() and a.kind.isin(['IDF','IDO']).all(),d
    assert a.id.notna().all(),d
    a['spot']=spot
    discrepancy=(a.underlying.where(a.underlying.gt(0))-spot).abs()
    op=a[a.kind.eq('IDO')].copy()
    traded=op[op.volume.gt(0)&op.close.gt(0)]
    complete=traded[['open','high','low','close']].gt(0).all(axis=1)
    # Closing price and last trade have different definitions. Retain both.
    ohlc=complete & traded.high.ge(traded[['open','low','close']].max(axis=1)) & traded.low.le(traded[['open','close','high']].min(axis=1))
    paired=traded.groupby(['expiry','strike']).side.nunique()
    if d<=FREEZE and o.get('ok'):
        slim=pd.DataFrame(o['rows'])
        exact=['FinInstrmId','ClsPric','SttlmPric','TtlTradgVol','StrkPric','OptnTp']
        x=all_.loc[all_.TckrSymb.eq('NIFTY'),exact].reset_index(drop=True)
        sl=slim[exact].copy()
        for k in exact[:-1]:sl[k]=pd.to_numeric(sl[k],errors='coerce')
        np.testing.assert_allclose(sl[exact[:-1]],x[exact[:-1]],atol=1e-9,rtol=0,equal_nan=True)
        assert sl.OptnTp.fillna('').eq(x.OptnTp.fillna('')).all(),d
    source={'day':d,'raw_path':str(raw.relative_to(ROOT)),'raw_sha256':actual,'slim_sha256':sha(p),
            'url':o.get('source_url',o.get('url')),'original_receipt':o.get('acquired_at',o.get('received')),
            'raw_bytes':raw.stat().st_size,'all_rows':len(all_),'nifty_rows':len(a),'option_rows':len(op),
            'futures_rows':int(a.kind.eq('IDF').sum()),'traded_option_rows':len(traded),
            'zero_volume_close_positive':int((op.volume.eq(0)&op.close.gt(0)).sum()),
            'no_trade_or_no_valid_close':int(len(op)-len(traded)),
            'complete_traded_ohlc':int(complete.sum()),'traded_ohlc_consistent':int(ohlc.sum()),
            'price_equals_previous_on_trade':int(traded.close.eq(traded.previous).sum()),
            'traded_close_neq_last':int(traded.close.sub(traded['last']).abs().gt(.005).sum()),
            'traded_close_neq_settlement':int(traded.close.sub(traded.settlement).abs().gt(.005).sum()),
            'same_expiry_strike_traded_pairs':int(paired.eq(2).sum()),'unpaired_traded_strikes':int(paired.eq(1).sum()),
            'duplicate_contract_session_rows':int(a.duplicated(['id','session']).sum()),
            'nonzero_underlying_mismatch_gt_05':int(discrepancy.gt(.05).sum()),
            'maximum_underlying_abs_delta':float(discrepancy.max()) if discrepancy.notna().any() else None,
            'actual_expiry_differs_from_listed':int(a.actual_expiry.notna().sum()-a.actual_expiry.eq(a.listed_expiry).sum()),
            'option_expiries':int(op.expiry.nunique()),'lot_values':sorted([int(k) for k in a.lot.dropna().unique()]),
            'actual_expiry_after_2026_rows':int(a.expiry.gt('2026-12-31').sum())}
    return a,source


def extract():
    spot=matrix('official-index-closes.csv',V11).nifty50
    tasks=[(p,float(spot.loc[p.stem])) for p in sorted((V5/'sources/fo').glob('*.json')) if p.stem in spot.index and p.stem<=FREEZE]
    assert len(tasks)>400
    rows=[];receipts=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for i,(df,receipt) in enumerate(pool.map(raw_one,tasks),1):
            rows.append(df)
            receipts.append(receipt)
            if i%100==0:print('Audited',i,'of',len(tasks),'native UDiFF dates',flush=True)
    raw=pd.concat(rows,ignore_index=True).sort_values(['day','kind','expiry','strike','side'])
    write('sources/nifty-udiff.csv.gz',raw,compression='gzip')
    write('daily-options-audit.csv',pd.DataFrame(receipts))
    save('options-source-audit.json',{'sessions':len(tasks),'first_day':raw.day.min(),'end_day':raw.day.max(),
          'nifty_raw_rows':len(raw),'header':COLS,'sources':receipts,
          'fields_unavailable':['bid','ask','best-quote timestamp','per-strike IV','Greeks','historical MIBOR term structure'],
          'source_delay':'Use the previous observed NSE trading session mark in main research. This EOD extraction has no reconstructed historical receipt clock.',
          'economic_price':'ClsPric, LastPric and SttlmPric are distinct marks. A traded close requires nonzero traded volume; the archive does not identify executable prices or same-second quotes.',
          'rate_assumption':'Fixed annual 6% continuous discount for main diagnostics, with zero and 9% stress. Policy repo does not identify matched-tenor market funding, stock-basket dividends or a tradable forward.'})
    print('Extracted',len(raw),'NIFTY derivatives rows',flush=True)


def black(k,v,is_call):
    """Undiscounted Black-76 premium divided by forward; v is total volatility."""
    z=np.log(k)
    d1=-z/v+.5*v
    d2=d1-v
    return np.where(is_call,ndtr(d1)-k*ndtr(d2),k*ndtr(-d2)-ndtr(-d1))


def solve_iv(k,option,is_call,tau):
    lower=np.where(is_call,np.maximum(1-k,0),np.maximum(k-1,0))
    upper=np.where(is_call,1.,k)
    ok=np.isfinite(option)&(option>lower+1e-8)&(option<upper-1e-8)
    lo=np.full(len(k),.002*np.sqrt(tau))
    hi=np.full(len(k),2.5*np.sqrt(tau))
    ok&=option<=black(k,hi,is_call)
    for _ in range(34):
        mid=(lo+hi)/2
        move=black(k,mid,is_call)<option
        lo=np.where(move,mid,lo)
        hi=np.where(move,hi,mid)
    return np.where(ok,(lo+hi)/(2*np.sqrt(tau)),np.nan)


@dataclass(frozen=True)
class Method:
    name:str
    field:str='close'
    minimum_volume:int=10
    rate:float=.06
    bandwidth:float=.85
    max_z:float=3.0
    tighter:bool=False
    actual_future:bool=False


METHODS=[Method('TRADE'),Method('LIQUID',minimum_volume=150,tighter=True),
         Method('SETTLEMENT',field='settlement'),Method('RATE_ZERO',rate=0.),
         Method('RATE_HIGH',rate=.09),Method('SMOOTH',bandwidth=1.65),
         Method('TRUNCATED',max_z=1.95),Method('FUTURE_FORWARD',actual_future=True)]


def projected_density(k,p,atm,years,method):
    """Fit bounded non-increasing vertical-spread probabilities and test recovered prices."""
    z=np.log(k)/(atm*np.sqrt(years))
    take=np.abs(z)<=method.max_z
    k,p,z=k[take],p[take],z[take]
    if len(k)<16 or (z<0).sum()<6 or (z>0).sum()<6 or z.min()>-1.13 or z.max()<1.13:
        return None,{'density_status':'inadequate two-sided strike support','density_strikes':len(k)}
    calls=p+np.maximum(1-k,0)
    raw=-np.diff(calls)/np.diff(k)
    mass_outlier=float(np.mean((raw<-.02)|(raw>1.02)))
    order_viol=float(np.mean(np.diff(raw)>.025))
    spread=gaussian_filter1d(raw,method.bandwidth,mode='nearest')
    prob=np.clip(isotonic_regression(spread,weights=np.diff(k),increasing=False).x,0.,1.)
    w=np.maximum(np.r_[1-prob[0],prob[:-1]-prob[1:],prob[-1]],0.)
    outside=float(w[0]+w[-1])
    if outside>.38 or mass_outlier>.45:
        return None,{'density_status':'excess wing mass or vertical violations','density_strikes':len(k),
                     'raw_bad_vertical_fraction':mass_outlier,'raw_convexity_violation_fraction':order_viol,'raw_external_mass':outside}
    # Endpoint atoms match the residual OTM premium at each boundary, within conservative wing caps.
    total=atm*np.sqrt(years)
    low=max(.60,k[0]-min(max(p[0],0)/max(w[0],.003),2.1*total))
    high=min(1.65,k[-1]+min(max(p[-1],0)/max(w[-1],.003),2.1*total))
    a=np.r_[low,k[1:-1],high]
    # Minimal exponential change to the projected probabilities centers F-normalized prices at one.
    before=float(w@a)
    base=w.copy()
    pwr=(a-1)/max(total,.001)
    lo,hi=-3.,3.
    for _ in range(35):
        m=(lo+hi)/2
        w=base*np.exp(np.clip(m*pwr,-25,25))
        w/=w.sum()
        if w@a<1:lo=m
        else:hi=m
    rmse=float(np.sqrt(np.mean(((np.maximum(a[None,:]-k[:,None],0)@w)-calls)**2)))
    clipped=float(np.abs(w-base).sum()/2)
    extra={'density_strikes':len(k),'support_lo_k':float(k[0]),'support_hi_k':float(k[-1]),
           'support_lo_z':float(z.min()),'support_hi_z':float(z.max()),'raw_bad_vertical_fraction':mass_outlier,
           'raw_convexity_violation_fraction':order_viol,'raw_external_mass':outside,'external_mass':float(w[0]+w[-1]),
           'density_call_rmse_fraction_forward':rmse,'forward_before_tilt':before,'mass_shift':clipped,
           'martingale_error':float(w@a-1)}
    limit=max(.0010,.11*total) if not method.tighter else max(.00085,.09*total)
    ok=abs(w@a-1)<1e-7 and clipped<=.14 and rmse<=limit and w[0]+w[-1]<=.38
    extra['density_status']='accepted' if ok else 'pricing reproduction or normalization QC'
    return (Distribution(a-1,w) if ok else None),extra


def expiry_surface(g,spot,future,method):
    day=g.day.iloc[0];expiry=g.expiry.iloc[0]
    dte=(pd.Timestamp(expiry)-pd.Timestamp(day)).days
    base={'day':day,'expiry':expiry,'method':method.name,'dte':dte,'spot':spot,'rate':method.rate,
          'future_close':float(future) if np.isfinite(future) else None}
    liquid=g[g.volume.ge(method.minimum_volume)&g[method.field].gt(0)&g.strike.gt(0)&g.side.isin(['CE','PE'])]
    liquid=liquid.sort_values(['volume','oi'],ascending=False).drop_duplicates(['strike','side'])
    pair=liquid.pivot(index='strike',columns='side',values=method.field)
    if not {'CE','PE'}.issubset(pair.columns):
        return {**base,'iv_status':'no two traded sides'},None,None
    tau=dte/365.
    df=np.exp(-method.rate*tau)
    near=pair.dropna().loc[lambda a:np.abs(a.index/spot-1)<=.045]
    if len(near)<5:
        return {**base,'iv_status':'fewer than five near parity pairs','paired_count':len(near)},None,None
    parity=near.index.to_numpy(float)+(near.CE.to_numpy()-near.PE.to_numpy())/df
    strongest=near.iloc[np.argsort((near.CE+near.PE).to_numpy())[:min(13,len(near))]]
    sample=strongest.index.to_numpy(float)+(strongest.CE-strongest.PE).to_numpy()/df
    robust=float(np.median(sample))
    scatter=float(np.median(abs(sample-robust))/spot)
    F=float(future) if method.actual_future and np.isfinite(future) else robust
    base.update(parity_forward=robust,forward=F,paired_count=len(near),parity_mad_fraction= scatter,
                parity_full_mad_fraction=float(np.median(abs(parity-robust))/spot),
                forward_basis=F/spot-1,future_parity_gap=(float(future)/robust-1) if np.isfinite(future) else None)
    if abs(F/spot-1)>.12 or scatter>.009:
        return {**base,'iv_status':'excess nonsynchronous parity scatter'},None,None
    strikes=pair.index.to_numpy(float)
    k=strikes/F
    side=k>=1.
    option=np.where(side,pair.CE.to_numpy(float),pair.PE.to_numpy(float))/(df*F)
    samples=np.isfinite(option)&(abs(np.log(k))<=.20)
    iv=solve_iv(k[samples],option[samples],side[samples],tau)
    k,option,sides=k[samples],option[samples],side[samples]
    valid=np.isfinite(iv)
    base.update(iv_trials=len(iv),valid_iv=int(valid.sum()),rejected_iv=int((~valid).sum()))
    points=pd.DataFrame({'day':day,'expiry':expiry,'strike':k*F,'moneyness_forward':k,'side':np.where(sides,'CE','PE'),
                          'premium_fraction_forward_undiscounted':option,'iv':iv,'iv_valid':valid})
    if valid.sum()<12 or min(sum(k[valid]<1),sum(k[valid]>=1))<4:
        return {**base,'iv_status':'too few valid two-sided IVs'},None,points
    k,option,iv=k[valid],option[valid],iv[valid]
    near_ids=np.argsort(abs(np.log(k)))[:7]
    atm=float(np.median(iv[near_ids]))
    if not (.03<atm<1.50):
        return {**base,'iv_status':'ATM IV fails sanity bounds'},None,points
    z=np.log(k)/max(atm*np.sqrt(tau),1e-6)
    down,up=np.interp([-.8,.8],z,iv,left=np.nan,right=np.nan)
    closest=near.iloc[np.argsort(abs(np.log(near.index/F)))[:5]]
    ck=closest.index.to_numpy(float)/F
    call_iv=solve_iv(ck,closest.CE.to_numpy()/(df*F),np.ones(len(ck),bool),tau)
    put_iv=solve_iv(ck,closest.PE.to_numpy()/(df*F),np.zeros(len(ck),bool),tau)
    difference=call_iv-put_iv;difference=difference[np.isfinite(difference)]
    straddle=float(np.median((closest.CE+closest.PE).to_numpy()/spot))
    lognormal_sd=atm*np.sqrt(tau)
    base.update(iv_status='accepted',atm_iv=atm,total_variance=atm*atm*tau,
                atm_straddle=straddle,straddle_maturity_normalized=straddle/np.sqrt(tau),
                skew_down_minus_up=float(down-up),curvature=float(.5*(down+up)-atm),down_iv=float(down),up_iv=float(up),
                atm_call_put_iv_gap=float(np.median(difference)) if len(difference) else np.nan,
                used_actual_future=bool(method.actual_future and np.isfinite(future)))
    density,diag=projected_density(k,option,atm,tau,method)
    if density is not None:
        stats=density.stats()
        a,w=density.a,density.w
        sd=np.sqrt(w@(a*a))
        diag.update(density_q10=float(density.quantile(.1)),density_q90=float(density.quantile(.9)),
                    implied_skew_moment=float(w@(a**3)/max(sd**3,1e-12)),density_forward_sd=float(sd),
                    density_up_forward_mass=stats['p_up'],density_five_pct_down=float(w[a<-.05].sum()),
                    lower_extrapolated_quantile=bool(1+float(density.quantile(.1))<diag['support_lo_k']),
                    upper_extrapolated_quantile=bool(1+float(density.quantile(.9))>diag['support_hi_k']))
    return {**base,**diag},density,points


def reconstruct():
    save('surface-registry.json',{'registered_at':now(),'methods':[m.__dict__ for m in METHODS],
                                  'expiry_min_days':2,'expiry_max_days':72,'quote_columns':COLS,
                                  'implementation':sha(SRC/'options.py')})
    data=pd.read_csv(OUT/'sources/nifty-udiff.csv.gz',low_memory=False)
    f=data[data.kind.eq('IDF')&data.volume.gt(0)&data.close.gt(0)]
    fut=f.sort_values('volume',ascending=False).drop_duplicates(['day','expiry']).set_index(['day','expiry']).close
    o=data[data.kind.eq('IDO')&data.expiry.le('2026-12-31')].copy()
    dte=(pd.to_datetime(o.expiry)-pd.to_datetime(o.day)).dt.days
    o=o[dte.between(2,72)]
    charts=[];weights=[];keys=[];diagnostics=[];points=[]
    for i,((day,expiry),g) in enumerate(o.groupby(['day','expiry'],sort=True),1):
        observed=float(fut.get((day,expiry),np.nan))
        for m in METHODS:
            # Alternative curves are evaluated on the same dates and observed expiries.
            q,law,iv=expiry_surface(g,float(g.spot.iloc[0]),observed,m)
            diagnostics.append(q)
            if m.name=='TRADE' and iv is not None:points.append(iv)
            if law is not None:
                keys.append((day,expiry,m.name))
                weights.append(law)
        if i%550==0:print('Reconstructed',i,'date-expiries',flush=True)
    table=pd.DataFrame(diagnostics)
    write('surface-quality.csv',table)
    write('strike-implied-volatility.csv.gz',pd.concat(points,ignore_index=True),compression='gzip')
    saved=pack_bundle('option-density-atoms.npz',keys,weights)
    save('surface-summary.json',{'methods':list(table.method.unique()),'expiry_method_rows':len(table),
         'date_expiries':len(table[table.method.eq('TRADE')]),'density_archive':saved,
         'iv_and_density_denominators':table.groupby(['method','iv_status'],dropna=False).size().rename('n').reset_index().to_dict('records'),
         'interpretation':'Risk-neutral conditional pricing diagnostics. F-normalized atom has mean one. Exact wings are not identified; constrained mass, clipping and acceptance details are logged.'})
    print('Archived',len(weights),'accepted risk-neutral density approximations',flush=True)


if __name__=='__main__':
    import sys
    {'extract':extract,'reconstruct':reconstruct}[sys.argv[1]]()
