import React from 'react';
import { AlertTriangle, Radio, Clock, ShieldAlert, Waves } from 'lucide-react';

export default function Navbar({ cyclone, risk }) {
  return (
    <header className="h-16 border-b border-gray-800 bg-gray-950/80 backdrop-blur px-6 flex items-center justify-between z-20">
      {/* Brand & Storm Name */}
      <div className="flex items-center space-x-4">
        <div className="p-2 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center space-x-2 text-red-400 animate-pulse">
          <Waves className="w-5 h-5" />
          <span className="font-bold text-sm tracking-wider uppercase">Cyclone Early Warning System</span>
        </div>

        <div className="h-6 w-px bg-gray-800" />

        <div className="flex items-center space-x-3">
          <h1 className="text-lg font-bold text-white tracking-wide">
            {cyclone?.name || 'Active Storm Monitoring'}
          </h1>
          <span className="px-2.5 py-0.5 text-xs font-semibold bg-red-600/90 text-white rounded-full shadow-lg shadow-red-900/50">
            Category {cyclone?.category || 3} Severe Cyclone
          </span>
        </div>
      </div>

      {/* Metrics & Countdown */}
      <div className="flex items-center space-x-6 text-sm">
        <div className="flex items-center space-x-2 bg-gray-900/90 border border-gray-800 px-3 py-1.5 rounded-lg">
          <Clock className="w-4 h-4 text-amber-400" />
          <span className="text-gray-400">Landfall ETA:</span>
          <span className="font-mono font-bold text-amber-300">~{risk?.landfall_eta_hours || 18} Hours</span>
        </div>

        <div className="flex items-center space-x-2 bg-gray-900/90 border border-gray-800 px-3 py-1.5 rounded-lg">
          <ShieldAlert className="w-4 h-4 text-red-400" />
          <span className="text-gray-400">Threat Level:</span>
          <span className="font-bold text-red-400 uppercase tracking-wider">{risk?.threat_level || 'RED ALERT'}</span>
        </div>

        <div className="flex items-center space-x-2 text-emerald-400 text-xs font-mono">
          <Radio className="w-4 h-4 animate-ping" />
          <span>LIVE GEE & AI SYNC</span>
        </div>
      </div>
    </header>
  );
}
