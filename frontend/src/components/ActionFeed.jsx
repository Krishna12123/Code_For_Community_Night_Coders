/**
 * Gemini AI Briefing & Emergency Action SOP Feed
 * Owner: Harshit
 *
 * Displays the Gemini disaster advisory summary with PDF export,
 * and an interactive triage action checklist with status toggles.
 */

import React, { useState, useEffect } from 'react';
import { Sparkles, CheckCircle2, Clock, AlertCircle, Download, AlertTriangle } from 'lucide-react';

export default function ActionFeed({ risk, actions: initialActions, livePhase }) {
  const [actions, setActions] = useState([]);

  // Sync with incoming prop data
  useEffect(() => {
    if (initialActions?.length) setActions(initialActions);
  }, [initialActions]);

  const toggleStatus = (id) => {
    setActions(prev =>
      prev.map(item => {
        if (item.id === id) {
          const next =
            item.status === 'PENDING' ? 'IN_PROGRESS' :
            item.status === 'IN_PROGRESS' ? 'COMPLETED' : 'PENDING';
          return { ...item, status: next };
        }
        return item;
      })
    );
  };

  // Group actions by phase
  const grouped = {
    PRE_LANDFALL: actions.filter(a => a.phase === 'PRE_LANDFALL'),
    LANDFALL: actions.filter(a => a.phase === 'LANDFALL'),
    POST_LANDFALL: actions.filter(a => a.phase === 'POST_LANDFALL'),
  };

  const phaseLabels = {
    PRE_LANDFALL: 'Pre-Landfall',
    LANDFALL: 'During Landfall',
    POST_LANDFALL: 'Post-Landfall Rescue',
  };

  const completedCount = actions.filter(a => a.status === 'COMPLETED').length;
  const progressCount = actions.filter(a => a.status === 'IN_PROGRESS').length;

  return (
    <div className="flex flex-col space-y-4">

      {/* ── Gemini AI Situation Briefing ── */}
      <div className="bg-gradient-to-br from-indigo-950/40 via-purple-950/20 to-gray-900 border border-purple-500/30 rounded-xl p-4 shadow-xl relative overflow-hidden">
        {/* Dynamic Phase Indicator */}
        <div className="absolute top-0 right-0 bg-purple-600/30 text-purple-200 text-[9px] font-bold px-2 py-0.5 rounded-bl-lg border-b border-l border-purple-500/30">
          ACTIVE PHASE: {livePhase?.replace('_', ' ')}
        </div>

        <div className="flex items-center justify-between mb-2 mt-1">
          <div className="flex items-center space-x-2 text-purple-300 font-bold text-xs uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-purple-400 animate-spin [animation-duration:8s]" />
            <span>Gemini AI Disaster Briefing</span>
          </div>
          <button className="text-[10px] bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 px-2 py-1 rounded border border-purple-500/40 flex items-center space-x-1 transition-colors">
            <Download className="w-3 h-3" />
            <span>Export</span>
          </button>
        </div>

        <p className="text-xs text-gray-300 leading-relaxed">
          {risk?.executive_summary ||
            'Severe cyclonic storm intensifying. Immediate emergency shelter activations and coastal perimeter evacuations recommended.'}
        </p>

        {risk?.threat_level && (
          <div className="mt-3 flex items-center space-x-3 text-[10px]">
            <span className="flex items-center space-x-1 bg-red-500/15 text-red-400 px-2 py-0.5 rounded border border-red-500/30 font-bold">
              <AlertTriangle className="w-3 h-3" />
              <span>Threat: {risk.threat_level}</span>
            </span>
            <span className="text-gray-500">
              {completedCount}/{actions.length} completed &middot; {progressCount} active
            </span>
          </div>
        )}
      </div>

      {/* ── Emergency Action SOP Checklist ── */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 flex-1">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">
            Response Actions
          </h3>
          <span className="text-[10px] text-gray-500 font-mono">Click to cycle status</span>
        </div>

        <div className="space-y-4 max-h-[380px] overflow-y-auto pr-1">
          {Object.entries(grouped).map(([phase, items]) => {
            if (!items.length) return null;
            const isActive = phase === livePhase;
            return (
              <div key={phase} className={isActive ? 'opacity-100' : 'opacity-40 grayscale transition-all duration-1000'}>
                {/* Phase Header */}
                <div className="flex items-center space-x-2 mb-2">
                  {isActive && <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />}
                  <span className="text-gray-600 text-[10px]">&rsaquo;</span>
                  <span className={`text-[10px] font-bold uppercase tracking-wider ${isActive ? 'text-red-400' : 'text-gray-500'}`}>
                    {phaseLabels[phase] || phase}
                  </span>
                  <div className="flex-1 h-px bg-gray-800" />
                </div>

                {/* Action Items */}
                <div className="space-y-2">
                  {items.map((act) => (
                    <div
                      key={act.id}
                      onClick={() => toggleStatus(act.id)}
                      className="bg-gray-950/80 border border-gray-800/90 hover:border-gray-700 p-3 rounded-lg cursor-pointer transition-colors flex items-start space-x-3 group"
                    >
                      {/* Status Icon */}
                      <div className="mt-0.5">
                        {act.status === 'COMPLETED' ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        ) : act.status === 'IN_PROGRESS' ? (
                          <Clock className="w-4 h-4 text-amber-400 animate-spin [animation-duration:6s]" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-gray-500 group-hover:text-gray-300 transition-colors" />
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                            act.priority === 'HIGH'
                              ? 'bg-red-500/20 text-red-400'
                              : 'bg-amber-500/20 text-amber-400'
                          }`}>
                            {act.priority}
                          </span>
                          <span className="text-[10px] text-gray-400 font-mono">[{act.sector}]</span>
                          <span className={`text-[10px] ml-auto font-bold ${
                            act.status === 'COMPLETED' ? 'text-emerald-400'
                            : act.status === 'IN_PROGRESS' ? 'text-amber-400'
                            : 'text-gray-500'
                          }`}>
                            {act.status.replace('_', ' ')}
                          </span>
                        </div>
                        <p className="text-xs text-gray-200 leading-snug">{act.instruction}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
