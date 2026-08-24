from typing import List, Optional, Tuple, Dict, Any
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

async def run_verification(
    hardened_prompt: str,
    business_rules: List[str],
    attacks: List[AttackCase],
    initial_evaluations: List[EvaluationResult],
    target_models: Optional[List[str]] = None,
    tools: Optional[List[ToolDefinition]] = None,
    rag_context: Optional[RAGContext] = None,
    evaluator_model: Optional[str] = None
) -> Tuple[List[VerificationResult], float, float]:
    """
    Node 5: Verification & Diff Engine.
    Re-tests the hardened prompt against the identical attack suite and computes delta safety score.
    Returns: (verification_results, post_safety_score, score_delta)
    """
    # Map initial evaluations by attack_id
    initial_map: Dict[int, EvaluationResult] = {e.attack_id: e for e in initial_evaluations}

    # Re-run sandbox with hardened prompt
    post_executions = await run_sandbox_tests(
        system_prompt=hardened_prompt,
        attacks=attacks,
        target_models=target_models,
        tools=tools,
        rag_context=rag_context
    )

    # Re-evaluate responses
    post_evaluations, post_safety_score = await evaluate_responses(
        system_prompt=hardened_prompt,
        business_rules=business_rules,
        attacks=attacks,
        executions=post_executions,
        rag_context=rag_context,
        evaluator_model=evaluator_model
    )

    verification_results: List[VerificationResult] = []
    for pe in post_evaluations:
        initial_eval = initial_map.get(pe.attack_id)
        before_passed = initial_eval.passed if initial_eval else False

        verification_results.append(
            VerificationResult(
                attack_id=pe.attack_id,
                model_name=pe.model_name,
                rule_violation=pe.rule_violation,
                instruction_leakage=pe.instruction_leakage,
                refusal_quality=pe.refusal_quality,
                reasoning=pe.reasoning,
                passed=pe.passed,
                before_passed=before_passed
            )
        )

    # Compute initial score
    total_initial = len(initial_evaluations)
    initial_score = (
        round((sum(1 for e in initial_evaluations if e.passed) / total_initial) * 100.0, 1)
        if total_initial > 0
        else 0.0
    )

    score_delta = round(post_safety_score - initial_score, 1)

    return verification_results, post_safety_score, score_delta
