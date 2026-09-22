# ⚙️ Cyclone Risk Assessment & Action Engine — Backend (`backend/`)

**Owner: Krishna**

This directory houses the **FastAPI Backend, SQLite/PostGIS Spatial Database, and Risk/Action Engine** for the Cyclone Disaster Response platform.

---

## 🏛️ Project Directory Structure

```text
backend/
├── app/
│   ├── main.py              # Application entrypoint & WebSocket alert broadcaster
│   ├── core/
│   │   └── config.py        # Settings & environment variable configuration
│   ├── schemas/
│   │   └── models.py        # Pydantic v2 data models & request/response schemas
│   ├── routers/
│   │   ├── cyclones.py      # Active storm tracking, cone points, and past track
│   │   ├── risk.py          # Multi-hazard risk scoring & district exposure
│   │   ├── actions.py       # SOP emergency triage recommendations & status updates
│   │   └── geospatial.py   # Earth Engine raster tile URLs & GeoJSON cone features
│   └── db/
│       ├── database.py      # SQLAlchemy session manager & table seeder
│       └── models.py        # SQLAlchemy ORM models (Districts, Hospitals, Shelters, Actions)
├── .env                     # Local environment variables
├── requirements.txt         # Python dependencies
└── README.md                # Documentation & API catalog
```

---

## 🚀 Setup & Execution

### 1. Create and Activate Python Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the FastAPI Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The database (`cyclone_risk.db`) will automatically initialize and populate baseline seed data on startup.

---

## 📡 API Endpoints Catalog

### 🌪️ Cyclones & Tracking (`/api/v1/cyclones`)
- `GET /api/v1/cyclones/active` — Real-time active storm eye position, past trajectory, and forecast cone.
- `GET /api/v1/cyclones/all` — List all tracked storms.
- `GET /api/v1/cyclones/{cyclone_id}` — Detailed storm profile by cyclone ID.

### ⚠️ Risk & Exposure (`/api/v1/risk`)
- `GET /api/v1/risk/exposure/{cyclone_id}` — Population at risk, district vulnerability ranking, affected hospitals, and executive threat summary.
- `GET /api/v1/risk/districts/{cyclone_id}` — District-wise risk score breakdown.

### 🛡️ Actions & SOPs (`/api/v1/actions`)
- `GET /api/v1/actions/recommendations/{cyclone_id}` — Prioritized disaster SOP checklists by phase (*Pre-Landfall*, *Landfall*, *Post-Landfall*).
- `POST /api/v1/actions/update-status` — Update triage action state (`PENDING`, `IN_PROGRESS`, `COMPLETED`).
  ```json
  {
    "action_id": "ACT-001",
    "status": "COMPLETED"
  }
  ```

### 🛰️ Geospatial Layers (`/api/v1/geospatial`)
- `GET /api/v1/geospatial/layers` — Active Sentinel-1 SAR flood & NASA GPM rainfall tile endpoints.
- `GET /api/v1/geospatial/cone/{cyclone_id}` — GeoJSON Polygon feature collection of the 72-hour cone of uncertainty.

### ⚡ Real-Time WebSocket Alerts (`/api/v1/ws/alerts`)
- `WS /api/v1/ws/alerts` — Live WebSocket channel for broadcasting real-time emergency bulletins to the frontend dashboard.

---

## 🧪 Interactive API Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
