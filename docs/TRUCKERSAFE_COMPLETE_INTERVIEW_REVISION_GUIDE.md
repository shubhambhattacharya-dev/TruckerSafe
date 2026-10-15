# TruckerSafe: Poore Project ki Samajh aur Interview Revision

## Zero se shuru. Hinglish mein. File by file.

Yeh guide us learner ke liye hai jisne pehle kabhi code nahi padha. Isko screen reader ya text-to-speech se sunne ke liye bhi likha gaya hai. Har section chhota rakha gaya hai. Code ka technical word aaye to uska simple meaning diya gaya hai.

Project ke code, test names, README, architecture note, deployment files aur decision records ko dekh kar yeh guide taiyar ki gayi hai. Jahan code aur purani documentation alag baat kehte hain, wahan guide implementation ko priority deti hai aur difference ko batati hai.

---

## Part 0. Is guide ko padhne ka best tareeka

### Sunne/padhne ka chapter map

1. **Shuruaat:** Part 0–2 mein padhne ka tareeka, shabdon ki dictionary, project ki kahaani aur mind map.
2. **Pehle poora flow:** Part 3 mein ek request ka form se jawab tak safar aur har “agar / warna” condition.
3. **Zaroori buniyad:** Part 4–5 mein frontend/backend shabd, safety rules, formulas aur unke seedhe examples.
4. **Backend ko samjho:** Part 6 ko uske subchapters mein suno. Har file ka purpose, input/output, condition check aur connection diya hai.
5. **Frontend ko samjho:** Part 7 UI aur API files ko subchapters mein rakhta hai.
6. **Project ke baaki tukde:** Part 8–11 tests, fixtures, documentation aur deployment/CI cover karte hain.
7. **Interview revision:** Part 12–16 dependencies, interview jawab, common galtiyan, recall aur short revision dete hain.

**Screen reader/TTS tareeka:** heading list se chapter/subchapter chun sakte hain. Ek baar mein ek file heading sunein; file ka naam sunne ke baad Purpose, Condition check aur Connects to sunen; phir agle file par jaayein. Code names English mein rahenge, explanation Hinglish mein hai.

### Teen rounds mein seekho

- **Round 1: Kahaani.** Pehle project purpose, system flow aur mind map suno.
- **Round 2: File tour.** Har file ke liye pehle “kyun”, phir “andar kya hota hai”, phir “kis file se judi hai” suno.
- **Round 3: Interview recall.** Answer chhupakar question padho, apne shabdon mein jawab bolo, phir sample jawab se compare karo.

### Jaldi dimaag mein baithane ke techniques

- **Chunking:** Ek baar mein ek chhota idea. Jaise pehle sirf address-to-map, phir route-to-weather.
- **Story hook:** TruckerSafe ko weather mein truck bhejne wale dispatcher ki kahaani samjho.
- **Teach-back:** Har section ke baad khud ko 20 second mein samjhao. Agar simple words mein nahi samjha pa rahe, dobara suno.
- **Active recall:** Answer dekhne se pehle khud yaad karne ki koshish karo. Yaad nikalna seekhne ko majboot banata hai.
- **Input-to-output:** Hamesha bolo: “Mujhe kya mila? Code ne kya kiya? Mujhe kya wapas mila?”
- **One-change prediction:** Ek condition badlo aur output predict karo. Jaise 54 mph se 55 mph wind ho jaye to risk kaise badlega?
- **Spaced revision:** Aaj, agle din, kuch din baad, aur kuch hafton baad important questions dobara recall karo. Jis question mein atko, usko pehle revise karo.
- **Audio pause:** TTS mein har heading ke baad pause do. Formula ko pehle words mein suno, phir symbols dekho.
- **Interview memory:** “Purpose, flow, condition, connection, limitation” — har file explain karne ka yahi paanch-part formula yaad rakho.

### Code padhne ke basic shabd

- **Program:** Computer ko diya hua step-by-step kaam.
- **File:** Ek digital page jisme related code rakha hota hai.
- **Folder:** Related files rakhne ki jagah.
- **Function:** Naam diya hua chhota reusable kaam. Input leta hai, kaam karta hai, result deta hai.
- **Input:** Function ya app ko di hui information.
- **Output:** Kaam ke baad mila result.
- **Condition:** “Agar aisa hai, to yeh karo” wala decision.
- **Loop:** Ek kaam ko multiple values ke liye baar-baar karna.
- **Class:** Ek blueprint jo related data aur actions ko group karta hai.
- **Object:** Blueprint se bana actual item, jaise ek particular weather record.
- **API:** Do software ke beech request/response ka tay tareeka, jaise restaurant mein order dene ka counter.
- **JSON:** Text format jisme software data bhejte hain; naam-value pairs aur lists hote hain.
- **Dependency:** Kisi aur ke banaye package/tool par nirbhar code, jise project apna kaam karne ke liye use karta hai.
- **Test:** Chhota automatic sawaal jo dekhta hai ki code se ummeed wala behavior aaya ya nahi.
- **Adapter:** Translator jo bahari service ka format hamare project ke format mein badalta hai.
- **Cache:** Pehle mila result temporary yaad rakhna, taki same kaam ke liye baar-baar network call na ho.
- **Database:** Structured digital register jisme information save hoti hai.
- **Build:** Source code ko deploy/run karne layak output mein badalna.

---

## Part 1. Project ko ek minute mein samjho

### Ek sentence

**TruckerSafe ek weather-aware truck route planner hai. Yeh candidate road routes par expected weather aur truck ka load dekh kar fixed safety rules se risk nikalta hai, routes ko rank karta hai, aur map, timeline, checkpoints aur explanation dikhata hai.**

### Real-life kahaani

Dispatcher ko Chicago se Denver tak 40,000-pound ka samaan bhejna hai. Use bas “sabse chhota rasta” nahi chahiye. Use yeh jaan-na hai: truck route ke beech kab pahunchega, us waqt hawa/baarish/baraf kaisi hogi, bhaari samaan ke saath kaunsa rasta avoid karna chahiye, aur har route ke kitne miles kis risk mein hain.

TruckerSafe address ko map location banata hai, road service se route options mangta hai, route par weather checkpoints banata hai, arrival time ke forecast ko safety table se check karta hai, route ka risk summary banata hai, phir safe route ko rank 1 deta hai. Browser us result ko map aur tables mein dikhata hai.

### Kya yeh project AI se route decide karta hai?

Nahi. Code ke risk rules aur ranker final decision lete hain. Explainer calculate kiye gaye result ke baare mein insaan ko samajh aane wali line banata hai. Yaad rakhne ka vaakya: **“Algorithm faisla karta hai; explanation us faisle ko shabdon mein batati hai.”**

### Abhi project mein kya hai?

- React plus TypeScript frontend.
- Django plus Django REST Framework API.
- OSRM road-route adapter.
- Nominatim address geocoder.
- Open-Meteo forecast adapter.
- Checkpoint ETA, weather risk, route aggregation, route ranking, IDW heatmap, deterministic explainer.
- LocalStorage “My Trips” page and a Django `Trip` model.
- Demo fixture mode, test suites, CI, and deployment configuration.

Yeh codebase poore user flow wala prototype/application foundation dikhata hai. Production-ready hone ka matlab alag hai: hosted service sach mein chal rahi hai ya nahi, credentials/settings surakshit hain ya nahi, aur asli traffic/failures sambhale jaate hain ya nahi. Code dekh kar live deployment ki sehat ka daava is guide mein nahi kiya gaya hai.

---

## Part 2. Project ka mind map

```text
TRUCKERSAFE
|
|-- User interface: React + TypeScript
|   |-- Route form, route cards, interactive Leaflet map
|   |-- Forecast timeline and wind/rain/snow/risk layers
|   |-- Checkpoint details, explainer, saved trips
|   `-- One typed API request -> one plan response
|
|-- Django API
|   |-- Serializer request ko sahi ya galat check karta hai
|   |-- View kaam ka kram jodti aur errors sambhalti hai
|   `-- JSON response routes, checkpoints, heatmap aur explanation lautaata hai
|
|-- Python services
|   |-- Address -> coordinates: Geocoder
|   |-- Coordinates -> road options: OSRM adapter
|   |-- Road points -> checkpoints: geo helpers
|   |-- Checkpoint -> arrival weather: ETA + Open-Meteo
|   |-- Weather + load -> risk band: risk engine
|   |-- Bands -> risky miles: aggregation
|   |-- Routes -> best-to-worst: ranker
|   `-- Samples -> heatmap: IDW + builder
|
|-- Tests: backend pytest, frontend Vitest, Playwright E2E
|
`-- Run/deploy: settings, CI, Render backend, Vercel frontend
```

---

## Part 3. Flow Chapter: ek request ka poora safar

### Subchapter 3.1 — Normal request: form se route response tak

```text
1. User form mein origin, destination, departure, load aur interval bharta hai.
2. React client fields ko typed request object mein badalta hai.
3. Browser POST /api/route-plans request Django ko bhejta hai.
4. Serializer missing, invalid, ya unsafe request values reject karta hai.
5. Django view address geocode karata hai.
6. OSRM se up to 3 real road alternatives aate hain.
7. Har road line validate hoti hai; ek copy display ke liye simplify hoti hai.
8. Original route par 10, 25, ya 50 mile ke weather checkpoints bante hain.
9. Har checkpoint ko route par distance aur expected arrival time milta hai.
10. ETA ke ghante aur nearby location par Open-Meteo forecast liya jata hai.
11. Same rounded location/hour ke result ko request ke andar memory cache reuse karta hai.
12. Missing weather hua to checkpoint ko conservative NO_TRAVEL aur incomplete mark kiya jata hai.
13. Available weather hua to wind/rain/snow bands aur truck-load rules lagte hain.
14. Adjacent checkpoints ke beech poore segment ko worse endpoint risk milta hai.
15. Route risk miles aur distance-weighted average score calculate hote hain.
16. Routes safety priority se rank hote hain.
17. Recommended route ke aas-paas weather samples se heatmap grid banti hai.
18. Template explainer computed statistics ko words mein summarize karta hai.
19. Django chuna hua JSON jawab deta hai; React cards/map/tables par dikhata hai.
```

Step 11 ka cache per request hai: agli alag request par fresh dictionary banegi. Yeh durable/shared cache (Redis jaise) nahi hai.

### Subchapter 3.2 — “Agar / warna” condition aur error branches

- Agar request galat hai, API 400 deta hai; external provider call shuru nahi hota.
- Agar routes hi nahi mile, API 422 `no_routes_found` deta hai.
- Agar route/weather provider fail kare, API 503 deta hai.
- Agar weather measurement missing hai, unknown ko zero nahi bolte; code conservative `NO_TRAVEL` mark karta hai, aur checkpoint ko incomplete flag deta hai.
- Agar data available hai, worst weather band base risk hai; heavy wind plus load band ko aur badha sakta hai.
- Agar kisi route par zero se zyada no-travel miles hain, woh disqualified hota hai; qualified alternatives pehle rank hote hain.
- Agar koi anjaana server error ho, saamne generic 500 jawab aur server log milta hai.

---

## Part 4. Buniyadi Chapter: API aur frontend ke shabd

### Frontend kya hai?

User ke browser mein dikhne wala hissa. Is project mein React components form, route cards, map aur tables banate hain.

### Backend kya hai?

Server side ka hissa. Request validate karta hai, providers se data mangta hai, safety math karta hai, response banata hai.

### HTTP request aur response?

Browser backend ko request bhejta hai. Backend status code aur response data deta hai. POST ka matlab aam taur par server ko structured input bhejna.

### Serializer?

Gatekeeper. JSON request ka shape aur limits check karta hai, jaise load 1,000–80,000 lb, supported checkpoint interval, departure time future mein.

### DTO / data contract?

Fields ki tay suchi. Frontend `types.ts` batata hai request/response mein kaunse fields honge; backend serializer/view ko wahi format dena hota hai. Ek side field name badle aur doosri side na badle to connection toot sakta hai.

### React state?

UI ki abhi ki yaad, jaise chuni hui route, active map layer, loading sanket aur maujooda API result.

### LocalStorage?

Browser ke andar chhota persistent notebook. “My Trips” request inputs save karta hai. Browser storage clear ho to local trips bhi ja sakte hain.

### Leaflet?

Browser map library. Yeh map tiles, road lines, checkpoint pins aur image overlay draw karti hai.

---

## Part 5. Buniyadi Chapter: risk rules, formulas aur algorithm

### Five risk labels

```text
LOW = 1
MODERATE = 2
HIGH = 3
SEVERE = 4
NO_TRAVEL = 5
```

Number order isliye hai taki `max()` worst band choose kar sake. Number risk probability nahi hai. Score 4 ka matlab “4x danger” nahi; sirf ordered label hai.

### Wind thresholds

