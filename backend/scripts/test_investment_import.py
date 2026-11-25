"""One-time source import tests use scratch DuckDB inputs and isolated PostgreSQL schemas."""
from datetime import datetime
from pathlib import Path
import sys
import tempfile
import unittest

import duckdb
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from test_investment_bots import test_database,instruments
from investment_bots.data import Inputs,NIFTY,canonical
from investment_bots.engine import DataBlocked,features
from investment_bots.import_duckdb import ingest,file_hash
from investment_bots.verification import reference_inputs,verify_inputs,verify_auction_classifier


class ImportTests(unittest.TestCase):
    def source(self,folder):
        p=Path(folder)/'source.duckdb';c=duckdb.connect(str(p));key='NSE_EQ|INE000000000'
        c.execute('CREATE TABLE candles(instrument_key VARCHAR,interval VARCHAR,ts TIMESTAMP,open DOUBLE,high DOUBLE,low DOUBLE,close DOUBLE,volume DOUBLE)')
        c.executemany('INSERT INTO candles VALUES(?,?,?,?,?,?,?,?)',[
            (key,'1day','2026-11-13',100.,101.,99.,100.,1000.),
            (key,'1day','2026-11-13 15:30:00',100.,101.,99.,100.,1000.),
            (key,'1day','2024-12-31',50.,51.,49.,50.,1000.),
            (NIFTY,'1day','2026-11-13',25000.,25100.,24900.,25000.,0.)])
        c.execute('CREATE TABLE corporate_actions(isin VARCHAR,name VARCHAR,ex_date DATE)')
        c.execute("INSERT INTO corporate_actions VALUES('INE000000000','Dividend','2026-11-13')")
        c.close();return p,key

    def test_import_is_read_only_windowed_deduplicated_and_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp,test_database() as db:
            source,key=self.source(tmp);inputs=Inputs(db);before=file_hash(source)
            a=ingest(source,inputs=inputs,progress=lambda m:None)
            b=ingest(source,inputs=inputs,progress=lambda m:None)
            self.assertEqual(file_hash(source),before)
            self.assertEqual(a,b);self.assertEqual(a['daily_rows'],2)
            self.assertEqual(a['corporate_actions'],1);self.assertFalse(a['metadata_ready'])
            with inputs.connection() as c:
                self.assertEqual(c.execute(f'SELECT count(*) FROM {db.market_table}').fetchone()[0],2)
                self.assertEqual(c.execute(f"SELECT (ts AT TIME ZONE 'Asia/Kolkata')::text FROM {db.market_table} WHERE instrument_key=%s",(key,)).fetchone()[0],'2026-11-13 00:00:00')

    def test_conflict_rolls_back_entire_import(self):
        with tempfile.TemporaryDirectory() as tmp,test_database() as db:
            source,key=self.source(tmp);inputs=Inputs(db)
            inputs.save_bars(key,[['2026-11-13',200,201,199,200,1000]],'2026-11-13')
            with self.assertRaisesRegex(DataBlocked,'panel_check'):ingest(source,inputs=inputs,progress=lambda m:None)
            with inputs.connection() as c:
                self.assertEqual(c.execute(f'SELECT count(*) FROM {db.market_table}').fetchone()[0],1)
            self.assertNotIn('duckdb_import',inputs.metadata())
            self.assertNotIn('corporate_actions',inputs.metadata())

    def bundle(self,folder,key):
        meta=instruments(2284);csv=Path(folder)/'dpanel_meta.csv'
        pd.DataFrame(meta.values()).rename(columns={'symbol':'trading_symbol'}).to_csv(csv,index=False)
        arrays={}
        for field,value in [('o',100),('h',101),('l',99),('c',100),('v',1000)]:
            arr=np.full((1,2284),np.nan);arr[0,0]=value;arrays[field]=arr
        panel=Path(folder)/'dpanel.npz.zip'
        with panel.open('wb') as f:
            np.savez_compressed(f,dates=np.array(['2026-11-13'],dtype='datetime64[ns]').astype('int64'),
                               keys=np.array(list(meta)),ix_Nifty_50=np.array([[25000,25100,24900,25000]]),**arrays)
        return csv,panel

    def test_frozen_panel_validates_before_pin_and_reload_uses_postgres(self):
        with tempfile.TemporaryDirectory() as tmp,test_database() as db:
            source,key=self.source(tmp);meta,panel=self.bundle(tmp,key);inputs=Inputs(db)
            report=ingest(source,metadata=meta,panel=panel,inputs=inputs,progress=lambda m:None)
            self.assertTrue(report['metadata_ready']);self.assertTrue(report['panel_comparison']['passed'])
            source.unlink();panel.unlink();meta.unlink()  # PostgreSQL is self-contained after import.
            rows,sessions,frames=inputs.load('2026-11-13')
            self.assertEqual(len(rows),2284);self.assertEqual(sessions,['2026-11-13'])
            self.assertEqual(frames['c'].loc['2026-11-13',key],100.)

    def test_frozen_panel_mismatch_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp,test_database() as db:
            source,key=self.source(tmp);meta,panel=self.bundle(tmp,key);inputs=Inputs(db)
            c=duckdb.connect(str(source));c.execute("UPDATE candles SET close=100.5 WHERE instrument_key=? AND ts>='2026-11-13'",[key]);c.close()
            with self.assertRaisesRegex(DataBlocked,'panel / source DB mismatch'):
                ingest(source,metadata=meta,panel=panel,inputs=inputs,progress=lambda m:None)
            with inputs.connection() as c:self.assertEqual(c.execute(f'SELECT count(*) FROM {db.market_table}').fetchone()[0],0)


class ReferenceGuardTests(unittest.TestCase):
    def test_auction_classifier_matches_1152_original_cases(self):
        self.assertEqual(verify_auction_classifier(),1152)

    def test_original_universe_and_signal_match_independently(self):
        meta=instruments(30);days=pd.bdate_range('2025-01-01',periods=100).strftime('%Y-%m-%d').tolist()
        t=np.arange(100);c=pd.DataFrame({k:100*np.exp(.002*t+.01*np.sin(t+i)) for i,k in enumerate(meta)},index=days)
        v=pd.DataFrame({k:100000+i*103 for i,k in enumerate(meta)},index=days)
        frames={'o':c,'h':c*1.01,'l':c*.99,'c':c,'v':v}
        u,scores=features(c,v,meta)
        ref=reference_inputs(meta,days,frames,np.full((100,4),100.))
        np.testing.assert_array_equal(u.to_numpy(),ref['U'])
        np.testing.assert_allclose(scores.to_numpy(),ref['score'],atol=1e-12,rtol=0,equal_nan=True)

    def test_runtime_rejects_reference_disagreement(self):
        meta=instruments(30);days=pd.bdate_range('2025-01-01',periods=100).strftime('%Y-%m-%d').tolist()
        t=np.arange(100);c=pd.DataFrame({k:100*np.exp(.002*t+.01*np.sin(t+i)) for i,k in enumerate(meta)},index=days)
        v=pd.DataFrame({k:100000+i*103 for i,k in enumerate(meta)},index=days)
        frames={'o':c,'h':c*1.01,'l':c*.99,'c':c,'v':v};u,scores=features(c,v,meta)
        u.iloc[-1,0]=False
        class IndexFixture:
            def index_prices(self,sessions):return np.full((len(sessions),4),100.)
        with self.assertRaisesRegex(DataBlocked,'universe/score mismatch'):
            verify_inputs(IndexFixture(),meta,days,frames,u,scores)


if __name__=='__main__':unittest.main(verbosity=2)
