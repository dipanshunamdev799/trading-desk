# V14 Trend Persistence And Path Direction

The path comparison varies estimated AR continuation, an explicitly shrunken historical drift, a domestic-location correction, a filtered variance/sign-state path, and conditional historical resampling. Drift inputs use mature volatility-normalized five-session forecasts and earlier breadth, rotation, synchronization and sign-streak measurements. Foreseen drift decays through the forecast. Realized directional persistence is scored separately from a one-session shock and from the terminal sign.

| horizon | cohort | model | n | disjoint | brier | log_loss | accuracy | balanced_accuracy | crps | mae | coverage80 | width80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | constant_iv | 265 | 53 | 0.250818 | 0.694783 | 0.430189 | 0.429891 | 0.010734 | 0.015086 | 0.807547 | 0.047585 |
| 5 | combined | regime_state | 265 | 53 | 0.251512 | 0.696173 | 0.452830 | 0.460903 | 0.010956 | 0.015094 | 0.773585 | 0.044071 |
| 5 | combined | trend_persistent | 265 | 53 | 0.248223 | 0.689580 | 0.554717 | 0.548539 | 0.010750 | 0.015017 | 0.777358 | 0.043320 |
| 5 | combined | trend_shrink | 265 | 53 | 0.247349 | 0.687842 | 0.588679 | 0.569098 | 0.010703 | 0.015013 | 0.807547 | 0.047527 |
| 5 | combined | simple_drift | 265 | 53 | 0.253726 | 0.700616 | 0.456604 | 0.450855 | 0.010823 | 0.015193 | 0.800000 | 0.047553 |
| 5 | combined | iv_scaled_blocks | 265 | 53 | 0.257679 | 0.708763 | 0.505660 | 0.509096 | 0.011161 | 0.015396 | 0.739623 | 0.042940 |
| 5 | combined | trend_blocks | 265 | 53 | 0.257516 | 0.708477 | 0.498113 | 0.503234 | 0.011160 | 0.015393 | 0.754717 | 0.043543 |
| 21 | combined | constant_iv | 217 | 11 | 0.250062 | 0.693271 | 0.516129 | 0.503279 | 0.025281 | 0.033258 | 0.741935 | 0.100155 |
| 21 | combined | regime_state | 217 | 11 | 0.250994 | 0.695137 | 0.479263 | 0.489129 | 0.024750 | 0.033593 | 0.741935 | 0.091201 |
| 21 | combined | trend_persistent | 217 | 11 | 0.250647 | 0.694447 | 0.502304 | 0.482830 | 0.025124 | 0.033434 | 0.737327 | 0.089268 |
| 21 | combined | trend_shrink | 217 | 11 | 0.249894 | 0.692947 | 0.511521 | 0.475884 | 0.025347 | 0.033495 | 0.755760 | 0.099802 |
| 21 | combined | simple_drift | 217 | 11 | 0.267965 | 0.729396 | 0.396313 | 0.383909 | 0.026471 | 0.034964 | 0.728111 | 0.099808 |
| 21 | combined | iv_scaled_blocks | 217 | 11 | 0.309986 | 0.825304 | 0.382488 | 0.435677 | 0.027427 | 0.035880 | 0.672811 | 0.084645 |
| 21 | combined | trend_blocks | 217 | 11 | 0.307206 | 0.819360 | 0.391705 | 0.446204 | 0.027295 | 0.035563 | 0.682028 | 0.085903 |
| 5 | early | constant_iv | 173 | 35 | 0.251453 | 0.696054 | 0.387283 | 0.389339 | 0.010153 | 0.014484 | 0.843931 | 0.050470 |
| 5 | early | regime_state | 173 | 35 | 0.251878 | 0.696905 | 0.427746 | 0.435358 | 0.010415 | 0.014474 | 0.774566 | 0.044175 |
| 5 | early | trend_persistent | 173 | 35 | 0.251000 | 0.695161 | 0.531792 | 0.535830 | 0.010196 | 0.014506 | 0.815029 | 0.045790 |
| 5 | early | trend_shrink | 173 | 35 | 0.250257 | 0.693694 | 0.554913 | 0.546559 | 0.010187 | 0.014525 | 0.843931 | 0.050400 |
| 5 | early | simple_drift | 173 | 35 | 0.251677 | 0.696518 | 0.508671 | 0.503306 | 0.010178 | 0.014491 | 0.843931 | 0.050427 |
| 5 | early | iv_scaled_blocks | 173 | 35 | 0.255902 | 0.704988 | 0.491329 | 0.513900 | 0.010449 | 0.014654 | 0.763006 | 0.044394 |
| 5 | early | trend_blocks | 173 | 35 | 0.256670 | 0.706590 | 0.456647 | 0.477733 | 0.010450 | 0.014672 | 0.786127 | 0.045032 |
| 21 | early | constant_iv | 141 | 7 | 0.250056 | 0.693259 | 0.503546 | 0.494014 | 0.024148 | 0.031152 | 0.815603 | 0.110050 |
| 21 | early | regime_state | 141 | 7 | 0.250657 | 0.694462 | 0.496454 | 0.503348 | 0.023652 | 0.031452 | 0.780142 | 0.091227 |
| 21 | early | trend_persistent | 141 | 7 | 0.249998 | 0.693148 | 0.539007 | 0.531757 | 0.023738 | 0.031321 | 0.815603 | 0.096769 |
| 21 | early | trend_shrink | 141 | 7 | 0.248665 | 0.690473 | 0.517730 | 0.497768 | 0.024156 | 0.031359 | 0.822695 | 0.109621 |
| 21 | early | simple_drift | 141 | 7 | 0.269367 | 0.732300 | 0.439716 | 0.422382 | 0.025208 | 0.033182 | 0.808511 | 0.109533 |
| 21 | early | iv_scaled_blocks | 141 | 7 | 0.324334 | 0.860204 | 0.453901 | 0.500000 | 0.026290 | 0.034553 | 0.666667 | 0.086188 |
| 21 | early | trend_blocks | 141 | 7 | 0.320644 | 0.852254 | 0.453901 | 0.500000 | 0.026120 | 0.034093 | 0.673759 | 0.087212 |
| 5 | later | constant_iv | 92 | 19 | 0.249623 | 0.692392 | 0.510870 | 0.504354 | 0.011828 | 0.016216 | 0.739130 | 0.042160 |
| 21 | later | constant_iv | 76 | 4 | 0.250072 | 0.693293 | 0.539474 | 0.520789 | 0.027384 | 0.037165 | 0.605263 | 0.081796 |
| 5 | later | regime_state | 92 | 19 | 0.250825 | 0.694797 | 0.500000 | 0.508466 | 0.011973 | 0.016258 | 0.771739 | 0.043875 |
| 21 | later | regime_state | 76 | 4 | 0.251620 | 0.696390 | 0.447368 | 0.463082 | 0.026787 | 0.037565 | 0.671053 | 0.091152 |
| 5 | later | trend_persistent | 92 | 19 | 0.243001 | 0.679085 | 0.597826 | 0.562893 | 0.011792 | 0.015979 | 0.706522 | 0.038676 |
| 21 | later | trend_persistent | 76 | 4 | 0.251849 | 0.696857 | 0.434211 | 0.376703 | 0.027695 | 0.037354 | 0.592105 | 0.075351 |
| 5 | later | trend_shrink | 92 | 19 | 0.241880 | 0.676837 | 0.652174 | 0.603290 | 0.011674 | 0.015930 | 0.739130 | 0.042124 |
| 21 | later | trend_shrink | 76 | 4 | 0.252174 | 0.697538 | 0.500000 | 0.422222 | 0.027556 | 0.037459 | 0.631579 | 0.081586 |
| 5 | later | simple_drift | 92 | 19 | 0.257578 | 0.708324 | 0.358696 | 0.351959 | 0.012036 | 0.016512 | 0.717391 | 0.042150 |
| 21 | later | simple_drift | 76 | 4 | 0.265365 | 0.724009 | 0.315789 | 0.326882 | 0.028815 | 0.038270 | 0.578947 | 0.081766 |
| 5 | later | iv_scaled_blocks | 92 | 19 | 0.261020 | 0.715863 | 0.532609 | 0.479197 | 0.012501 | 0.016790 | 0.695652 | 0.040206 |
| 21 | later | iv_scaled_blocks | 76 | 4 | 0.283366 | 0.760556 | 0.250000 | 0.301434 | 0.029534 | 0.038341 | 0.684211 | 0.081782 |
| 5 | later | trend_blocks | 92 | 19 | 0.259107 | 0.712023 | 0.576087 | 0.533866 | 0.012495 | 0.016747 | 0.695652 | 0.040744 |
| 21 | later | trend_blocks | 76 | 4 | 0.282274 | 0.758332 | 0.276316 | 0.333692 | 0.029474 | 0.038292 | 0.697368 | 0.083476 |

