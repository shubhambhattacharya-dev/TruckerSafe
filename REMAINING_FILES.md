# TruckerSafe — Remaining Files Checklist (~44 files)

## DAY 1 — finish (10 min)
- [ ] git add + push: `backend/apps/routing/services/recommend/ranker.py`
- [ ] git add + push: `backend/apps/routing/services/risk/aggregation.py`
- [ ] git add + push: `backend/apps/routing/tests/test_ranker.py`
- [ ] git add + push: `backend/apps/routing/tests/test_aggregation.py`

## DAY 2 — routing + weather + Django endpoint
- [x] `backend/apps/routing/services/routing/base.py`  ✅ done Oct 13
- [ ] `backend/apps/routing/services/routing/geocoder.py`
- [x] `backend/apps/routing/services/routing/osrm_adapter.py`  ✅ done Oct 13
- [ ] `backend/apps/routing/services/routing/eta.py`
- [x] `backend/apps/routing/services/weather/base.py`  ✅ done Oct 13
- [x] `backend/apps/routing/services/weather/open_meteo_adapter.py`  ✅ done Oct 13
- [x] `backend/apps/routing/services/weather/interpolation.py`  ✅ done Oct 13 (named interpolation.py, same role)
- [x] `backend/apps/routing/tests/test_open_meteo_adapter.py`  ✅ done Oct 13
- [x] `backend/apps/routing/tests/test_osrm_adapter.py`  ✅ done Oct 13 (bonus)
- [x] `backend/apps/routing/tests/test_weather_base.py`  ✅ done Oct 13 (bonus)
- [x] `backend/apps/routing/tests/test_interpolation.py`  ✅ done Oct 13 (bonus)
- [ ] `backend/apps/routing/services/routing/__init__.py`  ← MISSING, add empty file (every other package has one)
- [ ] `backend/fixtures/osrm_chicago_denver.json`
- [ ] `backend/fixtures/open_meteo_corridor.json`
- [ ] `backend/manage.py`  (django-admin startproject — auto-generates config/)
- [ ] `backend/config/settings.py`  (auto-generated, then edit)
- [ ] `backend/config/urls.py`  (auto-generated, then edit)
- [ ] `backend/config/wsgi.py`  (auto-generated)
- [ ] `backend/apps/routing/api/serializers.py`
- [ ] `backend/apps/routing/api/views.py`
- [ ] `backend/apps/routing/api/urls.py`
- [ ] `backend/apps/routing/models.py`
- [ ] `backend/apps/routing/services/recommend/explainer.py`
- [ ] `backend/apps/routing/services/recommend/templates.py`
- [ ] `backend/apps/routing/tests/test_api_contract.py`
- (optional) `services/routing/valhalla_adapter.py` + `factory.py` — only if OSRM throttles

## DAY 3 — heatmap + frontend + demo + deploy
- [ ] `backend/apps/routing/services/heatmap/idw.py`
- [ ] `backend/apps/routing/tests/test_idw.py`
- [ ] `backend/scripts/seed_demo_scenario.py`  (Chicago→Denver, Route 2 disqualified)
- [ ] `frontend/`  (Vite + React + TS scaffold — auto-generates most of the folder)
- [ ] `frontend/.env.example`
- [ ] `frontend/src/api/client.ts`
- [ ] `frontend/src/map/colors.ts`
- [ ] `frontend/src/map/layers.ts`
- [ ] `frontend/src/hooks/useRoutePlan.ts`
- [ ] `frontend/src/components/RouteForm.tsx`
- [ ] `frontend/src/components/MapView.tsx`
- [ ] `frontend/src/components/RouteCard.tsx`
- [ ] `frontend/src/components/RiskBar.tsx`
- [ ] `frontend/src/components/CheckpointTable.tsx`
- [ ] `frontend/src/components/HeatmapLayer.tsx`
- [ ] `frontend/src/components/LayerToggle.tsx`
- [ ] `frontend/src/components/ExplainerPanel.tsx`
- [ ] Deploy: backend → Railway/Render, frontend → Vercel

## DAY 4 — CI + tests + docs + Loom
- [ ] `.github/workflows/ci.yml`
- [ ] `frontend/src/tests/RiskBar.test.tsx`
- [ ] `frontend/src/tests/MapView.test.tsx`
- [ ] `frontend/src/tests/CheckpointTable.test.tsx`
- [ ] `README.md`  (full rewrite — now 1 line)
- [ ] `docs/architecture.md`
- [ ] `docs/screenshots/`
- [ ] `docs/decisions/ADR-001-routing-provider.md`
- [ ] `docs/decisions/ADR-002-weather-provider.md`
- [ ] `docs/decisions/ADR-003-risk-combination.md`
- [ ] `docs/decisions/ADR-004-conservative-segments.md`
- [ ] `docs/decisions/ADR-005-lexicographic-ranking.md`
- [ ] `docs/decisions/ADR-006-subhourly-interpolation.md`
- [ ] `docs/decisions/ADR-007-llm-explainer-only.md`
- [ ] `docs/decisions/ADR-008-idw-heatmap.md`
- [ ] Record Loom (5–10 min) + submit

DONE ALREADY (do not rebuild): engine.py, aggregation.py, ranker.py, haversine.py,
resampler.py, simplify.py + all 7 current test files — 278 tests green.
