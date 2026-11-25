"""Inventory older searches and replay a bounded search under serial block nulls."""
import hashlib
from .common import *
from .run_models import cohort_queries, inputs, indices
from .models import fit, location, laws, Distribution
from research.nifty_forecast_v6.common import V3, V4


def json_digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,default=str).encode()).hexdigest()


def previous():
    roots={3:V3,4:V4,5:V5,6:V6,7:V7,8:V8}
    config=[];inventory=[];shape=[]
    for version,folder in roots.items():
        for p in sorted(folder.glob('*registry*.json')):
            obj=json.loads(p.read_text(encoding='utf-8'));inventory.append({'version':version,'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'structure':'dict' if isinstance(obj,dict) else 'list'})
            if not isinstance(obj,dict):continue
            for k in ['configurations','configuration','specifications','hypotheses','specs','models','variants','systems']:
                rec=obj.get(k)
                if not isinstance(rec,dict):continue
                for n,value in rec.items():
                    if isinstance(value,dict):
                        fingerprint={k:v for k,v in value.items() if k not in ['hypothesis','parent','selection','diagnostic','description','only_horizon','horizons']}
                        config.append({'version':version,'registry':p.name,'model':n,'missing_design_detail':not bool(fingerprint),
                                       'config_hash':json_digest(value),'shape_hash':json_digest(fingerprint),'record':json.dumps(value,sort_keys=True,default=str)})
        choices=['all-predictions.csv','predictions.csv','distribution-predictions.csv']
        files=[p for name in choices if (p:=folder/name).exists()]
        for p in files:
            data=pd.read_csv(p)
            if 'model' not in data or 'horizon' not in data or 'origin' not in data:continue
            if 'split' in data:data=data[data.split=='outer_exposed']
            if 'cohort' in data:data=data[data.cohort=='primary']
            for (h,n),g in data.groupby(['horizon','model']):
                cols=[c for c in ['origin','p','predicted_mean','crps'] if c in g];z=g.sort_values('origin')[cols].copy()
                for c in cols[1:]:z[c]=z[c].round(11)
                shape.append({'version':version,'file':p.name,'model':n,'horizon':h,'n':len(g),'prediction_fingerprint':hashlib.sha256(z.to_csv(index=False).encode()).hexdigest()})
    legacy=ROOT/'artifacts/nifty_forecast'
    for p in sorted(legacy.rglob('*.json')):
        if 'registry' in p.name or 'manifest' in p.name:inventory.append({'version':'1–2','path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'structure':'legacy manifest'})
    c=pd.DataFrame(config);p=pd.DataFrame(shape)
    write('historical-config-inventory.csv',c);write('historical-prediction-fingerprints.csv',p);write('historical-registry-files.csv',pd.DataFrame(inventory))
    save('historical-search-accounting.json',{'registry_and_manifest_files':len(inventory),'parsed_config_records':len(c),'exact_config_hashes':c.config_hash.nunique(),
         'candidate_shape_hashes':c.shape_hash.nunique(),'scored_model_horizon_vectors':len(p),'distinct_vector_fingerprints':p.prediction_fingerprint.nunique(),
         'scope':'Recovered primary registry files and scored CSVs. V1–V2 formats heterogeneous. Fingerprints detect same stored vector on exact dates, not economic equality. Config precision and source identities are incomplete in early manifests.'})


def permute(values,rng,length):
    blocks=[values[j:j+length] for j in range(0,len(values),length)]
    return np.concatenate([blocks[j] for j in rng.permutation(len(blocks))])


def null_search():
    specs={'raw':('both_changes',{}),'residual':('residual',{}),'structure':('structure_change',{}),
           'compact':('small_resid',{}),'fin_panel':('financial_panel',{}),'ar_innovation':('innovation_ar',{}),
           'weighted':('small_resid',{'kind':'ew','half_life':90}), 'balanced':('cluster_rot',{'kind':'elastic','rep':'cluster','dedup':True})}
    x,_=inputs();q=cohort_queries(5);q=q[q.split=='later'];y=matrix('labels-5.csv');latest=[];scores=[]
    save('null-search-plan.json',{'at':now(),'configs':specs,'draws':24,'seed':SEED,'block_lengths':[5,10,15],
          'estimand':'Maximum Brier and CRPS gain for each refitted null search against same-date authentic historical law. Includes unpermuted search as draw -1.'})
    for draw in [-1,*range(24)]:
        block=[5,10,15][draw%3]
        for k,(fold,g) in enumerate(q.groupby('fold')):
            cutoff=g.origin.min();tr,ii,vv,_=indices(y,cutoff,{})
            yt=y.loc[tr,'return'].to_numpy();yi=y.loc[ii,'return'].to_numpy();yv=y.loc[vv,'return'].to_numpy()
            hold=Distribution(yt[-252:]);truth=y.loc[g.origin,'return'].to_numpy()
            hscore=[hold.score(v) for v in truth]
            if draw>=0:
                rng=np.random.default_rng(SEED+100*draw+k);yt=permute(yt,rng,block);yi=permute(yi,rng,block);yv=permute(yv,rng,block)
            for n,(frame,s) in specs.items():
                a=x[frame];model=fit(s,a.loc[tr],yt);inner=fit(s,a.loc[ii],yi)
                ds=laws(model,a.loc[g.origin],yv-location(inner,a.loc[vv]),a.loc[vv,'p_rv21'].to_numpy())
                for r,d,base in zip(g.itertuples(),ds,hscore):
                    current=d.score(r.realized_return)
                    scores.append({'draw':draw,'block':block if draw>=0 else 0,'model':n,'origin':r.origin,'fold':fold,'training_last_endpoint':y.loc[tr,'endpoint'].max(),
                                   'brier_gain':base['brier']-current['brier'],'crps_gain':base['crps']-current['crps']})
        print('Null search',draw,'complete',flush=True)
    data=pd.DataFrame(scores);write('null-search-predictions.csv',data)
    for (draw,block),g in data.groupby(['draw','block']):
        s=g.groupby('model')[['brier_gain','crps_gain']].mean()
        latest.append({'draw':int(draw),'block':int(block),'best_brier_gain':float(s.brier_gain.max()),'brier_winner':s.brier_gain.idxmax(),
                       'best_crps_gain':float(s.crps_gain.max()),'crps_winner':s.crps_gain.idxmax()})
    write('null-search-maxima.csv',pd.DataFrame(latest))


if __name__=='__main__':
    previous();null_search()
