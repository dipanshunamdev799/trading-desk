"use client";

import Link from "next/link";
import {useCallback, useEffect, useState} from "react";
import AppShell from "@/components/AppShell";
import "../trading-bots/bots.css";

type Metrics = {equity:number; cash:number; total_pnl:number; realized_pnl:number; unrealized_pnl:number; fees:number; exposure:number; drawdown:number};
type Position = {instrument_key:string; symbol:string; book:number; value:number; mark:number; basis:number; reference_quantity:number; unrealized_pnl:number; entry_session:string};
type Order = {instrument_key:string; symbol:string; book:number; side:string; quantity:number; status:string; reason:string; decision_session:string};
type Policy = {daily_buy_fraction:number;max_exposure:number;max_buy_orders:number;max_position_fraction:number};
type PaperTest = {id:string;starts_on:string;created_at:string;mode:string;policy:Policy};
type Bot = {definition:{id:string; name:string; title:string; description:string; fingerprint:string; day0:string; window_end:string; books:number; verification:string}; state:{enabled:boolean; status:string; error:string; checked_at:string|null}; metrics:Metrics; positions:Position[]; orders:Order[]; last_session:string|null; events:{id:number;at:string;kind:string;message:string}[]; history:(Metrics & {session:string})[];paper_test?:PaperTest|null;archived_reference?:boolean};
type Dashboard = {bots:Bot[]; inputs:{ready:boolean; panel_count:number; last_refresh:string|null; requirement:string; parity_verified:boolean; storage:string; research_archive:{filename:string; files_imported:number; missing:string[]}|null; import_summary?:{daily_rows:number;corporate_actions:number;last_session:string};verification?:{last_session:string;c0_orders_matched:number;day_zero_intents_matched:number;integrity:Record<string,{pass:boolean}>}}; global_controls:{kill_switch:boolean}; as_of:string; busy:boolean;paper_testing?:PaperTest|null};

const money = (v:number) => new Intl.NumberFormat("en-IN", {style:"currency",currency:"INR",maximumFractionDigits:2}).format(v);
const time = (v:string|null) => v ? new Date(v).toLocaleString("en-IN", {timeZone:"Asia/Kolkata",hour12:false}) + " IST" : "—";
const percent = (v:number) => (100*v).toFixed(2) + "%";

