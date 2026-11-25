"""Week-only combined chronology contrasts for identical complete cohorts."""
from .common import *
from research.nifty_forecast_v8.analyze import intervals


def run():
    p=pd.read_csv(OUT/'all-predictions.csv');u=pd.read_csv(OUT/'combined-cohort-leaderboard.csv');x=p[(p.horizon==5)&p.cohort.isin(['early','later'])]
    reference=x[x.model=='P_HIST'].set_index('origin').sort_index();cal=reference.index
    trials=[];desc=[]
    for name in u[(u.horizon==5)&(u.model!='P_HIST')].model:
        g=x[x.model==name].set_index('origin').reindex(cal)
        for score in ['brier','crps']:
            d=reference[score]-g[score];trials.append(d);desc.append({'model':name,'metric':score,'n':len(d),'gain':float(d.mean())})
    for block in [5,10,15]:
        lo,hi,b,c,k=intervals(trials,cal,block)
        for j,r in enumerate(desc):r[f'adjusted95_block{block}']=[float(lo[j]),float(hi[j])]
    save('combined-weekly-uncertainty.json',{'method':'Observed chronological origin order, shared 2,000 block draws, complete-cohort systems against P_HIST. Within-V9 only.',
         'contrasts':len(desc),'rows':desc})
    write('combined-weekly-uncertainty.csv',pd.DataFrame(desc))


if __name__=='__main__':run()
