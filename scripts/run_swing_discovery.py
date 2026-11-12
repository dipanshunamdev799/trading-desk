"""Execute the frozen broad strategy discovery, selection and falsification study."""
from __future__ import annotations
import sys,json,hashlib,sqlite3,time,math
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.swing_discovery.engine import simulate_many,execution_signature
from research.swing_discovery.diagnostics import summarize_run,development_score,pbo_cscv,deflated_sharpe
from research.swing.validation import search_max_t,trade_uncertainty
OUT=ROOT/'artifacts'/'swing_discovery'
PARTS={'development':('2024-11-10','2025-11-10'),'validation':('2025-11-10','2026-05-10'),'final':('2026-05-10','2026-11-10')}

def clean(v):
 if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [clean(x) for x in v]
 if isinstance(v,(np.floating,float)):return float(v) if np.isfinite(v) else None
 if isinstance(v,(np.integer,)):return int(v)
 if isinstance(v,(np.bool_,)):return bool(v)
 if isinstance(v,(pd.Timestamp,Path)):return str(v)
 return v
def save(name,value):
 path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(clean(value),indent=2,allow_nan=False),encoding='utf-8')
def digest(value):return hashlib.sha256(json.dumps(clean(value),sort_keys=True).encode()).hexdigest()
def normalize(c):
 # Nested parameters remain in the record; execution reads flattened values.
 c={**c,**c.get('params',{})};c.setdefault('initial_capital',1_000_000);c.setdefault('risk_fraction',.005)
 c.setdefault('min_turnover',50_000_000);c.setdefault('participation',.01)
 c.setdefault('exit','fixed');c.setdefault('stop_mode','atr');c.setdefault('stop_atr',2.);c.setdefault('buffer',.2)
 c.setdefault('reward',2.);c.setdefault('max_hold_sessions',10)
 return c

class Ledger:
 def __init__(self):
  self.conn=sqlite3.connect(OUT/'research.sqlite3');self.conn.execute('PRAGMA journal_mode=WAL')
  self.conn.execute('CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY,family TEXT,phase TEXT,configuration TEXT,description TEXT)')
  self.conn.execute('CREATE TABLE IF NOT EXISTS runs(key TEXT PRIMARY KEY,id TEXT,stage TEXT,pool TEXT,start TEXT,end TEXT,cost REAL,slippage REAL,summary TEXT,score REAL)')
  self.conn.execute('CREATE TABLE IF NOT EXISTS portfolio_days(key TEXT,day TEXT,equity REAL,net_return REAL,PRIMARY KEY(key,day))')
  self.conn.commit()
 def config(self,c,phase):
  existing=self.conn.execute('SELECT configuration FROM experiments WHERE id=?',(c['id'],)).fetchone()
  value=json.dumps(clean(c),sort_keys=True)
  if existing and existing[0]!=value:raise ValueError('Configuration changed for existingID '+c['id'])
  self.conn.execute('INSERT OR IGNORE INTO experiments VALUES(?,?,?,?,?)',(c['id'],c['family'],phase,value,c.get('description','')))
 def key(self,c,stage,pool,start,end,cost,slip):return digest([c,stage,pool,start,end,cost,slip])
 def exists(self,key):return bool(self.conn.execute('SELECT1 FROM runs WHERE key=?'.replace('SELECT1','SELECT 1'),(key,)).fetchone())
 def store(self,key,c,stage,pool,start,end,cost,slip,result,stock_rows=True):
  summary=summarize_run(result);score=development_score(summary,min_trades=50 if stage=='validation' else 100)
  self.conn.execute('INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?)',(key,c['id'],stage,pool,start,end,cost,slip,json.dumps(clean(summary)),score))
  frame=result['stock_metrics'].copy();frame.insert(0,'key',key)
  if stock_rows:frame.to_sql('stock_metrics',self.conn,if_exists='append',index=False,chunksize=200)
  self.conn.executemany('INSERT INTO portfolio_days VALUES(?,?,?,?)',[(key,str(d.date()),float(e),float(r)) for d,e,r in zip(result['dates'],result['equity'],result['returns'])])
  self.conn.commit();return summary
 def results(self,stage,pool):
  rows=[]
  for key,i,summary,score in self.conn.execute('SELECT key,id,summary,score FROM runs WHERE stage=? AND pool=?',(stage,pool)):
   rows.append({'key':key,'id':i,'score':score,**json.loads(summary)})
  return pd.DataFrame(rows)
 def returns(self,stage,pool):
  return pd.read_sql_query('SELECT r.id,d.day,d.net_return FROM runs r JOIN portfolio_days d ON r.key=d.key WHERE r.stage=? AND r.pool=?',self.conn,params=[stage,pool]).pivot(index='day',columns='id',values='net_return').fillna(0)

