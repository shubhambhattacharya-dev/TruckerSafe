# TruckerSafe — Weather-Aware Truck Routing

[![CI](https://github.com/shubhambhattacharya-dev/TruckerSafe/actions/workflows/ci.yml/badge.svg)](https://github.com/shubhambhattacharya-dev/TruckerSafe/actions)

Weather-aware truck-route planning system built with **React (TypeScript + Leaflet)** and **Django REST Framework (Python)**. TruckerSafe compares real road-route alternatives from OSRM, samples Open-Meteo forecast weather at estimated arrival times at 10/25/50-mile intervals, applies deterministic load-aware safety rules, and presents a recommended route with interactive maps, IDW weather heatmap layers, and a checkpoint audit table.

> **Prime Directive**: *The ALGORITHM decides, AI only explains. Every number on screen is reproducible by a unit test.*

---

## Architecture Diagram

```mermaid
flowchart TD
    User([Dispatcher / Driver]) -->|Enter trip details| SPA[React Frontend\nVite + TS + Leaflet]
    SPA -->|POST /api/route-plans/| DRF[Django REST API\nThin Views + Serializers]
    
    subgraph ServiceLayer [Service Layer - Pure Python Logic]
        DRF --> Geocode[NominatimGeocoder]
        Geocode --> OSRM[OSRMAdapter\nAlternatives = 3]
        OSRM --> Resample[PolylineResampler\nExact 10/25/50 mi arc-length]
        Resample --> ETA[ETAService\nArrival time per checkpoint]
        ETA --> Weather[OpenMeteoAdapter\nHourly Forecast + Spatial Cache]
        Weather --> Risk[RiskEngine\nPure 5x5x5 Decision Table + Load Rules]
        Risk --> Segments[Conservative Segment Aggregator\nWorse risk of endpoints]
        Segments --> Ranker[Lexicographic Ranker\n(no_travel, severe, high, avg, time)]
        Ranker --> Heatmap[HeatmapService\nIDW Grid 0.08° within 150km]
        Ranker --> Explainer[AI / Template Explainer\nDownstream text only]
    end

    Heatmap --> Output[(Aggregate JSON DTO)]
    Explainer --> Output
    Output -->|Single Response| SPA
```

### Architectural Patterns Used
- **Adapter Pattern**: All external integrations (`OSRMAdapter`, `OpenMeteoAdapter`, `NominatimGeocoder`) adhere to abstract interfaces. Swapping providers requires updating a single setting.
- **Service Layer Pattern**: Thin Django views only validate requests and serialize responses. All business logic lives in decoupled Python services without framework imports, making all 491 tests run in <2 seconds.
- **Strategy Pattern**: The safety rules engine uses an immutable decision table data structure rather than complex branching logic.
- **DTO / Contract Boundary**: Strictly typed request/response payload shared character-for-character between TypeScript interfaces and DRF serializers.
- **Downstream AI Boundary**: The LLM / rule template engine only narrates computed numbers; it cannot alter ranking or route metrics.

---

## Key Design Decisions

### 1. Worst-of-Three Condition Combination (ADR-003)
The specification provides three independent condition tables (wind, rain, snow) without specifying combination priority. Checkpoints evaluate wind, rain, and snow independently; the baseline checkpoint band is taken as the **worst (highest) band** across the three, followed by load-rule upgrades:
- Wind $\ge$ 55 mph $\rightarrow$ **No Travel** (all loads)
- Wind 45–54 mph with load > 30,000 lb $\rightarrow$ **No Travel**
- Wind 35–44 mph with load > 40,000 lb $\rightarrow$ **Severe**
- Rain > 1.00 in/hr or Snow > 3.0 in/hr $\rightarrow$ **No Travel**

### 2. Conservative Segment Aggregation (ADR-004)
A truck drives *through* the distance between checkpoints. Each segment is assigned the **worse risk of its two endpoints**. Miles per risk band sum exactly to total route distance.

### 3. ETA & Speed Fallback (ADR-006)
Checkpoint ETAs use cumulative segment durations from the routing engine scaled to total route duration. When routing durations are unavailable, a defensible **55 mph commercial highway speed** for 40,000 lb loaded trucks is applied. Checkpoint ETA and total ETA never disagree.

### 4. Lexicographic Ranking (ADR-005)
Routes are ranked by a strict tuple: `(no_travel_miles, severe_miles, high_miles, avg_risk_score, duration)` ascending. No arbitrary weighted scores are used; ties break deterministically by fewer high-risk miles, then lower average risk, then travel time.

---

## Run Locally

### Prerequisites
- Node.js 20+
- Python 3.12+ (Python 3.12, 3.13, and 3.14 supported)
- npm

### 1. Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

### 2. Frontend Setup
In a second terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`**. Vite automatically proxies `/api` requests to Django at `http://127.0.0.1:8000`.

---

## Demo Mode

To run completely offline without hitting external routing or weather APIs:
1. Copy `frontend/.env.example` to `frontend/.env`.
2. Set `VITE_DEMO_MODE=true`.
3. In demo mode, the application loads the deterministic fixture, labeled with a visible **DEMO DATA** banner in the UI.

To regenerate the Chicago-to-Denver demo fixture:
```powershell
cd backend
venv\Scripts\python scripts\seed_demo_scenario.py
```

---

## API Specification

**`POST /api/route-plans/`** (also aliased at `/api/route-plans`)

```json
{
  "origin": "Chicago, IL, USA",
  "destination": "Denver, CO, USA",
  "departure_time": "2026-10-15T08:00:00-05:00",
  "load_lb": 40000,
  "checkpoint_interval_miles": 25
}
```

**Response (200 OK)**:
```json
{
  "recommended_route_id": 1,
  "demo_data": false,
  "routes": [
    {
      "id": 1,
      "summary": { "distance_mi": 1050.2, "duration_min": 980.0, "eta": "2026-10-15T23:20:00Z" },
      "risk": { "severe_mi": 0.0, "high_mi": 12.0, "moderate_mi": 186.0, "low_mi": 852.2, "no_travel_mi": 0.0, "avg_score": 1.35 },
      "disqualified": false,
      "reason": null,
      "polyline_simplified": [[41.8781, -87.6298], [39.7392, -104.9903]],
      "checkpoints": [
        {
          "idx": 1, "lat": 41.8781, "lon": -87.6298, "distance_mi": 0.0,
          "eta": "2026-10-15T08:00:00Z", "location_name": "Checkpoint 1",
          "wind_mph": 12.5, "rain_in_hr": 0.0, "snow_in_hr": 0.0,
          "risk_band": "LOW"
        }
      ]
    }
  ],
  "explainer": {
    "headline": "Route 1 is recommended.",
    "bullets": ["Avoids severe wind corridor in Route 2", "Optimal travel time"]
  },
  "heatmap": {
    "bbox": [-105.99, 38.73, -86.62, 42.87],
    "rows": 52, "cols": 242,
    "wind": [ ... ], "rain": [ ... ], "snow": [ ... ]
  }
}
```

---

## Test Verification

Run all test suites locally:

```powershell
# Backend: Django checks + 492 pytest cases (service layer, risk matrix, contracts)
cd backend
venv\Scripts\python manage.py check
venv\Scripts\pytest -q

# Frontend: Vitest unit tests + production bundle build
cd frontend
npm test
npm run build

# End-to-End: Playwright browser workflow
npx playwright install chromium
npm run test:e2e
```

---

## Deployment

The app ships deploy-ready for **Render (backend)** and **Vercel (frontend)**.

### Backend → Render
1. Push this repository to GitHub.
2. On [Render](https://render.com), create a **Blueprint** pointing at the repo — it reads [`render.yaml`](render.yaml) and provisions:
   - Build: `pip install` → `collectstatic` → `migrate`
   - Start: `gunicorn config.wsgi:application` (WhiteNoise serves `/static/` and admin assets)
   - Health check: `/healthz/`
   - Env: `DJANGO_SECRET_KEY` (auto-generated), `DJANGO_DEBUG=false`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`
3. Note the service URL, e.g. `https://truckersafe-backend.onrender.com`.

### Frontend → Vercel
1. On [Vercel](https://vercel.com), **Import Project** → this repo → set **Root Directory** to `frontend/` ([`vercel.json`](frontend/vercel.json) handles the rest).
2. Set the environment variable `VITE_API_BASE=https://truckersafe-backend.onrender.com`.
3. Add the Vercel URL (e.g. `https://truckersafe.vercel.app`) to the backend's `CORS_ALLOWED_ORIGINS` on Render.

If the backend is cold or unreachable, the frontend serves the recorded demo fixture behind a visible **DEMO DATA** banner — the hosted URL never shows a dead dashboard.

---

## Scale Path (Production Foresight)

- **Asynchronous Processing**: Transition synchronous route evaluation to Celery tasks with Redis. The POST endpoint returns `202 Accepted` with a job ID; the frontend subscribes via WebSocket or polls.
- **Heatmap Tiling & CDN**: Pre-render IDW heatmap layers into Web Mercator slippy-map PNG tiles cached on Cloudflare/CloudFront per `(bbox, forecast_hour)` slice.
- **Weather Volume & Multi-Provider**: Replace Open-Meteo with commercial services (DTN, The Weather Company) by implementing a new adapter satisfying `WeatherProvider`.
- **Database Partitioning**: Partition `Trip` model on PostgreSQL by `created_at` monthly for trip archiving and fleet analytics.
- **Dynamic Road-Class Speeds**: Integrate OSRM per-waypoint speed annotations rather than fixed average speeds for improved ETA accuracy in mountain passes.

---

## Documentation & ADRs

All architectural design records are preserved under [`docs/decisions/`](docs/decisions/):
- [`ADR-001: Routing Provider Adapter`](docs/decisions/ADR-001-routing-provider.md)
- [`ADR-002: Weather Provider Adapter`](docs/decisions/ADR-002-weather-provider.md)
- [`ADR-003: Worst-of-Three Risk Combination`](docs/decisions/ADR-003-risk-combination.md)
- [`ADR-004: Conservative Segment Risk Aggregation`](docs/decisions/ADR-004-conservative-segments.md)
- [`ADR-005: Lexicographic Route Ranking`](docs/decisions/ADR-005-lexicographic-ranking.md)
- [`ADR-006: Sub-Hourly Weather Interpolation`](docs/decisions/ADR-006-subhourly-interpolation.md)
- [`ADR-007: Downstream LLM / Template Explainer`](docs/decisions/ADR-007-llm-explainer-only.md)
- [`ADR-008: Inverse-Distance Weighting (IDW) Heatmap`](docs/decisions/ADR-008-idw-heatmap.md)
