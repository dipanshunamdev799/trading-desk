# NIFTY session forecast experiment

The [17 November 2026 report](../../NIFTY_FORECAST_2026-11-17.md) records the
fixed forecast, all candidate results, current-factor scenarios and limitations.
The final artifact directory is `artifacts/nifty_forecast/2026-11-17/run-v3`.
Earlier input attempts and output runs remain as research provenance; they are
not separate independent experiments. There was no parameter search between runs.

`PROTOCOL.md` defines the study. `collect.py` freezes read-only inputs;
`supplement.py` contains this date's additional global-history batch. `engine.py`
creates feature panels, monthly walk-forward replays and an immutable call.
`report.py` produces the readable report and static figure. `verify.py` checks
information boundaries; `score.py` resolves the call once the daily candle exists.
These modules do not submit orders or control bots.

Run from the repository root using `.venv/Scripts/python.exe -m` followed by
the module name, for example `research.nifty_forecast.verify`. Reproduction must
use a new `--out` directory. The live collector is deliberately restricted to
the current pre-market date; saved input freezes support later reproduction.
The supplemental collector and report are specific to this dated experiment.

The model's weak historical performance is part of the recorded result.
The 59.8% raw upward output is not a demonstrated 59.8% success probability.

## Learned input weights

The [historical-error-weighted extension](../../NIFTY_LEARNED_WEIGHTS_2026-11-17.md)
learns 71 input coefficients inside 12 groups, then learns group allocations from
prior chronological prediction errors. Its final artifacts are in
`artifacts/nifty_forecast/2026-11-17/adaptive-v2`; the first experiment remains
unchanged. `ADAPTIVE_PROTOCOL.md` specifies fitting, evidence gates and controls.

- `extend_history.py` retrieves overlapping read-only institutional windows.
- `adaptive.py` fits monthly experts, daily allocations and prior-only calibration.
- `adaptive_diagnostics.py` measures conditional weight stability and sensitivity.
- `adaptive_report.py` writes the report and research figure.
- `verify_adaptive.py` tests error learning and information boundaries.

```powershell
.\.venv\Scripts\python.exe -m research.nifty_forecast.verify_adaptive
.\.venv\Scripts\python.exe -m research.nifty_forecast.adaptive --out artifacts/nifty_forecast/2026-11-17/adaptive-reproduction-01
.\.venv\Scripts\python.exe -m research.nifty_forecast.score --run artifacts/nifty_forecast/2026-11-17/adaptive-v2
```

The last command remains pending until the official daily candle exists.
For a future session, supply fresh frozen paths through `--inputs`, `--supplement`,
`--institutional` and `--reference-run`, plus a new output directory. No automatic
watcher or scheduler runs. The learned forecast is neutral; the historical study
does not establish an edge. Calibration worsened this evaluation, and its result
remains disclosed rather than replaced after inspection.

## Strict two-year check

The [two-year rerun](../../NIFTY_TWO_YEAR_2026-11-17.md) restricts raw prices,
indicator initialization, fitting and error-learning history to 17 November 2024
through 16 November 2026. Outputs are in `artifacts/nifty_forecast/2026-11-17/two-year-v1`.
Run `research.nifty_forecast.verify_two_year` for the boundary checks, or
`research.nifty_forecast.two_year --out <new-directory>` to reproduce it.
The 495-session total window leaves 96 decisions after training and weight-learning
warmup; it is not two years of independent out-of-sample forecasts.

## Week and month horizons

The [5/21-session experiment](../../NIFTY_WEEK_MONTH_2026-11-17.md) keeps the same
two-year input boundary but retrains separate weekly/monthly labels and weights.
Every training, weighting, calibration and magnitude outcome must have finished
its full horizon by the decision. `HORIZON_PROTOCOL.md` records the design.
Final artifacts are in `artifacts/nifty_forecast/2026-11-17/horizons-v2`.

Run `research.nifty_forecast.verify_horizons` for ten focused checks and
`research.nifty_forecast.score_horizons --run artifacts/nifty_forecast/2026-11-17/horizons-v2`
to score each horizon after maturity. No background watcher is running. The
monthly evaluation is poor and contains only two non-overlapping windows.
