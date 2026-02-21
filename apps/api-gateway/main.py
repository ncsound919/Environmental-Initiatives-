"""
ECOS API Gateway - FastAPI application
Exposes all 13 project brains as REST APIs
Completes Level 1 requirement: API Exposed
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, List, Any, Literal, Iterable
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import secrets
import base64
import re
import sys
import os
import logging
from pathlib import Path

# Add ecosystem-brains to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../packages/ecosystem-brains'))

from forecasting import (
    forecast_stream_flow,
    forecast_solar_irradiance,
    forecast_humidity,
    predict_bulb_failure,
)
from solvers import (
    optimize_nutrient_cycle,
    optimize_awg_schedule,
    optimize_geothermal_flow,
    optimize_fungal_match,
)
from dispatcher import dispatch
from checklist import execute_all_initiatives
from mqtt_service import EcosMqttService

app = FastAPI(
    title="ECOS API Gateway",
    description="Unified API for all 13 Environmental Businesses",
    version="1.0.0"
)

SECRET_KEY = os.environ.get("ECOS_JWT_SECRET")
if not SECRET_KEY:
    if os.environ.get("NODE_ENV") == "production":
        raise RuntimeError("ECOS_JWT_SECRET must be set in production")
    SECRET_KEY = secrets.token_urlsafe(32)

ROOT_DIR = Path(__file__).resolve().parents[2]
HARDWARE_MANIFEST_PATH = ROOT_DIR / "config" / "hardware-manifests.json"
MQTT_ENABLED = os.environ.get("MQTT_ENABLED", "false").lower() == "true"
_mqtt_service = None


def _load_hardware_manifest() -> Dict[str, Any]:
    if HARDWARE_MANIFEST_PATH.exists():
        with HARDWARE_MANIFEST_PATH.open() as f:
            return json.load(f)
    return {"metadata": {}, "initiatives": []}


HARDWARE_MANIFEST = _load_hardware_manifest()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class StreamFlowRequest(BaseModel):
    historical_data: Dict[str, List[float]]
    hours_ahead: int = 24


class SolarIrradianceRequest(BaseModel):
    historical_data: Dict[str, List[float]]
    hours_ahead: int = 24


class HumidityRequest(BaseModel):
    historical_data: Dict[str, List[float]]
    hours_ahead: int = 6


class BulbTelemetryRequest(BaseModel):
    voltage: float
    thermal_cycles: int
    uptime: float


class NutrientCycleRequest(BaseModel):
    waste_inputs: Dict[str, float]
    crop_demands: Dict[str, float]


class AWGScheduleRequest(BaseModel):
    humidity_forecast: List[float]
    energy_prices: List[float]
    target_liters: float


class GeothermalFlowRequest(BaseModel):
    building_loads: Dict[str, float]
    ground_temp: float
    available_capacity: float


class FungalMatchRequest(BaseModel):
    soil_data: Dict[str, float]


class DispatchRequest(BaseModel):
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)


class TelemetryIngestRequest(BaseModel):
    sensor_id: str = Field(min_length=1)
    project_code: str = Field(min_length=1)
    device_id: str = Field(min_length=1)
    measurement_type: str = Field(min_length=1)
    measurement_value: float
    unit: str = Field(min_length=1)
    timestamp: datetime
    quality_flag: Literal["valid", "suspect", "invalid"] = "valid"


class AuthTokenRequest(BaseModel):
    user_id: str = Field(min_length=1)
    email: EmailStr
    role: str = "USER"
    project_access: List[str] = Field(default_factory=list)


class BillingEstimateRequest(BaseModel):
    tier: Literal["free", "pro", "enterprise"] = "pro"
    usage_kwh: float = Field(default=0.0, ge=0.0)
    water_liters: float = Field(default=0.0, ge=0.0)


class FirmwareFlashRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=255)
    project_code: str = Field(min_length=1, max_length=255)
    firmware_version: str
    checksum: str


class DeploymentStatusRequest(BaseModel):
    zone: str = Field(min_length=1)
    project_code: str = Field(min_length=1)
    inputs_from: List[str] = Field(default_factory=list)
    outputs_to: List[str] = Field(default_factory=list)


class SaaSTierRequest(BaseModel):
    tier: Literal["free", "pro", "enterprise"]


class ControlCommandRequest(BaseModel):
    device_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    params: Dict[str, Any] = Field(default_factory=dict)


def _sign_token(payload: Dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True)
    encoded_payload = base64.urlsafe_b64encode(serialized.encode()).decode()
    nonce = secrets.token_urlsafe(8)
    message = f"{encoded_payload}.{nonce}"
    signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"v1.{message}.{signature}"


def _get_mqtt_service() -> EcosMqttService:
    global _mqtt_service
    if not MQTT_ENABLED:
        raise RuntimeError("MQTT disabled via MQTT_ENABLED=false")
    if _mqtt_service is None:
        broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
        broker_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
        try:
            service = EcosMqttService(broker_host=broker_host, broker_port=broker_port)
            service.connect()
            _mqtt_service = service
        except (ConnectionError, TimeoutError, OSError):
            logging.exception(
                "Failed to connect MQTT service to %s:%s; MQTT functionality will be unavailable until connection is restored",
                broker_host,
                broker_port,
            )
            _mqtt_service = None
    return _mqtt_service


def _validate_tier(tier: str, allowed: Iterable[str]) -> str:
    tier_key = tier.lower()
    allowed_values = list(allowed)
    if tier_key not in allowed_values:
        allowed_str = ", ".join(sorted(allowed_values))
        raise HTTPException(status_code=400, detail=f"Unknown tier. Allowed: {allowed_str}")
    return tier_key


# ============================================
# CORE ENDPOINTS
# ============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check"""
    return {
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }


