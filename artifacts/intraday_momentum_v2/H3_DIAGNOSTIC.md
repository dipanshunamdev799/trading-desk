# Retained-book feasibility experiment, frozen before its outcomes

Inventory revealed RELIANCE13Nov2026has30350rawfeedupdates/334source minutes.
This invalidates an assumption of no retained depth at all. Broad historical
inventory timed out. Restrict this initial diagnostic to that one independently
chosen large/liquid stock-day; do not search names/dates for best performance.
It is research-exposed and cannot qualify any strategy or replace primary rules.

Read authentic PGframes, align1s as-oflastsnapshot(max2sage), availability is
max(exchange source timestamp,local received timestamp), exclude crossed/
emptybook, retain coverage. Episodes every30s, last30s returns as target.
Train09:16..11:59 with labelend<=12:00; test13:00..15:00. No overlapping
train/test horizons. Three fixed ridgeOLS models(alpha1,train-only scaling):
P=past60s/past5s midreturns;PV adds log1p60svolumeincrement;PVD additionally
adds5level displayedimbalance,spread,past5simbalance mean/std. Missinghistory
remains missing. No true aggressor/cancellation/order event claims.

Paired test reportMAE,correlation,directionalhit,incremental differences.
Economic diagnostic:long predictions only, threshold predicted30sreturn>
decisionknownspread+estimatedfees+2bpextraadversefriction+10bpsbuffer.
Size<=₹1lakh,1%previous60stradedvolume,10%currentbestaskquantity. Entryask
and30sexitbid plus1bp/sideextraimpact,fees; spread already explicit, no added
10bpsall-in charge. These are quote markouts, not guaranteedfills or funded
portfolio returns; no daily-trade-count claim. Shorts not economically traded.
Report eligibleepisodes/censoring; one day implies no day-block confidence
interval or general significance/forwardperformance claim. Model budget3
diagnostics, separate from30candleportfolio configurations. H3 remains
FORWARD_DATA_REQUIRED regardless of this feasibility result.
