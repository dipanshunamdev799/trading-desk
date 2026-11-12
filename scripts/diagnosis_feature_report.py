"""Render existing causal-feature diagnostics, without selecting a new rule."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'artifacts/swing_diagnosis'

def table(frame):
    cols=list(frame.columns)
    def fmt(v):return f'{v:.4f}' if isinstance(v,(float,np.floating)) else str(v)
    return '\n'.join(['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']+['| '+' | '.join(map(fmt,row))+' |' for row in frame.itertuples(index=False,name=None)])

def main():
    finding=json.loads((P/'features-findings.json').read_text());design=json.loads((P/'features-design.json').read_text())
    f=pd.read_csv(P/'characteristics-forward-validation.csv');d=f[(f.bin=='selected_minus_opposite')&(f.stage!='development')]
    r=pd.read_csv(P/'regime-development-gates.csv');rg=r[(r.dimension=='expansion')&(r.stage!='development')]
    t=pd.read_csv(P/'breakdown-trade-diagnostics.csv')
    overall=t.groupby('stage').agg(trades=('net_r','size'),gross_r=('gross_r','mean'),fee_r=('fee_r','mean'),net_r=('net_r','mean'),forward5_pct=('entry_forward_close5_pct','mean'),forward10_pct=('entry_forward_close10_pct','mean'),forward20_pct=('entry_forward_close20_pct','mean')).reset_index()
    stop=t[t.reason.isin(['stop','gap_stop'])].groupby('stage').agg(stop_trades=('net_r','size'),mean_net_r=('net_r','mean'),forward20_pct=('entry_forward_close20_pct','mean'),pre_exit_mfe_over_1R_pct=('pre_exit_bar_mfe_r',lambda x:100*x.ge(1).mean())).reset_index()
    alln=t.groupby('stage').size();stop['share_all_trades_pct']=stop.apply(lambda x:100*x.stop_trades/alln[x.stage],axis=1)
    subset=r[(r.stage!='development')]
    subset.to_csv(P/'regime-forward-summary.csv',index=False)
    rows=['# Failure, causal stock characteristics and market regimes','',
      '**Basis:** '+finding['journal_basis'],'',
      '**Verified fact:** '+f"{finding['trades']:,} two-year trades from48 frozen finalists. They are separate stock sleeves and overlapping correlated rules, not one funded portfolio. Stage attribution here is by entry quarter within the continuous two-year path; it differs from resetting cash at each reported stage.",'',
      '## What failed: gross entries, exits and costs','',table(overall),'',
      'R is net profit divided by modeled initial cash risk. Gross R removes recorded transaction fees but retains slippage and the original path. Forward close columns are price-only percentage returns from each actual entry fill to the 5th/10th/20th session close; they exclude dividends, fees and alternative-path cash constraints. They diagnose entry timing and are not executable alternative strategies.','',
      '**Statistical observation:** development and final trade sets lose before fees as well as after fees; the validation gross margin is approximately flat and costs turn it negative. Cost is material, but it is not a sufficient explanation of the entire failure.','',
      table(stop),'',
      'The stop rows describe exits, not causation. Pre-exit excursions include complete held bars only and exclude exit-day extremes to avoid unknowable ordering. A later recovery after a stop does not prove that widening/removing that stop improves net portfolio performance. The existing coarse execution ablations and a matched entry-level replay are the appropriate controlled tests.','',
      '[Full breakdowns](breakdown-all-dimensions.csv) cover year/month, stock, sector, entry family, exit policy/reason, holding period, market trend/volatility/expansion. All executions are long only; there is no long-versus-short comparison.','',
      '## Causal stock-characteristic experiment','',
      'Thirteen frozen descriptors were sampled strictly before each of eight quarter boundaries. Their cross-sectional terciles used information available then. Each stock-quarter includes inactive rules/zero-trade cells. High-versus-low orientation was fitted only on original375 development companies in the first four quarters, and only trades with exits observable before the fit boundary could determine orientation. The95 reserved companies were excluded from fitting.','',
      'The outcome is average net P&L per original1m capital across all48 frozen stock-rule accounts, attributed to the next entry quarter. Contrasts sum quarter-level per-stock averages; they are percentage points of initial capital, not a new compounded portfolio return. Ten-session common-market-date block bootstrap retains same-date stock/rule dependence; BH corrects13 descriptor tests within each stage/pool.','',
      '**Statistical observation:** no positive selected-bin advantage survives BH q<=.05 in validation or final in either company pool. Some selected signs significantly fail in the reserved validation group. No stock selector is validated.','',
      table(d[['feature','orientation','stage','pool','delta','lo','hi','bh_q']]),'',
      '![Chronological feature transfer](charts/features-forward-transfer.png)','',
      'Feature definitions: ATR14/close;60-session volatility; absolute displacement/absolute travel efficiency;60-session return minus NIFTY; lagged20-session traded-value proxy; negative volume CV; frequency of >1% overnight gaps; return lag1 autocorrelation; NIFTY return correlation; leave-self-out same-sector peer return; normalized signed60-session trend; sign persistence; and frequency of rejections of the prior20-session low within0.5ATR. Historical sector labels, complete-data selection and volume-unit hypotheses are inherited limitations. Sector-peer momentum is not true sector-index relative strength.','',
      '## Regime-conditioned observations','',
      'Market trend uses signed NIFTY60-session return/(60-session daily-return volatility*sqrt60): absolute value<.5 is sideways; >=1 strong bull;0.5..1 weak bull; <=-1 strong bear; remainder weak bear. High volatility is20-session volatility above its prior252-session median. Expansion is vol20/vol60>1.2; contraction<.8. All labels use completed signal-day data.','',
      'Within each of four broad family groups, one regime per dimension was selected on development375 only, requiring100 training trades. It was then held fixed. The table below shows the development-selected expansion gate. Intervals use3000 common-calendar10-session blocks and are conditional on the selected frozen rule set; no claim is based on independent trade counts.','',
      table(rg[['broad_family','chosen_regime','stage','pool','n_selected','selected_signal_days','selected_months','largest_month_trade_fraction','selected_net_r','selected_r_lo','selected_r_hi','universal_net_r','delta_r_lo','delta_r_hi']]),'',
      '![Expansion gate diagnostic](charts/regime-expansion-transfer.png)','',
      '**Hypothesis:** volatility expansion may identify a market state worth testing with a small frozen rule set. The subset results are not an executable regime strategy. Suppressing a trade can permit a later entry, alter cash/risk sizing and change held corporate-action entitlements. A fresh gated replay and a funded portfolio are required, and any such test here is a new retrospective experiment triggered by these observations.','',
      '## Limits and next controlled experiments','',
      'All calendar dates and48 finalists were already researched. Causal descriptors do not undo strategy-selection leakage or create an untouched holdout. There are only eight quarters, forward outcomes overlap, market cycles are limited, family signals are correlated, and13 features plus12 regime selections add search degrees of freedom. The bootstrap does not remove these limitations.','',
      '1. Replay the fixed market-volatility-expansion gate on prespecified representative rules, comparing skipped/added entries, cash utilization and date concentration; preserve the universal control.','2. Check whether conditional performance remains after official sector-TRI controls, avoiding credit for a sector rally. Selected Bank/IT/Pharma TRI were acquired separately; a true stock/sector-index relative-strength selector was not part of this frozen13-descriptor diagnostic.','3. Test entry quality against risk/exposure-matched random entries and then vary one stop/exit rule on exactly matched decisions.','4. Freeze any surviving stock/regime selector for genuinely new prospective data. Preserve calendar and company reservations; do not optimize again on the final months.','',
      'Reproduction: `python scripts/diagnosis_features.py --corrected`, then `python scripts/diagnosis_feature_report.py`. Original-path diagnostic outputs remain in `features_original/`. The design, orientations, stock-quarter cells, full breakdowns and confidence values remain machine-readable beside this report.','']
    (P/'features-report.md').write_text('\n'.join(rows),encoding='utf-8')
    chart=P/'charts';chart.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(14,8),sharey=True);names=list(design['feature_names'])
    for ax,pool in zip(axes,['development375','reserved95']):
        for j,(stage,color) in enumerate([('validation','#1d6b95'),('final','#b04b2c')]):
            a=d[(d.pool==pool)&(d.stage==stage)].set_index('feature').reindex(names);y=np.arange(len(names))+(j-.5)*.18
            ax.errorbar(a.delta,y,xerr=np.vstack([a.delta-a.lo,a.hi-a.delta]),fmt='o',color=color,label=stage,capsize=2,markersize=4)
        ax.axvline(0,color='#444',lw=.8);ax.set_yticks(range(len(names)),names);ax.set_title(pool);ax.set_xlabel('Selected-minus-opposite P&L (percentage points)');ax.grid(axis='x',alpha=.2);ax.legend()
    axes[0].invert_yaxis();fig.suptitle('Historical-only stock descriptors: subsequent-quarter transfer\nConditional retrospective contrasts; common-date block95% intervals');fig.tight_layout();fig.savefig(chart/'features-forward-transfer.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(13,5),sharey=True);names=['EMA_KAMA','MACD_PPO','hybrid','support_resistance']
    for ax,pool in zip(axes,['development375','reserved95']):
        for j,(stage,color) in enumerate([('validation','#1d6b95'),('final','#b04b2c')]):
            a=rg[(rg.pool==pool)&(rg.stage==stage)].set_index('broad_family').reindex(names);y=np.arange(4)+(j-.5)*.18
            ax.errorbar(a.selected_net_r,y,xerr=np.vstack([a.selected_net_r-a.selected_r_lo,a.selected_r_hi-a.selected_net_r]),fmt='o',color=color,label=stage,capsize=2)
        ax.axvline(0,color='#444',lw=.8);ax.set_yticks(range(4),names);ax.set_title(pool);ax.set_xlabel('Conditional mean net R per selected trade');ax.grid(axis='x',alpha=.2);ax.legend()
    axes[0].invert_yaxis();fig.suptitle('Market volatility expansion: development-selected trade subsets\nCommon-date block95% intervals; not a funded strategy replay');fig.tight_layout();fig.savefig(chart/'regime-expansion-transfer.png',dpi=150);plt.close(fig)
    print('Rendered features-report.md and two diagnostic charts.')

if __name__=='__main__':main()
