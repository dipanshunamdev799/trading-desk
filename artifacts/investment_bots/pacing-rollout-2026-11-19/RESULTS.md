# Gradual investment paper deployment — 19 November 2026

The user-selected limits are active under `staged-paper-v1`:

- Maximum 10% of capital in new buys per trading session, up to ₹1 lakh per ₹10 lakh portfolio. The allowance falls if equity drops below starting capital.
- A 50% exposure cap when approving new buys. Subsequent price movements can change marked exposure.
- Maximum two filled buy orders per bot per session, including C1-R top-ups.
- A 5% per-stock entry cap. C2-S shares all limits across its five books, while each book retains its own cash.

A fresh run was activated with ₹10 lakh cash per strategy, no positions and zero P&L. Previous positions were retained in the original reference ledger, without fabricated closing trades or rewritten results. The dashboard's archive button and reference-scope exports expose those records.

Allocation-deferred entries stay queued for later sessions. A new selection replaces an outdated queue. C0-R-X retains its auction evidence gate, so rejected auction buys remain unfilled. C1-R does not concentrate its exposure target into the few names already entered during gradual deployment. Sells do not consume the buy allowance.

The new run begins with completed sessions from 19 November onward; it does not backdate earlier fills. Next-open results continue to reconcile the following morning. Restarting or repeating a cycle retains the same run ID and cannot create a second daily allowance. These are maximum limits, not required daily purchases.

Validation: 40 existing investment tests and 15 new deployment/integration tests passed. TypeScript and the production build passed. Runtime checks confirmed all four fresh balances, the original C0-R archive's 20 positions, current and archived exports, and byte-identical original session records. All 11 F&O definitions, configurations and requested states were unchanged.

The layout check confirmed no page-level overflow at 320px and 390px after correcting the investment cards' minimum widths. The full-site design gate also applies marketing-page rules to this existing application and flags remaining style checks; its detailed output is retained separately. It is not reported as a visual gate pass.

Implementation: `investment_bots/practice.py`, `investment_bots/service.py`, `investment_bots/db.py`, `backend/app/routers/investment_bots.py`, the investment dashboard and `backend/scripts/test_investment_pacing.py`. Paced execution has separate results and a separate policy fingerprint from the historically verified original strategy. PostgreSQL stores the policy, run seeds and immutable session records. No broker orders were submitted.
