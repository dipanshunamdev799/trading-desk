# V23 Historical path shape research

The 08:55 experiments preserve each original return window and realized OHLC outcome, and reuse the day's protected
point volatility forecast for the candidate laws. Weekly candidates scale to the offshore-plus-domestic point reference.
Monthly candidates scale to the GJR point reference. A common multiplier maps the mean simulated realized volatility
to the anchor. Each path still has its own sequence of returns, gaps and ranges.

The structure trials compare the original joint paths, constant-volatility bridges, Student-t GJR paths, contiguous
domestic analogues, random windows, volatility matches, shuffled intact daily candles and independent daily candles.
Gap removal keeps close-to-close returns and reassigns the opening move within the session. Removing excursions
clips the observed high and low to the open and close. A separate law forces every entire scenario to have the same
realized volatility, and an ablation removes donor volatility variation before re-anchoring. One preset law is 12%
wider. Donor volatility and realized returns enter only after the complete donor path matures.

| horizon | model | n | rv mae | range crps | range covered | drawdown crps | expansion brier | contraction brier | persistent direction brier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | analogue_india_on_IV_GJR | 265 | 0.036469 | 0.006159 | 0.864151 | 0.006139 | 0.155508 | 0.140539 | — |
| 5 | constant_vol_diffusion | 265 | 0.036469 | 0.006056 | 0.743396 | 0.006048 | 0.156766 | 0.127281 | 0.231332 |
| 5 | india_constant_scenario_risk | 265 | 0.036469 | 0.006485 | 0.600000 | 0.006153 | 0.233962 | 0.184906 | 0.236760 |
| 5 | india_gap_removed | 265 | 0.036469 | 0.006396 | 0.784906 | 0.006194 | 0.160515 | 0.136897 | 0.236760 |
| 5 | india_independent_days | 265 | 0.036469 | 0.005994 | 0.747170 | 0.006033 | 0.154524 | 0.130754 | 0.226689 |
| 5 | india_no_intraday_excursions | 265 | 0.036469 | 0.006738 | 0.784906 | 0.006194 | 0.160515 | 0.136897 | 0.236760 |
| 5 | india_random_same_episodes | 265 | 0.036469 | 0.006233 | 0.762264 | 0.006161 | 0.158726 | 0.136956 | 0.233943 |
| 5 | india_realized_donor_norm | 265 | 0.036469 | 0.006513 | 0.600000 | 0.006163 | 0.223041 | 0.170283 | 0.234637 |
| 5 | india_state_matched | 265 | 0.036469 | 0.006343 | 0.784906 | 0.006194 | 0.160515 | 0.136897 | 0.236760 |
| 5 | india_state_widened | 265 | 0.040795 | 0.006823 | 0.739623 | 0.006268 | 0.170774 | 0.140114 | 0.236760 |
| 5 | india_temporally_shuffled | 265 | 0.036469 | 0.006246 | 0.811321 | 0.006215 | 0.160515 | 0.136897 | 0.238332 |
| 5 | india_vol_same_episodes | 265 | 0.036469 | 0.006397 | 0.777358 | 0.006171 | 0.158792 | 0.136858 | 0.228911 |
| 5 | mixed_temporally_shuffled | 265 | 0.036469 | 0.006124 | 0.796226 | 0.006297 | 0.154036 | 0.138168 | 0.225786 |
| 5 | same_clock_GJR | 265 | 0.040097 | 0.006493 | 0.766038 | 0.005956 | 0.184671 | 0.148193 | — |
| 5 | same_clock_IV | 265 | 0.036801 | 0.005768 | 0.735849 | 0.005926 | 0.157940 | 0.131133 | — |
| 5 | student_t_gjr_same_anchor | 265 | 0.036469 | 0.006009 | 0.807547 | 0.006063 | 0.155261 | 0.134737 | 0.230803 |
| 21 | analogue_india_on_IV_GJR | 217 | 0.033103 | 0.014409 | 0.861751 | 0.013974 | 0.195207 | 0.117691 | — |
| 21 | constant_vol_diffusion | 217 | 0.033179 | 0.013819 | 0.686636 | 0.013912 | 0.195059 | 0.108808 | 0.004896 |
| 21 | india_constant_scenario_risk | 217 | 0.033179 | 0.014425 | 0.594470 | 0.013923 | 0.258065 | 0.133641 | 0.013113 |
| 21 | india_gap_removed | 217 | 0.033179 | 0.014195 | 0.824885 | 0.013709 | 0.198725 | 0.120840 | 0.013113 |
| 21 | india_independent_days | 217 | 0.033179 | 0.013644 | 0.705069 | 0.013941 | 0.191881 | 0.106899 | 0.004967 |
| 21 | india_no_intraday_excursions | 217 | 0.033179 | 0.014815 | 0.797235 | 0.013709 | 0.198725 | 0.120840 | 0.013113 |
| 21 | india_random_same_episodes | 217 | 0.033179 | 0.014269 | 0.829493 | 0.013799 | 0.198509 | 0.117071 | 0.011737 |
| 21 | india_realized_donor_norm | 217 | 0.033179 | 0.014321 | 0.594470 | 0.014051 | 0.258121 | 0.129992 | 0.012673 |
| 21 | india_state_matched | 217 | 0.033179 | 0.014230 | 0.824885 | 0.013709 | 0.198725 | 0.120840 | 0.013113 |
| 21 | india_state_widened | 217 | 0.033837 | 0.014390 | 0.806452 | 0.013746 | 0.187436 | 0.111367 | 0.013113 |
| 21 | india_temporally_shuffled | 217 | 0.033179 | 0.014291 | 0.774194 | 0.014450 | 0.198725 | 0.120840 | 0.005672 |
| 21 | india_vol_same_episodes | 217 | 0.033179 | 0.014426 | 0.815668 | 0.013754 | 0.199013 | 0.116159 | 0.014265 |
| 21 | mixed_temporally_shuffled | 217 | 0.033179 | 0.014609 | 0.764977 | 0.014588 | 0.188668 | 0.127864 | 0.005672 |
| 21 | same_clock_GJR | 217 | 0.037244 | 0.015488 | 0.737327 | 0.014113 | 0.207983 | 0.146967 | — |
| 21 | same_clock_IV | 217 | 0.040023 | 0.017179 | 0.585253 | 0.015369 | 0.203507 | 0.169197 | — |
| 21 | student_t_gjr_same_anchor | 217 | 0.033179 | 0.013868 | 0.797235 | 0.014097 | 0.181790 | 0.115301 | 0.004892 |

