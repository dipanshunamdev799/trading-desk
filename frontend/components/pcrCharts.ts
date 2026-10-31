import type { EChartsOption } from "./EChartPanel";
import type { PcrPoint } from "@/lib/api";

const clock = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", hour12: false });
export const formatPcr = (value: number | null | undefined, digits = 3) => value == null || !Number.isFinite(value) ? "—" : value.toFixed(digits);
const valid = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value) && value >= 0;

export function pcrTimeline(asOf: string, points: PcrPoint[], streamed: PcrPoint[] = []) {
  const rows = new Map<string, PcrPoint>();
  for (const point of points) {
    if (/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(point.time)) rows.set(point.time, { ...point, pcr: valid(point.pcr) ? point.pcr : null,
      volume_pcr: valid(point.volume_pcr) ? point.volume_pcr : null });
  }
  const lastProvider = [...rows.keys()].sort().at(-1) || "";
  for (const point of streamed) {
    if (/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(point.time) && point.time >= lastProvider && (valid(point.pcr) || valid(point.spot) && point.spot > 0)) {
      const previous = rows.get(point.time);
      rows.set(point.time, { ...previous, ...point,
        pcr: valid(point.pcr) ? point.pcr : previous?.pcr ?? null,
        spot: valid(point.spot) && point.spot > 0 ? point.spot : previous?.spot ?? null,
        source: valid(point.pcr) ? point.source : previous?.source,
      });
    }
  }
  const dated = [...rows.values()].map(point => ({ ...point, at: Date.parse(`${asOf}T${point.time}:00+05:30`) }))
    .filter(point => Number.isFinite(point.at)).sort((a, b) => a.at - b.at);
  if (!dated.length) return [];
  const byTime = new Map(dated.map(point => [point.at, point]));
  const result = [];
  for (let at = dated[0].at; at <= dated[dated.length - 1].at; at += 60_000) {
    result.push(byTime.get(at) || { time: clock.format(new Date(at)), at, pcr: null, volume_pcr: null, spot: null });
  }
  return result;
}

