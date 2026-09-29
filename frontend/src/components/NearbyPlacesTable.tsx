import React, { useState } from 'react';
import { NearbyPlace } from '../types';
import { MapPin, Navigation, Building2, Hospital, Shield, Mail, Plane } from 'lucide-react';

interface NearbyPlacesTableProps {
  places: NearbyPlace[];
}

export const NearbyPlacesTable: React.FC<NearbyPlacesTableProps> = ({ places }) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const categories = ['all', 'commercial', 'transit', 'hospital', 'police', 'post_office'];

  const filtered = selectedCategory === 'all'
    ? places
    : places.filter((p) => p.category.toLowerCase() === selectedCategory);

  const getCategoryIcon = (cat: string) => {
    switch (cat.toLowerCase()) {
      case 'hospital':
        return <Hospital className="w-3.5 h-3.5 text-rose-400" />;
      case 'transit':
        return <Plane className="w-3.5 h-3.5 text-blue-400" />;
      case 'police':
        return <Shield className="w-3.5 h-3.5 text-amber-400" />;
      case 'commercial':
        return <Building2 className="w-3.5 h-3.5 text-purple-400" />;
      case 'post_office':
        return <Mail className="w-3.5 h-3.5 text-pink-400" />;
      default:
        return <MapPin className="w-3.5 h-3.5 text-emerald-400" />;
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800 mb-5">
        <div className="flex items-center gap-2">
          <Navigation className="w-4 h-4 text-emerald-400" />
          <h3 className="text-base font-semibold text-white">Nearby Geographic Intelligence</h3>
          <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">
            {places.length} found
          </span>
        </div>

        {/* Category Filter Chips */}
        <div className="flex flex-wrap gap-1.5">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setSelectedCategory(c)}
              className={`text-xs px-2.5 py-1 rounded-md font-mono transition-colors uppercase ${
                selectedCategory === c
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-slate-800/80 text-slate-400 hover:text-slate-200 border border-transparent'
              }`}
            >
              {c.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-8 text-slate-500 font-mono text-xs">
          No nearby entities found matching category '{selectedCategory}'.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
                <th className="pb-3 pl-2">Entity Name</th>
                <th className="pb-3">Category</th>
                <th className="pb-3">Subtype / Address</th>
                <th className="pb-3 text-right pr-2">Distance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filtered.map((place, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2.5 pl-2 font-medium text-slate-200 flex items-center gap-2">
                    {getCategoryIcon(place.category)}
                    <span>{place.name}</span>
                  </td>
                  <td className="py-2.5">
                    <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[10px] uppercase">
                      {place.category}
                    </span>
                  </td>
                  <td className="py-2.5 text-slate-400">
                    {place.subtype || place.address || '—'}
                  </td>
                  <td className="py-2.5 pr-2 text-right">
                    <span className="font-semibold text-emerald-400 font-mono">
                      {place.distance_km} km
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
