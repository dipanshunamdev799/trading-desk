"""Causal timing, quote-bound execution and fail-closed V3 observer checks."""
import base64
from dataclasses import replace
from datetime import datetime,timedelta,timezone
import io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

from research.intraday_momentum_v3 import auth,capture,metadata,model,readiness
from research.intraday_momentum_v3.features import normalize,FeatureBuffer,timestamp
from research.intraday_momentum_v3.execution import depth_walk,markout,proposed_size,first_available
from research.intraday_momentum_v3.shadow import hypotheses,HypotheticalLedger,Evaluator
from research.intraday_momentum_v3.universe import Scanner
from research.intraday_momentum_v3 import evaluate

AT=datetime(2026,11,13,5,0,tzinfo=timezone.utc)


def quote(seconds=0,key='a',mid=100.,transport='ws',volume=100000.,bidqty=100000,askqty=100000):
    at=AT+timedelta(seconds=seconds)
    p={'ltpc':{'ltp':mid,'cp':97.,'ltq':100,'ltt':int(at.timestamp()*1000)},
       'marketLevel':{'bidAskQuote':[{'bidP':mid-.01,'bidQ':bidqty,'askP':mid+.01,'askQ':askqty}]},'vtt':volume,'tbq':bidqty,'tsq':askqty}
    return normalize(key,p,at,at,transport='ws') if transport=='ws' else replace(normalize(key,p,at,at),transport='rest')


def candidate(q):
    return dict(side=1,features={'low60':q.mid*.995,'high60':q.mid*1.005,'volume60':100000},
                volume_confirmation=True,depth_confirmation=True,predicted_gross_bps=100)


META={'in_mis':True,'in_suspended':False,'security_type':'NORMAL','stale_history':False}
GATE={'quality_pass':True,'predictor_frozen':True,'account_segments_verified':True,
      'short_execution_verified':False,'execution_uncertainty_bps':1}


class MetadataTests(unittest.TestCase):
    def row(self,kind='EQ',token=10):
        return dict(exchange='NSE',segment='NSE_EQ',instrument_type=kind,exchange_token=token,instrument_key='same-isin')
    def test_same_isin_different_series_is_not_current_suspension(self):
        r=metadata.reconcile([self.row()],[self.row()],[self.row('BE',11)])[0]
        self.assertTrue(r['in_mis']);self.assertFalse(r['in_suspended']);self.assertTrue(r['other_series_suspended'])
    def test_exact_listing_conflict_quarantines(self):
        self.assertEqual(metadata.reconcile([self.row()],[self.row()],[self.row()])[0]['execution_state'],'CONFLICT_QUARANTINE')
    def test_nonordinary_series_excluded(self):
        self.assertEqual(metadata.reconcile([self.row('BE')],[],[]),[])
    def test_token_numbers_and_strings_match(self):
        self.assertTrue(metadata.reconcile([self.row(token=10)],[self.row(token='10')],[])[0]['in_mis'])


class AuthTests(unittest.TestCase):
    def test_only_whitelisted_jwt_metadata_retained(self):
        claims={'iat':1,'exp':9999999999,'user_id':'SECRET-USER','email':'PRIVATE','other':'SECRET'}
        token='x.'+base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')+'.y'
        output=json.dumps(auth.safe_token_metadata(token))
        self.assertNotIn('SECRET',output);self.assertNotIn('PRIVATE',output);self.assertNotIn(token,output)
        self.assertFalse(auth.safe_token_metadata(token)['expired_by_local_clock'])
    def test_opaque_and_expired(self):
        self.assertEqual(auth.safe_token_metadata('opaque')['local_decode'],'OPAQUE_OR_UNDECODABLE')
        token='x.'+base64.urlsafe_b64encode(b'{"exp":1}').decode().rstrip('=')+'.y'
        self.assertTrue(auth.safe_token_metadata(token)['expired_by_local_clock'])


