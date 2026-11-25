# Timestamp correction and preserved first diagnostic

The first depth diagnostic, retained as depth-diagnostic.json and
depth-predictions.csv, aligned by exchange packet time alone. Review identified
that received_at may be later: such a snapshot is unavailable at the source
timestamp. Those first metrics are INVALIDATED for causal inference and are
preserved rather than overwritten. This is an implementation correction, not
a model/threshold/feature search after outcomes. Same stock/day, periods,
features, modelpenalty, execution assumptions and selection rules remain fixed.
Corrected run uses max(source_at,received_at) as availability and records
depth-diagnostic-asof.json/depth-predictions-asof.csv. Only corrected results
may enter findings. H3 remains FORWARD_DATA_REQUIRED under either result.
