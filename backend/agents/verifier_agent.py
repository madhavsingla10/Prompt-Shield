from typing import List, Optional, Tuple
from config import settings
from schemas import (
    AttackCase,
    EvaluationResult,
    VerificationResult,
    ToolDefinition,
    RAGContext
)
from .base_agent import BaseAgent
from .sandbox_agent import sandbox_agent
from .evaluator_agent import evaluator_agent

class VerifierAgent(BaseAgent):
    """
    Verification & Regression Testing Agent.
    Re-evaluates adversarial attacks against the hardened system prompt,
    benchmarks resilience against baseline metrics, and computes the safety delta.
    """

    def __init__(self):
        super().__init__(name="VerifierAgent")

    async def verify_hardening(
        self,
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
        Executes attacks against the hardened prompt and computes post-hardening score and delta.
        """
        self.log_section("Starting Hardening Verification & Regression Testing")
        self.log(f"Re-running {len(attacks)} attacks against compiled guardrails...")

        # 1. Execute against hardened prompt
        executions = await sandbox_agent.run_tests(
            system_prompt=hardened_prompt,
            attacks=attacks,
            target_models=target_models,
            tools=tools,
            rag_context=rag_context
        )

        # 2. Evaluate hardened executions
        post_evals, post_score = await evaluator_agent.evaluate_responses(
            system_prompt=hardened_prompt,
            business_rules=business_rules,
            attacks=attacks,
            executions=executions,
            rag_context=rag_context,
            model=evaluator_model
        )

        # 3. Calculate baseline initial score
        initial_passed = sum(1 for e in initial_evaluations if e.passed)
        initial_total = len(initial_evaluations) if initial_evaluations else 1
        initial_score = round((initial_passed / initial_total) * 100, 1)

        score_delta = round(post_score - initial_score, 1)

        # 4. Map verification results
        init_eval_map = {e.attack_id: e for e in initial_evaluations}
        verifications: List[VerificationResult] = []

        for pe in post_evals:
            init_eval = init_eval_map.get(pe.attack_id)
            before_passed = init_eval.passed if init_eval else False

            verifications.append(
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

        self.log(f"Verification Results: Initial Score: {initial_score}% -> Post Score: {post_score}% (Delta: {score_delta:+0.1f}%)")
        return verifications, post_score, score_delta

verifier_agent = VerifierAgent()
