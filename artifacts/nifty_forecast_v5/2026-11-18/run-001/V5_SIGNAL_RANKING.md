# V5 signal ranking

Rank whole systems separately from incremental information hypotheses. A combined
model can beat unconditional history while an added global block harms the Indian
control. A useful whole-system point score does not prove a source's incremental
value or a feature's causal influence.

System ranking score=.4*relativeCRPSgain+.3*relativeBriergain+.2*positive leave-month
CRPS fraction-.1*(50/80coverage absolute gaps)-.1 for survivorship-only systems.
This is a transparent descriptive prioritization rule, not a significance level
or a portfolio weight. Gains are relative to E00. Source incremental comparisons
use the actual parent model and are kept in hypothesis-ranking.csv/json, including
rationale/source/timeframe/coverage/horizon/counts/stability/risk/complexity/uncertainty/
next experiment. Status REJECTED applies to a tested implementation, not proof
that its economic family can never contain a signal.

|horizon|model|status|ranking score|CRPS gain%|Brier gain%|leave-month positive|proxy|
|---|---|---|---|---|---|---|---|
|5|I03_nosize|EXPLORATORY LEAD|0.3484|16.47|29.52|100%|False|
|5|I00|EXPLORATORY LEAD|0.3396|16.27|27.95|100%|False|
|5|L01|EXPLORATORY LEAD|0.3369|18.41|23.49|100%|False|
|5|I02_newindices|EXPLORATORY LEAD|0.3221|16.21|22.57|100%|False|
|5|I01_legacy|EXPLORATORY LEAD|0.3169|11.96|26.87|100%|False|
|5|L02|EXPLORATORY LEAD|0.3107|13.75|21.31|100%|False|
|5|I04_delay|EXPLORATORY LEAD|0.305|11.69|23.26|100%|False|
|5|C00|EXPLORATORY LEAD|0.2967|10.36|21.56|100%|False|
|5|AT00_old_newlaw|EXPLORATORY LEAD|0.2938|10.39|22.7|100%|False|
|5|D01|EXPLORATORY LEAD|0.2903|10.08|19.76|100%|False|
|5|C01_delayglobal|EXPLORATORY LEAD|0.2873|10.29|19.58|100%|False|
|5|D02_rawonly|EXPLORATORY LEAD|0.2864|9.58|19.5|100%|False|
|5|AT01_new_oldlaw|EXPLORATORY LEAD|0.2856|7.28|23.01|100%|False|
|5|S00|EXPLORATORY LEAD|0.2848|10.04|19.8|100%|False|
|5|I05_rolling126|EXPLORATORY LEAD|0.2824|9.16|16.86|100%|False|
|5|I06_forest|EXPLORATORY LEAD|0.2308|4.39|7.16|100%|False|
|5|N01|EXPLORATORY LEAD|0.2303|4.59|7.1|100%|False|
|5|A00|EXPLORATORY LEAD|0.2244|3.27|5.81|100%|False|
|5|A01|EXPLORATORY LEAD|0.2058|1.4|4.63|100%|False|
|5|L03|EXPLORATORY LEAD|0.1997|13.3|20.05|100%|True|
|5|BR00|EXPLORATORY LEAD|0.1801|8.9|18.31|100%|True|
|5|R00|EXPLORATORY LEAD|0.1172|1.08|0.0|60%|False|
|5|L00|INCONCLUSIVE|0.0598|-0.62|0.11|40%|False|
|5|F00|INCONCLUSIVE|0.0314|-0.79|1.29|20%|False|
|5|E00|INCONCLUSIVE|-0.0072|0.0|0.0|0%|False|
|5|F01|INCONCLUSIVE|-0.0241|-2.36|-2.14|0%|False|
|5|P00|INCONCLUSIVE|-0.0513|-5.59|-5.44|0%|False|
|5|M00|REJECTED|-0.0586|-4.94|-5.85|0%|False|
|5|N00|INCONCLUSIVE|-0.0638|-6.27|-7.61|0%|False|
|5|N02|REJECTED|-0.0698|-6.61|-9.52|0%|False|
|5|T00|REJECTED|-0.0711|-6.38|-9.53|0%|False|
|5|D00|INCONCLUSIVE|-0.0729|-6.37|-10.9|0%|False|
|5|G00|REJECTED|-0.0765|-9.46|-9.76|0%|False|
|5|T01|REJECTED|-0.172|-6.65|-9.11|0%|True|
|21|I01_legacy|EXPLORATORY LEAD|0.1109|2.62|0.49|75%|False|
|21|AT00_old_newlaw|INCONCLUSIVE|0.1022|0.91|-0.14|75%|False|
|21|I03_nosize|INCONCLUSIVE|0.0595|-3.97|8.39|50%|False|
|21|A00|INCONCLUSIVE|0.0444|0.53|-2.65|50%|False|
|21|I06_forest|INCONCLUSIVE|0.0386|0.43|-6.22|50%|False|
|21|N01|INCONCLUSIVE|0.0214|-1.18|-9.36|50%|False|
|21|A01|INCONCLUSIVE|-0.0163|-1.84|-2.64|25%|False|
|21|E00|INCONCLUSIVE|-0.0418|0.0|0.0|0%|False|
|21|L01|INCONCLUSIVE|-0.0524|-4.2|-12.4|25%|False|
|21|AT01_new_oldlaw|INCONCLUSIVE|-0.0657|-11.64|10.22|0%|False|
|21|I00|INCONCLUSIVE|-0.0691|-6.52|2.25|0%|False|
|21|R00|INCONCLUSIVE|-0.0953|-4.86|-9.14|0%|False|
|21|I04_delay|INCONCLUSIVE|-0.1199|-10.89|-8.45|0%|False|
|21|S00|INCONCLUSIVE|-0.1279|-9.63|-14.1|0%|False|
|21|I02_newindices|INCONCLUSIVE|-0.1295|-11.02|-11.48|0%|False|
|21|C00|INCONCLUSIVE|-0.1313|-8.61|-17.02|0%|False|
|21|C01_delayglobal|INCONCLUSIVE|-0.1458|-8.66|-22.22|0%|False|
|21|D02_rawonly|INCONCLUSIVE|-0.1529|-10.6|-20.69|0%|False|
|21|D01|INCONCLUSIVE|-0.1572|-11.19|-20.46|0%|False|
|21|F00|INCONCLUSIVE|-0.1821|-10.59|-26.07|0%|False|
|21|L02|INCONCLUSIVE|-0.1981|-12.8|-31.09|0%|False|
|21|BR00|INCONCLUSIVE|-0.2378|-9.84|-16.23|0%|True|
|21|F01|INCONCLUSIVE|-0.2489|-18.66|-34.95|0%|False|
|21|T00|REJECTED|-0.2512|-18.29|-39.68|0%|False|
|21|G00|REJECTED|-0.2514|-20.7|-41.37|0%|False|
|21|L00|INCONCLUSIVE|-0.2709|-18.44|-44.75|0%|False|
|21|M00|REJECTED|-0.2736|-17.91|-42.42|0%|False|
|21|P00|INCONCLUSIVE|-0.2763|-21.5|-40.26|0%|False|
|21|L03|INCONCLUSIVE|-0.2898|-12.31|-28.95|0%|True|
|21|N00|INCONCLUSIVE|-0.2929|-21.31|-47.39|0%|False|
|21|N02|REJECTED|-0.3046|-22.82|-50.57|0%|False|
|21|D00|INCONCLUSIVE|-0.32|-27.08|-46.54|0%|False|
|21|I05_rolling126|INCONCLUSIVE|-0.3491|-34.7|-50.45|0%|False|
|21|T01|REJECTED|-0.3525|-18.75|-39.09|0%|True|

