import asyncio
import time
from typing import List, Optional, Dict, Any
from config import settings
from schemas import AttackCase, ExecutionResult, ToolDefinition, RAGContext
from llm_client import llm_client

def _format_tools_for_llm(tools: Optional[List[ToolDefinition]]) -> Optional[List[Dict[str, Any]]]:
    """Converts ToolDefinition list into OpenAI-compatible tool schemas."""
    if not tools:
        return None

    formatted = []
    for tool in tools:
        properties = {}
        required_fields = []
        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.required:
                required_fields.append(param.name)

        formatted.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required_fields
                }
            }
        })
    return formatted

def _build_contextual_prompt(prompt: str, rag_context: Optional[RAGContext]) -> str:
    """Injects synthetic RAG documents into user query context if provided."""
    if not rag_context or not rag_context.records:
        return prompt

    docs_text = []
    for r in rag_context.records:
        docs_text.append(f"[Document ID: {r.id}] {r.title}:\n{r.content}")

    rag_block = (
        "=== RETRIEVED KNOWLEDGE CONTEXT ===\n"
        + "\n\n".join(docs_text)
        + "\n=== END KNOWLEDGE CONTEXT ===\n\n"
    )
    return f"{rag_block}User Query: {prompt}"

async def _execute_single_attack(
    attack: AttackCase,
    system_prompt: str,
    target_model: str,
    tools: Optional[List[ToolDefinition]],
    rag_context: Optional[RAGContext],
    semaphore: asyncio.Semaphore
) -> ExecutionResult:
    """Executes a single attack against a target model inside a concurrency-limited worker."""
    async with semaphore:
        formatted_tools = _format_tools_for_llm(tools)
        contextual_query = _build_contextual_prompt(attack.prompt, rag_context)

        res = await llm_client.generate(
            prompt=contextual_query,
            system_prompt=system_prompt,
            model=target_model,
            temperature=0.7,
            tools=formatted_tools
        )

        return ExecutionResult(
            attack_id=attack.id,
            model_name=target_model,
            raw_response=res.get("text", ""),
            latency_ms=res.get("latency_ms", 0.0),
            status=res.get("status", "success"),
            tool_calls=res.get("tool_calls"),
            error=res.get("error")
        )

async def run_sandbox_tests(
    system_prompt: str,
    attacks: List[AttackCase],
    target_models: Optional[List[str]] = None,
    tools: Optional[List[ToolDefinition]] = None,
    rag_context: Optional[RAGContext] = None,
    max_concurrency: int = 5
) -> List[ExecutionResult]:
    """
    Node 2: Multi-Model Sandbox Runner.
    Asynchronously executes adversarial payloads against target models in parallel.
    """
    models = target_models if target_models and len(target_models) > 0 else [settings.DEFAULT_TARGET_MODEL]
    semaphore = asyncio.Semaphore(max_concurrency)

    tasks = []
    for model_name in models:
        for attack in attacks:
            tasks.append(
                _execute_single_attack(
                    attack=attack,
                    system_prompt=system_prompt,
                    target_model=model_name,
                    tools=tools,
                    rag_context=rag_context,
                    semaphore=semaphore
                )
            )

    results: List[ExecutionResult] = await asyncio.gather(*tasks)
    return results
