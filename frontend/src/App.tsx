import { useCallback, useRef, useState } from "react";
import TopBar from "./components/TopBar";
import RouteForm, { DEFAULT_FORM, toRequest, type FormState } from "./components/RouteForm";
import MapView from "./components/MapView";
import ForecastTimeline from "./components/ForecastTimeline";
import LayerToggles from "./components/LayerToggles";
import RiskLegend from "./components/RiskLegend";
import RouteCard from "./components/RouteCard";
import DetailTabs from "./components/DetailTabs";
import MyTrips, { deleteTrip, loadTrips, saveTrip, type SavedTrip } from "./components/MyTrips";
import { fetchRoutePlan, type RoutePlanResult } from "./api/client";
import type { RoutePlanRequest, WeatherLayer } from "./types";

export default function App() {
  const [page, setPage] = useState<"plan" | "trips">("plan");
  const [form, setForm] = useState<FormState>(DEFAULT_FORM);
  const [result, setResult] = useState<RoutePlanResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState(1);
  const [layer, setLayer] = useState<WeatherLayer>("wind");
  const [forecastHour, setForecastHour] = useState(6);
  const [playing, setPlaying] = useState(false);
  const [trips, setTrips] = useState<SavedTrip[]>(() => loadTrips());
  const [savedFlash, setSavedFlash] = useState(false);
  const mapSection = useRef<HTMLDivElement>(null);

  const run = useCallback(async (f: FormState) => {
    setBusy(true);
    setError(null);
    setPlaying(false);
    try {
      const res = await fetchRoutePlan(toRequest(f));
      setResult(res);
      setSelectedId(res.plan.recommended_route_id);
      setForecastHour(6);
      if (window.innerWidth <= 900 && mapSection.current) {
        mapSection.current.scrollIntoView({ behavior: "smooth", block: "start" });
      } else {
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }, []);

  const loadTrip = (t: SavedTrip) => {
    setPage("plan");
    setForm({
      ...DEFAULT_FORM,
      origin: t.request.origin,
      destination: t.request.destination,
      loadLb: String(t.request.load_lb),
      intervalMi: String(t.request.checkpoint_interval_miles),
    });
    void run({
      ...DEFAULT_FORM,
      origin: t.request.origin,
      destination: t.request.destination,
      loadLb: String(t.request.load_lb),
      intervalMi: String(t.request.checkpoint_interval_miles),
    } as FormState);
  };

  const saveCurrent = () => {
    if (!result) return;
    saveTrip(result.request);
    setTrips(loadTrips());
    setSavedFlash(true);
    window.setTimeout(() => setSavedFlash(false), 1600);
  };

  const plan = result?.plan ?? null;
  const request: RoutePlanRequest | null = result?.request ?? null;
  const departureIso = request?.departure_time ?? toRequest(form).departure_time;

  return (
    <>
      <TopBar page={page} onNavigate={setPage} />

      {page === "trips" && (
        <MyTrips
          trips={trips}
          onLoad={loadTrip}
          onDelete={(id) => setTrips(deleteTrip(id))}
        />
      )}

      {page === "plan" && (
        <>
          <div className="plan-layout">
            <RouteForm initial={form} onSubmit={(f) => { setForm(f); void run(f); }} busy={busy} />
            <div className="map-panel" ref={mapSection}>
              <div className="card map-card">
                <div id="map-holder" style={{ position: "relative" }}>
                  <MapView
                    routes={plan?.routes ?? []}
                    recommendedId={plan?.recommended_route_id ?? 0}
                    selectedId={selectedId}
                    onSelectRoute={setSelectedId}
                    heatmap={plan?.heatmap ?? null}
                    layer={layer}
                    loadLb={request?.load_lb ?? (Number(form.loadLb) || 40000)}
                    departureIso={departureIso}
                    forecastHour={forecastHour}
                  />
                  {plan?.demo_data && <div className="demo-banner">DEMO DATA — recorded fixture, backend offline</div>}
                  {plan && (
                    <>
                      <ForecastTimeline
                        departureIso={departureIso}
                        hour={forecastHour}
                        onHour={setForecastHour}
                        playing={playing}
                        onTogglePlay={() => setPlaying((p) => !p)}
                      />
                      <LayerToggles active={layer} onChange={setLayer} />
                      <RiskLegend layer={layer} />
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>

          {busy && (
            <div className="state-panel card">
              <div className="spinner" />
              <h3>Analyzing routes…</h3>
              <p>Geocoding, fetching 3 route alternatives, sampling weather at every checkpoint and scoring risk.</p>
            </div>
          )}

          {error && (
            <div className="state-panel card">
              <h3>Could not plan this route</h3>
              <p>{error}</p>
              <button className="btn-ghost" onClick={() => setError(null)}>Try again</button>
            </div>
          )}

          {!busy && !error && !plan && (
            <div className="state-panel card">
              <h3>Plan your first route</h3>
              <p>
                Enter an origin, destination, departure time and load weight — TruckerSafe compares
                3 real route alternatives, samples weather at every checkpoint at your estimated
                arrival time, and ranks them by the risk rules.
              </p>
            </div>
          )}

          {plan && !busy && request && (
            <>
              <div className="route-cards">
                {plan.routes.map((r) => (
                  <RouteCard
                    key={r.id}
                    route={r}
                    recommendedId={plan.recommended_route_id}
                    selected={r.id === selectedId}
                    onSelect={setSelectedId}
                  />
                ))}
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end", padding: "0 14px", marginTop: 10 }}>
                <button className="btn-ghost" onClick={saveCurrent}>
                  {savedFlash ? "Saved ✓" : "💾 Save Trip"}
                </button>
              </div>
              <DetailTabs
                plan={plan}
                request={request}
                selectedId={selectedId}
                onSelectRoute={setSelectedId}
                onViewOnMap={() => mapSection.current?.scrollIntoView({ behavior: "smooth" })}
              />
            </>
          )}
        </>
      )}
    </>
  );
}
