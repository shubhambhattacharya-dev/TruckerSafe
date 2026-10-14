import type { Route } from "../types";
import { BAND_COLORS, routeColor } from "../map/colors";
import { fmtEta, fmtDuration, fmtMiles } from "../util/format";
import RiskBar from "./RiskBar";

interface Props {
  route: Route;
  recommendedId: number;
  selected: boolean;
  onSelect: (id: number) => void;
}

function avgRiskBadge(score: number): { label: string; color: string; bg: string } {
  if (score < 1.8) return { label: "Low", color: "#166534", bg: "#dcfce7" };
  if (score < 2.6) return { label: "Moderate", color: "#854d0e", bg: "#fef9c3" };
  if (score < 3.4) return { label: "High", color: "#9a3412", bg: "#ffedd5" };
  return { label: "Severe", color: "#991b1b", bg: "#fee2e2" };
}

const RoadIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
    <path d="M4 19 8 5M20 19 16 5M12 5v3m0 4v3m0 4v2" />
  </svg>
);
const ClockIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
    <circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" />
  </svg>
);

export default function RouteCard({ route, recommendedId, selected, onSelect }: Props) {
  const isRec = route.id === recommendedId;
  const badge = avgRiskBadge(route.risk.avg_score);
  const color = routeColor(route, recommendedId);

  return (
    <div
      className={`route-card ${selected ? "selected" : ""} ${isRec ? "recommended" : ""}`}
      onClick={() => onSelect(route.id)}
      role="button"
      aria-pressed={selected}
    >
      <div className="rc-head">
        <h3 style={{ color }}>Route {route.id}</h3>
        {isRec && <span className="chip green">Recommended</span>}
        {isRec && <span className="chip outline">Safest per risk rules</span>}
        {route.disqualified && <span className="chip purple">Disqualified</span>}
        {route.disqualified && <span className="chip red">⛔ No Travel (unsafe)</span>}
        {!isRec && !route.disqualified && route.route_name && (
          <span className="chip outline">{route.route_name}</span>
        )}
        <span className={`check-dot ${selected ? "on" : ""}`}>{selected ? "✓" : ""}</span>
      </div>

      {route.disqualified && route.reason && (
        <div className="dq-note" style={{ marginTop: 10 }}>
          <span aria-hidden>ⓘ</span>
          <span><b>Not recommended — wind exceeds safe limits for your load.</b><br />{route.reason}</span>
        </div>
      )}

      <div className="rc-stats">
        <div className="rc-stat">
          <span className="k"><RoadIcon /> Distance</span>
          <span className="v">{fmtMiles(route.summary.distance_mi)}</span>
        </div>
        <div className="rc-stat">
          <span className="k"><ClockIcon /> ETA (arrival)</span>
          <span className="v">{fmtDuration(route.summary.duration_min)}</span>
          <span className="s">{fmtEta(route.summary.eta)}</span>
        </div>
        <div className="rc-stat" style={{ textAlign: "right" }}>
          {route.disqualified ? (
            <>
              <span className="k" style={{ justifyContent: "flex-end" }}>⛔ No Travel</span>
              <span className="v" style={{ color: BAND_COLORS.NO_TRAVEL }}>(disqualified)</span>
            </>
          ) : (
            <>
              <span className="k" style={{ justifyContent: "flex-end" }}>Average Risk</span>
              <span className="badge-risk" style={{ background: badge.bg, color: badge.color }}>
                <span aria-hidden>{badge.label === "Low" ? "🛡" : badge.label === "Moderate" ? "⚠" : "⚠️"}</span>
                {badge.label}
              </span>
              <span className="s">avg score {route.risk.avg_score.toFixed(1)}</span>
            </>
          )}
        </div>
      </div>

      <RiskBar risk={route.risk} distanceMi={route.summary.distance_mi} />
    </div>
  );
}
