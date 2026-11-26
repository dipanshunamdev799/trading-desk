# Reproduce V22

Run from the trading-desk workspace with the established virtual environment. The run uses only artifact-verified 2025–2026
observations and stores source snapshots under this V22 directory. By default, the scripts reuse retained daily vendor
responses. Source acquisition requires network access and an existing read-only Upstox credential for broker checks.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$v22Python = '.\.venv\Scripts\python.exe'
$env:NIFTY_V22_CALENDAR_DEPS = Join-Path $env:TEMP 'nifty-v22-calendar-deps'
& $v22Python -m pip install --target $env:NIFTY_V22_CALENDAR_DEPS --no-deps exchange-calendars==4.13.3 pyluach korean-lunar-calendar toolz
$v22Steps = @('common','sources','source_checks','reference','panel','learning','analogues','india','risk','power','evidence')
foreach ($step in $v22Steps) {
    & $v22Python -W ignore::RuntimeWarning -m ("research.nifty_forecast_v22." + $step)
    if ($LASTEXITCODE -ne 0) { throw "Stopped in V22 module $step" }
}
& $v22Python -m research.nifty_forecast_v22.report
& $v22Python -m research.nifty_forecast_v22.verify
```

The archived forward receipts supply the ledger report during reproduction. To refresh the forward lane during an eligible
2026 date, run `& $v22Python -m research.nifty_forecast_v22.forward` before regenerating reports and verification. It preserves
the original issuances and captures newly available dated input receipts at the actual clock.

Return-law arrays contain concatenated arithmetic-return atoms and weights. Zero-based offsets delimit each law. The
matching case CSV provides the law ID, reference close, target end and exact cutoff. The analogue atlas links a case to
weighted scenario locations, source maturity and the corresponding `p5` or `p21` OHLC array. International model
archive columns describe an affine map of its stored normalized return support from the matched horizon file.

[Report index](NIFTY_V22_RESEARCH.md)
