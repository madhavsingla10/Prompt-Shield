'use client';

import React, { useState } from 'react';
import { Copy, Check, Download, ShieldCheck, Sparkles, Code, FileText, ArrowRight } from 'lucide-react';
import { HardenedPrompt } from '@/types/audit';

interface DiffViewerProps {
  originalPrompt: string;
  hardenedPrompt: string;
  changesMade?: string[];
  diffText?: string;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({
  originalPrompt,
  hardenedPrompt,
  changesMade = [],
  diffText,
}) => {
  const [viewMode, setViewMode] = useState<'side-by-side' | 'hardened' | 'unified-diff'>('side-by-side');
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopyHardened = () => {
    navigator.clipboard.writeText(hardenedPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([hardenedPrompt], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'hardened_system_prompt.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="space-y-4 rounded-2xl border border-zinc-800/80 bg-zinc-900/50 p-5 backdrop-blur-sm sm:p-6">
      {/* Header & Mode Switcher */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
              Compiled Hardened Prompt & Security Diff
            </h3>
          </div>
          <p className="text-xs text-zinc-400">
            Node 4 Guardrail Compiler reconstruction with XML boundaries and refusal protocols
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-zinc-800 bg-zinc-950 p-0.5 text-xs">
            <button
              type="button"
              onClick={() => setViewMode('side-by-side')}
              className={`rounded-md px-2.5 py-1 transition-colors ${
                viewMode === 'side-by-side'
                  ? 'bg-zinc-800 text-white font-medium'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Side-by-Side
            </button>
            <button
              type="button"
              onClick={() => setViewMode('hardened')}
              className={`rounded-md px-2.5 py-1 transition-colors ${
                viewMode === 'hardened'
                  ? 'bg-zinc-800 text-white font-medium'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Hardened Prompt
            </button>
            {diffText && (
              <button
                type="button"
                onClick={() => setViewMode('unified-diff')}
                className={`rounded-md px-2.5 py-1 transition-colors ${
                  viewMode === 'unified-diff'
                    ? 'bg-zinc-800 text-white font-medium'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`}
              >
                Unified Diff
              </button>
            )}
          </div>

          <button
            type="button"
            onClick={handleCopyHardened}
            className="flex items-center gap-1.5 rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-3 py-1.5 text-xs font-semibold text-cyan-300 transition-colors hover:bg-cyan-500/20"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            <span>{copied ? 'Copied!' : 'Copy Prompt'}</span>
          </button>

          <button
            type="button"
            onClick={handleDownload}
            className="flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white"
          >
            <Download className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Download</span>
          </button>
        </div>
      </div>

      {/* Defensive Patches Applied Chips */}
      {changesMade.length > 0 && (
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
            Defensive Enhancements Applied:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {changesMade.map((ch, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 rounded-md border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[11px] text-emerald-300"
              >
                <Sparkles className="h-3 w-3 text-emerald-400" />
                {ch}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Main Diff / Viewer Area */}
      {viewMode === 'side-by-side' && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {/* Left: Original Vulnerable Prompt */}
          <div className="flex flex-col rounded-xl border border-zinc-800 bg-zinc-950/80 p-4">
            <div className="mb-2 flex items-center justify-between border-b border-zinc-800/80 pb-2">
              <span className="text-xs font-semibold text-rose-400 uppercase tracking-wider">
                Original Vulnerable Prompt
              </span>
              <span className="text-[10px] text-zinc-500 font-mono">Baseline</span>
            </div>
            <pre className="flex-1 overflow-x-auto whitespace-pre-wrap font-mono text-xs leading-relaxed text-zinc-400">
              {originalPrompt}
            </pre>
          </div>

          {/* Right: Compiled Hardened Prompt */}
          <div className="flex flex-col rounded-xl border border-cyan-500/30 bg-cyan-950/20 p-4">
            <div className="mb-2 flex items-center justify-between border-b border-cyan-500/20 pb-2">
              <span className="text-xs font-semibold text-cyan-300 uppercase tracking-wider">
                Compiled Hardened Prompt (Node 4 Output)
              </span>
              <span className="text-[10px] text-cyan-400 font-mono">Protected</span>
            </div>
            <pre className="flex-1 overflow-x-auto whitespace-pre-wrap font-mono text-xs leading-relaxed text-cyan-100">
              {hardenedPrompt}
            </pre>
          </div>
        </div>
      )}

      {viewMode === 'hardened' && (
        <div className="rounded-xl border border-cyan-500/30 bg-zinc-950 p-4">
          <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-xs leading-relaxed text-cyan-100">
            {hardenedPrompt}
          </pre>
        </div>
      )}

      {viewMode === 'unified-diff' && diffText && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4 font-mono text-xs leading-relaxed overflow-x-auto">
          {diffText.split('\n').map((line, idx) => {
            let color = 'text-zinc-400';
            let bg = '';
            if (line.startsWith('+') && !line.startsWith('+++')) {
              color = 'text-emerald-300';
              bg = 'bg-emerald-500/10';
            } else if (line.startsWith('-') && !line.startsWith('---')) {
              color = 'text-rose-300';
              bg = 'bg-rose-500/10';
            } else if (line.startsWith('@@')) {
              color = 'text-cyan-400';
              bg = 'bg-cyan-500/10';
            }

            return (
              <div key={idx} className={`${color} ${bg} px-1.5 py-0.5 rounded`}>
                {line || ' '}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
