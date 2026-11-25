# V5 Indian internals and cross-sectional learning

Native historical index participation is distinct from a current stock basket.
The primary internal block uses23 domestic price indices (excluding spot and VIX),
relative5/21 returns, participation, dispersion, concentration, leadership-rank
persistence and defensive/cyclical rotation. Broad100/200/500,Next50 and size/style
indices materially expand the original sector-only information set.

|model|n/disjoint|Brier|logloss|accuracy|balanced|CRPS|mean MAE|RMSE|50 cover|80 cover|
|---|---|---|---|---|---|---|---|---|---|---|
|P00|92/19|0.272343|0.740884|54.35%|47.51%|0.012893|1.706%|2.424%|48.9%|68.5%|
|I00|92/19|0.186099|0.558036|76.09%|75.18%|0.010224|1.354%|1.985%|55.4%|76.1%|
|I01_legacy|92/19|0.188888|0.564913|72.83%|72.01%|0.010750|1.396%|2.060%|56.5%|75.0%|
|I02_newindices|92/19|0.200000|0.587242|66.30%|64.32%|0.010231|1.368%|1.986%|56.5%|76.1%|
|I03_nosize|92/19|0.182047|0.549215|76.09%|76.87%|0.010199|1.351%|1.981%|52.2%|76.1%|
|I04_delay|92/19|0.198222|0.585523|71.74%|70.05%|0.010782|1.422%|2.068%|55.4%|73.9%|
|I05_rolling126|92/19|0.214741|0.620195|67.39%|69.33%|0.011092|1.526%|2.112%|54.3%|80.4%|
|T00|92/19|0.282903|0.765260|57.61%|50.00%|0.012989|1.731%|2.450%|44.6%|68.5%|
|T01|92/19|0.281835|0.762554|57.61%|50.00%|0.013023|1.737%|2.456%|43.5%|68.5%|
|BR00|92/19|0.211004|0.609325|68.48%|66.55%|0.011124|1.446%|2.063%|56.5%|76.1%|

The weekly I00 Brier.186099/76.09% accuracy is an exposed-history lead. Dropping
mid/small-cap indices improves Brier to.182047, so the gain cannot be attributed
to adding every size series. Legacy-sector-only .188888 remains strong; the exact
increment from new indices is small/uncertain. One-session internal delay and
rolling126 reduce the point advantage; neither is quietly substituted into a
frozen earlier candidate. Current-stock breadth does not improve the joint model.

|hypothesis|metric|gain|simultaneous95|
|---|---|---|---|
|Native internals beyond index price|brier|+0.086244|[0.011628157453503984, 0.16085927230100652]|
|Native internals beyond index price|crps|+0.002669|[-0.0005355180923781759, 0.0058739430424342865]|
|New indices beyond old sectors|brier|+0.002789|[-0.02078224001476657, 0.026360450767666757]|
|New indices beyond old sectors|crps|+0.000526|[-0.0005267793046201283, 0.0015788114130012537]|
|Mid/small-cap contribution|brier|-0.004052|[-0.02061738418877282, 0.012512810837693261]|
|Mid/small-cap contribution|crps|-0.000025|[-0.0004818646552786221, 0.00043185476650069035]|

Transfer learning was actually executed:3,627 native sector-date rows from nine
sectors and 60,450 stock-date rows from 150 current stock identities. Shared Ridge
models use own return/trend/RV and common global/participation context, normalize
targets by origin RV*sqrt(h), and give all securities on a date total weight1.
Training dates and label endpoints are grouped/purged by date, never random stock
rows. Only matured endpoints enter any fit; no current membership weights aggregate
security forecasts into a purported historical NIFTY basket. Targets above50%
absolute return are quarantined in transfer training; this is a known tail/sample
selection limitation, not proof such moves cannot occur. No pre2025 state is used.

T00/T01 fail to improve the native internal model; stock-date abundance did not
create extra independent NIFTY outcomes. T01 and BR00 remain survivorship-exposed,
ineligible for the selected primary experimental systems. Monthly transfer is
especially poor. Native index composition may itself change historically, but
the published index series is used directly; today's stock membership is not
backcast as the index universe.
