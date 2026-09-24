import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MapDashboard from './components/MapDashboard';
import RiskPanel from './components/RiskPanel';
import ActionFeed from './components/ActionFeed';
import { fetchActiveCyclone, fetchRiskExposure, fetchActionRecommendations } from './services/api';

export default function App() {
  const [cyclone, setCyclone] = useState(null);
  const [risk, setRisk] = useState(null);
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [livePhase, setLivePhase] = useState('PRE_LANDFALL');

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

  return (
    <div className="flex flex-col h-screen w-screen bg-[#090d16] text-gray-100 overflow-hidden font-sans">
      {/* Top Alert Header */}
      <Navbar cyclone={cyclone} risk={risk} livePhase={livePhase} />

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
