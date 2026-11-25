"""Same-contract cash/futures spreads, roll measures and a priced risk proxy."""
from .common import *
from .experiments import cfg,run
from .features import cached


def num(row,key):
    return float(row.get(key) or 0.)


def expiry(row):
    return row['FininstrmActlXpryDt'] or row['XpryDt']


def market():
    official=pd.read_csv(OUT/'native-equal-weight-closes.csv').set_index('day').sort_index().cap50
    quotes=[];sources={};prior={};previous_day=None
    for path in sorted((V5/'sources/fo').glob('*.json')):
        doc=json.loads(path.read_text(encoding='utf-8'));day=doc['day']
        if not doc['ok'] or day not in official.index:continue
        sources[str(path.relative_to(ROOT))]=sha(path)
        raw=doc['rows'];futures=sorted([q for q in raw if q['FinInstrmTp']=='IDF' and expiry(q)>day and num(q,'ClsPric')>0],key=expiry)
        if len(futures)<2:continue
        f,nxt=futures[:2];spot=official.loc[day];dte=(pd.Timestamp(expiry(f))-pd.Timestamp(day)).days
        log_basis=np.log(num(f,'ClsPric')/spot);distance=(pd.Timestamp(expiry(nxt))-pd.Timestamp(expiry(f))).days
        active={(q['FinInstrmId'],q['NewBrdLotQty']):q for q in futures};key=(f['FinInstrmId'],f['NewBrdLotQty'])
        row={'day':day,'net_carry_30d':log_basis*30/max(5,dte),
             'curve_30d':np.log(num(nxt,'ClsPric')/num(f,'ClsPric'))*30/max(5,distance),
             'near_oi_concentration':num(f,'OpnIntrst')/max(1,sum(num(q,'OpnIntrst') for q in futures)),
             'next_volume_share':num(nxt,'TtlTradgVol')/max(1,sum(num(q,'TtlTradgVol') for q in futures)),
             'front_id':str(f['FinInstrmId']),'front_expiry':expiry(f),'next_expiry':expiry(nxt)}
        if previous_day is not None and official.index.get_loc(day)-official.index.get_loc(previous_day)==1 and key in prior:
            row['same_contract_excess_log_return']=np.log(num(f,'ClsPric')/num(prior[key],'ClsPric'))-np.log(spot/official.loc[previous_day])
            row['oi_change_over_volume']=(num(f,'OpnIntrst')-num(prior[key],'OpnIntrst'))/max(1,num(f,'TtlTradgVol')*num(f,'NewBrdLotQty'))
            nxtkey=(nxt['FinInstrmId'],nxt['NewBrdLotQty'])
            if nxtkey in prior:
                prev_share=num(prior[nxtkey],'OpnIntrst')/max(1,num(prior[key],'OpnIntrst')+num(prior[nxtkey],'OpnIntrst'))
                row['roll_open_interest_shift']=num(nxt,'OpnIntrst')/max(1,num(f,'OpnIntrst')+num(nxt,'OpnIntrst'))-prev_share
        # The same-expiry call and put must both have traded on that date.
        legs={}
        for o in raw:
            if o['OptnTp'] not in ['CE','PE'] or expiry(o)<=day:continue
            tenor=(pd.Timestamp(expiry(o))-pd.Timestamp(day)).days
            if 7<=tenor<=42 and num(o,'TtlTradgVol')>0 and num(o,'ClsPric')>0:
                legs.setdefault((tenor,num(o,'StrkPric')),{})[o['OptnTp']]=num(o,'ClsPric')
        valid=[(tenor,strike) for (tenor,strike),options in legs.items()
               if len(options)==2 and abs(strike/spot-1)<.015]
        if valid:
            tenor,strike=min(valid,key=lambda q:(abs(q[0]-21),abs(q[1]-spot)))
            prices=legs[tenor,strike];row['straddle_21day_scale']=sum(prices.values())/spot*np.sqrt(21/tenor)
            row['straddle_days']=tenor;row['straddle_strike']=strike
        previous_day=day;prior=active;quotes.append(row)
    data=pd.DataFrame(quotes).set_index('day').sort_index()
    data['front_roll']=data.front_id.ne(data.front_id.shift()).astype(float)
    data['net_carry_innovation']=data.net_carry_30d-data.net_carry_30d.rolling(42,min_periods=20).median().shift()
    write('dated-derivatives-inputs.csv',data,index=True)
    save('dated-derivatives-audit.json',{'sources':sources,'rows_with_two_futures':len(data),
          'field_counts':data.notna().sum().to_dict(),'detected_expiry_changes':int(data.front_roll.sum()-1),
          'boundary':'Official end-of-day fields lagged one observed NSE session. OI changes are matched by instrument ID and lot, with turnover in underlying units.',
          'options':'Matched traded near-ATM straddle premium scaled to 21 calendar days, a priced-risk proxy. Omitted an implied distribution or realized probability.',
          'carry':'Uses contract maturity and curve, with seasonally changing net carry corrected with a trailing median. An authenticated INR funding/dividend decomposition is unavailable.'})
    return data.reindex(official.index).shift()


def evaluate():
    d=market();x,_,_=cached();core=x['ten']
    groups={
      'DATED_FUTURES':['same_contract_excess_log_return','oi_change_over_volume','roll_open_interest_shift','near_oi_concentration',
                       'next_volume_share','front_roll','net_carry_innovation','curve_30d'],
      'DATED_STRADDLE':['straddle_21day_scale'],
    }
    frames={name:core.join(d[fields]) for name,fields in groups.items()}
    mask={name:d[fields].notna().any(axis=1).reindex(core.index).fillna(False) for name,fields in groups.items()}
    specs={}
    for name in groups:
        p=name+'_PARENT';specs[p]=cfg(eligible=name,parent='BASE10',hypothesis='Exact dated derivative eligibility control')
        specs[name]=cfg(name,p,eligible=name,hypothesis='One observed-session delayed derivative information with dated contract and expiry matching')
    run('datedderivatives',specs,custom=(frames,mask))


if __name__=='__main__':evaluate()
