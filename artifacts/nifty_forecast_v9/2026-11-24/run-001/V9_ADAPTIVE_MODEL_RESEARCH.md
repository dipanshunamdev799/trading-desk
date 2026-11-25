# NIFTY V9 · Adaptive Model Research

Run `2026-11-24/run-001`. Historical research using 2025–2026 observations.

Time-varying models use the same compact domestic rotation inputs and prequential date calendar across both cohorts. Exponentially weighted Ridge uses fixed half-lives of 45 or 90 fitting observations and normalizes weights to preserve overall penalty scale. Regularized Kalman regression updates a small coefficient vector in matured same-horizon endpoint order. The process noise is fixed relative to training target variance, with a slower alternative. The historical calibration residuals are generated from a distinct purged inner fit. The threshold experts blend 40% of the applicable high/low volatility, trend or breadth expert with 60% pooled estimation. Training medians set thresholds. Short-window blending uses equal 126-date/expanding weights or chooses `.60` and `.15` on a predeclared causal feature-distribution threshold of `.75`. These are contemporaneous observed regimes. Hidden-state smoothing does not enter the experiment.

| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_HIST | 92 | 19 | 12.363138 | 0.576087 | 0.500000 | 0.258296 | 0.709964 | 0.012210 | 0.016374 | 0.023210 | 0.006135 | 0.500000 | 0.728261 | 0.039943 |
| P_COMPACT | 92 | 19 | 12.363138 | 0.554348 | 0.538703 | 0.252389 | 0.699219 | 0.011908 | 0.015752 | 0.022145 | 0.005906 | 0.369565 | 0.706522 | 0.034588 |
| T_EW90 | 92 | 19 | 12.363138 | 0.500000 | 0.481374 | 0.268731 | 0.736272 | 0.012356 | 0.016260 | 0.022514 | 0.006144 | 0.336957 | 0.728261 | 0.037518 |
| T_EW45 | 92 | 19 | 12.363138 | 0.510870 | 0.487421 | 0.289423 | 0.783991 | 0.013004 | 0.017042 | 0.023323 | 0.006451 | 0.336957 | 0.739130 | 0.038866 |
| T_KALMAN | 92 | 19 | 12.363138 | 0.543478 | 0.532656 | 0.255078 | 0.706620 | 0.012042 | 0.015845 | 0.022064 | 0.006005 | 0.347826 | 0.728261 | 0.036452 |
| T_KALMAN_SLOW | 92 | 19 | 12.363138 | 0.565217 | 0.558297 | 0.248168 | 0.691209 | 0.011818 | 0.015592 | 0.021844 | 0.005897 | 0.369565 | 0.717391 | 0.034945 |
| T_STATIC_BLEND | 92 | 19 | 12.363138 | 0.500000 | 0.481374 | 0.265779 | 0.727940 | 0.012379 | 0.016319 | 0.022787 | 0.006143 | 0.369565 | 0.673913 | 0.035715 |
| T_CHANGE_WINDOW | 92 | 19 | 12.363138 | 0.500000 | 0.481374 | 0.259961 | 0.714029 | 0.012184 | 0.016045 | 0.022716 | 0.006049 | 0.369565 | 0.695652 | 0.035642 |
| T_RECENT126 | 92 | 19 | 12.363138 | 0.532609 | 0.509676 | 0.269948 | 0.738004 | 0.012633 | 0.016603 | 0.023247 | 0.006263 | 0.369565 | 0.739130 | 0.038584 |
| T_EXPERT_PARENT | 92 | 19 | 12.363138 | 0.543478 | 0.522496 | 0.250952 | 0.697111 | 0.011824 | 0.015711 | 0.021895 | 0.005869 | 0.369565 | 0.695652 | 0.034388 |
| T_VOL_EXPERT | 92 | 19 | 12.363138 | 0.543478 | 0.522496 | 0.265205 | 0.727435 | 0.012313 | 0.016295 | 0.022516 | 0.006107 | 0.304348 | 0.684783 | 0.034944 |
| T_TREND_EXPERT | 92 | 19 | 12.363138 | 0.576087 | 0.550798 | 0.241974 | 0.677047 | 0.011684 | 0.015594 | 0.021970 | 0.005786 | 0.391304 | 0.684783 | 0.034292 |
| T_BREADTH_EXPERT | 92 | 19 | 12.363138 | 0.554348 | 0.531930 | 0.253251 | 0.700726 | 0.011923 | 0.015808 | 0.022201 | 0.005892 | 0.369565 | 0.684783 | 0.034777 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_HIST | 173 | 35 | 28.982745 | 0.445087 | 0.482119 | 0.259447 | 0.712156 | 0.010878 | 0.014956 | 0.019931 | 0.005409 | 0.473988 | 0.710983 | 0.036450 |
| P_COMPACT | 173 | 35 | 28.982745 | 0.462428 | 0.482996 | 0.323155 | 0.873586 | 0.013434 | 0.017990 | 0.024756 | 0.006685 | 0.445087 | 0.699422 | 0.043751 |
| T_EW90 | 173 | 35 | 28.982745 | 0.456647 | 0.474291 | 0.312061 | 0.842949 | 0.013152 | 0.017783 | 0.024365 | 0.006497 | 0.439306 | 0.705202 | 0.042776 |
| T_EW45 | 173 | 35 | 28.982745 | 0.468208 | 0.477935 | 0.307144 | 0.829782 | 0.013019 | 0.017713 | 0.024154 | 0.006429 | 0.433526 | 0.710983 | 0.042542 |
| T_KALMAN | 173 | 35 | 28.982745 | 0.468208 | 0.487112 | 0.320587 | 0.867531 | 0.013903 | 0.018726 | 0.025606 | 0.006835 | 0.462428 | 0.693642 | 0.044964 |
| T_KALMAN_SLOW | 173 | 35 | 28.982745 | 0.485549 | 0.502901 | 0.324708 | 0.879233 | 0.014045 | 0.018904 | 0.025912 | 0.006912 | 0.462428 | 0.687861 | 0.045645 |
| T_STATIC_BLEND | 173 | 35 | 28.982745 | 0.450867 | 0.466734 | 0.311720 | 0.841691 | 0.013022 | 0.017597 | 0.024190 | 0.006471 | 0.462428 | 0.699422 | 0.042115 |
| T_CHANGE_WINDOW | 173 | 35 | 28.982745 | 0.485549 | 0.501754 | 0.306432 | 0.829044 | 0.012857 | 0.017388 | 0.023999 | 0.006383 | 0.485549 | 0.705202 | 0.042138 |
| T_RECENT126 | 173 | 35 | 28.982745 | 0.462428 | 0.469231 | 0.305010 | 0.825932 | 0.013594 | 0.018449 | 0.025801 | 0.006634 | 0.404624 | 0.693642 | 0.043277 |
| T_EXPERT_PARENT | 173 | 35 | 28.982745 | 0.485549 | 0.499460 | 0.320313 | 0.866250 | 0.013597 | 0.018199 | 0.025054 | 0.006774 | 0.445087 | 0.693642 | 0.043785 |
| T_VOL_EXPERT | 173 | 35 | 28.982745 | 0.485549 | 0.499460 | 0.322169 | 0.871450 | 0.013571 | 0.018157 | 0.025067 | 0.006747 | 0.445087 | 0.687861 | 0.043343 |
| T_TREND_EXPERT | 173 | 35 | 28.982745 | 0.468208 | 0.483671 | 0.319271 | 0.862723 | 0.013361 | 0.017942 | 0.024682 | 0.006679 | 0.439306 | 0.693642 | 0.043152 |
| T_BREADTH_EXPERT | 173 | 35 | 28.982745 | 0.473988 | 0.487787 | 0.315624 | 0.855042 | 0.013339 | 0.017847 | 0.024577 | 0.006642 | 0.445087 | 0.693642 | 0.043562 |


