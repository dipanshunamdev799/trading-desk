const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");
const echarts = require("echarts");

// Load the chart builder without requiring a browser or a Next.js server.
const source = fs.readFileSync(path.join(__dirname, "../components/maxpainCharts.ts"), "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
});
const chartExports = {};
new Function("exports", "require", compiled.outputText)(chartExports, require);
const { premiumPnlOption, payoutCurveOption, intradayOption } = chartExports;

function optionFor(view) {
  const seller = { name: "Seller combined", color: "#E5C07B", values: [-30e7, 10e7, -20e7], primary: true };
  const buyer = { name: "Buyer combined", color: "#61AFEF", values: [30e7, -10e7, 20e7], primary: true };
  const portfolio = view === "buyer" ? buyer : seller;
  return premiumPnlOption({
    candidates: [22000, 22500, 23500],
    series: view === "compare" ? [seller, buyer] : [
      portfolio,
      { name: "−10% premium", color: "#8B9AAB", values: portfolio.values.map((value) => value - 1e7), dashed: true },
      { name: "+10% premium", color: "#B8A0E0", values: portfolio.values.map((value) => value + 1e7), dashed: true },
    ],
    spot: 22623.75,
    maxPain: 22500,
    extremePrice: 22000,
    extremeLabel: view === "buyer" ? "Buyer max" : "Seller min",
    breakevens: [22350.25, 23078.5],
  });
}

for (const view of ["seller", "buyer", "compare"]) {
  test(`${view} renders exact spot, Max Pain, breakevens and extrema`, () => {
    const chart = echarts.init(null, null, { renderer: "svg", ssr: true, width: 900, height: 360 });
    try {
      chart.setOption(optionFor(view));
      const svg = chart.renderToSVGString();
      for (const label of ["Spot 22,623.75", "Max Pain 22,500", "BE 22,350.25", "BE 23,078.5", view === "buyer" ? "Buyer max 22,000" : "Seller min 22,000"]) {
        assert.ok(svg.includes(label), `Missing visible reference: ${label}`);
      }
      chart.dispatchAction({ type: "legendUnSelect", name: view === "buyer" ? "Buyer combined" : "Seller combined" });
      assert.ok(chart.renderToSVGString().includes("Spot 22,623.75"), "References must remain when a portfolio is hidden");
    } finally {
      chart.dispose();
    }
  });
}

test("uneven settlement prices use numeric coordinates", () => {
  const option = optionFor("seller");
  assert.equal(option.xAxis.type, "value");
  assert.deepEqual(option.series[0].data, [[22000, -30e7], [22500, 10e7], [23500, -20e7]]);
  const references = option.series.flatMap((series) => series.markLine?.data ?? []);
  assert.ok(references.some((line) => line.xAxis === 22623.75));
  assert.ok(references.some((line) => line.xAxis === 22350.25));
  assert.ok(references.some((line) => line.yAxis === 0));
});

test("tooltips read the P&L from price/value pairs", () => {
  const option = optionFor("seller");
  const tooltip = option.tooltip.formatter([
    { axisValue: 22500, seriesName: "Seller combined", value: [22500, 10e7], data: [22500, 10e7] },
    { axisValue: 22500, seriesName: "Seller −10% prem", value: [22500, -2e7], data: [22500, -2e7] },
  ]);
  assert.ok(tooltip.includes("Settlement 22,500"));
  assert.ok(tooltip.includes("₹10 Cr"));
  assert.ok(tooltip.includes("−₹2 Cr"));
});

test("payoff uses price coordinates and renders off-strike spot markers", () => {
  const option = payoutCurveOption({
    candidates: [22000, 22500, 23500],
    call: [0, 1e7, 4e7], put: [3e7, 1e7, 0], total: [3e7, 2e7, 4e7],
    maxPain: 22500, spot: 22623.75,
  });
  assert.equal(option.xAxis.type, "value");
  assert.deepEqual(option.series[0].data, [[22000, 3e7], [22500, 2e7], [23500, 4e7]]);
  const chart = echarts.init(null, null, { renderer: "svg", ssr: true, width: 760, height: 340 });
  try {
    chart.setOption(option);
    assert.ok(chart.renderToSVGString().includes("Spot 22,623.75"));
    assert.ok(chart.renderToSVGString().includes("Max Pain 22,500"));
    chart.dispatchAction({ type: "legendUnSelect", name: "Combined" });
    assert.ok(chart.renderToSVGString().includes("Spot 22,623.75"));
  } finally { chart.dispose(); }
  const tooltip = option.tooltip.formatter([
    { dataIndex: 1, seriesName: "Combined", value: [22500, 2e7] },
    { dataIndex: 1, seriesName: "Call", value: [22500, 1e7] },
    { dataIndex: 1, seriesName: "Put", value: [22500, 1e7] },
  ]);
  assert.ok(tooltip.includes("Settlement 22,500"));
  assert.ok(tooltip.includes("₹2 Cr"));
});

