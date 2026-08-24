'use client';

import React, { useState } from 'react';
import confetti from 'canvas-confetti';
import {
  ShieldAlert,
  Terminal,
  Layers,
  FileCode2,
  Share2,
  RotateCcw,
  Sparkles,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';
import { AuditRequest, AuditSummary, SSEEvent, NodeStage } from '@/types/audit';
import { PROMPT_PRESETS } from '@/lib/presets';
import { streamAuditPipeline, runAuditRest } from '@/lib/api';
import { Navbar } from '@/components/Navbar';
import { PromptForm } from '@/components/PromptForm';
import { PipelineVisualizer } from '@/components/PipelineVisualizer';
import { LiveConsole } from '@/components/LiveConsole';
import { ScoreCard } from '@/components/ScoreCard';
import { AttackExplorer } from '@/components/AttackExplorer';
import { DiffViewer } from '@/components/DiffViewer';
import { ExportModal } from '@/components/ExportModal';

export default function Home() {
  const [formData, setFormData] = useState<AuditRequest>(PROMPT_PRESETS[0].config);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [currentStage, setCurrentStage] = useState<NodeStage>('initializing');
  const [progress, setProgress] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>('Ready to test');
  const [consoleEvents, setConsoleEvents] = useState<SSEEvent[]>([]);
  const [auditSummary, setAuditSummary] = useState<AuditSummary | null>(null);
  const [activeTab, setActiveTab] = useState<'live' | 'explorer' | 'diff'>('live');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);

  const handleStartAudit = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    setConsoleEvents([]);
    setAuditSummary(null);
    setProgress(0.05);
    setCurrentStage('initializing');
    setStatusMessage('Starting multi-node red-teaming pipeline...');
    setActiveTab('live');

    let receivedCompletedEvent = false;

    try {
      await streamAuditPipeline(
        formData,
        (evt) => {
          setConsoleEvents((prev) => [...prev, evt]);
          setCurrentStage(evt.stage);
          setProgress(evt.progress);
          setStatusMessage(evt.message);
        },
        (error) => {
          setErrorMessage(error);
          setIsLoading(false);
        },
        (summary) => {
          receivedCompletedEvent = true;
          setAuditSummary(summary);
          setIsLoading(false);
          setCurrentStage('completed');
          setProgress(1.0);
          setStatusMessage(
            `Audit Completed! Initial Score: ${summary.initial_safety_score}% → Hardened Score: ${summary.post_safety_score}% (+${summary.score_delta}%)`
          );

          if (summary.score_delta >= 0) {
            confetti({
              particleCount: 80,
              spread: 70,
              origin: { y: 0.6 },
              colors: ['#06b6d4', '#10b981', '#3b82f6'],
            });
          }
        }
      );
    } catch (err: any) {
      console.warn('SSE Streaming fallback to REST audit:', err);
      try {
        const summary = await runAuditRest(formData);
        setAuditSummary(summary);
        setIsLoading(false);
        setCurrentStage('completed');
        setProgress(1.0);
        setStatusMessage('Audit completed successfully via standard endpoint.');
      } catch (restErr: any) {
        setErrorMessage(restErr.message || 'Audit execution failed');
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 selection:bg-cyan-500/30 selection:text-cyan-200">
      <Navbar />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-3 max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-300">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Autonomous Prompt Red-Teaming & Guardrail Compiler</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl lg:text-5xl text-white">
            Single Prompts Break. <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">
              Hardened Pipelines Defend.
            </span>
          </h1>
          <p className="text-sm text-zinc-400 leading-relaxed">
            Automatically generate 5-vector adversarial attacks, execute live sandbox probes, judge
            boundary violations, and compile verified impenetrable XML system prompts.
          </p>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="flex items-center gap-3 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs text-rose-300">
            <AlertCircle className="h-5 w-5 shrink-0 text-rose-400" />
            <div className="flex-1">
              <span className="font-semibold">Pipeline Error: </span>
              <span>{errorMessage}</span>
            </div>
          </div>
        )}

        {/* Top Control Grid: Left Form / Right Pipeline Status */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          {/* Left Column: Prompt Input & Configurator */}
          <div className="lg:col-span-5 space-y-6">
            <PromptForm
              formData={formData}
              setFormData={setFormData}
              onSubmit={handleStartAudit}
              isLoading={isLoading}
            />
          </div>

          {/* Right Column: Multi-Node Pipeline Visualizer & Live Interactive Workspace */}
          <div className="lg:col-span-7 space-y-6">
            {/* Visual 5-Node Stepper */}
            <PipelineVisualizer
              currentStage={currentStage}
              progress={progress}
              statusMessage={statusMessage}
            />

            {/* Results Score Card (Shows when Audit Summary is ready) */}
            {auditSummary && <ScoreCard summary={auditSummary} />}

            {/* Interactive Workspace Navigation Tabs */}
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 pb-3">
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setActiveTab('live')}
                    className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                      activeTab === 'live'
                        ? 'bg-zinc-800 text-white'
                        : 'text-zinc-400 hover:text-zinc-200'
                    }`}
                  >
                    <Terminal className="h-3.5 w-3.5" />
                    <span>Live Console</span>
                    {consoleEvents.length > 0 && (
                      <span className="rounded-full bg-zinc-700 px-1.5 text-[10px] text-zinc-300">
                        {consoleEvents.length}
                      </span>
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab('explorer')}
                    disabled={!auditSummary}
                    className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                      activeTab === 'explorer'
                        ? 'bg-zinc-800 text-white'
                        : auditSummary
                        ? 'text-zinc-400 hover:text-zinc-200'
                        : 'cursor-not-allowed text-zinc-600'
                    }`}
                  >
                    <Layers className="h-3.5 w-3.5" />
                    <span>Attack Explorer</span>
                    {auditSummary && (
                      <span className="rounded-full bg-cyan-500/20 px-1.5 text-[10px] text-cyan-300">
                        {auditSummary.attacks.length}
                      </span>
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab('diff')}
                    disabled={!auditSummary}
                    className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                      activeTab === 'diff'
                        ? 'bg-zinc-800 text-white'
                        : auditSummary
                        ? 'text-zinc-400 hover:text-zinc-200'
                        : 'cursor-not-allowed text-zinc-600'
                    }`}
                  >
                    <FileCode2 className="h-3.5 w-3.5 text-emerald-400" />
                    <span>Hardened Diff</span>
                  </button>
                </div>

                {auditSummary && (
                  <button
                    type="button"
                    onClick={() => setIsExportOpen(true)}
                    className="flex items-center gap-1.5 rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-3 py-1.5 text-xs font-semibold text-cyan-300 hover:bg-cyan-500/20"
                  >
                    <Share2 className="h-3.5 w-3.5" />
                    <span>Export Audit Report</span>
                  </button>
                )}
              </div>

              {/* Tab Views */}
              {activeTab === 'live' && (
                <LiveConsole
                  events={consoleEvents}
                  onClear={() => setConsoleEvents([])}
                />
              )}

              {activeTab === 'explorer' && auditSummary && (
                <AttackExplorer
                  attacks={auditSummary.attacks}
                  initialEvaluations={auditSummary.initial_evaluations}
                  postEvaluations={auditSummary.post_evaluations}
                />
              )}

              {activeTab === 'diff' && auditSummary && (
                <DiffViewer
                  originalPrompt={auditSummary.original_prompt}
                  hardenedPrompt={auditSummary.hardened_prompt}
                  changesMade={auditSummary.hardening_changes}
                  diffText={auditSummary.defensive_diff}
                />
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Export Report Modal */}
      {auditSummary && (
        <ExportModal
          summary={auditSummary}
          isOpen={isExportOpen}
          onClose={() => setIsExportOpen(false)}
        />
      )}
    </div>
  );
}
