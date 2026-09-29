import React from 'react';
import { BookOpen, Layers, ShieldAlert, Cpu } from 'lucide-react';

export const DocsPage: React.FC = () => {
  return (
    <div className="space-y-8 pb-16 max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-8 shadow-xl backdrop-blur-sm">
        <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-semibold uppercase mb-2">
          <BookOpen className="w-4 h-4" />
          System Architecture & Reference
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          GeoVerify India Documentation
        </h1>
        <p className="text-slate-300 mt-2 text-sm leading-relaxed">
          GeoVerify India is a multi-signal geographic and administrative consistency verification
          engine designed specifically for Indian addresses.
        </p>
      </div>

      {/* Section 1: Verification Pipeline */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-emerald-400" />
          Multi-Signal Verification Pipeline
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed">
          Instead of a binary "fake or real" classification, GeoVerify independently validates 6
          authoritative geographic and administrative layers:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg">
            <div className="text-emerald-400 font-bold mb-1">1. Normalization & Token Parsing</div>
            <p className="text-slate-400 font-sans">
              Expands abbreviations, cleans punctuation, resolves state/district aliases and maps to canonical standards.
            </p>
          </div>
          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg">
            <div className="text-emerald-400 font-bold mb-1">2. Administrative Hierarchy Engine</div>
            <p className="text-slate-400 font-sans">
              Validates hierarchical containment: Locality ➔ Sub-District / Taluka ➔ District ➔ State ➔ India.
            </p>
          </div>
          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg">
            <div className="text-emerald-400 font-bold mb-1">3. Point-in-Polygon GIS Boundaries</div>
            <p className="text-slate-400 font-sans">
              Performs geometric containment checks with Shapely / PostGIS against authoritative boundary polygons.
            </p>
          </div>
          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg">
            <div className="text-emerald-400 font-bold mb-1">4. PIN Code & Postal Circle Matching</div>
            <p className="text-slate-400 font-sans">
              Checks 6-digit PIN circle, sub-offices, and distance to official postal centroid.
            </p>
          </div>
          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg">
            <div className="text-emerald-400 font-bold mb-1">5. Geocoding Provider Layer</div>
            <p className="text-slate-400 font-sans">
              Provider abstraction (Mock Reference & OpenStreetMap Nominatim) with caching and rate limiting.
            </p>
          </div>
          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg">
            <div className="text-emerald-400 font-bold mb-1">6. Nearby Intelligence POIs</div>
            <p className="text-slate-400 font-sans">
              Finds contextual transit hubs, hospitals, police stations, and commercial landmarks within radius.
            </p>
          </div>
        </div>
      </div>

      {/* Section 2: Scoring Weights */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-emerald-400" />
          Consistency Scoring Weights
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase bg-slate-950/60">
                <th className="py-2.5 pl-3">Signal Category</th>
                <th className="py-2.5">Weight (Max Points)</th>
                <th className="py-2.5">Verification Criteria</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              <tr>
                <td className="py-2.5 pl-3 font-semibold text-emerald-400">Administrative Hierarchy</td>
                <td className="py-2.5 font-bold">25 pts</td>
                <td className="py-2.5 font-sans">Validates parent-child alignment between state and district.</td>
              </tr>
              <tr>
                <td className="py-2.5 pl-3 font-semibold text-emerald-400">Geographic Boundary Match</td>
                <td className="py-2.5 font-bold">25 pts</td>
                <td className="py-2.5 font-sans">Point coordinates fall strictly inside boundary polygons.</td>
              </tr>
              <tr>
                <td className="py-2.5 pl-3 font-semibold text-emerald-400">Locality Match</td>
                <td className="py-2.5 font-bold">20 pts</td>
                <td className="py-2.5 font-sans">Locality exists and maps to expected district / taluka.</td>
              </tr>
              <tr>
                <td className="py-2.5 pl-3 font-semibold text-emerald-400">PIN Code Consistency</td>
                <td className="py-2.5 font-bold">15 pts</td>
                <td className="py-2.5 font-sans">Postal circle prefix, district mapping & centroid proximity.</td>
              </tr>
              <tr>
                <td className="py-2.5 pl-3 font-semibold text-emerald-400">Geocoding Quality</td>
                <td className="py-2.5 font-bold">10 pts</td>
                <td className="py-2.5 font-sans">Confidence and granularity level of resolved coordinates.</td>
              </tr>
              <tr>
                <td className="py-2.5 pl-3 font-semibold text-emerald-400">Nearby Context</td>
                <td className="py-2.5 font-bold">5 pts</td>
                <td className="py-2.5 font-sans">Presence of verified landmarks and civic infrastructure.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Section 3: Result Statuses */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-emerald-400" />
          Verification Result Classifications
        </h2>
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3 bg-emerald-950/20 border border-emerald-800/40 rounded-lg">
            <span className="font-bold text-emerald-400">VERIFIED:</span>
            <span className="text-slate-300 font-sans ml-2">
              Score ≥ 85. Strong administrative, geographic boundary, and postal consistency across all layers.
            </span>
          </div>
          <div className="p-3 bg-teal-950/20 border border-teal-800/40 rounded-lg">
            <span className="font-bold text-teal-400">CONSISTENT:</span>
            <span className="text-slate-300 font-sans ml-2">
              Score ≥ 70. Authoritative evidence agrees, with minor non-critical omissions (e.g. missing landmark).
            </span>
          </div>
          <div className="p-3 bg-amber-950/20 border border-amber-800/40 rounded-lg">
            <span className="font-bold text-amber-400">NEEDS_REVIEW:</span>
            <span className="text-slate-300 font-sans ml-2">
              Discrepancies found (e.g. PIN circle mismatch) or incomplete information requiring manual review.
            </span>
          </div>
          <div className="p-3 bg-rose-950/20 border border-rose-800/40 rounded-lg">
            <span className="font-bold text-rose-400">INCONSISTENT:</span>
            <span className="text-slate-300 font-sans ml-2">
              Explicit administrative or boundary conflict (e.g. Locality asserted in an incorrect district).
            </span>
          </div>
          <div className="p-3 bg-purple-950/20 border border-purple-800/40 rounded-lg">
            <span className="font-bold text-purple-400">AMBIGUOUS:</span>
            <span className="text-slate-300 font-sans ml-2">
              Locality name exists in multiple states/districts without distinguishing context.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
