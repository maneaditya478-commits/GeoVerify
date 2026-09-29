import React from 'react';
import { ScoreBreakdown, VerificationStatus } from '../types';
import { Sparkles } from 'lucide-react';

interface ScoreGaugeProps {
  score: number;
  status: VerificationStatus;
  breakdown: ScoreBreakdown;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({ score, breakdown }) => {
  const getScoreColor = (val: number) => {
    if (val >= 85) return 'text-emerald-400 stroke-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (val >= 70) return 'text-teal-400 stroke-teal-400 bg-teal-500/10 border-teal-500/30';
    if (val >= 50) return 'text-amber-400 stroke-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-rose-400 stroke-rose-400 bg-rose-500/10 border-rose-500/30';
  };

  const categories = [
    { label: 'Admin Hierarchy', score: breakdown.hierarchy_score, max: breakdown.hierarchy_max },
    { label: 'Geo Boundary', score: breakdown.boundary_score, max: breakdown.boundary_max },
    { label: 'Locality Match', score: breakdown.locality_score, max: breakdown.locality_max },
    { label: 'PIN Consistency', score: breakdown.pincode_score, max: breakdown.pincode_max },
    { label: 'Geocoding Quality', score: breakdown.geocoding_score, max: breakdown.geocoding_max },
    { label: 'Nearby Context', score: breakdown.nearby_score, max: breakdown.nearby_max },
  ];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-slate-400 text-xs font-mono tracking-wider uppercase mb-1">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            Consistency Index
          </div>
          <h3 className="text-xl font-bold text-white tracking-tight">Geographic Consistency Score</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Transparent multi-signal deterministic score (Not a probability)
          </p>
        </div>

        {/* Large Score Pill */}
        <div className={`flex items-baseline gap-2 px-6 py-3 rounded-2xl border ${getScoreColor(score)}`}>
          <span className="text-4xl font-extrabold font-mono tracking-tight">{score}</span>
          <span className="text-sm font-semibold text-slate-400 font-mono">/ 100</span>
        </div>
      </div>

      {/* Sub-Score Breakdown Bars */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-6">
        {categories.map((cat, idx) => {
          const pct = Math.min(100, Math.round((cat.score / (cat.max || 1)) * 100));
          return (
            <div key={idx} className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <div className="flex justify-between items-center text-xs mb-1.5 font-mono">
                <span className="text-slate-300 font-medium">{cat.label}</span>
                <span className="text-slate-400">
                  <span className="text-emerald-400 font-bold">{cat.score}</span> / {cat.max}
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-1.5 rounded-full transition-all duration-500 ${
                    pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-rose-500'
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
