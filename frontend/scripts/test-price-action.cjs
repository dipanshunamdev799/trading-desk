const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');
const source = ts.transpileModule(fs.readFileSync(path.join(__dirname, '../lib/priceAction.ts'), 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
}).outputText;
const lib = {};
new Function('exports', 'require', source)(lib, require);
const study = { events: [{ concept: 11, group: 'setups' }, { concept: 44, group: 'advanced' }, { concept: 25, group: 'candles' }], lines: [{ concept: 7, group: 'levels' }], zones: [{ concept: 44, group: 'advanced' }] };

test('core preset, group toggles, clean chart and individual concepts select only their own annotations', () => {
  const core = lib.selectStudy(study, ['setups', 'advanced', 'levels', 'candles'], 'core', null);
  assert.deepEqual(core.events.map(e => e.concept), [11]);
  assert.deepEqual(core.lines.map(e => e.concept), [7]);
  assert.deepEqual(core.zones, []);
  assert.equal(lib.selectStudy(study, [], 'none', null).events.length, 0);
  const gap = lib.selectStudy(study, [], 'core', 44);
  assert.deepEqual(gap.events.map(e => e.concept), [44]);
  assert.equal(gap.zones.length, 1);
  assert.equal(gap.lines.length, 0);
  assert.deepEqual(lib.selectStudy(study, ['candles'], 'custom', null).events.map(e => e.concept), [25]);
});

test('session and confirmation clocks use IST even for UTC timestamps', () => {
  assert.equal(lib.istDay('2026-10-22T23:30:00Z'), '2026-10-23');
  assert.equal(lib.studyTime('2026-10-23T04:00:00Z'), '09:30');
});

test('personal shortcuts rank only used concepts, with stable ties and a six-concept limit', () => {
  const catalog = Array.from({ length: 9 }, (_, i) => ({ id: i + 1, label: `Concept ${i + 1}` }));
  assert.deepEqual(lib.frequentConcepts(catalog, {}), []);
  assert.deepEqual(lib.frequentConcepts(catalog, { 1: 1, 2: 4, 3: 4, 4: 2, 5: 3, 6: 1, 7: 9, 8: 5 }).map(r => r.id), [7, 8, 2, 3, 5, 4]);
  assert.deepEqual(lib.parseConceptUsage('{"1":5,"2":-1,"3":"4","48":10,"4":1.5,"5":2}'), { 1: 5, 5: 2 });
  for (const raw of ['broken', 'null', '[]', '"hello"']) assert.deepEqual(lib.parseConceptUsage(raw), {});
});

test('clean chart suppresses selected annotations; custom concepts combine across groups', () => {
  assert.deepEqual(lib.selectStudy(study, [], 'none', null, [11, 44]), { events: [], lines: [], zones: [] });
  const selected = lib.selectStudy(study, [], 'custom', null, [11, 44]);
  assert.deepEqual(selected.events.map(r => r.concept), [11, 44]);
  assert.equal(selected.zones.length, 1);
  assert.equal(selected.lines.length, 0);
  assert.deepEqual(lib.selectStudy(study, [], 'all', null, []).lines.map(r => r.concept), [7]);
});

