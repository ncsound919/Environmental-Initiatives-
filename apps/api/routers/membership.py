"""
ECOS Revenue Engine - Membership & Perks Router
Multi-tier membership (Free/Pro/Patron/Founder) with access control
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/membership", tags=["membership"])


class Tier(str, Enum):
    FREE = "free"
    PRO = "pro"
    PATRON = "patron"
    FOUNDER = "founder"


class Perk(BaseModel):
    id: str
    name: str
    description: str
    min_tier: Tier


class UserMembership(BaseModel):
    user_id: str
    tier: Tier
    active_since: datetime = Field(default_factory=datetime.now)
    perks_unlocked: List[str] = []
    total_spent: float = 0.0


MEMBERSHIPS_DB: dict = {}

ALL_PERKS = [
    Perk(id="api_access", name="API Gateway Access",
         description="Full REST API for all 13 projects", min_tier=Tier.PRO),
    Perk(id="analytics", name="Advanced Analytics",
         description="Predictive maintenance forecasting", min_tier=Tier.PRO),
    Perk(id="beta_fw", name="Beta Firmware",
         description="Early ESP32 firmware updates", min_tier=Tier.PRO),
    Perk(id="voting", name="Governance Voting",
         description="Vote on roadmap priorities", min_tier=Tier.PATRON),
    Perk(id="dev_chat", name="Developer Discord",
         description="Private engineering channel", min_tier=Tier.PATRON),
    Perk(id="rev_share", name="Revenue Sharing",
         description="Royalty pool distribution", min_tier=Tier.FOUNDER),
    Perk(id="kit_discount", name="DIY Kit 25% Discount",
         description="Physical kit discount", min_tier=Tier.FOUNDER),
]

TIER_PRICES = {Tier.FREE: 0, Tier.PRO: 29, Tier.PATRON: 99, Tier.FOUNDER: 499}
TIER_ORDER = [Tier.FREE, Tier.PRO, Tier.PATRON, Tier.FOUNDER]


@router.get("/tiers")
async def get_tiers():
    return [
        {
            "name": "Free",
            "price_monthly": 0,
            "price_annual": 0,
            "perks": ["Read docs", "Forum access", "Basic telemetry"],
            "popular": False,
        },
        {
            "name": "Pro",
            "price_monthly": 29,
            "price_annual": 290,
            "perks": ["Full API", "Advanced analytics", "Alerting", "API Gateway Access"],
            "popular": True,
        },
        {
            "name": "EcoChampion",
            "price_monthly": 99,
            "price_annual": 990,
            "perks": ["Gov voting", "Priority support", "Dev chat", "Beta Firmware"],
            "popular": False,
        },
        {
            "name": "PlanetGuardian",
            "price_monthly": 499,
            "price_annual": 4990,
            "perks": ["Revenue sharing", "25% kit discount", "Lifetime access", "Governance Voting"],
            "popular": False,
        },
    ]


@router.get("/perks", response_model=List[Perk])
async def list_perks(tier: Optional[Tier] = None):
    if tier:
        tier_idx = TIER_ORDER.index(tier)
        return [p for p in ALL_PERKS if TIER_ORDER.index(p.min_tier) <= tier_idx]
    return ALL_PERKS


class SubscribeRequest(BaseModel):
    """JSON body for POST /membership/subscribe (web-contract shape)."""
    user_id: Optional[str] = None
    tier: Optional[Tier] = None


@router.post("/subscribe", response_model=UserMembership)
async def subscribe(
    body: Optional[SubscribeRequest] = None,
    user_id: Optional[str] = None,
    tier: Optional[Tier] = None,
):
    # Web contract sends a JSON body; query params kept as a fallback.
    user_id = (body.user_id if body and body.user_id else user_id)
    tier = (body.tier if body and body.tier else tier)
    if not user_id or not tier:
        raise HTTPException(status_code=400, detail="user_id and tier are required")
    tier_idx = TIER_ORDER.index(tier)
    perks = [p.id for p in ALL_PERKS if TIER_ORDER.index(p.min_tier) <= tier_idx]
    membership = UserMembership(user_id=user_id, tier=tier, perks_unlocked=perks)
    MEMBERSHIPS_DB[user_id] = membership
    return membership


@router.get("/{user_id}", response_model=UserMembership)
async def get_user_membership(user_id: str):
    if user_id not in MEMBERSHIPS_DB:
        return UserMembership(user_id=user_id, tier=Tier.FREE)
    return MEMBERSHIPS_DB[user_id]


@router.get("/status/{user_id}", response_model=UserMembership)
async def get_membership_status(user_id: str):
    """Web-contract alias for GET /membership/{user_id}."""
    return await get_user_membership(user_id)


@router.delete("/cancel/{user_id}", response_model=UserMembership)
async def cancel_membership(user_id: str):
    """Downgrade a user to the Free tier (web-contract endpoint)."""
    if user_id not in MEMBERSHIPS_DB:
        return UserMembership(user_id=user_id, tier=Tier.FREE)
    membership = MEMBERSHIPS_DB[user_id]
    membership.tier = Tier.FREE
    membership.perks_unlocked = [p.id for p in ALL_PERKS if p.min_tier == Tier.FREE]
    return membership


@router.get("/stats/overview")
async def get_membership_stats():
    counts = {t.value: 0 for t in Tier}
    revenue = 0.0
    for m in MEMBERSHIPS_DB.values():
        counts[m.tier] = counts.get(m.tier, 0) + 1
        revenue += TIER_PRICES.get(m.tier, 0)
    return {
        "total_members": len(MEMBERSHIPS_DB),
        "by_tier": counts,
        "monthly_mrr_usd": revenue,
        "arr_usd": revenue * 12,
    }


@router.get("/revenue/summary")
async def get_membership_revenue():
    """Web-contract summary used by the Revenue Dashboard."""
    counts = {t.value: 0 for t in Tier}
    revenue = 0.0
    for m in MEMBERSHIPS_DB.values():
        counts[m.tier] = counts.get(m.tier, 0) + 1
        revenue += TIER_PRICES.get(m.tier, 0)
    return {
        "monthly_recurring_revenue": revenue,
        "arr_usd": revenue * 12,
        "total_members": len(MEMBERSHIPS_DB),
        "by_tier": counts,
    }
