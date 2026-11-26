"""Standardize forecast case tables and index immutable law and provenance locations."""
from collections import defaultdict
import csv as text_csv
import re

from .common import *

DIRECT_NAMES = re.compile(r'prediction|forecast|(?:^|-)cases|scores|endpoint-(?:origins|attribution|components)|range-origins|risk-origins|law-index|path-marginals')
COUNTERFACTUAL = re.compile(r'null|permut|placebo|shuffl|randomiz|synthetic|invariance')
SKIP = {'sources','raw','normalized','forward','downloads','cache','inputs','models','node_modules'}
LAW_FILES = {
    16: {'v15-replayed-gap-forecasts.csv.gz':'v15-replayed-gap-laws.npz'},
    17: {'original-clock-forecasts.csv.gz':'original-clock-laws.npz','opening-forecasts.csv.gz':'opening-laws.npz'},
    18: {'original-event-forecasts.csv.gz':'original-event-laws.npz','event-volatility-predictions.csv.gz':'event-volatility-laws.npz'},
    19: {'endpoint-cases.csv.gz':'endpoint-laws.npz','native-mechanism-cases.csv.gz':'native-mechanism-laws.npz',
         'native-residual-cases.csv.gz':'native-residual-laws.npz','postopen-cases.csv.gz':'postopen-endpoint-laws.npz',
         'postopen-risk-cases.csv.gz':'postopen-risk-laws.npz','risk-cases.csv.gz':'volatility-laws.npz'},
    20: {'native-mechanism-cases.csv.gz':'native-mechanism-laws.npz','architecture-cases.csv.gz':'architecture-laws.npz',
         'lifetime-parent-cases.csv.gz':'lifetime-parent-laws.npz','strong-parent-component-cases.csv.gz':'strong-parent-component-laws.npz'},
    21: {'index-forecast-cases.csv.gz':'index-forecast-laws.npz','protected-return-cases.csv.gz':'protected-return-laws.npz'},
    22: {'india-forecast-cases.csv.gz':'india-forecast-laws.npz','protected-india-return-cases.csv.gz':'protected-india-return-laws.npz'},
}
ORIGIN=('origin','origin_date','reference_date','decision_day','day','forecast_day','asof')
ISSUE=('decision','issue_ts','issued_at','decision_timestamp','as_of_timestamp','issue_ist','decision_local')
END=('target_end','endpoint','target_date','target_day','label_end_day','end','target','settlement_date','maturity_day','verified_calendar_target')
MOD=('model','model_id','method','strategy','expert','variant','name','configuration')
DATE='^202[56]-[0-9]{2}-[0-9]{2}$'
SIGN=('p','p_up','probability_up','up_probability','dist_up_probability','p_expand','probability','prediction')
REAL=('realized_return','actual_endpoint','actual','realized','outcome','actual_vol','ret','realized_path_volatility')
SCORE=('brier','endpoint_crps','crps','log_loss','mae','vol_mae','range_crps','drawdown_crps','tail_brier','qlike','variance_qlike',
       'width80','coverage80','correct','pinball','interval_score','expansion_brier','touch_brier','integrated_brier','squared_error')


def wildcard_value(frame,columns,default=''):
    k=next((c for c in columns if c in frame),None)
    return frame[k] if k is not None else pd.Series(default,index=frame.index)


def days(frame,candidates):
    base=pd.Series('',index=frame.index,dtype='str')
    for k in candidates:
        if k in frame:
            t=frame[k].astype('string').str.slice(0,10).fillna('')
            base=base.mask(base.eq('')&t.str.match(DATE,na=False),t)
    return base


def model_family(name):
    s=name.casefold()
    tests=[
       ('negative_control',r'null|permut|shuffl|randomized|random_aux|random_prior|placebo'),
       ('market_implied_risk',r'iv_|^iv|implied|option|skew|egarch|gjr|volatility|risk'),
       ('fundamental_event',r'corpor|reaction|filing|earnings|fundament|event'),
       ('positioning_flows',r'positio|smooth5|embargo|participant|fii|flows|crowd|delivery'),
       ('historical_path',r'analog|historic|random_walk|path|tail|block_resampl'),
       ('offshore_transmission',r'gift|offshore|foreign|world|international|transfer|loco|loro'),
       ('market_breadth',r'breadth|rotation|sector|stock|equity|constituent|basket'),
       ('combination',r'blend|mixture|ensemble|aggregate|pool|shared|multitask'),
       ('reference_baseline',r'parent|neutral|asymmetry|^v14|archived|exact|control'),
       ('domestic_price',r'trend|momentum|technical|price|slope|window|regime|revers|location'),
    ]
    return next((label for label,rule in tests if re.search(rule,s)),'unclassified')


