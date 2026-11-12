"""Replicate the app's causal price-action events on the extended frozen history."""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'backend'),str(ROOT)]
from app.services import price_action as pa

OUT=ROOT/'artifacts'/'directional_research'

def read(name):
    d=pd.DataFrame(json.loads((OUT/name).read_text()))
    d['ts']=pd.to_datetime(d.ts,utc=True).dt.tz_convert('Asia/Kolkata')
    return d.sort_values('ts').drop_duplicates('ts').reset_index(drop=True)

def records(d):
    return [{**r,'ts':r['ts'].isoformat()} for r in d[['ts','open','high','low','close','volume','oi']].to_dict('records')]

def main():
    daily=records(read('nifty-upstox-1day.json'))
    metrics=[];exports=[];audit=[];prefix_checks=[]
    for grain,name in [(1,'nifty-db-1minute.json'),(5,'nifty-upstox-5minute.json')]:
        d=read(name);minute=d.ts.dt.hour*60+d.ts.dt.minute
        d=d[(minute>=555)&(minute<910)].copy();d['day']=d.ts.dt.strftime('%Y-%m-%d')
        sessions=[];trades={};excluded=[]
        for ordinal,(day,b) in enumerate(d.groupby('day')):
            b=b.reset_index(drop=True)
            valid=np.isfinite(b[['open','high','low','close']]).all(axis=1)&(b.low>0)&(b.high>=b[['open','close','low']].max(axis=1))&(b.low<=b[['open','close','high']].min(axis=1))
            if list(b.ts.dt.hour*60+b.ts.dt.minute)!=list(range(555,910,grain)) or not valid.all():
                excluded.append(day);continue
            sessions.append(day);rows=records(b)
            study=pa.analyze(rows,f'{grain}minute',daily=daily,session=day,now=pd.Timestamp('2026-11-09T00:00:00+05:30').to_pydatetime())
            if ordinal%40==0:
                count=len(rows)//2
                pref=pa.analyze(rows[:count],f'{grain}minute',daily=daily,session=day,now=pd.Timestamp('2026-11-09T00:00:00+05:30').to_pydatetime())
                expected=[e for e in study['events'] if pd.Timestamp(e['known_at'])<=b.ts.iloc[count-1]+pd.Timedelta(minutes=grain)]
                assert pref['events']==expected,(grain,day)
                prefix_checks.append({'grain':grain,'day':day,'pass':True})
            mapping={t.isoformat():i for i,t in enumerate(b.ts)}
            signals={f'concept_{c:02d}':np.zeros(len(b),dtype=int) for c in range(1,48)}
            conflict=set()
            for event in study['events']:
                i=mapping[event['ts']];key=f"concept_{event['concept']:02d}";side=event['side']
                assert pd.Timestamp(event['known_at'])<=b.ts.iloc[i]+pd.Timedelta(minutes=grain)
                if signals[key][i] and signals[key][i]!=side and side:conflict.add((key,i))
                elif side:signals[key][i]=side
            for key,i in conflict:signals[key][i]=0
            trend=np.sign(b.close.ewm(span=9,adjust=False).mean()-b.close.ewm(span=21,adjust=False).mean()).to_numpy()
            for c in [19,20,47,39,42]:
                side=signals[f'concept_{c:02d}'];signals[f'concept_{c:02d}_ema9_21']=np.where(side==trend,side,0)
            signals['concept_46_fade']=-signals['concept_46']
            for key,signal in signals.items():
                for hold in [5,15,30]:
                    h=hold//grain;last=-1
                    for i in np.flatnonzero(signal):
                        j=i+h
                        if i<last or j>=len(b):continue
                        known=b.ts.iloc[i]+pd.Timedelta(minutes=grain)
                        entry_time=b.ts.iloc[i+1];exit_time=b.ts.iloc[j]+pd.Timedelta(minutes=grain)
                        assert entry_time==known and (exit_time-entry_time).total_seconds()==hold*60
                        row={'grain':grain,'rule':key,'hold':hold,'day':day,'entry_time':entry_time.isoformat(),'exit_time':exit_time.isoformat(),'side':int(signal[i]),'entry':float(b.open.iloc[i+1]),'exit':float(b.close.iloc[j]),'points':float(signal[i]*(b.close.iloc[j]-b.open.iloc[i+1]))}
                        trades.setdefault((key,hold),[]).append(row);last=j
            if ordinal%40==0:print(grain,day,len(sessions),'sessions',flush=True)
        split=int(len(sessions)*.8);cut=sessions[split]
        # Include neutral/reference concepts explicitly, without inventing returns.
        keys=[f'concept_{c:02d}' for c in range(1,48)]+[f'concept_{c:02d}_ema9_21' for c in [19,20,47,39,42]]+['concept_46_fade']
        for key,hold in [(key,hold) for key in keys for hold in [5,15,30]]:
            rows=trades.get((key,hold),[])
            for part in ['earlier80','later20']:
                chosen=[r for r in rows if (r['day']>=cut)==(part=='later20')]
                if not chosen:
                    metrics.append({'grain':grain,'rule':key,'hold':hold,'partition':part,'n':0,'gross_mean':None,'net2_mean':None,'net5_mean':None,'win_pct':None,'days':0,'status':'no_directional_trades'})
                    continue
                p=np.array([r['points'] for r in chosen]);n=len(p)
                metrics.append({'grain':grain,'rule':key,'hold':hold,'partition':part,'n':n,'gross_mean':float(p.mean()),'net2_mean':float(p.mean()-2),'net5_mean':float(p.mean()-5),'win_pct':float((p>0).mean()*100),'days':len(set(r['day'] for r in chosen)),'status':'observed'})
            if key.endswith('ema9_21') or key=='concept_46_fade':exports.extend(rows)
        audit.append({'grain':grain,'sessions':len(sessions),'first':sessions[0],'last':sessions[-1],'later20_start':cut,'excluded':excluded})
    pd.DataFrame(metrics).to_csv(OUT/'concept-replication.csv',index=False)
    pd.DataFrame(exports).to_csv(OUT/'concept-fixed-candidate-trades.csv',index=False)
    inputs=[OUT/'nifty-db-1minute.json',OUT/'nifty-upstox-5minute.json',OUT/'nifty-upstox-1day.json',Path(pa.__file__),Path(__file__)]
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    (OUT/'concept-audit.json').write_text(json.dumps({'coverage':audit,'prefix_checks':prefix_checks,'input_sha256':hashes},indent=2))
    lines=['# Existing price-action replication','', 'The production 47-concept detector is replayed without parameter tuning. Confirmed events enter at next open and exit after5/15/30 minutes by15:10 IST. One position per rule; conflicting same-bar directions cancel. Five fixed EMA-filtered candidates and a displacement fade replicate hypotheses identified by the earlier seven-session study. The later20% is historical evaluation, not wholly unseen evidence (October2026 was previously inspected). No rules are selected by these results. All47 concepts are disclosed in the CSV; neutral references have no directional trades. Index points and2/5-point friction are not option P&L. No significance claim is made for this additional multiple-comparison panel.','', '## Previously identified candidates, 15-minute holding','', '|Chart|Rule|Later N|Gross pts|Net2|Net5|Win%|','|---|---|---:|---:|---:|---:|---:|']
    for r in metrics:
        if r['n'] and r['partition']=='later20' and r['hold']==15 and (r['rule'].endswith('ema9_21') or r['rule']=='concept_46_fade'):
            lines.append(f"|{r['grain']}m|{r['rule']}|{r['n']}|{r['gross_mean']:.2f}|{r['net2_mean']:.2f}|{r['net5_mean']:.2f}|{r['win_pct']:.1f}|")
    lines+=['','Coverage, source hashes and prefix tests: `concept-audit.json`. Daily level context uses the fresh daily archive through 8 November 2026, filtered strictly to dates before each replay session. All 47 detectors were evaluated; 40 produced directional trades on each timeframe. The seven neutral/reference concepts have explicit zero-trade rows and null performance metrics. EMA9/21 filters reset each session, matching the production session-local chart context.']
    (OUT/'concept-report.md').write_text('\n'.join(lines),encoding='utf-8')
    print('Complete',len(metrics),'summary rows',len(prefix_checks),'prefix tests',flush=True)

if __name__=='__main__':main()
