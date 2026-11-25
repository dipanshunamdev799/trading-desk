"""Static comparison figures for the matched weekly and monthly cohorts."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import *


def run():
    ms=pd.DataFrame(read('metrics.json')).set_index(['cohort','horizon','model'])
    points=[('T_ROT_DOMESTIC','V7 direction'),('T_ELASTIC_EMBARGO','V7 distribution'),('R_RESIDUAL','Residual rotation'),
            ('A_STRUCTURE_LEVEL','Structure levels'),('A_STRUCTURE_CHANGE','Levels + changes'),('W_STRUCT_EMBARGO','Earlier cutoff')]
    fig,ax=plt.subplots(figsize=(10,5.8));offsets=[(8,3),(-4,12),(7,9),(8,2),(10,13),(10,-11)]
    for i,((name,label),offset) in enumerate(zip(points,offsets)):
        r=ms.loc['primary',5,name];ax.scatter(r.brier,r.crps,s=95,color='#8b95a5' if i<2 else '#1e6481',zorder=3)
        ax.annotate(label,(r.brier,r.crps),xytext=offset,textcoords='offset points',fontsize=10,ha='right' if i==1 else 'left')
    ax.set_xlim(.157,.188);ax.set_ylim(.00937,.01002);ax.set_xlabel('Brier loss (lower is better)');ax.set_ylabel('CRPS (lower is better)')
    ax.grid(alpha=.22);ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Weekly point-score tradeoff on identical historical origins',x=.08,ha='left',fontweight='bold',fontsize=15)
    fig.text(.08,.023,'92 overlapping origins, 19 disjoint windows. Both gains retain search-adjusted intervals that span zero.',color='#495461')
    fig.tight_layout(rect=[.04,.065,.99,.93]);fig.savefig(OUT/'weekly-proper-score-tradeoff.png',dpi=150);plt.close(fig)
    series=[('V6_MONTH_LAG1','V6 raw state + extra lag'),('M_STATE_SMOOTH','V8 smoothed state'),('MS_WINDOW','V8 shorter-window smooth'),('MS_ROLL','Shifted state control')]
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),sharey=True)
    for ax,metric in zip(axes,['brier','crps']):
        vals=[ms.loc[('primary',21,name),metric] for name,label in series]
        ax.barh(range(len(vals)),vals,color=['#8b95a5','#1e6481','#367a69','#b56a35'],height=.65)
        ax.set_yticks(range(len(vals)),[label for _,label in series]);ax.set_xlim(0,max(vals)*1.23)
        for j,v in enumerate(vals):ax.text(v+max(vals)*.02,j,f'{v:.6f}',va='center')
        ax.set_xlabel(metric.upper()+' (lower is better)');ax.spines[['top','right']].set_visible(False)
    axes[0].invert_yaxis();fig.suptitle('Monthly state timing challenged by a shifted control',x=.04,ha='left',fontweight='bold',fontsize=15)
    fig.text(.04,.025,'76 overlapping origins, about four disjoint outcomes. The shifted control is a fit-only falsification.',color='#495461')
    fig.tight_layout(rect=[.02,.08,.98,.92]);fig.savefig(OUT/'monthly-persistence-falsification.png',dpi=150);plt.close(fig)


if __name__=='__main__':run()