| horizon | cohort | event | model | n | disjoint | brier | log_loss | p | actual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | combined | persist_up | constant_iv | 265 | 53 | 0.065988 | 0.250619 | 0.087126 | 0.071698 |
| 5 | combined | persist_down | constant_iv | 265 | 53 | 0.063940 | 0.255284 | 0.081961 | 0.067925 |
| 5 | combined | persist_up | regime_state | 265 | 53 | 0.066413 | 0.256358 | 0.075470 | 0.071698 |
| 5 | combined | persist_down | regime_state | 265 | 53 | 0.062954 | 0.245936 | 0.069388 | 0.067925 |
| 5 | combined | persist_up | trend_persistent | 265 | 53 | 0.065438 | 0.248362 | 0.072754 | 0.071698 |
| 5 | combined | persist_down | trend_persistent | 265 | 53 | 0.064026 | 0.253184 | 0.081591 | 0.067925 |
| 5 | combined | persist_up | trend_shrink | 265 | 53 | 0.065136 | 0.246750 | 0.081351 | 0.071698 |
| 5 | combined | persist_down | trend_shrink | 265 | 53 | 0.064531 | 0.256370 | 0.086754 | 0.067925 |
| 5 | combined | persist_up | simple_drift | 265 | 53 | 0.065928 | 0.251549 | 0.085073 | 0.071698 |
| 5 | combined | persist_down | simple_drift | 265 | 53 | 0.064466 | 0.258366 | 0.083104 | 0.067925 |
| 5 | combined | persist_up | iv_scaled_blocks | 265 | 53 | 0.070949 | 0.279320 | 0.091924 | 0.071698 |
| 5 | combined | persist_down | iv_scaled_blocks | 265 | 53 | 0.063985 | 0.258906 | 0.068684 | 0.067925 |
| 5 | combined | persist_up | trend_blocks | 265 | 53 | 0.070768 | 0.277939 | 0.093125 | 0.071698 |
| 5 | combined | persist_down | trend_blocks | 265 | 53 | 0.064322 | 0.260803 | 0.073500 | 0.067925 |
| 21 | combined | persist_up | constant_iv | 217 | 11 | 0.023800 | 0.124056 | 0.068773 | 0.023041 |
| 21 | combined | persist_down | constant_iv | 217 | 11 | 0.024275 | 0.127710 | 0.062129 | 0.023041 |
| 21 | combined | persist_up | regime_state | 217 | 11 | 0.023985 | 0.126290 | 0.068141 | 0.023041 |
| 21 | combined | persist_down | regime_state | 217 | 11 | 0.023181 | 0.117080 | 0.056519 | 0.023041 |
| 21 | combined | persist_up | trend_persistent | 217 | 11 | 0.023064 | 0.118087 | 0.061190 | 0.023041 |
| 21 | combined | persist_down | trend_persistent | 217 | 11 | 0.024437 | 0.127878 | 0.061701 | 0.023041 |
| 21 | combined | persist_up | trend_shrink | 217 | 11 | 0.023318 | 0.119853 | 0.062601 | 0.023041 |
| 21 | combined | persist_down | trend_shrink | 217 | 11 | 0.025478 | 0.136856 | 0.068521 | 0.023041 |
| 21 | combined | persist_up | simple_drift | 217 | 11 | 0.024191 | 0.126980 | 0.066325 | 0.023041 |
| 21 | combined | persist_down | simple_drift | 217 | 11 | 0.025798 | 0.138149 | 0.066177 | 0.023041 |
| 21 | combined | persist_up | iv_scaled_blocks | 217 | 11 | 0.022222 | 0.103973 | 0.042035 | 0.023041 |
| 21 | combined | persist_down | iv_scaled_blocks | 217 | 11 | 0.023181 | 0.145163 | 0.016694 | 0.023041 |
| 21 | combined | persist_up | trend_blocks | 217 | 11 | 0.022222 | 0.103322 | 0.042120 | 0.023041 |
| 21 | combined | persist_down | trend_blocks | 217 | 11 | 0.023117 | 0.140495 | 0.017049 | 0.023041 |

[Realized October daily/overnight decomposition](october-case-realized-path.csv) · [Forecast-only feature contrasts](extreme-anatomy-contrasts.csv).
