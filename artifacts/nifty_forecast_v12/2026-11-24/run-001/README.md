# Reproduce NIFTY V12

Use the repository virtual environment and a fresh NIFTY_V12_OUT beneath artifacts/nifty_forecast_v12. The original 2025–2026 V1–V11 artifacts remain read-only dependencies. Source availability is conservative. All predictions use the November 17 historical freeze. The read-only refresh acquires a separate current vintage and has no effect on the fitted historical chronology.

~~~powershell
$py = '.\.venv\Scripts\python.exe'
$env:NIFTY_V12_OUT = 'artifacts/nifty_forecast_v12/replay-v12'
& $py -m research.nifty_forecast_v12.replay protect
& $py -m research.nifty_forecast_v12.replay direct
& $py -m research.nifty_forecast_v12.replay older
& $py -m research.nifty_forecast_v12.replay legacy
& $py -m research.nifty_forecast_v12.options extract
& $py -m research.nifty_forecast_v12.options reconstruct
& $py -m research.nifty_forecast_v12.alignment sources
& $py -m research.nifty_forecast_v12.alignment futures
& $py -m research.nifty_forecast_v12.alignment align
& $py -m research.nifty_forecast_v12.alignment refresh
& $py -m research.nifty_forecast_v12.features
& $py -m research.nifty_forecast_v12.phase
& $py -m research.nifty_forecast_v12.market market
& $py -m research.nifty_forecast_v12.market priced
& $py -m research.nifty_forecast_v12.ensemble
& $py -m research.nifty_forecast_v12.falsification
& $py -m research.nifty_forecast_v12.analysis
& $py -m research.nifty_forecast_v12.legacy_risk
& $py -m research.nifty_forecast_v12.figures
& $py -m research.nifty_forecast_v12.verify verify
& $py -m research.nifty_forecast_v12.reports
& $py -m research.nifty_forecast_v12.verify delivery
~~~

Copy this README and the original mission into a scratch run before generating its manifest. Acquisition clocks vary with reruns. The forward-measure option archive uses date, listed expiry and pricing method as keys. Each forecast law has horizon, model ID, origin and independently verified evaluation endpoint as keys. Each key's atoms and weights occupy the corresponding pair of offsets. Registry entries identify diagnostic risk-neutral prices and calibrated physical candidates. Use the complete-law archive to reproduce scores without reading pickled estimators. The original selected dates and saved coefficients are retained in V12 model artifacts.

[Research index](NIFTY_V12_RESEARCH.md) · [Source and fit registry](registry.json) · [Quality and reconstruction](surface-quality.csv) · [Forecast law archive](full-law-archive.json) · [Verification](verification.json) · [Manifest](manifest.json)
