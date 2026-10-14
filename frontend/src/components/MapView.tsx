import { useEffect, useMemo, useRef } from "react";
import L from "leaflet";
import type { HeatmapGrid, Route, WeatherLayer } from "../types";
import {
  BAND_COLORS,
  BAND_LABELS,
  classifyCheckpoint,
  classifyRain,
  classifySnow,
  classifyWind,
  routeColor,
} from "../map/colors";
import { fmtEta, fmtMiles } from "../util/format";

interface Props {
  routes: Route[];
  recommendedId: number;
  selectedId: number;
  onSelectRoute: (id: number) => void;
  heatmap: HeatmapGrid | null;
  layer: WeatherLayer;
  loadLb: number;
  departureIso: string;
  forecastHour: number;
}

/** Color a grid cell for the active layer — mirrors the backend decision table. */
function cellColor(layer: WeatherLayer, w: number, r: number, s: number, loadLb: number): string {
  if (layer === "wind") return BAND_COLORS[classifyWind(w)];
  if (layer === "rain") return BAND_COLORS[classifyRain(r)];
  if (layer === "snow") return BAND_COLORS[classifySnow(s)];
  return BAND_COLORS[classifyCheckpoint(w, r, s, loadLb)];
}

/** Render the heatmap grid to a data-URL image (client-side recolor, zero requests). */
function heatmapDataUrl(grid: HeatmapGrid, layer: WeatherLayer, loadLb: number): string {
  const { rows, cols } = grid;
  const src = document.createElement("canvas");
  src.width = cols;
  src.height = rows;
  const sctx = src.getContext("2d")!;
  const img = sctx.createImageData(cols, rows);
  const values = layer === "rain" ? grid.rain : layer === "snow" ? grid.snow : grid.wind;
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const i = row * cols + col;
      const [w, r, s] = [grid.wind[i], grid.rain[i], grid.snow[i]];
      const color = cellColor(layer, w, r, s, loadLb);
      const rgb = parseInt(color.slice(1), 16);
      const p = i * 4;
      img.data[p] = (rgb >> 16) & 255;
      img.data[p + 1] = (rgb >> 8) & 255;
      img.data[p + 2] = rgb & 255;
      img.data[p + 3] = 235;
    }
    void values;
  }
  sctx.putImageData(img, 0, 0);
  // Upscale with smoothing for a weather-map look.
  const big = document.createElement("canvas");
  big.width = cols * 6;
  big.height = rows * 6;
  const bctx = big.getContext("2d")!;
  bctx.imageSmoothingEnabled = true;
  bctx.imageSmoothingQuality = "high";
  bctx.drawImage(src, 0, 0, big.width, big.height);
  return big.toDataURL("image/png");
}

export default function MapView(props: Props) {
  const { routes, recommendedId, selectedId, onSelectRoute, heatmap, layer, loadLb, departureIso, forecastHour } = props;
  const holder = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const lines = useRef<L.Polyline[]>([]);
  const markers = useRef<L.LayerGroup | null>(null);
  const overlay = useRef<L.ImageOverlay | null>(null);
  const truck = useRef<L.Marker | null>(null);

  useEffect(() => {
    if (!holder.current || map.current) return;
    map.current = L.map(holder.current, {
      zoomControl: true,
      attributionControl: true,
      preferCanvas: true,
      minZoom: 2,
      maxBounds: [
        [-85, -180],
        [85, 180],
      ],
      maxBoundsViscosity: 1.0,
      worldCopyJump: false,
    });
    map.current.setView([39.8283, -98.5795], 4);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
      noWrap: true,
      bounds: [
        [-85, -180],
        [85, 180],
      ],
    }).addTo(map.current);
    markers.current = L.layerGroup().addTo(map.current);
    requestAnimationFrame(() => map.current?.invalidateSize());
    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Routes → polylines + checkpoint markers.
  useEffect(() => {
    const m = map.current;
    if (!m || !routes.length) return;
    lines.current.forEach((l) => l.remove());
    markers.current?.clearLayers();

    const bounds = L.latLngBounds([]);
    for (const route of routes) {
      const latlngs = route.polyline_simplified.map(([lat, lon]) => [lat, lon] as [number, number]);
      const color = routeColor(route, recommendedId);
      const line = L.polyline(latlngs, {
        color,
        weight: route.id === selectedId ? 5 : 3.5,
        opacity: 0.9,
      }).addTo(m);
      line.on("click", () => onSelectRoute(route.id));
      lines.current.push(line);
      latlngs.forEach(([lat, lon]) => bounds.extend([lat, lon]));

      for (const cp of route.checkpoints) {
        const marker = L.circleMarker([cp.lat, cp.lon], {
          radius: 4,
          color: "#ffffff",
          weight: 1.2,
          fillColor: BAND_COLORS[cp.risk_band],
          fillOpacity: 0.95,
        });
        marker.bindPopup(
          `<div class="route-popup"><b>Route ${route.id} · CP ${cp.idx}</b><br/>` +
          `${cp.location_name}<br/>${fmtMiles(cp.distance_mi)} · ETA ${fmtEta(cp.eta)}<br/>` +
          `Wind ${cp.wind_mph} mph · Rain ${cp.rain_in_hr} in/hr · Snow ${cp.snow_in_hr} in/hr<br/>` +
          `Risk: <b style="color:${BAND_COLORS[cp.risk_band]}">${BAND_LABELS[cp.risk_band]}</b></div>`,
        );
        markers.current?.addLayer(marker);
      }
    }
    m.fitBounds(bounds, { padding: [30, 30] });
  }, [routes, recommendedId, selectedId, onSelectRoute]);

  // Heatmap overlay — recolors from the same grid when the layer changes.
  const heatUrl = useMemo(
    () => (heatmap ? heatmapDataUrl(heatmap, layer, loadLb) : null),
    [heatmap, layer, loadLb],
  );
  useEffect(() => {
    const m = map.current;
    if (!m) return;
    overlay.current?.remove();
    overlay.current = null;
    if (!heatUrl || !heatmap) return;
    const [w, s, e, n] = heatmap.bbox;
    overlay.current = L.imageOverlay(heatUrl, [[s, w], [n, e]], { opacity: 0.55 })
      .addTo(m)
      .bringToBack();
  }, [heatUrl, heatmap]);

  // Forecast playhead: truck marker at the furthest checkpoint reached by the
  // slider time on the selected route (anchored to departure, no new requests).
  useEffect(() => {
    const m = map.current;
    if (!m || !routes.length) return;
    const route = routes.find((r) => r.id === selectedId) ?? routes[0];
    const t = new Date(departureIso).getTime() + forecastHour * 3600_000;
    const reached = route.checkpoints.filter((cp) => new Date(cp.eta).getTime() <= t);
    const cp = reached.length
      ? reached[reached.length - 1]
      : route.checkpoints[0];
    const icon = L.divIcon({
      className: "",
      html: `<div style="font-size:20px;filter:drop-shadow(0 1px 2px rgba(0,0,0,.4));">${reached.length ? "🚚" : "🕐"}</div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
    if (truck.current) truck.current.remove();
    truck.current = L.marker([cp.lat, cp.lon], { icon, zIndexOffset: 1000 }).addTo(m);
  }, [routes, selectedId, departureIso, forecastHour]);

  return <div id="map" ref={holder} role="application" aria-label="Route weather map" />;
}