@app.get("/projects")
async def list_projects():
    """List all 13 projects and their status"""
    projects = [
        {"id": "P01", "name": "EcoHomes OS", "type": "Foam Homes"},
        {"id": "P02", "name": "AgriConnect", "type": "Symbiosis"},
        {"id": "P03", "name": "RegeneraFarm", "type": "Closed-Loop Farm"},
        {"id": "P04", "name": "HempMobility", "type": "Hemp Lab"},
        {"id": "P05", "name": "LumiFreq", "type": "Resonant Light"},
        {"id": "P06", "name": "NucleoSim", "type": "Fast Reactor"},
        {"id": "P07", "name": "PlastiCycle", "type": "Bioreactor"},
        {"id": "P08", "name": "EverLume", "type": "Centennial Bulb"},
        {"id": "P09", "name": "AquaGen", "type": "AWG"},
        {"id": "P10", "name": "ThermalGrid", "type": "Geothermal"},
        {"id": "P11", "name": "Reserved", "type": "Future"},
        {"id": "P12", "name": "SolarShare", "type": "Solar Gardens"},
        {"id": "P13", "name": "MicroHydro", "type": "Micro-Hydro"},
    ]
    phase_results = execute_all_initiatives()
    for project in projects:
        project["readiness"] = f"{phase_results[project['id']]['readiness']}%"
    average_readiness = sum(result["readiness"] for result in phase_results.values()) / len(phase_results)
    return {"projects": projects, "total": 13, "average_readiness": f"{average_readiness:.1f}%"}


def _find_hardware_profile(project_code: str) -> Dict[str, Any]:
    for item in HARDWARE_MANIFEST.get("initiatives", []):
        if item.get("code") == project_code:
            return item
    return {}


@app.get("/api/checklist/readiness")
async def checklist_readiness():
    """Execute checklist Levels 2 and 3 across all initiatives."""
    phase_results = execute_all_initiatives()
    readiness_values = [result["readiness"] for result in phase_results.values()]
    average_readiness = sum(readiness_values) / len(readiness_values)
    initiatives_in_target = sum(1 for result in phase_results.values() if result["target_60_to_70"])
    return {
        "total_initiatives": len(phase_results),
        "initiatives_in_60_to_70_band": initiatives_in_target,
        "average_readiness": f"{average_readiness:.1f}%",
        "results": phase_results,
    }


@app.get("/hardware/manifest")
async def hardware_manifest():
    """Return hardware scaffolds for all initiatives."""
    return HARDWARE_MANIFEST


@app.get("/hardware/{project_code}")
async def hardware_profile(project_code: str):
    profile = _find_hardware_profile(project_code)
    if not profile:
        raise HTTPException(status_code=404, detail="Unknown project_code")
    return profile


