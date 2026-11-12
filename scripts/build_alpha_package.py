"""Build the phase map, hypothesis/experiment registry and readiness leaderboard."""
import hashlib,json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts'/'project_alpha'


def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False,default=str),encoding='utf-8')


def artifact(name):
    for folder in [OUT,ROOT,ROOT/'artifacts'/'directional_research_phase2',ROOT/'artifacts'/'directional_research']:
        path=folder/name
        if path.exists():return str(path.relative_to(ROOT))
    raise FileNotFoundError(name)


def main():
    definitions=[
      ('H01','Trend continuation','Slow information assimilation/continuing directional flow','Frozen EMA/Donchian/pullback, nextopen/actualreceivedask, fixedtime exits','Same-time30m momentum and randomizedsession direction','Reject incremental claim if conservative net or matched excess lower bounds fail','control-expanded-report.md','NOT_VALIDATED'),
      ('H02','Opening range','Opening information establishes a boundary; crossing may continue','Completed range, immediate/retest variants, timeandcostcontrols','Plain momentum and identical-time opposite direction','Fails if gain relies on one day, disappears atothergranularity or cannotcoveroptioncosts','concept-report.md','NOT_VALIDATED'),
      ('H03','Volatility expansion','Compression may precede faster realized movement','Compression/range-expansion fixedfamilies; compareactualoptionpricewhenavailable','Same-volatility/time price momentum','Falsified for deployment if option already prices movement or laternet uncertain','lab-report.md','NOT_VALIDATED'),
      ('H04','Sweep/reclaim reversals','Rejected breaks may reveal temporary exhaustion','Production47concept sweep/falsebreak/PDH/PDL plus fixedfailedbreak family','Rangefade and matchedmomentum','No edge if delayedconfirmationorcostsconsumepriceeffect','concept-report.md','NOT_VALIDATED'),
      ('H05','Momentum and relative strength','Persistence and correlated constituent information','Price momentum; ETFcontext; smallstockproxy fromearlierstudy. Fullhistoricalbreadth unavailable','Simple30m direction atidenticalentries','Addedcontextmustimprove pairedlaternet beyondcomplexity andcoveragechanges','feature-report.md','PARTIAL_DATA'),
      ('H06','Option expression','Delta/convexity/expiry mayexpress directional information efficiently','DatedATM/ITM/OTM/expiry policies; delta fromasofreceivedproviderGreeks; actualaskbidspread','Sameunderlyingsignal andnaivecontractpolicies','No validatedchoice withoutmultiregime quote/PnL evidence andstablefeesensitivity','exit-stream-delta-v2-report.md','PARTIAL_DATA'),
      ('H07','Positioning','PublicpriorOI/volume mayconditionpricecontinuation/reversal','ExactlypriorNSEsession PCRlevel/change,OIwalls,maxpain,volumePCR; pairedablations','Samecoveredprice-onlyopportunities','Fail if improvedsubsetnet lacksincremental simultaneouslowerbound oronlydropsonesharedloss','positioning-report.md','NO_INCREMENTAL_EVIDENCE'),
      ('H08','Abstention and regimes','Avoidingunfavourablecost/state/execution mayimprove deployability','Causaltrend/range/transition +freshness/depth/lot/clockgates','Ungatedsameopportunities andzeroPnlnotrade','Cannotclaimpredictivevaluefromrejectionalone; requirepairedlaternetandcoverage','timeframe-report.md','RESEARCH_ONLY'),
      ('H09','Exits and protection','Loss/hold rules trade falseexits against tail exposure','Smallfixedstops/targets/trailing/timegrid; eventgaps andmissingexit handling','Frozen60mtimeexit; adverse/favourablepathbounds','Rejectbest-exitclaimfrom5sessionsor guaranteed-stopassumption','exit-report.md','NOT_VALIDATED'),
      ('H10','Capital feasibility','Whole-lotbudgets andkillgates maylimitplannedexposure','Fourcapitals,twofractions,remainingday/weekheadroom,oneposition,cashfunding','Unit-lotunmanagedreference; full-premium shock','Cannotclaimriskcapguaranteedifgap/outage/fullpremiummorethanbudget','risk-metrics-report.md','SCENARIO_ONLY')]
    hypotheses=[{'hypothesis_id':h,'family':family,'mechanism':m,'test_specification':test,'baseline':base,'falsifier':fals,'evidence':artifact(evidence),'decision':decision} for h,family,m,test,base,fals,evidence,decision in definitions]
    dump('hypotheses.json',hypotheses)
    stages=[
      (0,'Existing-system audit','COMPLETED','system-audit.md','Professionaltradebooknotpresent;22.5Mstreamrecordsidentified'),
      (1,'Market research','COMPLETED_WITH_DATA_LIMITS','literature.md','Primarysources;mechanismsfalsifiable; broadhistoricalevent/breadthinformationmissing'),
      (2,'Scientific framework','IMPLEMENTED_WITH_EXECUTION_LIMITS','exit-stream-report.md','Eventengine,asofavailability,gaps,partial/failedfills,hashes;noverifiedexchangebookeventclock'),
      (3,'Competing families','TESTED_OR_DATA_LIMITED','hypotheses.json','Eightfamiliesmapped;15mconfirmationandpriorOIadded;nofamilyvalidated'),
      (4,'Incremental edge','TESTED_NOT_ESTABLISHED','positioning-report.md','Matchedcontrols/pairedablations/multiplicity;conditionalassociationnotcausalproof'),
      (5,'Option selection','EXPLORATORY_ONLY','exit-stream-delta-v2-report.md','ATM/ITM/OTM/expiry/deltacomparisons;3quoteoutcomescannotjustifyoptimization'),
      (6,'Exact entries/exits','RESEARCH_RULES_IMPLEMENTED','rulebook.md','Deterministic12exitpolicies;nochosenvalidatedexit;overnightdisabled'),
      (7,'Regime engine','DIAGNOSTIC_ONLY','timeframe-report.md','Causalstate/realizedfuture-labelconfusion;operationaloutputNO TRADE'),
      (8,'Adversarial validation','TESTED_WITH_UNMET_GATES','exit-verification.json','Walkforward,cost/latency/perturbation,concentration,missingdata,sequenceuncertainty;nonepromoted'),
      (9,'Metrics','COMPLETED_WITH_EVIDENCE_LIMITS','risk-metrics-report.md','PF/winloss/closedDD/duration/months/excursionbounds;realbrokerfillfailure/actualcapitalreturnsunsupported'),
      (10,'Capital protection','SCENARIO_TESTED','risk-feasibility.csv','384scenarios;wholelotsofteninfeasible;stopsnotlossguarantees'),
      (11,'Validated trading skill','CONDITIONAL_NOT_ELIGIBLE','forward-protocol.md','Briefrequiresvalidationfirst;no validatedprimary strategyexists;read-onlydiagnosticengineimplemented'),
      (12,'Research package and decision','DELIVERED_RESEARCH_ONLY','PROJECT_ALPHA_RESULTS.md','No primary/complementary strategy promoted;ledger/config/commands/evidenceincluded')]
    dump('phase-audit.json',[{'phase':i,'name':name,'status':status,'artifact':artifact(art),'finding':finding} for i,name,status,art,finding in stages])
    specs=[
      ('A00','H01', 'System/dataaudit','system-audit.md','extract_alpha_stream.py','stream-inventory.json'),
      ('A01','H07','PriorEODpositioning126summaries','positioning-report.md','research_alpha_positioning.py','positioning-summary.json'),
      ('A02','H09','48exit/contractpoliciesand2pathmodes','exit-report.md','research_alpha_exits.py','exit-summary.json'),
      ('A03','H06','80snapshotconfigs2qualitymodes','exit-stream-report.md','research_alpha_streams.py','exit-stream-summary.json'),
      ('A04','H06','ReceivedGreekavailabilityextension48configs2modes','exit-stream-delta-v2-report.md','extract_alpha_delta.py','exit-stream-delta-v2-summary.json'),
      ('A05','H08','15mconfirmation12summaries','timeframe-report.md','research_alpha_15m.py','timeframe-summary.json'),
      ('A06','H10','48metrics384riskcases','risk-metrics-report.md','research_alpha_metrics.py','metrics-summary.json'),
      ('A07','H08','Failclosedread-onlylivecheck','signal-engine-live-check.json','alpha_signal_engine.py','alpha-config.json'),
      ('A08','H06','1854datedfee/scenariorows','cost-report.md','research_alpha_costs.py','cost-protocol.json')]
    experiments=[]
    for eid,hid,name,report,script,data in specs:
        p=ROOT/'scripts'/script;source=OUT/data
        experiments.append({'experiment_id':eid,'hypothesis_id':hid,'experiment':name,'code_path':str(p.relative_to(ROOT)),'code_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
          'dataset_or_result_path':str(source.relative_to(ROOT)),'dataset_or_result_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'parameter_configuration':'Per-experiment preregistration plus alpha-config.json; all alternatives disclosed',
          'results':artifact(report),'interpretation':'Exploratory on inspectedhistoricaldata; see exactevidenceclass andlimitations',
          'decision':'RESEARCH ONLY','next_action':'Do notretuneonfinalhistory; establishfeasiblefrozenprofile andcollectnewpointintimeobservations'})
    dump('experiment-registry.json',{'date':'2026-11-10','prior_experiment_registries':['artifacts/directional_research/lab-preregister.json','artifacts/directional_research/lab-all-configurations.csv','artifacts/directional_research/daily-all-configurations.csv','artifacts/directional_research_phase2/phase2-manifest.json'],'experiments':experiments})
    ranks=[
      (1,'Frozenafternoontrendrouter','RESEARCH ONLY','Actual3dayask/bidproxy;broaderpriceeffectweak','No simultaneous/incrementalvalidatedpremiumedge','NO TRADE'),
      (2,'Pullback+priormonthPCRcontrarian','RESEARCH ONLY','35priceobservations;ordinarynetCIpositive','Incremental/correctedintervalfails;premiumsampletiny','NO TRADE'),
      (3,'DailyRSImonth-endITM','RESEARCH ONLY','27premiumproxies;net+415lot','CIspanslosses;overnightnotintradayprimaryscope','NO TRADE'),
      (4,'Openingrange+EMA','RESEARCH ONLY','1m51eventspositive','Weak5mtransfer;search/multiplicity;noquotebasedvalidation','NO TRADE'),
      (5,'Donchianstandalonecomplexity','NOT_PROMOTED','Positivegrossrecenttrendweek','Same-time directionduplicates30mmomentum','NO TRADE'),
      (6,'Gapcontinuation/RSIintradayselectedforms','REJECTED_SPECIFICATIONS','Finalmeansweakornegative','No robustnetedge in testedforms','NO TRADE'),
      (7,'Maxpainasdirectionalanchor','REJECTED_SPECIFICATION','Oneyearexpirycontrolstudy+priorOIablations','No unconditionalmagnet/addedvalue established','NO TRADE'),
      (8,'Delta/IVoptimizedtrade','DATA_LIMITED','Freshreceiveddeltacomparisons3outcomes','No stableIV/Greekvintageormultiregimesample','NO TRADE')]
    leaderboard=pd.DataFrame(ranks,columns=['research_priority','candidate','decision','supporting_evidence','limiting_evidence','operational_action']);leaderboard.to_csv(OUT/'strategy-leaderboard.csv',index=False)
    lines=['# Research readiness leaderboard','', 'Priority is information value and evidence readiness, not a ranking of expected trading profits. No primary or complementary strategy is validated. Numeric metrics remain in the original unit-specific panels; index points, rupees and scenario returns are not mixed into a score.','', '|Priority|Candidate|Decision|Evidence|Limitation|Action|','|---:|---|---|---|---|---|']
    for row in ranks:lines.append('|'+ '|'.join(map(str,row))+'|')
    (OUT/'strategy-leaderboard.md').write_text('\n'.join(lines),encoding='utf-8')
    # Normalize IV only in a new metadata artifact; original frozeninputs remain unchanged.
    selected=json.loads((OUT/'stream-selection-delta-v2.json').read_text());iv=[]
    for r in selected:
        if r['status']!='selected':continue
        received=r.get('greeks_source')=='received_provider_stream';raw=r.get('iv')
        iv.append({'strategy':r['strategy'],'entry_at':r['entry_at'],'policy':r['policy'],'instrument_key':r['instrument_key'],
          'iv_raw':raw,'raw_unit':'fraction' if received else 'percent','iv_pct':raw*100 if received and raw is not None else raw,
          'available_at':r.get('greeks_received_at') if received else r.get('chain_observed_at'),
          'independent_iv_calculation_time_verified':False,'iv_used_in_pnl_or_delta_selection':False,
          'warning':'Originalv2iv_atmayinheritchaintimestamp;do not useitforfreshness. This artifact states availability andunits only.'})
    dump('delta-iv-provenance.json',iv)
    print(json.dumps({'hypotheses':len(hypotheses),'phases':len(stages),'experiments':len(experiments),'leaderboard_rows':len(ranks),'iv_metadata_rows':len(iv)}))


if __name__=='__main__':main()
