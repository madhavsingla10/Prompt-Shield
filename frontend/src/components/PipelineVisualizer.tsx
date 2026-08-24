'use client';

import React from 'react';
import {
  Skull,
  PlaySquare,
  Scale,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Check
} from 'lucide-react';
import { NodeStage } from '@/types/audit';

interface PipelineVisualizerProps {
  currentStage: NodeStage;
  progress: number;
  statusMessage: string;
}

interface NodeStep {
  id: string;
  stageKey: NodeStage;
  name: string;
  subtext: string;
  icon: React.ComponentType<{ className?: string }>;
}

const NODES: NodeStep[] = [
  {
    id: 'node-1',
    stageKey: 'attack_generation',
    name: 'Node 1: Attack Gen',
    subtext: '5 Vector Payloads',
    icon: Skull,
  },
  {
    id: 'node-2',
    stageKey: 'sandbox_execution',
    name: 'Node 2: Sandbox',
    subtext: 'Live Target Models',
    icon: PlaySquare,
  },
  {
    id: 'node-3',
    stageKey: 'security_evaluation',
    name: 'Node 3: Evaluator',
    subtext: 'Judge Safety Score',
    icon: Scale,
  },
  {
    id: 'node-4',
    stageKey: 'guardrail_compilation',
    name: 'Node 4: Compiler',
    subtext: 'Synthesize Defense',
    icon: ShieldCheck,
  },
  {
    id: 'node-5',
    stageKey: 'verification',
    name: 'Node 5: Verifier',
    subtext: 'Delta Re-Testing',
    icon: CheckCircle2,
  },
];

const STAGE_ORDER: NodeStage[] = [
  'initializing',
  'attack_generation',
  'sandbox_execution',
  'security_evaluation',
  'guardrail_compilation',
  'verification',
  'completed',
];

export const PipelineVisualizer: React.FC<PipelineVisualizerProps> = ({
  currentStage,
  progress,
  statusMessage,
}) => {
  const currentStageIndex = STAGE_ORDER.indexOf(currentStage);
  const isFailed = currentStage === 'failed';
  const isCompleted = currentStage === 'completed';

  const getNodeState = (nodeStage: NodeStage) => {
    if (isFailed) return 'failed';
    if (isCompleted) return 'completed';

    const nodeIndex = STAGE_ORDER.indexOf(nodeStage);
    if (currentStageIndex > nodeIndex) return 'completed';
    if (currentStageIndex === nodeIndex) return 'running';
    return 'pending';
  };

  return (
    <div className="rounded-2xl border border-zinc-800/80 bg-zinc-900/50 p-5 backdrop-blur-sm sm:p-6">
      {/* Header & Status Indicator */}
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
            Multi-Node Autonomous Security Pipeline
          </h3>
          <p className="mt-1 text-sm font-medium text-zinc-200">
            {statusMessage || 'Awaiting audit trigger...'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="font-mono text-xs font-bold text-cyan-400">
              {Math.round(progress * 100)}%
            </span>
            <span className="ml-1 text-xs text-zinc-500">Progress</span>
          </div>
        </div>
      </div>

      {/* Animated Overall Progress Bar */}
      <div className="mb-6 h-1.5 w-full overflow-hidden rounded-full bg-zinc-800">
        <div
          className="h-full bg-gradient-to-r from-cyan-400 via-teal-400 to-emerald-400 transition-all duration-500 ease-out"
          style={{ width: `${Math.max(progress * 100, 2)}%` }}
        />
      </div>

      {/* 5-Node Flow Stepper */}
      <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-5">
        {NODES.map((node, idx) => {
          const state = getNodeState(node.stageKey);
          const Icon = node.icon;

          return (
            <div
              key={node.id}
              className={`relative flex flex-col rounded-xl border p-3 transition-all ${
                state === 'running'
                  ? 'border-cyan-500/60 bg-cyan-500/10 shadow-lg shadow-cyan-500/10'
                  : state === 'completed'
                  ? 'border-emerald-500/40 bg-emerald-500/5 text-zinc-300'
                  : 'border-zinc-800/80 bg-zinc-950/40 text-zinc-500'
              }`}
            >
              <div className="flex items-center justify-between">
                <div
                  className={`flex h-7 w-7 items-center justify-center rounded-lg ${
                    state === 'running'
                      ? 'bg-cyan-500 text-zinc-950 shadow-md shadow-cyan-500/30'
                      : state === 'completed'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-zinc-800 text-zinc-500'
                  }`}
                >
                  {state === 'running' ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : state === 'completed' ? (
                    <Check className="h-4 w-4 stroke-[3]" />
                  ) : (
                    <Icon className="h-4 w-4" />
                  )}
                </div>

                <span className="font-mono text-[10px] uppercase tracking-wider text-zinc-500">
                  Step 0{idx + 1}
                </span>
              </div>

              <div className="mt-2.5">
                <p
                  className={`text-xs font-semibold ${
                    state === 'running'
                      ? 'text-cyan-300'
                      : state === 'completed'
                      ? 'text-emerald-300'
                      : 'text-zinc-400'
                  }`}
                >
                  {node.name}
                </p>
                <p className="text-[11px] text-zinc-500">{node.subtext}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