@app.post("/hardware/{project_code}/control")
async def hardware_control(project_code: str, command: ControlCommandRequest):
    profile = _find_hardware_profile(project_code)
    if not profile:
        raise HTTPException(status_code=404, detail="Unknown project_code")
    allowed_actions = profile.get("controlActions", [])
    if allowed_actions and command.action not in allowed_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Action '{command.action}' not allowed. Allowed: {allowed_actions}",
        )

    topic = f"ecos/{project_code}/{command.device_id}/control"
    published = False
    if MQTT_ENABLED:
        service = _get_mqtt_service()
        if service:
            try:
                published = service.publish_control(
                    project_code=project_code,
                    device_id=command.device_id,
                    action=command.action,
                    params=command.params,
                )
            except (ConnectionError, TimeoutError, OSError):
                logging.exception(
                    "Failed to publish control command for device %s in project %s (action: %s)",
                    command.device_id,
                    project_code,
                    command.action,
                )
                published = False

    return {
        "status": "accepted",
        "mqtt_enabled": MQTT_ENABLED,
        "published": published,
        "project_code": project_code,
        "device_id": command.device_id,
        "action": command.action,
        "topic": topic,
        "allowed_actions": allowed_actions,
    }


# ============================================
# PROJECT-SPECIFIC ENDPOINTS
# ============================================

