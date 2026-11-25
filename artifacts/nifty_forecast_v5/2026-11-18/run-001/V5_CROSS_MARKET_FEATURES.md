# V5 cross-market features and time alignment

The initial matrix has 176 features:13 price/risk,52 native internals,52 aligned
global returns,19 derivative/transformed,18 structured lags,12 fixed cross-market
relationships and 10 research-only stock-breadth features. Separate liquidity
files add15 ETF and three research-only wider-stock volume features.

Global relationships include equal-weight available-market return/dispersion,
Indian-minus-global relative returns, oil x USD/INR, global return x participation,
US Tech100 versus Indian IT performance, Asia-minus-Europe divergence, equity/oil
divergence,21-session Indian/global and inter-global correlations, correlation
changes and cross-asset movement variability. No huge interaction-grid optimizer
was used. These features can be correlated and are not independent signals.

Premarket historical clock09:10 IST follows the completed Indian reference.
Known spot markets use IANA NewYork/London/Berlin/Paris/HongKong/Tokyo exchange
closing clocks plus a conservative two-hour publication allowance, handling DST.
Foreign daily bar dates remain source-session assumptions; receipt/revision
history is not authenticated. Unknown futures/CFD/FX conventions use a full extra
UTC-day completion buffer (source midnight+2days), not a fabricated exact close.
Actual available bars/holidays are respected by as-of joins; gaps over seven days
are missing, not indefinitely forward-filled. All assumed completion timestamps
are <=the recorded historical decision. No actual as-delivered vintage is claimed.

The extra global-delay stress C01_delayglobal adds an Indian-session lag to the
global/relationship block and stays exploratory. European/US close assumptions
and daily-anchor semantics remain a risk even with timezone-aware code; causal
code alone does not authenticate vendor publication history.

ETF proxies add GOLDBEES,SILVERBEES,MON100,HNGSNGBEES and NIFTYBEES returns,
realized variation and volume/prior21median. Gold/silver exposure is INR ETF
exposure, not spot; foreign ETFs carry tracking/premium/currency effects. The
price-only, native-only and joint liquidity ablations isolate the whole new block,
not each ETF's causal effect. Wider-stock median activity/active advances/volume
dispersion remain research-only current-basket proxies.

New-information attribution uses a2x2 experiment with cached estimators: exact
old sector features versus new native internals, and old V4 residual-shrunk law
versus V5's65% conditional/35% unconditional law. It is necessary because a better
forecast construction must not be advertised as proof of a new data source.

|model|n/disjoint|Brier|logloss|accuracy|balanced|CRPS|mean MAE|RMSE|50 cover|80 cover|
|---|---|---|---|---|---|---|---|---|---|---|
|AT00_old_newlaw|92/19|0.199665|0.586610|68.48%|67.90%|0.010942|1.409%|2.087%|58.7%|72.8%|
|AT01_new_oldlaw|92/19|0.198850|0.599065|70.65%|67.08%|0.011321|1.431%|2.176%|48.9%|68.5%|
|I00|92/19|0.186099|0.558036|76.09%|75.18%|0.010224|1.354%|1.985%|55.4%|76.1%|

The old/old reference is V4 D03 Brier.206257/CRPS.011882. Both changed feature
structure and changed distribution construction contribute descriptively; neither
crossed cell is independent validation. Additional global/broad/ETF increments
must still be judged with their matched ablations and uncertainty.
