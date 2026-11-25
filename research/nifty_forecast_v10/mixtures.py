"""Combine entire probability laws on identical historical origins."""
from .common import *
from .estimators import Distribution
from .experiments import buckets,cohort_queries,score_law

MIX={
 'J10_TARGET_BLEND':(['T_SIGNMAG','T_VOL_STUDENT'],[.50,.50],'T_VOL_STUDENT'),
 'J10_STRUCTURAL_BLEND':(['BASE_ROTATION','S_ELASTIC','T_VOL_STUDENT'],[.40,.30,.30],'BASE_ROTATION'),
 'J10_HISTORY_SHRINK':(['BASE_ROTATION','S_ELASTIC','T_VOL_STUDENT','HISTORY'],[.20,.15,.15,.50],'J10_STRUCTURAL_BLEND'),
 'J10_SMALL_BLEND':(['C85_SPREAD','T_SIGNMAG','HISTORY'],[.45,.35,.20],'C85_SPREAD'),
 'J10_TRANSFER_BLEND':(['X_ADAPT','T_VOL_STUDENT'],[.5,.5],'X_ADAPT'),
}


def run():
    save('mixture-registry.json',{'registered_at':now(),'code_hash':sha(SRC/'mixtures.py'),'configurations':{
      n:{'members':names,'weights':w,'parent':p,'hypothesis':'Fixed complete-law mixture; adaptive wave registered after main families'}
      for n,(names,w,p) in MIX.items()}})
    names={n for m,_,__ in MIX.values() for n in m};seen={}
    for b in ['base','target','composition','structure','transfer']:
        with (OUT/f'{b}-laws.jsonl').open(encoding='utf-8') as f:
            for line in f:
                row=json.loads(line)
                if row['model'] in names:seen[(row['horizon'],row['origin'],row['model'])]=row
    p=pd.read_csv(OUT/'base-predictions.csv');p=p[p.model.eq('HISTORY')].set_index(['horizon','origin'])
    cuts=[f'train_bucket_cut{j}' for j in range(5)]
    predictions=[];laws=[];ledger=[]
    for h in [5,21]:
        for (c,fold),g in cohort_queries(h).groupby(['split','fold'],sort=False):
            for name,(members,weights,parent) in MIX.items():
                count=0
                for row in g.itertuples():
                    found=[seen.get((h,row.origin,m)) for m in members]
                    if any(a is None for a in found):continue
                    a=np.concatenate([d['atoms'] for d in found]);w=np.concatenate([f*np.array(d['weights']) for d,f in zip(found,weights)])
                    law=Distribution(a,w);ref=p.loc[h,row.origin]
                    predictions.append({**score_law(h,fold,name,row,law,ref.reference_close,c),**buckets(law,row.realized_return,ref[cuts].to_numpy(float))})
                    laws.append({'model':name,'horizon':h,'cohort':c,'origin':row.origin,'endpoint':row.endpoint,
                                 'atoms':law.a.tolist(),'weights':law.w.tolist()})
                    count+=1
                ledger.append({'horizon':h,'cohort':c,'fold':fold,'model':name,'cutoff':g.origin.min(),
                               'status':'ok' if count else 'unestimated','query_count':count,'reason':None if count else 'component law absent'})
    write('mixture-predictions.csv',pd.DataFrame(predictions));save('mixture-ledger.json',ledger)
    (OUT/'mixture-laws.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in laws),encoding='utf-8')


if __name__=='__main__':run()