test("intraday tooltip shows the same precise prices and gap from either panel", () => {
  const option = intradayOption({ times: ["12:45"], maxPain: [22650], spot: [22399.15] });
  for (const seriesName of ["Max Pain", "Spot − Max Pain"]) {
    const tooltip = option.tooltip.formatter([{ axisValue: "12:45", dataIndex: 0, seriesName, data: 22650 }]);
    assert.ok(tooltip.includes("12:45 IST"));
    assert.ok(tooltip.includes("22,650.00"));
    assert.ok(tooltip.includes("22,399.15"));
    assert.ok(tooltip.includes("−250.85 pts"));
    assert.ok(!tooltip.includes("999999"));
  }
});

test("intraday missing prices stay missing and time labels sit below both panels", () => {
  const option = intradayOption({ times: ["09:15", "09:30", "09:45"], maxPain: [null, 22500, 22500], spot: [22600, null, 22550] });
  assert.equal(option.series[2].data[0].value, null);
  assert.equal(option.series[2].data[1].value, null);
  assert.equal(option.series[2].data[2].value, 50);
  assert.equal(option.xAxis[0].axisLabel.show, false);
  assert.equal(option.xAxis[1].axisLabel.show, true);
  assert.equal(option.xAxis[1].axisLine.onZero, false);
  const tooltip = option.tooltip.formatter([{ dataIndex: 0, axisValue: "09:15" }]);
  assert.ok(tooltip.includes("22,600.00"));
  assert.ok(tooltip.includes("—"));
});

test("history preserves price precision, sorts newest first and explains close distances", () => {
  const React = require("react");
  const { renderToStaticMarkup } = require("react-dom/server");
  const historySource = fs.readFileSync(path.join(__dirname, "../components/MaxPainHistory.tsx"), "utf8");
  const historyCompiled = ts.transpileModule(historySource, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX },
  });
  const historyExports = {};
  new Function("exports", "require", historyCompiled.outputText)(historyExports, (name) =>
    name === "@/components/maxpainCharts" ? chartExports : require(name)
  );
  const older = { expiry: "2026-10-27", obs_date: "2026-10-22", obs_time: "10:15", kind: "session", spot: 22677.35, max_pain: 22800, expiry_close: 22687.65, error_pts: -112.35 };
  const latest = { ...older, obs_date: "2026-10-23", spot: 22491.70, max_pain: 22750, expiry_close: null, error_pts: null };
  const html = renderToStaticMarkup(React.createElement(historyExports.default, { points: [older, latest], loading: false, error: null }));
  assert.ok(html.indexOf("2026-10-23") < html.indexOf("2026-10-22"));
  assert.ok(html.includes("22,491.70"));
  assert.ok(html.includes("−258.30"));
  assert.ok(html.includes("−112.35"));
  assert.ok(html.includes("Close − MP (pts)"));
  assert.ok(html.includes("Time (IST)"));
  assert.equal((html.match(/>—<\/td>/g) ?? []).length, 2);
  assert.equal(older.obs_date, "2026-10-22");
});

test("history requests include the selected as-of date", async () => {
  const apiSource = fs.readFileSync(path.join(__dirname, "../lib/api.ts"), "utf8");
  const apiCompiled = ts.transpileModule(apiSource, { compilerOptions: { module: ts.ModuleKind.CommonJS } });
  const apiExports = {};
  let requested;
  new Function("exports", "require", "fetch", apiCompiled.outputText)(apiExports, require, async (url) => {
    requested = url;
    return { ok: true, json: async () => ({ count: 0, points: [] }) };
  });
  await apiExports.api.maxPainHistory({ expiry: "2026-10-27", as_of: "2026-10-22", history_days: 10 });
  const query = new URL(requested, "http://localhost").searchParams;
  assert.equal(query.get("as_of"), "2026-10-22");
  assert.equal(query.get("expiry"), "2026-10-27");
});

