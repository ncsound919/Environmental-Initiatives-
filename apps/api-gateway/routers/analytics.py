"""
Level 5 – Advanced Analytics & Predictive Maintenance
Cross-project analytics, anomaly detection, and predictive maintenance
for all 13 ECOS initiatives. Multi-tenant aware.

Analytics are computed from REAL ingested telemetry (see telemetry_store.py,
fed by POST /api/iot/ingest and the MQTT bridge). No values are fabricated:
when a project has no stored data, the API reports no_data explicitly instead
of inventing readings.
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import math

from telemetry_store import (
    readings_for,
    measurement_types,
    project_energy_kwh,
    project_count,
    totals,
)
from carbon_credits.registry import calculate_carbon_credit, CarbonEvent, CARBON_PRICES

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

# Map project code to the carbon-credit event type its energy readings generate.
CARBON_EVENT_TYPE_BY_PROJECT = {
    "P12": "solar_gen",
    "P13": "hydro_gen",
    "P10": "geothermal_saving",
    "P03": "soil_carbon",
    "P11": "bio_carbon",
}


def _zscore_anomaly_rate(readings: List[Dict[str, Any]]) -> float:
    """Anomaly rate (0.0-1.0) computed from real readings via rolling z-score."""
    values = [r["measurement_value"] for r in readings]
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(variance) if variance > 0 else 0.0
    if std == 0:
        return 0.0
    outliers = sum(1 for v in values if abs(v - mean) / std > 2.5)
    return round(outliers / len(values), 4)


def _project_health(project_code: str) -> Dict[str, Any]:
    """Health metrics derived from real stored telemetry for one project."""
    readings = readings_for(project_code)
    if not readings:
        return {
            "has_data": False,
            "reading_count": 0,
            "anomaly_rate": 0.0,
            "health_score": None,
            "energy_kwh": 0.0,
            "measurement_types": [],
            "latest_reading_at": None,
        }
    latest = max(readings, key=lambda r: r["timestamp"])
    return {
        "has_data": True,
        "reading_count": len(readings),
        "anomaly_rate": _zscore_anomaly_rate(readings),
        "health_score": round(max(0.0, 100.0 * (1.0 - _zscore_anomaly_rate(readings))), 2),
        "energy_kwh": round(project_energy_kwh(project_code), 2),
        "measurement_types": measurement_types(project_code),
        "latest_reading_at": latest["timestamp"],
    }


def _carbon_events_from_telemetry() -> List[CarbonEvent]:
    """Build carbon credit events ONLY from real stored energy readings."""
    events: List[CarbonEvent] = []
    for project_code, event_type in CARBON_EVENT_TYPE_BY_PROJECT.items():
        energy_kwh = project_energy_kwh(project_code)
        if energy_kwh <= 0:
            continue
        events.append(
            CarbonEvent(
                project_id=int(project_code[1:]),
                project_code=project_code,
                event_type=event_type,
                quantity_kwh_or_kg=energy_kwh,
                unit="kwh",
                methodology="IPCC_AR6",
            )
        )
    return events


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
    metrics = []
    for project in PROJECTS:
        health = _project_health(project["id"])
        metrics.append({"project": project, **health})

    with_data = [m for m in metrics if m["has_data"]]
    healthy_count = sum(1 for m in with_data if m["health_score"] is not None and m["health_score"] >= 80)
    store_totals = totals()

    return {
        "tenant_id": tenant_id,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "data_source": "REAL_TELEMETRY",
        "summary": {
            "projects_total": len(PROJECTS),
            "projects_with_data": len(with_data),
            "projects_healthy": healthy_count,
            "projects_anomalous": len(with_data) - healthy_count,
            "total_readings": store_totals["total_readings"],
            "total_energy_kwh": store_totals["total_energy_kwh"],
        },
        "projects": metrics,
    }


@router.get("/project/{project_id}", summary="Per-project advanced analytics")
def project_analytics(project_id: str, tenant_id: str = Query("default")):
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if not project:
        return {"error": f"Unknown project {project_id}"}
    health = _project_health(project_id)
    return {
        "tenant_id": tenant_id,
        "project": project,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "data_source": "REAL_TELEMETRY",
        **health,
        "recommendations": _get_recommendations(project_id, health),
    }


def _get_recommendations(pid: str, health: dict) -> List[str]:
    recs = []
    if not health.get("has_data"):
        recs.append("No telemetry ingested yet – connect devices via POST /api/iot/ingest")
        return recs
    if health.get("anomaly_rate", 0) > 0.05:
        recs.append(f"Anomaly rate {health['anomaly_rate']:.1%} exceeds 5% – inspect recent telemetry")
    if health.get("energy_kwh", 0) > 0:
        recs.append(f"Energy generation on record: {health['energy_kwh']} kWh")
    else:
        recs.append("No energy readings stored yet for this project")
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
        "data_source": "REAL_TELEMETRY",
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
    events = _carbon_events_from_telemetry()
    credits = [calculate_carbon_credit(e) for e in events]
    total_avoided = sum(c.tonnes_co2e_avoided for c in credits)
    total_sequestered = sum(c.tonnes_co2e_sequestered for c in credits)
    total = total_avoided + total_sequestered
    return {
        "tenant_id": tenant_id,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "data_source": "REAL_TELEMETRY",
        "total_co2_avoided_kg": round(total_avoided * 1000.0, 1),
        "total_tonnes_co2e": round(total, 4),
        "vcs_credits_earned": round(total, 4),
        "estimated_market_value_usd": {
            market: round(total * price, 2)
            for market, price in CARBON_PRICES.items()
        },
        "verification_status": "unverified",
        "credits": [
            {
                "project_code": c.event.project_code,
                "event_type": c.event.event_type,
                "tonnes_co2e": c.total_tonnes_co2e,
                "verra_methodology": c.verra_methodology,
                "gold_standard_methodology": c.gold_standard_methodology,
            }
            for c in credits
        ],
        "projects": [
            {
                "project_id": p["id"],
                "tonnes_co2e": round(
                    sum(c.total_tonnes_co2e for c in credits if c.event.project_code == p["id"]),
                    4,
                ),
            }
            for p in PROJECTS
        ],
    }