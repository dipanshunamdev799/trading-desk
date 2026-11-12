"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import ChartPanel from "@/components/ChartPanel";
import DeskIcon from "@/components/DeskIcon";
import { SourceBadge } from "@/components/Bits";
import { api, fmtNum, fmtPnl, type BacktestSummary, type CandleSeries, type PaperSummary } from "@/lib/api";
import "./overview.css";

const journeys = [
  { number: "01", category: "Observe", icon: "chart", title: "Read the market", description: "Get to know NIFTY. Explore the price chart and the evidence behind each market factor.", href: "/nifty", action: "Explore NIFTY", tone: "mint" },
  { number: "02", category: "Compare", icon: "history", title: "Test your understanding", description: "Look through a historical backtest. See the returns, the declines and the trades in between.", href: "/backtests", action: "Inspect a backtest", tone: "sand" },
  { number: "03", category: "Practise", icon: "wallet", title: "Learn by doing", description: "Choose an instrument, review an order and follow a position in your simulated portfolio.", href: "/paper", action: "Try paper trading", tone: "blue" },
];
const learningSteps = ["observe", "backtest", "paper"].flatMap(id => [1, 2, 3].map(step => `${id}-${step}`));

export default function DeskPage() { return <AppShell title="Overview"><DeskContent /></AppShell>; }

