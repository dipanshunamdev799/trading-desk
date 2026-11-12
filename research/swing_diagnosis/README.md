# Swing failure diagnosis

The diagnosis is separate from `research/swing_discovery` and reads its frozen
data/ledgers. Start with `artifacts/swing_diagnosis/REPORT.md`. Original sources
and outputs are preserved; new semantic patches and replays are explicitly named.

Use repository `.venv/Scripts/python.exe` from the repository root. Review each
script's frozen design before reproducing. Typical order:

1. `scripts/diagnosis_audit.py` (independent calculations and enumerated action patch).
2. `python -m research.swing_diagnosis.audit_replay` (48 frozen finalists,
   corrected execution).
3. `scripts/diagnosis_fetch_indices.py` and `scripts/diagnosis_history.py` (read-only
   official TRI/membership acquisition and authenticated price availability probes).
4. `scripts/diagnosis_benchmarks.py` and `scripts/diagnosis_benchmarks_corrected.py`.
5. `scripts/diagnosis_features.py --corrected` and `scripts/diagnosis_feature_report.py`.
6. `scripts/diagnosis_portfolio.py`, then `scripts/diagnosis_portfolio.py --corrected`.
7. `scripts/diagnosis_exits.py`, then `scripts/diagnosis_uncertainty.py`.
8. `scripts/diagnosis_regime_replay.py`, then `scripts/diagnosis_regime_stress.py`.
9. `scripts/report_swing_diagnosis.py`.

The benchmark and feature agents' own report scripts/documentation retain exact
commands and source URLs. Frozen input caches prevent fabricated data but do not
certify provider revisions, historical spreads or point-in-time membership.
Network acquisition uses existing read-only analytics configuration without
printing credentials. No paper/live worker or order endpoint is used.

Tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_discovery*.py'
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_diagnosis*.py'
.\.venv\Scripts\python.exe -m unittest research.swing_diagnosis.audit_tests
```

The 58 existing tests, six funded/feature tests and five audit regressions passed.
Portfolio scenarios reconcile terminal cash with realized P&L and enforce cash and
position invariants. Statistically favorable retrospective outcomes remain
conditional on selected rules, calendar reuse and the few observed regimes.
Independent stock-company reservations do not create a pristine temporal holdout.
