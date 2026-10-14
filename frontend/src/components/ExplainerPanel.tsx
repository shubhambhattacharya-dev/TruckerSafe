import type { Route, RoutePlanResponse } from "../types";
import { fmtEta, fmtMiles } from "../util/format";

interface Props {
  plan: RoutePlanResponse;
  selected: Route;
}

/**
 * AI Explanation, done safely: the algorithm decided the ranking and every
 * number here comes from the API response. The narration text is produced
 * server-side from computed stats (template fallback guaranteed) — the
 * frontend renders it as-is and never invents facts.
 */
export default function ExplainerPanel({ plan, selected }: Props) {
  const recommended = plan.routes.find((r) => r.id === plan.recommended_route_id) ?? selected;
  const disqualified = plan.routes.find((r) => r.disqualified);
  return (
    <div className="summary-wrap">
      <div className="explainer card">
        <h3>🤖 {plan.explainer.headline}</h3>
        <ul>
          {plan.explainer.bullets.map((b, i) => (
            <li key={i}>{b}</li>
          ))}
        </ul>
        <div className="ai-note">
          Decision authority: the deterministic rule engine ranked these routes; the AI layer only
          narrates computed stats. If the AI service is unavailable, a template summary is shown
          instead — the numbers never change.
        </div>
      </div>
      <div>
        <div className="stat-box">
          <div className="k">Recommended — Route {recommended.id}</div>
          <div className="v">{fmtMiles(recommended.summary.distance_mi)}</div>
          <div className="k">arrives {fmtEta(recommended.summary.eta)}</div>
        </div>
        <div className="stat-box">
          <div className="k">Severe miles on recommended</div>
          <div className="v">{Math.round(recommended.risk.severe_mi)} mi</div>
        </div>
        <div className="stat-box">
          <div className="k">Average risk score</div>
          <div className="v">{recommended.risk.avg_score.toFixed(2)}</div>
        </div>
        {disqualified && (
          <div className="stat-box" style={{ borderColor: "#7c3aed" }}>
            <div className="k">Disqualified — Route {disqualified.id}</div>
            <div className="v" style={{ color: "#7c3aed" }}>{Math.round(disqualified.risk.no_travel_mi)} mi</div>
            <div className="k">No-Travel miles</div>
          </div>
        )}
      </div>
    </div>
  );
}
