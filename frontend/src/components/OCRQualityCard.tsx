import React from 'react';
import { OCRMetadata, DocumentMetadata } from '../types';
import { ShieldCheck, Cpu, Clock, CheckCircle2, AlertTriangle, XCircle, Languages } from 'lucide-react';

interface OCRQualityCardProps {
  ocr: OCRMetadata;
  document: DocumentMetadata;
  timings?: Record<string, number>;
}

export const OCRQualityCard: React.FC<OCRQualityCardProps> = ({ ocr, document: docMeta, timings }) => {
  const getQualityBadge = (status: string) => {
    switch (status) {
      case 'HIGH':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
            <CheckCircle2 className="w-3.5 h-3.5" /> High Quality
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
            <AlertTriangle className="w-3.5 h-3.5" /> Medium Quality
          </span>
        );
      case 'LOW':
      case 'FAILED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800">
            <XCircle className="w-3.5 h-3.5" /> Low Quality
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-indigo-600" />
            OCR Engine & Document Diagnostics
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            File: {docMeta.filename} &bull; {(docMeta.size_bytes / 1024).toFixed(1)} KB &bull; SHA256: {docMeta.sha256.slice(0, 10)}...
          </p>
        </div>
        {getQualityBadge(ocr.quality_status)}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <div className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
            <Cpu className="w-3 h-3 text-slate-400" /> Engine
          </div>
          <div className="text-sm font-bold text-slate-800 mt-1 capitalize">{ocr.engine}</div>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <div className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
            <Languages className="w-3 h-3 text-slate-400" /> Primary Script
          </div>
          <div className="text-sm font-bold text-slate-800 mt-1 uppercase">{ocr.primary_language}</div>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <div className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-slate-400" /> OCR Confidence
          </div>
          <div className="text-sm font-bold text-emerald-600 mt-1">
            {Math.round(ocr.mean_confidence * 100)}%
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <div className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
            <Clock className="w-3 h-3 text-slate-400" /> Total Pipeline Latency
          </div>
          <div className="text-sm font-bold text-slate-800 mt-1">
            {timings?.total_pipeline_ms ? `${timings.total_pipeline_ms} ms` : `${ocr.processing_time_ms} ms`}
          </div>
        </div>
      </div>

      {/* Latency Stage Breakdown */}
      {timings && Object.keys(timings).length > 0 && (
        <div>
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Execution Stage Latencies
          </div>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-2 text-center text-xs">
            {Object.entries(timings)
              .filter(([k]) => k !== 'total_pipeline_ms')
              .map(([stage, val]) => (
                <div key={stage} className="bg-slate-50/70 p-2 rounded border border-slate-100">
                  <div className="text-[10px] text-slate-500 truncate" title={stage.replace('_ms', '')}>
                    {stage.replace('_ms', '').replace('_', ' ')}
                  </div>
                  <div className="font-mono font-semibold text-slate-800 mt-0.5">{val} ms</div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};
