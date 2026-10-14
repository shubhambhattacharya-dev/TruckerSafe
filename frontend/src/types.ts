// Data contract — mirrors guidebook §5 (must match the DRF serializer
// character-for-character once the backend endpoint lands).

export type RiskBandName = "LOW" | "MODERATE" | "HIGH" | "SEVERE" | "NO_TRAVEL";

export interface RoutePlanRequest {
  origin: string;
  destination: string;
  departure_time: string;
  load_lb: number;
  checkpoint_interval_miles: number;
}

export interface RouteSummary {
  distance_mi: number;
  duration_min: number;
  eta: string;
}

export interface RouteRisk {
  severe_mi: number;
  high_mi: number;
  moderate_mi: number;
  low_mi: number;
  no_travel_mi: number;
  avg_score: number;
}

export interface Checkpoint {
  idx: number;
  lat: number;
  lon: number;
  distance_mi: number;
  eta: string;
  location_name: string;
  wind_mph: number;
  rain_in_hr: number;
  snow_in_hr: number;
  risk_band: RiskBandName;
}

export interface Route {
  id: number;
  summary: RouteSummary;
  risk: RouteRisk;
  disqualified: boolean;
  reason: string | null;
  route_name?: string;
  polyline_simplified: [number, number][];
  checkpoints: Checkpoint[];
}

export interface Explainer {
  headline: string;
  bullets: string[];
}

export interface HeatmapGrid {
  bbox: [number, number, number, number]; // [w, s, e, n]
  rows: number;
  cols: number;
  wind: number[];
  rain: number[];
  snow: number[];
}

export interface RoutePlanResponse {
  recommended_route_id: number;
  demo_data: boolean;
  routes: Route[];
  explainer: Explainer;
  heatmap: HeatmapGrid;
}

export type WeatherLayer = "risk" | "wind" | "rain" | "snow";