- Below 25 mph: LOW.
- 25 se below 35 mph: MODERATE.
- 35 se below 45 mph: HIGH.
- 45 se below 55 mph: SEVERE.
- 55 mph or above: NO_TRAVEL, any load.

### Rain thresholds

- Below 0.10 inch per hour: LOW.
- 0.10 se below 0.25: MODERATE.
- 0.25 se below 0.50: HIGH.
- 0.50 through exactly 1.00: SEVERE.
- Above 1.00: NO_TRAVEL.

### Snow thresholds

- Below 0.5 inch per hour: LOW.
- 0.5 se below 1.0: MODERATE.
- 1.0 se below 2.0: HIGH.
- 2.0 through exactly 3.0: SEVERE.
- Above 3.0: NO_TRAVEL.

### Load overrides

- Wind 55 or more: NO_TRAVEL for any load.
- Wind 45 to below 55 **and** load greater than 30,000 lb: NO_TRAVEL.
- Wind 35 to below 45 **and** load greater than 40,000 lb: risk at least SEVERE.
- “Greater than” strict hai. Exactly 30,000 or 40,000 lb us specific `>` condition ko satisfy nahi karta.

### One checkpoint example

Wind 38 mph means HIGH. Rain 0.05 means LOW. Snow 0 means LOW. Highest band HIGH hai. Agar cargo 42,000 lb hai, wind 35–44 aur load 40,000 se zyada hone ki wajah se final band SEVERE ho jayega.

### Haversine: Earth par distance

GPS coordinates Earth par hain, flat page par nahi. Haversine do locations ke beech curved Earth surface ka great-circle distance approximate karta hai.

```text
a = sin²(Δlatitude / 2)
    + cos(latitude 1) × cos(latitude 2) × sin²(Δlongitude / 2)

central angle = 2 × atan2(√a, √(1 − a))
distance in miles = Earth radius in miles × central angle
```

Degrees pehle radians bante hain, kyunki Python trigonometry radians use karti hai. Orange ke chilke par do dots ke beech dhaga kheenchne jaisa socho.

### ETA: arrival time estimate

```text
distance fraction = checkpoint distance / total route distance
checkpoint time = departure time + total route duration × distance fraction
```

Example: 200 minute route par 50 minute ke baad 25% distance mark par truck expected hai. Limitation: total duration ko route distance ke saath proportionally baanta gaya hai. Live traffic changes ya har road segment ki separate speed yahan calculate nahi hoti.

### Distance-weighted average risk

```text
average score = sum(segment miles × segment risk score) / total miles
```

Example: 10 miles LOW (score 1) and 10 miles SEVERE (score 4): `(10×1 + 10×4) / 20 = 2.5`. Zyada lamba segment average ko zyada affect karta hai.

### IDW heatmap

IDW ka full name Inverse Distance Weighting hai. Nearby sample grid cell ko zyada influence karta hai; far sample kam.

```text
weight = 1 / distance^power
estimated value = sum(weight × sample value) / sum(weights)
```

Is heatmap mein `power=2` aur adhiktam 8 nazdeeki samples use hote hain. Bilkul sample location par usi jagah ki value lagti hai. Beech ke rang andazati hain; woh naye asal weather readings nahi aur route safety ranking ka aadhar nahi.

---

## Part 6. Backend Chapter: har file ka kaam aur connection

Har file ko sunte waqt yeh paanch cheezein pakdo: **Purpose. Input/output. Conditions. Connects to. Interview question.**

### Subchapter 6.1 — Python dependencies aur Django start/config

Is subchapter mein `requirements.txt`, `manage.py`, Django settings, URL routing aur WSGI/ASGI entry points hain.

#### `backend/requirements.txt`

**Purpose:** Python packages ki dependency list.

**Kyun har package hai:**

- `Django`: web server framework, settings, route URLs, database tools.
- `djangorestframework`: JSON API view aur jawab banane ka framework.
- `django-cors-headers`: allowed browser frontend origins control.
- `requests`: OSRM aur Open-Meteo ko HTTP calls.
- `geopy`: Nominatim geocoding client.
- `numpy`: heatmap ke large number grids par vector math.
- `gunicorn`: production mein WSGI web server chalane ka process.
- `whitenoise`: Django static/admin assets serve karne ka simple option.
- `pytest`: automatic Python tests.

**Condition check:** Yeh file runtime par `if/else` decision nahi leti. Package install karte waqt Python version aur listed version limits compatible hone chahiye; incompatibility aaye to installation ruk sakti hai.

**Connects to:** backend source imports, `render.yaml` deployment install command, aur `.github/workflows/ci.yml` test environment.

**Interview:** “Dependency list kyun?” Jawab: “Taaki har environment mein project ke required packages ek jaise install hon. Main har package ko uske actual import ya server/test use se justify karta hoon.”

#### `backend/manage.py`

**Purpose:** Django commands ka front door. `runserver`, `migrate`, `check`, `collectstatic` isi se chalaye jaate hain.

**Flow:** settings module ka naam set karta hai, Django command runner import karta hai, command-line arguments pass karta hai.

**Condition check:** Command chalne par Python environment mein Django install hona chahiye; warna Django command runner import nahi hoga. Kaunsi action hogi yeh terminal argument, jaise `runserver` ya `migrate`, decide karta hai.

**Connects to:** `config/settings.py` configuration deta hai. Interview mein farq: `manage.py` developer commands chalata hai; hosted Gunicorn app ko `config.wsgi.application` se load karta hai.

#### `backend/config/__init__.py`

**Purpose:** `config` ko Python import package banata hai. Empty marker, business logic nahi.

**Condition check:** Koi runtime/business condition nahi. Yeh Python ko `config` folder se modules import karne deta hai.

**Connects to:** `settings.py`, `urls.py`, `wsgi.py` aur `asgi.py` isi package ke modules hain.

#### `backend/config/settings.py`

**Purpose:** Django app ka central configuration panel.

**Kaam:** environment variables se DEBUG, secret key, allowed hosts aur CORS origins padhta hai; Django apps/middleware register karta hai; SQLite database, UTC timezone, static files, DRF JSON renderer, pagination, logging, geocoder user-agent aur production HTTPS/security options set karta hai.

**Condition check:** `DEBUG` true/false, environment variable available/missing, allowed host request host mein hai/nahin, aur CORS origin allowed list mein hai/nahin—settings in values ke mutabik behavior configure karti hain. Production (`DEBUG=false`) mein secret key required hai; secure cookies, HTTPS redirect, HSTS aur security headers on hote hain.

**Zaroori baat:** secret key private random setting hai; production mein asli secret source code mein nahi rakhna chahiye. Fallback key sirf development ke liye hai.

**Connects to:** `manage.py`, `urls.py`, DRF, WhiteNoise, CORS middleware, database aur Render environment.

**Interview:** “Environment variables kyun?” Jawab: “Local, test aur hosted environment ki settings alag rakhi ja sakti hain, bina source code edit kiye aur private secret ko Git mein daale.”

#### `backend/config/urls.py`

**Purpose:** incoming URL ko correct function/view tak bhejne wali root directory.

**Routes:** Django admin, `/healthz/`, included `/api/v1/` routes, and `/api/route-plans/` plus slashless alias.

**Condition check:** Request ka URL kis pattern se match hota hai, uske hisaab se alag view chalega. Unknown URL ko Django not-found response deta hai. Health endpoint sirf server ke zinda/responding hone ko check karta hai.

**Health check:** `/healthz/` `{status: ok}` bhejta hai. Yeh sirf batata hai ki server jawab de raha hai; OSRM ya weather provider chal rahe hain, iska proof nahi.

**Connects to:** `route_plan` API view aur Render health-check setting.

#### `backend/config/wsgi.py`

**Purpose:** synchronous Django application ko Gunicorn/WSGI server se connect karta hai. WSGI ek web server handshake standard hai.

**Condition check:** Startup ke waqt Django settings/import valid hone chahiye; error aaye to application server start nahi kar pata. Is file mein request-level business conditions nahi hain.

**Connects to:** `render.yaml` ka Gunicorn startup command aur Django settings.

**Interview:** “Production kaunse module ko start karta hai?” `render.yaml` mein `gunicorn config.wsgi:application` command diya gaya hai.

#### `backend/config/asgi.py`

**Purpose:** ASGI-compatible Django application entry point. ASGI async-capable server protocol hai. Current Render command WSGI/Gunicorn use karta hai; ASGI file alternate entry point hai.

**Condition check:** ASGI server ise tabhi use karega jab uska startup command is application ko point kare. Current Render command WSGI use karta hai, isliye normal deployment path mein yeh active entry point nahi.

**Connects to:** Django settings aur future ASGI-compatible server; current `render.yaml` WSGI path use karta hai.

### Subchapter 6.2 — Routing app, database blueprint aur API gate

Is subchapter mein Django app registration, `Trip` model/migration, API URL, request validation aur HTTP view hain.

#### `backend/apps/__init__.py`

**Purpose:** top-level `apps` package marker. Empty; calculations nahi karta.

**Condition check:** Koi runtime/business condition nahi; import package banane ka marker hai.

**Connects to:** `apps.routing` package aur Django app configuration.

#### `backend/apps/routing/__init__.py`

**Purpose:** routing Django app package marker.

**Condition check:** Koi runtime/business condition nahi; yeh folder ko importable package banata hai.

**Connects to:** `apps.py`, `models.py`, `api` aur `services` subpackages.

#### `backend/apps/routing/apps.py`

**Purpose:** Django ko routing app ka name and default database ID type batata hai. Django startup par config load karta hai.

**Condition check:** Django startup par app ko `INSTALLED_APPS` mein listed hona chahiye; tabhi Django is configuration ko load karta hai. Is file mein route safety decision nahi.

**Connects to:** `settings.py` ke `INSTALLED_APPS`, aur isi app ke models/API/services.

#### `backend/apps/routing/models.py`

**Purpose:** database mein trip record ka blueprint `Trip` define karta hai: origin, destination, departure, load, interval, created time, saved JSON response.

**Condition check:** Model ke field types aur database constraints save ke waqt values ki shape/limits ko control kar sakte hain. Sirf model hone se record save nahi hota; API ko explicitly save call karna hota hai.

**Connects to:** `0001_initial.py` table banane ka migration batati hai. Inspected route API `Trip` ko create/read/delete nahi karti; frontend “My Trips” browser LocalStorage use karta hai. Model available hai, par user-facing database save connection maujood nahi dikhta.

**Interview:** “Model hone ka matlab trip database mein save ho raha hai?” Jawab: “Nahi. Model structure deta hai; view/service ko save call bhi karna hota hai. Is project ka UI LocalStorage use karta hai.”

#### `backend/apps/routing/migrations/__init__.py`

**Purpose:** migration folder ka marker. Empty.

**Condition check:** Koi runtime/business condition nahi; Python package marker hai.

**Connects to:** isi folder ki numbered migration files ko Django discover karne deta hai.

#### `backend/apps/routing/migrations/0001_initial.py`

**Purpose:** Django ko database table banane ke steps deta hai for `Trip`.

**Condition check:** Django migration status dekhta hai: agar migration pehle apply nahi hui to apply karta hai; already applied ho to dobara table create nahi karta.

**Analogy:** database ke liye blueprint-to-construction instructions. `manage.py migrate` in steps ko database par apply karta hai.

**Connects to:** `models.py` ke `Trip` fields aur Django database configuration.

#### `backend/apps/routing/api/__init__.py`

**Purpose:** API package marker. Empty.

**Condition check:** Koi runtime/business condition nahi; import package marker hai.

**Connects to:** isi folder ke `urls.py`, `serializers.py` aur `views.py`.

#### `backend/apps/routing/api/urls.py`

**Purpose:** routing API ke sub-paths define karta hai. `route-plans/` ko `route_plan` view se connect karta hai.

**Condition check:** URL path aur HTTP method alag checks hain: path is file mein match hota hai; POST-only rule `route_plan` view mein apply hota hai.

**Connects to:** root `config/urls.py` `/api/v1/` prefix ke saath is file ko include karta hai. Root config ke aliases frontend ke `/api/route-plans` path se bhi match karte hain.

#### `backend/apps/routing/api/serializers.py`

**Purpose:** request gatekeeper and normalizer.

**Input se output:** incoming JSON fields ko validate karke trusted Python values deta hai; galat value par readable validation error deta hai.

**Expected fields:** origin, destination, ISO departure time, load pounds, interval.

**Condition check:** address khaali/120 characters se lamba to reject; load integer 1,000–80,000 ke bahar to reject; interval 10/25/50 ke alawa ho to reject; departure past mein ya 120-hour forecast window se bahar ho to reject; origin aur destination capitalization ignore karne ke baad same hon to reject.

**Dono jagah validation kyun?** Browser jaldi feedback deta hai, lekin doosra client browser checks ko bypass kar sakta hai. Isliye server ko apni validation khud karni hi chahiye.

**Connects to:** `views.py` ise provider call se pehle chalata hai; frontend `types.ts` request shape batata hai, lekin asli bharosa server validation par hai.

