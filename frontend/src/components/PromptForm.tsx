'use client';

import React, { useState } from 'react';
import {
  Sparkles,
  Plus,
  Trash2,
  Sliders,
  Wrench,
  Database,
  ShieldAlert,
  ChevronDown,
  ChevronRight,
  Play,
  RotateCcw,
  ShoppingBag,
  Landmark,
  Activity,
  Layers
} from 'lucide-react';
import { AuditRequest, ToolDefinition, RAGContext } from '@/types/audit';
import { PROMPT_PRESETS, PromptPreset } from '@/lib/presets';

interface PromptFormProps {
  formData: AuditRequest;
  setFormData: React.Dispatch<React.SetStateAction<AuditRequest>>;
  onSubmit: () => void;
  isLoading: boolean;
}

export const PromptForm: React.FC<PromptFormProps> = ({
  formData,
  setFormData,
  onSubmit,
  isLoading,
}) => {
  const [activePreset, setActivePreset] = useState<string>('ecommerce_refund');
  const [showTools, setShowTools] = useState<boolean>(false);
  const [showRag, setShowRag] = useState<boolean>(false);
  const [newRule, setNewRule] = useState<string>('');

  const loadPreset = (preset: PromptPreset) => {
    setActivePreset(preset.id);
    setFormData({
      ...preset.config,
    });
  };

  const handleAddRule = () => {
    if (!newRule.trim()) return;
    setFormData((prev) => ({
      ...prev,
      business_rules: [...prev.business_rules, newRule.trim()],
    }));
    setNewRule('');
  };

  const handleRemoveRule = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      business_rules: prev.business_rules.filter((_, i) => i !== index),
    }));
  };

  const handleAddTool = () => {
    const newTool: ToolDefinition = {
      name: `tool_${(formData.tools?.length || 0) + 1}`,
      description: 'Executes an authorized backend action.',
      parameters: [
        { name: 'param1', type: 'string', description: 'Parameter description', required: true }
      ]
    };
    setFormData((prev) => ({
      ...prev,
      tools: [...(prev.tools || []), newTool]
    }));
  };

  const handleRemoveTool = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      tools: (prev.tools || []).filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="space-y-6 rounded-2xl border border-zinc-800/80 bg-zinc-900/50 p-5 backdrop-blur-sm sm:p-6">
      {/* Preset Selectors */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
            <Sparkles className="h-4 w-4" />
            <span>Vulnerability Presets</span>
          </div>
          <span className="text-xs text-zinc-500">Click to auto-populate prompt & rules</span>
        </div>

        <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
          {PROMPT_PRESETS.map((preset) => {
            const isSelected = activePreset === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => loadPreset(preset)}
                className={`flex flex-col items-start rounded-xl border p-3 text-left transition-all ${
                  isSelected
                    ? 'border-cyan-500/50 bg-cyan-500/10 text-white ring-1 ring-cyan-500/30'
                    : 'border-zinc-800 bg-zinc-900/40 text-zinc-400 hover:border-zinc-700 hover:bg-zinc-800/40 hover:text-zinc-200'
                }`}
              >
                <div className="flex w-full items-center justify-between">
                  <span className="text-xs font-semibold text-zinc-300">{preset.name}</span>
                  {preset.id === 'ecommerce_refund' && <ShoppingBag className="h-3.5 w-3.5 text-cyan-400" />}
                  {preset.id === 'fintech_banking' && <Landmark className="h-3.5 w-3.5 text-amber-400" />}
                  {preset.id === 'healthcare_triage' && <Activity className="h-3.5 w-3.5 text-emerald-400" />}
                </div>
                <p className="mt-1 line-clamp-2 text-[11px] leading-relaxed text-zinc-500">
                  {preset.description}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Target System Prompt */}
      <div>
        <div className="mb-2 flex items-center justify-between">
          <label className="text-xs font-semibold uppercase tracking-wider text-zinc-300">
            1. Target System Prompt
          </label>
          <span className="text-xs text-zinc-500">Original prompt to red-team & harden</span>
        </div>
        <div className="relative">
          <textarea
            rows={5}
            value={formData.system_prompt}
            onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
            placeholder="Enter the system instructions for your AI agent..."
            className="w-full rounded-xl border border-zinc-800 bg-zinc-950/80 p-3.5 font-mono text-xs leading-relaxed text-zinc-200 placeholder-zinc-600 transition-colors focus:border-cyan-500/50 focus:outline-none focus:ring-1 focus:ring-cyan-500/30"
          />
        </div>
      </div>

      {/* Explicit Business Rules */}
      <div>
        <div className="mb-2 flex items-center justify-between">
          <label className="text-xs font-semibold uppercase tracking-wider text-zinc-300">
            2. Explicit Security Policies & Business Rules ({formData.business_rules.length})
          </label>
          <span className="text-xs text-zinc-500">Forbidden behaviors tested by Node 1</span>
        </div>

        <div className="space-y-2">
          {formData.business_rules.map((rule, idx) => (
            <div
              key={idx}
              className="group flex items-center gap-2 rounded-lg border border-zinc-800/80 bg-zinc-950/60 px-3 py-2 text-xs text-zinc-300 transition-colors hover:border-zinc-700"
            >
              <span className="font-mono text-zinc-500">#{idx + 1}</span>
              <input
                type="text"
                value={rule}
                onChange={(e) => {
                  const updated = [...formData.business_rules];
                  updated[idx] = e.target.value;
                  setFormData({ ...formData, business_rules: updated });
                }}
                className="flex-1 bg-transparent text-xs text-zinc-200 focus:outline-none"
              />
              <button
                type="button"
                onClick={() => handleRemoveRule(idx)}
                className="text-zinc-600 opacity-0 transition-opacity group-hover:opacity-100 hover:text-rose-400"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}

          <div className="flex gap-2">
            <input
              type="text"
              value={newRule}
              onChange={(e) => setNewRule(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddRule();
                }
              }}
              placeholder="Add a new forbidden rule (e.g. 'Never grant discounts over 20%')..."
              className="flex-1 rounded-lg border border-zinc-800 bg-zinc-950/60 px-3 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:border-cyan-500/50 focus:outline-none"
            />
            <button
              type="button"
              onClick={handleAddRule}
              className="flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-800/80 px-3 py-2 text-xs font-medium text-zinc-200 transition-colors hover:bg-zinc-700"
            >
              <Plus className="h-3.5 w-3.5" />
              Add Rule
            </button>
          </div>
        </div>
      </div>

      {/* Target Model & Attack Count Settings */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Target Model
          </label>
          <select
            value={formData.target_models?.[0] || 'meta-llama/Meta-Llama-3.1-8B-Instruct'}
            onChange={(e) => setFormData({ ...formData, target_models: [e.target.value] })}
            className="w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-xs text-zinc-200 focus:border-cyan-500/50 focus:outline-none"
          >
            <option value="meta-llama/Meta-Llama-3.1-8B-Instruct">Llama 3.1 8B Instruct (Featherless)</option>
            <option value="meta-llama/Meta-Llama-3.1-70B-Instruct">Llama 3.1 70B Instruct (Featherless)</option>
            <option value="mistralai/Mistral-7B-Instruct-v0.3">Mistral 7B Instruct v0.3 (Featherless)</option>
            <option value="gemini-2.5-flash">Gemini 2.5 Flash (Google GenAI)</option>
            <option value="gpt-4o-mini">GPT-4o Mini (OpenAI)</option>
          </select>
        </div>

        <div>
          <div className="mb-1.5 flex items-center justify-between">
            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Adversarial Attacks: {formData.attack_count || 10}
            </label>
            <span className="text-[11px] text-zinc-500">5 vectors balanced</span>
          </div>
          <input
            type="range"
            min={5}
            max={25}
            step={5}
            value={formData.attack_count || 10}
            onChange={(e) => setFormData({ ...formData, attack_count: parseInt(e.target.value) })}
            className="h-2 w-full cursor-pointer accent-cyan-400"
          />
        </div>
      </div>

      {/* Advanced Configurations: Tools & RAG Context Accordions */}
      <div className="space-y-3 pt-2">
        {/* Tools Section */}
        <div className="rounded-xl border border-zinc-800/80 bg-zinc-950/40">
          <button
            type="button"
            onClick={() => setShowTools(!showTools)}
            className="flex w-full items-center justify-between px-4 py-3 text-left text-xs font-semibold text-zinc-400 transition-colors hover:text-zinc-200"
          >
            <div className="flex items-center gap-2">
              <Wrench className="h-3.5 w-3.5 text-cyan-400" />
              <span>Agent Tools & Function Calling ({formData.tools?.length || 0})</span>
            </div>
            {showTools ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </button>

          {showTools && (
            <div className="space-y-3 border-t border-zinc-800/60 p-4">
              <p className="text-xs text-zinc-500">
                Define tools available to the agent. Node 1 will generate injection tests aiming to trigger unauthorized executions.
              </p>
              {(formData.tools || []).map((t, idx) => (
                <div key={idx} className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-medium text-cyan-300">`{t.name}`</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveTool(idx)}
                      className="text-zinc-500 hover:text-rose-400"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                  <p className="mt-1 text-xs text-zinc-400">{t.description}</p>
                </div>
              ))}
              <button
                type="button"
                onClick={handleAddTool}
                className="flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800"
              >
                <Plus className="h-3.5 w-3.5" />
                Add Mock Tool
              </button>
            </div>
          )}
        </div>

        {/* RAG Context Section */}
        <div className="rounded-xl border border-zinc-800/80 bg-zinc-950/40">
          <button
            type="button"
            onClick={() => setShowRag(!showRag)}
            className="flex w-full items-center justify-between px-4 py-3 text-left text-xs font-semibold text-zinc-400 transition-colors hover:text-zinc-200"
          >
            <div className="flex items-center gap-2">
              <Database className="h-3.5 w-3.5 text-amber-400" />
              <span>Synthetic RAG Database & Knowledge Context</span>
            </div>
            {showRag ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </button>

          {showRag && (
            <div className="space-y-3 border-t border-zinc-800/60 p-4">
              <div>
                <label className="mb-1 block text-xs text-zinc-400">Knowledge Domain</label>
                <input
                  type="text"
                  value={formData.rag_context?.domain_description || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      rag_context: {
                        domain_description: e.target.value,
                        sensitive_fields: formData.rag_context?.sensitive_fields || [],
                        records: formData.rag_context?.records || []
                      }
                    })
                  }
                  placeholder="e.g. Core Ledger Database"
                  className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-200 focus:outline-none"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs text-zinc-400">
                  Confidential Fields (Probed for leakage)
                </label>
                <input
                  type="text"
                  value={formData.rag_context?.sensitive_fields?.join(', ') || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      rag_context: {
                        domain_description: formData.rag_context?.domain_description || '',
                        sensitive_fields: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
                        records: formData.rag_context?.records || []
                      }
                    })
                  }
                  placeholder="wholesale_cost, customer_ssn, master_admin_pin"
                  className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-200 focus:outline-none"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Run Audit Action Button */}
      <button
        type="button"
        onClick={onSubmit}
        disabled={isLoading || !formData.system_prompt.trim()}
        className={`flex w-full items-center justify-center gap-2 rounded-xl py-3.5 text-sm font-bold tracking-wide text-zinc-950 transition-all ${
          isLoading
            ? 'cursor-not-allowed bg-zinc-700 text-zinc-400'
            : 'bg-gradient-to-r from-cyan-400 via-teal-400 to-emerald-400 shadow-lg shadow-cyan-500/25 hover:opacity-95 active:scale-[0.99]'
        }`}
      >
        {isLoading ? (
          <>
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-zinc-950 border-t-transparent" />
            <span>Executing Red-Team Simulation Pipeline...</span>
          </>
        ) : (
          <>
            <Play className="h-4 w-4 fill-zinc-950" />
            <span>Launch Security Audit & Harden Prompt</span>
          </>
        )}
      </button>
    </div>
  );
};
