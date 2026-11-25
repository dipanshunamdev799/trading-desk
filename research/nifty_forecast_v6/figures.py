"""Standalone research figures from saved scores; no new experiments."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import *

def run():
    m={(r['horizon'],r['model']):r for r in read('metrics.json')+read('benchmark-metrics.json')}
    names=['I03_nosize','L01','F_NO_DEFENSIVE','W2_DEF_NORM','W2_NOAUTO_VOLUME']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':False})
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),sharey=True)
    for ax,metric,title in zip(axes,['brier','crps'],['Weekly probability loss (Brier)','Weekly distribution loss (CRPS)']):
        values=[m[5,n][metric] for n in names];ax.barh(range(len(names)),values,color=['#94a3b8','#64748b','#225d81','#37846e','#b85c3d'],height=.64)
        ax.set_yticks(range(len(names)),names);ax.set_title(title,loc='left',fontweight='bold');ax.set_xlim(0,max(values)*1.22);ax.set_xlabel('Lower is better; fractional-return units for CRPS')
        for j,v in enumerate(values):ax.text(v+max(values)*.015,j,f'{v:.6f}',va='center',fontsize=9)
    axes[0].invert_yaxis();fig.suptitle('NIFTY V6: improved historical weekly point scores',x=.02,ha='left',fontweight='bold',fontsize=14)
    fig.text(.02,.01,'92 overlapping origins / 19 disjoint windows. All history exposed. Search-adjusted improvement ranges include zero.',fontsize=10,color='#4b5563')
    fig.tight_layout(rect=[0,.06,1,.92]);fig.savefig(OUT/'weekly-results.png',dpi=160);plt.close(fig)
    nulls=read('monthly-expanded-nulls-metrics.json');rows=[m[21,'M_WEEKSTATE'],m[21,'M2_STATE_LAG1'],next(r for r in nulls if r['model']=='DIAGNOSTIC_STATE' and r['shift']==21),next(r for r in nulls if r['model']=='DIAGNOSTIC_STATE' and r['shift']==5)]
    labels=['Weekly-state model','One extra state lag','21-session shifted-state control','5-session shifted-state control']
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),sharey=True)
    for ax,metric,title in zip(axes,['brier','crps'],['Monthly Brier','Monthly CRPS']):
        values=[r[metric] for r in rows];ax.barh(range(4),values,color=['#225d81','#37846e','#d9903c','#b85c3d'],height=.64);ax.set_yticks(range(4),labels);ax.set_title(title,loc='left',fontweight='bold');ax.set_xlim(0,max(values)*1.22);ax.set_xlabel('Lower is better')
        for j,v in enumerate(values):ax.text(v+max(values)*.015,j,f'{v:.6f}',va='center',fontsize=9)
    axes[0].invert_yaxis();fig.suptitle('Monthly state mechanism remains inconclusive',x=.02,ha='left',fontweight='bold',fontsize=14)
    fig.text(.02,.01,'76 overlapping origins / only 4 disjoint windows. Shifted controls are diagnostic corruptions, not eligible forecast models.',fontsize=10,color='#4b5563');fig.tight_layout(rect=[0,.06,1,.92]);fig.savefig(OUT/'monthly-falsification.png',dpi=160);plt.close(fig)
    print('Rendered weekly and monthly research figures',flush=True)

if __name__=='__main__':run()
