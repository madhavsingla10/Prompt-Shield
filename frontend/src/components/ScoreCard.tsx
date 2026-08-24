'use client';

import React from 'react';
import { ShieldCheck, ShieldAlert, ArrowUpRight, TrendingUp, Bug, CheckCircle } from 'lucide-react';
import { AuditSummary } from '@/types/audit';

interface ScoreCardProps {
  summary: AuditSummary;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ summary }) => {
  const {
    initial_safety_score,
    post_safety_score,
    score_delta,
    total_attacks,
    initial_failed_count,
    post_failed_count,
  } = summary;

  const breachesFixed = Math.max(0, initial_failed_count - post_failed_count);

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
      {/* 1. Initial Safety Score */}
      <div className="flex flex-col justify-between rounded-2xl border border-rose-500/30 bg-rose-500/5 p-5 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-rose-400">
            Initial Safety Score
          </span>
          <ShieldAlert className="h-5 w-5 text-rose-400" />
        </div>
        <div className="mt-3">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold tracking-tight text-white">
              {initial_safety_score}%
            </span>
            <span className="text-xs text-rose-400 font-medium">
              ({total_attacks - initial_failed_count}/{total_attacks} blocked)
            </span>
          </div>
          <p className="mt-1 text-xs text-zinc-400">
            {initial_failed_count} vulnerabilities breached baseline prompt
          </p>
        </div>
      </div>

      {/* 2. Post-Hardening Safety Score */}
      <div className="flex flex-col justify-between rounded-2xl border border-emerald-500/40 bg-emerald-500/10 p-5 shadow-lg shadow-emerald-500/10 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
            Post-Hardened Score
          </span>
          <ShieldCheck className="h-5 w-5 text-emerald-400" />
        </div>
        <div className="mt-3">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold tracking-tight text-white">
              {post_safety_score}%
            </span>
            <span className="text-xs text-emerald-400 font-medium">
              ({total_attacks - post_failed_count}/{total_attacks} blocked)
            </span>
          </div>
          <p className="mt-1 text-xs text-zinc-400">
            Compiled with XML isolation & refusal protocol
          </p>
        </div>
      </div>

      {/* 3. Safety Score Delta Improvement */}
      <div className="flex flex-col justify-between rounded-2xl border border-cyan-500/30 bg-cyan-500/5 p-5 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
            Score Delta (ROI)
          </span>
          <TrendingUp className="h-5 w-5 text-cyan-400" />
        </div>
        <div className="mt-3">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold tracking-tight text-cyan-300">
              {score_delta >= 0 ? `+${score_delta}%` : `${score_delta}%`}
            </span>
            <ArrowUpRight className="h-4 w-4 text-cyan-400" />
          </div>
          <p className="mt-1 text-xs text-zinc-400">
            Net safety improvement post Node 4 compiler
          </p>
        </div>
      </div>

      {/* 4. Breaches Resolved */}
      <div className="flex flex-col justify-between rounded-2xl border border-zinc-800 bg-zinc-900/50 p-5 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Breaches Resolved
          </span>
          <CheckCircle className="h-5 w-5 text-teal-400" />
        </div>
        <div className="mt-3">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold tracking-tight text-white">
              {breachesFixed}
            </span>
            <span className="text-xs text-zinc-500">
              of {initial_failed_count} patched
            </span>
          </div>
          <p className="mt-1 text-xs text-zinc-400">
            Across 5 injection taxonomy categories
          </p>
        </div>
      </div>
    </div>
  );
};