The adaptive regressions did not automatically restore later performance. Compact representation itself is a different design from full native V8 and is explicitly controlled. The later native residual rotation and structure parents survive better than the compact dynamic alternatives. The earlier compact fits still tend to lose to the empirical benchmark. A true future regime-changing model remains unproven.

The expert layer uses seven complete law parents: native, residual rotation, structural changes, cluster-balanced Elastic Net, ETF activity, a simple reversion law and historical. `J9_EQUAL` is the equal-weight initial law and `J9_STATIC` then assigns half additional mass to history. Other options use recent strictly matured weighted losses, same-volatility past losses, regularized domestic/global reliability scores, or OOD shrinkage. Learned weights remain 60% equal and 40% soft estimates. Fall back to fixed weights below the fit threshold. See `expert-weights.csv` for every allocation.

| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J9_EQUAL | 92 | 19 | 12.363138 | 0.804348 | 0.806483 | 0.192438 | 0.574227 | 0.010484 | 0.013861 | 0.020791 | 0.005274 | 0.532609 | 0.793478 | 0.040855 |
| J9_STATIC | 92 | 19 | 12.363138 | 0.760870 | 0.751814 | 0.221214 | 0.634997 | 0.011211 | 0.015054 | 0.021888 | 0.005594 | 0.576087 | 0.782609 | 0.042314 |
| J9_PERFORMANCE | 92 | 19 | 12.363138 | 0.804348 | 0.806483 | 0.185713 | 0.559731 | 0.010297 | 0.013537 | 0.020368 | 0.005185 | 0.543478 | 0.793478 | 0.040162 |
| J9_DOMESTIC_GATE | 92 | 19 | 12.363138 | 0.815217 | 0.819303 | 0.188234 | 0.565092 | 0.010372 | 0.013682 | 0.020460 | 0.005212 | 0.554348 | 0.793478 | 0.040532 |
| J9_GLOBAL_GATE | 92 | 19 | 12.363138 | 0.793478 | 0.797049 | 0.189435 | 0.567980 | 0.010442 | 0.013825 | 0.020618 | 0.005243 | 0.543478 | 0.793478 | 0.040781 |
| J9_OOD | 92 | 19 | 12.363138 | 0.750000 | 0.742380 | 0.195789 | 0.580989 | 0.010556 | 0.013937 | 0.021020 | 0.005326 | 0.521739 | 0.793478 | 0.040832 |
| J9_REGIME | 92 | 19 | 12.363138 | 0.793478 | 0.797049 | 0.191414 | 0.572115 | 0.010459 | 0.013798 | 0.020733 | 0.005256 | 0.532609 | 0.793478 | 0.040831 |
| J9_REL_SHRINK | 92 | 19 | 12.363138 | 0.706522 | 0.680939 | 0.225095 | 0.642610 | 0.011230 | 0.015123 | 0.021816 | 0.005595 | 0.576087 | 0.771739 | 0.042474 |


