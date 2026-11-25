# Reproduce NIFTY V11

Use the repository virtual environment. Set NIFTY_V11_OUT to a fresh subdirectory inside artifacts/nifty_forecast_v11. Prior frozen paths for V1–V10 remain read-only dependencies. Copy the raw Nasdaq JSON from sources/nasdaq for an exact source vintage, or use the authenticated historical-download path in the international module. Select refresh separately to acquire a new snapshot. Reports for this delivery describe the completed November 23 refresh.

~~~powershell
$py = '.\.venv\Scripts\python.exe'
$env:NIFTY_V11_OUT = 'artifacts/nifty_forecast_v11/replay-v11'
& $py -m research.nifty_forecast_v11.replay freeze
& $py -m research.nifty_forecast_v11.replay older
& $py -m research.nifty_forecast_v11.replay v10
& $py -m research.nifty_forecast_v11.sources features
& $py -m research.nifty_forecast_v11.sources refresh
foreach ($batch in 'breadth','memory','overlap','distribution','disjoint') {
    & $py -m research.nifty_forecast_v11.engine $batch
    if ($LASTEXITCODE -ne 0) { throw "Fit batch failed: $batch" }
}
& $py -m research.nifty_forecast_v11.legacy_breadth
& $py -m research.nifty_forecast_v11.ensemble
& $py -m research.nifty_forecast_v11.ensemble --exact
& $py -m research.nifty_forecast_v11.international
& $py -m research.nifty_forecast_v11.falsification
& $py -m research.nifty_forecast_v11.analysis
& $py -m research.nifty_forecast_v11.verify protected
& $py -m research.nifty_forecast_v11.verify verify
& $py -m research.nifty_forecast_v11.archive
& $py -m research.nifty_forecast_v11.reports
& $py -m research.nifty_forecast_v11.verify delivery
~~~

Retain this README and the original mission in the rerun directory before delivery. The archived unsuccessful repair attempt is recorded in repair-registry.json and repair-ledger.json. Copy its three repair files from this run to include the earlier implementation attempt in the rerun audit. Fresh retests use the successful disjoint design.

[Study index](NIFTY_V11_RESEARCH.md) · [Full distribution archive](full-law-archive.json) · [All prediction outputs](all-predictions.csv) · [Verification](verification.json) · [Manifest](manifest.json)
