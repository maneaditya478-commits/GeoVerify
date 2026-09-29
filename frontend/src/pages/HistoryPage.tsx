import React, { useState } from 'react';
import { VerificationResponse } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { History, Search, ArrowUpRight } from 'lucide-react';

interface HistoryPageProps {
  history: VerificationResponse[];
  onSelectResult: (res: VerificationResponse) => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ history, onSelectResult }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = history.filter((item) => {
    const text = (
      item.normalized_address.normalized_text +
      ' ' +
      item.status +
      ' ' +
      item.verification_id
    ).toLowerCase();
    return text.includes(searchTerm.toLowerCase());
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-semibold uppercase mb-1">
            <History className="w-3.5 h-3.5" />
            Audit Log
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">Verification History</h2>
          <p className="text-xs text-slate-400 mt-1">
            Recent address consistency verification logs and forensic evidence.
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-72">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by address or ID..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-emerald-500"
          />
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
        </div>
      </div>

      {/* History Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        {filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-500 font-mono text-xs">
            No verification records found in session history.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px] bg-slate-950/60">
                  <th className="py-3.5 pl-4">Verification ID</th>
                  <th className="py-3.5">Address Verified</th>
                  <th className="py-3.5">Status</th>
                  <th className="py-3.5">Consistency Score</th>
                  <th className="py-3.5">Time</th>
                  <th className="py-3.5 pr-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {filtered.map((item) => (
                  <tr key={item.verification_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 pl-4 font-semibold text-slate-300">
                      {item.verification_id}
                    </td>
                    <td className="py-3 text-slate-200 font-sans max-w-xs truncate">
                      {item.normalized_address.normalized_text}
                    </td>
                    <td className="py-3">
                      <StatusBadge status={item.status} size="sm" />
                    </td>
                    <td className="py-3">
                      <span className="font-bold text-emerald-400">{item.score}</span>
                      <span className="text-slate-500"> / 100</span>
                    </td>
                    <td className="py-3 text-slate-400">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-3 pr-4 text-right">
                      <button
                        onClick={() => onSelectResult(item)}
                        className="inline-flex items-center gap-1 text-emerald-400 hover:text-emerald-300 font-medium font-sans hover:underline"
                      >
                        <span>Inspect</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
