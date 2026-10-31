const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const echarts = require("echarts");

function load(file, dependencies = {}) {
  const compiled = ts.transpileModule(fs.readFileSync(path.join(__dirname, file), "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX },
  });
  const exports = {};
  new Function("exports", "require", compiled.outputText)(exports, name => dependencies[name] || require(name));
  return exports;
}
const helpers = load("../components/optionGreeksCharts.ts");
const csvHelpers = load("../lib/optionGreeksCsv.ts");
const panel = load("../components/OptionGreeksPanel.tsx", {
  "@/components/optionGreeksCharts": helpers,
  "@/lib/optionGreeksCsv": csvHelpers,
  "@/components/EChartPanel": { default: () => null },
  "@/components/ExpandableChartPanel": { default: ({ children }) => React.createElement("div", null, children) },
  "@/components/SnapshotChartPanel": { default: ({ children, snapshot, asOf, loading }) => children({ snapshot, asOf, loading }) },
});
const data = {
  expiry: "2026-10-27", as_of: "2026-10-23", instrument_key: "NSE_INDEX|Nifty 50", source: "Upstox option chain",
  observed_at: "2026-10-23T15:25:00+05:30", reported_at: null, status: "historical", spot: 22620,
  data_available: true, available: 4, required: 4, complete_legs: 3, complete: false, hint: "A field is unavailable", basis: "Per-option provider values",
  rows: [
    { strike: 22500, call: { delta: .65, gamma: .000123, theta: -12.5, vega: 8.3, iv: 15.2 }, put: { delta: -.35, gamma: 0, theta: -11.2, vega: 8.3, iv: 16.1 } },
    { strike: 23000, call: { delta: .25, gamma: null, theta: -8, vega: 5, iv: 14 }, put: { delta: -.75, gamma: .00015, theta: -9, vega: 5, iv: 17 } },
  ],
};
function render(overrides = {}) {
  return renderToStaticMarkup(React.createElement(panel.default, { data, expiry: data.expiry, asOf: data.as_of, loading: false, selectedStrike: null, onSelectStrike() {}, ...overrides }));
}

test("signed Greeks, precise Gamma, true zero and missing values remain distinct", () => {
  assert.equal(helpers.formatGreek(-.35, "delta"), "-0.3500");
  assert.equal(helpers.formatGreek(.000123, "gamma"), "0.000123");
  assert.equal(helpers.formatGreek(0, "gamma"), "0.000000");
  assert.equal(helpers.formatGreek(null, "gamma"), "—");
  assert.equal(helpers.formatGreek(NaN, "delta"), "—");
  const html = render();
  for (const text of ["-0.3500", "-12.5000", "0.000000", "0.000123", "15.20", "—"]) assert.ok(html.includes(text), text);
});

test("saved source time is visible without claiming closing or live Greeks", () => {
  const html = render();
  for (const text of ["Saved session snapshot", "Captured", "Source Greek timestamp not supplied", "not necessarily the closing Greeks", "4/4 legs", "A field is unavailable"]) assert.ok(html.includes(text), text);
  assert.ok(!html.includes("Live Greeks"));
});

test("a mismatched date or expiry cannot display another selection's Greeks", () => {
  for (const overrides of [{ asOf: "2026-10-22" }, { expiry: "2026-11-03" }]) {
    const html = render(overrides);
    assert.ok(html.includes("unavailable for this selection"));
    assert.ok(!html.includes("-0.3500"));
    assert.ok(!html.includes("Captured"));
  }
});

test("latest REST and disconnected feed values carry distinct, honest status labels", () => {
  const rest = render({ data: { ...data, status: "latest_rest", hint: "Market closed. Current provider response; no certified closing timestamp." } });
  assert.ok(rest.includes("Latest available · market closed"));
  assert.ok(!rest.includes("Saved session snapshot"));
  const disconnected = render({ data: { ...data, status: "live", live_legs: 4 }, feedFresh: false });
  assert.ok(disconnected.includes("Retained feed snapshot"));
  assert.ok(disconnected.includes("live feed is unavailable or idle"));
  assert.ok(!disconnected.includes("4 legs streamed"));
});

test("missing dated snapshots show the reason rather than zero risk", () => {
  const html = render({ data: { ...data, data_available: false, status: "unavailable", rows: [], hint: "No option Greeks snapshot was saved for this date." } });
  assert.ok(html.includes("No option Greeks snapshot was saved"));
  assert.ok(!html.includes("0.0000"));
  assert.ok(!html.includes("greek-table"));
});

