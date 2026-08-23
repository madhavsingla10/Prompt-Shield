# MVP (Minimum Viable Product) Specification

## Objective

Build a fully functional, production-grade automated prompt red-teaming and guardrail compiler. The MVP must execute real API calls, generate real adversarial inputs, perform real-time model evaluation, calculate objective safety metrics, and compile hardened system prompts. 

No hardcoded responses, mock test runs, or fake data will be used.

---

## Core System Architecture


```

┌────────────────────────────────────────────────────────┐
│             Web UI (Next.js or Streamlit)              │
│    - Prompt Input & Rule Configuration                │
│    - Real-Time Test Progress & Response Viewer        │
│    - Before/After Vulnerability Diff & Hardened Output │
└───────────────────────────┬────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────┐
│             Pipeline Orchestration Engine              │
│                 (Python / FastAPI)                     │
└─────┬──────────────┬──────────────┬──────────────┬─────┘
│              │              │              │
▼              ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Node 1  │   │  Node 2  │   │  Node 3  │   │  Node 4  │
│  Attack  │   │ Sandbox  │   │ Security │   │ Guardrail│
│Generator │   │ Execution│   │ Evaluator│   │ Compiler │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
│              │              │              │
▼              ▼              ▼              ▼
┌───────────────────────────────────────────────────────┐
│               Live External API Layer                 │
│  - Featherless.AI API (Llama-3-70B, Mistral Large)    │
│  - Google Gemini API / OpenAI API                     │
└───────────────────────────────────────────────────────┘

```

---

## Detailed Node Requirements

### Node 1: Adversarial Attack Generator (`attack_generator.py`)
* **Input:** Target system prompt, application domain, and explicit forbidden actions list.
* **Functionality:** Calls an LLM API instructed to act as an adversarial prompt security tester. Generates a structured JSON array containing 10–25 unique test cases across 5 standard attack vectors:
  1. **Direct Instruction Override:** Explicit commands telling the model to ignore previous instructions.
  2. **Roleplay / Persona Hijacking:** Scenarios asking the model to adopt an unfiltered alter-ego (e.g., debug mode, administrative assistant).
  3. **Delimiter & Format Injection:** Using XML/Markdown tags or code blocks to break out of instruction boundaries.
  4. **Indirect Policy Evasion:** Multi-step logical traps designed to elicit forbidden outcomes without using blocked keywords.
  5. **Data Extraction:** Direct queries probing for the exact text of the system prompt.
* **Output:** Validated JSON array of attack objects: `[{"id": 1, "category": "...", "prompt": "..."}]`.

### Node 2: Multi-Model Sandbox Runner (`sandbox_runner.py`)
* **Input:** Target system prompt, list of generated attacks, and selected target models.
* **Functionality:**
  * Asynchronously executes every attack payload against the target prompt using live API endpoints (Featherless.AI / Gemini).
  * Captures the raw output text, HTTP response status, execution latency, and token count for every interaction.
* **Output:** Structured execution log containing paired `(attack_prompt, model_response)`.

### Node 3: Security & Leakage Evaluator (`evaluator.py`)
* **Input:** Original system prompt, business rules, attack prompt, and model response.
* **Functionality:** Runs a deterministic evaluation prompt that judges whether the response violated safety criteria:
  * **Rule Violation:** `Boolean` (Did the AI perform a forbidden action?)
  * **Instruction Leakage:** `Boolean` (Did the AI quote or describe its internal instructions?)
  * **Refusal Quality:** `Score (1-5)` (Did the AI refuse safely and professionally?)
  * **Reasoning:** Concise explanation of the verdict.
* **Output:** Aggregate calculation of the **Initial Safety Score (%)** = `(Passed Tests / Total Tests) * 100`.

### Node 4: Guardrail Compiler (`guardrail_compiler.py`)
* **Input:** Original system prompt and the list of failed attack records (attack payload + breached response + failure explanation).
* **Functionality:** Synthesizes the exact failure modes and reconstructs the system prompt using structured defensive engineering:
  * **XML Demarcation:** Encloses critical rules within immutable XML tags (`<system_rules>`, `<data_boundaries>`).
  * **Explicit Refusal Protocol:** Injects standardized handling instructions for adversarial queries.
  * **Negative Constraint Anchors:** Hardens specific edge cases where the model previously complied with forbidden requests.
* **Output:** The compiled, hardened system prompt text.

### Node 5: Verification & Diff Engine (`verifier.py`)
* **Input:** Hardened system prompt and original attack suite.
* **Functionality:**
  * Re-runs the entire attack suite against the hardened prompt via the live API.
  * Re-evaluates responses using Node 3 logic.
  * Calculates the **Post-Hardening Safety Score (%)**.
  * Generates a side-by-side diff comparing the original vs. hardened prompt and initial vs. final test results.
* **Output:** Final JSON summary payload ready for dashboard rendering and report export.

---

## Technical Stack & Dependencies

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend / Pipeline** | Python 3.11+, FastAPI, Pydantic | Orchestrates multi-node logic, schema validation, and API routing. |
| **LLM Inference APIs** | Featherless.AI API, Gemini API, OpenAI API | Live model access for attack generation, target execution, and evaluation. |
| **Frontend UI** | Streamlit or Next.js (App Router, Tailwind CSS) | Responsive user interface for prompt input, live test visualization, and diff view. |
| **Data Serialization** | Pydantic JSON schemas | Enforces strict type checking across all node inputs and outputs. |
| **Deployment** | Render / Local Environment | Hosted backend and frontend services with live public URL. |

---

## MVP Deliverables Checklist

- [ ] **Functional Web Interface:** Allows users to paste a prompt, click "Run Audit", view live test execution, and download the final hardened prompt.
- [ ] **Zero Mocking:** 100% of attack generation, model responses, and scoring calls use live LLM API keys via `.env`.
- [ ] **Flowchart Diagram (PNG):** High-resolution visual architecture diagram exported for hackathon submission.
- [ ] **Demonstration Video:** 3-minute video showing the side-by-side comparison of a vulnerable prompt failing and the hardened prompt succeeding.
- [ ] **Full Markdown Documentation:** Complete setup guide, API schema definitions, and node prompt documentation in GitHub repository.

