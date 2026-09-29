import React from 'react';
import { VerificationRequest, VerificationResponse } from '../types';
import { AddressInputForm } from '../components/AddressInputForm';
import { StatusBadge } from '../components/StatusBadge';
import { ScoreGauge } from '../components/ScoreGauge';
import { HierarchyTree } from '../components/HierarchyTree';
import { EvidenceCard } from '../components/EvidenceCard';
import { MapView } from '../components/MapView';
import { NearbyPlacesTable } from '../components/NearbyPlacesTable';
import { TransformationViewer } from '../components/TransformationViewer';
import { WarningsList } from '../components/WarningsList';
import { MapPin, Clock, Fingerprint } from 'lucide-react';

interface VerifyPageProps {
  result: VerificationResponse | null;
  onVerify: (req: VerificationRequest) => void;
  isLoading: boolean;
}

export const VerifyPage: React.FC<VerifyPageProps> = ({ result, onVerify, isLoading }) => {
  return (
    <div className="space-y-6 pb-12">
      {/* Hero & Address Input Box */}
      <AddressInputForm onVerify={onVerify} isLoading={isLoading} />

      {/* Verification Result Showcase */}
      {result && (
        <div className="space-y-6 animate-fadeIn">
          {/* Top Status Header Banner */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-3">
                <StatusBadge status={result.status} size="lg" />
                <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
                  <Fingerprint className="w-3.5 h-3.5 text-slate-500" />
                  ID: {result.verification_id}
                </span>
                <span className="text-xs font-mono text-slate-500 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {new Date(result.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-base text-slate-200 font-medium">{result.summary}</p>
            </div>

            {result.geocoding && (
              <div className="flex items-center gap-3 px-4 py-2.5 bg-slate-950/80 border border-slate-800 rounded-lg text-xs font-mono shrink-0">
                <MapPin className="w-4 h-4 text-emerald-400" />
                <div>
                  <div className="text-slate-400 text-[10px] uppercase">Geocoded Location</div>
                  <div className="text-slate-200 font-bold">
                    {result.geocoding.coordinates.latitude.toFixed(4)}° N,{' '}
                    {result.geocoding.coordinates.longitude.toFixed(4)}° E
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Warnings Banner if any */}
          <WarningsList warnings={result.warnings} />

          {/* Geographic Consistency Score Gauge */}
          <ScoreGauge
            score={result.score}
            status={result.status}
            breakdown={result.score_breakdown}
          />

          {/* Main 2-Column GIS Dashboard Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Administrative Hierarchy & Evidence Signals (5 cols) */}
            <div className="lg:col-span-5 space-y-6">
              <HierarchyTree hierarchy={result.administrative_hierarchy} />
              <TransformationViewer normalized={result.normalized_address} />
              <EvidenceCard evidence={result.evidence} explanation={result.explanation} />
            </div>

            {/* Right Column: Interactive Map & Nearby Intelligence (7 cols) */}
            <div className="lg:col-span-7 space-y-6">
              <MapView
                center={result.geocoding?.coordinates}
                displayName={result.normalized_address.normalized_text}
                boundaryGeoJson={result.boundary_verification.boundary_geojson}
                nearbyPlaces={result.nearby_places}
              />
              <NearbyPlacesTable places={result.nearby_places} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
