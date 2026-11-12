import unittest
import numpy as np
from research.swing_diagnosis.features import feature_panel,bootstrap,bh

class TestFeatures(unittest.TestCase):
    def test_future_prices_do_not_change_past_descriptors_or_regimes(self):
        rng=np.random.default_rng(918);n,t=4,410
        c=np.exp(np.cumsum(rng.normal(0,.01,(n,t)),axis=1))*100
        p={'neutral_close':c,'neutral_open':c*.999,'neutral_high':c*1.01,'neutral_low':c*.99,
           'neutral_volume':rng.uniform(1e5,1e6,(n,t)), 'niftyclose':np.exp(np.cumsum(rng.normal(0,.008,t)))*20000,
           'liquidity_turnover':np.full((n,t),1e8)}
        idx={'sector':['a','a','b','b']}
        a,ra=feature_panel(idx,p)
        short={k:v[:,:330].copy() if v.ndim==2 else v[:330].copy() for k,v in p.items()}
        b,rb=feature_panel(idx,short)
        for k in a:np.testing.assert_allclose(a[k][:,:330],b[k],equal_nan=True,err_msg=k)
        for k in ra:np.testing.assert_array_equal(ra[k][:330],rb[k],err_msg=k)

    def test_paired_zero_and_bh(self):
        out=bootstrap(np.zeros(70),draws=100)
        self.assertEqual((out['delta'],out['lo'],out['hi'],out['p']),(0,0,0,1))
        np.testing.assert_allclose(bh([.01,.04,.03]),[.03,.04,.04])

if __name__=='__main__':unittest.main()