**Interview:** “Serializer kya protect karta hai?” Jawab: “Galat ya missing input ko business logic aur external providers tak pahunchne se rokta hai, phir normalized Python values deta hai.”

#### `backend/apps/routing/api/views.py`

**Purpose:** HTTP request ka conductor. Serializer call karta hai, service steps connect karta hai, errors ko HTTP status mein map karta hai, aur response ko public contract tak filter karta hai.

**Input se output:** POST request leta hai; success par route plan JSON, aur failure par uske anuroop HTTP status/error JSON deta hai.

**Important functions:**

- `_coordinate_list`: GeoJSON `[longitude, latitude]` ko internal `(latitude, longitude)` list mein badal kar geometry validate karta hai.
- `_scaled_checkpoint_distances`: geometry-based cumulative distance ko OSRM road distance se scale karta hai; last point exact route distance banta hai. Beech ke values estimates hain.
- `_hour_bucket`: timezone-aware ETA ko UTC hour start mein round down karta hai.
- `_get_hourly_weather`: exact hour forecast mangta hai; same rounded lat/lon and hour cache key reuse karta hai. Provider error ko missing result ke roop mein log/cache karta hai.
- `_evaluate_checkpoint`: weather missing/incomplete hua to conservative `NO_TRAVEL`, missing fields list, and incomplete flag. Complete values hue to `classify_checkpoint` call.
- `_analyze_route`: route length/duration validates; polyline simplify; requested interval par checkpoints; checkpoint distances and ETAs; each ETA par weather/risk; risk aggregation; frontend checkpoint and route summaries.
- `plan_routes`: Geocoder, OSRM and Open-Meteo clients open; endpoints geocode; max 3 alternatives request; each route analyze; rank; integer IDs/reasons; heatmap samples/builder; explainer. `ExitStack` clients cleanup karta hai even if error aaye.
- `route_plan`: POST-only DRF endpoint. Invalid body 400; no routes 422; provider failure 503; unexpected error 500; success 200.

**Condition check, poora decision flow:** pehle HTTP method POST hai ya nahi; phir serializer input valid karta hai; phir address resolve hote hain; phir road alternatives mile ya nahi; phir provider call safal hai ya nahi; har checkpoint par weather complete hai ya missing; aakhir mein routes rank hote hain. Har failure branch apna status code banata hai.

**Bahut zaroori rule:** missing weather ko zero ya safe nahi maana jata. Lekin response mein checkpoint display fields `None` ko `0.0` bana kar bhej sakte hain, saath mein `incomplete_data` warning hoti hai. UI ko is warning ka samman karna chahiye; zero ko naapey hue shaant/sukhe weather ka proof na samjhein.

**Dhyan dene layak contract gap:** backend checkpoint response mein `incomplete_data` aa sakta hai; TypeScript ka `Checkpoint` type ise abhi declare nahi karta aur dikhne wali table bhi nahi dikhati. Driver ko missing weather samajh aaye, isliye frontend contract/UI ko behtar karna agla kaam ho sakta hai.

**Doosri seema:** local cache dictionary ek `plan_routes` run tak hi rehti hai; doosri request/user tak save nahi hoti.

**Connects to:** serializer, geocoder, OSRM/weather adapters, geo/risk/heatmap/recommend services, phir frontend `client.ts`.

**Interview:** “Kya view thin hai?” Jawab: “Yeh orchestration boundary hai, isliye chhoti single-purpose view se badi hai. Yeh adapters aur domain services ko jodti, failures ko translate karti aur public response banati hai. Aage orchestration ko planner service mein nikaal kar view ko HTTP par focused rakha ja sakta hai.”

### Subchapter 6.3 — Route providers aur raaste ki geometry

Is subchapter mein address lookup, OSRM route options, GPS distance, checkpoints, display simplification aur ETA ke helpers hain.

#### `backend/apps/routing/services/__init__.py`

**Purpose:** shared services package marker. Empty.

**Condition check:** Koi runtime/business condition nahi; shared service modules import karne ke liye package marker hai.

**Connects to:** routing, geo, weather, risk, heatmap aur recommend subpackages.

#### `backend/apps/routing/services/routing/__init__.py`

**Purpose:** routing helper package marker. Empty.

**Condition check:** Koi runtime/business condition nahi; Python import marker hai.

**Connects to:** `base.py`, `geocoder.py`, `osrm_adapter.py` aur `eta.py`.

#### `backend/apps/routing/services/routing/base.py`

**Purpose:** route data contract, shared errors, coordinate validation, provider interface.

**Condition check:** coordinate mein do finite numeric values honi chahiye; latitude -90 se 90 aur longitude -180 se 180 ke beech; alternatives integer 1 se 10 ke beech.

**Connects to:** `geocoder.py` aur `osrm_adapter.py` iske domain errors use karte hain; `RouteDict` sab providers ka output ek jaise shape mein rakhta hai.

#### `backend/apps/routing/services/routing/geocoder.py`

**Purpose:** insaan ke likhe address ko Nominatim/geopy ki madad se `(latitude, longitude)` GPS location mein badalna.

**Flow:** extra spaces saaf karta hai; length, language/country code aur pehchan dene wale user-agent ko check karta hai; seemit LRU cache dekhta hai; provider request ke beech zaroori gap rakhta hai; provider se address poochta hai; timeout, rate limit, address na milna ya invalid coordinate ko project error mein badalta hai; valid jawab cache karta hai.

**Condition check:** address 2–500 characters; returned coordinate legal GPS range mein; cache size zero ho to cache band; country codes comma-separated do-letter ASCII format mein.

**Connects to:** `views.py` ka `plan_routes` ise banata hai; iske GPS coordinates `OSRMAdapter` ko diye jaate hain.

**Interview:** “Rate limiter aur cache kyun?” Jawab: “Public provider ki request limit ka samman karne aur same address ko baar-baar lookup se bachane ke liye. Cache key mein language aur country bhi hote hain, kyunki unse address ka meaning badal sakta hai.”

#### `backend/apps/routing/services/routing/osrm_adapter.py`

**Purpose:** OSRM se road ke doosre options mangna aur unhe project ke ek saman route format mein badalna.

**Flow:** input validate karta hai; andar ke lat/lon ko OSRM URL ke lon/lat kram mein badalta hai; driving options aur poori GeoJSON line mangta hai; HTTP jawab, timeout, JSON aur OSRM status check karta hai; har route ke coordinates/distance/duration validate karta hai; normalized routes lautaata hai.

**Condition check:** start aur destination same nahi; provider maangi hui sankhya se kam routes de sakta hai; code nakli extra routes nahi banata; timeout, HTTP error, malformed response aur closed session handle hote hain.

**Connects to:** `RoutingProvider` contract follow karta hai; route results `views.py` aur `eta.py` ko jaate hain.

**Interview:** “Coordinates mein aam galti kya hoti hai?” Jawab: “App tuple mein pehle latitude phir longitude; GeoJSON mein pehle longitude phir latitude. Adapter isi kram ko saaf taur par badalta hai.”

#### `backend/apps/routing/services/routing/eta.py`

**Purpose:** checkpoints ko road line par rakhkar unki route par ab tak ki distance aur pahunchne ka andazati samay nikalna.

**Algorithm:** har road point tak ki jodi hui haversine miles nikalta hai. Har checkpoint ko paas ke road segments par project karta hai; sabse nazdeek segment chunta hai; segment ka kitna hissa paar hua, usse checkpoint ki route position andazta hai. ETA = route distance ka hissa × poore route ka samay.

**Condition check:** GeoJSON points valid; distance/duration positive; checkpoint list khaali nahi; GPS points valid aur default roop se route se 1 mile ke andar; route par unka order aage ki taraf ho; departure mein timezone ho; geometry aur declared route distance bahut alag na hon.

**Limitation:** poore route ki average speed ke hisaab se anuman hai; har road ke live traffic ka alag forecast nahi.

**Connects to:** OSRM ka `RouteDict`, `haversine_distance` aur `views.py` ke checkpoints/departure.

**Interview:** “Checkpoint ko route par project kyun karte ho?” Jawab: “Sample coordinate ko route ke mile-marker se jodna zaroori hai. Nazdeeki segment par projection se distance aur ETA dono ka anuman milta hai.”

#### `backend/apps/routing/services/geo/__init__.py`

**Purpose:** geography package marker. Empty.

**Condition check:** Koi runtime/business condition nahi; geography helper files ko importable package banata hai.

**Connects to:** `haversine.py`, `resampler.py` aur `simplify.py`.

#### `backend/apps/routing/services/geo/haversine.py`

**Purpose:** Earth ke ghumav ko dhyan mein rakhkar do GPS points ke beech miles nikalna.

**Condition check:** floating-point intermediate ko legal range mein clamp kiya jata hai, taki rounding ki wajah se square root/angle calculation invalid na ho.

**Connects to:** route resampler, ETA projector, view distance scaling aur heatmap route-distance logic.

**Interview:** “Seedha Pythagoras kyun nahi?” Jawab: “GPS coordinates Earth ki curved surface par hain. Great-circle distance us ghumav ko dhyan mein rakhta hai.”

#### `backend/apps/routing/services/geo/resampler.py`

**Purpose:** route ka start/end bachana aur poore road ke saath niyamit miles par checkpoints banana.

**Flow:** positive interval aur GPS points check karta hai; har road tukde ki doori naapta hai; paas-paas ke duplicate points chhodta hai; agla target mile jis segment ke andar aaye, Earth ke arc par beech ka coordinate nikalta hai; aakhir mein exact destination jodta hai.

**Condition check:** interval finite aur zero se bada; lat/lon legal geographic range mein; lagbhag globe ke ulte taraf wale do points reject, kyunki beech ka shortest path ambiguous ho sakta hai.

**Connects to:** `haversine.py` use karta hai; weather check se pehle route view ise call karti hai.

**Interview:** “Provider ke har point ko checkpoint kyun nahi banate?” Jawab: “Provider ke points ki density alag ho sakti hai. Distance-based checkpoints 10, 25 ya 50 miles par predictable weather sampling dete hain.”

#### `backend/apps/routing/services/geo/simplify.py`

**Purpose:** map par dikhane wali route line se bekaar points hatana, par asli mod bachaye rakhna.

**Algorithm:** Douglas–Peucker tareeka baar-baar lagta hai. Shuru aur aakhri point rakhta hai; seedhi line se sabse door beech ka point dhoondhta hai; uska antar tolerance se zyada ho to point rakhta aur line ko do hisson mein baantta hai; phir dohrata hai. Sab points tolerance ke andar hon to beech ke points hata deta hai.

**Condition check:** tolerance finite aur zero ya positive; coordinates valid; tolerance zero ho to sabhi points bachaye jaate hain. Date line ke paas longitude ka chhota direction liya jata hai; local flat projection ki wajah se distance approximate hota hai.

**Connects to:** `views.py` simplified geometry frontend display ko bhejti hai; checkpoint analysis original route par hoti hai.

**Interview:** “Simplified route aur checkpoint route alag kyun?” Jawab: “Map jaldi draw karne ke liye kam points chahiye; risk ke liye asal route geometry chahiye. Simplification sirf display ko halka karti hai, safety data ko badalti nahi.”

### Subchapter 6.4 — Weather provider aur forecast samay

Is subchapter mein common weather format, Open-Meteo adapter aur forecast time lookup/interpolation hai.

#### `backend/apps/routing/services/weather/__init__.py`

**Purpose:** weather package marker. Empty.

**Condition check:** Koi runtime/business condition nahi; weather modules ko importable package banata hai.

**Connects to:** `base.py`, `open_meteo_adapter.py` aur `interpolation.py`.

#### `backend/apps/routing/services/weather/base.py`

**Purpose:** sab weather providers ke liye ek jaisa record, units, rules, input validation aur weather-specific errors dena.

**`HourlyWeather`:** samay ke saath wind mph, baarish inches aur baraf inches rakhta hai. `None` ka matlab reading nahi mili, zero reading nahi. Frozen record banne ke baad galti se badla nahi ja sakta.

**Condition check:** timestamp timezone-aware ho; readings finite, nonnegative ya `None` hon; GPS bounds sahi hon; forecast period 1 ghante se 14 din ke beech ho. `None` ka matlab reading missing hai, zero nahi.

**Connects to:** Open-Meteo adapter yeh model return karta hai; interpolation aur route evaluation ise use karte hain.

**Interview:** “Weather provider ka common contract kyun?” Jawab: “Naya vendor lagaya ja sakta hai agar woh wahi normalized record aur validation rules follow kare. Isse vendor badalne par baaki code kam badalta hai.”

#### `backend/apps/routing/services/weather/open_meteo_adapter.py`

**Purpose:** Open-Meteo se har ghante ka forecast mangna aur uske jawab ko project format mein badalna.

