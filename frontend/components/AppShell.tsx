"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { api, type Health } from "@/lib/api";
import { useLiveMarket } from "@/lib/liveMarket";
import { WORKSPACE_TOOLS } from "@/lib/workspace";
import DeskIcon from "./DeskIcon";
import "./shell.css";

export default function AppShell({ children, title }: { children: ReactNode; title: string }) {
  const pathname = usePathname();
  const tool = WORKSPACE_TOOLS.find(item => item.href === pathname);
  const [health, setHealth] = useState<Health | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [search, setSearch] = useState("");
  const searchDialog = useRef<HTMLDialogElement>(null);
  const searchInput = useRef<HTMLInputElement>(null);
  const sidebarRef = useRef<HTMLElement>(null);
  const menuTriggerRef = useRef<HTMLButtonElement>(null);
  const mainRef = useRef<HTMLDivElement>(null);
  const live = useLiveMarket(["NSE_INDEX|Nifty 50"]);
  const groups = ["Start here", "Explore markets", "Practise & review"];
  const advancedActive = tool?.group === "Advanced tools";
  const [advancedOpen, setAdvancedOpen] = useState(advancedActive);
  const matches = WORKSPACE_TOOLS.filter(item => `${item.label} ${item.description} ${item.group}`.toLowerCase().includes(search.toLowerCase().trim()));

  useEffect(() => { document.title = `${tool?.label || title} · Trading Desk`; }, [tool?.label, title]);

  function openSearch() {
    setMenuOpen(false);
    setSearch("");
    if (!searchDialog.current?.open) searchDialog.current?.showModal();
    searchInput.current?.focus();
  }
  useEffect(() => {
    const keydown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") { event.preventDefault(); openSearch(); }
      if (event.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", keydown);
    return () => window.removeEventListener("keydown", keydown);
  }, []);
  useEffect(() => {
    const main = mainRef.current;
    if (main) main.inert = menuOpen;
    if (!menuOpen) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const focusFrame = requestAnimationFrame(() => sidebarRef.current?.querySelector<HTMLButtonElement>(".desk-mobile-close")?.focus());
    const trapFocus = (event: KeyboardEvent) => {
      if (event.key !== "Tab") return;
      const controls = Array.from(sidebarRef.current?.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), summary, [tabindex="0"]') || []).filter(element => {
        const closedDetails = element.closest("details:not([open])");
        const hiddenByDetails = closedDetails && element !== closedDetails.querySelector("summary");
        return !hiddenByDetails && element.getClientRects().length > 0 && getComputedStyle(element).visibility !== "hidden";
      });
      const first = controls[0], last = controls[controls.length - 1];
      if (!first || !last) return;
      if (!sidebarRef.current?.contains(document.activeElement)) { event.preventDefault(); first.focus(); }
      else if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", trapFocus);
    return () => { cancelAnimationFrame(focusFrame); document.body.style.overflow = previous; document.removeEventListener("keydown", trapFocus); if (main) main.inert = false; menuTriggerRef.current?.focus(); };
  }, [menuOpen]);
  useEffect(() => {
    const desktop = window.matchMedia("(min-width: 961px)");
    const closeOnDesktop = () => { if (desktop.matches) setMenuOpen(false); };
    desktop.addEventListener("change", closeOnDesktop);
    return () => desktop.removeEventListener("change", closeOnDesktop);
  }, []);
  useEffect(() => { setMenuOpen(false); searchDialog.current?.close(); if (advancedActive) setAdvancedOpen(true); }, [pathname, advancedActive]);
  useEffect(() => {
    let alive = true;
    const load = async () => {
      try { const h = await api.health(); if (alive) { setHealth(h); setHealthError(null); } }
      catch (e) { if (alive) setHealthError(e instanceof Error ? e.message : "API unreachable"); }
    };
    void load();
    const id = setInterval(load, 15000);
    return () => { alive = false; clearInterval(id); };
  }, []);

  const navLink = (item: typeof WORKSPACE_TOOLS[number]) => <Link key={item.href} href={item.href} className={pathname === item.href ? "active" : undefined} aria-current={pathname === item.href ? "page" : undefined} onClick={() => setMenuOpen(false)}><DeskIcon name={item.icon} size={18} /><span>{item.label}</span>{item.href === "/learn" && <small className="nav-new">GUIDE</small>}</Link>;

  return <div className="app-shell desk-shell">
    <a className="desk-skip-link" href="#desk-main">Skip to content</a>
    {menuOpen && <button className="desk-menu-backdrop" aria-label="Close navigation" onClick={() => setMenuOpen(false)} />}
    <aside ref={sidebarRef} id="desk-navigation" role={menuOpen ? "dialog" : undefined} aria-modal={menuOpen || undefined} aria-label="Workspace navigation" className={`sidebar ${menuOpen ? "is-open" : ""}`}>
      <Link href="/" className="desk-brand" aria-label="Trading Desk overview"><span className="desk-brand-mark"><DeskIcon name="chart" size={23} /></span><span>Trading<span className="desk-brand-light">Desk</span><small>RESEARCH & PRACTICE</small></span></Link>
      <button className="desk-mobile-close" onClick={() => setMenuOpen(false)} aria-label="Close navigation"><DeskIcon name="close" /></button>
      <nav className="nav" aria-label="Main navigation">
        {groups.map(group => <div className="desk-nav-group" key={group}><div className="desk-nav-heading">{group}</div>{WORKSPACE_TOOLS.filter(item => item.group === group).map(navLink)}</div>)}
        <div className="desk-nav-group"><button className="desk-advanced-toggle" aria-expanded={advancedOpen} aria-controls="desk-advanced-links" onClick={() => setAdvancedOpen(!advancedOpen)}><span>Advanced tools</span><DeskIcon name="chevron" size={13} /></button>{advancedOpen && <div id="desk-advanced-links">{WORKSPACE_TOOLS.filter(item => item.group === "Advanced tools").map(navLink)}</div>}</div>
      </nav>
      <div className="desk-sidebar-bottom">
        <Link className="desk-learn-prompt" href="/learn"><DeskIcon name="book" size={19} /><div><strong>A little guidance?</strong><span>Learn the desk, one step at a time.</span></div><DeskIcon name="arrow" size={16} /></Link>
        <details className="side-status"><summary><span className={`dot ${healthError ? "bad" : health?.database === "ok" ? "ok" : "warn"}`} />{healthError || (health && health.database !== "ok") ? "Connection needs attention" : health?.database === "ok" ? "Workspace connected" : "Checking connections"}<DeskIcon name="chevron" size={12} /></summary><div className="desk-status-detail"><div><span className={`dot ${live?.status.fresh ? "ok" : "warn"}`} />{live?.status.fresh ? "Upstox live feed" : live?.session?.phase === "closed" ? "Market closed · saved / REST data" : "REST data · live feed idle"}</div><div><span className={`dot ${healthError ? "bad" : health ? "ok" : "warn"}`} />API {healthError ? "unavailable" : health ? "connected" : "checking"}</div><div><span className={`dot ${healthError ? "warn" : health?.database === "ok" ? "ok" : "warn"}`} />Database {healthError ? "unavailable" : health?.database ?? "checking"}</div><div><span className={`dot ${!healthError && health?.upstox_token ? "ok" : "warn"}`} />Upstox token {healthError ? "unknown" : health ? health.upstox_token ? "configured" : "missing" : "checking"}</div><Link href="/data">Inspect data & connections <span aria-hidden="true">→</span></Link></div></details>
        <span className="desk-local-label">LOCAL WORKSPACE</span>
      </div>
    </aside>
    <div ref={mainRef} className="main">
      <header className="topbar"><div className="desk-topbar-title"><button ref={menuTriggerRef} className="desk-mobile-menu" aria-label="Open navigation" aria-expanded={menuOpen} aria-controls="desk-navigation" onClick={() => setMenuOpen(!menuOpen)}><DeskIcon name="menu" /></button><span className="desk-breadcrumb">{tool?.group || "Workspace"}<span>/</span></span><h1>{tool?.label || title}</h1></div><div className="topbar-actions"><button className="desk-search-trigger" onClick={openSearch}><DeskIcon name="search" size={16} /><span>Find a tool</span><kbd>Ctrl K</kbd></button><Link className="desk-help-link" href="/learn" aria-label="Open learning guide"><DeskIcon name="help" size={19} /><span>Guide</span></Link></div></header>
      <main id="desk-main" className="content" tabIndex={-1}>
        {tool?.steps && <section className="desk-page-guide" aria-label={`${tool.label} guide`}><div className="desk-page-intro"><p>{tool.description}</p><span className="desk-context-label">{tool.group === "Advanced tools" ? "Advanced workspace" : tool.href === "/paper" ? "Simulated portfolio" : "Research workspace"}</span></div><details key={pathname}><summary><DeskIcon name="help" size={16} />First time here? <span>See what to try</span><DeskIcon name="chevron" size={13} /></summary><div className="desk-guide-content"><div><h2>Try this workflow</h2><ol>{tool.steps.map(step => <li key={step}>{step}</li>)}</ol></div><div><h2>A few useful terms</h2><dl>{tool.terms?.map(([term, definition]) => <div key={term}><dt>{term}</dt><dd>{definition}</dd></div>)}</dl>{tool.next && <Link className="desk-text-link" href={tool.next.href}>{tool.next.label}<DeskIcon name="arrow" size={15} /></Link>}</div></div></details></section>}
        {children}
      </main>
    </div>
    <dialog ref={searchDialog} className="desk-search-dialog" aria-labelledby="desk-search-title" onClick={event => { if (event.target === event.currentTarget) searchDialog.current?.close(); }}><div className="desk-search-header"><DeskIcon name="search" /><label id="desk-search-title" className="sr-only" htmlFor="desk-tool-search">Find a tool</label><input ref={searchInput} id="desk-tool-search" placeholder="Find a tool or something to do…" value={search} onChange={event => setSearch(event.target.value)} autoComplete="off" /><button onClick={() => searchDialog.current?.close()} aria-label="Close tool search"><DeskIcon name="close" size={18} /></button></div><p className="desk-search-hint" aria-live="polite">{matches.length} {matches.length === 1 ? "destination" : "destinations"} · use Tab to explore, Enter to open</p><div className="desk-search-results">{matches.map(item => <Link key={item.href} href={item.href} onClick={() => searchDialog.current?.close()}><DeskIcon name={item.icon} /><div><strong>{item.label}<small>{item.group}</small></strong><span>{item.description}</span></div><DeskIcon name="arrow" size={17} /></Link>)}{!matches.length && <div className="empty-note">No tools match “{search}”. Try “paper”, “options” or “learn”.</div>}</div></dialog>
  </div>;
}
