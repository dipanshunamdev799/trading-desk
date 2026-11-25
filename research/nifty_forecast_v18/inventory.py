"""Inventory exchange disclosures, preserve their clocks, and deduplicate event arrivals."""
from bisect import bisect_right
from collections import Counter,defaultdict
from datetime import datetime,timedelta
import hashlib
import re
import sqlite3
from .common import *

DATE=r'(\d{1,2}(?:st|nd|rd|th)?[-/ ](?:[A-Za-z]{3,9}|\d{1,2})[-/, ]+20\d{2}|[A-Za-z]{3,9}\s+\d{1,2}(?:st|nd|rd|th)?[,]?\s+20\d{2}|20\d{2}-\d\d-\d\d)'
MATCH_DATE=re.compile(DATE,re.I)
PERIOD=re.compile(r'(?:quarter(?:\s+and\s+half\s+year)?|period|financial year|half[- ]year|nine months)\s+(?:ended|ending)\s+(?:on\s+)?'+DATE,re.I)
MEETING=re.compile(r'(?:to be held on|scheduled (?:to be held )?(?:on|for)|will be held on|meeting (?:dated|on))\s+'+DATE,re.I)
EFFECTIVE=re.compile(r'(?:with effect from|effective from|effective on|completed on|held on)\s+'+DATE,re.I)
MONEY=re.compile(r'(?:(?:₹|(?:INR|Rs\.?|USD|US\$|EUR)\s*)\s*\d[\d,.]*\s*(?:crore|cr\.?|lakh|million|billion)?|\d[\d,.]*\s*(?:%|crores?\b|lakhs?\b|million\b|billion\b))',re.I)
REVISION=re.compile(r'corrigendum|rectification|revised filing|revision to (?:the )?(?:filing|earlier)|resubmission|re-submit|withdraw(?:al|n) of (?:the )?(?:filing|announcement)',re.I)

