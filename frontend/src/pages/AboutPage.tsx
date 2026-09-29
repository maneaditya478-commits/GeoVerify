import React from 'react';
import { Compass, ShieldCheck, Lock, Github } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 pb-16 max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-8 shadow-xl backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-lg">
            <Compass className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">About GeoVerify India</h1>
            <p className="text-xs font-mono text-emerald-400">Open-Source Address Intelligence & GIS Consistency Platform</p>
          </div>
        </div>
        <p className="text-slate-300 text-sm leading-relaxed mt-4">
          GeoVerify India is a specialized geospatial verification engine designed to address the unique complexities of Indian addresses, such as colloquial locality names, transliteration variations, dynamic municipal ward structures, and administrative hierarchies.
        </p>
      </div>

      {/* Core Privacy & Operational Principles */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
            <Lock className="w-4 h-4" />
            <span>Privacy by Design</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            GeoVerify India does NOT claim or infer whether a particular individual resides at an address. It verifies solely the geographic existence, administrative consistency, and spatial validity of supplied location components.
          </p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
            <ShieldCheck className="w-4 h-4" />
            <span>No Black-Box Arbitrary Classifications</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            Every verification status and score comes with a complete, transparent breakdown of points and evidence bullets. An address is never labeled as fraudulent simply because a component has a slight typo.
          </p>
        </div>
      </div>

      {/* GitHub Open Source */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-white">Open Source & Community Driven</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Licensed under the MIT License. Contributions and local datasets welcome.
          </p>
        </div>
        <a
          href="https://github.com/maneaditya478-commits/GeoVerify"
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-slate-950 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-lg text-xs font-mono flex items-center gap-2 transition-colors"
        >
          <Github className="w-4 h-4" />
          <span>GitHub Repository</span>
        </a>
      </div>
    </div>
  );
};