test('chart starts clean, remembers concept usage, and restores shortcuts without restoring overlays', () => {
  const code = ts.transpileModule(fs.readFileSync(path.join(__dirname, '../components/PriceActionChart.tsx'), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX },
  }).outputText;
  const retainedStorage = global.localStorage;
  const storage = new Map();
  global.localStorage = { getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value) };
  const response = { instrument_key: 'NSE_INDEX|Nifty 50', interval: '5minute', candles: [], study: {
    ...study, catalog: [{ id: 11, label: 'Liquidity sweep' }, { id: 44, label: 'Fair value gap' }], sessions: [], groups: [], notes: [] } };
  function mount() {
    const hooks = []; let index = 0; let pending = [];
    const module = {};
    new Function('exports', 'require', code)(module, name => {
      if (name === 'react') return {
        useState(initial) { const slot = index++; if (!(slot in hooks)) hooks[slot] = typeof initial === 'function' ? initial() : initial; return [hooks[slot], value => { hooks[slot] = typeof value === 'function' ? value(hooks[slot]) : value; }]; },
        useMemo(fn) { return fn(); },
        useEffect(fn, deps) { const slot = index++; if (!hooks[slot] || deps.some((d, i) => d !== hooks[slot][i])) { hooks[slot] = deps; pending.push(fn); } },
      };
      if (name === '@/lib/priceAction') return lib;
      if (name === '@/lib/minutePolling') return { startMinutePolling: options => { options.onData(response); return () => {}; } };
      if (name === '@/lib/liveMarket') return { useLiveMarket() {} };
      if (name.startsWith('@/components/')) return { __esModule: true, default: () => null, SourceBadge: () => null };
      if (name.startsWith('@/')) return {};
      return require(name);
    });
    return () => { index = 0; const tree = module.default({ initialCandles: [] }); const effects = pending; pending = []; effects.forEach(fn => fn()); return tree; };
  }
  function find(tree, label) {
    if (!tree || typeof tree !== 'object') return null;
    if (tree.props?.['aria-label'] === label) return tree;
    for (const child of [tree.props?.children].flat(Infinity)) { const found = find(child, label); if (found) return found; }
    return null;
  }
  try {
    const render = mount(); render(); let tree = render();
    assert.equal(find(tree, 'Price action layers').props.value, 'none');
    find(tree, 'Add a price action concept').props.onChange({ target: { value: '11' } });
    tree = render();
    assert.equal(find(tree, 'Price action layers').props.value, 'custom');
    assert.equal(JSON.parse(storage.get(lib.CONCEPT_USAGE_KEY))['11'], 1);
    find(tree, 'Add a price action concept').props.onChange({ target: { value: '44' } });
    tree = render();
    assert.equal(find(tree, 'Selected concepts').props.children[1].length, 2);
    find(tree, 'Price action layers').props.onChange({ target: { value: 'none' } });
    tree = render();
    assert.equal(find(tree, 'Selected concepts'), null);
    const reload = mount(); reload(); tree = reload();
    assert.equal(find(tree, 'Price action layers').props.value, 'none');
    const shortcuts = find(tree, 'Frequently used concepts').props.children[1];
    assert.equal(shortcuts.length, 2);
    assert.ok(shortcuts.every(button => button.props['aria-pressed'] === false));
    shortcuts[0].props.onClick();
    assert.equal(JSON.parse(storage.get(lib.CONCEPT_USAGE_KEY))['11'], 2);
  } finally { global.localStorage = retainedStorage; }
});

test('zone primitive projects the observed bounds and begins at confirmation, then follows updated scales', () => {
  const code = ts.transpileModule(fs.readFileSync(path.join(__dirname, '../components/priceActionOverlay.ts'), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
  }).outputText;
  const module = {};
  new Function('exports', 'require', code)(module, name => name === '@/lib/priceAction' ? lib : require(name));
  const primitive = new module.PriceActionOverlay({ events: [], lines: [], zones: [{ start: '2026-10-23T09:30:00+05:30', end: '2026-10-23T09:40:00+05:30', high: 110, low: 100, side: 1, tested: false, active: true }] });
  let scale = 1, update = false;
  primitive.attached({ requestUpdate() { update = true; }, chart: { timeScale: () => ({ timeToCoordinate: stamp => (stamp-Date.parse('2026-10-23T09:15:00+05:30')/1000)/60*scale }) }, series: { priceToCoordinate: v => 200-v } });
  const rectangles = [];
  const context = { save() {}, restore() {}, beginPath() {}, rect() {}, clip() {}, setLineDash() {}, strokeRect() {}, fillRect(...r) { rectangles.push(r); } };
  const target = { useMediaCoordinateSpace: callback => callback({ context, mediaSize: { width: 700, height: 400 } }) };
  primitive.paneViews()[0].renderer().draw(target);
  assert.equal(update, true);
  assert.deepEqual(rectangles[0], [15, 90, 10, 10]);
  scale = 2;
  primitive.paneViews()[0].renderer().draw(target);
  assert.deepEqual(rectangles[1], [30, 90, 20, 10]);
  primitive.detached();
});
