import { LEGEND_TITLES, legendFor } from "../map/colors";
import type { WeatherLayer } from "../types";

export default function RiskLegend({ layer }: { layer: WeatherLayer }) {
  const rows = legendFor(layer);
  return (
    <div className="map-overlay legend">
      <div className="lg-title">
        <span>{LEGEND_TITLES[layer]}</span>
        <span title={layer === "wind" ? "* Severe winds escalate to No Travel for heavy loads" : undefined}>ⓘ</span>
      </div>
      {rows.map((r) => (
        <div className="lg-row" key={r.label + r.range}>
          <span className="dot" style={{ background: r.color }} />
          {r.range ? (
            <>
              <span className="range">{r.range}</span>
              <span className="lbl" style={{ gridColumn: "1 / -1", paddingLeft: 20, marginTop: -2 }}>
                {r.label}
              </span>
            </>
          ) : (
            <span className="lbl" style={{ fontWeight: 600 }}>{r.label}</span>
          )}
        </div>
      ))}
    </div>
  );
}
