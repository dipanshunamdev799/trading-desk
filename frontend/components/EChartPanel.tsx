"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts";
import { useExpandedChart } from "@/components/ExpandableChartPanel";

export type EChartsOption = echarts.EChartsOption;

export default function EChartPanel({
  option,
  height = 320,
  onClick,
}: {
  option: EChartsOption;
  height?: number;
  onClick?: (params: { dataIndex: number; name?: string; value?: unknown }) => void;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  const expanded = useExpandedChart();
  const chartRef = useRef<echarts.ECharts | null>(null);
  const legendRef = useRef<Record<string, boolean>>({});
  const clickRef = useRef(onClick);
  clickRef.current = onClick;

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let chart = chartRef.current;
    if (!chart) {
      chart = echarts.init(el, undefined, { renderer: "canvas" });
      chartRef.current = chart;
      chart.on("click", (params) => {
        const p = params as { dataIndex: number; name?: string; value?: unknown };
        clickRef.current?.({ dataIndex: p.dataIndex, name: p.name, value: p.value });
      });
      chart.on("legendselectchanged", (params) => {
        legendRef.current = (params as { selected: Record<string, boolean> }).selected;
      });
    }
    const legend = option.legend == null ? undefined : Array.isArray(option.legend)
      ? option.legend.map((entry) => ({ ...entry, selected: { ...legendRef.current, ...entry.selected } }))
      : { ...option.legend, selected: { ...legendRef.current, ...option.legend.selected } };
    chart.setOption({ ...option, legend }, true);
    chart.resize({ width: el.clientWidth, height: el.clientHeight });

    const ro = new ResizeObserver(() => {
      if (ref.current && chartRef.current) {
        chartRef.current.resize({ width: ref.current.clientWidth, height: ref.current.clientHeight });
      }
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [option, height]);

  useEffect(() => {
    return () => {
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, []);

  return <div ref={ref} className="echart-container" style={{ width: "100%", height: expanded ? "100%" : height }} />;
}
