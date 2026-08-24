'use client';

import React, { useEffect, useState } from 'react';
import { Shield, ShieldAlert, Cpu, ExternalLink, Activity, Code2 } from 'lucide-react';
import { checkBackendHealth } from '@/lib/api';

export const Navbar: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'online' | 'degraded' | 'offline'>('checking');

  useEffect(() => {
    const check = async () => {
      const res = await checkBackendHealth();
      if (res.status === 'healthy') setHealthStatus('online');
      else if (res.status === 'degraded') setHealthStatus('degraded');
      else setHealthStatus('offline');
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20">
            <Shield className="h-5 w-5 text-white" />
            <div className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-emerald-400 ring-2 ring-zinc-950" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-tight text-white">PromptShield</span>
              <span className="rounded-md bg-cyan-500/10 px-2 py-0.5 text-xs font-semibold text-cyan-400 ring-1 ring-inset ring-cyan-500/30">
                ARENA
              </span>
            </div>
            <p className="text-xs text-zinc-400">Automated Prompt Red-Teaming & Guardrail Compiler</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/60 px-3 py-1.5 text-xs sm:flex">
            <Activity className="h-3.5 w-3.5 text-zinc-400" />
            <span className="text-zinc-400">Backend:</span>
            {healthStatus === 'checking' && (
              <span className="flex items-center gap-1.5 text-zinc-400">
                <span className="h-2 w-2 animate-ping rounded-full bg-yellow-400" />
                Connecting...
              </span>
            )}
            {healthStatus === 'online' && (
              <span className="flex items-center gap-1.5 font-medium text-emerald-400">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                Online
              </span>
            )}
            {healthStatus === 'degraded' && (
              <span className="flex items-center gap-1.5 font-medium text-amber-400">
                <span className="h-2 w-2 rounded-full bg-amber-400" />
                Live / Ready
              </span>
            )}
            {healthStatus === 'offline' && (
              <span className="flex items-center gap-1.5 font-medium text-rose-400">
                <span className="h-2 w-2 rounded-full bg-rose-400" />
                Offline
              </span>
            )}
          </div>

          <a
            href="https://github.com/madhavsingla10/Prompt-Shield"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-300 transition-colors hover:bg-zinc-800 hover:text-white"
          >
            <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
            <span className="hidden sm:inline">GitHub</span>
          </a>
        </div>
      </div>
    </header>
  );
};
