"""Audit what primary PDF disclosures add to the exchange's short public descriptions."""
from pypdf import PdfReader
from .common import *
from .fundamentals import canonical
from .inventory import PLUS,MINUS,MONEY,UNCERTAIN,FUTURE,clean
from .sources import jobs

TYPES=('guidance','order_win','order_cancellation','credit','regulatory','acquisition','business_update')
PER_FAMILY=16

def announce():
    e=csv('issuer-events.csv.gz')
    choices=[]
    for group in TYPES:
        q=e[e.family.eq(group)&e.attachment.fillna('').str.lower().str.endswith('.pdf')].sort_values(['eligible','record_id'])
        if len(q):
            choices.extend(q.iloc[np.linspace(0,len(q)-1,min(PER_FAMILY,len(q)),dtype=int)].to_dict('records'))
    save('attachment-sample-registration.json',dict(at=now(),families=TYPES,per_family=PER_FAMILY,
         episodes=[r['episode_id'] for r in choices],
         rule='Equally spaced eligible metadata rows within event family. Read the first six available text pages. Sample selection uses timestamps and topic only.'))
    tasks=[];keep=[]
    for r in choices:
        u=canonical(r['attachment'])
        if not u:continue
        tasks.append((u,'sources/disclosure-sample/'+r['record_id'].replace(':','-')+'.pdf',None));keep.append(r)
    sources=list(jobs(tasks,5))
    results=[]
    for r,q in zip(keep,sources):
        path=OUT/q['file'] if q.get('file') else None
        pages=[];text=''
        if path and path.read_bytes()[:4]==b'%PDF':
            try:
                doc=PdfReader(path)
                pages=[clean(p.extract_text()) for p in doc.pages[:6]]
                text=' '.join(pages)
            except (ValueError,KeyError,RuntimeError,NotImplementedError):
                pass
        pos,neg=PLUS.search(text),MINUS.search(text)
        signed=int(pos is not None)-int(neg is not None)
        cues=[]
        for k,rx in [('positive',PLUS),('negative',MINUS),('sized',MONEY),('horizon',FUTURE),('uncertainty',UNCERTAIN)]:
            for i,p in enumerate(pages,1):
                m=rx.search(p)
                if m:
                    # Keep only a short supporting phrase, with the exact verified original and page.
                    cues.append(f'{k} p{i} '+(' '.join(m.group().split()[:16])))
                    break
        results.append(dict(episode=r['episode_id'],record_id=r['record_id'],symbol=r['symbol'],family=r['family'],
             available=r['eligible'],document=q.get('file'),available_text=int(len(text)>140),pages_attempted=len(pages),
             metadata_direction=r['text_sign'],document_direction=signed,document_conflict=int(bool(pos and neg)),
             monetary_or_percent_mention=int(bool(MONEY.search(text))),horizon_mention=int(bool(FUTURE.search(text))),
             uncertainty_mention=int(bool(UNCERTAIN.search(text))),support=' | '.join(cues),attachment_url=q['url']))
    table=pd.DataFrame(results)
    save('attachment-source-receipts.json',sources)
    write('attachment-content-audit.csv',table)
    print('Audited disclosure attachments',len(table),'with text on',int(table.available_text.sum()),flush=True)

def compare():
    s=csv('attachment-content-audit.csv')
    x=csv('stock-event-pairs.csv.gz',usecols=['episode','day','symbol','stage','horizon','beta_residual','matched_abnormal'])
    a=x[x.stage.eq('after_reaction')&x.horizon.eq(5)].merge(s[s.available_text.eq(1)],on=['episode','symbol'],validate='1:1')
    a=a[a.beta_residual.notna()].copy()
    eligible=a.metadata_direction.ne(0)&a.document_direction.ne(0)
    pairs=a[eligible].copy()
    for f,tag in [('metadata_direction','metadata'),('document_direction','attachment')]:
        pairs[tag+'_hit']=(np.sign(pairs.beta_residual)==pairs[f]).astype(int)
    write('attachment-event-matches.csv',pairs)
    save('attachment-comparison.json',dict(sampled=len(s),text_documents=int(s.available_text.sum()),document_signed=int(s.document_direction.ne(0).sum()),
         metadata_signed=int((s.available_text.eq(1)&s.metadata_direction.ne(0)).sum()),
         document_only_sign=int((s.available_text.eq(1)&s.document_direction.ne(0)&s.metadata_direction.eq(0)).sum()),
         different_sign=int((s.available_text.eq(1)&s.document_direction.ne(s.metadata_direction)).sum()),
         numeric_support=int(s.monetary_or_percent_mention.sum()),horizon_mentions=int(s.horizon_mention.sum()),
         matched_after_reaction=len(a),both_signed_matched=len(pairs),metadata_hit=int(pairs.metadata_hit.sum()),attachment_hit=int(pairs.attachment_hit.sum()),
         rule='Signed or conflicting text is determined from named phrases. Found monetary or percentage fragments are an audit of disclosure detail. They are not transcribed as a reported quantitative forecast. Direction comparison is a small, fixed diagnostic on identical cases.'))

if __name__=='__main__':
    import sys
    (compare if 'compare' in sys.argv else announce)()
