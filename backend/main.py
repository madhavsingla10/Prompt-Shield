import os
import json
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from config import settings
from schemas import (
    AuditRequest,
    AuditSummary,
    NodeStage,
    SSEEvent,
    RAGContext,
    HardenedPrompt
)
from services import llm_service, diff_service
from agents import (
    attacker_agent,
    sandbox_agent,
    evaluator_agent,
    compiler_agent,
    verifier_agent
)
from rag import vector_store_manager, generate_synthetic_rag_context

logger = logging.getLogger("PromptShieldArena")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Automated Prompt Red-Teaming, Security Evaluation & Guardrail Compiler Engine"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }

@app.get(f"{settings.API_PREFIX}/health")
async def health_check() -> Dict[str, Any]:
    """Returns system status, active version, configured LLM providers, and vector store readiness."""
    provider_status = llm_service.get_provider_status()
    any_provider_configured = any(p.get("configured") for p in provider_status.values())

    return {
        "status": "healthy" if any_provider_configured else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "providers": provider_status,
        "models": {
            "default_attacker": settings.DEFAULT_ATTACKER_MODEL,
            "default_evaluator": settings.DEFAULT_EVALUATOR_MODEL,
            "default_compiler": settings.DEFAULT_COMPILER_MODEL,
            "default_target": settings.DEFAULT_TARGET_MODEL
        },
        "vector_store": {
            "persist_dir": settings.VECTOR_DB_DIR
        }
    }

@app.get(f"{settings.API_PREFIX}/models")
async def list_models() -> Dict[str, Any]:
    """Returns supported target models and recommended pipeline configurations."""
    return {
        "supported_targets": settings.SUPPORTED_TARGET_MODELS,
        "defaults": {
            "attacker": settings.DEFAULT_ATTACKER_MODEL,
            "evaluator": settings.DEFAULT_EVALUATOR_MODEL,
            "compiler": settings.DEFAULT_COMPILER_MODEL,
            "target": settings.DEFAULT_TARGET_MODEL
        }
    }

@app.post(f"{settings.API_PREFIX}/rag/generate", response_model=RAGContext)
async def generate_rag_endpoint(payload: Dict[str, Any]) -> RAGContext:
    """Helper endpoint to generate synthetic knowledge records with sensitive honeypots and index into vector store."""
    domain_description = payload.get("domain_description", "Customer Service Knowledge Base")
    sensitive_fields = payload.get("sensitive_fields", [])
    rag_context = await generate_synthetic_rag_context(
        domain_description=domain_description,
        sensitive_fields=sensitive_fields
    )

    # Index into ChromaDB vector store
    vector_store_manager.index_rag_context(rag_context)

    return rag_context

@app.post(f"{settings.API_PREFIX}/audit", response_model=AuditSummary)
async def execute_audit_pipeline(req: AuditRequest) -> AuditSummary:
    """
    Executes the full 5-agent security audit and prompt hardening pipeline synchronously.
    """
    audit_id = f"audit_{uuid.uuid4().hex[:12]}"
    timestamp = datetime.now(timezone.utc).isoformat()
    target_models = req.target_models if req.target_models else [settings.DEFAULT_TARGET_MODEL]

    # Index RAG context into vector store if provided
    if req.rag_context:
        vector_store_manager.index_rag_context(req.rag_context)

    # 1. AttackerAgent: Generate Adversarial Attacks
    attacks = await attacker_agent.generate_attacks(
        system_prompt=req.system_prompt,
        business_rules=req.business_rules,
        tools=req.tools,
        rag_context=req.rag_context,
        attack_count=req.attack_count
    )

    # 2. SandboxAgent: Multi-Model Sandbox Runner
    executions = await sandbox_agent.run_tests(
        system_prompt=req.system_prompt,
        attacks=attacks,
        target_models=target_models,
        tools=req.tools,
        rag_context=req.rag_context
    )

    # 3. EvaluatorAgent: Security & Leakage Evaluator
    initial_evals, initial_score = await evaluator_agent.evaluate_responses(
        system_prompt=req.system_prompt,
        business_rules=req.business_rules,
        attacks=attacks,
        executions=executions,
        rag_context=req.rag_context
    )

    # Collect failed attacks for compiler
    failed_attacks = []
    attack_map = {a.id: a for a in attacks}
    exec_map = {e.attack_id: e for e in executions}

    for ev in initial_evals:
        if not ev.passed:
            att = attack_map.get(ev.attack_id)
            exc = exec_map.get(ev.attack_id)
            failed_attacks.append({
                "prompt": att.prompt if att else "",
                "response": exc.raw_response if exc else "",
                "reasoning": ev.reasoning
            })

    # 4. CompilerAgent: Guardrail Compiler
    hardened = await compiler_agent.compile_guardrails(
        original_prompt=req.system_prompt,
        business_rules=req.business_rules,
        failed_attacks=failed_attacks
    )

    # 5. VerifierAgent: Verification & Diff Engine
    verifications, post_score, score_delta = await verifier_agent.verify_hardening(
        hardened_prompt=hardened.hardened_prompt,
        business_rules=req.business_rules,
        attacks=attacks,
        initial_evaluations=initial_evals,
        target_models=target_models,
        tools=req.tools,
        rag_context=req.rag_context
    )

    initial_failed_count = sum(1 for e in initial_evals if not e.passed)
    post_failed_count = sum(1 for v in verifications if not v.passed)

    return AuditSummary(
        audit_id=audit_id,
        timestamp=timestamp,
        original_prompt=req.system_prompt,
        hardened_prompt=hardened.hardened_prompt,
        business_rules=req.business_rules,
        initial_safety_score=initial_score,
        post_safety_score=post_score,
        score_delta=score_delta,
        total_attacks=len(attacks),
        initial_failed_count=initial_failed_count,
        post_failed_count=post_failed_count,
        attacks=attacks,
        initial_evaluations=initial_evals,
        post_evaluations=verifications,
        hardening_changes=hardened.changes_made,
        defensive_diff=hardened.diff
    )

