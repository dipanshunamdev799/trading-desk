import type { MaxPainGreeks } from "./api";

function cell(value: unknown): string {
  if (value == null || typeof value === "number" && !Number.isFinite(value)) return "";
  // Numeric negatives are data; only text is protected against spreadsheet formulas.
  let text = String(value);
  if (typeof value === "string" && /^[\s]*[=+\-@]/.test(text)) text = "'" + text;
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

export function optionGreeksCsv(data: MaxPainGreeks, feedFresh?: boolean) {
  const headers = ["instrument_key", "as_of_ist", "expiry", "captured_at", "reported_at", "snapshot_status_at_capture", "feed_fresh_at_download", "source", "spot", "strike",
    "call_delta", "call_gamma", "call_theta", "call_vega", "call_iv_pct",
    "put_delta", "put_gamma", "put_theta", "put_vega", "put_iv_pct",
    "call_greeks_source", "call_greeks_at", "call_iv_source", "call_iv_at",
    "put_greeks_source", "put_greeks_at", "put_iv_source", "put_iv_at", "basis", "coverage_note"];
  const rows = [...data.rows].sort((a, b) => a.strike-b.strike).map(row => [
    data.instrument_key, data.as_of, data.expiry, data.observed_at, data.reported_at, data.status, feedFresh, data.source, data.spot, row.strike,
    row.call.delta, row.call.gamma, row.call.theta, row.call.vega, row.call.iv,
    row.put.delta, row.put.gamma, row.put.theta, row.put.vega, row.put.iv,
    row.call_provenance?.greeks_source, row.call_provenance?.greeks_at, row.call_provenance?.iv_source, row.call_provenance?.iv_at,
    row.put_provenance?.greeks_source, row.put_provenance?.greeks_at, row.put_provenance?.iv_source, row.put_provenance?.iv_at, data.basis, data.hint,
  ]);
  const safe = (value: string) => value.replace(/[^a-zA-Z0-9_-]+/g, "-").replace(/^-+|-+$/g, "");
  const at = data.observed_at && Number.isFinite(Date.parse(data.observed_at))
    ? new Date(data.observed_at).toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z") : "unknown";
  return { csv: "\uFEFF" + [headers, ...rows].map(row => row.map(cell).join(",")).join("\r\n") + "\r\n",
    filename: `option-greeks-${safe(data.instrument_key)}-expiry-${safe(data.expiry)}-asof-${safe(data.as_of)}-${at}.csv` };
}

export function downloadOptionGreeksCsv(data: MaxPainGreeks, feedFresh?: boolean) {
  const { csv, filename } = optionGreeksCsv(data, feedFresh);
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const anchor = document.createElement("a");
  anchor.href = url; anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click(); anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
