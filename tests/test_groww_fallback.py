import base64,json,unittest
from unittest.mock import Mock
from research.groww_fallback.probe import DataProbe,token_metadata


class GrowwProbeTests(unittest.TestCase):
    def test_jwt_subject_and_token_are_never_reported(self):
        p=base64.urlsafe_b64encode(b'{"exp":9999999999,"sub":"PRIVATE-ACCOUNT"}').decode().rstrip('=');token='x.'+p+'.y'
        result=json.dumps(token_metadata(token));self.assertNotIn('PRIVATE',result);self.assertNotIn(token,result);self.assertIn('expiry_ist',result)
    def test_order_routes_are_rejected_before_network(self):
        s=Mock();s.headers={};p=DataProbe('test',s)
        for route in ('/v1/order/create','https://other.example/','/v1/user/profile'):
            with self.assertRaises(ValueError):p.check(route,{})
        s.get.assert_not_called()
    def test_server_secrets_and_redirects_not_exposed(self):
        s=Mock();s.headers={};r=s.get.return_value;r.status_code=403;r.json.return_value={'status':'FAILURE','error':{'message':'SECRET-TOKEN'},'account':'PRIVATE'}
        result=DataProbe('test',s).check('/v1/live-data/quote',{})
        self.assertNotIn('SECRET',json.dumps(result));self.assertNotIn('PRIVATE',json.dumps(result));self.assertFalse(result['accepted'])
        self.assertFalse(s.get.call_args.kwargs['allow_redirects'])
    def test_success_reports_only_market_capabilities(self):
        s=Mock();s.headers={};r=s.get.return_value;r.status_code=200;r.json.return_value={'status':'SUCCESS','payload':{'depth':{'buy':[{}]*5,'sell':[{}]*5},'volume':100,'last_trade_time':123}}
        result=DataProbe('test',s).check('/v1/live-data/quote',{})
        self.assertTrue(result['accepted']);self.assertEqual(result['bid_levels'],5);self.assertTrue(result['has_volume']);self.assertFalse(result['has_quote_timestamp'])
    def test_opaque_missing_and_prefixed_tokens(self):
        self.assertIsNone(token_metadata('opaque')['expiry_ist'])
        for token in ('','Bearer test',' test'):
            with self.assertRaises(ValueError):DataProbe(token)


if __name__=='__main__':unittest.main()