FAMILIES={
 'earnings':r'integrated filing.? financial|financial results?|quarterly results?|earnings release|results for the (?:period|quarter|year)',
 'guidance':r'\bguidance\b|revenue outlook|profit outlook|earnings outlook|forecast (?:increase|decrease|revision)',
 'presentation':r'investor presentation|earnings presentation|company presentation',
 'order_cancellation':r'(?:cancell?|terminat|resciss|revok|withdraw).{0,45}(?:order|contract|agreement)',
 'order_win':r'bagging/receiving|order win|(?:bagged|secured|won|received|awarded).{0,36}(?:order|contract|letter of award)|letter of award',
 'expansion':r'business expansion|new facility|new plant|commencement of (?:commercial )?(?:operations|production)|capacity expansion',
 'acquisition':r'\bacquisitions?\b|acquires? (?:a|additional|the) (?:stake|interest)|amalgamation|merger|joint venture',
 'divestment':r'divest(?:ment|iture)|sale of (?:stake|subsidiary|business|assets)|dispos(?:al|ed) of (?:stake|subsidiary)',
 'capex':r'capital expenditure|\bcapex\b',
 'fundraising':r'fundrais|fund rais|raising (?:of )?(?:funds|capital)|qualified institutional placement|rights issue|preferential (?:issue|allotment)|issue of securities',
 'credit':r'credit rating|credit-rating|rating upgrade|rating downgrade|rating reaffirm',
 'debt':r'borrowings|debt repayment|debt securit|debenture|bond issue|loan default|debt refinancing|debt reduction',
 'litigation':r'litigat|\bdispute\b|court order|arbitration|tribunal|legal proceedings',
 'regulatory':r'action\(s\) (?:taken|initiated)|regulatory approval|regulatory developments|regulatory penalty|show cause|USFDA|tax demand',
 'management':r'change in manager|change in management|change in director|appoint(?:ment|ed)|resign(?:ation|ed)|cessation',
 'dividend':r'\bdividend\b',
 'buyback':r'buy[ -]?back|repurchase of shares',
 'action':r'corporate action|bonus (?:issue|shares)|stock split|sub.?division|demerger|rights entitlement|record date',
 'shareholding':r'shareholding pattern|promoter (?:share|acquir|dispos)|insider trading|disclosure under regulation 31|takeover regulations',
 'business_update':r'material (?:business|event|development|issue)|business updates?|operational updates?|sales volume|material agreement',
}
FAMILY_RX={k:re.compile(p,re.I) for k,p in FAMILIES.items()}
PLUS=re.compile(r'upgrad(?:ed|e)|rais(?:ed|es|ing) (?:its )?(?:guidance|outlook)|(?:increase|grow|grew|higher|improv).{0,26}(?:revenue|profit|margin|sales)|(?:secured|awarded|won|bagged).{0,32}(?:order|contract)|received.{0,22}(?:regulatory approval|letter of award)|rating outlook.{0,12}positive',re.I)
MINUS=re.compile(r'downgrad(?:ed|e)|reduc(?:ed|es|ing) (?:its )?(?:guidance|outlook)|(?:fall|declin|lower|decreas|loss).{0,26}(?:revenue|profit|margin|sales)|(?:cancel|terminat|revok).{0,30}(?:order|contract)|(?:penalty|fine) imposed|\bdefaulted\b|rating outlook.{0,12}negative',re.I)
UNCERTAIN=re.compile(r'subject to|contingent|uncertain|proposed|indicative|under consideration|potential|conditional',re.I)
FUTURE=re.compile(r'within \d+\s+(?:days|weeks|months|years)|over (?:the )?next \d+\s+(?:days|weeks|months|years)|by (?:the end of )?(?:Q[1-4]|FY\s*20\d{2}|20\d{2})',re.I)
SECTOR={
 'bank':r'\bbank(?:s|ing)?\b','finance':r'financ|insurance|asset manage|housing finance|credit rating',
 'it':r'computer|software|information technology|IT Enabled|telecom',
 'energy':r'refiner|petrol|power|oil|gas |coal|utility|utilities|energy',
 'auto':r'automobil|auto ancil|transport equipment|tyre',
 'consumer':r'food|FMCG|consumer|beverage|tobacco|household|retail|textil|personal care',
 'materials':r'metal|cement|mining|steel|chemical|paper|fertili',
 'health':r'pharma|health|hospital|biotech|diagnostic',
 'industrial':r'industrial|engineering|construction|capital goods|electrical|infrastructure|equipment',
}

def sector(s):
    return next((k for k,v in SECTOR.items() if re.search(v,s,re.I)),'other')

def clean(x):
    return re.sub(r'\s+',' ',str(x or '')).strip()

def one_day(s):
    if not s:return None
    s=re.sub(r'(?<=\d)(?:st|nd|rd|th)\b','',s.strip(),flags=re.I).replace(',','')
    try:
        return pd.to_datetime(s,dayfirst=not s[:4].isdigit(),format='mixed').strftime('%Y-%m-%d')
    except (ValueError,AttributeError):
        return None

def contextual_date(p,s):
    m=p.search(s)
    return one_day(m.group(1)) if m else None

def time_value(v):
    try:return datetime.strptime(clean(v),'%d-%b-%Y %H:%M:%S')
    except ValueError:return None

