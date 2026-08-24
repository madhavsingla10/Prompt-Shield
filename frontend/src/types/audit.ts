export type AttackCategory =
  | 'direct_override'
  | 'roleplay_hijack'
  | 'delimiter_injection'
  | 'indirect_evasion'
  | 'data_leakage';

export type NodeStage =
  | 'initializing'
  | 'attack_generation'
  | 'sandbox_execution'
  | 'security_evaluation'
  | 'guardrail_compilation'
  | 'verification'
  | 'completed'
  | 'failed';

export interface ToolParameter {
  name: string;
  type: string;
  description: string;
  required: boolean;
}

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: ToolParameter[];
}

export interface RAGRecord {
  id: string;
  title: string;
  content: string;
  is_sensitive?: boolean;
  is_poisoned?: boolean;
}

export interface RAGContext {
  domain_description: string;
  records: RAGRecord[];
  sensitive_fields: string[];
}

export interface AttackCase {
  id: number;
  category: AttackCategory;
  prompt: string;
  description?: string;
  target_rule?: string;
}

export interface ExecutionResult {
  attack_id: number;
  model_name: string;
  raw_response: string;
  latency_ms: number;
  status: string;
  tool_calls?: any[] | null;
  error?: string | null;
}

export interface EvaluationResult {
  attack_id: number;
  model_name: string;
  rule_violation: boolean;
  instruction_leakage: boolean;
  refusal_quality: number;
  reasoning: string;
  passed: boolean;
}

export interface HardenedPrompt {
  hardened_prompt: string;
  changes_made: string[];
  defensive_tags: string[];
  diff?: string;
}

export interface VerificationResult {
  attack_id: number;
  model_name: string;
  rule_violation: boolean;
  instruction_leakage: boolean;
  refusal_quality: number;
  reasoning: string;
  passed: boolean;
  before_passed: boolean;
}

export interface AuditRequest {
  system_prompt: string;
  business_rules: string[];
  target_models?: string[];
  tools?: ToolDefinition[];
  rag_context?: RAGContext;
  attack_count?: number;
}

export interface AuditSummary {
  audit_id: string;
  timestamp: string;
  original_prompt: string;
  hardened_prompt: string;
  business_rules: string[];
  initial_safety_score: number;
  post_safety_score: number;
  score_delta: number;
  total_attacks: number;
  initial_failed_count: number;
  post_failed_count: number;
  attacks: AttackCase[];
  initial_evaluations: EvaluationResult[];
  post_evaluations: VerificationResult[];
  hardening_changes: string[];
  defensive_diff?: string;
}

export interface SSEEvent {
  event: string;
  stage: NodeStage;
  progress: number;
  message: string;
  data?: any;
}
