const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");

const source = fs.readFileSync(path.join(__dirname, "../lib/minutePolling.ts"), "utf8");
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS } });
const flush = () => new Promise(setImmediate);

function harness(load, live = true) {
  let now = 10_000;
  let nextId = 0;
  const timers = new Map();
  const listeners = new Set();
  const visibility = {
    visibilityState: "visible",
    addEventListener: (_, listener) => listeners.add(listener),
    removeEventListener: (_, listener) => listeners.delete(listener),
  };
  const result = { calls: 0, data: [], errors: [], loading: [] };
  const exports = {};
  new Function("exports", "require", "Date", "setTimeout", "clearTimeout", "document", compiled.outputText)(
    exports, require, { now: () => now },
    (callback, delay) => { const id = ++nextId; timers.set(id, { at: now + delay, callback }); return id; },
    (id) => timers.delete(id), visibility
  );
  const stop = exports.startMinutePolling({
    load: () => { result.calls++; return load(result.calls); },
    onData: (data) => result.data.push(data),
    onError: (error) => result.errors.push(error),
    onLoading: (loading) => result.loading.push(loading), live,
  });
  return {
    result, stop, listeners,
    async advance(milliseconds) {
      const target = now + milliseconds;
      while (true) {
        const entry = [...timers.entries()].sort((a, b) => a[1].at - b[1].at)[0];
        if (!entry || entry[1].at > target) break;
        now = entry[1].at;
        timers.delete(entry[0]);
        entry[1].callback();
        await flush();
      }
      now = target;
      await flush();
    },
    async visible(state) {
      visibility.visibilityState = state;
      for (const listener of listeners) listener();
      await flush();
    },
  };
}

test("loads immediately, then refreshes at minute boundaries and stops on cleanup", async () => {
  const h = harness(async (call) => call);
  await flush();
  assert.equal(h.result.calls, 1);
  await h.advance(49_999);
  assert.equal(h.result.calls, 1);
  await h.advance(1);
  assert.equal(h.result.calls, 2);
  await h.advance(60_000);
  assert.equal(h.result.calls, 3);
  h.stop();
  await h.advance(120_000);
  assert.equal(h.result.calls, 3);
  assert.equal(h.listeners.size, 0);
});

test("historical selections load once without polling", async () => {
  const h = harness(async () => "history", false);
  await h.advance(300_000);
  assert.equal(h.result.calls, 1);
  assert.deepEqual(h.result.data, ["history"]);
  assert.equal(h.listeners.size, 0);
  h.stop();
});

test("hidden tabs pause and refresh immediately when visible again", async () => {
  const h = harness(async (call) => call);
  await flush();
  await h.visible("hidden");
  await h.advance(170_000);
  assert.equal(h.result.calls, 1);
  await h.visible("visible");
  assert.equal(h.result.calls, 2);
  h.stop();
});

test("slow requests never overlap and cancelled responses are ignored", async () => {
  let resolve;
  const h = harness(() => new Promise((done) => { resolve = done; }));
  await h.advance(170_000);
  assert.equal(h.result.calls, 1);
  h.stop();
  resolve("old selection");
  await flush();
  assert.deepEqual(h.result.data, []);
});

test("a failed refresh retains successful data and retries next minute", async () => {
  const h = harness(async (call) => { if (call === 2) throw new Error("temporary error"); return call; });
  await flush();
  await h.advance(50_000);
  assert.deepEqual(h.result.data, [1]);
  assert.equal(h.result.errors.length, 1);
  await h.advance(60_000);
  assert.deepEqual(h.result.data, [1, 3]);
  assert.equal(h.result.loading.at(-1), false);
  h.stop();
});
