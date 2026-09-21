# 🛰️ Geospatial, Earth Engine & Gemini AI Domain (`geospatial_ai/`)

**Owner: Vikash**

This module handles:
1. **Cyclone & Weather Data Ingestion**: Live feeds from IMD / NOAA / Open-Meteo.
2. **Google Earth Engine (GEE)**: Sentinel-1 SAR flood inundation mapping & GPM rainfall accumulation tile generation.
3. **Gemini 3.7 Flash AI**: Automated disaster briefings, district triage, and multimodal satellite image analysis.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
Ensure your `.env` contains:
```env
GEMINI_API_KEY="your-gemini-api-key"
GEE_PROJECT_ID="your-gee-project-id"
```

### 3. Run Ingestion / Test Pipelines
```bash
# Test Cyclone Ingestion
python data_ingestion/cyclone_tracker.py

# Test GEE Pipeline
python gee/gee_pipeline.py

# Test Gemini Advisory Engine
python gemini/ai_advisor.py
```
