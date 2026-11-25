"""Selection persistence and source-completeness guards, without market data."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.run_intraday_momentum import (
    freeze_json,passes_paper_gate,validate_acquisition,extension_markdown,resolution_markdown,
)


class RunnerTests(unittest.TestCase):
    def test_identical_freeze_preserves_original_bytes_and_timestamp(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'frozen.json'
            first={'generated_at':'first','code':'abc','selected':'A'}
            freeze_json(path,first);before=path.read_bytes()
            replay=freeze_json(path,{**first,'generated_at':'later'})
            self.assertEqual(replay['generated_at'],'first')
            self.assertEqual(path.read_bytes(),before)

    def test_changed_code_or_selection_cannot_replace_freeze(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'frozen.json'
            freeze_json(path,{'code':'abc','selected':'A'})
            with self.assertRaisesRegex(RuntimeError,'versioned'):
                freeze_json(path,{'code':'different','selected':'A'})
            self.assertEqual(json.loads(path.read_text())['code'],'abc')

    def test_paper_gate_rejects_positive_average_with_cash_loss(self):
        final=dict(trades=60,active_days=40,mean_net_bps_per_trade=5,total_return=.03)
        stress=dict(mean_net_bps_per_trade=1,total_return=.01)
        interval={'total_return_ci95':[.001,.06]}
        self.assertTrue(passes_paper_gate(final,stress,interval))
        self.assertFalse(passes_paper_gate(final,{**stress,'total_return':-.01},interval))
        self.assertFalse(passes_paper_gate({**final,'total_return':-.01},stress,interval))
        self.assertFalse(passes_paper_gate(final,stress,{'total_return_ci95':[-.001,.06]}))

    def test_missing_even_successful_source_job_is_incomplete(self):
        plan={'jobs':[{'id':'A'},{'id':'B'}]}
        good={'plan_sha256':'hash','jobs':[{'id':'A','status':'ok'},{'id':'B','status':'ok'}]}
        validate_acquisition(plan,good,'hash')
        with self.assertRaisesRegex(RuntimeError,'job set'):
            validate_acquisition(plan,{**good,'jobs':good['jobs'][:1]},'hash')
        with self.assertRaisesRegex(RuntimeError,'job set'):
            validate_acquisition(plan,{**good,'jobs':good['jobs']+[good['jobs'][0]]},'hash')
        with self.assertRaisesRegex(RuntimeError,'different plan'):
            validate_acquisition(plan,good,'other')

    def test_failed_source_cannot_be_ignored(self):
        with self.assertRaisesRegex(RuntimeError,'still incomplete'):
            validate_acquisition({'jobs':[{'id':'A'}]},
                {'plan_sha256':'hash','jobs':[{'id':'A','status':'failed'}]},'hash')

    def test_empty_diagnostics_do_not_invent_evidence(self):
        self.assertIn('No qualifying','\n'.join(extension_markdown({'groups':[]})))
        self.assertIn('No development-selected','\n'.join(resolution_markdown({'chosen':0})))


if __name__=='__main__':unittest.main()
