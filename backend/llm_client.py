"""
Compatibility bridge mapping legacy llm_client to services.llm_service
"""
from services.llm_service import LLMService, llm_service

# Global singleton alias
llm_client = llm_service

__all__ = ["LLMService", "llm_service", "llm_client"]

