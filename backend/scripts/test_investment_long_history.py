"""Versioned-history math, cash accounting and PostgreSQL import isolation."""
from pathlib import Path
import sys,tempfile,unittest
import numpy as np
import pandas as pd
import duckdb

ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from test_investment_bots import test_database,instruments
from investment_bots.data import Inputs
from investment_bots.engine import features
from investment_bots.long_history import ResearchStore,metrics,run_portfolio,trade_accounting,native_data,benchmark_curve
from investment_bots.reference import sim5


class ResearchMathTests(unittest.TestCase):
    def test_benchmark_does_not_silently_fill_long_data_gaps(self):
        from investment_bots.engine import DataBlocked
        with self.assertRaisesRegex(DataBlocked,'stale coverage'):benchmark_curve([100,110,np.nan,np.nan],0)
        curve,count=benchmark_curve([100,110,np.nan,120],0)
        np.testing.assert_allclose(curve,[1,1.1,1.1,1.2]);self.assertEqual(count,1)
    def test_result_boundary_accepts_numpy_scalars_but_rejects_nan(self):
        from investment_bots.data import canonical
        self.assertEqual(canonical(native_data({'orders':np.int64(512),'ok':np.bool_(True)})), '{"ok":true,"orders":512}')
        with self.assertRaises(ValueError):canonical(native_data({'return':np.float64(np.nan)}))

    def test_drawdown_year_boundaries_and_initial_capital(self):
        days=['2016-11-15','2016-12-30','2017-01-02','2017-12-29']
        r=metrics([1.,1.2,.9,1.3],days)
        self.assertAlmostEqual(r['total_return'],.3)
        self.assertAlmostEqual(r['max_drawdown'],-.25)
        self.assertAlmostEqual(r['annual_returns']['2016'],.2)
        self.assertAlmostEqual(r['annual_returns']['2017'],1.3/1.2-1)
        self.assertEqual(r['worst_drawdown']['peak'],'2016-12-30')
        self.assertEqual(r['worst_drawdown']['trough'],'2017-01-02')
        self.assertEqual(r['worst_drawdown']['recovery'],'2017-12-29')
        self.assertAlmostEqual(r['final_value_rupees'],1300000)

    def fixture(self):
        meta=instruments(70);rng=np.random.default_rng(15);t=110
        close=100*np.exp(np.cumsum(rng.normal(.001,.015,(t,70)),axis=0))
        a=dict(o=close,c=close,keys=list(meta),industry=np.array([meta[k]['industry'] for k in meta]))
        return a,rng.normal(size=(t,70)),pd.bdate_range('2016-01-01',periods=t).strftime('%Y-%m-%d').tolist()

    def test_explicit_research_bounds_do_not_change_frozen_default(self):
        a,_,days=self.fixture();meta=instruments(70)
        close=pd.DataFrame(a['c'],index=days,columns=a['keys']);vol=pd.DataFrame(100000,index=days,columns=a['keys'])
        self.assertTrue(features(close,vol,meta)[1].empty)
        u,s=features(close,vol,meta,start='2016-01-01',end='2016-12-31')
        self.assertTrue(s.iloc[:63].isna().all().all());self.assertTrue(s.iloc[-1].notna().all())
        _,prefix=features(close.iloc[:80],vol.iloc[:80],meta,start='2016-01-01',end='2016-12-31')
        pd.testing.assert_frame_equal(prefix,s.iloc[:80])

    def test_fractional_c0_matches_original_and_cashflow_reconciles(self):
        a,score,days=self.fixture();r=run_portfolio(a,score,0,'C0-R')
        ref=sim5.run(a,score,0,tiebreak=np.argsort(np.argsort(a['keys'])))
        np.testing.assert_allclose(r['eq'],ref['eq'],rtol=0,atol=1e-12)
        closed,orders,open_pnl=trade_accounting(r['books'],a['keys'],days)
        self.assertAlmostEqual(sum(t['net_pnl'] for t in closed)+open_pnl,1e6*(r['eq'][-1]-1),places=5)
        from investment_bots.data import canonical
        self.assertTrue(canonical(orders[0]))

    def test_c1_resize_cashflows_reconcile_in_both_share_modes(self):
        a,score,days=self.fixture()
        for whole in (False,True):
            with self.subTest(whole=whole):
                r=run_portfolio(a,score,0,'C1-R',integer=whole)
                closed,_,open_pnl=trade_accounting(r['books'],a['keys'],days,integer=whole)
                self.assertAlmostEqual(sum(t['net_pnl'] for t in closed)+open_pnl,1e6*(r['eq'][-1]-1),places=5)

    def test_c2_keeps_five_independent_capital_accounts(self):
        a,score,days=self.fixture();r=run_portfolio(a,score,0,'C2-S')
        self.assertEqual(len(r['books']),5)
        self.assertEqual(r['books'][4]['eq'][3],1.)
        self.assertEqual(r['eq'][0],1.)
        closed,_,open_pnl=trade_accounting(r['books'],a['keys'],days)
        self.assertAlmostEqual(sum(t['net_pnl'] for t in closed)+open_pnl,1e6*(r['eq'][-1]-1),places=5)


class HistoricalImportTests(unittest.TestCase):
    def test_import_excludes_bad_prices_and_preserves_paper_rows(self):
        with tempfile.TemporaryDirectory() as tmp,test_database() as db:
            with db.connection() as c:c.execute("INSERT INTO controls VALUES('paper_sentinel',0,'PAUSED','keep',NULL)")
            source=Path(tmp)/'old.duckdb';d=duckdb.connect(str(source))
            d.execute('CREATE TABLE candles(instrument_key VARCHAR,interval VARCHAR,ts TIMESTAMP,open DOUBLE,high DOUBLE,low DOUBLE,close DOUBLE,volume DOUBLE)')
            d.executemany('INSERT INTO candles VALUES(?,?,?,?,?,?,?,?)',[
                ('NSE_EQ|INE000000000','1day','2016-01-01',100,101,99,100,1000),
                ('NSE_EQ|INE000000000','1day','2016-01-04',0,0,0,0,1000)])
            d.close();study=ResearchStore(db);report=study.import_older(source)
            self.assertEqual(report['invalid_rows_excluded'],1);self.assertEqual(report['inserted'],1)
            self.assertEqual(study.import_older(source),report)
            with db.connection() as c:
                self.assertEqual(c.execute("SELECT status,error FROM controls WHERE id='paper_sentinel'").fetchone(),['PAUSED','keep'])
                self.assertEqual(c.execute(f'SELECT count(*) FROM {db.market_table}').fetchone()[0],1)


if __name__=='__main__':unittest.main(verbosity=2)
