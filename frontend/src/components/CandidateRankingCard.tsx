import React, { useState } from 'react';
import { EntityMatchResult } from '../types';
import { Award, ChevronDown, ChevronUp, ShieldAlert } from 'lucide-react';

interface CandidateRankingCardProps {
  candidates: EntityMatchResult[];
}

export const CandidateRankingCard: React.FC<CandidateRankingCardProps> = ({ candidates }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  if (!candidates || candidates.length === 0) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-6">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
            Context-Aware Candidate Ranking & Feature Breakdown
          </h3>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300">
          Top {candidates.length} Ranked Candidates
        </span>
      </div>

      <div className="space-y-3">
        {candidates.map((item, idx) => {
          const c = item.candidate;
          const b = item.breakdown;
          const exp = item.ranking_explanation;
          const isExpanded = expandedIndex === idx;
          const rank = exp?.rank || idx + 1;

          return (
            <div
              key={c.id || idx}
              className={`rounded-lg border transition-all ${
                rank === 1
                  ? 'border-indigo-200 dark:border-indigo-800/80 bg-indigo-50/20 dark:bg-indigo-950/10'
                  : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900'
              }`}
            >
              <div
                className="p-4 flex items-center justify-between cursor-pointer"
                onClick={() => setExpandedIndex(isExpanded ? null : idx)}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs ${
                      rank === 1
                        ? 'bg-indigo-600 text-white'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    #{rank}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                      <span>{c.name}</span>
                      {c.name_hi && (
                        <span className="text-xs font-normal text-slate-500 dark:text-slate-400">
                          ({c.name_hi})
                        </span>
                      )}
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 uppercase font-medium">
                        {c.entity_type}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      {[c.district, c.state, c.pincode].filter(Boolean).join(', ')}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
                      {item.match_score.toFixed(1)} / 100
                    </div>
                    <div className="text-[10px] text-slate-400">
                      {item.match_confidence} Confidence
                    </div>
                  </div>
                  <button className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                    {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {isExpanded && (
                <div className="px-4 pb-4 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
                  {exp?.summary && (
                    <div className="mb-3 p-2.5 rounded bg-slate-50 dark:bg-slate-800/60 text-slate-700 dark:text-slate-300 font-medium">
                      💡 {exp.summary}
                    </div>
                  )}

                  <div className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
                    Multi-Factor Score Components:
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 mb-3">
                    <div className="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block text-[10px]">Name Sim (25%)</span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{b.name_similarity.toFixed(1)} pts</span>
                    </div>
                    <div className="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block text-[10px]">Admin Context (25%)</span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{b.admin_context.toFixed(1)} pts</span>
                    </div>
                    <div className="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block text-[10px]">Hierarchy Match (15%)</span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{(b.parent_child_compatibility || 0).toFixed(1)} pts</span>
                    </div>
                    <div className="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block text-[10px]">PIN Compat (10%)</span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{b.pin_compatibility.toFixed(1)} pts</span>
                    </div>
                    <div className="p-2 rounded bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block text-[10px]">Spatial Prox (10%)</span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{b.geographic_proximity.toFixed(1)} pts</span>
                    </div>
                  </div>

                  {/* Penalties and channels */}
                  {exp?.applied_penalties && exp.applied_penalties.length > 0 && (
                    <div className="mt-2 p-2.5 rounded bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50">
                      <div className="text-[11px] font-bold text-red-800 dark:text-red-300 uppercase mb-1 flex items-center gap-1">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        Applied Conflict Penalties ({exp.total_penalty_deduction} pts):
                      </div>
                      <div className="space-y-1">
                        {exp.applied_penalties.map((pen, pIdx) => (
                          <div key={pIdx} className="text-xs text-red-700 dark:text-red-300">
                            • <span className="font-semibold">{pen.name} ({pen.deduction} pts):</span> {pen.reason}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {exp?.retrieval_channels && exp.retrieval_channels.length > 0 && (
                    <div className="mt-2.5 flex items-center gap-1.5 flex-wrap">
                      <span className="text-slate-400 text-[11px]">Discovered via channels:</span>
                      {exp.retrieval_channels.map((ch, cIdx) => (
                        <span
                          key={cIdx}
                          className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-medium"
                        >
                          {ch}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