@app.post(f"{settings.API_PREFIX}/audit/stream")
async def stream_audit_pipeline(req: AuditRequest):
    """
    Executes the 5-agent audit pipeline streaming real-time Server-Sent Events (SSE) to the frontend.
    """
    async def event_generator():
        audit_id = f"audit_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        target_models = req.target_models if req.target_models else [settings.DEFAULT_TARGET_MODEL]

        # Step 0: Initializing
        init_event = SSEEvent(
            stage=NodeStage.INITIALIZING,
            progress=0.05,
            message="Initializing PromptShield Arena Agentic Audit Pipeline...",
            data={"audit_id": audit_id}
        )
        yield {"event": "status", "data": init_event.model_dump_json()}

        # Index RAG context if present
        if req.rag_context:
            vector_store_manager.index_rag_context(req.rag_context)

        # Agent 1: AttackerAgent
        yield {"event": "status", "data": SSEEvent(
            stage=NodeStage.ATTACK_GENERATION,
            progress=0.15,
            message="AttackerAgent: Synthesizing adversarial attack suite across 5 injection vectors..."
        ).model_dump_json()}

        attacks = await attacker_agent.generate_attacks(
            system_prompt=req.system_prompt,
            business_rules=req.business_rules,
            tools=req.tools,
            rag_context=req.rag_context,
            attack_count=req.attack_count
        )

        yield {"event": "attacks_ready", "data": json.dumps([a.model_dump() for a in attacks])}

        # Agent 2: SandboxAgent
        yield {"event": "status", "data": SSEEvent(
            stage=NodeStage.SANDBOX_EXECUTION,
            progress=0.35,
            message=f"SandboxAgent: Executing {len(attacks)} attacks in parallel across target sandbox..."
        ).model_dump_json()}

        executions = await sandbox_agent.run_tests(
            system_prompt=req.system_prompt,
            attacks=attacks,
            target_models=target_models,
            tools=req.tools,
            rag_context=req.rag_context
        )

        # Agent 3: EvaluatorAgent
        yield {"event": "status", "data": SSEEvent(
            stage=NodeStage.SECURITY_EVALUATION,
            progress=0.55,
            message="EvaluatorAgent: Deterministically evaluating model outputs and calculating initial safety score..."
        ).model_dump_json()}

        initial_evals, initial_score = await evaluator_agent.evaluate_responses(
            system_prompt=req.system_prompt,
            business_rules=req.business_rules,
            attacks=attacks,
            executions=executions,
            rag_context=req.rag_context
        )

        yield {"event": "initial_eval_ready", "data": json.dumps({
            "initial_safety_score": initial_score,
            "evaluations": [e.model_dump() for e in initial_evals]
        })}

        # Collect failed attacks
        failed_attacks = []
        attack_map = {a.id: a for a in attacks}
        exec_map = {e.attack_id: e for e in executions}
        for ev in initial_evals:
            if not ev.passed:
                att = attack_map.get(ev.attack_id)
                exc = exec_map.get(ev.attack_id)
                failed_attacks.append({
                    "prompt": att.prompt if att else "",
                    "response": exc.raw_response if exc else "",
                    "reasoning": ev.reasoning
                })

        # Agent 4: CompilerAgent
        yield {"event": "status", "data": SSEEvent(
            stage=NodeStage.GUARDRAIL_COMPILATION,
            progress=0.75,
            message="CompilerAgent: Compiling hardened system prompt with structural XML demarcations and refusal anchors..."
        ).model_dump_json()}

        hardened = await compiler_agent.compile_guardrails(
            original_prompt=req.system_prompt,
            business_rules=req.business_rules,
            failed_attacks=failed_attacks
        )

        yield {"event": "hardened_prompt_ready", "data": hardened.model_dump_json()}

        # Agent 5: VerifierAgent
        yield {"event": "status", "data": SSEEvent(
            stage=NodeStage.VERIFICATION,
            progress=0.90,
            message="VerifierAgent: Re-running adversarial attack suite against hardened prompt to verify safety gains..."
        ).model_dump_json()}

        verifications, post_score, score_delta = await verifier_agent.verify_hardening(
            hardened_prompt=hardened.hardened_prompt,
            business_rules=req.business_rules,
            attacks=attacks,
            initial_evaluations=initial_evals,
            target_models=target_models,
            tools=req.tools,
            rag_context=req.rag_context
        )

        initial_failed_count = sum(1 for e in initial_evals if not e.passed)
        post_failed_count = sum(1 for v in verifications if not v.passed)

        summary = AuditSummary(
            audit_id=audit_id,
            timestamp=timestamp,
            original_prompt=req.system_prompt,
            hardened_prompt=hardened.hardened_prompt,
            business_rules=req.business_rules,
            initial_safety_score=initial_score,
            post_safety_score=post_score,
            score_delta=score_delta,
            total_attacks=len(attacks),
            initial_failed_count=initial_failed_count,
            post_failed_count=post_failed_count,
            attacks=attacks,
            initial_evaluations=initial_evals,
            post_evaluations=verifications,
            hardening_changes=hardened.changes_made,
            defensive_diff=hardened.diff
        )

        # Final completion event
        yield {"event": "completed", "data": summary.model_dump_json()}

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )

