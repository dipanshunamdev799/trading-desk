"""Pure/local fixtures only: no shared database changes."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
import zipfile
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from investment_bots.community_auction import gate_status,load_archive,number,observation
from investment_bots.reference import xsim


class AuctionTests(unittest.TestCase):
    def test_final_observation_never_passes_strict(self):
        ob=observation('ABC',100,10000,'01-Jul-2026 09:04:30',0,0)
        self.assertEqual(gate_status(ob,10,100,'strict'),'unverified_decision_capture')

    def test_proxy_missing_and_size_and_imbalance(self):
        ob=observation('ABC',100,1000,None,30,30)
        self.assertEqual(gate_status(None,1,100,'volume_proxy'),'missing_observation')
        self.assertEqual(gate_status(ob,100,100,'zero_imbalance_proxy'),'proxy_pass')
        self.assertEqual(gate_status(ob,101,100,'zero_imbalance_proxy'),'participation_limit')
        self.assertEqual(gate_status(ob,1,110,'volume_proxy'),'price_mismatch')
        ob['imbalance']=1
        self.assertEqual(gate_status(ob,10,100,'zero_imbalance_proxy'),'nonzero_market_imbalance')
        self.assertEqual(gate_status(ob,10,100,'volume_proxy'),'proxy_pass')
        ob['imbalance']=None
        self.assertEqual(gate_status(ob,10,100,'zero_imbalance_proxy'),'missing_market_imbalance')

    def test_conflicting_duplicate_is_excluded_not_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with zipfile.ZipFile(root/'ferozmd53.zip','w') as z:
                for suffix,volume in [('',100),(' (1)',200)]:
                    z.writestr('data/pre-open-FO-01-JUL-2026'+suffix+'.csv',
                        'SYMBOL,FINAL_PRICE,FINAL_QUANTITY,LAST_UPDATE\nABC,10,'+str(volume)+',01-Jul-2026 09:08:00\n')
            rows,audit=load_archive('ferozmd53',root)
            self.assertFalse(rows)
            self.assertEqual(audit['excluded_conflicting_keys'],1)

    def test_nonfinite_and_missing_are_not_inferred_zero(self):
        self.assertIsNone(number('nan'));self.assertIsNone(number('-'))
        self.assertEqual(number('1,000'),1000)
        self.assertIsNone(observation('ABC',1,100,None,None,0)['imbalance'])

    def test_quote_date_must_match_the_file_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with zipfile.ZipFile(root/'ferozmd53.zip','w') as z:
                z.writestr('data/pre-open-FO-01-JUL-2026.csv',
                    'SYMBOL,FINAL_PRICE,FINAL_QUANTITY,LAST_UPDATE\nABC,10,100,30-Jun-2026 09:08:00\nXYZ,20,200,01-Jul-2026 09:08:00\n')
            rows,audit=load_archive('ferozmd53',root)
            self.assertEqual(list(rows),[('2026-07-01','XYZ')])
            self.assertEqual(audit['wrong_or_unparseable_quote_date_rows_excluded'],1)

    def test_all_pass_proxy_reproduces_reference_accounting(self):
        prices=np.full((35,20),100.)
        closes=prices*(1+np.arange(35)[:,None]*.001)
        a=dict(o=prices,c=closes,industry=np.array(['group'+str(i//4) for i in range(20)]))
        score=np.tile(np.arange(20,dtype=float),(35,1))
        def fill(t,s,side,value,qty):
            tag=gate_status(observation('ABC',100,1e9,None,0,0),qty,100,'zero_imbalance_proxy')
            return (100.,1.,tag) if tag=='proxy_pass' else (None,0.,tag)
        ref=xsim.run(a,score,0,integer=True,ledger=True)
        proxy=xsim.run(a,score,0,integer=True,ledger=True,fill=fill)
        np.testing.assert_allclose(ref['eq'],proxy['eq'],rtol=0,atol=1e-12)
        self.assertEqual(ref['cash'],proxy['cash'])
        self.assertEqual(ref['costs'],proxy['costs'])

    def test_failed_sell_remains_pending_without_exceeding_position_cap(self):
        a=dict(o=np.full((12,4),100.),c=np.full((12,4),100.),industry=np.array(['Other']*4))
        score=np.tile([4.,3.,2.,1.],(12,1));score[5:]=[1.,2.,4.,3.]
        def fill(t,s,side,value,qty):return (None,0.,'missing_observation') if side=='S' else (100.,1.,'proxy_pass')
        r=xsim.run(a,score,0,N=2,keep=2,integer=True,ledger=True,fill=fill)
        self.assertEqual(set(r['pending']['sell']),{0,1})
        self.assertEqual(set(r['shares']),{0,1})
        self.assertLessEqual(max(r['n_names']),2)
        self.assertTrue(all(o['filled_value']==0 for o in r['ledger'] if o['side']=='S'))


if __name__=='__main__':unittest.main(verbosity=2)
