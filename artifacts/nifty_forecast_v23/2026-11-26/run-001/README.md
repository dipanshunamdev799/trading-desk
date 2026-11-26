# Reproduce the V23 research

Run from the trading-desk workspace with the existing virtual environment and frozen V1–V22 inputs. The V22 calendar
environment is used for completed foreign forward marks. Historical modeling reads only the November 17 vintage.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$v23Python = '.\.venv\Scripts\python.exe'
$steps = @('common','reference','archive','law_index','geometry','paths','forecast','evidence','parameter_uncertainty','precision','search_risk','attribution')
foreach ($step in $steps) {
    & $v23Python -W ignore -m ("research.nifty_forecast_v23." + $step)
    if ($LASTEXITCODE -ne 0) { throw "V23 failed in $step" }
}
& $v23Python -W ignore -m research.nifty_forecast_v23.attribution paths
& $v23Python -W ignore -m research.nifty_forecast_v23.report
& $v23Python -W ignore -m research.nifty_forecast_v23.verify
```

The archived Upstox/Yahoo source audit is held in the V23 source receipts, raw snapshots and paired-bar files.
To re-acquire those bounded daily bars, run `research.nifty_forecast_v23.sources` before rerunning `paths`.
Broker acquisition uses read-only market data and the existing Upstox credential. It does not expose the token.

The forward lane is clock-bound. The commands `forward stage`, `forward dry-run` and `forward watch` are the
one-run November 26 capture sequence and must be invoked before that morning cutoff to capture a new issue.
`forward settle` refreshes the ledger only after verified original targets are available. Replaying the reports
uses the saved forward receipts. Changes to native candidate state require a new authentic decision record.
Run `research.nifty_forecast_v23.gjr_continuation` for the historical V14 GJR risk replay and live state preflight.

A return-law NPZ stores atoms and weights concatenated with zero-based offsets. The case CSV identifies the law
and exact target. The source map records log versus arithmetic support from earlier versions. The joint path arrays
store log-relative OHLC. For exact reproduction use the library, donor order, clock, anchor and recipe.

[Research index](NIFTY_V23_RESEARCH.md)
