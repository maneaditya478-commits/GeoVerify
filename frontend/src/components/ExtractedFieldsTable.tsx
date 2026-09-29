import React from 'react';
import { ExtractedAddressCandidate, ExtractedAddressField } from '../types';
import { Sparkles, MapPin, Hash, Building, Compass } from 'lucide-react';

interface ExtractedFieldsTableProps {
  candidate?: ExtractedAddressCandidate | null;
}

const FIELD_ICONS: Record<string, React.ReactNode> = {
  premise: <Building className="w-3.5 h-3.5 text-blue-500" />,
  street: <Compass className="w-3.5 h-3.5 text-teal-500" />,
  locality: <MapPin className="w-3.5 h-3.5 text-indigo-500" />,
  subdistrict: <MapPin className="w-3.5 h-3.5 text-violet-500" />,
  district: <MapPin className="w-3.5 h-3.5 text-purple-500" />,
  state: <MapPin className="w-3.5 h-3.5 text-rose-500" />,
  pincode: <Hash className="w-3.5 h-3.5 text-amber-500" />,
};

export const ExtractedFieldsTable: React.FC<ExtractedFieldsTableProps> = ({ candidate }) => {
  if (!candidate) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center text-slate-400">
        No candidate address selected or extracted.
      </div>
    );
  }

  const fields = Object.entries(candidate.fields || {});

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-600" />
            Extracted Structured Components
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            OCR tokens parsed into Indian administrative hierarchy components with provenance
          </p>
        </div>
        {candidate.pin_recovered && (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <Sparkles className="w-3 h-3 text-amber-500" />
            PIN-First Recovered
          </span>
        )}
      </div>

      <div className="mb-4 bg-slate-50 rounded-lg p-3 border border-slate-100">
        <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">
          Assembled Standard Address String:
        </div>
        <div className="text-sm font-medium text-slate-800 mt-1">
          {candidate.assembled_address}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/70 text-slate-600">
              <th className="py-2.5 px-3 font-semibold">Field</th>
              <th className="py-2.5 px-3 font-semibold">Raw OCR Value</th>
              <th className="py-2.5 px-3 font-semibold">Normalized Canonical</th>
              <th className="py-2.5 px-3 font-semibold">Confidence</th>
              <th className="py-2.5 px-3 font-semibold">Notes / Recovery</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {fields.map(([fieldName, field]: [string, ExtractedAddressField]) => {
              const confPct = Math.round(field.confidence * 100);
              return (
                <tr key={fieldName} className="hover:bg-slate-50/50 transition-colors">
                  <td className="py-2.5 px-3 font-medium text-slate-900 capitalize flex items-center gap-1.5">
                    {FIELD_ICONS[fieldName] || <MapPin className="w-3.5 h-3.5 text-slate-400" />}
                    {fieldName}
                  </td>
                  <td className="py-2.5 px-3 text-slate-600 font-mono text-[11px]">
                    {field.raw_value || '—'}
                  </td>
                  <td className="py-2.5 px-3 font-semibold text-indigo-700">
                    {field.normalized_value || field.raw_value || '—'}
                  </td>
                  <td className="py-2.5 px-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-200 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            confPct >= 85 ? 'bg-emerald-500' : confPct >= 65 ? 'bg-amber-500' : 'bg-rose-500'
                          }`}
                          style={{ width: `${confPct}%` }}
                        />
                      </div>
                      <span className="font-mono text-[10px] text-slate-500">{confPct}%</span>
                    </div>
                  </td>
                  <td className="py-2.5 px-3 text-slate-500 text-[11px]">
                    <div className="flex flex-col gap-1">
                      {field.extraction_method && field.extraction_method !== 'EXPLICIT' && (
                        <span
                          className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold w-fit border ${
                            field.extraction_method === 'PIN_RECOVERY'
                              ? 'bg-amber-50 text-amber-700 border-amber-200'
                              : field.extraction_method === 'OCR_REPAIRED'
                              ? 'bg-blue-50 text-blue-700 border-blue-200'
                              : 'bg-purple-50 text-purple-700 border-purple-200'
                          }`}
                        >
                          {field.extraction_method.replace('_', ' ')}
                        </span>
                      )}
                      {field.correction_reason ? (
                        <span className="text-amber-700 bg-amber-50/50 px-1.5 py-0.5 rounded text-[10px]">
                          {field.correction_reason}
                        </span>
                      ) : !field.extraction_method || field.extraction_method === 'EXPLICIT' ? (
                        <span className="text-slate-400">Direct extract</span>
                      ) : null}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
