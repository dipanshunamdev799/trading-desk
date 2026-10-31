"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp,
  type Time,
  TickMarkType,
  ColorType,
  CrosshairMode,
  type SeriesMarker,
  type LogicalRange,
} from "lightweight-charts";
import type { Candle } from "@/lib/api";
import { useExpandedChart } from "@/components/ExpandableChartPanel";
import { PriceActionOverlay } from "@/components/priceActionOverlay";
import { compactStudyLabel, studyColor, studyTime, type StudyOverlay } from "@/lib/priceAction";

export type ChartPoint = { ts: string | number; value: number };

/** Parse API timestamps (ISO, date-only, epoch) to unix seconds. */
function toUnix(ts: string | number): number | null {
  if (typeof ts === "number" && Number.isFinite(ts)) {
    return ts < 1e12 ? Math.floor(ts) : Math.floor(ts / 1000);
  }
  if (typeof ts !== "string" || !ts) return null;
  const s = ts.trim().replace(" ", "T");
  // date-only
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
    const d = new Date(`${s}T00:00:00Z`).getTime();
    return Number.isFinite(d) ? Math.floor(d / 1000) : null;
  }
  // strip sub-second noise some drivers emit
  const cleaned = s.replace(/\.\d+/, (m) => m.slice(0, 4));
  const d = new Date(cleaned.endsWith("Z") || cleaned.includes("+") ? cleaned : `${cleaned}Z`).getTime();
  return Number.isFinite(d) ? Math.floor(d / 1000) : null;
}

type Bar = { time: UTCTimestamp; open: number; high: number; low: number; close: number };

function sanitizeCandles(candles: Candle[]): Bar[] {
  const map = new Map<number, Bar>();
  for (const c of candles) {
    const t = toUnix(c.ts);
    if (t == null) continue;
    const o = Number(c.open);
    const h = Number(c.high);
    const l = Number(c.low);
    const cl = Number(c.close);
    if (![o, h, l, cl].every(Number.isFinite)) continue;
    map.set(t, {
      time: t as UTCTimestamp,
      open: o,
      high: Math.max(h, o, cl),
      low: Math.min(l, o, cl),
      close: cl,
    });
  }
  return [...map.entries()].sort((a, b) => a[0] - b[0]).map(([, b]) => b);
}

function sanitizeEquity(points: ChartPoint[]): { time: UTCTimestamp; value: number }[] {
  const map = new Map<number, number>();
  for (const p of points) {
    const t = toUnix(p.ts);
    const v = Number(p.value);
    if (t == null || !Number.isFinite(v)) continue;
    map.set(t, v);
  }
  return [...map.entries()].sort((a, b) => a[0] - b[0]).map(([time, value]) => ({
    time: time as UTCTimestamp,
    value,
  }));
}

