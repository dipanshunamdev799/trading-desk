"""Render predeclared reference sample paths and drawdowns, not a selected winner."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts'/'project_alpha'


def main():
    candle=pd.read_csv(OUT/'exit-trades.csv')
    candle=candle[(candle.configuration=='month_end_proxy|ATM|time60')&(candle.ambiguity_mode=='adverse_first')&(candle.status=='observed_candle_proxy')]
    quotes=pd.read_csv(OUT/'exit-stream-trades.csv')
    quotes=quotes[(quotes.configuration=='ATM|time60|lat250|wait2000')&(quotes.execution_mode=='frame_snapshot')&(quotes.status=='observed_bid_ask_snapshot_proxy')]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig,axes=plt.subplots(2,2,figsize=(13,7),sharex='col')
    for col,data,title,pnl in [(0,candle,'November: monthly ATM / 60m candle proxy','severe_net_rupees_per_lot'),(1,quotes,'October: ATM / 60m received bid-ask proxy','illustrative_net_rupees_per_lot')]:
        data=data.sort_values('exit_at');values=data[pnl].to_numpy();curve=np.r_[0,np.cumsum(values)];drawdown=curve-np.maximum.accumulate(curve);steps=np.arange(len(curve))
        axes[0,col].plot(steps,curve,'o-',color='#155e75');axes[0,col].set_title(title,loc='left',fontsize=11,pad=14)
        axes[0,col].set_ylabel('Cumulative net INR / one dated lot')
        axes[1,col].fill_between(steps,drawdown,0,color='#c97970',alpha=.6);axes[1,col].plot(steps,drawdown,color='#9d4138')
        axes[1,col].set_ylabel('Drawdown at trade close, INR');axes[1,col].set_xlabel('Closed trade number')
        for row in [0,1]:
            axes[row,col].axhline(0,color='#6b7280',linewidth=.7);axes[row,col].grid(color='#e5e7eb');axes[row,col].set_axisbelow(True)
            for s in axes[row,col].spines.values():s.set_visible(False)
    fig.suptitle('Small sample paths do not establish positive expectancy',x=.02,ha='left',fontsize=17,fontweight='bold',y=.98)
    fig.text(.02,.91,'Fixed reference configurations, without performance selection. Each curve has a different price-evidence and cost model.',fontsize=11,color='#4b5563')
    fig.text(.02,.025,'Seven November candle trades and three October snapshot trades; inspected historical periods. No account compounding or validated capital return.\nDrawdowns at trade close omit unobserved intratrade equity. Individual source prices, costs and event journals are retained.',fontsize=9,color='#4b5563')
    fig.subplots_adjust(left=.09,right=.98,top=.81,bottom=.13,hspace=.35,wspace=.28);fig.savefig(OUT/'equity-drawdown.png',dpi=160,facecolor='white');plt.close(fig)
    print('Saved equity-drawdown.png')


if __name__=='__main__':main()
