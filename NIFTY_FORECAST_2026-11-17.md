# NIFTY forecast experiment — 17 November 2026

**Frozen call: a slight upward bias, with low confidence and substantial two-way risk.**
The fixed ensemble outputs **59.8% upward** for the close versus Monday's
25,291.10 reference, and **54.6% upward** from today's open to close.
These are raw model estimates, not demonstrated 60%/55% success rates.
The current US sell-off makes the domestic upward lean fragile. A clean bullish
trend throughout the session is not the forecast.

Issued **2026-11-17T00:41:57.880635+05:30**. Raw input batches were frozen at
2026-11-17T00:33:17.687726+05:30, 2026-11-17T00:34:15.755857+05:30. No 17 November Indian session prices
were available. Monday's quote is corroborated by the [NSE market page](https://www.nse.in/).
The [NSE 2026 holiday circular](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf)
and the saved Upstox holiday response show no scheduled holiday for 17 November.

## The actual call, ranges and ways it can fail

|Measure|Frozen estimate|Interpretation|
|---|---:|---|
|Close above Monday|59.8%|Raw ensemble probability; low trust in calibration|
|Close above today's open|54.6%|Separate outcome; models disagree materially|
|Analogue median close|25,311|About +20 points; a center estimate, not a precise target|
|Analogue weighted mean close|25,293|Almost flat; adverse tails offset frequent small gains|
|Central 50% historical closing band|25,173–25,429|Trailing 252-session empirical reference distribution|
|Central 80% historical closing band|25,008–25,559|An outside move remains possible|

The bands describe the **closing value**, not a boundary containing the intraday
path. Their walk-forward coverage was 45.6%
and 78.2%, respectively. They are deliberately
simple empirical bands rather than fitted precision targets.

Scenario markers, specified as a qualitative reading of observed levels:

- **Upward continuation:** acceptance above Monday's **25,337.60** high makes
  the recent **25,424.35** high the next reference; 25,500 is a nearby option-OI
  reference. These are conditional markers, not separately validated forecasts.
- **Two-way/base scenario:** repeated trading within Monday's **25,172.10–25,337.60**
  range would fit the weak directional evidence. The analogue median is 25,311.
- **Downward failure:** sustained trading below **25,172.10** would weaken the
  bullish reading; Friday's **25,054.40** low and the 25,000 area are lower references.
  Overnight news can gap directly through any of these levels.

## What the current inputs say

|Independent evidence group|Observed input at the freeze|Reading|
|---|---|---|
|Domestic prices|NIFTY +0.584%; Bank Nifty +0.888%; financials +0.574%|Supports an upward bias|
|Participation|31 advancing / 19 declining constituents, dated 15:29 IST; auto −1.288%, pharma −1.533%, metals −1.499%, realty −1.341%; FMCG +1.867%|Some breadth, but leadership is uneven and partly defensive|
|Overnight India proxy|GIFT Nifty 25,345.0, +0.196% versus its own previous value|Mild support; the futures/spot spread is not an exact opening-gap forecast|
|Global equities|S&P 500 -1.730%; Nasdaq -2.256%; Dow -1.230%; US futures -1.662%|The strongest contrary input; US cash session still open|
|Oil, currency and dollar|Brent 92.33, -3.662%; USD/INR 93.912, -0.130%; DXY +0.167%|Cheaper oil and firmer INR support India; global risk appetite is mixed|
|Volatility|India VIX 15.68, +1.161%|A move-size/risk input; not a directional vote|
|Participant futures|61,039 FII index-futures longs versus 117,726 shorts; net −56,687 contracts|Bearish positioning, which can also supply squeeze risk|
|Options and expiry|Listed expiry 17 November; PCR 0.944; max pain 25,200; ATM 25,300 straddle 167.9 points|Reference snapshot only: no publisher market timestamp|
|Cash institutions|FII/DII endpoint amounts fail the desk's documented-unit checks; official NSE adapter redirected|Excluded rather than assigning an unverified crore value|
|News and economic events|Upstox NIFTY news returned an empty object; no reliable complete event inventory was supplied|Unknown, not evidence that there are no events|

Current globals are delayed indicative quotes. The domestic constituent breadth
reading is near the close, not a separately verified closing breadth file.
Options OI does not reveal whether each position was initiated by a buyer or
writer. PCR, max pain and straddle premium have no fitted directional weight in
this experiment; straddle premium is not an 80% interval or a profit target.

## The historical check

The model uses **62 features**, **2,427 eligible feature rows**, Indian daily
history from January 2017, and available global history. Price features cover
returns, EMA distances, RSI, candle shape, gaps, realized volatility and ATR.
Context adds sector-relative returns, a sector participation proxy, India VIX,
and conservatively lagged completed global sessions. Sector participation is
not reconstructed constituent breadth; no present-day stock membership is
backfilled into a historical breadth label.

Fixed candidates and the equal-weight ensemble were specified in
[PROTOCOL.md](research/nifty_forecast/PROTOCOL.md) before performance was viewed.
The 504 target sessions run **4 November 2024–16 November 2026**. Each calendar
month is predicted with models fitted only to preceding resolved outcomes, with
at most 1,260 training examples. Scaling and imputation are fitted on training
data. Parameters were not tuned to this evaluation period.

