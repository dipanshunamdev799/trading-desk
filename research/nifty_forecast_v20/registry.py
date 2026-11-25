"""Consolidate earlier evidence with the measured V20 lifetime inventory."""
from .common import *
from .panel import GROUPS

CONTEXT={
 'offshore_gift':('V16–V17','Dated offshore index candles; conservative end-of-bar allowance','V16/V17 opening gap: 248 origins, Brier .100841, accuracy .887097','Instrument rolls, sparse valid pre-auction quotes and a weak link to later cash-session returns','Replicated retrospective association','Verified individual contracts and stable roll mapping'),
 'global_equities':('V5–V17','Dated foreign market equity returns and time-zone release/close allowance','V11 RSP/SPY increment .004731 earlier and −.033262 later versus the US cap/sector parent','Global equity overlap and weak transfer across regimes, with macro/FX potentially distinct','Cohort-dependent','Early session risk and first-print data'),
 'domestic_internals':('V1–V19','Native price, defensive rotation and futures basis known at stated clock','V8 native panel later Brier gain .002208 and V11 native phase-zero .231728 on 265 overlapping weekly origins','Sampling phase and training composition are influential','Cohort-dependent','Open-to-late market synchronization on new dates'),
 'financial_rotation':('V7–V19','Published bank/finance indices and realized sector returns, guarded by release','V8 bank-only later Brier gain .008170 and V9 bank residual later .005741','Performance varied in earlier periods and under shifted-market controls','Cohort-dependent','Real historic index composition and weights'),
 'equal_weight_breadth':('V10–V19','Official NIFTY 50/500 equal-weight relative changes as of the cash decision window','V11 V9 residual .003371 earlier and .004848 later Brier gains','Window and comparator sensitivity, weaker clustered model','Replicated retrospective association','Confirm with a frozen cohort and effective-date stock weights'),
 'stock_participation':('V11–V19','Dated NSE cash archive advance, distribution and lagged activity of eligible stocks','V17 date/ISIN breadth audit and V19 sector/stock controls. V19 monthly delivery-plus-price ranks −.02944','Cross-sectional data add explanatory variables, while independent NIFTY target dates remain fixed','Promising but inconclusive','Date-balanced auxiliary learning and survivorship checks'),
 'corporate_announcements':('V17–V19','NSE filing eligibility clock with late or duplicate episode handling','V18 material and structured corporate residual: native weekly .223481 Brier vs V14 .228529','Rebuilt same-clock ordinary augmentation losses and sensitivity to timing/activity','Promising but inconclusive','Short- and long-lifetime responses and a frozen activity gate'),
 'structured_financials':('V18–V19','First valid firm/period figures and earlier matched filing comparisons','V18 1,063 first firm-period contexts and 870 QoQ revenue comparisons. Ordinary weekly augmentation Brier .248263 at 08:55','Aggregation changes shape, unavailable archived analyst consensus','Failed against strong controls','Firm/industry surprises after point-in-time expectation and revision audit'),
 'participant_futures':('V18–V19','Published NSE category net/gross contracts, next-session 08:15 guard proxy','V19 V14 monthly .245042 to .228199 Brier and .024989 to .024010 CRPS; earlier gain .026437, later −.000954','Correlated category sums, economic state shifts, unstable early/late replication','Cohort-dependent','Late segments, dated expiries and better first-print coverage'),
 'participant_options':('V18–V19','Call and put side aggregates, no usable strike-level participant Greeks','V19 monthly views include disagreement and category options counts, primarily reused through the joint candidate','Option volumes and economically signed delta differ. Expiry and repeated counts overlap','Promising but inconclusive','Confirmed instrument-level exposures and strike date history'),
 'participant_volume':('V19','466 dated NSE participant-volume reports, opposite sides and market shares audited','V19 466 volume days independently audited from OI; conditional V19 risk combined weekly MAE .037158','Volume groups are collinear and anonymous. End-of-day timestamps are modeled','Methodologically established','Increment of executed-volume composition on later dated outcomes'),
 'delivery':('V18–V19','NSE EQ delivered quantities, percentage normalized using earlier issuer history','V19 1,439,636 archive rows. Weekly stock rank −.00318 to +.00300, monthly sector MAE .030702 to .030875','Little effect versus price/turnover, confounded by issuer composition and real free-float weights','Failed against strong controls','Independent future stock controls and historical free float'),
 'large_transactions':('V18–V19','Date/symbol/size/price grouped disclosures and matched two-leg heuristics','V19 2,969 unique legs across 151 dates. Weekly matched block excess .007225 falls to .000637 on size removal','Timing allowance, few bulk matches, hidden counterparties and negotiated size outliers','Failed against strong controls','Release-specific timing and new independent matched event dates'),
 'atm_iv':('V12–V19','Near-money dated option IV and separately measured actual future volatility','V16 raw weekly ATM IV MAE .037814, V16 combined risk .036469','IV timing, term interpolation and variance premium; direction use needs separate evidence','Replicated retrospective association','Fast versus slow horizon volatility and standardized close snapshot'),
 'option_surface':('V12–V19','Authenticated strike surface and previous eligible option-day skew/term observations','V14 native Student-t GJR monthly range .015422 is a strong competing control; V12 risk-neutral and realized path outcomes differ','Settlement flags, thin strikes, roll and price proxy. Q-density differs from realized return laws','Promising but inconclusive','Strict exact-expiry live probe and tail-shape calibration'),
 'realized_volatility':('V12–V19','Past cash realized volatility and causal GARCH conditional variance','V16 monthly GJR MAE .033179 and variance QLIKE .199677; Student EGARCH expansion .172872','Jump episodes can dominate average quality; point/range/barrier require different controls','Replicated retrospective association','Near-expiry and short opening-risk interactions'),
 'intraday_structure':('V8–V19','Guarded earlier realized opening, midpoint, late profiles and separately timed post-open cases','V10 later directional Brier .254052 to .250365. V17 post-open risk snapshots use their own 09:25 and 10:20 windows','Small directional increments, time shifts can match gains and later-case labels differ','Cohort-dependent','Current-session data only after market opens, more complete bar provenance'),
 'institutional_flows':('V18–V20','Provisional exchange net and confirmed custodian/Fund populations have distinct clocks and units','V19 accepted 64 CDSL days, 36 sector fortnights and 22 AMFI months; 59 comparable daily-custody observations','No full official dated exchange FII/DII overlap or ETF creation/redemption series','Unresolved because of insufficient data','First release copies and publication revision history'),
}

