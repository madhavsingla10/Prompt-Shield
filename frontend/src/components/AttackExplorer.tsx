'use client';

import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  ChevronDown,
  ChevronRight,
  Filter,
  Flame,
  UserX,
  Code2,
  Lock,
  Search,
  Sparkles
} from 'lucide-react';
import { AttackCase, EvaluationResult, VerificationResult, AttackCategory } from '@/types/audit';

interface AttackExplorerProps {
  attacks: AttackCase[];
  initialEvaluations: EvaluationResult[];
  postEvaluations?: VerificationResult[];
}

export const AttackExplorer: React.FC<AttackExplorerProps> = ({
  attacks,
  initialEvaluations,
  postEvaluations = [],
}) => {
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<'all' | 'breached' | 'passed'>('all');
  const [expandedId, setExpandedId] = useState<number | null>(attacks[0]?.id || null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const initEvalMap = new Map<number, EvaluationResult>(
    initialEvaluations.map((e) => [e.attack_id, e])
  );
  const postEvalMap = new Map<number, VerificationResult>(
    postEvaluations.map((e) => [e.attack_id, e])
  );

  const getCategoryIcon = (cat: AttackCategory) => {
    switch (cat) {
      case 'direct_override':
        return <Flame className="h-3.5 w-3.5 text-rose-400" />;
      case 'roleplay_hijack':
        return <UserX className="h-3.5 w-3.5 text-purple-400" />;
      case 'delimiter_injection':
        return <Code2 className="h-3.5 w-3.5 text-amber-400" />;
      case 'indirect_evasion':
        return <Search className="h-3.5 w-3.5 text-cyan-400" />;
      case 'data_leakage':
        return <Lock className="h-3.5 w-3.5 text-blue-400" />;
      default:
        return <Sparkles className="h-3.5 w-3.5 text-zinc-400" />;
    }
  };

  const filteredAttacks = attacks.filter((atk) => {
    const initEval = initEvalMap.get(atk.id);
    const matchesCategory = filterCategory === 'all' || atk.category === filterCategory;
    const matchesStatus =
      filterStatus === 'all' ||
      (filterStatus === 'breached' && initEval && !initEval.passed) ||
      (filterStatus === 'passed' && initEval && initEval.passed);
    const matchesSearch =
      !searchQuery ||
      atk.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      atk.description?.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesCategory && matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-zinc-900/50 p-5 backdrop-blur-sm sm:p-6">
      {/* Header & Search */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800/80 pb-4">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
            Adversarial Test Suite Explorer ({attacks.length} Payloads)
          </h3>
          <p className="text-xs text-zinc-400">
            Inspect individual attack vectors, model behavior, and judge verdicts
          </p>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search payloads..."
            className="rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-600 focus:border-cyan-500/50 focus:outline-none"
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => setFilterStatus('all')}
            className={`rounded-lg px-2.5 py-1 transition-colors ${
              filterStatus === 'all'
                ? 'bg-zinc-700 text-white font-semibold'
                : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
            }`}
          >
            All ({attacks.length})
          </button>
          <button
            type="button"
            onClick={() => setFilterStatus('breached')}
            className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 transition-colors ${
              filterStatus === 'breached'
                ? 'bg-rose-500/20 text-rose-300 font-semibold ring-1 ring-rose-500/40'
                : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
            }`}
          >
            <ShieldAlert className="h-3 w-3 text-rose-400" />
            Breached Initial ({initialEvaluations.filter((e) => !e.passed).length})
          </button>
          <button
            type="button"
            onClick={() => setFilterStatus('passed')}
            className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 transition-colors ${
              filterStatus === 'passed'
                ? 'bg-emerald-500/20 text-emerald-300 font-semibold ring-1 ring-emerald-500/40'
                : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
            }`}
          >
            <ShieldCheck className="h-3 w-3 text-emerald-400" />
            Blocked Initial ({initialEvaluations.filter((e) => e.passed).length})
          </button>
        </div>

        {/* Category Filter Dropdown */}
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="rounded-lg border border-zinc-800 bg-zinc-950 px-2.5 py-1 text-xs text-zinc-300 focus:outline-none"
        >
          <option value="all">All Vector Categories</option>
          <option value="direct_override">Direct Override</option>
          <option value="roleplay_hijack">Roleplay Hijack</option>
          <option value="delimiter_injection">Delimiter Injection</option>
          <option value="indirect_evasion">Indirect Evasion</option>
          <option value="data_leakage">Data Leakage</option>
        </select>
      </div>

      {/* Attacks List */}
      <div className="space-y-2">
        {filteredAttacks.length === 0 ? (
          <div className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-8 text-center text-xs text-zinc-500">
            No adversarial payloads match the selected filters.
          </div>
        ) : (
          filteredAttacks.map((atk) => {
            const initEval = initEvalMap.get(atk.id);
            const postEval = postEvalMap.get(atk.id);
            const isExpanded = expandedId === atk.id;

            return (
              <div
                key={atk.id}
                className={`overflow-hidden rounded-xl border transition-all ${
                  isExpanded
                    ? 'border-zinc-700 bg-zinc-950/90 shadow-lg'
                    : 'border-zinc-800/80 bg-zinc-950/40 hover:border-zinc-700'
                }`}
              >
                {/* Attack Card Row Header */}
                <button
                  type="button"
                  onClick={() => setExpandedId(isExpanded ? null : atk.id)}
                  className="flex w-full items-center justify-between p-3 text-left transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-zinc-500">#{atk.id}</span>
                    <div className="flex items-center gap-1.5 rounded-md border border-zinc-800 bg-zinc-900 px-2 py-0.5 text-[11px] font-medium text-zinc-300">
                      {getCategoryIcon(atk.category)}
                      <span>{atk.category.replace('_', ' ')}</span>
                    </div>
                    <span className="line-clamp-1 font-mono text-xs text-zinc-300 max-w-md">
                      {atk.prompt}
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    {/* Initial Status Badge */}
                    {initEval && (
                      <span
                        className={`flex items-center gap-1 rounded-md px-2 py-0.5 text-[10px] font-semibold uppercase ${
                          initEval.passed
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}
                      >
                        {initEval.passed ? 'Baseline: Blocked' : 'Baseline: Breached'}
                      </span>
                    )}

                    {/* Post-Hardening Status Badge */}
                    {postEval && (
                      <span
                        className={`flex items-center gap-1 rounded-md px-2 py-0.5 text-[10px] font-semibold uppercase ${
                          postEval.passed
                            ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}
                      >
                        {postEval.passed ? 'Hardened: Secured' : 'Hardened: Breached'}
                      </span>
                    )}

                    {isExpanded ? (
                      <ChevronDown className="h-4 w-4 text-zinc-400" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-zinc-400" />
                    )}
                  </div>
                </button>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="border-t border-zinc-800/80 bg-zinc-900/30 p-4 space-y-3 text-xs">
                    {/* Full Attack Prompt */}
                    <div>
                      <span className="font-semibold uppercase tracking-wider text-zinc-400">
                        Adversarial Payload:
                      </span>
                      <div className="mt-1 rounded-lg border border-zinc-800 bg-zinc-950 p-3 font-mono text-xs text-rose-300">
                        {atk.prompt}
                      </div>
                    </div>

                    {/* Target Rule / Attack Objective */}
                    {atk.description && (
                      <div className="flex items-center gap-2 text-zinc-400">
                        <span className="font-semibold text-zinc-300">Objective:</span>
                        <span>{atk.description}</span>
                      </div>
                    )}

                    {/* Evaluation Diagnostics */}
                    {initEval && (
                      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 pt-2 border-t border-zinc-800/60">
                        <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 p-3">
                          <span className="font-semibold text-zinc-400 uppercase text-[10px] tracking-wider">
                            Initial Evaluation Verdict
                          </span>
                          <div className="mt-2 space-y-1 text-xs">
                            <div className="flex justify-between">
                              <span className="text-zinc-500">Rule Violation:</span>
                              <span className={initEval.rule_violation ? 'text-rose-400 font-bold' : 'text-emerald-400'}>
                                {initEval.rule_violation ? 'TRUE (BREACHED)' : 'FALSE'}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-zinc-500">Instruction Leakage:</span>
                              <span className={initEval.instruction_leakage ? 'text-rose-400 font-bold' : 'text-emerald-400'}>
                                {initEval.instruction_leakage ? 'TRUE (LEAKED)' : 'FALSE'}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-zinc-500">Refusal Quality:</span>
                              <span className="font-mono text-zinc-200">{initEval.refusal_quality}/5</span>
                            </div>
                            <p className="mt-2 text-zinc-400 italic text-[11px]">
                              &quot;{initEval.reasoning}&quot;
                            </p>
                          </div>
                        </div>

                        {postEval && (
                          <div className="rounded-lg border border-cyan-500/20 bg-cyan-950/10 p-3">
                            <span className="font-semibold text-cyan-400 uppercase text-[10px] tracking-wider">
                              Post-Hardening Verdict
                            </span>
                            <div className="mt-2 space-y-1 text-xs">
                              <div className="flex justify-between">
                                <span className="text-zinc-500">Rule Violation:</span>
                                <span className={postEval.rule_violation ? 'text-rose-400 font-bold' : 'text-emerald-400'}>
                                  {postEval.rule_violation ? 'TRUE' : 'FALSE (BLOCKED)'}
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-zinc-500">Instruction Leakage:</span>
                                <span className={postEval.instruction_leakage ? 'text-rose-400 font-bold' : 'text-emerald-400'}>
                                  {postEval.instruction_leakage ? 'TRUE' : 'FALSE (SECURE)'}
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-zinc-500">Refusal Quality:</span>
                                <span className="font-mono text-zinc-200">{postEval.refusal_quality}/5</span>
                              </div>
                              <p className="mt-2 text-cyan-200/80 italic text-[11px]">
                                &quot;{postEval.reasoning}&quot;
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
