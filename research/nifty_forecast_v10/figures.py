"""Fixed-origin learning curves in both probability and distribution scores."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import *


def run():
    a=pd.read_csv(OUT/'learning-curves-fixed-origins.csv')
    order=['85','126','189','252','300','MAX']
    display={'PLAIN':('Recent Ridge','#272B33'),'SPREAD':('Spread dates','#137F78'),
             'BLOCK':('Block averaging','#BD641C'),'STUDENT':('Volatility Student-t','#5863A6')}
    fig,panels=plt.subplots(2,2,figsize=(10.6,6.8),layout='constrained')
    for row,h in enumerate([5,21]):
        data=a[a.horizon.eq(h)].set_index('model')
        for col,metric in enumerate(['brier','crps']):
            ax=panels[row,col]
            for model,(name,color) in display.items():
                choices=data.loc[[f'LC_{model}_{t}' for t in order]]
                ax.plot(order,choices[metric],label=name,color=color,marker='o',markersize=3.4,linewidth=1.7)
            ax.set_title(f'{h} sessions · {data.origins.iloc[0]} shared origins · {data.disjoint.iloc[0]} disjoint')
            ax.set_ylabel('Brier' if metric=='brier' else 'CRPS')
            if row==1:ax.set_xlabel('Eligible training rows (MAX = expanding)')
            ax.grid(axis='y',alpha=.24,linewidth=.55)
            ax.spines[['top','right']].set_visible(False)
    handles,names=panels[0,0].get_legend_handles_labels()
    fig.legend(handles,names,loc='outside upper center',ncols=4,frameon=False)
    fig.savefig(OUT/'learning-curves-fixed-origins.png',dpi=160,bbox_inches='tight')
    plt.close(fig)


if __name__=='__main__':run()
