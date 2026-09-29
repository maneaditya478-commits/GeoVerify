import React from 'react';
import { EvidenceGraphResponse } from '../types';
import {
  GitCommit,
  AlertTriangle,
  XCircle,
  CheckCircle2,
  Layers,
  Info,
} from 'lucide-react';

interface EvidenceGraphViewProps {
  graph?: EvidenceGraphResponse;
}

export const EvidenceGraphView: React.FC<EvidenceGraphViewProps> = ({ graph }) => {

  if (!graph || !graph.nodes || graph.nodes.length === 0) {
    return null;
  }

  const severityBadge = (severity: 'INFO' | 'WARNING' | 'CONFLICT') => {
    switch (severity) {
      case 'CONFLICT':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800 flex items-center gap-1">
            <XCircle className="w-3 h-3" /> CONFLICT
          </span>
        );
      case 'WARNING':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" /> WARNING
          </span>
        );
      case 'INFO':
      default:
        return (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> INFO
          </span>
        );
    }
  };

  const nodeStatusIcon = (status: string) => {
    switch (status) {
      case 'VERIFIED':
        return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
      case 'WARNING':
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      case 'CONFLICT':
        return <XCircle className="w-4 h-4 text-rose-500" />;
      default:
        return <Info className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-6">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <GitCommit className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
            Directed Evidence Graph & Semantic Relationships
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {graph.conflicts_count > 0 && (
            <span className="text-xs px-2.5 py-1 rounded-full font-bold bg-rose-100 text-rose-800 border border-rose-200 dark:bg-rose-950/60 dark:text-rose-300">
              {graph.conflicts_count} Conflict{graph.conflicts_count > 1 ? 's' : ''}
            </span>
          )}
          {graph.warnings_count > 0 && (
            <span className="text-xs px-2.5 py-1 rounded-full font-bold bg-amber-100 text-amber-800 border border-amber-200 dark:bg-amber-950/60 dark:text-amber-300">
              {graph.warnings_count} Warning{graph.warnings_count > 1 ? 's' : ''}
            </span>
          )}
          <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
            {graph.nodes.length} Nodes · {graph.relationships.length} Relationships
          </span>
        </div>
      </div>

      <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
        {graph.summary}
      </p>

      {/* Graph Visual Representation */}
      <div className="space-y-3">
        {/* Node cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {graph.nodes.map((node) => (
            <div
              key={node.id}
              className={`p-3.5 rounded-lg border flex flex-col justify-between transition-colors ${
                node.status === 'CONFLICT'
                  ? 'bg-rose-50/50 dark:bg-rose-950/20 border-rose-300 dark:border-rose-800'
                  : node.status === 'WARNING'
                  ? 'bg-amber-50/50 dark:bg-amber-950/20 border-amber-300 dark:border-amber-800'
                  : 'bg-slate-50 dark:bg-slate-800/40 border-slate-200/80 dark:border-slate-700/80'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-0.5">
                    {node.level}
                  </span>
                  <div className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                    {nodeStatusIcon(node.status)}
                    <span>{node.label}</span>
                  </div>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-200/70 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-mono">
                  {node.node_type}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Relationships Table / Flow */}
        <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800">
          <div className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-slate-400" />
            Evaluated Semantic Edges & Cross-Level Inferences:
          </div>

          <div className="space-y-2">
            {graph.relationships.map((rel) => {
              const srcNode = graph.nodes.find((n) => n.id === rel.source);
              const tgtNode = graph.nodes.find((n) => n.id === rel.target);
              const isConflict = rel.severity === 'CONFLICT';
              const isWarning = rel.severity === 'WARNING';

              return (
                <div
                  key={rel.id}
                  className={`p-3 rounded-lg border text-xs flex flex-col md:flex-row md:items-center justify-between gap-2 transition-all ${
                    isConflict
                      ? 'bg-rose-50/60 dark:bg-rose-950/30 border-rose-300 dark:border-rose-800 text-rose-900 dark:text-rose-200'
                      : isWarning
                      ? 'bg-amber-50/60 dark:bg-amber-950/30 border-amber-300 dark:border-amber-800 text-amber-900 dark:text-amber-200'
                      : 'bg-slate-50/70 dark:bg-slate-800/30 border-slate-200/70 dark:border-slate-700/70 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-slate-900 dark:text-white">
                      {srcNode ? srcNode.label : rel.source}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-200/80 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-mono text-[11px]">
                      ──[{rel.label}]──►
                    </span>
                    <span className="font-semibold text-slate-900 dark:text-white">
                      {tgtNode ? tgtNode.label : rel.target}
                    </span>
                    {rel.evidence_text && (
                      <span className="text-slate-500 dark:text-slate-400 italic text-[11px] block md:inline">
                        — {rel.evidence_text}
                      </span>
                    )}
                  </div>

                  <div className="shrink-0 flex items-center gap-2">
                    {severityBadge(rel.severity)}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
