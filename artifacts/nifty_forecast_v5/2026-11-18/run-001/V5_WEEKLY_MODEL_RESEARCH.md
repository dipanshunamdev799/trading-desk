# V5 weekly model research

Best whole-law CRPS point candidate L01 (native internals+ETF activity) has
Brier 0.197610,CRPS0.009963,accuracy 66.30%,
50/80coverage54.35%/77.17%.
Direction/Brier alternative I03_nosize has Brier.182047,76.09% accuracy,CRPS.010199;
it is a postselected removal stress and retains EXPLORATORY status.
The initial native lead I00 is .186099/.010224/76.09%. All 92origins overlap into
19 disjoint windows; effective-size diagnostic23.45 does not guarantee independence.

|model|n/disjoint|Brier|logloss|accuracy|balanced|CRPS|mean MAE|RMSE|50 cover|80 cover|
|---|---|---|---|---|---|---|---|---|---|---|
|E00|92/19|0.258296|0.709964|57.61%|50.00%|0.012210|1.637%|2.321%|50.0%|72.8%|
|P00|92/19|0.272343|0.740884|54.35%|47.51%|0.012893|1.706%|2.424%|48.9%|68.5%|
|I00|92/19|0.186099|0.558036|76.09%|75.18%|0.010224|1.354%|1.985%|55.4%|76.1%|
|C00|92/19|0.202619|0.591175|68.48%|67.22%|0.010946|1.417%|2.043%|56.5%|77.2%|
|D01|92/19|0.207246|0.601303|67.39%|65.94%|0.010980|1.436%|2.066%|58.7%|79.3%|
|N01|92/19|0.239955|0.672948|59.78%|62.72%|0.011649|1.596%|2.205%|47.8%|72.8%|
|L01|92/19|0.197610|0.582153|66.30%|65.34%|0.009963|1.341%|1.917%|54.3%|77.2%|
|I03_nosize|92/19|0.182047|0.549215|76.09%|76.87%|0.010199|1.351%|1.981%|52.2%|76.1%|

Global and derivatives blocks do not add incremental value to the strongest
Indian control. ETF addition improves CRPS descriptively but worsens I00 Brier;
neither incremental interval excludes zero after full search adjustment. The
strongest prior V4 comparisons also include zero. Some Brier improvements versus
neutral/unconditional/price are positive under the exploratory family adjustment,
which is a narrower and more useful finding than claiming every test failed.

Fresh experimental snapshot issued2026-11-18T22:51:50.449640+05:30; reference18 November
official NIFTY close25,227.95, corroborated independently by FO underlying. First
target session2026-11-19; five-session endpoint26 November.
The exchange calendar, including closures, supplies exact dates in JSON.
Unlike the earlier late V3/V4 scenarios, this experimental issue precedes the
first target session. It has not resolved or independently validated anything.
Source files were acquired before issue. US18 November's unfinished close is
excluded, and historical features through17 November were not changed.

|model|endpoint|P(up)|mean return|median return|mean endpoint|50 interval|80 interval|
|---|---|---|---|---|---|---|---|
|L01|2026-11-26|79.01%|+1.911%|+1.794%|25,710.06|25,339–26,035|25,000–26,630|
|I03_nosize|2026-11-26|68.17%|+1.106%|+0.753%|25,506.91|25,107–25,709|24,950–26,372|

**All numbers are uncalibrated model estimates, NOT VALIDATED.** L01 and I03 are
distinct laws; do not attach one probability to the other's mean/interval. Each
JSON law includes up/nonpositive probabilities, mean, median, seven buckets,
noncrossing quantiles, endpoint intervals, expected absolute movement and endpoint
dispersion. Expected future path volatility/breaches are UNAVAILABLE from endpoint
laws. Nominal intervals are not coverage guarantees. Live fitting is a distinct
V5 latest-as-of refit using mature endpoints; it does not change V4's monthly-refit
protocol or qualify as its primary prospective cohort. No trade is recommended.
