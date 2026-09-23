# 📦 Backend Data Contracts & Object Reference (`object.md`)

This document defines the complete data specifications, Pydantic models, and JSON payload examples for all data objects that the **FastAPI Backend (Krishna)** expects and consumes from **Vikash's Geospatial & AI Domain (`geospatial_ai/`)** for both **Day 1** and **Day 2**.

---

## 📑 Table of Contents

1. [Overview & Data Flow Architecture](#-overview--data-flow-architecture)
2. [📅 DAY 1 Objects](#-day-1-objects)
   - [1.1 Cyclone Tracking & Trajectory Object (`CycloneData`)](#11-cyclone-tracking--trajectory-object-cyclonedata)
   - [1.2 Live Marine Weather Object (`WeatherData`)](#12-live-marine-weather-object-weatherdata)
   - [1.3 Baseline Geospatial Tile Layer (`LayerInfo`)](#13-baseline-geospatial-tile-layer-layerinfo)
   - [1.4 Baseline Situation Summary (`AdvisoryBriefing`)](#14-baseline-situation-summary-advisorybriefing)
3. [📅 DAY 2 Objects](#-day-2-objects)
   - [2.1 GEE Sentinel-1 SAR Flood Inundation Layer (`LayerInfo`)](#21-gee-sentinel-1-sar-flood-inundation-layer-layerinfo)
   - [2.2 GEE NASA GPM Precipitation Accumulation Layer (`LayerInfo`)](#22-gee-nasa-gpm-precipitation-accumulation-layer-layerinfo)
   - [2.3 Multi-Hazard Geospatial Evidence Object (`GeospatialEvidence`)](#23-multi-hazard-geospatial-evidence-object-geospatialevidence)
   - [2.4 Gemini Deep Reasoning Disaster Briefing & SOP Object (`AdvisoryBriefing`)](#24-gemini-deep-reasoning-disaster-briefing--sop-object-advisorybriefing)
4. [🔗 Backend Consumption & Endpoint Mapping](#-backend-consumption--endpoint-mapping)

---

## 🌐 Overview & Data Flow Architecture

```mermaid
flowchart TD
    subgraph Vikash [Geospatial AI Domain: geospatial_ai]
        CT[CycloneTracker] --> D1_Cyc[1.1 CycloneData]
        CT --> D1_Wth[1.2 WeatherData]
        GEE[GEEPipeline] --> D2_SAR[2.1 SAR Flood Layer]
        GEE --> D2_GPM[2.2 GPM Rain Layer]
        GEE --> D2_Evi[2.3 GeospatialEvidence]
        GEM[GeminiDisasterAdvisor] --> D2_Adv[2.4 AdvisoryBriefing]
    end

    subgraph BackendBridge [Backend Service Layer: app/services]
        D1_Cyc --> DB_Track[data_bridge.py]
        D1_Wth --> DB_Track
        D2_SAR --> DB_Tile[data_bridge.py]
        D2_GPM --> DB_Tile
        D2_Evi --> DB_Risk[risk_engine.py]
        D2_Adv --> DB_AI[ai.py Router]
    end

    subgraph Endpoints [FastAPI Endpoints: app/routers]
        DB_Track --> API_Cyc[/api/v1/cyclones/active]
        DB_Track --> API_Cone[/api/v1/geospatial/cone]
        DB_Track --> API_Buf[/api/v1/geospatial/wind-buffers]
        DB_Tile --> API_Geo[/api/v1/geospatial/layers]
        DB_Risk --> API_Risk[/api/v1/risk/exposure/{id}]
        DB_AI --> API_AI[/api/v1/ai/briefing/{id}]
    end
```

---

## 📅 DAY 1 Objects

### 1.1 Cyclone Tracking & Trajectory Object (`CycloneData`)

- **Source**: `geospatial_ai.data_ingestion.cyclone_tracker.CycloneTracker.get_active_cyclone()`
- **Backend Consumer**: `backend.app.services.data_bridge.DataBridge.get_cyclone_tracking_data()`
- **Purpose**: Feeds live storm coordinates, wind category, historical path, and forecast trajectory for cone rendering and risk calculation.

#### Pydantic Schema:
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime

class Point(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    recorded_at: datetime
    wind_kmh: Optional[float] = Field(None, description="Sustained wind speed at this eye position")
    uncertainty_radius_km: Optional[float] = Field(0.0, description="Forecast uncertainty cone radius in km")

class CycloneData(BaseModel):
    cyclone_id: str = Field(..., example="CYC-2026-01")
    name: str = Field(..., example="Cyclone Vardah-II")
    source: Literal["live", "synthetic_fixture"]
    category: int = Field(..., ge=1, le=5, description="IMD/Saffir-Simpson intensity scale")
    max_sustained_wind_kmh: float = Field(..., example=165.0)
    central_pressure_mb: Optional[float] = Field(960.0, description="Central pressure in millibars")
    current_position: Point
    past_track: List[Point] = []
    forecast_track: List[Point] = []
    metadata: Dict[str, Any] = {}
```

#### JSON Example:
```json
{
  "cyclone_id": "CYC-2026-01",
  "name": "Cyclone Vardah-II",
  "source": "synthetic_fixture",
  "category": 3,
  "max_sustained_wind_kmh": 165.0,
  "central_pressure_mb": 960.0,
  "current_position": {
    "lat": 14.5,
    "lon": 82.1,
    "recorded_at": "2026-09-24T01:00:00Z",
    "wind_kmh": 165.0,
    "uncertainty_radius_km": 15.0
  },
  "past_track": [
    { "lat": 12.8, "lon": 85.2, "recorded_at": "2026-09-23T07:00:00Z", "wind_kmh": 110.0, "uncertainty_radius_km": 0.0 },
    { "lat": 13.4, "lon": 84.1, "recorded_at": "2026-09-23T13:00:00Z", "wind_kmh": 135.0, "uncertainty_radius_km": 0.0 },
    { "lat": 14.0, "lon": 83.0, "recorded_at": "2026-09-23T19:00:00Z", "wind_kmh": 150.0, "uncertainty_radius_km": 0.0 },
    { "lat": 14.5, "lon": 82.1, "recorded_at": "2026-09-24T01:00:00Z", "wind_kmh": 165.0, "uncertainty_radius_km": 0.0 }
  ],
  "forecast_track": [
    { "lat": 15.0, "lon": 81.3, "recorded_at": "2026-09-24T07:00:00Z", "wind_kmh": 175.0, "uncertainty_radius_km": 35.0 },
    { "lat": 15.6, "lon": 80.5, "recorded_at": "2026-09-24T13:00:00Z", "wind_kmh": 180.0, "uncertainty_radius_km": 50.0 },
    { "lat": 16.1, "lon": 79.8, "recorded_at": "2026-09-24T19:00:00Z", "wind_kmh": 150.0, "uncertainty_radius_km": 70.0 },
    { "lat": 16.7, "lon": 79.1, "recorded_at": "2026-09-25T01:00:00Z", "wind_kmh": 95.0, "uncertainty_radius_km": 90.0 }
  ],
  "metadata": {
    "basin": "North Indian Ocean (Bay of Bengal)",
    "landfall_expected": "South Andhra Pradesh Coast",
    "agency": "IMD / JTWC"
  }
}
```

---

### 1.2 Live Marine Weather Object (`WeatherData`)

- **Source**: `geospatial_ai.data_ingestion.cyclone_tracker.CycloneTracker.fetch_live_marine_weather()`
- **Backend Consumer**: `backend.app.services.data_bridge.DataBridge`
- **Purpose**: Real-time ground truth surface weather at storm coordinates.

#### Pydantic Schema:
```python
class WeatherData(BaseModel):
    source: Literal["live", "mock_fixture"]
    wind_speed_kmh: float
    wind_direction_deg: float
    surface_pressure_hpa: float
    precipitation_mm: float
```

#### JSON Example:
```json
{
  "source": "live",
  "wind_speed_kmh": 168.5,
  "wind_direction_deg": 315.0,
  "surface_pressure_hpa": 962.4,
  "precipitation_mm": 48.6
}
```

---

### 1.3 Baseline Geospatial Tile Layer (`LayerInfo`)

- **Source**: `geospatial_ai.gee.gee_pipeline.GEEPipeline`
- **Backend Consumer**: `backend.app.routers.geospatial`
- **Purpose**: Base map raster endpoints for SAR and Rainfall overlays.

#### JSON Example:
```json
{
  "dataset": "COPERNICUS/S1_GRD",
  "status": "available",
  "start_date": "2026-09-22",
  "end_date": "2026-09-24",
  "tile_url": "https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
  "reason": null
}
```

---

### 1.4 Baseline Situation Summary (`AdvisoryBriefing`)

- **Source**: `geospatial_ai.gemini.ai_advisor.GeminiDisasterAdvisor`
- **Backend Consumer**: `backend.app.routers.ai`
- **Purpose**: Initial text summary of storm status.

#### JSON Example:
```json
{
  "executive_summary": "Severe Cyclonic Storm 'Cyclone Vardah-II' is packing sustained winds of 165 km/h with central pressure 960 mb. Projected landfall along coastal Andhra Pradesh within 18 hours.",
  "threat_level": "RED",
  "high_risk_districts": ["Nellore", "Prakasam", "Bapatla"],
  "critical_actions": [
    {
      "priority": "HIGH",
      "phase": "PRE_LANDFALL",
      "sector": "Evacuation",
      "instruction": "Advise evacuation of all habitations within 5km from coastline."
    }
  ],
  "evidence_used": ["Simulated cyclone track", "Mock GPM accumulation"],
  "limitations": ["Demo scenario mode. Ground truth pending satellite overpass."],
  "mode": "demo_fixture"
}
```

---

## 📅 DAY 2 Objects

### 2.1 GEE Sentinel-1 SAR Flood Inundation Layer (`LayerInfo`)

- **Source**: `geospatial_ai.gee.gee_pipeline.GEEPipeline.get_sar_flood_layer(bbox, start_date, end_date)`
- **Backend Consumer**: `backend.app.services.data_bridge.DataBridge.get_gee_layers()`
- **Purpose**: Live cloud-penetrating Sentinel-1 SAR water mask XYZ tile URL for frontend raster display.

#### Pydantic Schema:
```python
class LayerInfo(BaseModel):
    dataset: str = "COPERNICUS/S1_GRD"
    status: Literal["available", "unavailable"]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    accumulation_mm: Optional[float] = None
    tile_url: Optional[str] = None
    reason: Optional[str] = None
```

#### JSON Example:
```json
{
  "dataset": "COPERNICUS/S1_GRD",
  "status": "available",
  "start_date": "2026-09-22",
  "end_date": "2026-09-24",
  "tile_url": "https://earthengine.googleapis.com/v1/projects/earthengine-legacy/maps/d598e21a2c53f88c-c89b7b91345/tiles/{z}/{x}/{y}",
  "reason": null
}
```

---

### 2.2 GEE NASA GPM Precipitation Accumulation Layer (`LayerInfo`)

- **Source**: `geospatial_ai.gee.gee_pipeline.GEEPipeline.get_gpm_rainfall_layer(bbox, start_date, end_date)`
- **Backend Consumer**: `backend.app.services.data_bridge.DataBridge.get_gee_layers()`
- **Purpose**: NASA GPM IMERG 24-hour total precipitation accumulation heatmap tile URL.

#### JSON Example:
```json
{
  "dataset": "NASA/GPM_L3/IMERG_V07",
  "status": "available",
  "start_date": "2026-09-22",
  "end_date": "2026-09-24",
  "accumulation_mm": 185.4,
  "tile_url": "https://earthengine.googleapis.com/v1/projects/earthengine-legacy/maps/a883e32b1f09c71a-e99d8a87612/tiles/{z}/{x}/{y}",
  "reason": null
}
```

---

### 2.3 Multi-Hazard Geospatial Evidence Object (`GeospatialEvidence`)

- **Source**: `geospatial_ai.gee.gee_pipeline.GEEPipeline.generate_evidence(bbox, date_str)`
- **Backend Consumer**: Passed into `GeminiDisasterAdvisor` & parsed for Flood Depth calculations in `risk_engine.py`.
- **Purpose**: Bundles spatial bounding box, SAR flood mask, and GPM precipitation into an evidence package.

#### Pydantic Schema:
```python
class GeospatialEvidence(BaseModel):
    analysis_region: Dict[str, Any]
    rainfall: LayerInfo
    flood: LayerInfo
    generated_at: datetime
```

#### JSON Example:
```json
{
  "analysis_region": {
    "bbox": [79.5, 12.5, 84.5, 17.5],
    "date": "2026-09-24"
  },
  "rainfall": {
    "dataset": "NASA/GPM_L3/IMERG_V07",
    "status": "available",
    "start_date": "2026-09-22",
    "end_date": "2026-09-24",
    "accumulation_mm": 185.4,
    "tile_url": "https://earthengine.googleapis.com/v1/projects/.../tiles/{z}/{x}/{y}"
  },
  "flood": {
    "dataset": "COPERNICUS/S1_GRD",
    "status": "available",
    "start_date": "2026-09-22",
    "end_date": "2026-09-24",
    "tile_url": "https://earthengine.googleapis.com/v1/projects/.../tiles/{z}/{x}/{y}"
  },
  "generated_at": "2026-09-24T01:00:00Z"
}
```

---

### 2.4 Gemini Deep Reasoning Disaster Briefing & SOP Object (`AdvisoryBriefing`)

- **Source**: `geospatial_ai.gemini.ai_advisor.GeminiDisasterAdvisor.generate_situation_briefing(storm_data, exposure_data, geospatial_evidence)`
- **Backend Consumer**: `backend.app.routers.ai` (`GET /api/v1/ai/briefing/{cyclone_id}`)
- **Purpose**: Structured AI commander situation assessment, prioritized high-risk districts, and sector-wise emergency action recommendations.

#### Pydantic Schema:
```python
class Action(BaseModel):
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    phase: Literal["PRE_LANDFALL", "LANDFALL", "POST_LANDFALL"]
    sector: Literal["Evacuation", "Medical", "Shelter", "Power", "Rescue", "Logistics", "Emergency"]
    instruction: str

class AdvisoryBriefing(BaseModel):
    executive_summary: str
    threat_level: Literal["RED", "ORANGE", "YELLOW", "GREEN", "UNKNOWN"]
    high_risk_districts: List[str]
    critical_actions: List[Action]
    evidence_used: List[str] = []
    limitations: List[str] = []
    mode: Literal["live", "demo_fixture"] = "live"
```

#### JSON Example:
```json
{
  "executive_summary": "Severe Cyclonic Storm 'Cyclone Vardah-II' packing sustained winds of 165 km/h with central pressure 960 mb is tracking WNW towards the south Andhra Pradesh coastline with expected landfall in Prakasam/Nellore district border within 18 hours. Multi-hazard satellite radar indicates 142.5 sq km inundation along low-lying coastal estuaries. Immediate high alert and evacuation of 0-5km coastal habitations is mandatory.",
  "threat_level": "RED",
  "high_risk_districts": [
    "Nellore",
    "Prakasam",
    "Bapatla",
    "Krishna"
  ],
  "critical_actions": [
    {
      "priority": "HIGH",
      "phase": "PRE_LANDFALL",
      "sector": "Evacuation",
      "instruction": "Initiate mandatory evacuation within 5km coastal belt in Nellore & Prakasam districts."
    },
    {
      "priority": "HIGH",
      "phase": "PRE_LANDFALL",
      "sector": "Medical",
      "instruction": "Pre-position backup diesel generators (100kVA) and trauma medicine stocks in 13 coastal hospitals."
    },
    {
      "priority": "HIGH",
      "phase": "PRE_LANDFALL",
      "sector": "Shelter",
      "instruction": "Activate 72 designated cyclone relief shelters with 3-day dry rations and water supply."
    },
    {
      "priority": "MEDIUM",
      "phase": "LANDFALL",
      "sector": "Power",
      "instruction": "Pre-emptively de-energize overhead 33kV/11kV power distribution lines in high-wind swath."
    },
    {
      "priority": "MEDIUM",
      "phase": "POST_LANDFALL",
      "sector": "Rescue",
      "instruction": "Mobilize 12 NDRF & SDRF search and rescue boat teams along vulnerable river estuaries."
    }
  ],
  "evidence_used": [
    "IMD/NOAA Active Cyclone Track & Wind Radii",
    "Copernicus Sentinel-1 SAR Flood Inundation Mask",
    "NASA GPM IMERG 24-Hr Precipitation Heatmap"
  ],
  "limitations": [
    "Satellite overpass interval has 3-6 hour latency. Ground truth validation recommended."
  ],
  "mode": "live"
}
```

---

## 🔗 Backend Consumption & Endpoint Mapping

| Vikash Object | Backend Service Layer | FastAPI Endpoint Exposed to Harshit (Frontend) |
| :--- | :--- | :--- |
| `CycloneData` | [`data_bridge.py`](file:///Users/krishnashukla/Desktop/cylone_project/backend/app/services/data_bridge.py) | `GET /api/v1/cyclones/active`<br>`GET /api/v1/cyclones/all`<br>`GET /api/v1/cyclones/{id}` |
| `CycloneData.forecast_track` | [`geometry_engine.py`](file:///Users/krishnashukla/Desktop/cylone_project/backend/app/services/geometry_engine.py) | `GET /api/v1/geospatial/cone/{id}` *(GeoJSON Polygon)* |
| `CycloneData.current_position` | [`geometry_engine.py`](file:///Users/krishnashukla/Desktop/cylone_project/backend/app/services/geometry_engine.py) | `GET /api/v1/geospatial/wind-buffers/{id}` *(34kt, 50kt, 64kt GeoJSON)* |
| `LayerInfo` (SAR & GPM) | [`data_bridge.py`](file:///Users/krishnashukla/Desktop/cylone_project/backend/app/services/data_bridge.py) | `GET /api/v1/geospatial/layers` |
| `CycloneData` + `DistrictDB` | [`risk_engine.py`](file:///Users/krishnashukla/Desktop/cylone_project/backend/app/services/risk_engine.py) | `GET /api/v1/risk/exposure/{id}`<br>`GET /api/v1/risk/districts/{id}` |
| `AdvisoryBriefing` | [`ai.py`](file:///Users/krishnashukla/Desktop/cylone_project/backend/app/routers/ai.py) | `GET /api/v1/ai/briefing/{id}` |
| `AdvisoryBriefing.critical_actions` | [`action_engine.py`](file:///Users/krishnashukla/Desktop/cylone_project/backend/app/services/action_engine.py) | `GET /api/v1/actions/recommendations/{id}`<br>`POST /api/v1/actions/update-status` |
