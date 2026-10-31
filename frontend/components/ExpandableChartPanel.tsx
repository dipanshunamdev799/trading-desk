"use client";

import { createContext, useContext, useEffect, useId, useRef, useState, type ReactNode } from "react";
import type { ChartAsOfControl } from "@/lib/chartAsOf";

const ExpandedChartContext = createContext(false);

export function useExpandedChart() {
  return useContext(ExpandedChartContext);
}

export default function ExpandableChartPanel({ title, children, asOf, onExpandedChange }: {
  title: string; children: ReactNode; asOf?: ChartAsOfControl; onExpandedChange?: (expanded: boolean) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const dateId = useId();
  const expandedCallback = useRef(onExpandedChange);
  expandedCallback.current = onExpandedChange;
  const changeExpanded = (value: boolean) => { setExpanded(value); expandedCallback.current?.(value); };
  const panelRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!expanded) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        changeExpanded(false);
      } else if (event.key === "Tab") {
        const controls = Array.from(panelRef.current?.querySelectorAll<HTMLElement>(
          'button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), summary, [tabindex="0"]'
        ) ?? []).filter((element) => element.getClientRects().length > 0);
        const first = controls[0];
        const last = controls[controls.length - 1];
        if (!panelRef.current?.contains(document.activeElement)) {
          event.preventDefault();
          (event.shiftKey ? last : first)?.focus();
        } else if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }
    }
    document.addEventListener("keydown", handleKeyDown, true);
    return () => {
      document.removeEventListener("keydown", handleKeyDown, true);
      document.body.style.overflow = previousOverflow;
      buttonRef.current?.focus({ preventScroll: true });
    };
  }, [expanded]);

  return (
    <ExpandedChartContext.Provider value={expanded}>
      <div ref={panelRef} className={`panel expandable-chart-panel${expanded ? " is-maximized" : ""}`}
        role={expanded ? "dialog" : undefined} aria-modal={expanded ? true : undefined}
        aria-label={expanded ? title : undefined}>
        <button ref={buttonRef} type="button" className="chart-size-button"
          aria-label={`${expanded ? "Restore" : "Maximize"} ${title}`}
          title={expanded ? "Restore chart (Esc)" : "Maximize chart"}
          aria-expanded={expanded} onClick={() => changeExpanded(!expanded)}>
          <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
            {expanded ? <path d="M2 7h5V2m11 5h-5V2M2 13h5v5m11-5h-5v5" />
              : <path d="M7 2H2v5m11-5h5v5M2 13v5h5m11-5v5h-5" />}
          </svg>
          <span>{expanded ? "Restore" : "Maximize"}</span>
        </button>
        {expanded && asOf && <div className="chart-asof-controls">
          <label htmlFor={dateId}>As of (this chart, IST)</label>
          <select id={dateId} value={asOf.value} onChange={event => asOf.onChange(event.target.value)}>
            <option value="">Main date · {asOf.mainDate || "checking session…"}</option>
            {asOf.dates.map(day => <option key={day} value={day}>{day}</option>)}
          </select>
          <span className="muted">Changes only this chart · trading sessions; data availability varies</span>
        </div>}
        {children}
      </div>
    </ExpandedChartContext.Provider>
  );
}
