"use client";

import { useState } from "react";

export type ChartAsOfControl = {
  mainDate: string; dates: string[]; value: string; onChange: (date: string) => void;
};

export function useChartAsOf(mainDate: string, dates: string[]) {
  const [expanded, setExpanded] = useState(false);
  const [selected, setSelected] = useState("");
  const independent = expanded && selected !== "";
  return {
    date: independent ? selected : mainDate,
    independent,
    control: { mainDate, dates, value: selected, onChange: setSelected } satisfies ChartAsOfControl,
    onExpandedChange: (value: boolean) => { setExpanded(value); if (!value) setSelected(""); },
  };
}