Monthly independent days and diffusion are competitive range baselines. In the original 192-draw experiment,
independent days scored 0.013644 and the constant-volatility diffusion 0.013819 against 0.014230 for state-matched
domestic windows. The independent-day law's drawdown score differs from the contiguous band's drawdown score.
Deleting intraday excursions raises the monthly domestic range CRPS from 0.014230 to 0.014815. Constraining every
path to the same realized variance worsens monthly expansion Brier from 0.198725 to 0.258065. Shuffling sessions
alters temporal path risk even when the terminal and volatility outcomes largely survive the shuffle.

## Independent high-draw confirmation

The same three generative baselines were regenerated with two separate seeds at 1,024 and 4,096 scenarios across every original origin. Each seed shares shock prefixes across budgets and common shocks between diffusion and Student-t GJR.

| horizon | model | n draws | n | range crps | seed min range crps | seed max range crps | drawdown crps | expansion brier | range coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | constant_vol_diffusion | 1,024 | 265 | 0.006011 | 0.006006 | 0.006017 | 0.006043 | 0.155961 | 0.739623 |
| 5 | constant_vol_diffusion | 4,096 | 265 | 0.006006 | 0.006004 | 0.006009 | 0.006037 | 0.155979 | 0.733962 |
| 5 | india_independent_days | 1,024 | 265 | 0.005988 | 0.005985 | 0.005991 | 0.006042 | 0.154285 | 0.766038 |
| 5 | india_independent_days | 4,096 | 265 | 0.005985 | 0.005985 | 0.005986 | 0.006043 | 0.154238 | 0.767925 |
| 5 | student_t_gjr_same_anchor | 1,024 | 265 | 0.005975 | 0.005975 | 0.005975 | 0.006061 | 0.155378 | 0.811321 |
| 5 | student_t_gjr_same_anchor | 4,096 | 265 | 0.005971 | 0.005969 | 0.005972 | 0.006056 | 0.155360 | 0.809434 |
| 21 | constant_vol_diffusion | 1,024 | 217 | 0.013740 | 0.013728 | 0.013752 | 0.013842 | 0.196038 | 0.718894 |
| 21 | constant_vol_diffusion | 4,096 | 217 | 0.013730 | 0.013721 | 0.013738 | 0.013845 | 0.196224 | 0.714286 |
| 21 | india_independent_days | 1,024 | 217 | 0.013650 | 0.013626 | 0.013674 | 0.013847 | 0.190738 | 0.705069 |
| 21 | india_independent_days | 4,096 | 217 | 0.013639 | 0.013632 | 0.013646 | 0.013840 | 0.190899 | 0.709677 |
| 21 | student_t_gjr_same_anchor | 1,024 | 217 | 0.013809 | 0.013803 | 0.013816 | 0.014033 | 0.184086 | 0.806452 |
| 21 | student_t_gjr_same_anchor | 4,096 | 217 | 0.013794 | 0.013789 | 0.013800 | 0.014024 | 0.184055 | 0.801843 |