test("missing previous OI stays missing in change charts and tooltips", () => {
  const params = { strikes: [22500, 22600], callOi: [100, 50], putOi: [200, 70],
    callPrev: [null, 40], putPrev: [null, 60], maxPain: null, spot: null };
  const option = chartExports.oiChartOption({ ...params, mode: "change" });
  assert.deepEqual(option.series[0].data, [[22500, null], [22600, 10]]);
  assert.deepEqual(option.series[1].data, [[22500, null], [22600, -10]]);
  const tooltip = option.tooltip.formatter([{ dataIndex: 0 }]);
  assert.ok(!tooltip.includes("Δ Call"));
  assert.ok(!tooltip.includes("Δ Put"));
});

test("OI percent change is unavailable when the previous OI is zero", () => {
  const option = chartExports.oiChartOption({ strikes: [22500], callOi: [100], putOi: [200],
    callPrev: [0], putPrev: [0], mode: "pct", maxPain: null, spot: null });
  assert.deepEqual(option.series[0].data, [[22500, null]]);
  assert.deepEqual(option.series[1].data, [[22500, null]]);
});

test("OI uses numeric prices and retains exact off-strike markers when call bars are hidden", () => {
  const option = chartExports.oiChartOption({ strikes: [680, 690, 720], callOi: [650, 1300, 1950],
    putOi: [1300, 1950, 650], mode: "total", maxPain: 720, spot: 692.8 });
  assert.equal(option.xAxis.type, "value");
  assert.deepEqual(option.series[0].data, [[680, 650], [690, 1300], [720, 1950]]);
  const chart = echarts.init(null, null, { renderer: "svg", ssr: true, width: 900, height: 360 });
  try {
    chart.setOption(option);
    assert.ok(chart.renderToSVGString().includes("Spot 692.80"));
    chart.dispatchAction({ type: "legendUnSelect", name: "Call OI" });
    const svg = chart.renderToSVGString();
    assert.ok(svg.includes("Spot 692.80"));
    assert.ok(svg.includes("Max Pain 720"));
  } finally { chart.dispose(); }
});

test("OI change axes retain signs and percent tooltips show the actual change", () => {
  const option = chartExports.oiChartOption({ strikes: [700], callOi: [50], putOi: [120],
    callPrev: [100], putPrev: [100], mode: "pct", maxPain: null, spot: null });
  assert.equal(option.yAxis.axisLabel.formatter(-50), "−50%");
  assert.equal(option.yAxis.axisLabel.formatter(20), "+20%");
  const tooltip = option.tooltip.formatter([{ dataIndex: 0 }]);
  assert.ok(tooltip.includes("−50.00%"));
  assert.ok(tooltip.includes("+20.00%"));
});

test("historical premium coverage labels carried prices with their actual dates and age", () => {
  const React = require("react");
  const { renderToStaticMarkup } = require("react-dom/server");
  const source = fs.readFileSync(path.join(__dirname, "../components/HistoricalPremiumCoverage.tsx"), "utf8");
  const compiled = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX },
  });
  const exports = {};
  new Function("exports", "require", compiled.outputText)(exports, require);
  const prices = { date: "2026-10-23", required: 48, available: 48, exact: 46, carried_forward: 2,
    carried: [{ strike: 620, side: "CE", close: 99.05, price_date: "2026-10-14", age_days: 9 },
              { strike: 630, side: "CE", close: 67.05, price_date: "2026-10-22", age_days: 1 }] };
  const html = renderToStaticMarkup(React.createElement(exports.default, { prices }));
  for (const value of ["48/48 premiums available", "46 session closes", "2 carried forward", "620 CE",
                       "₹99.05", "2026-10-14", "9 days", "630 CE", "₹67.05", "2026-10-22", "1 day"])
    assert.ok(html.includes(value), `Missing premium provenance: ${value}`);
  assert.equal(renderToStaticMarkup(React.createElement(exports.default, { prices: null })), "");
  assert.equal(renderToStaticMarkup(React.createElement(exports.default, { prices: { ...prices, carried_forward: 0 } })), "");
});
