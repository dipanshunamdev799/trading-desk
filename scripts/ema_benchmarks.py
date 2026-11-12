from pathlib import Path
import sys,json,zipfile,io,time
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
import requests
from research.ema_validation.engine import *

def main():
    q=prepare();p=q['p'];data=np.load(OUT/'deterministic_paths.npz');history=pd.read_csv(ROOT/'artifacts/swing_diagnosis/benchmark-tri-history.csv');history['date']=pd.to_datetime(history.day).dt.strftime('%Y-%m-%d')
    prices={name:g.set_index('date').value for name,g in history.groupby('index')};rows=[];daily=[]
    for stage in ['two_year','final_reset']:
        label=f'A_rs1_{stage}';cols=data[label+'_cols'];dates=p['dates'][cols];util=data[label+'_utilization'];nav=data[label+'_equity'];tr=data[label+'_trades']
        # Reconstruct end-of-day holdings; same-day round trips have no close exposure.
        weights=np.zeros((len(cols),len(p['symbols'])));lookup={int(t):j for j,t in enumerate(cols)}
        for x in tr:
            s,e,z=int(x[0]),int(x[2]),int(x[3]);qty=x[5]
            for t in range(e,z):
                if t>e:qty*=p['split_factor'][s,t]
                if t in lookup:weights[lookup[t],s]+=qty*p['actual']['close'][s,t]/nav[lookup[t]]
        assert np.allclose(weights.sum(axis=1),util,atol=1e-12)
        for index in ['Nifty 50','Nifty 500']:
            series=prices[index];rets=[]
            for t in cols:
                day=str(p['dates'][t].date());prev=str(p['dates'][t-1].date())
                if day not in series.index or prev not in series.index:raise ValueError('Missing official TRI session '+day)
                rets.append(series.loc[day]/series.loc[prev]-1)
            daily.append((stage,index,np.asarray(rets)))
        eqret=(p['actual']['close']*p['split_factor']+p['dividend']*p['split_factor'])/np.roll(p['actual']['close'],1,axis=1)-1
        daily.append((stage,'Frozen470 equal-weight total-return proxy',np.mean(eqret[p['eligible']][:,cols],axis=0)))
        # Hybrid sector context: verified exact sector labels; unmatched capital uses broadN500.
        sector_return=np.zeros(len(cols));mapping={'Banks':'Nifty Bank','IT - Software':'Nifty IT','Pharmaceuticals & Biotechnology':'Nifty Pharma'};mapped=0.
        lagweights=np.vstack([np.zeros((1,weights.shape[1])),weights[:-1]])
        for s,sectorname in enumerate(p['sector']):
            index=mapping.get(sectorname,'Nifty 500');series=prices[index]
            ret=np.asarray([series.loc[str(p['dates'][t].date())]/series.loc[str(p['dates'][t-1].date())]-1 for t in cols])
            sector_return+=lagweights[:,s]*ret
            if sectorname in mapping:mapped+=lagweights[:,s].sum()
        # Benchmark uses known previous-close deployed weights; cash yields zero.
        for index,ret,alreadyweighted in [(n,r,False) for st,n,r in daily if st==stage]+[('Bank_IT_Pharma sector TRI; N500 fallback',sector_return,True)]:
            cashweight=np.r_[0.,util[:-1]];returns=ret if alreadyweighted else cashweight*ret
            for friction in ['gross','modeled_costs']:
                equity=[];value=1e6;held=0.;turnover=0.;fees=0.
                for i,t in enumerate(cols):
                    weight=cashweight[i];target=value*weight;delta=target-held;notional=abs(delta)
                    charge=0.
                    if friction=='modeled_costs' and notional>1e-8:
                        rate,fixed=fee_coeff(p['dates'][t],delta>0,True);charge=notional*(rate+.0005)+fixed
                    cash=value-target-charge
                    if cash< -1e-7:raise AssertionError('Exposure benchmark cash deficit')
                    underlying=returns[i]/weight if weight>0 else 0.
                    held=target*(1+underlying);value=cash+held;fees+=charge;turnover+=notional;equity.append(value)
                if friction=='modeled_costs' and held>0:
                    rate,fixed=fee_coeff(p['dates'][cols[-1]],False,True);charge=held*(rate+.0005)+fixed;equity[-1]-=charge;fees+=charge;turnover+=held
                m=portfolio_metrics(pd.Series(equity,index=dates));rows.append(dict(stage=stage,benchmark=index,friction=friction,**m,exposure_pct=cashweight.mean()*100,turnover_multiple=turnover/1e6,fees=fees,
                  sector_mapped_fraction_of_invested=mapped/lagweights.sum() if alreadyweighted and lagweights.sum()>0 else None))
                slug=index.replace(' ','_').replace('/','_').replace(';','_')
                path=OUT/f'benchmark-{stage}-{slug}-{friction}.csv'
                pd.DataFrame({'date':dates,'equity':equity,'known_weight':cashweight}).to_csv(path,index=False)
                returns_b=np.asarray(equity)/np.r_[1e6,np.asarray(equity)[:-1]]-1
                returns_a=nav/np.r_[1e6,nav[:-1]]-1;n=len(nav);rng=np.random.default_rng(542331)
                starts=rng.integers(0,n,(3000,int(np.ceil(n/10))));ix=((starts[:,:,None]+np.arange(10))%n).reshape(3000,-1)[:,:n]
                advantage=100*(np.prod(1+returns_a[ix],axis=1)-np.prod(1+returns_b[ix],axis=1))
                rows[-1].update(EMA_advantage_pct=100*(nav[-1]/1e6-1)-m['total_return_pct'],advantage_ci95_low_pct=np.quantile(advantage,.025),advantage_ci95_high_pct=np.quantile(advantage,.975))
    pd.DataFrame(rows).to_csv(OUT/'exposure-matched-benchmarks.csv',index=False)
    save('benchmark-caveats.json',dict(timing='Prior-close known actual strategy utilization applied to daily close-to-close TRI returns; not an exact next-open ETF replication or alpha regression. Same-day positions absent from closingutilization. Allocation changes incur modeled generic delivery fees/slippage; cashrate0. No taxinterest,custody or ETF tracking error.',
      mapping={'Banks':'Nifty Bank TRI','IT - Software':'Nifty IT TRI','Pharmaceuticals & Biotechnology':'Nifty Pharma TRI','all_other_sectors':'Nifty500TRI explicit fallback'},
      cohort='Frozen470daily-equalweight total-return proxy inherits originalcohort/data-completeness bias and implicitrebalancing; not a historicindex.',
      metric='Exposure-matched means average utilization schedule proxy, not identical beta, stock/sector exposure, intraday timing or holding risk.'))
    raw=OUT/'historical_attempts';raw.mkdir(exist_ok=True)
    urls=['https://www.niftyindices.com/Indices_-_Market_Capitalisation_and_Weightage/indices_dataJan2016.zip',
      'https://www.niftyindices.com/Indices_-_Market_Capitalisation_and_Weightage/indices_dataJan2020.zip',
      'https://archives.nseindia.com/content/indices/IndexInclExcl.xls',
      'https://web.archive.org/cdx/search/cdx?url=niftyindices.com/IndexConstituent/ind_nifty500list.csv&output=json&filter=statuscode:200&from=2015&to=2017&collapse=timestamp:6']
    def fetch(item):
        i,url=item;result={'url':url}
        try:
            r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=25);(raw/f'{i}.bin').write_bytes(r.content);result.update(status=r.status_code,bytes=len(r.content),content_type=r.headers.get('Content-Type'),sha256=hashlib.sha256(r.content).hexdigest())
            if zipfile.is_zipfile(io.BytesIO(r.content)):
                z=zipfile.ZipFile(io.BytesIO(r.content));result['zip_members']=z.namelist()
        except Exception as e:result['error']=type(e).__name__
        return result
    if (OUT/'historical-attempts.json').exists():attempts=json.loads((OUT/'historical-attempts.json').read_text())['attempts']
    else:
        with ThreadPoolExecutor(max_workers=4) as pool:attempts=list(pool.map(fetch,enumerate(urls)))
    save('historical-attempts.json',dict(attempts=attempts,prior_evidence='artifacts/swing_diagnosis/history-feasibility.md',
      conclusion='No certified2016-2026historical500membership+ISIN+delisted/action ledger reconstructed in this phase. Any retrievedmonthlyarchives are aids, not proof ofall500orremovedstockpricecoverage. Do not backdate2024survivors; no earlier-stock performance is claimed.'))
    print('BENCHMARKS_COMPLETE')

if __name__=='__main__':main()