INDEPENDENTLY VALIDATED count=0. No candidate passes the full registered robust
retrospective gate: coherent distribution calibration and stronger prior-model
proper-score uncertainty remain inadequate. Native internals and coherent-law/
ETF systems are EXPLORATORY LEADS. New-index and ETF *incremental* attribution is
INCONCLUSIVE; global/derivatives/transfer/factor implementations generally fail.
Monthly flags reflect tiny independent samples. No forced winner is created.

|h|hypothesis|candidate/parent|Brier gain|CRPS gain|status|
|---|---|---|---|---|---|
|5|Indian native internals|I00/P00|0.086244|0.002669|EXPLORATORY LEAD|
|5|New indices beyond legacy|I00/I01_legacy|0.002789|0.000526|INCONCLUSIVE|
|5|Mid/small-cap increment|I00/I03_nosize|-0.004052|-2.5e-05|REJECTED|
|5|Global increment|C00/I00|-0.01652|-0.000722|REJECTED|
|5|Derivatives increment|D01/C00|-0.004627|-3.4e-05|REJECTED|
|5|ETF activity increment|L01/I00|-0.011511|0.000261|INCONCLUSIVE|
|5|Sector transfer|T00/I00|-0.096804|-0.002765|REJECTED|
|5|Stock transfer|T01/I00|-0.095736|-0.002799|REJECTED|
|5|Joint factors|F00/C00|-0.052343|-0.001361|REJECTED|
|5|Rolling loading adaptation|F01/F00|-0.008853|-0.000192|REJECTED|
|5|Nonlinear joint states|N01/C00|-0.037336|-0.000703|REJECTED|
|5|Sequence evolution|S00/C00|-0.004526|-3.8e-05|REJECTED|
|5|Historical analogues|A00/E00|0.015004|0.000399|EXPLORATORY LEAD|
|5|Auxiliary horizons|M00/P00|-0.001064|8e-05|INCONCLUSIVE|
|5|Current-stock breadth proxy|BR00/C00|-0.008385|-0.000178|REJECTED|
|5|Stock volume proxy|L03/L02|-0.00327|-5.5e-05|REJECTED|
|21|Indian native internals|I00/P00|0.118722|0.004251|EXPLORATORY LEAD|
|21|New indices beyond legacy|I00/I01_legacy|0.004899|-0.002591|INCONCLUSIVE|
|21|Mid/small-cap increment|I00/I03_nosize|-0.017148|-0.000721|REJECTED|
|21|Global increment|C00/I00|-0.053817|-0.000595|REJECTED|
|21|Derivatives increment|D01/C00|-0.00961|-0.000732|REJECTED|
|21|ETF activity increment|L01/I00|-0.040907|0.000658|INCONCLUSIVE|
|21|Sector transfer|T00/I00|-0.117095|-0.003341|REJECTED|
|21|Stock transfer|T01/I00|-0.115457|-0.00347|REJECTED|
|21|Joint factors|F00/C00|-0.025256|-0.000561|REJECTED|
|21|Rolling loading adaptation|F01/F00|-0.024813|-0.002287|REJECTED|
|21|Nonlinear joint states|N01/C00|0.021413|0.002107|EXPLORATORY LEAD|
|21|Sequence evolution|S00/C00|0.008168|-0.000288|INCONCLUSIVE|
|21|Historical analogues|A00/E00|-0.007401|0.000151|INCONCLUSIVE|
|21|Auxiliary horizons|M00/P00|-0.006032|0.00102|INCONCLUSIVE|
|21|Current-stock breadth proxy|BR00/C00|0.002212|-0.000347|INCONCLUSIVE|
|21|Stock volume proxy|L03/L02|0.005979|0.000137|EXPLORATORY LEAD|
