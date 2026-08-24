import asyncio
from typing import List, Optional, Tuple, Dict, Any
from config import settings
from schemas import (
    AttackCase,
    ExecutionResult,
    EvaluationResult,
    VerificationResult,
    ToolDefinition,
    RAGContext
)
from .sandbox_runner import run_sandbox_tests
from .evaluator import evaluate_responses

async def verify_hardened_prompt(
    hardened_prompt: str,
    original_prompt: str,
    business_rules: List[str],
    attacks: List[AttackCase],
    initial_evaluations: List[EvaluationResult],
    initial_safety_score: float,
    target_models: Optional[List[str]] = None,
    tools: Optional[List[ToolDefinition]] = None,
    rag_context: Optional[RAGContext] = None,
    evaluator_model: Optional[str] = None,
    max_concurrency: int = 5
) -> Tuple[List[VerificationResult], float, float, List[ExecutionResult]]:
    """
    Node 5: Verification & Diff Engine.
    Re-tests the compiled hardened prompt against the identical adversarial attack suite,
    evaluates safety improvement, and pairs initial vs post-hardening verdicts.
    """
    # 1. Execute attack suite against hardened prompt in sandbox
    post_executions = await run_sandbox_tests(
        system_prompt=hardened_prompt,
        attacks=attacks,
        target_models=target_models,
        tools=tools,
        rag_context=rag_context,
        max_concurrency=max_concurrency
    )

    # 2. Evaluate post-hardening model responses with evaluator judge
    post_evaluations, post_safety_score = await evaluate_responses(
        system_prompt=hardened_prompt,
        business_rules=business_rules,
        attacks=attacks,
        executions=post_executions,
        rag_context=rag_context,
        evaluator_model=evaluator_model,
        max_concurrency=max_concurrency
    )

    # 3. Build lookup of initial evaluation statuses
    # Map (attack_id, model_name) -> initial passed boolean
    initial_passed_map: Dict[Tuple[int, str], bool] = {
        (e.attack_id, e.model_name): e.passed for e in initial_evaluations
    }

    # 4. Assemble VerificationResult list
    verification_results: List[VerificationResult] = []
    for post_eval in post_evaluations:
        before_passed = initial_passed_map.get(
            (post_eval.attack_id, post_eval.model_name),
            False
        )
        verification_results.append(
            VerificationResult(
                attack_id=post_eval.attack_id,
                model_name=post_eval.model_name,
                rule_violation=post_eval.rule_violation,
                instruction_leakage=post_eval.instruction_leakage,
                refusal_quality=post_eval.refusal_quality,
                reasoning=post_eval.reasoning,
                passed=post_eval.passed,
                before_passed=before_passed
            )
        )

    # 5. Compute improvement delta
    score_delta = round(post_safety_score - initial_safety_score, 1)

    return verification_results, post_safety_score, score_delta, post_executions
