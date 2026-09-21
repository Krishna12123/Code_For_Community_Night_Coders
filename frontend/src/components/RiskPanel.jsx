import React from 'react';
import { Users, Droplets, Hospital, ShieldAlert, TrendingUp } from 'lucide-react';

export default function RiskPanel({ risk }) {
  return (
    <div className="flex flex-col space-y-4">
      {/* Top 3 High-level Stat Cards */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-900/80 border border-gray-800 p-3.5 rounded-xl">
          <div className="flex items-center justify-between text-gray-400 mb-1">
            <span className="text-xs font-medium">Population at Risk</span>
            <Users className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-xl font-bold text-white font-mono">
            {risk?.total_population_at_risk ? (risk.total_population_at_risk / 1000000).toFixed(2) + 'M' : '1.85M'}
          </div>
          <div className="text-[10px] text-red-400 mt-0.5 flex items-center space-x-1">
            <TrendingUp className="w-3 h-3" />
            <span>High Vulnerability</span>
          </div>
        </div>

        <div className="bg-gray-900/80 border border-gray-800 p-3.5 rounded-xl">
          <div className="flex items-center justify-between text-gray-400 mb-1">
            <span className="text-xs font-medium">SAR Flood Inundation</span>
            <Droplets className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-xl font-bold text-cyan-300 font-mono">
            315.7 km²
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">
            Across 4 Coastal Districts
          </div>
        </div>
      </div>

      {/* District Vulnerability Ranking */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 flex items-center justify-between">
          <span>District Threat Breakdown</span>
          <ShieldAlert className="w-4 h-4 text-amber-400" />
        </h3>

        <div className="space-y-3">
          {risk?.high_risk_districts?.map((district, idx) => (
            <div key={idx} className="bg-gray-950/60 border border-gray-800/80 p-2.5 rounded-lg">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-bold text-white">{district.district_name}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  district.risk_level === 'RED' ? 'bg-red-500/20 text-red-400 border border-red-500/40' :
                  district.risk_level === 'ORANGE' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' :
                  'bg-yellow-500/20 text-yellow-300 border border-yellow-500/40'
                }`}>
                  Risk {district.risk_score}/100 ({district.risk_level})
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden mb-2">
                <div
                  className={`h-full rounded-full ${
                    district.risk_level === 'RED' ? 'bg-red-500' :
                    district.risk_level === 'ORANGE' ? 'bg-amber-500' : 'bg-yellow-400'
                  }`}
                  style={{ width: `${district.risk_score}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-[11px] text-gray-400">
                <span>🌊 Flooded: {district.flooded_area_sq_km} km²</span>
                <span className="flex items-center space-x-1">
                  <Hospital className="w-3 h-3 text-red-400" />
                  <span>{district.vulnerable_hospitals} Hospitals at Risk</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
