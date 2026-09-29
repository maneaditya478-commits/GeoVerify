import React from 'react';
import { ScoreBreakdown, VerificationStatus, AddressScores, CompletenessResult } from '../types';
import { ShieldCheck, FileText, Target } from 'lucide-react';

interface ScoreGaugeProps {
  score: number;
  status: VerificationStatus;
  breakdown: ScoreBreakdown;
  scores?: AddressScores;
  completeness?: CompletenessResult;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  breakdown,
  scores,
  completeness,
}) => {
  const getScoreColor = (val: number) => {
    if (val >= 85) return 'text-emerald-400 stroke-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (val >= 70) return 'text-teal-400 stroke-teal-400 bg-teal-500/10 border-teal-500/30';
    if (val >= 50) return 'text-amber-400 stroke-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-rose-400 stroke-rose-400 bg-rose-500/10 border-rose-500/30';
  };

  const completenessRatingColor = (rating?: string) => {
    switch (rating) {
      case 'COMPLETE':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'ADEQUATE':
        return 'bg-teal-500/20 text-teal-300 border-teal-500/40';
      case 'PARTIAL':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      default:
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
    }
  };

  const categories = [
    { label: 'Admin Hierarchy', score: breakdown.hierarchy_score, max: breakdown.hierarchy_max },
    { label: 'Geo Boundary', score: breakdown.boundary_score, max: breakdown.boundary_max },
    { label: 'Locality Match', score: breakdown.locality_score, max: breakdown.locality_max },
    { label: 'PIN Consistency', score: breakdown.pincode_score, max: breakdown.pincode_max },
    { label: 'Geocoding Quality', score: breakdown.geocoding_score, max: breakdown.geocoding_max },
    { label: 'Nearby Context', score: breakdown.nearby_score, max: breakdown.nearby_max },
  ];

  const consistencyScore = scores?.geographic_consistency ?? score;
  const completenessScore = scores?.address_completeness ?? completeness?.score ?? 0;
  const entityMatchScore = scores?.entity_match ?? 0;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
      {/* Multi-Scores Header Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pb-6 border-b border-slate-800">
        {/* 1. Geographic Consistency Score */}
        <div className={`p-4 rounded-xl border flex flex-col justify-between ${getScoreColor(consistencyScore)}`}>
          <div>
            <div className="flex items-center gap-1.5 text-xs font-mono uppercase tracking-wider mb-1 text-slate-300">
              <ShieldCheck className="w-3.5 h-3.5" />
              Geographic Consistency
            </div>
            <p className="text-[11px] text-slate-400">
              Cross-signal administrative & geometric alignment
            </p>
          </div>
          <div className="flex items-baseline gap-1.5 mt-3">
            <span className="text-3xl font-extrabold font-mono">{consistencyScore}</span>
            <span className="text-xs font-semibold text-slate-400 font-mono">/ 100</span>
          </div>
        </div>

        {/* 2. Address Completeness Score */}
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs font-mono uppercase tracking-wider mb-1 text-slate-300">
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                Address Completeness
              </div>
              {completeness && (
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${completenessRatingColor(completeness.rating)}`}>
                  {completeness.rating}
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400">
              Presence of premise, locality, district, state & PIN
            </p>
          </div>
          <div className="flex items-baseline gap-1.5 mt-3">
            <span className="text-3xl font-extrabold font-mono text-white">{completenessScore}</span>
            <span className="text-xs font-semibold text-slate-400 font-mono">/ 100</span>
          </div>
        </div>

        {/* 3. Entity Match Score */}
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-mono uppercase tracking-wider mb-1 text-slate-300">
              <Target className="w-3.5 h-3.5 text-purple-400" />
              Entity Match Confidence
            </div>
            <p className="text-[11px] text-slate-400">
              Gazetteer & multi-factor candidate resolution
            </p>
          </div>
          <div className="flex items-baseline gap-1.5 mt-3">
            <span className="text-3xl font-extrabold font-mono text-white">{entityMatchScore}</span>
            <span className="text-xs font-semibold text-slate-400 font-mono">/ 100</span>
          </div>
        </div>
      </div>

      {/* Sub-Score Breakdown Bars */}
      <div className="pt-6">
        <div className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-3">
          Consistency Score Component Breakdown (6 Deterministic Signals):
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
    </div>
  );
};
