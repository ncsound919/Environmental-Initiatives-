"""
ECOS API Gateway – Level 5 Router Package
Register all Level 5 FastAPI routers with the main app.
Usage in main.py (already present at bottom of file):
    from routers import register_level5_routers
    register_level5_routers(app)
"""
from fastapi import FastAPI
from routers.analytics import router as analytics_router
from routers.compliance import router as compliance_router
from routers.tenants import router as tenants_router


def register_level5_routers(app: FastAPI) -> None:
    """Wire all Level 5 routers into the FastAPI application."""
    app.include_router(analytics_router)
    app.include_router(compliance_router)
    app.include_router(tenants_router)
