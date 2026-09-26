/**
 * Risk & Exposure Analytics Panel
 * Owner: Harshit
 *
 * Displays KPI stat cards, a Recharts district risk bar chart,
 * and detailed per-district threat breakdown cards.
 */

import React from 'react';
import { Users, Droplets, Cross, ShieldAlert, TrendingUp, Building2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const RISK_COLORS = {
  RED: '#ef4444',
  ORANGE: '#f59e0b',
  YELLOW: '#eab308',
  GREEN: '#22c55e'
};

export default function RiskPanel({ risk }) {
  const districts = risk?.high_risk_districts || [];

  // Recharts data
  const chartData = districts.map(d => ({
    name: d.district_name,
    score: d.risk_score,
    level: d.risk_level,
    color: RISK_COLORS[d.risk_level] || '#6b7280'
  }));

  // Aggregated totals
  const totalFlooded = districts.reduce((s, d) => s + d.flooded_area_sq_km, 0) || 315.7;
  const totalHospitals = districts.reduce((s, d) => s + d.vulnerable_hospitals, 0) || 18;
  const totalShelters = districts.reduce((s, d) => s + d.shelters_available, 0) || 135;

  return (
    <div className="flex flex-col space-y-4">

      {/* ── KPI Stat Cards (2x2 grid) ── */}
      <div className="grid grid-cols-2 gap-3">
        <StatCard
          label="Population at Risk"
          value={
            risk?.total_population_at_risk
              ? (risk.total_population_at_risk / 1e6).toFixed(2) + 'M'
              : '1.85M'
          }
          sub="High Vulnerability Zone"
          subColor="text-red-400"
          icon={<Users className="w-4 h-4 text-sky-400" />}
          subIcon={<TrendingUp className="w-3 h-3" />}
          valueColor="text-white"
        />
        <StatCard
          label="SAR Flood Inundation"
          value={`${totalFlooded.toFixed(1)} km\u00B2`}
          sub={`Across ${districts.length || 4} Coastal Districts`}
          icon={<Droplets className="w-4 h-4 text-cyan-400" />}
          valueColor="text-cyan-300"
        />
        <StatCard
          label="Hospitals at Risk"
          value={totalHospitals}
          sub="Within wind / surge zone"
          icon={<Cross className="w-4 h-4 text-red-400" />}
          valueColor="text-red-300"
        />
        <StatCard
          label="Shelters Available"
          value={totalShelters}
          sub="Active Relief Centers"
          subColor="text-emerald-400/70"
          icon={<Building2 className="w-4 h-4 text-emerald-400" />}
          valueColor="text-emerald-300"
        />
      </div>

      {/* ── District Risk Index Chart ── */}
      {chartData.length > 0 && (
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 flex items-center justify-between">
            <span>District Risk Index</span>
            <TrendingUp className="w-4 h-4 text-amber-400" />
          </h3>
          <div className="h-36">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} barCategoryGap="20%">
                <XAxis
                  dataKey="name"
                  tick={{ fill: '#9ca3af', fontSize: 10 }}
                  axisLine={{ stroke: '#374151' }}
                  tickLine={false}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fill: '#6b7280', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  width={30}
                />
                <Tooltip
                  contentStyle={{
                    background: '#111827',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#e2e8f0',
                    fontSize: '12px'
                  }}
                  formatter={(value) => [`${value} / 100`, 'Risk Score']}
                  cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                />
                <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.color} fillOpacity={0.85} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* ── District Threat Breakdown ── */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 flex items-center justify-between">
          <span>District Threat Breakdown</span>
          <ShieldAlert className="w-4 h-4 text-amber-400" />
        </h3>

        <div className="space-y-3">
          {districts.map((district, idx) => (
            <div key={idx} className="bg-gray-950/60 border border-gray-800/80 p-2.5 rounded-lg">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-bold text-white">{district.district_name}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  district.risk_level === 'RED'
                    ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                    : district.risk_level === 'ORANGE'
                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                    : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/40'
                }`}>
                  Risk {district.risk_score}/100 ({district.risk_level})
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden mb-2">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    district.risk_level === 'RED' ? 'bg-red-500'
                    : district.risk_level === 'ORANGE' ? 'bg-amber-500'
                    : 'bg-yellow-400'
                  }`}
                  style={{ width: `${district.risk_score}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-[11px] text-gray-400">
                <span className="flex items-center space-x-1">
                  <Droplets className="w-3 h-3 text-cyan-400" />
                  <span>Flooded: {district.flooded_area_sq_km} km\u00B2</span>
                </span>
                <span className="flex items-center space-x-1">
                  <Cross className="w-3 h-3 text-red-400" />
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


/* ── Reusable Stat Card ── */
function StatCard({ label, value, sub, subColor, icon, subIcon, valueColor }) {
  return (
    <div className="bg-gray-900/80 border border-gray-800 p-3.5 rounded-xl">
      <div className="flex items-center justify-between text-gray-400 mb-1">
        <span className="text-xs font-medium">{label}</span>
        {icon}
      </div>
      <div className={`text-xl font-bold font-mono ${valueColor || 'text-white'}`}>
        {value}
      </div>
      {sub && (
        <div className={`text-[10px] mt-0.5 flex items-center space-x-1 ${subColor || 'text-gray-400'}`}>
          {subIcon}
          <span>{sub}</span>
        </div>
      )}
    </div>
  );
}
