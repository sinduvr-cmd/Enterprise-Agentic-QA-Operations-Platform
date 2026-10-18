"""
Main FastAPI Application Entry Point for Enterprise Agentic QA Operations Platform.
"""
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database schema & seed demo data
    init_db()
    yield
    # Shutdown logic if any


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Enterprise Agentic QA Operations Platform combining requirement analysis, AI test generation, Playwright synthesis, Critic loops, human approvals, GitHub CI execution, and failure root-cause analysis.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health & Info Endpoints
@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
    }


@app.get("/api/v1/system-info", tags=["System"])
def system_info():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "github_mode": settings.GITHUB_INTEGRATION_MODE,
        "database": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite",
        "demo_mode": settings.DEMO_MODE,
        "keycloak_enabled": settings.KEYCLOAK_ENABLED,
    }


# Mount central API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount Static Files for Embedded Web Dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
@app.get("/dashboard", include_in_schema=False)
@app.get("/projects", include_in_schema=False)
@app.get("/qa-runs", include_in_schema=False)
@app.get("/approvals", include_in_schema=False)
@app.get("/reports", include_in_schema=False)
def serve_spa():
    """
    Serves the embedded Single Page Application.
    """
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {
        "message": "Enterprise Agentic QA Operations Platform API is running.",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
