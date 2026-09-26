/**
 * Toast Notification System
 * Owner: Harshit
 *
 * Displays real-time alert toasts that slide in from the top-right,
 * auto-dismiss after 6 seconds, and stack up to 4 at a time.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { AlertTriangle, Info, ShieldAlert, X } from 'lucide-react';

const SEVERITY_STYLES = {
  HIGH: { bg: 'bg-red-950/90 border-red-500/50', icon: ShieldAlert, iconColor: 'text-red-400', label: 'CRITICAL' },
  MEDIUM: { bg: 'bg-amber-950/90 border-amber-500/50', icon: AlertTriangle, iconColor: 'text-amber-400', label: 'WARNING' },
  LOW: { bg: 'bg-blue-950/90 border-blue-500/50', icon: Info, iconColor: 'text-blue-400', label: 'INFO' },
};

export default function ToastContainer({ alerts }) {
  const [visibleToasts, setVisibleToasts] = useState([]);
  const [seenIds, setSeenIds] = useState(new Set());

  // When new alerts arrive, show them as toasts
  useEffect(() => {
    if (!alerts?.length) return;

    const newToasts = [];
    for (const alert of alerts) {
      const id = alert.timestamp || `${Date.now()}-${Math.random()}`;
      if (seenIds.has(id)) continue;
      
      newToasts.push({ ...alert, id, createdAt: Date.now() });
      seenIds.add(id);
    }

    if (newToasts.length > 0) {
      setSeenIds(new Set(seenIds));
      setVisibleToasts(prev => [...newToasts, ...prev].slice(0, 4));
    }
  }, [alerts]);

  // Auto-dismiss after 6 seconds
  useEffect(() => {
    if (!visibleToasts.length) return;
    const timer = setInterval(() => {
      setVisibleToasts(prev => 
        prev.filter(t => Date.now() - t.createdAt < 6000)
      );
    }, 1000);
    return () => clearInterval(timer);
  }, [visibleToasts]);

  const dismiss = useCallback((id) => {
    setVisibleToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  if (!visibleToasts.length) return null;

  return (
    <div className="fixed top-20 right-4 z-50 flex flex-col space-y-2 max-w-sm">
      {visibleToasts.map((toast, i) => {
        const severity = SEVERITY_STYLES[toast.severity] || SEVERITY_STYLES.LOW;
        const Icon = severity.icon;

        return (
          <div
            key={toast.id}
            className={`${severity.bg} border rounded-lg p-3 shadow-2xl backdrop-blur-sm animate-slide-in flex items-start space-x-3`}
            style={{ 
              animationDelay: `${i * 100}ms`,
              opacity: 1 - (i * 0.15)
            }}
          >
            <Icon className={`w-5 h-5 ${severity.iconColor} flex-shrink-0 mt-0.5`} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-0.5">
                <span className={`text-[10px] font-bold uppercase tracking-wider ${severity.iconColor}`}>
                  {severity.label}
                </span>
                <button 
                  onClick={() => dismiss(toast.id)}
                  className="text-gray-500 hover:text-gray-300 transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
              <p className="text-xs text-gray-200 leading-snug">{toast.message}</p>
              {toast.source && (
                <span className="text-[9px] text-gray-500 font-mono mt-1 block">{toast.source}</span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
