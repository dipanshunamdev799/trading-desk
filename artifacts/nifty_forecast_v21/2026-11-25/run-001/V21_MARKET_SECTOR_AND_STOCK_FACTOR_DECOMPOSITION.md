# V21 Market Sector And Stock Factor Decomposition

The factor decomposition fits a shrunk market beta and a sector-relative beta using up to **100 earlier daily observations**. At least **35 paired rows** are required per leg. The empirical market and sector returns serve only as historical labels when fitting. Each future factor in the forecast is estimated or simulated from eligible earlier information. Raw security, market-relative, sector-relative and factor-residual labels are all separate. Names without a dated group fall back to a broad-market grouping. Financial leadership, cyclical and defensive structure, momentum, liquidity and relative volatility are evaluated in the dated designs. Size is proxied by the January liquidity ordering or dated index weights where supported. Authenticated financial-result features cover the available quality and earnings information. No standalone size or quality premium is inferred from undated classifications.

Median trailing diagnostics across the audit dates put raw squared return variation at **0.000575**, after the market term at **0.000399**, and after the sector-relative term at **0.000376**. Median market and sector coefficients were **0.9496** and **0.0000**. These are historical exposure diagnostics. The comparison of average absolute stock forecasts with the magnitude of their signed weighted sum shows how much component movement survives aggregation.

| horizon | n | weight eff | expected eff | realized eff | gross signal | net signal | portfolio over asset variance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 265 | 23.168585 | 21.359840 | 18.605076 | 0.003447 | 0.002970 | 0.344356 |
| 21 | 217 | 23.317193 | 21.401809 | 18.626830 | 0.009735 | 0.008466 | 0.331867 |

[factor-exposure-receipt.csv](factor-exposure-receipt.csv) · [feature-definitions.json](feature-definitions.json) · [component-panel.npz](component-panel.npz) · [stock-leaderboard.csv](stock-leaderboard.csv) · [market-factor-leaderboard.csv](market-factor-leaderboard.csv) · [concentration-cases.csv](concentration-cases.csv)