def iterate_sources():
    earlier=ROOT/'artifacts/nifty_forecast'
    for p in sorted(earlier.glob('*/*/*')):
        if p.is_file() and (p.name=='forecast.json' or p.name.startswith(('expert-predictions','historical-predictions'))):
            yield (2 if any('horizons' in k or 'two-year' in k for k in p.parts) else 1),p
    for v in range(3,23):
        root=root_for(v)
        for p in sorted(root.rglob('*')):
            rel=p.relative_to(root)
            if set(rel.parts[:-1])&SKIP or not p.is_file():
                continue
            if p.name.endswith(('.csv','.csv.gz')) and DIRECT_NAMES.search(p.name) and not re.search(r'leaderboard|fingerprint|coefficients|correlation|hour-share|ranking',p.name):
                yield v,p
            elif p.name.endswith(('.npz','-laws.jsonl')) and re.search('law|path|atoms|distribution-archive',p.as_posix(),re.I):
                yield v,p


def source_file(path,v):
    options={}
    root=root_for(v)
    law=LAW_FILES.get(v,{}).get(path.name)
    if law and (root/law).is_file() and path.parent==root:
        options=dict(file=root/law,style='indexed_weighted_or_equal_atoms')
    if v==11 and path.name.endswith('-predictions.csv') and path.parent==root:
        label=path.name.removesuffix('-predictions.csv')
        kk=root/f'distribution-archive/{label}.npz'
        js=root/f'{label}-laws.jsonl'
        if kk.is_file():
            options=dict(file=kk,style='keys horizon/model/origin/endpoint')
        elif js.is_file():
            options=dict(file=js,style='JSON lines with keys')
    if v==14 and path.name in ('endpoint-components.csv','endpoint-attribution.csv'):
        options=dict(file=root/'standalone-endpoint-laws.npz',style='keys horizon/origin/model/endpoint')
    if v==13 and path.name=='distribution-predictions.csv':
        options=dict(file=root/'joint-path-target-atoms-{h}.npz',style='keys origin/model plus archived target name; pointer only for covered model IDs')
    if v==22 and path.name.startswith('market-forecast-cases-'):
        h=path.name.removeprefix('market-forecast-cases-').split('.')[0]
        options=dict(file=root/f'market-forecast-atoms-{h}.npz',style='normalized indexed law plus exported scale and center')
    return options


