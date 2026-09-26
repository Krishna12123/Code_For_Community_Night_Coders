/**
 * API Service Client — Day 3 Integration
 * Bridges Harshit's React Frontend with Krishna's FastAPI Backend
 * 
 * Every function tries the real backend first, then falls back to
 * calibrated mock data so the frontend works standalone.
 */

const API_BASE = import.meta.env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// ─── Helper ───
async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}


// ═══════════════════════════════════════════
//  Cyclone Tracking
// ═══════════════════════════════════════════

export const fetchActiveCyclone = async () => {
  try {
    return await apiFetch('/cyclones/active');
  } catch (err) {
    console.warn('[API] Fallback cyclone data:', err.message);
    const now = new Date().toISOString();
    return {
      cyclone_id: 'CYC-2026-01',
      name: 'Cyclone Vardah-II',
      category: 3,
      max_sustained_wind_kmh: 165,
      central_pressure_mb: 960,
      current_position: { lat: 14.5, lon: 82.1, recorded_at: now },
      past_track: [
        { timestamp: '18h ago', lat: 12.8, lon: 85.2, wind_kmh: 110 },
        { timestamp: '12h ago', lat: 13.4, lon: 84.1, wind_kmh: 135 },
        { timestamp: '6h ago', lat: 14.0, lon: 83.0, wind_kmh: 150 },
        { timestamp: 'Now', lat: 14.5, lon: 82.1, wind_kmh: 165 }
      ],
      forecast_track: [
        { timestamp: '+6h', lat: 15.0, lon: 81.3, wind_kmh: 175, uncertainty_radius_km: 35 },
        { timestamp: '+12h', lat: 15.6, lon: 80.5, wind_kmh: 180, uncertainty_radius_km: 50 },
        { timestamp: '+18h', lat: 16.1, lon: 79.8, wind_kmh: 150, uncertainty_radius_km: 70 },
        { timestamp: '+24h', lat: 16.7, lon: 79.1, wind_kmh: 95, uncertainty_radius_km: 90 }
      ],
      metadata: { source: 'IMD / JTWC', basin: 'Bay of Bengal', landfall_expected: 'Andhra Pradesh coast' }
    };
  }
};


// ═══════════════════════════════════════════
//  Risk Exposure
// ═══════════════════════════════════════════

export const fetchRiskExposure = async (cycloneId) => {
  try {
    return await apiFetch(`/risk/exposure/${cycloneId}`);
  } catch (err) {
    console.warn('[API] Fallback risk data:', err.message);
    return {
      cyclone_id: cycloneId,
      total_population_at_risk: 1850000,
      flooded_area_sq_km: 315.7,
      high_risk_districts: [
        { district_name: 'Nellore', risk_score: 89.5, risk_level: 'RED', flooded_area_sq_km: 142.5, vulnerable_hospitals: 8, shelters_available: 42, population_exposed: 485000 },
        { district_name: 'Prakasam', risk_score: 81.0, risk_level: 'RED', flooded_area_sq_km: 98.0, vulnerable_hospitals: 5, shelters_available: 30, population_exposed: 320000 },
        { district_name: 'Bapatla', risk_score: 68.4, risk_level: 'ORANGE', flooded_area_sq_km: 54.2, vulnerable_hospitals: 3, shelters_available: 25, population_exposed: 180000 },
        { district_name: 'Krishna', risk_score: 45.0, risk_level: 'YELLOW', flooded_area_sq_km: 21.0, vulnerable_hospitals: 2, shelters_available: 38, population_exposed: 95000 }
      ],
      executive_summary: 'Severe Cyclonic Storm approaching coast. Mandatory coastal evacuation underway.',
      threat_level: 'RED',
      landfall_eta_hours: 18
    };
  }
};


// ═══════════════════════════════════════════
//  Action Recommendations
// ═══════════════════════════════════════════

export const fetchActionRecommendations = async (cycloneId) => {
  try {
    return await apiFetch(`/actions/recommendations/${cycloneId}`);
  } catch (err) {
    console.warn('[API] Fallback actions data:', err.message);
    return [
      { id: 'ACT-001', priority: 'CRITICAL', phase: 'PRE_LANDFALL', sector: 'Evacuation', instruction: 'Initiate mandatory evacuation of 45,000 residents from low-lying coastal villages (0-5km) in Nellore district.', status: 'IN_PROGRESS', assigned_agency: 'NDRF / District Emergency Operations' },
      { id: 'ACT-002', priority: 'HIGH', phase: 'PRE_LANDFALL', sector: 'Medical', instruction: 'Deploy diesel generator backup & oxygen reserves to 8 high-risk district hospitals.', status: 'COMPLETED', assigned_agency: 'Health Department' },
      { id: 'ACT-003', priority: 'HIGH', phase: 'PRE_LANDFALL', sector: 'Shelter', instruction: 'Activate 42 cyclone relief shelters with 72-hour dry food and potable water supplies.', status: 'IN_PROGRESS', assigned_agency: 'District Collector Office' },
      { id: 'ACT-004', priority: 'MEDIUM', phase: 'LANDFALL', sector: 'Power', instruction: 'Pre-emptively shut down secondary electrical grids in vulnerable storm-surge zones.', status: 'PENDING', assigned_agency: 'State Electricity Board' },
      { id: 'ACT-005', priority: 'HIGH', phase: 'LANDFALL', sector: 'Coast Guard', instruction: 'Deploy 12 NDRF teams with inflatable rescue boats along NH-16 corridor.', status: 'PENDING', assigned_agency: 'NDRF' },
      { id: 'ACT-006', priority: 'HIGH', phase: 'POST_LANDFALL', sector: 'Search & Rescue', instruction: 'Activate helicopter medevac operations in flooded Nellore and Prakasam sectors.', status: 'PENDING', assigned_agency: 'Indian Air Force / NDRF' },
      { id: 'ACT-007', priority: 'MEDIUM', phase: 'POST_LANDFALL', sector: 'Infrastructure', instruction: 'Deploy heavy cranes for debris clearance on blocked arterial roads and railway lines.', status: 'PENDING', assigned_agency: 'PWD / Indian Railways' }
    ];
  }
};


