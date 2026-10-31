"use client";

import { useEffect, useRef, useState } from "react";

export type MarketSession = { active: boolean; phase: "open" | "closed" | "unknown"; session_date: string | null; market_status: string; last_trade_at: string | null };
export type LiveQuote = { last_price: number; last_trade_time?: string; timestamp: string; volume?: number | null; oi?: number | null; ohlc?: Record<string, number>; _live_candles?: { interval: string; ts: string | number; open: number; high: number; low: number; close: number; vol?: number }[] };
export type LiveMarketEvent = { type: string; revision: number; instrument_keys: string[]; quotes: Record<string, LiveQuote>; session?: MarketSession; status: { enabled: boolean; connected: boolean; fresh?: boolean; active_instruments: number; last_frame_at: string | null; error: string | null; mode: string } };

type Listener = { keys: string[]; update: (event: LiveMarketEvent) => void };
const listeners = new Set<Listener>();
let socket: WebSocket | null = null;
let reconnect: ReturnType<typeof setTimeout> | undefined;
let heartbeat: ReturnType<typeof setInterval> | undefined;
let delay = 1000;
let lastEvent: LiveMarketEvent | null = null;

function watch() {
  if (socket?.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: "watch", instrument_keys: [...new Set([...listeners].flatMap(listener => listener.keys))] }));
}

function connect() {
  if (socket || !listeners.size) return;
  const url = new URL("/api/market/live", window.location.href);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  socket = new WebSocket(url);
  socket.onopen = () => { delay = 1000; watch(); heartbeat = setInterval(watch, 30_000); };
  socket.onmessage = message => {
    try {
      const event = JSON.parse(message.data) as LiveMarketEvent;
      if (event.type !== "market_update" || !Array.isArray(event.instrument_keys)) return;
      lastEvent = event;
      for (const listener of listeners) listener.update(event);
    } catch { /* Ignore malformed frames; REST fallback remains available. */ }
  };
  socket.onclose = () => {
    socket = null; clearInterval(heartbeat);
    if (lastEvent) {
      lastEvent = { ...lastEvent, instrument_keys: [], quotes: {}, status: { ...lastEvent.status, connected: false, fresh: false, mode: "rest", error: "Dashboard connection interrupted; reconnecting. REST fallback is available." } };
      for (const listener of listeners) listener.update(lastEvent);
    }
    if (listeners.size) { reconnect = setTimeout(connect, delay); delay = Math.min(delay * 2, 30_000); }
  };
  socket.onerror = () => socket?.close();
}

export function subscribeLiveMarket(keys: string[], update: (event: LiveMarketEvent) => void) {
  const listener = { keys, update };
  listeners.add(listener); if (lastEvent) update({ ...lastEvent, instrument_keys: [], quotes: {} }); connect(); watch();
  return () => {
    listeners.delete(listener); watch();
    if (!listeners.size) { clearTimeout(reconnect); clearInterval(heartbeat); lastEvent = null; const closing = socket; socket = null; if (closing) { closing.onclose = null; closing.close(); } }
  };
}

export function useLiveMarket(keys: string[], onUpdate?: (event: LiveMarketEvent) => void, enabled = true) {
  const [status, setStatus] = useState<LiveMarketEvent | null>(null);
  const callback = useRef(onUpdate);
  callback.current = onUpdate;
  const signature = [...new Set(keys)].sort().join(",");
  useEffect(() => {
    if (!enabled) return;
    let lastUpdate = 0;
    let previousConnection: string | undefined;
    return subscribeLiveMarket(signature ? signature.split(",") : [], event => {
      setStatus(event);
      const connection = `${event.status.connected}/${Boolean(event.status.fresh)}`;
      const changedConnection = previousConnection !== undefined && previousConnection !== connection;
      previousConnection = connection;
      if (document.visibilityState === "visible" && (changedConnection || event.instrument_keys.some(key => keys.includes(key)) && Date.now() - lastUpdate >= 3000)) {
        lastUpdate = Date.now(); callback.current?.(event);
      }
    });
  }, [signature, enabled]);
  return status;
}
