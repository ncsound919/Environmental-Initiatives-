"""
Level 5 – Advanced Analytics & Predictive Maintenance
Cross-project analytics, anomaly detection, and predictive maintenance
for all 13 ECOS initiatives. Multi-tenant aware.
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import math
import random

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# ── Project registry ───────────────────────────────────────────────────────────
PROJECTS = [
    {"id": "P01", "name": "EcoHomes OS", "zone": "A"},
    {"id": "P02", "name": "AgriConnect", "zone": "C"},
    {"id": "P03", "name": "RegeneraFarm", "zone": "C"},
    {"id": "P04", "name": "HempMobility", "zone": "D"},
    {"id": "P05", "name": "LumiFreq", "zone": "A"},
    {"id": "P06", "name": "NucleoSim", "zone": "D"},
    {"id": "P07", "name": "PlastiCycle", "zone": "D"},
    {"id": "P08", "name": "EverLume", "zone": "A"},
    {"id": "P09", "name": "AquaGen", "zone": "B"},
    {"id": "P10", "name": "ThermalGrid", "zone": "B"},
    {"id": "P11", "name": "BioSynth", "zone": "D"},
    {"id": "P12", "name": "SolarShare", "zone": "B"},
    {"id": "P13", "name": "MicroHydro", "zone": "B"},
]


def _simulate_health(project_id: str) -> Dict[str, Any]:
    """Deterministic-ish simulated telemetry for demo."""
    seed = sum(ord(c) for c in project_id)
    rng = random.Random(seed + int(datetime.now().hour))
    score = round(rng.uniform(72, 99), 2)
    anomaly = score < 80
    return {
        "health_score": score,
        "anomaly_detected": anomaly,
        "mtbf_hours": round(rng.uniform(800, 8760), 0),
        "next_maintenance_days": round(rng.uniform(1, 90), 0) if anomaly else round(rng.uniform(30, 365), 0),
        "efficiency_pct": round(rng.uniform(78, 97), 2),
        "carbon_kg_saved": round(rng.uniform(50, 5000), 1),
        "energy_kwh": round(rng.uniform(100, 50000), 1),
    }


# ── Schemas ───────────────────────────────────────────────────────────────
class AnomalyRequest(BaseModel):
    project_id: str
    readings: List[float]
    window_size: int = 10
    z_threshold: float = 2.5


class MaintenancePrediction(BaseModel):
    project_id: str
    asset_id: str
    age_hours: float
    sensor_values: Dict[str, float]


# ── Endpoints ─────────────────────────────────────────────────────────────
@router.get("/ecosystem", summary="Ecosystem-wide health dashboard")
def ecosystem_health(tenant_id: str = Query("default")):
    metrics = [{"project": p, **_simulate_health(p["id"])} for p in PROJECTS]
    anomalies = [m for m in metrics if m["anomaly_detected"]]
    total_carbon = round(sum(m["carbon_kg_saved"] for m in metrics), 1)
    total_energy = round(sum(m["energy_kwh"] for m in metrics), 1)
    avg_health = round(sum(m["health_score"] for m in metrics) / len(metrics), 2)
    return {
        "tenant_id": tenant_id,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "projects_total": len(PROJECTS),
            "projects_healthy": len(PROJECTS) - len(anomalies),
            "projects_anomalous": len(anomalies),
            "avg_health_score": avg_health,
            "total_carbon_kg_saved": total_carbon,
            "total_energy_kwh": total_energy,
        },
        "anomalies": anomalies,
        "projects": metrics,
    }


@router.get("/project/{project_id}", summary="Per-project advanced analytics")
def project_analytics(project_id: str, tenant_id: str = Query("default")):
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if not project:
        return {"error": f"Unknown project {project_id}"}
    health = _simulate_health(project_id)
    return {
        "tenant_id": tenant_id,
        "project": project,
        "as_of": datetime.now(timezone.utc).isoformat(),
        **health,
        "recommendations": _get_recommendations(project_id, health),
    }


def _get_recommendations(pid: str, health: dict) -> List[str]:
    recs = []
    if health["health_score"] < 85:
        recs.append(f"Schedule maintenance within {int(health['next_maintenance_days'])} days")
    if health["efficiency_pct"] < 85:
        recs.append("Efficiency below 85% – inspect actuators and sensors")
    if health["anomaly_detected"]:
        recs.append("Anomaly detected – review recent telemetry and run diagnostics")
    recs.append(f"Carbon savings on track: {health['carbon_kg_saved']} kg CO₂ avoided")
    return recs


@router.post("/anomaly-detect", summary="Z-score anomaly detection on a telemetry stream")
def detect_anomalies(req: AnomalyRequest):
    if len(req.readings) < req.window_size:
        return {"anomalies": [], "message": "Not enough data points"}
    results = []
    for i in range(req.window_size, len(req.readings)):
        window = req.readings[i - req.window_size: i]
        mean = sum(window) / len(window)
        variance = sum((x - mean) ** 2 for x in window) / len(window)
        std = math.sqrt(variance) if variance > 0 else 1e-9
        z = abs((req.readings[i] - mean) / std)
        if z > req.z_threshold:
            results.append({"index": i, "value": req.readings[i], "z_score": round(z, 3)})
    return {
        "project_id": req.project_id,
        "total_points": len(req.readings),
        "anomaly_count": len(results),
        "threshold": req.z_threshold,
        "anomalies": results,
    }


@router.post("/predictive-maintenance", summary="Predict time-to-failure for an asset")
def predict_maintenance(req: MaintenancePrediction):
    # Simplified Weibull-inspired failure model
    beta = 2.2   # shape (wear-out)
    eta = 8760.0 # scale (1-year characteristic life)
    reliability = math.exp(-(req.age_hours / eta) ** beta)
    ttf_hours = eta * ((-math.log(0.5)) ** (1 / beta)) - req.age_hours
    risk_level = "low" if reliability > 0.8 else "medium" if reliability > 0.5 else "high"
    return {
        "project_id": req.project_id,
        "asset_id": req.asset_id,
        "age_hours": req.age_hours,
        "reliability": round(reliability, 4),
        "risk_level": risk_level,
        "estimated_ttf_hours": max(0, round(ttf_hours, 1)),
        "action": "Schedule maintenance" if risk_level != "low" else "Continue monitoring",
    }


@router.get("/carbon-credits", summary="Cross-project carbon credit summary")
def carbon_summary(tenant_id: str = Query("default")):
    metrics = [_simulate_health(p["id"]) for p in PROJECTS]
    total_kg = sum(m["carbon_kg_saved"] for m in metrics)
    vcs_credits = round(total_kg / 1000, 4)  # 1 VCS credit = 1 tonne CO2
    return {
        "tenant_id": tenant_id,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "total_co2_avoided_kg": round(total_kg, 1),
        "vcs_credits_earned": vcs_credits,
        "estimated_market_value_usd": round(vcs_credits * 18.5, 2),  # ~$18.50/credit
        "projects": [
            {"project_id": PROJECTS[i]["id"], "co2_kg": round(metrics[i]["carbon_kg_saved"], 1)}
            for i in range(len(PROJECTS))
        ],
    }
