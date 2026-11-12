const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");
const compiled = ts.transpileModule(fs.readFileSync(path.join(__dirname, "../lib/strategyEvaluation.ts"), "utf8"), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
});
const helpers = {};
new Function("exports", "require", compiled.outputText)(helpers, name => name === "@/lib/api" ? { API_BASE: "/api" } : require(name));
const reading = { id: "max_pain", label: "Max Pain", group: "positioning", available: true, value: 24317.75, signal: -.8, reliability: 0 };

test("a measured options descriptor does not become a scoring input from availability or mapped-source metadata", () => {
  assert.equal(helpers.inputScoringStatus(reading), "descriptor");
  assert.equal(helpers.inputScoringLabel({ ...reading, scored: true }), "Measured descriptor");
  assert.equal(helpers.inputScoringStatus({ ...reading, scoring_status: "weighted" }), "descriptor");
});

test("explicit contextual and descriptor classifications remain unscored even with a populated signal", () => {
  assert.equal(helpers.inputScoringStatus({ ...reading, reliability: .9, scoring_status: "context" }), "context");
  assert.equal(helpers.inputScoringStatus({ ...reading, reliability: .9, scoring_status: "descriptor" }), "descriptor");
  assert.equal(helpers.inputScoringStatus({ ...reading, signal: null, scored: false }), "context");
});

test("stale or unavailable readings never display as scored, and a valid neutral signal can be scored", () => {
  assert.equal(helpers.inputScoringLabel({ ...reading, available: false, scoring_status: "weighted", reliability: .9 }), "Unavailable");
  assert.equal(helpers.inputScoringStatus({ ...reading, signal: 0, reliability: .9 }), "weighted");
  assert.equal(helpers.inputScoringStatus({ ...reading, signal: Number.NaN, reliability: .9 }), "context");
});

test("raw values retain decimals and contract text, while large collections have a concise audit preview", () => {
  assert.ok(helpers.auditValue(reading.value).includes("24,317.75"));
  assert.equal(helpers.auditValue("NSE_FO|12345"), "NSE_FO|12345");
  assert.equal(helpers.auditValue([{ strike: 24000 }, { strike: 24100 }]), "2 observations");
  assert.equal(helpers.auditValue(null), "Not supplied");
});
