# V13 Options Surface Dynamics

Built constant-calendar-maturity histories at 7, 14, 30 and 45 days from **2,559** liquid V12 expiry snapshots, preserving an earlier source day. Level summaries include ATM IV, upside and downside skew, curvature, implied quantiles, tail masses and term slope/curvature. One- and five-session changes, skew acceleration, slope sign transitions and same-listed-contract changes distinguish dynamics from rolls. A truncated OTM variance strip integrates only observed strikes. Four-factor PCA and regularized summaries are fit on matured rows. Missing wing or bracket support remains visible.

| horizon | cohort | model | n | disjoint | mae | rmse | qlike | bias | spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | shape_block_permute | 265 | 53 | 0.040362 | 0.054778 | 0.392159 | -0.011118 | 0.582086 |
| 5 | early | shape_block_permute | 173 | 35 | 0.041114 | 0.057021 | 0.373398 | -0.008982 | 0.628894 |
| 5 | later | shape_block_permute | 92 | 19 | 0.038948 | 0.050289 | 0.427438 | -0.015134 | 0.487385 |
| 5 | combined | shape_change | 265 | 53 | 0.038722 | 0.052664 | 0.368062 | -0.009936 | 0.609161 |
| 5 | early | shape_change | 173 | 35 | 0.038689 | 0.053890 | 0.340129 | -0.007497 | 0.665421 |
| 5 | later | shape_change | 92 | 19 | 0.038784 | 0.050278 | 0.420589 | -0.014521 | 0.482885 |
| 5 | combined | shape_combined | 265 | 53 | 0.040979 | 0.057179 | 0.420416 | -0.008916 | 0.577655 |
| 5 | early | shape_combined | 173 | 35 | 0.042156 | 0.060737 | 0.430828 | -0.006790 | 0.632807 |
| 5 | later | shape_combined | 92 | 19 | 0.038764 | 0.049806 | 0.400835 | -0.012915 | 0.486753 |
| 5 | combined | shape_level | 265 | 53 | 0.040589 | 0.054762 | 0.399562 | -0.009505 | 0.565225 |
| 5 | early | shape_level | 173 | 35 | 0.040900 | 0.056717 | 0.387945 | -0.007832 | 0.641839 |
| 5 | later | shape_level | 92 | 19 | 0.040003 | 0.050884 | 0.421408 | -0.012651 | 0.422838 |
| 5 | combined | shape_pca | 265 | 53 | 0.040086 | 0.053819 | 0.372360 | -0.006957 | 0.582707 |
| 5 | early | shape_pca | 173 | 35 | 0.039925 | 0.055021 | 0.339067 | -0.003562 | 0.662248 |
| 5 | later | shape_pca | 92 | 19 | 0.040388 | 0.051483 | 0.434965 | -0.013340 | 0.409352 |
| 5 | combined | shape_shift21 | 265 | 53 | 0.038882 | 0.052262 | 0.381180 | -0.008453 | 0.529666 |
| 5 | early | shape_shift21 | 173 | 35 | 0.038605 | 0.053608 | 0.374312 | -0.008308 | 0.581664 |
| 5 | later | shape_shift21 | 92 | 19 | 0.039405 | 0.049633 | 0.394094 | -0.008726 | 0.433241 |
| 5 | combined | sstrip_var30_sd | 253 | 53 | 0.042350 | 0.051502 | 0.305645 | 0.013880 | 0.605354 |
| 5 | early | sstrip_var30_sd | 165 | 35 | 0.042562 | 0.052859 | 0.292266 | 0.015716 | 0.656552 |
| 5 | later | sstrip_var30_sd | 88 | 18 | 0.041954 | 0.048857 | 0.330731 | 0.010438 | 0.532951 |
| 5 | combined | sstrip_var7_sd | 217 | 53 | 0.040290 | 0.050200 | 0.283678 | 0.015872 | 0.631765 |
| 5 | early | sstrip_var7_sd | 141 | 34 | 0.039416 | 0.050182 | 0.257875 | 0.019409 | 0.708378 |
| 5 | later | sstrip_var7_sd | 76 | 19 | 0.041912 | 0.050233 | 0.331548 | 0.009310 | 0.468298 |
| 21 | combined | shape_block_permute | 217 | 11 | 0.050366 | 0.073776 | 0.632276 | -0.015999 | 0.165614 |
| 21 | early | shape_block_permute | 141 | 7 | 0.060900 | 0.087760 | 0.861505 | -0.023446 | 0.152434 |
| 21 | later | shape_block_permute | 76 | 4 | 0.030822 | 0.035381 | 0.206995 | -0.002183 | 0.255885 |
| 21 | combined | shape_change | 217 | 11 | 0.042276 | 0.057242 | 0.488047 | -0.019630 | 0.292858 |
| 21 | early | shape_change | 141 | 7 | 0.049685 | 0.066855 | 0.654334 | -0.028685 | 0.305287 |
| 21 | later | shape_change | 76 | 4 | 0.028530 | 0.032610 | 0.179542 | -0.002831 | 0.396336 |
| 21 | combined | shape_combined | 217 | 11 | 0.044753 | 0.063415 | 0.669532 | -0.020904 | 0.214394 |
| 21 | early | shape_combined | 141 | 7 | 0.055947 | 0.075842 | 0.957797 | -0.032409 | 0.194092 |
| 21 | later | shape_combined | 76 | 4 | 0.023984 | 0.028476 | 0.134725 | 0.000441 | 0.594915 |
| 21 | combined | shape_level | 217 | 11 | 0.048385 | 0.067761 | 0.770767 | -0.019016 | 0.161400 |
| 21 | early | shape_level | 141 | 7 | 0.060668 | 0.081209 | 1.109816 | -0.028827 | 0.155653 |
| 21 | later | shape_level | 76 | 4 | 0.025597 | 0.029573 | 0.141743 | -0.000814 | 0.589310 |
| 21 | combined | shape_pca | 217 | 11 | 0.046693 | 0.063284 | 0.598417 | -0.018007 | 0.217373 |
| 21 | early | shape_pca | 141 | 7 | 0.056797 | 0.074849 | 0.829393 | -0.026971 | 0.218999 |
| 21 | later | shape_pca | 76 | 4 | 0.027948 | 0.032262 | 0.169896 | -0.001377 | 0.422474 |
| 21 | combined | shape_shift21 | 217 | 11 | 0.043658 | 0.059542 | 0.484398 | -0.010731 | 0.310538 |
| 21 | early | shape_shift21 | 141 | 7 | 0.053038 | 0.070472 | 0.664730 | -0.018360 | 0.268008 |
| 21 | later | shape_shift21 | 76 | 4 | 0.026255 | 0.030150 | 0.149834 | 0.003423 | 0.488913 |
| 21 | combined | sstrip_var30_sd | 206 | 11 | 0.039973 | 0.048935 | 0.232774 | 0.002125 | 0.425878 |
| 21 | early | sstrip_var30_sd | 134 | 7 | 0.045063 | 0.055163 | 0.261864 | -0.000052 | 0.378052 |
| 21 | later | sstrip_var30_sd | 72 | 4 | 0.030498 | 0.034470 | 0.178632 | 0.006176 | 0.348994 |
| 21 | combined | sstrip_var7_sd | 177 | 11 | 0.040316 | 0.050029 | 0.230292 | 0.005291 | 0.524017 |
| 21 | early | sstrip_var7_sd | 115 | 7 | 0.045913 | 0.056776 | 0.259750 | 0.005969 | 0.485662 |
| 21 | later | sstrip_var7_sd | 62 | 4 | 0.029933 | 0.034153 | 0.175653 | 0.004033 | 0.385964 |

