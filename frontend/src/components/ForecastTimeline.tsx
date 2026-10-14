import { useEffect } from "react";

interface Props {
  departureIso: string;
  hour: number;
  onHour: (h: number) => void;
  playing: boolean;
  onTogglePlay: () => void;
}

function clockAt(departureIso: string, h: number): string {
  const d = new Date(new Date(departureIso).getTime() + h * 3600_000);
  return d.toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric" });
}

const TICKS = [0, 6, 12, 24, 36, 48];

export default function ForecastTimeline({ departureIso, hour, onHour, playing, onTogglePlay }: Props) {
  useEffect(() => {
    if (!playing) return;
    const id = window.setInterval(() => onHour((hour + 1) % 49), 220);
    return () => window.clearInterval(id);
  }, [playing, hour, onHour]);

  return (
    <div className="map-overlay timeline">
      <div className="t-head">
        <button className="play-btn" onClick={onTogglePlay} title={playing ? "Pause" : "Play forecast"}>
          {playing ? "❚❚" : "▶"}
        </button>
        <div>
          Weather Forecast Along Route (anchored to departure time)
          <div style={{ fontWeight: 400, color: "var(--ink-soft)", fontSize: 11 }}>
            Showing conditions at <b>{clockAt(departureIso, hour)}</b> (+{hour}h)
          </div>
        </div>
      </div>
      <input
        type="range"
        min={0}
        max={48}
        step={1}
        value={hour}
        onChange={(e) => onHour(Number(e.target.value))}
        aria-label="Forecast hours after departure"
      />
      <div className="t-ticks">
        {TICKS.map((t) => (
          <span key={t} style={t === 0 ? { fontWeight: 700 } : undefined}>
            {t === 0 ? (
              <>
                <b>{clockAt(departureIso, 0)}</b>(Departure)
              </>
            ) : (
              <>
                <b>+{t}h</b>
                {clockAt(departureIso, t)}
              </>
            )}
          </span>
        ))}
      </div>
    </div>
  );
}
