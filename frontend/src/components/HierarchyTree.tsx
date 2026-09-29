import React from 'react';
import { AdministrativeHierarchyResult } from '../types';
import { Network, Check, AlertTriangle } from 'lucide-react';

interface HierarchyTreeProps {
  hierarchy: AdministrativeHierarchyResult;
}

export const HierarchyTree: React.FC<HierarchyTreeProps> = ({ hierarchy }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-emerald-400" />
          <h3 className="text-base font-semibold text-white">Administrative Hierarchy</h3>
        </div>
        <span
          className={`text-xs px-2.5 py-0.5 rounded-full font-mono font-medium ${
            hierarchy.is_consistent
              ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
              : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
          }`}
        >
          {hierarchy.is_consistent ? 'HIERARCHY VALID' : 'MISMATCH DETECTED'}
        </span>
      </div>

      {/* Visual Hierarchy Nodes */}
      <div className="space-y-3 font-mono text-sm">
        {hierarchy.hierarchy_chain.map((node, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${
              node.matched
                ? 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                : 'bg-rose-950/20 border-rose-900/50 text-rose-300'
            }`}
          >
            <div className="mt-0.5">
              {node.matched ? (
                <div className="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <Check className="w-3.5 h-3.5" />
                </div>
              ) : (
                <div className="w-5 h-5 rounded-full bg-rose-500/20 flex items-center justify-center text-rose-400">
                  <AlertTriangle className="w-3.5 h-3.5" />
                </div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase text-slate-500 font-bold tracking-wider">
                  {node.level}
                </span>
                {node.level_code && (
                  <span className="text-[10px] px-1.5 py-0.2 bg-slate-800 text-slate-300 rounded font-mono">
                    {node.level_code}
                  </span>
                )}
              </div>
              <div className="font-semibold text-slate-100 text-base mt-0.5">
                {node.canonical_name || node.name}
              </div>
              {node.evidence && (
                <div className="text-xs text-slate-400 mt-1 font-sans">
                  {node.evidence}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {hierarchy.mismatch_details && hierarchy.mismatch_details.length > 0 && (
        <div className="mt-4 p-3 bg-rose-950/30 border border-rose-800/40 rounded-lg text-xs text-rose-300 space-y-1">
          <div className="font-semibold flex items-center gap-1.5 text-rose-400">
            <AlertTriangle className="w-3.5 h-3.5" /> Hierarchy Inconsistencies:
          </div>
          {hierarchy.mismatch_details.map((m, i) => (
            <div key={i}>• {m}</div>
          ))}
        </div>
      )}
    </div>
  );
};
