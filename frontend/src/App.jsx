import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MapDashboard from './components/MapDashboard';
import RiskPanel from './components/RiskPanel';
import ActionFeed from './components/ActionFeed';
import { fetchActiveCyclone, fetchRiskExposure, fetchActionRecommendations } from './services/api';
import { Bell, X, AlertTriangle, Radio } from 'lucide-react';

export default function App() {
  const [cyclone, setCyclone] = useState(null);
  const [risk, setRisk] = useState(null);
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [livePhase, setLivePhase] = useState('PRE_LANDFALL');
  const [liveAlert, setLiveAlert] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const storm = await fetchActiveCyclone();
        setCyclone(storm);
        const [riskData, actionsData] = await Promise.all([
          fetchRiskExposure(storm.cyclone_id),
          fetchActionRecommendations(storm.cyclone_id)
        ]);
        setRisk(riskData);
        setActions(actionsData);
      } catch (e) {
        console.error('Failed to load initial data:', e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // WebSocket for real-time emergency alert broadcasting
  useEffect(() => {
    const wsUrl = import.meta.env?.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws/alerts';
    let socket = null;
    let retryTimeout = null;

    function connectWs() {
      try {
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
          console.log('[WebSocket] Connected to Emergency Alert Stream');
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'EMERGENCY_BROADCAST' || data.type === 'THREAT_ESCALATION') {
              setLiveAlert(data);
            }
          } catch (err) {
            console.warn('[WebSocket] Message parse error:', err);
          }
        };

        socket.onclose = () => {
          console.log('[WebSocket] Disconnected. Reconnecting in 5s...');
          retryTimeout = setTimeout(connectWs, 5000);
        };

        socket.onerror = () => {
          socket?.close();
        };
      } catch (err) {
        console.warn('[WebSocket] Setup error:', err);
      }
    }

    connectWs();

    return () => {
      if (retryTimeout) clearTimeout(retryTimeout);
      if (socket) socket.close();
    };
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen bg-[#090d16] text-gray-100 overflow-hidden font-sans">
      {/* Top Alert Header */}
      <Navbar cyclone={cyclone} risk={risk} livePhase={livePhase} />

      {/* Live Emergency Broadcast Banner (Day 3 Feature) */}
      {liveAlert && (
        <div className="bg-red-600/95 border-b border-red-400 text-white px-6 py-2 flex items-center justify-between shadow-2xl animate-pulse z-30">
          <div className="flex items-center space-x-3">
            <div className="p-1 bg-white/20 rounded-full">
              <AlertTriangle className="w-5 h-5 text-yellow-300" />
            </div>
            <span className="font-bold text-xs uppercase tracking-wider bg-black/40 px-2 py-0.5 rounded">
              {liveAlert.severity || 'CRITICAL ALERT'}
            </span>
            <span className="text-xs font-medium">
              {liveAlert.headline || liveAlert.message}
            </span>
          </div>
          <button
            onClick={() => setLiveAlert(null)}
            className="text-white/80 hover:text-white p-1 hover:bg-white/10 rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Main Command Center Split Screen */}
      <main className="flex-1 grid grid-cols-12 gap-4 p-4 min-h-0 overflow-hidden">
        {/* Left Side: 70% Interactive GIS Map */}
        <div className="col-span-8 h-full">
          <MapDashboard 
            cyclone={cyclone} 
            risk={risk} 
            onPhaseChange={setLivePhase}
          />
        </div>

        {/* Right Side: 30% Analytics, AI Briefing & Action SOPs */}
        <div className="col-span-4 h-full flex flex-col space-y-4 overflow-y-auto pr-1">
          <RiskPanel risk={risk} />
          <ActionFeed risk={risk} actions={actions} livePhase={livePhase} />
        </div>
      </main>
    </div>
  );
}

