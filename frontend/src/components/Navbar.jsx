/**
 * Top Alert Navigation Bar
 * Owner: Harshit
 *
 * Displays active cyclone name, category badge, live landfall countdown,
 * threat severity indicator, and system sync status.
 */

import React from 'react';
import { AlertTriangle, Radio, Clock, ShieldAlert, Wind } from 'lucide-react';

export default function Navbar({ cyclone, risk, livePhase, alerts }) {
  const etaHours = risk?.landfall_eta_hours ?? 18;

  // Format ETA directly from risk data (updated every second by App.jsx in demo mode)
  const hrs = Math.max(0, etaHours);
  const minsTotal = Math.max(0, Math.round((etaHours - Math.floor(etaHours)) * 60));
  const pad = (n) => String(n).padStart(2, '0');

  // Category color mapping
  const catColor = cyclone?.category >= 4
    ? 'bg-fuchsia-600/90 shadow-fuchsia-900/50'
    : cyclone?.category >= 3
    ? 'bg-red-600/90 shadow-red-900/50'
    : cyclone?.category >= 2
    ? 'bg-orange-600/90 shadow-orange-900/50'
    : 'bg-amber-600/90 shadow-amber-900/50';

  // Category label
  const catLabel = cyclone?.category >= 4
    ? 'Extremely Severe'
    : cyclone?.category >= 3
    ? 'Very Severe'
    : cyclone?.category >= 2
    ? 'Severe'
    : 'Cyclonic Storm';

  // ETA display — show LANDFALL if eta is 0
  const etaDisplay = etaHours <= 0
    ? livePhase === 'POST_LANDFALL' ? 'CROSSED' : 'NOW'
    : `${pad(hrs)}:${pad(minsTotal)}:00`;

  const etaColor = etaHours <= 0
    ? 'text-red-400 animate-pulse'
    : etaHours <= 6
    ? 'text-red-400'
    : 'text-amber-300';

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
            CAT {cyclone?.category || '—'} {catLabel}
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
          <span className={`font-mono font-bold tracking-wider text-sm ${etaColor}`}>
            {etaDisplay}
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

        {/* Alert Count Badge */}
        {alerts?.length > 0 && (
          <div className="flex items-center space-x-1 bg-red-500/15 border border-red-500/30 px-2 py-1 rounded-lg">
            <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
            <span className="text-[10px] font-bold text-red-400">{alerts.length}</span>
          </div>
        )}

        {/* Live Sync Indicator */}
        <div className="flex items-center space-x-2 text-emerald-400 text-xs font-mono">
          <Radio className="w-4 h-4 animate-pulse" />
          <span>LIVE SYNC</span>
        </div>
      </div>
    </header>
  );
}