export default function ChartPanel({
  candles,
  equity,
  height = 420,
  chartType = "candlestick",
  timeZone,
  study,
  showVolume = true,
  emaOverlays,
  indicatorCandles,
}: {
  candles: Candle[];
  equity?: ChartPoint[];
  height?: number;
  chartType?: "candlestick" | "line" | "area";
  timeZone?: string;
  study?: StudyOverlay;
  showVolume?: boolean;
  emaOverlays?: readonly { period: number; color: string }[];
  indicatorCandles?: Candle[];
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const viewport = useRef<LogicalRange | null>(null);
  const expanded = useExpandedChart();

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const width = Math.max(el.clientWidth || 640, 320);
    const formatTime = (time: Time, options: Intl.DateTimeFormatOptions): string => {
      const date = typeof time === "number" ? new Date(time * 1000)
        : typeof time === "string" ? new Date(`${time}T00:00:00Z`)
        : new Date(Date.UTC(time.year, time.month - 1, time.day));
      return new Intl.DateTimeFormat("en-IN", { timeZone, ...options }).format(date);
    };

    const chart = createChart(el, {
      width,
      height: Math.max(el.clientHeight || height, 160),
      autoSize: false,
      ...(timeZone ? { localization: { locale: "en-IN", timeFormatter: (time: Time) => formatTime(time, { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }) } } : {}),
      layout: {
        background: { type: ColorType.Solid, color: "#121820" },
        textColor: "#8B9AAB",
        fontFamily: "JetBrains Mono, Cascadia Code, ui-monospace, monospace",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: "#1A2330" },
        horzLines: { color: "#1A2330" },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: "#2DD4A8", width: 1, style: 2, labelBackgroundColor: "#2DD4A8" },
        horzLine: { color: "#2DD4A8", width: 1, style: 2, labelBackgroundColor: "#2DD4A8" },
      },
      rightPriceScale: { borderColor: "#243041" },
      timeScale: { borderColor: "#243041", timeVisible: true, secondsVisible: false,
        ...(timeZone ? { tickMarkFormatter: (time: Time, kind: TickMarkType) => formatTime(time,
          kind === TickMarkType.Year ? { year: "numeric" }
          : kind === TickMarkType.Month ? { month: "short" }
          : kind === TickMarkType.DayOfMonth ? { day: "2-digit" }
          : { hour: "2-digit", minute: "2-digit", hourCycle: "h23" }) } : {}),
      },
    });

    const bars = sanitizeCandles(candles);
    const eq = equity ? sanitizeEquity(equity) : [];

    let priceSeries: ISeriesApi<"Candlestick"> | ISeriesApi<"Area"> | ISeriesApi<"Line"> | null = null;
    if (bars.length) {
      if (chartType === "candlestick") {
        const candleSeries: ISeriesApi<"Candlestick"> = chart.addCandlestickSeries({
          upColor: "#2DD4A8",
          downColor: "#F07178",
          borderVisible: false,
          wickUpColor: "#2DD4A8",
          wickDownColor: "#F07178",
        });
        candleSeries.setData(bars);
        priceSeries = candleSeries;
      } else {
        const price = chartType === "area"
          ? chart.addAreaSeries({ lineColor: "#2DD4A8", topColor: "rgba(45,212,168,0.24)", bottomColor: "rgba(45,212,168,0.01)", lineWidth: 2 })
          : chart.addLineSeries({ color: "#2DD4A8", lineWidth: 2 });
        price.setData(bars.map((bar) => ({ time: bar.time, value: bar.close })));
        priceSeries = price;
      }
      if (showVolume) {
      const volumeSeries: ISeriesApi<"Histogram"> = chart.addHistogramSeries({
        priceFormat: { type: "volume" },
        priceScaleId: "vol",
      });
      chart.priceScale("vol").applyOptions({
        scaleMargins: { top: 0.82, bottom: 0 },
      });

      const byTime = new Map(candles.map((c) => [toUnix(c.ts), c]));
      volumeSeries.setData(
        bars.map((b) => {
          const src = byTime.get(b.time as unknown as number);
          return {
            time: b.time,
            value: Number(src?.volume) || 0,
            color: b.close >= b.open ? "rgba(45,212,168,0.35)" : "rgba(240,113,120,0.35)",
          };
        })
      );
      }
    }

    // Warm up from loaded history before filtering to the displayed session.
    // Seed each EMA with the first period's SMA, then smooth closing prices.
    if (bars.length && emaOverlays?.length) {
      const history = sanitizeCandles(indicatorCandles ?? candles);
      const visibleTimes = new Set(bars.map(bar => bar.time));
      for (const { period, color } of emaOverlays) {
        if (!Number.isInteger(period) || period < 1 || history.length < period) continue;
        let value = history.slice(0, period).reduce((sum, bar) => sum + bar.close, 0) / period;
        const multiplier = 2 / (period + 1);
        const points: { time: UTCTimestamp; value: number }[] = [];
        for (let index = period - 1; index < history.length; index++) {
          const bar = history[index];
          if (index >= period) value += multiplier * (bar.close - value);
          if (visibleTimes.has(bar.time)) points.push({ time: bar.time, value });
        }
        if (!points.length) continue;
        const ema = chart.addLineSeries({ color, lineWidth: 2, priceScaleId: "right",
          title: `EMA ${period}`, priceLineVisible: false });
        ema.setData(points);
      }
    }

    let tooltip: HTMLDivElement | null = null;
    if (priceSeries && study) {
      priceSeries.attachPrimitive(new PriceActionOverlay(study));
      const byTime = new Map<number, typeof study.events>();
      for (const event of study.events) {
        const time = toUnix(event.ts);
        if (time != null) byTime.set(time, [...(byTime.get(time) || []), event]);
      }
      let lastLabelIndex = -10;
      const markers: SeriesMarker<UTCTimestamp>[] = [...byTime].sort(([a], [b]) => a-b).map(([time, events]) => {
        const event = events.find(row => [11, 13, 14, 20, 39, 42].includes(row.concept)) || events[0];
        const index = bars.findIndex(bar => bar.time === time);
        const showLabel = index-lastLabelIndex >= 3 || study.focus === event.ts;
        if (showLabel) lastLabelIndex = index;
        return { time: time as UTCTimestamp, position: event.side > 0 ? "belowBar" : "aboveBar", color: studyColor(event.side),
          shape: event.side > 0 ? "arrowUp" : event.side < 0 ? "arrowDown" : "circle", size: .7,
          text: showLabel ? compactStudyLabel(event) + (events.length > 1 ? ` +${events.length-1}` : "") : "" };
      });
      priceSeries.setMarkers(markers);
      tooltip = document.createElement("div"); tooltip.className = "price-study-tooltip"; tooltip.style.display = "none";
      el.appendChild(tooltip);
      chart.subscribeCrosshairMove(param => {
        if (!tooltip || !param.point || param.time == null) { if (tooltip) tooltip.style.display = "none"; return; }
        const events = typeof param.time === "number" ? byTime.get(param.time) || [] : [];
        if (!events.length) { tooltip.style.display = "none"; return; }
        tooltip.textContent = `Confirmed ${studyTime(events[0].known_at)} IST\n` + events.map(row => `${row.label}${row.level != null ? ` · ${row.level.toFixed(2)}` : ""}`).join("\n");
        tooltip.style.display = "block";
        tooltip.style.left = `${Math.max(6, Math.min(param.point.x+16, el.clientWidth-290))}px`;
        tooltip.style.top = `${Math.max(6, Math.min(param.point.y+16, el.clientHeight-tooltip.offsetHeight-10))}px`;
      });
    }

    if (eq.length) {
      const line = chart.addLineSeries({
        color: "#61AFEF",
        lineWidth: 2,
        priceScaleId: bars.length ? "right" : "right",
        title: "equity",
      });
      line.setData(eq);
    }

    if (bars.length || eq.length) {
      chart.timeScale().fitContent();
      // zoom to last ~120 bars so long history is readable
      if (bars.length > 80) {
        chart.timeScale().setVisibleLogicalRange({
          from: Math.max(0, bars.length - 120),
          to: bars.length + 2,
        });
      }
      if (viewport.current) chart.timeScale().setVisibleLogicalRange(viewport.current);
      if (study?.focus) {
        const index = bars.findIndex(bar => bar.time === toUnix(study.focus!));
        if (index >= 0) chart.timeScale().setVisibleLogicalRange({ from: Math.max(-1, index-15), to: Math.min(bars.length+2, index+15) });
      }
    }

    chartRef.current = chart;

    const onResize = () => {
      if (ref.current) {
        chart.resize(Math.max(ref.current.clientWidth, 1), Math.max(ref.current.clientHeight, 160));
      }
    };
    window.addEventListener("resize", onResize);
    const ro = new ResizeObserver(onResize);
    ro.observe(el);
    onResize();

    return () => {
      viewport.current = chart.timeScale().getVisibleLogicalRange?.() || null;
      tooltip?.remove();
      window.removeEventListener("resize", onResize);
      ro.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [candles, equity, height, chartType, timeZone, study, showVolume, emaOverlays, indicatorCandles]);

  return <div ref={ref} className="chart-frame" style={{ height: expanded ? "100%" : height, width: "100%" }} />;
}
