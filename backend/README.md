# ⚙️ FastAPI Backend & Risk/Action Engine (`backend/`)

**Owner: Krishna**

This module provides:
1. **REST & WebSocket API Endpoints** for active cyclones, geospatial layer tiles, risk scores, and Gemini AI briefings.
2. **Risk & Exposure Engine**: Cone of uncertainty calculations, spatial intersection with population/hospitals, and composite multi-hazard risk indices.
3. **Action SOP Engine**: Dynamic rule-based emergency triage and action item dispatching.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the FastAPI Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Explore Interactive API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📡 API Endpoints Summary

- `GET  /api/v1/cyclones/active` - Active storm coordinates & forecast track
- `GET  /api/v1/cyclones/layers` - GEE SAR Flood & GPM Rainfall Tile URLs
- `GET  /api/v1/risk/exposure/{cyclone_id}` - Exposed population, affected districts & hospitals
- `GET  /api/v1/actions/recommendations/{cyclone_id}` - AI + Rule-based mitigation SOP checklist
- `POST /api/v1/actions/update-status` - Update triage SOP status (Pending -> Deployed)
- `WS   /api/v1/ws/alerts` - Real-time WebSocket emergency alert feed
