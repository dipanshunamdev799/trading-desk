"""Standalone figure from frozen Phase 2 summaries, without outcome selection."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'directional_research_phase2'


def main():
    data=json.loads((OUT/'option-premium-summary.json').read_text())['groups']
    data=sorted(data,key=lambda r:(r['strategy'],r['expiry_bucket'],r['strike_rule']))
    labels=[r['strategy'].split('|')[0].replace('_',' ')+' · '+('monthly proxy' if r['expiry_bucket']=='month_end_proxy' else 'nearest')+' · '+('ATM' if r['strike_rule']=='ATM' else 'ITM')+f" (n={r['n']})" for r in data]
    means=np.array([r['illustrative_net_mean_rupees_per_lot'] for r in data]);ci=np.array([r['net_ci95_rupees_per_lot'] for r in data]);ys=np.arange(len(data))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig,ax=plt.subplots(figsize=(13,9))
    ax.errorbar(means,ys,xerr=np.vstack([means-ci[:,0],ci[:,1]-means]),fmt='o',markersize=5,color='#155e75',ecolor='#91afb7',capsize=3)
    ax.axvline(0,color='#b4534b',linestyle='--',linewidth=1.2)
    ax.set_yticks(ys,labels);ax.invert_yaxis();ax.grid(axis='x',color='#e5e7eb');ax.set_axisbelow(True)
    ax.set_xlabel('Mean INR per dated lot / trade; illustrative net including dated sale STT',labelpad=12)
    for s in ax.spines.values():s.set_visible(False)
    fig.suptitle('Actual option prices did not validate a profitable candidate',x=.025,ha='left',fontsize=18,fontweight='bold',y=.98)
    fig.text(.025,.93,'All 16 fixed contract-policy groups are shown. Bars are conditional 95% calendar-month bootstrap intervals.',fontsize=11,color='#374151')
    fig.text(.025,.025,'106 underlying signals; 424 policy rows, including duplicate contract selections. Daily first-trade open / official close proxies.\nThese are historical price diagnostics; executable bid/ask, latency and exact total charges remain unverified.',fontsize=10,color='#4b5563')
    fig.subplots_adjust(left=.36,right=.98,top=.88,bottom=.12)
    fig.savefig(OUT/'option-premium-results.png',dpi=160,facecolor='white');plt.close(fig)
    print('Saved option-premium-results.png')


if __name__=='__main__':main()
