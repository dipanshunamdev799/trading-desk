const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");

function load(file, dependencies = {}) {
  const compiled = ts.transpileModule(fs.readFileSync(path.join(__dirname, file), "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX },
  });
  const exports = {};
  new Function("exports", "require", compiled.outputText)(exports, name => dependencies[name] || require(name));
  return exports;
}
const helpers = load("../components/ipoResearch.ts");
const cards = load("../components/IpoFactorCard.tsx", { "@/components/ipoResearch": helpers });
const base = { id: "qib", number: 1, label: "QIB subscription", status: "available", unit: "x", source: "Public source", value: 0 };

test("a genuine zero QIB reading is distinct from pending or missing bids", () => {
  const zero = renderToStaticMarkup(React.createElement(cards.default, { factor: base }));
  assert.ok(zero.includes("0.00×"));
  assert.ok(zero.includes("Primary demand signal"));
  const pending = renderToStaticMarkup(React.createElement(cards.default, { factor: { ...base, value: null, status: "pending" } }));
  assert.ok(pending.includes("Bidding not started"));
  assert.ok(!pending.includes("0.00×"));
});

test("a missing GMP quote cannot become a zero percent premium", () => {
  const html = renderToStaticMarkup(React.createElement(cards.default, { factor: { ...base, id: "gmp", unit: "gmp", value: null, status: "unavailable" } }));
  assert.ok(html.includes("Not available from connected sources"));
  assert.ok(!html.includes("0.00%"));
});

test("sources and periods remain visible while unsafe links are rejected", () => {
  const html = renderToStaticMarkup(React.createElement(cards.default, { factor: { ...base, period: "FY2026", source_url: "javascript:alert(1)", fetched_at: "2026-10-24T12:00:00Z" } }));
  assert.ok(html.includes("FY2026"));
  assert.ok(html.includes("Publisher timestamp not supplied"));
  assert.ok(!html.includes("javascript:"));
  assert.equal(helpers.safeIpoLink("http://example.com"), undefined);
});

test("unannounced IPOs stay separate and missing demand sorts after a real zero", () => {
  const rows = [
    { id: "unknown", name: "Unknown", stage: "announced", issue_type: "regular", signals: { qib: { value: null } } },
    { id: "pending", name: "Pending", stage: "upcoming", issue_type: "regular", signals: { qib: { value: null } } },
    { id: "zero", name: "Zero", stage: "open", issue_type: "sme", signals: { qib: { value: 0 } } },
  ];
  assert.deepEqual(helpers.visibleIpos(rows, "active", "all", "", "qib").map(row => row.id), ["zero", "pending"]);
  assert.deepEqual(helpers.visibleIpos(rows, "announced", "all", "", "date").map(row => row.id), ["unknown"]);
  assert.deepEqual(helpers.visibleIpos(rows, "active", "sme", "zero", "date").map(row => row.id), ["zero"]);
});
