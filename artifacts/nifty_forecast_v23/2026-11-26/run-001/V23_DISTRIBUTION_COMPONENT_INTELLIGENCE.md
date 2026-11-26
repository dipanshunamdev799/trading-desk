# V23 Distribution component intelligence

A coherent law starts with the protected endpoint atoms. Location changes translate the atoms in log-price space.
Dispersion changes are bounded scoreable stretches informed by the annualized IV or GJR reference at an eligible
clock. The sign-only intervention changes probability weights within each side. A monotone skew transform preserves
ordering. Tail-only transport borrows fixed tail mass from an earlier historical law. The combined construction uses
consistent atoms or a valid complete-law mixture, yielding the mean, median, interval, sign and tails from one law.

The cleanest result was the monthly domestic historical shape transformed to the original positioning parent's
log median and interdecile spread. The weekly reference still benefited modestly from changing location.

| horizon | model | n | brier | crps | coverage80 | width80 | tail down brier | tail up brier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | component_asymmetry_only | 265 | 0.222387 | 0.010172 | 0.826415 | 0.045423 | 0.117965 | 0.092495 |
| 5 | component_coherent_joint | 265 | 0.221733 | 0.010181 | 0.856604 | 0.050273 | 0.115649 | 0.096538 |
| 5 | component_historical_shape_only | 265 | 0.226389 | 0.010250 | 0.811321 | 0.045797 | 0.119018 | 0.094626 |
| 5 | component_iv_gjr_scale_only | 265 | 0.222185 | 0.010119 | 0.833962 | 0.046475 | 0.116812 | 0.092260 |
| 5 | component_location_only | 265 | 0.220248 | 0.010090 | 0.830189 | 0.045829 | 0.116314 | 0.093640 |
| 5 | component_sign_only | 265 | 0.221079 | 0.010111 | 0.833962 | 0.046000 | 0.116899 | 0.092648 |
| 5 | component_tail_only | 265 | 0.222778 | 0.010157 | 0.860377 | 0.049995 | 0.115787 | 0.094364 |
| 5 | protected_direction | 265 | 0.220133 | 0.010180 | 0.826415 | 0.045773 | 0.117409 | 0.095302 |
| 5 | protected_distribution | 265 | 0.222142 | 0.010121 | 0.822642 | 0.045852 | 0.117155 | 0.091805 |
| 21 | component_asymmetry_only | 217 | 0.223835 | 0.023184 | 0.714286 | 0.071940 | 0.124501 | 0.068093 |
| 21 | component_coherent_joint | 217 | 0.225508 | 0.023243 | 0.778802 | 0.088379 | 0.121650 | 0.067701 |
| 21 | component_historical_shape_only | 217 | 0.210496 | 0.022911 | 0.705069 | 0.071099 | 0.123172 | 0.077664 |
| 21 | component_iv_gjr_scale_only | 217 | 0.225082 | 0.023171 | 0.741935 | 0.080213 | 0.122930 | 0.066610 |
| 21 | component_location_only | 217 | 0.223058 | 0.023277 | 0.700461 | 0.071807 | 0.124345 | 0.069531 |
| 21 | component_sign_only | 217 | 0.222984 | 0.023179 | 0.709677 | 0.072823 | 0.124365 | 0.068499 |
| 21 | component_tail_only | 217 | 0.222793 | 0.023129 | 0.746544 | 0.081671 | 0.122832 | 0.068205 |
| 21 | protected_direction | 217 | 0.223431 | 0.023174 | 0.755760 | 0.094566 | 0.119926 | 0.068586 |
| 21 | protected_distribution | 217 | 0.223819 | 0.023184 | 0.714286 | 0.071940 | 0.124501 | 0.068095 |

## Attribution of the monthly shape gain

Reweighting the original parent to the domestic shape's positive mass reproduces the entire Brier improvement
(the two arms have identical sign probabilities). With the original sign mass restored, the domestic shape has the
parent's Brier by construction. The supplemental reweighting arm preserves shapes conditional on sign. It slightly
changes unconditional quantiles as a mathematical consequence. Matching median and interdecile spread is enforced
for the original shape substitution, with the finite support quantile convention stated in the code.

| model | n | probability | brier | crps | coverage80 | width80 | log location | log scale | asymmetry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| domestic_shape_full | 217 | 0.549138 | 0.210496 | 0.022911 | 0.705069 | 0.071099 | 0.005075 | 0.027921 | -0.324712 |
| domestic_shape_with_parent_sign_mass | 217 | 0.579178 | 0.223819 | 0.023358 | 0.700461 | 0.072189 | 0.005845 | 0.028326 | -0.302577 |
| half_parent_half_domestic | 217 | 0.564158 | 0.216584 | 0.022939 | 0.737327 | 0.073880 | 0.005075 | 0.028864 | -0.180364 |
| parent_with_domestic_sign_mass | 217 | 0.549138 | 0.210496 | 0.022751 | 0.723502 | 0.071730 | 0.004052 | 0.027875 | -0.033857 |
| symmetrized_domestic_shape | 217 | 0.584821 | 0.215130 | 0.023373 | 0.714286 | 0.071962 | 0.005075 | 0.027921 | 0.000000 |
| unchanged_direction_parent | 217 | 0.569929 | 0.223431 | 0.023174 | 0.755760 | 0.094566 | 0.005433 | 0.036705 | -0.013678 |
| unchanged_distribution_parent | 217 | 0.579178 | 0.223819 | 0.023184 | 0.714286 | 0.071940 | 0.005075 | 0.027921 | -0.008023 |

A retrospective algebraic decomposition separates the contribution of the average probability shift from the additional date-varying effect. Against V21, the uniform shift contributes about 0.007592 of the 0.013323 Brier improvement and date-specific changes contribute 0.005731. This decomposition uses realized outcomes for attribution. It does not fit a historical forecasting rule.

| horizon | clock | scope | reference | n | realized up | parent mean probability | shape mean probability | brier gain | uniform mean shift gain | date varying gain |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | native_0910 | combined | unchanged_distribution_parent | 217 | 0.437788 | 0.579178 | 0.549138 | 0.013323 | 0.007592 | 0.005731 |
| 21 | native_0910 | combined | unchanged_direction_parent | 217 | 0.437788 | 0.569929 | 0.549138 | 0.012935 | 0.005062 | 0.007873 |
| 21 | native_0910 | early | unchanged_distribution_parent | 141 | 0.453901 | 0.547484 | 0.522586 | 0.005046 | 0.004040 | 0.001006 |
| 21 | native_0910 | early | unchanged_direction_parent | 141 | 0.453901 | 0.541835 | 0.522586 | 0.009407 | 0.003015 | 0.006393 |
| 21 | native_0910 | later | unchanged_distribution_parent | 76 | 0.407895 | 0.637978 | 0.598399 | 0.028678 | 0.016646 | 0.012031 |
| 21 | native_0910 | later | unchanged_direction_parent | 76 | 0.407895 | 0.622051 | 0.598399 | 0.019481 | 0.009571 | 0.009910 |

[domestic-shape-attribution-cases.csv.gz](domestic-shape-attribution-cases.csv.gz) · [domestic-shape-attribution-intervals.csv](domestic-shape-attribution-intervals.csv) · [v23-return-laws.npz](v23-return-laws.npz) · [original-horizon-matched-comparisons.csv.gz](original-horizon-matched-comparisons.csv.gz) · [domestic-shape-brier-decomposition.csv](domestic-shape-brier-decomposition.csv)

[Back to the research index](NIFTY_V23_RESEARCH.md)
