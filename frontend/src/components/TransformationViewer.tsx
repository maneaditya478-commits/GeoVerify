import React from 'react';
import { NormalizedAddress } from '../types';
import { RefreshCw, CheckCircle2, ArrowRight } from 'lucide-react';

interface TransformationViewerProps {
  normalized: NormalizedAddress;
}

export const TransformationViewer: React.FC<TransformationViewerProps> = ({ normalized }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
        <div className="flex items-center gap-2">
          <RefreshCw className="w-4 h-4 text-emerald-400" />
          <h3 className="text-base font-semibold text-white">Address Normalization Pipeline</h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {normalized.transformations.length} transformation steps applied
        </span>
      </div>

      {/* Comparison Diff Box */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5 font-mono text-xs">
        <div className="p-3.5 bg-slate-950/70 border border-slate-800 rounded-lg">
          <div className="text-slate-500 uppercase font-bold text-[10px] mb-1 tracking-wider">
            Original Input
          </div>
          <div className="text-slate-300 font-sans text-sm break-words">
            "{normalized.original_input}"
          </div>
        </div>

        <div className="p-3.5 bg-emerald-950/20 border border-emerald-800/40 rounded-lg">
          <div className="text-emerald-500 uppercase font-bold text-[10px] mb-1 tracking-wider flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> Normalized Standard
          </div>
          <div className="text-emerald-300 font-sans text-sm break-words">
            "{normalized.normalized_text}"
          </div>
        </div>
      </div>

      {/* Transformation Audit Trail */}
      {normalized.transformations.length > 0 ? (
        <div className="space-y-2">
          <div className="text-xs uppercase font-mono text-slate-400 font-bold tracking-wider">
            Audit Trail
          </div>
          <div className="divide-y divide-slate-800/60 border border-slate-800/60 rounded-lg overflow-hidden bg-slate-950/40">
            {normalized.transformations.map((step, idx) => (
              <div key={idx} className="p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="px-1.5 py-0.5 bg-slate-800 text-slate-400 rounded text-[10px] uppercase">
                    {step.field}
                  </span>
                  <span className="text-slate-300 font-sans">{step.rule_applied}</span>
                </div>
                <div className="flex items-center gap-2 text-[11px] text-slate-400 bg-slate-900 px-2 py-1 rounded border border-slate-800 shrink-0">
                  <span className="line-through text-slate-500 truncate max-w-[120px]">{step.original_value}</span>
                  <ArrowRight className="w-3 h-3 text-emerald-400" />
                  <span className="text-emerald-300 font-semibold truncate max-w-[120px]">{step.transformed_value}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-xs font-mono text-slate-500 text-center py-2">
          Input address is already canonical. No normalization rules were triggered.
        </div>
      )}
    </div>
  );
};
