# NIFTY V18 — Information diffusion networks

We measured the announcing share, sector peers excluding that share, a matched native sector index where available, the broader index, and NIFTY over the same later interval. Firm-level exposures were fitted from earlier history. Same-date peer controls reduce common-market effects and native-index rows are displayed separately because index weights and the firm's mechanical share of each move vary. Bank/finance, IT, energy and other sector cohorts were available at different sample sizes. Raw announcing-stock effects and delayed peer excess returns receive separate rows. The intraday archive covers the smaller liquid basket, and no same-session sector bar may stand in for a later outcome. Lagged event inputs and price-only models provide a separate forecasts-based test of this association.

| sector | event family | horizon | metric | n | different dates | issuers | mean | low | high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bank | earnings | 1 | matched_abnormal | 28 | 26 | 5 | -0.003000 | -0.007695 | 0.001695 |
| bank | earnings | 1 | peer_excess | 28 | 26 | 5 | -0.001091 | -0.003591 | 0.001410 |
| bank | earnings | 1 | sector_excess | 28 | 26 | 5 | -0.000528 | -0.002622 | 0.001566 |
| bank | credit | 1 | matched_abnormal | 52 | 46 | 5 | -0.002091 | -0.009194 | 0.005011 |
| bank | credit | 1 | peer_excess | 47 | 42 | 5 | 0.000127 | -0.001648 | 0.001902 |
| bank | credit | 1 | sector_excess | 47 | 42 | 5 | 0.001168 | 0.000288 | 0.002048 |
| bank | earnings | 5 | matched_abnormal | 28 | 26 | 5 | 0.007992 | -0.000974 | 0.016959 |
| bank | earnings | 5 | peer_excess | 28 | 26 | 5 | -0.008882 | -0.013812 | -0.003953 |
| bank | earnings | 5 | sector_excess | 28 | 26 | 5 | -0.007160 | -0.009947 | -0.004372 |
| bank | credit | 5 | matched_abnormal | 52 | 46 | 5 | -0.005354 | -0.011340 | 0.000631 |
| bank | credit | 5 | peer_excess | 47 | 42 | 5 | 0.000457 | -0.003335 | 0.004248 |
| bank | credit | 5 | sector_excess | 47 | 42 | 5 | 0.000591 | -0.001872 | 0.003053 |
| bank | earnings | 21 | matched_abnormal | 24 | 23 | 5 | 0.002881 | -0.024498 | 0.030260 |
| bank | earnings | 21 | peer_excess | 24 | 23 | 5 | 0.008375 | -0.001021 | 0.017771 |
| bank | earnings | 21 | sector_excess | 24 | 23 | 5 | -0.002821 | -0.007369 | 0.001726 |
| bank | credit | 21 | matched_abnormal | 51 | 45 | 5 | -0.000772 | -0.015048 | 0.013503 |
| bank | credit | 21 | peer_excess | 46 | 41 | 5 | 0.007012 | -0.001011 | 0.015034 |
| bank | credit | 21 | sector_excess | 46 | 41 | 5 | -0.000383 | -0.006388 | 0.005621 |
| energy | earnings | 1 | matched_abnormal | 68 | 58 | 11 | 0.000041 | -0.004576 | 0.004658 |
| energy | earnings | 1 | peer_excess | 65 | 56 | 11 | -0.001790 | -0.004709 | 0.001128 |
| energy | earnings | 1 | sector_excess | 65 | 56 | 11 | -0.001064 | -0.003465 | 0.001337 |
| energy | credit | 1 | matched_abnormal | 82 | 79 | 8 | -0.001217 | -0.002681 | 0.000247 |
| energy | credit | 1 | peer_excess | 80 | 77 | 8 | -0.001094 | -0.002916 | 0.000727 |
| energy | credit | 1 | sector_excess | 80 | 77 | 8 | -0.001397 | -0.003537 | 0.000743 |
| energy | earnings | 5 | matched_abnormal | 67 | 57 | 11 | 0.001040 | -0.010977 | 0.013056 |
| energy | earnings | 5 | peer_excess | 64 | 55 | 11 | -0.005981 | -0.010477 | -0.001484 |
| energy | earnings | 5 | sector_excess | 64 | 55 | 11 | -0.003790 | -0.008463 | 0.000883 |
| energy | credit | 5 | matched_abnormal | 82 | 79 | 8 | -0.003110 | -0.006781 | 0.000562 |
| energy | credit | 5 | peer_excess | 80 | 77 | 8 | -0.003345 | -0.005718 | -0.000972 |
| energy | credit | 5 | sector_excess | 80 | 77 | 8 | -0.002882 | -0.005028 | -0.000735 |
| energy | earnings | 21 | matched_abnormal | 59 | 52 | 11 | -0.000129 | -0.012224 | 0.011967 |
| energy | earnings | 21 | peer_excess | 56 | 50 | 11 | -0.019447 | -0.024862 | -0.014032 |
| energy | earnings | 21 | sector_excess | 56 | 50 | 11 | -0.000452 | -0.006190 | 0.005286 |
| energy | credit | 21 | matched_abnormal | 77 | 74 | 8 | -0.007055 | -0.030043 | 0.015933 |
| energy | credit | 21 | peer_excess | 75 | 72 | 8 | -0.011540 | -0.016873 | -0.006206 |
| energy | credit | 21 | sector_excess | 75 | 72 | 8 | -0.005074 | -0.010149 | 1.50e-06 |
| finance | earnings | 1 | matched_abnormal | 43 | 38 | 7 | -0.004327 | -0.008790 | 0.000135 |
| finance | earnings | 1 | peer_excess | 39 | 35 | 7 | 0.000103 | -0.002764 | 0.002969 |
| finance | earnings | 1 | sector_excess | 39 | 35 | 7 | 0.001116 | 0.000272 | 0.001960 |
| finance | earnings | 5 | matched_abnormal | 42 | 37 | 7 | -0.003104 | -0.014052 | 0.007843 |
| finance | earnings | 5 | peer_excess | 38 | 34 | 7 | 0.005443 | 0.000859 | 0.010028 |
| finance | earnings | 5 | sector_excess | 38 | 34 | 7 | 0.003841 | 0.001890 | 0.005793 |

[Sector and wider-market links](domestic-diffusion-study.csv) · [Native and peer outcome panel](stock-event-pairs.csv.gz) · [Synchronized intraday rows](intraday-event-responses.csv.gz) · [Transfer and dated placebos](event-transfer-comparison.csv)
