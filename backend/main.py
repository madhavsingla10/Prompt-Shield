import os
import json
import uuid
import datetime
import asyncio
from typing import Dict, Any, List, AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from config import settings
from schemas import (
    AuditRequest,
    AuditSummary,
    NodeStage,
    SSEEvent,
    AttackCase,
    ExecutionResult,
    EvaluationResult,
    HardenedPrompt,
    VerificationResult
)
from llm_client import llm_client
from nodes import (
    generate_attacks,
    run_sandbox_tests,
    evaluate_responses,
    compile_guardrails,
    generate_prompt_diff,
    verify_hardened_prompt
)

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
    """
    Returns system status, active version, and configured LLM providers.
    """
    provider_status = llm_client.get_provider_status()
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
        }
    }

@app.get(f"{settings.API_PREFIX}/models")
async def list_models() -> Dict[str, Any]:
    """
    Returns supported target models and recommended pipeline configurations.
    """
    return {
        "supported_targets": settings.SUPPORTED_TARGET_MODELS,
        "defaults": {
            "attacker": settings.DEFAULT_ATTACKER_MODEL,
            "evaluator": settings.DEFAULT_EVALUATOR_MODEL,
            "compiler": settings.DEFAULT_COMPILER_MODEL,
            "target": settings.DEFAULT_TARGET_MODEL
        }
    }

async def execute_audit_pipeline(request: AuditRequest) -> AuditSummary:
    """
    Executes the complete 5-stage automated prompt red-teaming and guardrail compilation pipeline.
    """
    audit_id = f"audit_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Target models list
    target_models = request.target_models if request.target_models else [settings.DEFAULT_TARGET_MODEL]

    # --- Node 1: Adversarial Attack Generation ---
    attacks: List[AttackCase] = await generate_attacks(
        system_prompt=request.system_prompt,
        business_rules=request.business_rules,
        tools=request.tools,
        rag_context=request.rag_context,
        attack_count=request.attack_count
    )

    # --- Node 2: Multi-Model Sandbox Execution ---
    initial_executions: List[ExecutionResult] = await run_sandbox_tests(
        system_prompt=request.system_prompt,
        attacks=attacks,
        target_models=target_models,
        tools=request.tools,
        rag_context=request.rag_context,
        max_concurrency=settings.MAX_CONCURRENT_REQUESTS
    )

    # --- Node 3: Security & Leakage Evaluation ---
    initial_evaluations, initial_safety_score = await evaluate_responses(
        system_prompt=request.system_prompt,
        business_rules=request.business_rules,
        attacks=attacks,
        executions=initial_executions,
        rag_context=request.rag_context,
        max_concurrency=settings.MAX_CONCURRENT_REQUESTS
    )

    # --- Node 4: Guardrail Compilation ---
    hardened: HardenedPrompt = await compile_guardrails(
        system_prompt=request.system_prompt,
        business_rules=request.business_rules,
        evaluations=initial_evaluations,
        attacks=attacks,
        executions=initial_executions,
        tools=request.tools,
        rag_context=request.rag_context
    )

    # --- Node 5: Verification & Diff Engine ---
    verification_results, post_safety_score, score_delta, _ = await verify_hardened_prompt(
        hardened_prompt=hardened.hardened_prompt,
        original_prompt=request.system_prompt,
        business_rules=request.business_rules,
        attacks=attacks,
        initial_evaluations=initial_evaluations,
        initial_safety_score=initial_safety_score,
        target_models=target_models,
        tools=request.tools,
        rag_context=request.rag_context,
        max_concurrency=settings.MAX_CONCURRENT_REQUESTS
    )

    initial_failed_count = sum(1 for e in initial_evaluations if not e.passed)
    post_failed_count = sum(1 for v in verification_results if not v.passed)

    return AuditSummary(
        audit_id=audit_id,
        timestamp=timestamp,
        original_prompt=request.system_prompt,
        hardened_prompt=hardened.hardened_prompt,
        business_rules=request.business_rules,
        initial_safety_score=initial_safety_score,
        post_safety_score=post_safety_score,
        score_delta=score_delta,
        total_attacks=len(attacks),
        initial_failed_count=initial_failed_count,
        post_failed_count=post_failed_count,
        attacks=attacks,
        initial_evaluations=initial_evaluations,
        post_evaluations=verification_results,
        hardening_changes=hardened.changes_made,
        defensive_diff=hardened.diff
    )

@app.post(f"{settings.API_PREFIX}/audit", response_model=AuditSummary)
async def run_audit(request: AuditRequest) -> AuditSummary:
    """
    Synchronous / standard REST endpoint to trigger full prompt red-team audit and guardrail compilation.
    """
    try:
        summary = await execute_audit_pipeline(request)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit execution failed: {str(e)}")

