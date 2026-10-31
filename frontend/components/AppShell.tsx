"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { api, type Health } from "@/lib/api";
import { useLiveMarket } from "@/lib/liveMarket";

const NAV = [
  { href: "/", label: "Desk" },
  { href: "/nifty", label: "NIFTY" },
  { href: "/maxpain", label: "Max Pain" },
  { href: "/ipos", label: "IPOs" },
  { href: "/backtests", label: "Backtests" },
  { href: "/paper", label: "Paper" },
  { href: "/credit-spreads", label: "NIFTY Credit Spreads" },
  { href: "/data", label: "Data" },
];

export default function AppShell({ children, title }: { children: ReactNode; title: string }) {
  const pathname = usePathname();
  const [health, setHealth] = useState<Health | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const live = useLiveMarket(["NSE_INDEX|Nifty 50"]);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const h = await api.health();
        if (alive) {
          setHealth(h);
          setHealthError(null);
        }
      } catch (e) {
        if (alive) setHealthError(e instanceof Error ? e.message : "API unreachable");
      }
    };
    load();
    const id = setInterval(load, 15000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          Trading <span>Desk</span>
        </div>
        <nav className="nav">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={pathname === item.href ? "active" : undefined}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="side-status">
          <div title={live?.status.error || "Streaming is used for supported fields during active sessions; other data uses REST."}>
            <span className={`dot ${live?.status.fresh ? "ok" : "warn"}`} />
            {live?.status.fresh ? "Upstox live feed" : live?.session?.phase === "closed" ? "Market closed · REST" : live?.status.connected ? "Feed idle · REST fallback" : "REST / feed connecting"}
          </div>
          <div>
            <span className={`dot ${health?.ok ? "ok" : healthError ? "bad" : "warn"}`} />
            API {health?.ok ? "up" : healthError ? "down" : "…"}
          </div>
          <div>
            <span className={`dot ${health?.database === "ok" ? "ok" : "bad"}`} />
            DB {health?.database ?? "…"}
          </div>
          <div>
            <span className={`dot ${health?.upstox_token ? "ok" : "warn"}`} />
            Upstox token {health?.upstox_token ? "set" : "missing"}
          </div>
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <h1>{title}</h1>
          <div className="topbar-actions">
            <span className="badge">local · plug-and-play</span>
          </div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
