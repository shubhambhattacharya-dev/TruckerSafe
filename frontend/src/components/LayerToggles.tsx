import type { WeatherLayer } from "../types";

const LAYERS: { id: WeatherLayer; icon: string; label: string }[] = [
  { id: "risk", icon: "🛡", label: "Overall Risk" },
  { id: "wind", icon: "🌬", label: "Wind" },
  { id: "rain", icon: "🌧", label: "Rain" },
  { id: "snow", icon: "❄", label: "Snow" },
];

interface Props {
  active: WeatherLayer;
  onChange: (l: WeatherLayer) => void;
}

export default function LayerToggles({ active, onChange }: Props) {
  return (
    <div className="map-overlay layer-toggles">
      <div className="lt-title">Weather Layer</div>
      <div className="lt-row">
        {LAYERS.map((l) => (
          <button
            key={l.id}
            className={`lt-btn ${active === l.id ? "active" : ""}`}
            onClick={() => onChange(l.id)}
            aria-pressed={active === l.id}
          >
            <span aria-hidden>{l.icon}</span> {l.label}
          </button>
        ))}
      </div>
    </div>
  );
}
