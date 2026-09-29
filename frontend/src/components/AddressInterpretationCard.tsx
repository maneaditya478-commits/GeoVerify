import React from 'react';
import { ParsedAddress, NormalizedAddress } from '../types';
import { Sparkles, MapPin, Building, Hash, Languages, CheckCircle2 } from 'lucide-react';

interface AddressInterpretationCardProps {
  parsed: ParsedAddress;
  normalized: NormalizedAddress;
}

export const AddressInterpretationCard: React.FC<AddressInterpretationCardProps> = ({
  parsed,
  normalized,
}) => {
  const scriptBadgeColors: Record<string, string> = {
    Devanagari: 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-800',
    Latin: 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800',
    Mixed: 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800',
    Unknown: 'bg-slate-100 text-slate-800 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700',
  };

  const script = parsed.detected_script || normalized.detected_script || 'Latin';

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-6">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
            Address Interpretation & Transliteration
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-full border font-medium">
            <Languages className="w-3.5 h-3.5 text-slate-500" />
            <span className={scriptBadgeColors[script] || scriptBadgeColors.Latin}>
              {script} Script
            </span>
          </span>
          <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
            Parse Conf: {Math.round((parsed.parse_confidence || 0) * 100)}%
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        {/* State */}
        <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">
            State
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
            {parsed.state || normalized.state ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>{parsed.state || normalized.state}</span>
                {parsed.state_code && (
                  <span className="text-xs text-slate-400 font-normal">({parsed.state_code})</span>
                )}
              </>
            ) : (
              <span className="text-slate-400 italic text-xs">Not detected</span>
            )}
          </div>
        </div>

        {/* District */}
        <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">
            District / City
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
            {parsed.district || normalized.district ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>{parsed.district || normalized.district}</span>
              </>
            ) : (
              <span className="text-slate-400 italic text-xs">Not detected</span>
            )}
          </div>
        </div>

        {/* Sub-District / Taluka */}
        <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">
            Taluka / Tehsil
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
            {parsed.subdistrict || normalized.subdistrict ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>{parsed.subdistrict || normalized.subdistrict}</span>
              </>
            ) : (
              <span className="text-slate-400 italic text-xs">Not detected</span>
            )}
          </div>
        </div>

        {/* Locality */}
        <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-700/60">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">
            Locality / Area
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
            {parsed.locality || normalized.locality ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>{parsed.locality || normalized.locality}</span>
              </>
            ) : (
              <span className="text-slate-400 italic text-xs">Not detected</span>
            )}
          </div>
        </div>
      </div>

      {/* Premise, Landmarks, PIN */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <div className="flex items-center gap-2 p-2.5 rounded-md bg-slate-50 dark:bg-slate-800/30">
          <Building className="w-4 h-4 text-slate-500 shrink-0" />
          <div>
            <span className="text-slate-500 dark:text-slate-400">Premise / Road: </span>
            <span className="font-medium text-slate-800 dark:text-slate-200">
              {parsed.premise || 'None'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 p-2.5 rounded-md bg-slate-50 dark:bg-slate-800/30">
          <MapPin className="w-4 h-4 text-slate-500 shrink-0" />
          <div>
            <span className="text-slate-500 dark:text-slate-400">Landmarks: </span>
            <span className="font-medium text-slate-800 dark:text-slate-200">
              {parsed.landmarks && parsed.landmarks.length > 0
                ? parsed.landmarks.join(', ')
                : 'None'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 p-2.5 rounded-md bg-slate-50 dark:bg-slate-800/30">
          <Hash className="w-4 h-4 text-slate-500 shrink-0" />
          <div>
            <span className="text-slate-500 dark:text-slate-400">PIN Code: </span>
            <span className="font-semibold text-slate-900 dark:text-white">
              {parsed.pincode || normalized.pincode || 'None'}
            </span>
          </div>
        </div>
      </div>

      {/* Transformations log */}
      {normalized.transformations && normalized.transformations.length > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
          <div className="text-xs font-semibold text-slate-600 dark:text-slate-400 mb-2">
            Applied Normalization & Transliteration Steps ({normalized.transformations.length}):
          </div>
          <div className="space-y-1.5">
            {normalized.transformations.map((t, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between text-xs py-1 px-2.5 rounded bg-slate-50 dark:bg-slate-800/40 text-slate-700 dark:text-slate-300 font-mono"
              >
                <span>
                  <span className="text-slate-400 font-sans">{t.field}:</span> {t.original_value} →{' '}
                  <span className="font-semibold text-indigo-600 dark:text-indigo-400">
                    {t.transformed_value}
                  </span>
                </span>
                <span className="text-[11px] font-sans px-2 py-0.5 rounded bg-slate-200/70 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                  {t.rule_applied}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
