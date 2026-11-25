# NIFTY V8 · Monthly Persistence And Falsification

Run `2026-11-24/run-001`. Retrospective research.

V8 finds a lower historical monthly point score after averaging each reconstructed weekly forecast state over its prior 21 sessions. With current price and risk inputs `M_STATE_SMOOTH` reaches **.136132 Brier**, **.021511 CRPS** and **78.95%** nominal-80 coverage. A 126-date fit variant improves those point losses to **.132367 and .020474** with **85.53%** coverage. They lie on a sample with four disjoint windows. The ordinary price-plus-current-weekly-state fit scores **.249270** Brier, state without price **.222769**, a 21-session lagged raw state plus current price **.171065**, and price only **.404564**. The simple price persistence, reversion and historical-frequency controls expose how much the state result depends on the regime and training eligibility dates.

| model | n | disjoint | accuracy | balanced_accuracy | brier | log_loss | crps | mae | rmse | pinball | coverage50 | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V6_MONTH_STATE | 76 | 4 | 0.815789 | 0.834409 | 0.178345 | 0.543811 | 0.024823 | 0.033410 | 0.043058 | 0.012087 | 0.381579 | 0.657895 | 0.076202 |
| V6_MONTH_LAG1 | 76 | 4 | 0.750000 | 0.763799 | 0.175091 | 0.534801 | 0.024530 | 0.032281 | 0.043442 | 0.012149 | 0.328947 | 0.605263 | 0.072894 |
| V7_M_STATE_LAG21 | 76 | 4 | 0.763158 | 0.734767 | 0.171774 | 0.520543 | 0.025530 | 0.029936 | 0.048493 | 0.012927 | 0.697368 | 0.842105 | 0.093292 |
| V7_M_STATE_SHIFT5 | 76 | 4 | 0.684211 | 0.718280 | 0.190366 | 0.561496 | 0.023773 | 0.030176 | 0.042107 | 0.011846 | 0.368421 | 0.644737 | 0.073489 |
| V7_M_STATE_SHIFT21 | 76 | 4 | 0.631579 | 0.663799 | 0.187515 | 0.548883 | 0.024168 | 0.027607 | 0.042551 | 0.012028 | 0.631579 | 0.710526 | 0.080660 |
| M_HIST | 76 | 4 | 0.592105 | 0.500000 | 0.271313 | 0.736644 | 0.028335 | 0.038495 | 0.049888 | 0.013923 | 0.184211 | 0.828947 | 0.107385 |
| M_PRICE | 76 | 4 | 0.394737 | 0.483871 | 0.404564 | 1.061923 | 0.035624 | 0.043298 | 0.053788 | 0.017475 | 0.276316 | 0.421053 | 0.078195 |
| M_ONLY_STATE | 76 | 4 | 0.526316 | 0.564875 | 0.222769 | 0.636194 | 0.027749 | 0.035332 | 0.046679 | 0.013831 | 0.368421 | 0.565789 | 0.074677 |
| M_BOTH | 76 | 4 | 0.447368 | 0.533333 | 0.249270 | 0.690568 | 0.029510 | 0.037660 | 0.045806 | 0.014619 | 0.302632 | 0.447368 | 0.072803 |
| M_LAG_STATE | 76 | 4 | 0.763158 | 0.734767 | 0.171065 | 0.519084 | 0.025372 | 0.029730 | 0.047942 | 0.012830 | 0.710526 | 0.842105 | 0.091050 |
| M_LAG_PRICE | 76 | 4 | 0.657895 | 0.645878 | 0.236675 | 0.669227 | 0.032583 | 0.042046 | 0.052163 | 0.015810 | 0.328947 | 0.526316 | 0.081856 |
| M_ROLL_STATE | 76 | 4 | 0.684211 | 0.728315 | 0.183764 | 0.541081 | 0.023941 | 0.027512 | 0.041943 | 0.011866 | 0.644737 | 0.697368 | 0.080217 |
| M_BLOCK_TARGET | 76 | 4 | 0.381579 | 0.337276 | 0.274672 | 0.735886 | 0.029940 | 0.037553 | 0.049991 | 0.014953 | 0.473684 | 0.684211 | 0.096297 |
| M_STATE_SMOOTH | 76 | 4 | 0.789474 | 0.741935 | 0.136132 | 0.434581 | 0.021511 | 0.024518 | 0.041492 | 0.010882 | 0.736842 | 0.789474 | 0.079050 |
| M_INNOVATION | 76 | 4 | 0.644737 | 0.700000 | 0.310461 | 0.858401 | 0.031611 | 0.041152 | 0.050497 | 0.015588 | 0.263158 | 0.578947 | 0.085497 |
| M_PERSIST | 76 | 4 | 0.407895 | 0.500000 | 0.371925 | 0.988318 | 0.034597 | 0.044399 | 0.052822 | 0.017024 | 0.276316 | 0.447368 | 0.090058 |
| M_REVERT | 76 | 4 | 0.105263 | 0.098925 | 0.398992 | 1.033308 | 0.033343 | 0.042750 | 0.052491 | 0.016384 | 0.105263 | 0.460526 | 0.064459 |
| M_CONTINUE | 76 | 4 | 0.250000 | 0.231183 | 0.340776 | 0.887950 | 0.033333 | 0.041209 | 0.055347 | 0.016778 | 0.315789 | 0.618421 | 0.087354 |
| M_LAG_RETURN | 76 | 4 | 0.302632 | 0.370968 | 0.383279 | 1.009143 | 0.036536 | 0.045674 | 0.055718 | 0.018079 | 0.250000 | 0.421053 | 0.084851 |
| MS_STATE_ONLY | 76 | 4 | 0.592105 | 0.500000 | 0.215015 | 0.607492 | 0.027479 | 0.033255 | 0.047184 | 0.013531 | 0.460526 | 0.789474 | 0.095166 |
| MS_LAG5 | 76 | 4 | 0.592105 | 0.500000 | 0.201125 | 0.576084 | 0.027521 | 0.031314 | 0.047572 | 0.013471 | 0.657895 | 0.828947 | 0.097532 |
| MS_LAG21 | 76 | 4 | 0.486842 | 0.501434 | 0.291290 | 0.787325 | 0.035996 | 0.046930 | 0.059362 | 0.017342 | 0.394737 | 0.644737 | 0.099709 |
| MS_WINDOW | 76 | 4 | 0.855263 | 0.822581 | 0.132367 | 0.432753 | 0.020474 | 0.023172 | 0.038494 | 0.010393 | 0.763158 | 0.855263 | 0.085563 |
| MS_ROLL | 76 | 4 | 0.907895 | 0.917204 | 0.108239 | 0.381136 | 0.024107 | 0.027235 | 0.039497 | 0.011809 | 0.618421 | 0.763158 | 0.091329 |
| MS_PERMUTE | 76 | 4 | 0.789474 | 0.756989 | 0.196626 | 0.582574 | 0.025603 | 0.030069 | 0.046349 | 0.012912 | 0.539474 | 0.802632 | 0.100159 |
| MS_EMBARGO | 53 | 3 | 0.905660 | 0.807692 | 0.121300 | 0.413560 | 0.027445 | 0.034585 | 0.049826 | 0.013600 | 0.603774 | 0.716981 | 0.070657 |
| MS_MATCH_PRICE | 53 | 3 | 0.226415 | 0.461538 | 0.502525 | 1.293511 | 0.047454 | 0.059756 | 0.064623 | 0.022830 | 0.037736 | 0.188679 | 0.077310 |
| MS_MATCH_NOW | 53 | 3 | 0.905660 | 0.833654 | 0.132208 | 0.430048 | 0.027468 | 0.034105 | 0.050464 | 0.013737 | 0.528302 | 0.660377 | 0.072708 |
| MS_MATCH_LAG5 | 53 | 3 | 0.754717 | 0.500000 | 0.140206 | 0.441337 | 0.027898 | 0.033397 | 0.053052 | 0.013938 | 0.547170 | 0.716981 | 0.080992 |
| MS_MATCH_LAG21 | 53 | 3 | 0.396226 | 0.262500 | 0.336433 | 0.901843 | 0.039677 | 0.050353 | 0.066772 | 0.019403 | 0.207547 | 0.622642 | 0.078675 |
| MS_MATCH_ROLL | 53 | 3 | 0.962264 | 0.949038 | 0.080609 | 0.320057 | 0.026153 | 0.030710 | 0.045226 | 0.012988 | 0.566038 | 0.679245 | 0.082946 |


