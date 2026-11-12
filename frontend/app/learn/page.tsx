"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import "./learn.css";

const PROGRESS_KEY = "trading-desk.learn-progress.v1";
const lessons = [
  {
    id: "observe", number: "01", category: "Observe", title: "Read the market", href: "/nifty", action: "Open NIFTY research",
    description: "Start with price. Then look at one piece of evidence behind it.",
    steps: [
      "Find the NIFTY price chart and change its interval.",
      "Choose a core market factor and inspect its source date.",
      "Compare its recent movement with the NIFTY chart.",
    ],
    takeaway: "A reading and its timestamp belong together.",
  },
  {
    id: "backtest", number: "02", category: "Compare", title: "Inspect a backtest", href: "/backtests?slug=sample-momentum-nifty", action: "Open sample backtest",
    description: "See how a strategy behaved on past data, including its difficult periods.",
    steps: [
      "Open the included sample momentum backtest.",
      "Find the equity curve and look for a peak followed by a decline.",
      "Inspect a trade and compare its result with the overall return.",
    ],
    takeaway: "The sample explains the interface; it is not a live strategy result.",
  },
  {
    id: "paper", number: "03", category: "Practise", title: "Try a paper trade", href: "/paper", action: "Open paper trading",
    description: "Use simulated orders to understand an order, a fill and a position.",
    steps: [
      "Choose a stock, a side and a quantity in the order ticket.",
      "Review your order, then place it if you want to practise.",
      "Inspect its status in Orders and any resulting position.",
    ],
    takeaway: "Paper orders are simulated. A fill depends on the available price data.",
  },
] as const;

const glossary = [
  ["NIFTY 50", "An index tracking 50 large companies listed on India's National Stock Exchange. Its value is an index level, not a stock price."],
  ["OHLC", "Open, high, low and close: the four prices that describe a candle over its chosen time interval."],
  ["Volume", "The amount traded during an interval. Volume and open interest measure different things."],
  ["P&L", "Profit and loss. For a simple buy position, gross P&L is (exit price − entry price) × quantity, before costs."],
  ["Drawdown", "A decline from a previous peak in the equity curve. It helps describe how much a strategy lost during a difficult period."],
  ["Equity curve", "The account or strategy value plotted over time. Read its declines as well as its final value."],
  ["Backtest", "A historical simulation of a strategy. Results depend on the data, rules, costs and execution assumptions used."],
  ["Paper trading", "Simulated order placement and position tracking. It lets you practise the workflow without sending those orders to a broker."],
  ["Open interest (OI)", "The number of outstanding derivative contracts that have not been closed or settled. It describes positioning, not a guaranteed price direction."],
  ["Put-call ratio (PCR)", "A comparison of put activity with call activity. Check whether the ratio uses open interest or volume, and which expiry it covers."],
  ["Max pain", "The strike level with the lowest theoretical aggregate option payout at expiry for the selected open-interest snapshot. It is not a forecast."],
  ["Implied volatility (IV)", "The volatility implied by an option's market price under a pricing model. It does not tell you which direction the market will move."],
  ["Expiry", "The date on which a derivative contract expires. Compare options from the same expiry when inspecting a snapshot."],
  ["Credit spread", "An option position combining a sold option and a bought option for a net premium received. Its legs, strikes and expiry determine its payoff."],
  ["Research confidence", "This desk's score for how well a setup meets its research criteria. It is not a calibrated probability of profit."],
  ["Realized / unrealized P&L", "Realized P&L comes from closed trades. Unrealized P&L is the changing gain or loss on an open position at its current mark."],
] as const;

const stepIds = lessons.flatMap(lesson => lesson.steps.map((_, index) => `${lesson.id}-${index + 1}`));
const rupees = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 });

function readProgress(raw: string | null): Record<string, boolean> {
  const saved: unknown = JSON.parse(raw || "{}");
  if (!saved || typeof saved !== "object" || Array.isArray(saved)) return {};
  return Object.fromEntries(stepIds.map(id => [id, (saved as Record<string, unknown>)[id] === true]));
}