def map_rows(chunk,file,v,offset):
    start=days(chunk,ORIGIN)
    end=days(chunk,END)
    d=days(chunk,('day','forecast_day','decision_day','issue_date','decision','asof'))
    ok=start.between(FIRST,FREEZE)&end.between(FIRST,FREEZE)&start.le(end)
    invalid_order=int((start.ne('')&end.ne('')&start.gt(end)).sum())
    end=end[ok];d=d[ok];start=start[ok]
    a=chunk.loc[ok]
    frame=pd.DataFrame(index=a.index)
    frame['archive_version']=v
    frame['source_row']=np.asarray(a.index)+offset
    frame['source_file']=file.relative_to(ROOT).as_posix()
    frame['model']=wildcard_value(a,MOD,file.name)
    frame['origin']=start
    frame['decision_session']=d
    time=wildcard_value(a,ISSUE).astype('string')
    clock=wildcard_value(a,('cutoff','clock','checkpoint','information_cutoff','stage'), 'unknown clock')
    frame['information_cutoff']=clock
    frame['decision_timestamp']=time.where(time.str.contains('T| [0-9][0-9]:',regex=True,na=False))
    frame['timestamp_provenance']=np.where(frame.decision_timestamp.notna(),'explicit in source','unresolved')
    if 'issue_ns' in a:
        q=pd.to_numeric(a.issue_ns,errors='coerce')
        n=pd.to_datetime(q.where(q>0),unit='ns',utc=True)
        derive=frame.decision_timestamp.isna()&n.notna()
        frame.loc[derive,'decision_timestamp']=n[derive].astype(str)
        frame.loc[derive,'timestamp_provenance']='explicit UTC nanosecond source'
    for label,hh,idx in [('previous_1700','17:00',start),('preauction_0855','08:55',d),('native_0910','09:10',d)]:
        eligible=clock.eq(label)&idx.ne('')&frame.decision_timestamp.isna()
        frame.loc[eligible,'decision_timestamp']=idx[eligible]+'T'+hh+':00+05:30'
        frame.loc[eligible,'timestamp_provenance']='declared IST clock plus source calendar date'
    frame['reference_close']=wildcard_value(a,('reference_close','anchor_close','reference','price_anchor'))
    frame['target_session']=end
    frame['horizon']=wildcard_value(a,('horizon','h','sessions','target_horizon'))
    frame['target_type']=wildcard_value(a,('target_name','objective','track','task','target_family','measure'),file.stem)
    frame['instrument']=wildcard_value(a,('ticker','symbol','instrument','code','asset'))
    frame['cohort']=wildcard_value(a,('cohort','split','phase','evaluation_split'))
    frame['feature_families']=wildcard_value(a,('feature_families','features','field_family','block','feature_group','source_groups','candidate_block'))
    frame['training_start']=wildcard_value(a,('train_start','first_train','first_training_origin','train_first'))
    frame['training_end']=wildcard_value(a,('train_end','training_end','train_last','last_fit','fit_cutoff'))
    frame['training_last_mature']=wildcard_value(a,('last_mature','last_mature_ns','last_train_ns','last_training_end','max_label_end','last_label'))
    frame['training_rows']=wildcard_value(a,('train_n','n_train','n_training','fit_n','n_residual_train'))
    frame['parent']=wildcard_value(a,('parent','anchor','base','base_model'))
    frame['configuration_hash']=wildcard_value(a,('configuration_sha256','configuration_hash','model_hash','config_hash'))
    frame['training_eligibility']=np.where(frame.training_last_mature.astype('string').fillna('').ne(''),'source supplies last outcome marker','no per-origin maturity marker')
    frame['classification']='chronological or archived historical prediction'
    if v<=2:
        frame['classification']='pre-V3 provenance only; complete warm-up scope not established'
        frame['training_eligibility']='excluded from V23 analysis'
    elif COUNTERFACTUAL.search(file.name):
        frame['classification']='negative control, synthetic, or refit artifact'
    frame['selection']='retrospectively studied specification; prospective use not inferred'
    frame['law_id']=wildcard_value(a,('law','law_id','atoms_id','scenario_id','distribution_id'))
    spec=source_file(file,v)
    frame['law_path']=spec['file'].relative_to(ROOT).as_posix() if spec else ''
    frame['law_encoding']=spec.get('style','unresolved or summary only')
    ready=frame.law_id.astype('string').fillna('').ne('')
    if spec and spec['style'].startswith(('keys','JSON')):
        ready=np.ones(len(frame),bool)
    if v==13 and spec:
        ready=np.zeros(len(frame),bool)
        for h,g in frame.groupby('horizon'):
            key=root_for(v)/f'joint-path-target-atoms-{h}.npz'
            if not key.is_file():
                continue
            with np.load(key,allow_pickle=False) as npy:
                idx={(a,b):j for j,(a,b) in enumerate(npy['keys'])}
            ids=[idx.get((a,b),-1) for a,b in zip(g.origin,g.model,strict=True)]
            include=np.asarray(ids)>=0
            frame.loc[g.index,'law_id']=[str(k) if k>=0 else '' for k in ids]
            frame.loc[g.index,'law_path']=key.relative_to(ROOT).as_posix()
            ready[frame.index.get_indexer(g.index)]=include
    frame['law_status']=np.where(ready&bool(spec),'archived law pointer','summary or unresolved law')
    frame['probability']=wildcard_value(a,SIGN[:-1])
    frame['probability_field']=next((k for k in SIGN[:-1] if k in a),'')
    frame['mean']=wildcard_value(a,('predicted_mean','arithmetic_mean','endpoint_mean','mean','forecast_mean','point','pred_vol','prediction'))
    frame['median']=wildcard_value(a,('predicted_median','endpoint_median','median','forecast_median','median_forecast'))
    var=pd.to_numeric(wildcard_value(a,('variance','predictive_variance','endpoint_variance','var')),errors='coerce')
    sigma=pd.to_numeric(wildcard_value(a,('endpoint_std','forecast_std','predictive_sd')),errors='coerce')
    frame['variance']=var.fillna(sigma**2)
    for pct in ('01','05','10','25','50','75','90','95','99'):
        frame[f'q{pct}']=wildcard_value(a,(f'q{pct}',f'q{int(pct)}',f'endpoint_q{pct}'))
    frame['realized']=wildcard_value(a,REAL)
    frame['realized_field']=next((k for k in REAL if k in a),'')
    for score in SCORE:
        frame[score]=wildcard_value(a,(score,))
    if spec and spec['style']=='normalized indexed law plus exported scale and center':
        for k in ('center_normalized','horizon_scale'):
            frame[k]=a[k] if k in a else np.nan
    return frame,invalid_order


