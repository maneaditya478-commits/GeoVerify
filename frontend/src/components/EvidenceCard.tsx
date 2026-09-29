import React from 'react';
import { EvidenceItem } from '../types';
import { FileCheck2, CheckCircle, AlertCircle, AlertTriangle, MinusCircle } from 'lucide-react';

interface EvidenceCardProps {
  evidence: EvidenceItem[];
  explanation: string[];
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ evidence, explanation }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PASSED':
        return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      case 'WARNING':
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case 'FAILED':
        return <AlertCircle className="w-4 h-4 text-rose-400" />;
      default:
        return <MinusCircle className="w-4 h-4 text-slate-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PASSED':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'WARNING':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'FAILED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
        <div className="flex items-center gap-2">
          <FileCheck2 className="w-4 h-4 text-emerald-400" />
          <h3 className="text-base font-semibold text-white">Verification Signals & Evidence</h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {evidence.filter((e) => e.passed).length} / {evidence.length} signals passed
        </span>
      </div>

      {/* Narrative Explanation Bullets */}
      {explanation && explanation.length > 0 && (
        <div className="mb-6 p-4 bg-slate-950/70 border border-slate-800/80 rounded-lg">
          <div className="text-xs uppercase font-mono text-slate-400 tracking-wider font-semibold mb-2">
            Verification Narrative
          </div>
          <div className="space-y-1.5 font-mono text-xs">
            {explanation.map((item, idx) => (
              <div
                key={idx}
                className={
                  item.startsWith('✓')
                    ? 'text-emerald-400'
                    : item.startsWith('✗')
                    ? 'text-rose-400'
                    : 'text-slate-400'
                }
              >
                {item}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Structured Evidence Items */}
      <div className="space-y-3">
        {evidence.map((item, idx) => (
          <div
            key={idx}
            className="flex items-start justify-between gap-4 p-3 rounded-lg bg-slate-950/50 border border-slate-800/70 hover:border-slate-700 transition-colors"
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5">{getStatusIcon(item.status)}</div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs uppercase font-mono text-slate-500 font-bold tracking-wider">
                    {item.category}
                  </span>
                  <span className="text-sm font-semibold text-slate-200">{item.title}</span>
                </div>
                <p className="text-xs text-slate-400 mt-1">{item.description}</p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <span
                className={`text-[11px] font-mono px-2 py-0.5 rounded border uppercase font-medium ${getStatusBadge(
                  item.status
                )}`}
              >
                {item.status}
              </span>
              <span className="text-xs font-mono text-slate-400">
                +{item.score_contribution}/{item.weight} pts
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
