import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface WarningsListProps {
  warnings: string[];
}

export const WarningsList: React.FC<WarningsListProps> = ({ warnings }) => {
  if (!warnings || warnings.length === 0) return null;

  return (
    <div className="bg-amber-950/20 border border-amber-800/40 rounded-xl p-5 shadow-xl backdrop-blur-sm">
      <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm mb-3">
        <AlertTriangle className="w-4 h-4" />
        <span>Potential Geographic Inconsistencies & Flags ({warnings.length})</span>
      </div>
      <div className="space-y-2 text-xs font-mono text-amber-200/90">
        {warnings.map((w, idx) => (
          <div key={idx} className="flex items-start gap-2 bg-amber-950/40 p-2.5 rounded border border-amber-900/40">
            <span className="text-amber-400 font-bold">•</span>
            <span>{w}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