|Model|Today's close-up estimate|Close accuracy|Close Brier ↓|Today's intraday-up estimate|Intraday accuracy|Intraday Brier ↓|
|---|---:|---:|---:|---:|---:|---:|
|Historical frequency|52.1%|49.4%|0.2531|47.7%|52.8%|0.2497|
|Previous day|55.0%|52.8%|0.2497|55.0%|46.2%|0.2563|
|20-session trend|55.0%|50.8%|0.2517|55.0%|47.0%|0.2555|
|Price-only logistic|54.8%|53.2%|0.2529|43.5%|55.2%|0.2462|
|All-context logistic|54.5%|52.4%|0.2657|53.6%|51.0%|0.2554|
|60 historical analogues|57.5%|51.4%|0.2544|51.2%|52.2%|0.2503|
|Nonlinear random features|67.5%|51.4%|0.2573|58.8%|53.4%|0.2531|
|Fixed ensemble|59.8%|51.6%|0.2554|54.6%|52.8%|0.2497|
|Constant 50/50|50.0%|No directional call|0.2500|50.0%|No directional call|0.2500|

The main result is **no established predictive advantage from adding these
inputs**. The ensemble's close-direction accuracy is 51.6%, but its probability
score is worse than both historical frequency and constant 50/50. An always-down
direction would have been correct 50.6% of these sessions. The ensemble's paired
Brier improvement over historical frequency is −0.00229, with a conditional
95% ten-session-block interval of **-0.00928 to 0.00543**.
For intraday direction its accuracy matches the 52.8% frequency baseline; the
probability-score difference is negligible and its interval crosses zero.

Calibration is weak: close forecasts in the 55–60% bin occurred 105 times, but
only **48.6%** of those sessions closed up. Forecasts at least 60% upward occurred
156 times and closed up **55.8%** of the time. Today's 59.8% output therefore
cannot honestly be advertised as a calibrated 60% chance. The price-only model
currently gives only 43.5% for an up open-to-close session, versus 54.6% for the
ensemble. That disagreement is part of the result, not a reason to select a
different winner after the test.

The final replay observation uses Monday's provisional quote-derived daily
bar. A separate [503-session published-candle-only validation](artifacts/nifty_forecast/2026-11-17/run-v3/validation-published-only.json)
excludes it. Its close ensemble Brier is
0.2554 versus
0.2532 for
the baseline, so the conclusion is unchanged.

## Data quality and coverage

The catalog now contains **127 concepts**, broader than the older 64-factor
research snapshot. The new freeze retains **46,757 dashboard observations**.
An observation count is not an independent daily sample count. The complete
[127-concept input audit](artifacts/nifty_forecast/2026-11-17/run-v3/factor-inventory.md)
and its structured JSON preserve missing and excluded readings.

|Concept group|Total|Dated context|Undated context|Quality excluded|Unavailable|
|---|---:|---:|---:|---:|---:|
|commodities currencies|9|9|0|0|0|
|derivatives options|15|0|12|0|3|
|earnings constituents|11|0|0|0|11|
|economy government|20|0|0|0|20|
|global markets|10|9|0|0|1|
|institutional flows|8|2|0|2|4|
|news events|13|0|0|0|13|
|rates bonds|8|1|0|0|7|
|sectors breadth|15|11|0|0|4|
|technicals|18|14|0|0|4|

"Dated context" means a timestamp exists; it does not certify freshness or
historical trainability. Factor JSON retains source dates and age. Raw historical
prices are today's revised history, not an archived point-in-time data vintage.
The following safeguards and limits matter:

- Upstox's NIFTY daily endpoint still stops at Friday, 13 November. 10 Monday
  Indian index/VIX bars are reconstructed from post-close quote OHLC; their
  previous close must match the published historical series. NIFTY 500's Monday
  context is missing and receives a training-derived imputation plus a flag.
- Auto history supplied 474 duplicate session rows, including 248 with differing
  OHLC values. Canonicalization deterministically prefers the midnight daily
  row; duplicates never become extra training samples.
- Global history contained **177 invalid OHLC rows**, rejected before features
  were built. Gaps are not silently turned into valid bars. Close changes between
  remaining observed sessions can span multiple calendar days.
- For a 00:30 IST decision, the preceding US cash day may still be open. Fitted
  global features require a source date strictly earlier than target date minus
  one calendar day. This is conservative for Asian markets. The ongoing US
  sell-off appears in the written scenarios, not retrospectively in the fitted
  feature panel. The model therefore omits useful information visible now.
- Price, flow and option history do not have the same coverage. Recent snapshots
  were not backfilled across years; cash amounts with uncertain units were not used.
- [Upstox documents](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/)
  a maximum decade per daily request; the successful batch uses January 2017
  onward. Source errors and both acquisition and market times are preserved.

## Reproduce and score

Seven focused checks pass: raw-input hashes, unfinished-US-day exclusion,
invariance to future Indian-price changes, training-only scaling, next-session
labels, chronological walk-forward training, and logistic probability sanity.

```powershell
.\.venv\Scripts\python.exe -m research.nifty_forecast.verify
.\.venv\Scripts\python.exe -m research.nifty_forecast.engine --out artifacts/nifty_forecast/2026-11-17/reproduction-01
```

After the target session closes and Upstox publishes its daily candle:

```powershell
.\.venv\Scripts\python.exe -m research.nifty_forecast.score
```

The scorer writes a separate outcome file with the official daily open/close,
reference revisions, direction outcomes, Brier scores and interval hits. It
leaves the original [forecast.json](artifacts/nifty_forecast/2026-11-17/run-v3/forecast.json)
unchanged. The outcome is currently **unresolved**. No scheduler or orders were
created, and no existing bot configuration was changed.

The statistical experiment and the qualitative scenario assessment are both
frozen here. A better experiment from this starting point is a series of future
calls at one fixed clock, with timestamped intraday global inputs and published
option/flow observations captured prospectively. One good or bad day will not
establish whether the method works.
