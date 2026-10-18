"""
LLM Client Adapter supporting Gemini, OpenAI, and Deterministic Enterprise Mock.
Validates structured JSON against Pydantic models.
"""
import json
import logging
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel
import httpx

from backend.app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY

    def invoke_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[BaseModel],
        mock_fallback_fn=None,
    ) -> BaseModel:
        """
        Invokes LLM and returns validated Pydantic model.
        Falls back to mock/deterministic engine if provider is 'mock' or API keys are missing.
        """
        if self.provider == "gemini" and self.gemini_key:
            try:
                return self._call_gemini(system_prompt, user_prompt, response_model)
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}. Falling back to deterministic engine.")

        elif self.provider == "openai" and self.openai_key:
            try:
                return self._call_openai(system_prompt, user_prompt, response_model)
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}. Falling back to deterministic engine.")

        # Default / Deterministic Mock Provider
        if mock_fallback_fn:
            return mock_fallback_fn()

        raise RuntimeError(f"No valid LLM provider or fallback found for {response_model.__name__}")

    def _call_gemini(self, system_prompt: str, user_prompt: str, response_model: Type[BaseModel]) -> BaseModel:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={self.gemini_key}"
        schema = response_model.model_json_schema()
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system_prompt}\n\nTask:\n{user_prompt}\n\nRespond ONLY with valid JSON strictly adhering to schema:\n{json.dumps(schema)}"}]}
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed_json = json.loads(raw_text)
            return response_model.model_validate(parsed_json)

    def _call_openai(self, system_prompt: str, user_prompt: str, response_model: Type[BaseModel]) -> BaseModel:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        schema = response_model.model_json_schema()
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": f"{system_prompt}\nYou MUST return a JSON object adhering to this schema: {json.dumps(schema)}"},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]
            parsed_json = json.loads(raw_text)
            return response_model.model_validate(parsed_json)


llm_client = LLMClient()