export function pcrChartOption(asOf: string, points: PcrPoint[], streamed: PcrPoint[] = [], spotLabel = "Nifty 50"): EChartsOption {
  const rows = pcrTimeline(asOf, points, streamed);
  const values = rows.map(point => point.pcr).filter(valid);
  const volumeValues = rows.map(point => point.volume_pcr).filter(valid);
  const spotName = `${spotLabel} spot`;
  const spotValues = rows.map(point => point.spot).filter(value => valid(value) && value > 0);
  const min = Math.max(0, Math.floor(Math.min(1, ...values, ...volumeValues) * 20) / 20 - .03);
  const max = Math.ceil(Math.max(1, ...values, ...volumeValues) * 20) / 20 + .03;
  const segments = rows.slice(1).flatMap((row, index) => {
    const previous = rows[index];
    return valid(previous.pcr) && valid(row.pcr)
      ? [[previous.at, previous.pcr, row.at, row.pcr, Math.sign(row.pcr - previous.pcr)]] : [];
  });
  const volumeSegments = rows.slice(1).flatMap((row, index) => {
    const previous = rows[index];
    return valid(previous.volume_pcr) && valid(row.volume_pcr)
      ? [[previous.at, previous.volume_pcr, row.at, row.volume_pcr, Math.sign(row.volume_pcr - previous.volume_pcr)]] : [];
  });
  return {
    animation: false,
    grid: { left: 58, right: 88, top: 56, bottom: 50 },
    legend: { top: 4, right: 16, textStyle: { color: "#AAB8C7" },
      data: ["PCR (OI)", "PCR (volume)", spotName] },
    tooltip: { trigger: "axis", confine: true, backgroundColor: "#121820", borderColor: "#243041",
      textStyle: { color: "#E8EDF2" }, formatter: (raw: unknown) => {
        const index = (Array.isArray(raw) ? raw[0] : raw) as { dataIndex?: number } | undefined;
        const row = index?.dataIndex == null ? null : rows[index.dataIndex];
        if (!row) return "";
        return `${asOf} · ${row.time} IST<br/><b>OI PCR: ${formatPcr(row.pcr, 4)}</b><br/><b>Volume PCR: ${formatPcr(row.volume_pcr, 4)}</b>${valid(row.call_volume) && valid(row.put_volume) ? `<br/>Call / Put volume: ${row.call_volume.toLocaleString("en-IN")} / ${row.put_volume.toLocaleString("en-IN")}` : ""}<br/>Spot: ${valid(row.spot) && row.spot > 0 ? row.spot.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "—"}${row.source === "websocket" ? "<br/>OI PCR calculated from streamed OI" : ""}${valid(row.volume_pcr) ? `<br/>Volume is cumulative for the session${row.volume_source === "mixed_capture" ? " · mixed REST/feed capture" : row.volume_source === "websocket_capture" ? " · live feed capture" : " · saved REST capture"}` : ""}`;
      } },
    xAxis: { type: "time", min: rows.length === 1 ? rows[0].at - 60_000 : rows[0]?.at,
      max: rows.length === 1 ? rows[0].at + 60_000 : rows[rows.length - 1]?.at,
      axisLabel: { color: "#8B9AAB", hideOverlap: true, formatter: (value: number) => clock.format(new Date(value)) },
      axisLine: { lineStyle: { color: "#243041" } }, splitLine: { show: false }, axisTick: { show: false } },
    yAxis: [{ type: "value", min, max, name: "Put / Call ratio", nameTextStyle: { color: "#8B9AAB", align: "left" },
      axisLabel: { color: "#8B9AAB", formatter: (value: number) => value.toFixed(2) },
      splitLine: { lineStyle: { color: "#1A2330" } } },
      { type: "value", position: "right", scale: true, name: "Spot price", nameTextStyle: { color: "#61AFEF" },
        axisLabel: { color: "#61AFEF", formatter: (value: number) => value.toLocaleString("en-IN", { maximumFractionDigits: 2 }) },
        splitLine: { show: false } }],
    series: [{ name: "PCR (OI)", type: "line", smooth: false, connectNulls: false,
      showSymbol: values.length <= 1, symbolSize: 7, data: rows.map(row => [row.at, row.pcr]),
      lineStyle: { width: 0 }, itemStyle: { color: "#8B9AAB" },
      markLine: { silent: true, symbol: "none", lineStyle: { color: "#8B9AAB", type: "dashed", width: 1 },
        label: { formatter: "PCR 1.00 · equal put/call", position: "insideEndTop", color: "#AAB8C7" }, data: [{ yAxis: 1 }] },
    }, {
      name: "PCR (OI)", type: "custom", silent: true, clip: true,
      tooltip: { show: false }, encode: { x: [0, 2], y: [1, 3] }, data: segments,
      renderItem: (_params, api) => {
        const start = api.coord([api.value(0), api.value(1)]);
        const end = api.coord([api.value(2), api.value(3)]);
        const slope = Number(api.value(4));
        return { type: "line", shape: { x1: start[0], y1: start[1], x2: end[0], y2: end[1] },
          style: { stroke: slope > 0 ? "#20C997" : slope < 0 ? "#EF6672" : "#8B9AAB", lineWidth: 2.5 } };
      },
    }, {
      name: spotName, type: "line", yAxisIndex: 1, smooth: false, connectNulls: false,
      showSymbol: spotValues.length <= 1, symbolSize: 7,
      data: rows.map(row => [row.at, valid(row.spot) && row.spot > 0 ? row.spot : null]),
      lineStyle: { color: "#61AFEF", width: 2 }, itemStyle: { color: "#61AFEF" },
    }, {
      name: "PCR (volume)", type: "line", smooth: false, connectNulls: false,
      showSymbol: true, symbol: "diamond", symbolSize: 4, data: rows.map(row => [row.at, row.volume_pcr]),
      lineStyle: { width: 0 }, itemStyle: { color: "#E5C07B" },
    }, {
      name: "PCR (volume)", type: "custom", silent: true, clip: true,
      tooltip: { show: false }, encode: { x: [0, 2], y: [1, 3] }, data: volumeSegments,
      renderItem: (_params, api) => {
        const start = api.coord([api.value(0), api.value(1)]);
        const end = api.coord([api.value(2), api.value(3)]);
        const slope = Number(api.value(4));
        return { type: "line", shape: { x1: start[0], y1: start[1], x2: end[0], y2: end[1] },
          style: { stroke: slope > 0 ? "#20C997" : slope < 0 ? "#EF6672" : "#8B9AAB", lineWidth: 2.5, lineDash: [5, 4] } };
      },
    }],
  };
}