class FeatureTests(unittest.TestCase):
    def test_availability_includes_commit_and_rejects_future(self):
        q=quote();p={'ltpc':{'ltp':1},'marketLevel':{'bidAskQuote':[{'bidP':99,'bidQ':1,'askP':101,'askQ':1}]}}
        delayed=normalize('a',p,AT,AT,committed_at=AT+timedelta(seconds=1))
        self.assertFalse(delayed.fresh(AT));self.assertTrue(delayed.fresh(AT+timedelta(seconds=1)))
        b=FeatureBuffer();b.add(q);before=b.at('a','ws',AT);b.add(quote(1,mid=1000))
        self.assertEqual(before,b.at('a','ws',AT))
    def test_invalid_missing_crossed_and_stale(self):
        self.assertIsNone(normalize('a',{},None,AT));self.assertIsNone(timestamp('2026-11-13'))
        self.assertFalse(replace(quote(),bids=((102,1),),asks=((101,1),)).valid_book)
        self.assertFalse(quote().fresh(AT+timedelta(seconds=3)));self.assertTrue(quote(transport='rest').fresh(AT+timedelta(seconds=3)))
    def test_transport_buffers_do_not_mix(self):
        b=FeatureBuffer();b.add(quote());b.add(quote(transport='rest',mid=200))
        self.assertEqual(b.at('a','ws',AT)['mid'],100);self.assertEqual(b.at('a','rest',AT)['mid'],200)
    def test_exact_duplicates_and_source_reversal_flagged(self):
        b=FeatureBuffer();self.assertEqual(b.add(quote()),'accepted');self.assertEqual(b.add(quote()),'duplicate_source_payload')
        self.assertEqual(b.add(replace(quote(1),source_at=AT-timedelta(seconds=1))),'out_of_order_source')
    def test_burst_does_not_overweight_persistent_support(self):
        b=FeatureBuffer()
        for i in range(10):b.add(quote(i,bidqty=300,askqty=100))
        for i in range(1,50):b.add(quote(9+i/100,bidqty=100,askqty=300))
        f=b.at('a','ws',AT+timedelta(seconds=9.49))
        self.assertEqual(f['support_seconds10'],10);self.assertAlmostEqual(f['support_up_fraction'],.9)
    def test_volume_is_cumulative_difference_not_ltq_sum(self):
        b=FeatureBuffer()
        for i in range(361):b.add(quote(i,volume=100000+10*i,mid=100+i/10000))
        f=b.at('a','ws',AT+timedelta(seconds=360))
        self.assertEqual(f['volume60'],600);self.assertAlmostEqual(f['volume_acceleration'],1)
    def test_counter_reset_is_not_negative_traded_volume(self):
        b=FeatureBuffer();b.add(quote(0,volume=1000));b.add(quote(60,volume=10))
        self.assertIsNone(b.at('a','ws',AT+timedelta(seconds=60))['volume60'])


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.plan={'stocks':[dict(key=str(i),continuous_full=i<20) for i in range(60)],'controls':[str(i) for i in range(20)],'full_max':40}
    def test_budget_and_fixed_controls(self):
        s=Scanner(self.plan)
        for i in range(60):s.update(quote(key=str(i),mid=100+i))
        event=s.select(AT);self.assertEqual(len(event['full_keys']),40);self.assertTrue(set(self.plan['controls'])<=s.watch)
    def test_future_prefix_does_not_change_selection(self):
        s=Scanner(self.plan);s.update(quote(key='25'));before=s.select(AT)['full_keys'];s.update(quote(1,key='26',mid=1000))
        self.assertEqual(before,s.select(AT)['full_keys'])
    def test_old_source_cannot_roll_scanner_back(self):
        s=Scanner(self.plan);s.update(quote(1,key='25',mid=110));s.update(replace(quote(2,key='25'),source_at=AT))
        self.assertEqual(s.latest['25'].last,110)


