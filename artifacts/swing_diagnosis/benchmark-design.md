# Frozen benchmark diagnosis plan

This plan precedes benchmark outcome calculations. Existing research is read-only.

1. Reproduce same-cost buy-and-hold sleeves from existing outputs.
2. Two fixed simple rules: close above SMA-seeded EMA200, and positive prior60-session return. Both use the same 2ATR stop, fee-aware2R target,10-session cap,0.5%cash risk,1%lag-volume cap,5bpsfills and delivery fees as prior tests. These are signal controls, not optimized trend/momentum portfolios.
3. Twenty random-entry seeds (20261111..20261130), Bernoulli completed-day events. Per-stock probability equals mean raw entry-event frequency across48frozen rules during development2024-11-10..2025-11-10. It is then fixed for validation/final. This is a frequency-matched control; actual trade counts can differ because rule entries cluster and positions block entries. Retrospective development performance is not OOS. No seed is selected.
4. Evaluate all470eligible stocks, development, validation, final and fulltwo-year. Same calendar and portfolio metrics, exposure, gross/net, turnover measured from actual fills. Zero-cost reruns of controls answer cost sensitivity; they are not realistic tradable forecasts.
5. Obtain official NIFTY50TRI,NIFTY500TRI and NIFTYBank/IT/Pharma sectorTRI daily history through official index website endpoint. Cache raw response and status. If unavailable, mark missing; never relabel price index as TRI.
6. Examine official historical constituent/archive and adjusted data feasibility for5-10years. Current2024frozen universe cannot be backdated as historically selected.

New study dates are contaminated by earlier market-history use. No new untouched holdout is claimed. Index returns are fully invested published totalreturn with dividend reinvestment, no tradableETFcost; sleeve rules retain cash and cannot be interpreted as exposurematched alpha.
