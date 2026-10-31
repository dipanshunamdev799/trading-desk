"use client";

import type { EChartsOption } from "@/components/EChartPanel";

const AXIS = {
  axisLine: { lineStyle: { color: "#243041" } },
  axisLabel: { color: "#8B9AAB", fontSize: 11 },
  splitLine: { lineStyle: { color: "#1A2330", width: 0.8 } },
  axisTick: { show: false },
};

const TOOLTIP = {
  backgroundColor: "#121820",
  borderColor: "#243041",
  textStyle: { color: "#E8EDF2", fontSize: 12, fontFamily: "Inter, sans-serif" },
  extraCssText: "box-shadow:0 8px 24px rgba(0,0,0,0.45);border-radius:8px;",
};

export function fmtLevel(value: number | null | undefined, digits = 2): string {
  if (value == null || !Number.isFinite(value)) return "—";
  return value.toLocaleString("en-IN", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export function fmtPoints(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return "—";
  const rounded = Math.round(Math.abs(value) * 100) / 100;
  return `${rounded === 0 ? "" : value < 0 ? "−" : "+"}${fmtLevel(rounded)}`;
}

export function fmtInr(n: number, compact = false): string {
  if (n == null || !Number.isFinite(n)) return "—";
  const sign = n < 0 ? "−" : "";
  const a = Math.abs(n);
  // Indian market scale: L Cr (1e12) / K Cr (1e10) / Cr (1e7) / L (1e5)
  if (a >= 1e12) {
    const v = a / 1e12;
    return `${sign}₹${v.toFixed(compact ? 1 : 2)} L Cr`;
  }
  if (a >= 1e10) {
    const v = a / 1e7; // crores
    return `${sign}₹${v.toFixed(0)} Cr`;
  }
  if (a >= 1e7) {
    return `${sign}₹${(a / 1e7).toFixed(compact ? 0 : 1)} Cr`;
  }
  if (a >= 1e5) {
    return `${sign}₹${(a / 1e5).toFixed(compact ? 0 : 1)} L`;
  }
  return `${sign}₹${a.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

/** Short axis tick — keep under ~8 chars so labels don't clip. */
export function fmtInrAxis(n: number): string {
  if (!Number.isFinite(n)) return "";
  const sign = n < 0 ? "−" : "";
  const a = Math.abs(n);
  if (a >= 1e12) return `${sign}${(a / 1e12).toFixed(1)}LCr`;
  if (a >= 1e7) {
    const cr = a / 1e7;
    if (cr >= 1000) return `${sign}${(cr / 1000).toFixed(1)}KCr`;
    return `${sign}${cr.toFixed(cr >= 100 ? 0 : 1)}Cr`;
  }
  if (a >= 1e5) return `${sign}${(a / 1e5).toFixed(0)}L`;
  if (a >= 1e3) return `${sign}${(a / 1e3).toFixed(0)}K`;
  return `${sign}${a.toFixed(0)}`;
}

export function payoutCurveOption(
  params: {
    candidates: number[];
    call: number[];
    put: number[];
    total: number[];
    maxPain: number | null;
    spot: number | null;
  },
  visible?: {
    combined?: boolean;
    call?: boolean;
    put?: boolean;
    maxPain?: boolean;
    spot?: boolean;
  }
): EChartsOption {
  const { candidates, call, put, total, maxPain, spot } = params;
  const vis = {
    combined: visible?.combined !== false,
    call: visible?.call !== false,
    put: visible?.put !== false,
    maxPain: visible?.maxPain !== false,
    spot: visible?.spot !== false,
  };

  const ml: object[] = [];
  if (maxPain != null && vis.maxPain) {
    ml.push({
      xAxis: maxPain,
      label: { formatter: `Max Pain ${fmtLevel(maxPain, 0)}`, color: "#2DD4A8", position: "insideEndTop" },
      lineStyle: { color: "#2DD4A8", type: "dashed", width: 1.5 },
    });
  }
  if (spot != null && vis.spot) {
    ml.push({
      xAxis: spot,
      label: { formatter: `Spot ${fmtLevel(spot)}`, color: "#61AFEF", position: "insideStartTop" },
      lineStyle: { color: "#61AFEF", type: "dotted", width: 1.5 },
    });
  }

  return {
    backgroundColor: "transparent",
    animation: false,
    legend: {
      data: [
        ...(vis.combined ? ["Combined"] : []),
        ...(vis.call ? ["Call"] : []),
        ...(vis.put ? ["Put"] : []),
      ],
      type: "scroll",
      selectedMode: true,
      textStyle: { color: "#8B9AAB" },
      top: 0,
      left: 88,
      right: 24,
    },
    tooltip: {
      ...TOOLTIP,
      trigger: "axis",
      confine: true,
      axisPointer: { type: "line", lineStyle: { color: "#2DD4A8", width: 1 } },
      formatter: (raw: unknown) => {
        const items = raw as { value: [number, number | null]; seriesName: string }[];
        if (!items?.length) return "";
        const x = items[0].value[0];
        return [
          `<div style="font-weight:600;margin-bottom:4px">Settlement ${fmtLevel(x, 0)}</div>`,
          ...items.map((item) => `<div>${item.seriesName} payout: <b>${fmtInr(item.value[1] ?? NaN, true)}</b></div>`),
          spot != null
            ? `<div style="margin-top:4px;color:#8B9AAB">vs spot: ${fmtPoints(x - spot)} pts</div>`
            : "",
          maxPain != null
            ? `<div style="color:#2DD4A8">Max Pain strike: ${maxPain.toLocaleString("en-IN")}</div>`
            : "",
        ].join("");
      },
    },
    grid: { left: 88, right: 24, top: 44, bottom: 48 },
    xAxis: {
      type: "value",
      min: "dataMin",
      max: "dataMax",
      ...AXIS,
      axisLabel: {
        ...AXIS.axisLabel,
        hideOverlap: true,
        formatter: (v: number) => fmtLevel(v, 0),
      },
      name: "Settlement price",
      nameLocation: "middle",
      nameGap: 30,
      nameTextStyle: { color: "#8B9AAB" },
    },
    yAxis: {
      type: "value",
      ...AXIS,
      name: "Payout (₹)",
      nameLocation: "middle",
      nameGap: 64,
      nameTextStyle: { color: "#8B9AAB" },
      axisLabel: {
        ...AXIS.axisLabel,
        formatter: (v: number) => fmtInrAxis(v),
      },
    },
    series: [
      ...(vis.combined
        ? [
            {
              name: "Combined",
              type: "line" as const,
              data: candidates.map((price, i) => [price, total[i] ?? null]),
              showSymbol: false,
              z: 4,
              lineStyle: { color: "#E5C07B", width: 2.4 },
              itemStyle: { color: "#E5C07B" },
              markPoint: {
                symbol: "circle",
                symbolSize: 7,
                silent: true,
                itemStyle: { color: "#2DD4A8" },
                label: { show: false },
                data: [{ type: "min" as const, name: "Minimum payout" }],
              },
            },
          ]
        : []),
      ...(vis.call
        ? [
            {
              name: "Call",
              type: "line" as const,
              data: candidates.map((price, i) => [price, call[i] ?? null]),
              showSymbol: false,
              lineStyle: { color: "#E06C75", width: 1.5, type: "dashed" as const, opacity: 0.85 },
              itemStyle: { color: "#E06C75" },
            },
          ]
        : []),
      ...(vis.put
        ? [
            {
              name: "Put",
              type: "line" as const,
              data: candidates.map((price, i) => [price, put[i] ?? null]),
              showSymbol: false,
              lineStyle: { color: "#61AFEF", width: 1.5, type: "dashed" as const, opacity: 0.85 },
              itemStyle: { color: "#61AFEF" },
            },
          ]
        : []),
      {
        id: "payout-reference-levels",
        type: "line",
        data: [],
        silent: true,
        tooltip: { show: false },
        markLine: { silent: true, symbol: "none", data: ml as never },
      },
    ],
  };
}

export function oiChartOption(params: {
  strikes: number[];
  callOi: number[];
  putOi: number[];
  callPrev?: (number | null)[];
  putPrev?: (number | null)[];
  mode: "total" | "change" | "pct";
  maxPain: number | null;
  spot: number | null;
}): EChartsOption {
  const { strikes, callOi, putOi, callPrev, putPrev, mode, maxPain, spot } = params;
  const gaps = strikes.slice(1).map((strike, i) => strike - strikes[i]).filter((gap) => gap > 0);
  const padding = (gaps.length ? Math.min(...gaps) : 1) * 0.65;
  const levels = [...strikes, ...[maxPain, spot].filter((value): value is number => value != null && Number.isFinite(value))];

  const callVal = strikes.map((_, i) => {
    if (mode === "total") return callOi[i];
    const previous = callPrev?.[i];
    if (previous == null) return null;
    const ch = callOi[i] - previous;
    if (mode === "change") return ch;
    const base = callPrev?.[i] ?? 0;
    return base ? (ch / base) * 100 : null;
  });
  const putVal = strikes.map((_, i) => {
    if (mode === "total") return -putOi[i]; // mirrored
    const previous = putPrev?.[i];
    if (previous == null) return null;
    const ch = putOi[i] - previous;
    if (mode === "change") return -ch;
    const base = putPrev?.[i] ?? 0;
    return base ? -(ch / base) * 100 : null;
  });

  const ml: object[] = [];
  if (maxPain != null) {
    ml.push({
      xAxis: maxPain,
      label: { formatter: `Max Pain ${fmtLevel(maxPain, 0)}`, color: "#2DD4A8", position: "insideEndTop" },
      lineStyle: { color: "#2DD4A8", type: "dashed", width: 1.5 },
    });
  }
  if (spot != null) {
    ml.push({
      xAxis: spot,
      label: { formatter: `Spot ${fmtLevel(spot)}`, color: "#61AFEF", position: "insideStartBottom" },
      lineStyle: { color: "#61AFEF", type: "dotted", width: 1.5 },
    });
  }

  return {
    backgroundColor: "transparent",
    animation: false,
    legend: {
      data: ["Call OI", "Put OI (mirrored)"],
      textStyle: { color: "#8B9AAB" },
      top: 0,
      right: 8,
    },
    tooltip: {
      ...TOOLTIP,
      trigger: "axis",
      confine: true,
      axisPointer: { type: "shadow" },
      formatter: (raw: unknown) => {
        const items = raw as {
          axisValue: string;
          data: number;
          seriesName: string;
          dataIndex: number;
        }[];
        if (!items?.length) return "";
        const i = items[0].dataIndex;
        const s = strikes[i];
        const dist = spot != null ? s - spot : null;
        return [
          `<div style="font-weight:600">Strike ${s.toLocaleString("en-IN")}</div>`,
          `<div>Call OI: <b>${Math.abs(callOi[i]).toLocaleString("en-IN")}</b></div>`,
          `<div>Put OI: <b>${Math.abs(putOi[i]).toLocaleString("en-IN")}</b></div>`,
          callPrev?.[i] != null
            ? `<div>Δ Call: <b>${(callOi[i] - callPrev[i]!).toLocaleString("en-IN")}</b></div>`
            : "",
          putPrev?.[i] != null
            ? `<div>Δ Put: <b>${(putOi[i] - putPrev[i]!).toLocaleString("en-IN")}</b></div>`
            : "",
          mode === "pct" ? `<div>Δ Call %: <b>${callPrev?.[i] != null && callPrev[i]! > 0 ? `${fmtPoints((callOi[i] - callPrev[i]!) / callPrev[i]! * 100)}%` : "unavailable"}</b></div>` : "",
          mode === "pct" ? `<div>Δ Put %: <b>${putPrev?.[i] != null && putPrev[i]! > 0 ? `${fmtPoints((putOi[i] - putPrev[i]!) / putPrev[i]! * 100)}%` : "unavailable"}</b></div>` : "",
          dist != null
            ? `<div style="margin-top:4px;color:#8B9AAB">vs spot: ${dist >= 0 ? "+" : ""}${dist.toLocaleString("en-IN")} pts</div>`
            : "",
          s === maxPain ? `<div style="color:#2DD4A8">This is Max Pain</div>` : "",
        ].join("");
      },
    },
    grid: { left: 64, right: 24, top: 36, bottom: 48 },
    xAxis: {
      type: "value",
      min: Math.min(...levels) - padding,
      max: Math.max(...levels) + padding,
      ...AXIS,
      axisLabel: {
        ...AXIS.axisLabel,
        hideOverlap: true,
        formatter: (v: number) => fmtLevel(v, 0),
      },
    },
    yAxis: {
      type: "value",
      ...AXIS,
      axisLabel: {
        ...AXIS.axisLabel,
        formatter: (v: number) => {
          const a = Math.abs(v);
          const sign = mode === "total" || v === 0 ? "" : v < 0 ? "−" : "+";
          if (mode === "pct") return `${sign}${a.toFixed(0)}%`;
          if (a >= 1e6) return `${sign}${(a / 1e6).toFixed(1)}M`;
          if (a >= 1e3) return `${sign}${(a / 1e3).toFixed(0)}K`;
          return `${sign}${a}`;
        },
      },
    },
    series: [
      {
        name: "Call OI",
        type: "bar",
        data: strikes.map((strike, i) => [strike, callVal[i]]),
        barMaxWidth: 14,
        itemStyle: { color: "#E06C75", borderRadius: [2, 2, 0, 0] },
      },
      {
        name: "Put OI (mirrored)",
        type: "bar",
        data: strikes.map((strike, i) => [strike, putVal[i]]),
        barMaxWidth: 14,
        itemStyle: { color: "#61AFEF", borderRadius: [0, 0, 2, 2] },
      },
      { id: "oi-reference-levels", type: "line", data: [], silent: true, tooltip: { show: false },
        markLine: { silent: true, symbol: "none", data: ml as never } },
    ],
  };
}

export function premiumPnlOption(params: {
  candidates: number[];
  series: { name: string; color: string; values: number[]; dashed?: boolean; primary?: boolean }[];
  maxPain: number | null;
  spot: number | null;
  extremePrice: number | null;
  extremeLabel: string;
  breakevens: number[];
}): EChartsOption {
  const { candidates, series, maxPain, spot, extremePrice, extremeLabel, breakevens } = params;
  const priceLabel = (value: number) => value.toLocaleString("en-IN", { maximumFractionDigits: 2 });
  const ml: object[] = [{
    yAxis: 0,
    label: { show: false },
    lineStyle: { color: "#8B9AAB", type: "solid", width: 1 },
  }];
  if (maxPain != null) {
    ml.push({
      xAxis: maxPain,
      label: { formatter: `Max Pain ${priceLabel(maxPain)}`, color: "#2DD4A8", position: "insideEndTop" },
      lineStyle: { color: "#2DD4A8", type: "dashed", width: 1.5 },
    });
  }
  if (spot != null) {
    ml.push({
      xAxis: spot,
      label: { formatter: `Spot ${priceLabel(spot)}`, color: "#61AFEF", position: "insideStartTop" },
      lineStyle: { color: "#61AFEF", type: "dotted", width: 1.5 },
    });
  }
  if (extremePrice != null) {
    ml.push({
      xAxis: extremePrice,
      label: {
        formatter: `${extremeLabel} ${priceLabel(extremePrice)}`,
        color: "#E5C07B",
        position: extremePrice === Math.min(...candidates) ? "insideEndBottom" : "insideEndTop",
      },
      lineStyle: { color: "#E5C07B", type: "dashed", width: 1.5 },
    });
  }
  for (const be of breakevens.slice(0, 4)) {
    ml.push({
      xAxis: be,
      label: { formatter: `BE ${priceLabel(be)}`, color: "#F07178", position: "middle" },
      lineStyle: { color: "#F07178", type: "dotted", width: 1 },
    });
  }

  return {
    backgroundColor: "transparent",
    animation: false,
    legend: {
      type: "scroll",
      data: series.map((s) => s.name),
      textStyle: { color: "#8B9AAB" },
      pageTextStyle: { color: "#8B9AAB" },
      pageIconColor: "#8B9AAB",
      top: 0,
      left: 88,
      right: 24,
    },
    tooltip: {
      ...TOOLTIP,
      trigger: "axis",
      confine: true,
      axisPointer: { type: "line", lineStyle: { color: "#2DD4A8" } },
      formatter: (raw: unknown) => {
        const items = raw as { axisValue: number; seriesName: string; value: [number, number | null] }[];
        if (!items?.length) return "";
        const rows = items
          .map((i) => `<div>${i.seriesName}: <b>${fmtInr(i.value[1] ?? NaN, true)}</b></div>`)
          .join("");
        return `<div style="font-weight:600;margin-bottom:4px">Settlement ${priceLabel(items[0].value[0])}</div>${rows}`;
      },
    },
    grid: { left: 88, right: 24, top: 44, bottom: 48 },
    xAxis: {
      type: "value",
      min: "dataMin",
      max: "dataMax",
      ...AXIS,
      name: "Settlement price",
      nameLocation: "middle",
      nameGap: 30,
      nameTextStyle: { color: "#8B9AAB" },
      axisLabel: {
        ...AXIS.axisLabel,
        hideOverlap: true,
        formatter: priceLabel,
      },
    },
    yAxis: {
      type: "value",
      ...AXIS,
      name: "P&L (₹)",
      nameLocation: "middle",
      nameGap: 64,
      nameTextStyle: { color: "#8B9AAB" },
      axisLabel: { ...AXIS.axisLabel, formatter: (v: number) => fmtInrAxis(v) },
    },
    series: [
      ...series.map((s) => ({
        name: s.name,
        type: "line" as const,
        data: candidates.map((price, i) => [price, s.values[i] ?? null]),
        showSymbol: false,
        lineStyle: {
          color: s.color,
          width: s.primary ? 2.2 : 1.5,
          type: s.dashed ? ("dashed" as const) : undefined,
        },
        itemStyle: { color: s.color },
      })),
      {
        // Keep reference levels independent of portfolio names and legend toggles.
        id: "premium-pnl-reference-levels",
        type: "line",
        data: [],
        silent: true,
        tooltip: { show: false },
        markLine: { silent: true, symbol: "none", data: ml as never },
      },
    ],
  };
}

export function intradayOption(params: {
  times: string[];
  maxPain: (number | null)[];
  spot: (number | null)[];
}): EChartsOption {
  const { times, maxPain, spot } = params;
  const dist = times.map((_, i) => {
    const m = maxPain[i];
    const s = spot[i];
    return m != null && s != null && Number.isFinite(m) && Number.isFinite(s) ? s - m : null;
  });

  return {
    backgroundColor: "transparent",
    animation: false,
    legend: {
      data: ["Max Pain", "Spot", "Spot − Max Pain"],
      type: "scroll",
      textStyle: { color: "#8B9AAB" },
      top: 0,
      left: 80,
      right: 24,
    },
    tooltip: {
      ...TOOLTIP,
      trigger: "axis",
      confine: true,
      axisPointer: { type: "line", lineStyle: { color: "#8B9AAB" } },
      formatter: (raw: unknown) => {
        const items = raw as {
          axisValue: string;
          seriesName: string;
          dataIndex: number;
        }[];
        if (!items?.length) return "";
        const i = items[0].dataIndex;
        return [
          `<div style="font-weight:600;margin-bottom:4px">${times[i]} IST</div>`,
          `<div>Max Pain: <b>${fmtLevel(maxPain[i])}</b></div>`,
          `<div>Spot: <b>${fmtLevel(spot[i])}</b></div>`,
          `<div style="margin-top:4px">Spot − Max Pain: <b>${fmtPoints(dist[i])}${dist[i] != null ? " pts" : ""}</b></div>`,
        ].join("");
      },
    },
    grid: [
      { left: 80, right: 24, top: 44, height: "48%" },
      { left: 80, right: 24, top: "70%", bottom: 42 },
    ],
    xAxis: [
      {
        type: "category",
        gridIndex: 0,
        data: times,
        ...AXIS,
        axisLabel: { show: false },
        axisPointer: { snap: true, label: { show: false } },
      },
      {
        type: "category",
        gridIndex: 1,
        data: times,
        ...AXIS,
        axisLine: { ...AXIS.axisLine, onZero: false },
        axisLabel: { ...AXIS.axisLabel, show: true, hideOverlap: true },
        axisPointer: { snap: true, label: { show: false } },
        name: "Time (IST)",
        nameLocation: "middle",
        nameGap: 26,
        nameTextStyle: { color: "#8B9AAB" },
      },
    ],
    yAxis: [
      {
        type: "value", gridIndex: 0, ...AXIS, scale: true,
        name: "Price", nameLocation: "middle", nameGap: 58,
        nameTextStyle: { color: "#8B9AAB" },
        axisLabel: { ...AXIS.axisLabel, formatter: (value: number) => fmtLevel(value, 0) },
      },
      {
        type: "value",
        gridIndex: 1,
        ...AXIS,
        name: "Gap (pts)",
        nameLocation: "middle",
        nameGap: 58,
        nameTextStyle: { color: "#8B9AAB" },
        splitNumber: 3,
        axisLabel: {
          ...AXIS.axisLabel,
          formatter: (v: number) => `${v > 0 ? "+" : ""}${fmtLevel(v, 0)}`,
        },
      },
    ],
    axisPointer: { link: [{ xAxisIndex: "all" }] },
    series: [
      {
        name: "Max Pain",
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: maxPain,
        step: "end",
        showSymbol: false,
        lineStyle: { color: "#2DD4A8", width: 2 },
        itemStyle: { color: "#2DD4A8" },
      },
      {
        name: "Spot",
        type: "line",
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: spot,
        showSymbol: false,
        lineStyle: { color: "#61AFEF", width: 1.8, type: "dashed" },
        itemStyle: { color: "#61AFEF" },
      },
      {
        name: "Spot − Max Pain",
        type: "bar",
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: dist.map((value) => ({
          value,
          itemStyle: { color: value == null ? "transparent" : value >= 0 ? "rgba(45,212,168,0.75)" : "rgba(240,113,120,0.75)" },
        })),
        itemStyle: { color: "#8B9AAB" },
        barMaxWidth: 28,
        markLine: { silent: true, symbol: "none", label: { show: false }, data: [{ yAxis: 0 }], lineStyle: { color: "#8B9AAB", type: "solid" } },
      },
    ],
  };
}

