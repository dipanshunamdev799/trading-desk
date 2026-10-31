import type { HistoricalPremiumPrices } from "@/lib/api";

const price = new Intl.NumberFormat("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default function HistoricalPremiumCoverage({ prices }: { prices?: HistoricalPremiumPrices | null }) {
  if (!prices?.carried_forward) return null;
  return (
    <div className="historical-premium-coverage" style={{ border: "1px solid var(--border)", borderRadius: 8, padding: "10px 14px", marginBottom: 14 }}>
      <div style={{ fontSize: 13, marginBottom: 4 }}>
        <strong>{prices.available}/{prices.required} premiums available</strong>
        <span className="muted"> · {prices.exact} session closes · </span>
        <span style={{ color: "var(--warn)" }}>{prices.carried_forward} carried forward</span>
      </div>
      <p className="muted" style={{ margin: "4px 0 8px", fontSize: 12, lineHeight: 1.5 }}>
        These options had no traded close on {prices.date}. P&amp;L uses their last available traded close,
        with the original price date shown below. Price age is in calendar days.
      </p>
      <details open={prices.carried_forward <= 4}>
        <summary style={{ cursor: "pointer", fontSize: 12 }}>Inspect carried-forward prices ({prices.carried_forward})</summary>
        <div style={{ overflowX: "auto", marginTop: 8 }}>
          <table className="data">
            <thead><tr><th>Option</th><th>Premium</th><th>Price date (IST)</th><th>Age</th></tr></thead>
            <tbody>{prices.carried.map((leg) => (
              <tr key={`${leg.strike}-${leg.side}`}>
                <td>{leg.strike.toLocaleString("en-IN")} {leg.side}</td>
                <td className="mono">₹{price.format(leg.close)}</td>
                <td className="mono">{leg.price_date}</td>
                <td>{leg.age_days} {leg.age_days === 1 ? "day" : "days"}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