def archive_ledger():
    past=read('forward-ledger.json',V22)
    rows=[]
    for bucket in ('original_issues','inherited_v19','inherited_v20'):
        for r in past[bucket]:
            name=r.get('model',r.get('name',r.get('key')))
            file=r.get('source_artifact',r.get('law',r.get('file')))
            if file is None:
                file='prospective-ledger.jsonl' if r['version']=='V4' else 'experimental-forecasts.json'
            label='late diagnostic' if 'LATE' in name else 'genuine frozen prospective'
            rows.append(dict(version=r['version'],model=name,classification=label,status=r.get('maturity',r.get('status')),
                             issued_at=r.get('issued',r.get('issued_at')),horizon=r.get('horizon'),reference_close=r['reference_close'],
                             target_first=r['target_sessions'][0],target_last=r['target_sessions'][-1],target_sessions=' '.join(r['target_sessions']),
                             probability=r.get('p_up'),realized=r.get('realized_return'),law_path=(root_for(int(r['version'][1:]))/file).relative_to(ROOT).as_posix(),
                             issue_hash=r.get('issue_hash',r.get('law_sha256',r.get('sha256')))))
    write('master-prospective-inventory.csv',pd.DataFrame(rows))


def run():
    registry=[];sources=[];groups=defaultdict(lambda: {'records':0,'law_pointers':0,'files':set(),'clocks':set()})
    partitions={}
    digests={}
    c0=csv('original-target-panel.csv',root_for(17))
    calendars={h:c0.drop_duplicates('origin').set_index('origin')[f'end_original{h}'] for h in HORIZONS}
    try:
        for v,p in iterate_sources():
            rel=p.relative_to(ROOT).as_posix()
            exists=p.stat().st_size
            digest=sha(p)
            ref=dict(version=v,file=rel,bytes=exists,sha256=digest,duplicate_of=digests.get(digest,''))
            if p.name.endswith(('.npz','-laws.jsonl','.json')):
                sources.append(ref|dict(disposition='law or publication archive' if v>=3 else 'pre-V3 issue archive; scope not portable',rows=0,archived_rows=0))
                continue
            if digest in digests:
                sources.append(ref|dict(disposition='identical source file indexed as alias',rows=0,archived_rows=0))
                continue
            digests[digest]=rel
            opener=gzip.open if p.suffix=='.gz' else open
            with opener(p,'rt',encoding='utf-8-sig') as h:
                fields=next(text_csv.reader(h),[])
            recover=(v==13 and p.name in ('distribution-predictions.csv','volatility-predictions.csv','barrier-predictions.csv.gz')) or (
                     v==14 and p.name in ('endpoint-components.csv','endpoint-attribution.csv','process-risk-predictions.csv'))
            same_day=v==17 and p.name=='opening-forecasts.csv.gz'
            if not (set(fields)&set(ORIGIN) and (recover or same_day or set(fields)&set(END)) and set(fields)&set(SIGN+SCORE+REAL)):
                sources.append(ref|dict(disposition='aggregate, diagnostics or insufficient case keys',rows=0,archived_rows=0,
                                        recoverable_fields=' '.join(fields)))
                continue
            if v<=2:
                sources.append(ref|dict(disposition='pre-V3 source index only; possible pre-2025 fitted state',rows=0,archived_rows=0,
                                        recoverable_fields=' '.join(fields)))
                continue
            if v not in partitions:
                path=OUT/f'master-forecast-archive/v{v:02d}.csv.gz'
                path.parent.mkdir(exist_ok=True)
                partitions[v]=(gzip.open(path,'wt',encoding='utf-8',compresslevel=3,newline=''),True)
            rec=use=n_law=invalid=0
            for t in pd.read_csv(p,low_memory=False,chunksize=25000):
                if same_day:
                    t['verified_calendar_target']=t.day
                    t['horizon']=1
                    t['target_name']='opening gap'
                if recover and 'horizon' in t and 'origin' in t:
                    origin=t.origin.astype(str).str[:10]
                    t['verified_calendar_target']=''
                    for h,cal in calendars.items():
                        take=t.horizon.eq(h)
                        t.loc[take,'verified_calendar_target']=origin[take].map(cal)
                n,err=map_rows(t.reset_index(drop=True),p,v,rec)
                rec+=len(t);use+=len(n);invalid+=err
                n_law+=n.law_status.eq('archived law pointer').sum()
                for model,q in n.groupby('model',dropna=False):
                    r=groups[(v,str(model))]
                    r['records']+=len(q);r['law_pointers']+=int(q.law_status.eq('archived law pointer').sum())
                    r['files'].add(rel);r['clocks'].update(q.information_cutoff.dropna().astype(str).unique())
                n=n.reindex(columns=list(dict.fromkeys([*n.columns,'center_normalized','horizon_scale'])))
                # Normalize the ordering even when a source stores no local transform.
                keys0=[c for c in n.columns if c not in ('center_normalized','horizon_scale')]+['center_normalized','horizon_scale']
                if len(n):
                    stream,first=partitions[v]
                    n[keys0].to_csv(stream,index=False,header=first)
                    partitions[v]=(stream,False)
            sources.append(ref|dict(disposition='case rows retained within V23 date boundary',rows=rec,archived_rows=use,linked_laws=n_law,
                                    invalid_order=invalid, recoverable_fields=' '.join(fields)))
    finally:
        for file,_ in partitions.values():
            file.close()
    for (v,model),r in sorted(groups.items()):
        registry.append(dict(version=v,model=model,descriptive_family=model_family(model),case_rows=r['records'],law_pointers=r['law_pointers'],
                             source_files=len(r['files']),cutoffs=' | '.join(sorted(r['clocks'])),
                             registry_id=hashlib.sha256(f'{v}:{model}'.encode()).hexdigest(),
                             registry_scope='archive descriptor; read source and config hash where originally available'))
    a=pd.DataFrame(sources)
    b=pd.DataFrame(registry)
    write('master-forecast-source-catalog.csv',a)
    write('master-model-family-registry.csv',b)
    archive_ledger()
    summary=a.groupby('version',as_index=False).agg(inventoried_files=('file','size'),case_rows=('archived_rows','sum'),
         archived_law_links=('linked_laws','sum'),out_of_order=('invalid_order','sum'))
    print(summary.to_string(index=False),flush=True)
    write('master-archive-coverage.csv',summary)
    save('master-archive-schema.json',dict(
        archive='Version-partitioned gzip CSV. Source file SHA-256 and zero-based source case row are original provenance keys.',
        files=[f'master-forecast-archive/v{k:02d}.csv.gz' for k in partitions],
        historical_records=int(a.archived_rows.sum()), discovered_distinct_version_model_ids=len(b), linked_law_pointers=int(b.law_pointers.sum()),
        law_note='Some laws are keyed, equal-weight or on log-return units; use companion layout and file receipt. Incomplete summaries cannot produce an exact law.',
        completeness='The archive covers identified date-keyed forecast tables and a separate law inventory. Unmatched table conventions and V1–V2 possible pre-2025 warm-ups are retained as provenance only.',
        identity='Source case rows include overlapping experiments and predecessor duplicates. These are coverage counts, not independent predictions or distinct hypotheses.'))


if __name__=='__main__':
    run()
