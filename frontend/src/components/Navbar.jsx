/**
 * Top Alert Navigation Bar
 * Owner: Harshit
 *
 * Displays active cyclone name, category badge, live landfall countdown,
 * threat severity indicator, and system sync status.
 */

import React, { useState, useEffect } from 'react';
import { AlertTriangle, Radio, Clock, ShieldAlert, Wind } from 'lucide-react';

export default function Navbar({ cyclone, risk }) {
  const etaHours = risk?.landfall_eta_hours || 18;

  // Live countdown timer from ETA
  const [secondsLeft, setSecondsLeft] = useState(etaHours * 3600);

  useEffect(() => {
    setSecondsLeft(etaHours * 3600);
  }, [etaHours]);

  useEffect(() => {
    const interval = setInterval(() => {
      setSecondsLeft(prev => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const hrs = Math.floor(secondsLeft / 3600);
  const mins = Math.floor((secondsLeft % 3600) / 60);
  const secs = secondsLeft % 60;
  const pad = (n) => String(n).padStart(2, '0');

  // Category color mapping
  const catColor = cyclone?.category >= 4
    ? 'bg-fuchsia-600/90 shadow-fuchsia-900/50'
    : cyclone?.category >= 3
    ? 'bg-red-600/90 shadow-red-900/50'
    : 'bg-amber-600/90 shadow-amber-900/50';

  return (
    <header className="h-16 border-b border-gray-800 bg-gray-950/80 backdrop-blur px-6 flex items-center justify-between z-20">

      {/* Brand & Storm Identity */}
      <div className="flex items-center space-x-4">
        <div className="p-2 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center space-x-2 text-red-400 animate-pulse">
          <Wind className="w-5 h-5" />
          <span className="font-bold text-sm tracking-wider uppercase">Cyclone Command Center</span>
        </div>

        <div className="h-6 w-px bg-gray-800" />

        <div className="flex items-center space-x-3">
          <h1 className="text-lg font-bold text-white tracking-wide">
            {cyclone?.name || 'Active Storm Monitoring'}
          </h1>
          <span className={`px-2.5 py-0.5 text-xs font-semibold text-white rounded-full shadow-lg ${catColor}`}>
            CAT {cyclone?.category || 3} Severe
          </span>
          {cyclone && (
            <span className="text-[10px] font-mono text-gray-500 bg-gray-900 border border-gray-800 px-2 py-0.5 rounded">
              {cyclone.max_sustained_wind_kmh} km/h &middot; {cyclone.central_pressure_mb} hPa
            </span>
          )}
        </div>
      </div>

      {/* Metrics & Live Countdown */}
      <div className="flex items-center space-x-5 text-sm">

        {/* Landfall Countdown */}
        <div className="flex items-center space-x-2 bg-gray-900/90 border border-gray-800 px-3 py-1.5 rounded-lg">
          <Clock className="w-4 h-4 text-amber-400" />
          <span className="text-gray-400 text-xs">Landfall ETA</span>
          <span className="font-mono font-bold text-amber-300 tracking-wider text-sm">
            {pad(hrs)}:{pad(mins)}:{pad(secs)}
          </span>
        </div>

        {/* Threat Level */}
        <div className="flex items-center space-x-2 bg-gray-900/90 border border-gray-800 px-3 py-1.5 rounded-lg">
          <ShieldAlert className="w-4 h-4 text-red-400" />
          <span className="text-gray-400 text-xs">Threat</span>
          <span className="font-bold text-red-400 uppercase tracking-wider text-xs">
            {risk?.threat_level || 'RED'} ALERT
          </span>
        </div>

        {/* Live Sync Indicator */}
        <div className="flex items-center space-x-2 text-emerald-400 text-xs font-mono">
          <Radio className="w-4 h-4 animate-pulse" />
          <span>LIVE SYNC</span>
        </div>
      </div>
    </header>
  );
}
