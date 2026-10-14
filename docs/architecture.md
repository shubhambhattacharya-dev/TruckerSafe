# Architecture

TruckerSafe is a React/Vite client and Django REST API. A single `POST /api/route-plans/` request validates form input, geocodes the endpoints, asks OSRM for alternatives, samples Open-Meteo conditions at checkpoint ETAs, classifies risk, ranks routes, and returns one dashboard payload.

## Request path

```text
React form -> Django serializer -> geocoder + OSRM + Open-Meteo adapters
           -> resampler + ETA service -> deterministic RiskEngine
           -> risk aggregation + lexicographic ranking -> API response
           -> Leaflet map, route cards, checkpoint table, heatmap
```

External systems are isolated behind adapters. Django views orchestrate and translate errors; routing, weather, geometry, risk, ranking, and heatmap services are plain Python and unit tested. The frontend calls one endpoint, uses a generated heatmap grid for instant layer recoloring, and has an explicit demo mode for the recorded fixture.

## Reliability boundaries

- Risk classification and route ranking are deterministic; text explanation has no authority over them.
- API errors are visible to users in normal mode. `VITE_DEMO_MODE=true` is the only fixture fallback.
- Tests do not depend on live routing or weather providers. E2E uses the recorded fixture.
