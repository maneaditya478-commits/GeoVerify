import React from 'react';
import { VerificationStatus } from '../types';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, AlertCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: VerificationStatus;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-sm px-3 py-1 gap-1.5',
    lg: 'text-base px-4 py-1.5 gap-2 font-semibold',
  };

  const config: Record<
    VerificationStatus,
    { label: string; bg: string; text: string; border: string; icon: React.ReactNode }
  > = {
    VERIFIED: {
      label: 'VERIFIED',
      bg: 'bg-emerald-500/15',
      text: 'text-emerald-400',
      border: 'border-emerald-500/30',
      icon: <CheckCircle2 className={size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />,
    },
    CONSISTENT: {
      label: 'CONSISTENT',
      bg: 'bg-teal-500/15',
      text: 'text-teal-400',
      border: 'border-teal-500/30',
      icon: <CheckCircle2 className={size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />,
    },
    NEEDS_REVIEW: {
      label: 'NEEDS REVIEW',
      bg: 'bg-amber-500/15',
      text: 'text-amber-400',
      border: 'border-amber-500/30',
      icon: <AlertTriangle className={size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />,
    },
    INCONSISTENT: {
      label: 'INCONSISTENT',
      bg: 'bg-rose-500/15',
      text: 'text-rose-400',
      border: 'border-rose-500/30',
      icon: <XCircle className={size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />,
    },
    AMBIGUOUS: {
      label: 'AMBIGUOUS',
      bg: 'bg-purple-500/15',
      text: 'text-purple-400',
      border: 'border-purple-500/30',
      icon: <HelpCircle className={size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />,
    },
    UNABLE_TO_VERIFY: {
      label: 'UNABLE TO VERIFY',
      bg: 'bg-slate-500/15',
      text: 'text-slate-400',
      border: 'border-slate-500/30',
      icon: <AlertCircle className={size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />,
    },
  };

  const item = config[status] || config.UNABLE_TO_VERIFY;

  return (
    <span
      className={`inline-flex items-center rounded-full border font-mono tracking-wide ${item.bg} ${item.text} ${item.border} ${sizeClasses[size]}`}
    >
      {item.icon}
      <span>{item.label}</span>
    </span>
  );
};
