import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const layer = { addTo: vi.fn(() => layer), remove: vi.fn(), clearLayers: vi.fn(), bringToBack: vi.fn(), bindPopup: vi.fn(() => layer), on: vi.fn(() => layer) };
const map = { remove: vi.fn(), fitBounds: vi.fn(), invalidateSize: vi.fn(), setView: vi.fn(() => map) };

vi.mock("leaflet", () => ({
  default: {
    map: vi.fn(() => map), tileLayer: vi.fn(() => layer), layerGroup: vi.fn(() => layer),
    polyline: vi.fn(() => layer), circleMarker: vi.fn(() => layer), marker: vi.fn(() => layer),
    divIcon: vi.fn(() => ({})), imageOverlay: vi.fn(() => layer), latLngBounds: vi.fn(() => ({ extend: vi.fn() })),
  },
}));

import MapView from "../components/MapView";

describe("MapView", () => {
  it("renders an accessible map surface without route data", () => {
    render(<MapView routes={[]} recommendedId={0} selectedId={0} onSelectRoute={vi.fn()} heatmap={null} layer="wind" loadLb={40000} departureIso="2026-10-15T08:00:00Z" forecastHour={0} />);
    expect(screen.getByRole("application", { name: "Route weather map" })).toBeInTheDocument();
  });
});
