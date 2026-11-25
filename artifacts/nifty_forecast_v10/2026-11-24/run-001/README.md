# NIFTY V10 reproducibility

This run is a historical research archive for NIFTY 50 over the next five and 21 trading sessions. Its model inputs and outcomes use 2025–2026 observations, with the original 17 November 2026 freeze. The refreshed files are isolated under refresh/.

## Files

- [Research index](NIFTY_V10_RESEARCH.md) links all sixteen reports.
- [Configuration and fold ledger](experiment-registry.json) records dates, eligibility, preprocessing choices, effective sample sizes, warnings and model file hashes.
- [Complete scored results](all-predictions.csv) have per-origin probabilities, points, quantiles, intervals, bucket probabilities and realized outcomes. Weighted endpoint atoms are retained for the baseline and target families and designated specialist and mixture laws. Every system is reproducible from the registered inputs and dated fit partitions.
- [Actual selections by fold](training-information-by-fold.csv), the archived joblib models and coefficient tables preserve training chronology and fitted coefficients. Joblib files are local Python pickle artifacts and should only be loaded from this authenticated archive.
- [Artifacts and code manifest](manifest.json) binds byte hashes. [Verification](verification.json) records empirical checks.

## Exact rerun

Run from the repository root with the workspace virtual environment. Use a fresh NIFTY_V10_OUT subfolder under artifacts/nifty_forecast_v10. To hold data sources constant, copy sources/, refresh/, sector-intraday.csv, native-equal-weight-closes.csv, the two source-audit JSON files, MISSION.md and this README from this run to that subfolder. The paths in V1–V9 remain required for frozen price and target matrices and legacy replay. The acquisition program can make new read-only requests when source files are absent. Those requests have a new acquisition timestamp.

~~~powershell
$py = '.\.venv\Scripts\python.exe'
$env:NIFTY_V10_OUT = 'artifacts/nifty_forecast_v10/replay-v10'
& $py -m research.nifty_forecast_v10.reproduce
& $py -m research.nifty_forecast_v10.features
foreach ($batch in 'base','composition','overlap','structure','target','new') {
    & $py -m research.nifty_forecast_v10.experiments $batch
    if ($LASTEXITCODE -ne 0) { throw "Batch failed: $batch" }
}
& $py -m research.nifty_forecast_v10.derivatives
& $py -m research.nifty_forecast_v10.transfer
& $py -m research.nifty_forecast_v10.audit covariance
& $py -m research.nifty_forecast_v10.followup information
& $py -m research.nifty_forecast_v10.followup curves
& $py -m research.nifty_forecast_v10.followup perturb
& $py -m research.nifty_forecast_v10.mixtures
& $py -m research.nifty_forecast_v10.audit copies
& $py -m research.nifty_forecast_v10.audit refresh
& $py -m research.nifty_forecast_v10.audit protected
& $py -m research.nifty_forecast_v10.analyze
& $py -m research.nifty_forecast_v10.verify curve
& $py -m research.nifty_forecast_v10.figures
& $py -m research.nifty_forecast_v10.verify data
& $py -m research.nifty_forecast_v10.report
& $py -m research.nifty_forecast_v10.verify manifest
~~~

The mixture and several follow-up wave specifications were selected after reviewing initial outputs. Rerun reports retain that historical exposure. Source paths are versioned. Compare numerical scores using the supplied tolerances. Machine-local acquisition, fit registration and verification timestamps vary by rerun.
