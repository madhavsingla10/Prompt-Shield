# PromptShield Arena: Planned Repository Structure

This document outlines the planned directory layout and file structure for the **PromptShield Arena** workspace. It is structured into a Python FastAPI backend and a Next.js/Streamlit frontend.

---

## Workspace Directory Tree

```text
PromptShield Arena/
├── backend/
│   ├── requirements.txt            # Python dependencies (FastAPI, Pydantic, etc.)
│   ├── .env.example                # Template for environment variables (API keys)
│   ├── main.py                     # FastAPI server and pipeline orchestrator
│   ├── config.py                   # App configurations (LLM models, API configurations)
│   ├── schemas.py                  # Pydantic schemas for request/response serialization
│   └── nodes/
│       ├── __init__.py
│       ├── attack_generator.py     # Node 1: Generates tricky queries based on rules, tools, & RAG
│       ├── sandbox_runner.py       # Node 2: Runs queries asynchronously with mock tools
│       ├── evaluator.py            # Node 3: Inspects answers for rule breaches or data leaks
│       ├── guardrail_compiler.py   # Node 4: Compiles a hardened, secure system prompt
│       └── verifier.py             # Node 5: Re-tests the hardened prompt & computes score change
│
├── frontend/                       # Option A: Premium Next.js Frontend
│   ├── package.json                # npm dependencies (Tailwind, Lucide, Framer Motion)
│   ├── tailwind.config.js          # Custom theme styles (glassmorphism/dark mode)
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          # Global template & font configurations
│   │   │   └── page.tsx            # Main interactive security playground dashboard
│   │   └── components/
│   │       ├── PromptForm.tsx      # Rules, Prompts, Tools & RAG inputs
│   │       ├── LiveConsole.tsx     # Terminal-style output for active simulations
│   │       └── DiffViewer.tsx      # Side-by-side comparison of old vs. new prompts
│
└── README.md                       # Project setup, overview, and usage instructions
```

---

## Detailed File Responsibilities

### 1. Backend Layer (`backend/`)

*   **`main.py`**
    *   Hosts the FastAPI web server.
    *   Exposes endpoints such as `/api/audit` (runs the whole Node 1-5 pipeline) and `/api/health`.
*   **`schemas.py`**
    *   Defines structured data models, including:
        *   `ToolDefinition`: Name, description, and parameter specifications.
        *   `RAGContext`: Synthetic database descriptions and sample structures.
        *   `AuditRequest`: The user's system prompt, rules, selected target LLMs, tools, and RAG metadata.
        *   `AuditResponse`: Detailed logs, scores (initial vs. post-hardening), and the final compiled prompt.
*   **`nodes/attack_generator.py`**
    *   Constructs prompt engineering templates to command a security LLM to think like an adversary.
    *   Generates a JSON list of specialized injection payloads tailored to trigger the user's defined mock tools or leak simulated RAG tables.
*   **`nodes/sandbox_runner.py`**
    *   Coordinates parallel async HTTP requests using `httpx` to targets (Gemini, Llama 3, etc.).
    *   Mocks function-calling formats by injecting tool descriptions into the LLM target's API schema.
*   **`nodes/evaluator.py`**
    *   Queries a high-intelligence evaluator LLM to judge if the agent responses violated boundaries (e.g., agreed to generate an unauthorized coupon or printed secret database fields).
*   **`nodes/guardrail_compiler.py`**
    *   Assembles the hardened system prompt by programmatically inserting defensive anchors, refuse protocols, and XML tags around weak parameters.
*   **`nodes/verifier.py`**
    *   Sends the newly hardened system prompt back to `sandbox_runner` to repeat the exact test suite, ensuring the vulnerabilities are verified as resolved.

---

## 2. Frontend Layer (`frontend/`)

We recommend using **Next.js** with React to build a premium, wow-factor dashboard:
*   **Prompt Input Section:** Clean textareas for the System Prompt, coupled with dynamic forms where users can add/remove Tools (defining parameters) and RAG profiles.
*   **Real-Time Log Stream:** Interactive step-by-step terminal outputs showing Node 1 to Node 5 executing live.
*   **Before/After Diff Panel:** A visual side-by-side comparison highlighting exact text insertions made by the Guardrail Compiler.
