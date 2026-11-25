"""Presentation-only rendering of existing, frozen descriptive quality results."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from research.intraday_momentum_v3.common import OUT,dump,sha


def main():
    rows=sorted(json.loads((OUT/'detailed-quality.json').read_text())['results'],key=lambda r:r['fresh_valid_grid_fraction'])
    names={r['key']:r['symbol'] for r in json.loads((OUT/'metadata-reconciliation.json').read_text())}
    labels=[names.get(r['key'],r['key'])+' / '+r['day'][5:] for r in rows];values=[100*r['fresh_valid_grid_fraction'] for r in rows]
    fig,ax=plt.subplots(figsize=(10,7));fig.subplots_adjust(left=.23,right=.96,top=.86,bottom=.12)
    fig.suptitle('Retained quote continuity is uneven',x=.23,y=.97,ha='left',fontsize=16)
    fig.text(.23,.925,'16 prespecified stock-days; one-second grid, 09:15-15:10 IST',fontsize=10,color='#4c5864')
    fig.text(.23,.898,'Two-second freshness; descriptive archive evidence, not prospective validation',fontsize=9,color='#4c5864')
    ax.barh(labels,values,color=['#207f78' if x>=95 else '#718499' for x in values],height=.72)
    ax.axvline(95,color='#b15c28',ls='--',lw=1.2)
    for i,value in enumerate(values):ax.text(value+.5,i,f'{value:.1f}%',va='center',fontsize=8)
    ax.set(xlim=(0,104),xlabel='Fresh valid quote coverage (%)');ax.spines[['top','right']].set_visible(False)
    fig.text(.23,.035,'Dashed line: proposed forward-control coverage threshold of 95%',fontsize=9,color='#80522f')
    fig.savefig(OUT/'archive-quality.png',dpi=170);plt.close(fig)
    dump(OUT/'figure-provenance.json',dict(source=str(Path(__file__).resolve()),source_sha256=sha(Path(__file__)),
        data_sha256=sha(OUT/'detailed-quality.json'),figure_sha256=sha(OUT/'archive-quality.png'),presentation_only=True))


if __name__=='__main__':main()
