/**
 * API Service Client
 * Bridges Harshit's React Frontend with Krishna's FastAPI Backend
 */

const API_BASE = import.meta.env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const fetchActiveCyclone = async () => {
  const res = await fetch(`${API_BASE}/cyclones/active`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
};

export const fetchRiskExposure = async (cycloneId) => {
  const res = await fetch(`${API_BASE}/risk/exposure/${cycloneId}`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
};

export const fetchActionRecommendations = async (cycloneId) => {
  const res = await fetch(`${API_BASE}/actions/recommendations/${cycloneId}`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
};

export const fetchAIBriefing = async (cycloneId) => {
  try {
    const res = await fetch(`${API_BASE}/ai/briefing/${cycloneId}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[API] AI briefing unavailable:', err.message);
    return {
      mode: 'unavailable',
      executive_summary: 'AI briefing is currently unavailable. Backend connection failed.',
      threat_level: 'UNKNOWN',
      high_risk_districts: [],
      critical_actions: [],
      evidence_used: [],
      limitations: ['API connection offline']
    };
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
    throw err;
  }
};

export const fetchMarineWeather = async (lat = 14.5, lon = 82.1) => {
  const res = await fetch(`${API_BASE}/cyclones/marine/weather?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
};

export const fetchGeospatialLayers = async (cycloneId = 'CYC-2026-01') => {
  const res = await fetch(`${API_BASE}/geospatial/layers?cyclone_id=${cycloneId}`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
};

export const fetchForecastCone = async (cycloneId = 'CYC-2026-01') => {
  const res = await fetch(`${API_BASE}/geospatial/cone/${cycloneId}`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
};

export const fetchWindBuffers = async (cycloneId = 'CYC-2026-01') => {
  const res = await fetch(`${API_BASE}/geospatial/wind-buffers/${cycloneId}`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
};

export const updateActionStatus = async (actionId, newStatus) => {
  const res = await fetch(`${API_BASE}/actions/update-status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_id: actionId, status: newStatus }),
  });
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
};

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

  return () => {
    clearTimeout(reconnectTimer);
    if (ws) ws.close();
  };
}