def classify(subject,text):
    full=subject+' '+text
    planned=bool(re.search(r'(board meeting|meeting of the board|intimation)',full,re.I) and MEETING.search(text))
    period=contextual_date(PERIOD,text) if any(w in full.lower() for w in ('result','earnings','financial')) else None
    families=[k for k,rx in FAMILY_RX.items() if rx.search(full)]
    if planned:
        tag='earnings_schedule' if 'earnings' in families or re.search(r'results|earnings',text,re.I) else 'meeting_notice'
    elif 'earnings' in families and re.search(r'clarification|newspaper',subject,re.I):
        tag='earnings_followup'
    else:
        tag=families[0] if families else 'routine_or_unclassified'
    positive=PLUS.search(text);negative=MINUS.search(text)
    signed=int(positive is not None)-int(negative is not None)
    alternative=int(any(k in families for k in ('order_win','expansion','buyback')))-int(any(k in families for k in ('order_cancellation','litigation')))
    support=' | '.join(m.group() for m in (positive,negative,UNCERTAIN.search(text),FUTURE.search(text)) if m)
    material=int(tag not in ('routine_or_unclassified','meeting_notice','earnings_schedule','presentation','earnings_followup','shareholding')
                 or bool(positive or negative))
    return dict(family=tag,all_families='|'.join(families),report_period=period,
                period_inside_scope=int(bool(period and FIRST<=period<=FREEZE)),
                event_date=contextual_date(EFFECTIVE,text),scheduled=contextual_date(MEETING,text) if planned else None,
                text_sign=signed,category_direction_proxy=alternative,mixed=int(bool(positive and negative)),
                material=material,explicit_uncertainty=int(bool(UNCERTAIN.search(text))),evidence=support,
                inline_quantities=' | '.join(MONEY.findall(text)[:10]),
                stated_horizon=(FUTURE.search(text).group() if FUTURE.search(text) else None),
                revised=int(bool(REVISION.search(full))))