async function request(path:string, body?:unknown) {
  const r = await fetch("/api/investment-bots" + path, body === undefined ? {cache:"no-store"} : {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  const p = await r.json();
  if (!r.ok) throw new Error(typeof p.detail === "string" ? p.detail : JSON.stringify(p.detail || p));
  return p;
}

function Tag({value}:{value:string}) {return <span className={`bot-tag ${value.toLowerCase()}`}>{value.replaceAll("_", " ")}</span>}

export default function InvestmentBotsPage() {
  return <AppShell title="Investment bots"><Investments/></AppShell>;
}

function Investments() {
  const [data,setData] = useState<Dashboard|null>(null);
  const [selected,setSelected] = useState("C0_R");
  const [tab,setTab] = useState("positions");
  const [error,setError] = useState("");
  const [notice,setNotice] = useState("");
  const [busy,setBusy] = useState(false);
  const [showArchive,setShowArchive] = useState(false);
  const [archived,setArchived] = useState<Bot|null>(null);
  const refresh = useCallback(async () => {
    try {setData(await request("/dashboard")); setError("");}
    catch(e) {setError((e as Error).message);}
  },[]);
  useEffect(() => {refresh(); const timer=setInterval(refresh,10000); return () => clearInterval(timer);},[refresh]);
  useEffect(()=>{
    let cancelled=false;setArchived(null);
    if(showArchive) request(`/${selected}/archive`).then(b=>{if(!cancelled)setArchived(b);}).catch(e=>{if(!cancelled)setError((e as Error).message);});
    return ()=>{cancelled=true;};
  },[showArchive,selected]);
  const act = async (path:string, body:unknown, message:string) => {
    setBusy(true); setNotice("");
    try {await request(path,body); setNotice(message); await refresh();}
    catch(e) {setError((e as Error).message);}
    finally {setBusy(false);}
  };
  const bot = showArchive?archived:data?.bots.find(b => b.definition.id === selected);
  const total = (key:keyof Metrics) => data?.bots.reduce((sum,b) => sum+b.metrics[key],0) || 0;
  return <div className="bots investment-bots">
    <nav className="bot-categories" aria-label="Bot category"><Link href="/trading-bots">F&amp;O bots</Link><Link href="/investment-bots" aria-current="page">Investment bots</Link></nav>
    <div className="bot-heading"><div><p className="bot-eyebrow">NSE CASH EQUITY · PAPER PORTFOLIOS</p><h2>Investment bots</h2><p>Four stock portfolios with separate capital, records and controls from the F&amp;O workers.</p></div><div><Tag value="paper"/>{data&&<span className="bot-note">Updated {time(data.as_of)}</span>}</div></div>
    {error&&<div className="bot-alert" role="alert">{error} <button onClick={refresh}>Retry connection</button></div>}
    {!data&&<p role="status">Loading investment portfolios…</p>}
    {data&&<>
      <div className="bot-global-controls"><button className="bot-start" disabled={busy||showArchive} onClick={()=>act("/global/control",{action:"start"},"Investment bots enabled. Input checks still apply.")}>Start investment bots</button><button className="bot-danger" disabled={busy||showArchive} onClick={()=>act("/global/control",{action:"pause"},"Investment processing paused. Recorded holdings are retained.")}>Pause investment bots</button><button disabled={busy||data.busy||showArchive} onClick={()=>act("/run",{},"Paper reconciliation queued. The dashboard will update when input checks finish.")}>{data.busy?"Checking inputs…":"Run paper cycle"}</button></div>
      {notice&&<p className="bot-note" role="status">{notice}</p>}
      {data.global_controls.kill_switch&&<div className="bot-alert">Investment processing is paused. Holdings remain recorded. Start investment bots releases this pause; F&amp;O controls are independent.</div>}
      {data.paper_testing&&<section className="paper-policy" aria-label="Paper allocation limits"><div className="paper-policy-heading"><div><strong>Gradual paper deployment</strong><p>Fresh test from {data.paper_testing.starts_on}. Each bot has its own ₹10 lakh allocation.</p></div><button onClick={()=>{setArchived(null);setShowArchive(v=>!v);}}>{showArchive?"Back to current paper test":"View original run archive"}</button></div><dl><div><dt>New buys per trading day</dt><dd>Up to {percent(data.paper_testing.policy.daily_buy_fraction)}</dd></div><div><dt>Exposure cap for new buys</dt><dd>{percent(data.paper_testing.policy.max_exposure)}</dd></div><div><dt>Buy orders per bot per day</dt><dd>Up to {data.paper_testing.policy.max_buy_orders}</dd></div></dl><p className="bot-note">Limits cover all five C2-S books together. Entries deferred by these limits stay queued; C0-R-X auction rejections still apply. Original results remain in the archive. Restarting the app does not reset this test.</p></section>}
      {showArchive&&<div className="bot-ready" role="status"><strong>Original run archive · Read only</strong><p>These are the positions and results recorded before the fresh paper test. Current limits and controls apply to the active test.</p></div>}
      {!data.inputs.ready&&<div className="bot-alert" role="status"><strong>Waiting for frozen daily inputs</strong><p>{data.inputs.requirement}. The original daily panel and static metadata have not been imported into PostgreSQL. These bots stay enabled and make no simulated fills until the input checks pass.</p>{data.inputs.research_archive&&<p>{data.inputs.research_archive.filename}: {data.inputs.research_archive.files_imported} source files imported into PostgreSQL. Frozen source hashes match the specifications. The archive references the daily panel in a separate research folder.</p>}<p>Setup: <code>python -m investment_bots.data &quot;PATH_TO_FROZEN_BUNDLE&quot;</code>. See <code>investment_bots/README.md</code> for the required files.</p></div>}
      {data.inputs.ready&&<div className="bot-ready" role="status"><strong>PostgreSQL inputs ready{data.inputs.parity_verified?" · Historical replay verified":" · Verification pending"}</strong><p>{data.inputs.panel_count.toLocaleString("en-IN")} frozen stocks{data.inputs.import_summary?` · ${data.inputs.import_summary.daily_rows.toLocaleString("en-IN")} daily bars · ${data.inputs.import_summary.corporate_actions} corporate-action records · Data through ${data.inputs.import_summary.last_session}`:""}.</p>{data.inputs.verification&&<p>{Object.values(data.inputs.verification.integrity).filter(c=>c.pass).length}/9 integrity checks passed. {data.inputs.verification.c0_orders_matched} historical C0-R orders and {data.inputs.verification.day_zero_intents_matched} day-zero paper intentions match the original research. Historical performance is kept separate from the paper P&amp;L below.</p>}</div>}
      <div className="bot-stats">{[["Paper allocation",money(4_000_000)],["Portfolio equity",money(total("equity"))],["Reference P&L",money(total("total_pnl"))],["Holding records",data.bots.reduce((s,b)=>s+b.positions.length,0)]].map(([k,v])=><div key={k}><span>{k}</span><strong>{v}</strong></div>)}</div>
      <p className="bot-note">₹10 lakh per strategy; C2-S divides its allocation into five ₹2 lakh books. Completed daily bars drive next-session official-open paper fills at 0.225% cost per side, reconciled the following morning. The ledger uses fractional shares; intended whole-share orders are reported separately. {data.paper_testing?"Paced paper results use the limits above and have separate records from the original research run.":"Reconciled sessions can include reconstructed history."} No broker orders are submitted.</p>
      <div className="bot-workspace"><div className="bot-list">{data.bots.map(b=><button className={`bot-card ${selected===b.definition.id?"selected":""}`} key={b.definition.id} onClick={()=>{setArchived(null);setSelected(b.definition.id);}}><div className="bot-card-title"><strong>{b.definition.name}</strong><Tag value="paper"/></div><p>{b.definition.title}</p><p>{b.definition.description}</p><div className="bot-card-foot"><Tag value={b.state.status}/><b className={b.metrics.total_pnl<0?"loss":"gain"}>{money(b.metrics.total_pnl)}</b></div></button>)}</div>
        {bot&&<section className="panel bot-detail"><div className="panel-header"><h2>{bot.definition.name} · {bot.definition.title}</h2><Tag value={bot.state.status}/></div><div className="bot-detail-body"><p>{bot.definition.description}</p><div className="bot-controls"><button disabled={busy||showArchive||bot.state.enabled} onClick={()=>act(`/${selected}/control`,{action:"start"},`${bot.definition.name} enabled.`)}>Start portfolio</button><button disabled={busy||showArchive||!bot.state.enabled} onClick={()=>act(`/${selected}/control`,{action:"pause"},`${bot.definition.name} paused; holdings retained.`)}>Pause portfolio</button><span className="bot-note">{bot.state.enabled?"Enabled":"Paused"} · Last session {bot.last_session||"none processed"}</span></div>
          {bot.state.error&&<div className="bot-alert">{bot.state.error}</div>}
          <dl className="investment-metrics">{[["Equity",money(bot.metrics.equity)],["Cash",money(bot.metrics.cash)],["Realized P&L",money(bot.metrics.realized_pnl)],["Unrealized P&L",money(bot.metrics.unrealized_pnl)],["Exposure",percent(bot.metrics.exposure)],["Current drawdown",percent(bot.metrics.drawdown)]].map(([k,v])=><div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
          <div className="bot-tabs" role="tablist" aria-label="Portfolio details">{["positions","orders","equity","logs","rules"].map(t=><button role="tab" id={`investment-tab-${t}`} aria-controls="investment-tab-panel" aria-selected={tab===t} className={tab===t?"active":""} key={t} onClick={()=>setTab(t)}>{t}</button>)}</div>
          <div id="investment-tab-panel" role="tabpanel" aria-labelledby={`investment-tab-${tab}`}>
            {tab==="positions"&&<div className="bot-table-scroll"><table><thead><tr><th>Instrument</th><th>Book</th><th>Reference shares</th><th>Last mark</th><th>Value</th><th>Unrealized P&amp;L</th></tr></thead><tbody>{bot.positions.map(p=><tr key={`${p.book}-${p.instrument_key}`}><td title={p.instrument_key}>{p.symbol}</td><td>{p.book+1}</td><td>{p.reference_quantity.toFixed(4)}</td><td>{money(p.mark)}</td><td>{money(p.value)}</td><td>{money(p.unrealized_pnl)}</td></tr>)}</tbody></table>{!bot.positions.length&&<div className="bot-empty">No reference holdings recorded.</div>}</div>}
            {tab==="orders"&&<><p className="bot-note">{bot.paper_test?`Queued paper intentions. At most ${bot.paper_test.policy.max_buy_orders} buy orders can fill per trading day; entries deferred by the allocation limits stay queued. Auction rejections still apply to C0-R-X.`:"Latest close’s whole-share intentions for the next available session. These are paper reports. A rejected zero-share intent can still differ from the fractional reference ledger."}</p><div className="bot-table-scroll"><table><thead><tr><th>Decision session</th><th>Instrument</th><th>Book</th><th>Side</th><th>Whole shares</th><th>Status</th></tr></thead><tbody>{bot.orders.map((o,i)=><tr key={i}><td>{o.decision_session}</td><td title={o.instrument_key}>{o.symbol}</td><td>{o.book+1}</td><td>{o.side}</td><td>{o.quantity}</td><td><Tag value={o.status}/></td></tr>)}</tbody></table>{!bot.orders.length&&<div className="bot-empty">No paper intents for the latest session.</div>}</div></>}
            {tab==="equity"&&<div className="bot-table-scroll"><table><thead><tr><th>Session</th><th>Equity</th><th>Cash</th><th>Net P&amp;L</th><th>Exposure</th></tr></thead><tbody>{bot.history.slice(-60).reverse().map(r=><tr key={r.session}><td>{r.session}</td><td>{money(r.equity)}</td><td>{money(r.cash)}</td><td>{money(r.total_pnl)}</td><td>{percent(r.exposure)}</td></tr>)}</tbody></table>{!bot.history.length&&<div className="bot-empty">No sessions processed. Historical research returns are not included in this ledger.</div>}</div>}
            {tab==="logs"&&<>{bot.events.map(e=><div className="bot-log" key={e.id}><span>{time(e.at)}</span><strong>{e.kind}</strong><p>{e.message}</p></div>)}{!bot.events.length&&<div className="bot-empty">No portfolio events yet.</div>}</>}
            {tab==="rules"&&<><p>Anchor: {bot.paper_test?.starts_on||bot.definition.day0} · Research window ends: {bot.definition.window_end} · {bot.definition.books} independent book{bot.definition.books>1?"s":""}.</p><p>Stock selection: top 300 by 63-session median traded value; rank by 63-session return divided by 42-session volatility. Up to 20 names per book; retain ranks 0–39; six names per industry at selection.</p>{selected==="C1_R"&&<p>Target exposure uses the 20-session volatility of the C0-R shadow portfolio anchored on 1 April 2025. Exposure changes exceeding 10 percentage points trigger next-open rescaling.</p>}{selected==="C0_R_X"&&<p>Only auction evidence classified as likely permits a reference fill. Missing, stale, imbalanced or oversized auction observations leave sells pending and drop buys. Prospective capture runs while the app is open around the morning auction.</p>}<p className="bot-note">Source configuration: <code>{bot.definition.fingerprint}</code>. {bot.definition.verification}. Pause stops processing and retains holdings; resume reconciles the reference book from its fixed anchor.</p><a href={`/api/investment-bots/${selected}/specification`} target="_blank" rel="noreferrer">Read original strategy specification</a></>}
          </div>
          <div className="bot-exports">{["orders","executions","equity"].map(kind=><a key={kind} href={`/api/investment-bots/${selected}/export?kind=${kind}&scope=${showArchive?"reference":"active"}`}>Export {kind}</a>)}</div>
          <p className="bot-note">Input check {time(bot.state.checked_at)} · Estimated reference costs {money(bot.metrics.fees)} · Paper only</p>
        </div></section>}
      </div>
    </>}
  </div>;
}
