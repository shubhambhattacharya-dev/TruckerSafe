import { useState } from "react";
import type { RoutePlanRequest, RoutePlanResponse } from "../types";
import { BAND_COLORS, BAND_LABELS } from "../map/colors";
import { fmtEta, fmtMiles } from "../util/format";
import CheckpointTable from "./CheckpointTable";
import ExplainerPanel from "./ExplainerPanel";

type Tab = "overview" | "checkpoints" | "weather" | "summary";

interface Props {
  plan: RoutePlanResponse;
  request: RoutePlanRequest;
  selectedId: number;
  onSelectRoute: (id: number) => void;
  onViewOnMap: () => void;
}

const ShieldIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
    <path d="M12 3l7 3v5c0 4.5-3 8.5-7 10-4-1.5-7-5.5-7-10V6z" />
  </svg>
);
const MapIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
    <path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2zM9 4v14M15 6v14" />
  </svg>
);
const LinkIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
    <path d="M10 14a5 5 0 0 0 7 0l2-2a5 5 0 0 0-7-7l-1 1" />
    <path d="M14 10a5 5 0 0 0-7 0l-2 2a5 5 0 0 0 7 7l1-1" />
  </svg>
);

export default function DetailTabs({ plan, request, selectedId, onSelectRoute, onViewOnMap }: Props) {
  const [tab, setTab] = useState<Tab>("checkpoints");
  const [allExpanded, setAllExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const selected = plan.routes.find((r) => r.id === selectedId) ?? plan.routes[0];
  const departure = new Date(request.departure_time);

  const copyLink = async () => {
    const url = `${window.location.origin}${window.location.pathname}?origin=${encodeURIComponent(request.origin)}&destination=${encodeURIComponent(request.destination)}&load=${request.load_lb}&interval=${request.checkpoint_interval_miles}`;
    try {
      await navigator.clipboard.writeText(url);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = url;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
    }
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  };

  const ProgressCard = () => {
    const reached = selected.checkpoints.filter((c) => new Date(c.eta) <= new Date()).length;
    return (
      <div className="card progress-card">
        <h4>Route {selected.id} Progress</h4>
        <div className="prog-track"><span className="fill" style={{ width: `${(reached / Math.max(1, selected.checkpoints.length - 1)) * 100}%` }} /></div>
        <div className="prog-frac">{reached} / {Math.round(selected.summary.distance_mi)} mi</div>
        <div className="prog-row"><span className="ic">📍</span><span><span className="k">Total Distance</span><br /><span className="v">{fmtMiles(selected.summary.distance_mi)}</span></span></div>
        <div className="prog-row"><span className="ic">🕐</span><span><span className="k">Estimated Arrival</span><br /><span className="v">{fmtEta(selected.summary.eta)}</span><br /><span className="s">({selected.summary.duration_min >= 60 ? `${Math.floor(selected.summary.duration_min / 60)} h ${Math.round(selected.summary.duration_min % 60)} m` : `${Math.round(selected.summary.duration_min)} m`})</span></span></div>
        <div className="prog-row"><span className="ic">📍</span><span><span className="k">Checkpoints</span><br /><span className="v">{selected.checkpoints.length} (every {request.checkpoint_interval_miles} miles)</span></span></div>
        <div className="prog-row"><span className="ic" style={{ color: BAND_COLORS[selected.disqualified ? "NO_TRAVEL" : "LOW"] }}>{ShieldIcon()}</span><span><span className="k">Average Risk</span><br /><span className="v" style={{ color: selected.disqualified ? BAND_COLORS.NO_TRAVEL : BAND_COLORS.LOW }}>{selected.disqualified ? "No Travel" : BAND_LABELS.LOW}</span></span></div>
        <div className="prog-row"><span className="ic">🚩</span><span><span className="k">Departure</span> · {request.origin} · {departure.toLocaleString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" })}</span></div>
        <div className="prog-row"><span className="ic">🏁</span><span><span className="k">Destination</span> · {request.destination} · {fmtEta(selected.summary.eta)}</span></div>
      </div>
    );
  };

  return (
    <section className="details">
      <div className="tab-bar" role="tablist">
        <button role="tab" aria-selected={tab === "overview"} className={tab === "overview" ? "active" : ""} onClick={() => setTab("overview")}>Route Overview</button>
        <button role="tab" aria-selected={tab === "checkpoints"} className={tab === "checkpoints" ? "active" : ""} onClick={() => setTab("checkpoints")}>Checkpoints (Route {selected.id})</button>
        <button role="tab" aria-selected={tab === "weather"} className={tab === "weather" ? "active" : ""} onClick={() => setTab("weather")}>Weather Details</button>
        <button role="tab" aria-selected={tab === "summary"} className={tab === "summary" ? "active" : ""} onClick={() => setTab("summary")}>Summary</button>
        <div className="tab-actions">
          <button className="btn-ghost" onClick={onViewOnMap}><MapIcon /> View on Map</button>
          <button className="btn-ghost" onClick={copyLink}><LinkIcon /> {copied ? "Copied!" : "Copy Trip Link"}</button>
          <button className="btn-ghost" onClick={() => setAllExpanded((v) => !v)}>{allExpanded ? "⌃ Collapse All" : "⌄ Expand All"} ({selected.checkpoints.length})</button>
        </div>
      </div>

      <div className="tab-body" role="tabpanel">
        {tab === "overview" && (
          <>
            <ProgressCard />
            <div className="table-wrap">
              <h4>All Routes — ranked by the algorithm (fewest severe miles, then high, then risk, then time)</h4>
              <table>
                <thead>
                  <tr><th>Rank</th><th>Route</th><th>Distance</th><th>ETA</th><th>Avg risk</th><th>Severe mi</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {plan.routes.map((r) => (
                    <tr key={r.id} className="expandable" onClick={() => onSelectRoute(r.id)} style={{ cursor: "pointer", background: r.id === selectedId ? "#f8fafc" : undefined }}>
                      <td><b>{r.id === plan.recommended_route_id ? "① Recommended" : r.id}</b></td>
                      <td>Route {r.id}{r.route_name ? ` — ${r.route_name}` : ""}</td>
                      <td>{fmtMiles(r.summary.distance_mi)}</td>
                      <td>{fmtEta(r.summary.eta)}</td>
                      <td>{r.risk.avg_score.toFixed(1)}</td>
                      <td>{Math.round(r.risk.severe_mi)}</td>
                      <td>{r.disqualified ? <span className="chip purple">Disqualified</span> : r.id === plan.recommended_route_id ? <span className="chip green">Recommended</span> : <span className="chip outline">Qualified</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        {tab === "checkpoints" && (
          <>
            <ProgressCard />
            <CheckpointTable checkpoints={selected.checkpoints} intervalMi={request.checkpoint_interval_miles} allExpanded={allExpanded} />
          </>
        )}

        {tab === "weather" && (
          <div style={{ width: "100%" }}>
            <h4 style={{ margin: "0 0 10px" }}>Weather at Estimated Arrival Times — Route {selected.id}</h4>
            <div className="wx-grid">
              {selected.checkpoints.slice(0, 24).map((cp) => (
                <div className="wx-card" key={cp.idx}>
                  <div className="loc">{cp.idx}. {cp.location_name}</div>
                  <div className="eta">{fmtEta(cp.eta)} · {Math.round(cp.distance_mi)} mi</div>
                  <div className="wx-chips">
                    <span className="wx-chip">🌬 {cp.wind_mph} mph</span>
                    <span className="wx-chip">🌧 {cp.rain_in_hr.toFixed(2)} in/hr</span>
                    <span className="wx-chip">❄ {cp.snow_in_hr.toFixed(1)} in/hr</span>
                    <span className="chip-band" style={{ background: BAND_COLORS[cp.risk_band] }}>{BAND_LABELS[cp.risk_band]}</span>
                  </div>
                </div>
              ))}
            </div>
            {selected.checkpoints.length > 24 && (
              <p style={{ color: "var(--ink-faint)", fontSize: 12 }}>
                Showing first 24 of {selected.checkpoints.length} checkpoints — open the Checkpoints tab for the full table.
              </p>
            )}
          </div>
        )}

        {tab === "summary" && <ExplainerPanel plan={plan} selected={selected} />}
      </div>
    </section>
  );
}
