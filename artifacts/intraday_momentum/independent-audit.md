# Independent result audit

Audit date: **15 November 2026**. **Passed with the study's disclosed model limitations.** No strategy was rerun, no frozen artifact was edited, and no PostgreSQL write or real order was submitted.

Reviewed 24 base portfolios: **13,252 trade-ledger rows**, 11,880 daily-equity rows and 120 summaries. Independently recomputed each base-trade fee component, adverse 10bps fills, gross/net P&L, modeled slippage attribution, daily and terminal cash, and all reported base summary statistics. Verified integer quantities, cash collateral, decision-volume and entry-risk limits, next-open timing, one position, no daily stock reentry and three entries per day. **Zero discrepancies; maximum numeric difference: 4.1e-10.** These rows represent dependent variants, not independent observations.

All 60 stress-summary rows agree with their CSV. Stress trade ledgers are not exported, so stress executions were not independently recomputed. All 4,404 descriptive event rows reconcile with full and chronological counts/rates, exclusions, ambiguity counts and target/reversal levels. Current code, runner, plan and acquisition hashes match the research manifest. The report lists no execution failures.

The long-only 8% rules with and without the RVOL >= 1.5 gate produced exactly identical development and full-period executed ledgers for both stops; minimum executed RVOL was 1.5233. Short diagnostic ledgers differ, confirming distinct mechanisms. This observation does not establish that volume filters are ineffective; candidate-level rejection causes were not audited.

For `cross10-sl100-long_only`, fixed-path attribution reconciles: **Rs190,513.309 raw gross - Rs322,769.136 modeled slippage - Rs76,535.802 fees = -Rs208,791.629 net** across 417 trades, five ambiguous. This is attribution for fixed entries and quantities, not a zero-cost portfolio rerun.

Every full-period base portfolio lost money, and every primary configuration lost in every reported period slice. No development candidate qualified. The absence of a selected-model confidence interval and one-minute audit follows the frozen protocol. **No tested configuration qualifies for paper-bot selection.**

Arithmetic consistency does not certify historical fills, depth, circuits, short eligibility, exhaustive corporate actions or universal data coverage. The report's cohort, fee-plan, five-minute execution and pseudo-out-of-sample limitations remain applicable. Machine-readable details are in `independent-audit.json`.