**Flow:** base contract se coordinate/samay validate karta hai; provider query banata hai; timeout ke saath HTTP request karta hai aur asthayi error par retry karta hai; jawab ka format aur arrays ki lambai check karta hai; timestamp/units ko sorted `HourlyWeather` records mein badalta hai; missing value `None` hi rakhta hai; apna session band karta hai.

**Condition check:** provider JSON shape aur arrays ki lengths match; timestamps unique aur orderable; readings finite aur zero se kam nahi; retry sirf temporary failure status par hota hai.

**Connects to:** `WeatherProvider` contract follow karta hai; view checkpoint location aur ETA-hour range ke liye ise call karti hai.

**Interview:** “Bahar se aaye data ko validate kyun?” Jawab: “Remote API fail ho sakti hai, badal sakti hai ya adhura data de sakti hai. Adapter kacche, avishvasniya JSON ko seedha safety calculation tak jaane se rokta hai.”

#### `backend/apps/routing/services/weather/interpolation.py`

**Purpose:** checkpoint ke exact samay ka forecast lena, ya do forecast samayon ke beech hawa ka anuman lagana.

**Input se output:** sorted weather records aur target time leta hai; exact forecast record ya do records ke beech estimated wind deta hai.

**Algorithm:** forecast times ko UTC mein ek jaisa karta hai; samay sakhti se aage ke kram mein hone chahiye; binary search se target time dhoondhta hai; exact match par record lautaata hai; beech ke samay par wind ko seedhe anupat se andazta hai; range ke bahar ho to reject karta hai.

**Condition check:** records time ke hisaab se strictly aage badhein; exact time mile to wahi record; time beech mein ho to sirf wind interpolate; available forecast ke bahar ho to reject. Rain/snow ko minute ke hisaab se baantne ki koshish nahi hoti.

**Baarish ya baraf ka beech ka reading kyun nahi andazte?** Yeh ek ghante ka kul amount hai, ek pal ki reading nahi. Use minute-minute baantna aisa jhootha naap banana hoga jo provider ne diya hi nahi.

**Connects to:** `HourlyWeather` par nirbhar hai; current `views.py` exact forecast hour dhoondhti hai, isliye yeh helper aaj ke main request path mein call nahi hota.

**Interview:** “Binary search kya hai?” Jawab: “Sorted list mein beech ka item dekhkar aadhi list chhod dete hain; phir bachi aadhi mein wahi dohrate hain. Isliye har record ek-ek karke dekhne se jaldi result mil sakta hai.”

### Subchapter 6.5 — Checkpoint safety aur route risk summary

Is subchapter mein ek checkpoint ka risk label aur kai checkpoints ko route-mile summary mein badalne ka kaam hai.

#### `backend/apps/routing/services/risk/__init__.py`

**Purpose:** risk package marker. Empty.

**Condition check:** Koi runtime/business condition nahi; risk service modules ke liye package marker hai.

**Connects to:** `engine.py` aur `aggregation.py`.

#### `backend/apps/routing/services/risk/engine.py`

**Purpose:** ek checkpoint ki hawa, baarish, baraf aur samaan ke bhaar ko niyamit risk label mein badalna.

**Input se output:** ek checkpoint ka weather aur load leta hai; risk label, jaise `HIGH` ya `NO_TRAVEL`, aur decision metadata deta hai.

**Flow:** har weather cheez ka risk alag nikalta hai; sabse kharab label chunta hai; hawa aur load ke rules lagata hai; final label aur uske peeche ka kaaran deta hai.

**Condition check:** weather input complete aur valid ho tabhi call karein. Har hazard ka band alag check hota hai; sabse bada band base hota hai; wind ke saath load thresholds satisfy hon to risk aur badhta ya `NO_TRAVEL` hota hai.

**Connects to:** view ise sirf complete weather par chalati hai; `aggregation.py` returned band ke miles ginegi.

**Interview:** “Wind, rain aur snow mein worst band kyun lete ho?” Jawab: “Har hazard akela unsafe ho sakta hai. Ordered labels mein sabse bada band lena conservative, samajhne layak aur testable rule hai.”

#### `backend/apps/routing/services/risk/aggregation.py`

**Purpose:** checkpoint risk list ko poore route ke risk-miles aur average score mein badalna.

**Input se output:** route ke ordered checkpoints leta hai; har risk level mein miles aur distance-weighted average score return karta hai.

**Flow:** kam-se-kam do checkpoints, zero se shuru distance aur aage badhta kram check karta hai; har segment ke dono ends mein worse band chunta hai; us band mein segment ke miles jodta hai; score ko miles se guna karke jodta hai; total ko poori distance se divide karta hai; aakhir mein risk buckets ke miles ka sum route length se milata hai.

**Condition check:** distances finite aur nonnegative; band pehchana hua; cumulative distance peeche na jaye; optional route distance last checkpoint ke saath milti-julti ho; kam-se-kam do checkpoints hon aur shuruat zero se ho.

**Connects to:** view ke checkpoint outputs aur risk labels leta hai; result `ranker.py` aur UI ko jaata hai.

**Interview:** “Do checkpoints ke beech worse risk kyun lagate ho?” Jawab: “Truck dono samples ke beech se guzarta hai. Worse endpoint dene se beech ke miles ko bina proof safe nahi kehte.”

### Subchapter 6.6 — Heatmap ke samples aur grid banana

Is subchapter mein IDW formula aur usse map ke rang banane wala builder hai. Yeh display estimation hai, route rank nahi.

#### `backend/apps/routing/services/heatmap/__init__.py`

**Purpose:** heatmap package marker. Empty.

**Condition check:** Koi runtime/business condition nahi; heatmap helper modules ko package banata hai.

**Connects to:** `idw.py` aur `builder.py`.

#### `backend/apps/routing/services/heatmap/idw.py`

**Purpose:** NumPy ka use karke IDW naam ki dobara istemal hone wali interpolation math chalana.

**Input se output:** sample coordinates/values aur map grid leta hai; har grid cell ke liye estimated value deta hai.

**Flow:** power, tolerance, kitne nazdeeki samples lene hain aur chunk size validate karta hai; galat samples hataata hai; 2D coordinate grid check karta hai; cells ko chhote groups mein baantta hai; sample doori nikalta hai; exact match ho to wahi value leta hai, warna distance ke ulte power ke mutabik weighted average leta hai.

**Condition check:** invalid/missing sample hatao; usable sample na ho to `NaN`; exact sample par wahi value; `k` set ho to sirf paas ke limited samples; chunk size temporary memory limit karta hai.

**Connects to:** `builder.py` wind, rain aur snow ke liye ise alag-alag chalata hai.

**Interview:** “Grid ko chunks mein kyun chalate hain?” Jawab: “Har cell aur har sample ka distance ek saath rakhne se memory bahut lag sakti hai. Chhote groups temporary memory ko limit karte hain.”

#### `backend/apps/routing/services/heatmap/builder.py`

**Purpose:** route aur weather samples ko map par dikhane layak hawa/baarish/baraf grids mein badalna.

**Input se output:** route aur checkpoint weather leta hai; JSON response ke andar browser-drawable grid return karta hai.

**Flow:** route coordinates validate karta hai; aas-paas jagah chhodkar bounding box banata hai; lagbhag 0.08-degree grid banata hai; har weather layer ko 8 tak nazdeeki samples se andazta hai; route se 150 km se door cells chhupata hai; numbers round/flatten karta hai; unavailable `NaN` ko JSON `null` banata hai.

**Condition check:** coordinates invalid hon to reject; route corridor se 150 km se zyada door ke cells mask; missing estimate JSON mein `null`; grid bounds aur size request ke hisaab se limited.

**Connects to:** `views.py` ke complete checkpoint weather samples leta hai; frontend `MapView.tsx` response grid ko colors deta hai.

**Limit:** local display mein coordinate math approximate aur rang estimated hain. Heatmap sirf dikhane ke liye hai; risk score niyamit checkpoint rules aur aggregation se aata hai.

**Interview:** “Route corridor ke bahar mask kyun?” Jawab: “Door ke unobserved area ke liye reliable weather ka jhootha impression na bane aur bheji hui grid route ke paas focused rahe.”

### Subchapter 6.7 — Route chunna aur uska reason batana

Is subchapter mein deterministic route ranking aur ranked result ka explanation hai.

#### `backend/apps/routing/services/recommend/__init__.py`

**Purpose:** recommendation package marker. Empty.

**Condition check:** Koi runtime/business condition nahi; recommendation modules ka package marker hai.

**Connects to:** `ranker.py`, `templates.py` aur `explainer.py`.

#### `backend/apps/routing/services/recommend/ranker.py`

**Purpose:** candidate routes ko safety-first deterministic order mein sort karta hai.

**Input se output:** route summaries leta hai; sorted copy aur recommendation order return karta hai.

**Priority:** pehle surakshit/eligible routes; phir kam `NO_TRAVEL` miles, kam `SEVERE` miles, kam `HIGH` miles, kam average score, aur aakhir mein kam duration.

**Key idea:** lexicographic ka matlab hai pehla field pehle compare; barabar ho tabhi agla field dekho. Yeh aisa mila-jula score nahi jahan tez samay kisi `NO_TRAVEL` risk ko hara sake.

**Condition check:** sab ranking fields maujood, numeric, finite aur nonnegative; no-travel miles zero se zyada hon to route disqualified; exact tie par stable order bacha rehta hai.

**Connects to:** `views.py` ka `plan_routes` analyzed routes ko sort karke public IDs lagata hai.

**Interview:** “Weighted sum kyun nahi?” Jawab: “Weighted sum mein speed ke points severe risk ko chhupa sakte hain. Lexicographic order mein pehle safety priority saaf-saaf compare hoti hai.”

#### `backend/apps/routing/services/recommend/templates.py`

**Purpose:** recommended route ke calculate kiye metrics ko tay, facts par aadharit heading aur bullet text mein badalna.

**Input se output:** pehle se calculate route facts leta hai; headline aur bullet list banata hai.

**Flow:** route ID, average risk, severe/no-travel miles, duration aur load padhta hai; heading banata hai; disqualified route mile to uska reason jodta hai; warna batata hai ki eligible routes ko risk-miles par compare kiya gaya.

**Condition check:** agar disqualified route mile to reason dikhata hai; warna eligible routes ke risk-mile comparison ko explain karta hai. Yeh route ko rank ya recalculate nahi karta.

**Connects to:** `explainer.py` ise call karta hai; final text frontend panel ko milta hai.

#### `backend/apps/routing/services/recommend/explainer.py`

**Purpose:** explanation service entry point. Abhi yeh template generator ko kaam deta hai; is file mein external LLM API call nahi hai.

**Condition check:** is implementation mein explanation deterministic template se banti hai; LLM configured nahi hai. Required input facts hon tabhi unka summary ban sakta hai.

**Connects to:** `templates.py` aur API response; ranking par iska control nahi.

**Interview:** “Kya AI route decide karta hai?” Jawab: “Nahi. Ranked route ke baad fixed template explanation banata hai; decision rules aur ranker karte hain.”

---

## Part 7. Frontend Chapter: screen, state aur file connections

### Subchapter 7.1 — Frontend package, build/test setup aur browser entry

Is subchapter mein dependencies, HTML shell, Vite/TypeScript/test settings aur React entry point hain.

#### `frontend/package.json`

**Purpose:** frontend project identity, scripts and JavaScript package list.

**Condition check:** scripts tabhi chalenge jab required packages install hon aur environment mein Node.js/npm available ho. Development, test aur build scripts alag kaam karte hain.

**Dependencies kyun:** React/ReactDOM screen banate hain; Leaflet map banata hai. Developer tools mein Vite server/build, TypeScript checker, Vitest unit tests, Testing Library/jsdom UI tests aur Playwright browser automation chalate hain.

**Connects to:** `package-lock.json` exact package versions lock karta hai; CI aur local npm commands yahan ke scripts/dependencies use karte hain.

**Interview:** “React kyun?” Jawab: “Dashboard reusable components mein banta hai. Request result, selected route ya map layer badalne par zaroori screen dobara update ho sakti hai.”

#### `frontend/package-lock.json`

**Purpose:** packages ke exact tree ko lock karna. CI mein `npm ci` isi file se wahi versions install karta hai.

**Condition check:** `npm ci` ko is lock file aur `package.json` ka aapas mein match karna zaroori hai; mismatch ho to install fail ho sakta hai.

**Connects to:** `frontend/package.json` ke direct aur indirect packages; GitHub CI isi se exact install karta hai.

#### `frontend/index.html`

**Purpose:** browser page ka khaaka. Ismein root jagah hoti hai jahan React app lagta hai, saath hi page ki metadata.

**Condition check:** `main.tsx` jis `root` element ko dhoondhta hai, woh HTML mein hona chahiye; missing ho to React mount nahi kar payega.

**Connects to:** `src/main.tsx` isi page ke root element mein app lagata hai.