The smoothed-state timing mechanism fails scrutiny. A fit-only 21-session circular roll of the smoothed inputs gives **.108239 Brier** on the same 76 origins, although CRPS worsens to .024107. On the stricter 53-origin common availability cohort, the smoothed current model scores **.132208 Brier and .027468 CRPS** and the shifted-state placebo reaches **.080609 and .026153**. Genuine 21-session delayed smoothed states give **.336433** Brier there. Five-session delayed smoothed states hold up better. Unsurprisingly, older signals and altered dates can preserve broad persistent conditions. The circular controls wrap only allowed historical fitting rows and are labeled diagnostics. The target-block permutations disturb alignment without flattening all serial structure. They do not supply independent probability intervals. July on the stricter availability cohort and one earlier-cutoff smoothed fold did not fit under the inner sample requirement. V7's .024530 monthly CRPS remains a historical comparison; several new point estimates improve it, yet shifted controls and starting-date sensitivity still undermine independent conclusions.

| model | baseline | metric | n | gain | simultaneous95_block10 |
| --- | --- | --- | --- | --- | --- |
| MS_MATCH_NOW | V6_MONTH_LAG1 | brier | 53 | 0.045950 | — |
| MS_MATCH_NOW | V6_MONTH_LAG1 | crps | 53 | 0.003530 | — |
| MS_MATCH_NOW | V7_M_STATE_LAG21 | brier | 53 | 0.039331 | — |
| MS_MATCH_NOW | V7_M_STATE_LAG21 | crps | 53 | 0.002167 | — |
| MS_MATCH_ROLL | V6_MONTH_LAG1 | brier | 53 | 0.097549 | — |
| MS_MATCH_ROLL | V6_MONTH_LAG1 | crps | 53 | 0.004844 | — |
| MS_MATCH_ROLL | V7_M_STATE_LAG21 | brier | 53 | 0.090930 | — |
| MS_MATCH_ROLL | V7_M_STATE_LAG21 | crps | 53 | 0.003482 | — |
| MS_ROLL | V6_MONTH_LAG1 | brier | 76 | 0.066852 | — |
| MS_ROLL | V6_MONTH_LAG1 | crps | 76 | 0.000424 | — |
| MS_ROLL | V7_M_STATE_LAG21 | brier | 76 | 0.063535 | — |
| MS_ROLL | V7_M_STATE_LAG21 | crps | 76 | 0.001423 | — |
| MS_WINDOW | V6_MONTH_LAG1 | brier | 76 | 0.042725 | — |
| MS_WINDOW | V6_MONTH_LAG1 | crps | 76 | 0.004057 | — |
| MS_WINDOW | V7_M_STATE_LAG21 | brier | 76 | 0.039408 | — |
| MS_WINDOW | V7_M_STATE_LAG21 | crps | 76 | 0.005056 | — |
| M_STATE_SMOOTH | V6_MONTH_LAG1 | brier | 76 | 0.038960 | — |
| M_STATE_SMOOTH | V6_MONTH_LAG1 | crps | 76 | 0.003020 | — |
| M_STATE_SMOOTH | V7_M_STATE_LAG21 | brier | 76 | 0.035643 | — |
| M_STATE_SMOOTH | V7_M_STATE_LAG21 | crps | 76 | 0.004019 | — |