| model | n | disjoint | ESS | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J9_EQUAL | 173 | 35 | 28.982745 | 0.526012 | 0.544332 | 0.272295 | 0.746437 | 0.011816 | 0.016491 | 0.022347 | 0.005861 | 0.491329 | 0.791908 | 0.049830 |
| J9_STATIC | 173 | 35 | 28.982745 | 0.485549 | 0.507490 | 0.259548 | 0.713391 | 0.010933 | 0.015204 | 0.020492 | 0.005428 | 0.491329 | 0.797688 | 0.045704 |
| J9_PERFORMANCE | 173 | 35 | 28.982745 | 0.514451 | 0.533806 | 0.270750 | 0.742547 | 0.011606 | 0.016195 | 0.021999 | 0.005757 | 0.491329 | 0.803468 | 0.049597 |
| J9_DOMESTIC_GATE | 173 | 35 | 28.982745 | 0.514451 | 0.533806 | 0.274797 | 0.752603 | 0.011778 | 0.016359 | 0.022223 | 0.005856 | 0.479769 | 0.803468 | 0.049754 |
| J9_GLOBAL_GATE | 173 | 35 | 28.982745 | 0.520231 | 0.539069 | 0.273725 | 0.749953 | 0.011732 | 0.016335 | 0.022133 | 0.005834 | 0.479769 | 0.797688 | 0.049764 |
| J9_OOD | 173 | 35 | 28.982745 | 0.491329 | 0.512753 | 0.264420 | 0.726925 | 0.011463 | 0.016047 | 0.021236 | 0.005695 | 0.508671 | 0.791908 | 0.048717 |
| J9_REGIME | 173 | 35 | 28.982745 | 0.514451 | 0.533806 | 0.273152 | 0.748214 | 0.011772 | 0.016417 | 0.022219 | 0.005843 | 0.485549 | 0.797688 | 0.049733 |
| J9_REL_SHRINK | 173 | 35 | 28.982745 | 0.491329 | 0.513900 | 0.261291 | 0.717179 | 0.010899 | 0.015088 | 0.020097 | 0.005404 | 0.479769 | 0.768786 | 0.041135 |


