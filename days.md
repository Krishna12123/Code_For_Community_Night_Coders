# ⏱️ 3-Day Sprint Execution Plan (`days.md`)

A day-by-day, person-by-person breakdown for delivering the **Cyclone Risk Assessment & Action Engine** platform within **3 days**.

---

## 🎯 3-Day Sprint Overview

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 3-DAY SPRINT MILESTONES                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 📅 DAY 1: Foundation & Skeletons (Data ingestion, FastAPI base, React map init)        │
│ 📅 DAY 2: Core Intelligence (GEE flood mapping, Risk calculation, Dynamic UI layers)   │
│ 📅 DAY 3: Integration & Polish (End-to-end flow, Action triage panel, Final live demo) │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📅 DAY 1: Foundation, Data Ingestion & Baseline Setup

> **🎯 Goal of Day 1**: All 3 environments operational, API contracts locked, mock storm data flowing from backend to frontend map.

### 🧑‍💻 Vikash (Data, GEE & Gemini)
- [ ] **Task 1.1 (Environment & Auth)**: Setup Python virtualenv, install `earthengine-api`, `geemap`, `google-genai`, `requests`, `pandas`. Authenticate GEE service account/credentials.
- [ ] **Task 1.2 (Cyclone & Weather Ingestion)**:
  - Write script to fetch active/historical cyclone tracks (IMD / NOAA IBTrACS / GDACS).
  - Write weather fetcher for Open-Meteo / GFS (wind speed, central pressure, coordinate trajectory).
- [ ] **Task 1.3 (Gemini Setup & Baseline Prompt)**:
  - Configure Gemini API key.
  - Create initial structured prompt template to accept storm JSON and output executive situation summary.
- [ ] **Deliverable Day 1**: A standalone Python module returning standardized `cyclone_data.json` and basic Gemini text briefing.

---

