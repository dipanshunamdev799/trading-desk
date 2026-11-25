# V5 monthly model research

Monthly research still has 76 overlapping origins/four disjoint windows, effective
size diagnostic5.96. Richer data and pooled stock-date rows do not manufacture
independent months. All uncertainty intervals are withheld at this sample size.

|model|n/disjoint|Brier|logloss|accuracy|balanced|CRPS|mean MAE|RMSE|50 cover|80 cover|
|---|---|---|---|---|---|---|---|---|---|---|
|E00|76/4|0.279282|0.752849|40.79%|50.00%|0.028363|3.739%|4.879%|26.3%|61.8%|
|G00|76/4|0.394812|1.041745|26.32%|30.75%|0.034234|4.510%|5.364%|25.0%|60.5%|
|I00|76/4|0.273006|0.747674|52.63%|57.99%|0.030211|3.866%|4.883%|30.3%|50.0%|
|C00|76/4|0.326823|0.862906|36.84%|45.16%|0.030806|3.944%|4.840%|31.6%|52.6%|
|D01|76/4|0.336433|0.889496|43.42%|51.22%|0.031537|4.005%|4.952%|30.3%|48.7%|
|F00|76/4|0.352079|0.924482|34.21%|38.92%|0.031367|4.014%|4.977%|22.4%|46.1%|
|N01|76/4|0.305410|0.809382|40.79%|50.00%|0.028699|3.872%|4.774%|27.6%|56.6%|
|T00|76/4|0.390101|1.008528|36.84%|43.66%|0.033551|4.165%|5.280%|27.6%|43.4%|
|M00|76/4|0.397760|1.016811|23.68%|26.52%|0.033442|4.382%|5.187%|9.2%|46.1%|
|A00|76/4|0.286683|0.769134|40.79%|50.00%|0.028211|3.676%|4.697%|26.3%|53.9%|
|I01_legacy|76/4|0.277904|0.753668|48.68%|54.66%|0.027620|3.594%|4.452%|30.3%|48.7%|
|I03_nosize|76/4|0.255858|0.708978|56.58%|61.83%|0.029489|3.872%|4.811%|30.3%|50.0%|

I01_legacy is V5's lowest exposed monthly CRPS point score.027620, but nominal 80%
coverage48.68% is unacceptable, and it does not beat V4 D02's .027553 CRPS. Global,
factor, transfer, kernel/additive and auxiliary-task models are generally worse.
The lowest V5 monthly Brier can come from a different model and still fails neutral
or adequate distribution calibration. No coherent system dominates every metric.

The simple E00 historical law remains the conservative experimental default,
alongside separately displayed I01_legacy research output. Even E00's nominal 80%
historical coverage61.84% is not calibrated. Monthly complexity should not be
increased because an exposed point ranking looks attractive.

Fresh experimental reference18November25,227.95, issue2026-11-18T22:51:50.449640+05:30,
21-session endpoint18December2026; first target is 19 November per the saved calendar.

|model|endpoint|P(up)|mean return|median return|mean endpoint|50 interval|80 interval|
|---|---|---|---|---|---|---|---|
|E00|2026-12-18|48.81%|-0.502%|-0.042%|25,101.31|24,472–25,584|23,861–26,293|
|I01_legacy|2026-12-18|58.87%|+1.536%|+0.771%|25,615.38|24,914–25,972|24,458–27,770|

These are distinct NOT VALIDATED endpoint laws. They disagree because models
disagree; no output combines their statistics. All target dates remain within 2026.
No 2027 extension, resolved new horizon, independent validation or deployment
is claimed. Future path risk/realized volatility remain unavailable.
