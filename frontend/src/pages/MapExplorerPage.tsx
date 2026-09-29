import React, { useState } from 'react';
import { MapView } from '../components/MapView';
import { Map } from 'lucide-react';

const EXPLORER_POINTS = [
  {
    name: 'Kharadi (Pune, MH)',
    coords: { latitude: 18.5514, longitude: 73.9405 },
    district: 'Pune',
    state: 'Maharashtra',
  },
  {
    name: 'Hinjewadi (Pune, MH)',
    coords: { latitude: 18.5913, longitude: 73.7389 },
    district: 'Pune',
    state: 'Maharashtra',
  },
  {
    name: 'Whitefield (Bengaluru, KA)',
    coords: { latitude: 12.9698, longitude: 77.7499 },
    district: 'Bengaluru Urban',
    state: 'Karnataka',
  },
  {
    name: 'Connaught Place (New Delhi, DL)',
    coords: { latitude: 28.6315, longitude: 77.2167 },
    district: 'New Delhi',
    state: 'Delhi',
  },
  {
    name: 'Bandra West (Mumbai, MH)',
    coords: { latitude: 19.0596, longitude: 72.8295 },
    district: 'Mumbai Suburban',
    state: 'Maharashtra',
  },
  {
    name: 'Rajarhat (Kolkata, WB)',
    coords: { latitude: 22.5867, longitude: 88.4756 },
    district: 'North 24 Parganas',
    state: 'West Bengal',
  },
];

export const MapExplorerPage: React.FC = () => {
  const [selectedPoint, setSelectedPoint] = useState(EXPLORER_POINTS[0]);

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-semibold uppercase mb-1">
            <Map className="w-3.5 h-3.5" />
            GIS Boundary Visualizer
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">Geographic Map Explorer</h2>
          <p className="text-xs text-slate-400 mt-1">
            Inspect Indian administrative boundaries, postal regions, and landmark intelligence.
          </p>
        </div>

        {/* Quick Jump Buttons */}
        <div className="flex flex-wrap gap-1.5 font-mono text-xs">
          {EXPLORER_POINTS.map((pt, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedPoint(pt)}
              className={`px-3 py-1.5 rounded-lg border transition-all ${
                selectedPoint.name === pt.name
                  ? 'bg-emerald-600 text-white border-emerald-500 font-semibold'
                  : 'bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700'
              }`}
            >
              {pt.name}
            </button>
          ))}
        </div>
      </div>

      {/* Main Map */}
      <MapView
        center={selectedPoint.coords}
        displayName={`${selectedPoint.name} — ${selectedPoint.district}, ${selectedPoint.state}`}
      />
    </div>
  );
};