#### `frontend/vite.config.ts`

**Purpose:** Vite development server ki settings. React plugin JSX ko browser ke layak banata hai; dev server port 5173 par chalta hai aur `/api` request Django ke port 8000 ko bhejta hai.

**Condition check:** `/api` path ko proxy kiya jata hai; baaki frontend paths Vite serve karta hai. Backend port par Django chal raha ho to proxy request us tak pahunchti hai.

**Connects to:** React plugin, local frontend server aur Django development server.

**Interview:** “Development proxy kyun?” Jawab: “Har component mein backend host hardcode kiye bina frontend wahi `/api` path call karta hai; Vite local request Django tak bhejta hai.”

#### `frontend/tsconfig.json`

**Purpose:** TypeScript compiler ke options aur project references dena. Production build se pehle galat type pakadne mein madad karta hai.

**Condition check:** compiler settings ke mutabik invalid type/import/build error milne par TypeScript build fail hota hai; types ka hona runtime JSON ko validate nahi karta.

**Connects to:** frontend `.ts`/`.tsx` files aur Vite build/check scripts.

#### `frontend/vitest.config.ts`

**Purpose:** unit/component test chalane ki settings. Browser jaise `jsdom`, setup helper aur React plugin use karta hai; end-to-end folder ko unit run se alag rakhta hai.

**Condition check:** Vitest unit/component files chalata hai; E2E directory exclude hai, kyunki uska runner Playwright hai.

**Connects to:** `src/tests/setup.ts`, frontend component tests aur React plugin.

#### `frontend/playwright.config.ts`

**Purpose:** browser mein poora flow test karne ki settings. Port 4173 par frontend server shuru karta hai; repeatable fixture test ke liye demo mode set karta hai; test fail ho to trace save karta hai.

**Condition check:** browser journey demo fixture mode par depend karti hai, isliye external live forecast result test ko random nahi banata; failure par trace save hoti hai.

**Connects to:** `e2e/route-planning.spec.ts`, Vite preview server aur Playwright browser.

#### `frontend/vercel.json`

**Purpose:** Vercel par frontend deploy karne ke niyam: Vite build, `dist` output, single-page app ko `index.html` par bhejna, versioned files ko lambe samay cache karna.

**Condition check:** static asset ko uske path se serve karta hai; React client-side route ko page shell tak rewrite karta hai. Yeh backend Django deploy nahi karta.

**Connects to:** Vercel build system, Vite `dist` output aur browser entry `index.html`.

#### `frontend/.env.example`

**Purpose:** API ka base URL, demo mode aur request timeout set karne ka example. Ismein default/placeholder values hain, private password nahi.

**Condition check:** environment variable set na ho to client ka default behavior lagu hota hai; `VITE_DEMO_MODE=true` ho to recorded fixture return hoti hai, warna API request hoti hai.

**Connects to:** Vite environment, `api/client.ts` aur developer ki local `.env` file.

#### `frontend/src/vite-env.d.ts`

**Purpose:** TypeScript ko Vite ke import/environment types batana. Yeh type declaration hai; user ke liye chalne wala code nahi.

**Condition check:** compile-time par TypeScript ko Vite globals/imports ki declaration milti hai; runtime par yeh file JavaScript behavior nahi chalati.

**Connects to:** `tsconfig.json` aur frontend TypeScript files.

#### `frontend/src/main.tsx`

**Purpose:** frontend ka pehla chalne wala file. Leaflet/CSS load karta hai, HTML root jagah dhoondhta hai aur React Strict Mode mein `App` lagata hai.

**Condition check:** HTML root element maujood ho to `App` mount hota hai; Strict Mode development mein kuch lifecycle behavior dobara chala kar issues pakadne mein madad karta hai.

**Connects to:** `index.html`, `App.tsx`, global CSS aur Leaflet styles.

### Subchapter 7.2 — Data contract, API request aur top-level app state

Is subchapter mein frontend/backend data shapes, demo fixture, API client, screen state aur global styling ka connection hai.

#### `frontend/src/types.ts`

**Purpose:** frontend request/response JSON fields ka likha hua contract: route request, summary, risk totals, checkpoint, route, heatmap, explainer, response aur active layer.

**Condition check:** TypeScript compile ke waqt values ko declared shape se compare karta hai; server se aaya JSON is file se runtime par validate nahi hota.

**Connects to:** `client.ts` aur components in types ko use karte hain; backend serializer/view ko same field names aur shape return karni chahiye.

**Code mein dikha antar:** response mein checkpoint ka `incomplete_data` field aa sakta hai, lekin frontend `Checkpoint` type abhi ise list nahi karta. Type declaration server ke JSON ko runtime par badalti ya check nahi karti.

**Interview:** “Kya TypeScript types network data ko runtime par validate karte hain?” Jawab: “Nahi. Yeh compile ke waqt code consistency mein madad karte hain; JSON phir bhi runtime input hai. Stronger check ke liye runtime schema validation add ki ja sakti hai.”

#### `frontend/src/api/demoFixture.json`

**Purpose:** internet ke bina demo aur repeatable browser test ke liye save kiya gaya poora example plan. Demo banner batata hai ki yeh saved data hai, live provider ka jawab nahi.

**Condition check:** sirf explicit demo mode ya test is data ko use kare; normal live API failure ko fixture se chhupana nahi chahiye.

**Connects to:** `api/client.ts`, demo banner aur `playwright.config.ts`.

#### `frontend/src/api/client.ts`

**Purpose:** frontend aur backend ke beech ek hi API darwaza rakhna.

**Flow:** `VITE_DEMO_MODE=true` ho to turant fixture deta hai; warna `/api/route-plans` par JSON POST karta hai, timeout lagata hai, safal jawab parse karta hai, aur non-2xx status par server ka kaam ka error message nikalta hai.

**Condition check:** `VITE_DEMO_MODE=true` ho to fixture; otherwise POST live API. Normal mode mein failed API ko chupke se fake fixture se replace nahi kiya jata.

**Connects to:** `App.tsx` `fetchRoutePlan` call karta hai; request/response contracts `types.ts` mein hain; target URL Django API hai.

**Interview:** “Alag demo flag kyun?” Jawab: “Taaki asli API failure ko galti se real successful route data na samjha jaye. Fixture result ko demo label diya jata hai.”

#### `frontend/src/App.tsx`

**Purpose:** mukhya screen aur UI ki shared state ko sambhalna.

**Condition check:** submission ke dauran loading state; success par result/recommended route; error par message; route/layer/page change par corresponding panel dikhaya jata hai.

**State mein:** current page, form, response, loading/error, selected route, active weather layer, forecast hour, animation, saved trips aur map scroll target.

**Flow:** form submit -> API request banti hai -> plan mangta hai -> result rakhta hai -> recommended route select karta hai -> error/loading/result dikhata hai. Result cards, map aur detail tabs tak deta hai. Helper se trips save/load karta hai.

**Connects to:** main components, API client, types aur LocalStorage helpers ko jodta hai.

**Dekhi gayi seema:** saved trip load karne par origin/destination/load/interval wapas aate hain, lekin code saved departure time ke bajay default se date/time banata hai. Interview mein wahi batayein jo code karta hai; yeh na kahein ki har purana field theek se restore hota hai.

#### `frontend/src/index.css`

**Purpose:** poore app ke rang, akshar, form/cards, route cards, map overlays, tables, responsive layout aur loading/error roop ko ek jagah rakhna.

**Condition check:** media queries screen width ke hisaab se layout adjust karti hain; CSS khud route/API decision nahi leti.

**Connects to:** `main.tsx` isse ek baar load karta hai; components CSS class names use karte hain.

**Interview:** “CSS alag kyun?” Jawab: “Layout aur rang ke rules ko component ke data aur decision logic se alag rakhne ke liye.”

#### `frontend/src/api/client.ts` — request path example

**Purpose:** yeh alag source file nahi, `client.ts` ka request-path walkthrough hai.

**Condition check:** demo flag true ho to request yahin ruk kar fixture return hoti hai; warna API POST path follow hota hai.

**Connects to:** `RouteForm` -> `App.tsx` -> `client.ts` -> Django serializer/view -> response wapas `App.tsx` aur UI components.

### Subchapter 7.3 — Map colors aur user ko dikhne wale components

Is subchapter mein formatting helpers, map layers, route form/cards, checkpoint detail, explanation aur saved-trip screen hain.

`RouteForm` bhare fields ko request banata hai. `App` client call karta hai. Client JSON bhejta hai. Django serializer request check karta hai. Safalta par client plan lautaata hai; `App` plan rakhta hai aur React screen ke components dobara dikhata hai.

#### `frontend/src/map/colors.ts`

**Purpose:** shared frontend risk labels, palette, per-weather thresholds, legend rows and route colors.

**Condition check:** layer `risk`, `wind`, `rain`, ya `snow` ke mutabik alag legend return hota hai. Threshold boundary badle to backend ke `engine.py` ke saath milana zaroori hai.

**Zaroori baat:** browser mein heatmap cells ko rangne ke liye weather thresholds dobara likhe gaye hain. Inka backend `risk/engine.py` se mel rehna chahiye; test/code review antar pakde. Route ranking ka adhikar backend ke paas hai.

**Connects to:** `MapView.tsx`, `RiskLegend.tsx` aur backend `risk/engine.py` ke matching display thresholds.

**Interview:** “Frontend par classification kyun dohrate ho?” Jawab: “Interpolated grid ko bina extra API call color karne ke liye. Yeh display classification hai; actual route ranking backend karta hai.”

#### `frontend/src/util/format.ts`

**Purpose:** miles, duration, ETA, ghadi aur load ko user ke liye saaf roop mein dikhana. `percentShares` sabse bade remainder wali rounding se risk bar ka yog 100 rakhta hai.

**Condition check:** invalid date string ho to formatter usi string ko dikhata hai; total risk miles zero/negative hon to percentages zero; warna remainder method se total 100 hota hai.

**Math:** take exact percentages, round each down, distribute remaining percentage points to largest decimal remainders.

**Connects to:** `RouteCard`, `DetailTabs`, `RiskBar` aur map popups.

#### `frontend/src/components/TopBar.tsx`

**Purpose:** app brand and navigation buttons between Route Plan and My Trips.

**Condition check:** selected page/state ke hisaab se active navigation dikh sakti hai; click par parent ka callback page badalta hai.

**Connects to:** `App.tsx` current page aur navigation callback deta hai. SVG icon sirf decoration hai.

#### `frontend/src/components/RouteForm.tsx`

**Purpose:** collect addresses, departure date/time, load and checkpoint interval.

**Input se output:** form values aur validation messages leta/banata hai; sab local checks pass hon to normalized submission parent ko deta hai.

**Flow:** controlled inputs form state update karte hain; blank/same address, galat load, missing date/time jaise errors pakde jaate hain; local date/time timezone ke saath ISO timestamp banta hai; error na ho tabhi submit hota hai.

**Condition check:** interval 10, 25, 50 mein se; load bounds aur required fields sahi hon; date/time valid ho. Browser check ke baad backend serializer phir se validate karta hai.

**Connects to:** `App.tsx` current form deta hai aur submit callback leta hai.

#### `frontend/src/components/RouteCard.tsx`

**Purpose:** one candidate route summary card: recommended/disqualified tags, distance, time, average risk badge, risk miles bar.

**Condition check:** API ka recommended route ID match ho to Recommended tag; no-travel miles hon to disqualified status; risk values API result se dikhte hain.

**Connects to:** API route, `RiskBar`, `routeColor`, format helpers; click se `App.tsx` selected route badalta hai.

#### `frontend/src/components/RiskBar.tsx`

**Purpose:** display proportion and miles per risk category as colored horizontal bar and labels.

**Condition check:** rounded category percentages ka yog theek 100 hota hai; zero total miles ho to har share zero hota hai.

**Connects to:** route aggregate risk object aur `format.ts` ka `percentShares`; category order rangon ka display order tay karta hai.

#### `frontend/src/components/MapView.tsx`

**Purpose:** Leaflet map par base map, route lines, checkpoint markers/popups, heatmap aur samay ke saath badalta truck marker dikhana.

**Input se output:** selected route, checkpoints, map layer aur timeline state leta hai; interactive map par route/weather view dikhata hai.

**Flow:** ek effect map banata/hatata hai; doosra route badalne par line/markers dobara banata hai; teesra backend heatmap grid ko browser canvas par rangkar image overlay banata hai; timeline effect slider time se pehle wale aakhri ETA checkpoint ko chunta hai.

**No additional heatmap API request:** layer change recolors already returned grid locally.

**Condition check:** selected route recommended route se alag ho sakti hai; rang recommended/disqualified/other batate hain; slider departure se 48 ghante tak chalta hai. Layer badalne par naya API request nahi hota.

**Connects to:** Leaflet library, selected route/checkpoints, backend heatmap, `colors.ts`, timeline aur parent `App.tsx`.