async def audit_event_generator(request: AuditRequest) -> AsyncGenerator[str, None]:
    """
    Generates real-time Server-Sent Events (SSE) representing each stage of the security audit.
    """
    audit_id = f"audit_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    target_models = request.target_models if request.target_models else [settings.DEFAULT_TARGET_MODEL]

    def format_sse(stage: NodeStage, progress: float, message: str, data: Any = None) -> str:
        payload = {
            "event": "update",
            "stage": stage.value,
            "progress": round(progress, 2),
            "message": message,
            "data": data
        }
        return f"data: {json.dumps(payload)}\n\n"

    try:
        # 1. Initializing
        yield format_sse(
            NodeStage.INITIALIZING,
            0.05,
            f"Initializing red-team audit pipeline [{audit_id}]...",
            {"audit_id": audit_id, "timestamp": timestamp}
        )
        await asyncio.sleep(0.1)

        # 2. Node 1: Attack Generation
        yield format_sse(
            NodeStage.ATTACK_GENERATION,
            0.15,
            f"Generating {request.attack_count} adversarial test cases across 5 injection categories..."
        )
        attacks: List[AttackCase] = await generate_attacks(
            system_prompt=request.system_prompt,
            business_rules=request.business_rules,
            tools=request.tools,
            rag_context=request.rag_context,
            attack_count=request.attack_count
        )
        yield format_sse(
            NodeStage.ATTACK_GENERATION,
            0.30,
            f"Generated {len(attacks)} adversarial attack payloads.",
            {"attacks": [a.model_dump() for a in attacks]}
        )
        await asyncio.sleep(0.1)

        # 3. Node 2: Sandbox Execution
        yield format_sse(
            NodeStage.SANDBOX_EXECUTION,
            0.40,
            f"Executing {len(attacks)} payloads against {len(target_models)} target model(s) in parallel sandbox..."
        )
        initial_executions: List[ExecutionResult] = await run_sandbox_tests(
            system_prompt=request.system_prompt,
            attacks=attacks,
            target_models=target_models,
            tools=request.tools,
            rag_context=request.rag_context,
            max_concurrency=settings.MAX_CONCURRENT_REQUESTS
        )
        yield format_sse(
            NodeStage.SANDBOX_EXECUTION,
            0.55,
            f"Sandbox execution finished for {len(initial_executions)} model interactions.",
            {"executions_count": len(initial_executions)}
        )
        await asyncio.sleep(0.1)

        # 4. Node 3: Security & Leakage Evaluation
        yield format_sse(
            NodeStage.SECURITY_EVALUATION,
            0.65,
            "Evaluating model responses for rule violations and instruction leakage..."
        )
        initial_evaluations, initial_safety_score = await evaluate_responses(
            system_prompt=request.system_prompt,
            business_rules=request.business_rules,
            attacks=attacks,
            executions=initial_executions,
            rag_context=request.rag_context,
            max_concurrency=settings.MAX_CONCURRENT_REQUESTS
        )
        initial_failed = sum(1 for e in initial_evaluations if not e.passed)
        yield format_sse(
            NodeStage.SECURITY_EVALUATION,
            0.75,
            f"Initial evaluation complete. Safety Score: {initial_safety_score}% ({initial_failed} breaches detected).",
            {
                "initial_safety_score": initial_safety_score,
                "initial_failed_count": initial_failed,
                "evaluations": [e.model_dump() for e in initial_evaluations]
            }
        )
        await asyncio.sleep(0.1)

        # 5. Node 4: Guardrail Compilation
        yield format_sse(
            NodeStage.GUARDRAIL_COMPILATION,
            0.80,
            "Synthesizing failure modes and compiling hardened system prompt with XML boundaries..."
        )
        hardened: HardenedPrompt = await compile_guardrails(
            system_prompt=request.system_prompt,
            business_rules=request.business_rules,
            evaluations=initial_evaluations,
            attacks=attacks,
            executions=initial_executions,
            tools=request.tools,
            rag_context=request.rag_context
        )
        yield format_sse(
            NodeStage.GUARDRAIL_COMPILATION,
            0.90,
            "Guardrail compiler generated hardened system prompt.",
            {
                "hardened_prompt": hardened.hardened_prompt,
                "changes_made": hardened.changes_made,
                "defensive_tags": hardened.defensive_tags,
                "diff": hardened.diff
            }
        )
        await asyncio.sleep(0.1)

        # 6. Node 5: Verification & Diff Engine
        yield format_sse(
            NodeStage.VERIFICATION,
            0.95,
            "Re-testing hardened prompt against the attack suite to verify patch resilience..."
        )
        verification_results, post_safety_score, score_delta, _ = await verify_hardened_prompt(
            hardened_prompt=hardened.hardened_prompt,
            original_prompt=request.system_prompt,
            business_rules=request.business_rules,
            attacks=attacks,
            initial_evaluations=initial_evaluations,
            initial_safety_score=initial_safety_score,
            target_models=target_models,
            tools=request.tools,
            rag_context=request.rag_context,
            max_concurrency=settings.MAX_CONCURRENT_REQUESTS
        )
        post_failed = sum(1 for v in verification_results if not v.passed)

        # 7. Completed Summary
        summary = AuditSummary(
            audit_id=audit_id,
            timestamp=timestamp,
            original_prompt=request.system_prompt,
            hardened_prompt=hardened.hardened_prompt,
            business_rules=request.business_rules,
            initial_safety_score=initial_safety_score,
            post_safety_score=post_safety_score,
            score_delta=score_delta,
            total_attacks=len(attacks),
            initial_failed_count=initial_failed,
            post_failed_count=post_failed,
            attacks=attacks,
            initial_evaluations=initial_evaluations,
            post_evaluations=verification_results,
            hardening_changes=hardened.changes_made,
            defensive_diff=hardened.diff
        )

        yield format_sse(
            NodeStage.COMPLETED,
            1.0,
            f"Audit finished successfully. Safety score improved by +{score_delta}% (New Score: {post_safety_score}%).",
            summary.model_dump()
        )

    except Exception as e:
        yield format_sse(
            NodeStage.FAILED,
            1.0,
            f"Pipeline failed with error: {str(e)}",
            {"error": str(e)}
        )

@app.post(f"{settings.API_PREFIX}/audit/stream")
async def stream_audit(request: AuditRequest):
    """
    Streaming Server-Sent Events (SSE) endpoint providing real-time live execution progress.
    """
    return StreamingResponse(
        audit_event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