| model | metric | kind | min_gain | max_gain | positive |
| --- | --- | --- | --- | --- | --- |
| MS_MATCH_NOW | brier | disjoint_phase | 0.047878 | 0.119270 | 5/5 |
| MS_MATCH_NOW | brier | leave_month | 0.028032 | 0.069965 | 3/3 |
| MS_MATCH_NOW | brier | remove_top_gain | 0.024135 | 0.042111 | 4/4 |
| MS_MATCH_NOW | crps | disjoint_phase | 0.000809 | 0.005435 | 5/5 |
| MS_MATCH_NOW | crps | leave_month | 0.001392 | 0.005138 | 3/3 |
| MS_MATCH_NOW | crps | remove_top_gain | 0.001642 | 0.003269 | 4/4 |
| MS_WINDOW | brier | disjoint_phase | -0.045610 | 0.059383 | 3/5 |
| MS_WINDOW | brier | leave_month | 0.000564 | 0.087403 | 4/4 |
| MS_WINDOW | brier | remove_top_gain | -0.003963 | 0.037916 | 3/4 |
| MS_WINDOW | crps | disjoint_phase | 0.001946 | 0.007245 | 5/5 |
| MS_WINDOW | crps | leave_month | 0.002175 | 0.005942 | 4/4 |
| MS_WINDOW | crps | remove_top_gain | 0.001345 | 0.003662 | 4/4 |
| M_STATE_SMOOTH | brier | disjoint_phase | -0.001408 | 0.059339 | 4/5 |
| M_STATE_SMOOTH | brier | leave_month | -0.009735 | 0.082004 | 3/4 |
| M_STATE_SMOOTH | brier | remove_top_gain | -0.007106 | 0.034101 | 3/4 |
| M_STATE_SMOOTH | crps | disjoint_phase | 0.003583 | 0.004964 | 5/5 |
| M_STATE_SMOOTH | crps | leave_month | 0.000980 | 0.004508 | 4/4 |
| M_STATE_SMOOTH | crps | remove_top_gain | 0.000946 | 0.002789 | 4/4 |


No monthly superiority claim follows from four disjoint windows. The 10- and 15-session diagnostics use the same monthly origin cohort and retain their own targets and empirical benchmarks. Shorter horizon gains do not replace the primary definitions. [Monthly persistence figure](monthly-persistence-falsification.png)

All scores use exposed 2025–2026 history through the frozen November 17 close. Use gain as benchmark loss minus model loss. CRPS, return MAE and interval width are fractional returns.
