// Single source of truth for risk-band strings, colors and thresholds.
// Map colors derive from here — never hardcoded per component (guidebook §5).
// Thresholds mirror backend engine.py exactly (worst-of-three + load rules).

import type { RiskBandName } from "../types";

export const RISK_BANDS: readonly RiskBandName[] = [
  "LOW",
  "MODERATE",
  "HIGH",
  "SEVERE",
  "NO_TRAVEL",
];

export const BAND_COLORS: Record<RiskBandName, string> = {
  LOW: "#22c55e",
  MODERATE: "#eab308",
  HIGH: "#f97316",
  SEVERE: "#ef4444",
  NO_TRAVEL: "#7c3aed",
};

export const BAND_LABELS: Record<RiskBandName, string> = {
  LOW: "Low",
  MODERATE: "Moderate",
  HIGH: "High",
  SEVERE: "Severe",
  NO_TRAVEL: "No Travel",
};

export function classifyWind(mph: number): RiskBandName {
  if (mph >= 55) return "NO_TRAVEL";
  if (mph >= 45) return "SEVERE";
  if (mph >= 35) return "HIGH";
  if (mph >= 25) return "MODERATE";
  return "LOW";
}

export function classifyRain(inHr: number): RiskBandName {
  if (inHr > 1.0) return "NO_TRAVEL";
  if (inHr >= 0.5) return "SEVERE";
  if (inHr >= 0.25) return "HIGH";
  if (inHr >= 0.1) return "MODERATE";
  return "LOW";
}

export function classifySnow(inHr: number): RiskBandName {
  if (inHr > 3.0) return "NO_TRAVEL";
  if (inHr >= 2.0) return "SEVERE";
  if (inHr >= 1.0) return "HIGH";
  if (inHr >= 0.5) return "MODERATE";
  return "LOW";
}

const BAND_RANK: Record<RiskBandName, number> = {
  LOW: 1,
  MODERATE: 2,
  HIGH: 3,
  SEVERE: 4,
  NO_TRAVEL: 5,
};

/** Worst-of-three + load rules — mirrors backend classify_checkpoint(). */
export function classifyCheckpoint(
  windMph: number,
  rainInHr: number,
  snowInHr: number,
  loadLb: number,
): RiskBandName {
  const bands = [classifyWind(windMph), classifyRain(rainInHr), classifySnow(snowInHr)];
  let band = bands.reduce((a, b) => (BAND_RANK[b] > BAND_RANK[a] ? b : a));
  const w = classifyWind(windMph);
  if (w === "NO_TRAVEL") band = "NO_TRAVEL";
  else if (w === "SEVERE" && loadLb > 30000) band = "NO_TRAVEL";
  else if (w === "HIGH" && loadLb > 40000 && BAND_RANK[band] < BAND_RANK.SEVERE)
    band = "SEVERE";
  return band;
}

/** Legend model per active layer — the legend always matches the active layer. */
export interface LegendEntry {
  color: string;
  range: string;
  label: string;
}

export function legendFor(layer: "risk" | "wind" | "rain" | "snow"): LegendEntry[] {
  if (layer === "risk")
    return RISK_BANDS.map((b) => ({
      color: BAND_COLORS[b],
      range: "",
      label: BAND_LABELS[b],
    }));
  if (layer === "wind")
    return [
      { color: BAND_COLORS.LOW, range: "< 25", label: "Low" },
      { color: BAND_COLORS.MODERATE, range: "25 – 34", label: "Moderate" },
      { color: BAND_COLORS.HIGH, range: "35 – 44", label: "High" },
      { color: BAND_COLORS.SEVERE, range: "45 – 54", label: "Severe*" },
      { color: BAND_COLORS.NO_TRAVEL, range: "≥ 55", label: "No Travel" },
    ];
  if (layer === "rain")
    return [
      { color: BAND_COLORS.LOW, range: "< 0.10", label: "Low" },
      { color: BAND_COLORS.MODERATE, range: "0.10 – 0.25", label: "Moderate" },
      { color: BAND_COLORS.HIGH, range: "0.25 – 0.50", label: "High" },
      { color: BAND_COLORS.SEVERE, range: "0.50 – 1.00", label: "Severe" },
      { color: BAND_COLORS.NO_TRAVEL, range: "> 1.00", label: "No Travel" },
    ];
  return [
    { color: BAND_COLORS.LOW, range: "< 0.5", label: "Low" },
    { color: BAND_COLORS.MODERATE, range: "0.5 – 1.0", label: "Moderate" },
    { color: BAND_COLORS.HIGH, range: "1.0 – 2.0", label: "High" },
    { color: BAND_COLORS.SEVERE, range: "2.0 – 3.0", label: "Severe" },
    { color: BAND_COLORS.NO_TRAVEL, range: "> 3.0", label: "No Travel" },
  ];
}

export const LEGEND_TITLES: Record<"risk" | "wind" | "rain" | "snow", string> = {
  risk: "Overall Risk",
  wind: "Wind Speed (mph)",
  rain: "Rain (in/hr)",
  snow: "Snow (in/hr)",
};

/** Route line colors: recommended green, disqualified purple, others orange. */
export function routeColor(route: {
  disqualified: boolean;
  id: number;
}, recommendedId: number): string {
  if (route.id === recommendedId) return "#16a34a";
  if (route.disqualified) return "#7c3aed";
  return "#ea580c";
}
