"""Export canonical atom summaries for reconstructible endpoint laws."""
from .common import *
from .laws import Law

KEYED=(
    (14,'standalone-endpoint-laws.npz','horizon/origin/model/target'),
    *((11,f'distribution-archive/{name}.npz','horizon/model/origin/target') for name in
        ('breadth','disjoint','distribution','international','memory','overlap')),
    *((12,f'laws/{name}.npz','horizon/model/origin/target') for name in ('ensemble','market','phase','priced','aligned-Q')),
)
WEIGHTED={
    19:('native-mechanism-laws.npz','native-residual-laws.npz'),
    20:('architecture-laws.npz','native-mechanism-laws.npz','strong-parent-component-laws.npz','lifetime-parent-laws.npz'),
    21:('index-forecast-laws.npz','protected-return-laws.npz'),
    22:('india-forecast-laws.npz','protected-india-return-laws.npz'),
}
MATRIX=((17,'original-clock-laws.npz','atoms','log'),(17,'opening-laws.npz','atoms','log opening gap'),
        (18,'original-event-laws.npz','atoms','log'),(19,'endpoint-laws.npz','log_return_atoms','log'))


def archive_law_fields():
    p=OUT/'exact-return-law-fields.csv.gz'
    rows=[]
    content=[]
    first=True

    def add(v,file,i,law,key='',units='arithmetic return'):
        x,w=law.atoms,law.weights
        c=np.cumsum(w)
        z=x[np.searchsorted(c,np.array([.01,.05,.10,.5,.9,.95,.99])).clip(0,len(x)-1)]
        m=w@x
        rows.append(dict(version=v,file=file,law_id=i,key=key,stored_units=units,n_atoms=len(x),exact_sign_mass=w@(x>0),
                         arithmetic_mean=m,variance=max(0.,w@(x*x)-m*m),q01=z[0],q05=z[1],q10=z[2],q50=z[3],q90=z[4],q95=z[5],q99=z[6]))

    def flush():
        nonlocal first
        if rows:
            with gzip.open(p,'wt' if first else 'at',encoding='utf-8',compresslevel=4) as out:
                pd.DataFrame(rows).to_csv(out,index=False,header=first,float_format='%.13g')
            first=False
            rows.clear()

    for v,name,layout in (*KEYED,*((v,f,'indexed case ID') for v,s in WEIGHTED.items() for f in s)):
        root=root_for(v)
        full=root/name
        rel=full.relative_to(ROOT).as_posix()
        with np.load(full,allow_pickle=False) as q:
            if not {'atoms','weights','offsets'}.issubset(q.files):
                continue
            atom=q['atoms'];w=q['weights'];ends=q['offsets']
            keys=q['keys'] if 'keys' in q.files else None
            count=0
            for i,(lo,hi) in enumerate(zip(ends[:-1],ends[1:],strict=True)):
                if keys is not None:
                    fields=list(keys[i])
                    dates=[x for x in fields if len(x)==10 and x[:2]=='20']
                    if any(not FIRST<=x<=FREEZE for x in dates):
                        continue
                else:
                    fields=[]
                units='option-implied arithmetic return' if name.endswith('aligned-Q.npz') else 'arithmetic return'
                add(v,rel,i,Law.build(atom[lo:hi],w[lo:hi]),' | '.join(map(str,fields)),units)
                count+=1
                if len(rows)>=16000:
                    flush()
        content.append(dict(version=v,path=rel,encoding=layout,n=count,sha256=sha(full)))

    for v,name,key,units in MATRIX:
        path=root_for(v)/name
        rel=path.relative_to(ROOT).as_posix()
        with np.load(path,allow_pickle=False) as z:
            a=z[key]
        for i,x in enumerate(a):
            add(v,rel,i,Law.build(np.expm1(x.astype(float))),units=units)
            if len(rows)>=16000:
                flush()
        content.append(dict(version=v,path=rel,encoding='Indexed equal-weight log support transformed with expm1',n=len(a),sha256=sha(path)))

    seen={}
    for v in range(3,12):
        root=root_for(v)
        for path in sorted(root.rglob('*-laws.jsonl')):
            if 'sources' in path.parts or not path.stat().st_size:
                continue
            if v==11 and path.name.removesuffix('-laws.jsonl') in ('breadth','disjoint','distribution','international','memory','overlap'):
                continue
            rel=path.relative_to(ROOT).as_posix()
            digest=sha(path)
            if digest in seen:
                content.append(dict(version=v,path=rel,encoding='exact file alias to '+seen[digest],n=0,sha256=digest))
                continue
            seen[digest]=rel
            count=0
            with path.open(encoding='utf-8') as f:
                for i,line in enumerate(f):
                    z=json.loads(line)
                    origin=z.get('origin','')
                    endpoint=z.get('endpoint','')
                    if not isinstance(origin,str) or not isinstance(endpoint,str) or not (FIRST<=origin<=endpoint<=FREEZE):
                        continue
                    atoms=[]
                    if 'weights' in z and ('atoms' in z or 'return_atoms' in z):
                        atoms.append((z.get('model',''),z.get('atoms',z.get('return_atoms')),z['weights']))
                    for field in z:
                        if field.endswith('_atoms') and field!='return_atoms':
                            parent=field.removesuffix('_atoms')
                            if parent+'_weights' in z:
                                atoms.append((parent,z[field],z[parent+'_weights']))
                    for model,a,w in atoms:
                        k=[z.get('horizon',''),model,origin,endpoint]
                        add(v,rel,i,Law.build(a,w),' | '.join(map(str,k)))
                        count+=1
                        if len(rows)>=16000:
                            flush()
            content.append(dict(version=v,path=rel,encoding='original JSONL line and named atom/weight pair',n=count,sha256=digest))
    for h in HORIZONS:
        v=13
        f=root_for(v)/f'joint-path-target-atoms-{h}.npz'
        with np.load(f,allow_pickle=False) as a:
            key=a['keys'];target=a['targets'].tolist().index('endpoint_return');points=a['values'][:,:,target]
        c=0
        for i,(day,model) in enumerate(key):
            if FIRST<=day<=FREEZE:
                add(v,f.relative_to(ROOT).as_posix(),i,Law.build(points[i]),f'{h} | {model} | {day}')
                c+=1
        content.append(dict(version=v,path=f.relative_to(ROOT).as_posix(),encoding='exact equal-support endpoint from indexed joint-target scenario',
                            n=c,sha256=sha(f)))
    flush()
    write('exact-return-law-field-source-map.csv',pd.DataFrame(content))
    print('Indexed exact weighted or equal-support moments for',sum(s['n'] for s in content),'archived laws.',flush=True)


if __name__=='__main__':
    archive_law_fields()
