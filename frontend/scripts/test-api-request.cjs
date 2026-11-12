const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");

function harness(fetch) {
  const timers = new Map();
  let id = 0;
  const exports = {};
  const source = fs.readFileSync(path.join(__dirname, "../lib/api.ts"), "utf8");
  const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS } });
  new Function("exports", "fetch", "setTimeout", "clearTimeout", compiled.outputText)(
    exports, fetch,
    (callback, delay) => { timers.set(++id, { callback, delay }); return id; },
    id => timers.delete(id)
  );
  return { api: exports.api, timers };
}

test("a stalled IPO request aborts and exits loading with a useful error", async () => {
  let signal;
  const h = harness((_, init) => new Promise((resolve, reject) => {
    signal = init.signal;
    signal.addEventListener("abort", () => reject(new Error("aborted")), { once: true });
  }));
  const pending = assert.rejects(h.api.ipos(), /timed out after 20s.*retry/);
  const timer = [...h.timers.values()][0];
  assert.equal(timer.delay, 20_000);
  timer.callback();
  await pending;
  assert.equal(signal.aborted, true);
  assert.equal(h.timers.size, 0);
});

test("successful health checks clear their timeout and use the same-origin proxy", async () => {
  let url, options;
  const h = harness(async (target, init) => {
    url = target; options = init;
    return { ok: true, json: async () => ({ ok: true, database: "ok", upstox_token: true }) };
  });
  assert.equal((await h.api.health()).upstox_token, true);
  assert.equal(url, "/api/health");
  assert.equal(options.cache, "no-store");
  assert.equal(h.timers.size, 0);
});

test("failed API responses retain the server's useful diagnostic", async () => {
  const h = harness(async () => ({ ok: false, statusText: "Service Unavailable", json: async () => ({ detail: "Database unavailable" }) }));
  await assert.rejects(h.api.ipos(), /Database unavailable/);
  assert.equal(h.timers.size, 0);
});