| horizon | cohort | model | baseline | target | metric | n | disjoint | candidate | control | gain | low10 | high10 | low21 | high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | shape_change | shape_level | volatility | mae | 265 | 53 | 0.038722 | 0.040589 | 0.001867 | -0.002631 | 0.006365 | -0.003031 | 0.006764 |
| 5 | combined | shape_pca | shape_level | volatility | mae | 265 | 53 | 0.040086 | 0.040589 | 0.000503 | -0.001859 | 0.002865 | -0.002384 | 0.003389 |
| 5 | combined | shape_combined | shape_level | volatility | mae | 265 | 53 | 0.040979 | 0.040589 | -0.000390 | -0.002977 | 0.002197 | -0.003023 | 0.002244 |
| 5 | combined | shape_change | iv_nearest | volatility | mae | 265 | 53 | 0.038722 | 0.037814 | -0.000908 | -0.009567 | 0.007752 | -0.011808 | 0.009993 |
| 5 | combined | shape_shift21 | iv_nearest | volatility | mae | 265 | 53 | 0.038882 | 0.037814 | -0.001068 | -0.008776 | 0.006640 | -0.010436 | 0.008301 |
| 5 | combined | shape_pca | iv_nearest | volatility | mae | 265 | 53 | 0.040086 | 0.037814 | -0.002271 | -0.011101 | 0.006558 | -0.013127 | 0.008584 |
| 5 | combined | shape_block_permute | iv_nearest | volatility | mae | 265 | 53 | 0.040362 | 0.037814 | -0.002548 | -0.012814 | 0.007718 | -0.014427 | 0.009332 |
| 5 | combined | sstrip_var7_sd | iv_nearest | volatility | mae | 217 | 53 | 0.040290 | 0.037567 | -0.002723 | -0.006940 | 0.001494 | -0.007434 | 0.001988 |
| 5 | combined | shape_level | iv_nearest | volatility | mae | 265 | 53 | 0.040589 | 0.037814 | -0.002774 | -0.012758 | 0.007209 | -0.015538 | 0.009990 |
| 5 | combined | shape_combined | iv_nearest | volatility | mae | 265 | 53 | 0.040979 | 0.037814 | -0.003164 | -0.013704 | 0.007376 | -0.016639 | 0.010311 |
| 5 | combined | sstrip_var30_sd | iv_nearest | volatility | mae | 253 | 53 | 0.042350 | 0.037960 | -0.004390 | -0.008970 | 0.000189 | -0.008833 | 0.000052 |
| 5 | combined | shape_change | shape_level | volatility | qlike | 265 | 53 | 0.368062 | 0.399562 | 0.031500 | -0.064161 | 0.127161 | -0.070432 | 0.133432 |
| 5 | combined | shape_pca | shape_level | volatility | qlike | 265 | 53 | 0.372360 | 0.399562 | 0.027203 | -0.038268 | 0.092673 | -0.053024 | 0.107429 |
| 5 | combined | sstrip_var7_sd | iv_nearest | volatility | qlike | 217 | 53 | 0.283678 | 0.280227 | -0.003451 | -0.056567 | 0.049665 | -0.064979 | 0.058077 |
| 5 | combined | shape_combined | shape_level | volatility | qlike | 265 | 53 | 0.420416 | 0.399562 | -0.020853 | -0.106307 | 0.064600 | -0.105117 | 0.063411 |
| 5 | combined | sstrip_var30_sd | iv_nearest | volatility | qlike | 253 | 53 | 0.305645 | 0.279247 | -0.026398 | -0.089804 | 0.037008 | -0.091241 | 0.038445 |
| 5 | combined | shape_change | iv_nearest | volatility | qlike | 265 | 53 | 0.368062 | 0.276187 | -0.091875 | -0.235024 | 0.051274 | -0.271828 | 0.088078 |
| 5 | combined | shape_pca | iv_nearest | volatility | qlike | 265 | 53 | 0.372360 | 0.276187 | -0.096173 | -0.246696 | 0.054350 | -0.280675 | 0.088330 |
| 5 | combined | shape_shift21 | iv_nearest | volatility | qlike | 265 | 53 | 0.381180 | 0.276187 | -0.104993 | -0.312589 | 0.102603 | -0.345109 | 0.135123 |
| 5 | combined | shape_block_permute | iv_nearest | volatility | qlike | 265 | 53 | 0.392159 | 0.276187 | -0.115972 | -0.271131 | 0.039188 | -0.310820 | 0.078876 |
| 5 | combined | shape_level | iv_nearest | volatility | qlike | 265 | 53 | 0.399562 | 0.276187 | -0.123375 | -0.323038 | 0.076288 | -0.372253 | 0.125502 |
| 5 | combined | shape_combined | iv_nearest | volatility | qlike | 265 | 53 | 0.420416 | 0.276187 | -0.144229 | -0.366922 | 0.078465 | -0.421674 | 0.133217 |
| 21 | combined | shape_change | shape_level | volatility | mae | 217 | 11 | 0.042276 | 0.048385 | 0.006109 | -0.006483 | 0.018700 | -0.008273 | 0.020491 |
| 21 | combined | shape_combined | shape_level | volatility | mae | 217 | 11 | 0.044753 | 0.048385 | 0.003632 | -0.003243 | 0.010508 | -0.003586 | 0.010851 |
| 21 | combined | shape_pca | shape_level | volatility | mae | 217 | 11 | 0.046693 | 0.048385 | 0.001692 | -0.003974 | 0.007358 | -0.004447 | 0.007831 |
| 21 | combined | sstrip_var30_sd | iv_bracket | volatility | mae | 206 | 11 | 0.039973 | 0.039923 | -0.000049 | -0.005557 | 0.005458 | -0.007099 | 0.007000 |
| 21 | combined | sstrip_var7_sd | iv_bracket | volatility | mae | 177 | 11 | 0.040316 | 0.039841 | -0.000474 | -0.012730 | 0.011781 | -0.014736 | 0.013787 |
| 21 | combined | shape_change | iv_bracket | volatility | mae | 217 | 11 | 0.042276 | 0.039406 | -0.002870 | -0.014636 | 0.008896 | -0.017460 | 0.011720 |
| 21 | combined | shape_shift21 | iv_bracket | volatility | mae | 217 | 11 | 0.043658 | 0.039406 | -0.004252 | -0.014838 | 0.006335 | -0.017261 | 0.008757 |
| 21 | combined | shape_combined | iv_bracket | volatility | mae | 217 | 11 | 0.044753 | 0.039406 | -0.005346 | -0.022077 | 0.011384 | -0.025697 | 0.015004 |
| 21 | combined | shape_pca | iv_bracket | volatility | mae | 217 | 11 | 0.046693 | 0.039406 | -0.007287 | -0.021894 | 0.007321 | -0.024461 | 0.009888 |
| 21 | combined | shape_level | iv_bracket | volatility | mae | 217 | 11 | 0.048385 | 0.039406 | -0.008979 | -0.027679 | 0.009722 | -0.031175 | 0.013218 |
| 21 | combined | shape_block_permute | iv_bracket | volatility | mae | 217 | 11 | 0.050366 | 0.039406 | -0.010959 | -0.027455 | 0.005537 | -0.029855 | 0.007936 |
| 21 | combined | shape_change | shape_level | volatility | qlike | 217 | 11 | 0.488047 | 0.770767 | 0.282720 | -0.297687 | 0.863127 | -0.416935 | 0.982375 |
| 21 | combined | shape_pca | shape_level | volatility | qlike | 217 | 11 | 0.598417 | 0.770767 | 0.172350 | -0.216040 | 0.560740 | -0.295232 | 0.639932 |
| 21 | combined | shape_combined | shape_level | volatility | qlike | 217 | 11 | 0.669532 | 0.770767 | 0.101235 | -0.133938 | 0.336409 | -0.160144 | 0.362614 |
| 21 | combined | sstrip_var7_sd | iv_bracket | volatility | qlike | 177 | 11 | 0.230292 | 0.279100 | 0.048807 | -0.166203 | 0.263818 | -0.219950 | 0.317564 |
| 21 | combined | sstrip_var30_sd | iv_bracket | volatility | qlike | 206 | 11 | 0.232774 | 0.273311 | 0.040537 | -0.064362 | 0.145437 | -0.091120 | 0.172195 |
| 21 | combined | shape_shift21 | iv_bracket | volatility | qlike | 217 | 11 | 0.484398 | 0.267623 | -0.216775 | -0.646709 | 0.213160 | -0.745340 | 0.311790 |
| 21 | combined | shape_change | iv_bracket | volatility | qlike | 217 | 11 | 0.488047 | 0.267623 | -0.220424 | -0.562102 | 0.121253 | -0.670146 | 0.229297 |
| 21 | combined | shape_pca | iv_bracket | volatility | qlike | 217 | 11 | 0.598417 | 0.267623 | -0.330794 | -0.825168 | 0.163580 | -0.981353 | 0.319764 |
| 21 | combined | shape_block_permute | iv_bracket | volatility | qlike | 217 | 11 | 0.632276 | 0.267623 | -0.364653 | -0.866698 | 0.137392 | -1.031293 | 0.301987 |
| 21 | combined | shape_combined | iv_bracket | volatility | qlike | 217 | 11 | 0.669532 | 0.267623 | -0.401909 | -1.056515 | 0.252696 | -1.262980 | 0.459161 |
| 21 | combined | shape_level | iv_bracket | volatility | qlike | 217 | 11 | 0.770767 | 0.267623 | -0.503145 | -1.358004 | 0.351715 | -1.604621 | 0.598332 |

[Fixed-tenor surface inputs](constant-maturity-surface.csv) · [V12 priced density archive](../../../nifty_forecast_v12/2026-11-24/run-001/option-density-atoms.npz) · [NSE variance methodology](https://nsearchives.nseindia.com/s3fs-public/inline-files/white_paper_IndiaVIX.pdf).