### 🧑‍💻 Krishna (FastAPI Backend & DB)
- [x] **Task 1.1 (FastAPI Scaffold)**: Initialize FastAPI app (`app/main.py`, router structure, CORS for Harshit's React dev server, `.env` config).
- [x] **Task 1.2 (Pydantic Schemas & API Contracts)**:
  - Define schemas: `CycloneTrack`, `ForecastPoint`, `RiskAssessment`, `ActionRecommendation`, `GeeTileResponse`.
- [x] **Task 1.3 (Mock API Endpoints)**:
  - Build stub endpoints:
    - `GET /api/v1/cyclones/active`
    - `GET /api/v1/risk/exposure/{cyclone_id}`
    - `GET /api/v1/actions/recommendations/{cyclone_id}`
    - `GET /api/v1/geospatial/layers`
- [x] **Task 1.4 (Database / Geo Setup)**: Setup SQLite/PostgreSQL with spatial district boundaries and hospital/shelter mock datasets.
- [x] **Deliverable Day 1**: Working FastAPI server returning mock JSON payloads matching agreed schemas for Harshit to develop against.

---

### 🧑‍💻 Harshit (React Frontend & UI)
- [ ] **Task 1.1 (Project Initialization)**: Create React app with Vite + JavaScript (JSX) + Tailwind CSS + Lucide Icons.
- [ ] **Task 1.2 (Layout Skeleton)**: Build dashboard shell:
  - Top header (Cyclone name, Category badge, Landfall countdown timer).
  - Main split view (70% Map container, 30% Analytics/Action panel).
- [ ] **Task 1.3 (Base Map Setup)**:
  - Setup Mapbox GL JS / MapLibre GL canvas.
  - Render base satellite/dark tiles.
  - Add simple marker for current cyclone eye position from Krishna's mock API.
- [ ] **Deliverable Day 1**: Responsive dashboard UI with an interactive base map rendering initial mock coordinate marker.

---

## 📅 DAY 2: Core Processing, Risk Engine & Dynamic Layers

> **🎯 Goal of Day 2**: GEE SAR flood tile generation working, risk engine calculating exposed population/assets, and frontend rendering forecast cone & dynamic layers.

### 🧑‍💻 Vikash (Data, GEE & Gemini)
- [ ] **Task 2.1 (GEE Sentinel-1 SAR Flood Detection)**:
  - Implement SAR GRD backscatter thresholding / change detection before vs. after storm.
  - Generate flood extent binary mask.
- [ ] **Task 2.2 (GEE Tile Generation)**:
  - Generate XYZ Tile URL (`ee.Map.getTileUrl`) for:
    1. SAR Flood Inundation layer.
    2. GPM Rainfall Accumulation layer.
- [ ] **Task 2.3 (Gemini Deep Reasoning Engine)**:
  - Refine prompt to produce district-by-district threat analysis, hospital risk warnings, and actionable SOP checklists in structured JSON.
- [ ] **Deliverable Day 2**: Working GEE pipeline returning live XYZ tile URLs and Gemini engine generating structured emergency advisories.

---

### 🧑‍💻 Krishna (FastAPI Backend & Risk Engine)
- [x] **Task 2.1 (Cone of Uncertainty & Wind Buffer Logic)**:
  - Implement spatial buffering algorithms (34kt, 50kt, 64kt wind radii along track).
- [x] **Task 2.2 (Exposure & Risk Calculation Engine)**:
  - Overlay cone polygon with district dataset:
    - Calculate population within high wind / flood zone.
    - Identify vulnerable hospitals, shelters, and roads.
  - Compute Composite Risk Score ($\text{Score} \in [0, 100]$) and categorize into Green/Yellow/Orange/Red.
- [x] **Task 2.3 (Action Engine Rule Processor)**:
  - Build rule mapper: Risk Level $\rightarrow$ Trigger specific SOP protocols (evacuation radius, SDRF deployment, shelter activations).
- [x] **Task 2.4 (Service Integration)**: Connect Vikash's GEE tile generator and Gemini modules into FastAPI service layer.
- [x] **Deliverable Day 2**: Fully functional risk scoring and action generation backend responding with live GEE tile URLs and Gemini briefings.

---

### 🧑‍💻 Harshit (React Frontend & GIS Dashboard)
- [ ] **Task 2.1 (Cyclone Trajectory & Forecast Cone)**:
  - Render historical track line and forecast path.
  - Draw animated forecast cone of uncertainty (GeoJSON polygon).
  - Add clickable eye points with timestamp & wind speed tooltip cards.
- [ ] **Task 2.2 (Map Layer Controller)**:
  - Layer toggle switch for:
    - 🛰️ Sentinel-1 SAR Flood Extent (with opacity slider).
    - 🌧️ GPM Rainfall Accumulation.
    - 🏥 Critical Infrastructure POIs (Hospitals, Relief Shelters).
- [ ] **Task 2.3 (Metrics & Exposure Visuals)**:
  - Build KPI metric cards (Total Population at Risk, Flooded Area $\text{km}^2$, Available Shelters).
  - Add district vulnerability comparison bar/radar chart (Recharts).
- [ ] **Deliverable Day 2**: Interactive GIS map visualizing cyclone cone, toggleable raster layers, and dynamic risk metric cards.

---

## 📅 DAY 3: Integration, Action Center, Polish & Live Demo

> **🎯 Goal of Day 3**: Full end-to-end integration, interactive Action SOP triage panel, real-time alert broadcasts, and presentation-ready demo.

### 🧑‍💻 Vikash (Data, GEE & Gemini)
- [ ] **Task 3.1 (Multimodal Visual Assessment)**:
  - Pass satellite crop/flood mask thumbnail to Gemini Flash for automated visual damage summary.
- [ ] **Task 3.2 (Pipeline Optimization & Caching)**:
  - Optimize GEE computation latency; cache tile URLs and raster stats for demo speed.
- [ ] **Task 3.3 (Demo Scenarios & Test Datasets)**:
  - Prepare 2 high-impact demo scenarios:
    1. *Active/Recent Major Storm* (e.g., Cyclone Dana / Biparjoy).
    2. *Simulated Super Cyclone approaching dense coastal city*.
- [ ] **Deliverable Day 3**: Robust, fast data pipeline with tested demo datasets and automated Gemini visual insights.

---

### 🧑‍💻 Krishna (FastAPI Backend & Integration)
- [ ] **Task 3.1 (Real-Time Alerts & WebSocket)**:
  - Implement WebSocket channel (`/api/v1/ws/alerts`) for instant emergency bulletin broadcasts.
- [ ] **Task 3.2 (Action Status Updates & Report Generation)**:
  - Endpoints to update SOP task status (`Pending` $\rightarrow$ `In-Progress` $\rightarrow$ `Completed`).
  - Generate downloadable PDF / JSON Disaster Situation Report.
- [ ] **Task 3.3 (API Hardening & Edge Cases)**:
  - Handle rate limits, fallback mock data in case of offline/network issues, CORS verification.
- [ ] **Deliverable Day 3**: Production-grade backend with real-time alert broadcasting, task state updates, and export capabilities.

---

### 🧑‍💻 Harshit (React Frontend & Dashboard Polish)
- [ ] **Task 3.1 (Interactive Action & Triage Center)**:
  - Grouped action item checklist (*Pre-Landfall Evacuation*, *Infrastructure Securing*, *Post-Landfall Rescue*).
  - Interactive status toggles and assigned agency badges (NDRF, Health Dept, Coast Guard).
- [ ] **Task 3.2 (Gemini AI Situation Briefing Panel)**:
  - Formatted AI advisory card with severity highlighting.
  - "Download Official Advisory Report (PDF)" button.
- [ ] **Task 3.3 (UI Polish, Dark Mode & Responsive Layout)**:
  - Polished dark command-center aesthetic, smooth loading skeletons, toast notifications for incoming WebSocket alerts.
- [ ] **Deliverable Day 3**: Complete, visually stunning Command Center Dashboard ready for live demonstration.

---

## 🤝 Daily Sync Schedule (Recommended)

| Time | Meeting | Focus |
| :--- | :--- | :--- |
| **09:30 AM** | **Morning Standup (15 min)** | Review previous day output, unblock dependencies, confirm day goals. |
| **02:00 PM** | **Midday Integration Check (10 min)** | Verify API contracts, test endpoints between Krishna, Vikash & Harshit. |
| **07:00 PM** | **Evening Review & Merge (20 min)** | Merge code into main branch, run end-to-end integration test. |
