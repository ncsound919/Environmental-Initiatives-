"""Environmental Initiatives Platform - FastAPI Main Application
All revenue routers wired up and ready.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import challenges, membership, marketplace, gamification, diy_kits

app = FastAPI(
    title="Environmental Initiatives API",
    description="Revenue-generating API for Environmental Initiatives Platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS - origins are configured via ECOS_ALLOWED_ORIGINS (comma-separated).
# Defaults to local development only; no production origin is hardcoded.
_allowed_origins = [
    origin.strip()
    for origin in os.environ.get("ECOS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Revenue routers (routers already declare /api/... prefixes)
app.include_router(challenges.router, tags=["challenges"])
app.include_router(membership.router, tags=["membership"])
app.include_router(marketplace.router, tags=["marketplace"])
app.include_router(gamification.router, tags=["gamification"])
app.include_router(diy_kits.router, tags=["diy-kits"])


@app.get("/")
async def root():
    return {
        "name": "Environmental Initiatives API",
        "version": "2.0.0",
        "status": "operational",
        "revenue_modules": [
            "challenges",
            "membership",
            "marketplace",
            "gamification",
            "diy_kits",
        ],
        "docs": "/api/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "environmental-initiatives-api"}
