import React, { useState } from 'react';
import { Layers, Eye, EyeOff, Navigation, Wind, CloudRain, Building2, AlertOctagon } from 'lucide-react';

export default function MapDashboard({ cyclone, risk }) {
  const [activeLayers, setActiveLayers] = useState({
    track: true,
    cone: true,
    sarFlood: true,
    gpmRain: false,
    shelters: true
  });

  const toggleLayer = (key) => {
    setActiveLayers(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="relative w-full h-full bg-[#0b1120] rounded-xl overflow-hidden border border-gray-800 shadow-2xl flex flex-col">
      {/* Interactive Map Visual Mock Canvas */}
      <div className="relative flex-1 bg-gradient-to-br from-[#070b14] via-[#0d1627] to-[#081426] overflow-hidden flex items-center justify-center">
        
        {/* Synthetic Radar & Geospatial Grid */}
        <div className="absolute inset-0 opacity-15 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:24px_24px]" />
        
        {/* Coastal Contour Simulation */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-40" xmlns="http://www.w3.org/2000/svg">
          {/* Simulated Coastline */}
          <path
            d="M 280,0 Q 240,200 290,400 T 260,700 T 220,1000"
            fill="none"
            stroke="#38bdf8"
            strokeWidth="3"
            strokeDasharray="8 4"
          />
          {/* Land area fill */}
          <path
            d="M 0,0 L 280,0 Q 240,200 290,400 T 260,700 T 220,1000 L 0,1000 Z"
            fill="#0f172a"
            opacity="0.6"
          />
        </svg>

        {/* Dynamic GIS Layers */}

        {/* 1. SAR Flood Overlay */}
        {activeLayers.sarFlood && (
          <div className="absolute left-[180px] top-[240px] w-56 h-72 bg-cyan-500/20 rounded-full blur-2xl border border-cyan-400/40 pointer-events-none animate-pulse">
            <span className="absolute top-2 left-4 text-[10px] font-mono text-cyan-300 font-bold">
              🛰️ GEE Sentinel-1 SAR Flood Inundation Zone
            </span>
          </div>
        )}

        {/* 2. GPM Rainfall Accumulation */}
        {activeLayers.gpmRain && (
          <div className="absolute left-[140px] top-[200px] w-80 h-96 bg-purple-500/15 rounded-full blur-3xl pointer-events-none" />
        )}

        {/* 3. Cyclone Forecast Cone of Uncertainty */}
        {activeLayers.cone && (
          <svg className="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
            <polygon
              points="580,420 280,310 240,490"
              fill="rgba(239, 68, 68, 0.18)"
              stroke="rgba(239, 68, 68, 0.6)"
              strokeWidth="2"
              strokeDasharray="6 3"
            />
            {/* Projected Eye Track Path */}
            {activeLayers.track && (
              <line
                x1="580"
                y1="420"
                x2="260"
                y2="400"
                stroke="#f59e0b"
                strokeWidth="3"
              />
            )}
          </svg>
        )}

        {/* 4. Cyclone Eye Current Marker */}
        <div className="absolute left-[560px] top-[400px] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center cursor-pointer group">
          <div className="relative">
            <div className="w-12 h-12 rounded-full border-2 border-red-500 bg-red-500/30 flex items-center justify-center animate-spin [animation-duration:4s]">
              <div className="w-3 h-3 bg-red-400 rounded-full" />
            </div>
            <div className="absolute -inset-2 rounded-full border border-red-400/50 animate-ping [animation-duration:2s]" />
          </div>
          <div className="mt-2 bg-gray-900/95 border border-red-500/50 px-3 py-1 rounded shadow-xl text-center">
            <p className="text-xs font-bold text-red-400">{cyclone?.name || 'Eye Position'}</p>
            <p className="text-[10px] text-gray-300 font-mono">165 km/h | 960 hPa</p>
          </div>
        </div>

        {/* 5. Projected Landfall Target Marker */}
        <div className="absolute left-[260px] top-[400px] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
          <div className="p-2 bg-amber-500/20 border border-amber-400 rounded-full animate-bounce">
            <AlertOctagon className="w-5 h-5 text-amber-400" />
          </div>
          <div className="mt-1 bg-gray-900/90 border border-amber-500/40 px-2 py-0.5 rounded text-[10px] text-amber-300 font-bold">
            Projected Landfall (18h)
          </div>
        </div>

        {/* 6. Critical Infrastructure Shelters */}
        {activeLayers.shelters && (
          <>
            <div className="absolute left-[200px] top-[320px] bg-emerald-950/80 border border-emerald-500 px-2 py-1 rounded flex items-center space-x-1 text-[10px] text-emerald-300">
              <Building2 className="w-3 h-3" />
              <span>Nellore Shelter #4 (Cap: 1,200)</span>
            </div>
            <div className="absolute left-[190px] top-[460px] bg-emerald-950/80 border border-emerald-500 px-2 py-1 rounded flex items-center space-x-1 text-[10px] text-emerald-300">
              <Building2 className="w-3 h-3" />
              <span>Prakasam Shelter #12 (Cap: 800)</span>
            </div>
          </>
        )}

        {/* Map Coordinates Overlay */}
        <div className="absolute bottom-4 left-4 bg-gray-950/90 border border-gray-800 px-3 py-1.5 rounded-lg text-xs font-mono text-gray-400 flex items-center space-x-3">
          <Navigation className="w-3.5 h-3.5 text-sky-400" />
          <span>Eye: 14.50° N, 82.10° E</span>
          <span className="text-gray-600">|</span>
          <span>Zoom: 6.5x</span>
        </div>
      </div>

      {/* Layer Control Bar */}
      <div className="h-14 bg-gray-950 border-t border-gray-800 px-4 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2 text-gray-400 font-medium">
          <Layers className="w-4 h-4 text-sky-400" />
          <span>GIS Layers:</span>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => toggleLayer('cone')}
            className={`px-3 py-1.5 rounded-md border flex items-center space-x-1.5 transition ${
              activeLayers.cone
                ? 'bg-red-500/20 border-red-500/50 text-red-300'
                : 'bg-gray-900 border-gray-800 text-gray-500'
            }`}
          >
            <Wind className="w-3.5 h-3.5" />
            <span>Forecast Cone</span>
          </button>

          <button
            onClick={() => toggleLayer('sarFlood')}
            className={`px-3 py-1.5 rounded-md border flex items-center space-x-1.5 transition ${
              activeLayers.sarFlood
                ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300'
                : 'bg-gray-900 border-gray-800 text-gray-500'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>GEE Sentinel-1 SAR</span>
          </button>

          <button
            onClick={() => toggleLayer('gpmRain')}
            className={`px-3 py-1.5 rounded-md border flex items-center space-x-1.5 transition ${
              activeLayers.gpmRain
                ? 'bg-purple-500/20 border-purple-500/50 text-purple-300'
                : 'bg-gray-900 border-gray-800 text-gray-500'
            }`}
          >
            <CloudRain className="w-3.5 h-3.5" />
            <span>GPM Rainfall</span>
          </button>

          <button
            onClick={() => toggleLayer('shelters')}
            className={`px-3 py-1.5 rounded-md border flex items-center space-x-1.5 transition ${
              activeLayers.shelters
                ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                : 'bg-gray-900 border-gray-800 text-gray-500'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Shelters & POIs</span>
          </button>
        </div>
      </div>
    </div>
  );
}
