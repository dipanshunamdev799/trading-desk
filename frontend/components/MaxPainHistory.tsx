import { fmtLevel, fmtPoints } from "@/components/maxpainCharts";
import type { MaxPainHistoryPoint } from "@/lib/api";

function distanceTone(value: number | null): string {
  return value == null || !Number.isFinite(value) || value === 0 ? "muted" : value > 0 ? "pos" : "neg";
}

export default function MaxPainHistory({ points, loading, error, asOf }: {
  points: MaxPainHistoryPoint[];
  loading: boolean;
  error: string | null;
  asOf?: string;
}) {
  const rows = [...points].sort((a, b) =>
    b.obs_date.localeCompare(a.obs_date) || b.obs_time.localeCompare(a.obs_time) || a.expiry.localeCompare(b.expiry)
  );

  return (
    <section className="panel maxpain-history" aria-labelledby="maxpain-history-title" aria-busy={loading}>
      <div className="panel-header">
        <div>
          <h2 id="maxpain-history-title">Historical snapshots</h2>
          <p className="maxpain-caption">{asOf ? `Available sessions through ${asOf} · ` : ""}Latest first · prices to 2 decimals · times in IST</p>
        </div>
        <span className={`badge ${loading ? "warn" : "db"}`}>
          {loading ? "Loading…" : `${rows.length} snapshot${rows.length === 1 ? "" : "s"}`}
        </span>
      </div>
      {error ? (
        <div className="panel-body"><div className="error-box">{error}</div></div>
      ) : rows.length ? (
        <>
          <div className="table-wrap">
            <table className="data" aria-label="Historical Max Pain snapshots">
              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Time (IST)</th>
                  <th scope="col">Expiry</th>
                  <th scope="col">Type</th>
                  <th scope="col" className="num">Spot</th>
                  <th scope="col" className="num">Max Pain</th>
                  <th scope="col" className="num">Spot − MP (pts)</th>
                  <th scope="col" className="num">Close</th>
                  <th scope="col" className="num">Close − MP (pts)</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => {
                  const gap = Number.isFinite(row.spot) && Number.isFinite(row.max_pain) ? row.spot - row.max_pain : null;
                  const closeGap = row.expiry_close != null && Number.isFinite(row.expiry_close) && Number.isFinite(row.max_pain)
                    ? row.expiry_close - row.max_pain : null;
                  return (
                    <tr key={`${row.expiry}-${row.obs_date}-${row.obs_time}-${row.kind}-${index}`}>
                      <td className="mono"><time dateTime={row.obs_date}>{row.obs_date}</time></td>
                      <td className="mono muted">{row.obs_time}</td>
                      <td className="mono muted">{row.expiry}</td>
                      <td><span className={`badge ${row.kind === "settlement" ? "warn" : "db"}`}>
                        {row.kind === "settlement" ? "Settlement" : row.kind === "session" ? "Session" : row.kind}
                      </span></td>
                      <td className="num">{fmtLevel(row.spot)}</td>
                      <td className="num">{fmtLevel(row.max_pain)}</td>
                      <td className={`num ${distanceTone(gap)}`}>{fmtPoints(gap)}</td>
                      <td className="num">{fmtLevel(row.expiry_close)}</td>
                      <td className={`num ${distanceTone(closeGap)}`}>{fmtPoints(closeGap)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="maxpain-table-note">MP = Max Pain. Close is the session close for session rows and the expiry-day close for settlement rows. Signed distances show points above (+) or below (−) Max Pain.</p>
        </>
      ) : (
        <div className="empty-note">{loading ? "Loading historical snapshots…" : "No historical snapshots for this selection."}</div>
      )}
    </section>
  );
}
