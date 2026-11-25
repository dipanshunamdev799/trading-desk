"""Historical fixed-window case chart and individual conditional survival curves."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .common import *
from .data import Daily
from .scores import positions_of_hit
from .sequential import TICK


def run():
    source=Daily.load()
    s=pd.read_csv(OUT/'sequential-scores.csv.gz',usecols=['horizon','origin','model','checkpoint','vol_q10','vol_q50','vol_q90',
             'endpoint','endpoint_q10','endpoint_q50','endpoint_q90','p_up','range_q50','vol','brier','endpoint_crps'])
    keep=['frozen','iv_restart','vol_state','analogue','full']
    demo=s[s.origin.eq(DEMO)&s.model.isin(keep)]
    write('historical-example-updates.csv',demo.sort_values(['horizon','checkpoint','model']))
    entries=read('joint-update-archive.json')['files']
    calendar=pd.read_csv(OUT/'update-calendar.csv')
    case_rows=[]
    for horizon in HORIZONS:
        record=next(x for x in entries if x['horizon']==horizon and x['origin']==DEMO)
        c=calendar[calendar.origin.eq(DEMO)&calendar.horizon.eq(horizon)]
        prices=source.prices.iloc[source.positions[DEMO]+1:source.positions[DEMO]+horizon+1].to_numpy()/c.origin_reference.iloc[0]
        with np.load(OUT/record['file'],allow_pickle=False) as k:
            for row in c.itertuples(index=False):
                for name in ['historical','iv_restart','gjr_restart','particle','hybrid','analogue']:
                    f=np.exp(k[f'k{row.checkpoint:02}_{name}']*TICK)*row.realized_price_ratio
                    for j,side in [(1,'upper'),(2,'lower')]:
                        threshold=1.02 if j==1 else .98
                        hit=int(positions_of_hit(prices[:,j],threshold,j==1))
                        actual=hit-row.checkpoint
                        # If the level is already touched, report the resolved state with no scoring.
                        resolved=hit<=row.checkpoint
                        p=positions_of_hit(f[:,:,j],threshold,j==1)
                        for step in range(1,row.remaining+1):
                            case_rows.append(dict(horizon=horizon,origin=DEMO,checkpoint=row.checkpoint,asof=row.asof,
                              target=row.target,forecast_step=step,model=name,barrier=threshold,side=side,
                              already_touched=resolved,cdf=1. if resolved else float((p<=step).mean()),
                              day_probability=0. if resolved else float((p==step).mean()),actual_by_step=int(actual<=step)))
    write('historical-example-passage.csv',pd.DataFrame(case_rows))
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for h,j in [(5,0),(21,1)]:
        panel=demo[demo.horizon.eq(h)]
        by={name:g.sort_values('checkpoint') for name,g in panel.groupby('model')}
        actual=by['frozen']
        k=actual.checkpoint.to_numpy()
        for (target,units,a) in [('endpoint',100,axes[0,j]),('vol',100,axes[1,j])]:
            f=by['vol_state']
            a.fill_between(k,f[target+'_q10']*units,f[target+'_q90']*units,alpha=.17,color='#5e87ba',label='IV/GJR central 80%')
            a.plot(k,f[target+'_q50']*units,linewidth=2,color='#1f4b82',label='IV/GJR median')
            a.plot(k,by['iv_restart'][target+'_q50']*units,linestyle='-.',color='#375e4f',label='Restarted IV median')
            a.plot(k,actual[target+'_q50']*units,linestyle='--',color='#595959',label='Frozen median')
            a.plot(k,units*actual[target],linestyle=':',color='#aa3c27',linewidth=2,label='Realized at endpoint')
            a.set_xlabel('Completed sessions since origin')
            a.set_ylabel('Endpoint return (%)' if target=='endpoint' else 'Annualized realized volatility (%)')
            a.set_title(f'{h} sessions, {h==5 and "weekly" or "monthly"}')
            a.grid(alpha=.2)
            if j==0 and target=='endpoint':
                a.legend(loc='best',frameon=False,fontsize=8)
    fig.suptitle(f'NIFTY fixed-endpoint updates from {DEMO}\nReconstructed historical case')
    fig.savefig(OUT/'historical-fixed-endpoint-updates.png',dpi=180)
    plt.close(fig)


if __name__=='__main__':
    run()