function DeskContent() {
  const [summary, setSummary] = useState<PaperSummary | null>(null);
  const [backtests, setBacktests] = useState<BacktestSummary[] | null>(null);
  const [series, setSeries] = useState<CandleSeries | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [chartLoading, setChartLoading] = useState(true);
  const [reload, setReload] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Record<string, boolean>>({});
  const completed = learningSteps.filter(id => completedSteps[id]).length;

  useEffect(() => {
    const readProgress = () => {
      try { const saved = JSON.parse(localStorage.getItem("trading-desk.learn-progress.v1") || "{}"); setCompletedSteps(Object.fromEntries(learningSteps.map(id => [id, saved?.[id] === true]))); }
      catch { setCompletedSteps({}); }
    };
    readProgress(); window.addEventListener("storage", readProgress);
    return () => window.removeEventListener("storage", readProgress);
  }, []);

  useEffect(() => {
    let alive = true;
    setErrors({}); setChartLoading(true);
    const failed = (section: string, reason: unknown) => { if (alive) setErrors(current => ({ ...current, [section]: reason instanceof Error ? reason.message : "Unable to load" })); };
    api.paperSummary().then(result => { if (alive) setSummary(result); }).catch(reason => failed("portfolio", reason));
    api.backtests().then(result => { if (alive) setBacktests(result); }).catch(reason => failed("backtests", reason));
    const from = new Date(); from.setUTCFullYear(from.getUTCFullYear() - 1);
    api.candles({ instrument_key: "NSE_INDEX|Nifty 50", interval: "1day", from_date: from.toISOString().slice(0, 10) })
      .then(result => { if (alive) setSeries(result); }).catch(reason => failed("chart", reason)).finally(() => { if (alive) setChartLoading(false); });
    return () => { alive = false; };
  }, [reload]);

  const latest = series?.candles[series.candles.length - 1];
  const progressLabel = completed === 9 ? "A great foundation to build on." : completed ? "Pick up where you left off." : "A few small steps. At your own pace.";
  return <div className="overview-page">
    <section className="overview-welcome" aria-labelledby="overview-heading">
      <div className="overview-welcome-copy"><span className="overview-eyebrow"><span className="overview-eyebrow-line" />YOUR RESEARCH WORKSPACE</span><h2 id="overview-heading">Make sense<br />of the market<span>.</span></h2><p>Explore the evidence, test an idea, and practise with paper trades. A clearer path starts here.</p><div className="overview-welcome-actions"><Link className="overview-primary-link" href="/learn">{completed ? "Continue learning" : "Start learning"}<DeskIcon name="arrow" size={16} /></Link><Link className="overview-secondary-link" href="/nifty">Go to NIFTY overview<DeskIcon name="arrow" size={15} /></Link></div></div>
      <Link className="overview-path-preview" href="/learn" aria-label={`Open learning path, ${completed} of 9 steps complete`}><div className="overview-path-title"><span>YOUR LEARNING PATH</span><span>{completed}/9 steps</span></div><div className="overview-path-track"><span style={{ width: `${completed / 9 * 100}%` }} /></div><div className="overview-path-items">{journeys.map((journey, index) => <div key={journey.number} className={[1, 2, 3].every(step => completedSteps[`${["observe", "backtest", "paper"][index]}-${step}`]) ? "is-complete" : ""}><span className="overview-path-dot">{[1, 2, 3].every(step => completedSteps[`${["observe", "backtest", "paper"][index]}-${step}`]) ? <DeskIcon name="check" size={12} /> : journey.number}</span><span>{journey.category}<small>{["Understand what you see", "Read historical evidence", "Try the order workflow"][index]}</small></span>{index === 0 && !completed && <em>Start here</em>}</div>)}</div><div className="overview-path-bottom"><span>{progressLabel}</span><DeskIcon name="arrow" size={17} /></div></Link>
    </section>

    <section className="overview-journey" aria-labelledby="overview-journey-heading"><div className="overview-section-heading"><div><h2 id="overview-journey-heading">Three ways to find your footing</h2><p>Choose a starting point. Every tool has a guide when you need it.</p></div><Link className="desk-text-link" href="/learn">View the learning guide<DeskIcon name="arrow" size={15} /></Link></div><div className="overview-journey-grid">{journeys.map(journey => <Link className={`overview-journey-card ${journey.tone}`} href={journey.href} key={journey.href}><div className="overview-card-top"><span className="overview-card-icon"><DeskIcon name={journey.icon} size={22} /></span><span>{journey.number} / {journey.category}</span></div><h3>{journey.title}</h3><p>{journey.description}</p><div className="overview-card-action">{journey.action}<DeskIcon name="arrow" size={16} /></div></Link>)}</div></section>

    <section className="overview-at-a-glance" aria-labelledby="overview-glance-heading"><div className="overview-section-heading"><div><h2 id="overview-glance-heading">Your desk at a glance</h2><p>A little market context and a look at your practice.</p></div><button className="overview-refresh" onClick={() => setReload(value => value + 1)} disabled={chartLoading}>Refresh overview</button></div><div className="overview-data-grid"><div className="panel overview-chart"><div className="panel-header"><div><h3>NIFTY 50<span>Daily · past year</span></h3>{latest && <strong className="overview-index-value">{fmtNum(latest.close)}<small>Index level</small></strong>}</div><div className="overview-chart-header-right">{series && <SourceBadge source={series.source} />}<Link href="/nifty" aria-label="Open NIFTY price chart"><DeskIcon name="arrow" size={20} /></Link></div></div><div className="panel-body tight">{series?.candles.length ? <ChartPanel candles={series.candles} height={260} /> : <div className="overview-chart-empty" role="status"><DeskIcon name="chart" size={30} /><strong>{chartLoading ? "Loading the price chart…" : errors.chart ? "The chart couldn't connect" : "No price history available yet"}</strong><p>{chartLoading ? "Your other tools are ready to explore." : "Open NIFTY to inspect available market history and its sources."}</p>{!chartLoading && <Link className="desk-text-link" href="/nifty">Open NIFTY overview<DeskIcon name="arrow" size={14} /></Link>}</div>}</div><div className="overview-chart-note">{latest ? `Last saved candle: ${new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", day: "numeric", month: "short", year: "numeric" }).format(new Date(latest.ts))}` : "Each chart keeps the date and source of its observations."}</div>{errors.chart && <details className="overview-error-detail"><summary>Chart connection details</summary><p>{errors.chart}</p></details>}</div>
      <div className="overview-practice-panel"><div className="overview-practice-heading"><span className="overview-eyebrow">PRACTICE ACCOUNT</span><span className="badge warn">Paper only</span></div><div className="overview-practice-value"><span>Total profit & loss</span><strong className={summary && summary.total_pnl < 0 ? "neg" : summary ? "pos" : ""}>{summary ? fmtPnl(summary.total_pnl) : "—"}</strong><p>{errors.portfolio ? "Portfolio connection unavailable. You can still explore the learning exercises." : summary ? "Your simulated results, before trading costs." : "Loading your simulated portfolio…"}</p></div><div className="overview-practice-stats"><div><strong>{summary ? summary.open_positions : "—"}</strong><span>Open positions</span></div><div><strong>{backtests ? backtests.length : "—"}</strong><span>Saved backtests</span></div></div><Link className="overview-practice-link" href="/paper">Open paper portfolio<DeskIcon name="arrow" size={17} /></Link></div></div></section>

    <section className="overview-saved" aria-labelledby="overview-saved-heading"><div className="overview-section-heading"><div><h2 id="overview-saved-heading">Pick up a backtest</h2><p>Explore the story behind a historical result.</p></div><Link className="desk-text-link" href="/backtests">View all results<DeskIcon name="arrow" size={15} /></Link></div>{backtests?.length ? <div className="overview-saved-list">{backtests.slice(0, 3).map(result => <Link href={`/backtests?slug=${encodeURIComponent(result.slug)}`} key={result.slug}><span className="overview-saved-icon"><DeskIcon name="history" size={18} /></span><div><strong>{result.name || result.slug}{result.slug.startsWith("sample-") && <small>Sample</small>}</strong><span>{result.strategy || "Historical research"}{result.interval ? ` · ${result.interval}` : ""}</span></div><DeskIcon name="arrow" size={17} /></Link>)}</div> : <div className="overview-saved-empty">{errors.backtests ? "Saved results are unavailable while the API is disconnected. You can explore the exercises in Learn the desk." : backtests ? "No saved results yet. Open Backtest results to see how historical research is organized." : "Looking for saved backtests…"}</div>}</section>
    <div className="overview-footer"><span>Curious about a term? The glossary is always close by.</span><Link href="/learn#learn-glossary">Open the glossary<DeskIcon name="arrow" size={14} /></Link></div>
  </div>;
}
