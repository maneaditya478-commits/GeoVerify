import React from 'react';
import { AmbiguityDetails, EntityMatchResult } from '../types';
import { AlertTriangle, HelpCircle } from 'lucide-react';

interface AmbiguityCardProps {
  ambiguity: AmbiguityDetails;
  candidates?: EntityMatchResult[];
}

export const AmbiguityCard: React.FC<AmbiguityCardProps> = ({ ambiguity, candidates }) => {
  if (!ambiguity || (!ambiguity.is_ambiguous && (!candidates || candidates.length <= 1))) {
    return null;
  }

  const list = (ambiguity.top_candidates && ambiguity.top_candidates.length > 0)
    ? ambiguity.top_candidates
    : (candidates || []);

  return (
    <div className="bg-amber-50/60 dark:bg-amber-950/20 border-2 border-amber-300 dark:border-amber-700/60 rounded-xl p-6 shadow-sm">
      <div className="flex items-start gap-3.5 mb-4">
        <div className="p-2.5 rounded-lg bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 shrink-0">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-amber-900 dark:text-amber-200">
              Multiple Geographic Matches Detected
            </h3>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-200 dark:bg-amber-900 text-amber-900 dark:text-amber-200 uppercase tracking-wide">
              Ambiguous
            </span>
          </div>
          <p className="text-sm text-amber-800 dark:text-amber-300 mt-1">
            {ambiguity.ambiguity_reason ||
              'This address token exists in multiple distinct administrative jurisdictions. Additional context is required to determine the exact location.'}
          </p>
        </div>
      </div>

      {/* Disambiguation recommendations */}
      {ambiguity.suggested_disambiguations && ambiguity.suggested_disambiguations.length > 0 && (
        <div className="mb-5 p-3.5 rounded-lg bg-white/80 dark:bg-slate-900/80 border border-amber-200 dark:border-amber-800/80">
          <div className="text-xs font-bold text-amber-900 dark:text-amber-200 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <HelpCircle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
            Recommended Fields to Disambiguate:
          </div>
          <div className="flex flex-wrap gap-2">
            {ambiguity.suggested_disambiguations.map((field, idx) => (
              <span
                key={idx}
                className="text-xs font-semibold px-3 py-1 rounded-md bg-amber-100 dark:bg-amber-900/60 text-amber-900 dark:text-amber-200 border border-amber-300/80 dark:border-amber-700"
              >
                + {field}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Candidate entities list */}
      {list.length > 0 && (
        <div>
          <div className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2.5">
            Top Candidate Entities ({list.length}):
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {list.map((item, idx) => {
              const c = item.candidate;
              const isTop = idx === 0;
              return (
                <div
                  key={c.id || idx}
                  className={`p-4 rounded-lg border transition-all ${
                    isTop
                      ? 'bg-white dark:bg-slate-900 border-amber-400 dark:border-amber-600 shadow-sm'
                      : 'bg-white/60 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                        <span>{c.name}</span>
                        {c.name_hi && (
                          <span className="text-xs font-normal text-slate-500 dark:text-slate-400">
                            ({c.name_hi})
                          </span>
                        )}
                      </div>
                      <span className="text-[11px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 uppercase font-medium">
                        {c.entity_type}
                      </span>
                    </div>

                    <div className="text-right">
                      <div className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
                        {Math.round(item.match_score)} / 100
                      </div>
                      <span className="text-[10px] text-slate-400">Match Score</span>
                    </div>
                  </div>

                  <div className="text-xs text-slate-600 dark:text-slate-300 space-y-1 mt-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                    <div className="flex justify-between">
                      <span className="text-slate-400">State:</span>
                      <span className="font-medium text-slate-800 dark:text-slate-200">
                        {c.state || 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">District:</span>
                      <span className="font-medium text-slate-800 dark:text-slate-200">
                        {c.district || 'N/A'}
                      </span>
                    </div>
                    {c.subdistrict && (
                      <div className="flex justify-between">
                        <span className="text-slate-400">Sub-District:</span>
                        <span className="font-medium text-slate-800 dark:text-slate-200">
                          {c.subdistrict}
                        </span>
                      </div>
                    )}
                    {c.pincode && (
                      <div className="flex justify-between">
                        <span className="text-slate-400">PIN:</span>
                        <span className="font-mono font-medium text-slate-800 dark:text-slate-200">
                          {c.pincode}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
