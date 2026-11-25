# V5 advanced model experiments

The program ran20 initially registered configurations, eight registered native/
timing/window follow-ups, four registered liquidity extensions and two cached
feature/law attribution cells:34 distinct evaluated systems, independently at
5/21 sessions. The searchable registry records701 configuration/fold
attempts:11 original Indian-only-forest metadata failures are preserved and all 11
were repaired without changing model parameters. Attribution evaluations reuse
cached estimators, so the ledger count is not the number of elementary model fits.

|ID|mechanism|inputs|hypothesis|
|---|---|---|---|
|E00|empirical|price|Unconditional return law|
|P00|ridge|price|Price-only coherent control|
|G00|ridge|global|Global-only predictive information|
|I00|ridge|indian|Native broad/sector internal structure|
|C00|ridge|combined|Global increment beyond Indian prices/sectors|
|F00|pca|combined|Five static train-only joint factors|
|F01|rolling_pca|combined|Causal rolling126 loading adaptation|
|N00|spline|core|Low-complexity additive nonlinear response|
|N01|forest|combined|Shallow randomized conditional return law|
|N02|kernel|core|Regularized smooth joint-state interaction|
|R00|regime|core|Global-risk x domestic-volatility conditional law|
|A00|cosine|joint_derivatives|Angular state analogue with shrinkage|
|A01|manhattan|joint_derivatives|Robust L1 state analogue with shrinkage|
|S00|ridge|sequence|Cross-market evolution beyond static state|
|T00|sector_transfer|core|Date-grouped shared sector-to-NIFTY mapping|
|T01|stock_transfer|core|Wider equity transfer, survivorship-exposed|
|M00|multitask|core|Normalized shared1/3/5/21-session tasks|
|D00|ridge|derivatives|Price x positioning x expiry risk|
|D01|ridge|joint_derivatives|Derivative increment beyond global/Indian state|
|BR00|ridge|proxy|Wider current-stock participation proxy|

Regularized Ridge alpha 100; train-only median/standardization/clipping±5;
PCA5(static or causal recent126 loading fit); additive quadratic splines with
three knots; RBF KernelRidge alpha 10,gamma1/d; ExtraTrees64/depth 3/minleaf30/
maxfeatures.7; cosine/L1 analogues40 neighbors; causal global-sign x training-
median-RV regime distributions with 50 unconditional pseudoobservations.
Most endpoint laws mix65% conditional heldout-residual or leaf/analogue mass
with 35% unconditional historical mass. This reduces unsupported finite-support
certainty but is a fixed heuristic, not certified calibration. All parameters
were fixed within each registered batch; no automatic hyperparameter search.

Multi-horizon M00 shares1/3/5/21 targets normalized bysqrt(h) with a log-horizon
coordinate, date-balanced tasks and individually matured labels. It fails to
improve primary horizons. Structured cross-market lags were actually tested.
Small temporal CNN/RNN/attention/Transformer models were not run:403 daily origins
and four disjoint monthly windows cannot validate an additional neural search.
Millions of intraday snapshots do not change that. XGBoost/CatBoost duplicate
sweeps were not added; new additive/kernel/conditional-forest mechanisms already
test nonlinear alternatives. Formal HMM/Markov and latent dynamic-factor models
were not claimed: causal observed regimes and rolling factors are narrower tests.

V5 did not stop after failed global/transfer/factor results. It followed the
domestic lead with registered source ablations and then genuinely new ETF/liquidity
inputs. Every inspected expansion adds to the multiple-comparison family. Failed
results remain in experiment-registry.csv/json, with exact model artifact hashes.
No V4 candidate, source code, protocol or prospective ledger was modified.

Full numerical reproduction completed in a new isolated directory without market
data requests: all 34 systems and 11,992 historical records matched. Probability
and Brier differences were exactly0; maximum CRPS difference was below7e-18.
This verifies repeatability, not independent validation. Original failed attempts
remain preserved; corrected code need not repeat the metadata bug in the replay.
Nonlinear comparisons also differ in representations, so a losing kernel/additive
implementation does not identify an architecture's universal causal weakness.
