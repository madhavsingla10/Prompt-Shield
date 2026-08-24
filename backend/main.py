import os
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from schemas import AuditRequest, AuditSummary, NodeStage
from llm_client import llm_client

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