// ═══════════════════════════════════════════
//  Action Status Update (PUT to backend)
// ═══════════════════════════════════════════

export const updateActionStatus = async (actionId, newStatus) => {
  try {
    return await apiFetch('/actions/update-status', {
      method: 'POST',
      body: JSON.stringify({ action_id: actionId, status: newStatus }),
    });
  } catch (err) {
    console.warn('[API] Status update failed (offline):', err.message);
    return { status: 'offline', action_id: actionId, updated_to: newStatus };
  }
};


// ═══════════════════════════════════════════
//  Gemini AI Briefing
// ═══════════════════════════════════════════

export const fetchAIBriefing = async (cycloneId) => {
  try {
    return await apiFetch(`/ai/briefing/${cycloneId}`);
  } catch (err) {
    console.warn('[API] Fallback AI briefing:', err.message);
    return {
      cyclone_id: cycloneId,
      executive_summary: 'Severe Cyclonic Storm Vardah-II packing sustained winds of 165 km/h with central pressure 960 mb. Projected landfall along coastal Andhra Pradesh within 18 hours. High storm surge and severe inundation predicted in Nellore and Prakasam districts.',
      threat_level: 'RED',
      high_risk_districts: ['Nellore', 'Prakasam', 'Bapatla'],
      critical_actions: [
        { priority: 'HIGH', phase: 'PRE_LANDFALL', sector: 'Evacuation', instruction: 'Mandatory evacuation within 5km from coastline.' },
        { priority: 'HIGH', phase: 'PRE_LANDFALL', sector: 'Medical', instruction: 'Deploy mobile power generators and blood reserves.' }
      ],
      evidence_used: ['NOAA/IMD Cyclone Track', 'Sentinel-1 SAR Radar Flood Mask', 'NASA GPM IMERG Precipitation'],
      mode: 'calibrated_fallback'
    };
  }
};


// ═══════════════════════════════════════════
//  Geospatial Layers (GEE Tile URLs)
// ═══════════════════════════════════════════

export const fetchGeospatialLayers = async (cycloneId = 'CYC-2026-01') => {
  try {
    return await apiFetch(`/geospatial/layers?cyclone_id=${cycloneId}`);
  } catch (err) {
    console.warn('[API] Fallback layer data:', err.message);
    return {
      cyclone_id: cycloneId,
      layers: {
        sar_flood: { name: 'Sentinel-1 SAR Flood Inundation', type: 'raster_tile', tile_url: null, opacity: 0.75, status: 'offline' },
        gpm_rainfall: { name: 'GPM 24-Hr Precipitation', type: 'raster_tile', tile_url: null, opacity: 0.6, status: 'offline' }
      }
    };
  }
};


// ═══════════════════════════════════════════
//  Geospatial GeoJSON (Flood Zones, Shelters, Wind Buffers)
// ═══════════════════════════════════════════

export const fetchForecastCone = async (cycloneId = 'CYC-2026-01') => {
  try {
    return await apiFetch(`/geospatial/cone/${cycloneId}`);
  } catch (err) {
    console.warn('[API] Fallback forecast cone:', err.message);
    return null; // MapDashboard will use its local buildForecastCone()
  }
};

export const fetchWindBuffers = async (cycloneId = 'CYC-2026-01') => {
  try {
    return await apiFetch(`/geospatial/wind-buffers/${cycloneId}`);
  } catch (err) {
    console.warn('[API] Fallback wind buffers:', err.message);
    return null;
  }
};


// ═══════════════════════════════════════════
//  WebSocket Alert Connection
// ═══════════════════════════════════════════

const WS_URL = import.meta.env?.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws/alerts';

export function connectAlertWebSocket(onMessage, onError) {
  let ws;
  let reconnectTimer;

  function connect() {
    try {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log('[WS] Connected to alert channel');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch {
          console.warn('[WS] Non-JSON message:', event.data);
        }
      };

      ws.onerror = () => {
        console.warn('[WS] Connection error — alerts unavailable');
        if (onError) onError();
      };

      ws.onclose = () => {
        console.warn('[WS] Disconnected. Reconnecting in 10s...');
        reconnectTimer = setTimeout(connect, 10000);
      };
    } catch {
      console.warn('[WS] WebSocket not available');
    }
  }

  connect();

  // Return cleanup function
  return () => {
    clearTimeout(reconnectTimer);
    if (ws) ws.close();
  };
}