def run():
    register()
    sources=[];records=[];counts=Counter()
    for yr,n in ((2025,176022),(2026,169204)):
        name=f'sources/source-probes/announcements-{yr}.json.gz'
        payload=read(name,V17)
        assert len(payload)==n
        sources.append(dict(year=yr,rows=len(payload),file=(V17/name).relative_to(ROOT).as_posix(),sha256=sha(V17/name)))
        for k,x in enumerate(payload):
            ticker=clean(x.get('symbol')); text=clean(x.get('attchmntText')); subject=clean(x.get('desc'))
            dl=clean(x.get('attchmntFile')); industry=clean(x.get('smIndustry'))
            filing=time_value(x.get('an_dt')); p=time_value(x.get('exchdisstime'))
            eligible=bool(p and FIRST<=p.date().isoformat()<=FREEZE and (filing is None or p>=filing))
            suffix=''; clock=(p+timedelta(minutes=RELEASE_DELAY)) if eligible else None
            if p is not None:
                suffix='before_open' if p.strftime('%H:%M')<'09:15' else 'during_session' if p.strftime('%H:%M')<'15:30' else 'after_close'
            data=classify(subject,text)
            records.append(dict(record_id=f'{yr}:{k}',source_year=yr,source_row=k,symbol=ticker,
               isin=clean(x.get('sm_isin')),company=clean(x.get('sm_name')),industry=industry,sector=sector(industry),
               source_sequence=clean(x.get('seq_id')),filed=filing.isoformat(sep=' ') if filing else None,
               release=p.isoformat(sep=' ') if p else None,eligible=clock.isoformat(sep=' ') if clock else None,
               subject=subject,summary=text,attachment=dl,has_xbrl=int(x.get('hasXbrl') in (True,'True','Y','Yes')),
               status='timed' if eligible else 'outside_vintage_or_unverified_clock',publication_bucket=suffix,**data))
    frame=pd.DataFrame.from_records(records).sort_values(['release','record_id'],na_position='last')
    del records
    seen={}; episodes={}; periods={}; representatives=[];dups=[];reasons=[]
    for r in frame.itertuples(index=False):
        identity=r.symbol or r.isin or r.company
        why=''; source=None
        strong=[]
        if r.source_sequence and r.source_sequence not in ('0','-1'):
            strong.append(('exchange_sequence',identity,r.source_sequence))
        if r.attachment:
            strong.append(('identical_attachment',identity,r.attachment.lower().split('?',1)[0]))
        for key in strong:
            if key in seen:
                why=key[0];source=seen[key];break
        if source is None and r.summary and r.release and len(r.summary)>30:
            t=hashlib.blake2s(r.summary.lower().encode('utf8'),digest_size=12).hexdigest()
            key=(identity,r.family,t)
            prev=episodes.get(key)
            hour=datetime.fromisoformat(r.release)
            if prev and hour-prev[0]<=timedelta(hours=36):
                why='same_summary_within_36h';source=prev[1]
            elif r.eligible:
                episodes[key]=(hour,r.record_id)
        if source is None and r.eligible and r.family=='earnings' and r.report_period and not r.revised:
            term=(identity,r.report_period)
            old=periods.get(term)
            if old:
                why='additional_publication_same_earnings_period';source=old
            else:
                periods[term]=r.record_id
        if r.eligible:
            for key in strong:
                seen.setdefault(key,source or r.record_id)
        is_duplicate=int(source is not None)
        representatives.append(source or r.record_id);dups.append(is_duplicate);reasons.append(why)
        counts[why or 'representative']+=1
    frame['episode_id']=representatives;frame['duplicate']=dups;frame['duplicate_reason']=reasons
    seed=set(csv('issuer-seed.csv').stock)
    frame['seed_issuer']=frame.symbol.isin(seed).astype(int)
    usable=frame.loc[frame.eligible.notna()&frame.duplicate.eq(0)&frame.seed_issuer.eq(1)].copy()
    fields=['record_id','episode_id','symbol','isin','industry','sector','source_sequence','filed','release','eligible','subject',
            'family','all_families','report_period','event_date','scheduled','text_sign','category_direction_proxy','mixed','material',
            'explicit_uncertainty','evidence','inline_quantities','stated_horizon','revised','attachment','publication_bucket','summary']
    write('issuer-events.csv.gz',usable[fields])
    write('archive-category-counts.csv',frame.assign(timed=frame.eligible.notna().astype(int)).groupby(
           ['source_year','family','subject'],as_index=False).agg(rows=('record_id','size'),timed=('timed','sum'),duplicates=('duplicate','sum'),
           seed_rows=('seed_issuer','sum'),material=('material','sum')))
    write('extraction-examples.csv',usable[usable.evidence.ne('')|usable.family.isin(['earnings','earnings_schedule'])].groupby(
          ['family','text_sign'],group_keys=False).head(6)[fields[:-1]])
    database=OUT/'corporate-information.sqlite'
    with sqlite3.connect(database) as c:
        frame.to_sql('announcements',c,if_exists='replace',index=False,chunksize=5000)
        c.executescript('CREATE UNIQUE INDEX announcement_id ON announcements(record_id); CREATE INDEX eligible_time ON announcements(eligible); CREATE INDEX firm_clock ON announcements(symbol,eligible); CREATE INDEX event_family ON announcements(family,release);')
        pd.DataFrame(sources).to_sql('sources',c,if_exists='replace',index=False)
    counts2=frame.groupby(['source_year']).agg(rows=('record_id','size'),timed=('eligible','count'),duplicates=('duplicate','sum'),
                                            issuers=('symbol','nunique'),attached=('attachment',lambda x:int(x.ne('').sum())),
                                            amendments=('revised','sum')).reset_index()
    save('announcement-inventory.json',dict(source=sources,counts=counts2.to_dict('records'),
          duplicates=dict(counts),seed_rows=len(usable),seed_issuers=int(usable.symbol.nunique()),material_rows=int(usable.material.sum()),
          availability=f'Exchange dissemination plus {RELEASE_DELAY} minutes, local IST. Untimed or out-of-vintage observations are inventoried separately.',
          feature_source='Deterministic exchange title and exchange summary regexes. Financial fields enter only from separate published structured records. Attachment links flag availability in the listing. Verified downloads tracked separately.',
          dedup='Exchange sequence, identical attachment, identical text within 36 hours, and same issuer/reporting-period earnings releases where the period was explicit. Revision cues stay visible.'))
    print('Corporate inventory',len(frame),'archived records and',len(usable),'eligible issuer publications',flush=True)

if __name__=='__main__':
    run()
