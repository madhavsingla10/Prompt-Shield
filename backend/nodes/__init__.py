"""
PromptShield Arena Multi-Agent Framework
(Compatibility Layer mapping old node names to specialized Agents)
"""

from agents.attacker_agent import attacker_agent
from agents.sandbox_agent import sandbox_agent
from agents.evaluator_agent import evaluator_agent
from agents.compiler_agent import compiler_agent
from agents.verifier_agent import verifier_agent
from rag.synthetic_rag import generate_synthetic_rag_context

# Backward-compatible function aliases
generate_attacks = attacker_agent.generate_attacks
run_sandbox_tests = sandbox_agent.run_tests
evaluate_responses = evaluator_agent.evaluate_responses
compile_guardrails = compiler_agent.compile_guardrails
run_verification = verifier_agent.verify_hardening

__all__ = [
    "generate_attacks",
    "run_sandbox_tests",
    "evaluate_responses",
    "compile_guardrails",
    "run_verification",
    "generate_synthetic_rag_context"
]

