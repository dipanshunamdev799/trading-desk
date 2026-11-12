# Expanded MACD, EMA and support/resistance discovery

This is research-only code. It never submits broker orders or starts paper/live
workers. The earlier studies remain preserved in their own artifact directories.

The frozen coarse catalog has 1,174 configurations across 48 mechanism families;
134 additional neighbors were selected using development data only. Indicators
cover MACD/PPO, regular/hidden pivot divergence, histogram/zero/weekly timing,
EMA/ribbons/reclaims/contraction, KAMA, confirmed pivots/clusters, calendar and
floor levels, Donchian, breakout/retest/role reversal, sweeps, Fibonacci versus
adjacent controls, actual-rupee rounds, anchored VWAP proxies and seven hybrids.
Eight one-factor filters and separate risk/exit ablations make each experiment
interpretable without a Cartesian optimization over all components.
Filter thresholds are frozen reference values, not an additional optimized grid.
Sector-peer momentum is a cohort proxy; historical sector-index relative strength,
delivery volume and volume-at-price were not available as certified inputs.

The dated universe is 500 October 2024 fund holdings, published before the test
window. It is a primary-source cohort proxy, not a certified historical index
membership master. Thirty names are explicitly quarantined; 470 have complete
research data. Their daily panel contains 1,704 sessions for warmup, but only
11 November 2024 through 9 November 2026 is evaluated. Backdating the 2024-selected
universe to a 2020 investment portfolio would be invalid and is not done.

The chronological development/validation/final split is combined with 375
development companies and 95 reserved companies, chosen by frozen historical
ISIN hash, excluding the earlier 50-company cohort from the reserved group.
Reserved companies do not make the reused market calendar temporally untouched.

## Reproduce

Use the existing repository virtual environment from the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_discovery*.py'
.\.venv\Scripts\python.exe -m research.swing_discovery.data
.\.venv\Scripts\python.exe scripts\run_swing_discovery.py
.\.venv\Scripts\python.exe scripts\verify_discovery_intraday.py
.\.venv\Scripts\python.exe scripts\verify_swing_discovery.py
.\.venv\Scripts\python.exe scripts\finalize_swing_discovery.py
```

The daily panel is frozen in `daily-panel.npz`; acquisition and source fingerprints
are retained. Cache hits do not refetch. Analytics credentials are loaded from the
existing configuration without displaying them. Source-workbook extraction needs
`xlrd`; calculations use the recorded pandas/NumPy/Matplotlib versions.

The main runner resumes completed ledger keys and rejects changes to a previously
stored configuration. Refinement parents come only from original coarse
development results. Walk-forward folds search only the original coarse catalog;
later-selected neighbors cannot leak into earlier folds. The finalizer corrects
the statistical scope to coarse-only, deduplicated development CSCV/PBO and records
delivery hashes without modifying trading rules or executing extra experiments.

## Modules and execution meaning

- `data.py`: dated holdings, historical identity resolution, immutable source
  responses, stock/calendar/action audits, unit reconstruction and liquidity arrays.
- `structure.py`: delayed strict pivots, frozen levels, calendar levels, ordered
  Fibonacci anchors, current-rupee rounds and causal anchored VWAP proxy.
- `signals.py`: cached causal panel indicators, exact catalog manifest, generation
  and development-only neighborhoods. Completed weekly values release the next week.
- `engine.py`: chronological next-open stock sleeves, vectorization and batched
  parity, cash/risk/participation limits, taxes/fees, adverse gaps and stop-first
  daily ambiguity, modeled split/dividend entitlements, marked NAV and metrics.
- `diagnostics.py`: balanced scores with hard vetoes, common-calendar search
  controls, DSR with IID limitations and development-only CSCV/PBO.
- `benchmarks.py`: one buy-and-hold entry subject to the same liquidity, cash and
  fee assumptions; leftover cash remains idle, no reconstitution/reinvestment.
- `reporting.py`: frozen-family rankings, pure-versus-filtered category labels,
  exact top-20 rules, uncertainty, ablations, neighborhoods, stock/calendar/regime
  breakdowns, static figures and failure records.

Every stock has a separate initial Rs1,000,000 sleeve. Mean NAV summarizes those
independent allocations; it is not a pooled Rs1,000,000 account or a full-capital
position in every stock. Daily bars cannot reveal unknown intraday ordering.
Modeled volume units, adverse fill rates and corporate-action reconstruction are
assumptions with explicit limits, not certified historical spreads or quote depth.
Matched five-minute replay uses the preselected five rules and existing eligible
stocks only; counts overlap across periods and do not prove a five-minute portfolio.

## Artifacts

Begin with `artifacts/swing_discovery/REPORT.md` and `top-20.csv`. Exact parameters
and programmatic rules are in `top-20-exact-rules.json` and `top-20-rules.md`.
`research.sqlite3` holds all experiments, execution summaries, stock metrics and
portfolio calendars. CSVs retain ablations, all failed outcomes, stock/regime and
monthly/yearly summaries, uncertainty and neighborhood sensitivity. The frozen
protocol, holdings exclusions, raw fingerprints, source hashes, matched-resolution
check and independent verification remain alongside the results.

No frozen finalist passed the joint evidence screen. Descriptive leaders remain
failed diagnostics; prospective testing, observed execution quality and a funded
portfolio model are still required before any live-use claim.