# Project #13: Micro-Hydro
@app.post("/api/hydro/forecast")
async def hydro_forecast(request: StreamFlowRequest):
    """Forecast stream flow for Micro-Hydro power generation"""
    try:
        result = forecast_stream_flow(request.historical_data, request.hours_ahead)
        return {"project": "P13_HYDRO", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Project #12: Solar Gardens
@app.post("/api/solar/forecast")
async def solar_forecast(request: SolarIrradianceRequest):
    """Forecast solar irradiance for photovoltaic generation"""
    try:
        result = forecast_solar_irradiance(request.historical_data, request.hours_ahead)
        return {"project": "P12_SOLAR", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Project #9: AWG (Atmospheric Water Generator)
@app.post("/api/awg/forecast")
async def awg_forecast(request: HumidityRequest):
    """Forecast optimal humidity windows for water generation"""
    try:
        result = forecast_humidity(request.historical_data, request.hours_ahead)
        return {"project": "P09_AWG", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/awg/optimize")
async def awg_optimize(request: AWGScheduleRequest):
    """Optimize AWG run schedule to minimize energy costs"""
    try:
        result = optimize_awg_schedule(
            request.humidity_forecast,
            request.energy_prices,
            request.target_liters
        )
        return {"project": "P09_AWG", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Project #8: Centennial Bulb
@app.post("/api/bulb/predict")
async def bulb_predict(request: BulbTelemetryRequest):
    """Predict bulb failure probability using Bayesian model"""
    try:
        telemetry = {
            'voltage': request.voltage,
            'thermal_cycles': request.thermal_cycles,
            'uptime': request.uptime
        }
        result = predict_bulb_failure(telemetry)
        return {"project": "P08_BULB", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Project #3: Closed-Loop Farm
@app.post("/api/farm/optimize")
async def farm_optimize(request: NutrientCycleRequest):
    """Optimize nutrient cycle allocation"""
    try:
        result = optimize_nutrient_cycle(request.waste_inputs, request.crop_demands)
        return {"project": "P03_FARM", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Project #10: Geothermal Network
@app.post("/api/geothermal/optimize")
async def geothermal_optimize(request: GeothermalFlowRequest):
    """Optimize geothermal heat flow distribution"""
    try:
        result = optimize_geothermal_flow(
            request.building_loads,
            request.ground_temp,
            request.available_capacity
        )
        return {"project": "P10_GEOTHERMAL", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Project #2: Symbiosis (Fungal Matching)
@app.post("/api/symbiosis/recommend")
async def symbiosis_recommend(request: FungalMatchRequest):
    """Recommend fungal strain based on soil data"""
    try:
        result = optimize_fungal_match(request.soil_data)
        return {"project": "P02_SYMBIOSIS", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# DISPATCHER ENDPOINTS (Cross-Project Coordination)
# ============================================

@app.post("/api/dispatch")
async def dispatcher_endpoint(request: DispatchRequest):
    """Execute cross-project coordination actions"""
    try:
        result = dispatch(request.action, **request.params)
        return {"dispatcher": "ECOS", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dispatch/status")
async def dispatcher_status():
    """Get dispatcher system status"""
    try:
        result = dispatch('status')
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# LEVEL 2-5 CAPABILITIES (Connectivity, Billing, Deployment)
# ============================================


@app.post("/api/iot/ingest")
async def ingest_telemetry(request: TelemetryIngestRequest):
    """Level 2: Accept telemetry from MQTT pipeline"""
    now_utc = datetime.now(timezone.utc)
    if request.timestamp > now_utc:
        raise HTTPException(status_code=400, detail="Timestamp cannot be in the future")
    if request.timestamp < now_utc - timedelta(days=30):
        raise HTTPException(status_code=400, detail="Timestamp too old for ingestion window")
    topic = f"ecos/{request.project_code}/{request.device_id}/telemetry"
    return {
        "topic": topic,
        "ingested": True,
        "quality_flag": request.quality_flag,
        "echo": {
            "sensor_id": request.sensor_id,
            "measurement_type": request.measurement_type,
            "measurement_value": request.measurement_value,
            "unit": request.unit,
            "timestamp": request.timestamp.isoformat(),
        },
    }


@app.post("/api/auth/token")
async def issue_auth_token(request: AuthTokenRequest):
    """Level 2: Shared auth token issuance (versioned HMAC-signed token)"""
    issued_at = datetime.now(timezone.utc).replace(microsecond=0)
    expires_at = issued_at + timedelta(hours=24)
    payload = {
        "user_id": request.user_id,
        "email": request.email,
        "role": request.role,
        "project_access": request.project_access,
        "issued_at": issued_at.isoformat(),
        "exp": expires_at.isoformat(),
    }
    token = _sign_token(payload)
    return {
        "token": token,
        "expires_in_hours": 24,
        "scopes": request.project_access,
        "issued_at": issued_at.isoformat(),
        "expires_at": expires_at.isoformat(),
    }


@app.post("/api/billing/estimate")
async def billing_estimate(request: BillingEstimateRequest):
    """Level 2: Billing hook to estimate usage-based charges"""
    rate_card = {
        "free": {"kwh": 0.25, "water": 0.05, "platform": 0.0},
        "pro": {"kwh": 0.18, "water": 0.03, "platform": 5.0},
        "enterprise": {"kwh": 0.12, "water": 0.02, "platform": 15.0},
    }
    tier_key = _validate_tier(request.tier, rate_card.keys())
    rate = rate_card[tier_key]
    energy_cost = request.usage_kwh * rate["kwh"]
    water_cost = request.water_liters * rate["water"]
    total = energy_cost + water_cost + rate["platform"]
    return {
        "tier": tier_key,
        "energy_cost": round(energy_cost, 2),
        "water_cost": round(water_cost, 2),
        "platform_fee": rate["platform"],
        "total_estimate": round(total, 2),
    }


@app.post("/api/firmware/flash")
async def firmware_flash(request: FirmwareFlashRequest):
    """Level 3: Simulate OTA firmware flash queue"""
    if not re.fullmatch(r"[a-fA-F0-9]{64}", request.checksum):
        raise HTTPException(status_code=400, detail="Invalid firmware checksum format; expected 64 hex chars")
    if not re.fullmatch(r"v?\d+\.\d+\.\d+", request.firmware_version):
        raise HTTPException(status_code=400, detail="Invalid firmware version format")
    return {
        "project": request.project_code,
        "device_id": request.device_id,
        "firmware_version": request.firmware_version,
        "checksum": request.checksum,
        "status": "queued",
        "queued_at": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/deployment/status")
async def deployment_status(request: DeploymentStatusRequest):
    """Level 4: Field deployment + synergy readiness"""
    project_pattern = re.compile(r"^P\d{2}")
    validated_inputs = [code for code in request.inputs_from if project_pattern.match(code)]
    validated_outputs = [code for code in request.outputs_to if project_pattern.match(code)]
    invalid_inputs_from = [code for code in request.inputs_from if not project_pattern.match(code)]
    invalid_outputs_to = [code for code in request.outputs_to if not project_pattern.match(code)]
    synergy_ready = bool(validated_inputs and validated_outputs)
    return {
        "zone": request.zone,
        "project": request.project_code,
        "inputs_from": validated_inputs,
        "invalid_inputs_from": invalid_inputs_from,
        "outputs_to": validated_outputs,
        "invalid_outputs_to": invalid_outputs_to,
        "project_code_pattern": project_pattern.pattern,
        "synergy_ready": synergy_ready,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# Default SaaS tier configuration. Can be overridden at runtime via the
# SAAS_TIERS_JSON environment variable (must be a JSON object).
DEFAULT_SAAS_TIERS: Dict[str, Dict[str, Any]] = {
    "free": {
        "features": ["basic-dashboard", "read-only-api"],
        "regulatory_log": False,
        "support_level": "community",
    },
    "pro": {
        "features": ["dashboard", "api-access", "iot-pipeline"],
        "regulatory_log": True,
        "support_level": "standard",
    },
    "enterprise": {
        "features": [
            "dashboard",
            "api-access",
            "iot-pipeline",
            "billing-hooks",
            "audit-trail",
        ],
        "regulatory_log": True,
        "support_level": "dedicated",
    },
}


def _get_saas_tiers() -> Dict[str, Dict[str, Any]]:
    """Return SaaS tier configuration, allowing override via environment.

    If SAAS_TIERS_JSON is set and contains a valid JSON object, that object
    is used as the tier configuration. Otherwise, DEFAULT_SAAS_TIERS is used.
    """
    raw = os.getenv("SAAS_TIERS_JSON")
    if not raw:
        return DEFAULT_SAAS_TIERS

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback to default configuration on invalid JSON
        return DEFAULT_SAAS_TIERS

    # Ensure the loaded data is a mapping; otherwise, fall back
    if not isinstance(data, dict):
        return DEFAULT_SAAS_TIERS

    return data  # type: ignore[return-value]


@app.post("/api/saas/tier")
async def saas_tier(request: SaaSTierRequest):
    """Level 5: SaaS tiering + regulatory logging surface"""
    tiers = _get_saas_tiers()
    tier_key = _validate_tier(request.tier, tiers.keys())
    config = tiers[tier_key]

    audit_entry = {
        "tier": tier_key,
        "regulatory_log_enabled": config["regulatory_log"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "tier": tier_key,
        "features": config["features"],
        "support_level": config["support_level"],
        "regulatory_log": audit_entry,
    }


# ============================================
# PLACEHOLDER ENDPOINTS FOR REMAINING PROJECTS
# ============================================

@app.get("/api/foam-homes/status")
async def foam_homes_status():
    """Project #1: Foam Homes - Placeholder"""
    return {
        "project": "P01_FOAM_HOMES",
        "status": "Level 1 Complete - 20% Readiness",
        "features": ["Parametric Design Engine Ready", "BOM Generator Ready"]
    }


@app.get("/api/hemp-lab/status")
async def hemp_lab_status():
    """Project #4: Hemp Lab - Placeholder"""
    return {
        "project": "P04_HEMP_LAB",
        "status": "Level 1 Complete - 20% Readiness",
        "features": ["Material Testing Framework Ready", "FEA Simulation Ready"]
    }


@app.get("/api/greenhouse/status")
async def greenhouse_status():
    """Project #5: Greenhouse - Placeholder"""
    return {
        "project": "P05_GREENHOUSE",
        "status": "Level 1 Complete - 20% Readiness",
        "features": ["Light Recipe System Ready", "Feedback Control Ready"]
    }


@app.get("/api/reactor/status")
async def reactor_status():
    """Project #6: Fast Reactor - Placeholder"""
    return {
        "project": "P06_REACTOR",
        "status": "Level 1 Complete - 20% Readiness",
        "features": ["Physics Engine Ready", "Safety Simulation Ready"]
    }


@app.get("/api/bioreactor/status")
async def bioreactor_status():
    """Project #7: Bioreactor - Placeholder"""
    return {
        "project": "P07_BIOREACTOR",
        "status": "Level 1 Complete - 20% Readiness",
        "features": ["Bioprocess Control Ready", "Degradation Forecast Ready"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
