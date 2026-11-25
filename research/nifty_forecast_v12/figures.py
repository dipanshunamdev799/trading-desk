"""Compact scientific figures for the report suite."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import *


def phase():
    data=pd.read_csv(OUT/'phase-predictions.csv')
    laws=data[data.model.str.match(r'PH_NATIVE_\d\d$')]
    base=data[data.model.eq('PH_NATIVE_PHASE_MIXTURE')]
    fig,axes=plt.subplots(2,2,figsize=(10.8,6.4),layout='constrained')
    for i,h in enumerate([5,21]):
        a=laws[laws.horizon.eq(h)].groupby('model')[['brier','crps']].mean().sort_index()
        b=base[base.horizon.eq(h)][['brier','crps']].mean()
        for j,metric in enumerate(['brier','crps']):
            ax=axes[i,j]
            x=np.arange(len(a))
            ax.plot(x,a[metric],'.-',linewidth=1.25,color='#255984',label='Individual phases')
            ax.axhline(b[metric],color='#9A5C1F',ls='--',lw=1.5,label='Equal mixture')
            value=.25 if metric=='brier' else .011058 if h==5 else .025420
            ax.axhline(value,color='#626567',ls=':',lw=1.15,label='Symmetric reference')
            ax.set_title(f'{h} sessions · {metric.upper() if metric=="crps" else "Brier"}')
            ax.set_xlabel('Fixed trading-session phase')
            ax.set_xticks(x if h==5 else np.arange(0,len(x),2))
            ax.grid(axis='y',alpha=.20)
            ax.spines[['top','right']].set_visible(False)
    h,l=axes[0,0].get_legend_handles_labels()
    fig.legend(h,l,loc='outside upper center',ncols=3,frameon=False)
    fig.savefig(OUT/'phase-sensitivity.png',dpi=160,bbox_inches='tight')
    plt.close(fig)


def market_curve():
    info=pd.read_csv(OUT/'surface-quality.csv')
    a=info[info.method.eq('TRADE')&info.density_status.eq('accepted')&info.future_close.notna()].sort_values(['day','expiry'])
    ref=a.iloc[len(a)//2]
    wanted=(ref.day,ref.expiry,ref.method)
    found=next(d for k,d in bundle_entries(OUT/'option-density-atoms.npz') if k==wanted)
    strikes=pd.read_csv(OUT/'strike-implied-volatility.csv.gz',low_memory=False)
    q=strikes[strikes.day.eq(ref.day)&strikes.expiry.eq(ref.expiry)&strikes.iv_valid]
    q=q[q.moneyness_forward.between(ref.support_lo_k,ref.support_hi_k)]
    k=q.moneyness_forward.to_numpy();out=q.premium_fraction_forward_undiscounted.to_numpy()
    actual=out+np.maximum(1-k,0)
    fitted=np.maximum(1+found.a[None,:]-k[:,None],0)@found.w
    fig,axes=plt.subplots(1,2,figsize=(10.7,4.0),layout='constrained')
    axes[0].scatter((k-1)*100,actual*100,s=9,color='#596B87',label='Stitched traded prices')
    axes[0].plot((k-1)*100,fitted*100,color='#B25C32',label='Fitted option curve')
    axes[0].set_ylabel('Undiscounted call value (% of forward)')
    axes[0].legend(frameon=False)
    ax=axes[1]
    ax.step(found.a*100,np.cumsum(found.w)*100,where='post',color='#206C70')
    lo=(ref.support_lo_k-1)*100;hi=(ref.support_hi_k-1)*100
    if min(found.a)*100<lo:ax.axvspan(min(found.a)*100,lo,color='#D0A585',alpha=.30)
    if max(found.a)*100>hi:ax.axvspan(hi,max(found.a)*100,color='#D0A585',alpha=.30)
    ax.set_ylabel('Cumulative priced mass (%)')
    ax.set_title('Risk-neutral law and extrapolated wings')
    for x in axes:
        x.set_xlabel('Endpoint or strike relative to forward (%)')
        x.grid(axis='y',alpha=.18)
        x.spines[['top','right']].set_visible(False)
    fig.suptitle(f'NIFTY surface from {ref.day} · expiry {ref.expiry}')
    fig.savefig(OUT/'option-curve-check.png',dpi=160,bbox_inches='tight')
    plt.close(fig)


if __name__=='__main__':
    phase()
    market_curve()
