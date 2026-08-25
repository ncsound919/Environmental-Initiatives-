"""
Smoke tests for the ECOS Revenue API (apps/api).

Verifies the web-contract endpoints return the shapes the Next.js frontend
expects (see apps/web/src/lib/api.ts and the page components).
"""
import sys
import os
import importlib.util
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

_API_DIR = os.path.join(os.path.dirname(__file__), "..")


def _load_main() -> None:
    """Load apps/api/main.py under a unique name so it never collides with the
    api-gateway's equally-named main module when both test suites run in one
    process. The api dir is pinned to the front of sys.path and any previously
    cached `routers` package (from the gateway) is evicted so the api's own
    routers package is imported."""
    path = os.path.join(_API_DIR, "main.py")
    sys.path.insert(0, _API_DIR)
    sys.modules.pop("routers", None)
    spec = importlib.util.spec_from_file_location("ecos_api_main", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["ecos_api_main"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)


_load_main()

from ecos_api_main import app  # noqa: E402


@pytest.fixture()
def client():
    return TestClient(app)


def test_health(client):
    assert client.get("/health").status_code == 200


def test_challenges_contract(client):
    # List + stats (what /challenges page calls)
    assert client.get("/api/challenges").status_code == 200
    stats = client.get("/api/challenges/stats/overview").json()
    for key in ("total_challenges", "active_challenges", "total_prize_pool"):
        assert key in stats

    # Create returns web-contract alias fields
    body = {
        "title": "Optimize Waste Sorting ML",
        "description": "Build an ML model to sort recyclables with high accuracy across deployment endpoints and edge hardware.",
        "project_id": 3,
        "challenge_type": "data",
        "difficulty": "advanced",
        "bounty_usd": 2000,
        "milestones": ["dataset", "model", "deploy"],
        "required_skills": ["pytorch"],
        "deadline_days": 30,
    }
    created = client.post("/api/challenges/create", json=body).json()
    for key in ("category", "prize_usd", "participants"):
        assert key in created


def test_membership_contract(client):
    tiers = client.get("/api/membership/tiers").json()
    assert isinstance(tiers, list) and len(tiers) >= 4
    first = tiers[0]
    for key in ("name", "price_monthly", "price_annual", "perks", "popular"):
        assert key in first

    revenue = client.get("/api/membership/revenue/summary").json()
    assert "monthly_recurring_revenue" in revenue
    assert "total_members" in revenue

    assert client.get("/api/membership/status/u1").status_code == 200
    assert client.delete("/api/membership/cancel/u1").status_code == 200


def test_marketplace_contract(client):
    created = client.post(
        "/api/marketplace/listings",
        json={
            "seller_id": "s1",
            "title": "Solar Forecast Model",
            "description": "A forecasting model for solar output across deployments.",
            "product_type": "algorithm",
            "price_usd": 49.0,
        },
    ).json()
    for key in ("category", "listing_type", "units_sold"):
        assert key in created

    listings = client.get("/api/marketplace/listings").json()
    assert isinstance(listings, list)
    assert client.get("/api/marketplace/listings/MP00001").status_code == 200

    stats = client.get("/api/marketplace/stats/overview").json()
    for key in ("total_listings", "total_gmv_usd", "active_sellers"):
        assert key in stats


def test_gamification_contract(client):
    assert client.post("/api/gamification/xp/add?user_id=u1&action=challenge_won").status_code == 200
    lb = client.get("/api/gamification/leaderboard").json()
    assert isinstance(lb, list)
    if lb:
        for key in ("user_id", "level", "title", "total_xp"):
            assert key in lb[0]

    levels = client.get("/api/gamification/levels").json()
    assert isinstance(levels, list) and len(levels) >= 8
    for key in ("level", "title", "xp_required"):
        assert key in levels[0]

    stats = client.get("/api/gamification/stats/overview").json()
    for key in ("total_users", "total_xp_awarded", "total_quests"):
        assert key in stats

    assert client.get("/api/gamification/quests/u1").status_code == 200


def test_diy_kits_contract(client):
    kits = client.get("/api/kits").json()
    assert isinstance(kits, list) and len(kits) >= 5
    first = kits[0]
    assert "category" in first
    assert first["bom"][0]["component"]
    assert first["bom"][0]["unit_cost_usd"] > 0
    assert first["bom"][0]["qty"] >= 1

    stats = client.get("/api/kits/stats/overview").json()
    for key in ("total_kits", "total_revenue_usd", "community_builds"):
        assert key in stats


def test_no_api_api_double_prefix(client):
    # Regression: routers declare /api prefixes AND main.py used to add another.
    assert client.get("/api/api/challenges").status_code == 404


def test_mutation_endpoints_accept_json_body(client):
    """The web api.ts sends JSON bodies for mutations; routers must accept them."""
    # membership subscribe (body: {user_id, tier})
    r = client.post("/api/membership/subscribe", json={"user_id": "u_body", "tier": "pro"})
    assert r.status_code == 200, r.text
    assert r.json()["tier"] == "pro"

    # marketplace create + purchase (body: {buyer_id})
    created = client.post(
        "/api/marketplace/listings",
        json={
            "seller_id": "s_body",
            "title": "Body Contract Model",
            "description": "A listing created through the JSON body contract path to verify shapes.",
            "product_type": "algorithm",
            "price_usd": 25.0,
        },
    ).json()
    pid = created["id"]
    r = client.post(f"/api/marketplace/listings/{pid}/purchase", json={"buyer_id": "b_body"})
    assert r.status_code == 200, r.text
    assert r.json()["buyer_id"] == "b_body"

    # gamification addXp (body: {user_id, action, multiplier})
    r = client.post(
        "/api/gamification/xp/add",
        json={"user_id": "u_body", "action": "challenge_won", "multiplier": 2.0},
    )
    assert r.status_code == 200, r.text
    assert r.json()["xp_earned"] == 1000  # 500 * 2.0

    # kits order (body: {user_id, quantity, is_founder})
    r = client.post(
        "/api/kits/KIT-P01/order",
        json={"user_id": "u_body", "quantity": 2, "is_founder": True},
    )
    assert r.status_code == 200, r.text
    order = r.json()
    assert order["quantity"] == 2
    assert order["member_discount_applied"] is True

    # kits build-log (body: {user_id, progress_pct, notes})
    r = client.post(
        "/api/kits/KIT-P01/build-log",
        json={"user_id": "u_body", "progress_pct": 100, "notes": "done"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["completed"] is True


def test_challenge_leaderboard_contract(client):
    """GET /challenges/{id}/leaderboard (web-contract endpoint)."""
    body = {
        "title": "Leaderboard Test Challenge",
        "description": "A challenge created purely to verify the per-challenge leaderboard endpoint responds correctly.",
        "project_id": 3,
        "challenge_type": "data",
        "difficulty": "beginner",
        "bounty_usd": 500,
        "milestones": ["data"],
    }
    created = client.post("/api/challenges/create", json=body).json()
    cid = created["id"]
    r = client.get(f"/api/challenges/{cid}/leaderboard")
    assert r.status_code == 200, r.text
    assert r.json()["challenge_id"] == cid