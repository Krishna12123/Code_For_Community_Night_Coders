# 🖥️ React GIS Dashboard (`frontend/`)

**Owner: Harshit**

This application provides the real-time Command Center Dashboard:
1. **Interactive GIS Map**: Visualizes cyclone trajectory, forecast cone of uncertainty, wind buffer rings, and GEE raster layers (Sentinel-1 SAR flood extent & GPM rainfall).
2. **KPI Analytics Panel**: Live counters for Category, Central Pressure, Population at Risk, and Flooded District statistics.
3. **AI Situation Briefing & Action SOP Center**: Real-time Gemini 3.7 Flash advisory report with interactive triage action toggles.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🎨 Component Architecture
- `src/components/Navbar.jsx` - Top storm alert header, Category badge, Landfall timer
- `src/components/MapDashboard.jsx` - Interactive geospatial canvas with layer controls
- `src/components/RiskPanel.jsx` - Exposure KPI cards and district vulnerability metrics
- `src/components/ActionFeed.jsx` - Gemini disaster briefing & interactive SOP checklist
- `src/services/api.js` - API client connected to Krishna's FastAPI backend
