import type { EChartsOption } from "./EChartPanel";
import type { StudyGroup } from "@/lib/maxpainResearch";

export function chainConvergenceOption(group: StudyGroup): EChartsOption {
  return {
    animation: false, grid: { left: 50, right: 24, top: 42, bottom: 75 },
    legend: { top: 0, textStyle: { color: "#AAB8C7" } },
    tooltip: { trigger: "axis", confine: true },
    xAxis: { type: "category", data: group.by_asset.map(row => `${row.symbol}\nn=${row.n}`),
      axisLabel: { color: "#AAB8C7", fontSize: 10, interval: 0, rotate: 25 }, axisTick: { show: false } },
    yAxis: { type: "value", min: 0, max: 100, axisLabel: { color: "#AAB8C7", formatter: "{value}%" }, splitLine: { lineStyle: { color: "#243041" } } },
    series: [
      { name: "Frozen Max Pain", type: "bar", itemStyle: { color: "#B89AE8", borderRadius: [3, 3, 0, 0] }, data: group.by_asset.map(row => row.closer_rate), barMaxWidth: 30 },
      { name: "Opposite target control", type: "bar", itemStyle: { color: "#68788A", borderRadius: [3, 3, 0, 0] }, data: group.by_asset.map(row => row.mirror_rate), barMaxWidth: 30 },
    ],
  };
}

export function monthlyConvergenceOption(group: StudyGroup): EChartsOption {
  return {
    animation: false, grid: { left: 50, right: 24, top: 40, bottom: 45 },
    legend: { top: 0, textStyle: { color: "#AAB8C7" } }, tooltip: { trigger: "axis", confine: true },
    xAxis: { type: "category", data: group.by_month.map(row => `${row.month}\nn=${row.n}`), axisLabel: { color: "#AAB8C7", fontSize: 10 }, axisTick: { show: false } },
    yAxis: { type: "value", min: 0, max: 100, axisLabel: { color: "#AAB8C7", formatter: "{value}%" }, splitLine: { lineStyle: { color: "#243041" } } },
    series: [
      { name: "Frozen Max Pain", type: "line", data: group.by_month.map(row => row.closer_rate), itemStyle: { color: "#B89AE8" }, connectNulls: false, smooth: false },
      { name: "Opposite target control", type: "line", data: group.by_month.map(row => row.mirror_rate), itemStyle: { color: "#68788A" }, lineStyle: { type: "dashed" }, connectNulls: false, smooth: false },
    ],
  };
}
