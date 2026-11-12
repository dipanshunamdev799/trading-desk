"""Stock rankings, transfer validation, and pre-trade characteristic diagnostics."""
from __future__ import annotations
import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .validation import trade_uncertainty,search_max_t

def md(df,cols,names=None):
 if df.empty:return '_No qualifying observations._'
 out=['|'+'|'.join(names or cols)+'|','|'+'|'.join(['---']*len(cols))+'|']
 for _,r in df.iterrows():
  vals=[]
  for c in cols:
   v=r[c]
   if isinstance(v,str):vals.append(v)
   elif pd.isna(v):vals.append('—')
   elif c in ['n_trades','stocks','stocks_selected','positive_variants','tested_variants','best_n_trades']:vals.append(str(int(v)))
   else:vals.append(f'{v:.2f}')
  out.append('|'+'|'.join(vals)+'|')
 return '\n'.join(out)
def build_report(out,root):
 protocol=json.loads((out/'protocol.json').read_text());summary=json.loads((out/'run-summary.json').read_text())
 audit=json.loads((out/'stock-data-audit.json').read_text())
 m=pd.read_csv(out/'metrics.csv');t=pd.read_csv(out/'trades-with-characteristics.csv');daily=pd.read_csv(out/'daily-returns.csv');bh=pd.read_csv(out/'buy-hold.csv')
 ids=[c['id'] for c in protocol['configs']]
 main=m[m.id.isin(ids)].copy();primary=main[main.part=='two_year'].copy()
 divs=t[t.part=='two_year'].groupby(['symbol','id']).dividends.sum()
 primary['dividend_entitlements']=[divs.get((s,i),0.) for s,i in zip(primary.symbol,primary.id)]
 primary['price_component_net_return_pct']=(primary.net_profit-primary.dividend_entitlements)/1_000_000*100
 # Fit and save selections from development rows only. Historical full-period
 # ranking is explicitly separate and cannot change this selector.
 choices={};selection_rows=[]
 for i in ids:
  d=main[(main.id==i)&(main.part=='development')]
  pool=d[(d.n_trades>=8)&(d.expectancy_r>0)].sort_values(['expectancy_r','n_trades'],ascending=False)
  choices[i]=pool.head(5).symbol.tolist()
 (out/'frozen-stock-selections.json').write_text(json.dumps({'selector':protocol['selection'],'selected_from_development_only':choices},indent=2))
 variant_rows=[]
 for i in ids:
  g=primary[primary.id==i];v=main[(main.id==i)&(main.part=='validation')];f=main[(main.id==i)&(main.part=='final')];s=main[(main.id==i)&(main.part=='final_severe')]
  tr=t[(t.id==i)&(t.part=='two_year')]
  variant_rows.append({'id':i,'stocks':len(g),'positive_stocks':int(g.total_return_pct.gt(0).sum()),'positive_stock_pct':float(g.total_return_pct.gt(0).mean()*100),
   'n_trades':int(g.n_trades.sum()),'pooled_expectancy_r':float(tr.net_r.mean()) if len(tr) else np.nan,
   'mean_two_year_return_pct':g.total_return_pct.mean(),'median_two_year_return_pct':g.total_return_pct.median(),
   'mean_validation_return_pct':v.total_return_pct.mean(),'mean_final_return_pct':f.total_return_pct.mean(),'mean_final_severe_return_pct':s.total_return_pct.mean()})
  selected=choices[i]
  for part in ['validation','final','final_severe']:
   r=main[(main.id==i)&(main.symbol.isin(selected))&(main.part==part)]
   selection_rows.append({'id':i,'part':part,'stocks_selected':len(selected),'n_trades':int(r.n_trades.sum()),
     'mean_return_pct':float(r.total_return_pct.mean()) if len(r) else 0.,'selected_stocks':','.join(selected)})
 variants=pd.DataFrame(variant_rows).sort_values('mean_two_year_return_pct',ascending=False)
 variants.to_csv(out/'variant-summary.csv',index=False)
 pd.DataFrame(selection_rows).to_csv(out/'development-selected-stock-results.csv',index=False)
 # Multiple-comparison diagnostic includes controls and all eligible pairs, with
 # a shared 10-session bootstrap calendar preserving market-wide co-movement.
 vr=daily[daily.part=='validation'].copy();vr['pair']=vr.symbol+'|'+vr.id
 panel=vr.pivot(index='day',columns='pair',values='return').fillna(0)
 adjusted=search_max_t({c:panel[c] for c in panel},draws=2000)
 (out/'validation-search-control.json').write_text(json.dumps(adjusted,indent=2))
 primary['validation_adjusted_p']=[adjusted[f'{s}|{i}']['max_t_adjusted_p'] for s,i in zip(primary.symbol,primary.id)]
 for part in ['development','validation','final','final_severe']:
  mm=main[main.part==part][['symbol','id','n_trades','total_return_pct','expectancy_r']].rename(columns={c:f'{part}_{c}' for c in ['n_trades','total_return_pct','expectancy_r']})
  primary=primary.merge(mm,on=['symbol','id'],validate='one_to_one')
 primary['development_screen_pass']=(primary.development_n_trades>=8)&(primary.development_expectancy_r>0)
 primary['validation_screen_pass']=(primary.validation_n_trades>=5)&(primary.validation_expectancy_r>0)
 days=pd.to_datetime(sorted(daily[daily.part=='final'].day.unique()))
 cis={}
 # Every stock/rule final sample gets uncertainty; no extra final-based tuning.
 final=t[t.part=='final']
 for (symbol,i),g in final.groupby(['symbol','id']):
  cis[(symbol,i)]=trade_uncertainty(g,days,draws=1500)['r_ci95']
 primary['final_ci_low']=[cis.get((s,i),[None,None])[0] for s,i in zip(primary.symbol,primary.id)]
 primary['final_ci_high']=[cis.get((s,i),[None,None])[1] for s,i in zip(primary.symbol,primary.id)]
 primary['historical_evidence_gate']=(primary.development_screen_pass & primary.validation_screen_pass & (primary.final_n_trades>=10) &
   (primary.final_ci_low>0)&(primary.validation_adjusted_p<=.05)&(primary.final_severe_total_return_pct>0))
 primary['deployment_supported']=False
 leaderboard=primary.sort_values('total_return_pct',ascending=False)
 leaderboard.to_csv(out/'pair-leaderboard.csv',index=False)
 stock_rows=[]
 for s,g in primary.groupby('symbol'):
  best=g.sort_values('total_return_pct',ascending=False).iloc[0];bench=bh[(bh.symbol==s)&(bh.part=='two_year')].iloc[0]
  stock_rows.append({'symbol':s,'sector':best.sector,'best_variant_post_hoc':best.id,'best_return_pct':best.total_return_pct,
   'best_n_trades':int(best.n_trades),'median_variant_return_pct':g.total_return_pct.median(),
   'positive_variants':int(g.total_return_pct.gt(0).sum()),'tested_variants':len(g),
   'buy_hold_return_pct':bench.total_return_pct,'historical_gate_passes':int(g.historical_evidence_gate.sum())})
 stocks=pd.DataFrame(stock_rows).sort_values('median_variant_return_pct',ascending=False);stocks.to_csv(out/'stock-summary.csv',index=False)
 rank_correlation=float(stocks.median_variant_return_pct.rank().corr(stocks.buy_hold_return_pct.rank()))
 # Characteristic cutoffs use unique DEVELOPMENT stock/signal observations;
 # same-day macro exposure/duplicated variants are not independent replications.
 featurecols=['volatility_60','efficiency_60','momentum_126','beta_60','gap_60','liquidity_60']
 tt=t[t.id.isin(ids)&t.part.isin(['development','validation','final'])].copy()
 dev=tt[tt.part=='development'].drop_duplicates(['symbol','signal_time'])
 thresholds={c:dev[c].dropna().quantile([1/3,2/3]).tolist() for c in featurecols}
 (out/'characteristic-thresholds.json').write_text(json.dumps({'fit_period':'development only','thresholds':thresholds,'liquidity_caveat':'Provider-adjusted price times volume proxy; historical volume adjustment not independently certified. This feature is exploratory and cannot support a liquidity-based live selection rule.'},indent=2))
 type_rows=[]
 for feature in featurecols+['sector']:
  if feature=='sector':tt['bucket']=tt.sector
  else:
   lo,hi=thresholds[feature];tt['bucket']=np.where(tt[feature].isna(),'missing',np.where(tt[feature]<=lo,'low',np.where(tt[feature]<=hi,'mid','high')))
  for (part,bucket),g in tt.groupby(['part','bucket']):
   ci=trade_uncertainty(g,pd.to_datetime(sorted(daily[daily.part==part].day.unique())),draws=1500)['r_ci95']
   type_rows.append({'feature':feature,'bucket':bucket,'part':part,'stocks':g.symbol.nunique(),'n_trades':len(g),
    'expectancy_r':g.net_r.mean(),'net_profit':g.net_pnl.sum(),'ci_low':ci[0],'ci_high':ci[1]})
 types=pd.DataFrame(type_rows);types.to_csv(out/'stock-type-results.csv',index=False)
 hypotheses=types[(types.part=='development')&(types.stocks>=10)&(types.n_trades>=30)&(types.expectancy_r>0)&(types.feature!='liquidity_60')].sort_values('expectancy_r',ascending=False).head(2)
 (out/'frozen-stock-type-hypotheses.json').write_text(hypotheses.to_json(orient='records',indent=2))
 # Simple controls are reported explicitly rather than hidden in the pair search.
 control=m[m.control].groupby(['id','part']).agg(stocks=('symbol','size'),n_trades=('n_trades','sum'),mean_return_pct=('total_return_pct','mean')).reset_index()
 control.to_csv(out/'simple-controls.csv',index=False)
 (out/'registered-pair-dispositions.csv').write_text('')
 dispositions=[]
 excluded={a['symbol']:a for a in audit if a['ranking_excluded']}
 for spec in protocol['universe']:
  for i in ids:dispositions.append({'symbol':spec['symbol'],'id':i,'status':'quarantined_corporate_or_data_issue' if spec['symbol'] in excluded else 'tested','reasons':json.dumps(excluded.get(spec['symbol'],{}).get('exclusion_reasons',[]))})
 pd.DataFrame(dispositions).to_csv(out/'registered-pair-dispositions.csv',index=False)
 # Verify economic trade accounting and causality for every continuous journal.
 verify=[]
 for (symbol,i),g in t[t.part=='two_year'].groupby(['symbol','id']):
  g=g.sort_values('entry_time');entry=pd.to_datetime(g.entry_time,utc=True);exit=pd.to_datetime(g.exit_time,utc=True);signal=pd.to_datetime(g.signal_time,utc=True)
  assert (entry>=signal).all() and (exit>entry).all()
  assert (entry.iloc[1:].reset_index(drop=True)>=exit.iloc[:-1].reset_index(drop=True)).all()
  assert np.allclose(g.net_pnl,g.gross_pnl-g.fees,atol=1e-6)
  assert np.allclose(g.net_r,g.net_pnl/g.initial_cash_risk,atol=1e-8)
  prior=1_000_000+g.net_pnl.cumsum().shift(fill_value=0)
  assert (g.initial_cash_risk<=prior*.005+1e-5).all()
  assert (g.entry_fill*g.entry_quantity<=prior+1e-5).all()
  expected=m[(m.symbol==symbol)&(m.id==i)&(m.part=='two_year')].iloc[0]
  assert abs(g.net_pnl.sum()-expected.net_profit)<1e-5
  eq=pd.read_csv(out/f'journals/{symbol}-{i}-daily-equity.csv')
  assert abs(eq.equity.iloc[-1]-1_000_000-g.net_pnl.sum())<1e-5
  verify.append({'symbol':symbol,'id':i,'trades':len(g),'split_adjustments':int(g.share_adjustments.sum()),'dividends':g.dividends.sum()})
 verification={'passed':True,'stock_variant_journals_checked':len(verify),'continuous_trade_records_checked':int(sum(x['trades'] for x in verify)),
  'share_adjustments_in_held_trades':int(sum(x['split_adjustments'] for x in verify)),
  'dividend_entitlements':float(sum(x['dividends'] for x in verify)),
  'checks':['next-open information timestamp ordering','nonoverlap','capital and0.5%fee-inclusive risk','trade PnL/netR/equity reconciliation','stock split and dividend attribution'],
  'limits':'No independent certification of every historical price/volume, cash payment date, fill liquidity, or truly untouched final period.'}
 (out/'verification.json').write_text(json.dumps(verification,indent=2))
 # Charts: every eligible stock is shown, including losers and zero-trade rules.
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
 matrix=primary.pivot(index='symbol',columns='id',values='total_return_pct').reindex(columns=ids).sort_index()
 fig,ax=plt.subplots(figsize=(13,14),layout='constrained');vmax=max(5,float(np.nanquantile(np.abs(matrix.to_numpy()),.95)))
 im=ax.imshow(matrix.to_numpy(),aspect='auto',cmap='RdYlGn',vmin=-vmax,vmax=vmax)
 ax.set_xticks(range(len(ids)),ids,rotation=60,ha='right');ax.set_yticks(range(len(matrix)),matrix.index)
 ax.set_title('Stocks × fixed variants | continuous two-year net return (%)',loc='left',fontsize=14)
 fig.colorbar(im,ax=ax,label='Net return %, colours capped at95th absolute percentile');fig.savefig(out/'stock-variant-heatmap.png',dpi=150);plt.close(fig)
 fig,axes=plt.subplots(2,3,figsize=(15,8),layout='constrained')
 for ax,feature in zip(axes.flat,featurecols):
  for k,part in enumerate(['development','validation','final']):
   g=types[(types.feature==feature)&(types.part==part)].set_index('bucket').reindex(['low','mid','high'])
   ax.bar(np.arange(3)+(k-1)*.24,g.expectancy_r,width=.24,label=part)
  ax.set_xticks(range(3),['low','mid','high']);ax.axhline(0,color='grey',lw=.7);ax.set_title(feature);ax.set_ylabel('Pooled trade netR');ax.legend(fontsize=7)
 fig.suptitle('Stock characteristics measured before entries | correlated descriptive samples',fontsize=14)
 fig.savefig(out/'stock-characteristics.png',dpi=150);plt.close(fig)
 # Report uses full-period winners as discovery only, distinct from the frozen
 # development-selected stock transfer test and reserved-period checks.
 top=leaderboard.head(15)
 lines=['# Individual-stock swing strategy transfer test','',
  f'Tested **{summary["variants"]} fixed variants** on **{summary["tested_stocks"]} comparable stocks** from a registered starting universe of50stocks. Window:11November2024–9November2026; January2023onward warmup. Two timing controls are additional. No parameter was optimized per stock.','',
  '## What the results mean','',
  f'**No stock/variant pair passed the joint evidence screen.** {int(primary.total_return_pct.gt(0).sum())}of{len(primary)}pairs had positive two-year net returns, yet all13variants had negative mean returns across the45eligible stocks. Historical fit was stock-specific rather than a broadly transferable edge.','',
  'Eicher Motors had positive net returns on all13variants; Hindalco and Hero MotoCorp on12each, and M&M on11. These are discovery observations from the same period. Hindalco’s leading histogram variant weakened from+5.56%over the full period to+0.34%in the reserved final segment and−0.32%under severe final costs. Maruti’s leading histogram variant returned+5.04%overall but−0.91%in the final segment. The high profit factor for Eicher’s4Ralignment rule comes from only8trades and does not supply a dependable win-rate estimate.','',
  'The two characteristic hypotheses chosen in development did not transfer: medium directional efficiency went from+0.12Rper trade in development to−0.22Rin final; high volatility went from+0.11Rto−0.14R. No volatility, momentum, beta or gap bucket had positive final expectancy. Autos and metals/materials had small positive final pooled estimates (+0.064Rand+0.068R), with intervals spanning zero; telecom’s positive estimate comes from Bharti Airtel alone. This does not justify selecting a sector or stock type for investment.','',
  f'Across stocks, the rank correlation between median strategy return and buy-and-hold return was{rank_correlation:.2f}. That is evidence of some association with the stock’s overall path, not evidence of incremental alpha. Buy-and-hold exposure differs substantially from swing exposure.','',
  'Full-period winners below identify historical strategy fit. They are selected after seeing this period and are not investment recommendations. The stronger test is whether stocks chosen using development data and stock characteristics known before entry continued to work in later periods. This remains a swing-trading study; business valuation, earnings durability and suitability for long-term investment were not tested.','',
  '## Highest historical stock/variant returns','',md(top,['symbol','id','n_trades','total_return_pct','max_drawdown_pct','profit_factor','final_total_return_pct'],['Stock','Fixed variant','Two-year trades','Two-year net%','MTM DD%','PF','Reserved final net%']),'',
  '[All stock/variant rankings](pair-leaderboard.csv), [stock summaries](stock-summary.csv), [registered universe dispositions](registered-pair-dispositions.csv).','',
  '## Which variants transferred broadly','',
  'Every stock sleeve starts with₹10lakh, risks at most0.5%includingfees, and holds at mostonecash long position. Cross-stock means below are averages across separately funded sleeves. They do not simulate using one₹10lakh account to fund all stocks simultaneously. Positive stock breadth matters: one spectacular stock is weaker evidence than consistent results across many stocks.','',
  md(variants,['id','stocks','positive_stock_pct','n_trades','mean_two_year_return_pct','median_two_year_return_pct','mean_final_return_pct','mean_final_severe_return_pct'],['Variant','Stocks','Positive stocks%','Total trades','Mean two-year%','Median two-year%','Mean final%','Mean severe final%']),'',
  '## Stocks with broader historical fit','',
  'Ranked by median return across all13fixed variants, avoiding selection solely by each stock’s best historical rule. The best-rule column is explicitly post-hoc. Buy-and-hold invests nearly100%of capital, so its return is not exposure-matched to the risk-sized swing rules. Both include modeled cash dividend entitlement.','',
  md(stocks.head(15),['symbol','sector','median_variant_return_pct','positive_variants','best_variant_post_hoc','best_return_pct','buy_hold_return_pct'],['Stock','Sector','Median variant%','Positive variants/13','Best historical variant','Best net%','Buy & hold%']),'',
  '## Development-selected stock transfer','',
  'For each fixed rule, select up to5stocks with at least8development trades and positive development netR; rank by development expectancy only. The selector was specified before stock results were calculated. The same selected stocks are evaluated in validation and final; empty selection remains cash. No replacement by later winners is allowed. These samples are small, and this13-variant transfer study inherits selection from prior ETF research on overlapping dates.','',
  md(pd.DataFrame(selection_rows),['id','part','stocks_selected','n_trades','mean_return_pct','selected_stocks']),'',
  '## What kinds of stocks fit','',
  'Daily features are volatility over60sessions, directional efficiency over60sessions,126-session price momentum,60-session beta against NIFTY, average absolute overnight gap over60sessions, and a provider price×volume turnover proxy. Values enter trade records only after the daily candle is complete. Low/mid/high cutoffs are development-only terciles from unique stock/signal events. Sector is a fixed broad business classification, not a historical market-cap label. This large-cap universe cannot establish whether small-cap stocks work better.','',
  'The liquidity proxy is exploratory because historical volume adjustment was not independently certified. Split-neutral prices preserve scale-invariant trading signals, but cross-stock liquidity comparisons require verified contemporary volume and traded value. No live liquidity filter is inferred. Sector and feature-bin summaries pool correlated rule trades and repeat some market events; block intervals resample common10-session exit calendars and are conditional descriptive intervals, not independent confirmations.','',
  'Two development-chosen characteristic hypotheses (minimum30trades and10stocks; liquidity excluded):','',
  md(hypotheses,['feature','bucket','stocks','n_trades','expectancy_r']), '',
  'Reserved final stock-type evidence (all bins are disclosed, rather than selecting only favorable ones):','',
  md(types[types.part=='final'],['feature','bucket','stocks','n_trades','expectancy_r','ci_low','ci_high']), '',
  '[All type/sector results](stock-type-results.csv), [frozen cutoffs](characteristic-thresholds.json), [causal trade features](trades-with-characteristics.csv).','',
  '## Evidence gates and controls','',
  f'{int(primary.historical_evidence_gate.sum())}of{len(primary)}tested stock/variant pairs passed the joint historical screen: development>=8trades and positive netR, validation>=5and positive netR, final>=10and positive95%lower block bound, validation search-wide max-t adjustedp<=0.05, and positive severe final return. Deployment is not certified even when a historical row passes: a genuinely new forward period and executable quote/impact validation remain necessary.','',
  'Approximate one-sided max-t jointly resamples10-session validation calendars across stock/variant combinations and timing controls; it tests net daily returns versus cash, not excess return over buy-and-hold. The characteristic bucket search is additional exploratory analysis and is not fully corrected by the stock/variant max-t. Earlier use of the underlying market period prevents calling this an independent untouched holdout.','',
  md(control[control.part=='two_year'],['id','stocks','n_trades','mean_return_pct']), '',
  '## Data, costs and corporate-action treatment','',
  'Universe: the NIFTY50constituents at the first research session,11November2024; later index exits remain in the registered universe. The dated fund constituent document provides start ISINs; today’s Upstox master resolves instrument-key changes and company renames only. Data are5-minute Upstox candles, complete75-bar regular sessions for indicators, with short special-session raw candles restored for next-tradable-open execution and protective orders. Invalid warmup sessions are removed and audited; missing ordinary sessions within the evaluated period quarantine the stock.','',
  'Historical NSE corporate-action data were retrieved for2023–9November2026. Provider price continuity around each known split/bonus determines whether pre-event prices are already adjusted. Actual historical share-unit prices are reconstructed, while homogeneous split-neutral series drive indicators; stop/ATR values are converted back to the available share basis. A held position’s integer quantity and protective levels change on the ex-date. This avoids artificial split losses. Cash dividend economic entitlement is included for positions carried into the ex-date; payment-date availability and investor income tax/withholding are not modeled. The original ETF/index engine is unchanged; a separately tested stock engine implements entitlements.','',
  'Price-basis reconstruction is inferred from known exchange action ratios and observed provider continuity; every historical price has not been independently reconciled to an exchange bhavcopy. Dividend treatment assumes candle OHLC has not been adjusted for cash distributions. The pair leaderboard separately includes dividend entitlement and the net price component with that entitlement removed from the same realized trade ledger. That attribution is not a full rerun with different dividend-related capital sizing. Historical volume adjustment, dividend payment timing and independent raw-price certification remain material data limits.','',
  'Unresolved demergers, rights issues and fractional bonus entitlements are quarantined from comparable whole-period ranking rather than assigned fabricated proceeds. Large unexplained gaps are also flagged for review. The exclusion ledger is retained; conclusions apply to the eligible subset, not automatically all50starting members or the entire stock market.','',
  '\n'.join('- '+a['symbol']+': '+json.dumps(a.get('exclusion_reasons',a.get('reason',[])),default=str)+'; missing research dates='+str(a.get('ordinary_research_sessions_missing',[])) for a in audit if a['ranking_excluded']), '',
  'Equity delivery fees include₹20brokerage per order,0.1%STTon both buy and sell,0.015%buy stamp duty, date-aware exchange/IPFT/SEBI fees,18%GSTand applicable overnight DP fees. Baseline slippage2bps per side; severe stress doubles fees and uses5bps per side. Same-day exits conservatively use the declared delivery fee model. No observed historical bid/ask depth, volume participation cap or certified market-impact curve is available. Next-open entries, adverse gap stops, stop-first ambiguous candles and fee-inclusive cash-risk sizing follow the prior engine. No shorts, derivatives, leverage or averaging down.','',
  'Sources: [dated constituent list](nifty50-2024-11-11.pdf), [NSE historical corporate actions](https://www.nseindia.com/companies-listing/corporate-filings-actions), [September2024Nifty reconstitution](https://www.niftyindices.com/Press_Release/ind_prs23082024.pdf), [Upstox candles](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/), [broker cost schedule](https://upstox.com/brokerage-charges/). Raw source responses, hashes, constituent mappings, action records and every stock audit are retained.','',
  '## Figures','', '![Every eligible stock and fixed variant](stock-variant-heatmap.png)','', '![Causal stock characteristics](stock-characteristics.png)','',
  '## Reproduce','', '```powershell',r'.\.venv\Scripts\python.exe scripts\fetch_stock_swing.py',r'.\.venv\Scripts\python.exe scripts\run_stock_swing.py',r'.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_stock_swing.py"','```','',
  '[Protocol](protocol.json), [data audit](stock-data-audit.json), [verification](verification.json), [simple controls](simple-controls.csv).']
 text='\n'.join(lines)
 # Typeset prose only; keep exact variant names, code, links, and numeric tables.
 import re
 formatted=[];code=False
 for line in text.splitlines():
  if line.startswith('```'):code=not code;formatted.append(line);continue
  if code or line.startswith('|') or line.startswith('- '):formatted.append(line);continue
  pieces=re.split(r'(\[[^\]]*\]\([^)]*\)|`[^`]*`)',line)
  for j in range(0,len(pieces),2):
   pieces[j]=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',pieces[j])
   pieces[j]=re.sub(r'(?<=[A-Za-z])(?=[+−]\d)|(?<=%)(?=[A-Za-z])',' ',pieces[j])
   pieces[j]=re.sub(r'\bR(?=[a-z])','R ',pieces[j])
   pieces[j]=re.sub(r'(?<=[A-Za-z]):(?=\d)',': ',pieces[j])
   pieces[j]=pieces[j].replace('includingfees','including fees').replace('at mostone','at most one')
   for a,b in [('netR','net R'),('STTon','STT on'),('GSTand','GST and'),('%of','% of'),('%including','% including'),('onecash','one cash'),('with₹','with ₹'),('one₹','one ₹'),('include₹','include ₹'),('starts with₹','starts with ₹'),('adjustedp','adjusted p')]:pieces[j]=pieces[j].replace(a,b)
  formatted.append(''.join(pieces))
 (out/'report.md').write_text('\n'.join(formatted)+'\n',encoding='utf-8')
 sources=[root/'research/swing/stocks.py',root/'research/swing/stock_engine.py',Path(__file__),root/'scripts/run_stock_swing.py',root/'scripts/fetch_stock_swing.py']
 environment={'python':__import__('sys').version,'pandas':pd.__version__,'numpy':np.__version__,
  'source_sha256_at_delivery':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
  'source_input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'protocol.json',out/'universe.json',out/'nse-actions-all.json',out/'nifty50-2024-11-11.pdf']},
  'baseline_engine_unchanged_sha256':hashlib.sha256((root/'research/swing/engine.py').read_bytes()).hexdigest(),
  'library_note':'pypdf is needed only for first-run extraction of the dated constituent document; runtime trading uses pandas/numpy/matplotlib.'}
 (out/'environment.json').write_text(json.dumps(environment,indent=2))
 (root/'STOCK_SWING_RESEARCH_RESULTS.md').write_text('# Stock swing research\n\n'+f'{summary["variants"]} fixed variants transferred to {summary["tested_stocks"]} eligible starting-period NIFTY50 stocks.\n\n'+
  '[Complete report](artifacts/stock_swing_research/report.md) · [Pair rankings](artifacts/stock_swing_research/pair-leaderboard.csv) · [Stock summaries](artifacts/stock_swing_research/stock-summary.csv)\n\nHistorical rankings are exploratory and do not establish a live investment recommendation.\n',encoding='utf-8')
 print(json.dumps({'tested_stocks':summary['tested_stocks'],'pairs':len(primary),'historical_gate_passes':int(primary.historical_evidence_gate.sum()),'top_pairs':top[['symbol','id','total_return_pct','n_trades']].to_dict('records')}),flush=True)

if __name__=='__main__':
 root=Path(__file__).resolve().parents[2];build_report(root/'artifacts/stock_swing_research',root)