def run_group(ledger,panel,features,configs,stage,pool,stocks,start,end,cost=1.,slip=5.,keep=False,stock_rows=True):
 from research.swing_discovery.signals import generate
 groups=defaultdict(list)
 for c in configs:
  key=ledger.key(c,stage,pool,start,end,cost,slip)
  if not ledger.exists(key):groups[execution_signature(c)].append(c)
 total=sum(map(len,groups.values()));done=0;t0=time.monotonic()
 for group in groups.values():
  for offset in range(0,len(group),8):
   batch=group[offset:offset+8];signals=[generate(panel,c,features) for c in batch]
   out=simulate_many(panel,signals,batch,start,end,stocks=stocks,cost_multiplier=cost,slippage_bps=slip,keep_trades=keep)
   for c in batch:
    result=out[c['id']];key=ledger.key(c,stage,pool,start,end,cost,slip)
    ledger.store(key,c,stage,pool,start,end,cost,slip,result,stock_rows=stock_rows)
    if keep:
     path=OUT/'finalist_journals';path.mkdir(exist_ok=True)
     result['trades'].to_csv(path/f'{c["id"]}-{pool}-{stage}-trades.csv',index=False)
     pd.DataFrame({'equity':result['equity'],'return':result['returns']}).to_csv(path/f'{c["id"]}-{pool}-{stage}-equity.csv')
   done+=len(batch)
   if done%40<len(batch) or done==total:print(stage,pool,f'{done}/{total}',f'{time.monotonic()-t0:.1f}s',flush=True)
 return ledger.results(stage,pool)

