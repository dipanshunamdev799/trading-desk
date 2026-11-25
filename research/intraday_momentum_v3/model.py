"""Fixed nine ridge fits (3families × P/PV/PVD), future data only; no tuning."""
import gzip,json,hashlib
import numpy as np
import pandas as pd
from .common import OUT,dump,sha
from .features import timestamp

GROUPS={'P':['return5_bps','return60_bps','return300_bps','daily_return'],
        'PV':['return5_bps','return60_bps','return300_bps','daily_return','volume60','volume_acceleration'],
        'PVD':['return5_bps','return60_bps','return300_bps','daily_return','volume60','volume_acceleration',
               'imbalance1','imbalance5','imbalance_mean10','imbalance_std10','spread_bps','bid_depth5','ask_depth5']}


def oriented(features,side):
    result=dict(features)
    for key in ('return5_bps','return60_bps','return300_bps','daily_return','imbalance1','imbalance5','imbalance_mean10'):
        if result.get(key) is not None:result[key]*=side
    if side==-1:result['bid_depth5'],result['ask_depth5']=features.get('ask_depth5'),features.get('bid_depth5')
    return result


def panel():
    frozen=json.loads((OUT/'protocol-frozen.json').read_text());start=timestamp(frozen['frozen_at']);events={};labels={};controls=[]
    for path in sorted((OUT/'runs').glob('*/derived-events.jsonl.gz')):
        manifest=json.loads((path.parent/'manifest.json').read_text())
        if manifest.get('protocol_sha256')!=sha(OUT/'protocol-frozen.json'):continue
        with gzip.open(path,'rt',encoding='utf-8') as f:
            for line in f:
                r=json.loads(line)
                if r['kind']=='candidate':events[r['episode_id']]=r
                elif r['kind']=='matched_control':controls.append(r)
                elif r['kind']=='observed_outcome' and r.get('horizon_seconds')==900 and r.get('status')=='OBSERVED':labels[r['episode_id']]=r
    for c in controls:
        p=events.get(c['paired_to'])
        if p:c.update(family=p['family'],nonoverlapping_within_stock=p['nonoverlapping_within_stock'],is_control=True);events[c['episode_id']]=c
    rows=[]
    for ident,e in events.items():
        at=timestamp(e['at']);f=e['features'];source=timestamp(f.get('source_at'));receipt=timestamp(f.get('received_at'));label=labels.get(ident)
        if not label or at<start or source is None or source<start or receipt is None or receipt<start or e['transport']!='ws' or not e.get('nonoverlapping_within_stock'):continue
        if not '2026-01-01'<=at.date().isoformat()<='2026-12-31':continue
        f=oriented(f,e['side']);values=[f.get(k) for k in GROUPS['PVD']]
        if any(v is None or not np.isfinite(v) for v in values):continue
        rows.append(dict(episode_id=ident,session=at.astimezone(__import__('zoneinfo').ZoneInfo('Asia/Kolkata')).date().isoformat(),family=e['family'],
            side=e['side'],weight=.5 if e.get('is_control') else 1.,is_control=e.get('is_control',False),
            target_signed_bps=label['mid_return_bps']*e['side'],**{k:f[k] for k in GROUPS['PVD']}))
    return pd.DataFrame(rows)


def fit():
    ready=json.loads((OUT/'forward-readiness.json').read_text());days=sorted({r['session'] for r in ready['sessions'] if r['transport']=='ws' and r['quality_pass']})
    if len(days)<20:
        status={'status':'FORWARD_DATA_REQUIRED','quality_sessions':len(days),'required_training_sessions':20,'models_trained':0};dump(OUT/'model-status.json',status);print(json.dumps(status));return
    data=panel();train=data[data.session.isin(days[:20])] if len(data) else data
    if not len(train):dump(OUT/'model-status.json',{'status':'FORWARD_DATA_REQUIRED','reason':'No common eligible observed15minute labels'});return
    models={}
    for family in ('H3-A','H3-B','H3-C'):
        d=train[train.family.eq(family)]
        if len(d[~d.is_control])<30 or d.session.nunique()<10:continue
        for group,cols in GROUPS.items():
            x=d[cols].to_numpy(float);w=d.weight.to_numpy();y=d.target_signed_bps.to_numpy();mu=np.average(x,axis=0,weights=w);sd=np.sqrt(np.average((x-mu)**2,axis=0,weights=w));sd=np.where(sd>1e-12,sd,1)
            design=np.c_[np.ones(len(x)),(x-mu)/sd];penalty=np.eye(design.shape[1]);penalty[0,0]=0
            beta=np.linalg.solve(design.T@(w[:,None]*design)+penalty,design.T@(w*y))
            models[family+'|'+group]=dict(columns=cols,mean=mu.tolist(),scale=sd.tolist(),coefficients=beta.tolist(),ridge_alpha=1)
    if not models:
        dump(OUT/'model-status.json',dict(status='FORWARD_DATA_REQUIRED',reason='No family has30 nonoverlapping targets across10 training days',models_trained=0));return
    target=OUT/'frozen-forward-model.json'
    if target.exists():raise RuntimeError('Never overwrite a forward-frozen model; use a new protocol/version')
    value=dict(protocol_sha256=sha(OUT/'protocol-frozen.json'),training_sessions=days[:20],training_end=days[19],
        primary_horizon_seconds=900,model_budget=9,models=models,panel_sha256=hashlib.sha256(train.to_csv(index=False).encode()).hexdigest(),
        scope_end='2026-12-31',fit_uses_evaluation=False)
    dump(target,value);dump(OUT/'model-freeze.json',dict(model_sha256=sha(target),training_end=days[19],protocol_sha256=value['protocol_sha256']))
    train.to_csv(OUT/'training-panel.csv',index=False);dump(OUT/'model-status.json',dict(status='FROZEN_FOR_LATER_EVALUATION',models_trained=len(models)))


