import React from 'react';
import { DataSourceAttribution } from '../types';
import { Database, ExternalLink, ShieldCheck } from 'lucide-react';

interface DataSourcesCardProps {
  sources?: DataSourceAttribution[];
}

export const DataSourcesCard: React.FC<DataSourcesCardProps> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-emerald-400" />
          <h3 className="text-base font-semibold text-white">Authoritative Data Provenance</h3>
        </div>
        <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5" />
          GODL-India & ODbL
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {sources.map((src, idx) => (
          <div
            key={idx}
            className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-lg flex flex-col justify-between hover:border-slate-700 transition-colors"
          >
            <div>
              <div className="flex items-start justify-between gap-2">
                <span className="text-sm font-semibold text-slate-200">{src.name}</span>
                <a
                  href={src.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-400 hover:text-emerald-400 transition-colors shrink-0"
                  title="Official portal"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
              <p className="text-xs text-slate-400 mt-1">{src.coverage}</p>
            </div>
            <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/60 text-[11px] font-mono text-slate-500">
              <span>License: <strong className="text-slate-400">{src.license}</strong></span>
              <span>v{src.version}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