class ExecutionTests(unittest.TestCase):
    def test_partial_depth_does_not_invent_full_fill(self):
        r=depth_walk(((100,100),),20);self.assertEqual(r['modeled_available'],10);self.assertEqual(r['unfilled'],10);self.assertTrue(r['not_a_fill'])
    def test_spread_embedded_once_and_fees_applied(self):
        q=quote();r=markout(q,q,1,100,extra_bps=0)
        self.assertAlmostEqual(r['net_pnl'],-2-r['fees']);self.assertTrue(r['spread_already_embedded'])
    def test_zero_and_negative_size_rejected(self):
        for quantity in (0,-1):
            with self.assertRaises(ValueError):depth_walk(((100,100),),quantity)
    def test_account_guard_and_past_volume_guard(self):
        q=quote()
        self.assertEqual(proposed_size(q,1,1e6,5000,.005,10000,True,False)['reason'],'account_segment_unverified')
        self.assertFalse(proposed_size(q,1,1e6,5000,.005,None,True,True)['accepted'])
    def test_sizing_respects_whole_shares_cash_and_depth(self):
        r=proposed_size(quote(),1,10000,100,.005,100000,True,True)
        self.assertTrue(r['accepted']);self.assertIsInstance(r['quantity'],int);self.assertLess(r['entry_bound']*r['quantity'],10000)
    def test_first_next_quote_not_best_future_price(self):
        qs=[quote(1,mid=101),quote(2,mid=99)]
        self.assertEqual(first_available(qs,AT+timedelta(seconds=1),'ws').mid,101)
    def test_transport_markouts_incomparable(self):
        self.assertEqual(markout(quote(),quote(transport='rest'),1,1)['status'],'INCOMPARABLE')


class MarketTests(unittest.TestCase):
    def status(self):return {'last_updated':AT.isoformat(),'status':'NORMAL_OPEN'}
    def timings(self):return [{'exchange':'NSE','start_time':(AT-timedelta(hours=1)).isoformat(),'end_time':(AT+timedelta(hours=1)).isoformat()}]
    def test_open_requires_both_status_and_window(self):
        self.assertTrue(capture.market_window(self.status(),self.timings(),AT)[0])
        self.assertFalse(capture.market_window({**self.status(),'status':'CLOSED'},self.timings(),AT)[0])
        self.assertFalse(capture.market_window(self.status(),[],AT)[0])
    def test_prior_date_and_future_status_rejected(self):
        for delta in (-86400,2):
            self.assertFalse(capture.market_window({**self.status(),'last_updated':(AT+timedelta(seconds=delta)).isoformat()},self.timings(),AT)[0])
    def test_2027_hard_scope_guard(self):
        self.assertEqual(capture.market_window({},[],AT.replace(year=2027))[1],'2027_REQUIRES_EXPLICIT_APPROVAL')
    def test_one_owned_recorder_lock(self):
        with tempfile.TemporaryDirectory() as d,patch.object(capture,'OUT',Path(d)):
            with capture.RunLock():
                with self.assertRaises((RuntimeError,OSError)):
                    with capture.RunLock():pass
            with capture.RunLock():pass
    def test_invalid_book_interrupts_asof_coverage(self):
        start=AT.replace(hour=3,minute=45).timestamp()
        r=[dict(source=start,received=start,available=start,valid=True),dict(source=start+.5,received=start+.5,available=start+.5,valid=False)]
        self.assertAlmostEqual(readiness.covered_grid(r,'2026-11-13','ws'),1/21300)


