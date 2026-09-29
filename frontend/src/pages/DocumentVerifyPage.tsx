import React, { useState } from 'react';
import { api } from '../services/api';
import { DocumentVerificationResponse, ExtractedAddressCandidate } from '../types';
import { DocumentUploader } from '../components/DocumentUploader';
import { DocumentPreviewCanvas } from '../components/DocumentPreviewCanvas';
import { ExtractedFieldsTable } from '../components/ExtractedFieldsTable';
import { OCRQualityCard } from '../components/OCRQualityCard';
import { MultiAddressCandidateSelector } from '../components/MultiAddressCandidateSelector';
import { ScoreGauge } from '../components/ScoreGauge';
import { StatusBadge } from '../components/StatusBadge';
import { HierarchyTree } from '../components/HierarchyTree';
import { MapView } from '../components/MapView';
import { EvidenceCard } from '../components/EvidenceCard';
import { WarningsList } from '../components/WarningsList';
import { CandidateRankingCard } from '../components/CandidateRankingCard';
import { DataSourcesCard } from '../components/DataSourcesCard';
import { FileText, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const DocumentVerifyPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DocumentVerificationResponse | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('');

  const handleUpload = async (file: File, engine: string, extractOnly: boolean) => {
    setIsLoading(true);
    setError(null);

    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }

    try {
      const data = extractOnly
        ? await api.extractDocumentOnly(file, engine)
        : await api.verifyDocument(file, engine);
      setResult(data);
      if (data.address_candidates && data.address_candidates.length > 0) {
        setSelectedCandidateId(data.address_candidates[0].candidate_id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to process document');
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const currentCandidate: ExtractedAddressCandidate | undefined =
    result?.address_candidates.find((c) => c.candidate_id === selectedCandidateId) ||
    result?.primary_candidate ||
    result?.address_candidates[0];

  const verification = currentCandidate?.verification_result || result?.verification;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 mb-2">
          <FileText className="w-3.5 h-3.5" />
          Phase 7 Feature &bull; Document OCR Verification
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">
          Document-Based Address Intelligence & Verification
        </h1>
        <p className="text-sm text-slate-600 mt-1">
          Upload official proofs of address, electricity bills, rent agreements, or identity documents to extract structured address components with OCR and verify geographic consistency.
        </p>
      </div>

      {/* Upload Component */}
      <DocumentUploader onUpload={handleUpload} isLoading={isLoading} />

      {/* Error Alert */}
      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-800 flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-bold text-sm">Document Processing Error</div>
            <div className="text-xs mt-1">{error}</div>
          </div>
        </div>
      )}

      {/* Results View */}
      {result && (
        <div className="space-y-6">
          {/* Top Diagnostics Card */}
          <OCRQualityCard
            ocr={result.ocr}
            document={result.document}
            timings={result.stage_timings_ms}
          />

          {/* Multi-Address Candidate Selector */}
          {result.address_candidates.length > 1 && (
            <MultiAddressCandidateSelector
              candidates={result.address_candidates}
              selectedCandidateId={selectedCandidateId}
              onSelectCandidate={setSelectedCandidateId}
            />
          )}

          {/* 2-Column Document Preview & Extracted Fields Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6">
              <DocumentPreviewCanvas
                previewUrl={previewUrl}
                ocrResult={result.ocr.ocr_result}
                candidates={result.address_candidates}
                selectedCandidateId={selectedCandidateId}
                onSelectCandidate={setSelectedCandidateId}
              />
            </div>
            <div className="lg:col-span-6">
              <ExtractedFieldsTable candidate={currentCandidate} />
            </div>
          </div>

          {/* Verification Results (if verification was performed) */}
          {verification ? (
            <div className="space-y-6 pt-4 border-t border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight flex items-center gap-2">
                    <CheckCircle2 className="w-6 h-6 text-emerald-600" />
                    Authoritative Geographic Verification Result
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Evaluated against Survey of India, LGD, and India Post Postal Directory
                  </p>
                </div>
                <StatusBadge status={verification.status} size="lg" />
              </div>

              {/* Score Gauge & Summary Card */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div className="lg:col-span-4">
                  <ScoreGauge
                    score={verification.score}
                    status={verification.status}
                    breakdown={verification.score_breakdown}
                    scores={verification.scores}
                    completeness={verification.completeness}
                  />
                </div>
                <div className="lg:col-span-8 bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col justify-between">
                  <div>
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                      Verification Summary
                    </div>
                    <p className="text-base text-slate-800 font-medium leading-relaxed">
                      {verification.summary}
                    </p>
                    {verification.explanation && verification.explanation.length > 0 && (
                      <div className="mt-4 space-y-1.5">
                        {verification.explanation.map((exp, idx) => (
                          <div key={idx} className="text-xs text-slate-600 flex items-start gap-2">
                            <span className="text-indigo-600 font-bold">&bull;</span>
                            <span>{exp}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-mono">
                    <span>ID: {verification.verification_id}</span>
                    <span>Processed at {new Date(verification.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>

              {/* Warnings List */}
              {verification.warnings && verification.warnings.length > 0 && (
                <WarningsList warnings={verification.warnings} />
              )}

              {/* Hierarchy Tree & Map Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div className="lg:col-span-5">
                  <HierarchyTree hierarchy={verification.administrative_hierarchy} />
                </div>
                <div className="lg:col-span-7">
                  <MapView
                    center={verification.geocoding?.coordinates}
                    displayName={verification.geocoding?.display_name}
                    nearbyPlaces={verification.nearby_places}
                    boundaryGeoJson={verification.boundary_verification.boundary_geojson}
                  />
                </div>
              </div>

              {/* Candidate Entity Resolution Card */}
              {verification.candidate_matches && verification.candidate_matches.length > 0 && (
                <CandidateRankingCard candidates={verification.candidate_matches} />
              )}

              {/* Evidence Chain */}
              <EvidenceCard
                evidence={verification.evidence}
                explanation={verification.explanation}
              />

              {/* Data Sources Attribution */}
              {verification.data_sources && verification.data_sources.length > 0 && (
                <DataSourcesCard sources={verification.data_sources} />
              )}
            </div>
          ) : (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-center text-slate-600 text-sm">
              Address extracted without geographic verification. Uncheck "Extract address fields only" to execute full geographic consistency verification.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