The 4,096-draw test averages the two seeds per date before calculating paired loss intervals. The resulting intervals retain date dependence and do not count multiple draws as extra forecast outcomes.

| reference | model | block | n | gain | adjusted low | adjusted high |
| --- | --- | --- | --- | --- | --- | --- |
| same_clock_GJR | constant_vol_diffusion | 21 | 217 | 0.001758 | -0.000698 | 0.004213 |
| same_clock_GJR | india_independent_days | 21 | 217 | 0.001849 | -0.000897 | 0.004595 |
| same_clock_GJR | student_t_gjr_same_anchor | 21 | 217 | 0.001693 | -0.000625 | 0.004012 |
| same_clock_GJR | constant_vol_diffusion | 42 | 217 | 0.001758 | -0.001121 | 0.004637 |
| same_clock_GJR | india_independent_days | 42 | 217 | 0.001849 | -0.001378 | 0.005076 |
| same_clock_GJR | student_t_gjr_same_anchor | 42 | 217 | 0.001693 | -0.001016 | 0.004403 |
| india_state_matched | constant_vol_diffusion | 21 | 217 | 0.000500 | -0.000517 | 0.001517 |
| india_state_matched | india_independent_days | 21 | 217 | 0.000592 | -0.000154 | 0.001337 |
| india_state_matched | student_t_gjr_same_anchor | 21 | 217 | 0.000436 | -0.000621 | 0.001493 |
| india_state_matched | constant_vol_diffusion | 42 | 217 | 0.000500 | -0.000539 | 0.001540 |
| india_state_matched | india_independent_days | 42 | 217 | 0.000592 | -0.000050 | 0.001233 |
| india_state_matched | student_t_gjr_same_anchor | 42 | 217 | 0.000436 | -0.000688 | 0.001559 |

[v23-path-cases.csv.gz](v23-path-cases.csv.gz) · [path-risk-matched-intervals.csv.gz](path-risk-matched-intervals.csv.gz) · [path-law-recipes.csv.gz](path-law-recipes.csv.gz) · [path-donor-members.csv.gz](path-donor-members.csv.gz) · [larger-simulation-path-cases.csv.gz](larger-simulation-path-cases.csv.gz) · [larger-simulation-path-matched-intervals.csv](larger-simulation-path-matched-intervals.csv)

[Back to the research index](NIFTY_V23_RESEARCH.md)
