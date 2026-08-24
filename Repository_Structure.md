# PromptShield Arena: Repository Structure

This document outlines the directory layout and architecture for the **PromptShield Arena** workspace, built following the **`llm_engineering`** multi-agent framework patterns.

---

## Workspace Directory Tree

```text
PromptShield Arena/
├── backend/
│   ├── requirements.txt            # Python dependencies (FastAPI, tenacity, chromadb, etc.)
│   ├── .env.example                # Template for environment variables (API keys)
│   ├── main.py                     # FastAPI server and multi-agent SSE orchestrator
│   ├── config.py                   # Typed configuration with load_dotenv(override=True)
│   ├── schemas.py                  # Pydantic v2 schemas and validation models
│   ├── agents/                     # Multi-Agent Framework (llm_engineering pattern)
│   │   ├── __init__.py             # Agent registry exports
│   │   ├── base_agent.py           # BaseAgent with ANSI color logging & telemetry
│   │   ├── attacker_agent.py       # Red-Teaming & adversarial attack generator
│   │   ├── sandbox_agent.py        # Multi-model sandbox runner with concurrency & tool simulation
│   │   ├── evaluator_agent.py      # LLM-as-a-Judge security & leakage evaluator
│   │   ├── compiler_agent.py       # Guardrail compiler & XML prompt hardening architect
│   │   └── verifier_agent.py       # Verification diff & regression evaluation agent
│   ├── rag/                        # RAG & Vector Knowledge Base
│   │   ├── __init__.py             # RAG exports
│   │   ├── vector_store.py         # ChromaDB vector store with in-memory fallback
│   │   └── synthetic_rag.py        # Synthetic knowledge base & honeypot generator
│   ├── services/                   # Core Infrastructure Services
│   │   ├── __init__.py             # Service exports
│   │   ├── llm_service.py          # Unified LLM service with Tenacity exponential retries
│   │   └── diff_service.py         # Prompt diff generator & XML tag inspector
│   └── nodes/                      # Compatibility layer mapping to backend/agents/ & rag/
│       └── __init__.py             # Node aliases (generate_attacks, run_sandbox_tests, etc.)
│
├── frontend/                       # Next.js Frontend Dashboard
│   ├── package.json                # npm dependencies (Tailwind, Lucide, Framer Motion)
│   ├── tailwind.config.js          # Custom theme styles (glassmorphism/dark mode)
│   └── src/
│       ├── app/
│       │   ├── layout.tsx          # Global template & font configurations
│       │   └── page.tsx            # Interactive security playground dashboard
│       └── components/
│           ├── PromptForm.tsx      # Rules, Prompts, Tools & RAG inputs
│           ├── LiveConsole.tsx     # Real-time SSE streaming agent console
│           └── DiffViewer.tsx      # Side-by-side comparison of original vs. hardened prompt
│
└── README.md                       # Project setup, overview, and usage instructions
```

---

## Detailed Backend Responsibilities

### 1. Multi-Agent Framework (`backend/agents/`)
*   **`base_agent.py`**: Abstract `BaseAgent` featuring ANSI color-coded console logs (`\033[...]`) matching `llm_engineering/week8`, timestamps, and lifecycle logging.
*   **`attacker_agent.py`**: Generates adversarial test cases across 5 attack vectors (*direct_override*, *roleplay_hijack*, *delimiter_injection*, *indirect_evasion*, *data_leakage*).
*   **`sandbox_agent.py`**: Executes test suites across target models in parallel, binds function-calling schemas, and simulates mock tools.
*   **`evaluator_agent.py`**: Objective LLM-as-a-Judge evaluating rule violations, instruction leakage, and refusal quality (1–5 scale).
*   **`compiler_agent.py`**: Synthesizes XML boundary encapsulation (`<system_instructions>`, `<immutable_security_boundaries>`), precedence rules, and refusal anchors.
*   **`verifier_agent.py`**: Runs regression testing against hardened prompts, calculating safety score deltas.

### 2. RAG & Vector Knowledge Base (`backend/rag/`)
*   **`vector_store.py`**: ChromaDB vector indexer with in-memory fallback for semantic search and poisoned document detection.
*   **`synthetic_rag.py`**: Generates realistic domain documentation with embedded confidential honeypots and indirect injection payloads.

### 3. Services Layer (`backend/services/`)
*   **`llm_service.py`**: Unified asynchronous LLM client with `tenacity` exponential backoff retries (`wait_exponential`, `stop_after_attempt`).
*   **`diff_service.py`**: Generates unified diffs and inspects XML security tags.

### 4. Compatibility Layer (`backend/nodes/`)
*   Provides backward-compatible function aliases (`generate_attacks`, `run_sandbox_tests`, `evaluate_responses`, `compile_guardrails`, `run_verification`) delegating to the agent framework.

