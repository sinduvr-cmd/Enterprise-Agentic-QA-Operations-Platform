"""
Configuration module for Enterprise Agentic QA Operations Platform.
Reads from environment variables and provides sensible defaults for local development.
"""
import os
from typing import List, Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    PROJECT_NAME: str = "Enterprise Agentic QA Operations Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")

    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecret-jwt-key-agentic-qa-enterprise-change-in-prod-2026")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))
    KEYCLOAK_ENABLED: bool = os.getenv("KEYCLOAK_ENABLED", "false").lower() in ("true", "1", "yes")
    KEYCLOAK_SERVER_URL: Optional[str] = os.getenv("KEYCLOAK_SERVER_URL", None)
    KEYCLOAK_REALM: Optional[str] = os.getenv("KEYCLOAK_REALM", "enterprise-qa")
    KEYCLOAK_CLIENT_ID: Optional[str] = os.getenv("KEYCLOAK_CLIENT_ID", "qa-ops-platform")
    KEYCLOAK_CLIENT_SECRET: Optional[str] = os.getenv("KEYCLOAK_CLIENT_SECRET", None)

    # Database
    # Defaults to local SQLite for instant zero-configuration execution; production uses PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./enterprise_qa_ops.db"
    )

    # LLM Agent Providers (OpenAI / Gemini / Anthropic / Mock)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

    # GitHub Integration
    GITHUB_INTEGRATION_MODE: str = os.getenv("GITHUB_INTEGRATION_MODE", "mock")
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN", None)
    GITHUB_ORG: Optional[str] = os.getenv("GITHUB_ORG", "enterprise-qa-demo")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]


settings = Settings()
