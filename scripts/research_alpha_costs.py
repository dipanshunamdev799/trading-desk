"""Dated rate-based NSE long-option closing-sale fee sensitivities, not contract notes."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts'/'project_alpha';P2=ROOT/'artifacts'/'directional_research_phase2'


def fees(buy,sell,quantity,day,brokerage_per_order):
    if day<'2024-10-01':raise ValueError('Fee schedule unsupported before October2024')
    if min(buy,sell,quantity)<=0:raise ValueError('Positive premium and quantity required')
    b=buy*quantity;s=sell*quantity;turn=b+s
    exchange_rate=.0003503 if day<'2026-03-01' else .000355299
    ipft_rate=.000005 if day<'2026-03-01' else .000000001
    brokerage=2*brokerage_per_order;exchange=turn*exchange_rate;ipft=turn*ipft_rate;sebi=turn*.000001
    stt=s*(.001 if day<'2026-04-01' else .0015);stamp=b*.00003
    gst=.18*(brokerage+exchange+ipft)
    return {'brokerage':brokerage,'exchange':exchange,'ipft':ipft,'sebi':sebi,'sale_stt':stt,'buy_stamp':stamp,'gst':gst,
        'total_fees_unrounded':brokerage+exchange+ipft+sebi+stt+stamp+gst}


def main():
    protocol={'scenarios_brokerage_per_executed_order':[10,20,30],'orders_per_roundtrip':2,'fees_rounded':False,
        'account_tariff_verified':False,'source_dates':'Rates documented for2024Oct onward; historical client plan/rebates/rounding cannot be recovered.',
        'exchange_plus_ipft_combined':.0003553,'gst_base':'Brokerage+exchange+IPFT per published broker table; excludes SEBI levy',
        'spread':'Included once in snapshot ask/bid; candleprices still have unknownspread and latency. Additional0/2/5premium-point impact sensitivities retained separately.',
        'sources':['https://nsearchives.nseindia.com/content/circulars/FA73061.pdf','https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf','https://upstox.com/brokerage-charges/']}
    (OUT/'cost-protocol.json').write_text(json.dumps(protocol,indent=2))
    sources=[('daily',P2/'option-premium-trades.csv','premium_proxy_observed'),('recent_candle',P2/'option-intraday-trades.csv','observed_candle_proxy'),('recorded_snapshot',OUT/'exit-stream-trades.csv','observed_bid_ask_snapshot_proxy')]
    output=[]
    for source,path,status in sources:
        x=pd.read_csv(path);x=x[x.status==status]
        if source=='recorded_snapshot':x=x[x.execution_mode=='frame_snapshot']
        for r in x.to_dict('records'):
            day=str(r.get('exit_date') or r.get('exit_at'))[:10]
            for broker in [10,20,30]:
                cost=fees(float(r['premium_entry']),float(r['premium_exit']),int(r['lot']),day,broker)
                gross=(r['premium_exit']-r['premium_entry'])*r['lot']
                output.append({'source':source,'configuration':r.get('configuration') or ' / '.join([r['strategy'],r['expiry_bucket'],r['strike_rule']]),
                    'day':day,'brokerage_per_order':broker,'premium_entry':r['premium_entry'],'premium_exit':r['premium_exit'],'lot':r['lot'],
                    'gross_rupees':gross,**cost,'net_rate_based':gross-cost['total_fees_unrounded'],
                    'net_plus2_points':gross-cost['total_fees_unrounded']-2*r['lot'],'net_plus5_points':gross-cost['total_fees_unrounded']-5*r['lot']})
    d=pd.DataFrame(output);d.to_csv(OUT/'cost-trades.csv',index=False)
    g=d.groupby(['source','configuration','brokerage_per_order']).agg(n=('net_rate_based','size'),gross_mean=('gross_rupees','mean'),fees_mean=('total_fees_unrounded','mean'),net_mean=('net_rate_based','mean'),net_plus2_mean=('net_plus2_points','mean'),net_plus5_mean=('net_plus5_points','mean')).reset_index()
    g.to_csv(OUT/'cost-sensitivity.csv',index=False)
    # A change in fee allocation must not accidentally charge IPFT twice.
    a=fees(100,110,65,'2026-02-28',20);b=fees(100,110,65,'2026-03-01',20)
    assert np.isclose(a['exchange']+a['ipft'],b['exchange']+b['ipft'])
    assert np.isclose(fees(100,110,65,'2026-04-01',20)['sale_stt'],110*65*.0015)
    assert np.isclose(fees(100,110,65,'2026-03-31',20)['sale_stt'],110*65*.001)
    assert len(d)==3*(424+62+132)
    lines=['# Rate-based charge sensitivities','',f'{len(d)} trade/scenario rows cover actualdaily premiums,recentoptioncandles andhistoricallyreceivedsnapshots. Three brokerage assumptions(10/20/30INR perexecutedorder) are all disclosed. None is claimed as the recovered client tariff.',
        '', 'The model separates exchange,IPFT,SEBI,saleSTT,buystamp,GSTandbrokerage. It preserves theMarch2026 exchange/IPFT reallocation without doublecounting the oldIPFT. STTchanges on1April2026. GSTuses brokerage+exchange+IPFT perpublishedbroker table. Calculations are unrounded estimates; contract-note rounding,taxaggregation,rebates,partial-ordercharges and actualhistoricaltariff remain unverified.',
        '', 'Ask/bid snapshot returns already include spread. Candle returns still need unknownspread/latency sensitivities. Additional2/5premium-point scenarios do not replace observed spread. None of these fee assumptions creates more independent market observations.',
        '', 'Four numeric rate-transition/count checks passed. Fullpertradecostbreakdown and allconfigurationmeans are retained. [NSE fee circular](https://nsearchives.nseindia.com/content/circulars/FA73061.pdf), [NSE STT](https://nsearchives.nseindia.com/content/circulars/FATAX73524.pdf), [Upstox charges](https://upstox.com/brokerage-charges/).']
    (OUT/'cost-report.md').write_text('\n'.join(lines),encoding='utf-8');print(json.dumps({'trade_scenario_rows':len(d),'groups':len(g),'checks':4}))


if __name__=='__main__':main()
