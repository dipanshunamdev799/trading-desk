const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");
const compiled = ts.transpileModule(fs.readFileSync(path.join(__dirname, "../lib/creditSpreads.ts"), "utf8"), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
});
const helpers = {};
new Function("exports", compiled.outputText)(helpers);

test("bear call payoff caps gross loss at width less credit and deducts fees once", () => {
  const curve = helpers.payoff("BEAR_CALL", 25400, 25600, 30, 65, 100);
  assert.equal(curve[0][1], 1850);
  assert.equal(curve.at(-1)[1], -11150);
  assert.equal(Math.max(...curve.map(p => p[1])), 1850);
  assert.equal(Math.min(...curve.map(p => p[1])), -11150);
});
test("bull put payoff reverses direction and uses the protective lower strike", () => {
  const curve = helpers.payoff("BULL_PUT", 24600, 24400, 30, 65, 100);
  assert.equal(curve[0][1], -11150);
  assert.equal(curve.at(-1)[1], 1850);
});
test("missing marks stay unknown while a true zero is displayed", () => {
  assert.equal(helpers.money(null), "—");
  assert.equal(helpers.points(null), "—");
  assert.equal(helpers.money(0), "₹0.00");
  assert.equal(helpers.points(0), "0.00");
  assert.equal(helpers.money(1000000), "₹10,00,000.00");
});
test("market timestamps are displayed in IST including date rollover", () => {
  assert.match(helpers.ist("2026-10-28T23:00:00Z"), /29 Oct.*04:30:00 IST/);
});
