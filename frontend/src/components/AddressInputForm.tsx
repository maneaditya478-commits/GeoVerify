import React, { useState } from 'react';
import { VerificationRequest, StructuredAddressRequest } from '../types';
import { Search, Sliders, Loader2, Compass } from 'lucide-react';

interface AddressInputFormProps {
  onVerify: (req: VerificationRequest) => void;
  isLoading: boolean;
}

const PRESETS = [
  {
    label: 'Valid Kharadi (Pune)',
    address: 'Kharadi, Pune, Maharashtra 411014',
    type: 'valid',
  },
  {
    label: 'District Mismatch',
    address: 'Kharadi, Kolhapur, Maharashtra',
    type: 'inconsistent',
  },
  {
    label: 'State Mismatch',
    address: 'Pune, Karnataka',
    type: 'inconsistent',
  },
  {
    label: 'Typo & Abbreviation',
    address: 'Kharadi, Puna, Maharastra 411014',
    type: 'typo',
  },
  {
    label: 'Incomplete Locality',
    address: 'Kharadi',
    type: 'incomplete',
  },
  {
    label: 'Ambiguous Name',
    address: 'Rampur',
    type: 'ambiguous',
  },
  {
    label: 'Whitefield (Bengaluru)',
    address: 'Whitefield, Bengaluru, Karnataka 560066',
    type: 'valid',
  },
  {
    label: 'Connaught Place (Delhi)',
    address: 'Connaught Place, New Delhi, Delhi 110001',
    type: 'valid',
  },
];

export const AddressInputForm: React.FC<AddressInputFormProps> = ({ onVerify, isLoading }) => {
  const [activeTab, setActiveTab] = useState<'freeform' | 'structured'>('freeform');
  const [freeformAddress, setFreeformAddress] = useState<string>('Kharadi, Pune, Maharashtra 411014');
  const [radiusKm, setRadiusKm] = useState<number>(5.0);

  const [structured, setStructured] = useState<StructuredAddressRequest>({
    address_line: 'Flat 402, Ganga Carnation, Near EON IT Park',
    locality: 'Kharadi',
    subdistrict: 'Haveli',
    city: 'Pune',
    district: 'Pune',
    state: 'Maharashtra',
    pincode: '411014',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'freeform') {
      if (!freeformAddress.trim()) return;
      onVerify({
        address: freeformAddress.trim(),
        radius_km: radiusKm,
        include_geojson: true,
      });
    } else {
      onVerify({
        structured,
        radius_km: radiusKm,
        include_geojson: true,
      });
    }
  };

  const handleSelectPreset = (addr: string) => {
    setFreeformAddress(addr);
    setActiveTab('freeform');
    onVerify({
      address: addr,
      radius_km: radiusKm,
      include_geojson: true,
    });
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
      {/* Tab Switcher */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
          <button
            type="button"
            onClick={() => setActiveTab('freeform')}
            className={`text-xs px-3.5 py-1.5 rounded-md font-mono transition-colors ${
              activeTab === 'freeform'
                ? 'bg-emerald-600 text-white font-medium shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Free-Form Address
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('structured')}
            className={`text-xs px-3.5 py-1.5 rounded-md font-mono transition-colors ${
              activeTab === 'structured'
                ? 'bg-emerald-600 text-white font-medium shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Structured Components
          </button>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <Sliders className="w-3.5 h-3.5 text-emerald-400" />
          <span>Radius: {radiusKm} km</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {activeTab === 'freeform' ? (
          <div>
            <label className="block text-xs uppercase font-mono text-slate-400 font-bold mb-1.5 tracking-wider">
              Enter Indian Address to Verify
            </label>
            <div className="relative">
              <input
                type="text"
                value={freeformAddress}
                onChange={(e) => setFreeformAddress(e.target.value)}
                placeholder="e.g. Kharadi, Pune, Maharashtra 411014"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-3 text-slate-100 placeholder-slate-600 font-mono text-sm focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
              />
              <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 font-mono text-xs">
            <div className="sm:col-span-2 lg:col-span-3">
              <label className="block text-slate-400 mb-1">Premise / Address Line</label>
              <input
                type="text"
                value={structured.address_line || ''}
                onChange={(e) => setStructured({ ...structured, address_line: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Locality / Village</label>
              <input
                type="text"
                value={structured.locality || ''}
                onChange={(e) => setStructured({ ...structured, locality: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Sub-district / Taluka</label>
              <input
                type="text"
                value={structured.subdistrict || ''}
                onChange={(e) => setStructured({ ...structured, subdistrict: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">City / District</label>
              <input
                type="text"
                value={structured.district || ''}
                onChange={(e) =>
                  setStructured({ ...structured, district: e.target.value, city: e.target.value })
                }
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">State / UT</label>
              <input
                type="text"
                value={structured.state || ''}
                onChange={(e) => setStructured({ ...structured, state: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">PIN Code (6 digits)</label>
              <input
                type="text"
                value={structured.pincode || ''}
                onChange={(e) => setStructured({ ...structured, pincode: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1">Nearby Radius (km)</label>
              <input
                type="number"
                min="0.5"
                max="50"
                step="0.5"
                value={radiusKm}
                onChange={(e) => setRadiusKm(parseFloat(e.target.value) || 5.0)}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-100"
              />
            </div>
          </div>
        )}

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          {/* Preset Buttons */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-mono text-slate-500 uppercase font-semibold mr-1">
              Test Fixtures:
            </span>
            {PRESETS.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectPreset(preset.address)}
                className="text-[11px] font-mono px-2 py-1 rounded bg-slate-950 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-emerald-400 transition-colors"
              >
                {preset.label}
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full sm:w-auto px-6 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-950 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-mono"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Verifying...</span>
              </>
            ) : (
              <>
                <Compass className="w-4 h-4" />
                <span>Verify Consistency</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
