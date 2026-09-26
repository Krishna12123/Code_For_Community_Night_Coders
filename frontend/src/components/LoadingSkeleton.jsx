/**
 * Loading Skeleton
 * Owner: Harshit
 *
 * Full-screen loading skeleton shown while initial data loads.
 * Matches the dark command-center aesthetic.
 */

import React from 'react';

function Pulse({ className }) {
  return <div className={`animate-pulse bg-gray-800/60 rounded ${className}`} />;
}

export default function LoadingSkeleton() {
  return (
    <div className="flex flex-col h-screen w-screen bg-[#090d16] text-gray-100 overflow-hidden">
      {/* Navbar skeleton */}
      <header className="h-16 border-b border-gray-800 bg-gray-950/80 px-6 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Pulse className="w-48 h-10" />
          <div className="h-6 w-px bg-gray-800" />
          <Pulse className="w-40 h-6" />
          <Pulse className="w-20 h-6 rounded-full" />
        </div>
        <div className="flex items-center space-x-4">
          <Pulse className="w-36 h-8 rounded-lg" />
          <Pulse className="w-28 h-8 rounded-lg" />
          <Pulse className="w-20 h-6" />
        </div>
      </header>

      {/* Mode bar skeleton */}
      <div className="flex items-center px-4 pt-2 pb-0 space-x-3">
        <Pulse className="w-52 h-7 rounded-full" />
        <Pulse className="w-40 h-2 rounded-full" />
      </div>

      {/* Main content skeleton */}
      <main className="flex-1 grid grid-cols-12 gap-4 p-4 pt-2 min-h-0 overflow-hidden">
        {/* Map area */}
        <div className="col-span-8 h-full relative">
          <div className="absolute inset-0 bg-gray-900/50 rounded-xl border border-gray-800 overflow-hidden">
            {/* Fake map loading indicator */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="flex flex-col items-center space-y-4">
                <div className="w-16 h-16 border-4 border-gray-700 border-t-cyan-500 rounded-full animate-spin" />
                <span className="text-sm text-gray-500 font-mono">Initializing GIS Engine...</span>
              </div>
            </div>
            {/* Fake layer toggles */}
            <div className="absolute top-4 left-4 flex space-x-2">
              <Pulse className="w-20 h-8 rounded-lg" />
              <Pulse className="w-20 h-8 rounded-lg" />
              <Pulse className="w-20 h-8 rounded-lg" />
            </div>
          </div>
        </div>

        {/* Right panel */}
        <div className="col-span-4 h-full flex flex-col space-y-4 overflow-hidden">
          {/* Risk panel skeleton */}
          <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 space-y-3">
            <Pulse className="w-32 h-4" />
            <div className="grid grid-cols-2 gap-3">
              <Pulse className="h-20 rounded-lg" />
              <Pulse className="h-20 rounded-lg" />
              <Pulse className="h-20 rounded-lg" />
              <Pulse className="h-20 rounded-lg" />
            </div>
            <Pulse className="w-full h-32 rounded-lg" />
          </div>

          {/* AI briefing skeleton */}
          <div className="bg-gray-900/80 border border-purple-500/20 rounded-xl p-4 space-y-3">
            <div className="flex items-center space-x-2">
              <Pulse className="w-4 h-4 rounded-full" />
              <Pulse className="w-40 h-4" />
            </div>
            <Pulse className="w-full h-3" />
            <Pulse className="w-4/5 h-3" />
            <Pulse className="w-3/5 h-3" />
          </div>

          {/* Actions skeleton */}
          <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 space-y-3 flex-1">
            <Pulse className="w-28 h-4" />
            <Pulse className="w-full h-16 rounded-lg" />
            <Pulse className="w-full h-16 rounded-lg" />
            <Pulse className="w-full h-16 rounded-lg" />
          </div>
        </div>
      </main>
    </div>
  );
}