class LedgerTests(unittest.TestCase):
    def test_restart_preserves_capital_entry_count_and_pending_clock(self):
        q=quote();l=HypotheticalLedger(GATE);l.candidate(candidate(q),q,META);l.observe(quote(1))
        saved=json.loads(json.dumps(l.state(),default=str));r=HypotheticalLedger(GATE);r.restore(saved)
        self.assertEqual(r.count,1);self.assertEqual(r.used,{'a'});self.assertEqual(r.position['entry_quote'],l.position['entry_quote'])
        self.assertEqual(r.candidate(candidate(q),quote(2),META)['status'],'REJECTED_CAPITAL_BUSY')
    def test_restart_cannot_reset_daily_three_entry_cap(self):
        l=HypotheticalLedger(GATE);l.day=AT.astimezone(capture.IST).date().isoformat();l.count=3;l.equity=l.opening=987654
        r=HypotheticalLedger(GATE);r.restore(json.loads(json.dumps(l.state(),default=str)))
        self.assertEqual(r.equity,987654);self.assertEqual(r.candidate(candidate(quote()),quote(),META)['status'],'REJECTED_THREE_ENTRY_CAP')
    def test_missing_quality_model_or_confirmation_reject(self):
        q=quote()
        self.assertEqual(HypotheticalLedger().candidate(candidate(q),q,META)['status'],'REJECTED_QUALITY_GATE')
        self.assertEqual(HypotheticalLedger({'quality_pass':True}).candidate(candidate(q),q,META)['status'],'REJECTED_PREDICTOR_NOT_FROZEN')
        self.assertEqual(HypotheticalLedger(GATE).candidate({**candidate(q),'depth_confirmation':False},q,META)['status'],'REJECTED_CONFIRMATION_NOT_MET')
    def test_rest_never_inherits_ws_qualification(self):
        q=quote(transport='rest');self.assertEqual(HypotheticalLedger(GATE).candidate(candidate(q),q,META)['status'],'REJECTED_TRANSPORT_NOT_QUALIFIED')
    def test_observed_entry_requires_next_quote_and_cash_guard(self):
        q=quote();l=HypotheticalLedger(GATE);self.assertEqual(l.candidate(candidate(q),q,META)['status'],'HYPOTHETICAL_PENDING_NEXT_QUOTE')
        self.assertEqual(l.observe(q),[]);self.assertIsNone(l.position)
        self.assertEqual(l.observe(quote(1))[0]['status'],'HYPOTHETICAL_OPENED');self.assertEqual(l.count,1)
        self.assertEqual(l.candidate(candidate(q),quote(1),META)['status'],'REJECTED_CAPITAL_BUSY')
    def test_quote_after_latency_gap_is_unfilled(self):
        q=quote();l=HypotheticalLedger(GATE);l.candidate(candidate(q),q,META)
        self.assertEqual(l.observe(quote(3))[0]['status'],'HYPOTHETICAL_UNFILLED_LATENCY_GAP');self.assertEqual(l.count,0)
    def test_partial_next_quote_is_unfilled(self):
        q=quote();l=HypotheticalLedger(GATE);l.candidate(candidate(q),q,META)
        self.assertEqual(l.observe(quote(1,askqty=1))[0]['status'],'HYPOTHETICAL_UNFILLED_PARTIAL_DEPTH')
    def test_daily_entry_cap_and_no_reentry(self):
        q=quote();l=HypotheticalLedger(GATE);l.day=AT.astimezone(capture.IST).date().isoformat();l.count=3
        self.assertEqual(l.candidate(candidate(q),q,META)['status'],'REJECTED_THREE_ENTRY_CAP')
        l.count=0;l.used.add('a');self.assertEqual(l.candidate(candidate(q),q,META)['status'],'REJECTED_SAME_SYMBOL_REENTRY')
    def test_unknown_short_execution_rejects(self):
        q=quote();l=HypotheticalLedger(GATE);self.assertEqual(l.candidate({**candidate(q),'side':-1},q,META)['status'],'REJECTED_ACCOUNT_SEGMENT_UNVERIFIED')
    def test_partial_exit_reserves_capital(self):
        q=quote();l=HypotheticalLedger(GATE);l.candidate(candidate(q),q,META);l.observe(quote(1))
        self.assertEqual(l.observe(quote(2,mid=98,bidqty=1))[0]['status'],'UNRESOLVED_EXIT_CAPITAL_RESERVED')
        self.assertIsNotNone(l.position);self.assertTrue(l.halted)
    def test_actual_decision_clock_drives_entry_latency(self):
        q=quote();l=HypotheticalLedger(GATE);l.candidate(candidate(q),q,META,AT+timedelta(seconds=.5))
        self.assertEqual(l.observe(quote(1)),[]);self.assertIsNone(l.position)
        self.assertEqual(l.observe(quote(1.5))[0]['status'],'HYPOTHETICAL_OPENED')
    def test_thesis_exit_requires_later_quote(self):
        q=quote();l=HypotheticalLedger(GATE);l.candidate(candidate(q),q,META);l.observe(quote(1))
        f={'key':'a','imbalance_mean10':-.2,'mid':99.9};l.thesis(f,AT+timedelta(seconds=2));l.thesis(f,AT+timedelta(seconds=5))
        self.assertTrue(l.position.get('failure_exit_requested'));self.assertEqual(next(r for r in l.observe(quote(6,mid=99.9)) if r['status']=='HYPOTHETICAL_CLOSED')['reason'],'THESIS_FAILURE')


