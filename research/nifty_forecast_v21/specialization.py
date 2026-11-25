"""Move one source at a time through the same constituent and sector laws."""
from scipy.special import ndtr

from .common import *
from .joint import to_log,geo_draw,lagged_fit
from .learning import TARGETS
from .universe import SECTOR_NAMES
from research.nifty_forecast_v17.weekly import evaluate

ABLATORS=('technical','counts','semantic_and_surprise','observed_reaction','delivery_and_deals','pooled','random_aux_labels','shifted_company')


def run():
    panel=np.load(OUT/'component-panel.npz',allow_pickle=False)
    data=np.load(OUT/'equity-forecast-laws.npz',allow_pickle=False)
    years=np.load(OUT/'joint-simultaneous-laws.npz',allow_pickle=False)
    d=csv('joint-fit-receipts.csv')
    cm={v:i for i,v in enumerate(data['models'])}
    days=pd.Index(panel['days']);states=panel['market_features'];fields=list(panel['market_fields'])
    cases=[];sector=[];cal=[]
    base_draw=years['stock_returns'];s0=years['sector_returns'];ids=years['asset_indices'];item=years['asset_weights'];basis=years['basis']
    w=np.full(base_draw.shape[1],1/base_draw.shape[1]); sector_ix=[SECTOR_NAMES.index(k) for k in SECTORS]
    keep_fields=[j for j in range(states.shape[1]) if not fields[j].startswith('position_')]
    for h in HORIZONS:
        forecasts=data[f'mean{h}'];σ=data[f'sigma{h}'];index=panel[f'index{h}'];target=panel[f'target{h}'];cohort=panel[f'cohort{h}'];end=panel[f'end{h}'];
        eligible=panel['eligible'];m=panel[f'sector_target{h}'];z=m[:,sector_ix]
        for rid in d.index[d.horizon.eq(h)]:
            day=d.at[rid,'day'];i=days.get_loc(day)
            v=ids[rid]>=0
            stocks=ids[rid,v];wealth=base_draw[rid][:,v].astype(float);q=item[rid,v];ref=to_log(wealth)
            parent=np.nan_to_num(forecasts[cm['pooled'],i,stocks,0])
            actual=index[i]
            head=dict(day=day,horizon=h,cohort=cohort[i],end=end[i])
            for name in ABLATORS:
                pred=forecasts[cm[name],i,stocks,0]
                pred=np.where(np.isfinite(pred),pred,parent)
                delta=to_log(pred)-to_log(parent)
                a=geo_draw(delta,ref)@q+basis[rid]
                e=evaluate(a,w,actual)
                cases.append(head|dict(model=name,abs_location_change=float(np.abs(delta)@q),brier=e['brier'],crps=e['crps'],
                                      mae=e['mae'],mean=e['mean'],p=e['p'],covered=e['covered']))
            t=np.flatnonzero((end<day)&(np.arange(len(days))<i)&np.isfinite(index)&np.isfinite(z).all(axis=1))[-140:]
            both=lagged_fit(states,z,t,i,155);no_pos=lagged_fit(states[:,keep_fields],z,t,i,155)
            a=s0[rid]
            new=geo_draw(to_log(no_pos)-to_log(both),to_log(a))
            for j,name in enumerate(SECTORS):
                v0=evaluate(new[:,j],w,z[i,j]);v1=evaluate(a[:,j],w,z[i,j])
                sector.append(head|dict(sector=name,without_position_crps=v0['crps'],with_position_crps=v1['crps'],
                                        without_position_brier=v0['brier'],with_position_brier=v1['brier']))
            for name in ('history','technical','pooled','independent','random_aux_labels'):
                for label,k in [('absolute',0),('outperform_market',4)]:
                    x=target[i,:,k];y=forecasts[cm[name],i,:,k];ok=np.isfinite(x)&np.isfinite(y)&eligible[i]
                    prob=ndtr(y[ok]/σ[i,ok,k]) if k==0 else np.clip(y[ok],.005,.995)
                    bins=np.minimum((prob*5).astype(int),4)
                    for b in np.unique(bins):
                        g=bins==b
                        cal.append(head|dict(model=name,target=label,bin=int(b),n=int(g.sum()),mean_p=float(prob[g].mean()),
                              observed=float((x[ok][g]>0).mean())))
    c=pd.DataFrame(cases);s=pd.DataFrame(sector);p=pd.DataFrame(cal)
    write('fixed-joint-source-ablation-cases.csv.gz',c)
    write('sector-aggregate-position-cases.csv.gz',s)
    write('stock-probability-calibration.csv',p.groupby(['horizon','model','target','bin'],as_index=False).agg(
        dates=('day','nunique'),stock_cases=('n','sum'),predicted=('mean_p','mean'),observed=('observed','mean')))
    v=c.groupby(['horizon','model','cohort'],as_index=False).agg(n=('day','size'),brier=('brier','mean'),crps=('crps','mean'),
        mae=('mae','mean'),mean_shift=('abs_location_change','mean'),cover=('covered','mean'))
    write('source-propagation-scoreboard.csv',v)
    save('source-propagation-config.json',dict(method='Recenter each original stock scenario using alternative company estimates while keeping its dependence and tracking-basis atom.',
         role='Tests source propagation to the weighted index at the same 08:55 snapshot. Separate sector comparison removes market-wide participant fields from the same chronological fit.',
         company_calibration='Five probability bins. Day-level bin means are weighted equally across dates.'))
    print('Tracked source propagation over',len(c),'matched index cases',flush=True)


if __name__=='__main__':
    run()
