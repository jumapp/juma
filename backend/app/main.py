"""Jumapp FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint

from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.db import engine, get_db
from app.health_check import run_health_check
from app.routers import routers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown."""
    # Startup
    if settings.db_auto_create:
        from app.init_db import init_db
        await init_db()
    
    yield
    
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)


def _sanitize_nullables(d: Any) -> None:
    """Recursively convert OpenAPI 3.1 `anyOf` nullables into OpenAPI 3.0 `nullable: true`."""
    if isinstance(d, dict):
        if "anyOf" in d and len(d["anyOf"]) == 2:
            types = d["anyOf"]
            null_t = next((t for t in types if t.get("type") == "null"), None)
            other_t = next((t for t in types if t.get("type") != "null"), None)
            if null_t and other_t:
                d.pop("anyOf")
                d.update(other_t)
                d["nullable"] = True
        for v in list(d.values()):
            _sanitize_nullables(v)
    elif isinstance(d, list):
        for item in d:
            _sanitize_nullables(item)


def custom_openapi():
    """Custom OpenAPI schema generator with auth security schemes."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        openapi_version="3.0.3",
        description="Jumapp API with full Swagger UI support for headers, request bodies, and CRUD operations.",
        routes=app.routes,
    )
    
    _sanitize_nullables(openapi_schema)

    # Configure Security Schemes in OpenAPI Components
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    
    security_schemes["SuperAdminToken"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-Super-Admin-Token",
        "description": "Super Admin token for full access (default: dev-super-admin-token)"
    }
    security_schemes["MasjidEditorToken"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-Masjid-Editor-Token",
        "description": "Masjid Editor token (pass masjid UUID)"
    }
    security_schemes["DevUserToken"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-Dev-User-Token",
        "description": "Dev user authorization token"
    }
    security_schemes["HTTPBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Bearer token authorization"
    }
    
    # Attach security globally so Swagger UI displays Authorize button
    openapi_schema["security"] = [
        {"SuperAdminToken": []},
        {"MasjidEditorToken": []},
        {"DevUserToken": []},
        {"HTTPBearer": []},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
for router in routers:
    app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root() -> dict:
    """Root endpoint returning basic app info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "version": settings.app_version}


@app.get("/health/full")
async def full_health() -> JSONResponse:
    """Full health check with database connectivity."""
    health_data = await run_health_check()
    status_code = 200 if health_data["status"] == "healthy" else 503
    return JSONResponse(health_data, status_code=status_code)


@app.middleware("http")
async def add_db_to_request(request: Request, call_next: RequestResponseEndpoint):
    """Add database connection to request state."""
    async for db in get_db():
        request.state.db = db
        response = await call_next(request)
        return response
