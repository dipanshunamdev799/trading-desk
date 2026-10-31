const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const ts = require("typescript");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const compiled = ts.transpileModule(fs.readFileSync(path.join(__dirname, "../components/NiftyFactorCard.tsx"), "utf8"), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX },
});
const cards = {};
new Function("exports", "require", compiled.outputText)(cards, require);
const factor = { id: "fii_cash", label: "FII/FPI cash-market net flow", value: 887.65, unit: "₹ crore", status: "available",
  quality: "exchange_report", source: "NSE provisional cash report", source_url: "https://www.nseindia.com/reports/fii-dii",
  reported_at: "2026-10-23T00:00:00+05:30", reporting_date: "2026-10-23", change: null, change_pct: null,
  context: { gross_buy_cr: 14445.54, gross_sell_cr: 13557.89, unit_status: "verified", provisional: true } };

test("verified cash displays the net, both gross legs and session date without an invented release clock", () => {
  const html = renderToStaticMarkup(React.createElement(cards.default, { factor, onSelect: () => {} }));
  for (const text of ["887.65", "14,445.54", "13,557.89", "NSE provisional cash report", "Session 23 Oct 2026", "Net buying"])
    assert.ok(html.includes(text), text);
  assert.ok(!html.includes("Published 23 Oct, 00:00"));
  assert.equal(cards.factorStatusLabel(factor), "available");
});

test("zero and net selling are distinguished, and ambiguous units retain a specific label", () => {
  const zero = renderToStaticMarkup(React.createElement(cards.FactorChange, { factor: { ...factor, value: 0 } }));
  const selling = renderToStaticMarkup(React.createElement(cards.FactorChange, { factor: { ...factor, value: -20 } }));
  assert.ok(zero.includes("No net flow"));
  assert.ok(selling.includes("Net selling"));
  assert.equal(cards.factorStatusLabel({ ...factor, value: null, status: "missing", quality: "unverified_units" }), "Units unverified");
});
