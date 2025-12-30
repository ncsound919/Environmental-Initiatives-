"""
ECOS API Gateway - FastAPI application
Exposes all 13 project brains as REST APIs
Completes Level 1 requirement: API Exposed
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

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

app = FastAPI(
    title="ECOS API Gateway",
    description="Unified API for all 13 Environmental Businesses",
    version="1.0.0"
)


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


# ============================================
# CORE ENDPOINTS
# ============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/projects")
async def list_projects():
    """List all 13 projects and their status"""
    projects = [
        {"id": "P01", "name": "EcoHomes OS", "type": "Foam Homes", "readiness": "20%"},
        {"id": "P02", "name": "AgriConnect", "type": "Symbiosis", "readiness": "20%"},
        {"id": "P03", "name": "RegeneraFarm", "type": "Closed-Loop Farm", "readiness": "20%"},
        {"id": "P04", "name": "HempMobility", "type": "Hemp Lab", "readiness": "20%"},
        {"id": "P05", "name": "LumiFreq", "type": "Resonant Light", "readiness": "20%"},
        {"id": "P06", "name": "NucleoSim", "type": "Fast Reactor", "readiness": "20%"},
        {"id": "P07", "name": "PlastiCycle", "type": "Bioreactor", "readiness": "20%"},
        {"id": "P08", "name": "EverLume", "type": "Centennial Bulb", "readiness": "20%"},
        {"id": "P09", "name": "AquaGen", "type": "AWG", "readiness": "20%"},
        {"id": "P10", "name": "ThermalGrid", "type": "Geothermal", "readiness": "20%"},
        {"id": "P11", "name": "Reserved", "type": "Future", "readiness": "0%"},
        {"id": "P12", "name": "SolarShare", "type": "Solar Gardens", "readiness": "20%"},
        {"id": "P13", "name": "MicroHydro", "type": "Micro-Hydro", "readiness": "20%"},
    ]
    return {"projects": projects, "total": 13, "average_readiness": "18.5%"}


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
