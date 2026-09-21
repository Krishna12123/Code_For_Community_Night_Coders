import React, { useState } from 'react';
import { Sparkles, CheckCircle2, Clock, AlertCircle, Send, Download } from 'lucide-react';

export default function ActionFeed({ risk, actions: initialActions }) {
  const [actions, setActions] = useState(initialActions || []);

  const toggleStatus = (id) => {
    setActions(prev =>
      prev.map(item => {
        if (item.id === id) {
          const next = item.status === 'PENDING' ? 'IN_PROGRESS' :
                       item.status === 'IN_PROGRESS' ? 'COMPLETED' : 'PENDING';
          return { ...item, status: next };
        }
        return item;
      })
    );
  };

  return (
    <div className="flex flex-col space-y-4">
      {/* Gemini AI Situation Summary */}
      <div className="bg-gradient-to-br from-indigo-950/40 via-purple-950/20 to-gray-900 border border-purple-500/30 rounded-xl p-4 shadow-xl">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2 text-purple-300 font-bold text-xs uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-purple-400 animate-spin [animation-duration:8s]" />
            <span>Gemini 3.7 Flash Disaster Briefing</span>
          </div>
          <button className="text-[10px] bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 px-2 py-1 rounded border border-purple-500/40 flex items-center space-x-1 transition">
            <Download className="w-3 h-3" />
            <span>Export PDF Report</span>
          </button>
        </div>

        <p className="text-xs text-gray-300 leading-relaxed">
          {risk?.executive_summary ||
            "Severe cyclonic storm intensifying with estimated central pressure of 960 hPa. Immediate emergency shelter activations and coastal perimeter evacuations recommended."}
        </p>
      </div>

      {/* Emergency Action SOP Checklist */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 flex-1">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">
            Emergency Response SOP Actions ({actions.length})
          </h3>
          <span className="text-[10px] text-gray-500 font-mono">Click to update status</span>
        </div>

        <div className="space-y-2.5 max-h-[360px] overflow-y-auto pr-1">
          {actions.map((act) => (
            <div
              key={act.id}
              onClick={() => toggleStatus(act.id)}
              className="bg-gray-950/80 border border-gray-800/90 hover:border-gray-700 p-3 rounded-lg cursor-pointer transition flex items-start space-x-3 group"
            >
              <div className="mt-0.5">
                {act.status === 'COMPLETED' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : act.status === 'IN_PROGRESS' ? (
                  <Clock className="w-4 h-4 text-amber-400 animate-spin [animation-duration:6s]" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-gray-500 group-hover:text-gray-300" />
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    act.priority === 'HIGH' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
                  }`}>
                    {act.priority}
                  </span>
                  <span className="text-[10px] text-gray-400 font-mono">[{act.sector}]</span>
                  <span className={`text-[10px] ml-auto font-bold ${
                    act.status === 'COMPLETED' ? 'text-emerald-400' :
                    act.status === 'IN_PROGRESS' ? 'text-amber-400' : 'text-gray-500'
                  }`}>
                    {act.status}
                  </span>
                </div>
                <p className="text-xs text-gray-200 leading-snug">{act.instruction}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
