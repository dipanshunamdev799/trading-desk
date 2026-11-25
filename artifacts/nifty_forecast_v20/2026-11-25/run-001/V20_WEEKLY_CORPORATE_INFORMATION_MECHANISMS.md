# V20 Weekly Corporate Information Mechanisms

The weekly comparison uses the same native 09:10 V14 law. V18's full corporate residual is replayed exactly, with its input snapshot frozen at 08:55. The decomposition tests counts, signed semantic aggregates, period-matched financial surprises, sector weights, scheduled earnings and disagreement with the observed corporate price response. It also fits historical bias, position-only and combined position/corporate corrections. The archived V18 overlay and the V20 refit of a similar feature list have different reported rows so training coverage and regularization remain visible.

The activation and subgroup thresholds for announcement intensity use only available earlier observations. A high intensity date has a count rank of at least **0.70**. Every subgroup is compared with its own unchanged V14 parent on the exact same dates. Sign-probability reweighting keeps within-sign shapes, while scale-only and asymmetry-only modifications preserve full empirical laws.

| model | n | active | disjoint | brier | crps | log loss | covered | width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| asymmetry_only | 265 | 223 | 53 | 0.228104 | 0.010399 | 0.648044 | 0.826415 | 0.045761 |
| bias_only | 265 | 223 | 53 | 0.226018 | 0.010396 | 0.644569 | 0.818868 | 0.045703 |
| calendar | 265 | 223 | 53 | 0.223932 | 0.010319 | 0.640023 | 0.826415 | 0.045697 |
| corporate_plus_positioning | 265 | 223 | 53 | 0.230660 | 0.010331 | 0.652742 | 0.815094 | 0.045758 |
| corporate_v18_feature_set | 265 | 223 | 53 | 0.223838 | 0.010326 | 0.638662 | 0.818868 | 0.045704 |
| counts | 265 | 223 | 53 | 0.224304 | 0.010307 | 0.639830 | 0.822642 | 0.045735 |
| exact_v14 | 265 | 265 | 53 | 0.228529 | 0.010457 | 0.648943 | 0.826415 | 0.045780 |
| lag1 | 265 | 223 | 53 | 0.226081 | 0.010421 | 0.643574 | 0.807547 | 0.045708 |
| lag21 | 265 | 223 | 53 | 0.227032 | 0.010438 | 0.644137 | 0.830189 | 0.045692 |
| lag5 | 265 | 223 | 53 | 0.228049 | 0.010590 | 0.648241 | 0.822642 | 0.045690 |
| location_scale_asymmetry | 265 | 223 | 53 | 0.221956 | 0.010420 | 0.633662 | 0.815094 | 0.045789 |
| positioning_only | 265 | 223 | 53 | 0.234786 | 0.010547 | 0.662234 | 0.818868 | 0.045758 |
| preceding_evening | 265 | 223 | 53 | 0.223393 | 0.010347 | 0.637967 | 0.811321 | 0.045703 |
| price_reaction | 265 | 223 | 53 | 0.223384 | 0.010258 | 0.638699 | 0.830189 | 0.045719 |
| probability_only | 265 | 223 | 53 | 0.225928 | 0.010457 | 0.643400 | 0.830189 | 0.045594 |
| scale_only | 265 | 223 | 53 | 0.227652 | 0.010503 | 0.647336 | 0.803774 | 0.045901 |
| semantics | 265 | 223 | 53 | 0.225560 | 0.010415 | 0.643375 | 0.822642 | 0.045700 |
| slopes_without_intercept | 265 | 223 | 53 | 0.225022 | 0.010341 | 0.641167 | 0.807547 | 0.045775 |
| structured | 265 | 223 | 53 | 0.230514 | 0.010535 | 0.654114 | 0.815094 | 0.045699 |
| v18_corporate_native | 265 | 265 | 53 | 0.223481 | 0.010318 | 0.637789 | 0.818868 | 0.045700 |
| weighting | 265 | 223 | 53 | 0.229082 | 0.010473 | 0.650851 | 0.822642 | 0.045727 |

| cohort | regime | n | disjoint | mean n train | v19 brier gain | new brier gain | new crps gain |
| --- | --- | --- | --- | --- | --- | --- | --- |
| early | high_announcement | 45 | 12 | 110.200000 | -0.020195 | -0.019114 | -0.000682 |
| later | high_announcement | 33 | 9 | 140.000000 | 0.009123 | -0.005656 | -0.000348 |
| early | other_announcement | 86 | 21 | 94.511628 | -0.003322 | 0.012760 | 0.000730 |
| later | other_announcement | 59 | 14 | 140.000000 | -0.012962 | 0.020211 | 0.000236 |

[native-mechanism-cases.csv.gz](native-mechanism-cases.csv.gz) · [native-config.json](native-config.json) · [mechanism-regime-comparisons.csv](mechanism-regime-comparisons.csv) · [matched-block-intervals.csv.gz](matched-block-intervals.csv.gz) · [native-audit-null-replay.csv](native-audit-null-replay.csv) · [probability-calibration.csv](probability-calibration.csv)
