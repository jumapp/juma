"""Jumapp FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint

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
