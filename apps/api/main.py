"""Environmental Initiatives Platform - FastAPI Main Application
All revenue routers wired up and ready.
"""
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

# CORS - allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://environmental-initiatives.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Revenue routers
app.include_router(challenges.router, prefix="/api", tags=["challenges"])
app.include_router(membership.router, prefix="/api", tags=["membership"])
app.include_router(marketplace.router, prefix="/api", tags=["marketplace"])
app.include_router(gamification.router, prefix="/api", tags=["gamification"])
app.include_router(diy_kits.router, prefix="/api", tags=["diy-kits"])


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
