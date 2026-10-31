const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");

const source = ts.transpileModule(fs.readFileSync(path.join(__dirname, "../components/ChartPanel.tsx"), "utf8"), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX },
}).outputText;
const bars = [
  { ts: "2026-10-22T09:15:00+05:30", open: 100, high: 110, low: 90, close: 105, volume: 20 },
  { ts: "2026-10-23T09:15:00+05:30", open: 105, high: 115, low: 100, close: 112, volume: 25 },
];

function mount({ expanded = false, chartType = "candlestick", timeZone, study, showVolume, candles = bars, emaOverlays, indicatorCandles } = {}) {
  const frame = { clientWidth: expanded ? 1240 : 700, clientHeight: expanded ? 590 : 360 };
  const effects = []; const resizes = []; const series = [];
  let refIndex = 0, observer, options, removed = false, disconnected = false;
  let visibleRange, crosshair;
  const chart = {
    priceScale: () => ({ applyOptions() {} }), timeScale: () => ({ fitContent() {}, setVisibleLogicalRange(value) { visibleRange = value; } }),
    subscribeCrosshairMove(callback) { crosshair = callback; },
    resize: (...size) => resizes.push(size), remove: () => { removed = true; },
  };
  for (const kind of ["Candlestick", "Line", "Area", "Histogram"]) {
    chart[`add${kind}Series`] = options => { const entry = { kind, options, data: null, setData(data) { this.data = data; }, setMarkers(rows) { this.markers = rows; }, attachPrimitive(value) { this.primitive = value; } }; series.push(entry); return entry; };
  }
  const previousWindow = global.window; const previousObserver = global.ResizeObserver;
  const previousDocument = global.document;
  const tip = { style: {}, offsetHeight: 40, remove() {} };
  frame.appendChild = () => {};
  global.document = { createElement: () => tip };
  global.window = { addEventListener() {}, removeEventListener() {} };
  global.ResizeObserver = class {
    constructor(callback) { observer = callback; }
    observe() {} disconnect() { disconnected = true; }
  };
  const exports = {};
  new Function("exports", "require", source)(exports, name => {
    if (name === "react") return { useRef: () => ({ current: refIndex++ === 0 ? frame : null }), useEffect: effect => effects.push(effect) };
    if (name === "@/components/ExpandableChartPanel") return { useExpandedChart: () => expanded };
    if (name === "@/components/priceActionOverlay") return { PriceActionOverlay: class {} };
    if (name === "@/lib/priceAction") return { compactStudyLabel: () => "SWP", studyColor: side => side > 0 ? "green" : "red", studyTime: () => "09:20" };
    if (name === "lightweight-charts") return { createChart: (_frame, config) => { options = config; return chart; }, ColorType: { Solid: "solid" }, CrosshairMode: { Normal: 0 }, TickMarkType: { Year: 0, Month: 1, DayOfMonth: 2, Time: 3, TimeWithSeconds: 4 } };
    return require(name);
  });
  const tree = exports.default({ candles, height: 360, chartType, timeZone, study, showVolume, emaOverlays, indicatorCandles });
  const cleanup = effects.map(effect => effect());
  return { tree, frame, options, resizes, series, tip, crosshair: (...args) => crosshair(...args), get visibleRange() { return visibleRange; }, resize: () => observer(), cleanup() {
    cleanup.forEach(stop => stop?.()); global.window = previousWindow; global.ResizeObserver = previousObserver;
    global.document = previousDocument;
    assert.ok(removed && disconnected, "Chart and observer must be released");
  } };
}

const emaOverlays = [{ period: 9, color: "#FBBF24" }, { period: 21, color: "#A78BFA" }];
const emaHistory = Array.from({ length: 25 }, (_, index) => ({
  ts: new Date(Date.UTC(2026, 9, 23, 4, index)).toISOString(),
  open: index + 1, high: index + 1, low: index + 1, close: index + 1, volume: 0,
}));

