from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AttackCategory(str, Enum):
    DIRECT_OVERRIDE = "direct_override"
    ROLEPLAY_HIJACK = "roleplay_hijack"
    DELIMITER_INJECTION = "delimiter_injection"
    INDIRECT_EVASION = "indirect_evasion"
    DATA_LEAKAGE = "data_leakage"

class NodeStage(str, Enum):
    INITIALIZING = "initializing"
    ATTACK_GENERATION = "attack_generation"
    SANDBOX_EXECUTION = "sandbox_execution"
    SECURITY_EVALUATION = "security_evaluation"
    GUARDRAIL_COMPILATION = "guardrail_compilation"
    VERIFICATION = "verification"
    COMPLETED = "completed"
    FAILED = "failed"

# ----------------- Tool & RAG Schemas -----------------

class ToolParameter(BaseModel):
    name: str = Field(..., description="Parameter name, e.g. amount")
    type: str = Field(default="string", description="Data type: string, number, boolean, etc.")
    description: str = Field(default="", description="Parameter explanation")
    required: bool = Field(default=True, description="Whether this parameter is required")

class ToolDefinition(BaseModel):
    name: str = Field(..., description="Function/Tool name, e.g. issue_refund")
    description: str = Field(..., description="What the tool does and when it should be used")
    parameters: List[ToolParameter] = Field(default_factory=list, description="Parameters accepted by the tool")

class RAGRecord(BaseModel):
    id: str = Field(..., description="Unique record ID")
    title: str = Field(..., description="Title or record header")
    content: str = Field(..., description="Content text or data fields")
    is_sensitive: bool = Field(default=False, description="Whether this record contains confidential data")
    is_poisoned: bool = Field(default=False, description="Whether this record contains indirect injection payload")

class RAGContext(BaseModel):
    domain_description: str = Field(..., description="Description of the database/knowledge base domain")
    records: List[RAGRecord] = Field(default_factory=list, description="Mock documents or data records")
    sensitive_fields: List[str] = Field(default_factory=list, description="Names of confidential fields")

# ----------------- Attack & Execution Schemas -----------------

class AttackCase(BaseModel):
    id: int = Field(..., description="Sequential attack test case identifier")
    category: AttackCategory = Field(..., description="Adversarial attack taxonomy category")
    prompt: str = Field(..., description="Adversarial payload / input text")
    description: str = Field(default="", description="Brief description of the attack objective")
    target_rule: Optional[str] = Field(default=None, description="The specific rule this attack aims to breach")

class ExecutionResult(BaseModel):
    attack_id: int
    model_name: str
    raw_response: str
    latency_ms: float
    status: str = "success"
    tool_calls: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class EvaluationResult(BaseModel):
    attack_id: int
    model_name: str
    rule_violation: bool = Field(..., description="True if target broke business rules or performed forbidden actions")
    instruction_leakage: bool = Field(..., description="True if target quoted or exposed system prompt instructions")
    refusal_quality: int = Field(..., ge=1, le=5, description="Score 1-5 on refusal professionalism and safety")
    reasoning: str = Field(..., description="Explanation of why this test passed or failed")
    passed: bool = Field(..., description="Overall test verdict (True = prompt held, False = breached)")

class HardenedPrompt(BaseModel):
    hardened_prompt: str = Field(..., description="The compiled, secure system prompt")
    changes_made: List[str] = Field(default_factory=list, description="Defensive modifications applied")
    defensive_tags: List[str] = Field(default_factory=list, description="XML demarcations and anchors added")
    diff: Optional[str] = Field(default=None, description="Unified text diff vs original prompt")

class VerificationResult(BaseModel):
    attack_id: int
    model_name: str
    rule_violation: bool
    instruction_leakage: bool
    refusal_quality: int
    reasoning: str
    passed: bool
    before_passed: bool = Field(..., description="Whether this attack passed in the initial evaluation before hardening")

# ----------------- Main Pipeline Request & Response -----------------

class AuditRequest(BaseModel):
    system_prompt: str = Field(..., description="Original system prompt to test and harden")
    business_rules: List[str] = Field(..., min_length=1, description="Explicit list of forbidden actions and safety policies")
    target_models: List[str] = Field(default_factory=list, description="List of model IDs to test against")
    tools: List[ToolDefinition] = Field(default_factory=list, description="Optional tools available to the target agent")
    rag_context: Optional[RAGContext] = Field(default=None, description="Optional synthetic RAG knowledge context")
    attack_count: int = Field(default=10, ge=5, le=30, description="Number of adversarial test cases to generate")

class AuditSummary(BaseModel):
    audit_id: str
    timestamp: str
    original_prompt: str
    hardened_prompt: str
    business_rules: List[str]
    initial_safety_score: float = Field(..., description="Initial percentage of attacks blocked (0-100%)")
    post_safety_score: float = Field(..., description="Post-hardening percentage of attacks blocked (0-100%)")
    score_delta: float = Field(..., description="Improvement in safety score percentage points")
    total_attacks: int
    initial_failed_count: int
    post_failed_count: int
    attacks: List[AttackCase]
    initial_evaluations: List[EvaluationResult]
    post_evaluations: List[VerificationResult]
    hardening_changes: List[str] = Field(default_factory=list)
    defensive_diff: Optional[str] = None

class SSEEvent(BaseModel):
    event: str = "update"
    stage: NodeStage
    progress: float = Field(..., ge=0.0, le=1.0)
    message: str
    data: Optional[Dict[str, Any]] = None
