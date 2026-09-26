/**
 * API Service Client
 * Bridges Harshit's React Frontend with Krishna's FastAPI Backend
 */

const API_BASE = import.meta.env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const fetchActiveCyclone = async () => {
  try {
    const res = await fetch(`${API_BASE}/cyclones/active`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[API] Using fallback cyclone data:', err);
    return {
      cyclone_id: 'CYC-2026-01',
      name: 'Cyclone Vardah-II',
      category: 3,
      max_sustained_wind_kmh: 165,
      central_pressure_mb: 960,
      current_position: { lat: 14.5, lon: 82.1, recorded_at: new Date().toISOString() },
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
      ]
    };
  }
};

export const fetchRiskExposure = async (cycloneId) => {
  try {
    const res = await fetch(`${API_BASE}/risk/exposure/${cycloneId}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[API] Using fallback risk data:', err);
    return {
      cyclone_id: cycloneId,
      total_population_at_risk: 1850000,
      high_risk_districts: [
        { district_name: 'Nellore', risk_score: 89.5, risk_level: 'RED', flooded_area_sq_km: 142.5, vulnerable_hospitals: 8, shelters_available: 42 },
        { district_name: 'Prakasam', risk_score: 81.0, risk_level: 'RED', flooded_area_sq_km: 98.0, vulnerable_hospitals: 5, shelters_available: 30 },
        { district_name: 'Bapatla', risk_score: 68.4, risk_level: 'ORANGE', flooded_area_sq_km: 54.2, vulnerable_hospitals: 3, shelters_available: 25 },
        { district_name: 'Krishna', risk_score: 45.0, risk_level: 'YELLOW', flooded_area_sq_km: 21.0, vulnerable_hospitals: 2, shelters_available: 38 }
      ],
      executive_summary: 'Severe Cyclonic Storm approaching coast. Mandatory coastal evacuation underway.',
      threat_level: 'RED',
      landfall_eta_hours: 18
    };
  }
};

export const fetchActionRecommendations = async (cycloneId) => {
  try {
    const res = await fetch(`${API_BASE}/actions/recommendations/${cycloneId}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[API] Using fallback actions data:', err);
    return [
      { id: 'ACT-001', priority: 'HIGH', phase: 'PRE_LANDFALL', sector: 'Evacuation', instruction: 'Evacuate 45,000 residents from low-lying coastal villages (0-5km) in Nellore.', status: 'IN_PROGRESS' },
      { id: 'ACT-002', priority: 'HIGH', phase: 'PRE_LANDFALL', sector: 'Medical', instruction: 'Deliver diesel generator backup & oxygen supplies to 8 high-risk hospitals.', status: 'COMPLETED' },
      { id: 'ACT-003', priority: 'HIGH', phase: 'PRE_LANDFALL', sector: 'Shelter', instruction: 'Activate 42 cyclone relief shelters with 72-hour dry food and potable water supplies.', status: 'IN_PROGRESS' },
      { id: 'ACT-004', priority: 'MEDIUM', phase: 'LANDFALL', sector: 'Power', instruction: 'Pre-emptively shut down secondary electrical grids in vulnerable storm-surge zones.', status: 'PENDING' }
    ];
  }
};

export const updateActionStatusApi = async (actionId, status) => {
  try {
    const res = await fetch(`${API_BASE}/actions/update-status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action_id: actionId, status })
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[API] Error updating action status:', err);
    return null;
  }
};

export const fetchAIBriefing = async (cycloneId) => {
  try {
    const res = await fetch(`${API_BASE}/ai/briefing/${cycloneId}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[API] Using fallback AI briefing:', err);
    return null;
  }
};

export const downloadSituationReportPdf = async (cycloneId = 'CYC-2026-01') => {
  try {
    const res = await fetch(`${API_BASE}/reports/situation-report/pdf/${cycloneId}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Disaster_Situation_Report_${cycloneId}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    return true;
  } catch (err) {
    console.error('[API] Failed to download Situation Report PDF:', err);
    alert('Failed to download Situation Report PDF. Check backend connectivity.');
    return false;
  }
};

export const fetchMarineWeather = async (lat = 14.5, lon = 82.1) => {
  try {
    const res = await fetch(`${API_BASE}/cyclones/marine/weather?lat=${lat}&lon=${lon}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[API] Failed to fetch live marine weather:', err);
    return {
      lat,
      lon,
      wind_speed_kmh: 32.5,
      wind_speed_kt: 17.5,
      wind_direction_deg: 215.0,
      wind_direction_cardinal: 'SSW',
      surface_pressure_hpa: 1008.5,
      source: 'Calibrated Indian Ocean Baseline'
    };
  }
};