def main():
 from research.swing_discovery.data import prepare_data
 from research.swing_discovery.signals import build_features,catalog,neighbors,catalog_manifest
 OUT.mkdir(parents=True,exist_ok=True)
 panel=prepare_data(OUT)
 if 'niftyclose' in panel:panel['nifty']=panel['niftyclose']
 if 'liquidity_turnover' in panel:panel['liquidity_value']=panel['liquidity_turnover']
 if 'liquidity_volume' in panel:panel['median_volume20']=panel['liquidity_volume']
 assert 'liquidity_value' in panel and 'median_volume20' in panel,'Lagged liquidity constraints absent'
 eligible=np.asarray(panel.get('eligible',np.ones(len(panel['symbols']),bool)),bool)
 previous=json.loads((ROOT/'artifacts/stock_swing_research/universe.json').read_text())['stocks'];old={x['isin_at_start'] for x in previous}
 membership=json.loads((OUT/'universe.json').read_text())['stocks'];identity={x['symbol']:x['isin_at_start'] for x in membership}
 holdout=np.asarray([identity[s] not in old and int(hashlib.sha256(identity[s].encode()).hexdigest()[:8],16)%5==0 for s in panel['symbols']])&eligible
 training=eligible&~holdout;development=np.flatnonzero(training);reserved=np.flatnonzero(holdout);allstocks=np.flatnonzero(eligible)
 if len(development)<50 or len(reserved)<10:raise ValueError('Expanded universe/novel-stock holdout too small')
 from research.swing_discovery.benchmarks import write_benchmarks
 write_benchmarks(panel,OUT,development,reserved,allstocks)
 configs=[normalize(c) for c in catalog()];assert len({c['id'] for c in configs})==len(configs)
 protocol={'created_date':'2026-11-11','parts':PARTS,'configurations':configs,'catalog_manifest':catalog_manifest(),'universe':panel['symbols'],
  'development_stocks':[panel['symbols'][k] for k in development],'reserved_stocks':[panel['symbols'][k] for k in reserved],
  'selection':'Development-only fine neighborhoods for up to3positive, broad family rules. Validate full coarse+refined grid. Freeze one eligible highestbalancedscore rule per family (or rejected diagnostic if none) before reserved evaluation. Final top20 ranked descriptively by final/novel-company evidence; no new parameter choices after final.',
  'broad_candidate':'At least100development trades, positive development expectancy and sleeve return,>=50%positive-stock breadth; catastrophic worst-sleeve drawdown>25%veto. Validation requirespositive netexpectancy,positive sleeve return and>=50trades to become promising.',
  'neighbors':'Generate only from qualifying development parents, no validation/final-driven ranges.',
  'execution':'Daily next-tradable-open, completed daily/weekly indicators, stop-first dailyambiguity, actual-unit reconstruction/split/dividend entitlements,0.5%cashrisk, integer unlevered shares; independent₹1mstock sleeves.5bps baseline adverse fills,1%lag20median volume participation,minimum₹5croreprior20median traded-valueproxy. No certified historical spread/depth/volume adjustment.',
  'stress':'Final reruns with doublefees10bps/side and triplefees20bps/side; newexecutionsizing/targets, notsimpleP&L subtraction.',
  'inference':'Common-calendar10session max-t validation control, final blockbootstrap, development-only CSCV/PBO and IID-limited DSR diagnostic. All efforts triallogged. Genuine temporalunseen data unavailable becauseearliermarketperiodresearch overlaps. Reservedcompanies provide cross-sectional novelty only.',
  'walkforward':'All frozen coarse rules only: rolling9monthtrain/3monthtest folds ending2026-05-10. Main development fine-grid cannot enter earlier folds because it would leak later training outcomes.',
  'no_deployment':True,'seed':20261111,'data_audit':str(OUT/'data-audit.json')}
 if (OUT/'protocol.json').exists():
  prior=json.loads((OUT/'protocol.json').read_text())
  if prior!=clean(protocol):raise ValueError('Existing frozen protocol differs; use a new artifact directory')
 else:save('protocol.json',protocol)
 ledger=Ledger()
 for c in configs:ledger.config(c,'coarse')
 ledger.conn.commit();features=build_features(panel)
 t0=time.monotonic()
 dev=run_group(ledger,panel,features,configs,'development','development_stocks',development,*PARTS['development'])
 dev=dev[dev.id.isin([c['id'] for c in configs])].copy()
 byid={c['id']:c for c in configs};dev['family']=dev.id.map(lambda i:byid[i]['family'])
 good=dev[(dev.n_trades>=100)&(dev.expectancy_r>0)&(dev.total_return_pct>0)&(dev.positive_stock_pct>=50)&(dev.worst_stock_drawdown_pct<=25)]
 parents=good.sort_values('score',ascending=False).groupby('family',sort=False).head(3).id.tolist()
 ignore_identity=['id','description','parent','phase','parent_id','selection_scope','neighbor_axis','variant']
 refined=[];parent_map={};known={digest({k:v for k,v in c.items() if k not in ignore_identity}) for c in configs}
 for i in parents:
  for child in neighbors(byid[i]):
   child=normalize(child);h=digest({k:v for k,v in child.items() if k not in ignore_identity})
   if h in known:continue
   known.add(h);child['id']='fine_'+h[:16];parent_map.setdefault(i,[]).append(child['id']);refined.append(child)
 for c in refined:ledger.config(c,'development_refinement')
 ledger.conn.commit();save('development-refinement.json',{'parents':parents,'parent_map':parent_map,'configurations':refined,'used_validation':False,'used_final':False})
 if refined:dev=run_group(ledger,panel,features,refined,'development','development_stocks',development,*PARTS['development'])
 allconfigs=configs+refined;byid={c['id']:c for c in allconfigs}
 val=run_group(ledger,panel,features,allconfigs,'validation','development_stocks',development,*PARTS['validation'])
 dev=ledger.results('development','development_stocks').set_index('id');v=val.set_index('id')
 frozen=[]
 for family in sorted({c['family'] for c in allconfigs}):
  ids=[c['id'] for c in allconfigs if c['family']==family]
  candidates=[i for i in ids if dev.loc[i,'n_trades']>=100 and dev.loc[i,'expectancy_r'] is not None and dev.loc[i,'expectancy_r']>0
    and dev.loc[i,'total_return_pct']>0 and dev.loc[i,'positive_stock_pct']>=50 and dev.loc[i,'worst_stock_drawdown_pct']<=25
    and v.loc[i,'n_trades']>=50 and pd.notna(v.loc[i,'expectancy_r']) and v.loc[i,'expectancy_r']>0 and v.loc[i,'total_return_pct']>0]
  pool=candidates or ids
  choice=max(pool,key=lambda i:(.65*v.loc[i,'score']+.35*dev.loc[i,'score'],v.loc[i,'n_trades']))
  frozen.append({'id':choice,'family':family,'development_validation_eligible':bool(candidates),'config':byid[choice],
     'selection_score':.65*v.loc[choice,'score']+.35*dev.loc[choice,'score']})
 frozen.sort(key=lambda x:(x['development_validation_eligible'],x['selection_score']),reverse=True)
 save('frozen-finalists.json',{'finalists':frozen,'frozen_before_reserved_evaluation':True,'count':len(frozen),'preselected_finer_resolution_ids':[x['id'] for x in frozen[:5]]})
 # Search diagnostics use development/validation only.
 dr=ledger.returns('development','development_stocks');vr=ledger.returns('validation','development_stocks')
 save('pbo-development.json',pbo_cscv(dr[[c['id'] for c in configs]],blocks=6));save('validation-search-control.json',search_max_t({i:vr[i] for i in vr},draws=3000))
 trial_sr=np.divide(dr.mean().to_numpy(),dr.std(ddof=1).to_numpy(),out=np.zeros(dr.shape[1]),where=dr.std(ddof=1).to_numpy()>1e-14)
 save('dsr-development.json',{x['id']:deflated_sharpe(dr[x['id']],trial_sr,len(allconfigs)) for x in frozen})
 finalists=[x['config'] for x in frozen]
 for pool,stocks in [('development_stocks',development),('reserved_stocks',reserved),('all_eligible_stocks',allstocks)]:
  run_group(ledger,panel,features,finalists,'final',pool,stocks,*PARTS['final'],keep=True)
 for label,cost,slip in [('final_double10',2.,10.),('final_severe20',3.,20.)]:
  run_group(ledger,panel,features,finalists,label,'all_eligible_stocks',allstocks,*PARTS['final'],cost=cost,slip=slip)
 run_group(ledger,panel,features,finalists,'two_year','all_eligible_stocks',allstocks,'2024-11-10','2026-11-10',keep=True)
 folds=[('2024-11-10','2025-08-10','2025-11-10'),('2025-02-10','2025-11-10','2026-02-10'),('2025-05-10','2026-02-10','2026-05-10')]
 walk=[]
 for start,test,end in folds:
  stage='walktrain_'+test
  train=run_group(ledger,panel,features,configs,stage,'development_stocks',development,start,test,stock_rows=False)
  pool=train[(train.n_trades>=100)&(train.total_return_pct>0)&(train.expectancy_r>0)&(train.worst_stock_drawdown_pct<=25)]
  if len(pool):
   i=pool.sort_values('score',ascending=False).iloc[0].id;c=byid[i]
   r=run_group(ledger,panel,features,[c],'walktest_'+test,'all_eligible_stocks',allstocks,test,end,keep=True)
   walk.append({'train_start':start,'test_start':test,'test_end':end,'id':i,**r.iloc[0].to_dict()})
  else:walk.append({'train_start':start,'test_start':test,'test_end':end,'id':'cash_no_eligible_rule','total_return_pct':0,'n_trades':0})
 save('walk-forward.json',walk)
 allresults=[]
 for key,i,stage,pool,start,end,cost,slip,summary,score in ledger.conn.execute('SELECT * FROM runs'):
  allresults.append({'key':key,'id':i,'family':byid[i]['family'],'stage':stage,'pool':pool,'start':start,'end':end,'cost_multiplier':cost,'slippage_bps':slip,'score':score,**json.loads(summary)})
 pd.DataFrame(allresults).to_csv(OUT/'all-experiments.csv',index=False)
 save('run-summary.json',{'registered_stocks':len(panel['symbols']),'eligible_stocks':len(allstocks),'development_stocks':len(development),'reserved_new_stocks':len(reserved),
  'coarse_configurations':len(configs),'refined_configurations':len(refined),'families':len(frozen),'finalists':len(finalists),'execution_runs':len(allresults),'elapsed_seconds':time.monotonic()-t0,
  'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'research/swing_discovery').glob('*.py')}})
 from research.swing_discovery.reporting import build_report
 build_report(OUT,ROOT)
 print('DISCOVERY_COMPLETE',flush=True)

if __name__=='__main__':main()
