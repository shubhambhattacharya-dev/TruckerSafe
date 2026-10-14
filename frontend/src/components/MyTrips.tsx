import type { RoutePlanRequest } from "../types";

export interface SavedTrip {
  id: string;
  savedAt: string;
  request: RoutePlanRequest;
}

const KEY = "truckersafe.trips";

export function loadTrips(): SavedTrip[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]") as SavedTrip[];
  } catch {
    return [];
  }
}

export function saveTrip(request: RoutePlanRequest): SavedTrip {
  const trips = loadTrips();
  const trip: SavedTrip = {
    id: `${Date.now()}`,
    savedAt: new Date().toISOString(),
    request,
  };
  localStorage.setItem(KEY, JSON.stringify([trip, ...trips].slice(0, 20)));
  return trip;
}

export function deleteTrip(id: string): SavedTrip[] {
  const trips = loadTrips().filter((t) => t.id !== id);
  localStorage.setItem(KEY, JSON.stringify(trips));
  return trips;
}

interface Props {
  trips: SavedTrip[];
  onLoad: (t: SavedTrip) => void;
  onDelete: (id: string) => void;
}

export default function MyTrips({ trips, onLoad, onDelete }: Props) {
  return (
    <div className="card trips-page">
      <h2 style={{ marginTop: 0 }}>My Trips</h2>
      <p style={{ color: "var(--ink-soft)", marginTop: 0 }}>
        Saved route plans. Loading a trip re-runs the route plan with the same inputs.
      </p>
      {trips.length === 0 ? (
        <div className="empty">
          No saved trips yet — plan a route and press <b>Save Trip</b> to keep it here.
        </div>
      ) : (
        trips.map((t) => (
          <div className="trip-row" key={t.id}>
            <span aria-hidden>🚛</span>
            <span>
              <span className="route">{t.request.origin} → {t.request.destination}</span>
              <br />
              <span className="meta">
                Departure {new Date(t.request.departure_time).toLocaleString()} ·{" "}
                {t.request.load_lb.toLocaleString()} lb · every {t.request.checkpoint_interval_miles} mi
              </span>
            </span>
            <span className="spacer" />
            <button className="btn-ghost" onClick={() => onLoad(t)}>Load</button>
            <button className="btn-ghost" onClick={() => onDelete(t.id)}>Delete</button>
          </div>
        ))
      )}
    </div>
  );
}
