"""Static figures for matched-cohort research output."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import *


def run():
    results=pd.read_csv(OUT/'learning-curves.csv')
    later=results[(results.cohort=='later')&results.model.isin([f'L_ROT_{i}' for i in [85,126,189,252,300,'MAX']])].set_index('model')
    models=[f'L_ROT_{i}' for i in [85,126,189,252,300,'MAX']];v=later.loc[models]
    x=np.arange(len(v));early=results[(results.cohort=='early')&(results.model=='L_ROT_85')].iloc[0]
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for ax,col,title in zip(axes,['brier','crps'],['Probability loss','Distribution loss']):
        ax.plot(x,v[col],color='#246386',marker='o',linewidth=2,label='Later rotation, 92 matched origins');ax.scatter([0],[early[col]],color='#a45235',s=68,zorder=4,label='Earlier rotation at 85 observations')
        ax.axhline(later.iloc[0]['matched_history_'+col],ls='--',color='#64748b',label='Later historical benchmark')
        ax.set_xticks(x,['85','126','189','252','300','Expanding']);ax.set_xlabel('Mature training observations');ax.set_ylabel(col.upper()+' (lower is better)')
        ax.set_title(title,loc='left',fontweight='bold');ax.grid(axis='y',alpha=.22);ax.spines[['top','right']].set_visible(False)
    axes[0].legend(loc='upper right',fontsize=8,frameon=False)
    fig.suptitle('Later rotation depends on access to more training history',fontsize=15,fontweight='bold',x=.06,ha='left')
    fig.text(.06,.02,'Earlier point uses 173 exposed origins. Later size comparisons use identical 92 dates. Shorter training is also different training.',fontsize=9,color='#475569')
    fig.tight_layout(rect=[.03,.07,.99,.92]);fig.savefig(OUT/'matched-learning-curves.png',dpi=155);plt.close(fig)
    c=pd.read_csv(OUT/'combined-cohort-leaderboard.csv');c=c[c.horizon==5].set_index('model')
    ids=['P_HIST','P_ROT','P_CLUSTER','J9_STATIC','J9_REL_SHRINK'];labels=['Historical law','Residual rotation','Cluster-balanced rotation','Fixed history blend','Reliability-history blend']
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),sharey=True);pos=np.arange(len(ids))
    for ax,metric,label in zip(axes,['Brier','CRPS'],['Brier','CRPS']):
        a=c.loc[ids,'early_'+metric];b=c.loc[ids,'late_'+metric]
        ax.barh(pos-.17,a,height=.3,label='Earlier (173)',color='#b68971');ax.barh(pos+.17,b,height=.3,label='Later (92)',color='#32829b')
        ax.set_yticks(pos,labels);ax.set_xlabel(label+' (lower is better)');ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.16)
    axes[0].invert_yaxis();axes[1].legend(frameon=False,loc='lower right',bbox_to_anchor=(1,1.005),ncol=2,fontsize=9)
    fig.suptitle('Weekly model tradeoffs across the same two cohorts',x=.04,ha='left',fontweight='bold',fontsize=15)
    fig.text(.04,.02,'All dates are research-exposed. Distribution blending narrows the cohort gap while giving up the lowest later CRPS.',color='#475569',fontsize=9)
    fig.tight_layout(rect=[.02,.07,.99,.91]);fig.savefig(OUT/'weekly-cohort-tradeoffs.png',dpi=155);plt.close(fig)


if __name__=='__main__':run()
