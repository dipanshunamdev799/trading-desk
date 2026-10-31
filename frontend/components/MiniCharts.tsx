"use client";

function finite(values: number[]): number[] {
  return values.filter((v) => Number.isFinite(v));
}

function scaleTo(values: number[], height: number, pad = 10) {
  const vals = finite(values);
  if (!vals.length) return () => height / 2;
  const min = Math.min(...vals);
  const max = Math.max(...vals);
  const span = max - min || Math.abs(max) || 1;
  return (v: number) => height - pad - ((v - min) / span) * (height - pad * 2);
}

export function LineChart({
  series,
  height = 220,
  labels,
  yFormat,
  legend = true,
  vlines,
  highlight,
  xValues,
}: {
  series: { name: string; color: string; values: number[]; dashed?: boolean }[];
  height?: number;
  labels?: string[];
  yFormat?: (v: number) => string;
  legend?: boolean;
  /** Vertical reference lines (max pain, spot, …) in x-value space */
  vlines?: { x: number; color: string; label: string; dashed?: boolean }[];
  /** Scatter marker, e.g. min-payout at max pain */
  highlight?: { x: number; y: number; color: string } | null;
  /** Actual x-axis values (strike prices) for vlines/highlight */
  xValues?: number[];
}) {
  const width = 720;
  const n = Math.max(...series.map((s) => s.values.length), 0);
  if (!series.length || n === 0) {
    return (
      <div className="chart-empty" style={{ height }}>
        No series
      </div>
    );
  }

  const all = series.flatMap((s) => finite(s.values));
  if (!all.length) {
    return (
      <div className="chart-empty" style={{ height }}>
        No finite points
      </div>
    );
  }

  const plotH = height - (legend ? 18 : 0);
  const toY = scaleTo(all, plotH);
  const toX = (i: number) => 48 + (i / Math.max(1, n - 1)) * (width - 64);
  const min = Math.min(...all);
  const max = Math.max(...all);

  const xToPix = (xVal: number) => {
    if (!xValues || !xValues.length) return toX(0);
    // map continuous x (strike) onto index space
    const x0 = xValues[0];
    const x1 = xValues[xValues.length - 1];
    if (x1 === x0) return toX(0);
    const t = (xVal - x0) / (x1 - x0);
    return 48 + t * (width - 64);
  };

  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", height }} role="img">
      {[0, 0.25, 0.5, 0.75, 1].map((t) => {
        const y = 10 + t * (plotH - 20);
        return (
          <line key={t} x1={48} x2={width - 16} y1={y} y2={y} stroke="#243041" strokeWidth={0.6} />
        );
      })}

      {(vlines || []).map((v) => {
        const x = xToPix(v.x);
        return (
          <g key={v.label}>
            <line
              x1={x}
              x2={x}
              y1={10}
              y2={plotH - 16}
              stroke={v.color}
              strokeWidth={1.5}
              strokeDasharray={v.dashed ? "5 4" : undefined}
            />
            <text x={x + 4} y={18} fill={v.color} fontSize={11}>
              {v.label}
            </text>
          </g>
        );
      })}

      {series.map((s) => {
        const segs: string[] = [];
        let cur: string[] = [];
        s.values.forEach((v, i) => {
          if (Number.isFinite(v)) {
            cur.push(`${toX(i)},${toY(v)}`);
          } else if (cur.length) {
            segs.push(cur.join(" "));
            cur = [];
          }
        });
        if (cur.length) segs.push(cur.join(" "));
        return segs.map((pts, si) => (
          <polyline
            key={`${s.name}-${si}`}
            fill="none"
            stroke={s.color}
            strokeWidth={2}
            strokeDasharray={s.dashed ? "5 4" : undefined}
            points={pts}
            strokeLinejoin="round"
            strokeLinecap="round"
          />
        ));
      })}

      {highlight && Number.isFinite(highlight.y) && (
        <circle
          cx={xToPix(highlight.x)}
          cy={toY(highlight.y)}
          r={5}
          fill={highlight.color}
          stroke="#0B0F14"
          strokeWidth={1.5}
        />
      )}

      {labels &&
        labels.map((lab, i) =>
          i % Math.max(1, Math.ceil(n / 8)) === 0 && i < n ? (
            <text key={i} x={toX(i)} y={plotH - 4} fill="#8B9AAB" fontSize={11} textAnchor="middle">
              {lab}
            </text>
          ) : null
        )}

      {yFormat &&
        [0, 0.5, 1].map((t) => {
          const v = min + (1 - t) * (max - min);
          return (
            <text key={t} x={42} y={14 + t * (plotH - 24)} fill="#8B9AAB" fontSize={11} textAnchor="end">
              {yFormat(v)}
            </text>
          );
        })}

      {legend && (
        <g>
          {series.map((s, i) => (
            <g key={s.name} transform={`translate(${48 + i * 110}, ${height - 4})`}>
              <rect width={12} height={3} y={-8} fill={s.color} rx={1} />
              <text x={16} y={-2} fill="#8B9AAB" fontSize={11}>
                {s.name}
              </text>
            </g>
          ))}
        </g>
      )}
    </svg>
  );
}

