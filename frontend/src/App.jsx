import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import MapDashboard from './components/MapDashboard';
import RiskPanel from './components/RiskPanel';
import ActionFeed from './components/ActionFeed';
import ToastContainer from './components/ToastContainer';
import LoadingSkeleton from './components/LoadingSkeleton';
import { 
  fetchActiveCyclone, 
  fetchRiskExposure, 
  fetchActionRecommendations, 
  fetchAIBriefing,
  fetchGeospatialLayers,
  connectAlertWebSocket 
} from './services/api';
import { getDemoState } from './services/demoData';

// ═══════════════════════════════════════════
//  APP MODES:
//  'demo'  → Cyclone Fani replay (24h compressed to 24 min)
//  'live'  → Real-time data from Vikash's backend
// ═══════════════════════════════════════════
const INITIAL_MODE = 'demo'; // Change to 'live' when backend is ready

export default function App() {
  const [mode, setMode] = useState(INITIAL_MODE);
  const [cyclone, setCyclone] = useState(null);
  const [risk, setRisk] = useState(null);
  const [actions, setActions] = useState([]);
  const [shelters, setShelters] = useState([]);
  const [aiBriefing, setAiBriefing] = useState(null);
  const [geospatialLayers, setGeospatialLayers] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [livePhase, setLivePhase] = useState('PRE_LANDFALL');
  const [demoProgress, setDemoProgress] = useState(0);
  const [fastForward, setFastForward] = useState(false);
  
  const demoStateRef = useRef({
    lastTickTime: Date.now(),
    simulatedElapsedMs: 0,
    triggeredAlerts: new Set()
  });
  const fastForwardRef = useRef(false);

  useEffect(() => {
    fastForwardRef.current = fastForward;
  }, [fastForward]);

  // ── DEMO MODE: Tick every second ──
  useEffect(() => {
    if (mode !== 'demo') return;

    // Reset demo state on mount or mode switch
    demoStateRef.current = {
      lastTickTime: Date.now(),
      simulatedElapsedMs: 0,
      triggeredAlerts: new Set()
    };

    const DEMO_ALERTS = [
      { delay: 10000,  severity: 'HIGH',   message: 'IMD upgrades Cyclone Hudhud to Very Severe Cyclonic Storm. Red Alert issued for Visakhapatnam.' },
      { delay: 30000,  severity: 'MEDIUM', message: 'Vizag airport operations suspended. All flights diverted to Hyderabad.' },
      { delay: 60000,  severity: 'HIGH',   message: 'Storm surge warning: 1.4-2.0m surge expected along Visakhapatnam coast within 12 hours.' },
      { delay: 120000, severity: 'HIGH',   message: 'Evacuation update: 280,000 of 350,000 residents evacuated from low-lying areas in Visakhapatnam district.' },
      { delay: 300000, severity: 'MEDIUM', message: 'Indian Navy deploys INS Airavat and 3 patrol vessels for standby rescue operations off Vizag coast.' },
      { delay: 600000, severity: 'HIGH',   message: 'NDRF 6th Battalion deployed at Visakhapatnam with 18 rescue teams and inflatable boats.' },
      { delay: 900000, severity: 'HIGH',   message: 'LANDFALL IMMINENT: Eye of Cyclone Hudhud 30km from Visakhapatnam coast. Winds exceeding 185 km/h.' },
      { delay: 1200000, severity: 'HIGH',  message: 'LANDFALL IN PROGRESS at Visakhapatnam. Total power grid failure. All communication lines severed.' },
      { delay: 1500000, severity: 'MEDIUM', message: 'Post-landfall: 40,000+ trees uprooted across Vizag. NH-16 blocked at multiple points.' },
    ];

    function tick() {
      const now = Date.now();
      const dt = now - demoStateRef.current.lastTickTime;
      demoStateRef.current.lastTickTime = now;

      // 10x speed multiplier when fast forwarding
      const multiplier = fastForwardRef.current ? 15 : 1; 
      demoStateRef.current.simulatedElapsedMs += dt * multiplier;

      const simTime = demoStateRef.current.simulatedElapsedMs;
      const state = getDemoState(simTime);

      setCyclone(state.cyclone);
      setRisk(state.risk);
      setActions(state.actions);
      setShelters(state.shelters);
      setLivePhase(state.phase);
      setDemoProgress(state.progress);
      setAiBriefing({
        executive_summary: state.risk.executive_summary,
        threat_level: state.risk.threat_level,
        high_risk_districts: state.risk.high_risk_districts.map(d => d.district_name),
        evidence_used: ['IMD Best Track Archive (2014)', 'Sentinel-1 SAR Flood Analysis', 'NASA GPM IMERG Rainfall', 'JTWC Historical Records', 'AP SDMA Damage Reports'],
        mode: 'demo_replay'
      });
      setGeospatialLayers(null);
      setLoading(false);

      // Check alerts
      DEMO_ALERTS.forEach((alert, index) => {
        if (simTime >= alert.delay && !demoStateRef.current.triggeredAlerts.has(index)) {
          demoStateRef.current.triggeredAlerts.add(index);
          setAlerts(prev => [{
            type: 'ALERT',
            severity: alert.severity,
            message: alert.message,
            timestamp: new Date().toISOString(),
            source: 'CycloneRiskEngine (Demo)'
          }, ...prev].slice(0, 20));
        }
      });
    }

    tick(); // First render immediately
    // Run tick slightly faster so fast-forward is smooth
    const interval = setInterval(tick, 200); 
    return () => clearInterval(interval);
  }, [mode]);

  // ── LIVE MODE: Fetch from backend ──
  useEffect(() => {
    if (mode !== 'live') return;

    async function loadData() {
      try {
        const storm = await fetchActiveCyclone();
        setCyclone(storm);
        const [riskData, actionsData, briefing, layersData] = await Promise.all([
          fetchRiskExposure(storm.cyclone_id),
          fetchActionRecommendations(storm.cyclone_id),
          fetchAIBriefing(storm.cyclone_id),
          fetchGeospatialLayers(storm.cyclone_id).catch(() => null)
        ]);
        setRisk(riskData);
        setActions(actionsData);
        setAiBriefing(briefing);
        setGeospatialLayers(layersData);
      } catch (e) {
        console.error('Failed to load live data:', e);
      } finally {
        setLoading(false);
      }
    }
    loadData();

    // Auto-refresh every 2 minutes in live mode
    const interval = setInterval(loadData, 120000);
    return () => clearInterval(interval);
  }, [mode]);

  // ── WebSocket Alerts (live mode only) ──
  useEffect(() => {
    if (mode !== 'live') return;

    const handleAlert = (data) => {
      if (data.type === 'SYSTEM_INFO') return;
      setAlerts(prev => [data, ...prev].slice(0, 20));
    };

    const cleanup = connectAlertWebSocket(handleAlert);
    return cleanup;
  }, [mode]);

  // ── Mode Switch Handler ──
  const handleModeSwitch = () => {
    const newMode = mode === 'demo' ? 'live' : 'demo';
    setMode(newMode);
    setLoading(true);
    setCyclone(null);
    setRisk(null);
    setActions([]);
    setLivePhase('PRE_LANDFALL');
    setDemoProgress(0);
  };

  if (loading) return <LoadingSkeleton />;

  return (
    <div className="flex flex-col h-screen w-screen bg-[#090d16] text-gray-100 overflow-hidden font-sans">
      {/* Toast Notifications */}
      <ToastContainer alerts={alerts} />

      {/* Top Alert Header */}
      <Navbar cyclone={cyclone} risk={risk} livePhase={livePhase} alerts={alerts} />

      {/* Mode Switch + Demo Progress */}
      <div className="flex items-center px-4 pt-1 pb-0 space-x-3">
        <button
          onClick={handleModeSwitch}
          className={`text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-full border transition-all ${
            mode === 'demo'
              ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 hover:bg-amber-500/30'
              : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 hover:bg-emerald-500/30'
          }`}
        >
          {mode === 'demo' ? '\u25B6 Demo: Cyclone Hudhud Replay' : '\u25C9 Live: Real-Time Data'}
        </button>

        {mode === 'demo' && (
          <div className="flex items-center space-x-2 flex-1">
            <button
              onClick={() => setFastForward(!fastForward)}
              className={`text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-full border transition-all ${
                fastForward 
                  ? 'bg-red-500/20 text-red-300 border-red-500/40 hover:bg-red-500/30' 
                  : 'bg-gray-800 text-gray-400 border-gray-700 hover:bg-gray-700'
              }`}
            >
              {fastForward ? '\u23E9 15x Speed' : '\u23E9 Fast Forward'}
            </button>
            <div className="flex-1 h-1 bg-gray-800 rounded-full overflow-hidden max-w-xs">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-red-500 rounded-full transition-all duration-200"
                style={{ width: `${demoProgress * 100}%` }}
              />
            </div>
            <span className="text-[10px] text-gray-500 font-mono min-w-[80px]">
              {Math.round(demoProgress * 30)}h / 30h
            </span>
          </div>
        )}

        {mode === 'live' && (
          <span className="text-[10px] text-emerald-400/60 font-mono flex items-center space-x-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Connected to Vikash&apos;s pipeline</span>
          </span>
        )}
      </div>

      {/* Main Command Center Split Screen */}
      <main className="flex-1 grid grid-cols-12 gap-4 p-4 pt-2 min-h-0 overflow-hidden">
        {/* Left Side: 70% Interactive GIS Map */}
        <div className="col-span-8 h-full">
          <MapDashboard 
            cyclone={cyclone} 
            risk={risk} 
            onPhaseChange={mode === 'live' ? setLivePhase : undefined}
            mode={mode}
            shelters={shelters}
            geospatialLayers={geospatialLayers}
          />
        </div>

        {/* Right Side: 30% Analytics, AI Briefing & Action SOPs */}
        <div className="col-span-4 h-full flex flex-col space-y-4 overflow-y-auto pr-1">
          <RiskPanel risk={risk} />
          <ActionFeed 
            risk={risk} 
            actions={actions} 
            livePhase={livePhase} 
            aiBriefing={aiBriefing}
            cyclone={cyclone}
          />
        </div>
      </main>
    </div>
  );
}