OVERLAP={
 'offshore_gift':'The cash mark and overnight return share the cash reference, and the latest proxy can repeat an older eligible quote at 17:00.',
 'global_equities':'Foreign equity composites and regional spreads reuse market returns. VIX can overlap with the risk state.',
 'domestic_internals':'Futures basis and curve share the front contract. Sector dispersion can overlap domestic rotation and breadth.',
 'financial_rotation':'Finance index returns, leadership and its change reuse the same sector moves at different horizons.',
 'equal_weight_breadth':'Short and slow spread windows overlap. Universe overlap can link official equal-weight and stock-level breadth.',
 'stock_participation':'The top-volume seed and broad EQ set overlap. Advance participation shares price information with official breadth.',
 'corporate_announcements':'Counts use nested windows. Earnings and material announcements can be members of the same filing population.',
 'structured_financials':'Growth, profit, surprise and disagreement aggregate overlapping first-report issuer episodes.',
 'participant_futures':'Net index exposures sum across counterparty categories. Slow levels, changes and differences share the same OI archive.',
 'participant_options':'Call and put levels and their changes reuse category totals. Side-level counts overlap in time around expiry.',
 'participant_volume':'Gross-share variables have common market denominators, and stock and option volume are subsets of overall derivative activity.',
 'delivery':'High-delivery and rising-delivery measures share stocks and dates with total intensity, dispersion and concentration.',
 'large_transactions':'Count, size and turnover share reuse the same reported transactions, including negotiated two-leg disclosures.',
 'atm_iv':'ATM IV and VIX share near-money volatility information. Their gap explicitly reuses the IV level.',
 'option_surface':'Skew, term, curve and tail measures reuse parts of the dated strike surface and overlap ATM risk near the money.',
 'realized_volatility':'Market variance, its shock, and short/long ratios reuse rolling cash returns, some split into overnight and regular hours.',
 'intraday_structure':'Jump, first-hour and closing shares reuse earlier cash-bar volatility. Realized intraday and overnight paths jointly feed total risk.',
 'institutional_flows':'The daily and fortnightly custody totals observe related populations on different report calendars. AMFI covers a different investor route.',
}

def run():
    p=csv('asof-features.csv.gz')
    z=csv('information-lifetime-matrix.csv')
    v=z[z.cutoff.eq('preauction_0855')&z.age.eq('fresh')&z['mode'].eq('cumulative')&z.metric.eq('crps')&z.end_offset.isin(HORIZONS)]
    rows=[]
    for family,fields in GROUPS.items():
        era,source,prior,failure,status,question=CONTEXT[family]
        scope={k:int(g.reindex(columns=fields).notna().any(axis=1).sum()) for k,g in p.groupby('cutoff')}
        a=v[v.family.eq(family)].set_index('end_offset')
        s=dict(family=family,earlier_versions=era,defined_fields=', '.join(fields),raw_or_constructed='Observed inputs and named transforms feed a fitted correction',
             source_and_availability=source,known_1700=scope.get('previous_1700',0),known_0855=scope.get('preauction_0855',0),
             archived_matched_evidence=prior,known_failures=failure,redundant=OVERLAP[family],
             classification=status,open_question=question)
        for h in HORIZONS:
            r=a.loc[h]
            s|={f'h{h}_{k}':r[k] for k in ['matched','disjoint','parent','enhanced','gain','earlier_gain','later_gain','gain_vs_lag5','adjusted_low','adjusted_high']}
        rows.append(s)
    write('cumulative-information-registry.csv',pd.DataFrame(rows))
    core=csv('cumulative-hypothesis-registry.csv',V12)
    write('cumulative-v12-predecessor-registry.csv',core)
    save('registry-receipt.json',dict(major_families=len(rows),v12_earlier_inventory=len(core),
      labels=['Methodologically established','Replicated retrospective association','Promising but inconclusive','Cohort-dependent',
        'Failed against strong controls','Unresolved because of insufficient data','Independently validated'],
      independent_validations=0,source_file=(V12/'cumulative-hypothesis-registry.csv').relative_to(ROOT).as_posix(),
      source_sha256=sha(V12/'cumulative-hypothesis-registry.csv')))

if __name__=='__main__':
    run()

