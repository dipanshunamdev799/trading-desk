const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');
const echarts = require('echarts');
function load(file, dependencies={}) {
  const code = ts.transpileModule(fs.readFileSync(path.join(__dirname, file), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const exports = {};
  new Function('exports', 'require', code)(exports, name => dependencies[name] || require(name));
  return exports;
}
const { ivChartOption, ivTimeline, ivFormat } = load('../components/ivCharts.ts');
const DAY = '2026-10-28';
const point = (time, values={}) => ({ date: DAY, time, observed_at: `${DAY}T${time}:10+05:30`, iv: 20, call_iv: 19, put_iv: 21,
  strike: 22600, spot: 22602.5, expected_move: 530, lower: 22072.5, upper: 23132.5, days_to_expiry: 6,
  source: 'REST capture', iv_rank: 50, iv_percentile: 60, history_sessions: 10, ...values });

test('all four metrics use their own units, align real IST minutes, and never bridge missing captures', () => {
  const option = ivChartOption(DAY, [point('09:15'), point('09:17', { iv: 22, iv_rank: null, expected_move: null })]);
  assert.equal(option.grid.length, 3);
  assert.deepEqual(option.series.map(s => [s.name, s.yAxisIndex]), [['ATM IV', 0], ['IV Rank (sample)', 1], ['IV Percentile (sample)', 1], ['Expected move ±pts', 2]]);
  assert.deepEqual(option.series[0].data.map(row => row[1]), [20, null, 22]);
  assert.equal(option.series[0].data[0][0], Date.parse(`${DAY}T03:45:00Z`));
  assert.deepEqual(option.series[3].data.map(row => row[1]), [530, null, null]);
  assert.ok(option.series.every(s => s.connectNulls === false));
  assert.equal(option.yAxis[1].max, 100);
});

test('tooltip preserves genuine zero expiry move, missing rank and actual capture source', () => {
  const option = ivChartOption(DAY, [point('15:30', { expected_move: 0, iv_rank: null, iv_percentile: null, history_sessions: 0 })]);
  const tip = option.tooltip.formatter([{ dataIndex: 0 }]);
  assert.match(tip, /IV Rank \(sample\): —/);
  assert.match(tip, /Expected move: ±0.00 pts/);
  assert.match(tip, /Prior saved sessions: 0\/252/);
  assert.match(tip, /capture 15:30:10 IST/);
  assert.equal(ivFormat(null), '—');
  assert.equal(ivFormat(0), '0.00');
});

test('wrong dates are ignored and duplicate minute uses its latest original acquisition', () => {
  const rows = ivTimeline(DAY, [point('09:15'), point('09:15', { observed_at: `${DAY}T09:15:40+05:30`, iv: 25 }), point('09:16', { date: '2026-10-27' })]);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].point.iv, 25);
});

test('ECharts renders all four series and communicates missing history', () => {
  const chart = echarts.init(null, null, { renderer:'svg', ssr:true, width:1200, height:480 });
  try {
    chart.setOption(ivChartOption(DAY, [point('09:15'), point('09:16')]));
    let svg = chart.renderToSVGString();
    for (const color of ['#E5C07B', '#C5A1ED', '#61AFEF', '#2DD4A8']) assert.ok(svg.includes(color));
    chart.setOption(ivChartOption(DAY, [point('09:15', { iv_rank:null, iv_percentile:null, history_sessions:0 })]), true);
    svg = chart.renderToSVGString();
    assert.match(svg, /Rank \/ percentile need at least 2 prior saved sessions/);
  } finally { chart.dispose(); }
});

test('requests pass exact date, underlying and expiry without browser caching', async () => {
  const { api } = load('../lib/api.ts');
  const old = global.fetch;
  let request;
  global.fetch = async (...args) => { request = args; return { ok:true, json:async () => ({points:[]}) }; };
  try {
    await api.ivHistory({expiry:'2026-11-03',as_of:DAY,instrument_key:'NSE_INDEX|Nifty 50'});
    const url = new URL(request[0], 'http://localhost:3000');
    assert.equal(url.pathname, '/api/options/iv/history');
    assert.equal(url.searchParams.get('as_of'), DAY);
    assert.equal(url.searchParams.get('expiry'), '2026-11-03');
    assert.equal(url.searchParams.get('instrument_key'), 'NSE_INDEX|Nifty 50');
    assert.equal(request[1].cache, 'no-store');
  } finally { global.fetch = old; }
});
