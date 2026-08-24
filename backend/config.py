import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables with override=True following llm_engineering conventions
load_dotenv(override=True)

class Settings:
    # Service Information
    PROJECT_NAME: str = "PromptShield Arena"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"

    # API Keys & Endpoints
    FEATHERLESS_API_KEY: str = os.getenv("FEATHERLESS_API_KEY", "")
    FEATHERLESS_BASE_URL: str = os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    # Default Pipeline Model Roles
    DEFAULT_ATTACKER_MODEL: str = os.getenv("DEFAULT_ATTACKER_MODEL", "gemini-2.5-flash")
    DEFAULT_EVALUATOR_MODEL: str = os.getenv("DEFAULT_EVALUATOR_MODEL", "gemini-2.5-flash")
    DEFAULT_COMPILER_MODEL: str = os.getenv("DEFAULT_COMPILER_MODEL", "gemini-2.5-flash")
    DEFAULT_TARGET_MODEL: str = os.getenv("DEFAULT_TARGET_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")

    # Vector Database / RAG Configuration
    VECTOR_DB_DIR: str = os.getenv("VECTOR_DB_DIR", str(Path(__file__).parent / "data" / "chroma_db"))
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Retry and Resilience Parameters
    RETRY_MIN_SECONDS: int = int(os.getenv("RETRY_MIN_SECONDS", "2"))
    RETRY_MAX_SECONDS: int = int(os.getenv("RETRY_MAX_SECONDS", "30"))
    MAX_RETRY_ATTEMPTS: int = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))

    # Available Model Registry (for target testing and agent execution)
    SUPPORTED_TARGET_MODELS: List[Dict[str, Any]] = [
        {
            "id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "name": "Llama 3.1 8B Instruct",
            "provider": "featherless",
            "recommended_for": "target"
        },
        {
            "id": "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "name": "Llama 3.1 70B Instruct",
            "provider": "featherless",
            "recommended_for": "target"
        },
        {
            "id": "mistralai/Mistral-7B-Instruct-v0.3",
            "name": "Mistral 7B Instruct v0.3",
            "provider": "featherless",
            "recommended_for": "target"
        },
        {
            "id": "gemini-2.5-flash",
            "name": "Gemini 2.5 Flash",
            "provider": "gemini",
            "recommended_for": "all"
        },
        {
            "id": "gemini-2.5-pro",
            "name": "Gemini 2.5 Pro",
            "provider": "gemini",
            "recommended_for": "evaluator"
        },
        {
            "id": "gpt-4o-mini",
            "name": "GPT-4o Mini",
            "provider": "openai",
            "recommended_for": "target"
        }
    ]

    # Server Configuration
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,*").split(",")
        if origin.strip()
    ]

    # Execution Parameters
    DEFAULT_TIMEOUT_SECONDS: float = float(os.getenv("DEFAULT_TIMEOUT_SECONDS", "30.0"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    DEFAULT_ATTACK_COUNT: int = 10

settings = Settings()