| model | n | disjoint | brier | crps | early_Brier | late_Brier | early_CRPS | late_CRPS | abs_Brier_cohort_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P_CLUSTER | 265 | 53 | 0.236386 | 0.011775 | 0.260773 | 0.190529 | 0.012473 | 0.010463 | 0.070243 |
| J9_OOD | 265 | 53 | 0.240593 | 0.011148 | 0.264420 | 0.195789 | 0.011463 | 0.010556 | 0.068631 |
| J9_PERFORMANCE | 265 | 53 | 0.241228 | 0.011151 | 0.270750 | 0.185713 | 0.011606 | 0.010297 | 0.085037 |
| J9_GLOBAL_GATE | 265 | 53 | 0.244462 | 0.011284 | 0.273725 | 0.189435 | 0.011732 | 0.010442 | 0.084290 |
| J9_EQUAL | 265 | 53 | 0.244571 | 0.011354 | 0.272295 | 0.192438 | 0.011816 | 0.010484 | 0.079856 |
| J9_DOMESTIC_GATE | 265 | 53 | 0.244745 | 0.011290 | 0.274797 | 0.188234 | 0.011778 | 0.010372 | 0.086563 |
| J9_REGIME | 265 | 53 | 0.244775 | 0.011316 | 0.273152 | 0.191414 | 0.011772 | 0.010459 | 0.081738 |
| J9_STATIC | 265 | 53 | 0.246239 | 0.011029 | 0.259548 | 0.221214 | 0.010933 | 0.011211 | 0.038333 |
| J9_REL_SHRINK | 265 | 53 | 0.248725 | 0.011014 | 0.261291 | 0.225095 | 0.010899 | 0.011230 | 0.036197 |
| P_LIQ | 265 | 53 | 0.249811 | 0.012036 | 0.294561 | 0.165661 | 0.013121 | 0.009997 | 0.128900 |
| P_STRUCTURE | 265 | 53 | 0.250845 | 0.012056 | 0.296317 | 0.165337 | 0.013358 | 0.009608 | 0.130980 |
| P_ROT | 265 | 53 | 0.252015 | 0.012108 | 0.298696 | 0.164236 | 0.013232 | 0.009995 | 0.134460 |
| P_NATIVE | 265 | 53 | 0.255388 | 0.012233 | 0.298275 | 0.174742 | 0.013274 | 0.010276 | 0.123533 |
| P_HIST | 265 | 53 | 0.259048 | 0.011340 | 0.259447 | 0.258296 | 0.010878 | 0.012210 | 0.001152 |
| P_MOMENTUM | 265 | 53 | 0.269699 | 0.012073 | 0.283074 | 0.244548 | 0.012161 | 0.011907 | 0.038526 |
| P_COMPACT | 265 | 53 | 0.298587 | 0.012904 | 0.323155 | 0.252389 | 0.013434 | 0.011908 | 0.070766 |
| P_REVERT | 265 | 53 | 0.301263 | 0.012836 | 0.279024 | 0.343082 | 0.011707 | 0.014961 | 0.064058 |


The recent-performance combination improves combined Brier/CRPS versus equal weighting, and OOD/history blends reduce early losses for relatively modest later deterioration against equal weighting. The frozen later rotation benchmark remains better on the later sample. A simple fixed fallback is as competitive as more elaborate reliability weighting for combined CRPS. These comparisons favor keeping shrinkage as a control when evaluating adaptation rather than assuming learning helps.

Returns, CRPS and interval width use fractional units. Positive loss gain means matched benchmark loss minus candidate loss. All historical evaluations are exposed to the research program.