for (const chartType of ["candlestick", "line", "area"]) {
  test(`${chartType} view overlays EMA 9 and 21 with prior-history warmup`, () => {
    const view = mount({ chartType, candles: emaHistory.slice(-3), indicatorCandles: emaHistory, emaOverlays });
    try {
      for (const [period, expected] of [[9, [19, 20, 21]], [21, [13, 14, 15]]]) {
        const ema = view.series.find(row => row.options?.title === `EMA ${period}`);
        assert.ok(ema, `EMA ${period} must be present`);
        assert.deepEqual(ema.data.map(row => row.value), expected);
        assert.deepEqual(ema.data.map(row => row.time), emaHistory.slice(-3).map(row => Date.parse(row.ts) / 1000));
        assert.equal(ema.options.color, emaOverlays.find(row => row.period === period).color);
        assert.equal(ema.options.priceScaleId, "right");
      }
    } finally { view.cleanup(); }
  });
}

test("EMA waits for enough bars and incorporates the latest candle close", () => {
  const short = mount({ candles: emaHistory.slice(0, 8), emaOverlays });
  try { assert.ok(short.series.every(row => !row.options?.title?.startsWith("EMA"))); }
  finally { short.cleanup(); }
  const revised = emaHistory.map((row, i) => i === 24 ? { ...row, high: 35, close: 35 } : row);
  const view = mount({ candles: revised, emaOverlays });
  try {
    const fast = view.series.find(row => row.options?.title === "EMA 9");
    const slow = view.series.find(row => row.options?.title === "EMA 21");
    assert.equal(fast.data[0].value, 5);
    assert.equal(slow.data[0].value, 11);
    assert.equal(fast.data.at(-1).value, 23);
    assert.ok(Math.abs(slow.data.at(-1).value - (15 + 10 / 11)) < 1e-10);
  } finally { view.cleanup(); }
});

test("maximized chart uses available container height and resizes back on restore", () => {
  const view = mount({ expanded: true });
  try {
    assert.equal(view.tree.props.style.height, "100%");
    assert.equal(view.options.height, 590);
    assert.deepEqual(view.resizes.at(-1), [1240, 590]);
    view.frame.clientWidth = 700; view.frame.clientHeight = 360; view.resize();
    assert.deepEqual(view.resizes.at(-1), [700, 360]);
  } finally { view.cleanup(); }
});

test("NIFTY spot can hide untraded volume without affecting candles", () => {
  const view = mount({ showVolume: false });
  try { assert.deepEqual(view.series.map(row => row.kind), ["Candlestick"]); }
  finally { view.cleanup(); }
});

test("study combines same-candle matches and exposes their actual confirmation in the tooltip", () => {
  const study = { events: [
    { ts: bars[0].ts, known_at: "2026-10-22T09:20:00+05:30", concept: 11, side: -1, label: "Liquidity sweep", level: 107 },
    { ts: bars[0].ts, known_at: "2026-10-22T09:20:00+05:30", concept: 25, side: 0, label: "Doji" },
  ], lines: [], zones: [], focus: bars[0].ts };
  const view = mount({ study });
  try {
    assert.equal(view.series[0].markers.length, 1);
    assert.equal(view.series[0].markers[0].text, "SWP +1");
    assert.equal(view.series[0].markers[0].time, Date.parse(bars[0].ts)/1000);
    assert.ok(view.series[0].primitive);
    view.crosshair({ point: { x: 30, y: 60 }, time: Date.parse(bars[0].ts)/1000 });
    assert.match(view.tip.textContent, /Confirmed 09:20 IST.*\nLiquidity sweep · 107.00\nDoji/);
    assert.deepEqual(view.visibleRange, { from: -1, to: 4 });
  } finally { view.cleanup(); }
});

test("Indian price-action labels use IST while retaining actual UTC candle timestamps", () => {
  const view = mount({ timeZone: "Asia/Kolkata" });
  try {
    const stamp = Date.parse("2026-10-23T09:58:00Z") / 1000;
    assert.equal(view.options.timeScale.tickMarkFormatter(stamp, 3), "15:28");
    assert.match(view.options.localization.timeFormatter(stamp), /23 Oct 2026.*15:28/);
    assert.equal(view.series[0].data[0].time, Date.parse(bars[0].ts) / 1000);
  } finally { view.cleanup(); }
});

for (const [chartType, kind] of [["candlestick", "Candlestick"], ["line", "Line"], ["area", "Area"]]) {
  test(`${chartType} view renders its corresponding price series with correct prices`, () => {
    const view = mount({ chartType });
    try {
      const price = view.series.find(series => series.kind === kind);
      assert.ok(price);
      assert.deepEqual(price.data.map(row => row.close ?? row.value), [105, 112]);
      assert.equal(view.tree.props.style.height, 360);
    } finally { view.cleanup(); }
  });
}
