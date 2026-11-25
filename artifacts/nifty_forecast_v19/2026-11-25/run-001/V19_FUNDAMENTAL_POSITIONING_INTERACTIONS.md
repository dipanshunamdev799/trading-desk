# V19 Fundamental Positioning Interactions

Corporate information uses the V18 aggregate financial disclosure schedule and measured outcomes from the preserved point-in-time feeds. Added interaction fields combine earnings surprises with FII position changes, growth with breadth and delivery, financial news with stock derivatives, disclosure direction with concentration, and calendar exposures with eligible IV. They describe cross-state association. Financially identifying the counterparties and causes would require linkage and timing beyond these inputs.

| horizon | arm | n | active | brier | crps |
| --- | --- | --- | --- | --- | --- |
| 5 | B_corporate | 265 | 265 | 0.248263 | 0.011103 |
| 5 | A_structural | 265 | 265 | 0.238274 | 0.010658 |
| 5 | F_plus_corporate | 265 | 264 | 0.254909 | 0.011202 |
| 5 | G_interactions | 265 | 264 | 0.246780 | 0.011013 |
| 5 | C_delivery | 265 | 264 | 0.242413 | 0.010826 |
| 5 | F_all | 265 | 264 | 0.243393 | 0.010745 |
| 5 | D_participants | 265 | 265 | 0.239255 | 0.010619 |
| 5 | H_block_control | 265 | 265 | 0.241430 | 0.010661 |
| 5 | H_one_session | 265 | 265 | 0.244571 | 0.010754 |
| 5 | H_five_sessions | 265 | 265 | 0.245958 | 0.010871 |
| 5 | E_transactions | 265 | 265 | 0.247469 | 0.010952 |
| 21 | B_corporate | 217 | 217 | 0.312599 | 0.029850 |
| 21 | A_structural | 217 | 217 | 0.302805 | 0.028519 |
| 21 | F_plus_corporate | 217 | 216 | 0.290598 | 0.029068 |
| 21 | G_interactions | 217 | 216 | 0.297443 | 0.028899 |
| 21 | C_delivery | 217 | 216 | 0.336082 | 0.030889 |
| 21 | F_all | 217 | 216 | 0.290132 | 0.028048 |
| 21 | D_participants | 217 | 217 | 0.285350 | 0.027800 |
| 21 | H_block_control | 217 | 217 | 0.351503 | 0.031649 |
| 21 | H_one_session | 217 | 217 | 0.290813 | 0.027905 |
| 21 | H_five_sessions | 217 | 217 | 0.303937 | 0.028469 |
| 21 | E_transactions | 217 | 217 | 0.334182 | 0.030454 |

The additive path uses the exact archived corporate parent first, then estimates its additional error from matured cases. Comparing it with the structural-plus-nonprice model estimates the other order on the same origins. Interaction changes and the six-order Shapley results are incremental losses across paired tables.

| horizon | cutoff | addition | brier | crps |
| --- | --- | --- | --- | --- |
| 5 | preauction_0855 | corporate_first | -0.009989 | -0.000445 |
| 5 | preauction_0855 | positioning_after_corporate | -0.006646 | -0.000099 |
| 5 | preauction_0855 | positioning_first | -0.005119 | -0.000087 |
| 5 | preauction_0855 | corporate_after_positioning | -0.011516 | -0.000457 |
| 5 | preauction_0855 | interaction_after_corporate | 0.001483 | 0.000090 |
| 5 | previous_1700 | corporate_first | -0.009703 | -0.000473 |
| 5 | previous_1700 | positioning_after_corporate | -0.011974 | -0.000296 |
| 5 | previous_1700 | positioning_first | -0.010159 | -0.000209 |
| 5 | previous_1700 | corporate_after_positioning | -0.011518 | -0.000559 |
| 5 | previous_1700 | interaction_after_corporate | 0.000783 | -0.000014 |
| 21 | preauction_0855 | corporate_first | -0.009794 | -0.001331 |
| 21 | preauction_0855 | positioning_after_corporate | 0.022002 | 0.000782 |
| 21 | preauction_0855 | positioning_first | 0.012673 | 0.000472 |
| 21 | preauction_0855 | corporate_after_positioning | -0.000466 | -0.001021 |
| 21 | preauction_0855 | interaction_after_corporate | 0.015157 | 0.000951 |
| 21 | previous_1700 | corporate_first | -0.006357 | -0.001041 |
| 21 | previous_1700 | positioning_after_corporate | 0.020408 | 0.000649 |
| 21 | previous_1700 | positioning_first | 0.007959 | 0.000223 |
| 21 | previous_1700 | corporate_after_positioning | 0.006091 | -0.000615 |
| 21 | previous_1700 | interaction_after_corporate | 0.014979 | 0.000721 |

| horizon | cutoff | block | brier | crps |
| --- | --- | --- | --- | --- |
| 5 | preauction_0855 | delivery | -0.001175 | -0.000069 |
| 5 | preauction_0855 | participant | 0.001706 | 0.000158 |
| 5 | preauction_0855 | transactions | -0.005649 | -0.000176 |
| 5 | previous_1700 | delivery | -0.003686 | -0.000083 |
| 5 | previous_1700 | participant | -0.002926 | -1.77e-06 |
| 5 | previous_1700 | transactions | -0.003547 | -0.000125 |
| 21 | preauction_0855 | delivery | -0.013760 | -0.000966 |
| 21 | preauction_0855 | participant | 0.039274 | 0.002206 |
| 21 | preauction_0855 | transactions | -0.012841 | -0.000768 |
| 21 | previous_1700 | delivery | -0.013992 | -0.001042 |
| 21 | previous_1700 | participant | 0.034640 | 0.002025 |
| 21 | previous_1700 | transactions | -0.012689 | -0.000760 |

[corporate-addition-orders.csv](corporate-addition-orders.csv) · [v19-block-shapley-summary.csv](v19-block-shapley-summary.csv) · [v18-activity-shapley-summary.csv](v18-activity-shapley-summary.csv) · [v19-block-shapley.csv.gz](v19-block-shapley.csv.gz) · [endpoint-fit-receipts.ndjson.gz](endpoint-fit-receipts.ndjson.gz) · [refit-reselection-summary.csv](refit-reselection-summary.csv)
