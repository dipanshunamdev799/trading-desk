const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

function compiled(file) {
  return ts.transpileModule(fs.readFileSync(path.join(__dirname, file), "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
  }).outputText;
}
function feed() {
  const sockets = [], timers = new Map(); let timer = 0;
  class Socket {
    static OPEN = 1;
    constructor(url) { this.url = url; this.readyState = 0; this.sent = []; this.closed = false; sockets.push(this); }
    send(value) { this.sent.push(JSON.parse(value)); }
    close() { this.closed = true; this.readyState = 3; this.onclose?.(); }
    open() { this.readyState = 1; this.onopen(); }
  }
  const exports = {};
  new Function("exports", "require", "window", "WebSocket", "setTimeout", "clearTimeout", "setInterval", "clearInterval", compiled("../lib/liveMarket.ts"))(
    exports, require, { location: { href: "http://localhost:3000/maxpain" } }, Socket,
    (fn, ms) => { timers.set(++timer, { fn, ms }); return timer; }, id => timers.delete(id),
    (fn, ms) => { timers.set(++timer, { fn, ms }); return timer; }, id => timers.delete(id));
  return { ...exports, sockets, timers };
}
const update = { type: "market_update", revision: 1, instrument_keys: ["NSE_INDEX|Nifty 50"], quotes: {}, status: { connected: true, fresh: true, mode: "websocket", last_frame_at: new Date().toISOString() } };

test("dashboard listeners share one socket and subscribe to a deduplicated instrument set", () => {
  const f = feed(), events = [];
  const a = f.subscribeLiveMarket(["NSE_INDEX|Nifty 50"], e => events.push(e));
  const b = f.subscribeLiveMarket(["NSE_INDEX|Nifty 50", "NSE_EQ|HDFC"], () => {});
  assert.equal(f.sockets.length, 1);
  const ws = f.sockets[0]; ws.open();
  assert.deepEqual(ws.sent.at(-1).instrument_keys, ["NSE_INDEX|Nifty 50", "NSE_EQ|HDFC"]);
  ws.onmessage({ data: JSON.stringify(update) });
  assert.equal(events.at(-1).status.fresh, true);
  b(); assert.equal(ws.closed, false);
  assert.deepEqual(ws.sent.at(-1).instrument_keys, ["NSE_INDEX|Nifty 50"]);
  a(); assert.equal(ws.closed, true); assert.equal(f.timers.size, 0);
});

test("a dropped browser connection immediately clears live status and reconnects with its subscriptions", () => {
  const f = feed(), events = [];
  const cleanup = f.subscribeLiveMarket(["NSE_INDEX|Nifty 50"], e => events.push(e));
  const ws = f.sockets[0]; ws.open(); ws.onmessage({ data: JSON.stringify(update) }); ws.close();
  assert.equal(events.at(-1).status.connected, false);
  assert.equal(events.at(-1).status.fresh, false);
  assert.deepEqual(events.at(-1).quotes, {});
  const retry = [...f.timers.values()].find(entry => entry.ms === 1000); retry.fn();
  assert.equal(f.sockets.length, 2); f.sockets[1].open();
  assert.deepEqual(f.sockets[1].sent.at(-1).instrument_keys, ["NSE_INDEX|Nifty 50"]);
  cleanup();
});

const candleExports = {};
new Function("exports", compiled("../lib/liveCandles.ts"))(candleExports);
const merge = candleExports.mergeLiveCandles;
const now = Date.now(), iso = new Date(now).toISOString();
const day = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
const historical = { ts: new Date(now-86400000).toISOString(), open: 1, high: 3, low: 1, close: 2 };
const bar = { interval: "I1", ts: now-1000, open: 2, high: 4, low: 2, close: 3, vol: "12" };

test("exact live provider bars update current charts while historical ranges stay unchanged", () => {
  const quote = { timestamp: iso, last_price: 3, _live_candles: [bar] };
  assert.equal(merge([historical], quote, "1minute").length, 2);
  assert.equal(merge([historical], quote, "1minute").at(-1).volume, 12);
  assert.deepEqual(merge([historical], quote, "1minute", undefined, "2000-01-01"), [historical]);
  assert.deepEqual(merge([historical], quote, "5minute"), [historical]);
  assert.deepEqual(merge([historical], { ...quote, _live_candles: [{ ...bar, ts: now+60000 }] }, "1minute"), [historical]);
});

test("daily REST and feed timestamps map to one session bar", () => {
  const retained = { ...historical, ts: day+"T00:00:00+05:30" };
  const result = merge([retained], { _live_candles: [{ ...bar, interval: "1d" }] }, "1day");
  assert.equal(result.length, 1); assert.equal(result[0].close, 3);
});
