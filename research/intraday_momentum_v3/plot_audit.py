"""Standalone descriptive feed-quality figure, not a performance chart."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import OUT


def main():
    rows=json.loads((OUT/'detailed-quality.json').read_text())['results']
    meta={r['key']:r['symbol'] for r in json.loads((OUT/'metadata-reconciliation.json').read_text())}
    rows=sorted(rows,key=lambda r:r['fresh_valid_grid_fraction'])
    labels=[meta.get(r['key'],r['key'])+' / '+r['day'][5:] for r in rows];values=[100*r['fresh_valid_grid_fraction'] for r in rows]
    fig,ax=plt.subplots(figsize=(10,7),layout='constrained');fig.set_facecolor('white')
    ax.barh(labels,values,color=['#207f78' if x>=95 else '#718499' for x in values],height=.72)
    ax.axvline(95,color='#b15c28',ls='--',lw=1.4,label='Proposed forward-control threshold: 95%')
    for i,value in enumerate(values):ax.text(value+.4,i,f'{value:.1f}%',va='center',fontsize=8)
    ax.set(xlim=(0,104),xlabel='Fresh valid quote coverage (%)',title='Retained quote continuity is uneven')
    ax.text(0,1.015,'16 prespecified stock-days; 1-second grid, 09:15-15:10 IST; 2-second freshness',transform=ax.transAxes,fontsize=9,color='#4c5864')
    ax.spines[['top','right']].set_visible(False);ax.legend(loc='lower left',fontsize=8)
    fig.savefig(OUT/'archive-quality.png',dpi=170);plt.close(fig)


if __name__=='__main__':main()
