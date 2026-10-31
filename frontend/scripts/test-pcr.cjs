const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");
const echarts = require("echarts");

function load(file, dependencies={}) {
  const compiled = ts.transpileModule(fs.readFileSync(path.join(__dirname, file), "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const exports = {};
  new Function("exports", "require", compiled)(exports, name => dependencies[name] || require(name));
  return exports;
}
const { pcrChartOption, pcrTimeline } = load("../components/pcrCharts.ts");
const DAY = "2026-10-23";
const points = [{ time: "09:15", pcr: .82, spot: 22719.9 }, { time: "09:17", pcr: .738, spot: 22600 }];

test("PCR segments render green rising, red falling and neutral flat without bridging missing minutes", () => {
  const option = pcrChartOption(DAY, [
    { time: "09:15", pcr: .8 }, { time: "09:16", pcr: .9 },
    { time: "09:17", pcr: .85 }, { time: "09:18", pcr: .85 },
    { time: "09:20", pcr: .95 },
  ]);
  assert.equal(option.series[1].data.length, 3);
  const chart = echarts.init(null, null, { renderer: "svg", ssr: true, width: 1000, height: 260 });
  try {
    chart.setOption(option);
    const svg = chart.renderToSVGString();
    for (const color of ["#20C997", "#EF6672", "#8B9AAB"]) assert.ok(svg.includes(`stroke="${color}"`));
  } finally { chart.dispose(); }
});

test("PCR time axis uses real IST minutes, preserves ratios and leaves missing minutes as gaps", () => {
  const option = pcrChartOption(DAY, points);
  assert.equal(option.xAxis.type, "time");
  assert.equal(option.series[0].connectNulls, false);
  assert.equal(option.series[0].smooth, false);
  assert.deepEqual(option.series[0].data, [
    [Date.parse(DAY+"T09:15:00+05:30"), .82], [Date.parse(DAY+"T09:16:00+05:30"), null],
    [Date.parse(DAY+"T09:17:00+05:30"), .738],
  ]);
  assert.equal(option.xAxis.axisLabel.formatter(option.series[0].data[0][0]), "09:15");
  const tooltip = option.tooltip.formatter([{ dataIndex: 2 }]);
  assert.ok(tooltip.includes("0.7380")); assert.ok(tooltip.includes("22,600.00"));
  assert.ok(tooltip.includes("2026-10-23 · 09:17 IST"));
});

test("the reference line at one stays visible without marking a bullish or bearish threshold", () => {
  const option = pcrChartOption(DAY, points);
  assert.equal(option.series[0].markLine.data[0].yAxis, 1);
  assert.ok(option.yAxis[0].min < .738); assert.ok(option.yAxis[0].max > 1);
  const chart = echarts.init(null, null, { renderer: "svg", ssr: true, width: 1000, height: 260 });
  try {
    chart.setOption(option);
    assert.ok(chart.renderToSVGString().includes("PCR 1.00 · equal put/call"));
  } finally { chart.dispose(); }
});

test("fresh streamed OI can update the current minute without rewriting earlier provider history", () => {
  const result = pcrTimeline(DAY, points, [{ time: "09:15", pcr: 9, spot: null },
    { time: "09:17", pcr: .75, spot: null, source: "websocket" }, { time: "09:18", pcr: .76, spot: null }]);
  assert.equal(result[0].pcr, .82); assert.equal(result[2].pcr, .75); assert.equal(result[3].pcr, .76);
});

test("spot uses its own price axis, aligned minutes and gaps without changing PCR values", () => {
  const option = pcrChartOption(DAY, points);
  const spot = option.series[2];
  assert.equal(spot.name, "Nifty 50 spot"); assert.equal(spot.yAxisIndex, 1);
  assert.equal(option.yAxis[1].scale, true); assert.equal(spot.connectNulls, false);
  assert.deepEqual(spot.data.map(row => row[1]), [22719.9, null, 22600]);
  assert.deepEqual(spot.data.map(row => row[0]), option.series[0].data.map(row => row[0]));
  assert.equal(pcrChartOption(DAY, points, [], "HDFC Bank").series[2].name, "HDFC Bank spot");
  const chart = echarts.init(null, null, { renderer: "svg", ssr: true, width: 1000, height: 300 });
  try {
    chart.setOption(option);
    const svg = chart.renderToSVGString();
    assert.ok(svg.includes('stroke="#61AFEF"')); assert.ok(svg.includes("Nifty 50 spot"));
    chart.dispatchAction({ type: "legendUnSelect", name: "PCR (OI)" });
    assert.ok(chart.getModel().isSeriesFiltered(chart.getModel().getSeriesByIndex(0)));
    assert.ok(chart.getModel().isSeriesFiltered(chart.getModel().getSeriesByIndex(1)));
    assert.equal(chart.getModel().isSeriesFiltered(chart.getModel().getSeriesByIndex(2)), false);
  } finally { chart.dispose(); }
});

test("live updates preserve same-minute provider spot and PCR independently without filling other minutes", () => {
  const oiOnly = pcrTimeline(DAY, points, [{ time: "09:17", pcr: .75, spot: null, source: "websocket" }]);
  assert.equal(oiOnly[2].spot, 22600);
  const spotOnly = pcrTimeline(DAY, points, [
    { time: "09:17", pcr: null, spot: 22601 }, { time: "09:18", pcr: null, spot: 22602 },
    { time: "09:20", pcr: null, spot: 22603 },
  ]);
  assert.equal(spotOnly[2].pcr, .738); assert.equal(spotOnly[2].spot, 22601);
  assert.equal(spotOnly[3].pcr, null); assert.equal(spotOnly[3].spot, 22602);
  assert.equal(spotOnly[4].spot, null); assert.equal(spotOnly[4].pcr, null);
});

test("a genuine zero remains visible while invalid values stay missing", () => {
  const option = pcrChartOption(DAY, [{ time: "09:15", pcr: 0 }, { time: "09:16", pcr: NaN }]);
  assert.equal(option.series[0].data[0][1], 0); assert.equal(option.series[0].data[1][1], null);
  assert.equal(option.series[0].showSymbol, true);
  assert.equal(option.tooltip.formatter([{ dataIndex: 1 }]).includes("PCR: —"), true);
});

test("volume PCR keeps independent values, dashed slope colors, gaps, tooltip totals and legend visibility", () => {
  const option = pcrChartOption(DAY, [
    { time: "09:15", pcr: .8, volume_pcr: .5, call_volume: 100, put_volume: 50 },
    { time: "09:16", pcr: .7, volume_pcr: .6 },
    { time: "09:17", pcr: .9, volume_pcr: .4 },
    { time: "09:19", pcr: .8, volume_pcr: 0 },
  ]);
  assert.deepEqual(option.series[3].data.map(row => row[1]), [.5, .6, .4, null, 0]);
  assert.equal(option.series[4].data.length, 2);
  assert.equal(option.series[3].connectNulls, false); assert.equal(option.series[3].symbol, "diamond");
  assert.ok(option.tooltip.formatter([{ dataIndex: 0 }]).includes("Volume PCR: 0.5000"));
  assert.ok(option.tooltip.formatter([{ dataIndex: 0 }]).includes("100 / 50"));
  const chart = echarts.init(null, null, {renderer:"svg",ssr:true,width:1000,height:300});
  try {
    chart.setOption(option);
    assert.ok(chart.renderToSVGString().includes('stroke-dasharray="5,4"'));
    chart.dispatchAction({type:"legendUnSelect",name:"PCR (volume)"});
    assert.ok(chart.getModel().isSeriesFiltered(chart.getModel().getSeriesByIndex(3)));
    assert.ok(chart.getModel().isSeriesFiltered(chart.getModel().getSeriesByIndex(4)));
    assert.equal(chart.getModel().isSeriesFiltered(chart.getModel().getSeriesByIndex(0)),false);
  } finally { chart.dispose(); }
});

test("PCR requests carry the exact selected date, expiry and underlying with browser caching disabled", async () => {
  const prior = global.fetch; let requested, options;
  global.fetch = async (url, opts) => { requested = url; options = opts; return { ok: true, json: async () => ({ points: [] }) }; };
  try {
    const { api } = load("../lib/api.ts");
    await api.pcrIntraday({ expiry: "2026-10-27", as_of: DAY, instrument_key: "NSE_INDEX|Nifty 50" });
    const query = new URL(requested, "http://localhost").searchParams;
    assert.equal(query.get("as_of"), DAY); assert.equal(query.get("expiry"), "2026-10-27");
    assert.equal(query.get("instrument_key"), "NSE_INDEX|Nifty 50"); assert.equal(options.cache, "no-store");
  } finally { global.fetch = prior; }
});