export default function LearnPage() {
  const [completed, setCompleted] = useState<Record<string, boolean>>({});
  const [progressReady, setProgressReady] = useState(false);
  const [query, setQuery] = useState("");
  const [entry, setEntry] = useState("100");
  const [exit, setExit] = useState("110");
  const [quantity, setQuantity] = useState("5");

  useEffect(() => {
    const loadProgress = () => {
      try { setCompleted(readProgress(localStorage.getItem(PROGRESS_KEY))); }
      catch { /* Exercises still work when storage is unavailable. */ }
    };
    loadProgress();
    setProgressReady(true);
    const syncProgress = (event: StorageEvent) => { if (event.key === PROGRESS_KEY || event.key === null) loadProgress(); };
    window.addEventListener("storage", syncProgress);
    return () => window.removeEventListener("storage", syncProgress);
  }, []);

  function updateStep(id: string, checked: boolean) {
    let next = { ...completed, [id]: checked };
    try {
      let saved = completed;
      try { saved = readProgress(localStorage.getItem(PROGRESS_KEY)); }
      catch { /* Replace malformed saved progress with this session's progress. */ }
      next = { ...saved, [id]: checked };
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(next));
    } catch { next = { ...completed, [id]: checked }; }
    setCompleted(next);
  }

  const completedCount = stepIds.filter(id => completed[id]).length;
  const visibleTerms = glossary.filter(([term, definition]) => `${term} ${definition}`.toLowerCase().includes(query.trim().toLowerCase()));
  const entryValue = Number(entry), exitValue = Number(exit), quantityValue = Number(quantity);
  const validExample = entry.trim() !== "" && exit.trim() !== "" && quantity.trim() !== "" &&
    Number.isFinite(entryValue) && entryValue > 0 && Number.isFinite(exitValue) && exitValue >= 0 &&
    Number.isSafeInteger(quantityValue) && quantityValue > 0 && Number.isFinite((exitValue - entryValue) * quantityValue);
  const pnl = validExample ? (exitValue - entryValue) * quantityValue : null;

  return <AppShell title="Learn the desk">
    <div className="learn-page">
      <section className="learn-intro" aria-labelledby="learn-heading">
        <div>
          <span className="learn-eyebrow">Your first steps</span>
          <h2 id="learn-heading">A little practice.<br />A clearer trading desk.</h2>
          <p>Work through three short exercises at your own pace. Explore the tools, check off what you try, and look up unfamiliar terms here.</p>
          <a className="learn-text-link" href="#learn-playground">Try the P&amp;L example <span aria-hidden="true">↗</span></a>
        </div>
        <div className="learn-progress">
          <div className="learn-progress-label"><span>Your progress</span><strong>{completedCount}<span> / {stepIds.length}</span></strong></div>
          <progress value={completedCount} max={stepIds.length} aria-label="Completed learning steps" />
          <p>{completedCount === stepIds.length ? "All exercises checked. Revisit any tool whenever you like." : "Check off each step after you have tried it."}</p>
          <small>Progress stays in this browser when storage is available.</small>
        </div>
      </section>

      <section className="learn-path" aria-labelledby="learn-path-heading">
        <div className="learn-section-heading"><div><span className="learn-eyebrow">A suggested route</span><h2 id="learn-path-heading">From observation to practice</h2></div><span className="learn-muted">You can start with any exercise.</span></div>
        <div className="learn-lesson-grid">
          {lessons.map(lesson => {
            const lessonCount = lesson.steps.filter((_, index) => completed[`${lesson.id}-${index + 1}`]).length;
            return <article className={`learn-lesson ${lessonCount === lesson.steps.length ? "is-complete" : ""}`} key={lesson.id}>
              <div className="learn-lesson-meta"><span className="learn-lesson-number">{lesson.number}</span><span>{lesson.category}</span><span className="learn-lesson-count">{lessonCount} / {lesson.steps.length}</span></div>
              <h3>{lesson.title}</h3><p>{lesson.description}</p>
              <ol className="learn-checklist">
                {lesson.steps.map((step, index) => {
                  const id = `${lesson.id}-${index + 1}`;
                  return <li key={id}><label htmlFor={id}><input id={id} type="checkbox" checked={Boolean(completed[id])} disabled={!progressReady} onChange={event => updateStep(id, event.target.checked)} /><span>{step}</span></label></li>;
                })}
              </ol>
              <div className="learn-takeaway">{lesson.takeaway}</div>
              <Link className="learn-route-link" href={lesson.href}>{lesson.action}<span aria-hidden="true">→</span></Link>
            </article>;
          })}
        </div>
      </section>

      <section className="learn-playground" id="learn-playground" aria-labelledby="learn-example-heading">
        <div className="learn-example-intro"><span className="learn-eyebrow">Try the numbers</span><h2 id="learn-example-heading">How a buy trade makes or loses money</h2><p>Change the entry price, exit price or quantity to see how gross profit and loss changes.</p><span className="badge warn">Illustrative example · no order placed</span><p className="learn-example-note">This local calculation excludes fees, taxes and slippage. It uses your example values and needs no market connection.</p></div>
        <div className="learn-calculator">
          <div className="learn-calculator-inputs">
            <label htmlFor="learn-entry">Entry price (₹)<input id="learn-entry" type="number" min="0.01" step="0.01" inputMode="decimal" value={entry} onChange={event => setEntry(event.target.value)} /></label>
            <label htmlFor="learn-exit">Exit price (₹)<input id="learn-exit" type="number" min="0" step="0.01" inputMode="decimal" value={exit} onChange={event => setExit(event.target.value)} /></label>
            <label htmlFor="learn-quantity">Quantity<input id="learn-quantity" type="number" min="1" step="1" inputMode="numeric" value={quantity} onChange={event => setQuantity(event.target.value)} /></label>
          </div>
          <div className="learn-example-result" aria-live="polite" aria-atomic="true">
            <span>Example gross P&amp;L</span>
            <strong className={pnl == null ? "" : pnl > 0 ? "pos" : pnl < 0 ? "neg" : ""}>{pnl == null ? "—" : `${pnl > 0 ? "+" : ""}${rupees.format(pnl)}`}</strong>
            <p>{pnl == null ? "Enter a positive entry price, a nonnegative exit price and a whole quantity above zero." : `(${rupees.format(exitValue)} − ${rupees.format(entryValue)}) × ${quantityValue.toLocaleString("en-IN")} = ${rupees.format(pnl)}`}</p>
            {pnl != null && <small>{pnl > 0 ? "The exit price is higher than the entry price." : pnl < 0 ? "The exit price is lower than the entry price." : "Equal entry and exit prices give zero gross P&L."}</small>}
          </div>
        </div>
      </section>

      <section className="learn-glossary" id="learn-glossary" aria-labelledby="learn-glossary-heading">
        <div className="learn-section-heading"><div><span className="learn-eyebrow">Keep this close</span><h2 id="learn-glossary-heading">The desk, in plain language</h2></div><div className="learn-term-search"><label htmlFor="learn-term-query">Find a term</label><input id="learn-term-query" type="search" placeholder="Try drawdown, OI or expiry…" value={query} onChange={event => setQuery(event.target.value)} /></div></div>
        <div className="learn-search-count" role="status">{visibleTerms.length} of {glossary.length} terms</div>
        {visibleTerms.length ? <dl className="learn-term-grid">{visibleTerms.map(([term, definition]) => <div key={term}><dt>{term}</dt><dd>{definition}</dd></div>)}</dl> : <div className="learn-no-terms"><p>No terms match “{query}”. Try a shorter word.</p><button type="button" onClick={() => setQuery("")}>Clear search</button></div>}
      </section>
    </div>
  </AppShell>;
}
