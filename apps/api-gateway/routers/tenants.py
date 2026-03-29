"""
Level 5 – Multi-Tenant Management & SaaS Tier System
Handles tenant onboarding, SaaS plan enforcement (Free/Pro/Enterprise),
usage tracking, and feature gates for all 13 ECOS projects.
"""
from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/api/tenants", tags=["Tenants & SaaS"])

# ── SaaS Tier Definitions ──────────────────────────────────────────────────────────
TIERS: Dict[str, dict] = {
    "free": {
        "name": "Free",
        "price_usd_month": 0,
        "projects_allowed": 1,
        "api_calls_day": 500,
        "data_retention_days": 7,
        "mqtt_devices": 2,
        "analytics": False,
        "compliance": False,
        "sla": "none",
        "support": "community",
    },
    "pro": {
        "name": "Pro",
        "price_usd_month": 149,
        "projects_allowed": 5,
        "api_calls_day": 50_000,
        "data_retention_days": 90,
        "mqtt_devices": 50,
        "analytics": True,
        "compliance": False,
        "sla": "99.5%",
        "support": "email",
    },
    "enterprise": {
        "name": "Enterprise",
        "price_usd_month": 999,
        "projects_allowed": 13,
        "api_calls_day": -1,  # unlimited
        "data_retention_days": 365,
        "mqtt_devices": -1,  # unlimited
        "analytics": True,
        "compliance": True,
        "sla": "99.9%",
        "support": "dedicated",
    },
}

# ── In-memory tenant store (replace with PostgreSQL in prod) ──────────────────
TENANTS: Dict[str, dict] = {}
USAGE: Dict[str, dict] = {}


# ── Schemas ───────────────────────────────────────────────────────────────
class TenantCreate(BaseModel):
    name: str
    email: str
    plan: str = "free"
    organization: Optional[str] = None
    projects: List[str] = []


class TenantUpgrade(BaseModel):
    plan: str


class UsageRecord(BaseModel):
    endpoint: str
    project_id: Optional[str] = None
    cost_units: float = 1.0


# ── Helpers ───────────────────────────────────────────────────────────────
def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _get_or_404(tenant_id: str) -> dict:
    tenant = TENANTS.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")
    return tenant


# ── Endpoints ─────────────────────────────────────────────────────────────
@router.get("/tiers", summary="List all SaaS tiers and features")
def list_tiers():
    return {"tiers": [
        {"id": k, **v} for k, v in TIERS.items()
    ]}


@router.post("/", summary="Onboard a new tenant")
def create_tenant(body: TenantCreate):
    if body.plan not in TIERS:
        raise HTTPException(status_code=400, detail=f"Invalid plan '{body.plan}'. Choose: {list(TIERS)}")
    tier = TIERS[body.plan]
    if body.projects and len(body.projects) > tier["projects_allowed"]:
        raise HTTPException(
            status_code=403,
            detail=f"Plan '{body.plan}' allows {tier['projects_allowed']} project(s), got {len(body.projects)}"
        )
    tenant_id = str(uuid.uuid4())[:8]
    TENANTS[tenant_id] = {
        "id": tenant_id,
        "name": body.name,
        "email": body.email,
        "organization": body.organization,
        "plan": body.plan,
        "projects": body.projects,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "api_key": f"ecos_{tenant_id}_{uuid.uuid4().hex[:12]}",
    }
    USAGE[tenant_id] = {}
    return {"tenant": TENANTS[tenant_id], "tier_features": tier}


@router.get("/{tenant_id}", summary="Get tenant details")
def get_tenant(tenant_id: str):
    return _get_or_404(tenant_id)


@router.patch("/{tenant_id}/upgrade", summary="Upgrade or downgrade SaaS plan")
def upgrade_plan(tenant_id: str, body: TenantUpgrade):
    tenant = _get_or_404(tenant_id)
    if body.plan not in TIERS:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {body.plan}")
    old_plan = tenant["plan"]
    tenant["plan"] = body.plan
    return {
        "tenant_id": tenant_id,
        "old_plan": old_plan,
        "new_plan": body.plan,
        "features": TIERS[body.plan],
        "effective": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/{tenant_id}/usage", summary="Record API usage (metered billing hook)")
def record_usage(tenant_id: str, record: UsageRecord):
    tenant = _get_or_404(tenant_id)
    tier = TIERS[tenant["plan"]]
    today = _today()
    day_usage = USAGE[tenant_id].get(today, {"calls": 0, "units": 0.0})
    day_usage["calls"] += 1
    day_usage["units"] += record.cost_units
    USAGE[tenant_id][today] = day_usage
    limit = tier["api_calls_day"]
    over_limit = limit != -1 and day_usage["calls"] > limit
    return {
        "tenant_id": tenant_id,
        "date": today,
        "calls_today": day_usage["calls"],
        "units_today": day_usage["units"],
        "limit": limit if limit != -1 else "unlimited",
        "over_limit": over_limit,
        "action": "upgrade to Pro or Enterprise" if over_limit else "ok",
    }


@router.get("/{tenant_id}/usage", summary="Get usage summary for a tenant")
def get_usage(tenant_id: str):
    _get_or_404(tenant_id)
    usage = USAGE.get(tenant_id, {})
    total_calls = sum(v["calls"] for v in usage.values())
    return {
        "tenant_id": tenant_id,
        "daily_breakdown": usage,
        "total_calls_all_time": total_calls,
    }


@router.get("/", summary="List all tenants (admin only)")
def list_tenants():
    return {"tenants": list(TENANTS.values()), "count": len(TENANTS)}


@router.get("/feature-gate/{tenant_id}/{feature}", summary="Check if a feature is enabled for a tenant")
def feature_gate(tenant_id: str, feature: str):
    tenant = _get_or_404(tenant_id)
    tier = TIERS.get(tenant["plan"], {})
    enabled = bool(tier.get(feature, False))
    return {
        "tenant_id": tenant_id,
        "plan": tenant["plan"],
        "feature": feature,
        "enabled": enabled,
        "upgrade_to": None if enabled else "pro" if feature == "analytics" else "enterprise",
    }