**Interview:** “Canvas aur image overlay kyun?” Jawab: “Bahut saare heatmap cells tezi se draw hote hain; layer badalne par wahi data browser mein dobara rang sakta hai.”

#### `frontend/src/components/ForecastTimeline.tsx`

**Purpose:** map ke samay marker ke liye 0 se 48 ghante ka slider aur play/pause control.

**Condition check:** playing ho to har 220 ms hour aage badhta hai aur 48 ke baad 0 par aata hai; paused/unmounted hone par timer clear hota hai.

**Flow:** play chalu ho to har 220 millisecond selected hour badhta hai; 48 ke baad phir se zero hota hai; pause ya component hatne par timer saaf kiya jata hai.

**Connects to:** `App.tsx` ka hour/play state aur `MapView.tsx` ka moving time marker; weather dobara fetch nahi hota.

**Zaroori seema:** yeh pehle se aaye checkpoints ke ETA par display ko aage le jata hai; slider ke har badlav par backend se naya forecast nahi mangta.

#### `frontend/src/components/LayerToggles.tsx`

**Purpose:** overall risk, wind, rain ya snow map layer chunne ke buttons. Yeh sirf App state badalta hai.

**Condition check:** sirf valid layer selection parent state ko badalti hai; yeh backend risk decision nahi chalati.

**Connects to:** `App.tsx` selected-layer state, `MapView.tsx` drawing aur `RiskLegend.tsx`.

#### `frontend/src/components/RiskLegend.tsx`

**Purpose:** chuni hui map layer ke rang aur threshold labels shared `colors.ts` data se dikhana.

**Condition check:** active layer ke hisaab se legend rows badalti hain; color/range shared helper se aata hai, hardcoded component logic se nahi.

**Connects to:** `LayerToggles.tsx` se selected layer aur `map/colors.ts` definitions.

#### `frontend/src/components/CheckpointTable.tsx`

**Purpose:** har page par 8 checkpoints wali table; ek row kholkar extra detail dikha sakte hain. Distance, ETA, weather, risk aur coordinates dikhte hain.

**Condition check:** checkpoint count aur selected page ke hisaab se 8 rows tak dikhte hain; detail toggle khula/band state badalta hai; empty list ho to rows nahi.

**Connects to:** `DetailTabs.tsx` ke selected route checkpoints; user ko risk label ke peeche ki reading inspect karne deta hai.

#### `frontend/src/components/DetailTabs.tsx`

**Purpose:** chuni hui route ki jaankari ko overview, checkpoints, weather aur summary tabs mein baantna.

**Condition check:** ek waqt mein selected tab ka panel dikhaya jata hai; selected route badle to usi route ka detail update hota hai.

**Extra actions:** route chunna, map tak jaana, share karne layak query-link copy karna, checkpoint detail kholna. Current time se pehle ETA wale checkpoints se progress dikhata hai.

**Connects to:** `CheckpointTable` aur `ExplainerPanel`; route selection/scroll actions parent tak callback se jaate hain.

#### `frontend/src/components/ExplainerPanel.tsx`

**Purpose:** API se aayi explanation aur niyamit calculation ke route metrics dikhana.

**Condition check:** API explanation/facts available hon tab dikhte hain; yeh text ko format karta hai, ranking dobara calculate nahi.

**Connects to:** `DetailTabs.tsx` aur backend `explainer.py` ke response fields.

**Safety boundary:** text sirf samjhane ke liye hai; route ID aur numbers pehle calculate hue plan se aate hain. UI ranking dobara nahi nikalta.

#### `frontend/src/components/MyTrips.tsx`

**Purpose:** browser LocalStorage mein 20 tak trip request save/load/delete karna aur unki list dikhana.

**Condition check:** browser mein LocalStorage available ho; saved trip count 20 tak rakha jata hai; missing/invalid saved data ko safely handle karna UI behavior ke liye zaroori hai.

**Data:** request ke fields aur save karne ka samay rakhta hai; poora live provider jawab nahi. Load karne par route planning phir chalti hai; date/time restore ki seema `App.tsx` mein samjhayi hai.

**Connects to:** `App.tsx` list state aur load/delete/save handlers deta hai; browser storage backend database nahi hai.

### Subchapter 7.4 — Frontend tests aur demo response banane ka tool

Neeche har test/helper file ka purpose aur woh kis behavior ko check ya banata hai, diya hai.

#### `frontend/src/tests/setup.ts`

**Purpose:** shared Vitest setup for frontend tests, such as matchers or test environment setup.

**Condition check:** test runner har test file se pehle is setup ko load karta hai; setup fail ho to frontend tests start nahi honge.

**Connects to:** `vitest.config.ts` aur saare frontend component tests.

#### `frontend/src/tests/RiskBar.test.tsx`

**Purpose:** component test for risk bar rendering and percentage share behavior.

**Condition check:** risk labels/values ke hisaab se bar sahi render hota hai ya nahi aur percentage total 100 banta hai ya nahi.

**Connects to:** `RiskBar.tsx` aur `format.ts` ke percentage helper.

#### `frontend/src/tests/MapView.test.tsx`

**Purpose:** map component test with Leaflet methods mocked; avoids a real external map/browser requirement in unit tests.

**Condition check:** map props/state se expected map behavior aata hai ya nahi; Leaflet ke browser methods ko mock kiya jata hai, isliye yeh real map server health nahi check karta.

**Connects to:** `MapView.tsx`, Vitest setup aur mocked Leaflet functions.

#### `frontend/src/tests/CheckpointTable.test.tsx`

**Purpose:** checkpoint table rendering, paging/expansion behavior checks.

**Condition check:** rows, page size/navigation aur detail expand/collapse expected behavior dikhate hain ya nahi.

**Connects to:** `CheckpointTable.tsx`.

#### `frontend/e2e/route-planning.spec.ts`

**Purpose:** Playwright browser scenario that checks a user journey through form, demo route result and UI. Browser-level test differs from unit test because it runs a full page interaction.

**Condition check:** browser app kholta hai, demo route submit karta hai, expected results/map controls dekhta hai aur trip save journey check karta hai; live weather response test ka requirement nahi.

**Connects to:** `playwright.config.ts`, frontend UI aur deterministic demo fixture.

#### `frontend/demo/generate_demo_fixture.py`

**Purpose:** frontend fixture mein use hone wala recorded demo response banana/update karna. Fixture ka format badalne se pehle iska input/output dekhein, kyunki frontend types isi par nirbhar hain.

**Condition check:** OSRM network call safal ho aur route valid ho tab fixture ban sakti hai; weather personas synthetic hain. Script chalane se fixture file update/overwrite ho sakti hai.

**Connects to:** backend route/risk helpers aur `frontend/src/api/demoFixture.json`.

**Asli kaam:** live OSRM se road geometry mangta hai, phir jaan-boojhkar banaye gaye `clean`, `wind` aur `snow` weather examples tayyar karta hai; Open-Meteo call nahi karta. Project resampler, risk engine, aggregator, ranker aur simplifier use karke `frontend/src/api/demoFixture.json` likhta hai. Isliye road line OSRM se asli ho sakti hai, par weather/heatmap simulated hain. Script ko OSRM network chahiye aur yeh fixture file badal sakta hai.

---

## Part 8. Test Chapter: test files aur kya condition check hoti hai

### Subchapter 8.1 — Backend pytest setup aur test files

- `backend/conftest.py`: **Purpose:** Django test settings aur startup ready karna. **Check:** app import se pehle Django initialize hua ya nahi. **Connects:** pytest aur Django app.
- `backend/pytest.ini`: **Purpose:** pytest configuration. **Check:** kin naming patterns wali files test ke roop mein milni chahiye. **Connects:** test discovery.
- `backend/apps/routing/tests/__init__.py`: **Purpose:** tests folder ko Python package banana. **Check:** koi business condition nahi; package marker. **Connects:** routing test modules.
- `backend/apps/routing/tests/test_smoke.py`: **Purpose:** chhota sanity test. **Check:** test runner ek basic assertion chala sakta hai. **Connects:** pytest setup.
- `backend/apps/routing/tests/test_haversine.py`: **Purpose:** Earth-distance helper ka test. **Check:** known distance, ulta input dene par symmetry, zero aur nonnegative result. **Connects:** `haversine.py`.
- `backend/apps/routing/tests/test_resampler.py`: **Purpose:** checkpoint banana test karna. **Check:** regular spacing, route endpoints, duplicate point aur invalid input. **Connects:** `resampler.py`.
- `backend/apps/routing/tests/test_simplify.py`: **Purpose:** map line simplify karne ka test. **Check:** straight line reduce, bend preserve, tolerance aur geographic edge cases. **Connects:** `simplify.py`.
- `backend/apps/routing/tests/test_geocoder.py`: **Purpose:** address conversion test. **Check:** validation, provider errors, cache, rate limiter configuration aur client lifecycle. **Connects:** `geocoder.py`.
- `backend/apps/routing/tests/test_osrm_adapter.py`: **Purpose:** road provider boundary test. **Check:** request parameters, coordinate order, response validation aur failure conversion. **Connects:** `osrm_adapter.py`.
- `backend/apps/routing/tests/test_eta.py`: **Purpose:** checkpoint time/distance estimate test. **Check:** route projection, departure/arrival, distance ke paas hona aur route order. **Connects:** `eta.py`.
- `backend/apps/routing/tests/test_weather_base.py`: **Purpose:** common forecast contract test. **Check:** weather model, timezone, coordinates aur forecast window. **Connects:** `weather/base.py`.
- `backend/apps/routing/tests/test_open_meteo_adapter.py`: **Purpose:** weather-provider translation test. **Check:** request/response, malformed data aur network failure. **Connects:** `open_meteo_adapter.py`.
- `backend/apps/routing/tests/test_interpolation.py`: **Purpose:** time-based forecast helper test. **Check:** exact match, wind interpolation, sorted order aur valid time range. **Connects:** `interpolation.py`.
- `backend/apps/routing/tests/test_engine.py`: **Purpose:** safety rule test. **Check:** threshold boundaries, har weather hazard aur load override. **Connects:** `risk/engine.py`.
- `backend/apps/routing/tests/test_aggregation.py`: **Purpose:** checkpoint se route summary test. **Check:** segment band, weighted score aur total distance ka sum. **Connects:** `risk/aggregation.py`.
- `backend/apps/routing/tests/test_ranker.py`: **Purpose:** route order test. **Check:** safety priority, ties, invalid fields aur input mutate na hona. **Connects:** `recommend/ranker.py`.
- `backend/apps/routing/tests/test_idw.py`: **Purpose:** map interpolation formula test. **Check:** exact sample, weight behavior, invalid sample aur chunk result consistency. **Connects:** `heatmap/idw.py`.
- `backend/apps/routing/tests/test_heatmap_builder.py`: **Purpose:** heatmap JSON grid test. **Check:** grid boundary/size, missing value `null` aur route corridor mask. **Connects:** `heatmap/builder.py`.
- `backend/apps/routing/tests/test_api_contract.py`: **Purpose:** API data-shape test. **Check:** request aur response expected field names/types se milte hain ya nahi. **Connects:** serializer, view aur public API.
- `backend/apps/routing/tests/test_views.py`: **Purpose:** HTTP API flow test. **Check:** validation, orchestration, status codes aur response. **Connects:** `api/views.py`.
- `backend/apps/routing/tests/test_plan_routes_integration.py`: **Purpose:** planning ke kai modules ko saath test karna. **Check:** mocked external providers ke saath poora route-planning flow. **Connects:** view aur routing/weather/risk services.

**Interview:** “Unit, integration aur end-to-end test mein farq?”

- Unit test ek chhota hissa check karta hai; bahari dependency aksar mock hoti hai.
- Integration test project ke kai real modules ko jodkar check karta hai; external services controlled/mock ho sakti hain.
- End-to-end test browser se user ka poora visible flow chalata hai.

Har test file ka seedha matlab: test input do, expected output/behavior se compare karo, phir galat ho to test fail. Test file production request ke waqt nahi chalti; test command ke waqt chalti hai.

README mein test count diya ho sakta hai. Guide update karte waqt test suites dobara nahi chalaye gaye; interview mein aaj ka count tabhi batayein jab backend/frontend tests chala kar nateeja dekha ho. Purane document ka number aaj ke run ka saboot nahi.

---

## Part 9. Fixture Chapter: recorded example data

### Subchapter 9.1 — Provider aur demo ke example files

#### `backend/fixtures/osrm_chicago_denver.json`

**Purpose:** OSRM ka recorded sample response, jisse route adapter tests/demo repeatable bante hain. Yeh data hai, Python code nahi.

**Condition check:** test fixture loader ise tab use karta hai jab recorded response chahiye; JSON invalid ho to load/parse nahi hoga. Yeh live OSRM ko healthy prove nahi karta.

**Connects to:** `test_osrm_adapter.py`, route adapter aur demo tooling.

