import type { RouteRisk } from "../types";
import { BAND_COLORS } from "../map/colors";
import { percentShares } from "../util/format";

interface Props {
  risk: RouteRisk;
  distanceMi: number;
}

/** Order mirrors the approved mock: Severe, No Travel, High, Moderate, Low. */
const ORDER: { key: keyof RouteRisk; label: string; color: string }[] = [
  { key: "severe_mi", label: "Severe", color: BAND_COLORS.SEVERE },
  { key: "no_travel_mi", label: "No Travel", color: BAND_COLORS.NO_TRAVEL },
  { key: "high_mi", label: "High", color: BAND_COLORS.HIGH },
  { key: "moderate_mi", label: "Moderate", color: BAND_COLORS.MODERATE },
  { key: "low_mi", label: "Low", color: BAND_COLORS.LOW },
];

/**
 * Bars show miles per band; percentages are shares of route distance computed
 * with largest-remainder rounding so the labels always read consistently
 * (guard against the "bars sum to 98%" pitfall, guidebook §8).
 */
export default function RiskBar({ risk, distanceMi }: Props) {
  const miles = ORDER.map((o) => risk[o.key] as number);
  const shares = percentShares(miles);
  return (
    <div>
      <div className="risk-bar" role="img" aria-label="Miles per risk band">
        {ORDER.map((o, i) =>
          miles[i] > 0 ? (
            <span key={o.key} className="seg" style={{ width: `${shares[i]}%`, background: o.color }} />
          ) : null,
        )}
      </div>
      <div className="risk-labels">
        {ORDER.map((o, i) => (
          <div key={o.key} className="rl" style={{ flex: miles[i] > 0 ? `${shares[i]} 1 0` : "0 0 auto", marginRight: miles[i] > 0 ? 6 : 10, minWidth: 44 }}>
            <b>{Math.round(miles[i])} mi ({shares[i]}%)</b>
            {o.label}
          </div>
        ))}
      </div>
      <span hidden>{distanceMi}</span>
    </div>
  );
}