class ModelAndHypothesisTests(unittest.TestCase):
    def test_future_assessment_cannot_qualify_without_sessions(self):
        with tempfile.TemporaryDirectory() as d,patch.object(evaluate,'OUT',Path(d)),patch.object(evaluate,'load',return_value=None):
            (Path(d)/'forward-readiness.json').write_text('{"sessions":[]}');r=evaluate.assess()
            self.assertFalse(r['profitability_demonstrated']);self.assertEqual(r['status'],'FORWARD_DATA_REQUIRED')
    def test_day_resampling_requires_sessions_and_is_deterministic(self):
        self.assertIsNone(evaluate.day_bound([1]*29));a=evaluate.day_bound([1]*30)
        self.assertEqual(a,evaluate.day_bound([1]*30));self.assertEqual(a['lower_one_sided_98_75'],1)
    def test_training_calibration_requires_frozen_model(self):
        with tempfile.TemporaryDirectory() as d,patch.object(model,'OUT',Path(d)),patch.object(model,'load',return_value=None):
            model.calibration();self.assertEqual(json.loads((Path(d)/'calibration-status.json').read_text())['status'],'FORWARD_DATA_REQUIRED')
    def test_only_three_families(self):
        f=dict(return60_bps=30,return300_bps=100,daily_return=.03,volume_acceleration=3,spread_bps=2,
               support_up_fraction=1,support_seconds10=9,imbalance_mean10=.5)
        self.assertEqual([x['family'] for x in hypotheses(f)],['H3-A'])
        f.update(prior_high300=99,mid_min3=100,observed_seconds3=3,median_spread60=2)
        self.assertIn('H3-B',[x['family'] for x in hypotheses(f)])
        f.update(return60_bps=-30,spread_bps=5,imbalance_mean10=-.5)
        self.assertIn('H3-C',[x['family'] for x in hypotheses(f)])
    def test_signed_predictors_align_with_candidate_direction(self):
        f={'return60_bps':-20,'imbalance5':-.4,'bid_depth5':100,'ask_depth5':200}
        r=model.oriented(f,-1);self.assertEqual(r['return60_bps'],20);self.assertEqual(r['bid_depth5'],200);self.assertEqual(f['return60_bps'],-20)
    def test_train_date_and_scope_are_not_evaluation(self):
        m={'training_end':'2026-11-13','models':{}}
        self.assertEqual(model.predict(m,'H3-A',{},AT),{});self.assertEqual(model.predict(m,'H3-A',{},AT.replace(year=2027)),{})
    def test_no_models_created_without_sessions(self):
        with tempfile.TemporaryDirectory() as d,patch.object(model,'OUT',Path(d)),patch('sys.stdout',new_callable=io.StringIO):
            (Path(d)/'forward-readiness.json').write_text('{"sessions":[]}');model.fit()
            r=json.loads((Path(d)/'model-status.json').read_text());self.assertEqual(r['models_trained'],0);self.assertFalse((Path(d)/'frozen-forward-model.json').exists())
    def test_late_endpoint_censored_not_optimized(self):
        events=[];e=Evaluator({'stocks':[]},events.append);q=quote()
        e.pending[('a','ws')]=[dict(id='event',due=AT,horizon=900,entry_mid=100,entry_quote=q,side=1,quantity=10)]
        e.observe(quote(3));self.assertEqual(events[0]['status'],'CENSORED_ENDPOINT')
    def test_shutdown_keeps_future_labels_pending(self):
        events=[];e=Evaluator({'stocks':[]},events.append);e.pending[('a','ws')]=[dict(id='event',due=datetime.now(timezone.utc)+timedelta(days=1),horizon=900)]
        e.close();self.assertEqual(events[0]['status'],'PENDING_UNCOLLECTED_FUTURE')


if __name__=='__main__':unittest.main()