test("chart uses numeric strikes, missing-value gaps and original spot with precise tooltips", () => {
  const option = helpers.greekChartOption(data, "gamma", 22500);
  assert.equal(option.xAxis.type, "value");
  assert.deepEqual(option.series[0].data, [[22500, .000123], [23000, null]]);
  assert.equal(option.series[0].connectNulls, false);
  assert.equal(option.series[1].data[0][1], 0);
  const tip = option.tooltip.formatter([{ axisValue: 22500, seriesName: "Call", value: [22500, .000123] }]);
  assert.ok(tip.includes("0.000123"));
  for (const metric of ["delta", "gamma", "theta", "vega", "iv"]) {
    const chart = echarts.init(null, null, { renderer: "svg", ssr: true, width: 1000, height: 360 });
    try {
      chart.setOption(helpers.greekChartOption(data, metric, 22500));
      const svg = chart.renderToSVGString();
      for (const text of ["Spot 22,620", "Strike 22,500"]) assert.ok(svg.includes(text), text);
    } finally { chart.dispose(); }
  }
});

test("OI strike selection wins over nearest spot; a new chain drops a missing selection", () => {
  assert.equal(helpers.focusGreekStrike(data.rows, 22620, null), 22500);
  assert.equal(helpers.focusGreekStrike(data.rows, 22620, 23000), 23000);
  assert.equal(helpers.focusGreekStrike(data.rows, 22990, 24000), 23000);
  assert.equal(helpers.focusGreekStrike([], 22620, 23000), null);
});

function parseCsv(text) {
  const rows = []; let row = [], value = "", quoted = false;
  text = text.replace(/^\uFEFF/, "");
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char === '"') {
      if (quoted && text[i+1] === '"') { value += '"'; i++; }
      else quoted = !quoted;
    } else if (!quoted && char === ',') { row.push(value); value = ""; }
    else if (!quoted && char === '\r' && text[i+1] === '\n') { row.push(value); rows.push(row); row = []; value = ""; i++; }
    else value += char;
  }
  return rows;
}

test("CSV exports every strike and both sides at source precision, keeping blanks distinct from zeros", () => {
  const expanded = { ...data, rows: Array.from({length: 15}, (_, i) => ({ ...data.rows[i%2], strike: 22000+i*50 })) };
  const { csv, filename } = csvHelpers.optionGreeksCsv(expanded, false);
  const [headers, ...rows] = parseCsv(csv);
  const column = name => headers.indexOf(name);
  assert.equal(rows.length, 15); // export is independent of the near-focus table filter
  assert.equal(rows[0][column('call_gamma')], '0.000123');
  assert.equal(rows[0][column('put_gamma')], '0');
  assert.equal(rows[1][column('call_gamma')], '');
  assert.equal(rows[0][column('put_delta')], '-0.35');
  assert.equal(rows[0][column('call_theta')], '-12.5');
  assert.equal(rows[0][column('call_iv_pct')], '15.2');
  assert.equal(rows[0][column('as_of_ist')], data.as_of);
  assert.equal(rows[0][column('captured_at')], data.observed_at);
  assert.equal(rows[0][column('reported_at')], '');
  assert.equal(rows[0][column('feed_fresh_at_download')], 'false');
  assert.match(filename, /NSE_INDEX-Nifty-50-expiry-2026-10-27-asof-2026-10-23-20261023T095500Z.csv$/);
});

test("CSV escapes commas, quotes and multiline notes and retains per-field provenance", () => {
  const exported = { ...data, source:'Upstox, "saved"', hint:'Partial coverage\nOne field missing', rows:[{ ...data.rows[0],
    call_provenance:{greeks_source:'websocket',greeks_at:data.observed_at,iv_source:'rest',iv_at:data.observed_at} }] };
  const [headers, row] = parseCsv(csvHelpers.optionGreeksCsv(exported).csv);
  const value = name => row[headers.indexOf(name)];
  assert.equal(row.length, headers.length);
  assert.equal(value('source'), exported.source);
  assert.equal(value('coverage_note'), exported.hint);
  assert.equal(value('call_greeks_source'), 'websocket');
  assert.equal(value('call_iv_source'), 'rest');
  const safe = parseCsv(csvHelpers.optionGreeksCsv({...exported, source:'=1+1'}).csv);
  assert.equal(safe[1][headers.indexOf('source')], "'=1+1");
});

test("download buttons stay disabled for missing or mismatched snapshots", () => {
  assert.match(render(), /aria-label="Download option Greeks CSV"/);
  for (const overrides of [{asOf:'2026-10-22'}, {data:{...data,data_available:false,rows:[]}},
    {chartContext:{instrumentKey:'OTHER',snapshot:null,asOf:data.as_of,expiry:data.expiry,dates:[],loading:false,refreshId:0}}]) {
    const html = render(overrides);
    const button = html.match(/<button[^>]*aria-label="Download option Greeks CSV"[^>]*>/)?.[0];
    assert.ok(button?.includes('disabled=""'));
  }
});
