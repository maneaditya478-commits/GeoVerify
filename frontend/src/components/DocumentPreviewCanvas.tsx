import React, { useState } from 'react';
import { ExtractedAddressCandidate, OCRResult } from '../types';
import { Layers, MapPin, ZoomIn, ZoomOut } from 'lucide-react';

interface DocumentPreviewCanvasProps {
  previewUrl?: string | null;
  ocrResult?: OCRResult;
  candidates: ExtractedAddressCandidate[];
  selectedCandidateId?: string;
  onSelectCandidate?: (candidateId: string) => void;
}

export const DocumentPreviewCanvas: React.FC<DocumentPreviewCanvasProps> = ({
  previewUrl,
  ocrResult,
  candidates,
  selectedCandidateId,
  onSelectCandidate,
}) => {
  const [zoom, setZoom] = useState(1.0);
  const [showAllWords, setShowAllWords] = useState(false);

  const primaryPage = ocrResult?.pages?.[0];
  const pageWidth = primaryPage?.width || 800;
  const pageHeight = primaryPage?.height || 600;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 flex flex-col h-full">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-600" />
          <h3 className="text-sm font-bold text-slate-900">Document Canvas & OCR Region Overlay</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowAllWords(!showAllWords)}
            className={`text-xs px-2.5 py-1 rounded border transition-colors ${
              showAllWords ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-medium' : 'border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {showAllWords ? 'Hide Word Boxes' : 'Show Word Boxes'}
          </button>
          <div className="flex items-center border border-slate-200 rounded-lg overflow-hidden">
            <button
              onClick={() => setZoom(Math.max(0.7, zoom - 0.15))}
              className="p-1 hover:bg-slate-100 text-slate-600"
              title="Zoom out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-xs px-2 text-slate-600 font-mono">{Math.round(zoom * 100)}%</span>
            <button
              onClick={() => setZoom(Math.min(2.0, zoom + 0.15))}
              className="p-1 hover:bg-slate-100 text-slate-600"
              title="Zoom in"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 bg-slate-900 rounded-lg overflow-auto relative min-h-[380px] max-h-[500px] flex items-center justify-center p-4 border border-slate-800">
        <div
          className="relative bg-white shadow-2xl transition-transform origin-top"
          style={{
            transform: `scale(${zoom})`,
            width: `${Math.min(650, pageWidth)}px`,
            minHeight: '400px',
          }}
        >
          {previewUrl ? (
            <img src={previewUrl} alt="Uploaded document" className="w-full h-auto block select-none" />
          ) : (
            <div className="p-8 text-slate-800 font-mono text-xs whitespace-pre-wrap leading-relaxed select-text bg-amber-50/20 border-b border-slate-100">
              {ocrResult?.full_text || 'No preview image available.'}
            </div>
          )}

          {/* Render Candidate Address Bounding Boxes */}
          {candidates.map((cand, idx) => {
            const bbox = cand.region_bbox;
            const isSelected = cand.candidate_id === selectedCandidateId || (!selectedCandidateId && idx === 0);

            return (
              <div
                key={cand.candidate_id}
                onClick={() => onSelectCandidate && onSelectCandidate(cand.candidate_id)}
                className={`absolute cursor-pointer border-2 transition-all group ${
                  isSelected
                    ? 'border-indigo-600 bg-indigo-500/15 shadow-lg shadow-indigo-500/20'
                    : 'border-emerald-500 bg-emerald-500/10 hover:bg-emerald-500/20'
                }`}
                style={{
                  left: `${bbox ? (bbox.x / pageWidth) * 100 : 5}%`,
                  top: `${bbox ? (bbox.y / pageHeight) * 100 : 15 + idx * 25}%`,
                  width: `${bbox ? (bbox.width / pageWidth) * 100 : 90}%`,
                  height: `${bbox ? Math.max(30, (bbox.height / pageHeight) * 100) : 20}%`,
                }}
              >
                <div
                  className={`absolute -top-6 left-0 px-2 py-0.5 rounded text-[10px] font-bold tracking-wide uppercase flex items-center gap-1 shadow-sm ${
                    isSelected ? 'bg-indigo-600 text-white' : 'bg-emerald-600 text-white'
                  }`}
                >
                  <MapPin className="w-2.5 h-2.5" />
                  Address Region #{idx + 1} ({cand.address_type})
                </div>

                {/* Hover Tooltip */}
                <div className="hidden group-hover:block absolute bottom-full left-0 mb-1 z-20 w-64 p-2 bg-slate-900 text-white text-[11px] rounded-md shadow-xl pointer-events-none">
                  <div className="font-semibold text-emerald-400 mb-0.5">Detected Address:</div>
                  <div className="line-clamp-2 text-slate-200">{cand.assembled_address}</div>
                  <div className="mt-1 text-[9px] text-slate-400">
                    Confidence: {Math.round(cand.extraction_confidence * 100)}% &bull; Status: {cand.extraction_status}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-indigo-600 inline-block"></span>
            Primary Candidate Region
          </span>
          {candidates.length > 1 && (
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 inline-block"></span>
              Alternative Candidate Regions ({candidates.length - 1})
            </span>
          )}
        </div>
        <div>
          {ocrResult && (
            <span>
              Engine: <strong className="text-slate-700">{ocrResult.engine}</strong> &bull; Lang: <strong className="text-slate-700">{ocrResult.primary_language}</strong>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
