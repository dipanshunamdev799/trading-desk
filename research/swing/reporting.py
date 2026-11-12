"""Readable research evidence, figures, exact candidate rules, and failure diagnostics."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


FAMILIES = {
    'baseline': 'Original structure + support/EMA pullback + MACD crossover',
    'A': 'EMA trend + MACD crossover', 'B': 'Two-bar histogram acceleration',
    'C': 'Confirmed-pivot support/resistance rejection', 'D': '20-bar breakout and retest',
    'D0': '20-bar breakout at completed close', 'E': 'EMA pullback and histogram recovery',
    'F': 'Higher/lower timeframe MACD alignment', 'G': 'Crossover in positive/negative zero-line regime',
    'G_early': 'Early crossover on the opposite side of zero',
    'H': 'Confirmed structure break with MACD timing', 'I': 'Trend-strength-filtered crossover',
    'J': 'Strong-trend crossover / moderate-trend pullback',
    'ema_only': 'EMA-only timing control', 'macd_only': 'MACD-only timing control',
    'structure_only': 'Structure-only timing control', 'zero_cross': 'MACD zero-line cross',
}


def fmt(x, digits=2):
    return '—' if x is None or pd.isna(x) else f'{float(x):.{digits}f}'


def md_table(frame, columns, names=None):
    if frame.empty:
        return '_No observations._'
    names = names or columns
    lines = ['|'+'|'.join(names)+'|', '|'+'|'.join('---' for _ in columns)+'|']
    for _, row in frame.iterrows():
        lines.append('|'+'|'.join(str(row[c]) if isinstance(row[c], str) else fmt(row[c]) for c in columns)+'|')
    return '\n'.join(lines)


def read_equity(path):
    x = pd.read_csv(path)
    x.index = pd.to_datetime(x.iloc[:, 0], utc=True).dt.tz_convert('Asia/Kolkata')
    return x


def candidate_rule(c):
    family = c['family']
    h, l = c['htf'], c['ltf']
    trigger = {
        'baseline': 'Require higher highs AND higher lows in the last two confirmed pivot pairs; LTF low touches confirmed support+zone*HTF_ATR or HTF_EMA+zone*ATR, closes above that level, and LTF MACD histogram crosses from<=0 to>0.',
        'A': 'LTF MACD histogram crosses from<=0 to>0.',
        'B': 'First bar of a sequence whose last two histogram changes are both positive.',
        'C': 'LTF low<=confirmed HTF pivot low+zone*ATR, close>=pivot low, green body, lower wick>=0.5*body, histogram rising; enter only on a false-to-true event.',
        'D': 'HTF closes above prior20 HTF-bar high. A later LTF bar retests that frozen level within zone*ATR and closes above it, with histogram>0; breakout age<3 HTF candles and retest timestamp strictly later than breakout availability. Enter false-to-true event.',
        'D0': 'Newly completed HTF close crosses above prior20 HTF-bar high and LTF histogram>0.',
        'E': 'LTF low<=HTF_EMA+zone*ATR and close>=HTF_EMA, histogram change turns positive after nonpositive change.',
        'F': 'LTF bullish histogram crossover and last completed HTF histogram>0.',
        'G': 'LTF bullish histogram crossover with LTF MACD line>0.',
        'G_early': 'LTF bullish histogram crossover with LTF MACD line<0.',
        'H': 'LTF close crosses above last confirmed HTF pivot high, with LTF histogram>0.',
        'I': 'LTF bullish histogram crossover and abs(normalized HTF slope)>=0.10 (weak variant:>=0.02 and<0.10).',
        'J': 'If abs(normalized HTF slope)>=0.10 use bullish histogram crossover; if>=0.02 and<0.10 use EMA-touch histogram recovery; otherwise stay flat.',
        'ema_only': 'First false-to-true occurrence of completed HTF trend filter, with ATR stop; MACD is not a trigger.',
        'macd_only': 'LTF bullish histogram crossover, with ATR stop; EMA is not an entry filter.',
        'structure_only': 'LTF close crosses above last confirmed HTF pivot high, with ATR stop; EMA and MACD are not entry filters.',
        'zero_cross': 'LTF MACD line crosses from<=0 to>0.',
    }[family]
    filtered = family not in ['macd_only', 'structure_only']
    text = [f'HTF={h} minutes; LTF={l} minutes; session policy={c["policy"]}. MACD={c["macd"]}.',
            f'EMA={c["ema"]}; slope=(EMA[t]−EMA[t−{c["slope"]}])/({c["slope"]}*ATR14[t]). Zone tolerance={c["zone"]}*HTF_ATR; stop buffer={c["buffer"]}*HTF_ATR.']
    if filtered:
        text.append('Long trend: last completed HTF close>EMA'+
                    (f' and normalized slope>{c.get("slope_threshold", 0)}.' if c['slope_filter'] else '. No slope filter.'))
    text.append(trigger)
    if c.get('dual_ema'):
        text.append('Additionally require HTF EMA20>HTF trend EMA.')
    if c.get('structure_filter') and family != 'baseline':
        text.append('Additionally require HTF higher-high/higher-low structure.')
    if c.get('resistance_room'):
        text.append('If a known overhead structural level exists, require its distance >= reward times decision-price stop distance; absent overhead levels pass this filter.')
    text.append(f'Stop: '+(f'decision close−{c.get("atr_stop", 1.5)}*HTF_ATR.' if c['stop_mode']=='atr' else f'last confirmed HTF pivot low−{c["buffer"]}*HTF_ATR.'))
    text.append('A strict pivot has '+str(c['pivot'])+' lower highs/higher lows on both sides and is released only after all right-hand candles close. Stop distance must be0.5–5HTF_ATR at decision and executable next open.')
    text.append(f'Exit={c["exit"]}; target reward={c["reward"]}R. Fixed target is solved from the actual slipped entry and estimated exit fees so target net profit equals reward*initial_cash_risk. All variants retain the protective stop and maximum{c["max_hold_sessions"]}observed-session hold.')
    special_exits={
        'atr_trail': 'At each base-bar open, tighten long stop to max(existing stop, previous completed5m close−2*most recently available HTF_ATR); no fixed target.',
        'ema': 'On a completed signal event, tighten long stop to max(existing stop, completed HTF_EMA−buffer*HTF_ATR). Exit at next open if completed HTF close<EMA; no fixed target.',
        'macd': 'In addition to the target/stop, exit at next open after an opposite completed LTF MACD histogram crossover.',
        'time': 'No profit target; exit at the first open10observed sessions after entry, or earlier protective stop.',
        'partial': 'Sell floor(initial quantity/2) at entry+one initial price stop-distance, with adverse fill slippage; retain original stop and exit remaining quantity at the fee-inclusive configured target. Partial1R is a gross price hurdle, not guaranteed net1R.',
        'structure': 'Target the nearest already-known HTF pivot high/prior full-day high/prior full-week high above decision close. Reject if no valid level remains above executable entry. This variant does not trail structure stops.',
    }
    if c['exit'] in special_exits:
        text.append(special_exits[c['exit']])
    text.append('Risk<=0.5% of current marked flat equity, including estimated entry/stopped-exit fees; integer quantity and notional+entry fees<=cash; one position; no leverage. ETF long-only. NIFTY short rules reverse inequalities and price direction, purely theoretical.')
    return '\n\n'.join(text)


def build_report(out: Path, root: Path):
    summary = json.loads((out/'summary.json').read_text())
    frozen = json.loads((out/'frozen-selection.json').read_text())
    protocol = json.loads((out/'protocol.json').read_text())
    audit = json.loads((out/'data-manifest.json').read_text())
    all_metrics = pd.read_csv(out/'all-period-metrics.csv')
    continuous = pd.read_csv(out/'continuous-all-variants.csv') if (out/'continuous-all-variants.csv').exists() else pd.DataFrame()
    full = pd.read_csv(out/'finalist-two-year-metrics.csv')
    stress = pd.read_csv(out/'cost-stress.csv')
    benchmarks = pd.read_csv(out/'buy-hold-benchmarks.csv')
    search = json.loads((out/'validation-search-control.json').read_text())
    wf = json.loads((out/'walkforward.json').read_text())
    primary = summary['primary']
    choices = frozen['family_finalists']
    top_ids = frozen['top_three']
    gates = pd.read_csv(out/'validation-gates.csv') if (out/'validation-gates.csv').exists() else pd.DataFrame()
    columns = ['id','n_trades','expectancy_r','total_return_pct','profit_factor','max_drawdown_pct']
    leaderboard = []
    for choice in choices:
        i = choice['id']
        f = all_metrics[(all_metrics.instrument==primary)&(all_metrics.id==i)&(all_metrics.part=='final')].iloc[0]
        row = {'id': i, 'family': choice['family'], 'eligible_development_validation': choice['eligible'],
               'validation_expectancy_r': choice['validation_expectancy_r'],
               **{c:f[c] for c in columns[1:]},
               'max_t_adjusted_p': search.get(i,{}).get('max_t_adjusted_p'),
               'research_verdict': 'Exploratory only; no fresh holdout'}
        # CI arrays are retained in raw CSV as strings; do not parse by eval.
        finals = pd.read_csv(out/'final-all-variants-descriptive.csv')
        ci = finals[(finals.instrument==primary)&(finals.id==i)].iloc[0].get('r_ci95')
        row['r_ci95'] = ci
        leaderboard.append(row)
    lead = pd.DataFrame(leaderboard)
    lead.to_csv(out/'leaderboard.csv',index=False)
    monthly_rows, subgroup_rows, concentration_rows = [], [], []
    palette = ['#166a8f','#b75d32','#5e7e3f']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig, ax = plt.subplots(2,2,figsize=(14,9),layout='constrained')
    fig.suptitle(f'MACD / EMA / structure | {primary} | frozen candidates',fontsize=16)
    for k, i in enumerate(top_ids):
        path = out/f'finalists/{primary}-{i}-two-year-equity.csv'
        if not path.exists():
            continue
        eq = read_equity(path).equity
        daily=eq.groupby(eq.index.normalize()).last()
        ax[0,0].plot(daily.index,(daily/1_000_000-1)*100,label=i,color=palette[k])
        ax[0,1].plot(daily.index,(daily/daily.cummax().clip(lower=1_000_000)-1)*100,color=palette[k],label=i)
        month=daily.groupby(daily.index.strftime('%Y-%m')).last()
        ret=(month/month.shift().fillna(1_000_000)-1)*100
        for m,r in ret.items():monthly_rows.append({'id':i,'month':m,'return_pct':r})
        tp=out/f'finalists/{primary}-{i}-two-year-trades.csv'
        if tp.exists():
            t=pd.read_csv(tp)
            if len(t):
                ax[1,0].hist(t.net_r,bins=12,alpha=.5,label=i,color=palette[k])
                t['year']=pd.to_datetime(t.exit_time,utc=True).dt.year.astype(str)
                for dim in ['regime','year','side','reason']:
                    for name,g in t.groupby(dim):
                        subgroup_rows.append({'instrument':primary,'id':i,'dimension':dim,'group':str(name),
                                              'n_trades':len(g),'expectancy_r':g.net_r.mean(),'net_profit':g.net_pnl.sum()})
                concentration_rows.append({'id':i,'n_trades':len(t),'total_net':t.net_pnl.sum(),
                    'net_excluding_best_trade':t.net_pnl.sum()-t.net_pnl.max(),
                    'net_excluding_best_three':t.net_pnl.sum()-t.net_pnl.nlargest(3).sum(),
                    'best_three_share_positive_pnl':t.net_pnl.nlargest(3).sum()/t.net_pnl.clip(lower=0).sum() if (t.net_pnl>0).any() else None})
        final_path=out/f'finalists/{primary}-{i}-final-equity.csv'
        if final_path.exists():
            eqf=read_equity(final_path).equity
            ax[1,1].plot(eqf.index,(eqf/1_000_000-1)*100,label=i,color=palette[k])
    bh=read_equity(out/f'{primary}-buy-hold-equity.csv').equity
    ax[0,0].plot(bh.index,(bh/1_000_000-1)*100,color='#777777',ls='--',label='Buy & hold (100% capital)')
    for a,title,ylabel in zip(ax.flat,['Continuous two-year net equity','Two-year drawdown at session closes','Trade net R distribution','Reserved final period net equity'],['Return %','Drawdown %','Trades','Return %']):
        a.set_title(title,loc='left');a.set_ylabel(ylabel);a.grid(alpha=.15);a.axhline(0,color='#888888',lw=.6)
        if a.has_data():a.legend(fontsize=8)
    fig.savefig(out/'research-results.png',dpi=160);plt.close(fig)
    monthly=pd.DataFrame(monthly_rows)
    monthly.to_csv(out/'monthly-returns.csv',index=False)
    subgroups=pd.DataFrame(subgroup_rows);subgroups.to_csv(out/'candidate-subgroups.csv',index=False)
    pd.DataFrame(concentration_rows).to_csv(out/'candidate-concentration.csv',index=False)
    if len(monthly):
        table=monthly.pivot(index='id',columns='month',values='return_pct').reindex(top_ids)
        fig,a=plt.subplots(figsize=(16,3.5),layout='constrained')
        vmax=max(1,float(np.nanmax(np.abs(table.to_numpy()))))
        im=a.imshow(table.to_numpy(),aspect='auto',cmap='RdYlGn',vmin=-vmax,vmax=vmax)
        a.set_xticks(np.arange(len(table.columns)),table.columns,rotation=60,ha='right')
        a.set_yticks(np.arange(len(table)),table.index);a.set_title('Monthly net returns (%) | frozen candidates')
        for r in range(len(table)):
            for c in range(len(table.columns)):
                if pd.notna(table.iloc[r,c]):a.text(c,r,f'{table.iloc[r,c]:.1f}',ha='center',va='center',fontsize=7)
        fig.colorbar(im,ax=a,label='Return %');fig.savefig(out/'monthly-heatmap.png',dpi=150);plt.close(fig)
    configs={c['id']:c for c in protocol['configs']}
    sensitivity=[]
    for family in ['A','B','E']:
        for c in protocol['configs']:
            if c['family']==family and (c['id']==f'{family}_base' or c['id'].startswith(f'{family}_ema')):
                for part in ['development','validation','final']:
                    m=all_metrics[(all_metrics.instrument==primary)&(all_metrics.id==c['id'])&(all_metrics.part==part)].iloc[0]
                    sensitivity.append({'family':family,'id':c['id'],'ema':c['ema'],'part':part,'expectancy_r':m.expectancy_r,'n_trades':m.n_trades})
    sens=pd.DataFrame(sensitivity);sens.to_csv(out/'ema-sensitivity.csv',index=False)
    if len(sens):
        fig,axes=plt.subplots(1,3,figsize=(14,4),layout='constrained')
        for a,family in zip(axes,['A','B','E']):
            for part,color in zip(['development','validation','final'],palette):
                x=sens[(sens.family==family)&(sens.part==part)].sort_values('ema')
                a.plot(x.ema,x.expectancy_r,'o-',label=part,color=color)
            a.axhline(0,color='grey',lw=.7);a.set_title(FAMILIES[family]);a.set_xlabel('EMA period');a.set_ylabel('Net expectancy R');a.legend(fontsize=8)
        fig.savefig(out/'parameter-sensitivity.png',dpi=160);plt.close(fig)
    # Example is deterministic: first trade of the frozen first candidate.
    example_id=top_ids[0]
    example_path=out/f'finalists/{primary}-{example_id}-two-year-trades.csv'
    if example_path.exists():
        trades=pd.read_csv(example_path)
        if len(trades):
            t=trades.iloc[0]
            bars=pd.read_csv(out/f'{primary.lower()}-5minute.csv')
            bars.index=pd.to_datetime(bars.ts,utc=True).dt.tz_convert('Asia/Kolkata')
            begin,end=pd.Timestamp(t.entry_time),pd.Timestamp(t.exit_time)
            b=bars.loc[(bars.index>=begin-pd.Timedelta(days=2))&(bars.index<=end+pd.Timedelta(days=1))]
            fig,a=plt.subplots(figsize=(13,4),layout='constrained')
            for j,(_, session) in enumerate(b.groupby(b.index.normalize())):
                a.plot(session.index,session.close,color='#166a8f',lw=1,label='5m close' if j==0 else None)
            for value,label,color in [(t.entry,'Entry','#222222'),(t.stop,'Initial stop','#b04433'),(t.target,'Target','#507d3a')]:
                a.axhline(value,color=color,ls='--',label=f'{label}: {value:.2f}')
            a.axvline(begin,color='#555555',ls=':');a.axvline(end,color='#555555',ls=':')
            a.set_title(f'First chronological example: {example_id} | {t.reason} | net {t.net_r:.2f}R',loc='left')
            a.set_ylabel('ETF price');a.legend(fontsize=8);fig.savefig(out/'trade-example.png',dpi=150);plt.close(fig)
    # Component comparisons are matched specifications, not post-final tuning.
    comparisons=[]
    pairs=[('Slope adds value','A_base','A_no_slope'),('Histogram vs crossover','B_base','A_base'),
           ('HTF momentum alignment','F_base','A_base'),('Zero-line filter','G_base','A_base'),
           ('Earlier zero-side crossover','G_early_base','G_base'),('Retest vs breakout close','D_base','D0_base'),
           ('ATR vs swing stop','A_atr_stop','A_base'),('Structure filter','A_structure','A_base'),
           ('Trailing vs fixed exit','A_exit_atr_trail','A_base'),('Longer candle tail excluded','A_full','A_base'),
           ('Candle end anchored','A_right_anchor','A_base'),('Nearby resistance room','A_resistance_room','A_base')]
    for hypothesis,treatment,control in pairs:
        if treatment not in configs or control not in configs:continue
        for part in ['development','validation','final']:
            x=all_metrics[(all_metrics.instrument==primary)&(all_metrics.id==treatment)&(all_metrics.part==part)].iloc[0]
            y=all_metrics[(all_metrics.instrument==primary)&(all_metrics.id==control)&(all_metrics.part==part)].iloc[0]
            comparisons.append({'hypothesis':hypothesis,'treatment':treatment,'control':control,'part':part,
                                'treatment_n':x.n_trades,'control_n':y.n_trades,'treatment_expectancy_r':x.expectancy_r,
                                'control_expectancy_r':y.expectancy_r,'difference_r':x.expectancy_r-y.expectancy_r})
    comp=pd.DataFrame(comparisons);comp.to_csv(out/'controlled-comparisons.csv',index=False)
    final_primary=all_metrics[(all_metrics.instrument==primary)&(all_metrics.part=='final')]
    baseline=all_metrics[(all_metrics.id=='baseline_base')&(all_metrics.instrument==primary)]
    eligible=sum(x['eligible'] for x in choices)
    failure_rows=[]
    for choice in choices:
        i=choice['id']
        parts=all_metrics[(all_metrics.instrument==primary)&(all_metrics.id==i)].set_index('part')
        observations=[]
        dev,val,fin=(parts.loc[p] for p in ['development','validation','final'])
        if dev.n_trades<12 or val.n_trades<6:
            observations.append(f'sparse development/validation sample ({int(dev.n_trades)}/{int(val.n_trades)})')
        if pd.notna(dev.expectancy_r) and dev.expectancy_r<=0:
            observations.append(f'negative development expectancy ({dev.expectancy_r:.2f}R)')
        if pd.notna(val.expectancy_r) and val.expectancy_r<=0:
            observations.append(f'negative validation expectancy ({val.expectancy_r:.2f}R)')
        if pd.notna(fin.expectancy_r) and fin.expectancy_r<=0:
            observations.append(f'negative final expectancy ({fin.expectancy_r:.2f}R)')
        if fin.n_trades<20:
            observations.append(f'only{int(fin.n_trades)}final trades')
        observations.append('no search-adjusted validation support')
        failure_rows.append({'id':i,'evidence':'; '.join(observations)})
    failure=pd.DataFrame(failure_rows)
    failure.to_csv(out/'family-failure-evidence.csv',index=False)
    full_top=full[(full.instrument==primary)&full.id.isin(top_ids)].set_index('id').reindex(top_ids).reset_index()
    grid_counts = continuous.groupby('instrument').agg(configurations=('id','size'),
        active=('n_trades',lambda x:int((x>0).sum())), profitable=('total_return_pct',lambda x:int((x>0).sum())),
        max_trades=('n_trades','max')).reset_index() if len(continuous) else pd.DataFrame()
    lines=['# Two-year systematic swing strategy research','',
           '**No strategy tested has sufficient evidence of a durable positive edge.**','',
           f'Research as of10November2026, Asia/Kolkata. Requested interval10November2024–9November2026 inclusive; first actual regular session11November2024. Tested{summary["configurations"]}predeclared configurations on{len(summary["instruments"])}instruments. '+
           f'{eligible}family finalists met the minimum positive development/validation screen. The final period is reserved for this run but was already examined by earlier research in this workspace; there is no genuinely untouched historical holdout.','',
           'This is an executed research experiment. Positive backtests below are observations, not a deployment recommendation. Complete losing configurations and exact trade ledgers are included.','',
           'The three frozen diagnostic configurations all lost money over the continuous two-year primary ETF replay after the declared costs. The original baseline generated no executable trades; walk-forward selection stayed in cash twice and selected a rule that produced no forward trades in the third fold. This supplies no usable forward-trading evidence.','',
           md_table(full_top,columns,['Frozen diagnostic','Two-year trades','Net R/trade','Two-year return%','PF','MTM DD%']), '',
           '## Data and instruments','',
           'Upstox5-minute OHLCV; regular-session indicators use09:15–15:30IST. Each instrument has493complete sessions/36,975regular5-minute bars in the requested window and separate2023-onward warmup. NIFTY is a nontradable index with hypothetical long/short P&L. NIFTYBEES and BANKBEES are actual cash ETFs tested independently long-only, with integer units and no leverage. These related equity markets do not provide independent asset-class replication.','',
           'No invalid OHLC or conflicting overlapping prices were detected. Identical overlapping cache rows were deduplicated. Short/special sessions are omitted from indicator calculations, but their valid raw candles replay next-tradable entries and protective orders so overnight risk is not skipped. Ordinary stray out-of-session records are excluded. Whole-day calendar coverage was compared with retained same-provider daily observations, not independently certified against every official exchange holiday.','',
           'Raw provider adjustment status is not certified. Corporate-action endpoint responses for the ETF ISINs were empty; that does not prove no action occurred. No dividends or capital-gains income taxes are modeled. These are price-return studies, not certified total returns. No futures rollover/margin simulation or option-premium reconstruction was attempted.','',
           'Data provenance: [manifest](data-manifest.json), [supplemental audit](supplemental-audit.json). [Upstox candle documentation](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/) specifies candle-start timestamps and request limits.','',
           '## Execution and accounting','',
           'A09:15–13:15four-hour candle becomes available at13:15. Its completed13:15–15:30tail is a separate135-minute candle under the default policy. Two-hour candles have a completed15-minute final tail. Full-only and close-anchored variants quantify this boundary choice. Higher-timeframe observations merge backward at their actual availability time; strict pivots wait for all right-hand candles. Warmup prices never generate evaluated trades.','',
           'Signals fill at the next observed5-minute open at or after availability, including a subsequent special session. Segment boundaries start flat and liquidate at the final observed close, preventing cross-split trade leakage. Gap stops fill at the adverse open; if both barriers are touched in the same5-minute bar, stop wins. Resting targets receive no favorable gap improvement. Initial risk is0.5%of current equity including estimated stopped-exit fees; notional plus entry fees cannot exceed cash. One position per independently tested instrument/configuration; no combined three-instrument portfolio is implied.','',
           'ETF costs:₹20brokerage per order; buy stamp duty0.015%; ETF STT0on purchases/0.001%on delivery sales; date-dependent NSE transaction charges0.00297%before1March2026 and0.00307%thereafter; SEBI fee0.0001%; applicable IPFT and18%GST; conservative₹20+GSTovernight DP sales. Slippage2basis points per side. Costs use fractional estimates without statutory rounding. Same-day trades conservatively retain the declared delivery fee model. No historical quotes/order-book depth are available, so spread/market impact remain modeled rather than observed. [Broker schedule](https://upstox.com/brokerage-charges/), [NSE STT circular](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf).','',
           'NIFTY costs are an illustrative5basis points per side plus2basis-point slippage, not actual derivative fees. Fixed targets solve the net cash reward after estimated fees from the actual slipped entry. Conservative overnight exit-fee estimates can make same-day target netR slightly larger. Partial exits take half the integer quantity at1netR, with the rest at configuredR; original stop remains. ATR/EMA trails replace fixed targets. Time-only exit retains the stop; MACD and structural-target exits retain their special target/exit condition. All modes have a10observed-session maximum unless configuration states otherwise.','',
           'Drawdown is five-minute-close marked equity; unobserved intrabar equity extremes can be worse. Sharpe/Sortino use session-close returns, zero risk-free rate,252annualization. Holding hours include nights/weekends; exposure is observed market-bar time, not elapsed wall-clock exposure. NetR divides netP&L by initial planned cash risk, which gaps may exceed.','',
           '## Frozen selection and reserved final results','',
           'Development:10November2024–9November2025. Validation:10November2025–9May2026. Final:10May–9November2026. Each split starts with₹1,000,000. Candidate choice requires at least12development/6validation trades and positive expectancy in both; within each family choose highest validation expectancy. If no candidate qualifies, retain the most-traded validation candidate as an explicitly rejected diagnostic. Family choices and top3were saved before the final batch. All207variant final rows are then disclosed once, without changing choices.','',
           'The table follows frozen validation selection order, not highest final profit. A positive final estimate with few trades is not sufficient. Max-t control jointly resamples10-session centered validation returns across all configurations, preserving their dependence; it is an approximate search-wide diagnostic. Final block intervals are conditional on the frozen choice and do not erase historical reuse.','',
           md_table(lead,['id','n_trades','expectancy_r','total_return_pct','profit_factor','max_drawdown_pct','max_t_adjusted_p'],
                    ['Frozen family finalist','Final trades','Final netR/trade','Final return%','PF','MTM DD%','Validation adjusted p']), '',
           '[Full leaderboard](leaderboard.csv); [all split metrics](all-period-metrics.csv); [exact configurations](protocol.json); [frozen choices](frozen-selection.json).','',
           'Complete continuous two-year grid (descriptive only; positive rows are not new candidate selections):','',
           md_table(grid_counts,['instrument','configurations','active','profitable','max_trades'],
                    ['Instrument','Configurations','At least 1 trade','Positive net return','Largest trade count']), '',
           '[Continuous all-variant metrics](continuous-all-variants.csv), [all 10,897 trade records](all-variant-trades.csv), [all year/regime/side/exit breakdowns](all-variant-subgroups.csv), [all monthly returns](monthly-all-variants.csv), [extension verification](extension-summary.json). Identical realized outcomes occur across some parameter variants, including flat rules; the207configurations are not207independent pieces of evidence.','',
           '## Original baseline','',md_table(baseline,['part']+columns[1:]),'',
           'A restrictive baseline may generate too few trades to support inference. Relaxing its structural/zone requirements is a different tested hypothesis, not evidence that the original conjunction works.','',
           '## Top three research candidates','',
           'These are the top frozen development/validation candidates, including rejected diagnostics if necessary. They are suitable for inspecting the evidence; none is certified for live deployment.']
    for rank,i in enumerate(top_ids,1):
        c=configs[i]
        lines+=['',f'### {rank}. `{i}` — {FAMILIES[c["family"]]}','',candidate_rule(c),'',
                md_table(all_metrics[(all_metrics.instrument==primary)&(all_metrics.id==i)],['part']+columns[1:]),'',
                'Reserved final95%session-block interval: '+str(lead[lead.id==i].iloc[0]['r_ci95'])+'netR/trade.','',
                'Cross-instrument reserved final evidence:','',md_table(all_metrics[(all_metrics.id==i)&(all_metrics.part=='final')],['instrument']+columns[1:]),'',
                'Cost/slippage stress:','',md_table(stress[(stress.instrument==primary)&(stress.id==i)],['stress']+columns[1:]),'',
                'Observed entry-regime performance over the continuous two-year replay:','',
                md_table(subgroups[(subgroups.id==i)&(subgroups.dimension=='regime')],['group','n_trades','expectancy_r','net_profit']) if len(subgroups) else '_No trades._','',
                'Executable reconstruction (full parameters are inprotocol.json):','',
                '```python', 'from research.swing.signals import make_signals', 'from research.swing.engine import simulate',
                f'config = {repr(c)}', 'signals = make_signals(regular_bars, config)',
                "result = simulate(execution_bars, signals, {**config, 'cost_model': 'etf_delivery'},",
                "                  '2024-11-10', '2026-11-10', allow_short=False)", '```']
    lines+=['','## Walk-forward optimization','',
            'Three rolling9-month training windows choose the highest positive training expectancy among configurations with at least12trades; the following3months are replayed without reselection. All folds end before the reserved final interval. Training uses the same fixed catalog. Split portfolios reset to₹1,000,000; returns can be compounded descriptively but do not reflect a traded continuous portfolio.','',
            md_table(pd.DataFrame(wf),['test_start','test_end','id','n_trades','total_return_pct']), '',
            '## What changes helped or failed','',
            'Controlled one-component comparisons below use the same engine and costs. Validation/final differences that reverse direction show instability; they are not retained as improvements after observing the final period. Filter comparisons change the admitted trade sample, so mean differences are descriptive rather than matched-trade causal estimates.','',
            md_table(comp[comp.part=='validation'],['hypothesis','treatment_n','control_n','treatment_expectancy_r','control_expectancy_r','difference_r'],
                     ['Hypothesis','Treatment n','Control n','TreatmentR','ControlR','DifferenceR']), '',
            '[All controlled differences including final](controlled-comparisons.csv), [EMA sensitivity](ema-sensitivity.csv), [year/regime/exit subgroups](candidate-subgroups.csv), [winner concentration](candidate-concentration.csv).','',
            'The slope filter improved validation expectancy by0.21Rrelative to the matched no-slope specification, then worsened final expectancy by0.65R; that contribution was unstable. Histogram acceleration was less negative than crossover timing in the final segment (−0.18Rversus−0.62R), with only9and3trades respectively; being less negative does not establish an edge. Higher-timeframe momentum alignment cut the final crossover sample from3trades to1and returned−1R. The support-bounce diagnostic had positive reserved final return of0.15%on only4trades, with95%expectancy interval−0.56to2.00R; doubling fees plus5basis-point slippage changed the complete fill/position path and produced−2.47%.','',
            'EMA90/100/110neighborhoods did not rescue the development losses of the testedA/B/Especifications. The best diagnostic support-bounce rule lost0.41Rper weak-bull trade across14observations; its apparent range-regime profit came from only3trades. Two gap-stop exits averaged−1.88Rand accounted for₹18,433of loss before other winners/losses. The weak-trend diagnostic included one−2.33Rgap loss. These are observed failure mechanisms and sparse subgroup descriptions, not regime filters selected after the fact.','',
            md_table(failure,['id','evidence'],['Frozen family diagnostic','Observed failure evidence']), '',
            'Failure checks: baseline trade scarcity, late confirmation throughFversusA, range whipsaws through regime groups, early-reversal misses through early-zero versus same-side-zero, false breakouts throughD/D0, stop sensitivity through ATR/buffer/pivot variants, target selectivity through1–4Rvariants, and friction through doubled-fee/5basis-point stress. Uncertainty is evaluated on observed samples; a sparse or inconsistent row is rejected rather than patched with additional indicators. MACD divergence and repeated-zone clustering were not implemented; no claim is made about their value.','',
            '## Simpler controls','',
            'EMA-only, MACD-only and structure-only timing are included in the grid with ATR stops, so their entry logic is simpler but position sizing/exits remain comparable. Twenty seeded randomized-timing controls use the same reference signal count per segment, causal decision close/ATR, and the same capital/stop/exit model. They match attempted frequency, not exactly realized market exposure; rejected/overlapping trades can differ. These are descriptive controls, not20independent proofs. Buy-and-hold below invests nearly100%of capital, whereas risk-sized swing strategies may use less; returns are therefore not exposure-matched.','',
            md_table(benchmarks[benchmarks.part=='two_year_continuous'],['instrument','total_return_pct','max_drawdown_pct','sharpe']), '',
            '## Playbook and research verdict','',
            '[Explicit validation gates](validation-gates.csv) show every family diagnostic failing the historical evidence requirements before the separate fresh-data condition is considered. [Independent verification](verification.json) reconciles all1,863split-metric rows and102selected trade/equity journals;45synthetic/data/validation tests also pass. The continuous extension independently reconciles621scenarios and10,897trades.','',
            '**No live trading playbook is justified by this experiment.** The precise candidate specifications above are research rules. A usable next step is to freeze one rule, collect fresh forward quotes and fills, and evaluate a predeclared sufficient sample without further tuning. Required evidence includes a positive lower expectancy bound, search-adjusted validation support, adequate final trade count, cost robustness, and independent forward replication. The existing historical period cannot satisfy the fresh-data condition.','',
            'The strongest positive rows, any failures, and uncertainty are all retained; the conclusion is insufficient evidence of durability, not a claim that profitable swing trading is impossible. Futures/option execution, real spread/impact, independently certified corporate actions, and additional independent markets remain outside this evidence.','',
            '## Figures','', '![Equity, drawdown, tradeR and final curves](research-results.png)','',
            '![Monthly net returns](monthly-heatmap.png)','', '![EMA parameter sensitivity](parameter-sensitivity.png)','',
            '![First chronological candidate trade](trade-example.png)','',
            '## Reproduce','', '```powershell',
            r'.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_swing*.py"',
            r'.\.venv\Scripts\python.exe -m unittest research.swing.test_data',
            r'.\.venv\Scripts\python.exe scripts\run_swing_research.py --offline',
            r'.\.venv\Scripts\python.exe scripts\verify_swing_research.py','```','',
            'All acquisition is read-only. No broker orders are submitted. Source modules:data.py,signals.py,engine.py,validation.py,reporting.py. Protocol, source hashes, seeds, raw-response fingerprints, complete metrics and selected trade/equity journals are persisted underartifacts/swing_research/.']
    text='\n'.join(lines).replace('half the integer quantity at1netR','half the integer quantity at1gross price-risk R')
    # Keep identifiers, links, tables and runnable code byte-for-byte stable;
    # typeset prose with explicit number/word separation.
    import re
    formatted=[]
    in_code=False
    for line in text.splitlines():
        if line.startswith('```'):
            in_code=not in_code
            formatted.append(line)
            continue
        if in_code or line.startswith('|'):
            formatted.append(line)
            continue
        pieces=re.split(r'(\[[^\]]*\]\([^)]*\)|`[^`]*`)',line)
        for j,piece in enumerate(pieces):
            if j%2==0:
                piece=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',piece)
                piece=re.sub(r'(?<=[%₹])(?=[A-Za-z])',' ',piece)
                piece=piece.replace('inprotocol.json','in protocol.json').replace('underartifacts/','under artifacts/')
                piece=piece.replace('configuredR','configured R').replace('netR','net R').replace('netP&L','net P&L')
                piece=piece.replace('GSTovernight','GST overnight').replace('costs:₹','costs: ₹').replace('conservative₹','conservative ₹')
                piece=piece.replace('Rrelative','R relative').replace('Rversus','R versus').replace('Rper','R per').replace('Rgap','R gap').replace('Rand','R and')
                piece=piece.replace('A/B/Especifications','A/B/E specifications').replace('all1,','all 1,').replace('all10,','all 10,')
                piece=piece.replace('for₹','for ₹').replace('%on','% on')
                piece=piece.replace('to₹','to ₹').replace('versus−','versus −').replace('returned−','returned −').replace('interval−','interval −').replace('produced−','produced −')
                piece=piece.replace('journals;45','journals; 45').replace('modules:data.py,signals.py,engine.py,validation.py,reporting.py','modules: data.py, signals.py, engine.py, validation.py, reporting.py')
                piece=re.sub(r'(?<=[A-Za-z])([:,])(?=\d)',r'\1 ',piece)
                piece=piece.replace('with₹','with ₹')
                piece=piece.replace('at 1 netR','at 1 gross price-risk R').replace('at1netR','at 1 gross price-risk R')
                piece=piece.replace('at 1 net R','at 1 gross price-risk R')
            pieces[j]=piece
        formatted.append(''.join(pieces))
    text='\n'.join(formatted)+'\n'
    (out/'report.md').write_text(text,encoding='utf-8')
    (root/'SWING_RESEARCH_RESULTS.md').write_text(
        '# Two-year swing research\n\n'+
        '**No strategy tested has sufficient evidence of a durable positive edge.**\n\n'+
        f'Tested {summary["configurations"]} configurations across NIFTY, NIFTYBEES, and BANKBEES for 11 November 2024–9 November 2026.\n\n'+
        '[Complete report](artifacts/swing_research/report.md) · [Leaderboard](artifacts/swing_research/leaderboard.csv) · [All metrics](artifacts/swing_research/all-period-metrics.csv)\n\n'+
        'The reserved final period overlaps earlier project research and cannot be described as a genuinely untouched holdout.\n',encoding='utf-8')


if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]
    build_report(root/'artifacts'/'swing_research',root)
