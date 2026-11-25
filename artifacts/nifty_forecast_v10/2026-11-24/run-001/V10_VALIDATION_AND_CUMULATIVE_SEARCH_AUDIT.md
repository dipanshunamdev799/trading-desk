# V10 Validation And Cumulative Search Audit

All historical data were inspected in the V1–V10 research process. V9's historical inventory records **454 exact configuration fingerprints** and **583 distinct stored prediction fingerprints**. V10 added **155** named configurations, **298** scored model–horizon vectors and **266** distinct vector hashes under the V10 schema and rounding. Different historical schemas and recording coverage limit any single cumulative total. Initial batches, target-completeness correction, empirical overlap covariance, learning curves, and mixtures have dated registries. The last four stages are adaptive. Prior hash verification covered **11,284** protected files with **0** differences.

## Paired block bootstrap on weekly comparisons

| weekly scope | adjusted contrasts | origins | block-10 critical |
| --- | --- | --- | --- |
| early | 2178 | 173 | 3.737052 |
| later | 2886 | 92 | 3.646916 |
| combined | 2178 | 265 | 3.753538 |

Positive gain means control loss less candidate loss. The resampling uses 2,000 shared circular block draws for sizes 5, 10 and 15, maximizing standardized centered loss deviations across the declared comparison family within each scope. Nominal and simultaneous intervals are recorded. These bounds address a finite V10 set conditional on a research-exposed archive. Monthly reports use matched losses and disjoint stress given the low disjoint count.

## Bounded selection replay with block-permuted training labels

| horizon | cohort | score | origins | actual_max_gain | null_median | null_p95 | null_max | share_null_at_least_as_large |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | early | brier_gain | 4 | 0.063607 | 0.040806 | 0.150487 | 0.172946 | 0.250000 |
| 5 | early | crps_gain | 4 | 0.003542 | 0.002245 | 0.005357 | 0.005405 | 0.312500 |
| 5 | later | brier_gain | 5 | 0.120197 | 0.060400 | 0.100712 | 0.119849 | 0.000000 |
| 5 | later | crps_gain | 5 | 0.003928 | 0.001548 | 0.003846 | 0.003988 | 0.062500 |
| 21 | early | brier_gain | 4 | 0.059436 | 0.137079 | 0.247099 | 0.308858 | 1.000000 |
| 21 | early | crps_gain | 4 | 0.000607 | 0.003204 | 0.013041 | 0.014324 | 1.000000 |
| 21 | later | brier_gain | 4 | 0.054688 | -0.018684 | 0.100903 | 0.178451 | 0.187500 |
| 21 | later | crps_gain | 4 | -0.003795 | -0.004522 | 0.006378 | 0.008752 | 0.437500 |

Six representative specifications were compared on the first origin per selected exposed monthly fit, **16** null draws per horizon. Each draw refits each configuration and scores the biggest mean Brier or CRPS gain using real held-out outcomes, validation targets and history. The sparse origin subset and small simulation budget make the empirical tail coarse. This is a falsification check on the selected gain and has limited scope.

The exact-copy and future-information tests passed **54** V10 checks with maximum atom error **0**. Additional controls delay sources, remove groups and training months, resample training blocks, perturb monthly states and randomize, shift or replace transfer tasks. Search interval coverage, failure counts and legality of all fit partitions were verified by [verification](verification.json).

## Recorded unestimated folds

| model | reason | folds |
| --- | --- | --- |
| LC_BLOCK_126 | ValueError: fewer than registered mature training rows | 4 |
| LC_BLOCK_189 | ValueError: fewer than registered mature training rows | 10 |
| LC_BLOCK_252 | ValueError: fewer than registered mature training rows | 17 |
| LC_BLOCK_300 | ValueError: fewer than registered mature training rows | 21 |
| LC_PLAIN_126 | ValueError: fewer than registered mature training rows | 4 |
| LC_PLAIN_189 | ValueError: fewer than registered mature training rows | 10 |
| LC_PLAIN_252 | ValueError: fewer than registered mature training rows | 17 |
| LC_PLAIN_300 | ValueError: fewer than registered mature training rows | 21 |
| LC_SPREAD_126 | ValueError: fewer than registered mature training rows | 4 |
| LC_SPREAD_189 | ValueError: fewer than registered mature training rows | 10 |
| LC_SPREAD_252 | ValueError: fewer than registered mature training rows | 17 |
| LC_SPREAD_300 | ValueError: fewer than registered mature training rows | 21 |
| LC_STUDENT_126 | ValueError: fewer than registered mature training rows | 4 |
| LC_STUDENT_189 | ValueError: fewer than registered mature training rows | 10 |
| LC_STUDENT_252 | ValueError: fewer than registered mature training rows | 17 |
| LC_STUDENT_300 | ValueError: fewer than registered mature training rows | 21 |
| N_DOM_RISK | ValueError: INVALID_DISTRIBUTION | 25 |
| N_GLOBAL_RISK | ValueError: INVALID_DISTRIBUTION | 25 |
