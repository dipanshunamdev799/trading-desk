"""Render the frozen finalists, preserving distinct intraday/daily return units."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts'/'directional_research'


def main():
    intraday = json.loads((OUT/'lab-summary.json').read_text())
    daily = json.loads((OUT/'daily-summary.json').read_text())
    # Names are read from frozen outputs; no new performance selection.
    top = intraday.get('finalists', intraday.get('selected', []))
    if not top:
        raise RuntimeError('Finalist list absent in lab summary')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titleweight':'bold'})
    fig, axes = plt.subplots(1,2,figsize=(15,7),gridspec_kw={'width_ratios':[1.2,1]})
    for ax, rows, mean, interval, title, xlabel in [
        (axes[0],top,'holdout_net2_mean','net2_mean_ci95','Intraday: 11 frozen family finalists','Mean index points / trade, after illustrative 2 points'),
        (axes[1],daily['finalists'],'holdout_net5_bps','net5_ci95_bps','Multi-day: 4 frozen family finalists','Mean index basis points / trade, after illustrative 5 bps')]:
        rows=sorted(rows,key=lambda r:r['family'])
        y=np.arange(len(rows));m=np.array([r[mean] for r in rows]);ci=np.array([r[interval] for r in rows])
        ax.errorbar(m,y,xerr=np.vstack([m-ci[:,0],ci[:,1]-m]),fmt='o',color='#155e75',ecolor='#7ea6b0',capsize=4,markersize=6)
        ax.axvline(0,color='#be4b45',linewidth=1.2,linestyle='--')
        ax.set_yticks(y,[r['family'].replace('_',' ')+'  (n='+str(r.get('holdout_n'))+')' for r in rows])
        ax.invert_yaxis();ax.set_title(title,loc='left',pad=16);ax.set_xlabel(xlabel,labelpad=12)
        ax.grid(axis='x',color='#e5e7eb');ax.set_axisbelow(True)
        for spine in ax.spines.values():spine.set_visible(False)
    fig.suptitle('Positive averages have not established a dependable edge',x=.025,ha='left',fontsize=19,fontweight='bold',y=.98)
    fig.text(.025,.91,'Every finalist\'s 95% block-bootstrap interval includes zero. No finalist passes its descriptive gate.',fontsize=12,color='#374151')
    fig.text(.025,.035,'Historical final-period estimates; intervals are conditional and not adjusted for the strategy search.\nThese measure NIFTY direction, not executable option-premium P&L. Data frozen through 8 Nov 2026.',fontsize=10,color='#4b5563')
    fig.subplots_adjust(left=.17,right=.98,top=.81,bottom=.17,wspace=.75)
    fig.savefig(OUT/'research-results.png',dpi=160,facecolor='white')
    plt.close(fig)
    print('Saved research-results.png')


if __name__=='__main__':
    main()