#### `backend/fixtures/open_meteo_corridor.json`

**Purpose:** recorded hourly wind/rain/snow sample. Developer live forecast server ke bina conversion inspect/test kar sakta hai.

**Condition check:** data ka expected JSON shape aur weather arrays ki alignment sahi honi chahiye; malformed fixture parser/test pakad sakta hai.

**Connects to:** `test_open_meteo_adapter.py`, weather adapter aur `HourlyWeather` contract.

#### `backend/fixtures/demo_scenario.json`

**Purpose:** chhota scenario manifest: Chicago se Denver, load, checkpoint interval, expected route count aur jis route ke disqualified hone ki ummeed hai.

**Condition check:** scenario values planning request aur expected behavior se match karne chahiye; yeh metadata apne aap database ya route plan nahi banata.

**Connects to:** demo helper/script aur project ke explanation/test examples.

#### `backend/scripts/seed_demo_scenario.py`

**Purpose:** naam mein “seed” hai, lekin yeh database seed nahi karta. Example trip aur expected rule wala `backend/fixtures/demo_scenario.json` manifest likhta hai; yeh fixture documentation helper hai.

**Condition check:** script chalne par manifest file likhi/update hoti hai; yeh `Trip` table mein row nahi banata.

**Connects to:** demo scenario fixture aur uski documentation.

#### `frontend/src/api/demoFixture.json`

**Purpose:** explicit frontend demo mode ke liye poora UI response example.

**Condition check:** demo flag on ho tab client fixture deta hai; normal API mode mein yeh live response ka badal nahi.

**Connects to:** `api/client.ts`, `types.ts`, demo banner aur Playwright test.

### Demo-mode rule

Jab `VITE_DEMO_MODE=true` ho, frontend jaan-boojhkar saved fixture deta hai aur DEMO DATA label dikhata hai. Normal mode API call karta hai; failure ko error hi dikhata hai. Demo screenshot/result ko kabhi live provider calculation nahi kehna chahiye.

---

## Part 10. Documentation Chapter: project guide aur design decisions

### Subchapter 10.1 — README, architecture, ADR aur visual example

#### `README.md`

**Purpose:** project ka parichay, architecture, setup, API example, demo, testing commands, deployment aur future ideas samjhana. Har API request par yeh execute nahi hota.

**Condition check:** koi runtime condition nahi. Commands/test counts purane ho sakte hain; use karne se pehle current repo se verify karein.

**Connects to:** developers ko source folders, run/test commands aur deployment setup tak raasta dikhata hai.

#### `docs/architecture.md`

**Purpose:** request flow aur reliability ka short map.

**Condition check:** yeh executed logic nahi; agar architecture code se alag ho, code ki current implementation ko sach maana jaye.

**Connects to:** frontend form, Django API, provider adapters, services aur response.

#### `docs/decisions/ADR-001-routing-provider.md`

**Purpose:** OSRM chunne aur adapter boundary rakhne ka decision record. Route geometry/provider details business logic se alag rehte hain.

**Condition check:** OSRM kam alternatives de sakta hai; app nakli route nahi banati.

**Connects to:** `osrm_adapter.py`, route contract aur view.

#### `docs/decisions/ADR-002-weather-provider.md`

**Purpose:** Open-Meteo chunne aur common weather format rakhne ka reason.

**Condition check:** hourly wind/rain/snow data available ho; provider unavailable/malformed ho to adapter error/missing-data path use hota hai.

**Connects to:** weather adapter, `HourlyWeather` contract aur checkpoint evaluation.

#### `docs/decisions/ADR-003-risk-combination.md`

**Purpose:** multiple weather hazard ko combine karne ka rule document.

**Condition check:** wind, rain, snow ko alag classify karke worst band; phir cargo load wali wind condition risk upgrade kar sakti hai.

**Connects to:** `risk/engine.py` aur uske tests.

#### `docs/decisions/ADR-004-conservative-segments.md`

**Purpose:** do weather checkpoints ke beech conservative risk chunne ka reason.

**Condition check:** har segment par dono endpoint mein jo band worse ho, poora segment usi band mein count hota hai.

**Connects to:** `risk/aggregation.py` aur aggregation tests.

#### `docs/decisions/ADR-005-lexicographic-ranking.md`

**Purpose:** chhipe weighted score ke bajay saaf ranking priorities ka reason.

**Condition check:** current ranker pehle qualified routes ko disqualified se alag rakhta hai; uske baad risk fields aur duration dekhta hai. ADR wording aur implementation ko saath compare karna chahiye.

**Connects to:** `recommend/ranker.py` aur ranking tests.

#### `docs/decisions/ADR-006-subhourly-interpolation.md`

**Purpose:** checkpoint par arrival ke samay ke forecast ko chunne ka reason.

**Condition check:** wind ko waqt ke beech estimate kiya ja sakta hai; hourly rain/snow total ko fake minute readings mein nahi baanta jata.

**Connects to:** `weather/interpolation.py` aur checkpoint ETA/weather lookup.

#### `docs/decisions/ADR-007-llm-explainer-only.md`

**Purpose:** explanation ko route decision ke baad rakhne ka reason.

**Condition check:** current `templates.py` deterministic hai; yeh file LLM service call nahi karti.

**Connects to:** ranker ke baad `explainer.py`/`templates.py` aur API response.

#### `docs/decisions/ADR-008-idw-heatmap.md`

**Purpose:** ek baar heatmap grid bhejne aur browser mein layer color karne ka reason.

**Condition check:** layer switch par returned grid reuse hoti hai; naya backend API call nahi chahiye.

**Connects to:** `heatmap/idw.py`, `heatmap/builder.py` aur frontend `MapView.tsx`.

#### `docs/screenshots/dashboard.png`

**Purpose:** README/docs ke liye project screen ka visual udaharan.

**Condition check:** koi executable condition nahi; screenshot purana ho sakta hai aur current hosted app health prove nahi karta.

**Connects to:** README aur documentation; runtime app ise load nahi karti.

#### `docs/TRUCKERSAFE_COMPLETE_INTERVIEW_REVISION_GUIDE.md`

**Purpose:** yeh beginner explanation, file tour, architecture, interview questions, learning techniques aur limitations wali guide hai.

**Condition check:** koi runtime condition nahi. Code badalne par guide ke described behavior ko dobara verify karna chahiye.

**Connects to:** project ke files ko learner ke liye padhne layak kahaani mein jodti hai.

---

## Part 11. Deploy/Automation Chapter: hosting aur automatic checks

### Subchapter 11.1 — Backend hosting configuration

#### `render.yaml`

**Purpose:** Render par backend deploy steps configure karna: `backend` root, dependencies, static files, migrations, Gunicorn, `/healthz/` aur environment variables.

**Condition check:** hosting environment variables/secret aur build commands sahi hon; health URL respond kare. Health URL sirf Django process check hai.

**Connects to:** backend requirements, `manage.py`, `config.wsgi`, `settings.py` aur health endpoint.

**Interview:** “Health URL kyun?” Jawab: “Hosting platform ko sasta endpoint chahiye jo bataye Django process jawab de raha hai. Yeh zindagi/response check hai, external providers ka full test nahi.”

### Subchapter 11.2 — Code badlav par automatic test chalana

#### `.github/workflows/ci.yml`

**Purpose:** push aur pull request par GitHub Actions ke automatic project checks chalana.

**Condition check:** backend job packages install karke Django checks aur pytest chalata hai; frontend locked npm install, Vitest, TypeScript/Vite build aur Chromium/Playwright E2E chalata hai. Koi step fail ho to CI failure report hota hai.

**Connects to:** `requirements.txt`, `package-lock.json`, test configs aur deployment se pehle quality checks.

**CI ka matlab:** Continuous Integration; code push ya proposed change par automatic checks chalana.

#### `.gitignore`

**Purpose:** Git ko batana ki virtual environment, cache, private environment file ya build output jaise local/generated files save na kare.

**Condition check:** file path ignore pattern se match ho to Git use aam taur par naye changes ke roop mein track nahi karta; pehle se tracked file ignore rule se apne-aap untrack nahi hoti.

**Connects to:** local developer workflow, Git commits aur CI repository checkout.

---

## Part 12. Interview Chapter: tools aur dependencies kyun chune

### Python tools

- **Django:** backend web app, URL, settings aur database integration banane/sambhalne ke liye.
- **DRF:** API request validate karne aur HTTP status ke saath JSON jawab dene ke liye.
- **django-cors-headers:** browser se sirf anumati wale frontend origin ko API call karne dene ke liye.
- **requests:** route aur weather providers ko HTTP request bhejne ke liye.
- **geopy:** Nominatim se address-to-GPS kaam karne ke liye.
- **NumPy:** IDW heatmap ke bahut saare grid numbers par tez hisaab ke liye.
- **Gunicorn:** production mein Django WSGI application chalaane ke liye.
- **WhiteNoise:** is deployment mein alag static server ke bina app ki static files dene ke liye.
- **pytest:** backend ke automatic tests chalane ke liye.

### JavaScript and frontend tools

- **React / ReactDOM:** dobara istemal hone wale interactive screen components banane ke liye.
- **TypeScript:** browser par chalne se pehle kai field/type galti pakadne ke liye.
- **Leaflet:** interactive map layer aur markers ke liye.
- **Vite:** local development server aur frontend production build ke liye.
- **Vitest:** jaldi unit/component test chalane ke liye.
- **Testing Library:** user ko dikhne wale UI behavior ko check karne ke liye.
- **jsdom:** frontend tests ke liye nakli/browser-jaisa document dene ke liye.
- **Playwright:** poori website ko browser se automatic test karne ke liye.
- **npm lockfile:** indirect packages ke versions ko repeatable rakhne ke liye.

### External data providers

- **Nominatim:** “Yeh likha hua address map par kahan hai?” -> GPS coordinate.
- **OSRM:** “In GPS points ke beech kaunse sadak wale raaste hain?” -> route line, distance aur duration.
- **Open-Meteo:** “Is jagah aur ghante ka forecast kya hai?” -> hourly weather.

### Interview: “Agar provider fail ho to kya hota hai?”

“Adapter provider ki apni failure ko pakadkar project ka samajhne layak error banata hai. API view use niyantrit HTTP jawab mein badalti hai. Is code mein kuch checkpoint weather failures incomplete/`NO_TRAVEL` bante hain; route provider fail ho to plan response nahi milta.”

---

## Part 13. Interview Chapter: apne project ko samjhaane ke jawab

### “Apna project ek minute mein samjhaiye.”

“TruckerSafe React aur Django se bana weather-aware truck route planner hai. Frontend route request bhejta hai. Backend input validate karta hai, address ko GPS banata hai, OSRM se raaste mangta hai, niyamit doori par checkpoints banata hai, unka ETA nikalta hai, Open-Meteo forecast leta hai, weather aur load ke fixed safety rules lagata hai, risk-miles jodta hai aur routes ko rank karke heatmap/explanation ke saath dashboard jawab deta hai. Heatmap sirf andazati display hai; route rank saaf safety rules se aata hai. Bahari providers adapters ke peeche hain aur project mein backend, frontend aur browser test layers hain.”

### “Safety ranking ke liye machine learning kyun nahi?”

“Requirements threshold rules ke roop mein saaf hain. Niyamit rule table ko audit, dobara chala aur boundary par test karna aasaan hai. Aage ML forecast ya estimate mein madad kar sakta hai, lekin use chupke se tay safety rule ko badalne nahi dena chahiye.”

### “Departure ke bajay pahunchne ke samay ka weather kyun?”

“Door ke checkpoint par truck baad mein pahunchega. Chalte waqt ka weather wahan pahunchne ke samay jaisa zaroori nahi. ETA se har checkpoint ke liye sahi forecast hour chunte hain.”

### “Unknown weather ko `NO_TRAVEL` kyun mark karte ho?”

“Unknown hone ka matlab safe hona nahi. Conservative choice missing data ko zero nahi maanti. Response mein incomplete-data jaankari bhi rehti hai, taaki yeh seema chhupi na rahe.”

### “Bahut zyada weather calls kaise rokte ho?”

“Ek plan request ke andar rounded coordinate aur UTC forecast hour milkar cache key bante hain. Ek jaise cell/hour wale nazdeeki checkpoints wahi result reuse karte hain. Yeh ek request ki memory cache hai, alag server processes/users ki shared cache nahi.”

### “Adapter classes kyun kaam aati hain?”

“Yeh provider URL, units, data shape, timeout aur errors ko alag rakhti hain. Baaki services project ka ek jaisa format use karti hain, isliye provider badalne par poore app mein badlav nahi failta.”

### “Routes ko rank kaise karte ho?”

“Pehle qualified routes; phir kam no-travel miles, kam severe miles, kam high miles, kam average score aur chhota duration. Is order se safety ki priority bachi rehti hai aur tie ka nateeja predictable hota hai.”

### “Checkpoint ka risk poore route ka risk kaise banta hai?”

