import React from 'react';
import { ExtractedAddressCandidate } from '../types';
import { MapPin } from 'lucide-react';

interface MultiAddressCandidateSelectorProps {
  candidates: ExtractedAddressCandidate[];
  selectedCandidateId: string;
  onSelectCandidate: (candidateId: string) => void;
}

export const MultiAddressCandidateSelector: React.FC<MultiAddressCandidateSelectorProps> = ({
  candidates,
  selectedCandidateId,
  onSelectCandidate,
}) => {
  if (candidates.length <= 1) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <MapPin className="w-4 h-4 text-indigo-600" />
          Multiple Address Regions Detected ({candidates.length})
        </h3>
        <span className="text-xs text-slate-500">
          Select an address candidate below to inspect verification evidence
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {candidates.map((cand, idx) => {
          const isSelected = cand.candidate_id === selectedCandidateId || (!selectedCandidateId && idx === 0);

          return (
            <div
              key={cand.candidate_id}
              onClick={() => onSelectCandidate(cand.candidate_id)}
              className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                isSelected
                  ? 'border-indigo-600 bg-indigo-50/40 ring-1 ring-indigo-600 shadow-sm'
                  : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/50'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="inline-flex items-center gap-1 text-xs font-bold text-indigo-700 bg-indigo-100/70 px-2 py-0.5 rounded">
                  <MapPin className="w-3 h-3" /> Candidate #{idx + 1}: {cand.address_type}
                </span>
                <span className="text-[11px] font-mono text-slate-500">
                  {Math.round(cand.extraction_confidence * 100)}% Confidence
                </span>
              </div>
              <div className="text-xs text-slate-700 font-medium line-clamp-2 mt-1">
                {cand.assembled_address}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
