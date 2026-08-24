import os
import json
import time
import asyncio
import logging
from typing import Optional, List, Dict, Any, Union
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from config import settings

logger = logging.getLogger("LLMService")

class LLMService:
    """
    Unified, resilient asynchronous LLM service supporting Featherless.AI (Open-weights models),
    Google Gemini API, and OpenAI API with Tenacity retries and structured output formatting.
    """

    def __init__(self):
        self.featherless_api_key = settings.FEATHERLESS_API_KEY
        self.featherless_base_url = settings.FEATHERLESS_BASE_URL
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_base_url = settings.OPENAI_BASE_URL

        self._openai_client = None
        self._featherless_client = None
        self._gemini_client = None

    def _get_featherless_client(self):
        if not self._featherless_client and self.featherless_api_key:
            from openai import AsyncOpenAI
            self._featherless_client = AsyncOpenAI(
                base_url=self.featherless_base_url,
                api_key=self.featherless_api_key,
                timeout=settings.DEFAULT_TIMEOUT_SECONDS
            )
        return self._featherless_client

    def _get_openai_client(self):
        if not self._openai_client and self.openai_api_key:
            from openai import AsyncOpenAI
            self._openai_client = AsyncOpenAI(
                base_url=self.openai_base_url,
                api_key=self.openai_api_key,
                timeout=settings.DEFAULT_TIMEOUT_SECONDS
            )
        return self._openai_client

    def _get_gemini_client(self):
        if not self._gemini_client and self.gemini_api_key:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=self.gemini_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI SDK: {e}")
        return self._gemini_client

    def detect_provider(self, model: str) -> str:
        """Determines provider routing based on model identifier and available keys."""
        model_lower = model.lower()
        if "gemini" in model_lower:
            return "gemini"
        elif any(prefix in model_lower for prefix in ["gpt-", "o1-", "o3-", "text-embedding"]):
            return "openai"
        elif any(prefix in model_lower for prefix in ["meta-llama", "mistral", "qwen", "deepseek", "llama"]):
            if self.featherless_api_key:
                return "featherless"
            elif self.openai_api_key:
                return "openai"
            elif self.gemini_api_key:
                return "gemini"
        
        # Fallback order based on configured keys
        if self.featherless_api_key:
            return "featherless"
        elif self.gemini_api_key:
            return "gemini"
        elif self.openai_api_key:
            return "openai"
        return "mock"

    @retry(
        wait=wait_exponential(multiplier=1, min=settings.RETRY_MIN_SECONDS, max=settings.RETRY_MAX_SECONDS),
        stop=stop_after_attempt(settings.MAX_RETRY_ATTEMPTS),
        reraise=True
    )
    async def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        json_mode: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Core generation method decorated with Tenacity exponential retry backoff."""
        target_model = model or settings.DEFAULT_TARGET_MODEL
        provider = self.detect_provider(target_model)
        start_time = time.time()

        if provider == "gemini":
            return await self._generate_gemini(
                prompt=prompt,
                system_prompt=system_prompt,
                model=target_model,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
                start_time=start_time
            )
        elif provider in ("featherless", "openai"):
            client = self._get_featherless_client() if provider == "featherless" else self._get_openai_client()
            if not client:
                raise ValueError(f"Provider {provider} selected for model {target_model}, but API key is not configured.")
            return await self._generate_openai_compatible(
                client=client,
                prompt=prompt,
                system_prompt=system_prompt,
                model=target_model,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
                tools=tools,
                start_time=start_time
            )
        else:
            raise ValueError("No LLM API keys configured. Please set FEATHERLESS_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY.")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        json_mode: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Safe wrapper around generate_with_retry that handles unexpected exceptions."""
        start_time = time.time()
        target_model = model or settings.DEFAULT_TARGET_MODEL
        provider = self.detect_provider(target_model)
        try:
            return await self.generate_with_retry(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
                tools=tools
            )
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"Error during model generation ({target_model}): {str(e)}")
            return {
                "text": f"Error during model generation: {str(e)}",
                "tool_calls": None,
                "latency_ms": elapsed_ms,
                "status": "error",
                "error": str(e),
                "model": target_model,
                "provider": provider
            }

    async def _generate_openai_compatible(
        self,
        client,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool,
        tools: Optional[List[Dict[str, Any]]],
        start_time: float
    ) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await client.chat.completions.create(**kwargs)
        elapsed_ms = (time.time() - start_time) * 1000

        choice = response.choices[0]
        message = choice.message
        content = message.content or ""

        tool_calls = None
        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]

        return {
            "text": content,
            "tool_calls": tool_calls,
            "latency_ms": elapsed_ms,
            "status": "success",
            "error": None,
            "model": model,
            "provider": "openai_compatible"
        }

    async def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool,
        start_time: float
    ) -> Dict[str, Any]:
        client = self._get_gemini_client()
        if not client:
            raise ValueError("Google Gemini API client could not be initialized. Please check GEMINI_API_KEY.")

        gemini_model = model
        if not gemini_model.startswith("gemini-"):
            gemini_model = "gemini-2.5-flash"

        def _sync_call():
            config: Dict[str, Any] = {
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
            if system_prompt:
                config["system_instruction"] = system_prompt
            if json_mode:
                config["response_mime_type"] = "application/json"

            response = client.models.generate_content(
                model=gemini_model,
                contents=prompt,
                config=config
            )
            return response.text

        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, _sync_call)
        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "text": text or "",
            "tool_calls": None,
            "latency_ms": elapsed_ms,
            "status": "success",
            "error": None,
            "model": gemini_model,
            "provider": "gemini"
        }

    def get_provider_status(self) -> Dict[str, Any]:
        """Returns the readiness status of each provider."""
        return {
            "featherless": {
                "configured": bool(self.featherless_api_key),
                "base_url": self.featherless_base_url
            },
            "gemini": {
                "configured": bool(self.gemini_api_key)
            },
            "openai": {
                "configured": bool(self.openai_api_key),
                "base_url": self.openai_base_url
            }
        }

# Global singleton
llm_service = LLMService()