export function BarPairChart({
  categories,
  left,
  right,
  leftColor = "#E06C75",
  rightColor = "#61AFEF",
  height = 220,
  leftLabel = "Call",
  rightLabel = "Put",
  markX,
  yFormat,
}: {
  categories: number[];
  left: number[];
  right: number[];
  leftColor?: string;
  rightColor?: string;
  height?: number;
  leftLabel?: string;
  rightLabel?: string;
  markX?: number | null;
  yFormat?: (v: number) => string;
}) {
  const width = 720;
  if (!categories.length) {
    return (
      <div className="chart-empty" style={{ height }}>
        No data
      </div>
    );
  }
  const maxAbs = Math.max(...left.map((v) => Math.abs(Number(v) || 0)), ...right.map((v) => Math.abs(Number(v) || 0)), 1);
  const mid = height / 2 - 8;
  const barW = Math.max(2, ((width - 64) / categories.length) * 0.42);
  const xAt = (i: number) => 48 + (i / categories.length) * (width - 72);

  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", height }} role="img">
      <line x1={40} x2={width - 16} y1={mid} y2={mid} stroke="#243041" />
      {categories.map((k, i) => {
        const hL = (Math.max(0, Number(left[i]) || 0) / maxAbs) * (mid - 20);
        const hR = (Math.max(0, Number(right[i]) || 0) / maxAbs) * (mid - 20);
        return (
          <g key={k}>
            <rect x={xAt(i) - barW} y={mid - hL} width={barW} height={hL} fill={leftColor} opacity={0.9} />
            <rect x={xAt(i)} y={mid} width={barW} height={hR} fill={rightColor} opacity={0.9} />
          </g>
        );
      })}
      {markX != null &&
        (() => {
          const min = categories[0];
          const max = categories[categories.length - 1];
          const x = 48 + ((markX - min) / Math.max(1, max - min)) * (width - 72);
          return (
            <>
              <line x1={x} x2={x} y1={12} y2={height - 28} stroke="#2DD4A8" strokeDasharray="4 3" strokeWidth={1.5} />
              <text x={x + 4} y={18} fill="#2DD4A8" fontSize={11}>
                max pain
              </text>
            </>
          );
        })()}
      {categories.map((k, i) =>
        i % Math.max(1, Math.ceil(categories.length / 10)) === 0 ? (
          <text key={`t${k}`} x={xAt(i)} y={height - 8} fill="#8B9AAB" fontSize={11} textAnchor="middle">
            {Math.round(k)}
          </text>
        ) : null
      )}
      <text x={48} y={16} fill={leftColor} fontSize={11}>
        {leftLabel} ↑
      </text>
      <text x={48} y={height - 28} fill={rightColor} fontSize={11}>
        {rightLabel} ↓
      </text>
      {yFormat && (
        <text x={width - 16} y={16} fill="#8B9AAB" fontSize={11} textAnchor="end">
          peak {yFormat(maxAbs)}
        </text>
      )}
    </svg>
  );
}