“Kram mein paas-paas ke do checkpoints ke beech wale segment ko dono ends mein se worse risk milta hai. Har band ke miles jode jaate hain. Average score ka formula hai: har segment ka risk score × uske miles ka total, phir poore route ke miles se divide.”

### “Heatmap aur route risk mein kya farq hai?”

“Checkpoint rules sampled jagahon ko classify karke route rank tay karte hain. Heatmap ka IDW naapey gaye samples ke beech ke rang ka anuman lagata hai. Use naya measured weather ya naya route decision kehna galat hoga.”

### “Kya My Trips backend database mein save karta hai?”

“Frontend abhi request entries browser ke LocalStorage mein rakhta hai. Django `Trip` model aur migration hain, lekin dekhe gaye API code mein unke zariye database save/read karne ka endpoint nahi dikha.”

### “Agla sudhaar kya karoge?”

“Main har UI par incomplete weather ko saaf dikhata, TypeScript boundary par runtime response validation lagata, unused Trip database storage ko jodta ya hataata, badi view ka orchestration planner service mein le jaata, traffic zaroorat kare to shared cache jodta, aur deployed providers ko monitoring ke saath test karta.”

### Quick interview prompts for the remaining files

- **`apps.py`:** “Django ko yeh app kaise milti hai?” Jawab: settings mein `RoutingConfig` likha hai; yeh `apps.routing` package ka naam batata hai.
- **`config/asgi.py`:** “ASGI kis tarah ke server ke liye hai?” Jawab: async-capable server interface; abhi Render WSGI/Gunicorn chalata hai.
- **`manage.py`:** “Migration ya local server kaise chalate ho?” Jawab: settings chunne ke baad Django management command isi script se chalti hai.
- **`config/urls.py` aur `api/urls.py`:** “HTTP path ko view kaise milti hai?” Jawab: root URL patterns app ke paths jodte hain aur route-plan path ko `route_plan` view se milate hain.
- **`models.py` aur `0001_initial.py`:** “Python model database table kab banta hai?” Jawab: migration badlav likhe, `migrate` use database par lagaye; record save karne ke liye API ko model save call phir bhi karna hota hai.
- **`services/.../__init__.py`:** “Kya yeh file risk calculate karti hai?” Jawab: nahi; yeh import package marker hai. Asli kaam naam wale engine/helper module mein hai.
- **`templates.py` aur `explainer.py`:** “Kya explanation route ka rank badal sakti hai?” Jawab: nahi; yeh pehle se calculate facts ko shabdon mein rakhti hai.
- **`frontend/src/main.tsx`:** “React components kahan se shuru hote hain?” Jawab: HTML root `ReactDOM.createRoot` ko milta hai, phir usmein `App` lagta hai.
- **`frontend/src/types.ts`:** “Interface kya karta hai?” Jawab: TypeScript ko object ke fields batata hai; aaya hua JSON runtime par check nahi karta.
- **`frontend/src/vite-env.d.ts`:** “Vite types kyun declare karte hain?” Jawab: TypeScript ko Vite environment aur import metadata samajh aati hai.
- **`frontend/vite.config.ts`:** “Local API proxy kyun?” Jawab: browser `/api` path call karta hai aur Vite use Django tak pahunchata hai.
- **`frontend/tsconfig.json`:** “Strict mode kyun?” Jawab: development/build ke dauran missing ya incompatible value jaldi pakadne ke liye.
- **`frontend/.env.example`:** “Example env file Git mein kyun?” Jawab: zaroori setting names batane ke liye, bina private values commit kiye.
- **`frontend/src/api/client.ts`:** “HTTP error ko kahan badalna chahiye?” Jawab: API boundary/client par, taaki UI ko upyogi success object ya samajhne layak error mile.
- **`frontend/src/App.tsx`:** “Selected route aur loading state kaun sambhalta hai?” Jawab: top-level App shared state rakhta aur child components ko values/callbacks deta hai.
- **`frontend/src/components/TopBar.tsx`:** “Navigation component kyun?” Jawab: dobara istemal hone wali UI hai; parent page ki state deta hai.
- **`frontend/src/components/RouteForm.tsx`:** “Frontend aur backend dono par validation kyun?” Jawab: frontend jaldi feedback deta hai; backend bharosemand server-side check karta hai.
- **`frontend/src/components/RouteCard.tsx`:** “Recommended badge kis data se tay hota hai?” Jawab: response ke `recommended_route_id` se, local speed-only hisaab se nahi.
- **`frontend/src/components/RiskBar.tsx`:** “Percentages ka yog 100 kaise?” Jawab: helper pehle exact percentage neeche round karta hai, phir bache points sabse bade decimal remainder ko deta hai.
- **`frontend/src/components/MapView.tsx`:** “Refs/effects kyun?” Jawab: Leaflet map React ke bahar ka mutable object hai; ref use sambhalta hai, effect props badalne par banata/update karta/saaf karta hai.
- **`frontend/src/components/ForecastTimeline.tsx`:** “Play mode naya forecast mangta hai?” Jawab: nahi; pehle aaye checkpoint result par selected hour aage karta hai.
- **`frontend/src/components/LayerToggles.tsx`:** “Layer badalne par backend call hoti hai?” Jawab: nahi; selected display state badalti hai aur wahi grid dobara rangti hai.
- **`frontend/src/components/RiskLegend.tsx`:** “Legend map se milti kaise rehti hai?” Jawab: dono shared legend/risk color definitions lete hain.
- **`frontend/src/components/CheckpointTable.tsx`:** “Page kyun banate ho?” Jawab: lambi route mein bahut checkpoints ho sakte hain; ek page par 8 se table padhna aasaan rehta hai.
- **`frontend/src/components/DetailTabs.tsx`:** “Tabs kya jama karte hain?” Jawab: chuni route ka overview, checkpoints, weather aur summary.
- **`frontend/src/components/ExplainerPanel.tsx`:** “Kya yeh AI ka faisla hai?” Jawab: nahi; API ki explanation aur calculate kiye route facts dikhata hai.
- **`frontend/src/components/MyTrips.tsx`:** “Saved trips kahan rehte hain?” Jawab: browser LocalStorage mein, adhiktam 20 request entries.
- **`frontend/src/map/colors.ts`:** “TypeScript mein thresholds kyun dohraye?” Jawab: browser ko interpolated map cell rangne hain; Python rules ke saath inka mel rakhna hota hai.
- **`frontend/src/util/format.ts`:** “Formatting ek jagah kyun?” Jawab: kai components ko ek jaise units, dates aur percentage chahiye.
- **`frontend/src/index.css`:** “Har style inline kyun nahi?” Jawab: ek jagah ke styles se layout consistent, responsive aur badalne mein aasaan rehta hai.
- **`frontend/index.html`:** “Browser app kaise shuru karta hai?” Jawab: `src/main.tsx` load hota hai aur `root` div mein React lagata hai.
- **`frontend/vitest.config.ts` aur `src/tests/setup.ts`:** “Component tests ka setup kaise?” Jawab: Vitest `jsdom` aur shared setup use karta hai; Playwright browser tests ko alag rakhta hai.
- **`frontend/playwright.config.ts` aur `e2e/route-planning.spec.ts`:** “End-to-end mein kya test hota hai?” Jawab: browser app kholta, demo route submit karta, map layer badalta aur trip save karta hai.
- **`frontend/vercel.json` aur `render.yaml`:** “Deploy config do kyun?” Jawab: Vercel frontend serve/build karta; Render Django backend, health check aur environment chalata hai.
- **`.github/workflows/ci.yml`:** “CI kya automatic karta hai?” Jawab: push/pull request par backend, frontend build/tests aur browser journey check karta hai.
- **`frontend/package-lock.json`:** “Indirect packages lock kyun?” Jawab: local aur CI mein ek hi dependency tree install karne ke liye.
- **`backend/pytest.ini` aur `backend/conftest.py`:** “Pytest ko Django settings kaise pata?” Jawab: pytest config test files chunta hai; root conftest settings set karke Django shuru karta hai.
- **Fixture JSON files:** “Provider response save kyun?” Jawab: live service ke bina tests/demo ko jaan-pehchana example data milta hai.
- **`frontend/demo/generate_demo_fixture.py`:** “Kya demo ka saara weather asli hai?” Jawab: nahi; OSRM se road line mil sakti hai, par weather/heatmap ek niyantrit scenario ke liye banaye gaye synthetic examples hain.
- **`backend/scripts/seed_demo_scenario.py`:** “Kya yeh Trip rows likhta hai?” Jawab: nahi; JSON scenario manifest likhta hai.
- **README, architecture, ADRs:** “Decision records kyun rakhte hain?” Jawab: provider aur safety choice ka reason review ho sake, sirf code ka result nahi.
- **`.gitignore`:** “SQLite, virtualenv, build/test artifacts ignore kyun?” Jawab: yeh local/generated ya machine-specific hote hain; source aur package definitions share karne chahiye.
- **Dashboard screenshot:** “Yeh kis baat ka proof hai?” Jawab: ek samay ka visual roop; live deployment ya API chalne ka proof nahi.

---

## Part 14. Interview Chapter: aam galtiyon se bachna

- Interview mein yeh na kahein ki route rank AI karta hai; rank niyamit ranker karta hai.
- Estimated heatmap rang ko naapey hue weather reading na batayein.
- Unknown weather ko zero ya safe na kahein.
- LocalStorage trip ko Django database mein save hua na batayein.
- ETA ko live traffic wala na kahein; abhi ka formula route duration ko doori ke anupat baantta hai.
- Yeh na kahein ki OSRM hamesha 3 route deta hai; kam de sakta hai.
- `(latitude, longitude)` ko GeoJSON `[longitude, latitude]` ke saath ulta-pulta na karein.
- Current commands chalaye bina README ka test count na dohrayein.
- `/healthz/` ko forecast/route provider ka healthy hone ka proof na kahein.
- Local code dekh kar deployed URL online hone ka daava na karein.

---

## Part 15. Recall Chapter: khud ko chhote sawaal poochho

**Pehle jawab dekhe bina koshish karein.**

1. 38 mph hawa, halki baarish, baraf nahi aur 42,000 lb load ho to kya hoga?
   - Hawa `HIGH`; baarish/baraf `LOW`; heavy-load wind rule final risk ko `SEVERE` banata hai.

2. `types.ts` aur Django serializer dono kyun hain?
   - TypeScript compile ke waqt frontend shape errors pakadta hai; server serializer aayi hui avishvasniya request ko validate karta hai.

3. Coordinate kram ki sabse aham galti kya ho sakti hai?
   - Andar tuple mein pehle latitude, phir longitude; GeoJSON mein pehle longitude, phir latitude.

4. Kya 48-hour slider ke har kadam par weather API call hoti hai?
   - Nahi. Yeh pehle aaye checkpoints par visual samay marker chalata hai; har kadam par nayi request nahi hoti.

5. Ranking mein `NO_TRAVEL` ka kya matlab hai?
   - No-travel miles zero se zyada hon to route disqualified; qualified routes pehle rank hote hain.

6. Kya saamne dikhne wala My Trips `Trip` database use karta hai?
   - Nahi. UI browser LocalStorage use karta hai; model/migration hain, par save karne wala API path nahi dikha.

7. IDW weight kya karta hai?
   - Nazdeeki sample ka asar zyada; doori badhne par uska weight ghatta hai.

8. Test file pass hone se kya prove hota hai?
   - Us test environment mein wahi test cases pass hue; har production condition ya live provider healthy hai, yeh prove nahi hota.

---

## Part 16. Aakhri revision Chapter: ek nazar mein poora flow

- Geocoder address ko GPS banata hai.
- OSRM GPS points se sadak ke route options deta hai.
- Resampler road line se barabar doori ke checkpoints banata hai.
- Checkpoint distance aur route duration se pahunchne ka andazati samay milta hai.
- Pahunchne ka ghanta us jagah ka forecast chunta hai.
- Sabse kharab weather band aur load rules checkpoint risk dete hain.
- Do checkpoints mein worse endpoint segment ka risk tay karta hai.
- Segment miles aur score route summary dete hain.
- Lexicographic ranker tez route se pehle surakshit route chunta hai.
- IDW asli checkpoint samples ke beech ka visual weather andazta hai.
- Explainer nateeja samjhata hai, nateeja badal nahi sakta.
- React backend ka ek jawab dikhata hai; map layer browser mein rang badalti hai.
- Tests chhote rules, module connections aur user flow ko alag-alag star par bachate hain.

### Final interview sentence

“Maine TruckerSafe ko is tarah banaya ki safety decisions saaf, dobara chalane layak aur jaanchne layak hon: providers route/weather facts dete hain, Python ke niyamit rules score banate hain, fixed ranker routes ka order karta hai, aur frontend faisla apne haath mein liye bina nateeja samjhata hai.”

---

TruckerSafe project guide ka ant.