def calibration():
    """Freeze a conservative quote-cost tail allowance from training controls only."""
    m=load()
    if not m:dump(OUT/'calibration-status.json',dict(status='FORWARD_DATA_REQUIRED',reason='No frozen forward training model'));return
    path=OUT/'execution-calibration.json'
    if path.exists():raise RuntimeError('Never overwrite frozen execution calibration')
    dates=set(m['training_sessions']);rows=[]
    for eventfile in sorted((OUT/'runs').glob('*/derived-events.jsonl.gz')):
        manifest=json.loads((eventfile.parent/'manifest.json').read_text())
        if manifest.get('protocol_sha256')!=m['protocol_sha256']:continue
        with gzip.open(eventfile,'rt',encoding='utf-8') as stream:
            for line in stream:
                r=json.loads(line)
                if r['kind']!='diagnostic_entry_cost' or not r.get('is_control') or r.get('transport')!='ws':continue
                day=timestamp(r['at']).astimezone(__import__('zoneinfo').ZoneInfo('Asia/Kolkata')).date().isoformat();c=r.get('cost') or {}
                if day in dates and c.get('status')=='QUOTED_BOUND_ONLY':rows.append(dict(day=day,key=r['key'],cost_bps=-c['net_bps']))
    data=pd.DataFrame(rows)
    if len(data)<200 or data.day.nunique()<10:
        dump(OUT/'calibration-status.json',dict(status='FORWARD_DATA_REQUIRED',observations=len(data),reason='Need200 training control bounds across10 training sessions'));return
    daily=data.groupby('day').cost_bps.median().to_numpy();median=float(np.median(daily));tail=float(np.quantile(data.cost_bps,.95))
    value=dict(protocol_sha256=m['protocol_sha256'],model_sha256=sha(OUT/'frozen-forward-model.json'),training_end=m['training_end'],
        fresh_forward_controls=True,control_bounds=len(data),control_sessions=int(data.day.nunique()),
        median_day_cost_bps=median,p95_cost_bps=tail,uncertainty_bps=max(1.,tail-median),
        interpretation='Training-only observed quote-cost tail allowance, not measured market impact or actual fill uncertainty')
    dump(path,value);dump(OUT/'execution-calibration-freeze.json',dict(sha256=sha(path)))


def load():
    path=OUT/'frozen-forward-model.json';guard=OUT/'model-freeze.json'
    if not path.exists() or not guard.exists():return None
    lock=json.loads(guard.read_text());assert sha(path)==lock['model_sha256'];value=json.loads(path.read_text());assert value['protocol_sha256']==sha(OUT/'protocol-frozen.json');return value


def predict(model,family,features,at,side=1):
    if not model or at.date().isoformat()<=model['training_end'] or at.year>2026:return {}
    predictions={};features=oriented(features,side)
    for group in GROUPS:
        m=model['models'].get(family+'|'+group)
        if not m:continue
        x=[features.get(k) for k in m['columns']]
        if any(v is None or not np.isfinite(v) for v in x):continue
        z=(np.array(x)-m['mean'])/m['scale'];predictions[group]=float(np.r_[1,z]@m['coefficients'])
    return predictions

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('action',nargs='?',choices=['fit','calibrate'],default='fit');a=p.parse_args()
    fit() if a.action=='fit' else calibration()
