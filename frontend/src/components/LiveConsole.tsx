'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Terminal, Copy, Check, Trash2, ArrowDown } from 'lucide-react';
import { SSEEvent } from '@/types/audit';

interface LiveConsoleProps {
  events: SSEEvent[];
  onClear?: () => void;
}

export const LiveConsole: React.FC<LiveConsoleProps> = ({ events, onClear }) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [events, autoScroll]);

  const handleCopyLogs = () => {
    const text = events
      .map((e) => `[${e.stage.toUpperCase()}] (${Math.round(e.progress * 100)}%) ${e.message}`)
      .join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'attack_generation':
        return 'text-purple-400 bg-purple-500/10 border-purple-500/20';
      case 'sandbox_execution':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'security_evaluation':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'guardrail_compilation':
        return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20';
      case 'verification':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'completed':
        return 'text-emerald-300 bg-emerald-500/20 border-emerald-500/30 font-bold';
      case 'failed':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      default:
        return 'text-zinc-400 bg-zinc-800 border-zinc-700';
    }
  };

  return (
    <div className="flex flex-col rounded-2xl border border-zinc-800 bg-zinc-950 p-4 font-mono text-xs shadow-2xl">
      {/* Console Header */}
      <div className="mb-3 flex items-center justify-between border-b border-zinc-800/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="h-3 w-3 rounded-full bg-rose-500/80" />
            <div className="h-3 w-3 rounded-full bg-amber-500/80" />
            <div className="h-3 w-3 rounded-full bg-emerald-500/80" />
          </div>
          <div className="ml-2 flex items-center gap-1.5 text-zinc-400">
            <Terminal className="h-3.5 w-3.5" />
            <span className="font-semibold text-zinc-300">Live Simulation Terminal</span>
            <span className="text-[10px] text-zinc-600">({events.length} events)</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopyLogs}
            disabled={events.length === 0}
            className="flex items-center gap-1 rounded bg-zinc-900 px-2 py-1 text-[11px] text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-200"
          >
            {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
          {onClear && (
            <button
              type="button"
              onClick={onClear}
              disabled={events.length === 0}
              className="flex items-center gap-1 rounded bg-zinc-900 px-2 py-1 text-[11px] text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-rose-400"
            >
              <Trash2 className="h-3 w-3" />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Console Output Body */}
      <div className="h-64 overflow-y-auto space-y-2 pr-2 text-[11px] scrollbar-thin scrollbar-thumb-zinc-800">
        {events.length === 0 ? (
          <div className="flex h-full items-center justify-center text-zinc-600">
            <span>&gt; Ready. Click &quot;Launch Security Audit&quot; to begin red-team simulation.</span>
          </div>
        ) : (
          events.map((evt, idx) => (
            <div key={idx} className="flex items-start gap-2.5 leading-relaxed">
              <span className="shrink-0 text-zinc-600 select-none">
                {String(idx + 1).padStart(2, '0')}
              </span>
              <span
                className={`shrink-0 rounded border px-1.5 py-0.5 text-[10px] uppercase font-semibold ${getStageColor(
                  evt.stage
                )}`}
              >
                {evt.stage.replace('_', ' ')}
              </span>
              <span className="flex-1 text-zinc-300 break-words">{evt.message}</span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
